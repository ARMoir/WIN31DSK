#!/usr/bin/env python3
"""Report actual DOS/WIN 3.0 driver file size and NE minimum allocations.

Reads the original 4-color Microsoft TANDYDSP.DRV and color-correct PIXMAX
directly from a SHA-pinned Tandy CF image. Does not confuse the NE segment
minimums with total Windows conventional memory usage or Windows resources.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

APPROVED_IMAGE_SHA="29881151baf820b3e6453ebb9c024828109abea111e01fe52555c61a840adf73"
KNOWN={
    "TANDY4":{"path":"/WINDOWS/SYSTEM/TANDYDSP.DRV","sha256":"d593c03e52e338074df3c5c70973197bc61deeb72d615459ad90124afea126e0"},
    "PIXMAX":{"path":"/WINDOWS/SYSTEM/PIXMAX.DRV","sha256":"cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c"},
    "DIBXY":{"path":"/WINDOWS/SYSTEM/XDIB.DRV"},
}

def ne_stats(file):
    if len(file)<0x40 or file[0:2]!=b"MZ":
        raise ValueError("Not a DOS MZ/Windows NE executable")
    ne=struct.unpack_from("<I",file,0x3c)[0]
    if ne<0x40 or ne+0x40>len(file) or file[ne:ne+2]!=b"NE":
        raise ValueError("Invalid Windows NE signature")
    n=struct.unpack_from("<H",file,ne+0x1c)[0]
    tab=ne+struct.unpack_from("<H",file,ne+0x22)[0]
    align=struct.unpack_from("<H",file,ne+0x32)[0]
    if n==0 or tab+n*8>len(file):
        raise ValueError("Invalid NE segment table")
    segments=[]
    for idx in range(n):
        file_sector,file_len,flags,minimum=struct.unpack_from("<HHHH",file,tab+idx*8)
        # NE uses 0 to encode a full 64 KiB segment, not zero bytes.
        allocated=minimum if minimum else 65536
        length=file_len if file_len else 65536
        segments.append({"index":idx+1,
                         "minimum_allocation_bytes":allocated,
                         "stored_segment_length":length,
                         "file_offset_bytes":file_sector<<align if file_sector else 0,
                         "flags_hex":"0x%04x"%flags,
                         "data_segment":bool(flags&1)})
    return {
        "file_size_bytes":len(file),
        "ne_segments":n,
        "minimum_ne_segment_allocation_bytes":sum(x["minimum_allocation_bytes"] for x in segments),
        "code_segments_minimum_bytes":sum(x["minimum_allocation_bytes"] for x in segments if not x["data_segment"]),
        "data_segments_minimum_bytes":sum(x["minimum_allocation_bytes"] for x in segments if x["data_segment"]),
        "auto_data_segment":struct.unpack_from("<H",file,ne+0x0e)[0],
        "ne_initial_heap_bytes":struct.unpack_from("<H",file,ne+0x10)[0],
        "ne_initial_stack_bytes":struct.unpack_from("<H",file,ne+0x12)[0],
        "segments":segments,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--image",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    x=ap.parse_args()
    image=x.image.read_bytes()
    actual_image_sha=hashlib.sha256(image).hexdigest()
    if actual_image_sha!=APPROVED_IMAGE_SHA:
        raise RuntimeError("Wrong PIXMAX-owner-tested source CF image: "+actual_image_sha)
    sys.path.insert(0,"tools/tandy30/int33-test")
    from fat16_image import Fat16
    fat=Fat16(bytearray(image))
    results={}
    for label,meta in KNOWN.items():
        b=fat.read(meta["path"])
        digest=hashlib.sha256(b).hexdigest()
        if "sha256" in meta and digest!=meta["sha256"]:
            raise RuntimeError("Wrong driver binary "+label+": "+digest)
        d=ne_stats(b)
        d["path"]=meta["path"]
        d["sha256"]=digest
        results[label]=d
        print("%-9s size=%6d bytes  NE_min=%6d bytes  segments=%d (code=%d data=%d)"%
              (label,d["file_size_bytes"],d["minimum_ne_segment_allocation_bytes"],
               d["ne_segments"],d["code_segments_minimum_bytes"],d["data_segments_minimum_bytes"]))
    budget=192*1024
    results["experiment_limit"]={
        "total_minimum_ne_segments_max_bytes":budget,
        "kiB":192,
        "PIXMAX_headroom_bytes":budget-results["PIXMAX"]["minimum_ne_segment_allocation_bytes"],
        "PIXM4color_headroom_bytes":budget-results["TANDY4"]["minimum_ne_segment_allocation_bytes"],
        "individual_segment_max_bytes":65536,
        "note":"NE minimum allocations only. Resident page/resource heaps, Windows, GDI, kernel, MS-DOS, mouse and app allocations are not included. Runtime free conventional RAM is unknown.",
    }
    assert results["TANDY4"]["file_size_bytes"]==25840
    assert results["TANDY4"]["ne_segments"]==2
    assert results["TANDY4"]["minimum_ne_segment_allocation_bytes"]==20005
    assert results["PIXMAX"]["file_size_bytes"]==61968
    assert results["PIXMAX"]["minimum_ne_segment_allocation_bytes"]==126985
    print("PIXMAX 192KiB NE limit headroom:",results["experiment_limit"]["PIXMAX_headroom_bytes"],"bytes")
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(results,indent=2)+"\n")
    print("PASS original Tandy 4-color and corrected PIXMAX actual-binary NE comparisons")

if __name__=="__main__":main()
