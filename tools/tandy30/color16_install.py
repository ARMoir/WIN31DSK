#!/usr/bin/env python3
"""Add an experimental 320x200x16 Windows display to the verified Tandy CF image.

Preserves the exact known-working DOS, mouse, and startup configuration.
Installs a separate protected manual WIN.BAT launcher for 16-color video RAM.
Never modifies the source image and never starts Windows automatically.
"""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PARTITION_OFFSET = 63 * 512
CARD_BYTES = 31808 * 512
KNOWN_GOOD_SHA = "eca08b0eb4283854bfef71d98d8febe08ad8de89eb3d52a109a0b9d39993fa34"
DRIVER_SHA = "ac0b2a72693b4ac7dd19a28f4f24f180a9c0b0ca0ccaa3dab2c9d1d33055290c"
RESERVE_SHA = "644290e234cab9a6ac3799fa32959bb493d82d566501a8925720bb5a28c6afa8"
FONT_SHAS = {
    "XTESYS.FON": "e82303cb742cb715a147bb09a4d018c786f74d9a03e1ea765b28ecda21ac7e87",
    "XTEFIX.FON": "d4bb1d90c34ed4671b80170004113e50d7b5ea0137b71c1ab9d49f60e78049f4",
    "XTEOEM.FON": "4ed3252c4af2cbd461f448c52f68638d274e47586395a8e84e3e1557f1f38425",
}


def digest(b):
    return hashlib.sha256(b).hexdigest()


def run(*cmd):
    subprocess.run(cmd, check=True)


def boot_set(source):
    text = source.decode("cp437")
    match = re.search(r"(?im)^\[boot\][ \t]*\r?$", text)
    if not match:
        raise ValueError("Missing Windows 3.0 [boot] section")
    following = re.search(r"(?m)^\[[^\r\n]+\]", text[match.end():])
    stop = match.end() + following.start() if following else len(text)
    section = text[match.end():stop]
    edits = {
        "display.drv": "TR53216.DRV",
        "286grabber": "CGA.GR2",
        "fixedfon.fon": "XTEFIX.FON",
        "oemfonts.fon": "XTEOEM.FON",
        "fonts.fon": "XTESYS.FON",
    }
    for key, replacement in edits.items():
        pattern = re.compile(r"(?im)^([ \t]*" + re.escape(key) + r"[ \t]*=)[^\r\n]*")
        if len(pattern.findall(section)) != 1:
            raise ValueError("Missing or duplicate Windows " + key)
        section = pattern.sub(lambda m: m.group(1) + replacement, section, count=1)
    updated = text[:match.end()] + section + text[stop:]
    return updated.encode("cp437")


def dos_text(s):
    return (s.replace("\r\n", "\n").replace("\n", "\r\n")).encode("cp437")


