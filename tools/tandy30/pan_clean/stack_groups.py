#!/usr/bin/env python3
"""Stack three existing Windows 3.0 Program Manager groups one icon row high.

Group files remain complete: every icon bitmap, name, command, icon path,
directory entry and program is retained. Only show state, window rectangle,
item screen coordinates and the documented PMCC checksum are changed.
Never operate on a mounted CF card or a known-working source image.
"""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import struct
import subprocess

SOURCE_SHA = "d8d0a38c3bab6f5df1b1f94c90efbb9b34beb2e35b5b4c6e25e53a3ff9102328"
CARD_BYTES = 31808 * 512
# MDI client coordinates, top-to-bottom, within first physical 320x200 viewport.
RECTS = {
    "MAIN": (1, 0, 309, 54),
    "ACCESSOR": (1, 54, 309, 108),
    "GAMES": (1, 108, 309, 162),
}
GROUPS = ("MAIN", "ACCESSOR", "GAMES")

def digest(b):
    return hashlib.sha256(b).hexdigest()

def guest_read(image, name, staging):
    target = staging / (name.replace("/", "_"))
    subprocess.run(["mcopy", "-n", "-i", str(image) + "@@32256", "::/" + name, str(target)], check=True)
    return target.read_bytes()

def guest_write(image, name, payload, staging):
    target = staging / ("NEW_" + name.replace("/", "_"))
    target.write_bytes(payload)
    subprocess.run(["mcopy", "-o", "-i", str(image) + "@@32256", str(target), "::/" + name], check=True)

def checksum_ok(data):
    padded = data + (b"\0" if len(data) % 2 else b"")
    return sum(struct.unpack("<%dH" % (len(padded) // 2), padded)) % 65536 == 0

def item_specs(data):
    if data[:4] != b"PMCC" or len(data) < 42:
        raise ValueError("Not a Program Manager PMCC group")
    group_size = struct.unpack_from("<H", data, 6)[0]
    if group_size != len(data):
        raise ValueError("Unexpected Win3.1 tagged group; refusing write")
    if not checksum_ok(data):
        raise ValueError("Original PMCC group checksum failed")
    count = struct.unpack_from("<H", data, 32)[0]
    if not 0 < count < 200 or 34 + 2 * count > group_size:
        raise ValueError("Invalid item-offset table")
    slots = []
    names = []
    for i in range(count):
        offset = struct.unpack_from("<H", data, 34 + 2 * i)[0]
        if offset == 0:
            continue
        if offset < 34 + count * 2 or offset + 24 > group_size:
            raise ValueError("Program item offset outside file")
        x, y = struct.unpack_from("<hh", data, offset)
        details = []
        for field in (18, 20, 22):  # name, command, icon path offsets
            addr = struct.unpack_from("<H", data, offset + field)[0]
            if not 0 < addr < group_size:
                raise ValueError("Invalid program item string offset")
            end = data.find(b"\0", addr)
            if end <= addr:
                raise ValueError("Invalid name/command/path string")
            details.append(data[addr:end])
        slots.append((y, x, i, offset))
        names.append((i, tuple(details)))
    if len(slots) < 2:
        raise ValueError("Unexpected empty/short group")
    return slots, names

def rearrange(data, group):
    slots, names = item_specs(data)
    b = bytearray(data)
    # Explicit SW_SHOWNORMAL, even if MAIN was previously minimized.
    struct.pack_into("<H", b, 8, 1)
    struct.pack_into("<hhhh", b, 10, *RECTS[group])
    # Keep the previous reading order (original upper row first, then left-to-right).
    # Icons beyond 308px are available via the group's horizontal scrollbar.
    for index, (_, _, _, at) in enumerate(sorted(slots)):
        struct.pack_into("<hh", b, at, 14 + 75 * index, 0)
    # Microsoft Win3 PMCC checksum: negative 16-bit sum of all words,
    # including the checksum word. Pad an odd byte count for the sum only.
    struct.pack_into("<H", b, 4, 0)
    padded = bytes(b) + (b"\0" if len(b) & 1 else b"")
    words = struct.unpack("<%dH" % (len(padded) // 2), padded)
    struct.pack_into("<H", b, 4, (-sum(words)) & 0xffff)
    final = bytes(b)
    assert len(final) == len(data) and checksum_ok(final)
    new_slots, new_names = item_specs(final)
    assert names == new_names, "Program names, commands or icon paths changed"
    assert len(slots) == len(new_slots)
    for before, after in zip(slots, new_slots):
        assert before[2:] == after[2:]  # original item offsets & table
    assert struct.unpack_from("<H", final, 8)[0] == 1
    assert struct.unpack_from("<hhhh", final, 10) == RECTS[group]
    # Enforce no other changed bytes beyond known 10-byte header and XY points.
    allowed = set(range(4, 6)) | set(range(8, 18))
    for _, _, _, offset in slots:
        allowed.update(range(offset, offset + 4))
    assert all(data[i] == final[i] for i in range(len(data)) if i not in allowed)
    print("STACK", group, "icons:", len(slots), "rectangle:", RECTS[group],
          "sha256:", digest(final), "valid checksum")
    return final

def ini_stack(data):
    if b"AutoArrange=1" not in data or b"SaveSettings=0" not in data:
        raise ValueError("Unexpected Program Manager configuration")
    if b"Window=0 0 316 196 1" not in data:
        raise ValueError("Expected the proven first-viewport Program Manager geometry")
    for group in GROUPS:
        if ("C:\\WINDOWS\\" + group + ".GRP").encode() not in data:
            raise ValueError("Missing existing " + group + " group reference")
    # Auto-arrange would wrap icons into additional rows whenever the
    # group windows were resized. Explicit coordinates prevent that.
    new = data.replace(b"AutoArrange=1", b"AutoArrange=0")
    assert len(new) == len(data), "Keep DOS FAT16 file sizes unchanged"
    return new

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--staging", type=Path, required=True)
    args = ap.parse_args()
    original = args.source.read_bytes()
    if len(original) != CARD_BYTES or digest(original) != SOURCE_SHA:
        raise ValueError("CF source must be the verified border-2 Program Manager release")
    if args.output.exists() or args.staging.exists():
        raise ValueError("Refusing to overwrite previous image or staging files")
    args.staging.mkdir(parents=True)
    shutil.copyfile(args.source, args.output)
    for group in GROUPS:
        filename = "WINDOWS/" + group + ".GRP"
        data = guest_read(args.output, filename, args.staging)
        updated = rearrange(data, group)
        guest_write(args.output, filename, updated, args.staging)
        assert guest_read(args.output, filename, args.staging) == updated
    pm = guest_read(args.output, "WINDOWS/PROGMAN.INI", args.staging)
    saved = guest_read(args.output, "TANDY88/PRGPAN.INI", args.staging)
    if pm != saved:
        raise ValueError("Active Program Manager and PANON snapshot differ")
    pm_new = ini_stack(pm)
    for name in ("WINDOWS/PROGMAN.INI", "TANDY88/PRGPAN.INI"):
        guest_write(args.output, name, pm_new, args.staging)
        assert guest_read(args.output, name, args.staging) == pm_new
    print("IMAGE:", args.output, len(original), "bytes", digest(args.output.read_bytes()))
    print("No application programs, group items or icon resource bytes changed")

if __name__ == "__main__":
    main()
