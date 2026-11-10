# Tandy 1000 EX Windows 3.0 driver memory audit (November 10, 2026)

## Actual Microsoft four-color versus 16-color PIXMAX

Measured from the **binary NE segment tables** in the physically consistent DOS 6.22 / Windows 3.0 Tandy 1000 EX CF images, not estimated from source code or the size of the driver file.

| Driver | Installed filename | On-disk file bytes | NE segment minimum bytes | 16-bit NE segments |
| --- | --- | ---: | ---: | ---: |
| Original Microsoft 4-color Tandy | `C:\WINDOWS\SYSTEM\TANDYDSP.DRV` | **25,840** | **20,005 (19.54 KiB)** | **2** |
| Corrected owner-tested 16-color PIXMAX | `C:\WINDOWS\SYSTEM\PIXMAX.DRV` | **61,968** | **126,985 (124.01 KiB)** | **12** |

The four-color Microsoft driver has a code segment declaring **19,049 bytes** and a data segment declaring **956 bytes**. Its on-disk file is larger than the segment minimums because a Windows NE driver has an executable header, resources, alignment and other bytes that do not map 1:1 to segment minimum allocations.

- Tandy Microsoft `TANDYDSP.DRV` SHA-256: `d593c03e52e338074df3c5c70973197bc61deeb72d615459ad90124afea126e0` (present in original prior Tandy CF image; audited as preserved in all later PIXMAX builds).
- Corrected PIXMAX.DRV SHA-256: `cb635f55688fc1ca4fd284eacc63c009160d46996ce844d4cf0510799018959c`.
- Exact owner-tested source CF for re-audit: `tandy1000ex-win30-pixmax-default-colorfix-2026-11-10`, SHA-256 `29881151baf820b3e6453ebb9c024828109abea111e01fe52555c61a840adf73`.
- [Reproducible FAT16 extraction and NE report](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/driver_ne_memory.py).

The large 16-color increase is consistent with a software planar renderer, shadow framebuffer, panning and conversion, not necessarily a larger system-driver permanent free-RAM loss of exactly 107 KB. **Do not treat the NE minimum sum as peak, working set, free memory, disk image size, or resource heap usage.** Some NE code segments can be demand-loaded/discardable, and there may be additional Windows resources and runtime allocations. Only an on-device Windows memory probe can determine conventional RAM headroom while Calculator and other applications are running.

## User-approved experimental limit increase

**Old experiment limit:** 130,000 bytes of minimum NE segment allocations (~126.95 KiB).

**New experiment limit:** **192 KiB = 196,608 bytes** total minimum NE segment allocations.

**Headroom above existing PIXMAX allocations:** **69,623 bytes (67.99 KiB)**.

**Immutable architectural constraints:** individual 16-bit segment cannot exceed 65,536 bytes; normal 8088/8086-compatible driver code and native V20-only instruction auditing remain separate. The previously approved release remains the default, and experimental profile selectors must permit `PIXMAX`, `DIBXY` and `T4CGA` rollback. A larger aggregate budget does not make any driver faster on its own.

- [New 192 KiB driver build gate and per-segment report](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/build_pixtrials.py)
- [New 192 KiB CF packaging gate](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/tools/tandy30/hpxy_speed/pack_pixtrials.py)
- [Action that generates detailed NE_MEMORY_REPORT.json](https://github.com/ARMoir/WIN31DSK/blob/tandy16-rendering-performance/.github/workflows/tandy30-triple-turbo.yml)

The current PIXBURST, PIXV20 and PIXDIRTY binaries continue to fit within the old 130,000-byte test cap, so recompiling them with a higher acceptance ceiling should produce **no new speed gain**. The larger ceiling permits future candidates with an additional 32 KiB frame cache, larger color lookup structures or separate staging buffers, while preserving known-good drivers. Any memory-consuming feature must be measured for actual application launch, graphics correctness, responsiveness, and panning, especially on a 640 KiB conventional-memory Tandy EX.

## Practical test for the next large-memory trial

On physical hardware, run `MEM /C /P` before launching Windows to inspect DOS conventional-memory consumers. This does **not** measure Windows memory at runtime. For Windows 3.0 real mode, a dedicated test executable should call the Windows memory-management APIs (e.g., GlobalCompact / GlobalFreeSpace) before and after Calculator load. Report numeric free memory and largest contiguous block alongside the driver selection; do not infer available Windows RAM from the NE allocation minimum alone. Such a diagnostic has not yet been bundled and its Windows 3.0 API behavior needs validation.

The Windows boot logo, fonts, mouse, EX-specific video driver profiles, desktop groups and CF gold standard must never be sacrificed for experimental RAM gains.
