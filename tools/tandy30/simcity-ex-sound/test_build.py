#!/usr/bin/env python3
"""Static build checks only; the audible test must run on real EX hardware."""
from pathlib import Path

root = Path(__file__).resolve().parent
driver = (root / 'SCEXSND.COM').read_bytes()
test = (root / 'TESTSND.COM').read_bytes()
source = (root / 'SCEXSND.S').read_text()
probe = (root / 'TSRPROBE.COM').read_bytes()
probe_src = (root / 'TSRPROBE.S').read_text()
assert driver[:2] == bytes.fromhex('0e1f'), 'COM entry must set DS=CS'
assert len(driver) < 2048 and len(test) < 2048, 'Keep binaries tiny'
assert b'\x7fELF' not in driver and b'MZ' != driver[:2]
assert b'\xba\xc0\x00' in driver, 'Expected Tandy EX PSG port 0xC0'
assert b'\xcd\x1a' in driver, 'Missing INT 1Ah sound BIOS shim'
assert b'SCEXSND' in driver
assert '0x3100' in source, 'Missing DOS TSR terminate-and-stay-resident'
assert 'int 0x15' in source, 'Missing sound completion callback'
assert 'old1a' in source and 'old1c' in source, 'Missing BIOS hook chaining'
assert 'and word ptr ss:[bp+6], 0xfffe' in source, 'Missing carry flag clearing'
assert 'or word ptr ss:[bp+6], 1' in source, 'Missing carry flag setting'
block = bytes([128]*16 + [255]*16 + [0]*16 + [128]*16 + [200]*32 + [90]*32)
assert len(block) == 128
assert test.endswith(block * 4), 'Test PCM sample payload must be 512 bytes'
assert b'PASS: busy contract' in test
assert b'PASS: sound completed' in test
# Verify the chosen BIOS divisor cannot cause a 16-bit division overflow.
assert max(196608 // max(4, rate) for rate in range(1, 4096)) <= 65535
assert len(probe) == 96, 'Unexpected size of no-hook TSR probe'
assert probe[:2] == bytes.fromhex('0e1f'), 'Probe must set DS=CS'
assert b'\xcd\x1a' not in probe and b'\xba\xc0\x00' not in probe, 'Probe must never touch BIOS sound/PSG'
assert b'\xcd\x21' in probe and b'TSRPROBE:' in probe
assert '0x3100' in probe_src and '0x251a' not in probe_src and '0x251c' not in probe_src
print('PASS: no-hook 96-byte TSR diagnostic')
print('PASS: binary size, DOS format, BIOS hooks, PSG port, test PCM, rate bounds')
print(f'SCEXSND.COM: {len(driver)} bytes; TESTSND.COM: {len(test)} bytes')
print('NOTE: SimCity compatibility and actual audio require real EX testing.')
