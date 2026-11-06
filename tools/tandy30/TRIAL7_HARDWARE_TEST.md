# Tandy 1000 EX: 320×200×16, TRIAL7 rendering performance test (2026-11-06)

**Status: CF image statically validated; physical TRIAL7 test pending.**

The owner hardware-tested the original candidate05 16-color driver on a Tandy 1000 EX with NEC V20, then confirmed a substantial rendering improvement with the TR5 320×200×16 display driver. Mouse movement is smooth; GDI drawing is still slow. This follow-up changes **only the display-driver selection** and adds a third driver, with all mouse, font, DOS, and video-memory reservation components unchanged.

## A/B baselines and pinned binaries

| Driver | File in Windows SYSTEM | SHA-256 | State |
| --- | --- | --- | --- |
| Candidate05 | `TANDY88.DRV` | `ac1aadce894058ab6dbdeab2d2a3fd8673a8b4e78d8798198d295f61f32dafee` | Physical Windows/16-color boot confirmed, very slow |
| TR5 | `TR53216.DRV` | `33f681b0238310ae2614b3c1b923d260c816261442b1fa5cd51867c25a6cef61` | Physical Windows boot and noticeably faster rendering confirmed |
| TRIAL7 | `TR73216.DRV` | `f922f12168de69ec2f8a761ce7fce2cbe2080b9e3fcfb06e3a3dac4faba6d502` | Static image verification only; actual EX boot pending |

TRIAL7 is the exact upstream `TRIAL7/NEW/TR53216.DRV` driver bytes, **renamed** to preserve the installed TR5 binary. Both have NE internal module name `DISPLAY`. Upstream original runtime ZIP SHA-256: `a34deee520743858e89f5fab17f00cb16f9692196d02960f623f29cd2b827d6c`.

Upstream explanation and emulator benchmarks: [TRIAL7](https://github.com/astrobleem/oemdisplay-tandy/tree/main/experiments/TRIAL7), [performance report](https://github.com/astrobleem/oemdisplay-tandy/blob/main/experiments/TRIAL7/EVIDENCE/REPORT.TXT).

## Archived output identities (separate licensed images; not committed)

- Working TR5 source, 16,285,696 bytes: `3c655f715ac371a418e8c714cbd539eee3501f9abdabc8b822885c11ee808275`
- TRIAL7 test image, same 31,808 sectors: `73129da6ca249120ee7bb1902b6da6b31eca40753dabe2fcc2a8220372574774`
- Working candidate05 source: `8af7e2704bbbdb3ce7c98b3fdce7066d11d8236155b8eeefec50de379a0b1c2b`

No Microsoft image is committed. This branch's dedicated GitHub Actions workflow retrieves and checksum-verifies the upstream TRIAL7 package; successful [workflow run #42267655480](https://github.com/ARMoir/WIN31DSK/actions/runs/42267655480) provided the exact driver.

## On the physical Tandy

Flash **only** the separate test image onto a matching spare CF card. Boot to DOS and type `WIN` to invoke the unchanged mode-3/video-reservation guarded launcher. Windows Setup is **not** required. Measure Program Manager startup, window/dialog text and borders, moving windows, cursor response, and colors; do not assume any of the emulator speed ratios predict physical timing.

From DOS with Windows closed:

- `REST5` then `WIN` restores the hardware-working TR5 driver.
- `USETR7` then `WIN` reselects the test TRIAL7 driver.
- `REST05` then `WIN` restores the earlier candidate05 configuration.

These commands copy the exact saved `SYSTEM.INI` configurations, and **never bypass `RESERVE.COM`**. `WIN.BAT`, `MSMOUSE1.DRV`, `CTMOUSE.EXE`, the EGA fonts, and DOS startup remain byte-for-byte identical to the hardware-tested TR5 source. Both FAT16 mirrors, every file chain, readback of all pre-existing files, and exact physical image size passed validation.

The TRIAL7 upstream tests showed around 3.8× faster short labels with the pointer away, 26.5× faster direct vertical lines, and around 1.15× faster two-pixel rectangles in specific emulator workloads, **not full Windows**. Full-screen DIB/redraw cases saw no notable improvement. Further changes must be treated as separate, reversible experiments.
