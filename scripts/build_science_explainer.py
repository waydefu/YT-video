#!/usr/bin/env python3
"""G2 minimum proof: a FORMAL science-explainer PowerPoint with seamless Morph transitions.

Deliverable class: a normal, editable content deck for a popular-science YouTube video whose
slide-to-slide transitions are continuous camera moves instead of cuts (native Office Morph).
It is NOT a character animation. Subtle ambient loops are optional (--no-ambient).

One continuous "world" holds every slide's content as panels. Each slide is only a camera pose:
  1 title (wide)  ->  2 ZOOM-THROUGH into a window on the title page (panel B lives inside A)
  2 -> 3  PAN along the wall to the neighbouring window (panel C)
  3 -> 4  PULL-BACK REVEAL: the diagram turns out to be a picture frame inside a bigger scene (D)
Matching `!!` names across slides let Morph move the camera.

Topic: why the sky is blue (Rayleigh scattering). ALL FACTS ARE DRAFT AND NEED HUMAN REVIEW
(see docs/PPTX-SEAMLESS-EXPLAINER.md). Everything drawn is original procedural vector art.
STATUS: SPIKE. Layer A/B only; Microsoft PowerPoint playback (layer C) is NOT RUN.
Requires: python-pptx
"""
import argparse
import json
import random
import sys
import tempfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pptx_morph_patch  # noqa: E402
import pptx_motion  # noqa: E402

EMU = 914400
W, H = 13.333333, 7.5
FONT = "Noto Sans CJK TC"
HOLD_MS, MORPH_MS = 4800, 1500

# ---- world layout (inches). Panels are 16:9 cards; nested ones are scaled copies of the slide ----
B_W = 3.9                       # width of the small "window" panels
S_WIN = B_W / W                 # their scale relative to a full slide
A = dict(ox=0.0, oy=0.0, s=1.0)
B = dict(ox=8.55, oy=1.15, s=S_WIN)
C = dict(ox=13.6, oy=1.15, s=S_WIN)
FRAME_LOCAL = (4.4, 1.55, 4.5)  # where, inside D, the picture frame (= panel C) hangs: x, y, width
S_D = B_W / FRAME_LOCAL[2]
D = dict(ox=C["ox"] - FRAME_LOCAL[0] * S_D, oy=C["oy"] - FRAME_LOCAL[1] * S_D, s=S_D)
WORLD_END = 18.5
# The sky is split in two (PowerPoint shapes top out near 56 in once zoomed). The seam sits in the gap
# between the two windows, outside the wide shot (x > 13.33) and outside both close-up shots.
SEAM_X = 13.45


def centre(p):
    return p["ox"] + W * p["s"] / 2, p["oy"] + H * p["s"] / 2


SHOTS = [  # camera (cx, cy, zoom), caption
    (*centre(A), 1.0, "01"), (*centre(B), 1 / S_WIN, "02"),
    (*centre(C), 1 / S_WIN, "03"), (*centre(D), 1 / S_D, "04"),
]
C_ = dict(navy="0A1024", sky_top="0B2A6B", sky_bot="5FB4FF", sun="FFD54A", glow="FFE9A0", white="FFFFFF",
          ink="F4F7FF", muted="B9C6E4", red="FF4D4D", orange="FF9F1C", yellow="FFE066", green="3DDC84",
          blue="3D8BFF", violet="9B5CFF", wood="6B4423", dusk_top="3B1C5A", dusk_bot="FF8A3D", ground="1D1233")


def rgb(h):
    return RGBColor.from_string(h)


