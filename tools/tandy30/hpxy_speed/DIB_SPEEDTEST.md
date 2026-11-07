# Tandy 1000 EX, next 16-color responsiveness experiment: XR155 + DIB unroll

**Status, November 6, 2026:** Built, statically validated and published as a **separate optional CF test image**. There is **no physical-Tandy performance measurement or compatibility confirmation** for this candidate. The owner's preferred XR155 + CGA-font default, adaptive four-color switch and original hardware-verified gold standard remain byte-for-byte unchanged.

## Tested contents and links

- [Download 16 MB experiment CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-xrcga-dib-speedtest-2026-11-06/TANDY1000EX_WIN30_XRCGA_DIB_SPEEDTEST_CF.img)
- [Release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-xrcga-dib-speedtest-2026-11-06)
- [Successful build / binary validation](https://github.com/ARMoir/WIN31DSK/actions/runs/42325319905)
- [Standalone XDIB driver](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-xrcga-dib-speedtest-2026-11-06/XDIB.DRV)
- CF image SHA256: `adca85db75d58d33238d4e39fdd1138180776c77fd16d8b322c796159aefcb8c`
- Experimental `XDIB.DRV`: 61,040 bytes, SHA256 `c9f2737c11c06044cb80c00d0bec410de5a9f23d3f5c28bcaf20f298ad18f49c`

## Switching without reflashing

The new image boots **exactly the prior preferred XRCGA configuration** by default. It contains the existing 320×200 16-color physical view, 640×256 pannable desktop, CGA bitmap fonts, BorderWidth=2, original three-row Program Manager, preserved boot logo and original mouse. Both the 4-color fallback and gold-standard HPXY remain installed.

From DOS, **after exiting Windows**:

| DOS commands | Display / intent |
| --- | --- |
| `DIBXY`, then `WIN` | Test experimental XR155+DIB converter. Same CGA fonts, same 16 colors and panning |
| `XRCGA`, then `WIN` | Restore the original tested XR155 with CGA fonts |
| `T4CGA`, then `WIN` | Original responsive Microsoft four-color Tandy display, CGA fonts, 640-wide Program Manager |
| `FASTXY`, then `WIN` | Original XR155 with XT font family |
| `GOLDXY`, then `WIN` | Original unoptimized HPXY with original XT fonts |

The `DIBXY.BAT` script reuses the existing reliable six-file profile switch, selecting `C:\TANDY88\XDIB.INI` and the unchanged 16-color Program Manager snapshots. It checks every copied file using `C:\DOS\FC.EXE /B` before reporting success. Running `XRCGA` restores the existing unmodified XR155 binary and all three groups, regardless of which of the four-color modes was selected previously.

## Why it might help (and limits)

XR155 already narrows visible screen updates for selected Windows GDI Output calls. The remaining full viewport refreshes, 4-bit DIB import/export and Windows GDI/Kernel work still cost many cycles. The upstream [DIB-only performance experiment](https://github.com/astrobleem/oemdisplay-tandy/blob/main/experiments/SOLPERF/README.MD) unrolls two fixed 4-byte-per-group conversion loops. In a controlled 86Box HX emulator experiment, 64-call DIB microbenchmarks showed `SetDIBits` 4,120→3,625 ms (~12%) and `GetDIBits` 2,471→2,197 ms (~11%); a full Solitaire startup improved by only about 1.16%. Those results apply to the upstream reference driver, not this XR155 combination or the owner's physical V20. The benefit might be modest or absent for Calculator and Program Manager.

The new candidate compiles with pinned 8086 instruction restrictions, unchanged DIB pixel operations, MASM/LINK4, and the conservative NE memory budget. The upstream DIB source was pinned by exact Git blob `e75be73fd88a109ae1f93b85191a7c30337e680b`. XR155 source/toolchain remain pinned to original older commits and the overlay is applied after XR155's X/Y patch. We did not add a large palette table, modify cursor ownership, shorten retrace timing or touch the panning startup logic.

The build verified every existing file in the adaptive XRCGA CF image was unmodified. Exactly **three files were added**:

- `C:\WINDOWS\SYSTEM\XDIB.DRV`
- `C:\TANDY88\XDIB.INI`
- `C:\DIBXY.BAT`

Checks included FAT mirrors, partition size, all existing Program Manager and games/shortcut resources, existing font files, all EXE/COM/DRV binaries, DOS protected `WIN.BAT`, boot splash/logo files, serial mouse and original switchers.

## Useful physical tests

Compare the same application under **XRCGA** and **DIBXY**, keeping XTIDE and CF card unchanged:

1. Windows fully draws its three-row Program Manager (record time if convenient)
2. Calculator fully draws all buttons (historical XRCGA baseline about 24 seconds)
3. Paintbrush opening a saved 16-color bitmap, zoom/scroll or repainting an overlapping bitmap window (bitmap conversion is the direct target)
4. Cursor, color accuracy, all three program groups and Ctrl+Alt+arrows/Control+Alt+Home

If the screen or cursor looks wrong, restart at DOS and use `XRCGA` to restore the previous XR155 driver immediately. Never replace the gold-standard CF image or original release.

## Further possibilities

This DIB-unrolling trial is intentionally small and reversible. If it only improves DIB workloads modestly, the next meaningful optimization needs safe dirty-rectangle/copy instrumentation on **BitBlt, text and whole-window updates**, plus real-hardware measurements. More aggressive batching or skipping video updates can break cursor/overlap correctness and would require an isolated build with dedicated framebuffer regression tests first.
