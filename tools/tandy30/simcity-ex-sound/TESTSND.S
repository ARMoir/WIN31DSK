/* SCEXSND BIOS and sound test. GNU assembler 16-bit DOS .COM */
.intel_syntax noprefix
.code16
.section .text
.global start
start:
    push cs
    pop ds
    push cs
    pop es
    mov ax, 0x8100
    int 0x1a
    jc busy
    cmp ax, 0x00c4
    jne no_driver
    mov dx, offset detected
    mov ah, 9
    int 0x21
    push cs
    pop es
    mov bx, offset pcm_data
    mov cx, 512
    mov dx, 4000
    mov ax, 0x8307
    int 0x1a
    jc busy
    /* A second playback must report busy while the first is active. */
    push cs
    pop es
    mov bx, offset pcm_data
    mov cx, 512
    mov dx, 4000
    mov ax, 0x8307
    int 0x1a
    jnc expected_busy_missing
    mov dx, offset started
    mov ah, 9
    int 0x21
wait_for_sound:
    mov ax, 0x8100
    int 0x1a
    jc wait_for_sound
    mov dx, offset finished
    mov ah, 9
    int 0x21
    mov ax, 0x4c00
    int 0x21
expected_busy_missing:
    mov dx, offset error_busy
    mov ah, 9
    int 0x21
    mov ax, 0x4c03
    int 0x21
no_driver:
    mov dx, offset missing
    mov ah, 9
    int 0x21
    mov ax, 0x4c01
    int 0x21
busy:
    mov dx, offset busy_text
    mov ah, 9
    int 0x21
    mov ax, 0x4c02
    int 0x21
detected: .ascii "Tandy digital BIOS API detected (SCEXSND if on EX).\r\n$"
started:  .ascii "PASS: busy contract. Sound requested: listen for the effect.\r\n$"
finished: .ascii "PASS: sound completed and status returned idle.\r\n$"
error_busy: .ascii "FAIL: second playback did not report busy.\r\n$"
missing:  .ascii "No compatible Tandy digital sound BIOS. Run SCEXSND first.\r\n$"
busy_text: .ascii "Sound API reports busy. Retry in a second.\r\n$"
/* 512-byte unsigned PCM with roughly envelope-shaped bursts. */
pcm_data:
.rept 4
.rept 16
    .byte 128
.endr
.rept 16
    .byte 255
.endr
.rept 16
    .byte 0
.endr
.rept 16
    .byte 128
.endr
.rept 32
    .byte 200
.endr
.rept 32
    .byte 90
.endr
.endr
pcm_end:
