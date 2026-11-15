/* Isolated interrupt-vector diagnostic for Tandy 1000 EX.
   Passes all BIOS calls through unchanged; do not stack with sound shim. */
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
    mov dx, offset msg
    mov ah, 9
    int 0x21
    mov dx, offset resident_end
    add dx, 15
    shr dx, 1
    shr dx, 1
    shr dx, 1
    shr dx, 1
    mov ax, 0x3100
    int 0x21
handler:
    jmp far ptr cs:[old_vector]
old_vector:
    .word 0, 0
msg:
    .ascii "HOOK1A: installed INT 1Ah pass-through only.\r\n$"
.align 16
resident_end:
