#!/usr/bin/env python3
"""Build a mouse-enabled Windows 3.0 image without modifying the baseline."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile

PARTITION_OFFSET = 63 * 512
IMAGE_SIZE = 16 * 1024 * 1024

def run(*args):
    subprocess.run(args, check=True)

def mcopy(image, source, dest):
    run("mcopy", "-o", "-i", f"{image}@@{PARTITION_OFFSET}", str(source), dest)

def read_dos(image, path, destination):
    run("mcopy", "-i", f"{image}@@{PARTITION_OFFSET}", path, str(destination))

def replace_ini(text):
    pattern = re.compile(r"(?im)^(\s*mouse\.drv\s*=).*$")
    section = re.search(r"(?im)^\[boot\]\s*$", text)
    if not section:
        raise ValueError("Windows SYSTEM.INI has no [boot] section")
    boundaries = list(re.finditer(r"(?m)^\[[^\]\r\n]+\]\s*$", text))
    idx = next((i for i, m in enumerate(boundaries) if m.start() == section.start()), None)
    if idx is None:
        raise ValueError("Cannot find [boot] section bounds")
    end = boundaries[idx + 1].start() if idx + 1 < len(boundaries) else len(text)
    boot = text[section.end():end]
    if pattern.search(boot):
        boot = pattern.sub(r"\g<1>mouse.drv", boot, count=1)
    else:
        boot = "\r\nmouse.drv=mouse.drv" + boot
    updated = text[:section.end()] + boot + text[end:]
    # Preserve separate display-driver and hardware settings.
    return updated

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("mouse_driver", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.mouse_driver.is_file():
        raise SystemExit(
            f"Missing Windows 3.0-compatible MOUSE.DRV at {args.mouse_driver}. "
            "Add a legitimately obtained Windows 3.0 mouse driver to the TANDY30 branch. "
            "The DOS MOUSE.SYS alone does not enable the Windows mouse."
        )
    driver = args.mouse_driver.read_bytes()
    if len(driver) < 1024 or driver[:2] != b"MZ":
        raise SystemExit("Provided mouse driver does not resemble a valid DOS/Windows executable driver (MZ header).")
    if args.baseline.stat().st_size != IMAGE_SIZE:
        raise SystemExit("Baseline must be exactly 16 MiB (16777216 bytes).")
    with args.baseline.open("rb") as src:
        mbr = src.read(512)
        if mbr[510:512] != b"\x55\xaa":
            raise SystemExit("Invalid MBR signature")
        ptype = mbr[450]
        start, count = struct.unpack_from("<II", mbr, 454)
        if ptype not in (0x01, 0x04, 0x06) or start != 63 or start + count > IMAGE_SIZE // 512:
            raise SystemExit(f"Unexpected DOS partition layout: type={ptype:#x}, start={start}, sectors={count}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.baseline, args.output)
    with tempfile.TemporaryDirectory() as work:
        temp = Path(work)
        ini = temp / "SYSTEM.INI"
        read_dos(args.output, "::/WINDOWS/SYSTEM.INI", ini)
        original = ini.read_bytes()
        # Windows 3.0 expects CRLF text, and the file may use DOS codepage characters.
        updated = replace_ini(original.decode("cp437")).replace("\r\n", "\n").replace("\n", "\r\n").encode("cp437")
        ini.write_bytes(updated)
        mcopy(args.output, args.mouse_driver, "::/WINDOWS/SYSTEM/MOUSE.DRV")
        mcopy(args.output, ini, "::/WINDOWS/SYSTEM.INI")
        check = temp / "CHECK.INI"
        read_dos(args.output, "::/WINDOWS/SYSTEM.INI", check)
        if not re.search(rb"(?im)^mouse\.drv\s*=\s*mouse\.drv\s*$", check.read_bytes()):
            raise SystemExit("Failed to verify Windows mouse driver activation")
        readback = temp / "VERIFY.DRV"
        read_dos(args.output, "::/WINDOWS/SYSTEM/MOUSE.DRV", readback)
        if readback.read_bytes() != driver:
            raise SystemExit("Mouse driver did not round-trip correctly")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n", encoding="ascii"
    )
    print(f"Created {args.output} ({args.output.stat().st_size} bytes) SHA256 {digest}")

if __name__ == "__main__":
    main()
