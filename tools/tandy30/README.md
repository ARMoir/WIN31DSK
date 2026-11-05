# Tandy 1000 EX, Windows 3.0 mouse build

This branch keeps `builds/TANDY1000EX_WIN30_NOGAMES_16MB.img` as an **unchanged 16 MiB baseline**.

The [Tandy Windows 3.0 mouse workflow](../../.github/workflows/tandy30-mouse.yml) builds `TANDY1000EX_WIN30_MOUSE_16MB.img` as a downloadable GitHub Actions artifact. It copies the baseline, injects a Microsoft-serial-mouse-compatible **Windows 3.0** driver, edits `C:\WINDOWS\SYSTEM.INI` under `[boot]` to set `mouse.drv=mouse.drv`, verifies both files, and produces a SHA-256 checksum.

## Required driver

Supply a legitimately obtained Windows 3.0-compatible `MOUSE.DRV` at:

`drivers/tandy30/MOUSE.DRV`

The current baseline includes `C:\MOUSE\MOUSE.SYS` and `C:\MOUSE\MOUSE.COM`, but only `C:\WINDOWS\SYSTEM\NOMOUSE.DRV`. Those DOS drivers **cannot** substitute for the missing Windows driver. The workflow deliberately fails without `MOUSE.DRV`, rather than pretending to produce a mouse-enabled image.

For a Microsoft-compatible serial mouse, look for a genuine Windows 3.0-compatible Microsoft Mouse 8.x driver. The workflow's structural check is only a sanity check, not a proof of Windows version or hardware compatibility. Do not substitute `NOMOUSE.DRV` or rename an unrelated driver.

## Run

1. Add `drivers/tandy30/MOUSE.DRV` to the `TANDY30` branch.
2. Open **Actions > Tandy 1000 EX Windows 3.0 mouse image > Run workflow**, selecting `TANDY30`.
3. Download the `TANDY1000EX_WIN30_MOUSE_16MB` build artifact after the job succeeds.
4. Write the image to a test CompactFlash card and boot on real Tandy hardware.

The workflow installs `mtools` on Ubuntu, which modifies the FAT partition *inside* the raw disk image without reformatting its MBR, partition table, or XT-IDE-compatible layout.

## Hardware test

Confirm the serial mouse uses the expected COM port and IRQ, check that it works in DOS, then test Windows 3.0. A successful workflow verifies file installation and INI configuration only; it does not prove actual hardware mouse movement. Keep the original CF backup until the new image has booted and been tested.

The disk image contains historical proprietary software. Ensure you have permission to distribute any additional driver before committing it to a public repository.
