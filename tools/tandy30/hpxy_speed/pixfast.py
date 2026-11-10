#!/usr/bin/env python3
"""Two all-out 8086/V20-compatible planar-to-Tandy RGBI 4bpp engines.

PIXFAST: 512-byte CS word lookup. Four pixels at a time, two STOSW/group.
PIXMAX: 1024-byte dual CS word lookup. No output-bit shifts.

Only replace the hot xyc_group planar->packed conversion in the XR155+DIB
stage. Keep all viewport logic, staged Y-pan, cursor hide/show, bank masking,
register save frame, and overlay memory behavior unchanged. Build both
in independent staging directories and benchmark them on real Tandy hardware.

Neither version is presumed to be faster without hardware measurements.
"""
from pathlib import Path
import hashlib

ORIGINAL = """xyc_group:
    mov ah,[si]
    mov bl,[si+80]
    mov bh,[si+160]
    mov dh,[si+240]
    rept 4
      get_nibble
      shl al,1
      shl al,1
      shl al,1
      shl al,1
      mov dl,al
      get_nibble
      or al,dl
      stosb
    endm
""".replace("\n","\r\n")

def pack(r,g):
    # For four pixels: p0/p1 in low byte, p2/p3 in high byte.
    # Source bits 3,2,1,0 are left-to-right; red = RGBI bit0,
    # green = bit1. A 16-bit MOV to ES:DI writes them in this order.
    p=[((r>>bit)&1) | (((g>>bit)&1)<<1) for bit in (3,2,1,0)]
    return (p[0]<<4)|p[1]|(p[2]<<12)|(p[3]<<8)

def ref(r,g,b,intensity):
    result=[]
    for n in range(0,8,2):
        vals=[]
        for pixel in (n,n+1):
            bit=7-pixel
            vals.append(( ((intensity>>bit)&1)<<3 )
                       |( ((b>>bit)&1)<<2 )
                       |( ((g>>bit)&1)<<1 )
                       |  ((r>>bit)&1))
        result.append((vals[0]<<4)|vals[1])
    return bytes(result)

def calculated(r,g,b,intensity):
    lut=[pack(i&15,i>>4) for i in range(256)]
    out=[]
    for shift in (4,0):
        rg=lut[((r>>shift)&15)|(((g>>shift)&15)<<4)]
        bi=lut[((b>>shift)&15)|(((intensity>>shift)&15)<<4)]
        word=rg | (bi<<2)
        out += [word&255,word>>8]
    return bytes(out)

def test():
    import random
    assert len(set(pack(r,g) for r in range(16) for g in range(16)))==256
    # Exhaustive four-pixel color plane combinations, all 65,536.
    for red in range(16):
      for green in range(16):
       for blue in range(16):
        for it in range(16):
            x=calculated(red*17,green*17,blue*17,it*17)
            y=ref(red*17,green*17,blue*17,it*17)
            assert x==y,(red,green,blue,it,x.hex(),y.hex())
    rng=random.Random(0x1000E)
    for n in range(250000):
        r,g,b,it=(rng.getrandbits(8) for _ in range(4))
        assert calculated(r,g,b,it)==ref(r,g,b,it)
    for col in range(16):
        v=calculated(*[(255 if (col & (1<<p)) else 0) for p in range(4)])
        assert v==bytes([(col<<4)|col]*4)
    print("PASS 65536 exhaustive 4-pixel combinations, 250000 randomized groups, all 16 solid RGBI colors")

def nibble_index(plane,other,half):
    # Create a byte: high nibble of green or intensity; low nibble
    # of red or blue. Preserve CX (the outer 8-pixel-group count).
    lines=["    mov bl,[si+%d]"%plane]
    if half=="hi":
        lines += ["    shr bl,1"]*4
        lines += ["    mov al,[si+%d]"%other,"    and al,0f0h"]
    else:
        lines += ["    and bl,0fh","    mov al,[si+%d]"%other]
        lines += ["    shl al,1"]*4
    lines += ["    or bl,al","    xor bh,bh","    shl bx,1"]
    return lines

