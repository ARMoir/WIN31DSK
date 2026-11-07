#!/usr/bin/env python3
"""Produce reversible 4-color and 16-color Tandy EX graphics/font choices.

Input is the exact pinned XR155 CF candidate. All driver and font binary bytes
are preserved; only SYSTEM.INI and WIN.INI are selected and DOS snapshots/scripts
are added. Confirm original Microsoft TANDYDSP.DRV against initial mouse image.
"""
from pathlib import Path
import argparse, hashlib, subprocess, shutil, re

XR_IMAGE_SHA="0f0238cce3e63182a7da06c5302de45435e03f7911399fdeb0559e8343cf412b"
MOUSE_IMAGE_SHA="eca08b0eb4283854bfef71d98d8febe08ad8de89eb3d52a109a0b9d39993fa34"
ORIGINAL_TANDY_SHA="d593c03e52e338074df3c5c70973197bc61deeb72d615459ad90124afea126e0"
IMAGE_BYTES=31808*512

FONT_SETS={
    "XT":("XTCSYS.FON","XTCFIX.FON","XTCOEM.FON"),
    "CGA":("CGASYS.FON","CGAFIX.FON","CGAOEM.FON"),
    "EGA":("EGASYS.FON","EGAFIX.FON","EGAOEM.FON"),
}
# Convenient DOS commands; every configuration uses a separate snapshot.
CHOICES={
    "TANDY4":("TANDYDSP.DRV","XT"),  # Exactly what the user wants to try first
    "T4XT":("TANDYDSP.DRV","XT"),
    "T4CGA":("TANDYDSP.DRV","CGA"),
    "T4EGA":("TANDYDSP.DRV","EGA"),
    "XRXT":("XR155.DRV","XT"),
    "XRCGA":("XR155.DRV","CGA"),
    "XREGA":("XR155.DRV","EGA"),
}
SNAPSHOTS={
    ("TANDYDSP.DRV","XT"):"T4XT.INI",
    ("TANDYDSP.DRV","CGA"):"T4CGA.INI",
    ("TANDYDSP.DRV","EGA"):"T4EGA.INI",
    ("XR155.DRV","XT"):"XRXT.INI",
    ("XR155.DRV","CGA"):"XRCGA.INI",
    ("XR155.DRV","EGA"):"XREGA.INI",
}

def sha(b):return hashlib.sha256(b).hexdigest()
def cp_read(image,guest,out):
    target=out/("READ_"+guest.replace("/","_"))
    if target.exists():target.unlink()
    subprocess.run(["mcopy","-i",str(image)+"@@32256","::/"+guest,str(target)],check=True)
    return target.read_bytes()
def cp_write(image,guest,data,out):
    target=out/("WRITE_"+guest.replace("/","_"))
    target.write_bytes(data)
    subprocess.run(["mcopy","-o","-i",str(image)+"@@32256",str(target),"::/"+guest],check=True)
    if cp_read(image,guest,out)!=data:raise ValueError("Readback changed: "+guest)

def ini_update(data,assignments):
    lines=data.splitlines(keepends=True)
    section=None
    seen={k:0 for k in assignments}
    result=[]
    for line in lines:
        line_strip=line.strip()
        if line_strip.startswith(b"[") and line_strip.endswith(b"]"):
            section=line_strip.lower().decode("ascii")
        m=re.match(rb"(?i)^([a-z0-9_.]+)\s*=(.*?)(\r?\n)?$",line)
        if m and section=="[boot]":
            k=m.group(1).decode("ascii").lower()
            if k in assignments:
                eol=b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
                line=k.encode()+b"="+assignments[k].encode()+eol
                seen[k]+=1
        result.append(line)
    if any(v!=1 for v in seen.values()):raise ValueError("Unexpected boot ini keys: "+str(seen))
    return b"".join(result)

def win_no_pan(raw):
    active=False
    seen=0
    lines=[]
    for line in raw.splitlines(keepends=True):
        t=line.strip()
        if t.startswith(b"[") and t.endswith(b"]"):
            active=t.lower()==b"[windows]"
        if active and line.lower().startswith(b"load="):
            if line.strip().upper()!=b"LOAD=C:\\WINDOWS\\PAN.EXE":
                raise ValueError("Unexpected PAN startup")
            line=b"load=\r\n"
            seen+=1
        lines.append(line)
    if seen!=1:raise ValueError("Expected one load=PAN.EXE")
    return b"".join(lines)

