#!/usr/bin/env python3
"""Office-native Morph injection for PPTX. Standard library only.

Usage:
  python scripts/pptx_morph_patch.py draft.pptx final.pptx --duration 1300 --hold 4700
A slide's objects with an alt text beginning "!!" are given matching cNvPr@name.
PowerPoint itself (not LibreOffice) is required to verify the actual transition.
"""
import argparse
import hashlib
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as etree

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"

def transition(duration, hold, first=False):
    if first:
        return f'<p:transition spd="slow" advTm="{hold}" advClick="1"><p:fade/></p:transition>'
    return (
        f'<mc:AlternateContent xmlns:mc="{MC}">'
        f'<mc:Choice xmlns:p159="{P159}" Requires="p159">'
        f'<p:transition spd="slow" advTm="{hold}" advClick="1" '
        f'xmlns:p14="{P14}" p14:dur="{duration}">'
        '<p159:morph option="byObject"/></p:transition></mc:Choice>'
        f'<mc:Fallback><p:transition spd="slow" advTm="{hold}" advClick="1">'
        '<p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
    )

def apply(src: Path, dest: Path, duration: int, hold: int, dedupe: bool = True):
    with ZipFile(src) as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}
    slides = sorted(
        (s for s in parts if re.fullmatch(r"ppt/slides/slide[0-9]+[.]xml", s)),
        key=lambda s: int(re.search(r"slide([0-9]+)", s).group(1)),
    )
    if len(slides) < 2:
        raise RuntimeError("Need at least two slides")
    seen_matched = defaultdict(set)
    for i, path in enumerate(slides):
        xml = parts[path].decode("utf-8")
        if "<p:transition" in xml or "<mc:AlternateContent" in xml:
            raise RuntimeError(f"Slide already has a transition: {path}")
        def rename(m):
            tag = m.group(0)
            text = re.search(r'\bdescr="(!![^"]+)"', tag)
            if not text:
                return tag
            key = text.group(1)
            # Prevent accidental collisions within one slide.
            if key in seen_matched[i]:
                return tag
            seen_matched[i].add(key)
            return re.sub(r'\bname="[^"]*"', f'name="{key}"', tag)
        xml = re.sub(r"<p:cNvPr\b[^>]*>", rename, xml)
        xml = xml.replace("</p:sld>", transition(duration, hold, first=(i == 0)) + "</p:sld>")
        etree.fromstring(xml.encode("utf-8"))
        parts[path] = xml.encode("utf-8")
    duplicate_count = 0
    if dedupe:
        media = [x for x in parts if x.startswith("ppt/media/")]
        canonical = {}
        duplicate = {}
        for name in media:
            digest = hashlib.sha256(parts[name]).hexdigest()
            if digest not in canonical:
                canonical[digest] = name
            else:
                duplicate[name] = canonical[digest]
        for path in [x for x in parts if x.startswith("ppt/slides/_rels/") and x.endswith(".rels")]:
            xml = parts[path].decode("utf-8")
            for old, new in duplicate.items():
                xml = xml.replace("../media/" + old.split("/")[-1], "../media/" + new.split("/")[-1])
            parts[path] = xml.encode("utf-8")
        for old in duplicate:
            del parts[old]
        duplicate_count = len(duplicate)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(dest, "w", compression=ZIP_DEFLATED, compresslevel=8) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)
    return len(slides), duplicate_count

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--duration", type=int, default=1300, help="Morph transition milliseconds")
    ap.add_argument("--hold", type=int, default=4700, help="Auto-advance milliseconds")
    ap.add_argument("--no-dedupe", action="store_true")
    args = ap.parse_args()
    if args.duration < 100 or args.hold < 100:
        ap.error("duration and hold must be >= 100 ms")
    n, reduced = apply(args.input, args.output, args.duration, args.hold, not args.no_dedupe)
    print(f"{args.output} — {n-1} Morph transitions, {reduced} duplicate media removed")
