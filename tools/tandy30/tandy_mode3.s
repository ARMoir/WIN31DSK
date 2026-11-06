/* Restore BIOS text mode 3 before the Tandy Windows 3.0 video-memory guard.
 * 8086/NEC V20-safe. Never starts Windows or modifies startup.
 * Tiny .COM, exits to DOS when video BIOS returns.
 */
.intel_syntax noprefix
.code16
.section .text
.global _start
_start:
    mov ax, 0x0003
    int 0x10
    mov ax, 0x4c00
    int 0x21
