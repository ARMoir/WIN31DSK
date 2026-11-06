# Experimental Tandy 1000 EX Windows 3.0 in 320x200, 16 colors

**STATUS: Built in GitHub Actions; real Tandy hardware test pending.**

This **separate experimental CompactFlash image** starts from the *exact*
[verified working DOS/Windows mouse image](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05).
It does not modify, replace or overwrite the preserved release.

## What is different

- Active Windows display: `TR53216.DRV`, Tandy EX/HX native mode 09h, **320x200 with 16 colors**.
- Source: [Windows XT fixed display profiles](https://github.com/astrobleem/oemdisplay-tandy/blob/4fe890a951d93826e9ced6dbb98934ef6e0dccd0/docs/FIXED.MD);
  the source ZIP is pinned to its immutable upstream commit and verified SHA.
- The 16-color driver, three matching display fonts and `RESERVE.COM`
  are installed in the experimental image with checksums/readback tests.
- `AUTOEXEC.BAT`, `CONFIG.SYS`, `CTMOUSE.EXE`, Windows 1.04
  `MSMOUSE1.DRV` and `TANDYDSP.DRV` remain unchanged.
- The existing Windows `SYSTEM.INI` is backed up as
  `C:\WINXT\SYSOLD.INI`; no normal Windows installation files are deleted.
- The new **`C:\WIN.BAT`** intercepts the user's manual `WIN` command
  at the root DOS prompt, runs the video-memory reservation helper, then
  starts `C:\WINDOWS\WIN.COM /R`.
- If the video-memory guard fails, Windows does *not* start.
  The required memory reservation is not optional.

## How to test on actual Tandy

1. Flash the experimental image to a spare CF card with **exactly
   31,808 sectors (16,285,696 bytes)**.
2. Boot normally to `C:\>`. Windows **does not automatically start**.
3. Run `MTEST` to verify the known-good DOS serial mouse.
4. Exit with Esc. At the **root DOS prompt**, type **`WIN`**.
   This runs the guarded `C:\WIN.BAT` so `RESERVE.COM` executes first.
   Do not `CD C:\WINDOWS` and invoke `WIN.COM` directly.
5. Report whether reservation succeeded, Windows booted, all 16 colors
   appeared, and the mouse still moved/clicked.

## Safe rollback without reflashing

At DOS, type:

```dos
C:\WINXT\RESTORE
```

The restore batch copies the original `SYSTEM.INI` back and removes
`C:\WIN.BAT`. You can then type `WIN` normally to use the
original 640x200 four-color video driver with your already verified
Windows 1.04 serial mouse. If the experimental Windows startup locked
the system, reboot first. The preserved GitHub Release is always
available as an independent fallback.

## Notes and limitations

Windows XT's 320x200 driver and 8086 memory reservation helper were
tested by the upstream project in DOSBox-X, **not** on this physical
Tandy configuration. Our image builder validates the disk and included
files, not real hardware compatibility. Some standard Windows 3.0
dialogs may be too large for 320x200. The machine's DOSMAX UMB
configuration may affect the reservation helper; its refusal is a
safety mechanism, not a reason to skip the guard.

Upstream package pin:
- URL:
  `https://raw.githubusercontent.com/astrobleem/oemdisplay-tandy/4fe890a951d93826e9ced6dbb98934ef6e0dccd0/downloads/experimental/FIXED/WINXT720.ZIP`
- SHA-256 of source ZIP:
  `8b3b07d788c665c926a60e0beb9152627d920894d572bdfa4730af58d0ec8440`
- Expanded `TR53216.DRV` SHA-256:
  `ac0b2a72693b4ac7dd19a28f4f24f180a9c0b0ca0ccaa3dab2c9d1d33055290c`
- `RESERVE.COM` SHA-256:
  `644290e234cab9a6ac3799fa32959bb493d82d566501a8925720bb5a28c6afa8`

The `TANDY30` Windows 1.04 mouse release stays immutable and verified.
