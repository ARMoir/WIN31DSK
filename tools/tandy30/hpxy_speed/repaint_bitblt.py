#!/usr/bin/env python3
"""Narrow the XR155+DIB TBitBlt viewport presentation to proven X/Y bounds.

Experimental private staged-source patch. The original GDI BitBlt renderer,
ROP semantics, bitmap source, shadow-pixel writes and identity SRCCOPY full
resynchronization remain unchanged. Only eligible already-screen-clipped
destination BitBlt presentation changes from full-width FlushRows to
bounded FlushRetainColumns; the guarded full-screen fallback remains intact.

This is not a hardware-verified optimization. A successful MASM build is only
a static sanity check. Physical framebuffer and timing tests are required.
"""
from pathlib import Path
import hashlib

BLT_BEFORE = """    push ax
    push bx
    cmp resync,0
    jne TBitBlt_full
    mov bx,xextent
    or bx,bx
    jle TBitBlt_full
    mov ax,dstx
    or ax,ax
    js TBitBlt_full
    add ax,bx
    jo TBitBlt_full
    cmp ax,SCREEN_WIDTH
    jg TBitBlt_full
    mov bx,yextent
    or bx,bx
    jle TBitBlt_full
    mov ax,dsty
    or ax,ax
    js TBitBlt_full
    add bx,ax
    jo TBitBlt_full
    cmp bx,SCREEN_HEIGHT
    jg TBitBlt_full
    call FlushRows
    jmp short TBitBlt_flushed
TBitBlt_full:
    call FlushShadow
TBitBlt_flushed:
    pop bx
    pop ax
""".replace("\n","\r\n")

BLT_AFTER = """    ; RPAINT: preserve renderer result and all working registers.
    push ax
    push bx
    push cx
    push dx
    cmp resync,0
    jne TBitBlt_full
    mov bx,xextent
    or bx,bx
    jle TBitBlt_full
    mov ax,dstx
    or ax,ax
    js TBitBlt_full
    add ax,bx
    jo TBitBlt_full
    cmp ax,SCREEN_WIDTH
    jg TBitBlt_full
    ; Preserve proven, exclusive, right pixel endpoint.
    mov dx,ax
    mov bx,yextent
    or bx,bx
    jle TBitBlt_full
    mov ax,dsty
    or ax,ax
    js TBitBlt_full
    add bx,ax
    jo TBitBlt_full
    cmp bx,SCREEN_HEIGHT
    jg TBitBlt_full
    ; AX=first row, BX=exclusive last row, CX/DX=8-pixel column range.
    ; Both X endpoints were checked in the logical 640-wide coordinate
    ; system, so adding 7 to the last endpoint cannot wrap.
    mov cx,dstx
    shr cx,1
    shr cx,1
    shr cx,1
    add dx,7
    shr dx,1
    shr dx,1
    shr dx,1
    ; The existing cursor-retention compositor clips the rectangle to
    ; the present 320x200 viewport and respects the 640x256 shadow bands.
    call FlushRetainColumns
    jmp short TBitBlt_flushed
TBitBlt_full:
    ; Do not weaken the identity-SRCCOPY full-resynchronization contract
    ; or the out-of-bounds fallback for less trusted GDI inputs.
    call FlushShadow
TBitBlt_flushed:
    pop dx
    pop cx
    pop bx
    pop ax
""".replace("\n","\r\n")

def patch(renderer):
    p=Path(renderer)/"EGA/TSOFT.ASM"
    orig=p.read_bytes()
    text=orig.decode("latin1")
    if "\n" in text.replace("\r\n",""):
        raise RuntimeError("Refusing non-CRLF assembly source")
    if text.count(BLT_BEFORE)!=1:
        begin=text.index("cProc TBitBlt,")
        end=text.index("cProc TOutput,",begin)
        raise RuntimeError("Unexpected TBitBlt source; exact generated block follows:\\n"+text[begin:end][-4400:])
    if text.count("FlushRetainColumns proc near")!=0 and text.count("FlushRetainColumns label near")!=1:
        raise RuntimeError("Unexpected cursor-retain XY compositor symbol")
    after=text.replace(BLT_BEFORE,BLT_AFTER,1)
    if after.count(BLT_AFTER)!=1:raise RuntimeError("Failed unique patch check")
    if after.replace(BLT_AFTER,BLT_BEFORE,1)!=text:
        raise RuntimeError("Unexpected source edits outside guarded BitBlt")
    p.write_bytes(after.encode("latin1"))
    result={
        "feature":"narrow logical-X BitBlt rectangle repaint only",
        "prepatched_source_sha256":hashlib.sha256(orig).hexdigest(),
        "postpatched_source_sha256":hashlib.sha256(after.encode("latin1")).hexdigest(),
        "scope":"TBitBlt screen destination proven valid positive X/Y extents only",
        "changed_asm_files":["EGA/TSOFT.ASM"],
        "fallback":"original full FlushShadow when bounds invalid, resync requested or incomplete",
        "untouched":["BitBlt renderer","shadow bytes","ROP","DIB converters","font renderer",
                     "Output bounds","identity screen SRCCOPY","panning","viewport",
                     "cursor-retention code","all original binaries"],
        "hardware_qualification":"NOT_TESTED"
    }
    print(result)
    return result
