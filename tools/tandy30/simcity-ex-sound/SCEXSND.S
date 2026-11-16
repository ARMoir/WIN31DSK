/* SimCity Tandy EX sound BIOS->PSG resynthesis TSR v0.30; 8086/V20, MIT. */
.intel_syntax noprefix
.code16
.section .text
.global start
start:
    push cs
    pop ds
    mov ax, 0xe7a1
    int 0x1a
    cmp ax, 0x5343
    jne begin_install
    mov dx, offset already
    mov ah, 9
    int 0x21
    mov ax, 0x4c00
    int 0x21
begin_install:
    mov ax, 0x351a
    int 0x21
    mov [old1a], bx
    mov [old1a+2], es
    mov ax, 0x351c
    int 0x21
    mov [old1c], bx
    mov [old1c+2], es
    mov dx, offset installed
    mov ah, 9
    int 0x21
    mov dx, offset int1a_entry
    mov ax, 0x251a
    int 0x21
    mov dx, offset int1c_entry
    mov ax, 0x251c
    int 0x21
    mov dx, offset resident_end
    add dx, 15
    mov cl, 4
    shr dx, cl
    mov ax, 0x3100
    int 0x21
int1a_entry:
    cmp ax, 0xe7a1
    jne chk81
    mov ax, 0x5343
    iret
chk81:
    cmp ah, 0x81
    jne chk83
    jmp bios_handler
chk83:
    cmp ah, 0x83
    jne chk84
    jmp bios_handler
chk84:
    cmp ah, 0x84
    jne chk85
    jmp bios_handler
chk85:
    cmp ah, 0x85
    jne chain1a
    jmp bios_handler
chain1a:
    jmp far ptr cs:[old1a]
bios_handler:
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
    jne not_status
    mov ax, 0x00c4
    and word ptr ss:[bp+6], 0xfffe
    cmp byte ptr [active], 0
    je bios_done
    or word ptr ss:[bp+6], 1
    jmp bios_done
not_status:
    cmp ah, 0x83
    je playback
    mov byte ptr [active], 0
    call silence_all
    mov ah, 0
    and word ptr ss:[bp+6], 0xfffe
    jmp bios_done
playback:
    mov ah, 0
    cmp byte ptr [active], 0
    je new_play
    or word ptr ss:[bp+6], 1
    jmp bios_done
new_play:
    and word ptr ss:[bp+6], 0xfffe
    test cx, cx
    jz bios_done
    mov [remaining],cx
    mov [caller_volume],al
    and byte ptr [caller_volume],7
    mov si,bx
    mov cl,4
    shr si,cl
    mov ax,es
    add ax,si
    mov [pcm_seg],ax
    and bx,15
    mov [pcm_off],bx
    mov bx,dx
    and bx,0x0fff
    cmp bx,2
    jae rate_valid
    mov bx,2
rate_valid:
    mov [sample_delay],bx
    mov dx,1
    xor ax,ax
    div bx
    mov [bytes_per_tick],ax
    call silence_all
    mov byte ptr [active],1
bios_done:
    pop es
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ds
    pop bp
    iret
int1c_entry:
    pushf
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push bp
    push ds
    push es
    push cs
    pop ds
    cmp byte ptr [active], 0
    jne timer_active
    jmp timer_done
timer_active:
    mov ax,[bytes_per_tick]
    cmp ax,[remaining]
    jbe step_ok
    mov ax,[remaining]
step_ok:
    mov [tick_step],ax
    cmp ax, 12
    jae can_analyze
    jmp skip_analysis
can_analyze:
    mov si,[pcm_off]
    cmp si, 0xffbf
    jbe window_valid
    jmp skip_analysis
window_valid:
    mov ax,[pcm_seg]
    mov es,ax
    mov cx,[tick_step]
    cmp cx,64
    jbe count_ready
    mov cx,64
count_ready:
    mov [window_count],cl
    mov byte ptr [min_sample],255
    mov byte ptr [max_sample],0
    xor di,di
    xor bx,bx
    mov byte ptr [last_sign],0
analyze_loop:
    mov al,es:[si]
    inc si
    cmp al,[min_sample]
    jae min_done
    mov [min_sample],al
min_done:
    cmp al,[max_sample]
    jbe max_done
    mov [max_sample],al
max_done:
    cmp al,128
    jb below_mid
    cmp byte ptr [last_sign],0
    jne high_already
    inc bx
high_already:
    mov byte ptr [last_sign],1
    sub al,128
    jmp accumulate
below_mid:
    mov byte ptr [last_sign],0
    mov ah,128
    sub ah,al
    mov al,ah
