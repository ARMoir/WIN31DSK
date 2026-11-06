#!/usr/bin/env python3
"""Diagnostic-only trace of Windows XT RESERVE.COM initial platform checks.

Does not bypass, relax, or invert any video-memory safety check. Each of five
existing nonmatching platform-check branches is rerouted to its own error
message, then to the EXACT SAME original DOS cleanup/failure path at 02CFh.

Changes only /WINXT/RESERVE.COM in a separate, checksum-pinned experimental
Tandy CF image. Nothing in its DOS boot, Windows mouse, display, or launcher
configuration is touched.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "int33-test"))
from fat16_image import Fat16, CARD_BYTES

SOURCE_IMAGE_SHA = "ee9a7a214faabd1af8c250f0e3937d0de184291de71242f52b2ab67403a1d526"
RESERVE_ORIGINAL_SHA = "644290e234cab9a6ac3799fa32959bb493d82d566501a8925720bb5a28c6afa8"
ORIGINAL_FAIL = 0x02CF
# These are the existing near JMPs on failure, following corresponding
# CMP/JNE tests in exact binary audited with objdump -D -mi8086.
CHECKS = [
    (0x0129, "e9a301", b"RESERVE TRACE 1: FFFF:000E not FF$"),
    (0x013B, "e99101", b"RESERVE TRACE 2: FC00:0000 not 21$"),
    (0x014E, "e97e01", b"RESERVE TRACE 3: BIOS KB not 624$"),
    (0x015B, "e97101", b"RESERVE TRACE 4: Video mode not 3$"),
    (0x0168, "e96401", b"RESERVE TRACE 5: DOS version below 3$"),
]

def digest(data):
    return sha256(data).hexdigest()

def jmp_from(source_addr, target_addr):
    # E9: 16-bit relative near JMP. This is 8086-safe.
    displacement = (target_addr - source_addr - 3) & 0xFFFF
    return b"\xE9" + struct.pack("<H", displacement)

def trace_driver(original):
    if digest(original) != RESERVE_ORIGINAL_SHA or len(original) != 1512:
        raise ValueError("RESERVE.COM is not the pinned upstream build")

    binary = bytearray(original)
    start = 0x0100 + len(binary)
    stub_size = 6  # BA imm16; E9 signed16
    messages_start = start + stub_size * len(CHECKS)

    messages = []
    position = messages_start
    expected = {}
    for address, expected_hex, msg in CHECKS:
        old = bytes.fromhex(expected_hex)
        if original[address-0x100:address-0x100+3] != old:
            raise ValueError(f"Unexpected failure jump at {address:04x}")
        expected[address] = old
        messages.append((position, msg))
        position += len(msg) + 2  # DOS CR LF after message, dollar terminator already included

    for idx, (address, _, _) in enumerate(CHECKS):
        stub_addr = start + idx * stub_size
        msg_addr = messages[idx][0]
        binary[address-0x100:address-0x100+3] = jmp_from(address, stub_addr)
        stub = b"\xBA" + struct.pack("<H", msg_addr) + jmp_from(stub_addr+3, ORIGINAL_FAIL)
        if len(stub) != stub_size:
            raise ValueError("Wrong diagnostic trampoline length")
        binary.extend(stub)

    for _, msg in messages:
        binary.extend(msg + b"\r\n")
    if len(binary) > 2048:
        raise ValueError("Diagnostic cannot fit existing RESERVE.COM FAT cluster")

    # Verify no instructions except exactly five original failure jumps changed.
    for i, (before, after) in enumerate(zip(original, binary)):
        if before != after and not any((address-0x100) <= i < (address-0x100+3)
                                       for address in expected):
            raise ValueError(f"Unexpected original binary change at {i:04x}")
    for idx, (address, _, _) in enumerate(CHECKS):
        stub_addr = start + idx * stub_size
        new_jump = bytes(binary[address-0x100:address-0x100+3])
        assert new_jump == jmp_from(address, stub_addr)
        stub = bytes(binary[stub_addr-0x100:stub_addr-0x100+6])
        assert stub == b"\xBA" + struct.pack("<H", messages[idx][0]) + jmp_from(stub_addr+3, ORIGINAL_FAIL)
        assert binary[messages[idx][0]-0x100:messages[idx][0]-0x100+len(messages[idx][1])] == messages[idx][1]
    return bytes(binary)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("source_image", type=Path)
    p.add_argument("output_image", type=Path)
    args = p.parse_args()

    src = args.source_image.read_bytes()
    if len(src) != CARD_BYTES or digest(src) != SOURCE_IMAGE_SHA:
        raise ValueError("Input does not match the exact plain-DOS 16-color test image")
    image = Fat16(bytearray(src))
    path = "/WINXT/RESERVE.COM"
    original = image.read(path)
    traced = trace_driver(original)
    image.write_existing(path, traced)

    for path_check in ("/CONFIG.SYS", "/AUTOEXEC.BAT", "/CTMOUSE.EXE",
                       "/WIN.BAT", "/WINXT/RESTORE.BAT",
                       "/WINDOWS/SYSTEM.INI", "/WINDOWS/SYSTEM/MSMOUSE1.DRV",
                       "/WINDOWS/SYSTEM/TR53216.DRV",
                       "/WINDOWS/SYSTEM/TANDYDSP.DRV"):
        fresh = Fat16(bytearray(src))
        if fresh.read(path_check) != image.read(path_check):
            raise ValueError(f"Working configuration changed: {path_check}")
    assert image.read("/WINXT/RESERVE.COM") == traced
    output = bytes(image.b)
    if len(output) != CARD_BYTES:
        raise ValueError("Incorrect CF card size")
    args.output_image.parent.mkdir(parents=True, exist_ok=True)
    args.output_image.write_bytes(output)
    args.output_image.with_name(args.output_image.name+".sha256").write_text(
        f"{digest(output)}  {args.output_image.name}\n", encoding="ascii")
    print(f"Generated diagnostic {len(traced)}-byte RESERVE.COM: SHA256 {digest(traced)}")
    print(f"Generated CF image {len(output)} bytes SHA256 {digest(output)}")
    print("All five original platform checks and memory safety path remain in force.")
    print("Original mouse, DOS startup, Windows video, recovery and manual WIN unchanged.")

if __name__ == "__main__":
    main()
