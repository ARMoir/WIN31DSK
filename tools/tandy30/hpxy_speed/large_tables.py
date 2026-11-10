#!/usr/bin/env python3
"""Tandy EX RGBI large-table performance trials.

FAST4K: 4096 byte direct input-plane words (four planes x high/low x
        256 words), replacing repeated nibble-index creation.
MAX8K:  8192 byte 12-bit three-plane nibble lookup plus 32 byte intensity
        nibble table, reducing four-plane assembly to two LUT reads/half.
BURST4K: FAST4K direct-plane algorithm in the existing proven two-group
         burst path, including the original 8KiB VRAM-wrap fallback.

These are real alternative algorithms, not padded tables. Both algorithms
use the original I-R-G-B nibble bit order, never I-B-G-R.
"""
from pathlib import Path
import importlib.machinery
import hashlib
import random

def source():
    return importlib.machinery.SourceFileLoader("base_corrected_pixmax",str(Path(__file__).with_name("pixfast.py"))).load_module()

def asm_word(x):
    return "0%04xh" % x  # leading zero makes MASM 5 accept hex beginning A-F

def word4(vals):
    assert len(vals)==4
    return (vals[0]<<4)|vals[1]|(vals[2]<<12)|(vals[3]<<8)

def plane_word(value, color_bit, half):
    base=0 if half=="hi" else 4
    return word4([((value>>(7-base-i))&1)<<color_bit for i in range(4)])

def pack3(n):
    b=n&15
    g=(n>>4)&15
    r=(n>>8)&15
    return word4([(((r>>bit)&1)<<2)|(((g>>bit)&1)<<1)|((b>>bit)&1) for bit in (3,2,1,0)])

def packi(n):
    return word4([((n>>bit)&1)<<3 for bit in (3,2,1,0)])

def make_words(label,words):
    out=[label+" label word"]
    for offset in range(0,len(words),8):
        out.append("    dw "+",".join(asm_word(x) for x in words[offset:offset+8]))
    return "\r\n".join(out)+"\r\n"

PLANE_COLORS=[
    ("b",160,0),("g",80,1),("r",0,2),("i",240,3)
]

def table4():
    out=["; FAST4K/BURST4K: 4096 real LUT bytes, 8 direct raw-plane half words."]
    for channel,_,bit in PLANE_COLORS:
        for half in ("hi","lo"):
            out.append(make_words("pix4_"+channel+"_"+half,
                                  [plane_word(i,bit,half) for i in range(256)]))
    return "\r\n".join(out)

def group4():
    out=["    ; 4KiB table of full-byte -> four pixel contributions.",
         "    ; AX first four pixels; DX next four; BX rebuilt safely.",
         "    ; Original Tandy I-R-G-B color nibble guaranteed."]
    for i,(name,offset,bit) in enumerate(PLANE_COLORS):
        out += ["    mov bl,[si+%d]"%offset,
                "    xor bh,bh",
                "    shl bx,1"]
        verb="mov" if i==0 else "or"
        out += ["    "+verb+" ax,word ptr cs:pix4_"+name+"_hi[bx]",
                "    "+verb+" dx,word ptr cs:pix4_"+name+"_lo[bx]"]
    out += ["    stosw","    mov ax,dx","    stosw"]
    return "\r\n".join(out)+"\r\n"

def table8():
    return ("; MAX8K: 8192 byte 12-bit RGB word table + 32 byte intensity table.\r\n"
            +make_words("pix8_rgb",[pack3(i) for i in range(4096)])
            +make_words("pix8_i",[packi(i) for i in range(16)]))

def nib8(half):
    # BX layout: r nibble in BH low bits; low BG byte contains b nibble in
    # bits0..3 and g nibble in bits4..7. CS lookup index is 2*BX.
    #
    # High half: high nibble of R and B need >>4; high nibble of G
    # already occupies the needed bits4..7.
    # Low half: low B/R nibble is already positioned; G needs <<4.
    out=["    ; combined three-plane %s four-pixel window"%half,
         "    mov bl,[si+160]"]
    if half=="hi":
        out += ["    shr bl,1"]*4
        out += ["    mov dl,[si+80]","    and dl,0f0h",
                "    or bl,dl",
                "    mov bh,[si]",
                "    shr bh,1","    shr bh,1","    shr bh,1","    shr bh,1"]
    else:
        out += ["    and bl,0fh",
                "    mov dl,[si+80]","    and dl,0fh",
                "    shl dl,1","    shl dl,1","    shl dl,1","    shl dl,1",
                "    or bl,dl",
                "    mov bh,[si]","    and bh,0fh"]
    out += ["    shl bx,1",
            "    mov ax,word ptr cs:pix8_rgb[bx]",
            "    mov bl,[si+240]"]
    if half=="hi":
        out += ["    shr bl,1"]*4
    else:
        out += ["    and bl,0fh"]
    out += ["    xor bh,bh","    shl bx,1",
            "    or ax,word ptr cs:pix8_i[bx]",
            "    stosw"]
    return "\r\n".join(out)+"\r\n"

def group8():
    return ("    ; MAX8K: packed RGB from 12-bit index plus intensity nibble.\r\n"
            +nib8("hi")+nib8("lo"))

