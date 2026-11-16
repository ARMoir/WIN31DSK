# SimCity EX Sound Driver v0.31

**Experimental, real-hardware sound quality not yet verified.** Target: Tandy 1000 EX, NEC V20 / 8088-compatible CPU, DOS 6.22, original 1989 DOS SimCity.

## Real EX hardware feedback and v0.31 tuning

v0.30 was confirmed working on a Tandy 1000 EX, including audible sound with original SimCity. The gameplay recording showed fairly quiet effects at maximum volume and somewhat messy disasters.

**v0.31** adds +3 PSG gain steps to the PCM envelope (preserving its dynamic range), raises the octave and bass voice levels two steps, lowers the noise pitch and adds a small hysteresis band to reduce chatter between tone/noise modes. This is intended to sound louder and smoother without making disasters harsh; **v0.31 is not yet hardware-tested.**

**SCEX30.COM** is the exact old hardware-tested v0.30 binary. To roll back, reboot, copy it over SCEXSND.COM, then run SCEXSND again. Do not stack resident versions.

## What changed

v0.30 replaced the original noise-envelope-only driver with **PSG resynthesis**. A tiny resident program intercepts later Tandy SL/TL digital BIOS calls (INT 1Ah AH=81h/83h/84h/85h), analyzes at most 64 PCM samples per 18.2 Hz BIOS clock tick, estimates fundamental pitch from zero crossings, scales loudness from the signal envelope, and drives all **three independent Tandy SN76489 tone channels** (fundamental, octave, suboctave). It switches to the PSG noise channel for high-frequency/transient material. It uses I/O port 0xC0, does not reprogram the PIT or DMA, and avoids 386/286 instructions.

**Not a DAC:** the EX cannot output arbitrary PCM faithfully. This technique may sound fuller than a PC speaker for some effects and worse for others. v0.30 is confirmed operating with the original DOS game on EX hardware; v0.31's sound quality is not yet verified.

## Real Tandy EX test

Reboot first to clear all older sound/diagnostic TSRs. Back up your functioning CF image. Copy **both** v0.31 COM files to `C:\SIMCITY` and run from DOS:

```dos
C:
CD \SIMCITY
SCEXSND
TESTSND
SIMCITY
```

Expected installation line: **SCEXSND 0.31: EX 3-voice audio synthesis enabled.** `TESTSND` should play a short changing-pitch effect followed by a noisy sound, confirm busy status, and return to DOS. Then compare the actual SimCity audio against the game's IBM/PC-speaker option. If SimCity still announces "Tandy sound BIOS missing", or sounds worse than the PC speaker, this approach is not yet good enough; no additional diagnostic round is required.

Do not add it to AUTOEXEC.BAT while experimental. Driver remains loaded once per boot; **reboot to unload**. Stop testing and reboot if the machine hangs. Do not run under Windows 3.0 or stack with HOOK1A, HOOK1C or SCGATE.

## Hardware findings and fix

November 15, 2026: v0.1 printed its installation message but hung. `TSRPROBE`, `HOOK1A`, `HOOK1C` and `SCGATE` returned normally on real EX hardware. The original driver used assembler-generated long conditional jumps, which could encode 386-only 0F 8x opcodes. v0.30 uses short conditional jumps, safe near unconditional jumps and an explicit instruction-stream audit. The playback path is rewritten; static build tests and a mathematical sound model pass, **not a substitute for EX testing**.

## Micropolis reference

The [SimHacker/Micropolis repository](https://github.com/SimHacker/micropolis) supplies useful **sound-effect names and reference audio** (bulldozer, siren, explosion, etc.) in `MicropolisCore/res/sounds` and dispatch code in `micropolis-activity/src/sim/w_sound.c`. They are **Unix-era assets, not original DOS Tandy BIOS routines**; we have not copied their sound files or GPL code into this independently written MIT driver.

## Files and limitations

- `SCEXSND.COM`: 1008-byte resident driver.
- `SCEX30.COM`: preserved working v0.30 driver.
- `TESTSND.COM`: 544-byte DOS test generating its 4,096-byte PCM sample in RAM (three tones and noise). It has a 3-second busy timeout.
- `SCEXSND.S`, `TESTSND.S`: assembly source; `BUILD.SH`: GNU binutils build; `test_build.py` and `test_driver.py`: static, ISA and sound-model checks.
- Old diagnostic tools remain for history but are no longer required to try the replacement.
- BIOS microphone recording (AH=82h) is not implemented; other INT 1Ah calls chain to the ROM. Completion sends INT 15h AX=91FBh.
- If SimCity uses short samples with no discernible pitch, those parts may be muted; 18.2 Hz envelope updates limit precision. PSG effects can overwrite other simultaneously playing Tandy tones.
- No proprietary SimCity, DOS, Windows, or Micropolis assets are included.

References: [Tandy SL sound API](https://www.manualslib.com/manual/1219946/Tandy-1000-Sl.html?page=564), [playback convention](https://www.manualslib.com/manual/1219946/Tandy-1000-Sl.html?page=566), [DOSBox-X sound BIOS](https://dosbox-x.com/doxygen/html/bios_8cpp_source.html). MIT license: LICENSE.
