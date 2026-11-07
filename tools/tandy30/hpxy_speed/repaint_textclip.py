#!/usr/bin/env python3
"""Conservative text repaint optimization for XR155+DIB on Tandy EX.

Current XDIB/XR155 ALREADY has column-scoped BitBlt/Pixel/Output
presentation. This experimental patch optimizes a different path:
TStrBlt currently copies whole logical row ranges even when its
validated GDI clip rectangle constrains rendering to fewer columns.

Only if text_bounds has proved a non-null, correctly bounded clipping
rectangle and marked dirty=2 do we use the clip's X endpoints for the
existing cursor-safe XY FlushRetainColumns compositor. Other cases
retain EXACT original text_flush fallback. No renderer, text, glyph,
palette, cursor, clip or resource data are changed.

Never claim a physical speed gain from compiling this patch.
"""
from pathlib import Path
import hashlib

def single(source,old,new,label):
    actual=source.count(old)
    if actual!=1:
        raise RuntimeError("RPAINT text clip anchor "+label+" matched "+str(actual)+" times")
    return source.replace(old,new,1)

def patch(renderer):
    path=Path(renderer)/"EGA/TSOFT.ASM"
    raw=path.read_bytes()
    data=raw.decode("latin1")
    if "\n" in data.replace("\r\n",""):
        raise RuntimeError("Refusing mixed line endings in assembly")
    start=data.index("cProc TStrBlt,")
    end=data.index("cProc TExtTextOut,",start)
    section=data[start:end]
    # Narrowing is safe only for exactly the GDI screen-text path whose
    # text_bounds macro has already verified the clip pointer, clip rectangle,
    # count, font layout, no decoration, transform, and vertical bounds.
    section=single(section,
        "    localW rowlast\r\ncBegin\r\n",
        "    localW rowlast\r\n    localW colfirst\r\n    localW collast\r\ncBegin\r\n",
        "two text-window locals")
    section=single(section,
        "    text_bounds 0,0,0\r\n    cCall RStrBlt,",
        """    text_bounds 0,0,0
    ; Only dirty=2 proves the normal bitmap font and full
    ; legal clip rectangle. Cache its horizontal limits before
    ; the GDI renderer executes, avoiding access after it returns.
    cmp dirty,2
    jne TStrBlt_no_clip_columns
    push ax
    push di
    push es
    les di,clip
    mov ax,es:[di].left
    mov colfirst,ax
    mov ax,es:[di].right
    mov collast,ax
    pop es
    pop di
    pop ax
TStrBlt_no_clip_columns:
    cCall RStrBlt,""".replace("\n","\r\n"),
        "validated horizontal text clip bounds")
    section=single(section,
        "    text_flush\r\nTStrBlt_done:",
        """    cmp dirty,2
    jne TStrBlt_generic_flush
    ; Rendered pixels cannot escape the saved clipping rectangle.
    ; A 640-wide clip still redraws the same viewport as before.
    ; Convert pixel X limits to 8-pixel exclusive group endpoints.
    push ax
    push bx
    push cx
    push dx
    mov ax,rowfirst
    mov bx,rowlast
    mov cx,colfirst
    mov dx,collast
    add dx,7
    shr cx,1
    shr cx,1
    shr cx,1
    shr dx,1
    shr dx,1
    shr dx,1
    ; Original XY compositor clamps both axes to the actual
    ; 320x200 viewport and retains the on-screen mouse cursor.
    call FlushRetainColumns
    pop dx
    pop cx
    pop bx
    pop ax
    jmp TStrBlt_done
TStrBlt_generic_flush:
    ; Keep the existing full/row fallbacks for unproven cases.
    text_flush
TStrBlt_done:""".replace("\n","\r\n"),
        "text-clipped partial-row presentation")
    out=data[:start]+section+data[end:]
    if out[:start]!=data[:start] or out[start+len(section):]!=data[end:]:
        raise RuntimeError("Unexpected change outside TStrBlt")
    if "FlushRetainColumns label near" not in data:
        raise RuntimeError("Expected existing cursor-safe XY column converter")
    if out.count("cProc TStrBlt,")!=1 or out.count("cProc TExtTextOut,")!=1:
        raise RuntimeError("Unexpected duplicate driver text proc")
    path.write_bytes(out.encode("latin1"))
    result={
        "scope":"TStrBlt text with already-validated GDI clip rectangle only",
        "method":"present actual clipping X columns plus previously validated Y rows",
        "changed_source":["EGA/TSOFT.ASM, only cProc TStrBlt"],
        "before_source_sha256":hashlib.sha256(raw).hexdigest(),
        "after_source_sha256":hashlib.sha256(out.encode("latin1")).hexdigest(),
        "fallback":"existing text_flush unchanged for invalid/null clip, unusual fonts, other text operations",
        "original_paths_untouched":["TBitBlt","TPixel","TOutput","TExtTextOut",
                                   "RStrBlt renderer","shadow buffers",
                                   "panning","cursor-retention","DIB transfer"],
        "physical_speedup":"UNMEASURED"
    }
    print(result)
    return result
