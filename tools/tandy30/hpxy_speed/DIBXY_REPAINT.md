# Tandy 1000 EX Windows 3.0: DIBXY default plus experimental text repaint

**Status, November 9, 2026: compiled and static-verified; initial real-hardware Program Manager startup measurement reported for REPIX, further repaint correctness and responsiveness testing pending.** The owner already reported that **DIBXY** ran on the physical Tandy 1000 EX, with Program Manager loading in 58 seconds, Calculator in 24 seconds, and a more responsive overall feeling than earlier 16-color configurations. This image changes the default to that previously tested DIBXY driver and adds a separately selectable experimental text-repaint renderer.

## Initial REPIX physical-hardware result (November 9, 2026)

The owner tested `REPIX` (the new `RPAINT.DRV` text-clip repaint candidate) on the physical Tandy 1000 EX and reported **Program Manager ready in 1:11 (71 seconds)**. The prior `DIBXY` Program Manager measurement was **58 seconds**, a 13-second increase (about 22% longer elapsed startup time). These are observations from separate runs, not a controlled benchmark, and do not prove that REPIX has higher redraw latency.

This optimization was designed to reduce conversions for certain *clipped text repaint operations*, not general Windows startup. No REPIX Calculator result, artifact report or subjective interaction assessment has yet been reported. **Keep `DIBXY` as the default**; `REPIX` remains experimental and reversible from the DOS prompt. Useful checks are scrolling Notepad, uncovering text behind windows and checking for stale glyphs or cursor artifacts. Avoid promoting REPIX until there is a measurable or visible interactive benefit without correctness regressions.

