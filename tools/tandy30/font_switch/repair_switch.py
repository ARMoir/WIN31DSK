#!/usr/bin/env python3
"""Repair DOS 6.x switch scripts with explicit FC.EXE byte verification.

Original 4-color test image is immutable. This repair changes nine BAT
switches only. COPY in MS-DOS does not reliably replace inherited ERRORLEVEL;
a separate FC.EXE /B comparison returns the real result.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess

INPUT_SHA="9d2451f83baa313d6f96078a39c4969ca236401d52ca7a7e440318403db97b86"
CAPACITY=31808*512
SWITCHES={
  "TANDY4":("T4XT.INI","WIN4.INI"),
  "T4XT":("T4XT.INI","WIN4.INI"),
  "T4CGA":("T4CGA.INI","WIN4.INI"),
  "T4EGA":("T4EGA.INI","WIN4.INI"),
  "XRXT":("XRXT.INI","WINXR.INI"),
  "XRCGA":("XRCGA.INI","WINXR.INI"),
  "XREGA":("XREGA.INI","WINXR.INI"),
  "FASTXY":("XRXT.INI","WINXR.INI"),
  "GOLDXY":("SYSHPXY.INI","WINXR.INI"),
}
def digest(b):return hashlib.sha256(b).hexdigest()

def make(name,system,win):
    sys_src="C:\\TANDY88\\"+system
    win_src="C:\\TANDY88\\"+win
    lines=[
      "@ECHO OFF",
      "REM DOS-only display/font switch. Run outside Windows.",
      "REM No drivers, fonts, programs or boot logo are changed.",
      "IF NOT EXIST "+sys_src+" GOTO MISSING",
      "IF NOT EXIST "+win_src+" GOTO MISSING",
      "IF NOT EXIST C:\\DOS\\FC.EXE GOTO NOFC",
      "ECHO Selecting "+name+" ...",
      "COPY "+sys_src+" C:\\WINDOWS\\SYSTEM.INI",
      "C:\\DOS\\FC.EXE /B "+sys_src+" C:\\WINDOWS\\SYSTEM.INI > NUL",
      "IF ERRORLEVEL 1 GOTO BADSYS",
      "COPY "+win_src+" C:\\WINDOWS\\WIN.INI",
      "C:\\DOS\\FC.EXE /B "+win_src+" C:\\WINDOWS\\WIN.INI > NUL",
      "IF ERRORLEVEL 1 GOTO BADWIN",
      "ECHO Success: "+name+" selected. Type WIN.",
      "GOTO END",
      ":MISSING",
      "ECHO ERROR: Missing a saved INI file in C:\\TANDY88.",
      "GOTO END",
      ":NOFC",
      "ECHO ERROR: C:\\DOS\\FC.EXE is missing. No files changed.",
      "GOTO END",
      ":BADSYS",
      "ECHO ERROR: SYSTEM.INI did not match the selected profile.",
      "ECHO Check COPY output; do not start Windows until fixed.",
      "GOTO END",
      ":BADWIN",
      "ECHO ERROR: WIN.INI did not match the selected profile.",
      "ECHO Check COPY output; do not start Windows until fixed.",
      ":END",
    ]
    return ("\r\n".join(lines)+"\r\n").encode("ascii")

def mread(image,path,stage):
    target=stage/("R_"+path.replace("/","_"))
    if target.exists():target.unlink()
    subprocess.run(["mcopy","-i",str(image)+"@@32256","::/"+path,str(target)],check=True)
    return target.read_bytes()
def mwrite(image,path,blob,stage):
    temp=stage/("W_"+path.replace("/","_"))
    temp.write_bytes(blob)
    subprocess.run(["mcopy","-o","-i",str(image)+"@@32256",str(temp),"::/"+path],check=True)
    assert mread(image,path,stage)==blob

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    a=p.parse_args()
    inp=a.source.read_bytes()
    if len(inp)!=CAPACITY or digest(inp)!=INPUT_SHA:
        raise ValueError("Wrong source CF image, refusing repair")
    if a.output.exists() or a.stage.exists():
        raise ValueError("Fresh output and staging required")
    a.stage.mkdir(parents=True)
    shutil.copyfile(a.source,a.output)
    for name,(system,win) in SWITCHES.items():
        before=mread(a.output,name+".BAT",a.stage)
        assert b"IF ERRORLEVEL 1 GOTO FAILED" in before,("Unexpected original script",name)
        for snapshot in (system,win):
            assert mread(a.output,"TANDY88/"+snapshot,a.stage)
        new=make(name,system,win)
        mwrite(a.output,name+".BAT",new,a.stage)
        print("REPAIR",name,len(before),"->",len(new),"bytes",digest(new))
    assert mread(a.output,"WINDOWS/WIN.INI",a.stage)==mread(a.source,"WINDOWS/WIN.INI",a.stage)
    assert mread(a.output,"WINDOWS/SYSTEM.INI",a.stage)==mread(a.source,"WINDOWS/SYSTEM.INI",a.stage)
    print("FINAL",a.output,a.output.stat().st_size,digest(a.output.read_bytes()))
    print("Original BIOS/DOS boot, Windows boot logo, all EXE/COM/DRV/FON, groups, INIs untouched")

if __name__=="__main__":main()
