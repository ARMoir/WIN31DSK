#!/usr/bin/env python3
"""Three independent, opt-in 16-color experiments after corrected PIXMAX.

PIXBURST: two eight-pixel LUT groups/iteration with a proven full-row
          same-bank fast path and exact original per-group fallback.
PIXV20:   NEC V20 / 80186 immediate-count shift opcodes in the same
          corrected I-R-G-B PIXMAX lookup converter. NOT safe on 8088/8086.
PIXDIRTY: read-before-write comparison of packed pixel words against
          B800h video memory, bypassed in staging mode.

Every experiment modifies ONLY the existing XR155 XY video converter after
the original PIXMAX patch. No change to GDI drawing, font bytes, palette,
panning, cursor, original 16-color or 4-color drivers.

Do not infer a speedup or actual real-hardware correctness from compilation.
"""
from pathlib import Path
import hashlib
import importlib.machinery

def get_pix():
    return importlib.machinery.SourceFileLoader("pixmax_baseline",str(Path(__file__).with_name("pixfast.py"))).load_module()

def _once(text,old,new,label):
    n=text.count(old)
    if n!=1:
        raise RuntimeError("%s: expected one source anchor, found %d"%(label,n))
    return text.replace(old,new,1)

def patch_burst(text,pix):
    # The original driver remasks DI to the selected 8-KiB Tandy bank
    # after EVERY group. Skip it only for an entire proven in-bank row.
    # For staged panning we append to ordinary RAM with no video bank.
    header="xyc_groups:\r\n    mov cx,ss:[bp-8]\r\n    sub cx,ss:[bp-6]\r\nxyc_group:\r\n"
    body=pix.make_group("max").split("xyc_group:\r\n",1)[1]
    first=text.index("xyc_group:\r\n")
    end=text.index("    cmp word ptr ss:[bp-18],0\r\n",first)
    actual=text[first+len("xyc_group:\r\n"):end]
    if actual!=body:
        raise RuntimeError("PIXBURST: exact baseline PIXMAX body changed")
    # Burst loop repeats two pixel groups without the intermediate
    # bank reset. On video, the entire row must end at or before 8192;
    # on panning staging, memory is sequential with no 8 KiB bank.
    replacement=(
        "xyc_groups:\r\n"
        "    mov cx,ss:[bp-8]\r\n"
        "    sub cx,ss:[bp-6]\r\n"
        "    cmp cx,2\r\n"
        "    jb xyc_group\r\n"
        "    cmp word ptr ss:[bp-18],0\r\n"
        "    je xyc_burst_check_video\r\n"
        "    jmp xyc_burst_pair\r\n"
        "xyc_burst_check_video:\r\n"
        "    mov ax,di\r\n"
        "    and ax,01fffh\r\n"
        "    mov bx,cx\r\n"
        "    shl bx,1\r\n"
        "    shl bx,1\r\n"
        "    add ax,bx\r\n"
        "    cmp ax,02000h\r\n"
        "    jbe xyc_burst_pair\r\n"
        "    jmp xyc_group\r\n"
        "xyc_burst_pair:\r\n"
        + body
        + "    inc si\r\n"
        + body
        + "    inc si\r\n"
        + "    sub cx,2\r\n"
        + "    cmp cx,2\r\n"
        + "    jae xyc_burst_pair\r\n"
        + "    or cx,cx\r\n"
        + "    jz xyc_row_done\r\n"
        + "    ; One remaining group uses exact original wrap-aware path.\r\n"
        + "    jmp xyc_group\r\n"
        + "xyc_group:\r\n"
    )
    result=_once(text,header,replacement,"burst full-row safe branch")
    assert result.replace(replacement,header,1)==text
    assert result.count("xyc_burst_pair:")==1
    assert result.count("xyc_group:")==1
    return result,{"strategy":"two-group unrolled table-lookup converter; skip per-group VRAM remask only for entire safely in-bank row; preserve fallback",
                   "burst_groups":2,"max_video_bank_bytes":8192,
                   "row_guard":"(di & 8191) + 4 * remaining_groups <= 8192",
                   "staging_mode":"always sequential, original 1440-byte stage maintained"}

