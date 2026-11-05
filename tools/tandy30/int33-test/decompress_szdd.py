#!/usr/bin/env python3
"""Expand Microsoft Windows 3.0 SZDD-compressed installation drivers."""
from pathlib import Path
import hashlib
import struct
import sys

def expand(data: bytes) -> bytes:
    if data[:8] != b'SZDD\x88\xf0\x27\x33' or data[8] != 0x41:
        raise ValueError('Not an SZDD A-mode compressed driver')
    target = struct.unpack_from('<I', data, 10)[0]
    window = bytearray(b' ' * 4096)
    pos = 0xFEE
    out = bytearray()
    source = 14
    while len(out) < target:
        if source >= len(data):
            raise ValueError('Truncated SZDD control byte')
        flags = data[source]; source += 1
        for _ in range(8):
            if flags & 1:
                if source >= len(data):
                    raise ValueError('Truncated SZDD literal')
                c = data[source]
                source += 1
                out.append(c)
                window[pos] = c
                pos = (pos + 1) & 0xFFF
            else:
                if source + 1 >= len(data):
                    raise ValueError('Truncated SZDD backreference')
                a, b = data[source:source+2]
                source += 2
                offset = a | ((b & 0xF0) << 4)
                count = (b & 0xF) + 3
                for i in range(count):
                    c = window[(offset+i) & 0xFFF]
                    out.append(c)
                    window[pos] = c
                    pos = (pos + 1) & 0xFFF
                    if len(out) == target:
                        break
            if len(out) == target:
                break
            flags >>= 1
    if len(out) != target or source != len(data):
        raise ValueError(f'Unexpected SZDD output/trailing input: output={len(out)}/{target}, trailing={len(data)-source}')
    return bytes(out)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: decompress_szdd.py INPUT OUTPUT')
    source = Path(sys.argv[1]); target = Path(sys.argv[2])
    b = expand(source.read_bytes())
    target.write_bytes(b)
    print(f'Expanded {source} -> {target}: {len(b)} bytes SHA256 {hashlib.sha256(b).hexdigest()}')
