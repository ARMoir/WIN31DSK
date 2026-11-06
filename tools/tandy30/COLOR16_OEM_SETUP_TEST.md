# Tandy 1000 EX, Windows 3.0, 320x200 16 colors: OEM Setup control test

## Physical A/B result: original graphics driver ALSO crashes with XT settings

**CONFIRMED ON PHYSICAL TANDY, November 6, 2026:** The owner restored
the Windows XT `XTTEST.INI` configuration, manually changed only
`display.drv=TR53216.DRV` to `display.drv=TANDYDSP.DRV`, and started
Windows from the root guarded `WIN` launcher. **Windows still crashed.**

This completes an important controlled result:

| Configuration | Real Tandy result |
| --- | --- |
| Stock `SYSOLD.INI` + stock `TANDYDSP.DRV` | Windows desktop **works** |
| Windows XT `XTTEST.INI` + `TR53216.DRV` | Windows exits to DOS after splash |
| Windows XT `XTTEST.INI` + stock `TANDYDSP.DRV` | Windows **also crashes** |

**Conclusion:** The replacement driver alone is **not established as the
cause** of the crash. Something else in the XT Setup configuration or
installed resources can stop even the formerly working stock display.

For recovery, restore the exact stock INI:

```dos
COPY C:\WINXT\SYSOLD.INI C:\WINDOWS\SYSTEM.INI
```

**Next low-risk controlled test:** From the working stock
`SYSOLD.INI` configuration, change only the three font names under
`[boot]` to the installed Windows XT font files
(`fixedfon.fon=XTEFIX.FON`, `oemfonts.fon=XTEOEM.FON`,
`fonts.fon=XTESYS.FON`), **keeping** `display.drv=TANDYDSP.DRV`,
`mouse.drv=msmouse1.drv`, the video guard, DOS boot and every other
`SYSTEM.INI` line unchanged. Back up `SYSTEM.INI` first.
If the stock driver then crashes, the replacement font set is
implicated. If it boots, the remaining XT settings or their combination
must be tested separately. This test does not require reflashing.

The known-good Windows 3.0 mouse release is immutable and unaffected.

---


## Real-hardware A/B result: original four-color Windows boots (November 6, 2026)

**CONFIRMED ON THE PHYSICAL TANDY:** The owner restored
`C:\WINXT\SYSOLD.INI` over `C:\WINDOWS\SYSTEM.INI`, then manually launched
Windows from `C:\>`. **Windows booted successfully** with the original
`TANDYDSP.DRV` display in the *same* experimental plain-DOS CF environment.
The Windows XT display settings installed by Setup remain backed up as
`C:\WINXT\XTTEST.INI` and were not deleted.

The same machine and DOS image with Windows XT 320x200 16-color OEM settings
displayed startup artwork and then exited to DOS. This controlled comparison
significantly narrows the failure to **the OEM video driver and/or SYSTEM.INI
changes and associated display resources made during its installation**.
It does not isolate the display binary itself. The system's DOS boot,
CuteMouse, guarded WIN launcher and memory helper need no further speculative
changes based on this test.

**DO NOT overwrite the current working `SYSTEM.INI`** or reinstall
Windows to continue investigation. The hardware-verified 4-color mouse
Release remains untouched.

### Next diagnostic (same CF card, no reflash, no Windows changes)

At DOS, compare the working and experimental Windows configurations:

```dos
FC /L C:\WINXT\SYSOLD.INI C:\WINXT\XTTEST.INI
```

Photograph the output, especially `[boot]`, `display.drv`,
`mouse.drv`, `fixedfon.fon`, `oemfonts.fon`, `fonts.fon`, and
`286grabber` entries. The aim is to distinguish display settings from
mouse or other unexpected changes **before** making another test.
If `FC` is unavailable on this DOS image, save the two files and upload
them for comparison instead.

This test only reads files. Retain `SYSOLD.INI`, `XTTEST.INI`, and the
working installed `SYSTEM.INI`; Windows remains manually launched.

---


## Physical hardware result: OEM installation did NOT fix Windows startup

On the actual Tandy 1000 EX, Windows 3.0 Setup successfully displayed the
OEM choice **Tandy EX/HX 320x200 16 colors** and the owner installed it.
Launching Windows then displayed the custom **Windows XT splash screen**
instead of the original blue startup screen, but **Windows exited/crashed
back to C:\\> without reaching the GUI**.

**Do not call this a successful graphical Windows boot, functioning 16-color
desktop, or working display driver.** The owner clarified that the original
blue screen was also startup artwork. The new image only proves that new
startup artwork can be displayed and the selected OEM installation was
accepted by Setup. The underlying startup failure remains.

