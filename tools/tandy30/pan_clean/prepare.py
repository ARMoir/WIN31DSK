#!/usr/bin/env python3
"""Prepare a separate panning Windows 3.0 CF image without deleting any old file.

Source is a pinned, already hardware-tested 31,808-sector RRECT CF image.
Uses only upstream HPXY/PAN driver binaries from an exact pinned WINXT.ZIP.
No Microsoft files are redistributed individually; destination is the existing
user-owned Windows image. Executes only on the GitHub Actions build machine.
"""
import argparse
import hashlib
import re
import struct
import subprocess
import zipfile
from pathlib import Path
import sys

CARD_SIZE=31808*512
ROOT='::'

def sha(b): return hashlib.sha256(b).hexdigest()

def run(*args):
    subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def read_guest(image,path,target):
    run('mcopy','-i',str(image)+'@@32256','::'+path,str(target))
    return target.read_bytes()

def write_guest(image,src,path):
    run('mcopy','-o','-i',str(image)+'@@32256',str(src),'::'+path)

def replace_once(source,pattern,repl,label):
    changed,n=re.subn(pattern,lambda m: m.group(1)+repl,source,flags=re.I|re.M)
    if n!=1:raise ValueError('%s expected once, got %d'%(label,n))
    return changed

def set_ini(source,section,key,value):
    lines=source.splitlines(keepends=True)
    active=False
    count=0
    out=[]
    for line in lines:
        stripped=line.strip()
        if stripped.startswith(b'[') and stripped.endswith(b']'):
            active=(stripped.lower()==b'['+section.lower()+b']')
        if active and re.match(rb'\s*'+re.escape(key)+rb'\s*=',line,re.I):
            eol=b'\r\n' if line.endswith(b'\r\n') else b'\n' if line.endswith(b'\n') else b''
            line=key+b'='+value+eol
            count+=1
        out.append(line)
    if count!=1:raise ValueError('INI key %s/%s found %d times'%(section,key,count))
    return b''.join(out)