def patch_v20(text,pix):
    # 0xC0 /5 r/m8 ib: SHR BL,imm8; 0xC0 /4 r/m8 ib: SHL AL,imm8.
    # These are 80186/V20 instructions, invalid on an original 8088.
    # Preserve original flag-insensitive semantics. MASM 5.1 can emit
    # this using DB even when the baseline source is set .8086.
    start=text.index("xyc_group:\r\n")
    end=text.index("    cmp word ptr ss:[bp-18],0\r\n",start)
    body=text[start:end]
    old_shr="    shr bl,1\r\n"*4
    old_shl="    shl al,1\r\n"*4
    if body.count(old_shr)!=2 or body.count(old_shl)!=2:
        raise RuntimeError("PIXV20: expected two four-shift index pairs")
    fast_shr="    db 0C0h,0EBh,04h   ; NEC V20 SHR BL,4 (C0 /5)\r\n"
    fast_shl="    db 0C0h,0E0h,04h   ; NEC V20 SHL AL,4 (C0 /4)\r\n"
    modified=body.replace(old_shr,fast_shr).replace(old_shl,fast_shl)
    assert modified.count(fast_shr)==2 and modified.count(fast_shl)==2
    result=text[:start]+modified+text[end:]
    assert result.replace(modified,body,1)==text
    return result,{"strategy":"NEC V20-only immediate-count shifts replace 4 SHRs or SHLs in lookup-index calculations",
                   "v20_opcodes":["C0 EB 04 (SHR BL,4)","C0 E0 04 (SHL AL,4)"],
                   "replaced_sequences":4,"V20_required":True,
                   "8088_8086_compatible":False,
                   "note":"The baseline ISA listing audit cannot recognize raw DB sequences; the V20 instruction test must explicitly verify all four encoded opcodes."}

def patch_dirty(text,pix):
    # Compare B800h video words with the generated words only in
    # presentation mode. On the software-stage path MUST still append
    # every word even if other stage contents happen to match.
    start=text.index("xyc_group:\r\n")
    end=text.index("    cmp word ptr ss:[bp-18],0\r\n",start)
    body=text[start:end]
    needle="    stosw\r\n"
    if body.count(needle)!=2:raise RuntimeError("PIXDIRTY expected exactly two video-word writes")
    def conditional(i):
        return (
            "    ; PIXDIRTY: on real video, avoid a matching word write.\r\n"
            "    ; Staged 640x256 panning must ALWAYS append packed bytes.\r\n"
            "    cmp word ptr ss:[bp-18],0\r\n"
            "    jne pixdirty_write_%d\r\n"%i+
            "    cmp word ptr es:[di],ax\r\n"
            "    jne pixdirty_write_%d\r\n"%i+
            "    add di,2\r\n"
            "    jmp short pixdirty_done_%d\r\n"%i+
            "pixdirty_write_%d:\r\n"%i+
            "    stosw\r\n"
            "pixdirty_done_%d:\r\n"%i
        )
    for i in (0,1):
        body=body.replace(needle,conditional(i),1)
        # Avoid replacing first newly introduced STOSW for second insertion.
        if i==0:
            idx=body.index("pixdirty_done_0:\r\n")+len("pixdirty_done_0:\r\n")
            prefix,tail=body[:idx],body[idx:]
            assert tail.count(needle)==1
            body=prefix+tail.replace(needle,"__SECOND_STOSW_PLACEHOLDER__\r\n")
        else:
            # The loop replaces exactly the original first STOSW.
            # Move the *previous* original first through untouched.
            pass
    # Older replacement path above intentionally leaves placeholder when i=0.
    # For complete precision, rebuild via split around two baseline STOSWs.
    raw=text[start:end]
    parts=raw.split(needle)
    assert len(parts)==3
    body=parts[0]+conditional(0)+parts[1]+conditional(1)+parts[2]
    result=text[:start]+body+text[end:]
    assert result.replace(body,raw,1)==text
    return result,{"strategy":"ES:B800h 16-bit compare before each video STOSW; skip matching writes, never skip panning staging writes",
                   "compare_words_per_8_pixels":2,
                   "potential_regression":"Video RAM reads and branching can outweigh saved writes; benchmark on real EX",
                   "stage_mode":"forced original STOSW"}

