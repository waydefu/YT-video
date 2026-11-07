#!/usr/bin/env python3
"""Fetch the vendor brand files that have a recorded rights status for this deck (nothing else).

Status per asset is in docs/ASSET-RIGHTS.md (OpenCode: GUIDELINE-PERMITTED; Cursor: NOMINATIVE-USE-ASSESSMENT).
Files are downloaded from the vendor's own official download at build time, SHA256-checked against the pins below
(mismatch = stop, never substitute), and written to build/ (gitignored, not committed). The deck builder uses a mark
only if present and matching its pin. Nothing is taken from third-party icon sets or screenshots.
Usage: python scripts/brand_assets.py [--out build/ai-subscriptions/brand]
"""
import argparse
import hashlib
import io
import json
import ssl
import sys
import urllib.request
import zipfile
from pathlib import Path

ASSETS = {
    "opencode-wordmark-light.png": {
        "vendor": "OpenCode",
        "url": "https://opencode.ai/brand/files/opencode-wordmark-light.png",
        "sha256": "2173071b9e2644a37e64b7e773889b590691308e737114ef8124f6faf762facb",
        "terms_url": "https://opencode.ai/brand",
        "accessed": "2026-11-07",
        "rules": "Light version on light backgrounds; no recolor/stretch/shadow/glow; no other words beside it; "
                 "clear space >= 2 strokes; min 117x21 px; do not imply endorsement; trademark of Anomaly.",
    },
    "cursor-lockup-horizontal-2d-light.png": {
        "vendor": "Cursor",
        "url": "https://ptht05hbb1ssoooe.public.blob.vercel-storage.com/assets/brand/cursor-brand-assets.zip",
        "zip_sha256": "97488a7751914e60f9ff532bc33810cdeaebdddc017548abe6ca2bc29bbc3928",
        "zip_member": "General Logos/Lockup Horizontal/PNG/LOCKUP_HORIZONTAL_2D_LIGHT.png",
        "sha256": "5b3ea43ff38738235f73b452a40030a4343e09c9f4428e890b9484da4ae9940a",
        "terms_url": "https://cursor.com/brand",
        "accessed": "2026-11-07",
        "rules": "Brand page offers the asset pack to 'represent Cursor consistently and accurately'; it states no third-party "
                 "licence terms. Refer to the product as 'Cursor' (not 'Cursor AI'). Used unaltered, dark-ink (LIGHT) "
                 "variant on a light background, never as the deck's own or a partner/sponsor mark.",
    },
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(path, expected):
    """True only if the file exists and matches the pinned SHA256."""
    p = Path(path)
    return p.is_file() and sha256(p) == expected


def fetch(out):
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, a in ASSETS.items():
        dest = out / name
        if not verify(dest, a["sha256"]):
            req = urllib.request.Request(a["url"], headers={"User-Agent": "yt-video-brand-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
                data = r.read()
            if "zip_member" in a:
                zgot = hashlib.sha256(data).hexdigest()
                if zgot != a["zip_sha256"]:
                    sys.exit(f"STOP: asset pack SHA256 {zgot} != pinned {a['zip_sha256']} (vendor changed it; re-review the terms)")
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    data = z.read(a["zip_member"])
            got = hashlib.sha256(data).hexdigest()
            if got != a["sha256"]:
                sys.exit(f"STOP: {name} SHA256 {got} != pinned {a['sha256']} (vendor changed the file; re-review the terms)")
            dest.write_bytes(data)
        manifest[name] = {k: v for k, v in a.items()}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("build/ai-subscriptions/brand"))
    args = ap.parse_args()
    for name in fetch(args.out):
        print("ok", args.out / name)


if __name__ == "__main__":
    main()
