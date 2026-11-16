# SCEXSND v0.32 — sound for original DOS SimCity on a Tandy 1000 EX

8086/V20-compatible real-mode DOS TSR. Emulates later SL/TL digital sound BIOS (INT 1Ah, AH=81h/83h/84h/85h), synthesizing approximate sound through the EX's original three-voice/noise generator at port 0C0h. MIT licensed.

## Upgrade from hardware-tested v0.31

- **Correct playback speed:** Original SimCity DOS v1.02 calls the Tandy BIOS with DX=0300h. The DAC is clocked at approximately 3.579545 MHz, not the 1.193 MHz PC timer used by v0.31's playback step. v0.32 advances 256 bytes per 18.2-Hz tick rather than ~85, eliminating 3x stretched effects.
- **Three distinct short sound profiles:** Original SOUNDDAT.V4 includes blocks that expand to 384, 768, and 1,536 PCM bytes. At the game's exact DX=0300h playback setting these now have separate PSG renditions: a high fading click, a low mechanically rattling/descending loop, and a medium bright two-note effect. Other samples keep the v0.31 pitch-envelope converter.
- **Reference from newer v2.00:** BULLLOOP.VOC is a low, rough 0.164-second mechanical effect; PLOP.VOC is a high, fast 0.126-second click. No proprietary audio is included.
- **CPU safety:** Branches are audited for 8086-compatible opcodes. The original v0.1 hang was caused by a 386-only conditional branch; v0.32's expanded code has been checked for that problem.

**Important:** The 0.165s v1.02 block and v2.00 BULLLOOP have matching duration, but waveform analysis did *not* establish that they are the same in-game sound. The 384/768/1536 mappings are distinct data blocks, not proven names for the bulldozer/road buttons. If both tools trigger the exact same sample, we will need an action-aware game patch rather than a pure BIOS shim to separate them.

## Test on your real Tandy EX

Reboot first to unload the old TSR. Copy SCEXSND.COM and TESTSND.COM to the SimCity folder and run from **plain DOS**, not Windows:

```dos
C:
CD \SIMCITY
SCEXSND
TESTSND
SIMCITY
```

TESTSND is optional. SCEXSND should announce **v0.32** and immediately return to DOS. Start SimCity once the TSR is installed. Compare bulldozing, placing roads, and disaster effects. This is a single in-game comparison, not a request for a new series of diagnostics.

**Do not put it in AUTOEXEC.BAT yet** or stack with old HOOK/SCGATE tests. Reboot to unload. If it hangs, reboot and restore the proven v0.31 binary by copying **SCEX31.COM to SCEXSND.COM**; its matching TEST31.COM is also saved. No boot image or Windows 3.0 file is changed.

## Tests and limitations

`BUILD.SH` uses GNU binutils. `test_driver.py` audits 8086 opcode support, Tandy BIOS hooks, the 3.579MHz playback timing, and unique effect-length cases. `test_build.py` includes the older diagnostic tests. `inspect_archives.py` optionally checks your own v1.02/v2.00 ZIPs locally without shipping any game data.

**v0.32 has passed static checks only; actual EX audio quality remains unverified.** The EX has no DAC and cannot reproduce arbitrary 8-bit PCM faithfully. This synthesizer approximates effects using three square-wave oscillators and noise. Do not load this TSR on an SL/TL with a functioning digital BIOS.

See [SOUND_RESEARCH.md](SOUND_RESEARCH.md) for the actual source-file measurements and their limitations.

## Miles Tandy driver reference

The proprietary v2.00 `TANDY.ADV` music driver has been disassembled for research, without copying its code or assets. See [TANDY_ADV_ANALYSIS.md](TANDY_ADV_ANALYSIS.md) for the verified PSG note, volume, voice allocation, and audio routing details, and their limits for our v1.02 digital-effects TSR.
