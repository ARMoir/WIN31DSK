# Tandy 1000 EX Windows 3.0 mouse build

The [TANDY30 GitHub Actions workflow](../../.github/workflows/tandy30-mouse.yml) builds a separate image sized exactly for a 31,808-sector (16,285,696-byte) CF card from the unchanged `builds/TANDY1000EX_WIN30_NOGAMES_16MB.img` baseline.

First, `shrink_cf.py` safely shrinks the DOS partition and FAT16 boot parameters, after confirming the discarded clusters are unused. The unchanged 16 MiB baseline stays in GitHub.

The workflow downloads [Microsoft Mouse Software 9.01](https://archive.org/details/msm901) from Internet Archive, verifies the package's pinned SHA-256 checksum, expands `MSM901/MOUSE.DR$` to `MOUSE.DRV` using a small `libmspack` KWAJ extractor, and injects it into `C:\WINDOWS\SYSTEM\MOUSE.DRV`. It changes the `[boot]` mouse driver setting in `SYSTEM.INI` to `mouse.drv=mouse.drv`. No installation utilities, pointer manager or games are added.

**To run:** Open GitHub Actions, select **Tandy 1000 EX Windows 3.0 mouse image**, choose `TANDY30`, click **Run workflow**. A successful build publishes `TANDY1000EX_WIN30_MOUSE_CF_31808S.img` and its SHA-256 file as a downloadable artifact.

The build script verifies the MBR, partition boundaries, size, and read-back of the new mouse driver and SYSTEM.INI. GitHub success does *not* prove compatibility with a V20/8088-class Tandy 1000 EX or serial-port mapping. Test on a spare CF card and keep the known-working image.

**Microsoft Mouse 9.01** includes Windows 3.0 support in its README but primarily targets Microsoft's own mice. A compatible serial mouse and functional COM port are still necessary. We are not installing an updated DOS driver in this initial test, since existing DOS mouse setup should remain unchanged.

The legacy Microsoft driver is downloaded at build time and is **not committed** to this repository. The resulting disk image contains proprietary third-party software; assess licensing before redistributing artifacts.

## If the mouse still does not work

Booting successfully validates the disk layout, not mouse function. Confirm the **new mouse build**, rather than the no-games baseline, is the image written to the CF card. The no-games baseline still has `mouse.drv=nomouse.drv` in Windows 3.0.

At a DOS prompt, run `TYPE C:\\WINDOWS\\SYSTEM.INI` or use the DOS editor to check the `[boot]` section. A mouse-enabled build must show `mouse.drv=mouse.drv` and include `C:\\WINDOWS\\SYSTEM\\MOUSE.DRV`.

Next, verify the serial mouse physically responds in DOS, and whether the serial port is COM1 or COM2. If DOS does not recognize the mouse, the remaining problem may involve the serial port, wiring, interrupt, mouse protocol, or DOS mouse-driver selection, rather than the Windows driver. The build does not force COM1 because that mapping has not been verified on the Tandy expansion card.

The target size is **31,808 sectors**, not the larger nominal 16 MiB (32,768 sectors). Avoid the Win32 Disk Imager oversize warning by using the updated image.

## DOS mouse test: MTEST.COM

The workflow now assembles `tools/tandy30/mtest.s` into a tiny **8086/V20-compatible** DOS program and places it at `C:\\MTEST.COM` in the generated mouse-enabled CF image. The standalone `MTEST.COM` is also attached to the Actions build artifact.

**On the Tandy:** boot to a DOS prompt (do not start Windows), then type:

```dos
C:\\>MTEST
```

The program clears to an 80-column text display, reports the BIOS COM1/COM2 base addresses and whether the DOS INT 33h driver is responding, and shows mouse X, Y and button mask values in hex. Move the mouse and click both buttons. Press **Esc** or **Q** to exit. Button bits are **left=0001, right=0002, middle=0004**. The program does **not** install a mouse driver or speak to the serial port directly.

**How to interpret results:**

- **No DOS mouse driver** means INT 33h initialization failed. Check that `MOUSE.SYS` was actually loaded by CONFIG.SYS (or install the DOS mouse driver separately).
- **Driver detected, but X/Y never change:** most likely the DOS driver can't see the physical mouse, or the wrong COM port/protocol, serial wiring, power, or IRQ is in use.
- **X/Y change and buttons respond:** DOS is receiving mouse events. If Windows still has no pointer, focus on the Windows 3.0 `MOUSE.DRV` setting and driver compatibility.

BIOS COM port values of `0000` mean no port is recorded at that BIOS-data-area entry, which is not conclusive proof that an expansion-port serial adapter is missing. Typical standard addresses are COM1=03F8 and COM2=02F8.

No actual Tandy hardware test is performed by the workflow. The image remains sized to the card's exact 31,808 sectors.

## Experimental CuteMouse 2.1 beta 4 V20 build

A **separate** [TANDY30 CuteMouse workflow](../../.github/workflows/tandy30-cutemouse.yml) creates `TANDY1000EX_WIN30_CTMOUSE_CF_31808S.img` (exactly **31,808 sectors**, 16,285,696 bytes). The original baseline and the earlier Microsoft-mouse test build remain untouched.

The workflow compiles [Davide Bresolin's 8086-compatible CuteMouse 2.1b4 fork](https://github.com/davidebreso/ctmouse) at pinned commit `0dd8f324bd465376ec3778c785f33398bf909619` with [JWasm](https://github.com/Baron-von-Riedesel/JWasm) at pinned commit `0a1008d696109a83d2b02cda90853b0a96218c0e`. It builds with `-0` for the 8086 instruction set (suitable for NEC V20) and includes its GPL license, source links, and a standalone `CTMOUSE.EXE` in the Actions artifact.

The image includes:
- `C:\\CTMOUSE.EXE`, the newly built DOS driver.
- `C:\\MTEST.COM`, the existing INT 33h mouse test.
- Windows 3.0's `MOUSE.DRV` from the pinned Microsoft Mouse 9.01 archive.
- `CONFIG.SYS` with the old `devicehigh=\\mouse\\mouse.sys` line **commented out**. CuteMouse is **not loaded automatically**, so a failed driver cannot strand you at boot.

### Real-hardware test (Dexxa M-DX800S, COM1, IRQ4)

Boot the new image, stop at the DOS prompt, and enter:

```dos
C:\\>CTMOUSE /S14
C:\\>MTEST
```

The `/S14` argument forces COM1, IRQ4. Move and click; `MTEST` should report a detected driver and changing X/Y/button values. If that works, exit `MTEST` with Esc or Q and try `WIN` to see whether Windows 3.0 can use the pointer.

If CuteMouse fails to detect the Dexxa, **reboot** and try the Mouse Systems mode:

```dos
C:\\>CTMOUSE /S14 /M
C:\\>MTEST
```

**Important correction:** In CuteMouse 2.1b4, `/M` enables Mouse Systems detection; `/Y` is deliberately ignored for backwards compatibility. The source's option table confirms this.

You can also copy just the standalone `CTMOUSE.EXE` from the Actions artifact onto your existing DOS CF image for a quick trial, but for a clean comparison use the new image so `CONFIG.SYS` does not load Microsoft `MOUSE.SYS`.

The Mouse Systems switch is a *detection* option. The mouse's physical MC/PC switch still determines what serial protocol it actually sends. If both modes fail, the next useful test is a raw COM1 serial-byte probe, comparing data with the working ELKS configuration (typically 1200 baud). No mouse behavior is claimed until confirmed on the Tandy.

### Rebuilding

Actions → **Tandy 1000 EX Windows 3.0 + CuteMouse (V20 test)** → Run workflow (branch `TANDY30`). Download the artifact `TANDY1000EX_WIN30_CTMOUSE_CF_31808S`, extract it, and flash the `.img`. Keep the original CF card as a fallback.

## DOS autoload, Windows on PATH, native COM1 driver (latest build)

The revised CuteMouse workflow generates **`TANDY1000EX_WIN30_CTMOUSE_MSSYS_CF_31808S.img`**. This variant keeps the same exact **31,808-sector** CF capacity and adds the Windows 3.0 **`MSMOUSE1.DRV`** driver from the user-provided Windows 3.0 installation media. The checked-in compressed driver data is validated against SHA-256 `91a0cf78237b1e3c3e257ea49c1b540eefa4b816e1a69734cf99de57305cb23b` during the workflow. It was extracted from `MSMOUSE1.DRV` (SZDD-expanded) in the source archive.

The image's Windows `SYSTEM.INI` uses:
```ini
[boot]
display.drv=TANDYDSP.DRV
mouse.drv=msmouse1.drv
```
The existing `TANDYDSP.DRV` display setting is preserved, not overwritten. We retain `MOUSE.DRV` for reference but switch active Windows mouse support to the native Mouse Systems COM1 driver. This is a **hardware experiment**, not yet verified on the Tandy.

The updated DOS `CONFIG.SYS` continues to disable the old Microsoft DOS mouse driver. The `AUTOEXEC.BAT` keeps its original entries and extends its PATH with `C:\\WINDOWS`, then runs:
```bat
C:\\CTMOUSE.EXE /S14 /M
```

After boot, the mouse should already be available to DOS programs. Run `MTEST` to confirm it, then type `WIN` at any DOS prompt to start Windows 3.0. **Windows is not started automatically.**

Windows 3.0 uses a separate Windows mouse driver, so working DOS mouse motion does not guarantee a Windows pointer. If mouse movement fails in Windows, note whether clicks or movement are registered, and try the Windows 3.0 Setup mouse configuration next. Do not change the Tandy display driver until we establish that it is responsible.