accumulate:
    xor ah,ah
    add di,ax
    loop analyze_loop
    mov [crossings],bx
    mov ax,di
    xor dx,dx
    mov bl,[window_count]
    xor bh,bh
    div bx
    mov cl,3
    shr ax,cl
    cmp ax,14
    jbe loudness_ok
    mov ax,14
loudness_ok:
    mov bl,[caller_volume]
    mul bl
    mov bl,7
    div bl
    mov ah,15
    sub ah,al
    mov [attenuation],ah
    cmp byte ptr [attenuation],15
    jne loud_sound
    call silence_all
    jmp skip_analysis
loud_sound:
    mov al,[max_sample]
    sub al,[min_sample]
    cmp al,16
    jae signal_moving
    call silence_all
    jmp skip_analysis
signal_moving:
    mov bx,[crossings]
    test bx,bx
    jnz crossings_ok
    call silence_all
    jmp skip_analysis
crossings_ok:
    mov ax,[sample_delay]
    mov bl,[window_count]
    xor bh,bh
    mul bx
    mov si,ax
    mov di,dx
    shl ax,1
    rcl dx,1
    add ax,si
    adc dx,di
    mov bx,[crossings]
    mov cl,5
    shl bx,cl
    div bx
    cmp ax,1023
    jbe divider_below_max
    mov ax,1023
divider_below_max:
    cmp ax,16
    jae divider_above_min
    mov ax,16
divider_above_min:
    mov [divider],ax
    mov dx,0xc0
    mov ax,[crossings]
    mov bl,[window_count]
    shr bl,1
    shr bl,1
    shr bl,1
    xor bh,bh
    cmp ax,bx
    jbe pitched_effect
    mov al,0xe4
    out dx,al
    mov al,[attenuation]
    or al,0xf0
    out dx,al
    mov al,0x9f
    out dx,al
    mov al,0xbf
    out dx,al
    mov al,0xdf
    out dx,al
    jmp skip_analysis
pitched_effect:
    mov bx,[divider]
    mov al,0x80
    call set_tone
    mov ax,[divider]
    shr ax,1
    cmp ax,16
    jae octave_ok
    mov ax,16
octave_ok:
    mov bx,ax
    mov al,0xa0
    call set_tone
    mov ax,[divider]
    shl ax,1
    cmp ax,1023
    jbe suboctave_ok
    mov ax,1023
suboctave_ok:
    mov bx,ax
    mov al,0xc0
    call set_tone
    mov dx,0xc0
    mov al,[attenuation]
    or al,0x90
    out dx,al
    mov al,[attenuation]
    add al,4
    cmp al,15
    jbe vol1_ready
    mov al,15
vol1_ready:
    or al,0xb0
    out dx,al
    mov al,[attenuation]
    add al,6
    cmp al,15
    jbe vol2_ready
    mov al,15
vol2_ready:
    or al,0xd0
    out dx,al
    mov al,0xff
    out dx,al
skip_analysis:
    mov ax,[tick_step]
    sub [remaining],ax
    add [pcm_off],ax
    jnc no_wrap
    add word ptr [pcm_seg],0x1000
no_wrap:
    cmp word ptr [remaining],0
    jne timer_done
    mov byte ptr [active],0
    call silence_all
    mov ax,0x91fb
    int 0x15
timer_done:
    pop es
    pop ds
    pop bp
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    popf
    jmp far ptr cs:[old1c]
set_tone:
    push ax
    push bx
    push cx
    push dx
    mov dx,0xc0
    and al,0xe0
    mov ah,bl
    and ah,0x0f
    or al,ah
    out dx,al
    mov ax,bx
    mov cl,4
    shr ax,cl
    and al,0x3f
    out dx,al
    pop dx
    pop cx
    pop bx
    pop ax
    ret
silence_all:
    push ax
    push dx
    mov dx,0xc0
    mov al,0x9f
    out dx,al
    mov al,0xbf
    out dx,al
    mov al,0xdf
    out dx,al
    mov al,0xff
    out dx,al
    pop dx
    pop ax
    ret
old1a:          .word 0,0
old1c:          .word 0,0
active:         .byte 0
caller_volume:  .byte 0
last_sign:      .byte 0
window_count:   .byte 0
attenuation:    .byte 15
min_sample:     .byte 255
max_sample:     .byte 0
pcm_off:        .word 0
pcm_seg:        .word 0
remaining:      .word 0
bytes_per_tick: .word 0
tick_step:      .word 0
sample_delay:   .word 0
crossings:      .word 0
divider:        .word 0
installed:      .ascii "SCEXSND 0.30: EX 3-voice audio synthesis enabled. Reboot to unload.\r\n$"
already:        .ascii "SCEXSND is already installed.\r\n$"
.align 16
resident_end:
