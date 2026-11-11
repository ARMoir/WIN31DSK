#!/usr/bin/env python3
"""Build exact three-mode Tandy EX Windows 3.0 CF from owner-tested sources.

1. T4CGA: original Microsoft four-color TANDYDSP.DRV 640x200.
2. NOPAN16: physical-hardware-verified TRIAL7 TR73216.DRV 320x200x16;
            EGA fonts and NO PAN.EXE at startup.
3. PIXMAX: physical-hardware-verified correct-color PIXMAX.DRV 16-color,
            320x200 viewport of 640x256 logical panning desktop, DEFAULT.

Deletes obsolete experimental selector BATs, display drivers, staging profiles,
older no-longer-selected fonts and pan-control experiments. Does not remove
any of the user's Windows apps, games, shortcuts, mouse or Windows boot logo.
All surviving original files must match the pinned input byte-for-byte except
active INI files if intentionally changed (this build leaves active ones alone).

The original releases and source disks are immutable.
"""
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,"tools/tandy30/int33-test")
from fat16_image import Fat16

PIXMAX_IMAGE_SHA="29881151baf820b3e6453ebb9c024828109abea111e01fe52555c61a840adf73"
TRIAL7_IMAGE_SHA="73129da6ca249120ee7bb1902b6da6b31eca40753dabe2fcc2a8220372574774"
TRIAL7_DRIVER_SHA="f922f12168de69ec2f8a761ce7fce2cbe2080b9e3fcfb06e3a3dac4faba6d502"
PIXMAX_DRIVER_SHA="cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c"
TANDY4_DRIVER_SHA="d593c03e52e338074df3c5c70973197bc61deeb72d615459ad90124afea126e0"
WIN_LAUNCHER_SHA="8e40254d0aa31687a45bedea4b7cd7c66a8293893138d59ebaa5ffc166b04935"

ROOT_SWITCHES={
    "SETUP16.BAT","REST05.BAT","REST5.BAT","USETR7.BAT",
    "USER8.BAT","REST7.BAT","PANOFF.BAT","PANON.BAT","PANHELP.TXT",
    "FASTXY.BAT","GOLDXY.BAT","TANDY4.BAT","T4XT.BAT","T4EGA.BAT",
    "XRXT.BAT","XRCGA.BAT","XREGA.BAT","DIBXY.BAT","PIXFAST.BAT",
    # Defensive: any older optional experiment selectors.
    "REPIX.BAT","PIXBURST.BAT","PIXV20.BAT","PIXDIRTY.BAT",
    "FAST4K.BAT","MAX8K.BAT","BURST4K.BAT"
}
KEEP_ROOT_SWITCHES={"PIXMAX.BAT","T4CGA.BAT","NOPAN16.BAT"}
KEEP_TANDY88={
    "PIXMAX.INI","T4CGA.INI","NOPAN16.INI",
    "WINXR.INI","WIN4.INI","WINNP.INI",
    "PM16.INI","PM4.INI",
    "M16.GRP","M4.GRP","A16.GRP","A4.GRP","G16.GRP","G4.GRP"
}
KEEP_WINXT={"RESERVE.COM","TGA3.COM"}
DROP_DISPLAY={
    "TR53216.DRV","TANDY88.DRV","RR8.DRV","HPXY.DRV",
    "XR155.DRV","XDIB.DRV","PIXFAST.DRV","RPAINT.DRV",
    "PIXV20.DRV","PIXBURST.DRV","PIXDIRTY.DRV",
    "FAST4K.DRV","MAX8K.DRV","BURST4K.DRV"
}
KEEP_DISPLAY={"TR73216.DRV","PIXMAX.DRV","TANDYDSP.DRV"}
DROP_FONT={"XTESYS.FON","XTEFIX.FON","XTEOEM.FON",
           "XTCSYS.FON","XTCFIX.FON","XTCOEM.FON"}
DROP_WINDOWS={"XTPAN.EXE","XYCTL.EXE","PANCTL.EXE","CGACTL.EXE"}
EXPECTED_ORIGINAL_FILES=426
IMAGE_BYTES=31808*512

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def files(fs):
    out={}
    def walk(directory=None,prefix=""):
        for _,name,attr,cluster,_size in fs.entries(directory):
            if name in (".",".."):continue
            p=prefix+"/"+name
            if attr&16:walk(cluster,p)
            else:out[p]=digest(fs.read(p))
    walk()
    return out

