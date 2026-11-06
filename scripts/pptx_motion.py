#!/usr/bin/env python3
"""Autoplay idle-motion layer ("living 2D") for PowerPoint decks. Standard library only.

What it does
------------
Injects a PowerPoint ``<p:timing>`` tree that starts by itself when the slide
begins (``onBegin`` + With/After Previous, so no click is needed) and loops
forever (``repeatCount="indefinite"`` = "Repeat: Until End of Slide"). Targets
are found by ``p:cNvPr@name`` so the same names that drive Morph pairing also
drive the idle motion.

Effects (all emphasis/path class, so nothing appears or disappears):
  breathe  grow/shrink with ease in/out         amplitude, amplitude_x, period_ms
  sway     rotate +-degrees about shape centre  degrees, period_ms, clockwise
  blink    short scale-Y close/open, long gap   period_ms, close_ms, closed_pct
  float    straight there-and-back motion path  dx_in, dy_in, period_ms
  orbit    closed elliptical motion path        rx_in, ry_in, period_ms, clockwise
  spin     continuous 360 degree rotation       period_ms, clockwise

Honest scope: these are rigid 2D transforms of whole shapes/groups. PowerPoint
has no mesh deformation, so this is NOT equivalent to Live2D Cubism. The XML
structure follows PowerPoint-authored templates but has NOT been played back in
Microsoft PowerPoint by this tool; see docs/PPTX-LIVE-MOTION.md.

Usage:
  python scripts/pptx_motion.py in.pptx out.pptx --spec motion.json
  python scripts/pptx_motion.py --list
Spec: {"slides": {"1": [{"target": "!!HEAD", "effect": "sway", "degrees": 2}]}}
"""
import argparse
import json
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
EMU_PER_IN = 914400
ROT_UNIT = 60000  # 1 degree in DrawingML angle units
SHAPE_TAGS = ("sp", "pic", "grpSp", "cxnSp", "graphicFrame")

DEFAULTS = {
    "breathe": {"amplitude": 1.5, "amplitude_x": None, "period_ms": 2400, "delay_ms": 0},
    "sway": {"degrees": 2.0, "period_ms": 3200, "clockwise": True, "delay_ms": 0},
    "blink": {"period_ms": 4800, "close_ms": 80, "closed_pct": 8.0, "delay_ms": 0},
    "float": {"dx_in": 0.0, "dy_in": 0.06, "period_ms": 3200, "delay_ms": 0},
    "orbit": {"rx_in": 0.08, "ry_in": 0.05, "period_ms": 6400, "clockwise": True, "delay_ms": 0},
    "spin": {"period_ms": 24000, "clockwise": True, "delay_ms": 0},
}


class MotionError(ValueError):
    """Raised for unknown targets, duplicate names or bad parameters."""


def slide_paths(names):
    found = [n for n in names if re.fullmatch(r"ppt/slides/slide[0-9]+[.]xml", n)]
    return sorted(found, key=lambda n: int(re.search(r"slide([0-9]+)", n).group(1)))


def slide_size_in(parts):
    root = ET.fromstring(parts["ppt/presentation.xml"])
    size = root.find(f"{{{P}}}sldSz")
    if size is None:
        raise MotionError("presentation.xml has no p:sldSz")
    return int(size.get("cx")) / EMU_PER_IN, int(size.get("cy")) / EMU_PER_IN


def shape_index(xml):
    """Return {name: [(id, tag, has_txbody), ...]} for every named shape."""
    root = ET.fromstring(xml.encode("utf-8"))
    parent = {c: p for p in root.iter() for c in p}
    found = {}
    for cnv in root.iter(f"{{{P}}}cNvPr"):
        holder = parent.get(parent.get(cnv))
        if holder is None:
            continue
        tag = holder.tag.rsplit("}", 1)[-1]
        if tag not in SHAPE_TAGS:
            continue
        has_text = holder.find(f"{{{P}}}txBody") is not None
        found.setdefault(cnv.get("name"), []).append((int(cnv.get("id")), tag, has_text))
    return found


def _params(effect, raw):
    if effect not in DEFAULTS:
        raise MotionError(f"unknown effect {effect!r}; choose from {sorted(DEFAULTS)}")
    unknown = set(raw) - set(DEFAULTS[effect]) - {"target", "effect"}
    if unknown:
        raise MotionError(f"{effect}: unknown parameters {sorted(unknown)}")
    merged = dict(DEFAULTS[effect])
    merged.update({k: v for k, v in raw.items() if k not in ("target", "effect")})
    for key in ("period_ms", "close_ms", "delay_ms"):
        if key in merged and (not isinstance(merged[key], (int, float)) or merged[key] < 0):
            raise MotionError(f"{effect}: {key} must be a non-negative number")
    if merged.get("period_ms", 1000) < 200:
        raise MotionError(f"{effect}: period_ms must be >= 200")
    return merged


class _Ids:
    def __init__(self, start=5):
        self.value = start

    def take(self):
        self.value += 1
        return self.value - 1


def _tgt(spid):
    return f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'


