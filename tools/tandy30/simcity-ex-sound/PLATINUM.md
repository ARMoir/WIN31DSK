# SCPLAT 1.0 — experimental Platinum audio for the Tandy 1000 EX

The **TANDY30 branch** contains an experimental SimCity DOS v1.02 sound TSR
named **SCPLAT.COM**. It is separate from the existing **SCEXSND v0.32**
driver, which remains unchanged as a fallback.

## What the experimental driver does

- Recognizes **all eight** known expanded sample-block byte lengths from the
  original DOS v1.02 SOUNDDAT.V4 (11264, 8704, 10752, 13440, 5120, 384,
  768, 1536) at the game's documented DX=0300h sound BIOS clock.
- Instead of reconstructing all eight from PCM in real time, gives each a
  distinct hand-arranged PSG voice/noise patch with pitch sweeps, per-voice
  attenuation, noise envelopes, and quieter harmonic layers.
- Falls back to the v0.32 generic PCM-to-PSG analyzer for unknown sizes and
  playback rates. Preserves INT 1Ah BIOS compatibility, INT 1Ch chaining,
  normal timer speed, source volume, sound completion, and silence on stop.
- Generates no proprietary original sound data and includes no Miles binaries.
- Keeps expensive analysis out of the 7 MHz V20's normal 18.2 Hz playback tick.

**This is experimental, not yet audibly tested on the real Tandy EX.** The
original eight blocks are numbered by length, not by their actual in-game
action. A specific block has NOT been proven to correspond to bulldozing,
roads or any particular disaster, so the patch timbres need A/B testing
before further tuning.

The first edition deliberately does NOT use a faster IRQ0 handler,
concurrent music, or PC-speaker fourth-voice bass. Those features require
separate hardware tests so they do not harm SimCity timing or stability.

## Test on the real Tandy

Download the successful **Tandy 1000 EX SimCity sound shim** Actions artifact
for the TANDY30 branch. The artifact includes SCPLAT.COM, SCEXSND.COM,
TESTPLAT.COM, TESTSND.COM and rollback executables.

1. Reboot the Tandy first. Do not stack this TSR with SCEXSND, old HOOK
   diagnostics or SCGATE. The drivers use a common installed signature to
   discourage simultaneous installation.
2. Use **plain DOS**, not the Windows 3.0 environment.
3. In your SimCity v1.02 directory, run:

       SCPLAT
       TESTPLAT
       SIMCITY

4. TESTPLAT plays all eight synth presets in sequence. Then listen to construction,
   bulldozing and disaster effects in SimCity. Also check game
   responsiveness and whether events trigger reliably.
5. For an A/B test, **reboot**, install SCEXSND instead, and replay the same
   game actions. If SCPLAT causes glitches, stay with SCEXSND.

The current 16 MB DOS/Windows boot image, AUTOEXEC.BAT, original game files,
and old COM rollbacks are intentionally **not modified**.

## Build and safety

Run from this folder on a machine with Python 3 and GNU binutils:

    sh BUILD.SH
    python3 test_build.py
    python3 test_driver.py
    python3 test_platinum.py

The **make_platinum.py** generator derives SCPLAT.S from unchanged
SCEXSND.S, and BUILD.SH assembles SCPLAT.COM. CI validates the original
v0.32 binary hash and original v0.31 fallback separately before uploading
the new artifact. The test checks the eight patches, DOS format, limits and
8086-only instructions, but is NOT an emulator or acoustic test.

See SOUND_RESEARCH.md for the source sample measurements and the research
boundary. TandyAMP supplied the general synthesis, attenuation and
performance ideas, not copyrighted program or audio data.
