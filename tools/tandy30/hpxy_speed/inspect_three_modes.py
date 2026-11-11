#!/usr/bin/env python3
"""Inspect pinned PIXMAX and original physical-verified TRIAL7 images for clean release."""
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,"tools/tandy30/int33-test")
from fat16_image import Fat16
P=(Path(sys.argv[1]),Path(sys.argv[2]))
for path in P:
    raw=path.read_bytes()
    fs=Fat16(bytearray(raw))
    print("=== IMAGE",path.name,"SHA",sha256(raw).hexdigest(),"===")
    files=[]
    def walk(cluster=None,prefix=''):
        for _,name,attr,cl,size in fs.entries(cluster):
            if name in (".",".."):continue
            p=prefix+"/"+name
            if attr&16: walk(cl,p)
            else: files.append((p,size))
    walk()
    print("FILE_COUNT",len(files))
    for prefix in ("/","/TANDY88/","/WINXT/","/WINDOWS/","/WINDOWS/SYSTEM/"):
        print("=== DIR",prefix,"===")
        for p,size in files:
            if p.rsplit("/",1)[0]+"/"==prefix:
                print("F",p,"bytes",size)
    for p in ("/PIXMAX.BAT","/T4CGA.BAT","/DIBXY.BAT","/FASTXY.BAT","/XRCGA.BAT","/TANDY4.BAT","/USETR7.BAT","/REST5.BAT",
              "/TANDY88/PIXMAX.INI","/TANDY88/T4CGA.INI","/WINDOWS/SYSTEM.INI","/WINDOWS/WIN.INI",
              "/WINDOWS/PROGMAN.INI","/WIN.BAT"):
        try:
            raw=fs.read(p)
            print("=== FILE",p,"sha",sha256(raw).hexdigest(),"===")
            print(raw[:11000].decode("cp437",errors="replace"))
        except FileNotFoundError:pass
    for name in ("/WINDOWS/SYSTEM/TR73216.DRV","/WINDOWS/SYSTEM/TR53216.DRV","/WINDOWS/SYSTEM/PIXMAX.DRV"):
        try:
            b=fs.read(name);print("=== BINARY",name,len(b),sha256(b).hexdigest())
        except FileNotFoundError:pass
