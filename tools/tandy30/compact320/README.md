# Compact Windows 3.0 user interface experiment, Tandy 1000 EX

**Status: build and real-hardware qualification pending.** Do not substitute any driver from this branch for the hardware-working images without the complete, successfully validated separately published CF test image.

The physical 320 x 200 x 16 color limit of first-generation Tandy EX/HX graphics remains unchanged. Genuine 640 x 200 x 16 output requires enhanced Tandy graphics from later SL/TL/RL hardware or a compatible external graphics adapter. The existing 640 x 256 x 16-color Windows XT HPXY desktop is a *logical*, pannable desktop with a 320 x 200 physical viewport.

## Reversible compact UI experiment

- Keep the 320 x 200 x 16 RRECT drawing driver and compile a fresh alternative with the upstream `COMPACT.PY` compact320 OEM profile.
- Original Windows 3.0 CGASYS.FON, CGAFIX.FON and CGAOEM.FON are present on the owner's hardware-tested CF image (verified by GitHub Actions inspect run #42285644599). This avoids introducing experimental replacements.
- The existing `C:\WINDOWS\WIN.INI` uses `BorderWidth=4`; the trial sets it to `1`.
- Compact profile replaces graphics resource sizes for titlebar buttons (16x8) and scrollbar arrows/thumbs (12x8) and updates associated font/display descriptors. It does not patch Windows USER.EXE or the serial mouse.
- Original `SYSTEM.INI` and `WIN.INI` are saved independently. Planned DOS `CMPOFF` restores both from the saved pre-trial copies, while `CMPON` selects compact mode. All known-working drivers stay installed.
- Preserve 31,808-sector CF geometry, original guarded `WIN.BAT` launcher, CuteMouse, original Windows 1.04 `MSMOUSE1.DRV`, the RRECT and TRIAL7 restore paths.
- Clipping of stock fixed-size programs (notably Calculator) can remain even if Windows titlebars shrink. Do not promise that every stock application fits.
- `WIN.INI BorderWidth=1` alone only saves border pixels; it does not shrink the caption or force application content to reflow.

## Source and build

- [Compact-profile GitHub Actions build](https://github.com/ARMoir/WIN31DSK/actions/workflows/tandy30-compact320.yml)
- [Historical TR5 source](https://github.com/astrobleem/oemdisplay-tandy/tree/1eac04fdc571f73037b502ecf1f085028271866e)
- [Opt-in compact OEM metrics source](https://github.com/astrobleem/oemdisplay-tandy/blob/main/src/tandysw/COMPACT.PY)
- [Existing hardware-tested RRECT image](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-rrect-16color-test-2026-11-06)
- [Existing hardware-tested TRIAL7 baseline](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-trial7-16color-performance-2026-11-06)

A successful compiler and filesystem audit would establish a *new experimental boot image*, not physical GUI compatibility. The user's previous tests demonstrated that font/driver mismatches can crash Windows on the real EX. No unverified build is labelled hardware-working.