def batch(text):
    return ('\r\n'.join(text)+'\r\n').encode('ascii')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--image',type=Path,required=True)
    ap.add_argument('--packet',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--stage',type=Path,required=True)
    a=ap.parse_args()
    root=a.stage
    root.mkdir(parents=True,exist_ok=False)
    original=a.image.read_bytes()
    assert len(original)==CARD_SIZE and original[510:512]==b'\x55\xaa'
    assert sha(original)=='bedf5aa14c6259ad526074ce2412528a91f170feda9b3798befb78e8746f5e8b'
    assert sha(a.packet.read_bytes())=='35266732e122068d03c44c98a610621d65c06c38c29b8ca3d1d0513a94d30fca'
    a.out.write_bytes(original)
    with zipfile.ZipFile(a.packet) as z:
        def payload(name):
            member='WINXT/'+name
            found=[n for n in z.namelist() if n.upper()==member.upper()]
            if len(found)!=1:raise ValueError('WINXT ZIP missing exact member '+member)
            return z.read(found[0])
        drivers=('HPXY.DRV','XTCSYS.FON','XTCFIX.FON','XTCOEM.FON')
        owners=('PAN.EXE','XYCTL.EXE','PANKEY.DLL','XTPAN.EXE','PANCTL.EXE','CGACTL.EXE')
        for name in drivers+owners:
            data=payload(name)
            if not data or len(data)>150000:raise ValueError('Unexpected helper '+name)
            (root/name).write_bytes(data)
    sy=read_guest(a.out,'/WINDOWS/SYSTEM.INI',root/'SYSBASE.INI')
    wn=read_guest(a.out,'/WINDOWS/WIN.INI',root/'WINBASE.INI')
    pm=read_guest(a.out,'/WINDOWS/PROGMAN.INI',root/'PRGBASE.INI')
    for group in ('MAIN','ACCESSOR','GAMES'):
        g=read_guest(a.out,'/WINDOWS/'+group+'.GRP',root/(group+'.GRP'))
        assert len(g)>500 and g[:4]==b'PMCC'
        print('Preserve '+group+'.GRP',len(g),'bytes sha256',sha(g))
    # Keep the working Windows 1.04 serial mouse as-is.
    if not re.search(rb'(?im)^mouse\.drv=msmouse1\.drv\r?$',sy):
        raise ValueError('Unexpected or unknown known-good Windows mouse selection')
    sy2=sy
    for key,value in [
        (b'display.drv',b'HPXY.DRV'),(b'fonts.fon',b'XTCSYS.FON'),
        (b'fixedfon.fon',b'XTCFIX.FON'),(b'oemfonts.fon',b'XTCOEM.FON')
    ]:
        sy2=set_ini(sy2,b'boot',key,value)
    sy2=set_ini(sy2,b'boot.description',b'display.drv',
                b'Tandy EX/HX HPXY 640x256 logical, 16 colors, 320x200 viewport')
    wn2=wn
    wn2=set_ini(wn2,b'windows',b'BorderWidth',b'1')
    # Windows 3.0's run= token loads the PAN dispatcher, which detects HPXY
    # and launches its XYCTL owner. Nothing else originally occupied run=.
    if not re.search(rb'(?im)^run=\r?$',wn):
        raise ValueError('Nonempty WIN.INI run=; refuse destructive startup edit')
    wn2=set_ini(wn2,b'windows',b'run',b'C:\\WINDOWS\\PAN.EXE')
    # Classic Windows appearance, avoids expensive desktop wallpaper painting.
    for section,key,value in [
      (b'Desktop',b'Pattern',b'0 0 0 0 0 0 0 0'),
      (b'Desktop',b'Wallpaper',b''),
      (b'Desktop',b'TileWallpaper',b'0'),
      (b'Desktop',b'GridGranularity',b'2'),
      (b'Desktop',b'IconSpacing',b'76'),
      (b'colors',b'Background',b'0 128 128'),
      (b'colors',b'Menu',b'192 192 192'),
      (b'colors',b'ActiveTitle',b'0 0 128'),
      (b'colors',b'ActiveBorder',b'0 0 128'),
      (b'colors',b'TitleText',b'255 255 255')
    ]:
        wn2=set_ini(wn2,section,key,value)
    # Keep the original three groups and original .GRP files exactly.
    assert all(x in pm for x in
         (b'MAIN.GRP',b'ACCESSOR.GRP',b'GAMES.GRP'))
    pm2=pm
    pm2=set_ini(pm2,b'Settings',b'Window',b'0 0 640 256 3')
    pm2=set_ini(pm2,b'Settings',b'AutoArrange',b'1')
    pm2=set_ini(pm2,b'Settings',b'SaveSettings',b'0')
    files={'SYSPAN.INI':sy2,'WINPAN.INI':wn2,'PRGPAN.INI':pm2,
           'SYSBASE.INI':sy,'WINBASE.INI':wn,'PRGBASE.INI':pm}
    for name,data in files.items():
        (root/name).write_bytes(data)
    (root/'PANOFF.BAT').write_bytes(batch([
         '@ECHO OFF',
         'REM Use from DOS with Windows fully closed.',
         'COPY C:\\TANDY88\\SYSBASE.INI C:\\WINDOWS\\SYSTEM.INI',
         'IF ERRORLEVEL 1 GOTO FAILED',
         'COPY C:\\TANDY88\\WINBASE.INI C:\\WINDOWS\\WIN.INI',
         'IF ERRORLEVEL 1 GOTO FAILED',
         'COPY C:\\TANDY88\\PRGBASE.INI C:\\WINDOWS\\PROGMAN.INI',
         'IF ERRORLEVEL 1 GOTO FAILED',
         'ECHO Original RRECT display and Windows layout selected.',
         'GOTO END',':FAILED',
         'ECHO Restore failed: check files before starting Windows.',
         ':END']))
    (root/'PANON.BAT').write_bytes(batch([
         '@ECHO OFF',
         'REM Use from DOS with Windows fully closed.',
         'COPY C:\\TANDY88\\SYSPAN.INI C:\\WINDOWS\\SYSTEM.INI',
         'IF ERRORLEVEL 1 GOTO FAILED',
         'COPY C:\\TANDY88\\WINPAN.INI C:\\WINDOWS\\WIN.INI',
         'IF ERRORLEVEL 1 GOTO FAILED',
         'COPY C:\\TANDY88\\PRGPAN.INI C:\\WINDOWS\\PROGMAN.INI',
         'IF ERRORLEVEL 1 GOTO FAILED',
         'ECHO HPXY 16-color pannable desktop and organized groups selected.',
         'GOTO END',':FAILED',
         'ECHO Switching failed: check files before starting Windows.',
         ':END']))
    (root/'PANHELP.TXT').write_bytes(batch([
        'Tandy EX Windows 3.0 640x256 logical / 320x200 16-color viewport.',
        'Windows starts manually with WIN from DOS. Setup is NOT required.',
        'PAN is in Windows startup; optionally choose File Run PAN.EXE.',
        'Ctrl-Alt-arrows pan the desktop. Ctrl-Alt-Home returns home.',
        'Ctrl-Alt-End brings active window into view.',
        'Use PAN /SETTINGS inside Windows to set Software/Hardware pan.',
        'From DOS with Windows closed: PANOFF then WIN restores RRECT.',
        'From DOS: PANON then WIN reselects this panning test.',
        'All existing Main, Accessories, Games groups, shortcuts and apps kept.',
        'Do not bypass RESERVE.COM or replace the known-good mouse driver.']))
    for name in drivers:
        write_guest(a.out,root/name,'/WINDOWS/SYSTEM/'+name)
    for name in owners:
        write_guest(a.out,root/name,'/WINDOWS/'+name)
    for name in files:
        write_guest(a.out,root/name,'/TANDY88/'+name)
    for name in ('PANOFF.BAT','PANON.BAT','PANHELP.TXT'):
        write_guest(a.out,root/name,'/'+name)
    for filename,dest in [('SYSPAN.INI','SYSTEM.INI'),('WINPAN.INI','WIN.INI'),
                          ('PRGPAN.INI','PROGMAN.INI')]:
        write_guest(a.out,root/filename,'/WINDOWS/'+dest)
    print('Wrote PAN / BorderWidth=1 / tidy Program Manager image:',a.out,
          a.out.stat().st_size,'sha256',sha(a.out.read_bytes()))

if __name__=='__main__':
    main()
