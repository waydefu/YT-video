#!/usr/bin/env python3
"""A continuous "world" of slide-sized panels where every slide is just a camera pose (for Morph decks).

You design each panel like a normal 13.333 x 7.5 in slide (panel-local coordinates). The World places panels
relative to each other so that moving the camera from one slide to the next is one of:
  pan_right / pan_down   the next panel sits beside / below the previous one at the same scale
  zoom_in(window)        the next panel is a miniature "window" inside a reserved box of the previous panel
  pull_back(frame)       the previous panel turns out to be a picture hanging in a reserved frame of a bigger next panel
Every slide draws all panels that the neighbouring camera moves can see, under globally unique `!!` names, so
PowerPoint's Morph tweens positions and sizes into one continuous shot. Text sizes are compensated so that the
panel a slide is focused on reads at its design size.

Layer-A/B tooling only: this builds the file; it cannot prove how Microsoft PowerPoint plays it.
Requires: python-pptx, Pillow
"""
from collections import defaultdict

from lxml import etree
from PIL import Image
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

EMU = 914400
W, H = 13.333333, 7.5
MAX_SHAPE_IN = 55.0  # PowerPoint's UI tops out near 56 in; larger shapes risk problems


def rgb(h):
    return RGBColor.from_string(h)


class Panel:
    def __init__(self, idx, ox, oy, s, draw, kind, target=False, rank=None):
        self.idx, self.ox, self.oy, self.s, self.draw, self.kind, self.target = idx, ox, oy, s, draw, kind, target
        self.rank = idx if rank is None else rank

    @property
    def rect(self):
        return (self.ox, self.oy, self.ox + W * self.s, self.oy + H * self.s)


class Ctx:
    """Draw in the local coordinates of the current panel, seen through the slide's camera."""

    def __init__(self, slide, view):
        self.sl, (self.cx, self.cy, self.z) = slide, view
        self.p = None
        self.texts = defaultdict(list)
        self.biggest = (0.0, "")

    # ---- geometry -------------------------------------------------------------------------------------------
    def pt(self, lx, ly):
        p = self.p
        return W / 2 + (p.ox + lx * p.s - self.cx) * self.z, H / 2 + (p.oy + ly * p.s - self.cy) * self.z

    @property
    def k(self):
        return self.p.s * self.z

    def _emu(self, v):
        return Emu(int(round(v * EMU)))

    def _name(self, name):
        return f"!!P{self.p.idx:02d}_{name}"

    def _track(self, name, w, h):
        self.biggest = max(self.biggest, (max(w, h), name))
        if max(w, h) > MAX_SHAPE_IN:
            raise ValueError(f"{name} would be {max(w, h):.1f} in wide/high on this slide (limit {MAX_SHAPE_IN})")

    def _finish(self, shp, name, fill, alpha=None, grad=None, line=None):
        shp.name = self._name(name)
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
        if line:
            shp.line.color.rgb = rgb(line[0])
            shp.line.width = Pt(line[1])
        else:
            shp.line.fill.background()
        if shp._element.spPr.find(qn("a:effectLst")) is None:  # never inherit the theme's shadow
            etree.SubElement(shp._element.spPr, qn("a:effectLst"))
        return shp

    # ---- primitives -----------------------------------------------------------------------------------------
    def rect(self, name, lx, ly, lw, lh, fill=None, alpha=None, grad=None, line=None, kind=MSO_SHAPE.RECTANGLE, round_=None):
        x, y = self.pt(lx, ly)
        w, h = lw * self.k, lh * self.k
        self._track(self._name(name), w, h)
        shp = self.sl.shapes.add_shape(kind, self._emu(x), self._emu(y), self._emu(w), self._emu(h))
        if round_ is not None:
            shp.adjustments[0] = round_
        return self._finish(shp, name, fill, alpha, grad, line)

    def oval(self, name, cx, cy, r, fill, alpha=None, line=None):
        return self.rect(name, cx - r, cy - r, 2 * r, 2 * r, fill, alpha, line=line, kind=MSO_SHAPE.OVAL)

    def poly(self, name, pts, fill, alpha=None, line=None):
        e = [(int(round(x * EMU)), int(round(y * EMU))) for x, y in (self.pt(*q) for q in pts)]
        xs, ys = [p[0] for p in e], [p[1] for p in e]
        self._track(self._name(name), (max(xs) - min(xs)) / EMU, (max(ys) - min(ys)) / EMU)
        fb = self.sl.shapes.build_freeform(e[0][0], e[0][1], scale=1.0)
        fb.add_line_segments(e[1:], close=True)
        return self._finish(fb.convert_to_shape(), name, fill, alpha, line=line)

    def card(self, name, lx, ly, lw, lh, fill, border="D5D0C2", shadow=True, round_=None):
        """A panel-like card: soft shadow + fill + hairline border."""
        if shadow:
            self.rect(name + "_sh", lx + .06, ly + .09, lw, lh, "000000", alpha=.10,
                      kind=MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE, round_=round_)
        return self.rect(name, lx, ly, lw, lh, fill, line=(border, .75),
                         kind=MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE, round_=round_)

    def picture(self, name, path, lx, ly, lw, lh, align="center"):
        """Place an image inside the box, scaled to fit (never cropped or stretched)."""
        iw, ih = Image.open(path).size
        scale = min(lw / iw, lh / ih)
        w, h = iw * scale, ih * scale
        px = lx + (lw - w) / 2 if align == "center" else lx
        py = ly + (lh - h) / 2
        x, y = self.pt(px, py)
        self._track(self._name(name), w * self.k, h * self.k)
        pic = self.sl.shapes.add_picture(str(path), self._emu(x), self._emu(y), self._emu(w * self.k), self._emu(h * self.k))
        pic.name = self._name(name)
        return pic

    def text(self, name, paras, lx, ly, lw, lh, pt, color, face, ea, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, after=0.0, spacing=1.0, track=True):
        """paras: str | [str | [(text, {bold,color,pt,face}), ...]]. Sizes are in design points of the panel."""
        x, y = self.pt(lx, ly)
        w, h = lw * self.k, lh * self.k
        self._track(self._name(name), w, h)
        box = self.sl.shapes.add_textbox(self._emu(x), self._emu(y), self._emu(w), self._emu(h))
        box.name = self._name(name)
        tf = box.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        if isinstance(paras, str):
            paras = [paras]
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = spacing
            p.space_after = Pt(after * self.k)
            runs = [(para, {})] if isinstance(para, str) else para
            for text, st in runs:
                r = p.add_run()
                r.text = text
                f = r.font
                f.name, f.size = st.get("face", face), Pt(max(1.0, st.get("pt", pt) * self.k))
                f.bold = st.get("bold", bold)
                f.color.rgb = rgb(st.get("color", color))
                rpr = r._r.get_or_add_rPr()
                etree.SubElement(rpr, qn("a:ea")).set("typeface", st.get("ea", ea))
        if track:
            self.texts[self.p.idx].append(box.name)
        return box


