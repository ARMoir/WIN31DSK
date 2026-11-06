# Hardware-verified Tandy 1000 EX: DOS 5 + Windows 3.0 serial mouse

**Status:** Verified working on physical hardware on 2026-11-05.
**Preserved release:** https://github.com/ARMoir/WIN31DSK/releases/tag/tandy1000ex-win30-mouse-verified-2026-11-05
**Original successful CI run:** https://github.com/ARMoir/WIN31DSK/actions/runs/42133405035
**Source commit for successful run:** [121ae1d8d8a64a6b02b9ffcbc77065813af5f8e5](https://github.com/ARMoir/WIN31DSK/commit/121ae1d8d8a64a6b02b9ffcbc77065813af5f8e5)
**Source branch:** `TANDY30`

## Exact archived image

- Artifact: `TANDY1000EX_WIN104_MSSYS_COM1_CF_31808S`.
- File: `TANDY1000EX_WIN104_MSSYS_COM1_CF_31808S.img`.
- SHA-256: `eca08b0eb4283854bfef71d98d8febe08ad8de89eb3d52a109a0b9d39993fa34`.
- Image size: **16,285,696 bytes / 31,808 sectors**. Do not replace with a larger nominal 16 MiB image; this size matches the actual CF card.
- This release stores the **exact binary extracted from the successful workflow**, not a new approximation or rebuild.

## Verified hardware and configuration

- **Computer:** Tandy 1000 EX, NEC V20 CPU, XTIDE CompactFlash.
- **Serial port:** Tandy EX/HX 3-in-1 V2 COM1, base 0x3F8, IRQ4.
- **Mouse:** Dexxa M-DX800S serial, Mouse Systems protocol.
- **DOS:** CuteMouse v2.1b4 8086-compatible build, started by `AUTOEXEC.BAT` using **`C:\CTMOUSE.EXE /S14 /M`**.
- **DOS test:** `MTEST.COM` reports movement and button state correctly.
- **Windows:** Windows **3.0** with the **Windows 1.04** original `MSMOUSE1.DRV` for Mouse Systems COM1, 1,966 bytes, SHA-256 `99b3578809422728d64ad4cdbe17361cdde400840167c8d90c7499842c2812b8`.
- **Windows setting:** `[boot]` `mouse.drv=msmouse1.drv` in `C:\WINDOWS\SYSTEM.INI`.
- **Video:** Original working `TANDYDSP.DRV` remains unchanged.
- **Startup:** DOS prompt. **Windows does not start at boot.** The user manually types `WIN` from DOS. `C:\WINDOWS` remains on `PATH`.

## Physical test outcome

The owner reported: **"Omg that one works!"** after loading the Windows 1.04 mouse-driver image. Earlier trial images all failed when Windows loaded: Windows 3.0's `MSMOUSE1.DRV`, the 3.0 stock `MOUSE.DRV`, Microsoft Mouse 9.01, and two INT33 binary patch variants.

Do **not** switch the default Windows driver to any failed version. Keep the working release unchanged when experimenting. Commit future work in a different build or branch.

## Rebuild and verify

The reproducible image generator is `/.github/workflows/tandy30-cutemouse.yml` on `TANDY30`; the original Windows 1.04 mouse-driver bytes are in `tools/tandy30/win104_msmouse1.drv.gz.b64`.

To verify a downloaded release image:

```sh
echo "eca08b0eb4283854bfef71d98d8febe08ad8de89eb3d52a109a0b9d39993fa34  TANDY1000EX_WIN104_MSSYS_COM1_CF_31808S.img" | sha256sum -c -
```

The archival GitHub Actions workflow `/.github/workflows/tandy30-archive.yml` checks this exact hash and uploads both the validated disk image and checksum to the release. The release is the permanent distribution location, unlike the expiring workflow artifact.

## On the physical Tandy

1. Write the verified `.img` to the matching CompactFlash card.
2. Boot to DOS; CuteMouse should load automatically.
3. Run `MTEST` to check the mouse (Esc exits).
4. Type `WIN` to launch Windows **manually**.

If changing Windows drivers later causes crashes, boot DOS and set the `[boot]` entry to `mouse.drv=nomouse.drv`. Windows then boots without mouse support; this was a confirmed recovery method.

## Preservation policy

- Keep the verified image + checksum attached to the dedicated GitHub Release.
- Keep the tag `tandy1000ex-win30-mouse-verified-2026-11-05` pointing to the exact source commit used for successful CI, `121ae1d8d8a64a6b02b9ffcbc77065813af5f8e5`.
- Do not overwrite, delete, or silently replace the verified release assets.
- Do not auto-start Windows.
