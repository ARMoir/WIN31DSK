/* Tandy DOS Mouse Test - 8086/NEC V20 compatible (DOS .COM)
 * Uses BIOS, DOS and mouse INT 33h calls; no Windows required.
 * as --32 -o mtest.o mtest.s
 * ld -m elf_i386 -Ttext 0x100 --oformat binary -o MTEST.COM mtest.o
 */
.intel_syntax noprefix
.code16
.section .text
.global _start
_start:
    push cs
    pop ds
    cld
    mov ax, 0x0003             /* 80x25 text mode */
    int 0x10
    mov dx, offset title_text
    call puts
    mov dx, offset hint_text
    call puts

    /* BIOS data area contains the base addresses for COM1/COM2. */
    mov ax, 0x0040
    mov es, ax
    mov dx, offset com1_text
    call puts
    mov ax, word ptr es:[0]
    call hex16
    mov dx, offset com2_text
    call puts
    mov ax, word ptr es:[2]
    call hex16
    mov dx, offset line_end
    call puts

    /* AX=0000h checks/resets the installed DOS INT 33h mouse driver. */
    xor ax, ax
    int 0x33
    test ax, ax
    jnz driver_found
    jmp no_driver             /* short conditional jump: 8086-safe */
driver_found:
    mov word ptr [button_count], bx
    mov dx, offset driver_text
    call puts
    mov ax, word ptr [button_count]
    call hex16
    mov dx, offset line_end
    call puts
    mov dx, offset help_text
    call puts
    mov ax, 0x0001             /* show mouse cursor in text mode */
    int 0x33

again:
    mov ah, 0x01               /* BIOS keyboard status, nonblocking */
    int 0x16
    jz sample_mouse
    xor ah, ah
    int 0x16
    cmp al, 27                 /* Escape */
    je quit
    cmp al, 'q'
    je quit
    cmp al, 'Q'
    je quit

sample_mouse:
    mov ax, 0x0003             /* BX=buttons; CX=X; DX=Y */
    int 0x33
    cmp bx, word ptr [last_buttons]
    jne update
    cmp cx, word ptr [last_x]
    jne update
    cmp dx, word ptr [last_y]
    je again
update:
    mov word ptr [last_buttons], bx
    mov word ptr [last_x], cx
    mov word ptr [last_y], dx
    mov ah, 0x02
    xor bh, bh
    mov dh, 11
    xor dl, dl
    int 0x10                  /* set text cursor at row 11 */
    mov dx, offset x_text
    call puts
    mov ax, word ptr [last_x]
    call hex16
    mov dx, offset y_text
    call puts
    mov ax, word ptr [last_y]
    call hex16
    mov dx, offset buttons_text
    call puts
    mov ax, word ptr [last_buttons]
    call hex16
    mov dx, offset tail_text
    call puts
    jmp again

quit:
    mov ax, 0x0002             /* hide mouse cursor */
    int 0x33
    mov ax, 0x4c00
    int 0x21

no_driver:
    mov dx, offset no_driver_text
    call puts
    xor ah, ah
    int 0x16                  /* wait for a key */
    mov ax, 0x4c01
    int 0x21

/* DX -> dollar-terminated string. */
puts:
    push ax
    mov ah, 0x09
    int 0x21
    pop ax
    ret

/* AX -> 4 uppercase hex digits; preserves registers; 8086-safe. */
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
    jbe hex_digit
    add dl, 'A' - 10
    jmp hex_output
hex_digit:
    add dl, '0'
hex_output:
    mov ah, 0x02
    int 0x21
    loop hex_next
    pop dx
    pop cx
    pop bx
    pop ax
    ret

last_x:       .word 0xffff
last_y:       .word 0xffff
last_buttons: .word 0xffff
button_count: .word 0

title_text:     .ascii "Tandy 1000 EX | DOS Serial Mouse Test v1.0\r\n$"
hint_text:      .ascii "8086/V20 - tests DOS INT 33h, not Windows mouse drivers.\r\n$"
com1_text:      .ascii "BIOS COM1 base: $"
com2_text:      .ascii "  COM2 base: $"
line_end:       .ascii "\r\n$"
driver_text:    .ascii "DOS mouse driver found. Buttons reported: $"
help_text:      .ascii "Move and click mouse. Buttons bits: L=1 R=2 M=4. ESC/Q quits.\r\n$"
x_text:         .ascii "X: $"
y_text:         .ascii "   Y: $"
buttons_text:   .ascii "   Buttons: $"
tail_text:      .ascii "   (hex)    $"
no_driver_text: .ascii "NO DOS MOUSE DRIVER detected (INT 33h reset returned 0000).\r\nCheck MOUSE.SYS/MOUSE.COM loading, COM port, and mouse power.\r\nPress any key...$"
