#!/usr/bin/env python3
"""G2 minimum proof: a layered, original-vector "living 2D" PowerPoint deck.

Pipeline (all native, editable PPTX; no video, no external assets):
  1. python-pptx draws one continuous world (sunburst, parallax hills, particles,
     a layered character rig) and re-poses it as 3 camera shots (wide, push-in,
     pan). Cross-slide `!!` names let PowerPoint Morph move the camera.
  2. scripts/pptx_morph_patch.py adds Office-native Morph (+ fade fallback).
  3. scripts/pptx_motion.py adds autoplay looping idle motion: breathing, blink,
     head/hair sway, floating sign, orbiting particles, rotating sunburst.
  4. scripts/pptx_validate.py checks structure (layer A only).

STATUS: SPIKE. Layer A/B only. Native PowerPoint playback (layer C) is NOT RUN.
Everything drawn here is original procedural geometry; no third-party art.
Requires: python-pptx
"""
import argparse
import json
import math
import random
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pptx_morph_patch  # noqa: E402
import pptx_motion  # noqa: E402

EMU = 914400
W, H = 13.333333, 7.5
FONT = "Noto Sans CJK TC"
C = dict(bg="151A33", ray="1C2350", far="262F63", mid="313D7A", near="1B2147",
         skin="FFD9B8", hair="3B2A6B", hair2="5B45A0", cloth="FF6F91", cream="FFF1DC",
         iris="6A4FB0", ink="241B3A", mint="7AE0C3", gold="FFB86B", blush="FF8FA3")
SHOTS = [  # (camera x, camera y, zoom, caption, label)
    (4.6, 3.6, 1.00, "01 · 全景：背景與角色同時在動", "WIDE"),
    (4.6, 2.75, 2.70, "02 · 特寫：眨眼、髮絲、呼吸", "PUSH-IN"),
    (9.6, 3.3, 1.15, "03 · 平移：多層視差與漂浮", "PAN"),
]
CAM0 = SHOTS[0][:3]
HOLD_MS, MORPH_MS = 4800, 1400


class Camera:
    def __init__(self, shot):
        self.cx, self.cy, self.z = shot[:3]

    def pt(self, x, y, depth=1.0):
        z = 1 + (self.z - 1) * depth
        cx = CAM0[0] + (self.cx - CAM0[0]) * depth
        cy = CAM0[1] + (self.cy - CAM0[1]) * depth
        return W / 2 + (x - cx) * z, H / 2 + (y - cy) * z

    def k(self, depth=1.0):
        return 1 + (self.z - 1) * depth


def rgb(h):
    return RGBColor.from_string(h)


def style(shp, fill, alpha=None, line=None, width=0):
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            clr = shp._element.spPr.find(qn("a:solidFill"))[0]
            etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(width or 1)
    else:
        shp.line.fill.background()


def catmull(points, n=8, closed=True):
    out, m = [], len(points)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0, p1, p2, p3 = (points[(i + j) % m] if closed else points[min(max(i + j, 0), m - 1)]
                          for j in (-1, 0, 1, 2))
        for s in range(n):
            t = s / n
            out.append(tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t
                                    + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t * t
                                    + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t ** 3)
                             for a in (0, 1)))
    return out


