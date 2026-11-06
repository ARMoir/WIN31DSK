/* TANDYCHK.COM: read-only V20/8086 DOS conventional-memory diagnostics.
 *
 * Does NOT switch video modes, allocate/release memory, write system RAM,
 * load a TSR or start Windows. Reads the exact preconditions from upstream
 * Windows XT RESERVE.COM: Tandy ROM bytes, BIOS text mode, DOS major version,
 * BDA conventional KB, and terminal DOS MCB end.
 *
 * Build on Linux:
 *   as --32 -o tandychk.o tandychk.s
 *   ld -m elf_i386 -Ttext 0x100 --oformat binary -o TANDYCHK.COM tandychk.o
 */
.intel_syntax noprefix
.code16
.section .text
.global _start

_start:
    push cs
    pop ds
    cld
    mov dx, offset title
    call puts
    mov dx, offset desc
    call puts

    /* Current BIOS video mode (no mode change). */
    mov ah, 0x0f
    int 0x10
    xor ah, ah
    mov word ptr [mode_value], ax
    mov dx, offset mode_text
    call puts
    mov ax, word ptr [mode_value]
    call decimal
    mov dx, offset mode_expected
    call puts

    /* INT 12h reports DOS conventional memory from firmware/BIOS. */
    int 0x12
    mov word ptr [int12_value], ax
    mov dx, offset int12_text
    call puts
    mov ax, word ptr [int12_value]
    call decimal
    mov dx, offset kb_text
    call puts

    /* BIOS data area 0040:0013, must be exactly 624 for stock RESERVE.COM. */
    mov ax, 0x0040
    mov es, ax
    mov ax, word ptr es:[0x0013]
    mov word ptr [bda_kb], ax
    mov dx, offset bda_text
    call puts
    mov ax, word ptr [bda_kb]
    call decimal
    mov dx, offset bda_hex
    call puts
    mov ax, word ptr [bda_kb]
    call hex16
    mov dx, offset bda_expected
    call puts

    /* DOS version, main and minor numbers (no modifications). */
    mov ah, 0x30
    int 0x21
    mov word ptr [dos_ver], ax
    mov dx, offset dos_text
    call puts
    mov ax, word ptr [dos_ver]
    xor ah, ah
    call decimal
    mov dl, '.'
    call putchar
    mov ax, word ptr [dos_ver]
    mov al, ah
    xor ah, ah
    call decimal
    mov dx, offset dos_expected
    call puts

    /* Two exact ROM signature bytes read by the upstream RESERVE.COM. */
    mov dx, offset sig1_text
    call puts
    mov ax, 0xffff
    mov es, ax
    mov al, byte ptr es:[0x000e]
    xor ah, ah
    call hex16
    mov dx, offset sig1_expected
    call puts

    mov dx, offset sig2_text
    call puts
    mov ax, 0xfc00
    mov es, ax
    mov al, byte ptr es:[0x0000]
    xor ah, ah
    call hex16
    mov dx, offset sig2_expected
    call puts

    /* DOS List-of-Lists contains segment of first conventional MCB. */
    mov ah, 0x52
    int 0x21
    cmp bx, 2
    jae mcb_address_ok
    jmp mcb_unavailable
mcb_address_ok:
    mov ax, word ptr es:[bx-2]
    mov word ptr [first_mcb], ax
    mov dx, offset first_text
    call puts
    mov ax, word ptr [first_mcb]
    call hex16
    mov dx, offset newline
    call puts

    /* Only read MCB fields; sanity-bound walks to prevent malformed loops. */
    mov di, word ptr [first_mcb]
    xor bp, bp
mcb_loop:
    cmp di, 0x0050
    jb mcb_invalid
    cmp di, 0xa000
    jae mcb_invalid
    inc bp
    cmp bp, 512
    ja mcb_invalid
    mov ax, di
    mov es, ax
    mov al, byte ptr es:[0]
    cmp al, 'M'
    je mcb_type_ok
    cmp al, 'Z'
    je mcb_type_ok
    jmp mcb_invalid
mcb_type_ok:
    mov si, di
    add si, word ptr es:[3]
    jc mcb_invalid
    inc si
    jz mcb_invalid
    cmp si, di
    jbe mcb_invalid
    cmp si, 0xa000
    ja mcb_invalid
    mov al, byte ptr es:[0]
    cmp al, 'Z'
    je mcb_found
    mov di, si
    jmp mcb_loop

