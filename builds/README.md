# Hardware-tested WIN31DSK builds

These are the **three IMG revisions reported working on a real 10 MHz IBM PS/2 Model 50Z (80286, 2 MB RAM, 1.44 MB floppy, no hard drive)**. They are ordered by capability, with the recommended desktop last.

**Important:** The full disk images contain Microsoft MS-DOS 6.22 and Windows 3.1 system files, which Microsoft has **not** released under the MIT license used for [MS-DOS versions 1.25, 2.0 and 4.0](https://github.com/microsoft/MS-DOS). Accordingly, this public repository provides build metadata and sources/scripts only; **the complete IMG binaries are not distributed here**. Users must obtain these system files through appropriately licensed media.

| Build | Recommended descriptive filename | Original locally verified IMG | Real hardware confirmation |
| --- | --- | --- | --- |
| **SkiFree / 286** | `WIN31DSK-01-SkiFree-286-2MB.img` | `WIN31DSK_LowMemory_SkiFree_GDI_Relocated.img` | Windows 3.1 Standard Mode ran, SkiFree played successfully, and B: switching stopped. Starts from DOS prompt with `WIN /S`. |
| **Classic Games + Calculator / 286** | `WIN31DSK-02-ProgramManager-Games-Calculator-286-2MB.img` | `WIN31DSK_ProgramManager_Games_286_Beta.img` | Windows 3.1 Program Manager launched; Solitaire, Minesweeper, and Calculator ran on the original 286 in this earlier lightweight revision. Later expanded Calculator builds were not stable. |
| **Notepad Desktop / 286** — **preferred** | `WIN31DSK-03-Notepad-Desktop-286-2MB.img` | `WIN31DSK_286_Notepad_CleanLayout_TEST.img` | Windows 3.1 Program Manager, Notepad, and the clean Games/Applications layout were confirmed on the 50Z. The retained games, Clock, and smaller PS/2 mouse driver originated in a prior tested configuration. |

Each IMG is 1,474,560 bytes (a complete 1.44 MB disk). SHA-256, in the same order:

```text
0f451c25b5c139380d5c206676d292e3c0652be2ebb54d1adef562f0443df2fd  WIN31DSK-01-SkiFree-286-2MB.img
4753d27205e8f68862d66b5ee91048a6c7abbcfcbfa9562b261b16053cb97e8b  WIN31DSK-02-ProgramManager-Games-Calculator-286-2MB.img
3963c37e53ef658557138b7f3674503e0f8d862dbb1998a7df1769c8d7408d1a  WIN31DSK-03-Notepad-Desktop-286-2MB.img
```

## Preferred Notepad desktop

- MS-DOS 6.22, Windows 3.1 **Standard Mode** (80286-compatible), Windows 3.1 Program Manager.
- Games: **Solitaire, Minesweeper, Reversi**.
- Applications: **Windows 3.0 Notepad, Windows 3.0 Clock** (with registered `DIGITAL.FON`).
- Original Windows 3.0 smaller PS/2 `MOUSE.DRV`; `ASSIGN.COM B=A` workaround for phantom floppy B: prompts; **no `DOS=HIGH`**.
- Group windows placed in two non-overlapping rows at 640×480 VGA, 88-pixel icon spacing, wrapping titles.
- 75,776 bytes free on its 1.44 MB FAT12 floppy.

## Not part of the verified set

The Calculator-as-shell build produced an immediate A: read error. Both File Manager replacements encountered A: read errors; the expanded Windows 3.0 Program Manager introduced new disk errors; `DOS=HIGH` variants had Calculator memory and/or Clock GDI faults. Those files remain **experimental**, even if some individual apps ran in them.

## Build integrity

The three original images were checked locally for FAT12 mirror agreement and file allocation integrity. Checksums can be verified on a user's local copies:

```powershell
Get-FileHash .\WIN31DSK-03-Notepad-Desktop-286-2MB.img -Algorithm SHA256
```

These hashes identify the exact tested image revisions. Renaming an image does not change its checksum; editing it does.