class Scene:
    def __init__(self, slide, cam):
        self.sl, self.cam = slide, cam

    def poly(self, shapes, name, world_pts, fill, depth=1.0, alpha=None, smooth=0):
        pts = catmull(world_pts, smooth) if smooth else world_pts
        e = [(int(x * EMU), int(y * EMU)) for x, y in (self.cam.pt(x, y, depth) for x, y in pts)]
        fb = shapes.build_freeform(e[0][0], e[0][1], scale=1.0)
        fb.add_line_segments(e[1:], close=True)
        shp = fb.convert_to_shape()
        shp.name = name
        style(shp, fill, alpha)
        return shp

    def oval(self, shapes, name, cx, cy, w, h, fill, depth=1.0, alpha=None, kind=MSO_SHAPE.OVAL):
        x, y = self.cam.pt(cx, cy, depth)
        k = self.cam.k(depth)
        shp = shapes.add_shape(kind, Emu(int((x - w * k / 2) * EMU)), Emu(int((y - h * k / 2) * EMU)),
                               Emu(int(w * k * EMU)), Emu(int(h * k * EMU)))
        shp.name = name
        style(shp, fill, alpha)
        return shp

    def invisible(self, shapes, name, cx, cy, w, h):
        return self.oval(shapes, name, cx, cy, w, h, None, kind=MSO_SHAPE.RECTANGLE)

    def group(self, name):
        g = self.sl.shapes.add_group_shape()
        g.name = name
        return g

    def text(self, shapes, name, text, x, y, w, h, pt, color, depth=1.0, bold=False, align=PP_ALIGN.LEFT):
        px, py = self.cam.pt(x, y, depth)
        k = self.cam.k(depth)
        box = shapes.add_textbox(Emu(int(px * EMU)), Emu(int(py * EMU)), Emu(int(w * k * EMU)), Emu(int(h * k * EMU)))
        box.name = name
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        para = tf.paragraphs[0]
        para.alignment = align
        run = para.add_run()
        run.text = text
        run.font.name, run.font.size, run.font.bold = FONT, Pt(pt * k), bold
        run.font.color.rgb = rgb(color)
        return box


def ridge(base, amp, phase, x0=-2.6, x1=14.6, step=0.5, bottom=9.5):
    pts = [(x0, bottom)]
    x = x0
    while x <= x1 + 1e-6:
        pts.append((x, base + amp * math.sin(x * 0.55 + phase) + amp * 0.5 * math.sin(x * 1.3 + phase * 2)))
        x += step
    pts.append((x1, bottom))
    return pts


