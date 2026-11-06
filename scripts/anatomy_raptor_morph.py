#!/usr/bin/env python3
"""Single-scene, editable, native-PowerPoint Morph study of Anatomy Raptor.
NOT a finished video or a verified Microsoft PowerPoint playback. A/B QA can
run headlessly; C (native playback) requires supported Microsoft PowerPoint.

Source image: wheresryan22/anatomy/.github/assets/raptor-engine-firing.webp
MIT © 2026 Ryan. Do not replace it with arbitrary or placeholder images.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import re
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

W, H = 13.33333, 7.5
BG = "EEECE6"
INK = "182B2C"
SUB = "394B4B"
COPPER = "C35F3F"
MUTED = "707B79"
FONT = "Noto Sans CJK TC"
SERIF = "Noto Serif CJK TC"
IMAGE_SHA256 = "c42a9eb6aacb506f7baf0fd91d4fbb04649999e9615f9847585daff595a62d55"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
TIMINGS = [1400, 2550, 2550, 2800]   # slide advance milliseconds
MORPH_DURATION = 1800                  # transition milliseconds

# Same physical engine throughout. Never swap to an unrelated figure.
POSES = [
    dict(x=5.00, y=-2.65, h=15.10, scene="01", kicker="DETAIL / CLOSE-UP",
         a="一個細節，", b="藏著整套系統。",
         note="從零件，看見運作原理。"),
    dict(x=6.47, y=0.34, h=6.42, scene="02", kicker="REVEAL / PULL BACK",
         a="拉遠一步，", b="全貌就出現。",
         note="從局部，理解整體。"),
    dict(x=6.92, y=-1.48, h=11.62, scene="03", kicker="INSPECT / MOVE CLOSER",
         a="看清連接，", b="才理解運作。",
         note="沿著結構，追蹤運作。"),
    dict(x=6.16, y=0.29, h=6.72, scene="04", kicker="FINALE / WIDE SHOT",
         a="Anatomy", b="讓抽象，變具體。",
         note="SVG · WebGL · 3D Beta"),
]


def inches(v):
    return Inches(v)


def color(v):
    return RGBColor.from_string(v)


def label(slide, name, value, x, y, width, height, size,
          foreground=INK, face=FONT, bold=False, align=PP_ALIGN.LEFT):
    item = slide.shapes.add_textbox(inches(x), inches(y),
                                    inches(width), inches(height))
    item.name = name
    tf = item.text_frame
    tf.clear()
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paragraph = tf.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = value
    run.font.name = face
    run.font.size = Pt(size)
    run.font.color.rgb = color(foreground)
    run.font.bold = bold
    return item


def bar(slide, name, x, y, width, height, fill):
    from pptx.enum.shapes import MSO_SHAPE
    item = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  inches(x), inches(y),
                                  inches(width), inches(height))
    item.name = name
    item.fill.solid()
    item.fill.fore_color.rgb = color(fill)
    item.line.fill.background()
    return item


def official_figure(source: Path, output: Path):
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA256:
        raise ValueError("Official image SHA mismatch; refuse substitution.")
    original = Image.open(source).convert("RGB")
    if original.size != (900, 940):
        raise ValueError(f"Unexpected original size: {original.size}")
    # Remove the original figure card's UI labels; keep the actual engine.
    cropped = original.crop((124, 67, 790, 837)).resize(
        (1148, 1328), Image.Resampling.LANCZOS
    )
    pixels = cropped.load()
    rgba = Image.new("RGBA", cropped.size)
    out = rgba.load()
    alpha = Image.new("L", cropped.size)
    mask = alpha.load()
    for yy in range(cropped.height):
        for xx in range(cropped.width):
            r, g, b = pixels[xx, yy]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            sat = max(r, g, b) - min(r, g, b)
            exhaust = r > g + 11 and r > b + 5 and sat >= 18 and lum > 95
            if exhaust:
                opacity = int((sat - 10) * 4.5 + (254 - lum) * .37)
                rr, gg, bb = int(.70*r+.30*194), int(.55*g+.45*78), int(.40*b+.60*53)
            else:
                opacity = int((234 - lum) * 4.8)
                rr, gg, bb = 39, 54, 54
            mask[xx, yy] = max(0, min(248, opacity))
            out[xx, yy] = (rr, gg, bb, 255)
    rgba.putalpha(alpha.filter(ImageFilter.GaussianBlur(radius=1.4)))
    rgba.save(output, optimize=True)


def paper(output: Path):
    rng = random.Random(42)
    im = Image.new("RGB", (1920, 1080), (238, 236, 230))
    canvas = ImageDraw.Draw(im)
    for _ in range(5200):
        xx, yy = rng.randrange(1920), rng.randrange(1080)
        delta = rng.choice((-7, -4, -2, 1, 3, 4))
        canvas.point((xx, yy), fill=(238+delta, 236+delta, 230+delta))
    for xx in (88, 112, 1798):
        canvas.line((xx, 100, xx, 987), fill=(218, 215, 207), width=1)
    canvas.rectangle((113, 143, 117, 297), fill=(195, 95, 63))
    im.save(output, optimize=True)


def slide(ppt, pose, paper_path: Path, engine_path: Path, license_text: str, index: int):
    page = ppt.slides.add_slide(ppt.slide_layouts[6])
    page.background.fill.solid()
    page.background.fill.fore_color.rgb = color(BG)
    a = page.shapes.add_picture(str(paper_path), 0, 0,
                                width=inches(W), height=inches(H))
    a.name = "!!PAPER"
    art = Image.open(engine_path)
    artw = pose["h"] * art.width / art.height
    a = page.shapes.add_picture(str(engine_path),
                                inches(pose["x"]), inches(pose["y"]),
                                width=inches(artw), height=inches(pose["h"]))
    a.name = "!!ENGINE"
    label(page, "!!BRAND", "ANATOMY", 1.18, .32, 3.1, .35, 16, bold=True)
    bar(page, "!!LITTLE_RULE", 1.19, 1.20, .58, .024, COPPER)
    label(page, "SHOT_"+pose["scene"],
          pose["scene"]+"   /   "+pose["kicker"],
          1.20, 1.52, 4.47, .38, 11, COPPER, bold=True)
    if index == 3:
        label(page, "TITLE_A_"+pose["scene"], pose["a"],
              1.17, 2.18, 4.60, .97, 51, face=SERIF)
        label(page, "TITLE_B_"+pose["scene"], pose["b"],
              1.18, 3.37, 4.56, .86, 31, face=SERIF)
    else:
        label(page, "TITLE_A_"+pose["scene"], pose["a"],
              1.18, 2.29, 4.58, .91, 42, face=SERIF)
        label(page, "TITLE_B_"+pose["scene"], pose["b"],
              1.18, 3.26, 4.58, .92, 39, face=SERIF)
    bar(page, "!!SPLIT_LINE", 1.21, 4.47, .76, .017, COPPER)
    label(page, "DESC_"+pose["scene"], pose["note"],
          1.18, 4.69, 4.63, .53, 21, SUB)
    label(page, "!!SOURCE",
          "SOURCE  /  WHERESRYAN22 · MIT © 2026 RYAN",
          1.18, 6.74, 6.0, .27, 9, MUTED)
    for j in range(4):
        bar(page, "!!PIP_"+str(j), 1.19+j*.35, 6.48,
            .23, .030, COPPER if j == index else "9CABA6")
    page.notes_slide.notes_text_frame.text = (
        "Anatomy authorial example, NOT interactive within PowerPoint. "
        "Source: https://github.com/wheresryan22/anatomy, "
        ".github/assets/raptor-engine-firing.webp. Original image licensed "
        "under MIT © 2026 Ryan. Native Morph is not verified in Microsoft "
        "PowerPoint by CI; LibreOffice previews are static-only.\n\n" +
        license_text
    )
    return page


def inject_native_morph(draft: Path, dest: Path):
    with ZipFile(draft) as archive:
        data = {name: archive.read(name) for name in archive.namelist()}
    slides = sorted(
        (p for p in data if re.fullmatch(r"ppt/slides/slide\d+\.xml", p)),
        key=lambda p: int(re.search(r"slide(\d+)", p).group(1)),
    )
    assert len(slides) == 4
    for index, path in enumerate(slides):
        xml = data[path].decode("utf-8")
        hold = TIMINGS[index]
        if index == 0:
            trans = (
                f'<p:transition xmlns:p="{P}" spd="slow" '
                f'advTm="{hold}" advClick="1"><p:fade/></p:transition>'
            )
        else:
            trans = (
                f'<mc:AlternateContent xmlns:mc="{MC}">'
                f'<mc:Choice xmlns:p159="{P159}" Requires="p159">'
                f'<p:transition xmlns:p="{P}" xmlns:p14="{P14}" '
                f'p14:dur="{MORPH_DURATION}" spd="slow" '
                f'advTm="{hold}" advClick="1">'
                f'<p159:morph option="byObject"/></p:transition>'
                f'</mc:Choice><mc:Fallback>'
                f'<p:transition xmlns:p="{P}" spd="slow" '
                f'advTm="{hold}" advClick="1"><p:fade/></p:transition>'
                f'</mc:Fallback></mc:AlternateContent>'
            )
        if "</p:clrMapOvr>" in xml:
            xml = xml.replace("</p:clrMapOvr>",
                              "</p:clrMapOvr>"+trans, 1)
        else:
            xml, count = re.subn(r"(<p:clrMapOvr[^>]*/>)",
                                 lambda m: m.group(1)+trans, xml, count=1)
            if count != 1:
                raise ValueError("Cannot locate clrMapOvr for transition insertion")
        ET.fromstring(xml.encode())
        data[path] = xml.encode()
    with ZipFile(dest, "w", ZIP_DEFLATED, compresslevel=8) as archive:
        for path, value in data.items():
            archive.writestr(path, value)


def inspect(path: Path):
    ppt = Presentation(path)
    assert len(ppt.slides) == 4
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        xmls = [archive.read(f"ppt/slides/slide{i}.xml").decode()
                for i in range(1, 5)]
        for x in xmls:
            ET.fromstring(x.encode())
            assert "!!PAPER" in x and "!!ENGINE" in x
        assert sum('<p159:morph option="byObject"/>' in x for x in xmls) == 3
        assert sum("<mc:Fallback>" in x for x in xmls) == 3
        assert not any(p.lower().endswith((".mp4", ".mov", ".avi"))
                       for p in archive.namelist())
        for idx, page in enumerate(ppt.slides):
            names = [o.name for o in page.shapes]
            assert names.count("!!ENGINE") == 1
            assert names.count("!!PAPER") == 1
            for obj in page.shapes:
                if not obj.has_text_frame or not obj.text.strip():
                    continue
                xx, yy, ww, hh = (v / 914400 for v in (
                    obj.left, obj.top, obj.width, obj.height))
                assert .1 <= xx and .1 <= yy, (idx, obj.name)
                assert xx+ww <= W-.1 and yy+hh <= H-.1, (idx, obj.name)
                assert obj.name not in ("!!EDITION", "TAG_"+str(idx))
            assert "MIT License" in page.notes_slide.notes_text_frame.text
    return {"slides":4, "native_morph":3, "matching_figure":True,
            "text_bounds":"PASS", "static_visual":"REQUIRES_IMAGE_REVIEW",
            "powerpoint_playback":"BLOCKED/NOT_RUN"}


def build(source: Path, license_path: Path, output: Path):
    license_text = license_path.read_text(encoding="utf-8")
    if "MIT License" not in license_text or "Copyright (c) 2026 Ryan" not in license_text:
        raise ValueError("Missing original author MIT license")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        image = tmp/"engine.png"
        background = tmp/"paper.png"
        official_figure(source, image)
        paper(background)
        ppt = Presentation()
        ppt.slide_width = inches(W)
        ppt.slide_height = inches(H)
        for index, pose in enumerate(POSES):
            slide(ppt, pose, background, image, license_text, index)
        draft = tmp/"draft.pptx"
        ppt.save(draft)
        inject_native_morph(draft, output)
    return inspect(output)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--license", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("build/anatomy-raptor/Anatomy_Raptor_Morph_Candidate.pptx"))
    args = ap.parse_args()
    print(json.dumps(build(args.image, args.license, args.output), ensure_ascii=False))
