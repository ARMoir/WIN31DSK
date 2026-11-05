# Tandy 1000 EX Windows 3.0 mouse build

The [TANDY30 GitHub Actions workflow](../../.github/workflows/tandy30-mouse.yml) builds a separate image sized exactly for a 31,808-sector (16,285,696-byte) CF card from the unchanged `builds/TANDY1000EX_WIN30_NOGAMES_16MB.img` baseline.

First, `shrink_cf.py` safely shrinks the DOS partition and FAT16 boot parameters, after confirming the discarded clusters are unused. The unchanged 16 MiB baseline stays in GitHub.\n\nThe workflow downloads [Microsoft Mouse Software 9.01](https://archive.org/details/msm901) from Internet Archive, verifies the package's pinned SHA-256 checksum, expands `MSM901/MOUSE.DR$` to `MOUSE.DRV` using a small `libmspack` KWAJ extractor, and injects it into `C:\WINDOWS\SYSTEM\MOUSE.DRV`. It changes the `[boot]` mouse driver setting in `SYSTEM.INI` to `mouse.drv=mouse.drv`. No installation utilities, pointer manager or games are added.

**To run:** Open GitHub Actions, select **Tandy 1000 EX Windows 3.0 mouse image**, choose `TANDY30`, click **Run workflow**. A successful build publishes `TANDY1000EX_WIN30_MOUSE_CF_31808S.img` and its SHA-256 file as a downloadable artifact.

The build script verifies the MBR, partition boundaries, size, and read-back of the new mouse driver and SYSTEM.INI. GitHub success does *not* prove compatibility with a V20/8088-class Tandy 1000 EX or serial-port mapping. Test on a spare CF card and keep the known-working image.

**Microsoft Mouse 9.01** includes Windows 3.0 support in its README but primarily targets Microsoft's own mice. A compatible serial mouse and functional COM port are still necessary. We are not installing an updated DOS driver in this initial test, since existing DOS mouse setup should remain unchanged.

The legacy Microsoft driver is downloaded at build time and is **not committed** to this repository. The resulting disk image contains proprietary third-party software; assess licensing before redistributing artifacts.

## If the mouse still does not work

Booting successfully validates the disk layout, not mouse function. Confirm the **new mouse build**, rather than the no-games baseline, is the image written to the CF card. The no-games baseline still has `mouse.drv=nomouse.drv` in Windows 3.0.

At a DOS prompt, run `TYPE C:\\WINDOWS\\SYSTEM.INI` or use the DOS editor to check the `[boot]` section. A mouse-enabled build must show `mouse.drv=mouse.drv` and include `C:\\WINDOWS\\SYSTEM\\MOUSE.DRV`.

Next, verify the serial mouse physically responds in DOS, and whether the serial port is COM1 or COM2. If DOS does not recognize the mouse, the remaining problem may involve the serial port, wiring, interrupt, mouse protocol, or DOS mouse-driver selection, rather than the Windows driver. The build does not force COM1 because that mapping has not been verified on the Tandy expansion card.

The target size is **31,808 sectors**, not the larger nominal 16 MiB (32,768 sectors). Avoid the Win32 Disk Imager oversize warning by using the updated image.
