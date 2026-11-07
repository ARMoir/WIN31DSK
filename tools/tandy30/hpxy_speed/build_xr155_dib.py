#!/usr/bin/env python3
"""Build experimental XR155 + fixed-group DIB import/export unrolling.

Reproduce the exact existing XR155 source pipeline and add the upstream
hpxydib/DIB.PY optimization after the XR155 overlay, before the 8086
MASM/LINK and instruction audit. This is NOT an on-device speed measurement.
"""
from pathlib import Path
import importlib.machinery
import hashlib
import json
import struct
import sys

def load(name,path):
    return importlib.machinery.SourceFileLoader(name,str(path)).load_module()

def main():
    if len(sys.argv)!=4:
        raise SystemExit("Usage: build_xr155_dib.py <toolchain-view> <dosbox-x> <new-output>")
    repo=Path(sys.argv[1]).resolve()
    dosbox=Path(sys.argv[2]).resolve()
    out=Path(sys.argv[3]).resolve()
    if out.exists():raise SystemExit("Refuse existing output")
    sys.path.insert(0,str(repo/"src/tandysw"))
    b=load("build88_dib",repo/"src/tandysw/BUILD88.PY")
    xy=load("xr155_xy",repo/"experiments/XYRRECT/XRPATCH.PY")
    dib=load("xr155_dib",repo/"src/hpxydib/DIB.PY")
    original_prep=b.baseline.prepare
    original_run=b.bounded_run
    state={}
    def prep(r,o):
        renderer,res=original_prep(r,o)
        state["renderer"]=renderer
        return renderer,res
    def run(*args,**kwargs):
        if not state.get("patched"):
            renderer=state["renderer"]
            xy.patch(renderer,batch=True)
            before={
                p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (renderer/"BMC_ETI.ASM",renderer/"BMC_ITE.ASM")
            }
            dib.patch(renderer)
            after={
                p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (renderer/"BMC_ETI.ASM",renderer/"BMC_ITE.ASM")
            }
            if any(before[n]==after[n] for n in before):
                raise SystemExit("No DIB conversion change for "+str(before))
            state.update(patched=True,pre_dib=before,post_dib=after)
        return original_run(*args,**kwargs)
    b.baseline.prepare=prep
    b.bounded_run=run
    oldargs=sys.argv[:]
    try:
        sys.argv=["BUILD88.PY","--repo",str(repo),"--dosbox",str(dosbox),
                  "--out",str(out),"--mode","320x200x16","--ui-profile","compact320"]
        b.main()
    finally:
        sys.argv=oldargs
        b.baseline.prepare=original_prep
        b.bounded_run=original_run
    if not state.get("patched"):raise SystemExit("Patch never applied")
    report=json.loads((out/"RESULT.json").read_text())
    if report.get("build")!="PASS":raise SystemExit("8086/NE audit failed")
    driver=out/"TANDY88.DRV"
    binary=driver.read_bytes()
    if binary[:2]!=b"MZ":raise SystemExit("Not a Windows driver executable")
    ne=struct.unpack_from("<I",binary,0x3c)[0]
    if binary[ne:ne+2]!=b"NE":raise SystemExit("Not Windows NE driver")
    n=struct.unpack_from("<H",binary,ne+0x1c)[0]
    off=ne+struct.unpack_from("<H",binary,ne+0x22)[0]
    gross=sum(struct.unpack_from("<H",binary,off+8*i+6)[0] or 65536 for i in range(n))
    if gross>127531:raise SystemExit("Above pinned NE budget: "+str(gross))
    (out/"XDIB.DRV").write_bytes(binary)
    result=dict(candidate="XR155 + upstream DIB four-group unrolling",
                mode="640x256 logical panning, 320x200 16-color view",
                runtime="NOT_TESTED_ON_PHYSICAL_TANDY",
                original_runtime_driver="XR155.DRV",
                original_runtime_sha256="ae2d06f69ff68e64f099c3e0af79028e40e7dca89bd442de23eb18d36be4dca1",
                driver="XDIB.DRV",driver_bytes=len(binary),
                sha256=hashlib.sha256(binary).hexdigest(),
                ne_segments=n,ne_gross_alloc_bytes=gross,ne_budget_bytes=127531,
                before_dib_files=state["pre_dib"],after_dib_files=state["post_dib"],
                source_build_report="RESULT.json describes base build flags, not final XY/DIB overlay")
    (out/"XDIB_REPORT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
