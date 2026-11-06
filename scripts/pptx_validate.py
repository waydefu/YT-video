#!/usr/bin/env python3
"""Structural (layer A) validator for Morph + idle-motion PPTX decks. Stdlib only.

It proves XML structure and authoring contracts. It does NOT prove that
Microsoft PowerPoint plays the deck smoothly (layer C) or that it looks good
(layer B). Exit code 1 on any FAIL; WARN never fails unless --strict.

  python scripts/pptx_validate.py deck.pptx [--min-loops 3] [--hold-ms 4800] [--json]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"
SHAPES = {"sp", "pic", "grpSp", "cxnSp", "graphicFrame"}
ORDER = ["cSld", "clrMapOvr", "transition", "AlternateContent", "timing", "extLst"]


def q(ns, name):
    return f"{{{ns}}}{name}"


def local(el):
    return el.tag.rsplit("}", 1)[-1]


def iteration_ms(row):
    """Length of one loop iteration of an effect row (ms), or None."""
    longest = 0
    for cbhvr in row.iter(q(P, "cTn")):
        if cbhvr is row:
            continue
        dur = cbhvr.get("dur")
        if not dur or dur == "indefinite":
            continue
        delay = 0
        cond = cbhvr.find(f"{q(P, 'stCondLst')}/{q(P, 'cond')}")
        if cond is not None and cond.get("delay", "0").isdigit():
            delay = int(cond.get("delay"))
        span = int(dur) * (2 if cbhvr.get("autoRev") == "1" else 1)
        longest = max(longest, delay + span)
    if row.get("autoRev") == "1":
        longest = max(
            (int(c.get("dur")) for c in row.iter(q(P, "cTn"))
             if c is not row and (c.get("dur") or "").isdigit()), default=0) * 2
    return longest or None


def check_slide(name, xml, number, total, args, report):
    fails, warns = report["fails"], report["warns"]
    root = ET.fromstring(xml)
    kids = [local(c) for c in root]
    positions = [ORDER.index(k) for k in kids if k in ORDER]
    if positions != sorted(positions):
        fails.append(f"{name}: child order {kids} violates cSld, clrMapOvr, transition, timing, extLst")
    # object names
    names = Counter()
    ids = Counter()
    for cnv in root.iter(q(P, "cNvPr")):
        names[cnv.get("name")] += 1
        ids[cnv.get("id")] += 1
    for dup in [k for k, v in ids.items() if v > 1]:
        fails.append(f"{name}: duplicate shape id {dup}")
    bang = {k for k in names if k and k.startswith("!!")}
    for k in sorted(bang):
        if names[k] > 1:
            fails.append(f"{name}: duplicate Morph name {k} (matching becomes ambiguous)")
    report["bang"][number] = bang
    # transition
    has_morph = root.find(f".//{q(P159, 'morph')}") is not None
    if number > 1 and not has_morph:
        fails.append(f"{name}: no p159:morph transition")
    if number > 1 and has_morph:
        fb = root.find(f".//{q(MC, 'Fallback')}")
        if fb is None:
            fails.append(f"{name}: Morph has no mc:Fallback fade")
    report["morph"] += 1 if has_morph else 0
    # timing
    timing = root.find(q(P, "timing"))
    loops = 0
    iterations = []
    if timing is not None:
        cids = Counter(c.get("id") for c in timing.iter(q(P, "cTn")))
        for dup in [k for k, v in cids.items() if v > 1]:
            fails.append(f"{name}: duplicate cTn id {dup}")
        shape_ids = set(ids)
        for tgt in timing.iter(q(P, "spTgt")):
            if tgt.get("spid") not in shape_ids:
                fails.append(f"{name}: spTgt {tgt.get('spid')} references a missing shape")
        roots = [c for c in timing.iter(q(P, "cTn")) if c.get("nodeType") == "tmRoot"]
        if len(roots) != 1:
            fails.append(f"{name}: expected exactly one tmRoot, found {len(roots)}")
        auto = any(c.get("evt") == "onBegin" for c in timing.iter(q(P, "cond")))
        for row in timing.iter(q(P, "cTn")):
            if row.get("presetClass") in ("emph", "path"):
                if row.get("repeatCount") == "indefinite":
                    loops += 1
                    it = iteration_ms(row)
                    spin = any(abs(int(r.get("by", "0"))) == 21600000 for r in row.iter(q(P, "animRot")))
                    if spin and it and args.hold_ms and args.spin_symmetry_deg:
                        turned = 360.0 * args.hold_ms / it
                        if abs(turned / args.spin_symmetry_deg - round(turned / args.spin_symmetry_deg)) < 1e-6:
                            continue  # rotationally symmetric art looks identical at every cut
                    if it:
                        iterations.append(it)
                else:
                    warns.append(f"{name}: effect {row.get('id')} does not loop (one-shot)")
        if loops and not auto:
            fails.append(f"{name}: loops exist but nothing auto-starts (no onBegin) — would need a click")
        for bld in timing.iter(q(P, "bldP")):
            if bld.get("spid") not in shape_ids:
                fails.append(f"{name}: bldP spid {bld.get('spid')} missing")
    report["loops"][number] = loops
    if loops < args.min_loops:
        report["dead"].append(number)
        warns.append(f"{name}: only {loops} looping effects (< {args.min_loops}) — risks a static, non-'living' slide")
    if args.hold_ms and iterations:
        off = sorted({it for it in iterations if args.hold_ms % it})
        if off:
            warns.append(f"{name}: loop periods {off} ms do not divide hold {args.hold_ms} ms — "
                         "poses will be mid-cycle when the next Morph starts (possible visual pop)")
    # readability: tiny text is unreadable on phones / recordings
    for run in root.iter(q(A, "r")):
        rpr, txt = run.find(q(A, "rPr")), run.find(q(A, "t"))
        if rpr is not None and txt is not None and (txt.text or "").strip() and (rpr.get("sz") or "").isdigit():
            if int(rpr.get("sz")) < args.min_font * 100:
                warns.append(f"{name}: '{txt.text.strip()[:20]}' is {int(rpr.get('sz')) / 100:g} pt (< {args.min_font} pt)")
    # text safe area
    size = report["size"]
    for sp in root.iter(q(P, "sp")):
        if sp.find(q(P, "txBody")) is None:
            continue
        text = "".join(t.text or "" for t in sp.iter(q(A, "t"))).strip()
        xfrm = sp.find(f".//{q(A, 'xfrm')}")
        if not text or xfrm is None:
            continue
        off, ext = xfrm.find(q(A, "off")), xfrm.find(q(A, "ext"))
        x, y = int(off.get("x")), int(off.get("y"))
        w, h = int(ext.get("cx")), int(ext.get("cy"))
        mx, my = args.edge * size[0], args.edge * size[1]
        if x >= size[0] or y >= size[1] or x + w <= 0 or y + h <= 0:
            continue  # fully off-canvas world object (e.g. a sign waiting for a later camera shot)
        if x < mx or y < my or x + w > size[0] - mx or y + h > size[1] - my:
            report["safe"].append(f"slide {number}: '{text[:24]}' outside {args.edge:.0%} edge-safe area")


def validate(path, args):
    report = {"fails": [], "warns": [], "bang": {}, "loops": {}, "dead": [], "safe": [],
              "morph": 0, "size": (0, 0)}
    try:
        zf = ZipFile(path)
    except (BadZipFile, FileNotFoundError) as exc:
        report["fails"].append(f"cannot open package: {exc}")
        return report
    with zf:
        if zf.testzip() is not None:
            report["fails"].append("corrupt ZIP member")
        names = zf.namelist()
        pres = ET.fromstring(zf.read("ppt/presentation.xml"))
        sz = pres.find(q(P, "sldSz"))
        report["size"] = (int(sz.get("cx")), int(sz.get("cy")))
        if abs(report["size"][0] / report["size"][1] - 16 / 9) > 0.01:
            report["warns"].append(f"slide size {report['size']} is not 16:9")
        slides = sorted((n for n in names if re.fullmatch(r"ppt/slides/slide[0-9]+[.]xml", n)),
                        key=lambda n: int(re.search(r"([0-9]+)", n.split("/")[-1]).group(1)))
        for i, name in enumerate(slides, 1):
            check_slide(name, zf.read(name), i, len(slides), args, report)
    report["slides"] = len(slides)
    for i in range(2, len(slides) + 1):
        shared = report["bang"].get(i, set()) & report["bang"].get(i - 1, set())
        if len(shared) < 2:
            report["fails"].append(f"slides {i-1}->{i}: only {len(shared)} shared !! objects; Morph needs anchors")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path)
    ap.add_argument("--min-loops", type=int, default=3)
    ap.add_argument("--hold-ms", type=int, default=0)
    ap.add_argument("--spin-symmetry-deg", type=float, default=0,
                    help="pattern repeat angle of spinning art (e.g. 22.5 for 16 alternating rays)")
    ap.add_argument("--min-font", type=float, default=14, help="warn below this pt size")
    ap.add_argument("--edge", type=float, default=0.05, help="text edge-safe margin (fraction)")
    ap.add_argument("--strict", action="store_true", help="treat WARN and safe-area as FAIL")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = validate(args.deck, args)
    out = {k: v for k, v in rep.items() if k != "bang"}
    out["bang"] = {k: sorted(v) for k, v in rep["bang"].items()}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=list))
    else:
        print(f"{args.deck}: {rep.get('slides', 0)} slides, {rep['morph']} Morph transitions, "
              f"loops per slide {rep['loops']}")
        for tag, key in (("FAIL", "fails"), ("WARN", "warns"), ("SAFE", "safe")):
            for line in rep[key]:
                print(f"{tag}: {line}")
        print("RESULT:", "FAIL" if rep["fails"] else "PASS (layer A only; PowerPoint playback NOT verified)")
    bad = bool(rep["fails"]) or (args.strict and (rep["warns"] or rep["safe"]))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
