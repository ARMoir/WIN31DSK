/* SimCity EX Sound - experimental BIOS->Tandy PSG compatibility TSR
 * GNU as syntax (.code16).  Builds as a tiny .COM for real-mode DOS.
 * Copyright (c) 2026 - provided under MIT license.
 * This is experimental: emulate the *API*, synthesize rough noise envelopes,
 * do NOT pretend to recreate 8-bit DAC sound.
 */
.intel_syntax noprefix
.code16
.section .text
.global start

start:
    push cs
    pop ds
    /* Check our installation signature using private INT 1Ah service 0xE7,
       avoiding accidental second installation. */
    mov ax, 0xE701
    int 0x1a
    cmp ax, 0x53EC
    je already_installed

    mov ax, 0x351a
    int 0x21
    mov word ptr [old1a], bx
    mov word ptr [old1a + 2], es
    mov ax, 0x351c
    int 0x21
    mov word ptr [old1c], bx
    mov word ptr [old1c + 2], es

    mov dx, offset int1a_handler
    mov ax, 0x251a
    int 0x21
    mov dx, offset int1c_handler
    mov ax, 0x251c
    int 0x21

    /* No PSG writes while installing (don't interrupt an existing tune). */
    mov dx, offset installed_text
    mov ah, 9
    int 0x21
    mov dx, offset resident_end
    add dx, 15
    shr dx, 4
    mov ax, 0x3100
    int 0x21

already_installed:
    mov dx, offset already_text
    mov ah, 9
    int 0x21
    mov ax, 0x4c00
    int 0x21

/* For unsupported INT 1A functions, jump to the original handler. */
int1a_handler:
    cmp ax, 0xE701
    je signature
    cmp ah, 0x81
    je handle_int1a
    cmp ah, 0x83
    je handle_int1a
    cmp ah, 0x84
    je handle_int1a
    cmp ah, 0x85
    je handle_int1a
    jmp far ptr cs:[old1a]
signature:
    mov ax, 0x53EC
    iret

handle_int1a:
    push bp
    mov bp, sp
    push ds
    push bx
    push cx
    push dx
    push si
    push di
    push es
    push cs
    pop ds
    cmp ah, 0x81
    je status
    cmp ah, 0x83
    je play
    /* AH=84 or 85: stop/reset */
    mov byte ptr [active], 0
    call mute_psg
    xor ah, ah
    and word ptr ss:[bp+6], 0xfffe
    jmp int1a_done

status:
    mov ax, 0x00c4
    and word ptr ss:[bp+6], 0xfffe
    cmp byte ptr [active], 0
    je int1a_done
    or word ptr ss:[bp+6], 1
    jmp int1a_done

play:
    xor ah, ah
    cmp byte ptr [active], 0
    je start_play
    or word ptr ss:[bp+6], 1
    jmp int1a_done

start_play:
    and word ptr ss:[bp+6], 0xfffe
    /* ES:BX --> PCM byte buffer, CX byte count, DX rate divisor, AL volume.
       Normalize the far pointer so samples can cross most 64K segment
       boundaries (BX begins between 0 and 15). */
    mov si, bx
    shr si, 1
    shr si, 1
    shr si, 1
    shr si, 1
    mov di, es
    add di, si
    mov word ptr [pcm_seg], di
    and bx, 15
    mov word ptr [pcm_off], bx
    mov word ptr [remaining], cx
    and al, 7
    mov byte ptr [sample_volume], al
    test cx, cx
    jz int1a_done
    mov bx, dx
    and bx, 0x0fff
    cmp bx, 4
    jae rate_ok
    mov bx, 4
rate_ok:
    /* 196,608 sample clock cycles per BIOS 18.2065Hz tick.
       Frequency ratio is 3:1 for PSG (3.579545MHz) vs system PIT
       (1.193182MHz), so step = 196608 / divisor. No PIT changes. */
    mov dx, 3
    xor ax, ax
    div bx
    test ax, ax
    jnz nonzero_step
    inc ax
nonzero_step:
    mov word ptr [bytes_per_tick], ax
    mov byte ptr [active], 1
    /* Set Tandy noise channel to white noise, softest by default. */
    mov dx, 0x00c0
    mov al, 0xE4
    out dx, al
    mov al, 0xFF
    out dx, al
    xor ah, ah

