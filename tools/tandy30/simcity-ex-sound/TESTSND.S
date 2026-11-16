/* Runtime PCM test (8086): synthesized 500/250/660Hz + noise in RAM. */
.intel_syntax noprefix
.code16
.section .text
.global start
start:
    push cs
    pop ds
    mov ax,0xe7a1
    int 0x1a
    cmp ax,0x5343
    je found
    mov dx,offset missing
    jmp fail_print
found:
    mov dx,offset detected
    mov ah,9
    int 0x21
    push cs
    pop es
    mov di,offset samples
    mov cx,64
wave1:
    push cx
    mov al,64
    mov cx,8
    rep stosb
    mov al,192
    mov cx,8
    rep stosb
    pop cx
    loop wave1
    mov cx,32
wave2:
    push cx
    mov al,48
    mov cx,16
    rep stosb
    mov al,208
    mov cx,16
    rep stosb
    pop cx
    loop wave2
    mov cx,85
wave3:
    push cx
    mov al,54
    mov cx,6
    rep stosb
    mov al,202
    mov cx,6
    rep stosb
    pop cx
    loop wave3
    mov al,128
    mov cx,4
    rep stosb
    mov cx,128
noise:
    push cx
    mov al,12
    stosb
    mov al,202
    stosb
    mov al,235
    stosb
    mov al,43
    stosb
    mov al,230
    stosb
    mov al,6
    stosb
    mov al,145
    stosb
    mov al,111
    stosb
    pop cx
    loop noise
    /* One 4096-byte playback followed by an immediate busy retry. */
    mov bx,offset samples
    mov cx,4096
    mov dx,150
    mov ax,0x8307
    int 0x1a
    jc failed_busy
    push cs
    pop es
    mov bx,offset samples
    mov cx,4096
    mov dx,150
    mov ax,0x8307
    int 0x1a
    jnc failed_not_busy
    mov dx,offset sounding
    mov ah,9
    int 0x21
    xor ah,ah
    int 0x1a
    mov [started_tick],dx
poll:
    mov ax,0x8100
    int 0x1a
    jnc finished
    xor ah,ah
    int 0x1a
    sub dx,[started_tick]
    cmp dx,55
    jb poll
    mov dx,offset timeout
    jmp fail_print
finished:
    mov dx,offset success
    mov ah,9
    int 0x21
    mov ax,0x4c00
    int 0x21
failed_busy:
    mov dx,offset busy
    jmp fail_print
failed_not_busy:
    mov dx,offset not_busy
fail_print:
    mov ah,9
    int 0x21
    mov ax,0x4c01
    int 0x21
started_tick: .word 0
detected: .ascii "SCEXSND 0.32 detected; testing three-voice synthesis.\r\n$"
sounding: .ascii "BUSY test passed. Listen for several tones and noisy finish.\r\n$"
success:  .ascii "PASS: sound completed; driver returned idle.\r\n$"
missing:  .ascii "SCEXSND 0.32 not installed.\r\n$"
busy:     .ascii "Driver is busy.\r\n$"
not_busy: .ascii "FAIL: simultaneous playback was accepted.\r\n$"
timeout:  .ascii "FAIL: timed out after 3 seconds. Reboot.\r\n$"
.align 16
.section .bss
.align 16
samples: .space 4096
