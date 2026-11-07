"""Shared visual kit for panel/camera decks built on scripts/pptx_world.py.

Light "paper" theme, native editable shapes only (no pictures needed). Fonts are module state: the deck's
fonts must exist on the machine that plays it (nothing is embedded or redistributed).
"""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

from pptx_world import H, W

FONTS = {"sans": "Noto Sans CJK TC", "serif": "Noto Serif CJK TC", "mono": "DejaVu Sans Mono"}
SANS, SERIF, MONO = FONTS["sans"], FONTS["serif"], FONTS["mono"]

PAPER, CARD, WALL = "F1EFE7", "FBFAF6", "E9E5D8"
INK, SUB, MUTED = "182B2C", "394B4B", "6B7775"
COPPER, LINE, WHITE = "C35F3F", "D5D0C2", "FFFFFF"
GOOD, BAD = "2E7D5B", "B3402A"
DARK, DARKTXT, DARKSUB = "1B2A2A", "F1EFE7", "A9B5B2"
WIN_W = 3.9
FRAME = (0.9, 2.1, WIN_W)


def set_fonts(sans, serif, mono):
    global SANS, SERIF, MONO
    SANS, SERIF, MONO = sans, serif, mono


def T(c, name, paras, x, y, w, h, pt, color=INK, face=None, **kw):
    face = {None: SANS, "serif": SERIF, "mono": MONO}.get(face, face)
    return c.text(name, paras, x, y, w, h, pt, color, face, SANS, **kw)


def base(c, kicker, headline, tint=CARD, hint=None):
    c.card("card", 0, 0, W, H, tint, shadow=True)
    T(c, "kicker", kicker, 0.9, 0.62, 5.5, 0.3, 14, COPPER, face="mono", bold=True)
    if hint:
        T(c, "hint", hint, 6.3, 0.62, 6.3, 0.3, 14, MUTED, align=PP_ALIGN.RIGHT)
    if headline:
        T(c, "headline", headline, 0.9, 0.98, 11.7, 0.8, 40, INK, bold=True)


def window(c, wx, wy, ww=WIN_W):
    """Reserved box where the next panel appears as a miniature (frame drawn on the previous panel)."""
    wh = ww * H / W
    c.rect("win_sh", wx - .02, wy + .05, ww + .24, wh + .24, "000000", alpha=.12)
    c.rect("win", wx - .12, wy - .12, ww + .24, wh + .24, WHITE, line=(INK, 1.5))


def frame(c, fx, fy, fw, tint=WHITE):
    """A picture frame on the wall that will hold the previous panel."""
    fh = fw * H / W
    c.rect("frm_sh", fx - .1, fy - .05, fw + .5, fh + .5, "000000", alpha=.16)
    c.rect("frm", fx - .22, fy - .22, fw + .44, fh + .44, tint, line=(INK, 2.5))


def para_list(items, mark="•", mark_color=COPPER, body_color=SUB):
    """[(lead, body)] -> paragraphs with a coloured bullet, bold lead and normal body (lead may be '')."""
    out = []
    for lead, body in items:
        runs = [(f"{mark} ", {"color": mark_color, "bold": True})]
        if lead:
            runs.append((lead, {"bold": True, "color": INK}))
        runs.append((body, {"color": body_color}))
        out.append(runs)
    return out


def hbar(c, name, x, y, w, h, value, vmax, color):
    """A horizontal bar whose length is proportional to value (a real, editable rectangle)."""
    return c.rect(name, x, y, max(0.04, w * value / vmax), h, color)


def line(c, name, x, y, w, color=LINE, h=0.015):
    return c.rect(name, x, y, w, h, color)


def row_cells(c, name, y, cells, pt=16, h=0.5, bold_first=True, first_color=INK):
    """cells: [(x, w, text, kwargs)] -> one text box per cell on a shared row."""
    for i, (x, w, text, kw) in enumerate(cells):
        kw = dict(kw)
        color = kw.pop("color", first_color if i == 0 else SUB)
        bold = kw.pop("bold", bold_first and i == 0)
        T(c, f"{name}_{i}", text, x, y, w, h, kw.pop("pt", pt), color, bold=bold, **kw)
