# WIN31DSK — Windows 3.1 from one floppy on an IBM PS/2 Model 50Z

Experimental, **286-compatible** MS-DOS 6.22 / Windows 3.1 **1.44 MB** floppy builds for an original 10 MHz IBM PS/2 Model 50Z with 2 MB of RAM. Each contains the original 16-bit SkiFree.

## Editions

| Edition | Startup shell | Notes |
| --- | --- | --- |
| `WIN31DSK_Full_FileManager_286.img` | `WINFILE.EXE` | File Manager, Notepad, Minesweeper, SkiFree. Earlier edition booted on real 50Z, but SkiFree reported insufficient memory with 2 MB RAM. |
| `WIN31DSK_LowMemory_SkiFreeShell_286.img` | `SKI.EXE` | Launches SkiFree directly when Windows starts, without File Manager or Task List. **New version not yet hardware-tested.** |

The earlier Task Manager edition successfully reached its UI on the real 50Z, but **Task List does not have a File > Run launcher**. The new low-memory build replaces it with SkiFree itself as the shell.

### Phantom drive B: and repeated swap prompts

MS-DOS 6.22 treats a PC with one actual floppy as **two logical drives, A: and B:**. Accessing B: can produce `Insert diskette for drive B:` even though there is no second physical drive. The same prompt occurred in **both** File Manager and Task Manager editions, so setting File Manager's initial view to A: was not sufficient.

The documented DOS workaround is **`ASSIGN B=A`**: it redirects B: requests to A: without simulated disk swaps. It requires `ASSIGN.COM`, an external program included in Microsoft's **MS-DOS 6.22 Supplemental Disk** (not generally present on the normal 6.22 boot floppy).

The builder's optional `--assign-file` argument adds a user-supplied `ASSIGN.COM` and invokes `A:\ASSIGN.COM B=A` from `AUTOEXEC.BAT` before Windows starts. This is a **promising but untested fix on the Model 50Z**. Do not expect the versions built without `--assign-file` to stop all A:/B: prompts.

## Booting

Write an IMG with WinImage as a raw floppy image (do not copy the file itself). Boot the PS/2. At the DOS prompt run:

```dos
WIN /S
```

This forces Windows 3.1 Standard Mode for the 286. The low-memory edition should start SkiFree as the Windows shell; the full edition starts File Manager, where SkiFree can be opened from `A:\SKI.EXE`.

If Windows pauses at the splash screen without drive light activity, the console may be waiting on a hidden A:/B: swap prompt; pressing Enter eventually booted an earlier edition on the real 50Z. Disk media read errors are separate and may require a different floppy.

**Status:** The previous full desktop and Task List builds have booted on actual hardware. The new direct-SkiFree shell and optional ASSIGN mapping have **not** been tested on that machine. Disk integrity checks are not a substitute for a successful boot test.

## Rebuild from your own source image

The repository contains scripts, **not Microsoft DOS/Windows or SkiFree binary images**. Provide your own legally obtained corrected SkiFree + Windows 3.1 source floppy image, then run:

```sh
python build_variants.py --source PS2_50Z_Win31_286_SkiFree_FIXED.img --output-dir dist
```

To build versions that try to suppress the A:/B: prompts:

```sh
python build_variants.py --source PS2_50Z_Win31_286_SkiFree_FIXED.img --output-dir dist --assign-file ASSIGN.COM
```

The script verifies floppy size, mirrored FAT tables, core DOS/Windows files, and checks that original executables remain byte-identical to the supplied source. It does not assemble licensed Windows or DOS components from scratch.

## Sources

