#!/usr/bin/env python3
"""Download the verified CC0 Poly Haven marble bust GLB mirror, no AI mesh creation."""
import argparse
import hashlib
import struct
from pathlib import Path
from urllib.request import Request, urlopen

ASSET = "marble_bust_01"
ORIGINAL = "https://polyhaven.com/a/marble_bust_01"
DOWNLOAD = "https://files.innerscene.com/library/marble-bust-f5604fc9/154620fb9200428d8399/polyhaven-marble-bust-01.glb"
USER_AGENT = "BROKE-TRIO-Video-Production/1.0 (source: waydefu/YT-video)"
EXPECTED_SHA256 = "f09278501571c32e50edabcf9a2508427fe967c9511393ef18a6c9f360f340dd"

def fetch(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    req = Request(DOWNLOAD, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=90) as response:
        data = response.read(30_000_000)
    if len(data) < 1000 or len(data) > 30_000_000:
        raise ValueError("Asset unexpectedly small or large")
    magic, version, total = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError("Expected self-contained glTF 2.0 binary GLB")
    actual = hashlib.sha256(data).hexdigest()
    if actual != EXPECTED_SHA256:
        raise ValueError(f"Downloaded asset hash mismatch: {actual} != {EXPECTED_SHA256}")
    output.write_bytes(data)
    print("Model:", ORIGINAL)
    print("Downloaded from CC0 Poly Haven model mirrored by Innerscene:", DOWNLOAD)
    print("Bytes:", len(data))
    print("sha256:", hashlib.sha256(data).hexdigest())

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="assets/external/marble_bust_01.glb")
    fetch(p.parse_args().output)
