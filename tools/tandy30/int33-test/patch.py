#!/usr/bin/env python3
"""Patch Windows 3.0 MOUSE.DRV for DOS INT 33h on a Tandy V20 CF image.

Only the existing MOUSE.DRV file and SYSTEM.INI are edited in-place.
Uses FAT16 to preserve the original disk allocation and boot sectors.
"""
import argparse
from hashlib import sha256
from pathlib import Path
import re
from fat16_image import Fat16

CARD_BYTES = 31808 * 512
ORIGINAL_SHA = '8ca171370b9b51a1c642ec2a03363f1e30f675733078b91b8eaf34a8299fe476'
PATCHED_SHA = '87f892abc191f9d947cf4f62071e817d7f189d3f1ffc5be2e78255ddd4564399'
OLD = bytes.fromhex('b430cd213c0a7205')
NEW = bytes.fromhex('b430cd213c0aeb00')

def digest(b):
    return sha256(b).hexdigest()

def update_ini(before):
    text = before.decode('cp437')
    start = re.search(r'(?im)^\[boot\][ \t]*\r?$', text)
    if start is None:
        raise ValueError('No [boot] section')
    end = re.search(r'(?m)^\[[^\r\n]+\]', text[start.end():])
    stop = start.end()+end.start() if end else len(text)
    boot = text[start.end():stop]
    pat = re.compile(r'(?im)^([ \t]*mouse\.drv[ \t]*=)[^\r\n]*')
    if len(pat.findall(boot)) != 1:
        raise ValueError('Expected one [boot] mouse.drv entry')
    boot = pat.sub(lambda m: m.group(1)+'mouse.drv', boot, count=1)
    return (text[:start.end()]+boot+text[stop:]).encode('cp437')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_image',type=Path)
    ap.add_argument('original_mouse_drv',type=Path)
    ap.add_argument('output_image',type=Path)
    args = ap.parse_args()
    drv = args.original_mouse_drv.read_bytes()
    if digest(drv) != ORIGINAL_SHA or drv[:2] != b'MZ' or drv.count(OLD) != 1:
        raise ValueError('Wrong original Windows 3.0 mouse driver')
    patched = drv.replace(OLD, NEW)
    if digest(patched) != PATCHED_SHA:
        raise ValueError('INT 33h patch verification failed')
    fat = Fat16(bytearray(args.input_image.read_bytes()))
    ini = fat.read('/WINDOWS/SYSTEM.INI')
    display = re.search(rb'(?im)^display\.drv=[^\r\n]+', ini)
    if not display:
        raise ValueError('Missing Windows display driver setting')
    auto = fat.read('/AUTOEXEC.BAT')
    config = fat.read('/CONFIG.SYS')
    if b'C:\\CTMOUSE.EXE /S14 /M' not in auto.upper():
        raise ValueError('Input image lacks working CuteMouse startup')
    if fat.read('/WINDOWS/SYSTEM/MOUSE.DRV')[:2] != b'MZ':
        raise ValueError('Input image lacks original MOUSE.DRV')
    fat.write_existing('/WINDOWS/SYSTEM/MOUSE.DRV',patched)
    fat.write_existing('/WINDOWS/SYSTEM.INI',update_ini(ini))
    after = fat.read('/WINDOWS/SYSTEM.INI')
    if display.group(0) not in after or b'mouse.drv=mouse.drv' not in after.lower():
        raise ValueError('Windows configuration validation failed')
    if fat.read('/AUTOEXEC.BAT') != auto or fat.read('/CONFIG.SYS') != config:
        raise ValueError('DOS startup configuration changed')
    output = bytes(fat.b)
    args.output_image.parent.mkdir(parents=True,exist_ok=True)
    args.output_image.write_bytes(output)
    args.output_image.with_name(args.output_image.name+'.sha256').write_text(
        f'{digest(output)}  {args.output_image.name}\n',encoding='ascii')
    print('Created',args.output_image,'bytes',len(output),'SHA256',digest(output))

if __name__ == '__main__':
    main()