### Next controlled A/B test on the existing experimental CF, no reflash

We have not yet established whether the original `TANDYDSP.DRV` still
starts Windows using the experimental plain-DOS configuration and guarded
video reservation. First back up the current experimental `SYSTEM.INI`,
then temporarily restore the original `SYSTEM.INI` already saved on the
card. **Do not use `C:\\WINXT\\RESTORE` for this comparison**, because
that also restores DOSMAX and would change two variables simultaneously.

From DOS:

```dos
COPY C:\WINDOWS\SYSTEM.INI C:\WINXT\XTTEST.INI
COPY C:\WINXT\SYSOLD.INI C:\WINDOWS\SYSTEM.INI
CD \
WIN
```

The original `SYSOLD.INI` selects `TANDYDSP.DRV` and the original
verified Windows 1.04 `MSMOUSE1.DRV`. The same plain DOS CONFIG,
CuteMouse, guarded manual WIN and reserved video memory remain active.

- If the stock four-color Windows desktop works, suspect the new
  16-color OEM display installation (including driver/support files).
- If it still exits back to DOS, investigate the experimental DOS memory
  layout, reservation/launcher and other differences from the verified
  release before blaming the 16-color display driver.

After testing, restore the experimental driver selection:

```dos
COPY C:\WINXT\XTTEST.INI C:\WINDOWS\SYSTEM.INI
```

Reboot after a hang. The known-good archived mouse-enabled release is
untouched. Windows starts only when the owner manually types `WIN`.

---

## Important: Windows 3.0 Setup maintenance mode fix (November 6, 2026)

The original experimental Release's `SETUP16.BAT` ran
`C:\WINDOWS\SETUP.EXE` **from the root DOS directory**, which accidentally
started the new-installation wizard. The user encountered the error
*"The Windows 3.0 installation directory you have specified is not valid"*.
**Do not continue that installer. Press F3 to exit.**

On the already-flashed experimental CF image, **do not reflash**.
Run the installed DOS Setup from within its actual Windows directory:

```dos
C:
CD \WINDOWS
SETUP
```

Microsoft Windows 3.0 Setup then opens the **existing-installation maintenance**
screen, where Display / Other can install the OEM driver from `C:\WINXT`,
without reinstalling Windows. If a new-installation welcome screen appears
again, exit without proceeding. Keep the mouse setting unchanged and decline
any DOS boot-file rewrites.

The workflow `.github/workflows/tandy30-16color-oemsetup.yml` has been
corrected to generate a future `SETUP16.BAT` that changes into
`C:\WINDOWS` before invoking `SETUP.EXE`, but the **already-published test
Release asset is unchanged**. The manual commands above are the right
instructions for that specific downloaded image.

Source: Microsoft KB Q63484, Installing Third-Party Windows 3.0 Drivers:
https://www.betaarchive.com/wiki/index.php/Microsoft_KB_Archive/63484

---


**Status: GitHub build validated. Real Tandy hardware NOT tested with this new image.**