mcb_found:
    mov word ptr [last_mcb], di
    mov word ptr [arena_end], si
    mov ax, word ptr es:[1]
    mov word ptr [last_owner], ax
    mov ax, word ptr es:[3]
    mov word ptr [last_size], ax

    mov dx, offset end_text
    call puts
    mov ax, word ptr [arena_end]
    call hex16
    mov dx, offset end_expected
    call puts
    mov dx, offset last_text
    call puts
    mov ax, word ptr [last_mcb]
    call hex16
    mov dx, offset owner_text
    call puts
    mov ax, word ptr [last_owner]
    call hex16
    mov dx, offset size_text
    call puts
    mov ax, word ptr [last_size]
    call hex16
    mov dx, offset newline
    call puts
    jmp finish

mcb_invalid:
    mov dx, offset mcb_bad
    call puts
    jmp finish

mcb_unavailable:
    mov dx, offset mcb_na
    call puts

finish:
    mov dx, offset last_note
    call puts
    xor ah, ah
    int 0x16
    mov ax, 0x4c00
    int 0x21

/* DX points to DOS "$"-terminated display string. */
puts:
    push ax
    mov ah, 0x09
    int 0x21
    pop ax
    ret

/* Output one character in DL via DOS. */
putchar:
    push ax
    mov ah, 0x02
    int 0x21
    pop ax
    ret

/* 16-bit AX => exactly 4 hexadecimal digits, 8086-safe. */
hex16:
    push ax
    push bx
    push cx
    push dx
    mov bx, ax
    mov cx, 4
hex_next:
    rol bx, 1
    rol bx, 1
    rol bx, 1
    rol bx, 1
    mov dl, bl
    and dl, 0x0f
    cmp dl, 9
    jbe hex_numeric
    add dl, 'A' - 10
    jmp hex_emit
hex_numeric:
    add dl, '0'
hex_emit:
    mov ah, 0x02
    int 0x21
    loop hex_next
    pop dx
    pop cx
    pop bx
    pop ax
    ret

/* AX unsigned in decimal. No 186+ instructions and no DOS allocations. */
decimal:
    push ax
    push bx
    push cx
    push dx
    xor cx, cx
    mov bx, 10
decimal_divide:
    xor dx, dx
    div bx
    push dx
    inc cx
    test ax, ax
    jnz decimal_divide
decimal_output:
    pop dx
    add dl, '0'
    mov ah, 0x02
    int 0x21
    loop decimal_output
    pop dx
    pop cx
    pop bx
    pop ax
    ret

mode_value: .word 0
int12_value: .word 0
bda_kb: .word 0
dos_ver: .word 0
first_mcb: .word 0
last_mcb: .word 0
arena_end: .word 0
last_owner: .word 0
last_size: .word 0

title: .ascii "TANDYCHK 1.0 | V20/8086 | Read-only Windows 16-color diagnostics\r\n$"
desc: .ascii "No changes to memory, video mode, startup or mouse.\r\n\r\n$"
mode_text: .ascii "BIOS current video mode: $"
mode_expected: .ascii "   (RESERVE needs 3)\r\n$"
int12_text: .ascii "INT 12h conventional KB: $"
kb_text: .ascii "\r\n$"
bda_text: .ascii "BIOS KB at 0040:0013: $"
bda_hex: .ascii "   HEX=$"
bda_expected: .ascii "  (RESERVE needs 624 / 0270)\r\n$"
dos_text: .ascii "DOS version: $"
dos_expected: .ascii "   (RESERVE needs DOS 3+)\r\n$"
sig1_text: .ascii "Tandy ROM FFFF:000E: $"
sig1_expected: .ascii "  (RESERVE needs 00FF)\r\n$"
sig2_text: .ascii "Tandy ROM FC00:0000: $"
sig2_expected: .ascii "  (RESERVE needs 0021)\r\n$"
first_text: .ascii "First DOS MCB segment: $"
end_text: .ascii "DOS MCB terminal end: $"
end_expected: .ascii "  (RESERVE needs 9C00)\r\n$"
last_text: .ascii "Last MCB segment: $"
owner_text: .ascii "  owner=$"
size_text: .ascii "  size=$"
newline: .ascii "\r\n$"
mcb_bad: .ascii "DOS MCB chain invalid/unexpected. No memory writes attempted.\r\n$"
mcb_na: .ascii "DOS List-of-Lists MCB pointer unavailable.\r\n$"
last_note: .ascii "\r\nPhotograph this screen. Press any key to return to DOS.\r\n$"
