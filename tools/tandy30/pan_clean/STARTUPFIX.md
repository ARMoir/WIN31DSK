# Tandy EX 16-color panning home screen: border 2 and Program Manager startup correction

**Release:** [pan-border2-progman-2026-11-06](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-pan-border2-progman-2026-11-06)

**Status:** The preceding HPXY/panning image booted on the owner's physical Tandy 1000 EX, displayed 640x256 logical/320x200 visible, and showed the Games group after Alt+Tab. The exact layout and startup fix here has **not yet been tested on the real machine**.

## Intended first view

- Windows 3.0 runs Program Manager as its normal shell, centered inside the physical visible screen at x=0, y=0, width=316, height=196. The previous geometry 0,0,640,256/maximized made the initial top-left view awkward.
- The existing Main, Accessories and Games group files remain byte-for-byte identical, with all games, group icons and original shortcut targets. Program Manager retains AutoArrange=1 and MinOnRun=0. The default Games window from the original groups remains intact.
- BorderWidth=2, balancing more area with more visible borders.
- The Panning dispatcher is moved from [windows] run=C:\WINDOWS\PAN.EXE to load=C:\WINDOWS\PAN.EXE, with run= now blank. Win3.0 run= minimized Program Manager, as confirmed on the owner's hardware; load= launches panning in the background. No PAN executable changes.
- The first physical screen is 320x200 in 16 colors; the logical desktop is still 640x256. Use Ctrl+Alt+arrows to move around it, Ctrl+Alt+Home for origin, Ctrl+Alt+End for the active window. For settings run PAN.EXE /SETTINGS from Program Manager.
- No changes to WIN.BAT, RESERVE.COM, DOS boot, serial mouse MSMOUSE1.DRV, the graphics driver HPXY.DRV, any fonts, any games, any .GRP, shell executable, or original RRECT/TRIAL7 rollback configuration.

## Recovering from DOS

Exit Windows (or reboot) and use PANOFF then WIN to restore the exact earlier RRECT SYSTEM.INI/WIN.INI/PROGMAN.INI. PANON then WIN reselects the updated HPXY/panning/border2 layout. Keep the known-working separate CF image in case anything fails.

## Provenance

- Baseline: earlier user-tested [640x256 logical pan/border1 image](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-pan-16color-border1-clean-2026-11-06), SHA256 4f73b9c37a9d8b2dfbe12574a3cb7925c09f639e59945986a310c6aa81b22484.
- New disk (renamed GitHub asset, binary bytes unchanged): [TANDY1000EX_WIN30_PAN_16COLOR_BORDER2_PROGMAN_VISIBLE_CF.img](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-pan-border2-progman-2026-11-06/TANDY1000EX_WIN30_PAN_16COLOR_BORDER2_PROGMAN_VISIBLE_CF.img), SHA256 d8d0a38c3bab6f5df1b1f94c90efbb9b34beb2e35b5b4c6e25e53a3ff9102328.
- Size unchanged: 16,285,696 bytes / 31,808 sectors.
- [Build run #42292096866](https://github.com/ARMoir/WIN31DSK/actions/runs/42292096866) verified identical original file inventory; only four INI files changed: WINDOWS/WIN.INI and TANDY88/WINPAN.INI, WINDOWS/PROGMAN.INI and TANDY88/PRGPAN.INI. Both FAT copies and original partition data remain intact.

The first screen should show Program Manager rather than PAN, and the Games window/icons should stay available. Actual visibility and layout still depend on Windows 3.0 behavior on the owner's real EX; no simulated screenshot is claimed.