class Ctx:
    """Draws panel-local coordinates through the slide's camera."""

    def __init__(self, slide, shot):
        self.sl, (self.cx, self.cy, self.z) = slide, shot[:3]
        self.n = 0

    def _pt(self, p, lx, ly):
        return (W / 2 + (p["ox"] + lx * p["s"] - self.cx) * self.z,
                H / 2 + (p["oy"] + ly * p["s"] - self.cy) * self.z)

    def _k(self, p):
        return p["s"] * self.z

    def _finish(self, shp, name, fill, alpha=None, grad=None):
        shp.name = "!!" + name
        shp.line.fill.background()
        if grad:
            shp.fill.gradient()
            shp.fill.gradient_angle = 270
            for stop, col, pos in zip(shp.fill.gradient_stops, grad, (0, 1)):
                stop.color.rgb, stop.position = rgb(col), pos
        elif fill is None:
            shp.fill.background()
        else:
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(fill)
            if alpha is not None:
                clr = shp._element.spPr.find(qn("a:solidFill"))[0]
                etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))
        if shp._element.spPr.find(qn("a:effectLst")) is None:  # never inherit the theme's shadow
            etree.SubElement(shp._element.spPr, qn("a:effectLst"))
        return shp

    def rect(self, name, p, lx, ly, lw, lh, fill=None, alpha=None, grad=None, kind=MSO_SHAPE.RECTANGLE):
        x, y = self._pt(p, lx, ly)
        k = self._k(p)
        shp = self.sl.shapes.add_shape(kind, Emu(int(x * EMU)), Emu(int(y * EMU)),
                                       Emu(int(lw * k * EMU)), Emu(int(lh * k * EMU)))
        return self._finish(shp, name, fill, alpha, grad)

    def oval(self, name, p, cx, cy, r, fill, alpha=None):
        return self.rect(name, p, cx - r, cy - r, 2 * r, 2 * r, fill, alpha, kind=MSO_SHAPE.OVAL)

    def poly(self, name, p, pts, fill, alpha=None):
        e = [(int(x * EMU), int(y * EMU)) for x, y in (self._pt(p, *q) for q in pts)]
        fb = self.sl.shapes.build_freeform(e[0][0], e[0][1], scale=1.0)
        fb.add_line_segments(e[1:], close=True)
        return self._finish(fb.convert_to_shape(), name, fill, alpha)

    def seg(self, name, p, x1, y1, x2, y2, width, fill, alpha=None):
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** 0.5 or 1
        ox, oy = -dy / n * width / 2, dx / n * width / 2
        return self.poly(name, p, [(x1 + ox, y1 + oy), (x2 + ox, y2 + oy), (x2 - ox, y2 - oy), (x1 - ox, y1 - oy)],
                         fill, alpha)

    def text(self, name, p, value, lx, ly, lw, lh, pt, color, bold=False, align=PP_ALIGN.LEFT):
        x, y = self._pt(p, lx, ly)
        k = self._k(p)
        box = self.sl.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)), Emu(int(lw * k * EMU)), Emu(int(lh * k * EMU)))
        box.name = "!!" + name
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        para = tf.paragraphs[0]
        para.alignment = align
        run = para.add_run()
        run.text = value
        run.font.name, run.font.size, run.font.bold = FONT, Pt(max(1.0, pt * k)), bold
        run.font.color.rgb = rgb(color)
        return box


def draw_a(c):
    c.rect("A_BG1", A, 0, 0, SEAM_X + .06, H, grad=(C_["sky_top"], C_["sky_bot"]))
    c.rect("A_BG2", A, SEAM_X, 0, WORLD_END - SEAM_X, H, grad=(C_["sky_top"], C_["sky_bot"]))
    rnd = random.Random(11)
    for i in range(24):
        c.oval(f"A_STAR_{i:02d}", A, rnd.uniform(0.3, WORLD_END - 0.3), rnd.uniform(0.2, 3.2), rnd.uniform(.02, .05),
               C_["white"], alpha=rnd.uniform(.35, .9))
    c.oval("A_GLOW1", A, 2.8, 1.9, 1.6, C_["glow"], alpha=.16)
    c.oval("A_GLOW2", A, 2.8, 1.9, 1.25, C_["glow"], alpha=.22)
    c.oval("A_SUN", A, 2.8, 1.9, .85, C_["sun"])
    c.text("A_TXT1", A, "為什麼天空是藍色？", 1.2, 3.75, 7.4, 1.1, 54, C_["white"], bold=True)
    c.text("A_TXT2", A, "一束白光，如何染藍整片天空", 1.25, 4.95, 7.0, .6, 26, C_["ink"])
    for tag, pan in (("B", B), ("C", C)):
        c.rect(f"A_WINFRAME_{tag}", A, pan["ox"] - .12, pan["oy"] - .12, B_W + .24, H * S_WIN + .24, C_["white"], alpha=.92)


