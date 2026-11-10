# Large RGBI lookup-table trial: FAST4K vs MAX8K vs BURST4K

**November 10, 2026: Native builds and independent color-oracle checks passed. Initial physical Tandy EX performance measurements now recorded below.** These are individual stopwatch readings, not repeated controlled trials. Colors/panning/long-term stability for each new driver were not explicitly reported.

## Download and build details

- [Bootable 16 MB CF image, PIXMAX default](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-fast4k-max8k-burst4k-2026-11-10/TANDY1000EX_WIN30_LARGE_LUT_4K_8K_CF.img)
- [Versioned release and standalone drivers](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-fast4k-max8k-burst4k-2026-11-10)
- [Successful GitHub Actions run #42895339011](https://github.com/ARMoir/WIN31DSK/actions/runs/42895339011)
- Card SHA-256: `5772d3d3dea95c5607eb1205675564f1caf47658e4d66887b00fa749201f7bd7`
- All **426** original files were SHA-256-identical, including corrected PIXMAX.DRV, original DIBXY, T4CGA, boot logo, original serial mouse, CGA fonts, panning executable, Windows user profile, games and three-row Program Manager groups. Exactly nine opt-in files were added: three drivers, three INI snapshots and three DOS selector BAT files.

## At DOS, exit Windows first

| DOS command | Behavior |
| --- | --- |
| `FAST4K` then `WIN` | Experimental **4,096-byte** direct-plane lookup; replaces repeated four-bit nibble index assembly with full input-plane byte tables |
| `MAX8K` then `WIN` | Experimental **8,224-byte** LUT (8,192 bytes for 12-bit RGB contribution + 32 bytes intensity), merging three RGB color planes into one lookup |
| `BURST4K` then `WIN` | Same 4,096-byte LUT as FAST4K, plus tested two-group burst structure; bypass per-group bank-wrap masking only after safe bank-boundary check |
| `PIXMAX` then `WIN` | Known-good, original-color owner-tested **1,024-byte** lookup, default on this new image |
| `DIBXY` then `WIN` | Earlier owner-tested 16-color driver fallback |
| `T4CGA` then `WIN` | Original Tandy four-color driver and alternate layout |

If a test driver shows incorrect colors, missing graphics, mouse artifacts, slow startup or panning problems, exit Windows or reboot and select `PIXMAX` then `WIN`. Do not reflash merely to switch modes.

## Compiled native driver sizes and memory

| Driver | LUT bytes | Driver file bytes | Windows NE segment minimum bytes | Compiler / ISA check |
| --- | ---: | ---: | ---: | --- |
| Original PIXMAX | 1,024 | 61,968 | 126,985 | Owner-tested on NEC V20 |
| FAST4K | 4,096 | **64,992** | **130,011** | Passed 8086/MASM/NE |
| MAX8K | 8,224 | **69,168** | **134,179** | Passed 8086/MASM/NE |
| BURST4K | 4,096 | **65,200** | **130,219** | Passed 8086/MASM/NE |

Total NE segment minimum allowance: **196,608 bytes (192 KiB)**. None of these drivers requires V20-only opcodes, unlike the earlier separate PIXV20 trial. The NE allocation sum is not a measurement of Windows free RAM or peak runtime usage.

### How these algorithms differ

**FAST4K / BURST4K.** For each of the four original IRGB planes, direct-index `CS` tables provide the packed contributions for both four-pixel halves of an eight-pixel group. Eight tables of 256 word entries each = **4096 bytes**. This avoids the repeated nibble extraction in the old 1 KiB PIXMAX loop, trading four extra table reads for fewer shifts. Both use word stores, but BURST4K adds the guarded unrolled 2-group loop.

**MAX8K.** An index of 12 bits (B/G/R four-bit nibble each) points to one prepacked four-pixel RGB-contribution word: 4096 entries × 2 bytes = **8192 bytes**. Intensity contributes a second 16-entry word LUT (32 bytes). It still creates the 12-bit index at runtime, so **this is not guaranteed faster than PIXMAX or FAST4K**, even though the table is much larger. These are actual table contents that influence every pixel, not dummy padding.

The original assembly's channel order is **intensity, red, green, blue**, matching the color-correct PIXMAX. All source generators were compared with independent bit-serial reference routines over 65,536 exhaustive and 60,000 additional deterministic randomized pixel-plane patterns, plus the original owner-reported red/blue regression. Program Manager and Calculator start-up, text, cursor, panning and full/partial repaint require real-hardware verification.

## Real-hardware results, November 10, 2026

The owner provided a photo of stopwatch notes for each large-table trial. These are Program Manager and Calculator startup times in seconds.

| Driver / source | Program Manager | Calculator | Display observations |
| --- | ---: | ---: | --- |
| **PIXMAX corrected 1 KiB, earlier separate run** | Not established for corrected driver | **18.8 sec** | Owner verified corrected colors and good responsiveness |
| **FAST4K** | **57 sec** | 24 sec | No specific additional feedback |
| **MAX8K** | 59 sec | **21 sec** | No specific additional feedback |
| **BURST4K** | 58 sec | 24 sec | No specific additional feedback |
| PIXFAST original smaller LUT, earlier separate run | 58 sec | 21 sec | Previously tested |
| PIXBURST original smaller LUT, earlier separate run | 59 sec | 21 sec | Previously tested |
| PIXV20, earlier separate run | 57 sec | 23 sec | Previously tested |
| PIXDIRTY, earlier separate run | 59 sec | 22 sec | Previously tested |

**Conclusion:** There is no clear measured speed win from increasing the table beyond corrected PIXMAX's 1 KiB. The larger MAX8K achieves 21-second Calculator time, slower than the earlier 18.8-second PIXMAX result. FAST4K and BURST4K both need 24 seconds. The 57/58/59-second Program Manager differences may be within stopwatch and boot-to-boot variation; corrected PIXMAX Program Manager startup remains unreported. Do not call PIXMAX a fundamental hardware limit based on these measurements, but **stop pursuing ever-larger LUTs as the next default optimization**. It is plausible that extra index work, data-memory traffic and instruction-fetch overhead outweigh shifts saved.

**Recommendation:** Retain the owner-approved correct-color PIXMAX as default and preserve all earlier releases. Further significant gains likely require fundamentally different work reduction (profiling real GDI primitives, clipping/unneeded redraw, screen/bank handling, disk/memory bottlenecks) rather than larger fixed RGBI tables. Do not promote any of the new larger-table drivers on these data.

**Build implementation:** [large_tables.py](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/large_tables.py), [build_large_tables.py](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/build_large_tables.py), [pack_large_tables.py](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/pack_large_tables.py), [workflow](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/.github/workflows/tandy30-large-tables.yml).

Owner preference: push the memory-for-speed tradeoff aggressively, but keep the proven PIXMAX default and all original display options reversible.
