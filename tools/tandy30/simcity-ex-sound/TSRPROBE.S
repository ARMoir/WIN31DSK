/* TSRPROBE: isolate DOS AH=31h TSR termination (no interrupt hooks).
 * DOS .COM, Intel 8086 compatible; harmless to sound/Windows settings.
 * Run only once per reboot; it stays resident until reboot.
 */
.intel_syntax noprefix
.code16
.section .text
.global start
start:
    push cs
    pop ds
    mov dx, offset msg
    mov ah, 9
    int 0x21
    /* A .COM address is relative to PSP:0, so this includes PSP size. */
    mov dx, offset resident_end
    add dx, 15
    mov cl, 4
    shr dx, cl
    mov ax, 0x3100
    int 0x21
msg:
    .ascii "TSRPROBE: DOS TSR exit test (NO sound/interrupt hooks).\r\n$"
.align 16
resident_end:
