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
from pptx.enum.text import PP_ALIGN
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


def stack_rows(c, headline, rows, hl=None, x0=X0, x1=7.5, top=1.8, pitch=1.55, tint=K.CARD):
    """Rows of (label, colour, detail) as a label line over a detail line; same names on every slide of a series."""
    page(c, headline, X0, X1, tint)
    if hl is not None:
        c.rect("hl", x0 - 0.2, top + hl * pitch - 0.1, x1 - x0 + 0.4, pitch - 0.06, Y.HL_FILL, line=(COPPER, 2.5),
               kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.12)
    for i, (label, color, detail) in enumerate(rows):
        dim = hl is not None and i != hl
        y = top + i * pitch
        T(c, f"rl{i}", label, x0, y, x1 - x0, 0.6, 34, MUTED if dim else color, bold=True)
        T(c, f"rd{i}", detail, x0, y + 0.58, x1 - x0, 0.9, MIN_PT, MUTED if dim else INK)


def with_picture(art, name, box):
    def deco(c):
        c.picture(f"pic_{name}", art(name), *box)
    return deco


PIC = (7.9, 1.6, 4.7, 5.0)  # right-hand picture box (landscape slide, rail on the left)


def both(first, second):
    def draw(c):
        first(c)
        second(c)
    return draw


def series_rows(headline, rows, steps, **kw):
    return [(lambda c, h=h: Y.rows_page(c, headline, rows, h, x0=X0, x1=X1, **kw)) for h in steps]


def series_stack(headline, rows, steps, art=None, pics=None, box=PIC, **kw):
    out = []
    for i, h in enumerate(steps):
        def draw(c, h=h, i=i):
            stack_rows(c, headline, rows, h, **kw)
            if pics:
                c.picture(f"pic_{pics[i]}", art(pics[i]), *box)
        out.append(draw)
    return out


def hook(art, stage):
    def draw(c):
        Y.page(c, "讓 AI 畫一張會拆開的圖", K.CARD, 1.0, 12.3)
        c.picture("pic_hook_" + ("apart" if stage else "firing"), art("fig_raptor_apart" if stage else "fig_raptor_firing"),
                  6.9, 1.6, 5.8, 5.0)
        T(c, "hk_a", "官方 Raptor 2 範例", 1.0, 2.3, 5.6, 0.7, 34, SUB, bold=True)
        T(c, "hk_b", "拆成 11 組總成" if stage else "完整狀態", 1.0, 3.3, 5.6, 0.9, 40, COPPER, bold=True)
        T(c, "hk_c", "官方靜態圖前後對照" if stage else "開源專案提供的範例", 1.0, 4.5, 5.6, 0.9, MIN_PT, INK)
    return draw


def menu_page(c):
    Y.page(c, "八個章節", WALL, 1.0, 12.3)


def sheets(art):
    def draw(c):
        page(c, "另可要求 A4 列印版")
        for i, (name, label) in enumerate([("sheet_poster", "海報"), ("sheet_drawing", "技術圖"), ("sheet_detailed", "詳解頁")]):
            x = X0 + i * 3.3
            c.picture(f"pic_{name}", art(name), x, 1.75, 3.0, 4.0)
            T(c, f"sh{i}", label, x, 5.85, 3.0, 0.55, MIN_PT, INK, bold=True, align=PP_ALIGN.CENTER)
        T(c, "sh_note", "亮色與暗色主題都有", X0, 6.4, 9.7, 0.5, MIN_PT, SUB)
    return draw


def raptor(art, stage):
    def draw(c):
        rows = [("11 組總成", COPPER, "懸停即拆開"), ("幾何稽核", COPPER, "僅針對此範例")]
        stack_rows(c, "Raptor 2 官方範例", rows, None if stage == 0 else 1, x1=7.0)
        box = (7.6, 1.5, 4.9, 5.3) if stage == 0 else (7.0, -0.2, 7.0, 8.2)  # the same poster, enlarged to its part numbers
        c.picture("pic_poster", art("poster_raptor_figure"), *box)
    return draw


