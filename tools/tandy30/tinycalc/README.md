# TinyCalc for Tandy 1000 EX Windows 3.0 (320x200)

**Status (2026-11-06):** Compiled with original Microsoft C6 Win16 tools targeting 8086, with fixed-point calculations and no FPU requirement. MZ/NE executable structure and entire CF image passed static checks. Physical Windows execution is **not yet tested**.

## Downloads

- [Standalone TCALC.EXE (7,759 bytes)](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-tinycalc-compact-test-2026-11-06/TCALC.EXE)
- [Entire CF test image (16,285,696 bytes)](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-tinycalc-compact-test-2026-11-06/TANDY1000EX_WIN30_RRECT_TINYCALC_320X200.img)
- [GitHub Release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-tinycalc-compact-test-2026-11-06)
- [Successful build and image validation](https://github.com/ARMoir/WIN31DSK/actions/runs/42284466688)

CF image SHA256: fb6559ce06fff1684a7b7b0bccb821cf40ac8c8e70d593bbd3c66c807f9cbf00
TCALC.EXE SHA256: b221357c128240984d9096d7635e685d80148e54342f06a4e80fdefa7f006ec4

## How to use

1. Flash the separate test image to a correctly sized CF card, or copy only TCALC.EXE into C:\WINDOWS on the existing one.
2. Boot DOS, type WIN to start Windows through the original video-memory reservation launcher.
3. From Program Manager use File > Run > C:\WINDOWS\TCALC.EXE.
4. Test clicks, keyboard input, display, decimals, backspace and calculations.

The stock Microsoft Calculator is untouched, and its Program Manager shortcut still launches the original CALC.EXE. This compact alternative is an original 8086 program with its own 194x166-pixel window and 20 Windows buttons; physical titlebar and actual runtime layout still require testing.

## Capabilities and limits

Basic signed arithmetic (+ - * /), decimal input, clear, clear entry, backspace, sign toggle, equals, keyboard digits and operations. Values have three fractional digits and maximum magnitude 99,999.999, with truncation after division. Division by zero and overflow show an error. No scientific, memory register, clipboard or full stock-Calculator feature parity.

The image is derived from the RRECT hardware-tried test image. The pipeline verified that **every prior file was byte-for-byte unchanged**, including Microsoft CALC.EXE, SYSTEM.INI, WIN.INI, original Windows 3.0 EGA fonts, graphics drivers, original Windows 1.04 COM1 mouse driver, CuteMouse, AUTOEXEC.BAT and the guarded WIN.BAT. Only C:\WINDOWS\TCALC.EXE and C:\TCALC.TXT were added.

## Future general compact Windows mode

Upstream [compact 320 UI profiles](https://github.com/astrobleem/oemdisplay-tandy/blob/main/src/tandysw/COMPACT.PY) can shrink Windows system caption/menu and control geometry using different OEM metrics and fonts, but they require a **separate reversible driver test**. The user's physical font/driver history includes crashes. That global optimization is not part of this app and has not been hardware-qualified.