def draw_b(c):
    c.rect("B_BG", B, 0, 0, W, H, C_["navy"])
    c.seg("B_BEAM", B, 0.9, 3.85, 5.95, 3.85, .14, C_["white"])
    c.poly("B_PRISM", B, [(5.9, 5.0), (6.45, 2.5), (7.0, 5.0)], C_["white"], alpha=.28)
    cols = [C_["red"], C_["orange"], C_["yellow"], C_["green"], C_["blue"], C_["violet"]]
    for i, col in enumerate(cols):
        y0, y1 = 2.35 + i * .5, 2.35 + (i + 1) * .5
        c.poly(f"B_BAND_{i}", B, [(6.85, 3.85), (12.6, y0), (12.6, y1)], col, alpha=.9)
    c.text("B_TXT1", B, "白光＝各種顏色的光", 0.9, 0.55, 11.5, .9, 40, C_["white"], bold=True)
    c.text("B_TXT2", B, "藍光波長短，紅光波長長", 0.9, 6.2, 11.5, .7, 28, C_["muted"])


def draw_c(c):
    c.rect("C_BG", C, 0, 0, W, H, grad=(C_["sky_top"], C_["sky_bot"]))
    c.seg("C_BEAM", C, 0.0, 3.85, 1.6, 3.85, .16, C_["white"])
    c.seg("C_RED", C, 1.6, 3.85, 13.3, 3.85, .1, C_["red"])
    rnd = random.Random(5)
    mols = [(3.4, 3.85), (5.6, 3.4), (7.9, 4.4), (10.2, 3.6), (4.6, 4.9), (8.8, 2.9), (11.6, 4.8), (6.4, 5.3)]
    for i, (mx, my) in enumerate(mols):
        c.oval(f"C_MOL_{i}", C, mx, my, .13, C_["white"], alpha=.85)
    zig = [(3.4, 3.85), (4.3, 2.7), (5.6, 3.4), (6.7, 2.4), (7.9, 4.4), (9.0, 5.5), (10.2, 3.6), (11.3, 2.4)]
    for i in range(len(zig) - 1):
        c.seg(f"C_BLUE_{i}", C, *zig[i], *zig[i + 1], .08, C_["blue"])
    c.text("C_TXT1", C, "藍光更容易被空氣分子散射", 0.9, 0.55, 11.5, .9, 40, C_["white"], bold=True)
    c.text("C_TXT2", C, "散射強度與波長的 4 次方成反比", 0.9, 5.85, 11.5, .6, 28, C_["white"])
    c.text("C_TXT3", C, "藍光（約 450 nm）比紅光（約 700 nm）散射約 6 倍", 0.9, 6.5, 11.5, .5, 24, C_["ink"])


def draw_d(c):
    c.rect("D_BG", D, 0, 0, W, H, grad=(C_["dusk_top"], C_["dusk_bot"]))
    c.oval("D_SUN", D, 11.0, 4.35, .95, C_["yellow"])
    c.rect("D_CLOUD1", D, 9.2, 1.75, 1.9, .42, C_["white"], alpha=.28, kind=MSO_SHAPE.OVAL)
    c.rect("D_CLOUD2", D, 10.9, 1.2, 1.3, .3, C_["white"], alpha=.22, kind=MSO_SHAPE.OVAL)
    c.rect("D_GROUND", D, 0, 4.7, W, H - 4.7, C_["ground"])
    c.poly("D_HILL", D, [(0, 4.7), (2.5, 4.25), (5.0, 4.6), (8.0, 4.2), (13.333, 4.65), (13.333, 4.75), (0, 4.75)], C_["ground"])
    fx, fy, fw = FRAME_LOCAL
    fh = fw * H / W
    c.rect("D_FRAME_SHADOW", D, fx - .1, fy - .1, fw + .35, fh + .35, "000000", alpha=.35)
    c.rect("D_FRAME", D, fx - .25, fy - .25, fw + .5, fh + .5, C_["wood"])
    c.text("D_TXT1", D, "日落為什麼是紅色？", 0.9, 0.45, 8.0, .7, 40, C_["white"], bold=True)
    c.text("D_TXT2", D, "太陽靠近地平線時，光要穿過更厚的大氣", 0.9, 5.15, 11.5, .6, 28, C_["white"])
    c.text("D_TXT3", D, "藍光多半被散射掉，剩下紅橙光抵達眼睛", 0.9, 5.85, 11.5, .6, 28, C_["white"])


