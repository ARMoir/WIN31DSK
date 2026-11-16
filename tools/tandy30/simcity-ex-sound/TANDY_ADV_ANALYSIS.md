# TANDY.ADV investigation (SimCity Classic DOS v2.00)

**Source:** owner-provided `SimCity_DOS_EN_Version-20-Quaders-Release(1).zip`, archive entry `Sim City v2.00/DATA/TANDY.ADV` (8,746 bytes, SHA-256 `ccf90daba63f33e686d89eb1205a817c90723f2dec6095978ad20c3a9b3cf80f`).

**Scope:** Original DOS SimCity **v1.02** remains the game running on the NEC V20 Tandy 1000 EX. This investigation describes the newer v2.00 **Miles Design Drivers music/MIDI driver**, *not* a direct replacement for the `SCEXSND` v1.02 Tandy digital-sound BIOS TSR. The corresponding v2.00 `README.TXT` explicitly distinguishes line 2 (`*.ADV` MIDI/music) from line 7 (`*.ADV` digitized sound). This binary has a music-driver-type header matching `PCSPKR.ADV` rather than digitized-audio `SBDIG.ADV`.

## Verified byte-level findings

All file offsets are hexadecimal and **file offsets**, not loaded DOS memory addresses. This table records inferences from direct 16-bit Intel instruction disassembly and from contained data tables; it does not reproduce proprietary driver code.

| Offset(s) | Observed behavior | Engineering implications |
| --- | --- | --- |
| `0x00DF` | Embedded name `Tandy 3-voice internal sound`. | Confirms the intended synthesizer. |
| `0x035A–0x036F` | Silences all three tone channels via writes to PSG I/O port `0xC0`; writes `0x68` to I/O port `0x61`. | Sets an explicit audio-route state. On an EX, port `0x61` bits 5–6 select the PSG route and bit 4 can disable the internal speaker; altering this state must be done cautiously. |
| `0x00FD–0x015C`, `0x015D–0x01BC` | Two matching 96-entry note lookup arrays; 4 low divisor bits and upper divisor bits. | Extremely fast PSG pitch programming using lookup tables instead of floating-point. |
| `0x01BD–0x023C` | A 128-entry volume/attenuation lookup mapping MIDI-scale values to PSG attenuation codes 15 (silent) through 0 (loudest). | A useful model for controlled per-channel fade and gain, not a digital PCM reconstruction method. |
| `0x023D–0x0242` | Precomputed volume and tone latch masks for the three tone channels. | Avoids repeated register-mask calculations on a slow 8088/V20. |
| `0x03D3–0x0435` | Periodic update toggles an offset state and refreshes active voices. | Evidence of timed modulation/pitch changes, useful as a conceptual reference for smoothing effects. |
| `0x0497–0x04E2` | Checks the availability of three hardware voice slots, allocates one and invokes a fallback when all slots are occupied. | Distinct voice management is preferable to unconditionally using all three channels for one effect. |
| `0x05BC–0x069E` | Looks up surrounding semitone divisors and computes a weighted interpolated pitch using a `0x2000` reference and signed arithmetic. | Smooth portamento/pitch bend without high-frequency recalculation of pitch from scratch. |
| `0x06B7–0x06D6` | Writes PSG tone latch, data and volume at `0xC0`, separated by short instruction delays. | Gives proper register order and pacing for Tandy chip writes. |

Example frequency-divider values, independently reconstructed from the two note tables using `3,579,545 / (32 * period)`: table index 45 = 508 (~220 Hz), index 57 = 254 (~440 Hz), index 69 = 127 (~881 Hz). These values demonstrate octave-consistent note mapping.

The chip supports **three tone channels and one noise channel**; neither `TANDY.ADV` nor the EX offers a native 8-bit DAC. The ADV expects the Miles MIDI interface and cannot replace `SCEXSND.COM` or be directly loaded by original DOS SimCity v1.02.

## Comparison with SCEXSND v0.32

- `SCEXSND` intercepts the v1.02 **digital** sound BIOS calls and tries to approximate arbitrary PCM as tone/noise; it does not receive MIDI notes or named sound events.
- `TANDY.ADV` starts with note and volume information. Its pitch table is a good fit for MIDI but **not a direct substitute for PCM pitch detection**.
- The current v0.32 PSG writes already use the correct 10-bit divider and direct `0xC0` output. The potential differences are pitch smoothing, amplitude-envelope shape, tone allocation and optional audio-multiplexer setup.
- **Port 0x61 routing is not a guaranteed volume boost.** On an EX, source selection affects the internal/external path; since v0.31 already produces audible PSG sound, sound routing evidently works in the user's current configuration. Changing port 0x61 without preserving other bits could interfere with the speaker, keyboard and timer controls.
- Pitch/volume changes in the current TSR are tied to the 18.2 Hz DOS timer. Adding fast chip writes, MIDI lookups or more elaborate synthesis will not automatically solve the limited temporal resolution or improve every disaster effect.
- No evidence in `TANDY.ADV` identifies which **v1.02** sound buffer is used for bulldozing vs road construction. Those mappings need to be established from v1.02's original game, not from Miles MIDI.

## Suggested enhancements, in risk order (not yet implemented)

1. **Per-channel volume envelopes and damped pitch changes.** Reuse the *concept* of lookup-based attenuation and interpolation; store previous pitch/attenuation per voice to smooth abrupt 55 ms changes. Keep an audible, conservative default.
2. **More deliberate voice allocation.** Reserve one main tone, use another for harmonic/rumble and noise only for rough attacks. Avoid three equally loud oscillators that muddy bulldozing and disasters; enable changes through a testable option.
3. **Optional PSG routing on the EX.** If audio routing genuinely requires it, read-modify-write port `0x61` to select the PSG while preserving unrelated bits and restoring previous state if feasible. Do **not** simply copy the Miles driver's unconditional `0x68` write into a TSR on arbitrary PCs.
4. **Register pacing.** Add a minimal delay between the PSG's tone-latch, frequency data and attenuation writes only if actual hardware produces glitches; the existing I/O instructions may already be slow enough at 7 MHz.

**Status:** Investigation only; v0.32 source/binary, existing tests, Windows 3.0 image, and AUTOEXEC.BAT remain unchanged. The observed techniques have not been demonstrated to sound better in v1.02 until an implementation is tested on the actual EX.

### References

- User-provided `TANDY.ADV` and `README.TXT` from DOS SimCity Classic v2.00.
- [Tandy 1000 SX Technical Reference Manual](https://www.lo-tech.co.uk/downloads/manuals/tandy/Tandy_1000SX_Technical_Reference_Manual.pdf): three-voice sound circuit and port 61 multiplexer.
- [IBM PCjr and Tandy 1000 multiplexer analysis](https://nerdlypleasures.blogspot.com/2013/06/ibm-pcjr-and-tandy-1000-sound.html): model differences, EX volume path.
- [SN76489 specification and period formula](https://tanepiper.github.io/game-frame/hardware/tandy-psg).
- [Miles sound driver categories from `README.TXT`](https://github.com/ARMoir/WIN31DSK/tree/TANDY30/tools/tandy30/simcity-ex-sound): installation and research in this project.