def _scale(ids, spid, dur, x, y):
    return (f'<p:animScale><p:cBhvr><p:cTn id="{ids.take()}" dur="{dur}" fill="hold"/>'
            f'{_tgt(spid)}</p:cBhvr><p:by x="{x}" y="{y}"/></p:animScale>')


def _rot(ids, spid, dur, by):
    return (f'<p:animRot by="{by}"><p:cBhvr><p:cTn id="{ids.take()}" dur="{dur}" fill="hold"/>'
            f'{_tgt(spid)}<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst>'
            "</p:cBhvr></p:animRot>")


def _motion(ids, spid, dur, path):
    return (f'<p:animMotion origin="layout" path="{path}" pathEditMode="relative" ptsTypes="">'
            f'<p:cBhvr><p:cTn id="{ids.take()}" dur="{dur}" fill="hold"/>{_tgt(spid)}'
            "<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName>"
            "</p:attrNameLst></p:cBhvr></p:animMotion>")


def _f(value):
    return f"{value:.5f}".rstrip("0").rstrip(".") or "0"


def _ellipse_path(rx, ry, clockwise):
    """Closed cubic-Bezier ellipse that starts and ends at the origin (0,0)."""
    k = 0.5522847498
    sgn = 1 if clockwise else -1
    cx, cy = 0.0, ry
    pts = [
        (cx + sgn * rx * k, cy - ry, cx + sgn * rx, cy - ry * k, cx + sgn * rx, cy),
        (cx + sgn * rx, cy + ry * k, cx + sgn * rx * k, cy + ry, cx, cy + ry),
        (cx - sgn * rx * k, cy + ry, cx - sgn * rx, cy + ry * k, cx - sgn * rx, cy),
        (cx - sgn * rx, cy - ry * k, cx - sgn * rx * k, cy - ry, cx, cy - ry),
    ]
    segments = " ".join("C " + " ".join(_f(v) for v in seg) for seg in pts)
    return f"M 0 0 {segments} Z"


