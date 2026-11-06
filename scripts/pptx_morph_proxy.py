#!/usr/bin/env python3
"""Layer-B PROXY of a Morph transition: render in-between frames from geometry. NOT a playback test.

Morph matches objects by name and interpolates position and size (and font size for text) between the
two slides, fading unmatched objects. This script reproduces only that geometry in plain slides so the
middle of a transition can be inspected with any renderer (e.g. LibreOffice) for gaps, flashes, objects
passing through text, or zoom ratios that would feel like a jump. Real PowerPoint easing, text handling
and timing are NOT reproduced, so this can only FAIL a design, never prove it works.

  python scripts/pptx_morph_proxy.py deck.pptx proxy.pptx --steps 3
Output: slide 1, N in-between frames, slide 2, N frames, ... Each proxy frame carries a PROXY label.
Supports shapes, freeforms, text boxes and pictures (not groups). Pictures that appear or vanish pop instead of fading.
Requires: python-pptx
"""
import argparse
import copy
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

KINDS = ("sp", "cxnSp", "pic")


def smoothstep(t):
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def named(slide):
    return {s.name: s for s in slide.shapes if s.name.startswith("!!")}


def set_alpha(element, factor):
    """Multiply the alpha of a solid fill (gradient fills are left opaque)."""
    sf = element.spPr.find(qn("a:solidFill")) if element.spPr is not None else None
    if sf is None or not len(sf):
        return
    clr = sf[0]
    alpha = clr.find(qn("a:alpha"))
    current = int(alpha.get("val")) / 100000 if alpha is not None else 1.0
    if alpha is None:
        alpha = etree.SubElement(clr, qn("a:alpha"))
    alpha.set("val", str(int(max(0.0, min(1.0, current * factor)) * 100000)))


def rebind_picture(el, new_slide, origin_slide):
    """A copied p:pic must point at the image part through a relationship of the NEW slide."""
    for blip in el.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            part = origin_slide.part.related_part(rid)
            blip.set(qn("r:embed"), new_slide.part.relate_to(part, RT.IMAGE))


def frame(prs, src, dst, t, label):
    e = smoothstep(t)
    new = prs.slides.add_slide(prs.slide_layouts[6])
    new.background.fill.solid()
    bg = src.background.fill
    try:
        new.background.fill.fore_color.rgb = bg.fore_color.rgb
    except Exception:
        pass
    tree = new.shapes._spTree
    s_map, d_map = named(src), named(dst)
    # objects only on the source fade out underneath; the destination slide's z-order wins for the rest
    for name, shp in s_map.items():
        if name not in d_map and shp._element.tag.rsplit("}", 1)[-1] in KINDS:
            el = copy.deepcopy(shp._element)
            if el.tag.endswith("}pic"):
                rebind_picture(el, new, src)
            else:
                set_alpha(el, 1 - e)
            tree.append(el)
    for shp in dst.shapes:
        if not shp._element.tag.rsplit("}", 1)[-1] in KINDS:
            continue
        el = copy.deepcopy(shp._element)
        other = s_map.get(shp.name)
        if el.tag.endswith("}pic"):
            rebind_picture(el, new, dst)
        tree.append(el)
        moved = [x for x in new.shapes if x._element is el][0]
        if other is None:
            if not el.tag.endswith("}pic"):
                set_alpha(el, e)
            continue
        moved.left = Emu(int(lerp(other.left, shp.left, e)))
        moved.top = Emu(int(lerp(other.top, shp.top, e)))
        moved.width = Emu(int(lerp(other.width, shp.width, e)))
        moved.height = Emu(int(lerp(other.height, shp.height, e)))
        a_runs = list(other._element.iter(qn("a:rPr")))
        b_runs = list(el.iter(qn("a:rPr")))
        if len(a_runs) == len(b_runs):
            for ra, rb in zip(a_runs, b_runs):
                if ra.get("sz") and rb.get("sz"):
                    rb.set("sz", str(int(lerp(int(ra.get("sz")), int(rb.get("sz")), e))))
    for i, el in enumerate(tree.iter(qn("p:cNvPr")), start=2):
        el.set("id", str(i))  # proxy slides must not carry colliding ids
    box = new.shapes.add_textbox(Emu(int(prs.slide_width * .35)), Emu(int(prs.slide_height * .955)),
                                 Emu(int(prs.slide_width * .3)), Emu(int(prs.slide_height * .04)))
    box.name = "PROXY_LABEL"
    run = box.text_frame.paragraphs[0].add_run()
    run.text, run.font.size = label, Pt(10)
    return new


def build(src_path, dst_path, steps):
    prs = Presentation(src_path)
    originals = list(prs.slides)
    order = []
    for i, slide in enumerate(originals):
        order.append(slide)
        if i + 1 < len(originals):
            for k in range(1, steps + 1):
                t = k / (steps + 1)
                order.append(frame(prs, slide, originals[i + 1], t, f"PROXY slide {i + 1}->{i + 2}  t={t:.2f}  (geometry only)"))
    ids = prs.slides._sldIdLst
    elements = list(ids)
    by_part = {id(s.part): el for s, el in zip(list(prs.slides), elements)}
    for el in elements:
        ids.remove(el)
    for s in order:
        ids.append(by_part[id(s.part)])
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(dst_path)
    return len(order)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--steps", type=int, default=3, help="in-between frames per transition")
    args = ap.parse_args()
    print(f"{args.output}: {build(args.input, args.output, args.steps)} slides (PROXY, not PowerPoint playback)")


if __name__ == "__main__":
    main()
