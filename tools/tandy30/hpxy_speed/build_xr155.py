#!/usr/bin/env python3
"""Build opt-in HPXY XR155: bounded 640x256 XY Output flushes.

Uses a pinned old upstream source/view and the exact upstream XR155 patch
modules. Rebuilds from source with Microsoft MASM and LINK4 under DOSBox-X,
keeping existing complete instruction/link audits. No emulator runtime or
physical Tandy qualification is implied.
"""
from pathlib import Path
import importlib.machinery
import hashlib
import json
import struct
import sys

def load(name, path):
    return importlib.machinery.SourceFileLoader(name,str(path)).load_module()

def main():
    if len(sys.argv)!=4:
        raise SystemExit("Usage: build_xr155.py <toolchain-source-view> <dosbox-x> <new-output>")
    repo=Path(sys.argv[1]).resolve()
    dosbox=Path(sys.argv[2]).resolve()
    out=Path(sys.argv[3]).resolve()
    if out.exists():raise SystemExit("Refusing to overwrite an existing output")
    sys.path.insert(0,str(repo/"src/tandysw"))
    b=load("build88_xr155",repo/"src/tandysw/BUILD88.PY")
    p=load("xr155_patch",repo/"experiments/XYRRECT/XRPATCH.PY")
    original_prep=b.baseline.prepare
    original_run=b.bounded_run
    state={}
    def prep(r,o):
        renderer,resources=original_prep(r,o)
        state["renderer"]=renderer
        state["resources"]=resources
        return renderer,resources
    def buildrun(*args,**kwargs):
        if "patched" not in state:
            p.patch(state["renderer"],batch=True)
            state["patched"]=True
            state["post_patch_src_sha256"]=hashlib.sha256(
                (state["renderer"]/"EGA/TSOFT.ASM").read_bytes()).hexdigest()
        return original_run(*args,**kwargs)
    b.baseline.prepare=prep
    b.bounded_run=buildrun
    argv=sys.argv[:]
    try:
        sys.argv=["BUILD88.PY","--repo",str(repo),"--dosbox",str(dosbox),
                  "--out",str(out),"--mode","320x200x16","--ui-profile","compact320"]
        b.main()
    finally:
        sys.argv=argv
        b.baseline.prepare=original_prep
        b.bounded_run=original_run
    if not state.get("patched"):
        raise SystemExit("XR155 source patch did not execute")
    result=json.loads((out/"RESULT.json").read_text())
    if result.get("build")!="PASS":
        raise SystemExit("8086 assembly/link audit did not pass")
    source_driver=out/"TANDY88.DRV"
    blob=source_driver.read_bytes()
    if blob[:2]!=b"MZ":raise SystemExit("Missing MZ executable header")
    ne=struct.unpack_from("<I",blob,0x3c)[0]
    if ne>=len(blob)-64 or blob[ne:ne+2]!=b"NE":
        raise SystemExit("Missing NE driver header")
    count=struct.unpack_from("<H",blob,ne+0x1c)[0]
    offsets=ne+struct.unpack_from("<H",blob,ne+0x22)[0]
    gross=sum(struct.unpack_from("<H",blob,offsets+i*8+6)[0] or 65536 for i in range(count))
    budget=127531
    if gross>budget:
        raise SystemExit(f"XR155 exceeds conservative upstream project memory budget: {gross} > {budget}")
    out_driver=out/"XR155.DRV"
    out_driver.write_bytes(blob)
    report={
      "driver":"XR155.DRV",
      "candidate":"HPXY 640x256 16-color XY + RRECT + synchronous narrow Output",
      "status":"COMPILED_AND_STATICALLY_AUDITED; NO_RUNTIME_OR_PHYSICAL_TEST",
      "source":"astrobleem/oemdisplay-tandy",
      "sha256":hashlib.sha256(blob).hexdigest(),
      "bytes":len(blob),
      "ne_segments":count,
      "ne_gross_alloc_bytes":gross,
      "ne_project_ceiling":budget,
      "source_patch_sha256":state["post_patch_src_sha256"],
      "source_build_report":"RESULT.json; source mode label describes original BUILD88, not effective XY overlay",
      "graphics":{"logical":[640,256,16],"physical":[320,200,16]},
      "other_files":"None; this builder produces only experimental binary and reports"
    }
    (out/"XR155_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
