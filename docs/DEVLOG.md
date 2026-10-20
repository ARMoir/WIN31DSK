# WIN31DSK development log

> **Historical archive.** This document preserves the project's original chronological experiments and hardware-test notes. Earlier conclusions, proposed fixes and image filenames may have been superseded. For the current status, see the [project README](../README.md) and [verified builds](../builds/README.md).

---

## Current hardware-tested baseline (2026-10-20)

**Preferred build:** `WIN31DSK_286_Notepad_CleanLayout_TEST.img`

**Owner-confirmed on the real IBM PS/2 Model 50Z:** Windows boots, **Notepad launches successfully**, and the default Program Manager group/icon layout **looks fantastic** at the machine's VGA resolution. This is the first configuration the owner has explicitly selected as the keeper after the Calculator/File Manager experiments. The other apps and native PS/2 mouse are carried over from the earlier Clock-working, games-working base; please continue to distinguish that history from a fresh extended stress test of every app in this specific image.

- **Hardware:** original 10 MHz Intel 80286, 2 MB RAM, one 1.44 MB floppy, no hard drive.
- **Startup:** MS-DOS 6.22, Windows 3.1 Standard Mode, original Windows 3.1 Program Manager, **no `DOS=HIGH`**.
- **Games:** Solitaire, Minesweeper, Reversi.
- **Applications:** original Windows 3.0 Notepad and Windows 3.0 Clock, with `DIGITAL.FON` registered.
- **Drivers/boot:** 4,896-byte native Windows 3.0 PS/2 `MOUSE.DRV`, `ASSIGN.COM B=A` to prevent phantom floppy B: prompts.
- **Layout:** Games and Applications in separate clean rows, 88-pixel icon spacing, title wrapping, reproducible default group positions.
- **Floppy:** 1,474,560-byte image; **75,776 bytes free**.
- **SHA-256:** `3963c37e53ef658557138b7f3674503e0f8d862dbb1998a7df1769c8d7408d1a`.

