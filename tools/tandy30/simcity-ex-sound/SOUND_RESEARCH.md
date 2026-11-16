# SimCity DOS sound research — November 2026

## Original DOS v1.02 (the version actually running on the EX)

Source archive supplied by the owner: `SimCity_DOS_EN_v102.zip`. `SIMCITY.EXE` is 191,235 bytes; `SOUNDDAT.V4` is 26,002 bytes. The sound data contains a 16-bit total length followed by **eight sequential length-prefixed 4-bit sample blocks**. The executable expands each packed byte to two unsigned PCM bytes and issues Tandy BIOS `INT 1Ah` with `AX=8307h`, `DX=0300h`, and `CX=expanded byte length`.

| Block | Packed bytes | 8-bit PCM bytes | Playback at 3.579545 MHz / 768 |
|---|---:|---:|---:|
| 0 | 5632 | 11264 | 2.417 sec |
| 1 | 4352 | 8704 | 1.867 sec |
| 2 | 5376 | 10752 | 2.307 sec |
| 3 | 6720 | 13440 | 2.884 sec |
| 4 | 2560 | 5120 | 1.099 sec |
| 5 | 192 | 384 | 0.082 sec |
| 6 | 384 | 768 | 0.165 sec |
| 7 | 768 | 1536 | 0.330 sec |

The three short lengths are all distinct, so a BIOS TSR can recognize them when DX=0300h. **Their exact in-game purposes are not yet confirmed.**

## DOS v2.00 (newer version, reference only)

Source archive supplied by the owner: `SimCity_DOS_EN_Version-20-Quaders-Release(1).zip`. The game has individually named Creative Voice samples:
- `BULLLOOP.VOC`: 0.164 sec, ~11111 Hz, low rumble/grind
- `PLOP.VOC`: 0.126 sec, ~10989 Hz, high click decaying rapidly
- `EXPLODE.VOC`: 2.305 sec, ~5525 Hz
- `COPTER.VOC`: 2.397 sec, ~5525 Hz
- `POLICE.VOC`: 1.283 sec, ~11111 Hz

It also includes a newer AIL/Miles `TANDY.ADV` driver. These assets and driver are **not** a drop-in substitute for original DOS v1.02.

Although v1.02 block 6 has nearly exactly the same duration as v2.00 `BULLLOOP.VOC`, direct waveform comparison did not prove correspondence. v0.32 uses its *timbre* (deep rough sound) as a design reference for block 6, not its proprietary PCM bytes. Likewise PLOP inspired the high-frequency click profile.

## BIOS timing bug fixed

The Tandy SL/TL `INT 1Ah/AH=83h` digital sample clock is about **3.579 MHz** with a 12-bit sample-rate divisor. Original SimCity uses DX=0300h = 768: ~4661 bytes/sec. `INT 1Ch` ticks at 18.2065 Hz, yielding **196608/768=256 PCM bytes per tick**. v0.31 had incorrectly used `65536/768=85 bytes per tick`, stretching sounds about 3x. The existing PSG pitch formula already accounted for the 3:1 clock; this upgrade fixes playback progression, not that pitch formula.

## License and evidence boundaries

Only original driver/analysis source and numeric measurements are committed. No proprietary v1.02/v2.00 program binaries, VOC files, waveform tables, or graphics are distributed. Hardware compatibility and audible improvement for v0.32 remain to be verified on the real Tandy 1000 EX.

Reference documentation: [Tandy SL sound BIOS](https://www.manualslib.com/manual/1219946/Tandy-1000-Sl.html?page=566), [Ralf Brown's Interrupt List](https://www.delorie.com/djgpp/doc/rbinter/id/33/23.html), [SimHacker/Micropolis](https://github.com/SimHacker/micropolis) (Unix-era separate implementation).
