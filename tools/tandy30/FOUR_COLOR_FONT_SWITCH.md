# Tandy 1000 EX original 4-color display and switchable Windows fonts

**Status:** November 6, 2026, experimental; build verified, first physical Tandy 4-color/font test pending. The original 16-color gold-standard release is **unchanged**.

## Important correction, November 6, 2026: DOS profile switch failure

**Use the [corrected four-color font-switch CF image](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-4color-fontswitch-dosfix-2026-11-06)** for switching tests. The first image had a **DOS batch-file false failure**: the `COPY` command didn't reliably reset `ERRORLEVEL`, and the scripts treated a preserved nonzero code as a failed copy. Suppressed `COPY` output made the cause invisible on the hardware photo. This was not a failure of original `TANDYDSP.DRV` or the updated font binaries.

The corrected image changed **only nine DOS BAT selector files**. Each now checks both source INI filenames, displays `COPY` output, then invokes the bundled `C:\\DOS\\FC.EXE /B` to verify the destination INI byte-for-byte before checking `ERRORLEVEL`. The image was validated in GitHub Actions. Physical test of the repaired scripts is still pending. Drivers, all font files, splash/boot logo, mouse, protected `WIN.BAT`, exact old 389+ app/game files and Program Manager geometry are untouched.

For the previously flashed first image, a DOS prompt workaround (no reflashing) is:

```bat
COPY C:\\TANDY88\\T4CGA.INI C:\\WINDOWS\\SYSTEM.INI
COPY C:\\TANDY88\\WIN4.INI C:\\WINDOWS\\WIN.INI
C:\\DOS\\FC.EXE /B C:\\TANDY88\\T4CGA.INI C:\\WINDOWS\\SYSTEM.INI
C:\\DOS\\FC.EXE /B C:\\TANDY88\\WIN4.INI C:\\WINDOWS\\WIN.INI
WIN
```

Both `FC` commands must report no differences before starting Windows. To switch back to optimized XR155, replace `T4CGA.INI` with `XRXT.INI` and `WIN4.INI` with `WINXR.INI` in the same four commands. The standalone repaired image eliminates the need for manual copying.

## Original experimental image (v1, switching commands have a DOS bug)

- [Download CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-original4color-fonttest-2026-11-06/TANDY1000EX_WIN30_ORIGINAL4COLOR_FONTTEST_XR155_SWITCH_CF.img)
- [GitHub Release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-original4color-fonttest-2026-11-06)
- [Successful GitHub Actions verification](https://github.com/ARMoir/WIN31DSK/actions/runs/42320980957)
- CF image 16,285,696 bytes, SHA-256 `9d2451f83baa313d6f96078a39c4969ca236401d52ca7a7e440318403db97b86`

## What it contains

This experiment uses the **original** Tandy driver from the owner's earliest physical-machine-verified Windows 3.0 mouse image:

- Original Microsoft `C:\WINDOWS\SYSTEM\TANDYDSP.DRV`
- Original resolution/color profile **640x200 in four colors**
- Driver size 25,840 bytes
- Driver SHA-256 `d593c03e52e338074df3c5c70973197bc61deeb72d615459ad90124afea126e0`
- The experimental CF's bundled `TANDYDSP.DRV` was compared **byte-for-byte** against that earliest mouse image. No patched/third-party Tandy 4-color driver was substituted.

The image initially selects original TANDYDSP with the newer XT bitmap fonts (`XTCSYS.FON`, `XTCFIX.FON`, `XTCOEM.FON`) to answer the first question. Those fonts are not yet proven compatible with the original TANDYDSP on physical hardware.

## Switching at the DOS prompt

**Always exit Windows before switching and type `WIN` after selecting a profile.** Windows 3.0 cannot safely change display drivers or its three [boot] bitmap font filenames in place while running. Use these root commands:

| DOS command | Display | Font family | Panning startup |
| --- | --- | --- | --- |
| `TANDY4` (also `T4XT`) | Original TANDYDSP, 640x200 four colors | New XT `XTC*.FON` | Disabled, fixed physical screen |
| `T4CGA` | Original TANDYDSP, 640x200 four colors | Original compact CGA `CGA*.FON` | Disabled |
| `T4EGA` | Original TANDYDSP, 640x200 four colors | Original EGA `EGA*.FON` | Disabled |
| `FASTXY` (also `XRXT`) | Optimized XR155, 640x256 16-color pan with 320x200 viewport | XT `XTC*.FON` | Enabled |
| `XRCGA` | XR155 16-color panning | Compact CGA `CGA*.FON` | Enabled |
| `XREGA` | XR155 16-color panning | EGA `EGA*.FON` | Enabled |
| `GOLDXY` | Original HPXY 16-color panning | Original gold-standard XT fonts | Enabled |

Example from the DOS prompt after Windows exits: type `T4CGA`, then `WIN`. To restore 16-color XR155 with the full gold-standard layout and current fonts, exit Windows, type `FASTXY`, and then `WIN`. `GOLDXY` continues to select the unoptimized but verified original HPXY renderer. The existing `PANON` and `PANOFF` rollback commands remain available and unchanged, but may replace the current display/font profile.

The Program Manager still uses the same three-row Main, Accessories, Games geometry. **The original Tandy display is 640px wide**, so it will not fill the display in exactly the same way as the 320px-wide XR155 viewport. Panning is disabled only while the original fixed-resolution display is selected. All existing font and driver files remain unchanged, and every profile can be revisited later.

## Why try CGA and EGA fonts?

Windows 3.0 renders bitmap fonts. Smaller/less complex bitmap glyphs can reduce pixels painted and may improve overall readability or drawing time, but speed is **not guaranteed**: most time may be spent in Windows GDI, window framing and palette-to-video conversion. The CGA, EGA and updated XT font families offer a practical visual A/B test without needing a new font compiler or risking the original driver binary. An alternate font set could also be visually unsuitable or cause a startup failure. Check actual hardware before making a preferred choice.

## What is preserved

The workflow independently enumerated the complete 394-file XR155 input image and confirmed all of its original files still exist in the output. Exactly **four original configuration files** were intentionally changed: `WINDOWS/SYSTEM.INI`, `WINDOWS/WIN.INI`, and the two root DOS switches `GOLDXY.BAT` and `FASTXY.BAT`. The switches now restore the matching `WIN.INI` PAN setting as well as the display selection. Exactly **15 new** files were added: six device/font `.INI` snapshots, two panning-load snapshots and seven additional DOS `.BAT` selectors.

All original `.EXE`, `.COM`, `.DRV`, `.FON`, `.GRP`, `.BMP` and logo/splash resources are byte-identical, including the Windows boot logo, the original Windows guarded `WIN.BAT` launcher, COM1 Mouse Systems driver, 27 grouped shortcuts, all games, the gold-standard three-row placement and the original XR155/HPXY drivers. MBR, full disk geometry, both FAT mirrors and all original file paths passed verification.

If the original 4-color driver/font combination fails to start, reboot to DOS, run `FASTXY`, then `WIN`, or restore the original known-working gold-standard CF card. No firmware or Windows Setup changes are necessary.

This is **not a speed benchmark result** and no hardware-compatibility or font acceleration is claimed until the owner reports testing.
