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

