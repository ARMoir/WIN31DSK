# Tandy 1000 EX: PIXMAX triple-turbo real-hardware shootout

**Build date:** November 10, 2026

**Initial physical NEC V20 timings reported November 10, 2026.** The owner tested PIXFAST, PIXBURST, PIXV20 and PIXDIRTY, recording both Program Manager and Calculator timings. These are preliminary single-run measurements; screen colors, panning and long-term stability of each experimental driver have not yet been individually confirmed. Compilation and reference-image tests alone are not sufficient to qualify a new default.

## The new experimental CF card

- [Download complete 16 MB bootable card](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-pixmax-triple-turbo-2026-11-10/TANDY1000EX_WIN30_PIXMAX_TRIPLE_TURBO_CF.img)
- [GitHub release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-pixmax-triple-turbo-2026-11-10)
- [Build and verification run](https://github.com/ARMoir/WIN31DSK/actions/runs/42878927239)
- CF SHA-256: `660e9bf5cfc27593878f694460ffb376b3e5b8d965c904861bf4f0e62d28b402`

**Default stays owner-tested color-corrected PIXMAX:** 16 colors, compact CGA fonts, 320×200 hardware viewport on 640×256 pannable desktop, original three-row Main/Accessories/Games layout, all applications, boot splash/logo and original Windows 1.0 serial mouse driver. PIXMAX previously achieved Calculator startup in **18.8 seconds** on the user's physical NEC V20. No corrected-PIXMAX Program Manager time is on record.

**File-integrity audit:** All 426 original image files passed SHA256 identity; exactly nine optional files were added: three Windows display drivers, three DOS profile snapshots in `C:\TANDY88`, and three DOS selector BATs in `C:\`. The protected original gold-standard release and the corrected PIXMAX-default release have not been changed.

## November 10, 2026: actual NEC V20 comparison (owner-provided photo of stopwatch notes)

The phone screenshot lists each driver followed by a Program Manager time and Calculator time. "Fast" is interpreted as the PIXFAST selector. It also shows a standalone **54** before the "Fast" label, without its associated driver or task visible. **Do not assign that 54 seconds to PIXMAX or any particular workload.**

| Driver | Program Manager startup | Calculator startup | Notes |
| --- | ---: | ---: | --- |
| PIXFAST | 58 sec | **21 sec** | Tied fastest Calculator among these four |
| PIXBURST | 59 sec | **21 sec** | Tied fastest Calculator among these four |
| PIXV20 | **57 sec** | 23 sec | Fastest Program Manager among these four |
| PIXDIRTY | 59 sec | 22 sec | No measurable improvement relative to PIXFAST/BURST in these samples |
| **Corrected PIXMAX baseline, earlier separate test** | Not confirmed for corrected build | **18.8 sec** | Remains fastest recorded Calculator time overall |

**Interpretation:** PIXBURST does **not** uniquely win the Calculator test. It ties PIXFAST at 21 seconds, and both trail the earlier color-corrected PIXMAX's 18.8-second measurement. PIXV20 leads Program Manager startup by one second relative to PIXFAST. These small differences might be run-to-run noise until repeated. Do not promote any new experiment as the default based on these numbers. Maintain correct-color PIXMAX as the standard.

**Next action after checking visual correctness and repeatability:** test 4/8/16 KiB lookup variants and memory-for-speed tradeoffs under the newly approved **192 KiB (196,608-byte) experimental NE minimum-allocation ceiling**. Keep each table-size experiment independent and avoid changing the default until it wins a real-hardware comparison.

## Try all three, no repeated flashing

Exit Windows fully to the DOS prompt before each selection. Type the selector, then `WIN`.

| Selector | Engine | Key change | Risk / constraint |
| --- | --- | --- | --- |
| `PIXBURST` | Two adjacent PIXMAX eight-pixel groups per loop | When an entire row is proven to fit within the current 8 KiB VRAM bank, skip the expensive per-group wrap mask; also optimize panning stage copies | May be slower for short/clip-heavy spans |
| `PIXV20` | NEC V20-specific PIXMAX | Substitute 80186/V20 immediate-count `SHR BL,4` and `SHL AL,4` opcodes for four repeated single-bit shifts in each table index | **NEC V20 ONLY.** Do **not** run on an Intel 8088/8086 |
| `PIXDIRTY` | PIXMAX with read-before-write video comparisons | Read matching packed words from B800h and skip two-byte writes if the same pixels are already displayed; staged panning memory always receives the original write | Video reads can be slow on an 8-bit bus and may negate the savings |
| `PIXMAX` | Owner-tested, corrected 1 KiB RGBI lookup | Restore known-good performance and colors | Recommended default |
| `DIBXY` | Pre-PIXMAX 16-color engine | Backup driver | Original baseline |
| `T4CGA` | Original four-color Tandy driver | Responsive four-color setup, wider Program Manager | Four instead of sixteen colors |

The `PIXV20` driver intentionally emits four V20/80186-only shift opcodes using the byte assembler directive and verifies those sequences in the compiled binary. The upstream 8086 instruction audit does **not** decode raw byte directives. The other two trial drivers remain 8086-compatible.

## Suggested quick real-machine comparison

Check for correct red/blue title bars first. For each driver, open Program Manager, open Calculator once if useful, then move Calculator across Notepad and uncover some text. Move the mouse over window borders, scroll a group, and verify left/right/up/down desktop panning including return home. Missing graphics, flicker or freezes disqualify a driver regardless of elapsed time.

Important performance metric is **subjective redraw responsiveness**, not just Calculator startup. PIXDIRTY's VRAM read-before-write can regress significantly. The user's corrected PIXMAX reference remains **18.8 seconds for Calculator**.

After any experiment, return to DOS and run:

```bat
PIXMAX
WIN
```

If a driver makes Windows unusable, restart the Tandy and type the same two commands at DOS. No changes to BIOS, XTIDE firmware or boot sectors are needed.

## Exact implementation

- [Pixel-engine patcher](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/pixtrials.py)
- [Native driver builder](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/build_pixtrials.py)
- [CF preservation packer](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/pack_pixtrials.py)
- [Reproducible GitHub Actions workflow](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/.github/workflows/tandy30-triple-turbo.yml)

Original build-validated driver sizes: **PIXBURST 62,272 bytes, PIXV20 61,952 bytes, PIXDIRTY 62,000 bytes**. The minimum native Windows NE allocations fit within the prior conservative 127,531-byte project budget for all three. The memory ceiling has since been raised to **192 KiB for new experiments**; that is a build allowance, not proof of additional usable conventional RAM. Initial actual V20 timings are documented above.

**Do not promote a trial as default just because it builds.** The known-good color-corrected PIXMAX stays the first-run profile and original gold release is preserved.
