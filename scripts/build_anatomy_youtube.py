#!/usr/bin/env python3
"""Anatomy YouTube cut: ~43 landscape (16:9) slides, main text >= 30 pt, official upstream imagery, a morphing chapter
navigation (ring menu -> left rail that stays and re-lights per chapter) and per-slide hold times from the narration.

Follows the user's Google Doc "Anatomy 科普影片｜旁白與分鏡 v2（官方展示版）" (scripts/anatomy_script.py): a third-party
introduction narrated as "官方展示／依 README 說明", no hands-on claims. Imagery is OFFICIAL upstream material
(wheresryan22/anatomy, MIT, (c) 2026 Ryan) prepared by scripts/anatomy_assets.py; nothing is redrawn or altered.

STATUS: SPIKE/PREVIEW. Layers A and B only; desktop PowerPoint playback, video export and phone viewing are NOT RUN.
Usage: python scripts/anatomy_assets.py && python scripts/build_anatomy_youtube.py
"""
import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anatomy_script as S  # noqa: E402
import build_ai_subscriptions_youtube as Y  # noqa: E402  (shared page / rows helpers)
import deck_kit as K  # noqa: E402
import deck_motion as M  # noqa: E402
import pptx_morph_patch  # noqa: E402
from deck_kit import BAD, COPPER, GOOD, INK, MUTED, SUB, WALL, WHITE, T  # noqa: E402
from pptx_world import EMU, H, W, World  # noqa: E402

X0, X1 = 2.9, 12.6  # content area right of the rail
MIN_PT = 30
CREDIT = "圖與資料：wheresryan22/anatomy · MIT © 2026 Ryan"
CX, CY = W / 2, 3.9
DUR_STAY, DUR_PAN = 900, 1300
MONO_BG = "1B2A2A"


class Art:
    def __init__(self, folder):
        self.dir = Path(folder)

    def __call__(self, name):
        path = self.dir / f"{name}.png"
        if not path.is_file():
            raise FileNotFoundError(f"missing official asset {path}; run scripts/anatomy_assets.py first")
        return path


def page(c, headline, x0=X0, x1=X1, tint=K.CARD):
    Y.page(c, headline, tint, x0, x1)


ROW_TOP, ROW_PITCH = 1.8, 1.5  # the grid every row series and picture box is aligned to


def stack_rows(c, headline, rows, hl=None, x0=X0, x1=7.5, top=ROW_TOP, pitch=ROW_PITCH, tint=K.CARD):
    """Rows of (label, colour, detail): one two-line text per row, centred in its cell, so the highlight box, the label and
    the detail always share the same centre line. Same names on every slide of a series."""
    page(c, headline, X0, X1, tint)
    if hl is not None:
        c.rect("hl", x0 - 0.2, top + hl * pitch, x1 - x0 + 0.4, pitch - 0.1, Y.HL_FILL, line=(COPPER, 2.5),
               kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.12)
    for i, (label, color, detail) in enumerate(rows):
        dim = hl is not None and i != hl
        T(c, f"rt{i}", [[(label, {"pt": 34, "bold": True, "color": MUTED if dim else color})],
                        [(detail, {"pt": MIN_PT, "bold": False, "color": MUTED if dim else INK})]],
          x0, top + i * pitch, x1 - x0, pitch - 0.1, MIN_PT, INK, anchor=MSO_ANCHOR.MIDDLE)


# right-hand picture zone, aligned to the row grid: one big card on top, the others as tilted thumbnails underneath
BIG = (7.9, ROW_TOP, 4.7, 3.0)
THUMBS = [(7.9, 5.0, 2.2, 1.3, -4.0), (10.4, 5.0, 2.2, 1.3, 4.0)]


def pic_deck(c, art, names, active):
    """All pictures of a series on every slide under fixed names; the active one is the big card, the rest wait as
    thumbnails. Next slide they swap places, so Morph shuffles the cards (move, resize, rotate) instead of cross-fading."""
    others = [i for i in range(len(names)) if i != active]
    for i, name in enumerate(names):
        if i == active:
            c.picture(f"pic_{name}", art(name), *BIG)
        else:
            x, y, w, h, rot = THUMBS[others.index(i)]
            c.picture(f"pic_{name}", art(name), x, y, w, h, rot=rot)


