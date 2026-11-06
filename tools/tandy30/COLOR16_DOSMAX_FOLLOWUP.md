# Tandy 1000 EX 16-color display: DOSMAX memory arena failure and second trial

**TEST BUILD AVAILABLE:** [Download the plain-DOS 16-color experimental CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-16color-plain-dos-test-2026-11-05/TANDY1000EX_WIN30_16COLOR_PLAINDOS_CF_31808S.img) or [view its Release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-16color-plain-dos-test-2026-11-05). [Successful GitHub Actions run #42142849182](https://github.com/ARMoir/WIN31DSK/actions/runs/42142849182).

- Size: 16,285,696 bytes (31,808 sectors).
- SHA-256: `ee9a7a214faabd1af8c250f0e3937d0de184291de71242f52b2ab67403a1d526`.
- Artifact and GitHub Release are **experimental; actual video reservation and Windows startup must still be tested on the Tandy**.

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

## Real hardware result on second 16-color image (plain DOS)

A photograph from the physical Tandy EX, using the plain-DOS image, shows:

```text
RESERVE: need Tandy, text mode 3, BIOS 624K and DOS 3+. No reservation.
16-color video memory reservation failed. Windows was NOT started.
```

**Important change in failure:** the original DOSMAX image passed the initial
platform gate and stopped later with `unsupported or corrupt DOS arena`.
The plain-DOS image instead fails the **initial platform gate**. Therefore,
one or more of the hardware/DOS preconditions observed by RESERVE.COM
differed after changing CONFIG.SYS. Plausible causes include BIOS reported
conventional-memory size, but the photo does not isolate the failing check.
Do not force the BIOS memory word to 624K or bypass the guard without
checking the physical memory map.

### Read-only diagnostic to locate the exact failure

**[Download TANDYCHK.COM](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-16color-memory-diagnostic-2026-11-05/TANDYCHK.COM)** or
[download the separate memory diagnostic CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-16color-memory-diagnostic-2026-11-05/TANDY1000EX_WIN30_16COLOR_MEMORY_DIAG_CF_31808S.img).

The tool is 1,224 bytes, 8086/V20-compatible and read-only. The new CF
image was built from the exact second trial, adding **only**
`C:\TANDYCHK.COM`. It does not modify DOS startup, Windows, mouse,
video driver, guarded WIN, or the previous Release images.

Boot DOS, then type:

```dos
TANDYCHK
```

Photograph its output. It reports:
- BIOS video mode, expected 3.
- Conventional memory in KB from INT 12h and from the BIOS data area,
  expected **624** for this particular guard.
- DOS major.minor version, expected 3 or newer.
- Tandy ROM signatures at `FFFF:000E` (expected `00FF`) and
  `FC00:0000` (expected `0021`).
- First DOS MCB, terminal MCB end (expected `9C00` for this guard),
  and last MCB owner and size.

The tool performs **no DOS allocations, video mode switch, memory writes
or Windows startup**. It waits for a keypress before returning to DOS.
Do not bypass `RESERVE.COM` even if one field differs. The next safe
fix depends on the actual reported values.

### Preserve known-good

The verified Windows 3.0 + working Windows 1.04 Mouse Systems COM1
image remains unchanged:
https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05

---

## Follow-up diagnostic, November 6, 2026

The read-only `TANDYCHK` photo from actual hardware reports:

| Checked by RESERVE.COM | Actual Tandy value | Expected |
| --- | --- | --- |
| BIOS video mode | 3 | 3 |
| INT 12h / BIOS BDA conventional KB | 624 / 624 (0270h) | 624 |
| DOS version | 5.0 | 3+ |
| ROM FFFF:000E | 00FF | 00FF |
| ROM FC00:0000 | 0021 | 0021 |

Every displayed platform condition meets the original reservation program's
requirements. The diagnostic image **does not show the terminal DOS MCB
boundary**, because its visible output stops at the first DOS MCB segment.
Do not assume the top of the arena is 9C00h from this screenshot alone.

The first plain-DOS run still printed the single generic `need Tandy,
text mode 3, BIOS 624K and DOS 3+` error. Since all observed prerequisites
match, we cannot explain that rejection reliably from the photo alone. It
may reflect a value changing specifically at the time the reservation
program is run; no new RAM settings should be guessed or forced.

### Diagnostic error trace, exact upstream RESERVE.COM safety retained

[Download the **separate** trace CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-16color-reserve-trace-2026-11-06/TANDY1000EX_WIN30_16COLOR_RESVTRACE_CF_31808S.img).
[Verified GitHub Actions build #42248257875](https://github.com/ARMoir/WIN31DSK/actions/runs/42248257875).

- Image size: 16,285,696 bytes (31,808 sectors).
- SHA-256: `55f0f111a64918caf78eec724825f8d00eef6afac00d9f79385de60b4f7492ee`.
- The image is based on the **exact** plain-DOS 16-color experiment.
- The only changed DOS file is `C:\WINXT\RESERVE.COM`. Its five original
  initial failure jumps now print **distinct** messages (TRACE 1 through TRACE 5)
  before taking the **same original failure/cleanup path**.
- No original ROM, BDA, video, or DOS-version comparisons are relaxed or bypassed.
  The memory reservation and safety checks after these five branches are
  byte-for-byte unchanged.
- DOS startup, working CuteMouse, Windows 1.04 COM1 mouse driver,
  `TR53216.DRV`, recovery files, and the guarded manual `WIN` command
  are all byte-for-byte unchanged.

Test: flash a spare CF, boot DOS, and type `WIN` at `C:\>` (do not launch
Windows automatically or bypass the guard). Photograph **any new
`RESERVE TRACE` line**. If the trace identifies no initial failure, but
`RESERVE.COM` fails later with an arena message, record that result.
If the reservation succeeds and Windows starts, test colors and mouse
separately. The archived known-good mouse release is untouched.
