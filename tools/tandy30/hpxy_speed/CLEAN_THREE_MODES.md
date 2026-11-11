# Tandy 1000 EX Windows 3.0: clean three-mode CF release

**New release, November 11, 2026.** The exact source-card manifests and assembled image passed static preservation and DOS FAT16 checks. New combined profiles still require physical NEC V20 hardware confirmation.

## Download

- [Clean 16 MB CF disk image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-clean-three-modes-2026-11-11/TANDY1000EX_WIN30_THREE_MODES_CLEAN_CF.img)
- [Versioned GitHub release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-clean-three-modes-2026-11-11)
- [Successfully completed build #43091033815](https://github.com/ARMoir/WIN31DSK/actions/runs/43091033815)
- [Detailed removed/added file manifest](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-clean-three-modes-2026-11-11/THREE_MODES_MANIFEST.json)
- **Image SHA-256:** `a5aba16e31376c7b3d6aa6723e5f2d68b6d1bc761c8e34bf1f826a3562a3d024`.
- 16,285,696 bytes, 31,808 sectors.

## Three native display choices

Exit Windows completely to DOS before choosing a driver. After the selector runs, enter `WIN` manually; Windows does not autostart at boot. The original `WIN.BAT` resets the Tandy to DOS video mode 3, reserves video memory with `RESERVE.COM`, then runs Windows in real mode. Never invoke `WINDOWS\WIN.COM` directly.

| DOS selection then `WIN` | Driver | Screen | Status |
| --- | --- | --- | --- |
| **`T4CGA`** | `TANDYDSP.DRV` | **640×200, 4 colors, no panning** | Original Microsoft Tandy 4-color. Previously owner-tested and highly responsive; original wide Program Manager group snapshots |
| **`NOPAN16`** | `TR73216.DRV` (TRIAL7) | **320×200, 16 colors, native, no panning** | Exactly the original real-hardware-booted TRIAL7 driver and EGA font profile; newly integrated with current compact three-row group layout |
| **`PIXMAX`** | `PIXMAX.DRV` | **320×200, 16-color viewport of 640×256 desktop, with panning** | Corrected owner-tested PIXMAX, Calculator **18.8 seconds**, preferred default and 3-row compact layout |

**Initial selected profile is PIXMAX.** `NOPAN16` sets `WINDOWS\SYSTEM.INI` to the original owner-tested `SYS7.INI` contents, and `WIN.INI` to the panning desktop's simple background/BorderWidth=2 but with `load=` (not `load=C:\WINDOWS\PAN.EXE`). The native TRIAL7 display driver itself is 320×200 without an expanded logical desktop. It uses the original EGA font trio in the successful prior TRIAL7 system profile. The group/layout snapshots use the current compact Main/Accessories/Games layout; test their appearance on actual hardware, because the old TRIAL7 and newer PIXMAX profiles were previously tested in different complete images.

`PIXMAX` and `T4CGA` DOS selectors and their original matched profiles, desktop snapshots, fonts and drivers are **byte-identical** to the working source release. Every switch verifies the six files it installs with DOS 6.22 `FC /B` and does not start Windows until you manually enter `WIN`.

## Exactly which experiments were removed?

The image started from the checksum-pinned corrected PIXMAX release containing **426 files**. The clean image has **351 files**:

- **348** surviving original files are byte-for-byte unchanged.
- **78** old experiment files were removed from the DOS directory inventory, including the unused TANDY88/TR5/RR8/HPXY/XR155/XDIB/PIXFAST display drivers, unused mode-switch BATs, staging INIs, trial fonts, spare Windows XT installer files and alternative pan-control experiments.
- **3** new files were added: `NOPAN16.BAT`, `TANDY88\NOPAN16.INI`, and `TANDY88\WINNP.INI`.
- The only root display mode selectors are `T4CGA.BAT`, `NOPAN16.BAT`, and `PIXMAX.BAT`. (The existing `WIN.BAT` launcher and `AUTOEXEC.BAT` are not display selectors.)
- The only available EX-specific 16-color experiment driver binaries left under `WINDOWS\SYSTEM` are the selected native TRIAL7 and corrected PIXMAX; the Microsoft four-color display driver remains. Standard Microsoft Windows installation component binaries, including unselected stock display drivers, are preserved rather than stripped from the operating system.
- All Windows applications and the complete Main, Accessories and Games icon groups, the original custom Windows logo/splash, Windows 1.04 Mouse Systems serial driver, `CTMOUSE.EXE`, `MTEST.COM`, real-mode DOS startup, `WINXT\RESERVE.COM`, `WINXT\TGA3.COM` and `WINDOWS\PAN.EXE` remain unchanged.

The deleted file names may still exist as unallocated sectors in the raw CF image, since this is a FAT16 file-inventory cleanup, **not** a secure disk wipe. They are no longer DOS-visible or selectable.

## Test plan and limitations

1. Boot image. DOS command `WIN` should launch correctly in default 16-color PIXMAX pannable mode, with original colors, serial mouse, logo, and 3-row Program Manager.
2. Exit to DOS, select `NOPAN16`, then `WIN`. The Windows 3.0 screen should present a fixed 320×200 native desktop. No movement/panning should occur at any edge. Check text and 3 rows with the original TRIAL7 EGA fonts and mouse.
3. Exit to DOS, select `T4CGA`, then `WIN`. Check 640×200 4 colors, original wide three-row layout and responsiveness.
4. Return to `PIXMAX` and `WIN` to verify the 640×256 logical panning desktop is restored.

The individually selected TRIAL7 and PIXMAX drivers were previously observed on physical Tandy hardware, but this **combined three-profile image has not yet been tested on the real machine**. A reliable Program Manager and Calculator startup comparison of NOPAN16 versus corrected PIXMAX has not been performed; it is not accurate to call TRIAL7 definitely faster without measurement. If NOPAN16 causes issues, reboot to DOS and use `PIXMAX` then `WIN` to recover.

## Reproducibility

- [Strict FAT16 cleanup, profile and binary preservation packer](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/pack_clean_three_modes.py)
- [Reproducible GitHub Actions build](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/.github/workflows/tandy30-clean-three-modes.yml)
- Verified inputs: owner-tested PIXMAX default image SHA-256 `29881151baf820b3e6453ebb9c024828109abea111e01fe52555c61a840adf73`; owner-tested TRIAL7 native image SHA-256 `73129da6ca249120ee7bb1902b6da6b31eca40753dabe2fcc2a8220372574774`.
- The source gold releases were untouched. All changes were made only to a **new release/image**.
