#!/usr/bin/env python3
"""Static 8086/V20 safety and PCM->PSG model test; actual hardware remains untested."""
from pathlib import Path
import re
import subprocess

base = Path(__file__).parent
binary = (base / 'SCEXSND.COM').read_bytes()
tester = (base / 'TESTSND.COM').read_bytes()
src = (base / 'SCEXSND.S').read_text()
testsrc = (base / 'TESTSND.S').read_text()
assert len(binary) == 1312, f'Unexpected driver size: {len(binary)}'
assert len(tester) == 544, f'Unexpected sound test size: {len(tester)}'
assert binary[:2] == b'\x0e\x1f' and tester[:2] == b'\x0e\x1f'
assert b'SCEXSND 0.32' in binary and b'SCEXSND 0.32' in tester
assert 'noise_mode:' in src and 'noise_already:' in src and 'add ax,3' in src
assert 'mov al,0xe5' in src and 'add al,2' in src
assert 'mov dx,3' in src, "Tandy sample rate must use 3.579545MHz clock"
assert 'cmp dx,0x0300' in src
assert 'synth_short_effect:' in src and 'effect_type:' in src
assert all(f'cmp cx,{n}' in src for n in (384,768,1536))
assert b'\xba\xc0\x00' in binary
assert 'out dx,al' in src and 'old1a' in src and 'old1c' in src
assert 'add word ptr [pcm_seg],0x1000' in src, '64 KB linear pointer handling missing'
assert 'min_sample' in src and 'crossings' in src and 'mul bx' in src
assert 'int 0x15' in src and 'int 0x21' not in src[src.index('int1c_entry:'):src.index('old1a:')]
assert '.section .bss' in testsrc and 'samples: .space 4096' in testsrc
assert 'cmp dx,55' in testsrc, 'Missing audible test watchdog'
sym = subprocess.check_output(['nm','-n',str(base/'SCEXSND.o')],text=True)
end = int(re.search(r'^([0-9a-f]+) [A-Za-z] old1a$', sym, re.M).group(1),16)
dis = subprocess.check_output(['objdump','-d','-m','i8086',f'--stop-address={end}',str(base/'SCEXSND.o')],text=True)
ops = []
for line in dis.splitlines():
    m = re.match(r'^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2} )+)\s+([a-z][\w.]*)', line)
    if m:
        op = int(m.group(1).split()[0],16)
        assert op not in (0x0f,0x66,0x67,0x60,0x61,0x68,0x6a), f'Unsafe instruction: {line}'
        ops.append(op)
assert len(ops) > 200, 'Too few instructions examined'

# Independently regenerate the test's four PCM patterns and model real integer math.
pcm = bytes([64]*8+[192]*8)*64 + bytes([48]*16+[208]*16)*32
pcm += bytes([54]*6+[202]*6)*85 + bytes([128])*4
pcm += bytes([12,202,235,43,230,6,145,111])*128
def atten(avg,volume=7):
    return 15 - min(15, (avg >> 3)+3)*volume//7
assert atten(0)==12 and atten(16)==10 and atten(48)==6 and atten(96)==0
assert atten(16,0)==15
assert len(pcm)==4096
divisors=[]
step=65536//150
for off in range(0,len(pcm),step):
    chunk=pcm[off:off+min(64,step,len(pcm)-off)]
    crosses=sum(1 for i,v in enumerate(chunk) if v>=128 and (i==0 or chunk[i-1]<128))
    if crosses and max(chunk)-min(chunk)>=16:
        div=max(16,min(1023,(150*len(chunk)*3)//(32*crosses)))
        divisors.append((off,111860/div,crosses>len(chunk)//8))
assert 450 < divisors[0][1] < 550, divisors
assert any(215<hz<285 for off,hz,n in divisors if 1500<=off<=2100), divisors
assert any(550<hz<850 for off,hz,n in divisors if 2100<=off<=3000), divisors
assert any(n for off,hz,n in divisors if off>3000), divisors
assert (3*65536)//768 == 256
assert [384,768,1536] == [2*n for n in (192,384,768)]
assert abs((3579545/768) / 18.2065 - 256) < 1.0
assert len(set([384,768,1536])) == 3
print(f'PASS: 8086-only instruction audit ({len(ops)} ops), TSR buffer math, 3 tone regions and noise classification.')
print('NOTE: This is not an audible real-hardware or actual SimCity test.')
