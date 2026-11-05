# Tandy 1000 EX Windows 3.0 mouse build

The [TANDY30 GitHub Actions workflow](../../.github/workflows/tandy30-mouse.yml) builds a separate 16 MiB test image from the unchanged `builds/TANDY1000EX_WIN30_NOGAMES_16MB.img` baseline.

The workflow downloads [Microsoft Mouse Software 9.01](https://archive.org/details/msm901) from Internet Archive, verifies the package's pinned SHA-256 checksum, expands `MSM901/MOUSE.DR$` to `MOUSE.DRV` using a small `libmspack` KWAJ extractor, and injects it into `C:\WINDOWS\SYSTEM\MOUSE.DRV`. It changes the `[boot]` mouse driver setting in `SYSTEM.INI` to `mouse.drv=mouse.drv`. No installation utilities, pointer manager or games are added.

**To run:** Open GitHub Actions, select **Tandy 1000 EX Windows 3.0 mouse image**, choose `TANDY30`, click **Run workflow**. A successful build publishes `TANDY1000EX_WIN30_MOUSE_16MB.img` and its SHA-256 file as a downloadable artifact.

The build script verifies the MBR, partition boundaries, size, and read-back of the new mouse driver and SYSTEM.INI. GitHub success does *not* prove compatibility with a V20/8088-class Tandy 1000 EX or serial-port mapping. Test on a spare CF card and keep the known-working image.

**Microsoft Mouse 9.01** includes Windows 3.0 support in its README but primarily targets Microsoft's own mice. A compatible serial mouse and functional COM port are still necessary. We are not installing an updated DOS driver in this initial test, since existing DOS mouse setup should remain unchanged.

The legacy Microsoft driver is downloaded at build time and is **not committed** to this repository. The resulting disk image contains proprietary third-party software; assess licensing before redistributing artifacts.