def build_slide(prs, idx, shot):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = rgb(C_["navy"])
    c = Ctx(sl, shot)
    draw_a(c)
    draw_b(c)
    if idx == 3:  # D exists only on the reveal slide; Morph fades it in while the camera pulls back
        draw_d(c)
    draw_c(c)     # C stays above D so it reads as the picture inside the frame
    for j in range(4):
        pip = c.rect(f"HUD_PIP_{j}", dict(ox=0, oy=0, s=1), 0.9 + j * .38, .5, .26, .035,
                     C_["yellow"] if j == idx else "5A6C96")
        pip.name = f"!!HUD_PIP_{j}"
    hud = Ctx(sl, (W / 2, H / 2, 1.0))
    hud.text("HUD_NOTE", dict(ox=0, oy=0, s=1), "SPIKE · 內容待審", 9.4, .4, 3.1, .3, 14, C_["muted"], align=PP_ALIGN.RIGHT)
    sl.notes_slide.notes_text_frame.text = (
        "SPIKE：原創向量；科普內容為草稿，事實待人工審核。轉場為原生 Morph，PowerPoint 實播：NOT RUN。")
    return sl


def motion_spec(ambient=True):
    if not ambient:
        return {"slides": {}}
    base = {"A_SUN": ("breathe", dict(amplitude=2.0, period_ms=2400)),
            "A_GLOW1": ("breathe", dict(amplitude=3.0, period_ms=2400)),
            "A_GLOW2": ("breathe", dict(amplitude=2.0, period_ms=1200))}
    slides = {}
    for i, shot in enumerate(SHOTS):
        z = shot[2]
        rows = [{"target": n, "effect": e, **kw} for n, (e, kw) in base.items()]
        for m in range(3):
            rows.append({"target": f"!!C_MOL_{m}"[2:], "effect": "orbit", "period_ms": (2400, 1200, 2400)[m],
                         "rx_in": round(.05 * z * S_WIN * 3, 3), "ry_in": round(.03 * z * S_WIN * 3, 3), "clockwise": m % 2 == 0})
        if i == 3:
            rows += [{"target": "D_SUN", "effect": "breathe", "amplitude": 2.0, "period_ms": 2400},
                     {"target": "D_CLOUD1", "effect": "float", "dx_in": .12, "dy_in": .02, "period_ms": 2400},
                     {"target": "D_CLOUD2", "effect": "float", "dx_in": -.1, "dy_in": .02, "period_ms": 2400}]
        for r in rows:
            r["target"] = "!!" + r["target"].lstrip("!")
        slides[str(i + 1)] = rows
    return {"slides": slides}


def readable_manifest():
    """Text that is meant to be read on each slide (the focused panel + HUD). Nested glimpses elsewhere are not."""
    focus = ["A", "B", "C", "D"]
    names = {"A": ["A_TXT1", "A_TXT2"], "B": ["B_TXT1", "B_TXT2"], "C": ["C_TXT1", "C_TXT2", "C_TXT3"],
             "D": ["D_TXT1", "D_TXT2", "D_TXT3"]}
    return {str(i + 1): ["!!" + n for n in names[f]] + ["!!HUD_NOTE"] for i, f in enumerate(focus)}


def build(output, hold=HOLD_MS, duration=MORPH_MS, ambient=True):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    for i, shot in enumerate(SHOTS):
        build_slide(prs, i, shot)
    spec = motion_spec(ambient)
    with tempfile.TemporaryDirectory() as d:
        draft, morph = Path(d) / "draft.pptx", Path(d) / "morph.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, morph, duration, hold, dedupe=True)
        report = pptx_motion.apply(morph, output, spec) if ambient else {}
        if not ambient:
            Path(output).write_bytes(morph.read_bytes())
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable_manifest(), ensure_ascii=False, indent=1), encoding="utf-8")
    Path(output).with_suffix(".motion.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, default=Path("build/science-explainer/science-explainer-spike.pptx"))
    ap.add_argument("--hold", type=int, default=HOLD_MS, help="per-slide hold (ms); tie to narration length")
    ap.add_argument("--duration", type=int, default=MORPH_MS, help="Morph transition (ms)")
    ap.add_argument("--no-ambient", action="store_true", help="transitions only; no ambient loops")
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = build(args.output, args.hold, args.duration, not args.no_ambient)
    print(f"{args.output}: {len(SHOTS)} slides, {sum(map(len, report.values()))} ambient loops "
          f"(SPIKE; PowerPoint playback NOT RUN)")


if __name__ == "__main__":
    main()
