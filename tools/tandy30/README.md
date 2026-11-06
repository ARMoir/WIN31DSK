# Tandy 1000 EX: Windows 3.0 with a working serial mouse

**STATUS: VERIFIED ON REAL HARDWARE (November 5, 2026). DO NOT REPLACE THE KNOWN-GOOD MOUSE DRIVER.**

## Download the preserved, tested CF image

**[Permanent GitHub Release: Tandy 1000 EX, Windows 3.0 serial mouse](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05)**

- Image: [`TANDY1000EX_WIN104_MSSYS_COM1_CF_31808S.img`](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-mouse-verified-2026-11-05/TANDY1000EX_WIN104_MSSYS_COM1_CF_31808S.img)
- [SHA-256 checksum file](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-mouse-verified-2026-11-05/TANDY1000EX_WIN104_MSSYS_COM1_CF_31808S.img.sha256)
- Size: **16,285,696 bytes / 31,808 sectors**. This is the exact physical CompactFlash capacity, not a full nominal 16 MiB image.
- SHA-256: `eca08b0eb4283854bfef71d98d8febe08ad8de89eb3d52a109a0b9d39993fa34`.
- Original successful Actions build: [#42133405035](https://github.com/ARMoir/WIN31DSK/actions/runs/42133405035).
- Pinned release tag: [`tandy1000ex-win30-mouse-verified-2026-11-05`](https://github.com/ARMoir/WIN31DSK/tree/tandy1000ex-win30-mouse-verified-2026-11-05), pointing to commit `121ae1d8d8a64a6b02b9ffcbc77065813af5f8e5`.

**The release contains the original byte-for-byte image that the owner tested on physical hardware.** It is preserved independently of 30-day Actions artifact retention. Do not replace the verified image when trying new drivers.

## Tested hardware

| Component | Verified configuration |
| --- | --- |
| Machine | Tandy 1000 EX, NEC V20 |
| Disk | XTIDE CompactFlash, 31,808-sector image |
| Serial adapter | Tandy EX/HX 3-in-1 V2, COM1 at `0x3F8`, IRQ4 |
| Mouse | Dexxa M-DX800S serial, Mouse Systems mode |
| DOS driver | CuteMouse 2.1b4, 8086-compatible |
| DOS startup | `C:\CTMOUSE.EXE /S14 /M` automatically from `AUTOEXEC.BAT` |
| DOS verification | `MTEST.COM`, mouse movement and button responses |
| Windows OS | **Windows 3.0** |
| Working Windows mouse driver | **Windows 1.04** original `MSMOUSE1.DRV` for Mouse Systems on COM1 |
| Windows driver size | 1,966 bytes |
| Windows driver SHA-256 | `99b3578809422728d64ad4cdbe17361cdde400840167c8d90c7499842c2812b8` |
| Windows mouse setting | `mouse.drv=msmouse1.drv` under `[boot]` in `C:\WINDOWS\SYSTEM.INI` |
| Windows graphics | Original working `TANDYDSP.DRV`, unchanged |

**Boot behavior:** The computer boots to the ordinary DOS command prompt. It does **not** launch Windows automatically. The `PATH` includes `C:\WINDOWS` so Windows starts only when the user manually types `WIN`.

The owner confirmed that this particular Windows 1.04 driver image works on the Tandy after the Windows 3.0 mouse drivers failed.

## Rebuild from source

- [Single-image GitHub Actions workflow](../../.github/workflows/tandy30-cutemouse.yml), branch `TANDY30`.
- [Windows 1.04 COM1 source driver](win104_msmouse1.drv.gz.b64), pinned by checksum and restored in CI.
- [8086-compatible CuteMouse builder](build_cutemouse.sh).
- [DOS image builder and mouse setup](build_mouse.py).
- [Detailed hardware verification, failure history and preservation policy](VERIFIED_RELEASE.md).
- [Archived failed INT33 experiments](int33-test/README.md).
- [One-time GitHub Release preservation workflow](../../.github/workflows/tandy30-archive.yml).

The [archive workflow run #42135354904](https://github.com/ARMoir/WIN31DSK/actions/runs/42135354904) downloaded the **exact** image from the owner's successful run, checked its SHA-256, verified the FAT16 startup files and Windows driver, and published it as an immutable-reference GitHub Release asset. The original, checksum-pinned source code remains available for rebuilds.

## Using the image

1. Download the verified image from the Release and flash it to the correct-capacity CompactFlash card.
2. Boot into DOS; CuteMouse should load without manually typing any startup commands.
3. Type `MTEST` to verify the DOS mouse. Press Esc to exit.
4. Type `WIN` whenever you want Windows 3.0. Windows mouse support works with the original Windows 1.04 Mouse Systems driver.

For a recovery from an **experimental** driver that fails to start Windows, set `mouse.drv=nomouse.drv` under `[boot]` in `C:\WINDOWS\SYSTEM.INI`; this boots Windows without the mouse.

## Rejected drivers

The original Windows 3.0 `MOUSE.DRV`, Windows 3.0 `MSMOUSE1.DRV`, Microsoft Mouse 9.01, and multiple INT33 binary-patched versions caused Windows startup crashes or hangs on physical Tandy hardware. **None of these should be substituted into the known-good image.** See [historical test notes](int33-test/README.md) for details.

Any future enhancements must preserve the working release, the original Windows 1.04 COM1 mouse driver, and the user's requirement that Windows never auto-start.
