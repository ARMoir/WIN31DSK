# Windows 3.0 mouse on Tandy 1000 EX: real hardware status

**Important: the current INT33-patched Windows image is NOT a working
Windows mouse build.** Hardware testing on Tandy 1000 EX (NEC V20,
Tandy EX/HX 3-in-1 serial COM1/IRQ4, Dexxa M-DX800S) confirms:

- DOS boots normally with `C:\CTMOUSE.EXE /S14 /M`.
- `MTEST` responds to pointer motion and buttons.
- Windows 3.0 boots with `mouse.drv=nomouse.drv`.
- Windows hangs/crashes when `mouse.drv=msmouse1.drv` is enabled.
- Windows hangs with the Microsoft Mouse 9.01 INT33 patch.
- Windows crashes almost immediately with the original 3.0 `MOUSE.DRV`
  patched for the OS/2/PMMOUSE INT33 path.

The original patch was demonstrated for PicoMEM PMMOUSE, **not** for
CuteMouse on a real 8250/16450 serial adapter:
https://github.com/FreddyVRetro/ISA-PicoMEM/issues/47

## Current recovery

From DOS edit `C:\WINDOWS\SYSTEM.INI`, under `[boot]`:

```ini
mouse.drv=nomouse.drv
```

Then `WIN` boots Windows without a mouse; DOS mouse support remains intact.

## Better direction

Avoid further edits to the legacy Microsoft mouse-driver initialization
path until there is a specific tested rationale. An actual Windows 3.x
INT33 callback bridge is a better candidate, e.g. the GPL-licensed
`VBMOUSE.DRV` source by Javier S. Pedro, which has a real Windows 3.0
real-mode driver interface and registers a DOS INT33 callback:
https://git.javispedro.com/cgit/vbados.git/tree/mousew16.c

**Architecture caution:** upstream builds use Open Watcom `-6`
(686-oriented code generation), which cannot safely be assumed to run on
the Tandy's V20. A prospective build must target 8086, omit 386-only
hooks, check required INT33 functions against CuteMouse, and verify
Windows actually boots on real hardware. Do not label this fixed from
GitHub CI success alone.

**Startup invariant:** The user wants a normal DOS boot with CuteMouse
autoloaded, not automatic launching of Windows. Windows is started
manually with `WIN` from any directory (`C:\WINDOWS` is on DOS PATH).


## Next controlled hardware test: stock Windows 3.0 driver

The `TANDY30` workflow now publishes **one** output image,
`TANDY1000EX_WIN30_STOCK_MOUSE_CF_31808S.img`, containing the
**unmodified** original Windows 3.0 `MOUSE.DRV` (4,896 bytes; SHA-256
`8ca171370b9b51a1c642ec2a03363f1e30f675733078b91b8eaf34a8299fe476`).
This is deliberately **not** the earlier failed INT33 binary patch, and
**not** the separate `MSMOUSE1.DRV` hardware driver. It retains DOS
CuteMouse `/S14 /M`, a manual `WIN` command, and the original Tandy
graphics driver.

Rationale: Microsoft's stock Windows mouse driver may use DOS INT 33h
when direct hardware probing does not find its supported mouse hardware.
This is a hypothesis to verify on the Tandy, **not a working fix yet**.

Test: Boot DOS → run `MTEST` → exit `MTEST` → type `WIN`.
Report one of: Windows boots and mouse works, Windows boots without mouse,
or Windows crashes/hangs. For any startup regression restore
`mouse.drv=nomouse.drv` in `C:\WINDOWS\SYSTEM.INI` under `[boot]`.
