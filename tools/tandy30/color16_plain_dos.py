#!/usr/bin/env python3
"""Make a diagnostic 16-color Tandy CF image with unlinked conventional DOS memory.

The original 16-color trial failed safely at RESERVE.COM because DOS' arena
topology did not match its validated 624 KB / 9C00h conventional layout.
The known-good original CF release and 16-color v1 image remain untouched.

This only changes CONFIG.SYS on the *new* experimental image. The original
DOSMAX configuration is saved for a reversible DOS restoration.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent / 'int33-test'))
from fat16_image import Fat16, CARD_BYTES

SOURCE_SHA = 'd1cff2224f1b43b0be87b49e86905591268a564b4d55c42a6881899b93698453'
PARTITION_OFFSET = 63 * 512
PLAIN = (r'''FILES=30
BUFFERS=20
DEVICE=C:\DOS\SETVER.EXE
DOS=LOW
REM No DOSMAX, USE!UMBS, or SHELLMAX. Normal DOS MCB arena.
REM Legacy MOUSE.SYS disabled. AUTOEXEC loads CTMOUSE /S14 /M
SHELL=C:\COMMAND.COM C:\ /E:256 /P
'''.replace('\n','\r\n').encode('cp437'))

RESTORE = (r'''@ECHO OFF
REM Restore both original DOSMAX and Windows 640x200 display.
IF NOT EXIST C:\WINXT\CONFOLD.SYS GOTO BAD
IF NOT EXIST C:\WINXT\SYSOLD.INI GOTO BAD
COPY /Y C:\WINXT\SYSOLD.INI C:\WINDOWS\SYSTEM.INI
IF ERRORLEVEL 1 GOTO BAD
COPY /Y C:\WINXT\CONFOLD.SYS C:\CONFIG.SYS
IF ERRORLEVEL 1 GOTO BAD
IF EXIST C:\WIN.BAT DEL C:\WIN.BAT
ECHO Original Windows display and DOSMAX restored. REBOOT.
GOTO END
:BAD
ECHO Restore failed. DO NOT overwrite the verified CF release.
:END
'''.replace('\n','\r\n').encode('cp437'))

def d(data):
    return sha256(data).hexdigest()

def run(*args):
    subprocess.run(args, check=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('source',type=Path)
    p.add_argument('output',type=Path)
    a = p.parse_args()
    old = a.source.read_bytes()
    if len(old) != CARD_BYTES or d(old) != SOURCE_SHA:
        raise ValueError('Not the exact checked experimental 16-color image v1')
    image = Fat16(bytearray(old))
    cfg = image.read('/CONFIG.SYS')
    if (b'USE!UMBS.SYS' not in cfg.upper() or
        b'DOSMAX.EXE' not in cfg.upper() or
        b'SHELLMAX.COM' not in cfg.upper()):
        raise ValueError('Unexpected original DOSMAX configuration')
    if b'SHELL=C:\\COMMAND.COM' not in PLAIN:
        raise ValueError('Plain COMMAND.COM configuration lost')
    if not image.read('/COMMAND.COM').startswith(b'\xE9') and len(image.read('/COMMAND.COM')) < 40000:
        raise ValueError('Missing normal root DOS COMMAND.COM')
    mouse = image.read('/WINDOWS/SYSTEM/MSMOUSE1.DRV')
    if d(mouse) != '99b3578809422728d64ad4cdbe17361cdde400840167c8d90c7499842c2812b8':
        raise ValueError('Verified Windows 1.04 serial mouse driver changed')
    if b'DISPLAY.DRV=TR53216.DRV' not in image.read('/WINDOWS/SYSTEM.INI').upper():
        raise ValueError('16-color driver configuration missing')
    if b'RESERVE.COM' not in image.read('/WIN.BAT').upper():
        raise ValueError('Video reservation guard missing')
    image.write_existing('/CONFIG.SYS',PLAIN)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(image.b)

    target = f'{a.output}@@{PARTITION_OFFSET}'
    with tempfile.TemporaryDirectory() as temp:
        folder=Path(temp)
        backup=folder/'CONFOLD.SYS'
        restore=folder/'RESTORE.BAT'
        backup.write_bytes(cfg)
        restore.write_bytes(RESTORE)
        run('mcopy','-o','-i',target,str(backup),'::/WINXT/CONFOLD.SYS')
        run('mcopy','-o','-i',target,str(restore),'::/WINXT/RESTORE.BAT')
    output = Fat16(bytearray(a.output.read_bytes()))
    if output.read('/WINXT/CONFOLD.SYS') != cfg:
        raise ValueError('Original CONFIG.SYS backup mismatch')
    if output.read('/WINXT/RESTORE.BAT') != RESTORE:
        raise ValueError('Restoration script mismatch')
    if output.read('/CONFIG.SYS') != PLAIN:
        raise ValueError('Plain DOS config mismatch')
    for path in ('/AUTOEXEC.BAT','/CTMOUSE.EXE',
                 '/WINDOWS/SYSTEM/MSMOUSE1.DRV','/WINDOWS/SYSTEM/TR53216.DRV',
                 '/WINDOWS/SYSTEM/TANDYDSP.DRV','/WINDOWS/SYSTEM.INI',
                 '/WIN.BAT','/WINXT/RESERVE.COM'):
        if output.read(path) != Fat16(bytearray(old)).read(path):
            raise ValueError('Unexpected modified file: '+path)
    result=a.output.read_bytes()
    if len(result)!=CARD_BYTES:
        raise ValueError('Wrong card size')
    a.output.with_name(a.output.name+'.sha256').write_text(
        f'{d(result)}  {a.output.name}\n', encoding='ascii')
    print(f'Created {a.output}, bytes {len(result)}, SHA256 {d(result)}')
    print('CONFIG.SYS: conventional DOS using COMMAND.COM, NO DOSMAX/USE!UMBS/SHELLMAX.')
    print('Original DOSMAX config backed up; Windows 1.04 mouse and new video unchanged.')
    print('RESERVE.COM still guards manual WIN; do not bypass failures.')

if __name__=='__main__':
    main()
