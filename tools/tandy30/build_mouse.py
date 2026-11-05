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
IMAGE_SIZE = 31808 * 512

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
    parser.add_argument("--dos-test", type=Path, help="8086-compatible MTEST.COM to install at C:\\MTEST.COM")
    parser.add_argument("--cutemouse", type=Path, help="8086-compatible CTMOUSE.EXE; disable legacy MOUSE.SYS startup line")
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
        raise SystemExit("Input image must match CF card capacity: 31808 sectors (16285696 bytes).")
    with args.baseline.open("rb") as src:
        mbr = src.read(512)
        if mbr[510:512] != b"\x55\xaa":
            raise SystemExit("Invalid MBR signature")
        ptype = mbr[450]
        start, count = struct.unpack_from("<II", mbr, 454)
        if ptype not in (0x01, 0x04, 0x06) or start != 63 or start + count != IMAGE_SIZE // 512:
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
        if args.dos_test:
            tester = args.dos_test.read_bytes()
            if not 128 <= len(tester) <= 65536 or tester.startswith(b"MZ"):
                raise SystemExit("MTEST.COM must be a small DOS .COM binary")
            mcopy(args.output, args.dos_test, "::/MTEST.COM")
            test_copy = temp / "VERIFY.COM"
            read_dos(args.output, "::/MTEST.COM", test_copy)
            if test_copy.read_bytes() != tester:
                raise SystemExit("DOS mouse test program did not round-trip correctly")
            print(f"Installed DOS mouse tester C:\\MTEST.COM ({len(tester)} bytes)")
        if args.cutemouse:
            cutemouse = args.cutemouse.read_bytes()
            if len(cutemouse) < 1024 or cutemouse[:2] != b"MZ":
                raise SystemExit("CTMOUSE.EXE must be a DOS MZ executable")
            config = temp / "CONFIG.SYS"
            read_dos(args.output, "::/CONFIG.SYS", config)
            current_config = config.read_bytes()
            lines = current_config.decode("cp437").splitlines(keepends=True)
            pattern = re.compile(r"(?i)^\s*DEVICE(?:HIGH)?\s*=\s*(?:[A-Z]:)?\\MOUSE\\MOUSE\.SYS(?:\s|$)")
            hits = [i for i, line in enumerate(lines) if pattern.match(line)]
            if len(hits) != 1:
                raise SystemExit(f"Expected one legacy MOUSE.SYS line in CONFIG.SYS, found {len(hits)}")
            lines[hits[0]] = "REM " + lines[hits[0]]
            new_config = "".join(lines).encode("cp437")
            config.write_bytes(new_config)
            mcopy(args.output, args.cutemouse, "::/CTMOUSE.EXE")
            mcopy(args.output, config, "::/CONFIG.SYS")
            verify_driver = temp / "CTVERIFY.EXE"
            read_dos(args.output, "::/CTMOUSE.EXE", verify_driver)
            if verify_driver.read_bytes() != cutemouse:
                raise SystemExit("CTMOUSE.EXE did not round-trip correctly")
            verify_config = temp / "CONFIG.VER"
            read_dos(args.output, "::/CONFIG.SYS", verify_config)
            if verify_config.read_bytes() != new_config or any(
                pattern.match(line) for line in new_config.decode("cp437").splitlines()
            ):
                raise SystemExit("Failed to disable old Microsoft DOS MOUSE.SYS")
            print("Installed CTMOUSE.EXE, disabled legacy CONFIG.SYS mouse entry; not automatically loaded")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n", encoding="ascii"
    )
    print(f"Created {args.output} ({args.output.stat().st_size} bytes) SHA256 {digest}")

if __name__ == "__main__":
    main()
