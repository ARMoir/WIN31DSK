# SimCity EX Sound — experimental 16-bit DOS driver

For **Tandy 1000 EX** (NEC V20/8088 class), not a Windows sound driver. This project intercepts the later Tandy SL/TL digital-sound BIOS API and attempts to translate unsigned 8-bit PCM *amplitude envelopes* into sound on the EX's built-in 3-voice/noise PSG. **It is not a real DAC emulator.** The EX has no DAC, and SimCity compatibility is not yet verified on actual hardware.

## Files

- **SCEXSND.COM** — tiny resident driver (INT 1Ah AH=81h status, 83h play, 84h stop, 85h reset; INT 1Ch timer and INT 15h AX=91FBh completion).
- **TESTSND.COM** — audible hardware test; verifies the BIOS status, second-call busy response and completion.
- **SCEXSND.S / TESTSND.S** — source, assembled as DOS .COM with GNU binutils.
- **BUILD.SH** — reproducible Linux build; run with `sh BUILD.SH`.

## Testing on the real EX

Copy both COM files to your CF card (for example `C:\SIMCITY`). At a DOS prompt:

```dos
C:
CD \SIMCITY
SCEXSND
TESTSND
```

Expected: installation message; “PASS: busy contract”; short noisy PSG effect; “PASS: sound completed”. If that succeeds, launch your original **SimCity** from DOS and report whether the “Tandy sound BIOS missing” message disappears and whether sound changes. Some versions may need Tandy sound reselected in the game's configuration.

**Use in plain DOS only. Do NOT put the driver in AUTOEXEC.BAT or boot it automatically with Windows 3.0.** It stays resident until reboot; reboot to uninstall and restore normal vectors. Back up your working CF image. Do not load on a later Tandy SL/TL already equipped with a native DAC.

## Limitations

- Only the EX PSG **noise** voice is used, yielding crude sound effects, not digitized music/speech. Timer sampling is only 18.2 Hz to minimize load on a 7 MHz V20.
- May conflict with a game's existing use of the PSG noise voice; no automatic mixing.
- BIOS AH=82h (microphone input) not implemented. Unrecognized INT 1Ah services chain to the ROM.
- No real-hardware validation yet; the presence of these files does **not** establish that SimCity will select or work with this shim.
- A real 64KiB-crossing test and simultaneous program/driver behavior remain to be tested.
- These files are standalone extras and **do not modify the proven Windows 3.0 CF images**.

References: [SL/TL BIOS services](https://www.manualslib.com/manual/1219946/Tandy-1000-Sl.html?page=564), [playback calling convention](https://www.manualslib.com/manual/1219946/Tandy-1000-Sl.html?page=566), [completion callback](https://www.manualslib.com/manual/1219946/Tandy-1000-Sl.html?page=567), [DOSBox-X BIOS implementation](https://dosbox-x.com/doxygen/html/bios_8cpp_source.html).

MIT licensed (see LICENSE). No proprietary DOS, Windows or SimCity files included.
