#!/usr/bin/env python3
"""Anatomy explainer deck: a formal, editable 13-slide science/tech-explainer PPT with seamless Morph transitions.

Audience: viewers of a YouTube video that explains what Anatomy is, what it can do, how to install and use it,
who it suits, its strengths and limits, and who should skip it. Imagery is OFFICIAL upstream material
(wheresryan22/anatomy, MIT, (c) 2026 Ryan) prepared by scripts/anatomy_assets.py; nothing is redrawn.
Facts are taken from the upstream README at the pinned commit and still need human review before publishing.

Transitions (one continuous world, see scripts/pptx_world.py):
 1>2 zoom-through, 2>3 pull-back reveal, 3>4 pan, 4>5 pan, 5>6 zoom-through, 6>7 pull-back reveal,
 7>8 pan, 8>9 pan, 9>10 zoom-through, 10>11 pull-back reveal, 11>12 pan, 12>13 pan down.
 (A zoom-through is always followed by a pull-back: a pan right after it would land inside the parent page.)

STATUS: SPIKE/PREVIEW. Layers A and B only; Microsoft PowerPoint playback and video export are NOT RUN.
Usage: python scripts/anatomy_assets.py && python scripts/build_anatomy_explainer.py
Requires: python-pptx, Pillow
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pptx_morph_patch  # noqa: E402
from pptx_world import EMU, H, W, World  # noqa: E402

FONTS = {"sans": "Noto Sans CJK TC", "serif": "Noto Serif CJK TC", "mono": "DejaVu Sans Mono"}
SANS, SERIF, MONO = FONTS["sans"], FONTS["serif"], FONTS["mono"]  # rebound by set_fonts() before drawing
PAPER, CARD, WALL = "F1EFE7", "FBFAF6", "E9E5D8"
INK, SUB, MUTED = "182B2C", "394B4B", "6B7775"
COPPER, LINE = "C35F3F", "D5D0C2"
GOOD, BAD = "2E7D5B", "B3402A"
DARK, DARKTXT, DARKSUB = "1B2A2A", "F1EFE7", "A9B5B2"
HOLD_MS, MORPH_MS = 8000, 1500
WIN_W = 3.9
FRAME = (0.9, 2.1, WIN_W)
N = 13

KICKERS = ["ANATOMY · AGENT SKILL", "01 / 它是什麼", "02 / 輸出形式", "03 / 三種圖", "04 / 功能", "05 / 官方範例",
           "06 / 安裝", "07 / 使用", "08 / 適合誰", "09 / 優點", "10 / 缺點與限制", "11 / 不適合誰", "12 / 一句話"]
CREDIT = "圖與資料：wheresryan22/anatomy · MIT © 2026 Ryan"


class Art:
    """Resolved official-asset paths."""

    def __init__(self, folder):
        self.dir = Path(folder)

    def __call__(self, name):
        path = self.dir / f"{name}.png"
        if not path.is_file():
            raise FileNotFoundError(f"missing official asset {path}; run scripts/anatomy_assets.py first")
        return path


def set_fonts(sans, serif, mono):
    """Fonts must exist on the machine that plays the deck; override here (see docs/PPTX-ANATOMY-EXPLAINER.md)."""
    global SANS, SERIF, MONO
    SANS, SERIF, MONO = sans, serif, mono


def T(c, name, paras, x, y, w, h, pt, color=INK, face=None, **kw):
    face = {None: SANS, "serif": SERIF, "mono": MONO}.get(face, face)
    return c.text(name, paras, x, y, w, h, pt, color, face, SANS, **kw)


def base(c, i, headline, tint=CARD, hint=None):
    c.card("card", 0, 0, W, H, tint, shadow=True)
    T(c, "kicker", KICKERS[i], 0.9, 0.62, 5.5, 0.3, 14, COPPER, face="mono", bold=True)
    if hint:
        T(c, "hint", hint, 6.3, 0.62, 6.3, 0.3, 14, MUTED, align=PP_ALIGN.RIGHT)
    if headline:
        T(c, "headline", headline, 0.9, 0.98, 11.7, 0.8, 40, INK, bold=True)


def window(c, wx, wy, ww=WIN_W):
    """The reserved box where the next panel appears as a miniature (frame drawn on the previous panel)."""
    wh = ww * H / W
    c.rect("win_sh", wx - .02, wy + .05, ww + .24, wh + .24, "000000", alpha=.12)
    c.rect("win", wx - .12, wy - .12, ww + .24, wh + .24, "FFFFFF", line=(INK, 1.5))


def frame(c, fx, fy, fw, tint="FFFFFF"):
    """A picture frame on the wall that will hold the previous panel."""
    fh = fw * H / W
    c.rect("frm_sh", fx - .1, fy - .05, fw + .5, fh + .5, "000000", alpha=.16)
    c.rect("frm", fx - .22, fy - .22, fw + .44, fh + .44, tint, line=(INK, 2.5))


# ------------------------------------------------------------------------------------------ panels
def para_list(items, mark="•", mark_color=COPPER):
    """[(lead, body)] -> paragraphs with a coloured bullet, bold lead and normal body."""
    return [[(f"{mark} ", {"color": mark_color, "bold": True}), (lead, {"bold": True}), (body, {"color": SUB})] for lead, body in items]


def p01(art):
    def draw(c):
        base(c, 0, None)
        c.picture("hero", art("fig_raptor_firing"), 7.3, 0.95, 5.36, 5.6)
        T(c, "hero_cap", "官方範例 · Raptor 2 引擎（SVG 零件 + WebGL 羽流）", 7.3, 6.5, 5.36, 0.3, 14, MUTED, align=PP_ALIGN.CENTER)
        T(c, "title", "Anatomy", 0.85, 0.95, 6.4, 1.4, 96, INK, face="serif", bold=True)
        T(c, "subtitle", ["讓 AI 把一個概念，", "做成一台會動的機器"], 0.9, 2.45, 6.3, 1.15, 32, INK, bold=True)
        T(c, "desc", ["Claude Code 技能（Agent Skill）。", "也支援 Antigravity、OpenCode、Codex、MiniMax Code。"],
          0.9, 3.7, 6.35, 0.95, 16, SUB, after=2)
        window(c, 0.9, 4.8)
    return draw


def p02(art):
    def draw(c):
        base(c, 1, "用「發明一個物件」來解釋概念")
        T(c, "lead", "你說想解釋什麼，Claude 就設計一個實體物件，讓它的運作本身就是那個概念。", 0.9, 2.0, 6.5, 1.15, 24, INK)
        for n, (head, sub) in enumerate([("快取鍵 → 彈子鎖", "沒變就跳過工作：每根銷都對上，鎖才會轉動。"),
                                          ("GPU context → 龍門繪圖機", "一個 context 服務多個 canvas：單一印頭走訪 16 個井。")]):
            y = 3.4 + n * 1.6
            c.card(f"ex{n}", 0.9, y, 6.5, 1.45, "FFFFFF", border=LINE, shadow=False)
            T(c, f"ex{n}h", head, 1.15, y + 0.16, 6.0, 0.45, 22, COPPER, bold=True)
            T(c, f"ex{n}b", sub, 1.15, y + 0.7, 6.0, 0.7, 18, SUB)
        c.picture("fig", art("fig_raptor_apart"), 7.85, 1.7, 4.8, 4.75)
        T(c, "fig_cap", "官方範例：滑過 Raptor 2，就拆成 11 個組件", 7.5, 6.45, 5.1, 0.3, 14, MUTED, align=PP_ALIGN.CENTER)
    return draw


def p03(art):
    sheets = [("sheet_poster", "一頁海報"), ("sheet_drawing", "一頁技術圖"), ("sheet_detailed", "詳解頁")]

    def draw(c):
        base(c, 2, "能做出什麼？", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛說的「它是什麼」，只是其中一頁。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        T(c, "sheet_hint", "官方可列印 A4（Raptor 2）", 6.2, 1.62, 6.4, 0.3, 14, MUTED)
        for n, (asset, label) in enumerate(sheets):
            x = 6.2 + n * 2.2
            c.rect(f"sheet{n}_sh", x + .05, 2.05, 1.77, 2.5, "000000", alpha=.18)
            c.picture(f"sheet{n}", art(asset), x, 2.0, 1.77, 2.5)
            T(c, f"sheet{n}_cap", label, x - .2, 4.62, 2.17, 0.3, 14, SUB, align=PP_ALIGN.CENTER)
        items = [("輸出形式：", "獨立 HTML 頁面、單一 .svg 檔（樣式內嵌）、React／Next.js 元件。"),
                 ("主題與列印：", "亮、暗兩種主題；Raptor 與街機另可列印成 A4（海報、技術圖、詳解）。"),
                 ("你拿到的是原始碼：", "Node 建置腳本與它產生的頁面；React 則是幾何模組與元件。")]
        T(c, "out", para_list(items), 0.9, 5.15, 11.7, 1.6, 20, INK, after=6)
    return draw


def p04(art):
    cols = [("cap_dial_indicator", "SVG", "核心。實心等角零件、四階明暗、由後往前繪製，附即時讀數與緩動。"),
            ("cap_ripple_tank", "SVG + WebGL", "火焰、排氣、水、焦散、燈光：shader 在同一個等角相機裡；沒有 WebGL 時 SVG 仍可閱讀。"),
            ("cap_turning_dial", "3D（beta）", "零件以真 3D 轉動（轉盤、手指彎曲、零件斷裂落下），其餘仍是靜態圖。")]

    def draw(c):
        base(c, 3, "三種圖，共用一套工具")
        for n, (asset, label, desc) in enumerate(cols):
            x = 0.9 + n * 3.95
            c.picture(f"img{n}", art(asset), x, 1.95, 3.7, 2.95)
            T(c, f"lab{n}", label, x, 5.0, 3.7, 0.42, 24, COPPER, bold=True)
            T(c, f"dsc{n}", desc, x, 5.5, 3.7, 1.2, 16, SUB)
    return draw


def p05(art):
    def draw(c):
        base(c, 4, "不只好看：能互動、能驗證")
        items = [("會動：", "滑過 Raptor 引擎，拆成 11 個組件；指標與鍵盤都能操作。"),
                 ("有讀數：", "圖上每個數字，都來自驅動零件的同一個小模型。"),
                 ("自我驗證：", "幾何稽核證明沒有管線穿過任何東西；Claude 逐接頭特寫、逐張檢查截圖。"),
                 ("可及性：", "偏好減少動態時圖會靜止；沒有 WebGL 時 SVG 仍可閱讀。")]
        T(c, "feat", para_list(items), 0.9, 1.95, 6.9, 2.65, 18, INK, after=7)
        c.picture("poster", art("poster_raptor_figure"), 8.4, 1.5, 3.0, 4.75)
        T(c, "poster_cap", "官方 A4 海報的零件編號圖（Raptor 2）", 7.6, 6.3, 4.6, 0.3, 14, MUTED, align=PP_ALIGN.CENTER)
        window(c, 0.9, 4.75)
    return draw


def p06(art):
    tiles = [("cap_dial_indicator", "dial-indicator", "最小範例，約 300 行"),
             ("cap_desk_computer", "desk-computer", "1984 風格桌上電腦，可打字"),
             ("cap_arcade_cabinet", "arcade-cabinet", "投幣街機，約 240 個實體"),
             ("fig_raptor_firing", "raptor-engine", "拆成 11 個組件 + WebGL 羽流"),
             ("cap_ripple_tank", "ripple-tank", "漣漪槽，兩層 WebGL"),
             ("cap_turning_dial", "turning-dial", "3D 模式（beta）")]

    def draw(c):
        base(c, 5, "官方範例一覽", hint="共 8 個範例；另有 test-rig、spot-plate（React 站內圖）")
        for n, (asset, name, desc) in enumerate(tiles):
            x, y = 0.9 + (n % 3) * 3.95, 1.75 + (n // 3) * 2.45
            c.card(f"t{n}", x, y, 3.75, 2.3, "FFFFFF", border=LINE, shadow=False)
            c.picture(f"t{n}img", art(asset), x + .1, y + .06, 3.55, 1.5)
            T(c, f"t{n}name", name, x + .2, y + 1.6, 3.4, 0.3, 16, INK, face="mono", bold=True)
            T(c, f"t{n}desc", desc, x + .2, y + 1.93, 3.4, 0.3, 14, SUB)
    return draw


def p07(art):
    reqs = [("Node.js 20.10+", "只用內建模組：不用 npm install，也不需要 API 金鑰。"),
            ("Chrome / Chromium", "技能自我檢查（截圖、特寫）時使用。"),
            ("React 18+", "只有要輸出 React／Next.js 元件時才需要。")]

    def draw(c):
        base(c, 6, "一行指令安裝", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", ["剛剛的「官方範例」。", "也可 git clone 或下載 ZIP，放進各代理的 skills 資料夾。",
                           "安裝用的 skills CLI 本身可能要求較新的 Node（官方註明 1.7.1 版需要 22.20 以上）。"],
          0.9, 4.75, 4.4, 1.95, 14, SUB, after=4)
        c.rect("code", 5.6, 1.85, 7.07, 1.6, DARK, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.06)
        T(c, "cmd", "$ npx skills add wheresryan22/anatomy -g", 5.85, 2.02, 6.65, 0.5, 18, DARKTXT, face="mono")
        T(c, "cmd2", ["-a claude-code | antigravity | opencode", "-a codex | minimax-code"], 5.85, 2.65, 6.65, 0.7, 14, DARKSUB, face="mono")
        for n, (head, body) in enumerate(reqs):
            y = 3.75 + n * 1.0
            c.rect(f"req{n}bar", 5.6, y, 0.07, 0.8, COPPER)
            T(c, f"req{n}h", head, 5.85, y, 6.7, 0.4, 20, INK, bold=True)
            T(c, f"req{n}b", body, 5.85, y + .42, 6.7, 0.4, 16, SUB)
    return draw


def p08(art):
    habits = [("① 說觀念，不說畫法", "講要解釋什麼，並給真實數字（尺寸、數量、速率、門檻）。"),
              ("② 或直接點名物件", "例如濃縮咖啡機、本生燈、鎖，並說明哪裡該動。"),
              ("③ 說清楚放哪", "獨立 HTML、單一 SVG 或 React／Next.js 元件；亮或暗。")]

    def draw(c):
        base(c, 7, "怎麼用？")
        c.rect("code", 0.9, 1.85, 11.77, 1.6, DARK, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.06)
        T(c, "cmd", ["/anatomy explain how a token bucket rate limiter works,", "interactive"], 1.2, 2.0, 11.2, 0.9, 22, DARKTXT, face="mono")
        T(c, "cmd2", "Codex 請改用 $anatomy；Antigravity、OpenCode、MiniMax Code 用 /anatomy。", 1.2, 2.95, 11.2, 0.35, 16, DARKSUB)
        for n, (head, body) in enumerate(habits):
            x = 0.9 + n * 3.97
            c.card(f"hab{n}", x, 3.75, 3.8, 2.2, "FFFFFF", border=LINE, shadow=False)
            T(c, f"hab{n}h", head, x + .22, 3.93, 3.4, 0.4, 20, COPPER, bold=True)
            T(c, f"hab{n}b", body, x + .22, 4.5, 3.4, 1.3, 17, SUB)
        T(c, "auto", "不必打指令也行：要求等角插圖、文件配圖或互動解說時，Claude 也會自動載入。", 0.9, 6.15, 11.7, 0.5, 18, MUTED)
    return draw


def p09(art):
    rows = [("技術文件、部落格、Landing page 作者", "需要精緻、可互動的等角說明圖，而不是範本圖庫。"),
            ("講師、DevRel、教學影片製作者", "想用一台機器的運作，解釋抽象概念：快取、連線池、限流。"),
            ("已在用支援代理的開發者", "Claude Code、Antigravity、OpenCode、Codex、MiniMax Code，一行指令就能接上。")]

    def draw(c):
        base(c, 8, "適合這些人", hint="依官方定位與用法整理")
        for n, (head, body) in enumerate(rows):
            y = 1.9 + n * 1.62
            c.card(f"aud{n}", 0.9, y, 7.2, 1.45, "FFFFFF", border=LINE, shadow=False)
            c.rect(f"aud{n}bar", 0.9, y, 0.08, 1.45, GOOD)
            T(c, f"aud{n}h", head, 1.2, y + .13, 6.7, 0.42, 22, INK, bold=True)
            T(c, f"aud{n}b", body, 1.2, y + .65, 6.7, 0.75, 16, SUB)
        c.picture("fig", art("cap_desk_computer"), 8.6, 1.7, 4.0, 2.5)
        window(c, 8.7, 4.4)
    return draw


def p10(art):
    rows = [("零相依", "只用 Node 內建模組；不用 npm install，也不需要 API 金鑰。"),
            ("原始碼歸你", "交付 Node 建置腳本與它產生的頁面；React 則是幾何模組與元件。"),
            ("會自己檢查", "幾何稽核、逐接頭特寫與截圖；技能要求 Claude 逐張檢視。"),
            ("輸出彈性", "HTML、單檔 SVG、React；亮暗主題；可列印 A4。"),
            ("優雅降級", "沒有 WebGL 時 SVG 仍可閱讀；偏好減少動態時圖會靜止。"),
            ("跨代理、MIT", "開放的 Agent Skills 格式；MIT 授權。")]

    def draw(c):
        base(c, 9, "優點")
        for n, (head, body) in enumerate(rows):
            x, y = 0.9 + (n % 2) * 6.0, 1.85 + (n // 2) * 1.62
            c.card(f"pro{n}", x, y, 5.7, 1.45, "FFFFFF", border=LINE, shadow=False)
            c.rect(f"pro{n}bar", x, y, 0.08, 1.45, GOOD)
            T(c, f"pro{n}m", "✓", x + .25, y + .12, 0.5, 0.5, 26, GOOD, bold=True)
            T(c, f"pro{n}h", head, x + .8, y + .13, 4.7, 0.42, 22, INK, bold=True)
            T(c, f"pro{n}b", body, x + .8, y + .62, 4.7, 0.8, 16, SUB)
    return draw


def p11(art):
    rows = [("不是圖表庫", "沒有座標軸或資料系列；數字用即時讀數。"),
            ("只畫機器與器物", "不畫人物或精確地圖；沒機構可建的概念較弱。"),
            ("刻意很慢", "Raptor 建置數分鐘；3D 全稽核約 15–20 分鐘。"),
            ("Shader 需要 WebGL", "沒有 WebGL 時，只剩 SVG 本體。"),
            ("3D 模式是 beta", "380 零件壓測約 20 fps；節流手機約 13–15 fps。"),
            ("Codex 沙盒", "可能擋住無頭 Chrome；圖仍會建出，檢查失敗。")]

    def draw(c):
        base(c, 10, "缺點與限制", tint=WALL, hint="官方 README「Limits」與 3D beta 說明")
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛的「優點」，也有代價。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        for n, (head, body) in enumerate(rows):
            y = 1.7 + n * 0.82
            c.rect(f"con{n}bar", 5.6, y + .02, 0.07, 0.68, BAD)
            T(c, f"con{n}h", head, 5.85, y, 6.8, 0.4, 20, INK, bold=True)
            T(c, f"con{n}b", body, 5.85, y + .38, 6.8, 0.35, 16, SUB)
    return draw


def p12(art):
    rows = [("需要資料圖表", "折線、長條、儀表板：請用圖表庫。"),
            ("需要人物插畫或精確地圖", "它畫的是機器與器物。"),
            ("想幾分鐘就出一張靜態圖", "一張圖是一整段長工作。"),
            ("沒有支援的代理或 Node 環境", "需要 Claude Code 等代理，以及 Node 20.10+。"),
            ("要把 3D beta 放進行動裝置正式站", "效能風險：節流手機實測約 13–15 fps。")]

    def draw(c):
        base(c, 11, "不適合這些人", hint="依官方「Limits」整理，非官方明列名單")
        for n, (head, body) in enumerate(rows):
            y = 1.95 + n * 0.95
            c.card(f"no{n}", 0.9, y, 11.77, 0.82, "FFFFFF", border=LINE, shadow=False)
            c.rect(f"no{n}bar", 0.9, y, 0.08, 0.82, BAD)
            T(c, f"no{n}m", "✕", 1.2, y + .14, 0.5, 0.55, 24, BAD, bold=True)
            T(c, f"no{n}h", head, 1.9, y + .08, 5.6, 0.42, 22, INK, bold=True)
            T(c, f"no{n}b", body, 1.9, y + .46, 10.4, 0.32, 16, SUB)
    return draw


def p13(art):
    links = [("GitHub", "github.com/wheresryan22/anatomy"), ("官網", "skills.wheresryan.sh/anatomy"),
             ("安裝", "npx skills add wheresryan22/anatomy -g")]

    def draw(c):
        base(c, 12, None)
        T(c, "big1", "想把抽象概念，做成一台可以互動的機器？", 0.9, 1.25, 7.5, 1.5, 38, INK, bold=True)
        T(c, "big2", ["Anatomy 適合你。", "要圖表、人物或快速出圖，就不適合。"], 0.9, 2.95, 7.5, 1.4, 28, SUB, after=4)
        for n, (k, v) in enumerate(links):
            y = 4.6 + n * 0.5
            T(c, f"lk{n}", k, 0.9, y, 1.3, 0.4, 18, COPPER, bold=True)
            T(c, f"lv{n}", v, 2.3, y, 6.3, 0.4, 18, INK, face="mono")
        T(c, "src", "圖片與資料來源：wheresryan22/anatomy（MIT © 2026 Ryan），內容核對於 2026-11-06（commit 1482e84）。", 0.9, 6.15, 7.6, 0.55, 14, MUTED)
        c.picture("fig", art("fig_raptor_apart"), 8.7, 1.1, 3.95, 4.95)
        T(c, "fig_cap", "官方範例：Raptor 2，拆開來看", 8.5, 6.15, 4.15, 0.3, 14, MUTED, align=PP_ALIGN.CENTER)
    return draw


# ------------------------------------------------------------------------------------------ deck
NOTES = [
    "封面。口白（草稿）：今天介紹 Anatomy——讓 AI 把概念做成一台會動的機器。",
    "它是什麼。口白：你說要解釋什麼，Claude 就發明一個物件，讓它的運作本身就是那個概念。例如快取鍵變成彈子鎖。",
    "輸出形式與列印：獨立 HTML、單檔 SVG、React 元件；亮暗主題；A4 海報／技術圖／詳解；交付的是原始碼。",
    "三種圖：SVG、SVG+WebGL、3D（beta）。口白：同一套工具，三種表現力。",
    "功能：互動拆解、即時讀數、自我驗證、可及性。",
    "官方範例一覽（8 個範例中的 6 個縮圖；另有 test-rig、spot-plate）。",
    "安裝：一行指令；需求：Node 20.10+、Chrome/Chromium、React 18+（僅 React 輸出）。skills CLI 1.7.1 版官方註明需要 Node 22.20+。",
    "使用：/anatomy（Codex 用 $anatomy）；三個習慣；也會自動載入。",
    "適合誰（依官方定位整理）。",
    "優點。",
    "缺點與限制（官方 README Limits 節）。官方原文：3D 小圖可跑 60 fps；380 零件壓力測試在 1440 px 寬約 20 fps，節流手機設定約 13–15 fps（高負載機器上量測）。",
    "不適合誰（依官方 Limits 整理，非官方明列名單）。",
    "結語與連結。",
]


def build(assets, output, hold=HOLD_MS, duration=MORPH_MS, fonts=None):
    if fonts:
        set_fonts(*fonts)
    art = Art(assets)
    license_text = (Path(assets) / "LICENSE_ANATOMY.txt").read_text(encoding="utf-8")
    if "MIT License" not in license_text or "Copyright (c) 2026 Ryan" not in license_text:
        raise ValueError("missing upstream MIT license text")
    world = World(gap=0.6)
    world.first(p01(art))
    world.add(p02(art), "zoom_in", window=(0.9, 4.8, WIN_W))
    world.add(p03(art), "pull_back", frame=FRAME)
    world.add(p04(art), "pan_right")
    world.add(p05(art), "pan_right")
    world.add(p06(art), "zoom_in", window=(0.9, 4.75, WIN_W))
    world.add(p07(art), "pull_back", frame=FRAME)
    world.add(p08(art), "pan_right")
    world.add(p09(art), "pan_right")
    world.add(p10(art), "zoom_in", window=(8.7, 4.4, WIN_W))
    world.add(p11(art), "pull_back", frame=FRAME)
    world.add(p12(art), "pan_right")
    world.add(p13(art), "pan_down")

    def hud(c, j):
        for n in range(N):
            c.rect(f"pip{n}", 0.9 + n * 0.3, 0.3, 0.24, 0.04, COPPER if n == j else "CFCABB")
        T(c, "credit", CREDIT, 6.6, 6.84, 6.0, 0.26, 14, MUTED, align=PP_ALIGN.RIGHT)

    def notes(j):
        return (NOTES[j] + "\n\n來源與授權：官方素材來自 https://github.com/wheresryan22/anatomy（固定 commit 1482e8469b0a9e0d8cc18ea2740a01423d29ae80）；"
                "事實取自其 README，發布前請人工核對。PowerPoint 原生 Morph 實播狀態：NOT RUN。\n\n" + license_text)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    readable = world.build(prs, hud=hud, notes=notes)
    with tempfile.TemporaryDirectory() as d:
        draft = Path(d) / "draft.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, output, duration, hold, dedupe=True)
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable, ensure_ascii=False, indent=1), encoding="utf-8")
    return world


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assets", type=Path, default=Path("build/anatomy/assets"))
    ap.add_argument("--output", type=Path, default=Path("build/anatomy/anatomy-explainer.pptx"))
    ap.add_argument("--hold", type=int, default=HOLD_MS, help="per-slide hold (ms); set from narration length")
    ap.add_argument("--duration", type=int, default=MORPH_MS, help="Morph transition (ms)")
    ap.add_argument("--font-sans", default=FONTS["sans"], help="must be installed where the deck is played")
    ap.add_argument("--font-serif", default=FONTS["serif"])
    ap.add_argument("--font-mono", default=FONTS["mono"])
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world = build(args.assets, args.output, args.hold, args.duration, (args.font_sans, args.font_serif, args.font_mono))
    print(f"{args.output}: {N} slides, 12 native Morph transitions (SPIKE; PowerPoint playback NOT RUN)")
    print("slide kind scale zoom:", world.describe())


if __name__ == "__main__":
    main()