class World:
    def __init__(self, gap=0.6):
        self.panels, self.gap = [], gap

    def first(self, draw):
        self.panels.append(Panel(0, 0.0, 0.0, 1.0, draw, "start"))
        return self.panels[-1]

    def add(self, draw, kind, **kw):
        prev = self.panels[-1]
        n = len(self.panels)
        if kind == "pan_right":
            panel = Panel(n, prev.ox + (W + self.gap) * prev.s, prev.oy, prev.s, draw, kind)
        elif kind == "pan_down":
            panel = Panel(n, prev.ox, prev.oy + (H + self.gap) * prev.s, prev.s, draw, kind)
        elif kind == "zoom_in":
            wx, wy, ww = kw["window"]
            panel = Panel(n, prev.ox + wx * prev.s, prev.oy + wy * prev.s, prev.s * ww / W, draw, kind)
        elif kind == "pull_back":
            fx, fy, fw = kw["frame"]
            s = prev.s * W / fw
            panel = Panel(n, prev.ox - fx * s, prev.oy - fy * s, s, draw, kind, target=True, rank=prev.rank - 0.5)
        else:
            raise ValueError(kind)
        self.panels.append(panel)
        return panel

    def view(self, i):
        p = self.panels[i]
        return p.ox + W * p.s / 2, p.oy + H * p.s / 2, 1.0 / p.s

    def _visible(self, j):
        n = len(self.panels)
        rects = [self.panels[k].rect for k in range(max(0, j - 1), min(n, j + 2))]
        boxes = []
        for a, b in ((j - 1, j), (j, j + 1)):
            if 0 <= a < n and 0 <= b < n:
                ra, rb = self.panels[a].rect, self.panels[b].rect
                boxes.append((min(ra[0], rb[0]), min(ra[1], rb[1]), max(ra[2], rb[2]), max(ra[3], rb[3])))
        if not boxes:
            boxes = [rects[0]]
        out = []
        for p in self.panels:
            if p.target and j < p.idx:
                continue  # a pull-back scene only exists from its own slide on (Morph fades it in)
            r = p.rect
            if any(r[0] < b[2] and r[2] > b[0] and r[1] < b[3] and r[3] > b[1] for b in boxes):
                out.append(p)
        return sorted(out, key=lambda p: p.rank)

    def build(self, prs, hud=None, notes=None):
        """Create one slide per panel. Returns {slide_number: [readable text names]} for the validator."""
        readable = {}
        for j in range(len(self.panels)):
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            ctx = Ctx(sl, self.view(j))
            for p in self._visible(j):
                ctx.p = p
                p.draw(ctx)
            names = list(ctx.texts.get(j, []))
            if hud:
                cx, cy, z = self.view(j)  # HUD lives in slide coordinates: panel scale 1/z cancels the camera zoom
                ctx.p = Panel(99, cx - W / 2 / z, cy - H / 2 / z, 1.0 / z, None, "hud")
                hud(ctx, j)
                names += ctx.texts.get(99, [])
            if notes:
                sl.notes_slide.notes_text_frame.text = notes(j)
            readable[str(j + 1)] = names
        return readable

    def describe(self):
        return [(p.idx + 1, p.kind, round(p.s, 4), round(1 / p.s, 3)) for p in self.panels]
