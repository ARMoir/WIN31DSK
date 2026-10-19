# WIN31DSK — Windows 3.1 on one 1.44 MB floppy

Two experimental single-floppy Windows 3.1 **286 Standard Mode** builds for the IBM PS/2 Model 50Z (10 MHz 80286, 2 MB RAM, one floppy drive). Both derive from a verified DOS 6.22 boot image and contain the original 16-bit SkiFree.

## Editions

| Edition | Windows shell | Extras | Status |
| --- | --- | --- | --- |
| `WIN31DSK_Full_FileManager_286.img` | File Manager | Notepad, Minesweeper, SkiFree | File Manager booted on real 50Z in the earlier build. SkiFree showed insufficient memory with 2 MB. New A:-focused configuration is **untested**. |
| `WIN31DSK_LowMemory_TaskManager_286.img` | Task Manager | SkiFree | Designed to reduce startup memory consumption; **not yet hardware-tested**. |

Both images are raw 1,474,560-byte floppy images. They boot to `A:\>`; type `WIN /S` for Windows 3.1 Standard Mode. Neither launches SkiFree automatically. In the low-memory edition, launch `A:\SKI.EXE` from Task Manager's Run command if available.

### B: drive switching

MS-DOS can expose *one physical floppy drive* as both logical **A:** and **B:**. Accessing B: may show an “Insert diskette for drive B:” prompt even with only one actual drive. The original build booted Windows successfully after pressing Enter at the A:/B: prompts a few times.

The full build's `WINFILE.INI` specifies `A:\*.*`, disables launch indexing, and hides the drive bar. The low-memory build doesn't launch File Manager at all. **These are experimental mitigations, not proven fixes** for the B: prompt. If prompted, leave the same disk inserted and press Enter. [Microsoft's archived single-drive explanation](https://helparchive.huntertur.net/document/34460).

### Writing and booting

1. Use WinImage to *write the IMG as a disk image* to a spare 1.44 MB floppy.
2. Boot the PS/2. At the `A:\>` prompt type `WIN /S`.
3. In the full edition run `SKI.EXE` from File Manager. In the low-memory edition use Task Manager's Run command, entering `A:\SKI.EXE`.
4. If DOS hangs during startup, F5 bypasses startup files and F8 steps through them; media errors may require rewriting a different floppy.

## Reproducible builds

Because this is a **public repository**, proprietary DOS, Windows, and SkiFree binaries are **not committed by this project**. Users must supply their own legally obtained source image.

Place `fatmini.py` and `build_variants.py` together, then run:

```sh
python build_variants.py --source PS2_50Z_Win31_286_SkiFree_FIXED.img --output-dir dist
```

The source is the corrected 1.44 MB Windows 3.1 + DOS 6.22 + SkiFree image, not the earlier faulty decompression builds. Python 3.9+; no external dependencies. Build output and SHA-256 sums are printed at completion.

Source inspiration: [Winhistory Windows 3.1 floppy](https://www.winhistory.de/more/386/wof.htm). Windows File Manager settings: [Windows 3.1 Resource Kit](https://vtda.org/docs/computing/Microsoft/OS/030-31645_Microsoft_Windows_3.1_Resource_Kit_1992.pdf).
