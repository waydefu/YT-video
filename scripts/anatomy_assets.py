#!/usr/bin/env python3
"""Fetch and prepare OFFICIAL Anatomy source material for the explainer deck. Nothing is committed.

Source: https://github.com/wheresryan22/anatomy at a pinned commit. MIT License, Copyright (c) 2026 Ryan.
Every input is checked against a SHA256 pin; a mismatch stops the run (no silent substitution).
Outputs (build/anatomy/assets by default):
  fig_*.png        README screenshots converted from WebP (raptor firing/apart, ripple tank, turning dial, dial indicator)
  cap_*.png        the framed figure card of upstream's own example pages, captured at 3x (needs node + playwright)
  poster_*.png     figure regions cropped from upstream's vector A4 poster PDFs, rasterised at 300 dpi (needs pdftoppm)
  sheet_*.png      full A4 pages of upstream's printable sheets
  LICENSE_ANATOMY.txt, manifest.json (provenance: pinned commit, input and output SHA256)
The MIT licence text must travel with every deck built from these files (the builder embeds it in speaker notes).
Requires: Pillow, poppler-utils (pdftoppm); for cap_* also node + playwright.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

REV = "1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
BASE = f"https://raw.githubusercontent.com/wheresryan22/anatomy/{REV}/"
PINS = {
    "LICENSE": "87c078ab9d90a3044f359e6b563d4e6afea7aa060897cf4f21618687b3856796",
    ".github/assets/raptor-engine-firing.webp": "c42a9eb6aacb506f7baf0fd91d4fbb04649999e9615f9847585daff595a62d55",
    ".github/assets/raptor-engine-apart.webp": "db1bee237411d26d97e2e88f60949a75f9f160a0139d03382f46a2e2d6801050",
    ".github/assets/ripple-tank.webp": "1312c34386e18792d44c3d3e1939d22e14bc48ce67e4f48eb29c543e741f79c2",
    ".github/assets/turning-dial.webp": "f77d1a97efc718d875ca3abfa0c0a0b64049797006e188f804383d0173281739",
    ".github/assets/dial-indicator.webp": "a1f0550e0938a3c76316fddd272792d5f50609cceca7217606b187868d7f4fe7",
    "examples/raptor-engine/raptor-engine-poster-a4.pdf": "a3f3c40c5b9f916a0d457909d853f83e1aef61f2858f09632430a9065fe25756",
    "examples/raptor-engine/raptor-engine-drawing-a4.pdf": "3a4de2fc7dd52dc9149dc9038996ce2da8b3dcce250be8bae42faeebb4cca698",
    "examples/raptor-engine/raptor-engine-detailed-a4.pdf": "8ea62e8fc0566dc54c54f3e58112cb7bf4d2a5ebb3666782d85bc4e8a3ef179e",
    "examples/arcade-cabinet/arcade-cabinet-poster-a4.pdf": "2d45bd3bdf863bd908d19cd2c1304bdbceed117a7a817098af4e751d88f376e8",
    "examples/desk-computer/desk-computer-light.html": "ce63c5bed81b76491a82f5e94d22e5f64744c87bc448fdad8726ae0c6ecd0b59",
    "examples/arcade-cabinet/arcade-cabinet-light.html": "f54197aa4c3b7e5b00469266f38f79bc0d907f52bf572838eea2acaac89ddbc7",
    "examples/dial-indicator/dial-indicator-light.html": "bc1810e340d916a25cc1749589b44096b7e41970f22fa7fce569bbefc0613093",
    "examples/ripple-tank/ripple-tank-light.html": "15b5b7a1e738fb5e435e9c1dccea874f6d292962fb31943fdd4466c15b351b59",
    "examples/turning-dial/turning-dial-light.html": "7873a4873e4f1a204ca59691765915f155f44095c2c290730aa2b915b4c88c9e",
    "examples/raptor-engine/raptor-engine-light.html": "48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537",
}
WEBP = {"fig_raptor_firing": "raptor-engine-firing", "fig_raptor_apart": "raptor-engine-apart",
        "fig_ripple_tank": "ripple-tank", "fig_turning_dial": "turning-dial", "fig_dial_indicator": "dial-indicator"}
CAPTURES = {"cap_desk_computer": "desk-computer/desk-computer-light", "cap_arcade_cabinet": "arcade-cabinet/arcade-cabinet-light",
            "cap_dial_indicator": "dial-indicator/dial-indicator-light", "cap_ripple_tank": "ripple-tank/ripple-tank-light",
            "cap_turning_dial": "turning-dial/turning-dial-light", "cap_raptor_engine": "raptor-engine/raptor-engine-light"}
# search boxes as fractions of the A4 page (left, top, right, bottom): the isometric figure with its callouts sits in
# this band, clear of the title/statistics column on the left and of the parts list below. The figure is then
# auto-cropped to its own ink so no part is ever cut off.
POSTER_CROPS = {"poster_raptor": ("examples/raptor-engine/raptor-engine-poster-a4.pdf", (0.36, 0.13, 0.95, 0.76)),
                "poster_arcade": ("examples/arcade-cabinet/arcade-cabinet-poster-a4.pdf", (0.33, 0.13, 0.999, 0.76))}
SHEETS = {"sheet_poster": ("examples/raptor-engine/raptor-engine-poster-a4.pdf", 1),
          "sheet_drawing": ("examples/raptor-engine/raptor-engine-drawing-a4.pdf", 1),
          "sheet_detailed": ("examples/raptor-engine/raptor-engine-detailed-a4.pdf", 1)}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(rel, raw, local_src):
    dest = raw / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        if local_src:
            shutil.copyfile(Path(local_src) / rel, dest)
        else:
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(BASE + rel, timeout=90) as r:
                        dest.write_bytes(r.read())
                    break
                except Exception as exc:  # noqa: BLE001 - retry any transport error
                    if attempt == 3:
                        raise RuntimeError(f"download failed for {rel}: {exc}") from exc
                    time.sleep(2 ** (attempt + 1))
    got = sha256(dest)
    if got != PINS[rel]:
        raise RuntimeError(f"SHA256 mismatch for {rel}: expected {PINS[rel]}, got {got} (refusing to substitute)")
    return dest


def pdf_page(pdf, page, dpi, out_png):
    stem = out_png.with_suffix("")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf), str(stem)],
                   check=True)
    return Image.open(out_png).convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("build/anatomy/assets"))
    ap.add_argument("--local-src", type=Path, help="use files from a local checkout of the pinned commit (still SHA-checked)")
    ap.add_argument("--no-capture", action="store_true", help="skip cap_* (no node/playwright available)")
    args = ap.parse_args()
    raw = args.out / "raw"
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    files = {rel: fetch(rel, raw, args.local_src) for rel in PINS}
    shutil.copyfile(files["LICENSE"], out / "LICENSE_ANATOMY.txt")
    text = (out / "LICENSE_ANATOMY.txt").read_text(encoding="utf-8")
    if "MIT License" not in text or "Copyright (c) 2026 Ryan" not in text:
        raise RuntimeError("upstream LICENSE is not the expected MIT text")
    for name, key in WEBP.items():
        Image.open(files[f".github/assets/{key}.webp"]).convert("RGB").save(out / f"{name}.png", optimize=True)
    for name, (rel, box) in POSTER_CROPS.items():
        page = pdf_page(files[rel], 1, 300, out / f"{name}_page.png")
        w, h = page.size
        region = page.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
        ink = region.convert("L").point(lambda v: 255 if v < 245 else 0).getbbox()
        if ink is None:
            raise RuntimeError(f"{name}: no figure found in the search box")
        pad = int(0.012 * w)
        l, t, r, b = ink
        region.crop((max(0, l - pad), max(0, t - pad), min(region.width, r + pad), min(region.height, b + pad))).save(
            out / f"{name}_figure.png", optimize=True)
    for name, (rel, number) in SHEETS.items():
        pdf_page(files[rel], number, 150, out / f"{name}.png")
    if not args.no_capture:
        pairs = []
        for name, stem in CAPTURES.items():
            pairs += [str(files[f"examples/{stem}.html"]), str(out / f"{name}.png")]
        subprocess.run(["node", str(Path(__file__).with_name("anatomy_capture.mjs")), "3", *pairs], check=True)
    manifest = {"source": "https://github.com/wheresryan22/anatomy", "commit": REV,
                "license": "MIT, Copyright (c) 2026 Ryan",
                "inputs": {rel: PINS[rel] for rel in PINS},
                "outputs": {p.name: sha256(p) for p in sorted(out.glob("*.png")) if not p.name.endswith("_page.png")}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(manifest['outputs'])} official-derived images in {out} (pinned {REV[:10]}, SHA-verified inputs)")


if __name__ == "__main__":
    sys.exit(main())
