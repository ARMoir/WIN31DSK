#!/usr/bin/env python3
"""Package three opt-in PIXMAX turbo variants without modifying baseline files.

Runs against the owner-approved color-corrected PIXMAX-default disk. Verifies
the SHA-256 of every existing file and protects boot, panning, layouts, icons,
fonts, mouse and DOS command switchers.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import struct
import sys

ORIGINAL_CARD_SHA="29881151baf820b3e6453ebb9c024828109abea111e01fe52555c61a840adf73"
ORIGINAL_PIXMAX_SHA="cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c"
CARD_BYTES=31808*512
NAMES={"PIXBURST":"burst","PIXV20":"v20","PIXDIRTY":"dirty"}

def sha(b):return hashlib.sha256(b).hexdigest()

def inventory(fs):
    files={}
    def walk(cluster=None,prefix=''):
        for _,name,attr,next_cluster,_ in fs.entries(cluster):
            if name in ('.','..'):continue
            p=prefix+'/'+name
            if attr & 16:walk(next_cluster,p)
            else:files[p]=sha(fs.read(p))
    walk()
    return files

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--package",type=Path,required=True)
    a=ap.parse_args()
    original=a.source.read_bytes()
    assert len(original)==CARD_BYTES and sha(original)==ORIGINAL_CARD_SHA, "Wrong verified PIXMAX default source"
    if a.output.exists():raise RuntimeError("Refusing to overwrite existing card")
    shutil.copyfile(a.source,a.output)
    staging=a.package/"stage-three"
    if staging.exists():raise RuntimeError("Refusing existing stage directory")
    staging.mkdir(parents=True)
    disk=str(a.output)+"@@32256"
    def get(path):
        dst=staging/("read_"+path.replace("/","_"))
        if dst.exists():dst.unlink()
        subprocess.run(["mcopy","-i",disk,"::/"+path,str(dst)],check=True)
        return dst.read_bytes()
    def put(path,data):
        src=staging/("write_"+path.replace("/","_"))
        src.write_bytes(data)
        subprocess.run(["mcopy","-o","-i",disk,str(src),"::/"+path],check=True)
        if get(path)!=data:raise RuntimeError("FAT16 roundtrip mismatch "+path)
    default=get("WINDOWS/SYSTEM.INI")
    assert default==get("TANDY88/PIXMAX.INI")
    assert default.count(b"display.drv=PIXMAX.DRV")==1
    assert b"fonts.fon=CGASYS.FON" in default
    assert b"mouse.drv=msmouse1.drv" in default.lower()
    assert sha(get("WINDOWS/SYSTEM/PIXMAX.DRV"))==ORIGINAL_PIXMAX_SHA
    selector=get("PIXMAX.BAT")
    assert selector.count(b"PIXMAX.INI")>=3
    assert selector.count(b"C:\\DOS\\FC.EXE /B")==6
    for name,mode in NAMES.items():
        driver=(a.package/(name+".DRV")).read_bytes()
        report=json.loads((a.package/(name+"_REPORT.json")).read_text())
        assert report["experimental_patch"]["variant"]==mode
        assert sha(driver)==report["sha256"]
        assert report["ne_gross_alloc_bytes"]<=130000
        if mode=="v20":
            assert report["V20_only_opcode_audit"]["shr_bl_4"]>=2
            assert report["V20_only_opcode_audit"]["shl_al_4"]>=2
        profile=default.replace(b"display.drv=PIXMAX.DRV",b"display.drv="+name.encode()+b".DRV")
        assert profile.count(b"display.drv="+name.encode()+b".DRV")==1
        script=selector.replace(b"PIXMAX.INI",name.encode()+b".INI").replace(b"PIXMAX",name.encode())
        assert script.count(b"C:\\DOS\\FC.EXE /B")==6
        assert script.count((name+".INI").encode())>=3
        assert b"C:\\WINDOWS\\PROGMAN.INI" in script
        put("WINDOWS/SYSTEM/"+name+".DRV",driver)
        put("TANDY88/"+name+".INI",profile)
        put(name+".BAT",script)
        print("ADDED",name,"size",len(driver),"NE minimum",report["ne_gross_alloc_bytes"])
    assert get("WINDOWS/SYSTEM.INI")==default
    assert get("DIBXY.BAT") and get("T4CGA.BAT")
    sys.path.insert(0,"tools/tandy30/int33-test")
    from fat16_image import Fat16
    old=Fat16(bytearray(original))
    new=Fat16(bytearray(a.output.read_bytes()))
    assert len(old.b)==len(new.b)==CARD_BYTES
    assert old.b[:old.part]==new.b[:new.part], "MBR/partition altered"
    fat_size=struct.unpack_from("<H",new.b,new.part+22)[0]*512
    assert new.b[new.fat:new.fat+fat_size]==new.b[new.fat+fat_size:new.fat+fat_size*2]
    original_files,newfiles=inventory(old),inventory(new)
    assert set(original_files)<=set(newfiles), "One or more original files removed"
    assert all(original_files[p]==newfiles[p] for p in original_files), "Some original file bytes changed"
    new_names=set(newfiles)-set(original_files)
    desired={"/"+name+".BAT" for name in NAMES}
    desired|={"/TANDY88/"+name+".INI" for name in NAMES}
    desired|={"/WINDOWS/SYSTEM/"+name+".DRV" for name in NAMES}
    assert new_names==desired,(new_names,desired)
    assert new.read("/WINDOWS/SYSTEM.INI")==old.read("/WINDOWS/SYSTEM.INI")
    assert new.read("/WINDOWS/SYSTEM/PIXMAX.DRV")==old.read("/WINDOWS/SYSTEM/PIXMAX.DRV")
    for p in ("/WIN.BAT","/AUTOEXEC.BAT","/CONFIG.SYS","/DIBXY.BAT",
              "/T4CGA.BAT","/PIXMAX.BAT","/WINDOWS/WIN.INI",
              "/WINDOWS/PROGMAN.INI","/WINDOWS/MAIN.GRP",
              "/WINDOWS/ACCESSOR.GRP","/WINDOWS/GAMES.GRP",
              "/WINDOWS/SYSTEM/TANDYDSP.DRV","/WINDOWS/SYSTEM/MSMOUSE1.DRV",
              "/WINDOWS/SYSTEM/CGASYS.FON","/WINDOWS/PAN.EXE"):
        assert new.read(p)==old.read(p),p
    assert b"WIN.COM /R" in new.read("/WIN.BAT").upper()
    assert b"RESERVE.COM" in new.read("/WIN.BAT").upper()
    print("PASS",len(original_files),"existing files all original SHA-256, only nine experiment files added")
    print("PASS PIXMAX 16-color default and original I-R-G-B palette, icon groups, boot logo, mouse, panning and T4CGA unchanged")
    print("CAUTION PIXV20 uses NEC V20-only 80186 opcodes and MUST NOT be run on a plain Intel 8088/8086")
    result=sha(a.output.read_bytes())
    (a.output.parent/(a.output.name+".sha256")).write_text(result+"  "+a.output.name+"\n")
    print("CF",a.output,len(original),"SHA256",result)

if __name__=="__main__":main()