def make_group(variant):
    if variant not in ("fast","max"):
        raise ValueError(variant)
    result=[
        "xyc_group:",
        "    ; PIX%s: 8 packed RGBI pixels per 4 planar bytes; 2 STOSW."%variant.upper(),
        "    ; CS table reads keep DS pointing at the original shadow band.",
        "    ; DX = low-color pair, AX = high-color pair; CX/SI preserved.",
    ]
    for half in ("hi","lo"):
        result += ["    ; "+half+" four-pixel half"]
        result += nibble_index(0,80,half)
        result += ["    mov dx,word ptr cs:pix_lut_rg[bx]"]
        result += nibble_index(160,240,half)
        if variant=="fast":
            result += ["    mov ax,word ptr cs:pix_lut_rg[bx]",
                       "    shl ax,1","    shl ax,1"]
        else:
            result += ["    mov ax,word ptr cs:pix_lut_bi[bx]"]
        result += ["    or ax,dx","    stosw"]
    return "\r\n".join(result)+"\r\n"

def make_table(variant):
    words=[pack(i&15,i>>4) for i in range(256)]
    lines=["    ; 256 lookup entries: nibble-pair to packed 4-pixel RGBI word.",
           "    ; Memory byte order = p0,p1,p2,p3, compatible with STOSW.",
           "pix_lut_rg label word"]
    for j in range(0,256,8):
        lines.append("    dw "+",".join("%04xh"%v for v in words[j:j+8]))
    if variant=="max":
        lines += ["    ; PIXMAX: pre-shifted blue/intensity contribution table.",
                  "pix_lut_bi label word"]
        for j in range(0,256,8):
            lines.append("    dw "+",".join("%04xh"%(v<<2) for v in words[j:j+8]))
    return "\r\n".join(lines)+"\r\n"

def patch(renderer,variant):
    path=Path(renderer)/"EGA/TSOFT.ASM"
    before=path.read_bytes()
    text=before.decode("latin1")
    if "\n" in text.replace("\r\n",""):
        raise RuntimeError("Assembly source must use canonical CRLF")
    if text.count(ORIGINAL)!=1:
        raise RuntimeError("Unexpected conversion anchor, count="+str(text.count(ORIGINAL)))
    if text.count("FlushColumns endp\r\n")!=1:
        raise RuntimeError("Unexpected XY compositor layout")
    assert text.index(ORIGINAL)<text.index("FlushColumns endp\r\n")
    replacement=make_group(variant)
    table=make_table(variant)
    updated=text.replace(ORIGINAL,replacement,1)
    updated=updated.replace("FlushColumns endp\r\n",
            "FlushColumns endp\r\n\r\n"+table,1)
    # Every changed source span is accounted for; no shadow/cursor,
    # bank-switch, pan staging, boundary check or GDI path is modified.
    verify=updated.replace(replacement,ORIGINAL,1).replace(table,"",1)
    verify=verify.replace("FlushColumns endp\r\n\r\n",
                          "FlushColumns endp\r\n",1)
    assert verify==text
    path.write_bytes(updated.encode("latin1"))
    return {
        "variant":variant,
        "table_bytes":512 if variant=="fast" else 1024,
        "before_source_sha256":hashlib.sha256(before).hexdigest(),
        "after_source_sha256":hashlib.sha256(updated.encode("latin1")).hexdigest(),
        "affected_path":"EGA/TSOFT.ASM",
        "modified_code":"xyc_group only",
        "unchanged":["all shadow pixels","all GDI rasterizer code","scroll/pan stage",
                     "cursor overlays","bitblt bounds","screen bank wrap",
                     "full fallback conversion","all DIB input/output"],
        "hardware_speed":"NOT_MEASURED"
    }

if __name__=="__main__":
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument("--test",action="store_true")
    p.add_argument("--source",type=Path)
    p.add_argument("--variant",choices=["fast","max"])
    a=p.parse_args()
    test()
    if a.source and a.variant:
        print(json.dumps(patch(a.source,a.variant),indent=2))
