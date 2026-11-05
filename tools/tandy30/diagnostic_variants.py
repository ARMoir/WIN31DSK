#!/usr/bin/env python3
"""Create two controlled Windows 3.0 mouse startup experiments.

Input: validated card-sized TANDY30 image with Windows Mouse Systems driver
and DOS CuteMouse /S14 /M autoload.
Outputs (copies only):
  1) Keep DOS CuteMouse, restore Windows NOMOUSE.DRV
  2) Keep Windows MSMOUSE1.DRV, disable DOS CuteMouse autoload

Do not edit display driver or baseline. Both resulting raw disk images are
31,808 sectors (the actual CompactFlash card capacity).
"""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

CARD_BYTES = 31808 * 512
OFFSET_BYTES = 63 * 512

def mcopy(image, src, dst, overwrite=False):
    cmd = ["mcopy"]
    if overwrite:
        cmd.append("-o")
    cmd.extend(("-i", f"{image}@@{OFFSET_BYTES}", str(src), str(dst)))
    subprocess.run(cmd, check=True, capture_output=True, text=True)

def read_file(image, dospath):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "file"
        mcopy(image, dospath, p)
        return p.read_bytes()

def write_file(image, dospath, content):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "file"
        p.write_bytes(content)
        mcopy(image, p, dospath, overwrite=True)
    if read_file(image, dospath) != content:
        raise RuntimeError(f"Failed FAT16 read-back check for {dospath}")

def windows_mouse(ini, new_name):
    original = ini.decode("cp437")
    lines = original.splitlines(keepends=True)
    in_boot = False
    matched = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_boot = stripped.lower() == "[boot]"
        elif in_boot and re.match(r"(?i)^[ \t]*mouse[.]drv[ \t]*=", line):
            newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            lines[i] = f"mouse.drv={new_name}{newline}"
            matched += 1
    if matched != 1:
        raise RuntimeError(f"Expected one mouse.drv line in [boot], found {matched}")
    return "".join(lines).encode("cp437")

def configured_driver(ini):
    in_boot = False
    found = {}
    for line in ini.decode("cp437").splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_boot = line.lower() == "[boot]"
        elif in_boot and not line.startswith(";") and "=" in line:
            key, value = line.split("=", 1)
            if key.strip().lower() in ("mouse.drv", "display.drv"):
                found[key.strip().lower()] = value.strip().lower()
    return found

def remove_dos_mouse_autoload(autoexec):
    lines = autoexec.decode("cp437").splitlines(keepends=True)
    pattern = re.compile(r"(?i)^[ \t]*C:\\CTMOUSE[.]EXE[ \t]+/S14[ \t]+/M[ \t]*$")
    kept = [line for line in lines if not pattern.fullmatch(line.strip())]
    if len(kept) != len(lines) - 1:
        raise RuntimeError("Expected exactly one DOS CuteMouse autoload line")
    return "".join(kept).encode("cp437")

def make(source, target, *, mouse, no_autoload):
    shutil.copyfile(source, target)
    ini_path = "::/WINDOWS/SYSTEM.INI"
    auto_path = "::/AUTOEXEC.BAT"
    before = read_file(target, ini_path)
    old_settings = configured_driver(before)
    if old_settings.get("mouse.drv") != "msmouse1.drv":
        raise RuntimeError(f"Unexpected source Windows mouse driver: {old_settings}")
    edited = windows_mouse(before, mouse)
    write_file(target, ini_path, edited)
    now = configured_driver(read_file(target, ini_path))
    if now.get("mouse.drv") != mouse.lower():
        raise RuntimeError(f"Windows driver mismatch: {now}")
    if now.get("display.drv") != old_settings.get("display.drv"):
        raise RuntimeError("Display driver unexpectedly changed")
    if mouse == "nomouse.drv":
        read_file(target, "::/WINDOWS/SYSTEM/NOMOUSE.DRV")
    else:
        read_file(target, "::/WINDOWS/SYSTEM/MSMOUSE1.DRV")
    if no_autoload:
        original_auto = read_file(target, auto_path)
        replacement = remove_dos_mouse_autoload(original_auto)
        write_file(target, auto_path, replacement)
    if target.stat().st_size != CARD_BYTES:
        raise RuntimeError("Output does not match physical CompactFlash card size")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_name(target.name + ".sha256").write_text(
        f"{digest}  {target.name}\n", encoding="ascii")
    print(f"{target.name}: {CARD_BYTES} bytes, Windows={mouse}, DOS CuteMouse auto={not no_autoload}, sha256={digest}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("directory", type=Path)
    args = ap.parse_args()
    if args.source.stat().st_size != CARD_BYTES:
        raise SystemExit("Expected 31,808-sector mouse-enabled source")
    args.directory.mkdir(parents=True, exist_ok=True)
    make(args.source, args.directory / "TANDY1000EX_WIN30_DOSMOUSE_WIN_NOMOUSE_CF_31808S.img",
         mouse="nomouse.drv", no_autoload=False)
    make(args.source, args.directory / "TANDY1000EX_WIN30_MSSYS_NO_DOSMOUSE_CF_31808S.img",
         mouse="msmouse1.drv", no_autoload=True)

if __name__ == "__main__":
    main()
