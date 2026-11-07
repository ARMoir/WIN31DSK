# Tandy 1000 EX: faster HPXY drawing, XR155 A/B driver experiment

**Status (November 6, 2026):** exact upstream XR155 native driver bytes reproduced, 8086/8088 build/instruction audit passed, full gold-standard CF image byte-preservation checked. **Owner reported XR155 works well on the actual Tandy 1000 EX.** This confirms a successful initial physical-hardware use report, but does not establish a measured drawing-speed advantage, exhaustive app compatibility, or all panning-control behaviors. The original HPXY gold-standard release remains the fallback baseline.

## Download

- [Experimental bootable CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-hpxyspeed-xr155-trial-2026-11-06/TANDY1000EX_WIN30_HPXYSPEED_XR155_16COLOR_CF.img) (16,285,696 bytes)
- [Standalone XR155 16-bit display driver](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-hpxyspeed-xr155-trial-2026-11-06/XR155.DRV) (60,800 bytes)
- [Experimental release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-hpxyspeed-xr155-trial-2026-11-06)
- [Successful GitHub Actions workflow](https://github.com/ARMoir/WIN31DSK/actions/runs/42299660110)

Image SHA-256: `0f0238cce3e63182a7da06c5302de45435e03f7911399fdeb0559e8343cf412b`.
XR155 driver SHA-256: `ae2d06f69ff68e64f099c3e0af79028e40e7dca89bd442de23eb18d36be4dca1`.

## What this targets

The gold-standard HPXY 16-color driver exposes a 640x256 Windows 3.0 logical desktop through a 320x200 physical Tandy RGBI viewport. Rendering into the logical planar shadow buffer and repeatedly presenting the visible viewport can be expensive on a V20. XR155 combines the upstream XY shadow and viewport compositor with the RRECT bounded-Output gate, then adds **synchronous narrow X/Y presentation** for selected Windows GDI drawing operations, using the already existing 8088-safe video-copy implementation. It does not switch hardware video modes, change colors or introduce a 386 requirement.

The expected benefit is fewer converted pixels when drawing lines/borders and portions of windows, not a guaranteed overall speedup. Whole-screen drawing and certain unsupported GDI operations still require larger copies. Hardware mode/software mode panning may have different performance characteristics. This is a hypothesis to test against the working HPXY build.

The experimental driver is **exactly** the upstream artifact recorded in [upstream native XR155 emulator qualification](https://github.com/astrobleem/oemdisplay-tandy/blob/main/docs/QUAL/DOSINST/XRSYNC.JSN), whose pinned `runtime_driver_sha256` is also `ae2d06f69ff68e64f099c3e0af79028e40e7dca89bd442de23eb18d36be4dca1`. The compiled NE driver has 12 segments, and its gross NE minimum allocations total 125,803 bytes, under the conservative upstream project limit of 127,531 bytes. These are **not** physical EX speed measurements or free-memory readings.

## A/B experiment without reflashing

Flash the **separate** experimental image to a compatible CF card and boot DOS. Leave the exact gold-standard CF and GitHub release untouched. Launch using the original guarded `WIN` batch. New driver `XR155.DRV` is initially selected.

From DOS **only, after Windows exits or after reboot**:

- `GOLDXY` then `WIN` selects the *original* hardware-verified HPXY.DRV from the gold-standard image, preserving the panning desktop and three group rows.
- `FASTXY` then `WIN` reselects the **XR155.DRV** experimental driver.

These scripts switch only `C:\WINDOWS\SYSTEM.INI` between `C:\TANDY88\SYSHPXY.INI` and `C:\TANDY88\SYSFAST.INI`; neither changes `WIN.INI`, mouse, colors, fonts, Program Manager, PAN, DOS files or group layouts. Running `PANON` restores the original HPXY.DRV; use `FASTXY` again afterward if you want XR155. Both drivers remain installed as distinct .DRV filenames.

Compare the same sequence under each driver on real hardware: Windows launch to all three group rows fully drawn, File Manager and Notepad window opening, repaint after covering/uncovering a window, Calculator paint time, Paintbrush drawing, mouse response, Ctrl+Alt+arrow panning, and Ctrl+Alt+Home. Where practical, record seconds for the same operation. Try exact same panning mode for both tests. Include error/color/cursor artifacts in the report. Do not treat 86Box emulator timings as V20 timings.

## File and compatibility guarantees

Built from an exact 2026-10-26 upstream source snapshot `8d48aa04560a4730c9ee3d946bed865ca9be0c43`, with checksum-locked MASM/LINK4 compiler inputs. Existing 8086 instruction, NE/link, project-memory and source checks ran. The completed CF build independently verified both FAT copies, 31,808-sector geometry, original MBR, all 389 original files and one deliberate SYSTEM.INI modification; exactly five experimental files were added:

1. `C:\WINDOWS\SYSTEM\XR155.DRV`
2. `C:\TANDY88\SYSHPXY.INI` (gold selection snapshot)
3. `C:\TANDY88\SYSFAST.INI` (XR155 selection snapshot)
4. `C:\GOLDXY.BAT`
5. `C:\FASTXY.BAT`

All existing Main, Accessories and Games group bytes (27 shortcuts), panning executables, gold HPXY.DRV, mouse `MSMOUSE1.DRV`, original Tandy font files, DOS startup and guarded `WIN.BAT` are identical to the gold standard.

If XR155 fails to boot Windows or shows bad drawing, reboot to DOS and use GOLDXY. Do not rerun Windows Setup or disable RESERVE.COM to troubleshoot this experiment.

## Further options if XR155 is not fast enough

Investigate narrower affected-region refresh for complex GDI operations, and separately the qualified upstream bounded incremental pan path (2,816-byte stage, pure Y4 no-blank) for longer viewport movements. Neither should be applied automatically to the gold-standard image. A planned independent performance suite should measure full redraw versus thin-geometry drawing on actual V20 hardware.
