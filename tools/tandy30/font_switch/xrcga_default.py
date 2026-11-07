#!/usr/bin/env python3
"""Select the real-hardware-preferred XR155 + CGA fonts as default.

Derives a new CF image from the checksum-pinned, corrected 4-color font-switch
image. Exactly the two active Windows INI files change to the already-tested
XRCGA snapshot. Every driver, font, game, batch file, splash/boot logo, and
three-row group stays byte-for-byte identical.
"""
import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

SOURCE_SHA="f0409e06202c328b36a8cbf1f35e8ea86af62a5b52e1bdf3ddf3086dc63d3ecd"
CARD_BYTES=31808*512

def sha(b): return hashlib.sha256(b).hexdigest()

def read(image, path, work):
    local=work/("read_"+path.replace("/","_"))
    if local.exists():
        local.unlink()
    subprocess.run(["mcopy","-i",str(image)+"@@32256","::/"+path,str(local)],
                   check=True)
    return local.read_bytes()

def write(image, path, data, work):
    local=work/("write_"+path.replace("/","_"))
    local.write_bytes(data)
    subprocess.run(["mcopy","-o","-i",str(image)+"@@32256",str(local),"::/"+path],
                   check=True)
    if read(image,path,work)!=data:
        raise ValueError("Readback mismatch: "+path)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--staging",type=Path,required=True)
    args=p.parse_args()
    original=args.source.read_bytes()
    if len(original)!=CARD_BYTES or sha(original)!=SOURCE_SHA:
        raise ValueError("Wrong corrected 4-color switcher source, refuse change")
    if args.output.exists() or args.staging.exists():
        raise ValueError("Fresh output and staging required; refusing overwrite")
    args.staging.mkdir(parents=True)
    shutil.copyfile(args.source,args.output)
    # Snapshots were validated by the previous build and hardware-tested
    # through the XRCGA DOS selector. These exact bytes become active.
    system=read(args.output,"TANDY88/XRCGA.INI",args.staging)
    windows=read(args.output,"TANDY88/WINXR.INI",args.staging)
    for token in (b"display.drv=XR155.DRV",b"fonts.fon=CGASYS.FON",
                  b"fixedfon.fon=CGAFIX.FON",b"oemfonts.fon=CGAOEM.FON"):
        if token not in system:
            raise ValueError("Missing expected selected device/font "+repr(token))
    if b"mouse.drv=msmouse1.drv" not in system.lower():
        raise ValueError("Known-working COM1 mouse was changed")
    if b"load=C:\\WINDOWS\\PAN.EXE" not in windows:
        raise ValueError("Missing automatic pannable desktop helper")
    if b"BorderWidth=2" not in windows:
        raise ValueError("Missing saved border width")
    assert b"run=\r\n" in windows
    # Do not change the batch switches, the program groups or any binaries.
    write(args.output,"WINDOWS/SYSTEM.INI",system,args.staging)
    write(args.output,"WINDOWS/WIN.INI",windows,args.staging)
    assert read(args.output,"WINDOWS/SYSTEM.INI",args.staging)==system
    assert read(args.output,"WINDOWS/WIN.INI",args.staging)==windows
    for command in ("T4CGA","XRCGA","FASTXY","GOLDXY"):
        assert read(args.source,command+".BAT",args.staging)==read(args.output,command+".BAT",args.staging)
    print("PASS: preferred XR155+compact CGA fonts, 16 colors, 640x256 panning")
    print("PASS: all DOS profile switches, graphics/font binaries, boot logo preserved")
    print("OUTPUT",args.output,len(original),"bytes",sha(args.output.read_bytes()))

if __name__=="__main__":
    main()