def build_slide(prs, idx, shot):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = rgb(C["bg"])
    s = Scene(sl, Camera(shot))
    sh = sl.shapes
    s.poly(sh, "!!BG", [(-2.8, -2.5), (14.8, -2.5), (14.8, 9.6), (-2.8, 9.6)], C["bg"], depth=0.15)
    # sunburst: 16 symmetric rays; spin period (19200 ms) = quarter turn per 4800 ms hold,
    # and 90 deg is 4 x the 22.5 deg pattern period, so the pattern is identical at each cut.
    rays = s.group("!!RAYS")
    for j in range(16):
        a0, a1 = math.radians(j * 22.5), math.radians(j * 22.5 + 11.25)
        s.poly(rays.shapes, f"RAY_{j}", [(4.6, 3.0), (4.6 + 8.2 * math.cos(a0), 3.0 + 8.2 * math.sin(a0)),
                                         (4.6 + 8.2 * math.cos(a1), 3.0 + 8.2 * math.sin(a1))], C["ray"], depth=0.35)
    rnd = random.Random(7)
    for j in range(18):
        s.oval(sh, f"!!P{j:02d}", rnd.uniform(-1.5, 13.5), rnd.uniform(0.2, 5.4), (r := rnd.uniform(.05, .13)), r,
               rnd.choice([C["cream"], C["mint"], C["blush"], C["gold"]]), depth=0.7, alpha=0.9)
    s.poly(sh, "!!HILL_FAR", ridge(4.7, .35, 0.4), C["far"], depth=0.4)
    s.poly(sh, "!!HILL_MID", ridge(5.3, .4, 2.0), C["mid"], depth=0.65)
    # floating sign (native, editable text)
    sign = s.group("!!SIGN")
    s.poly(sign.shapes, "SIGN_PANEL", [(12.0, 1.6), (14.7, 1.6), (14.7, 3.5), (12.0, 3.5)], C["cream"], smooth=6)
    s.text(sign.shapes, "SIGN_TXT1", "按下播放", 12.25, 1.85, 2.2, 0.75, 30, C["ink"], bold=True)
    s.text(sign.shapes, "SIGN_TXT2", "畫面就會自己動", 12.25, 2.65, 2.3, 0.5, 16, C["iris"])
    # ---- character rig (original geometry) ----
    body = s.group("!!BODY")
    s.poly(body.shapes, "TORSO", [(3.0, 6.6), (3.15, 5.0), (3.7, 4.35), (4.6, 4.2), (5.5, 4.35), (6.05, 5.0), (6.2, 6.6)],
           C["cloth"], smooth=6)
    s.poly(body.shapes, "COLLAR", [(3.95, 4.25), (4.6, 5.05), (5.25, 4.25), (4.95, 4.15), (4.6, 4.45), (4.25, 4.15)], C["cream"])
    s.poly(sh, "NECK", [(4.38, 3.5), (4.82, 3.5), (4.86, 4.4), (4.34, 4.4)], "F2C5A0")
    head = s.group("!!HEAD")
    hs = head.shapes
    s.poly(hs, "HAIR_BACK", [(3.35, 2.6), (3.5, 1.7), (4.1, 1.2), (4.6, 1.12), (5.1, 1.2), (5.7, 1.7), (5.85, 2.6),
                            (5.8, 3.7), (5.35, 3.95), (3.85, 3.95), (3.4, 3.7)], C["hair"], smooth=6)
    s.oval(hs, "EAR_L", 3.58, 2.75, .22, .34, C["skin"])
    s.oval(hs, "EAR_R", 5.62, 2.75, .22, .34, C["skin"])
    s.oval(hs, "FACE", 4.6, 2.65, 1.95, 2.2, C["skin"])
    s.oval(hs, "CHEEK_L", 4.0, 3.12, .36, .2, C["blush"], alpha=.5)
    s.oval(hs, "CHEEK_R", 5.2, 3.12, .36, .2, C["blush"], alpha=.5)
    for tag, ex in (("L", 4.17), ("R", 5.03)):
        eye = s.group(f"!!EYE_{tag}")
        s.oval(eye.shapes, f"WHITE_{tag}", ex, 2.78, .36, .44, "FFFFFF")
        s.oval(eye.shapes, f"IRIS_{tag}", ex, 2.82, .25, .36, C["iris"])
        s.oval(eye.shapes, f"PUPIL_{tag}", ex, 2.84, .13, .2, C["ink"])
        s.oval(eye.shapes, f"GLINT_{tag}", ex + .05, 2.72, .07, .07, "FFFFFF")
        s.oval(eye.shapes, f"LASH_{tag}", ex, 2.57, .44, .05, C["ink"], kind=MSO_SHAPE.ROUNDED_RECTANGLE)
        head.shapes._spTree.append(eye._element)  # nest the eye group inside the head group
    s.poly(hs, "MOUTH", [(4.42, 3.27), (4.6, 3.34), (4.78, 3.27), (4.6, 3.46)], "D9506A", smooth=5)
    s.poly(hs, "BANGS", [(3.45, 2.5), (3.6, 1.65), (4.2, 1.18), (4.6, 1.12), (5.0, 1.18), (5.6, 1.65), (5.75, 2.5),
                        (5.45, 2.15), (5.15, 2.4), (4.85, 2.0), (4.6, 2.38), (4.3, 2.0), (4.0, 2.4), (3.75, 2.15)],
           C["hair"], smooth=5)
    s.poly(hs, "HAIR_SHINE", [(4.0, 1.5), (4.55, 1.3), (5.05, 1.38), (4.55, 1.5)], C["hair2"], smooth=5)
    s.invisible(hs, "PIVOT_WEIGHT", 4.6, 5.6, 2.5, 3.9)  # symmetric about the neck so sway pivots there
    for tag, hx, sign_ in (("L", 3.5, -1), ("R", 5.7, 1)):
        lock = s.group(f"!!HAIR_{tag}")
        s.poly(lock.shapes, f"LOCK_{tag}", [(hx - .16, 2.3), (hx + .16, 2.3), (hx + .2 * sign_ + .12, 3.4),
                                          (hx + .1 * sign_, 4.15), (hx - .1 * sign_ - .1, 3.4)], C["hair"], smooth=6)
        s.invisible(lock.shapes, f"LOCK_{tag}_W", hx, 1.5, .5, 1.6)  # root-centred pivot
    s.poly(sh, "!!HILL_NEAR", ridge(6.2, .25, 3.3), C["near"], depth=1.0)
    # ---- HUD (identical `!!` names stay fixed across Morph; captions are per-slide) ----
    sl_w = Scene(sl, Camera((W / 2, H / 2, 1.0, "", "")))
    sl_w.text(sh, "!!HUD_TITLE", "會呼吸的簡報", 0.85, 0.5, 6.0, 0.55, 24, C["cream"], bold=True)
    sl_w.text(sh, "!!HUD_SUB", "LIVING DECK  ·  NATIVE MORPH + AUTOPLAY LOOPS  ·  SPIKE", 0.85, 1.05, 8.0, 0.3, 11, C["gold"])
    sl_w.text(sh, f"CAPTION_{idx + 1}", shot[3], 0.85, 6.5, 8.0, 0.35, 15, C["cream"])
    sl_w.text(sh, f"LABEL_{idx + 1}", shot[4], 10.6, 6.5, 1.9, 0.35, 12, C["gold"], align=PP_ALIGN.RIGHT)
    for j in range(3):
        bar = sh.add_shape(MSO_SHAPE.RECTANGLE, Emu(int((0.85 + j * 0.7) * EMU)), Emu(int(6.4 * EMU)),
                           Emu(int(0.56 * EMU)), Emu(int(0.03 * EMU)))
        bar.name = f"!!PROGRESS_{j}"
        style(bar, C["gold"] if j == idx else "5A648F")
    sl.notes_slide.notes_text_frame.text = (
        "SPIKE：原創向量素材，無第三方圖像。原生 Morph + 自動循環動態層；"
        "PowerPoint 實播狀態：NOT RUN。此動畫為剛體 2D 變換，不等同 Live2D 網格變形。")
    return sl