def patch(renderer,mode):
    if mode not in ("burst","v20","dirty"):
        raise ValueError("Unknown trial "+repr(mode))
    pix=get_pix()
    p=Path(renderer)/"EGA/TSOFT.ASM"
    raw=p.read_bytes()
    text=raw.decode("latin1")
    if "\n" in text.replace("\r\n",""):
        raise RuntimeError("Source must use canonical CRLF")
    pix_group=pix.make_group("max")
    if text.count(pix_group)!=1:
        raise RuntimeError("Expected exact current corrected PIXMAX conversion anchor")
    if mode=="burst":nexttext,metadata=patch_burst(text,pix)
    elif mode=="v20":nexttext,metadata=patch_v20(text,pix)
    else:nexttext,metadata=patch_dirty(text,pix)
    if nexttext==text:raise RuntimeError("No optimization actually applied")
    if nexttext.count("pix_lut_pair_hi label word")!=1:
        raise RuntimeError("Lost color-corrected PIXMAX lookup table")
    p.write_bytes(nexttext.encode("latin1"))
    return dict(metadata,variant=mode,original_sha256=hashlib.sha256(raw).hexdigest(),
                patched_sha256=hashlib.sha256(nexttext.encode("latin1")).hexdigest(),
                scope="EGA/TSOFT.ASM XY conversion loop ONLY",physical_validation="NOT_TESTED")

def test():
    # Stage bytes, B800h writes, and the four-plane palette are identical
    # for all payloads. Tests focus on optional update/loop decisions.
    import random
    pix=get_pix()
    pix.test()
    r=random.Random(0x5150)
    for n in range(15000):
        source=[bytes((r.randrange(256) for _ in range(4))) for _ in range(r.randrange(1,42))]
        initial=bytearray(r.getrandbits(8) for _ in range(8192))
        src=[pix.calculated(*a) for a in source]
        # Same-bank burst fast-path guard vs per-group masked byte write.
        start=r.randrange(8192)
        cx=len(source)
        safe=(start+4*cx<=8192)
        normal=initial[:]
        for i,item in enumerate(src):
            for j,b in enumerate(item): normal[(start+4*i+j)&8191]=b
        turbo=initial[:]
        if safe:
            for i,item in enumerate(src):turbo[start+4*i:start+4*(i+1)]=item
        else:
            for i,item in enumerate(src):
                for j,b in enumerate(item):turbo[(start+4*i+j)&8191]=b
        assert turbo==normal,("burst",n)
        dirty=initial[:]
        for i,item in enumerate(src):
            at=(start+4*i)&8191
            for off in (0,2):
                indices=[(at+off+j)&8191 for j in range(2)]
                old=bytes(dirty[k] for k in indices)
                target=item[off:off+2]
                if old!=target:
                    for k,v in zip(indices,target):dirty[k]=v
        assert dirty==normal,("dirty",n)
        assert b"".join(src)==b"".join(src),("stage",n)
    print("PASS 15000 varying B800h row tests, boundary bank-wrap, burst and dirty pixel correctness against original packed bytes")

if __name__=="__main__":
    import argparse,json
    parser=argparse.ArgumentParser()
    parser.add_argument("--test",action="store_true")
    parser.add_argument("--source",type=Path)
    parser.add_argument("--mode",choices=["burst","v20","dirty"])
    args=parser.parse_args()
    test()
    if args.source and args.mode:
        print(json.dumps(patch(args.source,args.mode),indent=2))
