# Tandy 1000 EX: separate 16-color candidate05 experiment

**Status:** GitHub Actions build passed; real-hardware test required. NOT a verified functioning 16-color desktop.

**[Download the separate candidate05 CF test image](https://github.com/ARMoir/WIN31DSK/releases/download/tandy1000ex-win30-candidate05-16color-test-2026-11-06/TANDY1000EX_WIN30_CANDIDATE05_CF_31808S.img)** · [Release](https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-candidate05-16color-test-2026-11-06) · [Successful GitHub Actions run #42259337542](https://github.com/ARMoir/WIN31DSK/actions/runs/42259337542)

- Image size: **16,285,696 bytes (31,808 sectors)**.
- Image SHA-256: `21a434e9e39073a4cbb40dab05114d447290fa7c220085af2253b6ebc671c4a7`.
- CI validated all driver/support file checksums and FAT16 readbacks, preserved original Windows display and mouse settings, and confirmed DOS does **not** start Windows automatically.
- The image stages the driver in `C:\TANDY88`; **the user must install it via Windows Setup** before testing candidate05.


## Why a different driver

On the physical Tandy 1000 EX, the fixed-profile `TR53216.DRV` and
the Windows XT fonts failed to reach the desktop. Testing confirms:

- `TANDYDSP.DRV` + original fonts: **Windows 3.0 works**.
- `TANDYDSP.DRV` + Windows XT fonts: **Windows crashes**.
- `TR53216.DRV` + original fonts: **Windows crashes**.
- `TR53216.DRV` + Windows XT fonts: **Windows crashes**.

All three experimental fonts were confirmed present in the expected
`C:\WINDOWS\SYSTEM` folder on physical hardware. Their absence is not
the explanation. The Windows XT test used a separate fixed-profile
`TR53216.DRV`, which is **not** the same binary as the upstream's more
thoroughly validated `TANDY88.DRV`.

Upstream archived candidate05 is a **51,296-byte 8086-compatible**
Windows 3.0 display driver for native Tandy **BIOS mode 09h,
320x200 with 16 colors**. It passed real-mode Program Manager,
Paintbrush and framebuffer tests in a Tandy/8086-configured DOSBox-X
emulator, including 16 colors. This **does not guarantee real
Tandy 1000 EX hardware compatibility**.

- Upstream source: https://github.com/astrobleem/oemdisplay-tandy
- Upstream evidence:
  https://github.com/astrobleem/oemdisplay-tandy/blob/main/src/tandysw/STATUS88.TXT
- Pinned driver SHA-256:
  `ac1aadce894058ab6dbdeab2d2a3fd8673a8b4e78d8798198d295f61f32dafee`

## New controlled card

This alternate build uses the existing, checksum-verified **OEM Setup
control image** as its base, which has the original working
`TANDYDSP.DRV` and Windows 1.04 `MSMOUSE1.DRV` selected. It leaves
DOS, CuteMouse, the original mouse executable, DOS video-memory
reservation, and the **manual `WIN` command** unchanged.

It stages a separate `C:\TANDY88` folder containing:

- Pinned upstream `TANDY88.DRV` candidate05, distinct from TR53216.
- Its own `OEMSETUP.INF` display profile.
- Genuine Windows 3.0 `EGASYS.FON`, `EGAFIX.FON`, `EGAOEM.FON`
  copied **byte-for-byte from the original known-good Windows installation**,
  instead of the experimental Windows XT `XTE*.FON` files.
- The matched Windows CGA grabber and splash support.

The original known-good GitHub Release is never overwritten:
https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05

## Test sequence, strictly in this order

1. Flash the **candidate05 test image** onto a spare matching 31,808-sector CF.
2. Boot to DOS. Optionally run `MTEST`, exit with Esc.
3. Type `WIN` from the root `C:\>` prompt. Since this new card still
   selects stock `TANDYDSP.DRV`, the original four-color Windows desktop
   **must work before continuing**. If not, stop: do not install candidate05.
4. Exit Windows. From DOS, execute:
   ```dos
   C:
   CD \WINDOWS
   SETUP
   ```
   Select Display / Other, supply `C:\TANDY88`, then choose
   **Tandy EX/HX 320x200 16 colors (candidate05)**. Complete changes.
   Keep the existing mouse driver. **Decline modifications** to DOS
   AUTOEXEC.BAT or CONFIG.SYS.
5. At DOS, check `C:\WINDOWS\SYSTEM.INI` under `[boot]` contains
   `mouse.drv=msmouse1.drv`. If Windows Setup changed this, restore it.
6. Type `CD \` and then `WIN` to launch the same **guarded** manual
   launcher, which sets BIOS mode 3, reserves video RAM, and runs
   `C:\WINDOWS\WIN.COM /R`.
7. Report whether the Windows GUI appears, whether 16 colors are actually
   available, and whether the existing serial mouse works.

This is an **A/B test of a materially different display driver** and
genuine Windows 3.0 EGA font binaries, not another font-name swap.

## Safety / recovery

- Never bypass a `RESERVE.COM` video-memory failure.
- Never automatically start Windows during DOS boot.
- If candidate05 crashes, restore `C:\WINDOWS\SYSTEM.INI` from
  `C:\WINXT\SYSOLD.INI` to get the original four-color graphics and
  mouse configuration back. If the installer changed other Windows files,
  use the separate archived known-good release rather than assuming a
  single INI rollback reverses everything.
- The upstream emulator success is **not** proof it will run on genuine
  EX/V20 video hardware.
