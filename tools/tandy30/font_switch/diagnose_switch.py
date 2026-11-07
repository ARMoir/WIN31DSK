#!/usr/bin/env python3
"""Read-only FAT16 forensics on the original four-color release."""
from pathlib import Path
import sys,struct

if len(sys.argv)!=2:sys.exit("Usage: diagnose_switch.py IMAGE.img")
b=Path(sys.argv[1]).read_bytes()
part=struct.unpack_from("<I",b,454)[0]*512
bps=struct.unpack_from("<H",b,part+11)[0]
spc=b[part+13];nfats=b[part+16]
roots=struct.unpack_from("<H",b,part+17)[0]
res=struct.unpack_from("<H",b,part+14)[0]
spf=struct.unpack_from("<H",b,part+22)[0]
fat=part+res*bps
root=fat+nfats*spf*bps
data=root+((roots*32+bps-1)//bps)*bps
def chain(start):
    c=start;seen=set()
    while 2<=c<0xfff8 and c not in seen:
        yield c;seen.add(c)
        c=struct.unpack_from("<H",b,fat+c*2)[0]
def records(cl=None):
    raw=b[root:root+roots*32] if cl is None else b"".join(b[data+(i-2)*spc*bps:data+(i-1)*spc*bps] for i in chain(cl))
    for i in range(0,len(raw),32):
        x=raw[i:i+32]
        if x[0]==0:break
        if x[0]==229 or x[11]==0xf:continue
        n=x[:8].decode("cp437").rstrip()
        e=x[8:11].decode("cp437").rstrip()
        yield (n+"."+e if e else n),x[11],struct.unpack_from("<H",x,26)[0],struct.unpack_from("<I",x,28)[0]
dirs={n.upper():(a,c,sz) for n,a,c,sz in records()}
print("Root dirs",[(n,hex(a),c) for n,(a,c,sz) in dirs.items() if n in ("TANDY88","WINDOWS")])
for dn,targets in {
    "WINDOWS":("SYSTEM.INI","WIN.INI"),
    "TANDY88":("SYSHPXY.INI","XRXT.INI","T4CGA.INI","T4XT.INI","WINXR.INI","WIN4.INI"),
}.items():
    cl=dirs[dn][1]
    sub={n.upper():(a,c,sz) for n,a,c,sz in records(cl)}
    for item in targets:
        if item not in sub:
            print("MISSING:",dn,item, "AVAILABLE:",list(sub))
            continue
        attr,c,sz=sub[item]
        print(dn,item,"attrs",hex(attr),"cluster",c,"size",sz,"READ_ONLY",bool(attr&1))
for fn in ("GOLDXY.BAT","T4CGA.BAT","TANDY4.BAT"):
    print(fn, dirs.get(fn))
print("Total bytes",len(b))
