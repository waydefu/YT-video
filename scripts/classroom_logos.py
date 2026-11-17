#!/usr/bin/env python3
"""Brand marks for the classroom AI/Agent deck: fetch, verify (SHA256), tint, rasterise, write a rights manifest.

Source: the `simple-icons` npm package on jsDelivr, pinned per icon. The package's icon data is CC0 1.0, but the MARKS
THEMSELVES remain trademarks of their owners. The user decided (2026-11-17) to use the marks in a classroom deck and to
label them "教學引用" with a list; this script does not make them licensed. See docs/CLASSROOM-AI-AGENTS.md section 3.

Usage: python3 scripts/classroom_logos.py [--out build/classroom/assets]   (needs network + Node playwright with the pre-installed Chromium)
Status per mark is written to manifest.json: every entry is NOMINATIVE-CLASSROOM-USE (not GUIDELINE-PERMITTED).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

CDN = "https://cdn.jsdelivr.net/npm/simple-icons@{ver}/icons/{slug}.svg"
# key -> (slug, pinned version, SHA256 of the SVG, owner, tint colour)
MARKS = {
    "claude": ("claude", "16.38.0", "2d6fda79eb18ddccca35b799eeb3cece0dfabc22520ce3b10abd25668df9fa93", "Anthropic", "C35F3F"),
    "openai": ("openai", "13.0.0", "2b4a04ddc2395b20d168694d3850ce2050a702c4a0cdeb4d8b31b9a970481a8c", "OpenAI", "2E7D5B"),
    "gemini": ("googlegemini", "16.38.0", "a6228d8846040401e941a39ed17459785e8324dbb7b870ce84233c9b3e9863a0", "Google", "5B7FD6"),
    "kimi": ("kimi", "16.38.0", "01fb4be70032974e2c9a4f2af9688ea505ad7d996de8866cea0844c4b0581091", "Moonshot AI", "237F94"),
    "deepseek": ("deepseek", "16.38.0", "7a55a0a7391d116eba7d32807d6838478f9209f6034612941e74fbb14934e2ef", "DeepSeek", "4D6BFE"),
    "cursor": ("cursor", "16.38.0", "71572a9be192cc069ec22b48d785e61d754eeed7edb7d082d615f6d5620f70ec", "Anysphere (Cursor)", "3B6EA5"),
    "opencode": ("opencode", "16.38.0", "6f7d203200ba051cdbaa726c4de0a729cee3f1cec47953f189399d951af58c4c", "OpenCode (SST / Anomaly)", "A37A12"),
}


def fetch(slug, ver):
    url = CDN.format(ver=ver, slug=slug)
    req = urllib.request.Request(url, headers={"User-Agent": "classroom-deck-asset-fetch"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return url, r.read()


def tint(svg: bytes, color: str) -> bytes:
    text = svg.decode("utf-8")
    return re.sub(r"<svg ", f'<svg fill="#{color}" ', text, count=1).encode("utf-8")


RENDER_JS = """
const { chromium } = require('playwright');
(async () => {
  const [svg, png] = process.argv.slice(1);
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 480, height: 480 }, deviceScaleFactor: 1 });
  const fs = require('fs');
  await pg.setContent('<body style="margin:0;background:transparent"><img style="width:480px;height:480px" src="data:image/svg+xml;base64,' +
    fs.readFileSync(svg).toString('base64') + '"></body>');
  await pg.screenshot({ path: png, omitBackground: true });
  await b.close();
})();
"""


def rasterise(svg: Path, png: Path):
    """SVG -> 480x480 transparent PNG with the pre-installed Chromium (no extra downloads)."""
    subprocess.run(["node", "-e", RENDER_JS, str(svg.resolve()), str(png.resolve())], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("build/classroom/assets"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for key, (slug, ver, sha, owner, color) in MARKS.items():
        url, data = fetch(slug, ver)
        digest = hashlib.sha256(data).hexdigest()
        if sha and digest != sha:
            sys.exit(f"{key}: SHA256 mismatch ({digest}); refusing to use it")
        svg = args.out / f"logo_{key}.svg"
        svg.write_bytes(tint(data, color))
        png = args.out / f"logo_{key}.png"
        rasterise(svg, png)
        manifest[key] = {"owner": owner, "source": url, "sha256": digest, "icon_data_license": "CC0-1.0 (simple-icons)",
                         "mark_status": "NOMINATIVE-CLASSROOM-USE", "label_on_slide": "教學引用",
                         "note": "Trademark of its owner; not endorsed; replace with the vendor's brand-kit file for any public posting."}
        print(f"{key}: {digest[:12]}  {url}")
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