[Download separate experimental CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-16color-oem-setup-test-2026-11-06/TANDY1000EX_WIN30_16COLOR_OEMSETUP_CF_31808S.img) |
[GitHub Actions successful run #42251273920](https://github.com/ARMoir/WIN31DSK/actions/runs/42251273920)

- Filename: `TANDY1000EX_WIN30_16COLOR_OEMSETUP_CF_31808S.img`
- Exact size: **16,285,696 bytes, 31,808 sectors**
- SHA-256: `5d80da3674e64e5835d35d42fb1f6da5a3c6afff9f79f33ca354a4544c8d39cc`
- Test image is a **separate prerelease**, never a replacement for the
  [hardware-verified Windows 1.04 serial mouse release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05).

## Why this trial exists

The owner confirmed the old unmodified Windows 3.0 Tandy 640x200 four-color
display and Windows 1.04 serial COM1 mouse are both usable in the preserved
release. Later 320x200 16-color attempts failed on hardware:

1. `RESERVE.COM` initially reported `unsupported or corrupt DOS arena`
   while DOSMAX upper-memory extensions were active.
2. Using ordinary DOS and `COMMAND.COM`, it reported the generic platform
   check failure.
3. A diagnostic variant identified **TRACE 4: BIOS video mode not 3**.
4. Running `MTEST` first explicitly set BIOS text mode 3.
5. Then `RESERVE.COM` confirmed `16K video overlap reserved`, but Windows
   hung during startup without an error.

That result **does not prove Windows entered BIOS mode 4**. Upstream Tandy
EX/HX 320x200 16-color drivers target BIOS **mode 09h**, whereas mode 04h is
CGA 320x200 four-color. The video switch causing the hang was not measured.

A critical difference in our earlier test: it copied the driver and fonts
and **manually edited `SYSTEM.INI`**, while the upstream driver developer
explicitly instructs using **Windows 3.0 Setup / Display / Other** to install
the driver and matching resources. We cannot yet tell if that shortcut
caused the failure, but it deserves a controlled test.

## How this CF image differs

The build starts from the checksum-verified second 16-color test, retains
the 16-color memory-safe conventional DOS layout, and prepares Windows
for the supported Setup procedure:

- Restores `C:\WINDOWS\SYSTEM.INI` from the known-good
  `C:\WINXT\SYSOLD.INI`. The active display is **still**
  `TANDYDSP.DRV`, the original 640x200 four-color driver.
- Leaves `mouse.drv=msmouse1.drv` and the original Windows **1.04**
  `MSMOUSE1.DRV` unchanged.
- Preserves CuteMouse `/S14 /M`, DOS configuration, Windows components,
  original display driver, video-memory guard, and original backup files.
- Stages an **uncompressed, checksum-verified OEM driver and fonts** at
  `C:\WINXT`, including `OEMSETUP.INF`, `TR53216.DRV`,
  `XTESYS.FON`, `XTEFIX.FON`, `XTEOEM.FON`, `CGA.GR2`, and logo files.
- Installs a tiny 8086/V20-safe `C:\WINXT\TGA3.COM` that sets BIOS text
  mode 3. `C:\WIN.BAT` uses it immediately before the original
  `RESERVE.COM` check and `C:\WINDOWS\WIN.COM /R`. It does not bypass or
  disable any memory checks.
- Adds `C:\SETUP16.BAT`, which displays steps and starts the existing
  Windows 3.0 Setup program.
- **DOS always boots normally; Windows starts only when the user types `WIN`.**

Upstream Windows XT 8086 display project:
https://github.com/astrobleem/oemdisplay-tandy

Their installation guide:
https://github.com/astrobleem/oemdisplay-tandy/blob/main/docs/FIXED.MD

## Physical hardware test: follow in order

**Step 1, test the control BEFORE installing the new display.**

Flash to your matching 31,808-sector CompactFlash card. Boot DOS.
At the root `C:\>` prompt type `WIN` without running `MTEST`.
The new manual launcher initializes BIOS text mode 3, then invokes the
unchanged video-memory guard, then Windows real mode.

Because `SYSTEM.INI` is back to stock, Windows should still use the
**original 640x200 four-color driver** at this stage. If it hangs,
**stop**. Do not install the 16-color driver yet. Report whether the
reservation succeeded and whether Windows started. This isolates the
effect of conventional DOS and the memory reservation from the new
display driver.

**Step 2, ONLY after the stock-display control succeeds.**

Exit Windows normally, return to the DOS prompt, and start Setup in maintenance mode **from inside C:\\WINDOWS**:

```dos
C:
CD \\WINDOWS
SETUP
```

Inside Windows 3.0 Setup, select **Display**, then **Other**, enter
`C:\WINXT` as the OEM driver source, and choose
**Tandy EX/HX 320x200 16 colors**. Select **Complete Changes**.
Keep the existing mouse selection, and choose **No Changes** if Setup
offers to edit `CONFIG.SYS` or `AUTOEXEC.BAT`.

**Step 3, test the newly installed display.**

From the root `C:\>` prompt, type `WIN` once more.
Report whether (a) video reservation succeeded, (b) Windows starts,
(c) the 16 colors actually appear, and (d) the original serial mouse
responds.

If Windows locks up, cold restart the test card rather than skipping the
safety checks. To restore the original display and DOS configuration on
this **experimental** card, type:

```dos
C:\WINXT\RESTORE
```

and reboot. The original Windows 3.0 mouse-verified GitHub Release
remains separately archived and unaffected.

## Scope of CI verification

GitHub Actions verified exact upstream source ZIP/checksums; the
decompressed driver; all OEM support files on the FAT16 image;
the original Windows display configuration *before Setup*;
byte-for-byte original `AUTOEXEC.BAT`, `CONFIG.SYS`,
`CTMOUSE.EXE`, Windows 1.04 `MSMOUSE1.DRV`, and `TANDYDSP.DRV`;
the new guarded `WIN.BAT`; and exact CF card size/checksum.

**GitHub CI cannot verify real BIOS mode transitions, Windows Setup
behavior, Windows startup, or serial mouse behavior on physical hardware.**
Do not describe this experiment as a working 16-color image until it is
tested by the owner.