int1a_done:
    pop es
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ds
    pop bp
    iret

/* Standard BIOS 18.2 Hz timer hook. No PIT manipulation; chains INT 1Ch. */
int1c_handler:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push ds
    push es
    push cs
    pop ds
    cmp byte ptr [active], 0
    je int1c_done

    mov cx, word ptr [remaining]
    test cx,cx
    jz finish_playback
    mov bx, word ptr [bytes_per_tick]
    cmp bx, cx
    jbe step_clamped
    mov bx, cx
step_clamped:
    /* Sample eight evenly spaced PCM bytes, estimate average absolute
       distance from neutral midpoint. ~18 volume-envelope updates/second.
       No busy-loop while SimCity runs, so very cheap on a 7 MHz V20. */
    mov ax, word ptr [pcm_seg]
    mov es, ax
    mov si, word ptr [pcm_off]
    mov dx, bx
    shr dx, 3
    test dx, dx
    jnz stride_ok
    inc dx
stride_ok:
    xor di, di              /* running sum */
    mov cx, bx
    cmp cx, 8
    jbe sample_loop
    mov cx, 8
sample_loop:
    mov al, byte ptr es:[si]
    cmp al, 128
    jae sample_upper
    neg al                   /* note: below-neutral magnitude computed next */
    add al, 128              /* 128 - original byte */
    jmp sample_add
sample_upper:
    sub al, 128
sample_add:
    xor ah, ah
    add di, ax
    add si, dx
    loop sample_loop
    /* Average over min(8, bytes_in_this_tick) bytes. */
    mov ax, di
    xor dx, dx
    mov bx, word ptr [bytes_per_tick]
    cmp bx, word ptr [remaining]
    jbe div_count_ok
    mov bx, word ptr [remaining]
div_count_ok:
    cmp bx, 8
    jbe div_ready
    mov bx, 8
div_ready:
    div bx
    mov di, ax

    /* ATTEN = 15 - min(15, meanAmp/6), scaled by caller volume 0..7.
       Low amplitudes yield softer noise, higher transient levels louder. */
    mov ax, di
    xor dx, dx
    mov bx, 6
    div bx
    cmp ax, 15
    jbe vol_in_range
    mov ax, 15
vol_in_range:
    mov bl, byte ptr [sample_volume]
    mul bl                  /* AX = 0..105 */
    mov bl, 7
    div bl                  /* AL = 0..15 */
    cmp al, 15
    jbe scaled_ok
    mov al, 15
scaled_ok:
    mov ah, 15
    sub ah, al
    mov al, ah
    or al, 0xF0
    mov dx, 0x00c0
    out dx, al

    mov bx, word ptr [bytes_per_tick]
    mov cx, word ptr [remaining]
    cmp bx, cx
    jbe advance
    mov bx, cx
advance:
    sub word ptr [remaining], bx
    add word ptr [pcm_off], bx
    jnc pointer_advanced
    /* 64K offset rollover: carry the equivalent 0x1000 paragraphs
       into the segment, retaining the correct real-mode address. */
    add word ptr [pcm_seg], 0x1000
pointer_advanced:
    cmp word ptr [remaining], 0
    jne int1c_done
finish_playback:
    mov byte ptr [active], 0
    call mute_psg
    /* Tandy BIOS issues INT 15h AX=91FB on completion. */
    mov ax, 0x91fb
    int 0x15
int1c_done:
    pop es
    pop ds
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    jmp far ptr cs:[old1c]

mute_psg:
    push ax
    push dx
    mov dx, 0x00c0
    mov al, 0xff
    out dx, al
    pop dx
    pop ax
    ret

old1a:            .word 0,0
old1c:            .word 0,0
active:           .byte 0
sample_volume:    .byte 0
pcm_off:          .word 0
pcm_seg:          .word 0
remaining:        .word 0
bytes_per_tick:   .word 0
installed_text:   .ascii "SCEXSND 0.1: Experimental Tandy EX sound shim installed.\r\n$"
already_text:
    .ascii "SCEXSND is already installed.\r\n$"
.align 16
resident_end:
