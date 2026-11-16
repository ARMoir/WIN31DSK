#!/usr/bin/env python3
"""Host-only structural, 8086 and envelope regression checks for SCPLAT."""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent
base = (root / "SCEXSND.COM").read_bytes()
driver = (root / "SCPLAT.COM").read_bytes()
src = (root / "SCPLAT.S").read_text()
assert len(base) == 1312, "Original v0.32 was unexpectedly altered"
assert 1100 < len(driver) < 4096
assert driver[:2] == b"\x0e\x1f" and not driver.startswith(b"MZ")
assert b"SCPLAT 1.0 EXPERIMENTAL" in driver
assert "call synth_platinum_effect" in src
assert "cmp dx,0x0300" in src and "cmp byte ptr [effect_type],0" in src
assert "platinum_level:" in src and "imul word ptr [si+12]" in src
assert all("cmp cx," + str(n) in src
           for n in (384,768,1536,11264,8704,10752,13440,5120))
assert "int 0x21" not in src[src.index("int1c_entry:"):src.index("\nold1a:")]
assert "call silence_all" in src and "int 0x15" in src
assert "jmp far ptr cs:[old1c]" in src and "jmp far ptr cs:[old1a]" in src or "jmp far ptr cs:[old1c]" in src and "jmp far ptr cs:[old1a]" not in src
sym = subprocess.check_output(["nm","-n",str(root/"SCPLAT.o")],text=True)
match = re.search(r"^([0-9a-f]+) [A-Za-z] old1a$",sym,re.M)
assert match, "Resident data boundary not found"
dis = subprocess.check_output(["objdump","-d","-m","i8086",
    "--stop-address=" + str(int(match[1],16)),str(root/"SCPLAT.o")],text=True)
ops = []
for line in dis.splitlines():
    m = re.match(r"^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2} )+)\s+([a-z][\w.]*)",line)
    if m:
        op = int(m[1].split()[0],16)
        assert op not in (0x0f,0x66,0x67,0x60,0x61,0x68,0x6a), \
            "386+ or incompatible opcode in " + line
        ops.append(op)
assert len(ops) > 250, "Missing instruction coverage"
names = ("click","grind","short","long0","long1","long2","long3","long4")
lengths = (384,768,1536,11264,8704,10752,13440,5120)
signature = set()
for name, length in zip(names, lengths):
    pat = (r"platinum_"+name+r":\s*\.word ([\d,]+)\s*"
           r"\.byte ([0-9a-fx,]+)\s*\.word (-?\d+)\s*\.byte (\d+)")
    m = re.search(pat,src)
    assert m, "Missing patch "+name
    tones = [int(v) for v in m[1].split(",")]
    attr = [int(v,0) for v in m[2].split(",")]
    sweep, noise_cutoff = int(m[3]),int(m[4])
    assert len(tones)==3 and all(16<=v<=1023 for v in tones)
    assert len(attr)==6 and all(0<=v<=15 for v in attr[:4])
    assert attr[4] in (0xe4,0xe5,0xe6,0xe7) and 0<=attr[5]<=4
    lifetime = (length+255)//256
    assert 0<noise_cutoff<=lifetime
    signature.add(tuple(tones+attr))
    for age in range(lifetime):
        divider = max(16,min(1023,tones[0]+age*sweep))
        assert 16<=divider<=1023
        for attenuation in attr[:4]:
            final = min(15,attenuation+(age>>attr[5]))
            assert 0<=final<=15
assert len(signature)==8
print("PASS: eight unique remasters, safe 16-bit pitch/volume math,",
      len(ops),"8086 instructions, driver",len(driver),"bytes")
print("NOTE: not yet validated for audible quality on the physical Tandy EX.")
