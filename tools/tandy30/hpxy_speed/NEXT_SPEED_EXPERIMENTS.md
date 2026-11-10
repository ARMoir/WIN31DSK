# After corrected PIXMAX: aggressive Tandy 1000 EX 7 MHz V20 optimization plan

**Status: November 10, 2026.** Owner confirmed correct PIXMAX colors and 18.8-second Calculator load on real Tandy EX. Earlier DIBXY baseline was 24 seconds Calculator, 58 seconds Program Manager. Earlier 58s/22s PIXMAX sample was on a **wrong-color first version**, not the corrected driver. The Program Manager time for corrected PIXMAX has not been reported yet.

## Current owner-preferred bootable image

- [PIXMAX default color-fixed 16 MB CF](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-pixmax-default-colorfix-2026-11-10/TANDY1000EX_WIN30_PIXMAX_DEFAULT_RGBFIX_CF.img)
- [Verified build](https://github.com/ARMoir/WIN31DSK/actions/runs/42869797740)
- CF SHA256: `29881151baf820b3e6453ebb9c024828109abea111e01fe52555c61a840adf73`
- PIXMAX.DRV SHA256: `cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c`

The source image's file inventory was verified: all files were preserved exactly except `WINDOWS/SYSTEM.INI`, which now selects the already user-tested PIXMAX profile. From DOS after Windows exits: `DIBXY` then `WIN` restores proven DIBXY; `T4CGA` then `WIN` restores 4-color. Original logo, mouse, games, desktop groups, CGA fonts, panning and gold baseline remain unchanged.

## High-risk, high-reward experiments to isolate as their own DOS-selectable drivers

### 1. PIXBURST: remove loop-control and bank-mask overhead from the hottest RGBI video converter

The corrected PIXMAX converter already writes 8 pixels via only two `STOSW` instructions and two 256-entry word tables. It still performs per-group loop control and per-group 8-KiB bank-offset remasking. Test 2× and 4× **sequential eight-pixel-group unrolling** with a fast path whenever the entire write span is proven to stay in a single bank. Carry the existing bank wrap code as fallback. Verify every row, viewport pan, unaligned X and right-edge clipping; compare every byte of the two-stage converted video output. Less branching and fewer instructions in the hot path may be a more reliable speed target than expensive additional GDI checks. Results unknown.

### 2. PIXV20: CPU-specialized converter with NEC V20 instruction alternatives

The owner's installed NEC V20 supports some instructions not available on an original Intel 8088. Compile a **V20-only** candidate that tries immediate-count shifts and any other verified short instruction sequences in the pixel engine, keeping the portable PIXMAX as default/fallback. Fewer instruction bytes may help an 8-bit instruction-prefetch bottleneck, but a multi-bit shift is **not automatically faster** on V20 than multiple one-bit shifts; compare actual time, including instruction prefetch and 8-bit video-bus contention, before committing. Static 8086 compatibility audit is no longer valid for V20-only extensions: add a distinct V20 ISA check and never silently ship it for original 8088 models.

### 3. PIXDIRTY: conditional update only when the packed visible pixel group changed

Potentially avoid writes to Tandy video memory for unchanged 4-byte groups, especially during overlapping-window repaints. A full packed visible-frame cache would cost roughly **32,000 bytes** (320×200×4 bits), a substantial amount of the EX's limited RAM. Reading video memory to compare directly can also be slower than writing. To be useful, use a separate RAM allocation and benchmark cache lookup/write avoidance on small clipped rectangles. Restore full conversion for panning, cursor interaction, invalid cache or large refreshes. Treat this as experimental; it may regress the way REPIX did.

### 4. Native-viewport alternative (only if a nonpanning option is acceptable)

Test a dedicated 320×200 logical, 16-color Windows mode to avoid painting offscreen pixels in the 640×256 pannable desktop. This would sacrifice part of the existing desktop/panning functionality, so it must be an optional named mode, not the PIXMAX default. Requires its own resource, desktop/group, and mouse tests. Do not claim Windows 3.0 application compatibility without testing.

## Measurement discipline

- Start from the exact released **PIXMAX-default** CF, installing each candidate as a separate named driver and verified DOS selector. Do not overwrite the gold-standard source or release.
- Require independent reference color oracle matching original `get_nibble` **I-R-G-B** order, explicit red/blue tests, 16 solid colors, known patterns, cursor and pan tests. The earlier incorrect-color PIXMAX passed self-referential tests, which was a real bug.
- Preserve original `WINDOWS/SYSTEM/XDIB.DRV`, `PIXMAX.DRV`, `TANDYDSP.DRV`, `WIN.BAT`, CGA fonts, logo, saved Main/Accessories/Games layout, mouse and color-corrected INI.
- Evaluate Program Manager load, Calculator load, window opening/dragging, Notepad redraw, text, cursor, and left/right/up/down panning. Corrected PIXMAX Calculator reference = **18.8 s**; Program Manager not timed for corrected PIXMAX.
- Do not promote a candidate based on simulator clock counts alone; on-device V20 performance and visual correctness decide.

**Recommendation:** build and compare **PIXBURST first**, then a separate **PIXV20** sequence variant. Consider PIXDIRTY only if a profiling experiment shows that video writes are dominating clipped repaints.