def build_row(effect, spid, grp_id, node_type, ids, size_in, raw):
    """Return (row_xml, iteration_ms, params) for one effect."""
    p = _params(effect, raw)
    width_in, height_in = size_in
    delay = int(p["delay_ms"])
    row_id = ids.take()
    attrs = {"presetSubtype": "0", "fill": "hold", "grpId": str(grp_id),
             "nodeType": node_type, "repeatCount": "indefinite"}
    ease = ' accel="50000" decel="50000"'
    if effect == "breathe":
        half = int(p["period_ms"] // 2)
        ay = 100000 + round(p["amplitude"] * 1000)
        ax_pct = p["amplitude"] * 0.3 if p["amplitude_x"] is None else p["amplitude_x"]
        ax = 100000 + round(ax_pct * 1000)
        cls, preset, extra = "emph", 6, ' autoRev="1"' + ease
        body = _scale(ids, spid, half, ax, ay)
        iteration = half * 2
    elif effect == "sway":
        half = int(p["period_ms"] // 2)
        sign = 1 if p["clockwise"] else -1
        by = sign * round(2 * p["degrees"] * ROT_UNIT)
        cls, preset, extra = "emph", 8, ' autoRev="1"' + ease
        body = _rot(ids, spid, half, by)
        iteration = half * 2
    elif effect == "blink":
        period, close = int(p["period_ms"]), int(p["close_ms"])
        if period < 4 * close:
            raise MotionError("blink: period_ms must be at least 4 x close_ms")
        y = max(1000, round(p["closed_pct"] * 1000))
        pad = (f'<p:animScale><p:cBhvr><p:cTn id="{ids.take()}" dur="{period}" fill="hold"/>'
               f'{_tgt(spid)}</p:cBhvr><p:by x="100000" y="100000"/></p:animScale>')
        blink_id = ids.take()
        shut = (f'<p:animScale><p:cBhvr><p:cTn id="{blink_id}" dur="{close}" autoRev="1" fill="hold">'
                f'<p:stCondLst><p:cond delay="{period - 2 * close}"/></p:stCondLst></p:cTn>'
                f'{_tgt(spid)}</p:cBhvr><p:by x="100000" y="{y}"/></p:animScale>')
        cls, preset, extra = "emph", 6, ""
        body = pad + shut
        iteration = period
    elif effect == "float":
        half = int(p["period_ms"] // 2)
        path = f'M 0 0 L {_f(p["dx_in"] / width_in)} {_f(p["dy_in"] / height_in)} E'
        cls, preset, extra = "path", 0, ' autoRev="1"' + ease
        body = _motion(ids, spid, half, path)
        iteration = half * 2
    elif effect == "orbit":
        path = _ellipse_path(p["rx_in"] / width_in, p["ry_in"] / height_in, p["clockwise"])
        cls, preset, extra = "path", 0, ""
        body = _motion(ids, spid, int(p["period_ms"]), path)
        iteration = int(p["period_ms"])
    else:  # spin
        sign = 1 if p["clockwise"] else -1
        cls, preset, extra = "emph", 8, ""
        body = _rot(ids, spid, int(p["period_ms"]), sign * 360 * ROT_UNIT)
        iteration = int(p["period_ms"])
    head = (f'<p:cTn id="{row_id}" presetID="{preset}" presetClass="{cls}" '
            + " ".join(f'{k}="{v}"' for k, v in attrs.items()) + extra + ">")
    row = (f'<p:par>{head}<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
           f"<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>")
    return row, iteration, p


def timing_xml(rows, builds):
    bld = ""
    if builds:
        bld = "<p:bldLst>" + "".join(
            f'<p:bldP spid="{s}" grpId="{g}" animBg="1"/>' for s, g in builds) + "</p:bldLst>"
    return (
        "<p:timing><p:tnLst><p:par>"
        '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
        "<p:childTnLst><p:par>"
        '<p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
        '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
        '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
        f"<p:childTnLst>{''.join(rows)}</p:childTnLst></p:cTn></p:par>"
        "</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>"
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f"</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>{bld}</p:timing>"
    )


def _offset_rotation(xml, spid, delta):
    """Pre-rotate a shape by `delta` so a +-d sway is centred on its neutral pose."""
    start = xml.index(f'<p:cNvPr id="{spid}"')
    match = re.compile(r"<a:xfrm\b([^>]*)>").search(xml, start)
    if not match:
        raise MotionError(f"shape {spid} has no explicit a:xfrm to pre-rotate")
    between = xml[start:match.start()]
    if re.search(r"<p:(sp|pic|grpSp)>", between):
        raise MotionError(f"shape {spid} has no explicit a:xfrm to pre-rotate")
    attrs = match.group(1)
    current = re.search(r'\brot="(-?[0-9]+)"', attrs)
    new_rot = (int(current.group(1)) if current else 0) + delta
    if current:
        attrs = attrs.replace(current.group(0), f'rot="{new_rot}"')
    else:
        attrs += f' rot="{new_rot}"'
    return xml[:match.start()] + f"<a:xfrm{attrs}>" + xml[match.end():]


def _insert_timing(xml, timing):
    if "<p:timing" in xml:
        raise MotionError("slide already has p:timing; refusing to overwrite")
    for marker in ("<p:extLst", "</p:sld>"):
        idx = xml.rfind(marker)
        if idx != -1:
            return xml[:idx] + timing + xml[idx:]
    raise MotionError("slide XML has no closing p:sld")


def apply_to_slide(xml, size_in, effects, preoffset=True):
    index = shape_index(xml)
    ids = _Ids()
    rows, builds, used, report = [], [], {}, []
    for number, raw in enumerate(effects):
        name, effect = raw.get("target"), raw.get("effect")
        hits = index.get(name, [])
        if len(hits) != 1:
            raise MotionError(f"target {name!r} matched {len(hits)} shapes (need exactly 1)")
        spid, _tag, has_text = hits[0]
        grp = used.get(spid, 0)
        used[spid] = grp + 1
        node = "afterEffect" if number == 0 else "withEffect"
        row, iteration, params = build_row(effect, spid, grp, node, ids, size_in, raw)
        rows.append(row)
        if has_text and _tag == "sp":
            builds.append((spid, grp))
        if effect == "sway" and preoffset and grp == 0:
            xml = _offset_rotation(xml, spid, -round(params["degrees"] * ROT_UNIT))
        report.append({"target": name, "effect": effect, "iteration_ms": iteration,
                       "delay_ms": int(params["delay_ms"])})
    return _insert_timing(xml, timing_xml(rows, builds)), report


def apply(src, dst, spec, preoffset=True):
    """Apply a motion spec; returns {slide_number: [effect report, ...]}."""
    with ZipFile(src) as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}
    size = slide_size_in(parts)
    paths = slide_paths(parts)
    result = {}
    for key, effects in spec.get("slides", {}).items():
        number = int(key)
        if not 1 <= number <= len(paths):
            raise MotionError(f"slide {number} not in deck of {len(paths)}")
        if not effects:
            continue
        name = paths[number - 1]
        xml, report = apply_to_slide(parts[name].decode("utf-8"), size, effects, preoffset)
        ET.fromstring(xml.encode("utf-8"))
        parts[name] = xml.encode("utf-8")
        result[number] = report
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(dst, "w", compression=ZIP_DEFLATED, compresslevel=8) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", type=Path)
    ap.add_argument("output", nargs="?", type=Path)
    ap.add_argument("--spec", type=Path, help="JSON motion spec")
    ap.add_argument("--list", action="store_true", help="print effects and defaults")
    ap.add_argument("--no-preoffset", action="store_true", help="do not pre-rotate sway targets")
    args = ap.parse_args()
    if args.list:
        print(json.dumps(DEFAULTS, indent=2, ensure_ascii=False))
        return
    if not (args.input and args.output and args.spec):
        ap.error("input, output and --spec are required")
    report = apply(args.input, args.output, json.loads(args.spec.read_text("utf-8")),
                   not args.no_preoffset)
    total = sum(len(v) for v in report.values())
    print(f"{args.output} — {total} looping effects on {len(report)} slides")


if __name__ == "__main__":
    main()
