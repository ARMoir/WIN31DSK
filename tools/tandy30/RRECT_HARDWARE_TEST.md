# Tandy 1000 EX Windows 3.0: RRECT 16-color rendering trial

**Status:** source-compiled 8086-compatible driver passed the upstream structural, instruction, REP-prefix and link audits. The physical Tandy 1000 EX has **not** yet tested this specific driver. The separately preserved TRIAL7 image is still the chosen known-working baseline.

## Objective

Reduce unnecessary **full-screen shadow-to-VRAM conversion/copies** when Windows 3.0 renders rounded keys, shapes, borders and some native applications. The user reports that the serial mouse is smooth and that the display redraw is the major remaining bottleneck.

The source is the upstream [RRECT bounded-framebuffer experiment](https://github.com/astrobleem/oemdisplay-tandy/blob/main/docs/RRECT.MD). Its 86Box HX/8088 7.16MHz comparison reports approximately 92.5 seconds to 10.4 seconds for Calculator's full repaint, 13.6 to 1.4 seconds for Reversi and 36.1 to 4.5 seconds for Paintbrush. These are application-specific **emulator** results, not a predicted whole-desktop improvement on the owner's EX/V20.

## Exact driver and build history

- RRECT is built from the exact upstream TR5 source commit `1eac04fdc571f73037b502ecf1f085028271866e` and the upstream `src/rrect` tooling pinned to commit `4fe890a951d93826e9ced6dbb98934ef6e0dccd0`.
- The exact archived developer DDK and toolchain inputs are checksum-verified using `tools/BUILDDEPS/LOCK.JSON`.
- A fresh DOSBox-X MASM build of the original TR5 320×200×16 driver reproduced SHA-256 `33f681b0238310ae2614b3c1b923d260c816261442b1fa5cd51867c25a6cef61` **byte-for-byte**.
- The corresponding RRECT candidate is 54,992 bytes, SHA-256 `79719cc78809453fec49bf596eeedcfffc7f96e67cc1b66222e1ab3ac6bb2c19`.
- [Audited RRECT build, GitHub Actions run #42278833076](https://github.com/ARMoir/WIN31DSK/actions/runs/42278833076). The workflow uploaded the compiled driver and build report separately from the CF image.

This RRECT candidate derives from TR5, not TRIAL7. The targeted polyline and non-drawing-marker optimizations can be more significant for certain large redraw workloads, but **some TRIAL7 short-text/border refinements are not included**. The physical test is an A/B comparison, not a blanket claim of superiority.

## CF image layout and safety

The experimental disk image starts from the byte-exact, owner-tested TRIAL7 GitHub release (SHA-256 `73129da6ca249120ee7bb1902b6da6b31eca40753dabe2fcc2a8220372574774`). It adds `C:\WINDOWS\SYSTEM\RR8.DRV` under a new name, saves `C:\TANDY88\SYSRR.INI`, and selects `display.drv=RR8.DRV` under `[boot]` in `C:\WINDOWS\SYSTEM.INI`. Both older drivers remain installed, including TRIAL7's `TR73216.DRV` and the hardware-working `TR53216.DRV`.

All original DOS boot files, `C:\WIN.BAT`, the `TGA3.COM` + `RESERVE.COM` video-memory guard, original Windows 3.0 EGA fonts, CuteMouse and the Windows 1.04 `MSMOUSE1.DRV` Mouse Systems serial driver remain unchanged.

No Setup, automatic Windows boot, mouse change, font change, or CONFIG.SYS change is allowed.

## Real-hardware test

1. Flash the **new RRECT image** to an independent matching **31,808-sector CF card**, keeping the known-working TRIAL7 CF image archived.
2. Boot to DOS. Type `WIN` at `C:\>`. The unchanged launcher will set video text mode, validate the 16KB video overlap reservation, then start `WIN.COM /R`.
3. Compare Program Manager startup, drawing a window, opening Calculator, dragging a window and moving the mouse. A stopwatch is preferable, but a visible speed report is still useful.
4. **Rollback from DOS** (Windows closed): type `REST7` followed by `WIN` to select the known-working TRIAL7 driver. `REST5` and `REST05` are retained for the previous hardware-working alternatives.
5. To select the experimental RRECT driver again: `USER8` followed by `WIN`.

Do not bypass a failed `RESERVE.COM` check. A failed graphics boot does not imply that the disk or serial mouse failed.

## Validation and limits

The build and FAT16 image validation check compiler/link audits, installed driver hash, exact original file readback, both FAT copies, cluster chains, identical mouse/boot/restore/font file content and unchanged card geometry. **No physical execution or cycle-calibrated native speed data has been obtained for this RRECT build.** Any release remains labeled experimental until the user tests it on their EX.
