/* Original, royalty-free EX Platinum eight-effect live probe, 8086/V20. */
.intel_syntax noprefix
.code16
.section .text
.global start
start:
    push cs
    pop ds
    /* Only the experimental Platinum TSR answers the extended signature. */
    mov ax,0xe7a2
    int 0x1a
    cmp ax,0x504c
    je recognized
    mov dx,offset missing
    jmp failure
recognized:
    mov dx,offset intro
    mov ah,9
    int 0x21
    mov si,offset sample_lengths
    mov di,offset sample_labels
    mov bp,8
next_effect:
    mov dx,[di]
    mov ah,9
    int 0x21
    push cs
    pop es
    mov bx,offset scratch_samples
    mov cx,[si]
    mov dx,0x0300
    mov ax,0x8307
    int 0x1a
    jnc effect_started
    mov dx,offset failed_play
    jmp failure
effect_started:
    xor ah,ah
    int 0x1a
    mov [start_tick],dx
poll_effect:
    mov ax,0x8100
    int 0x1a
    jc effect_running
    jmp effect_completed
effect_running:
    xor ah,ah
    int 0x1a
    sub dx,[start_tick]
    cmp dx,75
    jb poll_effect
    mov dx,offset timeout
    jmp failure
effect_completed:
    add si,2
    add di,2
    dec bp
    jz all_completed
    jmp next_effect
all_completed:
    mov dx,offset success
    mov ah,9
    int 0x21
    mov ax,0x4c00
    int 0x21
failure:
    mov ah,9
    int 0x21
    mov ax,0x4c01
    int 0x21
start_tick: .word 0
sample_lengths: .word 11264,8704,10752,13440,5120,384,768,1536
sample_labels:
    .word msg0,msg1,msg2,msg3,msg4,msg5,msg6,msg7
intro:       .ascii "SCPLAT 1.0 confirmed; playing eight original-length PSG presets.\r\n$"
msg0:        .ascii "Block 0 (2.42s): \r\n$"
msg1:        .ascii "Block 1 (1.87s): \r\n$"
msg2:        .ascii "Block 2 (2.31s): \r\n$"
msg3:        .ascii "Block 3 (2.88s): \r\n$"
msg4:        .ascii "Block 4 (1.10s): \r\n$"
msg5:        .ascii "Block 5 (0.08s): \r\n$"
msg6:        .ascii "Block 6 (0.16s): \r\n$"
msg7:        .ascii "Block 7 (0.33s): \r\n$"
missing:     .ascii "SCPLAT not installed; reboot and run SCPLAT first.\r\n$"
failed_play: .ascii "FAIL: sound BIOS rejected playback.\r\n$"
timeout:     .ascii "FAIL: effect timed out; reboot to recover.\r\n$"
success:     .ascii "\r\nPASS: all eight effects finished; driver idle.\r\n$"
.align 16
.section .bss
.align 16
scratch_samples: .space 13440