VARIANTS={
    "fast4k":{"name":"FAST4K","table_bytes":4096,"engine":"direct-plane","burst":False},
    "max8k":{"name":"MAX8K","table_bytes":8224,"engine":"three-plane","burst":False},
    "burst4k":{"name":"BURST4K","table_bytes":4096,"engine":"direct-plane","burst":True},
}

def _replace_one(t,old,new,desc):
    if t.count(old)!=1:
        raise RuntimeError(desc+" anchor count expected 1, got "+str(t.count(old)))
    return t.replace(old,new,1)

def patch(renderer,variant):
    if variant not in VARIANTS:raise ValueError(variant)
    v=VARIANTS[variant]
    pix=source()
    p=Path(renderer)/"EGA/TSOFT.ASM"
    original=p.read_bytes()
    text=original.decode("latin1")
    if "\n" in text.replace("\r\n",""):
        raise RuntimeError("Expected CRLF source")
    old_group=pix.make_group("max").split("xyc_group:\r\n",1)[1]
    old_table=pix.make_table("max")
    if text.count(old_table)!=1:
        raise RuntimeError("Corrected PIXMAX table not found")
    # Apply the audited PIXBURST scaffold only for the burst candidate.
    if v["burst"]:
        burst=importlib.machinery.SourceFileLoader("original_burst",str(Path(__file__).with_name("pixtrials.py"))).load_module()
        text,scaffold=burst.patch_burst(text,pix)
        groups=3   # two unrolled bodies and the exact bank-wrap fallback
    else:
        scaffold=None
        groups=1
    if text.count(old_group)!=groups:
        raise RuntimeError("Original corrected PIXMAX body count %d vs %d"%(text.count(old_group),groups))
    table=table4() if v["engine"]=="direct-plane" else table8()
    new_group=group4() if v["engine"]=="direct-plane" else group8()
    assert new_group.count("    stosw\r\n")==2
    assert len(table)>10000
    text=text.replace(old_group,new_group)
    text=_replace_one(text,old_table,table,"PIXMAX table")
    if text.count(new_group)!=groups:raise RuntimeError("Failed to insert all updated bodies")
    if text.count("pix_lut_pair_hi label word")!=0:
        raise RuntimeError("Old unused table still present")
    p.write_bytes(text.encode("latin1"))
    return {"variant":variant,"name":v["name"],
            "engine":v["engine"],"table_bytes":v["table_bytes"],
            "table_bytes_replaced":1024,
            "burst_loop":v["burst"],
            "burst_scaffold":scaffold,
            "pix_group_replacements":groups,
            "source_before":hashlib.sha256(original).hexdigest(),
            "source_after":hashlib.sha256(text.encode("latin1")).hexdigest(),
            "scope":"Only corrected XY video converter LUT and optional proven burst control",
            "hardware_speed":"NOT_MEASURED"}

def calc4(r,g,b,it):
    src={"b":b,"g":g,"r":r,"i":it}
    out=[]
    for half in ("hi","lo"):
        v=0
        for name,_,shift in PLANE_COLORS:
            v |= plane_word(src[name],shift,half)
        out += [v&255,v>>8]
    return bytes(out)

def calc8(r,g,b,it):
    res=[]
    for sh in (4,0):
        ix=((r>>sh)&15)<<8 | ((g>>sh)&15)<<4 | ((b>>sh)&15)
        v=pack3(ix)|packi((it>>sh)&15)
        res += [v&255,v>>8]
    return bytes(res)

def test():
    pix=source()
    pix.test()
    for plane,expected in ((0,4),(1,2),(2,1),(3,8)):
        ch=[0]*4; ch[plane]=255
        want=bytes([expected*17]*4)
        assert calc4(*ch)==want and calc8(*ch)==want,("color channel",plane)
    # Independent exhaustive four-pixel channel tests, including alternate
    # checkerboard patterns and every 16-color solid in original IRGB order.
    for r in range(16):
      for g in range(16):
       for b in range(16):
        for i in range(16):
            planes=[r*17,g*17,b*17,i*17]
            want=pix.ref(*planes)
            assert calc4(*planes)==want,("4K",planes)
            assert calc8(*planes)==want,("8K",planes)
    rg=random.Random(0x4844)
    for x in range(60000):
        planes=[rg.randrange(256) for _ in range(4)]
        want=pix.ref(*planes)
        assert calc4(*planes)==want,("4k",x,planes)
        assert calc8(*planes)==want,("8k",x,planes)
    assert len(table4().split("    dw "))>400
    assert len(table8().split("    dw "))>500
    assert VARIANTS["fast4k"]["table_bytes"]==8*256*2
    assert VARIANTS["max8k"]["table_bytes"]==(4096+16)*2
    assert "\r\n" in group4() and "\r\n" in group8()
    print("PASS 4KiB raw-plane LUT and 8KiB 12-bit RGB LUT vs independent I-R-G-B reference: 65,536 full color combinations, 60,000 random groups, all 16 solids")

if __name__=="__main__":
    import argparse,json
    ap=argparse.ArgumentParser()
    ap.add_argument("--test",action="store_true")
    ap.add_argument("--source",type=Path)
    ap.add_argument("--variant",choices=list(VARIANTS))
    opts=ap.parse_args()
    test()
    if opts.source and opts.variant:
        print(json.dumps(patch(opts.source,opts.variant),indent=2))