The [November 9 verification rebuild](https://github.com/ARMoir/WIN31DSK/actions/runs/42716985298) passed and confirmed file-by-file identical contents to the [November 6 release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-dibxy-default-repaint-2026-11-06), although the raw CF disk hash can differ due to FAT metadata and timestamps.

## Exact verified release

- [Download bootable 16,285,696-byte CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-dibxy-default-repaint-2026-11-06/TANDY1000EX_WIN30_DIBXY_DEFAULT_REPAINT_TEST_CF.img)
- [Release page](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-dibxy-default-repaint-2026-11-06)
- [GitHub Actions verification](https://github.com/ARMoir/WIN31DSK/actions/runs/42327370865)
- [Standalone experimental RPAINT.DRV](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-dibxy-default-repaint-2026-11-06/RPAINT.DRV)
- **CF SHA-256:** `c8aa6efa28571c0d1569a28f1c55465b0082aa51a81e95741fb44fcaf7de2cfc`
- **RPAINT.DRV:** 61,120 bytes, 12 NE segments, SHA-256 `33e8dfb17b09ad2f0b78199181c51d4aa90ae2e4070696186c7e08fd42463f6d`
- **Gross NE minimum allocations:** 126,127 bytes, below original project conservative ceiling 127,531 bytes. This is a linker budget calculation, not conventional-RAM free space.

## Operating and switching (no additional reflashing)

On a freshly flashed experimental CF card, type **`WIN`** from DOS: the system starts with the owner's preferred DIBXY display driver, CGA fonts, 16-color physical 320x200 viewport, logical 640x256 panning desktop, BorderWidth=2, and the same opening Main / Accessories / Games three-row layout.

For a driver comparison, **exit Windows to DOS first**:

| DOS commands | Result |
| --- | --- |
| `REPIX` then `WIN` | **Experimental** RPAINT driver: XR155 + DIB with narrowed presentation for proven clip-bounded ordinary Windows text |
| `DIBXY` then `WIN` | Restore owner-tested DIBXY with CGA fonts and 16 colors |
| `XRCGA` then `WIN` | Original XR155 with CGA fonts |
| `T4CGA` then `WIN` | Responsive original Microsoft four-color Tandy driver, CGA fonts, automatically wider Program Manager |
| `GOLDXY` then `WIN` | Original conservative HPXY 16-color baseline |

The existing `DIBXY.BAT`, `XRCGA.BAT`, `T4CGA.BAT` and `GOLDXY.BAT` are unchanged. New `REPIX.BAT` copies `RPAINT.INI` and the original compact Program Manager profiles, verifying the six files byte-by-byte using bundled `C:\DOS\FC.EXE /B`.

## What actually changed in the renderer

**Important finding:** Our first attempt to optimize column-bounded `BitBlt` did not pass its exact-source guard because the inherited XR155 pipeline **already** bounds both `BitBlt` and single-pixel operations to the smallest proven columns via the existing `FlushRetainColumns` compositor. That path was therefore left entirely untouched. We did not ship a redundant or speculative `BitBlt` patch.

Instead, the new `repaint_textclip.py` patch applies only to the Windows 3.0 `TStrBlt` drawing entry. Its original `text_bounds 0,0,0` helper validates the actual text, font, clipping rectangle, vertical bounds and unmodified rendering semantics. When it sets `dirty=2` (a recognized bounded screen-text operation), the new code saves the **legal clipping rectangle's X endpoints before rendering**, then uses those X endpoints together with the preexisting Y bounds to invoke the **existing** foreground cursor-aware XY viewport compositor. This copies fewer pixels only when the clip is narrower than the view. It does not change the underlying glyph rasterization.

The original `text_flush` path is retained for unsupported/unproven fonts, invalid/null clipping rectangles, memory bitmaps, and other operations. The existing `TExtTextOut`, `TBitBlt`, `TPixel`, `TOutput`, panning logic and mouse compositing instructions are unchanged.

The correctness hypothesis is that `RStrBlt` never writes outside its validated GDI clipping rectangle, so eliminating refreshes *outside that rectangle* cannot miss a changed pixel. Compilation and source-level bounds checks are not equivalent to an actual-Windows framebuffer comparison. This experiment must not be promoted until real Tandy tests show no stale text, missing redraw or cursor artifacts.

### Everything preserved

The successful build verified the original CF image, partition size, FAT mirrors and all **420 existing files**. Only `C:\WINDOWS\SYSTEM.INI` changed to select DIBXY as default. Exactly three new files were added:

- `C:\WINDOWS\SYSTEM\RPAINT.DRV` (compiled experimental driver)
- `C:\TANDY88\RPAINT.INI` (CGA font and RPAINT display profile)
- `C:\REPIX.BAT` (DOS-only verified profile switch)

**All 420 original file bytes**, including the Windows boot logo and splash resources, Main / Accessories / Games `.GRP` files and original shortcuts, original CGA/XT/EGA font binaries, Windows/DOS serial mouse, original XDIB and XR155 drivers, panning helper, safeguarded `WIN.BAT` with `RESERVE.COM`, games, and adaptive four-color layouts remain unchanged. The separately tagged gold-standard release and DIBXY release are untouched.

## Recommended real-hardware comparison

Instead of repeatedly timing Calculator startups, compare interactive behaviors that actually stress the changed text clip:

- Open Notepad. Type lines, select text, move the caret, scroll to reveal previously hidden text. Watch for **missing characters or stale fragments**.
- Open Calculator or File Manager over Notepad, then move and close it, exposing Notepad beneath. Watch whether text repaints fully with no artifacts.
- Check Program Manager group scrolling, the mouse pointer over text, `Ctrl+Alt+Arrow` panning and return home.
- If useful, compare opening a text-filled Notepad window with `DIBXY` versus `REPIX`, with the same desktop and XTIDE firmware.

If any display artifacts, freezes, or cursor issues appear: reboot or exit to DOS, run **`DIBXY`**, then **`WIN`**. No firmware changes or new CF write are necessary.

Hardware performance gain is **unmeasured**. Narrower conversions may improve *text repainting* in clipped child windows but need not improve the initial full-screen Program Manager load or Calculator startup. Future optimization candidates should be chosen only after evidence from this path.
