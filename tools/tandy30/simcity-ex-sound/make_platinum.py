#!/usr/bin/env python3
"""Generate experimental SCPLAT.S from unchanged SCEXSND v0.32 source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "SCEXSND.S"
DEST = ROOT / "SCPLAT.S"

DETECTION = """    /* Original SimCity DOS v1.02: eight distinct expanded sound blocks.
       Only recognized at its verified DX=0300h playback rate. */
    mov byte ptr [effect_type],0
    mov byte ptr [effect_age],0
    cmp dx,0x0300
    je platinum_recognize
    jmp generic_play
platinum_recognize:
    cmp cx,384
    jne platinum_len_768
    mov byte ptr [effect_type],1
    jmp generic_play
platinum_len_768:
    cmp cx,768
    jne platinum_len_1536
    mov byte ptr [effect_type],2
    jmp generic_play
platinum_len_1536:
    cmp cx,1536
    jne platinum_len_11264
    mov byte ptr [effect_type],3
    jmp generic_play
platinum_len_11264:
    cmp cx,11264
    jne platinum_len_8704
    mov byte ptr [effect_type],4
    jmp generic_play
platinum_len_8704:
    cmp cx,8704
    jne platinum_len_10752
    mov byte ptr [effect_type],5
    jmp generic_play
platinum_len_10752:
    cmp cx,10752
    jne platinum_len_13440
    mov byte ptr [effect_type],6
    jmp generic_play
platinum_len_13440:
    cmp cx,13440
    jne platinum_len_5120
    mov byte ptr [effect_type],7
    jmp generic_play
platinum_len_5120:
    cmp cx,5120
    jne platinum_unknown
    mov byte ptr [effect_type],8
platinum_unknown:
"""

ENGINE = """/* Eight distinct, table-driven PSG patches; no copyrighted PCM included.
   Format: 3x 16-bit divider, 3 tone attenuation bytes, noise attenuation,
   noise latch, fade shift, signed divider sweep/tick, noise lifetime ticks.
   The original block identities and acoustics require real EX confirmation. */
synth_platinum_effect:
    push ax
    push bx
    push cx
    push dx
    push si
    cmp byte ptr [caller_volume],0
    jne platinum_audible
    call silence_all
    jmp platinum_done
platinum_audible:
    xor bh,bh
    mov bl,[effect_type]
    dec bx
    shl bx,1
    mov si,[platinum_patch_ptrs+bx]
    mov al,[effect_age]
    xor ah,ah
    imul word ptr [si+12]
    add ax,[si]
    cmp ax,16
    jge platinum_check_top
    mov ax,16
platinum_check_top:
    cmp ax,1023
    jle platinum_pitch_ready
    mov ax,1023
platinum_pitch_ready:
    mov bx,ax
    mov al,0x80
    call set_tone
    mov bx,[si+2]
    mov al,0xa0
    call set_tone
    mov bx,[si+4]
    mov al,0xc0
    call set_tone
    mov cl,[si+11]
    mov al,[effect_age]
    shr al,cl
    mov [effect_fade],al
    mov bl,[si+6]
    mov bh,0x90
    call platinum_level
    mov bl,[si+7]
    mov bh,0xb0
    call platinum_level
    mov bl,[si+8]
    mov bh,0xd0
    call platinum_level
    mov al,[effect_age]
    cmp al,[si+14]
    jb platinum_noise_active
    mov dx,0xc0
    mov al,0xff
    out dx,al
    jmp platinum_noise_done
platinum_noise_active:
    mov dx,0xc0
    mov al,[si+10]
    out dx,al
    mov al,[effect_fade]
    shl al,1
    mov [effect_fade],al
    mov bl,[si+9]
    mov bh,0xf0
    call platinum_level
platinum_noise_done:
    inc byte ptr [effect_age]
platinum_done:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

/* BL=base 0..15, BH=PSG attenuation register high nibble.
   All layers decay independently; upper layers are intentionally softer. */
platinum_level:
    push ax
    push bx
    push dx
    mov al,7
    sub al,[caller_volume]
    add al,bl
    add al,[effect_fade]
    cmp al,15
    jbe platinum_level_in_range
    mov al,15
platinum_level_in_range:
    or al,bh
    mov dx,0xc0
    out dx,al
    pop dx
    pop bx
    pop ax
    ret

platinum_patch_ptrs:
    .word platinum_click,platinum_grind,platinum_short
    .word platinum_long0,platinum_long1,platinum_long2
    .word platinum_long3,platinum_long4
platinum_click:
    .word 140,225,340
    .byte 3,7,12,8,0xe7,0
    .word 20
    .byte 1
platinum_grind:
    .word 850,720,590
    .byte 2,5,9,8,0xe5,2
    .word 65
    .byte 3
platinum_short:
    .word 280,390,560
    .byte 3,6,11,10,0xe6,2
    .word 18
    .byte 3
platinum_long0:
    .word 740,650,310
    .byte 3,7,10,9,0xe5,3
    .word -5
    .byte 40
platinum_long1:
    .word 540,280,910
    .byte 3,7,11,9,0xe6,3
    .word 6
    .byte 29
platinum_long2:
    .word 270,480,820
    .byte 4,8,11,6,0xe7,3
    .word 7
    .byte 38
platinum_long3:
    .word 640,490,920
    .byte 2,6,10,7,0xe5,3
    .word 7
    .byte 48
platinum_long4:
    .word 180,360,690
    .byte 3,7,11,8,0xe6,2
    .word -5
    .byte 14

"""

def replace_once(src, old, new):
    if src.count(old) != 1:
        raise ValueError("Unexpected v0.32 source structure: " + old[:60])
    return src.replace(old, new, 1)

def main():
    src = BASE.read_text(encoding="utf-8")
    if "SCEXSND 0.32:" not in src:
        raise ValueError("Expected v0.32; inspect source before regenerating")
    start = src.index("    /* Recognize the three short")
    end = src.index("generic_play:", start)
    src = src[:start] + DETECTION + src[end:]
    src = replace_once(src,
        "    cmp byte ptr [effect_type],0\n    je analyze_generic\n    call synth_short_effect\n    jmp skip_analysis",
        "    cmp byte ptr [effect_type],0\n    je analyze_generic\n    call synth_platinum_effect\n    jmp skip_analysis")
    start = src.index("synth_short_effect:")
    end = src.index("\nold1a:", start)
    src = src[:start] + ENGINE + src[end:]
    src = replace_once(src, "effect_age:     .byte 0",
                       "effect_age:     .byte 0\neffect_fade:    .byte 0")
    src = replace_once(src,
        'installed:      .ascii "SCEXSND 0.32: EX 3-voice audio synthesis enabled. Reboot to unload.\\r\\n$"',
        'installed:      .ascii "SCPLAT 1.0 EXPERIMENTAL: eight PSG remasters. Reboot to unload.\\r\\n$"')
    src = replace_once(src,
        'already:        .ascii "SCEXSND is already installed.\\r\\n$"',
        'already:        .ascii "SCEXSND or SCPLAT already installed. Reboot before switching.\\r\\n$"')
    src = replace_once(src,
        "/* SimCity Tandy EX sound BIOS->PSG resynthesis TSR v0.30; 8086/V20, MIT. */",
        "/* SCPLAT 1.0: experimental PSG remaster for V20; v0.32 base; MIT. */")
    DEST.write_text(src, encoding="utf-8")
    print("Generated SCPLAT.S (base SCEXSND.S unchanged)")

if __name__ == "__main__":
    main()
