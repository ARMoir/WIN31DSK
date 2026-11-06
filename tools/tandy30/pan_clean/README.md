# Tandy 1000 EX Windows 3.0: organized 16-color panning desktop

**EXPERIMENTAL, awaiting first physical-machine test.** The source is the user's previously physically exercised RRECT 320×200×16 Windows CF image; this is a **separate, additive CF image** and does not alter the TRIAL7 or RRECT releases. The panning driver comes from upstream Windows XT and has native Tandy HX/EX emulator acceptance, but has not been qualified with the owner's original Windows 1.04 serial mouse driver and V20 hardware.

## Features

- **640×256 logical desktop**, presented as a **320×200, 16-color physical Tandy EX viewport**. This does **not** enable a physical 640×200 16-color hardware mode.
- **BorderWidth=1** instead of 4.
- **Clean Program Manager** arrangement with AutoArrange=1, a maximized logical desktop and a plain teal desktop/background, standard grey menus and navy title bars.
- Simplified background: no tiled wallpaper or heavy checkerboard pattern, reducing unnecessary paint work.
- **ALL existing groups preserved without modifying the original .GRP files**, especially Main, Accessories and **Games** (including all their existing icons/shortcuts). No games, other programs, Windows program files, existing data or folder was deleted.
- The hardware-tested original **Windows 1.04 serial Mouse Systems driver MSMOUSE1.DRV** remains selected and all DOS CuteMouse/COM1 configuration remains byte-for-byte unchanged.
- Upstream HPXY.DRV uses matching upstream CGA-metric XTCSYS/XTCFIX/XTCOEM fonts in separate filenames; all original EGA and CGA fonts stay present and untouched.
- The guarded boot launcher WIN.BAT, including mode-3 reset, RESERVE.COM and WIN.COM /R, is unchanged. Windows still starts manually from DOS, not automatically.

## Download and test

[GitHub panning release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-pan-16color-border1-clean-2026-11-06)

[Complete matching 31,808-sector CF image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-pan-16color-border1-clean-2026-11-06/TANDY1000EX_WIN30_PAN_16COLOR_BORDER1_CLEAN.img)

Flash the new image to a spare CF card of **at least the same capacity**. Boot DOS; start Windows by typing `WIN`. Do **not** rerun Windows Setup. The PAN dispatcher is installed as `C:\WINDOWS\PAN.EXE` and configured under `WIN.INI [windows] run=` to start during Windows startup.

- **Ctrl+Alt+arrow keys**: pan around the virtual desktop.
- **Ctrl+Alt+Home**: return to the upper-left view.
- **Ctrl+Alt+End**: bring the active window into view.
- **Program Manager > File > Run**: `C:\WINDOWS\PAN.EXE /SETTINGS` to adjust panning/presentation.
- Hardware/software selection is supported by upstream HPXY. Default/selected behavior on real hardware is not claimed until tested.

## Fully reversible from DOS

Exit Windows (or reboot) to a DOS prompt before using the scripts. DO NOT run them while Windows is open.

- `PANOFF` followed by `WIN`: restores the **exact original RRECT** SYSTEM.INI, WIN.INI and PROGMAN.INI.
- `PANON` followed by `WIN`: restores the panning driver, border 1 and tidy-layout configurations.
- The earlier `REST7` driver-selection command is still available, but for a complete return to the previous nonpan appearance and startup, use `PANOFF`.

Recovery copies are stored under `C:\TANDY88\SYSBASE.INI`, `WINBASE.INI`, `PRGBASE.INI`, and counterpart `SYSPAN.INI`, `WINPAN.INI`, `PRGPAN.INI`.

## What is and is not solved

The larger 640×256 virtual desktop gives oversized program windows room and lets you reach clipped sections by panning. **It does not make the physical monitor display more than 320×200 pixels at once**, nor does it cause nonresizable applications to shrink. With a larger shadow framebuffer it may use more conventional memory and may be slower than RRECT. The thin borders, compact icon organization, uncluttered desktop and reduced wallpaper work are independent usability improvements. This test does *not* include the separate compact titlebar OEM build, which has different font/driver compatibility risks.

## Published build identity

- [Successful GitHub Actions run #42289210112](https://github.com/ARMoir/WIN31DSK/actions/runs/42289210112)
- Image SHA-256: `4f73b9c37a9d8b2dfbe12574a3cb7925c09f639e59945986a310c6aa81b22484`
- Image size: `16,285,696` bytes (`31,808` 512-byte sectors)
- Initial run #42289116823 passed the image and group-preservation checks but could not publish the release because the release notes were not yet committed. The corrected run completed all steps and uploaded the same type of full CF image.

## Build provenance and static validation

- Input CF image checksum: `bedf5aa14c6259ad526074ce2412528a91f170feda9b3798befb78e8746f5e8b`.
- Upstream fixed [WINXT.ZIP (Windows XT)](https://github.com/astrobleem/oemdisplay-tandy/releases/download/windows-xt/WINXT.ZIP) checksum: `35266732e122068d03c44c98a610621d65c06c38c29b8ca3d1d0513a94d30fca`.
- [Upstream panning controls and native evidence](https://github.com/astrobleem/oemdisplay-tandy/blob/main/docs/PANNING.MD).
- Build workflow checks that every pre-existing file survives, only SYSTEM.INI, WIN.INI and PROGMAN.INI differ, and the original Main, Accessories and Games .GRP files and game executables are byte-identical. The MBR/partition bytes, both FAT mirrors, selected fonts/mouse/driver files and 16,285,696-byte card geometry are also verified.
- Actual physical Windows startup, panning, application access and mouse response remain for the owner to test.

**Do not claim hardware success until the user has tested this image.**