def choose_removals(original):
    removed=set()
    for path in original:
        parent,filename=path.rsplit("/",1)
        if parent=="" and filename in ROOT_SWITCHES:
            removed.add(path)
        elif parent=="/TANDY88" and filename not in KEEP_TANDY88:
            removed.add(path)
        elif parent=="/WINXT" and filename not in KEEP_WINXT:
            removed.add(path)
        elif parent=="/WINDOWS/SYSTEM" and (filename in DROP_DISPLAY or filename in DROP_FONT):
            removed.add(path)
        elif parent=="/WINDOWS" and filename in DROP_WINDOWS:
            removed.add(path)
    if "/WINDOWS/SYSTEM/PIXMAX.DRV" in removed or "/WINXT/RESERVE.COM" in removed:
        raise RuntimeError("Protected file wrongly classified")
    # No unrecognized experimental display modes may survive.
    for path in original:
        if path in removed:continue
        if path.rsplit("/",1)[0]=="" and path.endswith(".BAT"):
            if path not in {"/WIN.BAT","/AUTOEXEC.BAT","/PIXMAX.BAT","/T4CGA.BAT"}:
                raise RuntimeError("Unrecognized root BAT left behind: "+path)
    return removed

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pixmax",type=Path,required=True)
    ap.add_argument("--trial7",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    opts=ap.parse_args()
    raw=opts.pixmax.read_bytes()
    old7=opts.trial7.read_bytes()
    if len(raw)!=IMAGE_BYTES or digest(raw)!=PIXMAX_IMAGE_SHA:
        raise RuntimeError("Unexpected owner-tested PIXMAX source")
    if len(old7)!=IMAGE_BYTES or digest(old7)!=TRIAL7_IMAGE_SHA:
        raise RuntimeError("Unexpected owner-tested TRIAL7 source")
    if opts.output.exists():
        raise RuntimeError("Refusing overwrite of existing image")
    old=Fat16(bytearray(raw))
    t7=Fat16(bytearray(old7))
    originals=files(old)
    if len(originals)!=EXPECTED_ORIGINAL_FILES:raise RuntimeError("Unexpected base inventory size")
    # Verify actual native no-panning TRIAL7 binary in both original images.
    tr7b=old.read("/WINDOWS/SYSTEM/TR73216.DRV")
    assert tr7b==t7.read("/WINDOWS/SYSTEM/TR73216.DRV")
    assert digest(tr7b)==TRIAL7_DRIVER_SHA
    assert digest(old.read("/WINDOWS/SYSTEM/PIXMAX.DRV"))==PIXMAX_DRIVER_SHA
    assert digest(old.read("/WINDOWS/SYSTEM/TANDYDSP.DRV"))==TANDY4_DRIVER_SHA
    assert digest(old.read("/WIN.BAT"))==WIN_LAUNCHER_SHA
    assert old.read("/TANDY88/SYS7.INI")==t7.read("/TANDY88/SYS7.INI")
    np_ini=old.read("/TANDY88/SYS7.INI")
    assert np_ini.count(b"display.drv=TR73216.DRV")==1
    for kind in (b"EGAFIX.FON",b"EGAOEM.FON",b"EGASYS.FON"):
        assert kind in np_ini
    assert b"mouse.drv=msmouse1.drv" in np_ini.lower()
    assert b"display.drv=PIXMAX.DRV" in old.read("/TANDY88/PIXMAX.INI")
    assert b"display.drv=TANDYDSP.DRV" in old.read("/TANDY88/T4CGA.INI")
    # Save 3 new files before deleting old source SYS7.INI.
    winxr=old.read("/TANDY88/WINXR.INI")
    assert winxr.count(b"load=C:\\WINDOWS\\PAN.EXE")==1
    win_np=winxr.replace(b"load=C:\\WINDOWS\\PAN.EXE",b"load=")
    assert b"PAN.EXE" not in win_np.upper()
    assert b"BorderWidth=2" in win_np
    # Exact six-file verified profile switch. Change only the graphics
    # profile, WIN.INI layout, selector text. Keep PM16 3-row group files.
    select=old.read("/PIXMAX.BAT")
    assert select.count(b"C:\\DOS\\FC.EXE /B")==6
    assert select.count(b"PIXMAX.INI")>=3
    assert select.count(b"WINXR.INI")>=3
    np_switch=select.replace(b"PIXMAX.INI",b"NOPAN16.INI")
    np_switch=np_switch.replace(b"WINXR.INI",b"WINNP.INI")
    np_switch=np_switch.replace(b"PIXMAX",b"NOPAN16")
    np_switch=np_switch.replace(b"profile (320x200 view)",
       b"profile (320x200 native, no panning)")
    assert np_switch.count(b"C:\\DOS\\FC.EXE /B")==6
    assert np_switch.count(b"NOPAN16.INI")>=3
    assert np_switch.count(b"WINNP.INI")>=3
    assert b"PM16.INI" in np_switch
    assert b"WIN.COM" not in np_switch
    assert b"PAN.EXE" not in np_switch.upper()
    # PIXMAX and T4CGA retain their exact tested selectors.
    assert old.read("/TANDY88/PIXMAX.INI")==old.read("/WINDOWS/SYSTEM.INI")
    assert b"PAN.EXE" in old.read("/TANDY88/WINXR.INI")
    assert b"PAN.EXE" not in old.read("/TANDY88/WIN4.INI").upper()
    shutil.copyfile(opts.pixmax,opts.output)
    disk=str(opts.output)+"@@32256"
    tmp=opts.output.parent/"clean-stage"
    if tmp.exists():raise RuntimeError("Refuse existing build stage")
    tmp.mkdir(parents=True)
    def get(path):
        dest=tmp/("get_"+path.strip("/").replace("/","_"))
        if dest.exists():dest.unlink()
        subprocess.run(["mcopy","-i",disk,"::"+path,str(dest)],check=True)
        return dest.read_bytes()
    def put(path,data):
        dest=tmp/("put_"+path.strip("/").replace("/","_"))
        dest.write_bytes(data)
        subprocess.run(["mcopy","-o","-i",disk,str(dest),"::"+path],check=True)
        if get(path)!=data:raise RuntimeError("Cannot verify new file "+path)
    # Remove obsolete display experiments without removing any user apps.
    deletions=choose_removals(originals)
    for path in sorted(deletions):
        subprocess.run(["mdel","-i",disk,"::"+path],check=True,stdout=subprocess.DEVNULL)
    put("/TANDY88/NOPAN16.INI",np_ini)
    put("/TANDY88/WINNP.INI",win_np)
    put("/NOPAN16.BAT",np_switch)
    output=Fat16(bytearray(opts.output.read_bytes()))
    actual=files(output)
    add={"/TANDY88/NOPAN16.INI","/TANDY88/WINNP.INI","/NOPAN16.BAT"}
    assert set(originals)-set(actual)==deletions
    assert set(actual)-set(originals)==add, (set(actual)-set(originals),add)
    modified=[p for p in set(originals)&set(actual) if originals[p]!=actual[p]]
    if modified:raise RuntimeError("Original files modified: "+repr(modified))
    for path in ("/WIN.BAT","/AUTOEXEC.BAT","/CONFIG.SYS",
                 "/WINDOWS/SYSTEM/PIXMAX.DRV","/WINDOWS/SYSTEM/TR73216.DRV",
                 "/WINDOWS/SYSTEM/TANDYDSP.DRV","/WINDOWS/SYSTEM/MSMOUSE1.DRV",
                 "/WINDOWS/SYSTEM/CGASYS.FON","/WINDOWS/SYSTEM/EGASYS.FON",
                 "/WINDOWS/SYSTEM/TNDYLOGO.RLE","/WINDOWS/PAN.EXE",
                 "/WINDOWS/WIN.INI","/WINDOWS/SYSTEM.INI",
                 "/WINDOWS/PROGMAN.INI","/WINDOWS/MAIN.GRP",
                 "/WINDOWS/ACCESSOR.GRP","/WINDOWS/GAMES.GRP",
                 "/WINXT/RESERVE.COM","/WINXT/TGA3.COM",
                 "/PIXMAX.BAT","/T4CGA.BAT",
                 "/TANDY88/PIXMAX.INI","/TANDY88/T4CGA.INI",
                 "/TANDY88/WINXR.INI","/TANDY88/WIN4.INI",
                 "/TANDY88/PM16.INI","/TANDY88/PM4.INI"):
        assert actual[path]==originals[path],path
    assert output.read("/WINDOWS/SYSTEM.INI")==output.read("/TANDY88/PIXMAX.INI")
    assert output.read("/WINDOWS/WIN.INI")==output.read("/TANDY88/WINXR.INI")
    assert output.read("/TANDY88/NOPAN16.INI")==t7.read("/TANDY88/SYS7.INI")
    assert output.read("/TANDY88/WINNP.INI")==win_np
    assert output.read("/NOPAN16.BAT")==np_switch
    assert output.read("/PIXMAX.BAT")==old.read("/PIXMAX.BAT")
    assert output.read("/T4CGA.BAT")==old.read("/T4CGA.BAT")
    for item in ("/WINDOWS/SYSTEM/TR53216.DRV",
                 "/WINDOWS/SYSTEM/HPXY.DRV",
                 "/WINDOWS/SYSTEM/XR155.DRV",
                 "/WINDOWS/SYSTEM/XDIB.DRV",
                 "/WINDOWS/SYSTEM/PIXFAST.DRV","/USETR7.BAT",
                 "/PANON.BAT","/PANOFF.BAT"):
        assert item not in actual,item
    # Keep no other mode switch BATs on root.
    root_bat={p for p in actual if p.count("/")==1 and p.endswith(".BAT")}
    assert root_bat=={"/WIN.BAT","/AUTOEXEC.BAT",
                      "/PIXMAX.BAT","/T4CGA.BAT","/NOPAN16.BAT"},root_bat
    # Exactly 3 native Tandy driver binaries remain, all known-working.
    installed_tandy_display={p for p in actual if p.startswith("/WINDOWS/SYSTEM/") and
             p.rsplit("/",1)[1] in DROP_DISPLAY | KEEP_DISPLAY}
    assert installed_tandy_display=={"/WINDOWS/SYSTEM/"+x for x in KEEP_DISPLAY}
    assert output.b[:old.part]==old.b[:old.part], "Boot code or partition table altered"
    fatlength=struct.unpack_from("<H",output.b,output.part+22)[0]*512
    assert output.b[output.fat:output.fat+fatlength]==output.b[output.fat+fatlength:output.fat+2*fatlength]
    # Deleted chain contents may persist in free clusters but no obsolete
    # experiment is visible from DOS filesystem. This is not a disk wipe.
    img_sha=digest(opts.output.read_bytes())
    report={
        "status":"STATIC_BUILD_OK_REAL_HARDWARE_3_MODE_SWITCH_NOT_YET_TESTED",
        "base_card":str(opts.pixmax),"base_sha256":PIXMAX_IMAGE_SHA,
        "trial7_hardware_verified_card":str(opts.trial7),"trial7_sha256":TRIAL7_IMAGE_SHA,
        "output":opts.output.name,"sha256":img_sha,
        "original_files":len(originals),"retained_unchanged":len(originals)-len(deletions),
        "deleted_experimental_files":sorted(deletions),"added":sorted(add),
        "total_visible_files":len(actual),
        "selected_initial_profile":"PIXMAX",
        "modes":[
          {"selector":"T4CGA","driver":"TANDYDSP.DRV","colors":4,"physical":"640x200","panning":False,
           "hardware_status":"previously verified"},
          {"selector":"NOPAN16","driver":"TR73216.DRV","colors":16,"physical":"320x200","logical":"320x200","panning":False,
           "hardware_status":"TRIAL7 driver verified alone, integration with new 3-row UI pending"},
          {"selector":"PIXMAX","driver":"PIXMAX.DRV","colors":16,"physical":"320x200","logical":"640x256","panning":True,
           "hardware_status":"corrected PIXMAX owner-tested, Calculator 18.8s"}],
        "preserved":["WIN.BAT mode-3 and video reservation",
         "Windows 1.0 serial mouse driver","DOS 6.22","all user applications and groups",
         "original Tandy boot splash and fonts","PAN.EXE for PIXMAX",
         "three-row compact/wide Program Manager layouts"],
        "warning":"No new CF physical test was performed; mode switch profiles may need on-device adjustment"
    }
    opts.report.write_text(json.dumps(report,indent=2)+"\n")
    (opts.output.parent/(opts.output.name+".sha256")).write_text(img_sha+"  "+opts.output.name+"\n")
    print("PASS clean bootable 3-mode CF",opts.output.name,"sha256",img_sha)
    print("PASS",report["original_files"],"original files,",report["retained_unchanged"],
          "retained identical,",len(deletions),"obsolete experiments deleted,",
          len(add),"new mode-control files; total",len(actual))
    print("PASS only three root DOS mode selectors T4CGA, NOPAN16, PIXMAX")
    print("PASS TR73216 original verified native 320x200 driver and no PAN.EXE in NOPAN16 WIN.INI")
    print("PASS PIXMAX current default and 4-color wide layout exactly preserved")
    print("PASS mouse, logo, program groups, DOS files, all Windows apps and FAT16 mirrors preserved")

if __name__=="__main__":
    main()