def series_rows(headline, rows, steps, **kw):
    return [(lambda c, h=h: Y.rows_page(c, headline, rows, h, x0=X0, x1=X1, top=ROW_TOP, pitch=1.15 if len(rows) > 3 else ROW_PITCH,
                                        **kw)) for h in steps]


def series_stack(headline, rows, steps, art=None, pics=None, **kw):
    out = []
    for i, h in enumerate(steps):
        def draw(c, h=h):
            stack_rows(c, headline, rows, h, **kw)
            if pics and len(pics) == 1:
                c.picture(f"pic_{pics[0]}", art(pics[0]), *BIG)
            elif pics:
                pic_deck(c, art, pics, h)
        out.append(draw)
    return out


def hook(art, stage):
    def draw(c):
        Y.page(c, "讓 AI 畫一張會拆開的圖", K.CARD, 1.0, 12.3)
        # a pulse behind the engine: three rings that fan out when it comes apart
        M.draw_ripple(c, "rp", 9.8, 4.1, M.ripple_radii(3, 1.0 if stage else 0.3, 2.6), COPPER, base_alpha=0.1)
        c.picture("pic_hook_" + ("apart" if stage else "firing"), art("fig_raptor_apart" if stage else "fig_raptor_firing"),
                  6.9, 1.6, 5.8, 5.0)
        T(c, "hk_a", "Raptor 2 火箭引擎", 1.0, 2.3, 5.6, 0.7, 34, SUB, bold=True)
        T(c, "hk_b", "拆成 11 組" if stage else "裝好的樣子", 1.0, 3.3, 5.6, 0.9, 40, COPPER, bold=True)
        T(c, "hk_c", "滑鼠移上去就會拆" if stage else "官方範例，不是我們做的", 1.0, 4.5, 5.6, 0.9, MIN_PT, INK)
    return draw


def menu_page(c):
    Y.page(c, "八個章節", WALL, 1.0, 12.3)


SHEET_NAMES = [("sheet_poster", "海報"), ("sheet_drawing", "技術圖"), ("sheet_detailed", "詳解頁")]


def sheets(art, fan):
    """Three A4 sheets: side by side with captions, then dealt into a tilted, overlapping fan (same objects, Morph moves them)."""
    def draw(c):
        page(c, "想印出來，另外說一聲")
        for i, (name, label) in enumerate(SHEET_NAMES):
            if fan:
                box, rot = (X0 + 3.15 + (i - 1) * 2.0, 1.7, 3.4, 4.2), (i - 1) * 9.0
                cap_x = X0 + 3.15 + (i - 1) * 2.0 - 0.1
            else:
                box, rot = (X0 + i * 3.3, 1.7, 3.0, 4.0), 0.0
                cap_x = X0 + i * 3.3
            c.picture(f"pic_{name}", art(name), *box, rot=rot)
            T(c, f"sh{i}", label, cap_x + (0.0 if fan else 0.0), 5.9, 3.0 if not fan else 3.4, 0.5, MIN_PT, INK, bold=True,
              align=PP_ALIGN.CENTER)
        T(c, "sh_note", "亮色、暗色主題都有" if fan else "不會每次自動附贈", X0, 6.5, 9.7, 0.5, MIN_PT, SUB)
    return draw


def raptor(art, stage):
    def draw(c):
        rows = [("11 組零件", COPPER, "滑鼠移上去就拆開"), ("幾何稽核", COPPER, "只驗過這一個範例")]
        stack_rows(c, "Raptor 2 官方範例", rows, None if stage == 0 else 1, x1=7.0)
        # the same poster, small then enlarged to read the part numbers (kept inside the HUD and edge-safe zones)
        box = (9.0, 2.0, 3.6, 4.2) if stage == 0 else (7.2, 0.95, 5.4, 6.3)
        c.picture("pic_poster", art("poster_raptor_figure"), *box)
    return draw


TOOLS = ["claude-code", "antigravity", "opencode", "codex", "minimax-code"]
CHIP_POS = [(X0, 3.95, 3.0), (X0 + 3.25, 3.95, 3.0), (X0 + 6.5, 3.95, 3.2), (X0, 4.95, 2.4), (X0 + 2.65, 4.95, 3.8)]  # x, y, w


