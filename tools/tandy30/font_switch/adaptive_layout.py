#!/usr/bin/env python3
"""Fit Windows 3.0 Program Manager to each Tandy EX display profile.

Source: exact XR155+CGA-default CF image (already with fixed DOS switchers).
Creates fixed 320-wide or 640-wide PM/group window snapshots; DOS BAT scripts
copy the appropriate snapshot after selecting graphics + fonts. No Windows
program, driver, font, icon graphic, or boot logo is modified. All nine
switcher commands use the bundled DOS FC /B to validate written files.
"""
from pathlib import Path
import argparse, hashlib, shutil, subprocess, struct

EXPECTED_SHA="0b1f0986e7befb59f6f5ae53030a3d49725e137376234703bea5cb7ccb2ea3b3"
CARD_SIZE=31808*512
GROUPS=("MAIN","ACCESSOR","GAMES")
RECTS={
    "MAIN":(1,0,629,54),
    "ACCESSOR":(1,54,629,108),
    "GAMES":(1,108,629,162),
}
# The already tested MS-DOS 6.22 profile names are preserved as entry points.
MODES={
    "TANDY4":("T4XT.INI","WIN4.INI","4"),
    "T4XT":("T4XT.INI","WIN4.INI","4"),
    "T4CGA":("T4CGA.INI","WIN4.INI","4"),
    "T4EGA":("T4EGA.INI","WIN4.INI","4"),
    "FASTXY":("XRXT.INI","WINXR.INI","16"),
    "XRXT":("XRXT.INI","WINXR.INI","16"),
    "XRCGA":("XRCGA.INI","WINXR.INI","16"),
    "XREGA":("XREGA.INI","WINXR.INI","16"),
    "GOLDXY":("SYSHPXY.INI","WINXR.INI","16"),
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dosread(image,path,stage):
    out=stage/("READ_"+path.replace("/","_"))
    if out.exists():out.unlink()
    subprocess.run(["mcopy","-i",str(image)+"@@32256","::/"+path,str(out)],
                   check=True)
    return out.read_bytes()

def doswrite(image,path,data,stage):
    out=stage/("WRITE_"+path.replace("/","_"))
    out.write_bytes(data)
    subprocess.run(["mcopy","-o","-i",str(image)+"@@32256",str(out),"::/"+path],
                   check=True)
    assert dosread(image,path,stage)==data,("Readback mismatch",path)

def checksum_ok(data):
    padded=data+(b"\0" if len(data)&1 else b"")
    return sum(struct.unpack("<%dH"%(len(padded)//2),padded))%65536==0

def widen_group(original,name):
    if original[:4]!=b"PMCC" or not checksum_ok(original):
        raise ValueError(name+" invalid original PMCC header/checksum")
    if struct.unpack_from("<hhhh",original,10)[0:2]!=(1,RECTS[name][1]):
        raise ValueError("Unexpected original x/y for "+name)
    if struct.unpack_from("<hhhh",original,10)[2]!=309:
        raise ValueError("Unexpected 320 viewport group rectangle "+name)
    b=bytearray(original)
    struct.pack_into("<hhhh",b,10,*RECTS[name])
    struct.pack_into("<H",b,4,0)
    pad=bytes(b)+(b"\0" if len(b)&1 else b"")
    words=struct.unpack("<%dH"%(len(pad)//2),pad)
    struct.pack_into("<H",b,4,(-sum(words))&0xffff)
    updated=bytes(b)
    assert len(updated)==len(original)
    assert checksum_ok(updated)
    # Only the two changed bytes of right-hand window edge and checksum vary.
    allowed=set(range(4,6))|set(range(10,18))
    assert all(a==c for i,(a,c) in enumerate(zip(original,updated)) if i not in allowed)
    assert original[18:]==updated[18:], "Icon data must not change"
    print("GROUP",name,"wide rectangle",RECTS[name],"original",digest(original),"wide",digest(updated))
    return updated

def batch(name,config,win,flavor):
    pm="PM4.INI" if flavor=="4" else "PM16.INI"
    group_files={
        "MAIN.GRP":"M"+flavor+".GRP",
        "ACCESSOR.GRP":"A"+flavor+".GRP",
        "GAMES.GRP":"G"+flavor+".GRP",
    }
    copies=[
        ("C:\\TANDY88\\"+config,"C:\\WINDOWS\\SYSTEM.INI"),
        ("C:\\TANDY88\\"+win,"C:\\WINDOWS\\WIN.INI"),
        ("C:\\TANDY88\\"+pm,"C:\\WINDOWS\\PROGMAN.INI"),
    ] + [("C:\\TANDY88\\"+v,"C:\\WINDOWS\\"+k) for k,v in group_files.items()]
    lines=[
        "@ECHO OFF",
        "REM Set Windows display, fonts and desktop size together, DOS only.",
        "REM Each copied file is verified by DOS 6.22 FC /B.",
        "IF NOT EXIST C:\\DOS\\FC.EXE GOTO NOFC",
    ]
    lines += ["IF NOT EXIST "+src+" GOTO MISSING" for src,_ in copies]
    lines+=["ECHO Switching "+name+" profile ("+("640x200" if flavor=="4" else "320x200")+" view)..."]
    for src,dst in copies:
        lines +=[
            "COPY "+src+" "+dst,
            "C:\\DOS\\FC.EXE /B "+src+" "+dst+" > NUL",
            "IF ERRORLEVEL 1 GOTO BAD",
        ]
    lines += [
        "ECHO "+name+" selected, Program Manager windows resized. Type WIN.",
        "GOTO END",
        ":MISSING",
        "ECHO ERROR: Missing saved profile file in C:\\TANDY88.",
        "GOTO END",
        ":NOFC",
        "ECHO ERROR: C:\\DOS\\FC.EXE required for verified switching.",
        "GOTO END",
        ":BAD",
        "ECHO ERROR: Copy verification failed. Check the last COPY result.",
        "ECHO Do not start Windows until the profile is restored.",
        ":END",
    ]
    return ("\r\n".join(lines)+"\r\n").encode("ascii")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--staging",type=Path,required=True)
    a=ap.parse_args()
    raw=a.source.read_bytes()
    if len(raw)!=CARD_SIZE or digest(raw)!=EXPECTED_SHA:
        raise ValueError("Wrong preferred-XRCGA default image")
    if a.output.exists() or a.staging.exists():
        raise ValueError("Refusing to overwrite an existing output")
    a.staging.mkdir(parents=True)
    shutil.copyfile(a.source,a.output)
    pm16=dosread(a.output,"WINDOWS/PROGMAN.INI",a.staging)
    assert b"Window=0 0 316 196 1" in pm16
    assert b"AutoArrange=0" in pm16 and b"SaveSettings=0" in pm16
    pm4=pm16.replace(b"Window=0 0 316 196 1",b"Window=0 0 636 196 1")
    assert len(pm4)==len(pm16) and pm4.count(b"Window=0 0 636 196 1")==1
    doswrite(a.output,"TANDY88/PM16.INI",pm16,a.staging)
    doswrite(a.output,"TANDY88/PM4.INI",pm4,a.staging)
    for initial,base in (("MAIN","M"),("ACCESSOR","A"),("GAMES","G")):
        current=dosread(a.output,"WINDOWS/"+initial+".GRP",a.staging)
        four=widen_group(current,initial)
        doswrite(a.output,"TANDY88/"+base+"16.GRP",current,a.staging)
        doswrite(a.output,"TANDY88/"+base+"4.GRP",four,a.staging)
    # Keep original active XRCGA as default, and 16-bit switches restored.
    assert dosread(a.output,"WINDOWS/PROGMAN.INI",a.staging)==pm16
    assert dosread(a.output,"WINDOWS/SYSTEM.INI",a.staging)==dosread(a.output,"TANDY88/XRCGA.INI",a.staging)
    assert dosread(a.output,"WINDOWS/WIN.INI",a.staging)==dosread(a.output,"TANDY88/WINXR.INI",a.staging)
    for name,(sys,win,flavor) in MODES.items():
        data=batch(name,sys,win,flavor)
        if b"C:\\DOS\\FC.EXE /B" not in data:
            raise ValueError("Cannot switch without verification")
        doswrite(a.output,name+".BAT",data,a.staging)
        print("SWITCH",name,flavor,"size",len(data),"bytes")
    print("DONE",a.output,len(raw),digest(a.output.read_bytes()))
    print("Boot logo, all fonts, games, previous 320 layout and original images preserved")
if __name__=="__main__":
    main()