def make_switch(name,profile,win_snapshot):
    output=[
        "@ECHO OFF",
        "REM Run at DOS prompt only, after Windows has exited.",
        "REM Does not replace any EXE, DRV, FON, Windows logo, or games.",
        "COPY C:\\TANDY88\\"+profile+" C:\\WINDOWS\\SYSTEM.INI > NUL",
        "IF ERRORLEVEL 1 GOTO FAILED",
        "COPY C:\\TANDY88\\"+win_snapshot+" C:\\WINDOWS\\WIN.INI > NUL",
        "IF ERRORLEVEL 1 GOTO FAILED",
        "ECHO "+name+" graphics and font profile selected.",
        "ECHO Type WIN to start Windows.",
        "GOTO END",
        ":FAILED",
        "ECHO ERROR: Cannot switch Windows config. Check both INI files.",
        ":END"
    ]
    return ("\r\n".join(output)+"\r\n").encode("ascii")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--mouse-original",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--staging",type=Path,required=True)
    a=parser.parse_args()
    image=a.source.read_bytes()
    original=a.mouse_original.read_bytes()
    if len(image)!=IMAGE_BYTES or sha(image)!=XR_IMAGE_SHA:raise ValueError("Source is not XR155 test")
    if len(original)!=IMAGE_BYTES or sha(original)!=MOUSE_IMAGE_SHA:raise ValueError("Original mouse image mismatch")
    if a.out.exists() or a.staging.exists():raise ValueError("Do not overwrite existing build")
    a.staging.mkdir(parents=True)
    shutil.copyfile(a.source,a.out)

    old_tandy=cp_read(a.mouse_original,"WINDOWS/SYSTEM/TANDYDSP.DRV",a.staging)
    test_tandy=cp_read(a.out,"WINDOWS/SYSTEM/TANDYDSP.DRV",a.staging)
    if sha(old_tandy)!=ORIGINAL_TANDY_SHA or old_tandy!=test_tandy:
        raise ValueError("Original Microsoft 4-color Tandy driver is NOT byte-for-byte intact")
    print("PASS Original TANDYDSP.DRV",len(test_tandy),sha(test_tandy))
    for fset in FONT_SETS.values():
        for fname in fset:
            b=cp_read(a.out,"WINDOWS/SYSTEM/"+fname,a.staging)
            if len(b)<1000:raise ValueError("Missing font "+fname)
            print("FONT",fname,len(b),sha(b))
    sysini=cp_read(a.out,"WINDOWS/SYSTEM.INI",a.staging)
    winini=cp_read(a.out,"WINDOWS/WIN.INI",a.staging)
    if not (b"display.drv=XR155.DRV" in sysini and b"fonts.fon=XTCSYS.FON" in sysini):
        raise ValueError("Unexpected XR155 default or fonts")
    win4=win_no_pan(winini)
    assert b"BorderWidth=2" in win4 and b"run=\r\n" in win4
    # Only the TANDY4 non-panning mode suppresses PAN.EXE startup.
    cp_write(a.out,"TANDY88/WIN4.INI",win4,a.staging)
    cp_write(a.out,"TANDY88/WINXR.INI",winini,a.staging)

    for (driver,flavor),filename in SNAPSHOTS.items():
        s,f,o=FONT_SETS[flavor]
        cfg=ini_update(sysini,{
            "display.drv":driver,
            "fonts.fon":s,
            "fixedfon.fon":f,
            "oemfonts.fon":o,
        })
        if b"mouse.drv=msmouse1.drv" not in cfg.lower():
            raise ValueError("Accidental mouse change")
        cp_write(a.out,"TANDY88/"+filename,cfg,a.staging)
    for name,(driver,flavor) in CHOICES.items():
        snapshot=SNAPSHOTS[(driver,flavor)]
        switchwin="WIN4.INI" if driver=="TANDYDSP.DRV" else "WINXR.INI"
        cp_write(a.out,name+".BAT",make_switch(name,snapshot,switchwin),a.staging)
    # Existing FASTXY/GOLDXY commands must also restore WIN.INI after
    # a fixed Tandy 4-color session (which disables the PAN startup helper).
    cp_write(a.out,"FASTXY.BAT",
             make_switch("FASTXY","XRXT.INI","WINXR.INI"),a.staging)
    cp_write(a.out,"GOLDXY.BAT",
             make_switch("GOLDXY","SYSHPXY.INI","WINXR.INI"),a.staging)
    # First boot into original TANDYDSP with modern fonts, as requested.
    t4=cp_read(a.out,"TANDY88/T4XT.INI",a.staging)
    cp_write(a.out,"WINDOWS/SYSTEM.INI",t4,a.staging)
    cp_write(a.out,"WINDOWS/WIN.INI",win4,a.staging)
    assert cp_read(a.out,"WINDOWS/SYSTEM/TANDYDSP.DRV",a.staging)==old_tandy
    print("PASS: TANDY4 640x200 4 colors with modern XT bitmap fonts selected")
    print("PASS: Boot logo, Windows programs, existing panning/driver files unchanged")
    print("IMAGE",a.out,len(image),sha(a.out.read_bytes()))

if __name__=="__main__":
    main()
