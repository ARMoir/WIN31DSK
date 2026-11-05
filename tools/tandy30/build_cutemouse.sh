#!/usr/bin/env bash
# Compile 8086/8088/V20-compatible CuteMouse from pinned GPL sources.
set -euo pipefail

OUT_DIR="${1:-output}"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

JWASM_SHA="0a1008d696109a83d2b02cda90853b0a96218c0e"
CTMOUSE_SHA="0dd8f324bd465376ec3778c785f33398bf909619"

git clone --quiet https://github.com/Baron-von-Riedesel/JWasm.git "$BUILD_DIR/jwasm"
git -C "$BUILD_DIR/jwasm" checkout --quiet "$JWASM_SHA"
make -C "$BUILD_DIR/jwasm" -f GccUnix.mak -j2
ASM="$BUILD_DIR/jwasm/build/GccUnixR/jwasm"
test -x "$ASM"

git clone --quiet https://github.com/davidebreso/ctmouse.git "$BUILD_DIR/ctmouse"
git -C "$BUILD_DIR/ctmouse" checkout --quiet "$CTMOUSE_SHA"
make -C "$BUILD_DIR/ctmouse" AS="$ASM" -j2

CTMOUSE="$BUILD_DIR/ctmouse/ctmouse.exe"
test -s "$CTMOUSE"
python3 - "$CTMOUSE" <<'PY'
from pathlib import Path
import struct
import sys
exe = Path(sys.argv[1]).read_bytes()
if exe[:2] != b"MZ":
    raise SystemExit("CTMOUSE.EXE is missing the MZ executable header")
if len(exe) > 65536:
    raise SystemExit("CTMOUSE.EXE is unexpectedly large")
# The source Makefile sets JWasm -0 (8086 ISA) and produces a DOS executable.
print(f"Created 8086-mode CuteMouse DOS executable: {len(exe)} bytes")
PY
cp "$CTMOUSE" "$OUT_DIR/CTMOUSE.EXE"
cp "$BUILD_DIR/ctmouse/copying" "$OUT_DIR/CTMOUSE_GPL.txt"
printf 'JWasm source: https://github.com/Baron-von-Riedesel/JWasm/tree/%s\n' "$JWASM_SHA" > "$OUT_DIR/CTMOUSE_SOURCES.txt"
printf 'CuteMouse source: https://github.com/davidebreso/ctmouse/tree/%s\n' "$CTMOUSE_SHA" >> "$OUT_DIR/CTMOUSE_SOURCES.txt"
sha256sum "$OUT_DIR/CTMOUSE.EXE"
