# Three-row Program Manager home screen, Tandy 1000 EX

**Status, 2026-11-06: GOLD STANDARD, HARDWARE-VERIFIED DESKTOP LAYOUT.** The owner booted this exact image on their real Tandy 1000 EX with NEC V20 and Tandy CM-5 RGB monitor. Their supplied photograph visibly confirms Program Manager at startup, with Main at the top, Accessories in the middle, and Games at the bottom. All three groups are open as one-row strips, with visible horizontal scrollbars and icon labels. The owner explicitly chose it as the new gold-standard baseline. Performance, every individual game, and every panning key combination are **not** independently measured or exhaustively tested in this image. Preserve the preceding panning and RRECT CF releases unchanged as recovery choices.

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

## Physical-machine acceptance, November 6, 2026

The owner shared a photograph of the actual Tandy CM-5 showing Windows 3.0 Program Manager, Main / Accessories / Games simultaneously visible and ordered correctly. The screenshot includes the original File Manager, Control Panel, Print Manager, Clipboard, Write, Paintbrush, Terminal, Notepad, Solitaire, Reversi, ZZT and SkiFree icons, with remaining icons accessible by horizontal group scrolling. The current 320x200 hardware viewport has visible title bars, borders and scrollbars, with no obvious redraw corruption in the photograph. The owner confirmed: "Yes this is the new gold standard!"

Acceptance is limited to the visually confirmed startup and layout. Panning and its 640x256 logical desktop were demonstrated on the preceding panning image on physical hardware. Retain those controls in this build, but don't claim full panning-key coverage or exhaustive application testing.

This exact SHA-256 is now an immutable reference baseline for future graphics, panning and Windows UI experiments. Do not rebuild or replace its GitHub release asset. Publish subsequent experiments using distinct versioned filenames/tags.

## Physical test

Flash this separate image to a suitable CF card, boot DOS, and type `WIN`. Check that all three one-icon-row group windows are visible, menus and icons are not vertically clipped, Program Manager starts in front, and horizontal group scrollbars expose all extra game and accessory icons. For panning use Ctrl+Alt+arrows and Ctrl+Alt+Home. To return from DOS to the original RRECT desktop, use `PANOFF` followed by `WIN`. A working previous pan/border-2 CF image should be retained as fallback.

The owner's physical photograph confirms the three group rows fit the initial viewport. Future refinements must use separate experimental images and must not modify this baseline. The compiler was not used to recompile Program Manager or modify Microsoft's original programs.

## Source of file format

The Program Manager group-file format is documented in the Microsoft Windows 3.1 SDK, with Microsoft Q86334 corrections to header field widths. Existing image headers were inspected and validated to be authentic Windows 3.0 PMCC format, using a negative sum of all little-endian 16-bit words including the stored checksum, padding one odd-length trailing byte **only for the checksum calculation**.
