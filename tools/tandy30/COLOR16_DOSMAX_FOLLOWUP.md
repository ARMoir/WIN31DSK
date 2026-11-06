# Tandy 1000 EX 16-color display: DOSMAX memory arena failure and second trial

## Real hardware result on first 16-color image

On the original Tandy 1000 EX, the experimental
`TANDY1000EX_WIN30_320X200_16COLOR_CF_31808S` booted DOS and CuteMouse
successfully, but the guarded `WIN` command correctly refused to launch:

```text
RESERVE: unsupported or corrupt DOS arena. No reservation.
16-color video memory reservation failed. Windows was NOT started.
```

This is **not a Windows display driver crash**. The 16-color driver was not
started. `RESERVE.COM` checks the exact memory-control-block (MCB) chain.
It expects a standard 624KB BIOS conventional memory map, ending at segment
9C00h, with a free contiguous 16KB at the top.

Inspection of the actual first trial disk confirmed `CONFIG.SYS` loads
`CLEARMEM.SYS`, `USE!UMBS.SYS`, `DOSMAX.EXE`, links UMBs via `DOS=UMB,HIGH`
and starts `SHELLMAX.COM`. Those nonstandard memory-manager features are a
**likely** cause of the unsupported linked DOS arena, but their role is not
confirmed until the second image is tested on hardware.

## Experimental follow-up: plain conventional DOS configuration

The second trial starts with the *exact* image from the first 16-color
release (SHA-256 `d1cff2224f1b43b0be87b49e86905591268a564b4d55c42a6881899b93698453`).

It changes only `CONFIG.SYS` and the rollback backup/scripts:

- Removes DOSMAX/CLEARMEM/USE!UMBS and SHELLMAX from CONFIG.SYS.
- Sets `DOS=LOW` and `SHELL=C:\COMMAND.COM C:\ /E:256 /P`. The
  standard `C:\COMMAND.COM` exists in the exact input disk image.
- Leaves `AUTOEXEC.BAT`, automatic `CTMOUSE /S14 /M`, original Windows
  1.04 `MSMOUSE1.DRV`, video driver `TR53216.DRV`, original
  `TANDYDSP.DRV` and the guarded `C:\WIN.BAT` all **byte-for-byte unchanged**.
- Leaves `RESERVE.COM` **unmodified**. Windows still never starts if the
  memory reservation fails.
- Preserves original DOSMAX configuration in `C:\WINXT\CONFOLD.SYS`.
  Updates `C:\WINXT\RESTORE.BAT` to restore both the original Windows
  display and DOSMAX configuration, with instructions to reboot.

This test makes a diagnosis; it is not yet known whether Windows will
start with the clean arena or whether the original mouse continues
to work under the unoptimized configuration.

**Do not touch the separate, real-hardware-verified Windows 3.0 + Windows 1.04
mouse release**, archived here:

https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05

## Testing

1. Download the **plain DOS** 16-color experimental release image and flash
   it to a 31,808-sector spare CompactFlash card.
2. Boot to DOS and check the DOS mouse with `MTEST`; Esc exits.
3. At the **root** `C:\>` prompt, type `WIN`.
4. If the reservation succeeds, see whether Windows 3.0 displays 16 colors
   and the Windows mouse continues to respond.
5. If the reservation refuses again, **do not bypass it**. Report the exact
   `RESERVE:` line. Additional DOS arena tracing is needed before proceeding.

Restore the baseline display and DOSMAX on the *experimental card* from DOS:

```dos
C:\WINXT\RESTORE
```

Then **reboot**. The backup stored in the image restores the prior DOS
configuration and the original `SYSTEM.INI`. Or simply flash the
verified working release onto the CF card.

The upstream video utility requires conventional memory ending at 9C00h:
https://github.com/astrobleem/oemdisplay-tandy/blob/main/src/tandysw/RESERVE.MD
and its implementation:
https://github.com/astrobleem/oemdisplay-tandy/blob/main/src/tandysw/RESERVE.ASM
