# SimCity EX Sound — experimental 16-bit DOS driver

For **Tandy 1000 EX** (NEC V20/8088 class), not a Windows sound driver. This project intercepts the later Tandy SL/TL digital-sound BIOS API and attempts to translate unsigned 8-bit PCM *amplitude envelopes* into sound on the EX's built-in 3-voice/noise PSG. **It is not a real DAC emulator.** The EX has no DAC, and SimCity compatibility is not yet verified on actual hardware.

## Hardware issue reported: hang after install message

The first real Tandy 1000 EX run on November 15, 2026 printed the SCEXSND 0.1 installation message but did **not** return to the DOS prompt. **Do not run SCEXSND.COM again until this is debugged.** Reboot clears the resident interrupt hooks; keep this experiment out of AUTOEXEC.BAT.

**Hardware result:** `TSRPROBE.COM` returned to `C:\SIMCITY>` on November 15, 2026. Plain DOS TSR termination works; original `SCEXSND.COM` remains unsafe after it hung during installation.

**Hardware update (November 15):** `HOOK1A.COM` and `HOOK1C.COM` both returned to the DOS prompt. They were run consecutively in the same boot, so this validates that both simple pass-through hooks can coexist; it does not fully establish separate-boot behavior. The original installer hang is therefore more likely to be in its additional interrupt logic or initialization rather than vector installation alone.

**Next test: SCGATE.COM** — a tiny 128-byte BIOS status-only shim. It installs only INT 1Ah, intercepts AH=81h and returns a simulated idle digital-sound BIOS status. Every other function chains to the original BIOS. No INT 1Ch hook, no PSG writes, no sound.

1. Reboot first to remove the previous hook diagnostics.
2. Run `SCGATE` from a normal DOS prompt. It should print "sound BIOS status only" and return to the prompt immediately.
3. Check that you can type `DIR` and see output. Then reboot again.
4. **Do not run SimCity, TESTSND, SCEXSND or the other hook diagnostics in the same boot.** If it hangs, reboot.

If SCGATE also returns normally, the remaining trouble is more likely in SCEXSND's timer routine or its other BIOS functions than in the simple AH=81h interception.

## Files

- **SCGATE.COM** — next stage: INT 1Ah sound BIOS status-only (AH=81h), zero sound/timer writes.
- **HOOK1A.COM** — 112-byte INT 1Ah pass-through, no sound or timer hook.
- **HOOK1C.COM** — 112-byte INT 1Ch pass-through, no sound or INT 1Ah hook.
- **TSRPROBE.COM** — 96-byte non-sound DOS TSR termination diagnostic; installs **no** interrupt hooks. Next hardware test.
- **SCEXSND.COM** — tiny resident driver (INT 1Ah AH=81h status, 83h play, 84h stop, 85h reset; INT 1Ch timer and INT 15h AX=91FBh completion).
- **TESTSND.COM** — audible hardware test; verifies the BIOS status, second-call busy response and completion.
- **SCEXSND.S / TESTSND.S** — source, assembled as DOS .COM with GNU binutils.
- **BUILD.SH** — reproducible Linux build; run with `sh BUILD.SH`.

## Original test plan (paused: installation hang on real EX)

**Do not proceed with this original sequence until the installer hang is resolved.**

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