- [Microsoft KB 34908 — single physical floppy maps to A: and B:](https://www.betaarchive.com/wiki/index.php/Microsoft_KB_Archive/34908)
- [Microsoft KB 115243 — Windows B: prompt workaround via ASSIGN.COM](https://www.betaarchive.com/wiki/index.php/Microsoft_KB_Archive/115243)
- [MS-DOS 6.22 supplemental files: ASSIGN.COM](https://freedos.link/OS/Using_MS-DOS_622.pdf)
- [Winhistory single-floppy Windows 3.1](https://www.winhistory.de/more/386/wof.htm)

### Troubleshooting `Error loading DISPLAY.DRV`

A physical PS/2 test of an earlier direct-SkiFree floppy showed `Error loading DISPLAY.DRV` after A:/B: swap prompts. The `DISPLAY.DRV` binary in that image is byte-identical to the file in a Task List variant that reached Windows successfully, so **do not assume the VGA driver is missing**. Possible causes include an intermittent floppy read, an unsatisfied drive-swap request, or a Windows startup failure. The ASSIGN-enabled edition has **not** yet been tested against this error.

At the DOS prompt test `DIR A:\DISPLAY.DRV` and `COPY A:\DISPLAY.DRV NUL` (the second command reads the whole file). If a data or CRC error occurs, rewrite the image to a different 1.44 MB floppy and verify the write. A good DOS file read does not guarantee Windows can initialize the driver; if the error persists, use a known-working boot image and compare the startup files, one change at a time.


### GDI.EXE relocated-file diagnostic (2026-10-19)

The first build confirmed to reach File Manager was `PS2_50Z_Win31_286_SkiFree_FIXED.img`. Subsequent low-memory builds failed with `Error loading GDI.EXE`, and `COPY A:\GDI.EXE NUL` returned a disk read error on the Model 50Z.

A comparison found **identical GDI.EXE bytes** in the working and failing IMG files (SHA-256 `6d28146961ab4733e167b1657289206ce16a856e431f843e4ee3d504836dfb6f`). The file was also located in the same FAT12 clusters (314–745) in both images.

A separate experimental test image, `WIN31DSK_LowMemory_SkiFree_GDI_Relocated.img`, preserves the existing low-memory SkiFree/ASSIGN build but takes `GDI.EXE` from the first working image and **moves all 432 of its FAT12 clusters to previously unused locations** (starting at 1863; no overlap with the original clusters). All other file contents, the DOS boot sector, and the startup settings are unchanged. This does not establish that the previous GDI bytes were bad. It tests whether different physical floppy locations change the read result.

**Not yet tested on the real PS/2.** The last part of relocated GDI uses late disk tracks, so reliable media and write verification are important. Keep the earlier working image as a fallback.

## Experimental six-app Program Manager floppy (2026-10-19)

A later build derived from the original hardware-tested Program Manager edition includes two separate groups:

| Games | Applications |
| --- | --- |
| Solitaire | Calculator |
| Minesweeper | Clock |
| Reversi (from the original Windows 3.0 executable) | Character Map |

The image is **1,474,560 bytes** with **2,048 bytes free**. The user-provided `REVERSI.EXE` is 16,688 bytes and imports only `KERNEL`, `USER`, and `GDI`, which are already present. The optional `REVERSI.HLP` is omitted to fit.

To make room while preserving the previously working applications, `TASKMAN.EXE` and `COMM.DRV` were removed, and `[boot] comm.drv=` was set blank. This disables Windows serial communications and the separate Task List utility, but not Program Manager or DOS itself. The original DOS boot files, relocated `GDI.EXE`, `ASSIGN.COM B=A`, and other application binaries remain unchanged.

**Hardware test pending:** Reversi has not yet been verified on the Model 50Z. Clock also remains experimental because `COMMDLG.DLL` cannot fit. The actual IMG is intentionally **not committed to this public repository**, because it contains proprietary Microsoft executables. Owners should use their own licensed source files.

### Six-app no-splash startup fix (2026-10-19)

The first six-app Reversi beta failed at startup with only `Error loading` and no filename. Root cause: to make space, that beta removed `COMM.DRV` and set `comm.drv=` to an empty value in `SYSTEM.INI`. Microsoft's [KB 83548](https://www.betaarchive.com/wiki/index.php/Microsoft_KB_Archive/83548) specifically lists blank `COMM.DRV=` values as a source of this loading failure.

A corrected experimental variant is named `WIN31DSK_ProgramManager_6Apps_NoSplash_FIXED_BETA.img`. It starts from the six-app beta and:
- Replaces the 44,170-byte logo-bearing `WIN.COM` with the exact 16,112-byte original `WIN.CNF` loader already embedded at the start of `WIN.COM`. This is a documented Windows 3.1 no-splash technique; it does **not** remove critical display drivers, fonts, or GDI.
- Removes the now-redundant `WIN.CNF` file.
- Restores `COMM.DRV` and its proper `comm.drv=COMM.DRV` setting from the previously working three-app Program Manager image.
- Restores `TASKMAN.EXE`, which fits again.
- Keeps DOS 6.22, floppy A/B alias fix, relocated `GDI.EXE`, Program Manager groups, and all six application executables intact.

The resulting 1.44 MB image has **32,768 bytes free** (SHA-256 `4ef615690259819f69ef9257d27f043f5f745663cdae1552abb7d5d698f7a2e6`). FAT12 chains and mirrored allocation tables were checked. **Real 286 testing is still pending.** Keep the last hardware-confirmed working image.

A contemporary description of the logo-free launcher: [1995 Windows 3.1 startup-logo discussion](https://groups.google.com/g/bit.listserv.win3-l/c/Iq_rjl2-Ekc).


## Five-app build with authentic Windows 3.0 Clock (2026-10-19)

The `W3.zip` installed Windows 3.0 archive provided by the user has `CLOCK.EXE` (11,136 bytes) and `DIGITAL.FON` (1,712 bytes). Inspection of its NE imports confirmed the clock requires only `KERNEL`, `USER`, and `GDI`—unlike the Windows 3.1 Clock, it does **not** import the `COMMDLG.DLL` that cannot fit alongside our other programs.

The new experimental `WIN31DSK_5Apps_Win30Clock_FullFont_286_BETA.img` is based on the corrected no-splash Program Manager image and contains:

| Games | Applications |
| --- | --- |
| Solitaire | Calculator |
| Minesweeper | Clock (Windows 3.0 + DIGITAL.FON) |
| Reversi | |

It removes Character Map, replaces Windows 3.1 Clock with Windows 3.0 Clock, and adds DIGITAL.FON. **58,880 bytes remain free** on the 1,474,560-byte floppy. It retains the DOS 6.22 boot components, `ASSIGN.COM B=A`, relocated known-working `GDI.EXE`, no-splash loader, `COMM.DRV`, and Task List. All other game and application executable bytes are preserved. **This edition still needs testing on the real 286.**

Because Reversi previously displayed a Windows `Cannot read from drive A:` message after drawing its board, a separate diagnostic `WIN31DSK_5Apps_Win30Clock_ReversiRelocated_286_BETA.img` keeps everything identical except the unchanged Reversi EXE is stored on another contiguous cluster chain (starting at cluster 2721 instead of 3). That is a media/placement experiment, **not a verified fix**, and should only be used if the standard edition has a reproducible read problem. The original Reversi executable is the same Windows 3.0 binary in the W3 archive.

These IMG builds contain proprietary Microsoft binaries and are not committed to this public repository; please build from your own licensed source files.

### Smaller Windows 3.0 mouse driver experiment (2026-10-20)

A new test uses `WINDOWS/SYSTEM/MOUSE.DRV` from the user-provided Windows 3.0 `W3.zip` (4,896 bytes), replacing Windows 3.1's 10,672-byte `MOUSE.DRV`. It frees **5,632 bytes of FAT12 allocation space**. This is a **Windows driver**; the roughly 5 KB `CTMOUSE.EXE` in the Mini-Windows 3.11 image is a separate *DOS* driver and does not replace it.

- `WIN31DSK_5Apps_SmallMouse_Only_286_TEST.img`: only substitutes `MOUSE.DRV` into the clock-font-registered baseline; no `DOS=HIGH` change.
- `WIN31DSK_5Apps_DOS_HIGH_SmallMouse_286_TEST.img`: same substitution into the separate `DOS=HIGH` experimental build.

Both are full 1.44 MB FAT12 images with **64,512 bytes free**. Every other file, its cluster chain, and the boot sector match each respective baseline; FAT mirrors and chain integrity checked. **Neither image has been boot-tested on the IBM PS/2**, and a Windows 3.0 driver may not behave perfectly under Windows 3.1. Test the mouse-only variant first and retain the last working disk. A smaller driver does not guarantee an equivalent improvement in usable RAM or remedy the reported runtime floppy read errors.
