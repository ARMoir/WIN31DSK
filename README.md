# WIN31DSK

**Windows 3.1 on a single 1.44 MB floppy — running on a 10 MHz 80286 with 2 MB of RAM and no hard drive.**

This project started with an original IBM PS/2 Model 50Z and a simple question: *how much of Windows can we squeeze onto one floppy and actually run on the real machine?*

The answer is a working Windows 3.1 **Standard Mode** desktop with Program Manager, three games, two accessories, a PS/2 mouse, and a surprisingly tidy VGA layout. No hard disk or RAM upgrade required.

> **Assembled on a modern computer; tested on real vintage hardware.** The floppy images were created and optimized off-machine, then written to physical disks and tested on the original IBM PS/2 Model 50Z. The preferred Notepad edition booted, its desktop layout looked right, and Notepad launched on the PS/2. Games, Clock, and mouse support were also tested during development; see [the build notes](builds/README.md) for the precise testing history.

## The machine

| | |
| --- | --- |
| **Computer** | IBM PS/2 Model 50Z |
| **CPU** | Intel 80286, 10 MHz |
| **RAM** | 2 MB |
| **Storage** | One 1.44 MB floppy drive; **no hard drive** |
| **Display** | VGA, 640 × 480 |
| **Software** | MS-DOS 6.22 + Windows 3.1 Standard Mode |

## What's on the preferred floppy?

**Windows desktop:** Windows 3.1 Program Manager, arranged into two easy-to-read groups:

| Games | Applications |
| --- | --- |
| Solitaire | Notepad |
| Minesweeper | Clock |
| Reversi | |

The desktop also includes:

- **Working PS/2 mouse** using the compact native Windows 3.0 mouse driver.
- **Automatic startup:** the floppy boots DOS and starts Windows with `WIN /S`.
- **No phantom B: swapping prompts** thanks to `ASSIGN.COM B=A`.
- **Clean icon layout** with separate Games and Applications rows, sensible spacing, and wrapped labels.
- **Original Windows 3.0 Clock** with its digital font registered correctly.
- **75,776 bytes free** on the 1,474,560-byte FAT12 floppy.

The Windows 3.1 kernel and Program Manager run alongside carefully selected Windows 3.0 accessories and drivers, chosen because they fit and work better on this particular 286.

## Hardware-tested editions

Three milestone images survived testing on the actual PS/2:

| Edition | What's included | Status |
| --- | --- | --- |
| **01 — SkiFree** | Windows 3.1 Standard Mode with playable SkiFree | Tested |
| **02 — Games + Calculator** | Program Manager, Solitaire, Minesweeper, **working Calculator** | Tested; older, lighter desktop |
| **03 — Notepad Desktop** | Program Manager, Solitaire, Minesweeper, Reversi, Notepad, Clock | **Preferred build** |

See **[Verified builds](builds/README.md)** for the exact image names, SHA-256 checksums, and what was tested. The `builds/` directory is a catalog, **not a download directory for the Microsoft disk images**.

## Running it

With a disk written from your own properly licensed DOS/Windows files:

1. Insert the 1.44 MB boot floppy into a compatible 286 with enough RAM.
2. Power on. The preferred edition starts DOS 6.22 and then Windows 3.1 automatically.
3. Use Program Manager to launch the games and accessories.
4. To reach the DOS prompt, choose **File → Exit Windows** in Program Manager. Run `WIN /S` to start Windows again.

**Drive-letter note:** `ASSIGN B=A` is there to stop Windows from asking to swap between virtual A: and B: on a single-drive system. It deliberately aliases B: to A:. If you add a *physical* second floppy drive, you'll want to revisit that startup command. DOS-recognized hard drives such as C: are unaffected.

## How we got it to fit

The challenge wasn't just file size. With only 2 MB of RAM and Windows running directly from a floppy, we encountered startup faults, GDI crashes, memory errors, and Windows repeatedly asking to read drive A:.

The working approach combined:

- A genuine **80286-compatible Standard Mode** installation, rather than 386 Enhanced Mode.
- Keeping Windows 3.1 **Program Manager** instead of the smaller but troublesome Windows 3.0 version.
- Smaller Windows 3.0 components where testing justified them, including `MOUSE.DRV`, Clock, and Notepad.
- The right `DIGITAL.FON` registration for Clock.
- Careful FAT12 file placement and conservative DOS startup settings; **no `DOS=HIGH`** in the preferred build.
- Removing Calculator and File Manager from the final edition after they proved unreliable in the expanded desktop. (Calculator **did** run in the earlier games edition.)

The full trial-and-error story, including failed approaches, is preserved in the **[development log](docs/DEVLOG.md)**.

## What's in this repository?

| File / folder | Purpose |
| --- | --- |
| [`builds/`](builds/README.md) | Tested editions, filenames, checksums, limitations |
| [`docs/DEVLOG.md`](docs/DEVLOG.md) | Original hardware tests and troubleshooting history |
| [`fatmini.py`](fatmini.py) | Minimal Python FAT12 floppy-image reader/writer |
| [`build_variants.py`](build_variants.py) | Script for **early** File Manager / SkiFree experiments |

**Build-script status:** `build_variants.py` is a legacy experiment script; it does **not** yet recreate the final Notepad desktop from scratch. The current repository is a record of the project and its utilities, not a one-command Windows 3.1 installer.

## Software and licensing

The complete floppy images incorporate Microsoft MS-DOS 6.22, Windows 3.x, and other original software. Those binaries are **not included in this public repository**. Microsoft's [open-source MS-DOS releases](https://github.com/microsoft/MS-DOS) do not include MS-DOS 6.22 or Windows 3.1. Use your own appropriately licensed source media.

---

*Created on modern hardware and tested on a real IBM PS/2 Model 50Z. Retro hardware has a way of making every kilobyte count.*
