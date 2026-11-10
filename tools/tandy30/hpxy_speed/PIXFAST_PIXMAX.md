# Tandy 1000 EX Windows 3.0: PIXFAST and PIXMAX all-out 16-color performance experiment

**IMPORTANT COLOR-CHANNEL ERRATUM (November 10, 2026):** The November 9 experimental `PIXFAST.DRV` and `PIXMAX.DRV` have a **red/blue channel swap**. The user identified abnormal title bar/icon colors on physical Tandy hardware. Those first experimental drivers are **not color-correct** and should not be used for normal work. At DOS, enter `DIBXY` then `WIN` to restore correct colors, or `T4CGA` then `WIN` to select original four-color graphics. The original compiled `get_nibble` macro packs **intensity, red, green, blue** in that order; the new lookup used intensity, blue, green, red. The Python test had replicated the error and was therefore not independent. Both table generators and the oracle have now been corrected. **Corrected November 10 build: [download the RGBFIX CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-dibxy-pixfast-pixmax-colorfix-2026-11-10/TANDY1000EX_WIN30_DIBXY_PIXFAST_PIXMAX_RGBFIX_CF.img).** [Successful GitHub Actions run #42846890830](https://github.com/ARMoir/WIN31DSK/actions/runs/42846890830). Corrected CF SHA-256: `b450250f5553116f248632d5ab7b988d65b18ced6237640548ca0afb35714b10`; corrected PIXMAX.DRV SHA-256: `cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c`; corrected PIXFAST.DRV SHA-256: `755af5c3b7b009d46c7ceb3e22775ca2c384c74cac678dae219ea2a990ece268`. Code-level oracle and build checks pass; corrected colors are **not yet independently confirmed on physical Tandy hardware**. The first November 9 release should be treated as superseded, not as a correct-color benchmark.


**Status, November 10, 2026:** GitHub build and pixel oracle tests passed. The owner has now tested PIXMAX on the physical Tandy 1000 EX and reports Program Manager fully loaded in **58 seconds** and Calculator in **22 seconds**. This is initial operational and timing evidence, not a complete graphics or cursor-correctness qualification. PIXFAST has not yet been timed on hardware.

## Released image and verified CI

- [Experimental 16 MB bootable CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-dibxy-pixfast-pixmax-2026-11-09/TANDY1000EX_WIN30_DIBXY_PIXFAST_PIXMAX_CF.img)
- [Versioned GitHub release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-dibxy-pixfast-pixmax-2026-11-09)
- [Successful GitHub Actions build](https://github.com/ARMoir/WIN31DSK/actions/runs/42729387707)
- CF image size 16,285,696 bytes; SHA256 `d4f6fb206d3f8bc18ea2ea6c39df65fba57fad2d8f2254e4f43aba343d3ec08e`
- `PIXFAST.DRV`: 61,472 bytes; SHA256 `9a7dc0dd192cb0c9b27199f5b64b89bfbc83c89cbef747bdc192604cbf3cc4d3`; gross NE allocations 126,481 bytes
- `PIXMAX.DRV`: 61,968 bytes; SHA256 `6004cf95565162b184492a46120c64632f4ccf212bd3df632fcedd792bbf3450`; gross NE allocations 126,985 bytes
- The existing conservative NE memory ceiling is 127,531 bytes; both new drivers pass. These minimum allocations are not the amount of free conventional RAM.

## How to select modes

The image initially starts with the existing owner-tested **DIBXY** display driver, compact CGA fonts, 320×200 16-color physical viewport, 640×256 pannable desktop, `BorderWidth=2`, and the original three-row Main / Accessories / Games Program Manager.

**Exit Windows fully to the DOS prompt before changing modes:**

| DOS selection and launch | What you get |
| --- | --- |
| `PIXFAST` then `WIN` | Experimental 512-byte-table RGBI converter, CGA fonts and 16 colors |
| `PIXMAX` then `WIN` | Experimental 1024-byte dual-table RGBI converter, CGA fonts and 16 colors |
| `DIBXY` then `WIN` | Restore the owner-tested normal 16-color DIBXY driver; known-good fallback |
| `T4CGA` then `WIN` | Restore the highly responsive original four-color Tandy driver and its wider layout |
| `XRCGA` then `WIN` | Original XR155 with compact CGA fonts |
| `GOLDXY` then `WIN` | Original HPXY 16-color baseline |

Both new DOS BAT selectors inherit the corrected six-file, `FC.EXE /B` byte-verified profile switch with the current compact layout snapshots. They do not require rerunning Windows Setup. The standard DIBXY, XR155, four-color and original HPXY driver files are not modified.

## What's aggressively optimized

In the existing `XYCOPY.ASM` inner loop, an eight-pixel group loads four plane bytes then calls `get_nibble` eight times and assembles four packed RGBI bytes with four byte stores. Ignoring loop-control overhead, that body contains **80 single-bit SHL/RCL instructions per 8-pixel group**: each of eight pixels transposes four plane bits with eight shifts/rotations, and the high nibble of each packed output byte is shifted four more times (16 shifts).

The new engines use a **16-bit lookup result for four pixels**:

- **PIXFAST:** one 256-entry 16-bit code-segment table (512 bytes). Two table lookups and a two-bit shift produce each four-pixel half, followed by `STOSW`. Across eight pixels it executes approximately 20 bit shifts, four table loads, and two word stores.
- **PIXMAX:** two 256-entry 16-bit tables (1024 bytes), one pre-shifted for the upper two RGBI bits. It eliminates the output shifts entirely: approximately 16 input-bit shifts, four table loads, and two word stores across eight pixels. Whether the larger code footprint and lookup traffic is actually faster on the physical NEC V20 is unknown.

These are *instruction counts for the changed inner conversion algorithm*, not clock-cycle timings, measured speedups, or full-window performance projections.

The replacement is strictly confined to the existing XY `xyc_group` converter and its constant CS lookup data. The shadow memory layout, planar RGBI bit significance, four-color alternate driver, original GDI bitmap rasterizer, DIB import/export unrolling, bank masking, half-open clipping, panning stage, cursor overlay, and full-viewport fallback are unchanged. The patcher verifies exact source anchors and reversibility.

### Verified correctness and preservation

The build passed:

1. A Python independent reference oracle for **65,536 exhaustive four-pixel plane combinations**, **250,000 deterministic randomized eight-pixel groups**, and each of the **16 solid Tandy RGBI colors**.
2. The pinned MASM/LINK4 Windows 3.0 display-driver build, with 8086/8088-compatible ISA audit, NE segment validity and conservative allocation budget checks.
3. FAT16 partition / FAT mirror checks and per-file SHA256 preservation of all **420 original files**, including `WIN.BAT`, Windows logo/splash resources, all games, original graphics and font binaries, Windows serial mouse, original group/shortcut files, and panning helper. The one intentional existing-file update is `C:\WINDOWS\SYSTEM.INI` selecting the already-tested DIBXY default.
4. Exactly **six** new files: two display drivers under `C:\WINDOWS\SYSTEM`, two matching INI profiles in `C:\TANDY88`, and two root DOS mode switches. Nothing is replaced in the preserved gold-standard or DIBXY releases.

**Limitations:** Python source-level pixel agreement is not proof that every instruction in the built driver works identically on the physical EX or that it is faster. The driver is real 8086-compatible Windows 3.0 native code and compiled, but **there is no actual Tandy hardware qualification yet**. Do not promote either candidate to the boot default until tested. If anything crashes, shows wrong colors, loses characters, or misplaces the mouse, reboot to DOS and run `DIBXY` then `WIN`.

## Hardware speed comparison

Try `DIBXY`, `PIXFAST`, and `PIXMAX` in any order without reflashing, keeping XTIDE firmware and CF image fixed. Suggested short test: watch Program Manager repaint, launch Calculator once, then drag one window over another and uncover it, checking both speed and complete redraw.

Previous owner-tested **DIBXY baseline:** Program Manager **58 seconds**, Calculator **24 seconds**, and good interactive responsiveness. Previous REPIX text-repaint trial was rejected (Program Manager **71 seconds**, less desirable subjective responsiveness), and its code is **not** present in PIXFAST or PIXMAX. The four-color Tandy/CGA alternative remains available.

### Actual NEC V20 test update, November 10, 2026

| Driver | Program Manager | Calculator |
| --- | ---: | ---: |
| DIBXY, owner-tested baseline | **58 s** | **24 s** |
| PIXMAX, first owner hardware test | **58 s** | **22 s** |
| PIXFAST | Not yet reported | Not yet reported |
| REPIX, rejected | **71 s** | Not reported |

PIXMAX's Program Manager startup was unchanged relative to the DIBXY measurement; Calculator was **2 seconds faster** (8.3% less elapsed time). This is a single unpaired run per profile; it establishes neither statistical significance nor reliable advantage for all workloads. The owner has not yet commented on PIXMAX's subjective interactive responsiveness, panning, text correctness or mouse artifacts. Retain DIBXY as the known-good default until the candidate passes more real-hardware observations. No source or driver changes are warranted by the timing alone.

**Next useful comparison:** PIXFAST versus PIXMAX on the same image, especially Calculator and the responsiveness of overlapping windows. Compare any color glitches, cursor behavior and panning before promoting either driver. The original DIBXY rollback remains `DIBXY` then `WIN` from DOS.


