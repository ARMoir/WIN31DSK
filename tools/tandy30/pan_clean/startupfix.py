#!/usr/bin/env python3
"""Reversible Windows 3.0 PAN foreground startup fix + border 2.

Offline, on a copy of the owner's hardware-tested panning CF image. Only
WINDOWS/WIN.INI and TANDY88/WINPAN.INI are edited, same lengths as originals.
Original RRECT rollback snapshots, Program Manager executable and every .GRP file stay intact.
"""
from pathlib import Path
import argparse, hashlib, re, shutil, subprocess

EXPECTED_SHA="4f73b9c37a9d8b2dfbe12574a3cb7925c09f639e59945986a310c6aa81b22484"
IMAGE_BYTES=31808*512

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(image, name, staging):
    local=staging/name.split("/")[-1]
    if local.exists():local.unlink()
    subprocess.run(["mcopy","-i",str(image)+"@@32256","::/"+name,str(local)],check=True)
    return local.read_bytes()

def write(image, name, local):
    subprocess.run(["mcopy","-o","-i",str(image)+"@@32256",str(local),"::/"+name],check=True)

def modify(raw):
    assert b"\r\n" in raw, "Expected DOS line endings"
    # Verify these keys are in [windows] rather than simply matching another section.
    active=False
    seen={"load":0,"run":0,"borderwidth":0}
    parts=[]
    for line in raw.splitlines(keepends=True):
        stripped=line.strip()
        if stripped.startswith(b"[") and stripped.endswith(b"]"):
            active=stripped.lower()==b"[windows]"
        if active:
            m=re.match(rb"^([A-Za-z]+)\s*=(.*?)(\r?\n)?$",line)
            if m:
                key=m.group(1).decode("ascii").lower()
                if key in seen:
                    seen[key]+=1
                    val=m.group(2).strip()
                    if key=="load":
                        assert not val, "Unexpected existing load="
                        line=b"load=C:\\WINDOWS\\PAN.EXE\r\n"
                    elif key=="run":
                        assert val.upper()==b"C:\\WINDOWS\\PAN.EXE", "Unexpected run="
                        line=b"run=\r\n"
                    else:
                        assert val==b"1", "Unexpected BorderWidth"
                        line=b"BorderWidth=2\r\n"
        parts.append(line)
    assert seen=={"load":1,"run":1,"borderwidth":1},seen
    result=b"".join(parts)
    # PAN.exe has moved from run to load; same total string length.
    assert len(result)==len(raw),(len(result),len(raw))
    assert result.count(b"C:\\WINDOWS\\PAN.EXE")==1
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--staging",type=Path,required=True)
    a=p.parse_args()
    original=a.source.read_bytes()
    assert len(original)==IMAGE_BYTES and sha(original)==EXPECTED_SHA
    assert not a.output.exists()
    a.staging.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(a.source,a.output)
    old=read(a.output,"WINDOWS/WIN.INI",a.staging)
    pan=read(a.output,"TANDY88/WINPAN.INI",a.staging)
    assert old==pan,"Current startup INI and PANON snapshot differ"
    fixed=modify(old)
    update=a.staging/"FIXED.INI"
    update.write_bytes(fixed)
    write(a.output,"WINDOWS/WIN.INI",update)
    write(a.output,"TANDY88/WINPAN.INI",update)
    assert read(a.output,"WINDOWS/WIN.INI",a.staging)==fixed
    assert read(a.output,"TANDY88/WINPAN.INI",a.staging)==fixed
    # Fit Program Manager's normal window into the initial physical
    # 320x200 viewport. Preserve group paths and every .GRP byte.
    old_pm=read(a.output,"WINDOWS/PROGMAN.INI",a.staging)
    saved_pm=read(a.output,"TANDY88/PRGPAN.INI",a.staging)
    assert old_pm==saved_pm,"PANON Program Manager snapshot disagrees with active config"
    assert old_pm.count(b"Window=0 0 640 256 3")==1
    updated_pm=old_pm.replace(b"Window=0 0 640 256 3",b"Window=0 0 316 196 1")
    assert len(updated_pm)==len(old_pm)
    for entry in [b"MAIN.GRP",b"ACCESSOR.GRP",b"GAMES.GRP",b"AutoArrange=1",b"MinOnRun=0"]:
        assert entry in updated_pm,entry
    pm_path=a.staging/"FIXPM.INI"
    pm_path.write_bytes(updated_pm)
    write(a.output,"WINDOWS/PROGMAN.INI",pm_path)
    write(a.output,"TANDY88/PRGPAN.INI",pm_path)
    assert read(a.output,"WINDOWS/PROGMAN.INI",a.staging)==updated_pm
    assert read(a.output,"TANDY88/PRGPAN.INI",a.staging)==updated_pm
    print("PASS: background panning, BorderWidth=2, Program Manager normal 316x196 viewport-sized window:",str(a.output),sha(a.output.read_bytes()))

if __name__=="__main__":
    main()
