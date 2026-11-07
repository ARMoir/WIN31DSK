# Adaptive Tandy EX Program Manager, 16-color XR155 / original four-color Tandy

**Status, November 6, 2026:** Verified CF build published. The 320-pixel three-row home layout was previously hardware-tested; the new 640-pixel four-color layout and switcher snapshots have passed offline FAT16 verification but **remain untested in physical Tandy display sessions**.

## Download

- [Bootable 16 MB CF disk image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-xrcga-t4cga-adaptive-layout-2026-11-06/TANDY1000EX_WIN30_XRCGA_T4CGA_ADAPTIVE_LAYOUT_CF.img)
- [GitHub release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-xrcga-t4cga-adaptive-layout-2026-11-06)
- [Successful build](https://github.com/ARMoir/WIN31DSK/actions/runs/42324503025)
- SHA-256: `4f5eb554ced179e8b44cf6c1f74bec53e56c4c6e78fe2123d79da8101325ab9f`

## What changes automatically with the selected mode

The normal DOS switch scripts select **driver, three bitmap font filenames, PAN startup behavior, and all four Program Manager layout files together**. No special Windows Setup procedure is needed. They operate outside Windows, not while a Windows session is running.

| Selection | Graphics and fonts | Program Manager window | Three MDI group windows |
| --- | --- | --- | --- |
| `XRCGA` (default) | XR155, 16 colors, 640x256 logical pannable desktop / 320x200 viewport, CGA fonts | 316x196 | Original 320px wide single-row Main / Accessories / Games |
| `T4CGA` | Original 640x200 four-color Microsoft TANDYDSP, CGA fonts | 636x196 | Expanded 628px wide, same three single-row group windows |
| `TANDY4`, `T4XT`, `T4EGA` | Four-color driver, corresponding font set | 636x196 | Expanded 628px layout |
| `FASTXY`, `XRXT`, `XREGA`, `GOLDXY` | 16-color XR155 or original HPXY, corresponding font set | 316x196 | Exact original 320px layout |

For every choice, the Main / Accessories / Games group items are unmodified. The four-color group snapshots change **only** window rectangle fields and a recalculated Windows 3.0 PMCC header checksum. They leave item positions, bitmap/icon objects, command names, shortcuts and original ordering intact. Wider group windows reveal more icons before scrolling.

The snapshots are in `C:\TANDY88`:

- `PM16.INI` and `PM4.INI` for the 316px/636px parent Program Manager
- `M16.GRP`, `A16.GRP`, `G16.GRP`: original 320-view group files
- `M4.GRP`, `A4.GRP`, `G4.GRP`: expanded 640-view group window rectangles

Each of the nine selectors copies **six** files in a fixed order (SYSTEM.INI, WIN.INI, PROGMAN.INI and the three groups), immediately verifies each copy with `C:\DOS\FC.EXE /B`, and reports failure visibly if a copy does not match. Do not start Windows if a script reports a verification error.

## Testing on real Tandy hardware

Boot the new card, enter `WIN`, and verify the original three-row Program Manager with CGA text appears and all Games remain. Exit Windows to DOS, run `T4CGA` and then `WIN`: on the 640x200 four-color desktop, Program Manager should become wider and the three open group strips should have longer icon rows. To return, exit Windows, enter `XRCGA`, then `WIN`: the original 320x200 view and exact compact group layout should return. Only do the switching at the DOS prompt after Windows is closed.

The Windows boot logo, protected `WIN.BAT`, mouse, CGA/XT/EGA font binaries, both existing graphics drivers, applications, games and all original 389+ file inventory are preserved. The immutable, already hardware-verified three-row gold-standard image and earlier preferred-XRCGA default image are separate unchanged releases.

This is **profile-dependent restore at the DOS mode-switch step**, not dynamic Win16 live resizing. Windows 3.0 Program Manager does not infer and refit the saved group rectangles after arbitrary Windows Setup mode changes.