def install(stage):
    def draw(c):
        if stage < 2:
            page(c, "安裝")
            # the tool names live behind the command box and slide out of it on the second slide
            for i, (name, (x, y, w)) in enumerate(zip(TOOLS, CHIP_POS)):
                out = stage == 1
                cx, cy, cw, ch = (x, y, w, 0.75) if out else (x, 2.45, w, 0.75)  # folded: same size, hidden inside the command box
                c.rect(f"chip{i}", cx, cy, cw, ch, "FBEBDD", line=(COPPER, 1.5), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.3)
                T(c, f"chip_t{i}", name, cx, cy + (ch - 0.5) / 2, cw, 0.5, MIN_PT, INK, face="mono", bold=True, align=PP_ALIGN.CENTER,
                  track=out)
            c.rect("cmd", X0, 1.9, 9.7, 1.6, MONO_BG, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
            T(c, "cmd_t", ["$ npx skills add", "  wheresryan22/anatomy -g"], X0 + 0.3, 1.9, 9.2, 1.6, MIN_PT, WHITE, face="mono",
              anchor=MSO_ANCHOR.MIDDLE)
            T(c, "cmd_cap", "官方的一行安裝指令" if stage == 0 else "再加 -a，指定要裝給哪個工具",
              X0, 3.95 if stage == 0 else 5.95, 9.7, 0.6, MIN_PT, SUB if stage == 0 else INK)
        elif stage == 2:
            rows = [("Node 20.10 以上", COPPER, "Anatomy 本身的要求"), ("不用 npm install", COPPER, "只用 Node 內建模組"),
                    ("不用另申請金鑰", COPPER, "AI Agent 的帳號要自己備")]
            stack_rows(c, "安裝", rows, None, x1=X1)
        else:
            rows = [("skills CLI 1.7.1", COPPER, "它要 Node 22.20 以上"), ("Chrome", COPPER, "自動檢查要用到"),
                    ("React 18 以上", COPPER, "只有輸出 React 才需要")]
            stack_rows(c, "安裝", rows, None, x1=X1)
    return draw


def closing(art, stage):
    def draw(c):
        page(c, "授權與來源")
        T(c, "lic", "MIT © 2026 Ryan", X0, 1.9, 6.0, 0.9, 40, INK, bold=True)
        T(c, "lic_u", ["github.com/", "wheresryan22/anatomy"], X0, 3.0, 6.0, 1.2, MIN_PT, SUB, face="mono")
        T(c, "lic_n", "第三方科普介紹" if not stage else ["第三方介紹，", "跟作者沒有關係"], X0, 4.6, 6.0, 1.4, 34, COPPER, bold=True)
        c.picture("pic_close", art("fig_raptor_apart"), 9.2, 1.5, 3.4, 5.2)
    return draw


# ------------------------------------------------------------------------------------------------ deck order
def deck(art):
    """[(key, scene, draw, kind)] in slide order; kind = the transition INTO the slide.
    Chapters enter alternately from the right and from below (the camera zig-zags through the world); inside a chapter the
    same panel is redrawn ('stay') and Morph shuffles cards, slides rows and unfolds options."""
    out = []
    enter = {}  # scene -> how the camera arrives

    def add(scene, key, draw, kind=None):
        out.append((key, scene, draw, kind))

    def entry(scene, i):
        if i:
            return "stay"
        enter[scene] = "pan_down" if len(enter) % 2 else "pan_right"
        return enter[scene]

    add("s01", "hook0", hook(art, 0))
    add("s01", "hook1", hook(art, 1), "stay")
    add("s01", "menu", menu_page, "pan_right")  # ring menu in the HUD
    enter["s01"] = "pan_right"
    s2 = [("Claude 技能", COPPER, "也能給另外 4 個工具用"), ("先發明物件", COPPER, "再用它講概念"),
          ("快取鍵", COPPER, "畫成一把彈子鎖"), ("GPU context", COPPER, "畫成龍門繪圖機")]
    for i, d in enumerate(series_rows("Anatomy 是什麼", s2, (0, 1, 2, 3), label_w=3.7)):
        add("s02", f"what{i}", d, entry("s02", i))
    s3 = [("HTML", COPPER, "獨立網頁，直接開"), ("SVG", COPPER, "單一檔，樣式內嵌"), ("React", COPPER, "React／Next.js 元件")]
    for i, d in enumerate(series_rows("三種輸出", s3, (0, 1, 2), label_w=2.6)):
        add("s03", f"out{i}", d, entry("s03", i))
    add("s03", "sheets0", sheets(art, False), "stay")
    add("s03", "sheets1", sheets(art, True), "stay")
    s4 = [("SVG", COPPER, "核心，等角立體零件"), ("SVG + WebGL", COPPER, "火焰、水、燈光"), ("3D", COPPER, "還在 beta，零件會轉")]
    for i, d in enumerate(series_stack("三種圖", s4, (0, 1, 2), art, ["cap_dial_indicator", "cap_ripple_tank", "cap_turning_dial"])):
        add("s04", f"kind{i}", d, entry("s04", i))
    add("s05", "raptor0", raptor(art, 0), entry("s05", 0))
    add("s05", "raptor1", raptor(art, 1), "stay")
    s6 = [("dial-indicator", COPPER, "約 300 行程式"), ("desk-computer", COPPER, "約 85 個實體"),
          ("arcade-cabinet", COPPER, "約 240 個實體")]
    for i, d in enumerate(series_stack("官方範例有多大", s6, (0, 1, 2), art, ["cap_dial_indicator", "cap_desk_computer", "cap_arcade_cabinet"])):
        add("s06", f"ex{i}", d, entry("s06", i))
    for i in range(4):
        add("s07", f"inst{i}", install(i), entry("s07", i))
    s8 = [("下指令", COPPER, "/anatomy，Codex 用 $anatomy"), ("先說", COPPER, "要講的概念，加真實數字"),
          ("再說", COPPER, "哪個零件要動"), ("最後", COPPER, "輸出形式、亮色還是暗色")]
    for i, d in enumerate(series_rows("怎麼用", s8, (0, 1, 2, 3), label_w=2.0)):
        add("s08", f"use{i}", d, entry("s08", i))
    s9 = [("科普影片", COPPER, "要把原理講清楚"), ("技術文章", COPPER, "要說明機構怎麼動"), ("產品說明", COPPER, "東西有零件、有結構")]
    for i, d in enumerate(series_stack("誰用得到（依官方定位整理）", s9, (0, 1, 2), art, ["cap_desk_computer"])):
        add("s09", f"fit{i}", d, entry("s09", i))
    s10 = [("好安裝", GOOD, "一行指令"), ("沒額外依賴", GOOD, "只用 Node 內建模組"), ("檔案能再改", GOOD, "HTML、SVG、React"),
           ("有檢查流程", GOOD, "但還是要自己驗")]
    for i, d in enumerate(series_rows("優點", s10, (0, 1, 2, 3), label_w=3.3)):
        add("s10", f"pro{i}", d, entry("s10", i))
    s11 = [("不是圖表庫", BAD, "沒有座標軸、資料圖"), ("做得慢", BAD, "一張圖要跑一段長流程"), ("特效要 WebGL", BAD, "沒有就只看得到 SVG"),
           ("3D 還是 beta", BAD, "官方壓測約 20 FPS")]
    for i, d in enumerate(series_rows("限制（官方數據，不是我們測的）", s11, (0, 1, 2, 3), label_w=3.6)):
        add("s11", f"con{i}", d, entry("s11", i))
    s12 = [("統計圖表", BAD, "它不是圖表庫"), ("精確地圖", BAD, "也不畫人物"), ("急著要圖", BAD, "流程偏慢，等不及")]
    for i, d in enumerate(series_rows("不適合的情況（依官方限制整理）", s12, (0, 1, 2), label_w=3.3)):
        add("s12", f"not{i}", d, entry("s12", i))
    add("s13", "end0", closing(art, 0), entry("s13", 0))
    add("s13", "end1", closing(art, 1), "stay")
    return out


def slot_ms(slides):
    count = Counter(scene for _, scene, *_ in slides)
    return [S.SCENE_SECONDS[scene] * 1000 / count[scene] for _, scene, *_ in slides]


def durations_ms(slides):
    return [0] + [DUR_STAY if k == "stay" else DUR_PAN for _, _, _, k in slides[1:]]


def holds_ms(slides):
    """Auto-advance time: the slot minus the Morph into the slide (measured additive on a phone, see PPTX-MOTION-KIT.md)."""
    d = durations_ms(slides)
    return [int(slot - d[j]) for j, slot in enumerate(slot_ms(slides))]


def build(output, assets, fonts=None):
    if fonts:
        K.set_fonts(*fonts)
    art = Art(assets)
    slides = deck(art)
    world = World(gap=0.6)
    for key, scene, draw, kind in slides:
        if kind is None:
            world.first(draw)
        else:
            world.add(draw, kind, dur=DUR_STAY if kind == "stay" else DUR_PAN)
    n = len(slides)
    menu_j = next(j for j, (key, *_rest) in enumerate(slides) if key == "menu")
    license_text = (Path(assets) / "LICENSE_ANATOMY.txt").read_text(encoding="utf-8")
    first_of_scene = {}
    for j, (_, scene, *_r) in enumerate(slides):
        first_of_scene.setdefault(scene, j)

    def hud(c, j):
        c.rect("hud_track", 1.0, 0.25, 11.3, 0.05, "D9D4C6")
        c.rect("hud_fill", 1.0, 0.25, 11.3 * (j + 1) / n, 0.05, COPPER)
        T(c, "hud_credit", CREDIT, 6.0, 0.36, 6.5, 0.35, 16, MUTED, align=PP_ALIGN.RIGHT)
        if j == menu_j:
            c.oval("hub", CX, CY, 1.1, COPPER)
            T(c, "hub_t", "章節", CX - 0.8, CY - 0.25, 1.6, 0.5, 30, WHITE, bold=True, align=PP_ALIGN.CENTER)
            M.draw_menu(c, "rm", S.CHAPTERS, M.ring_layout(8, CX, CY, 2.5), None, label_dx=0.6, label_w=1.6)
        elif j > menu_j:
            scene = slides[j][1]
            c.oval("hub", 0.95, 0.85, 0.15, COPPER)
            T(c, "hub_t", "", 0.9, 0.8, 0.1, 0.1, 14, WHITE)
            M.draw_menu(c, "rm", S.CHAPTERS, M.column_layout(8, 0.95, 1.45, 0.72), S.SCENE_CHAPTER[scene], r_idle=0.3,
                        r_active=0.4, label_dx=0.55, pt=20, label_w=1.5)

    def notes(j):
        key, scene = slides[j][0], slides[j][1]
        head = f"[{key}] " + (S.NARRATION[scene] if first_of_scene[scene] == j else "（同一段旁白，延續上一頁）")
        extra = f"\n\n授權：圖像與資料取自 wheresryan22/anatomy（MIT © 2026 Ryan）。\n{license_text}" if j in (0, n - 1) else ""
        return (f"{head}\n\n本頁約 {slot_ms(slides)[j] / 1000:g} 秒（含轉場 {durations_ms(slides)[j] / 1000:g} 秒）。"
                "\n資料：上游 README 固定版本 1482e84；旁白採「官方展示／依 README 說明」，非本片實測。"
                "\nPowerPoint 原生 Morph 桌面版放映與匯出影片：NOT RUN。" + extra)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    readable = world.build(prs, hud=hud, notes=notes, hud_readable=False)
    with tempfile.TemporaryDirectory() as d:
        draft = Path(d) / "draft.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, output, durations_ms(slides)[:1] + world.durations(DUR_PAN)[1:], holds_ms(slides), dedupe=True)
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable, ensure_ascii=False, indent=1), encoding="utf-8")
    return world, slides


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assets", type=Path, default=Path("build/anatomy/assets"))
    ap.add_argument("--output", type=Path, default=Path("build/anatomy/youtube/anatomy-youtube.pptx"))
    ap.add_argument("--font-sans", default=K.FONTS["sans"])
    ap.add_argument("--font-serif", default=K.FONTS["serif"])
    ap.add_argument("--font-mono", default=K.FONTS["mono"])
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world, slides = build(args.output, args.assets, (args.font_sans, args.font_serif, args.font_mono))
    total = (sum(holds_ms(slides)) + sum(durations_ms(slides))) / 1000
    print(f"{args.output}: {len(slides)} slides, {len(slides) - 1} native Morph transitions (~{total:g} s; SPIKE; PowerPoint playback NOT RUN)")


if __name__ == "__main__":
    main()
