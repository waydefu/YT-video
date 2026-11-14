#!/usr/bin/env python3
"""16-slide demo of the motion motifs in scripts/deck_motion.py (ripple rings, ring-to-rail menu, vertical pager with a
persistent rail, rolling numerals, arc wheel list, re-dealing cards) with a different Morph duration per transition.

Content is generic placeholder text; the point is the mechanisms. Original shapes only.
STATUS: SPIKE/PREVIEW. Layers A and B only; how PowerPoint tweens rotation and font size is NOT verified.
Usage: python scripts/build_motion_kit_demo.py [--output build/motion-kit/motion-kit-demo.pptx]
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_kit as K  # noqa: E402
import deck_motion as M  # noqa: E402
import pptx_morph_patch  # noqa: E402
from deck_kit import CARD, COPPER, INK, MUTED, SUB, WHITE, T  # noqa: E402
from pptx_world import EMU, H, W, World  # noqa: E402

ITEMS = ["引言", "問題", "方法", "結果", "討論", "結論"]
CX, CY = W / 2, 3.75
# transition duration (ms) INTO each slide; slide 1's value is unused. Short for pager steps, longer for reveals.
DURATIONS = [0, 1100, 900, 700, 800, 600, 600, 600, 700, 600, 800, 500, 500, 800, 600, 600]
HOLD_MS = 2200


def page(c, headline=None):
    c.card("card", 0, 0, W, H, CARD, shadow=True)
    if headline:
        T(c, "headline", headline, 1.0, 0.6, 11.3, 0.8, 36, INK, bold=True)


def ripple(t, logo_at=(CX, CY), logo_r=0.9, alpha=0.22, title=False):
    def draw(c):
        page(c)
        M.draw_ripple(c, "rp", logo_at[0], logo_at[1], M.ripple_radii(4, t, 9.0), COPPER, base_alpha=alpha)
        c.oval("logo", logo_at[0], logo_at[1], logo_r, WHITE, line=(COPPER, 2.0))
        T(c, "logo_t", "示", logo_at[0] - 0.5, logo_at[1] - 0.45, 1.0, 0.9, 40, COPPER, bold=True, align=PP_ALIGN.CENTER)
        if title:
            T(c, "ttl", "章節導覽示範", 4.4, 2.7, 8.0, 1.0, 54, INK, bold=True)
            T(c, "sub", "旋轉　垂直換頁　放射選單", 4.4, 3.9, 8.0, 0.6, 24, SUB)
    return draw


def content(letter, title, lines):
    def draw(c):
        page(c)
        T(c, "ctitle", title, 3.6, 1.1, 8.5, 0.9, 44, INK, bold=True)
        T(c, "cbody", lines, 3.6, 2.4, 4.6, 3.0, 26, SUB, after=10)
        c.rect("cimg", 8.5, 2.3, 3.8, 3.0, "E3DFD2", line=(K.LINE, 1.0))
        T(c, "cimg_t", "示意圖", 8.5, 3.5, 3.8, 0.6, 26, MUTED, align=PP_ALIGN.CENTER)
    return draw


def roll(active):
    def draw(c):
        page(c, "數字滾動")
        nums = M.roll_layout(3, active, 1.2, 2.0, 5.4, -20.0)
        M.draw_roll(c, "rn", ["01", "02", "03"], nums, 110, COPPER, w=2.6, h=1.8)
        for it in nums:
            it["x"] = 3.8
            it["y"] += 0.5
        M.draw_roll(c, "rt", ["引言", "問題", "方法"], nums, 44, INK, w=6.0, h=1.0)
    return draw


def wheel(active):
    def draw(c):
        page(c, "弧線清單")
        c.oval("arc", 7.2, CY, 3.4, None, line=(K.LINE, 2.0))
        M.draw_wheel(c, "wl", ITEMS, M.wheel_layout(6, active, 7.2, CY, 3.4, step_deg=20.0), COPPER)
        T(c, "wstage", f"目前：{ITEMS[active]}", 8.2, 3.2, 4.4, 0.8, 34, INK, bold=True)
    return draw


def cards(state):
    texts = [["案例一", "案例二", "案例三", "案例四"], ["案例一", "案例二", "案例三", "案例四"], ["重點 A", "重點 B", "重點 C", "重點 D"]]
    def draw(c):
        page(c, "卡片重排")
        M.draw_cards(c, "cd", texts[state], M.shuffle_layout(2, 2, 3.5, 1.7, 3.2, 2.0, 0.3, state))
    return draw


SLIDES = [  # (draw, device)
    (ripple(0.12), None), (ripple(1.0), "stay"), (ripple(1.3, (2.2, CY), 1.2, 0.10, True), "stay"),
    (lambda c: page(c), "stay"),  # radial menu lives in the HUD
    (content("A", "引言", ["說明問題背景", "列出本章重點", "一頁一個重點"]), "stay"),
    (content("B", "問題", ["描述目前的限制", "每章整塊向上換頁", "左側欄保持不動"]), "pan_down"),
    (content("C", "方法", ["說明做法", "左欄啟動項改變", "內容像翻頁"]), "pan_down"),
    (content("D", "結果", ["呈現結果", "再往下一章", "動作要短"]), "pan_down"),
    (roll(0), "pan_right"), (roll(1), "stay"),
    (wheel(0), "pan_right"), (wheel(1), "stay"), (wheel(2), "stay"),
    (cards(0), "pan_right"), (cards(1), "stay"), (cards(2), "stay"),
]


def build(output, hold=HOLD_MS, fonts=None):
    if fonts:
        K.set_fonts(*fonts)
    world = World(gap=0.6)
    for i, (draw, kind) in enumerate(SLIDES):
        if kind is None:
            world.first(draw)
        else:
            world.add(draw, kind, dur=DURATIONS[i])
    n = len(SLIDES)

    def hud(c, j):
        c.rect("hud_track", 1.0, 0.25, 11.3, 0.05, "D9D4C6")
        c.rect("hud_fill", 1.0, 0.25, 11.3 * (j + 1) / n, 0.05, COPPER)
        if j == 3:  # radial menu
            c.oval("hub", CX, 3.9, 1.1, COPPER)
            T(c, "hub_t", "目錄", CX - 0.8, 3.65, 1.6, 0.5, 30, WHITE, bold=True, align=PP_ALIGN.CENTER)
            M.draw_menu(c, "rm", ITEMS, M.ring_layout(6, CX, 3.9, 2.4), None, label_dx=0.6)
        elif 4 <= j <= 7:  # the same markers as a rail, the active one filled
            c.oval("hub", 1.0, 0.9, 0.2, COPPER)
            T(c, "hub_t", "", 0.9, 0.8, 0.2, 0.2, 14, WHITE)
            M.draw_menu(c, "rm", ITEMS, M.column_layout(6, 1.1, 1.7, 0.95), j - 4, label_dx=0.7)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    readable = world.build(prs, hud=hud, hud_readable=False)
    with tempfile.TemporaryDirectory() as d:
        draft = Path(d) / "draft.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, output, world.durations(900), hold, dedupe=True)
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable, ensure_ascii=False, indent=1), encoding="utf-8")
    return world


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, default=Path("build/motion-kit/motion-kit-demo.pptx"))
    ap.add_argument("--hold", type=int, default=HOLD_MS)
    ap.add_argument("--font-sans", default=K.FONTS["sans"])
    ap.add_argument("--font-serif", default=K.FONTS["serif"])
    ap.add_argument("--font-mono", default=K.FONTS["mono"])
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build(args.output, args.hold, (args.font_sans, args.font_serif, args.font_mono))
    print(f"{args.output}: {len(SLIDES)} slides, {len(SLIDES) - 1} native Morph transitions (SPIKE; PowerPoint playback NOT RUN)")


if __name__ == "__main__":
    main()
