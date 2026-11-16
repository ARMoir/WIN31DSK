#!/usr/bin/env python3
"""Optional owner-supplied SimCity DOS v1.02/v2.00 archive comparison. No asset output."""
import argparse, struct, zipfile

p=argparse.ArgumentParser()
p.add_argument("v102_zip")
p.add_argument("v200_zip")
a=p.parse_args()
with zipfile.ZipFile(a.v102_zip) as z:
    name=next(n for n in z.namelist() if n.upper().endswith("SOUNDDAT.V4"))
    data=z.read(name)
    assert struct.unpack_from("<H",data)[0]==len(data)-2
    off=2
    lengths=[]
    while off<len(data):
        n=struct.unpack_from("<H",data,off)[0]
        assert n>0 and off+2+n<=len(data)
        lengths.append(n)
        off+=n+2
    assert off==len(data) and lengths==[5632,4352,5376,6720,2560,192,384,768]
    print("v1.02 packed sound bytes:",lengths)
with zipfile.ZipFile(a.v200_zip) as z:
    for effect in ("BULLLOOP","PLOP","EXPLODE","COPTER","POLICE"):
        name=next(n for n in z.namelist() if n.upper().endswith("/"+effect+".VOC"))
        v=z.read(name)
        assert v.startswith(b"Creative Voice File\x1a")
        off=struct.unpack_from("<H",v,20)[0]
        assert v[off]==1
        length=int.from_bytes(v[off+1:off+4],"little")
        rate=1e6/(256-v[off+4])
        print(effect,f"{(length-2)/rate:.3f}s",f"{rate:.0f}Hz")
print("No proprietary audio is written or shipped.")
