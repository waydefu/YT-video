#!/usr/bin/env python3
"""G2 minimum proof: a "board tour" for data-heavy slides (7 slides, native Morph), built on the AI-subscriptions content.

Why: the picture-frame trick of the reference video (previous page hung in a frame) is natural for pictures but reads
as decoration for tables and charts. Here the world is a BOARD: one hub slide holds five windows (the platform pages).
The camera zooms into the first window, PANS between the neighbouring windows at the same zoom (previous/next page are
simply the neighbours on the board, no frames), then zooms back out to the hub, which is redrawn with every card ticked.
Same `!!` names on both hub slides, so Morph continues the same objects.

STATUS: SPIKE/PREVIEW sample, not the final deck. Layers A and B only; PowerPoint playback is NOT RUN.
Figures come from the user's document (snapshot 2026-11-03) and were not re-verified against vendors.
Usage: python scripts/build_board_tour_sample.py [--output ...] [--hold 8000] [--font-sans ...]
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
import ai_subscriptions_data as D  # noqa: E402
import build_ai_subscriptions_deck as bd  # noqa: E402
import deck_kit as K  # noqa: E402
import pptx_morph_patch  # noqa: E402
from deck_kit import GOOD, INK, LINE, MUTED, SUB, WALL, WHITE, T, base, hbar, para_list  # noqa: E402
from pptx_world import EMU, H, W, World  # noqa: E402

N = 7
WIN_W = 3.6  # hub window width: the zoom ratio is W / WIN_W = 3.7x
COLS, ROWS = (0.9, 4.95, 9.0), (2.2, 4.7)
# tour order = snake over the board: three across the top row, down on the right, then back left
SLOTS = [(COLS[0], ROWS[0]), (COLS[1], ROWS[0]), (COLS[2], ROWS[0]), (COLS[2], ROWS[1]), (COLS[1], ROWS[1])]
LABELS = ["Claude／ChatGPT", "Cursor", "Antigravity／OpenCode", "Kimi", "DeepSeek"]
COLORS = [bd.PLAT["Claude"], bd.PLAT["Cursor"], bd.PLAT["Antigravity"], bd.PLAT["Kimi"], bd.PLAT["DeepSeek"]]
WIN_H = WIN_W * H / W


def hub(done):
    """The board. `done` = every card visited (the second hub slide); names are identical so Morph keeps the objects."""
    def draw(c):
        base(c, "BOARD TOUR · 樣片", "七個平台，一張地圖", tint=WALL)
        for i, ((x, y), label, color) in enumerate(zip(SLOTS, LABELS, COLORS)):
            c.rect(f"wf{i}", x - .05, y - .05, WIN_W + .1, WIN_H + .1, None, line=(GOOD if done else INK, 2.0 if done else 1.5))
            T(c, f"wl{i}", label, x, y - .42, WIN_W - .5, 0.36, 16, color, bold=True)
            T(c, f"wk{i}", "✓" if done else str(i + 1), x + WIN_W - .45, y - .42, 0.5, 0.36, 16,
              GOOD if done else MUTED, bold=True, align=PP_ALIGN.RIGHT)
        x, y = COLS[0], ROWS[1]
        c.card("legend", x, y, WIN_W, WIN_H, WHITE, border=LINE, shadow=False)
        T(c, "legend_t", "五張卡片＝七個平台" if not done else "七個平台都走過了", x + .25, y + .2, WIN_W - .5, 0.5, 18, INK, bold=True)
        T(c, "legend_b", "鏡頭依序走過每一張卡片，上一頁與下一頁就是相鄰的卡片；最後回到這張地圖。" if not done
          else "回到地圖：每張卡片都看過了。接著可以放大下一個主題。", x + .25, y + .8, WIN_W - .5, 1.1, 15, SUB)
    return draw


def cursor_child():
    """Cursor page re-laid for board mode: no hung frame, so the chart can use the full width."""
    def draw(c):
        base(c, bd.KICKERS[6], "Cursor：週池倍率")
        for n, (tier, price, mult) in enumerate(D.CURSOR_MULTIPLIERS):
            y = 1.95 + n * 0.62
            T(c, f"cm{n}", f"{tier} ${price}", 0.9, y, 2.3, 0.45, 18, bd.PLAT["Cursor"], bold=True)
            hbar(c, f"cmb{n}", 3.3, y + .04, 7.0, 0.38, mult, 50, bd.PLAT["Cursor"])
            T(c, f"cmv{n}", f"{mult}×", 10.5, y, 1.2, 0.45, 18, INK, bold=True)
        items = [("", "第一方模型週池，由 Cursor Agent／CLI、Cloud Agents、Grok Bot、Grok Chat／Voice／Imagine 共用"),
                 ("", "第三方模型：Plus 不支援；Premium 起另購預付 credit，按 API list price"),
                 ("", "舊制 Pro／Pro+／Ultra：兩個月池（Cursor Models／Other Models）；切換新制可選但永久")]
        T(c, "cnotes", para_list(items), 0.9, 4.65, 11.7, 2.0, 16, SUB, after=6)
    return draw


TALK = ["地圖：七個平台、五個詳細頁。", "Claude 與 ChatGPT／Codex 的方案與官方估計。", "Cursor 新制週池倍率。",
        "Antigravity 與 OpenCode Go 的規則。", "Kimi 新制：Plus 起才有 Kimi Code。", "DeepSeek 公開單價與峰離峰。",
        "回到地圖：五張卡片都看過了。"]


def build(output, hold=8000, duration=1500, fonts=None):
    if fonts:
        K.set_fonts(*fonts)
    K.DECOR = False  # board mode: no hung frames / reserved windows on the panels
    try:
        world = World(gap=0.6)
        world.first(hub(False))
        children = [bd.p06(), cursor_child(), bd.p08(), bd.p09(), bd.p10()]
        for (x, y), draw in zip(SLOTS, children):
            world.add(draw, "nest", window=(x, y, WIN_W), parent=0)
        world.add(hub(True), "zoom_out", to=0)

        def hud(c, j):
            for n in range(N):
                c.rect(f"pip{n}", 0.9 + n * 0.3, 0.3, 0.24, 0.04, K.COPPER if n == j else "CFCABB")
            T(c, "foot", "樣片 · 資料快照 2026-11-03（v5.1）· 取自提供文件，未重新核對", 4.6, 6.84, 8.0, 0.26, 14, MUTED,
              align=PP_ALIGN.RIGHT)

        def notes(j):
            return (f"{TALK[j]}\n\n本頁為「地圖巡覽」轉場樣片（SPIKE/PREVIEW）；資料取自使用者文件 v5.1（快照 2026-11-03），未重新核對。"
                    "\nPowerPoint 原生 Morph 實播狀態：NOT RUN。")

        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
        readable = world.build(prs, hud=hud, notes=notes)
    finally:
        K.DECOR = True
    with tempfile.TemporaryDirectory() as d:
        draft = Path(d) / "draft.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, output, duration, hold, dedupe=True)
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable, ensure_ascii=False, indent=1), encoding="utf-8")
    return world


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, default=Path("build/ai-subscriptions/board-tour-sample.pptx"))
    ap.add_argument("--hold", type=int, default=8000)
    ap.add_argument("--duration", type=int, default=1500)
    ap.add_argument("--font-sans", default=K.FONTS["sans"])
    ap.add_argument("--font-serif", default=K.FONTS["serif"])
    ap.add_argument("--font-mono", default=K.FONTS["mono"])
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world = build(args.output, args.hold, args.duration, (args.font_sans, args.font_serif, args.font_mono))
    print(f"{args.output}: {N} slides, {N - 1} native Morph transitions (SPIKE; PowerPoint playback NOT RUN)")
    print("zoom ratios:", sorted({round(z, 2) for _, _, _, z in world.describe()}))


if __name__ == "__main__":
    main()