def motion_spec():
    """Per-slide idle loops. Amplitudes in inches scale with the camera zoom."""
    slides = {}
    for i, shot in enumerate(SHOTS):
        k = Camera(shot).k(1.0)
        rows = [
            {"target": "!!RAYS", "effect": "spin", "period_ms": 19200},
            {"target": "!!BODY", "effect": "breathe", "amplitude": 1.2, "period_ms": 2400},
            {"target": "!!HEAD", "effect": "sway", "degrees": 1.6, "period_ms": 4800},
            {"target": "!!EYE_L", "effect": "blink", "period_ms": 2400, "close_ms": 70, "closed_pct": 8},
            {"target": "!!EYE_R", "effect": "blink", "period_ms": 2400, "close_ms": 70, "closed_pct": 8},
            {"target": "!!HAIR_L", "effect": "sway", "degrees": 3.0, "period_ms": 2400},
            {"target": "!!HAIR_R", "effect": "sway", "degrees": 3.0, "period_ms": 2400, "clockwise": False},
            {"target": "!!SIGN", "effect": "float", "dy_in": round(0.07 * k, 3), "period_ms": 2400},
        ]
        for j, (period, rx) in enumerate([(4800, .10), (2400, .06), (4800, .14), (1600, .05), (2400, .08), (4800, .09)]):
            rows.append({"target": f"!!P{j:02d}", "effect": "orbit", "period_ms": period,
                         "rx_in": round(rx * k, 3), "ry_in": round(rx * 0.6 * k, 3), "clockwise": j % 2 == 0})
        slides[str(i + 1)] = rows
    return {"slides": slides}


def build(output, hold=HOLD_MS, duration=MORPH_MS):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    for i, shot in enumerate(SHOTS):
        build_slide(prs, i, shot)
    spec = motion_spec()
    with tempfile.TemporaryDirectory() as d:
        draft, morph = Path(d) / "draft.pptx", Path(d) / "morph.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, morph, duration, hold, dedupe=True)
        report = pptx_motion.apply(morph, output, spec)
    output.with_suffix(".motion.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, default=Path("build/living-scene/living-scene-spike.pptx"))
    ap.add_argument("--hold", type=int, default=HOLD_MS)
    ap.add_argument("--duration", type=int, default=MORPH_MS)
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = build(args.output, args.hold, args.duration)
    print(f"{args.output}: {len(SHOTS)} slides, {sum(map(len, report.values()))} looping effects "
          f"(SPIKE; PowerPoint playback NOT RUN)")


if __name__ == "__main__":
    main()
