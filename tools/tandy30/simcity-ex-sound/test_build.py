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
assert len(driver) < 2048 and len(test) < 1024, 'Keep binaries tiny'
assert b'\x7fELF' not in driver and b'MZ' != driver[:2]
assert b'\xba\xc0\x00' in driver, 'Expected Tandy EX PSG port 0xC0'
assert b'\xcd\x1a' in driver, 'Missing INT 1Ah sound BIOS shim'
assert b'SCEXSND' in driver
assert '0x3100' in source, 'Missing DOS TSR terminate-and-stay-resident'
assert 'int 0x15' in source, 'Missing sound completion callback'
assert 'old1a' in source and 'old1c' in source, 'Missing BIOS hook chaining'
assert 'and word ptr ss:[bp+6], 0xfffe' in source, 'Missing carry flag clearing'
assert 'or word ptr ss:[bp+6], 1' in source, 'Missing carry flag setting'
assert b'SCEXSND 0.30 detected' in test, 'Unexpected test edition'
assert b'BUSY test passed' in test
assert b'\x0e\x1f' == test[:2]
assert b'PASS: sound completed' in test
# Verify the chosen BIOS divisor cannot cause a 16-bit division overflow.
assert max(65536 // max(2, rate) for rate in range(1, 4096)) <= 65535
assert len(probe) == 96, 'Unexpected size of no-hook TSR probe'
assert probe[:2] == bytes.fromhex('0e1f'), 'Probe must set DS=CS'
assert b'\xcd\x1a' not in probe and b'\xba\xc0\x00' not in probe, 'Probe must never touch BIOS sound/PSG'
assert b'\xcd\x21' in probe and b'TSRPROBE:' in probe
assert '0x3100' in probe_src and '0x251a' not in probe_src and '0x251c' not in probe_src
print('PASS: no-hook 96-byte TSR diagnostic')
print('PASS: binary size, DOS format, BIOS hooks, PSG port, test PCM, rate bounds')
print(f'SCEXSND.COM: {len(driver)} bytes; TESTSND.COM: {len(test)} bytes')
# Isolate interrupts independently. Probes must be pure pass-through.
for name, interrupt in (('HOOK1A', 0x1A), ('HOOK1C', 0x1C)):
    code = (root / (name + '.COM')).read_bytes()
    src = (root / (name + '.S')).read_text()
    assert code[:2] == b'\x0e\x1f', f'{name}: initialize DS=CS'
    assert 64 <= len(code) < 256, f'{name}: unexpected size'
    assert bytes((0xB8, interrupt, 0x35)) in code, f'{name}: missing old vector read'
    assert bytes((0xB8, interrupt, 0x25)) in code, f'{name}: missing hook'
    assert b'\x2e\xff\x2e' in code, f'{name}: far JMP must use CS override'
    assert b'\xb8\x00\x31\xcd\x21' in code, f'{name}: missing TSR DOS termination'
    assert 'jmp far ptr cs:[old_vector]' in src
    assert 'out ' not in src and 'int 0x15' not in src
    other = 0x1A if interrupt == 0x1C else 0x1C
    assert bytes((0xB8, other, 0x25)) not in code, f'{name}: other interrupt vector modified'
    print(f'PASS: {name} one-vector chain only ({len(code)} bytes)')

gate = (root / 'SCGATE.COM').read_bytes()
gate_src = (root / 'SCGATE.S').read_text()
assert len(gate) == 128, 'Unexpected size of status-only diagnostic'
assert gate[:2] == b'\x0e\x1f'
assert b'\xb8\x1a\x35\xcd\x21' in gate
assert b'\xb8\x1a\x25\xcd\x21' in gate
assert b'\xb8\x00\x31\xcd\x21' in gate
assert b'\x80\xfc\x81' in gate, 'Missing AH=81h gate'
assert b'\xb8\xc4\x00' in gate, 'Status must return AX=00C4'
assert b'\x2e\xff\x2e' in gate, 'Unhandled BIOS calls must chain'
assert b'\xba\xc0\x00' not in gate
assert '0x251c' not in gate_src and 'out ' not in gate_src
print('PASS: SCGATE status-only BIOS interception without sound/timer hook')
print('NOTE: SimCity compatibility and actual audio require real EX testing.')
