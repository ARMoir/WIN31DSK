#!/usr/bin/env python3
"""Build aggressive independent PIXBURST / PIXV20 / PIXDIRTY trial.

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
    if len(sys.argv)!=5 or sys.argv[4] not in ("burst","v20","dirty"):
        raise SystemExit("Usage: build_pixtrials.py <toolchain-view> <dosbox-x> <new-output> <burst|v20|dirty>")
    variant=sys.argv[4]
    repo=Path(sys.argv[1]).resolve()
    dosbox=Path(sys.argv[2]).resolve()
    out=Path(sys.argv[3]).resolve()
    if out.exists():raise SystemExit("Refuse existing output")
    sys.path.insert(0,str(repo/"src/tandysw"))
    b=load("build88_dib",repo/"src/tandysw/BUILD88.PY")
    xy=load("xr155_xy",repo/"experiments/XYRRECT/XRPATCH.PY")
    dib=load("xr155_dib",repo/"src/hpxydib/DIB.PY")
    pixel=load("rgbilut",Path(__file__).with_name("pixfast.py"))
    trials=load("pixtrials",Path(__file__).with_name("pixtrials.py"))
    pixel.test()
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
            pix= pixel.patch(renderer,"max")
            trial=trials.patch(renderer,variant)
            after={
                p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (renderer/"BMC_ETI.ASM",renderer/"BMC_ITE.ASM")
            }
            if any(before[n]==after[n] for n in before):
                raise SystemExit("No DIB conversion change for "+str(before))
            state.update(patched=True,pre_dib=before,post_dib=after,pixel=pix,trial=trial)
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
    # The sum is an estimate of NE load-time minimum segment allocations,
    # not a measurement of free conventional RAM or Windows loader overhead.
    # A 16-bit NE segment can never have >65536 bytes of minimum allocation.
    segments=[]
    for idx in range(n):
        disk_off,stored_size,flags,min_raw=struct.unpack_from("<HHHH",binary,off+8*idx)
        min_bytes=min_raw or 65536
        segments.append(dict(index=idx+1,minimum_bytes=min_bytes,
                             stored_bytes=stored_size or 65536,
                             flags_hex="0x%04x"%flags))
    gross=sum(seg["minimum_bytes"] for seg in segments)
    # User-approved high-risk trial budget: 192 KiB total minimum NE segments.
    # Preserve individual 16-bit segments, correct colors, I/O and rollback.
    budget=192*1024
    if gross>budget:
        raise SystemExit("Experimental NE allocation exceeds 192 KiB maximum: %d > %d"%(gross,budget))
    basename={"burst":"PIXBURST","v20":"PIXV20","dirty":"PIXDIRTY"}[variant]
    (out/(basename+".DRV")).write_bytes(binary)
    result=dict(candidate="Owner-tested corrected PIXMAX plus aggressive trial "+variant,
                mode="640x256 logical panning, 320x200 16-color view",
                runtime="NOT_TESTED_ON_PHYSICAL_TANDY",
                original_runtime_driver="PIXMAX.DRV",
                original_runtime_sha256="cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c",
                driver=basename+".DRV",driver_bytes=len(binary),
                sha256=hashlib.sha256(binary).hexdigest(),
                ne_segments=n,ne_gross_alloc_bytes=gross,
                experimental_ne_budget=budget,
                experimental_ne_budget_kib=192,
                exceeds_prior_conservative_budget=(gross>127531),
                prior_experimental_limit_bytes=130000,
                ne_segment_allocations=segments,
                memory_scope="NE segment minimum only, not actual runtime conventional RAM",
                raw_driver_file_bytes=len(binary),
                before_dib_files=state["pre_dib"],after_dib_files=state["post_dib"],
                pixel_converter=state["pixel"],experimental_patch=state["trial"],
                source_build_report="RESULT.json describes base build flags, not final XY/DIB overlay")
    if variant=="v20":
        # Explicit ISA test for intentionally raw-encoded 80186/NEC V20 instructions.
        # The original 8086 listing audit does not decode these DB bytes.
        counts={"shr_bl_4":binary.count(bytes.fromhex("C0 EB 04")),
                "shl_al_4":binary.count(bytes.fromhex("C0 E0 04"))}
        if counts["shr_bl_4"]<2 or counts["shl_al_4"]<2:
            raise SystemExit("PIXV20 required V20 opcode sequences absent: "+repr(counts))
        result["V20_only_opcode_audit"]=counts
    (out/(basename+"_REPORT.json")).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