def install(stage):
    def draw(c):
        if stage < 2:
            page(c, "安裝")
            c.rect("cmd", X0, 1.9, 9.7, 1.6, MONO_BG, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
            T(c, "cmd_t", ["$ npx skills add", "  wheresryan22/anatomy -g"], X0 + 0.3, 2.15, 9.2, 1.2, MIN_PT, WHITE, face="mono")
            T(c, "cmd_cap", "官方一行安裝" if stage == 0 else ["加 -a 指定工具：claude-code、antigravity、", "opencode、codex、minimax-code"],
              X0, 3.9, 9.7, 1.6, MIN_PT, SUB if stage == 0 else INK)
        elif stage == 2:
            rows = [("Node.js 20.10+", COPPER, "Anatomy 本身最低需求"), ("不需 npm install", COPPER, "只用 Node 內建模組"),
                    ("不需工具專用金鑰", COPPER, "Agent 帳號另算")]
            stack_rows(c, "安裝", rows, None, x1=X1)
        else:
            rows = [("skills CLI 1.7.1", COPPER, "要求 Node 22.20 以上"), ("Chrome／Chromium", COPPER, "自動檢查用"),
                    ("React 18+", COPPER, "僅 React 輸出需要")]
            stack_rows(c, "安裝", rows, None, x1=X1)
    return draw


def closing(art, stage):
    def draw(c):
        page(c, "授權與來源")
        T(c, "lic", "MIT © 2026 Ryan", X0, 1.9, 6.0, 0.9, 40, INK, bold=True)
        T(c, "lic_u", ["github.com/", "wheresryan22/anatomy"], X0, 3.0, 6.0, 1.2, MIN_PT, SUB, face="mono")
        T(c, "lic_n", "第三方科普介紹" if not stage else ["第三方科普介紹，", "與作者無關聯"], X0, 4.6, 6.0, 1.4, 34, COPPER, bold=True)
        c.picture("pic_close", art("fig_raptor_apart"), 9.2, 1.5, 3.4, 5.2)
    return draw


# ------------------------------------------------------------------------------------------------ deck order
def deck(art):
    """[(key, scene, draw, kind)] in slide order; kind = the transition INTO the slide."""
    out = []

    def add(scene, key, draw, kind=None):
        out.append((key, scene, draw, kind))

    add("s01", "hook0", hook(art, 0))
    add("s01", "hook1", hook(art, 1), "stay")
    add("s01", "menu", menu_page, "pan_right")  # ring menu in the HUD
    s2 = [("Agent 技能", COPPER, "Claude 技能，另可用於 4 個其他工具"), ("發明物件", COPPER, "用一個實體物件解釋概念"),
          ("例子", COPPER, "快取鍵→彈子鎖；GPU context→龍門繪圖機")]
    for i, d in enumerate(series_rows("Anatomy 是什麼", s2, (None, 0, 1, 2), label_w=2.9)):
        add("s02", f"what{i}", d, "pan_right" if i == 0 else "stay")
    s3 = [("HTML", COPPER, "獨立網頁"), ("單一 SVG", COPPER, "樣式內嵌的一個檔"), ("React", COPPER, "React／Next.js 元件")]
    for i, d in enumerate(series_rows("輸出形式", s3, (0, 1, 2), label_w=3.4)):
        add("s03", f"out{i}", d, "pan_right" if i == 0 else "stay")
    add("s03", "sheets", sheets(art), "pan_right")
    s4 = [("SVG", COPPER, "核心；等角立體零件"), ("SVG＋WebGL", COPPER, "火焰、水、燈光、蒸氣"), ("3D（beta）", COPPER, "零件真的會轉動")]
    for i, d in enumerate(series_stack("三種圖", s4, (0, 1, 2), art, ["cap_dial_indicator", "cap_ripple_tank", "cap_turning_dial"])):
        add("s04", f"kind{i}", d, "pan_right" if i == 0 else "stay")
    add("s05", "raptor0", raptor(art, 0), "pan_right")
    add("s05", "raptor1", raptor(art, 1), "stay")
    s6 = [("dial-indicator", COPPER, "約 300 行"), ("desk-computer", COPPER, "約 85 個實體"),
          ("arcade-cabinet", COPPER, "約 240 實體、15 線纜")]
    for i, d in enumerate(series_stack("官方範例的規模", s6, (0, 1, 2), art, ["cap_dial_indicator", "cap_desk_computer", "cap_arcade_cabinet"])):
        add("s06", f"ex{i}", d, "pan_right" if i == 0 else "stay")
    for i in range(4):
        add("s07", f"inst{i}", install(i), "pan_right" if i == 0 else "stay")
    s8 = [("指令", COPPER, "/anatomy　Codex：$anatomy"), ("習慣一", COPPER, "說概念，給真實數字"),
          ("習慣二", COPPER, "或說物件與會動的部分"), ("習慣三", COPPER, "指定輸出形式與亮暗")]
    for i, d in enumerate(series_rows("使用", s8, (0, 1, 2, 3), label_w=2.2)):
        add("s08", f"use{i}", d, "pan_right" if i == 0 else "stay")
    s9 = [("科普與教學", COPPER, "把原理講清楚"), ("技術文章", COPPER, "需要說明機構"), ("產品說明", COPPER, "主題有零件、有結構")]
    for i, d in enumerate(series_stack("適合誰（依官方定位整理）", s9, (0, 1, 2), art, ["cap_desk_computer"] * 3)):
        add("s09", f"fit{i}", d, "pan_right" if i == 0 else "stay")
    s10 = [("安裝簡單", GOOD, "一行指令"), ("免額外依賴", GOOD, "Node 內建模組"), ("輸出可編輯", GOOD, "HTML、SVG、React"),
           ("有稽核流程", GOOD, "仍需自己驗證")]
    for i, d in enumerate(series_rows("優點", s10, (0, 1, 2, 3), label_w=3.3)):
        add("s10", f"pro{i}", d, "pan_right" if i == 0 else "stay")
    s11 = [("非圖表庫", BAD, "沒有座標軸與資料圖"), ("刻意較慢", BAD, "一張圖要一段長流程"), ("WebGL 特效", BAD, "缺少時 SVG 仍可讀"),
           ("3D 仍是 beta", BAD, "官方壓測約 20 FPS")]
    for i, d in enumerate(series_rows("限制（官方數據，非本片實測）", s11, (0, 1, 2, 3), label_w=3.3)):
        add("s11", f"con{i}", d, "pan_right" if i == 0 else "stay")
    s12 = [("統計圖表", BAD, "它不是圖表庫"), ("精確地圖", BAD, "或人物插畫"), ("要立即出圖", BAD, "製作流程偏慢")]
    for i, d in enumerate(series_rows("不適合誰（依官方限制整理）", s12, (0, 1, 2), label_w=3.3)):
        add("s12", f"not{i}", d, "pan_right" if i == 0 else "stay")
    add("s13", "end0", closing(art, 0), "pan_right")
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