**Not included:** Calculator (insufficient-memory errors) and File Manager (intermittent/consistent Windows floppy-read errors on the user's machine). Those variants remain documented below as experiments, not working release recommendations.

The Windows/DOS binary image contains proprietary Microsoft files and is **not distributed through this public source repository**.


---

# WIN31DSK — Windows 3.1 from one floppy on an IBM PS/2 Model 50Z

Experimental and hardware-tested **286-compatible** MS-DOS 6.22 / Windows 3.1 **1.44 MB** floppy builds for an original 10 MHz IBM PS/2 Model 50Z with 2 MB of RAM. Earlier variants included 16-bit SkiFree; the preferred Notepad desktop edition instead includes Solitaire, Minesweeper, Reversi, Clock, and Notepad.

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

## 286 memory + mouse-driver performance experiment (2026-10-20)

Two **separate test images**, derived from the exact five-app Windows 3.0 Clock edition with working DIGITAL.FON registration, let us isolate the effect of conventional-memory optimizations on a 2 MB Model 50Z:

- `WIN31DSK_5Apps_Clock_DOS_HIGH_286_TEST.img`: **control**; enables `DOS=HIGH` in `CONFIG.SYS` while retaining every other DOS/Windows program, driver, application, and physical file location. Free space: 58,880 bytes.
- `WIN31DSK_5Apps_Clock_DOS_HIGH_MOUSE30_286_TEST.img`: same, but replaces native Windows 3.1 `MOUSE.DRV` (10,672 bytes) with the original Windows 3.0 `MOUSE.DRV` (4,896 bytes) taken from the user's Windows 3.0 distribution. The original 3.0 SYSTEM.INI identifies its native mouse driver as Microsoft/IBM PS/2. The mouse driver stays at its original starting cluster; 11 tail clusters are freed. Free space: 64,512 bytes.

Both keep the **Games** group (Solitaire, Minesweeper, Reversi), **Applications** (Calculator, Windows 3.0 Clock), relocated `GDI.EXE`, original DOS boot files, `ASSIGN.COM B=A`, and font registration. The second version saves 5.5 KiB of disk allocation but **may or may not** reduce in-memory usage or work correctly under Windows 3.1. `CTMOUSE.EXE` from Mini-Windows is **not** included: it is a DOS resident driver, not a drop-in replacement for a native Windows mouse driver.

**Recommended testing:** Boot the DOS=HIGH-only control first; verify Clock and several minutes of Solitaire. Then try the Windows 3.0 mouse-driver image, confirming pointer movement and buttons before gameplay. If either build fails, go back to the exact prior Clock-working image. These are filesystem-validated builds, **not yet tested on real hardware**. They are not guaranteed to cure `Cannot read from drive A:` read errors. No licensed IMG binaries are committed to this public repository.

Detailed standalone test notes: `WIN31DSK_286_Performance_MouseDriver_TEST_README.md` (distributed with the test ZIP, not committed here).


### Controlled rollback: remove DOS=HIGH while keeping smaller PS/2 mouse driver (2026-10-20)

A new diagnostic image, `WIN31DSK_5Apps_Clock_SmallMouse_NoDOSHIGH_286_TEST.img`, is the exact byte-for-byte equivalent of the previously built `WIN31DSK_5Apps_SmallMouse_Only_286_TEST.img`. It differs from `WIN31DSK_5Apps_Clock_DOS_HIGH_MOUSE30_286_TEST.img` **only in `CONFIG.SYS`**, reverting to:

```ini
DEVICE=A:\HIMEM.SYS
FILES=30
BUFFERS=10
```

Confirmed directly in the image: `DIGITAL.FON` (1,712 bytes) is present and `WIN.INI` includes `DIGITAL 100,96,96: Digital Font=DIGITAL.FON` in `[fonts]`. Native Windows 3.0 `MOUSE.DRV` is still 4,896 bytes. The boot sector, the games and utility executables, GDI, and every other file's contents and disk locations are unchanged from the DOS=HIGH + smaller mouse build. The only on-disk byte differences were **31 bytes** associated with the `CONFIG.SYS` change. Filesystem checks passed.

SHA-256: `7ced4cf3a91777e7092cc52f342e1a573d277255fd6036a41f725503f4f7c9c1`.

**Status: testing on the actual PS/2 is pending.** This isolates the DOS=HIGH variable after Calculator reported insufficient memory and Clock raised a GDI protection fault in the optimized image. It does not establish that DOS=HIGH caused either issue. Test Calculator first after a cold boot; test Clock first after a separate cold boot, then longer gameplay to check for read errors. The IMG contains proprietary components and is not hosted in this public repository.


### Calculator insufficient-memory investigation (2026-10-20)

Real hardware update: On the smaller Windows 3.0 mouse / **no DOS=HIGH** five-app build, **Clock is working again**, and the games work, but Windows 3.1 `CALC.EXE` reports **insufficient memory even when launched first**. No proof this is caused solely by Calculator's code; the 2 MB system and Program Manager memory overhead are suspects.

Compared user-provided Windows 3.0 installed executables:

| Component | Win 3.1 | Win 3.0 | Disk allocation saved |
| --- | ---: | ---: | ---: |
| `CALC.EXE` | 43,072 bytes | 40,480 bytes | 2,560 bytes |
| `PROGMAN.EXE` | 115,312 bytes | 55,200 bytes | 60,416 bytes |

The older Calculator's declared NE heap and stack requirements are **the same** as the 3.1 one (2,048 / 6,144 bytes), so swapping Calculator alone may not make much difference. The older Program Manager is more promising for memory pressure, but there is no guarantee its group-file handling and 3.1 API calls are compatible.

Two FAT12-validated, **not yet hardware-tested** experimental IMG variants were built from the exact `WIN31DSK_5Apps_Clock_SmallMouse_NoDOSHIGH_286_TEST.img` baseline:
- `WIN31DSK_286_Win30Calculator_Only_TEST.img` changes only `CALC.EXE` to the 3.0 version (67,072 free bytes).
- `WIN31DSK_286_Win30ProgramManager_And_Calculator_TEST.img` changes both `CALC.EXE` and `PROGMAN.EXE` to 3.0 versions (127,488 free bytes).

Both preserve the DOS boot files, floppy A:/B: mapping, no-DOS=HIGH startup, smaller Windows 3.0 mouse driver, proven Clock font configuration, relocated `GDI.EXE`, and every other executable byte-for-byte at the same starting sectors. FAT mirrors, chains, and orphan/cross-link checks passed. **Test the Calculator-only version first**, then the reduced Program Manager variant if it still gives insufficient memory. Keep the currently Clock-working image as fallback. The proprietary IMG files are not committed to the public repository.


### File Manager replaces Calculator — 286 diagnostic images (2026-10-20)

After a dedicated Calculator-as-Windows-shell test immediately displayed `Cannot read from drive A:` on the real Model 50Z, we decided to replace Calculator rather than spend more memory and disk space on it. Two images were built from the **Clock-working, Windows 3.1 Program Manager, small PS/2 mouse, no-DOS=HIGH** version:

| Test image | Change | Free FAT12 space |
| --- | --- | ---: |
| `WIN31DSK_286_FileManager_4Apps_286_TEST.img` | Removes CALC.EXE; adds **Windows 3.0 WINFILE.EXE** (106,288 bytes), and replaces Calculator Program Manager item with **File Manager** using an authentic Windows 3.0-derived icon | 1,536 bytes |
| `WIN31DSK_286_FileManager_4Apps_ExtraSpace_TEST.img` | Same, but also removes WIN87EM.DLL (not directly imported by any remaining bundled Win16 application) | 14,336 bytes |

**Neither image has been hardware-tested.** Both preserve Windows 3.1 Program Manager, Solitaire, Minesweeper, Reversi, original Windows 3.0 Clock plus registered DIGITAL.FON, smaller PS/2 native mouse, `ASSIGN B=A`, `WIN /S`, and the no-`DOS=HIGH` configuration. The 3.0 File Manager imports `SYSTEM`, `KERNEL`, `GDI`, `USER`, and `KEYBOARD`; all are present. Both images have byte-valid application files, mirrored FATs, no cluster cross-links/orphans, and a verified checksum for the modified Program Manager group. The extra-space variant may fail to run third-party applications requiring floating-point emulation; preserve the DLL in the primary edition.

**DOS Prompt within Windows:** Standard Mode on an 80286 needs `WINOLDAP.MOD` and VGA `.2GR` support to launch DOS applications from Program Manager; these support files aren't on the small floppy and won't fit alongside File Manager. An icon pointing at `COMMAND.COM` alone would not be reliable, so no such icon was added. Instead use **Program Manager → File → Exit Windows** to reach DOS `A:\>`, then `WIN /S` to restart Windows. File Manager can browse DOS-recognized `C:`, `D:`, etc. drives and launch compatible Win16 programs, subject to dependencies and available RAM. A physical second floppy drive `B:` would require changing the startup `ASSIGN B=A` alias.

This experiment should not be promoted to a stable build until File Manager, Clock, games, and any read-error behavior are verified on the real PS/2. Original Microsoft IMG binaries are not committed to this public repository.


### Notepad replaces unreliable File Manager; tidy VGA Program Manager layout (2026-10-20)

Hardware follow-up: Both previous File Manager images had `Cannot read from drive A:` errors when opening File Manager (the more spacious version otherwise worked), so File Manager has been removed from this experiment. Calculator had previously failed due to memory errors, including when attempted as the Windows shell.

**Hardware-tested and selected as the preferred edition** `WIN31DSK_286_Notepad_CleanLayout_TEST.img`, built from the hardware-confirmed **Clock-working** `WIN31DSK_5Apps_Clock_SmallMouse_NoDOSHIGH_286_TEST.img`:
- Remove `CALC.EXE` (43,072 bytes); add original Windows 3.0 `NOTEPAD.EXE` (31,936 bytes; imports `KERNEL`, `GDI`, `USER`, `KEYBOARD`, all available).
- Preserve native Windows 3.1 **PROGMAN.EXE**, all three games, Windows 3.0 Clock and font registration, the working 4,896-byte Windows 3.0 PS/2 mouse driver, `WIN87EM.DLL`, the `ASSIGN B=A` drive-alias fix, and the **no-`DOS=HIGH`** DOS configuration.
- Rename Calculator program group item to **Notepad**, with command `A:\NOTEPAD.EXE` and a 1-bit monochrome icon derived from the authentic 1990 Windows 3.0 icon in `ACCESSOR.GRP`.
- Arrange Games and Applications group windows into **two separate full-width rows** at 640×480 VGA using original `.GRP` rectangle fields (Games: 20,15–612,192; Applications: 20,205–612,397).
- Explicitly enable `WIN.INI` `[Desktop]` options `IconSpacing=88`, `IconTitleWrap=1`, `IconTitleSize=8` and keep `PROGMAN.INI` `AutoArrange=1`, `SaveSettings=0` for a repeatable clean boot.
- 75,776 bytes of floppy space free; 40 files; FAT12 mirrors, file chains, and `.GRP` checksums validated. Only `WIN.INI`, `APPS.GRP`, `GAMES.GRP`, deleted `CALC.EXE`, and added `NOTEPAD.EXE` differ at the file-content level from the Clock-working source.
- SHA-256: `3963c37e53ef658557138b7f3674503e0f8d862dbb1998a7df1769c8d7408d1a`

**Hardware test outcome:** the owner confirms Notepad launches successfully and the startup group/icon layout looks fantastic; they selected this edition as the keeper. The Games, Clock, and mouse driver are preserved from an earlier working baseline, but extended simultaneous-app stress testing of this exact image has not been separately reported. No copyrighted IMG files are committed to this repo.
