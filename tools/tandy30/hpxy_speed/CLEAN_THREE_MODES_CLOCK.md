# Tandy 1000 EX: clean 3-mode Windows CF with LS, DOSKEY and manual boot clock

**Released November 11, 2026.**

- [Download bootable 16 MB CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-clean-three-modes-ls-doskey-clock-2026-11-11/TANDY1000EX_WIN30_THREE_MODES_LS_DOSKEY_CLOCK_CF.img)
- [Versioned GitHub release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-clean-three-modes-ls-doskey-clock-2026-11-11)
- [Successful GitHub Actions build #43093138912](https://github.com/ARMoir/WIN31DSK/actions/runs/43093138912)
- [Exact SHA256 / preservation manifest](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-clean-three-modes-ls-doskey-clock-2026-11-11/THREE_MODES_MANIFEST.json)
- CF SHA-256: `bbcef7d76bfdf1a2eb3d93927313378887736ba2f173f8f491c4842d468cccfd`

## Boot sequence

Tandy 1000 EX has no battery-backed RTC in this hardware configuration. DOS software cannot infer the real current time from a CompactFlash disk when the machine is powered off. Thus `AUTOEXEC.BAT` now invokes the new `C:\DOS\CLOCK.BAT` **before** starting resident `DOSKEY`. The existing PATH already contains `C:\DOS`. The exact code appended to `AUTOEXEC.BAT` is:

```bat
REM Tandy EX has no battery-backed clock; prompt each boot
CALL C:\DOS\CLOCK.BAT
REM Command history: Up/Down arrows, F7 list
C:\DOS\DOSKEY.COM /INSERT
```

The clock utility is intentionally not resident:

```bat
@ECHO OFF
ECHO.
ECHO ===== TANDY DATE AND TIME =====
ECHO Set date, or press ENTER to keep the shown date.
DATE
ECHO Set time, or press ENTER to keep the shown time.
TIME
ECHO.
```

These are DOS 6.22 built-ins, with prompts for date and time when run without parameters. Press Enter to leave the shown value as-is; after cold boot, on a Tandy without RTC, the shown time/date can be wrong. Use the actual current date/time whenever needed. `CALL` is important: invoking another BAT without CALL in AUTOEXEC would transfer control without returning to start DOSKEY. At any future DOS prompt, type `CLOCK` to repeat date/time entry.

`C:\DOS\LS.BAT` is also installed with `DIR %1 %2 %3 %4 %5 %6 %7 %8 %9`. This supports `ls`, `ls /w`, and `ls *.exe` under DOS 6.22. The original `DOSKEY.COM` executable is present on the pinned source disk and left untouched. It enables command history, F7 list, and commonly Up/Down keys, but the Tandy EX's physical keyboard translation has not yet been tested.

## Three display modes unchanged

From DOS exit Windows and run the mode selector, then `WIN`:

- `T4CGA`: original Microsoft 640×200 four-color driver
- `NOPAN16`: original TRIAL7 native 320×200 16-color nonpanning driver
- `PIXMAX`: corrected 16-color pannable driver with compact 3-row desktop, remains default; previously measured Calculator 18.8 seconds

The build statically verified the known CF source-image SHA256, boot partition, both FAT mirrors, original DOS and Windows executables, saved groups, logo, serial mouse, display drivers and profile switchers. It removed 78 obsolete experiments from the FAT inventory, retained 348 original source files unchanged, added the native NOPAN16 selectors and CLOCK.BAT, and only modified AUTOEXEC.BAT and (when different) LS.BAT. All prior GitHub releases are immutable and untouched.

**Hardware qualification:** these utilities and the combined profile switching have not yet been tested on physical Tandy hardware. If DOSKEY Up/Down fails on the unusual Tandy keys, test F7, or disable the single DOSKEY startup line. The date/time prompts should work as ordinary DOS commands. If an RTC expansion or connected host clock later becomes available, CLOCK.BAT can be changed to sync automatically instead.
