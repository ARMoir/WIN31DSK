#!/usr/bin/env python3
"""Fetch and expand a pinned Microsoft Mouse 9.01 Windows driver for CI."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import sys
from urllib.request import urlopen
import zipfile
from io import BytesIO

URL = "https://archive.org/download/msm901/MSM901.zip"
SHA256 = "1bf2adf59b9e494dff8cc909e6c7fd76348a32a00224e8b416c5ef96b14c19f4"
MEMBER = "MSM901/MOUSE.DR$"

def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "output/MOUSE.DRV")
    output.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(URL, timeout=120) as response:
        archive = response.read()
    digest = hashlib.sha256(archive).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"Unexpected Microsoft Mouse package SHA256: {digest}; expected {SHA256}")
    with zipfile.ZipFile(BytesIO(archive)) as zf:
        packed = zf.read(MEMBER)
    if not packed.startswith(b"KWAJ"):
        raise SystemExit("MOUSE.DR$ is not the expected KWAJ format")
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "MOUSE.DR$"
        expanded = Path(tmp) / "MOUSE.DRV"
        source.write_bytes(packed)
        subprocess.run(["output/expand_kwaj", str(source), str(expanded)], check=True)
        driver = expanded.read_bytes()
    if len(driver) < 1024 or not driver.startswith(b"MZ"):
        raise SystemExit(f"Expanded driver lacks MZ header (length {len(driver)})")
    output.write_bytes(driver)
    print(f"Expanded Windows mouse driver: {len(driver)} bytes; SHA256 {hashlib.sha256(driver).hexdigest()}")

if __name__ == "__main__":
    main()
