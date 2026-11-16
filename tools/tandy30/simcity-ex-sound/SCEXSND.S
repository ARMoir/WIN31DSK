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
    jne status_busy
    jmp bios_done
status_busy:
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
    /* Recognize the three short v1.02 SOUNDDAT.V4 blocks by their exact
       expanded lengths, ONLY at the original BIOS rate DX=0300h. */
    mov byte ptr [effect_type],0
    mov byte ptr [effect_age],0
    cmp dx,0x0300
    jne generic_play
    cmp cx,384             /* block 5: 0.082s short sample */
    jne not_short_click
    mov byte ptr [effect_type],1
    jmp generic_play
not_short_click:
    cmp cx,768             /* block 6: 0.165s sample */
    jne not_grind
    mov byte ptr [effect_type],2
    jmp generic_play
not_grind:
    cmp cx,1536            /* block 7: 0.330s sample */
    jne generic_play
    mov byte ptr [effect_type],3
generic_play:
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
    cmp bx,4
    jae rate_valid
    mov bx,4
rate_valid:
    mov [sample_delay],bx
    /* Tandy DAC clock is 3.579545MHz, not the 1.193182MHz PIT clock.
       196608 / divisor bytes per 18.2Hz tick (v0.31 used 65536). */
    mov dx,3
    xor ax,ax
    div bx
    mov [bytes_per_tick],ax
    mov byte ptr [noise_mode],0
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
    cmp byte ptr [effect_type],0
    je analyze_generic
    call synth_short_effect
    jmp skip_analysis
analyze_generic:
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
    add ax,3                /* +3 PSG attenuation steps, preserves dynamics */
    cmp ax,15
    jbe loudness_ok
    mov ax,15
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
    /* Two-count hysteresis: no abrupt 18Hz tone/noise oscillation. */
    mov ax,[crossings]
    mov bl,[window_count]
    shr bl,1
    shr bl,1
    shr bl,1
    xor bh,bh
    cmp byte ptr [noise_mode],0
    jne noise_already
    add bx,2
    cmp ax,bx
    ja noisy_effect
    jmp pitched_effect
noise_already:
    cmp ax,bx
    jb pitched_effect
noisy_effect:
    mov byte ptr [noise_mode],1
    mov al,0xe5          /* lower noise pitch, smoother for disasters */
    out dx,al
    mov al,[attenuation]
    add al,4             /* noise stays below the strengthened tone channels */
    cmp al,15
    jbe noise_level_ready
    mov al,15
noise_level_ready:
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
    mov byte ptr [noise_mode],0
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
    add al,2
    cmp al,15
    jbe vol1_ready
    mov al,15
vol1_ready:
    or al,0xb0
    out dx,al
    mov al,[attenuation]
    add al,4
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
/* Three distinct short-sound PSG profiles, derived from the v1.02
   sound-block lengths and v2.00 timbre references; no samples included.
   Attribution to bulldozer/road is provisional until gameplay confirmed. */
synth_short_effect:
    push ax
    push bx
    push dx
    cmp byte ptr [caller_volume],0
    jne short_audible
    call silence_all
    jmp short_done
short_audible:
    mov al,7
    sub al,[caller_volume]
    mov [effect_att],al
    cmp byte ptr [effect_type],2
    jne not_short_grind
    /* 0.165s low mechanical loop: descending rumble and restrained noise */
    mov bx,860
    cmp byte ptr [effect_age],0
    je grind_pitch_set
    mov bx,940
    cmp byte ptr [effect_age],1
    je grind_pitch_set
    mov bx,1023
grind_pitch_set:
    mov al,0x80
    call set_tone
    mov bx,720
    mov al,0xa0
    call set_tone
    mov bx,590
    mov al,0xc0
    call set_tone
    mov dx,0xc0
    mov al,[effect_att]
    or al,0x90
    out dx,al
    mov al,[effect_att]
    add al,2
    or al,0xb0
    out dx,al
    mov al,[effect_att]
    add al,4
    or al,0xd0
    out dx,al
    mov al,0xe5
    out dx,al
    mov al,[effect_att]
    add al,6
    or al,0xf0
    out dx,al
    jmp short_done
not_short_grind:
    cmp byte ptr [effect_type],1
    jne short_medium
    /* 0.082s high, decaying two-tone click */
    mov bx,140
    cmp byte ptr [effect_age],0
    je click_pitch
    mov bx,175
click_pitch:
    mov al,0x80
    call set_tone
    mov bx,225
    mov al,0xa0
    call set_tone
    mov dx,0xc0
    mov al,[effect_att]
    cmp byte ptr [effect_age],0
    je click_volume
    add al,7
click_volume:
    or al,0x90
    out dx,al
    mov al,[effect_att]
    add al,4
    or al,0xb0
    out dx,al
    mov al,0xdf
    out dx,al
    mov al,0xff
    out dx,al
    jmp short_done
short_medium:
    /* 0.330s brighter two-note effect */
    mov bx,275
    cmp byte ptr [effect_age],2
    jb medium_pitch
    mov bx,325
medium_pitch:
    mov al,0x80
    call set_tone
    mov bx,390
    mov al,0xa0
    call set_tone
    mov dx,0xc0
    mov al,[effect_att]
    or al,0x90
    out dx,al
    mov al,[effect_att]
    add al,3
    or al,0xb0
    out dx,al
    mov al,0xdf
    out dx,al
    mov al,0xff
    out dx,al
short_done:
    inc byte ptr [effect_age]
    pop dx
    pop bx
    pop ax
    ret

old1a:          .word 0,0
old1c:          .word 0,0
active:         .byte 0
caller_volume:  .byte 0
last_sign:      .byte 0
window_count:   .byte 0
attenuation:    .byte 15
noise_mode:     .byte 0
effect_type:    .byte 0
effect_age:     .byte 0
effect_att:     .byte 15
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
installed:      .ascii "SCEXSND 0.32: EX 3-voice audio synthesis enabled. Reboot to unload.\r\n$"
already:        .ascii "SCEXSND is already installed.\r\n$"
.align 16
resident_end:
