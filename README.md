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
