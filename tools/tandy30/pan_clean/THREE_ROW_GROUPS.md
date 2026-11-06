# Three-row Program Manager home screen, Tandy 1000 EX

**Status, 2026-11-06:** Built and checked successfully in GitHub Actions, **hardware test pending**. This is a separate CF test image. The previously tested 16-color panning/border-2 image remains unchanged.

## Download

- [Bootable 16,285,696-byte CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-pan-border2-three-groups-2026-11-06/TANDY1000EX_WIN30_PAN16_BORDER2_THREE_ROW_GROUPS_CF.img)
- [GitHub Release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-pan-border2-three-groups-2026-11-06)
- [Verified build workflow](https://github.com/ARMoir/WIN31DSK/actions/runs/42295553868)

Image SHA-256: `d781c144c059f47da488ea1546c242bc63856a04eaf34b4cf98f3c65399bfcf5`

## Layout

The original Windows 3.0 Program Manager window stays at x=0, y=0, width 316, height 196 inside the physical 320×200 view. Three groups appear as **open, single-row-height windows** in this order:

| Group | Group window rectangle (left, top, right, bottom) | Original item count |
| --- | --- | --- |
| Main | (1, 0, 309, 54) | 6 |
| Accessories | (1, 54, 309, 108) | 10 |
| Games | (1, 108, 309, 162) | 11 |

Positions are relative to Program Manager's client area, not the full CRT. Each group's program icons were rearranged in its original reading order (top-to-bottom, left-to-right) into one horizontal row, 75 logical pixels apart. Icons outside the visible group width should be accessible using that group's horizontal scrollbar. **Not all 27 shortcuts can be simultaneously visible within 320 pixels**; they are preserved and scrollable.

AutoArrange was switched from 1 to 0 in `PROGMAN.INI` so Windows does not immediately wrap the icon row, and `SaveSettings=0` remains unchanged.

Main's previous minimized state was changed to normal. Accessories and Games also open normally. Windows 3.0 `PMCC` group file offsets, filenames, resource objects, bitmap bytes, app names, commands and icon paths are preserved; only group window state/rectangle, item coordinates and requisite 16-bit negative-sum checksums change. All group file checksums were independently verified after writing.

## All existing content preserved

Based on the preceding tested image's exact SHA256 `d8d0a38c3bab6f5df1b1f94c90efbb9b34beb2e35b5b4c6e25e53a3ff9102328`. No files were added or removed; exactly these five data files changed:

- `C:\WINDOWS\MAIN.GRP`
- `C:\WINDOWS\ACCESSOR.GRP`
- `C:\WINDOWS\GAMES.GRP`
- `C:\WINDOWS\PROGMAN.INI`
- `C:\TANDY88\PRGPAN.INI`

The original all-games executables, shortcuts, icon bitmaps, group paths and other files remain untouched. Preserved: border 2; 640×256 logical pan / 320×200 16-color physical view; PAN in WIN.INI load= background start; original Windows serial mouse and DOS CuteMouse settings; HPXY display driver; original fonts; guarded WIN.BAT with TGA3 and RESERVE; and PANON/PANOFF/REST7 scripts.

## Physical test

Flash this separate image to a suitable CF card, boot DOS, and type `WIN`. Check that all three one-icon-row group windows are visible, menus and icons are not vertically clipped, Program Manager starts in front, and horizontal group scrollbars expose all extra game and accessory icons. For panning use Ctrl+Alt+arrows and Ctrl+Alt+Home. To return from DOS to the original RRECT desktop, use `PANOFF` followed by `WIN`. A working previous pan/border-2 CF image should be retained as fallback.

If any group row is clipped due to actual Windows 3.0 titlebar/scrollbar metrics, the next iteration should adjust its rectangle heights; this was not asserted as physically tested. The compiler was not used to recompile Program Manager or modify Microsoft's original programs.

## Source of file format

The Program Manager group-file format is documented in the Microsoft Windows 3.1 SDK, with Microsoft Q86334 corrections to header field widths. Existing image headers were inspected and validated to be authentic Windows 3.0 PMCC format, using a negative sum of all little-endian 16-bit words including the stored checksum, padding one odd-length trailing byte **only for the checksum calculation**.
