/* Diagnostic stage: emulate ONLY INT 1Ah/AH=81h sound detection.
 * No INT 1Ch hook, no PSG output, no memory pointers or timer work.
 * Run only after reboot; do not combine with SCEXSND or other probes.
 */
.intel_syntax noprefix
.code16
.section .text
.global start
start:
    push cs
    pop ds
    mov ax, 0x351a
    int 0x21
    mov word ptr [old_vector], bx
    mov word ptr [old_vector+2], es
    mov dx, offset handler
    mov ax, 0x251a
    int 0x21
    mov dx, offset message
    mov ah, 9
    int 0x21
    mov dx, offset resident_end
    add dx, 15
    mov cl, 4
    shr dx, cl
    mov ax, 0x3100
    int 0x21
handler:
    cmp ah, 0x81
    jne chain
    push bp
    mov bp, sp
    mov ax, 0x00c4
    and word ptr ss:[bp+6], 0xfffe
    pop bp
    iret
chain:
    jmp far ptr cs:[old_vector]
old_vector:
    .word 0,0
message:
    .ascii "SCGATE: sound BIOS status only; no timer/sound hooks.\r\n$"
.align 16
resident_end:
