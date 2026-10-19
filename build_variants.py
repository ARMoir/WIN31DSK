#!/usr/bin/env python3
"""Generate 286 Windows 3.1 single-floppy variants from a user-supplied source image.

Requires fatmini.py next to this script. Does not ship Microsoft or SkiFree binaries.
"""
import argparse
import hashlib
from pathlib import Path
from fatmini import FAT12

IMAGE_SIZE = 1474560
WINFILE_SETTINGS = ("[Settings]\r\n"
                    "IndexOnLaunch=0\r\n"
                    "DriveBar=0\r\n"
                    "StatusBar=0\r\n"
                    "dir1=48,7,543,236,-1,-1,3,30,201,1808,150,A:\\*.*\r\n").encode('ascii')

def validate(d):
    assert len(d.b) == IMAGE_SIZE
    start, n = d.fatstart, d.fatsz*d.bps
    assert d.b[start:start+n] == d.b[start+n:start+2*n], 'FAT mismatch'
    for filename in ('IO.SYS','MSDOS.SYS','COMMAND.COM','HIMEM.SYS','WIN.COM','KRNL286.EXE','SKI.EXE'):
        assert len(d.readfile(filename)) > 0, filename
    assert b'B:\\' not in d.readfile('SYSTEM.INI').upper()

def build(source, output_dir):
    original = FAT12(source.read_bytes())
    validate(original)
    cfg = original.readfile('SYSTEM.INI')
    assert b'shell=WINFILE.EXE' in cfg, 'Expected corrected File Manager source image'
    output_dir.mkdir(parents=True, exist_ok=True)

    full = FAT12(source.read_bytes())
    full.writefile('WINFILE.INI', WINFILE_SETTINGS)
    validate(full)
    full_path = output_dir / 'WIN31DSK_Full_FileManager_286.img'
    full_path.write_bytes(full.b)

    low = FAT12(source.read_bytes())
    low.writefile('SYSTEM.INI', cfg.replace(b'shell=WINFILE.EXE', b'shell=TASKMAN.EXE'))
    for filename in ('WINFILE.EXE', 'WINMINE.EXE', 'NOTEPAD.EXE'):
        try:
            low.delete(filename)
        except KeyError:
            pass
    validate(low)
    low_path = output_dir / 'WIN31DSK_LowMemory_TaskManager_286.img'
    low_path.write_bytes(low.b)

    for path in (full_path, low_path):
        d = FAT12(path.read_bytes())
        validate(d)
        print(f'{path.name}: {len(d.b)} bytes, {d.freebytes()} bytes free, sha256 {hashlib.sha256(d.b).hexdigest()}')
    for filename in ('IO.SYS','MSDOS.SYS','COMMAND.COM','HIMEM.SYS','KRNL286.EXE','WIN.COM','SKI.EXE'):
        assert full.readfile(filename) == original.readfile(filename)
        assert low.readfile(filename) == original.readfile(filename)
    print('DOS boot and Windows core files and SkiFree retained byte-for-byte.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Corrected source IMG (user supplied)')
    parser.add_argument('--output-dir', type=Path, default=Path('dist'))
    args = parser.parse_args()
    build(args.source, args.output_dir)