LAUNCHER = dos_text(r"""@ECHO OFF
REM Manual 320x200 16-color Windows. DOS always boots normally.
C:\WINXT\RESERVE.COM
IF ERRORLEVEL 1 GOTO BAD
C:\WINDOWS\WIN.COM /R
GOTO DONE
:BAD
ECHO 16-color video memory reservation failed. Windows was NOT started.
ECHO To restore 640x200: C:\WINXT\RESTORE
:DONE
""")
RESTORE = dos_text(r"""@ECHO OFF
IF NOT EXIST C:\WINXT\SYSOLD.INI GOTO BAD
COPY /Y C:\WINXT\SYSOLD.INI C:\WINDOWS\SYSTEM.INI
IF ERRORLEVEL 1 GOTO BAD
IF EXIST C:\WIN.BAT DEL C:\WIN.BAT
ECHO Restored original Tandy Windows display. Type WIN as usual.
GOTO DONE
:BAD
ECHO Restore failed. Keep your verified source CF card.
:DONE
""")
TEST_NOTES = dos_text("""TANDY 1000 EX 320x200 16-COLOR EXPERIMENT (NOT HARDWARE VERIFIED)
Original verified Windows 3.0 and Windows 1.04 COM1 mouse retained.
At C:\\> type MTEST; Esc exits. Type WIN manually to test color.
Root WIN.BAT runs RESERVE.COM before invoking Windows real mode.
Never start WIN.COM directly from C:\\WINDOWS with this driver.
If reservation fails, Windows does not start.
To restore original 640x200 display, type C:\\WINXT\\RESTORE.
Your separate released known-good image has not been changed.
""")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("verified_image", type=Path)
    p.add_argument("display_driver", type=Path)
    p.add_argument("reserve_helper", type=Path)
    p.add_argument("font_directory", type=Path)
    p.add_argument("output_image", type=Path)
    a = p.parse_args()
    original_bytes = a.verified_image.read_bytes()
    if len(original_bytes) != CARD_BYTES or digest(original_bytes) != KNOWN_GOOD_SHA:
        raise ValueError("Input is not the EXACT known-good hardware image")
    sources = {
        "TR53216.DRV": (a.display_driver, DRIVER_SHA),
        "RESERVE.COM": (a.reserve_helper, RESERVE_SHA),
        "CGA.GR2": (a.font_directory/"CGA.GR2", "1fc24254a1b76c2030a0ae60e25a17d6df4730c2a99d293ca22886059d8be067"),
    }
    sources.update((name, (a.font_directory/name, sha)) for name, sha in FONT_SHAS.items())
    for name, (source, expected) in sources.items():
        content = source.read_bytes()
        if digest(content) != expected:
            raise ValueError(f"{name} does not match its expected SHA256")
    a.output_image.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a.verified_image, a.output_image)
    image = f"{a.output_image}@@{PARTITION_OFFSET}"

    def copy_in(source, destination):
        run("mcopy", "-o", "-i", image, str(source), "::" + destination)

    def read_back(dos_path):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "file.bin"
            run("mcopy", "-i", image, "::" + dos_path, str(out))
            return out.read_bytes()

    original_ini = read_back("/WINDOWS/SYSTEM.INI")
    original_auto = read_back("/AUTOEXEC.BAT")
    original_config = read_back("/CONFIG.SYS")
    original_mouse = read_back("/WINDOWS/SYSTEM/MSMOUSE1.DRV")
    original_video = read_back("/WINDOWS/SYSTEM/TANDYDSP.DRV")
    if b"CTMOUSE.EXE /S14 /M" not in original_auto.upper():
        raise ValueError("Known-good DOS mouse configuration missing")
    if b"mouse.drv=msmouse1.drv" not in original_ini.lower():
        raise ValueError("Known-good Windows mouse configuration missing")
    if b"display.drv=tandydsp.drv" not in original_ini.lower():
        raise ValueError("Known-good Tandy display configuration missing")

    run("mmd", "-i", image, "::/WINXT")
    with tempfile.TemporaryDirectory() as tmpdir:
        work = Path(tmpdir)
        outputs = {
            "/WINXT/SYSOLD.INI": original_ini,
            "/WINDOWS/SYSTEM.INI": boot_set(original_ini),
            "/WIN.BAT": LAUNCHER,
            "/WINXT/RESTORE.BAT": RESTORE,
            "/WINXT/TEST16.TXT": TEST_NOTES,
        }
        for path, payload in outputs.items():
            host = work / path.rsplit("/", 1)[-1]
            host.write_bytes(payload)
            copy_in(host, path)
            if read_back(path) != payload:
                raise ValueError(f"Read-back mismatch: {path}")
        for filename, (host, _) in sources.items():
            destination = ("/WINXT/" if filename == "RESERVE.COM" else "/WINDOWS/SYSTEM/") + filename
            copy_in(host, destination)
            if read_back(destination) != host.read_bytes():
                raise ValueError(f"Read-back mismatch: {destination}")
    if (read_back("/AUTOEXEC.BAT") != original_auto or
        read_back("/CONFIG.SYS") != original_config or
        read_back("/WINDOWS/SYSTEM/MSMOUSE1.DRV") != original_mouse or
        read_back("/WINDOWS/SYSTEM/TANDYDSP.DRV") != original_video):
        raise ValueError("Working DOS, mouse, or original graphics files were changed")
    result = a.output_image.read_bytes()
    if len(result) != CARD_BYTES:
        raise ValueError("Incorrect CF size")
    a.output_image.with_name(a.output_image.name+".sha256").write_text(
        f"{digest(result)}  {a.output_image.name}\n", encoding="ascii")
    print(f"Created 320x200x16 experiment: {a.output_image} ({len(result)} bytes)")
    print(f"SHA256: {digest(result)}")
    print("Verified: DOS CuteMouse, original Windows mouse and Tandy display unchanged.")
    print("Windows must be manually launched from C:\\> using guarded WIN.BAT.")


if __name__ == "__main__":
    main()
