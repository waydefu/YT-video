#!/usr/bin/env python3
"""Classroom deck "AI 與 Agent 入門": ~50 landscape slides, native Morph moves, click-to-advance, speaker notes.

Audience: non-technical students, ~45-50 min. Style: the same world/panel/camera model and chapter navigation (ring menu ->
left rail) as the Anatomy deck; chapters alternate camera moves, inside a chapter the same panel is redrawn ("stay") so
Morph slides rows, re-sorts bars, moves a slider knob, swings logos from a ring into a column.
Content: scripts/classroom_ai_agents_script.py (facts from the user's verified Docs, dated). Logos: scripts/classroom_logos.py
(NOMINATIVE-CLASSROOM-USE, labelled "教學引用"). STATUS: SPIKE/PREVIEW; layers A and B only, PowerPoint playback NOT RUN.
Usage: python3 scripts/classroom_logos.py && python3 scripts/build_classroom_ai_agents.py
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
import build_ai_subscriptions_youtube as Y  # noqa: E402  (page / rows_page helpers)
import classroom_ai_agents_script as S  # noqa: E402
import deck_kit as K  # noqa: E402
import deck_motion as M  # noqa: E402
import pptx_morph_patch  # noqa: E402
from deck_kit import BAD, COPPER, GOOD, INK, MUTED, SUB, WALL, WHITE, T  # noqa: E402
from pptx_world import EMU, H, W, World  # noqa: E402

X0, X1 = 2.9, 12.6          # content area right of the rail
MIN_PT = 26                 # classroom floor for main text (projected, not a phone); the HUD is exempt
DUR_STAY, DUR_PAN = 900, 1300
ROW_TOP, ROW_PITCH = 1.8, 1.5
MONO_BG = "1B2A2A"
LOGO_KEYS = ["claude", "openai", "gemini", "kimi", "deepseek", "cursor", "opencode"]
LOGO_NAMES = ["Claude", "ChatGPT", "Gemini", "Kimi", "DeepSeek", "Cursor", "OpenCode"]
TRACK = "E3DFD2"
FOOT = f"資料截至 {S.CHECK_DATE}（Google 部分 {S.GOOGLE_CHECK_DATE}），價格以官方為準 · Logo 為教學引用，商標屬各公司，與各公司無關聯"


class Art:
    def __init__(self, folder):
        self.dir = Path(folder)

    def __call__(self, key):
        path = self.dir / f"logo_{key}.png"
        if not path.is_file():
            raise FileNotFoundError(f"missing {path}; run scripts/classroom_logos.py first")
        return path


def page(c, headline, x0=X0, x1=X1, tint=K.CARD):
    Y.page(c, headline, tint, x0, x1)


def rows(headline, data, steps, label_w=3.4, pitch=None, top=ROW_TOP):
    """One draw function per highlight step; same names on every step so Morph glides the highlight box."""
    p = pitch or (ROW_PITCH if len(data) <= 3 else 1.15)
    return [(lambda c, h=h: Y.rows_page(c, headline, data, h, label_w=label_w, top=top, pitch=p, x0=X0, x1=X1)) for h in steps]


def stack(c, headline, data, hl=None, top=ROW_TOP, pitch=ROW_PITCH, x0=X0, x1=X1):
    """Label over detail, one centred two-line text per row (same layout rule as the Anatomy deck)."""
    page(c, headline, X0, X1)
    if hl is not None:
        c.rect("hl", x0 - 0.2, top + hl * pitch, x1 - x0 + 0.4, pitch - 0.1, Y.HL_FILL, line=(COPPER, 2.5),
               kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.12)
    for i, (label, color, detail) in enumerate(data):
        dim = hl is not None and i != hl
        T(c, f"rt{i}", [[(label, {"pt": 32, "bold": True, "color": MUTED if dim else color})],
                        [(detail, {"pt": MIN_PT + 2, "bold": False, "color": MUTED if dim else INK})]],
          x0, top + i * pitch, x1 - x0, pitch - 0.1, MIN_PT, INK, anchor=MSO_ANCHOR.MIDDLE)


def logo_rows(c, art, headline, data, top=ROW_TOP, pitch=1.2, name_w=3.0, pt=28):
    """data = [(logo key, name, detail)]; the logo sits in the row's centre line."""
    page(c, headline)
    for i, (key, name, detail) in enumerate(data):
        y = top + i * pitch
        c.picture(f"lg{i}", art(key), X0, y + (pitch - 0.1 - 0.7) / 2, 0.7, 0.7)
        T(c, f"ln{i}", name, X0 + 0.95, y, name_w, pitch - 0.1, pt + 2, INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        T(c, f"ld{i}", detail, X0 + 0.95 + name_w + 0.15, y, X1 - (X0 + 0.95 + name_w + 0.15), pitch - 0.1, pt, SUB,
          anchor=MSO_ANCHOR.MIDDLE)


# ------------------------------------------------------------------------------------------------ scene pages
def cover(art, stage):
    def draw(c):
        Y.page(c, None, WALL, 1.0, 12.3)
        M.draw_ripple(c, "rp", 10.4, 3.0, M.ripple_radii(3, 0.45 if stage == 0 else 1.0, 2.1), COPPER, base_alpha=0.09)
        T(c, "title", "AI 與 Agent 入門", 1.0, 1.7, 9.0, 1.3, 60, INK, bold=True)
        T(c, "sub", "給非技術同學的 45 分鐘", 1.0, 3.1, 9.0, 0.8, 34, SUB)
        if stage:
            for i, (key, nm) in enumerate(zip(LOGO_KEYS, LOGO_NAMES)):
                x = 1.0 + i * 1.62
                c.picture(f"cl{i}", art(key), x + 0.3, 4.75, 0.8, 0.8)
                T(c, f"cn{i}", nm, x - 0.35, 5.65, 1.9, 0.45, 24, SUB, align=PP_ALIGN.CENTER)
    return draw


def menu_page(c):
    Y.page(c, "八個章節", WALL, 1.0, 12.3)


def loop(stage):
    nodes = [("看", "讀檔案、搜尋網頁"), ("想", "決定下一步做什麼"), ("做", "改檔、下指令、用工具"), ("檢查", "結果對嗎？不對就再來")]

    def draw(c):
        page(c, "Agent 的工作循環")
        cx, cy = 5.7, 4.3
        pts = M.ring_layout(4, cx, cy, 1.75)
        c.oval("goal", cx, cy, 0.8, "FBEBDD", line=(COPPER, 2.0))
        T(c, "goal_t", "目標", cx - 0.7, cy - 0.3, 1.4, 0.6, 30, COPPER, bold=True, align=PP_ALIGN.CENTER)
        for i, ((x, y), (lab, _)) in enumerate(zip(pts, nodes)):
            on = i == stage
            c.oval(f"nd{i}", x, y, 0.72 if on else 0.55, COPPER if on else TRACK)
            T(c, f"nl{i}", lab, x - 0.65, y - 0.3, 1.3, 0.6, 30 if on else 26, WHITE if on else MUTED, bold=True, align=PP_ALIGN.CENTER)
        T(c, "lp_cap", [[(nodes[stage][0] + "：", {"bold": True, "color": COPPER, "pt": 32}), (nodes[stage][1], {"pt": 28})]],
          8.4, 3.4, 4.2, 1.8, 28, INK, anchor=MSO_ANCHOR.MIDDLE)
    return draw


def four(c):
    page(c, "Agent ＝ 四塊拼起來")
    items = [("模型", "大腦：負責想"), ("工具", "雙手：讀檔、上網、執行"), ("上下文", "桌面：這次記得的東西"), ("說明書", "規則：.md 與 Skill")]
    for i, (a, b) in enumerate(items):
        x, y = X0 + (i % 2) * 4.95, 1.9 + (i // 2) * 2.45
        c.rect(f"fc{i}", x, y, 4.7, 2.2, K.WHITE, line=(K.LINE, 1.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
        T(c, f"ft{i}", [[(a, {"pt": 36, "bold": True, "color": COPPER})], [(b, {"pt": 28})]], x + 0.3, y, 4.1, 2.2, 28, INK,
          anchor=MSO_ANCHOR.MIDDLE)


def context(stage):
    full = [("說明書", 1.9, "C35F3F"), ("對話", 2.6, "3B6EA5"), ("檔案", 2.6, "237F94"), ("工具結果", 2.4, "A37A12")]
    packed = [("說明書", 1.9, "C35F3F"), ("摘要", 1.6, "3B6EA5"), ("", 0.04, "237F94"), ("", 0.04, "A37A12")]

    def draw(c):
        page(c, "上下文：它這次記得多少")
        c.rect("desk", X0, 2.2, 9.5, 1.2, TRACK, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.1)
        x = X0
        for i, (lab, w, col) in enumerate((packed if stage else full)):
            c.rect(f"sg{i}", x, 2.2, w, 1.2, col, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.1)
            T(c, f"sl{i}", lab, x, 2.2, max(w, 0.5), 1.2, 26, WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
              track=bool(lab))
            x += w
        T(c, "cx1", "桌面空間快滿了，再放就會忘掉" if not stage else "快滿時，舊內容先壓成摘要", X0, 3.8, 9.5, 0.7, 34, COPPER, bold=True)
        T(c, "cx2", "桌面大小用 token 計算，約 25 萬到 100 萬 token（依模型）", X0, 4.8, 9.5, 1.3, 28, INK)
    return draw


def md_file(c):
    page(c, ".md 檔：給 Agent 的說明書")
    c.rect("md_box", X0, 1.9, 9.5, 2.6, MONO_BG, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.06)
    T(c, "md_t", ["# AGENTS.md", "- 用繁體中文回答", "- 改完先跑測試", "- 不要刪除檔案"], X0 + 0.4, 1.9, 8.8, 2.6, 28, WHITE,
      face="mono", anchor=MSO_ANCHOR.MIDDLE)
    T(c, "md_c", "放在專案資料夾，每次開工它都先讀。檔名依工具而定：CLAUDE.md、AGENTS.md", X0, 4.8, 9.5, 1.4, 28, INK)


def skill(stage):
    def draw(c):
        page(c, "Skill：需要才讀的做法")
        for i, (a, b, col) in enumerate([(".md 說明書", "每次都讀\n放通用規則", MUTED), ("Skill 技能包", "要用才載入\n放專門做法", COPPER)]):
            x = X0 + i * 4.95
            on = (i == 1) == bool(stage) or stage == 0
            hot = stage == 1 and i == 1
            c.rect(f"sk{i}", x, 1.9, 4.7, 2.7, Y.HL_FILL if hot else K.WHITE, line=(COPPER if hot else K.LINE, 2.5 if hot else 1.0),
                   kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
            T(c, f"skt{i}", [[(a, {"pt": 34, "bold": True, "color": col if (hot or stage == 0) else MUTED})],
                             [(b.split("\n")[0], {"pt": 28})], [(b.split("\n")[1], {"pt": 28})]],
              x + 0.3, 1.9, 4.1, 2.7, 28, INK if on else MUTED, anchor=MSO_ANCHOR.MIDDLE)
        T(c, "sk_c", "一個資料夾，裡面一份 SKILL.md" if stage == 0 else "例如：做簡報的步驟、審查程式的清單", X0, 5.0, 9.5, 0.8, 30, SUB)
    return draw


def slider(stage):
    stops = [("低", 3.9), ("高", 7.75), ("最高", 11.6)]
    caps = ["快、省額度，適合改錯字", "比較準，適合一般工作", "最慢最花，留給難題"]

    def draw(c):
        page(c, "思考程度：它想多久")
        c.rect("trk", 3.4, 3.35, 8.5, 0.18, TRACK, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
        c.rect("trf", 3.4, 3.35, max(0.2, stops[stage][1] - 3.4), 0.18, COPPER, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
        for i, (lab, x) in enumerate(stops):
            T(c, f"st{i}", lab, x - 0.8, 3.85, 1.6, 0.6, 30, COPPER if i == stage else MUTED, bold=True, align=PP_ALIGN.CENTER)
        c.oval("knob", stops[stage][1], 3.44, 0.34, COPPER, line=(WHITE, 3.0))
        T(c, "th_c", caps[stage], X0, 5.0, 9.5, 0.9, 36, INK, bold=True)
        T(c, "th_n", "想得多通常更準，但更慢、更花額度", X0, 2.0, 9.5, 0.8, 30, SUB)
    return draw


def lineup_logo(art, key, headline, data):
    def draw(c):
        Y.rows_page(c, headline, data, None, label_w=3.5, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1)
        c.picture("hlogo", art(key), 11.4, 0.55, 1.0, 1.0)
    return draw


def google_page(art, data):
    """Google line-up with the date of the official-page read; Orchestrator is mentioned as a one-line footnote."""
    def draw(c):
        logo_rows(c, art, "Google：11 月新模型", data, pitch=1.1, name_w=3.9, pt=26)
        T(c, "g_foot", f"Antigravity 官方頁 {S.GOOGLE_CHECK_DATE}；另有 Orchestrator 搭配", X0, 6.3, 9.7, 0.5, 24, MUTED)
    return draw


def ring_menu(art, stage):
    prods = [("Anthropic", "Claude · Claude Code"), ("OpenAI", "ChatGPT · Codex"), ("Google", "Gemini · Antigravity"),
             ("月之暗面", "Kimi · Kimi Code"), ("DeepSeek", "聊天 App · API"), ("Cursor", "Cursor · Grok"),
             ("OpenCode", "OpenCode · Go 方案")]

    def draw(c):
        page(c, "七家 AI 公司" if stage == 0 else "每家的 App 與 Agent")
        cx, cy = 7.75, 4.2
        ring = M.ring_layout(7, cx, cy, 1.95)
        col = M.column_layout(7, X0, 1.8, 0.72)
        for i in range(7):
            if stage == 0:
                x, y = ring[i]
                c.oval(f"disc{i}", x, y, 0.55, WHITE, line=(K.LINE, 1.0))
                c.picture(f"lg{i}", art(LOGO_KEYS[i]), x - 0.36, y - 0.36, 0.72, 0.72)
                left = x - cx < -0.3  # names go on the outer side so they never touch a neighbour's logo
                T(c, f"nm{i}", LOGO_NAMES[i], (x - 0.7 - 1.9) if left else (x + 0.7), y - 0.25, 1.9, 0.5, 26, SUB,
                  align=PP_ALIGN.RIGHT if left else PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
                T(c, f"pd{i}", "", X0 + 3.3, 1.8 + i * 0.72, 6.0, 0.6, 28, INK, track=False)
            else:
                x, y = col[i]
                c.oval(f"disc{i}", x + 0.3, y + 0.33, 0.3, WHITE, line=(K.LINE, 1.0))
                c.picture(f"lg{i}", art(LOGO_KEYS[i]), x + 0.03, y + 0.06, 0.55, 0.55)
                T(c, f"nm{i}", prods[i][0], x + 0.8, y, 2.4, 0.66, 28, INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
                T(c, f"pd{i}", prods[i][1], x + 3.3, y, 6.2, 0.66, 28, SUB, anchor=MSO_ANCHOR.MIDDLE)
        if stage == 0:
            T(c, "ctr", "AI 公司", cx - 1.2, cy - 0.35, 2.4, 0.7, 36, COPPER, bold=True, align=PP_ALIGN.CENTER)
    return draw


def bench(stage):
    def draw(c):
        page(c, "寫程式 Agent 比賽：分數" if stage == 0 else "同一場比賽：每題花多少美元")
        order = sorted(range(len(S.BENCH)), key=(lambda i: -S.BENCH[i][1]) if stage == 0 else (lambda i: S.BENCH[i][2]))
        vmax = 70.0 if stage == 0 else 20.0
        for pos, i in enumerate(order):
            name, score, cost = S.BENCH[i]
            val = score if stage == 0 else cost
            y = 1.85 + pos * 0.72
            T(c, f"bn{i}", name, X0, y, 3.7, 0.6, 28, INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
            K.hbar(c, f"bb{i}", X0 + 3.8, y + 0.08, 4.2, 0.44, val, vmax, COPPER if stage == 0 else "237F94")
            T(c, f"bv{i}", f"{val:.2f}%" if stage == 0 else f"US${val:.2f}", X0 + 3.8 + 4.2 * val / vmax + 0.15, y, 1.7, 0.6, 28, SUB,
              anchor=MSO_ANCHOR.MIDDLE)
        T(c, "bfoot", "Vals AI 2026-10-29・同框架・*Carbon 不等於 Argon", X0, 6.3, 9.7, 0.5, 24, MUTED)
    return draw


def gates(stage):
    def draw(c):
        page(c, "月費的三道閘門")
        for i, label in enumerate(["5 小時", "每週", "每月"]):
            x = X0 + i * 3.3
            closed = stage == 1 and i == 1
            c.rect(f"gt{i}", x, 2.0, 3.0, 0.95, BAD if closed else GOOD, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.2)
            T(c, f"gl{i}", label, x, 2.0, 3.0, 0.95, 32, WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            c.rect(f"gb{i}", x, 3.3, 3.0, 0.45, TRACK, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
            level = (0.7, 0.0, 0.6)[i] if stage else 0.6
            c.rect(f"gf{i}", x, 3.3, max(0.2, 3.0 * level), 0.45, COPPER, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
        T(c, "g_cap", "一道關上，就先停下" if stage else "三道門都要通過", X0, 4.3, 9.5, 0.7, 36, INK, bold=True)
        T(c, "g_note", "5 小時不是一天只能用 5 小時，而是每段 5 小時有一份上限", X0, 5.3, 9.5, 1.3, 28, SUB)
    return draw


def token(stage):
    def draw(c):
        page(c, "token：算錢的單位")
        names = [("快取輸入", "讀過的，最便宜", "0.003"), ("新輸入", "新給它的", "0.15"), ("輸出", "它寫的", "0.60")]
        for i, (a, b, v) in enumerate(names):
            x = X0 + i * 3.3
            c.rect(f"tk{i}", x, 1.9, 3.0, 3.0, K.WHITE, line=(K.LINE, 1.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
            T(c, f"tkt{i}", [[(a, {"pt": 32, "bold": True, "color": COPPER})], [(b, {"pt": 26})],
                              [(f"US${v}" if stage else "", {"pt": 36, "bold": True, "color": INK})]],
              x + 0.2, 1.9, 2.6, 3.0, 26, SUB, anchor=MSO_ANCHOR.MIDDLE)
        T(c, "tk_c", "token 是文字量的單位，不是問了幾次" if not stage else "DeepSeek V4.1 Flash 離峰，每 100 萬 token", X0, 5.3, 9.5, 1.2, 30, INK)
    return draw


def api_calc(c):
    page(c, "一億 token 要多少錢？")
    T(c, "ap_n", ["DeepSeek，一億 token：", "9,200 萬快取＋700 萬新輸入＋100 萬輸出"], X0, 1.6, 9.7, 1.0, 26, SUB)
    for i, (lab, v) in enumerate(S.DEEPSEEK_100M):
        y = 2.75 + i * 0.85
        T(c, f"ab{i}", lab, X0, y, 3.4, 0.7, 28, INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        K.hbar(c, f"abb{i}", X0 + 3.5, y + 0.1, 4.0, 0.5, v, 18.0, COPPER if i < 2 else "237F94")
        T(c, f"abv{i}", f"US${v:.3f}", X0 + 3.5 + 4.0 * v / 18.0 + 0.15, y, 2.0, 0.7, 28, SUB, anchor=MSO_ANCHOR.MIDDLE)
    T(c, "ap_f", "只是特定比例的試算，不是包月；Search／Fetch 另計", X0, 6.3, 9.7, 0.6, 26, MUTED)


def ladder(art, stage):
    sets = [[("claude", "Claude", "Pro $20 · Max $100 · Ultra $200"),
             ("openai", "ChatGPT", "Go $8 · Plus $20 · Pro $100／$200／$500"),
             ("cursor", "Cursor", "Plus $8 · Premium $30 · Super $100 · Ultra $200")],
            [("gemini", "Antigravity", "Google AI Pro 約 $20 · Ultra $100／$200"),
             ("opencode", "OpenCode", "Go $10 · Go+ $40"),
             ("kimi", "Kimi", "人民幣：Go ¥49 · Plus ¥99 · Pro ¥199 · Max ¥699 · Ultra ¥1,399")]]

    def draw(c):
        logo_rows(c, art, "各家月費階梯" if stage == 0 else "各家月費階梯（續）", sets[stage], pitch=1.45, name_w=2.3, pt=26)
    return draw


def free_rows(art, stage):
    sets = [[("claude", "Claude", "受限聊天，不含 Claude Code"), ("openai", "ChatGPT", "Luna 聊天＋本機 Codex"),
             ("gemini", "Google", "Gemini 3.8 Flash，有週額度"), ("kimi", "Kimi", "網頁 K3.1 Pro 限量")],
            [("deepseek", "DeepSeek", "網頁／App 聊天免費，API 另計"), ("cursor", "Cursor", "Free：有限的 Agent 與聊天"),
             ("opencode", "OpenCode", "工具免費，部分模型限時免費")]]

    def draw(c):
        logo_rows(c, art, "免費可以做什麼" if stage == 0 else "免費可以做什麼（續）", sets[stage], pitch=1.2 if stage == 0 else 1.45,
                  name_w=2.6, pt=26)
    return draw


def closing(art):
    def draw(c):
        Y.page(c, None, WALL, 1.0, 12.3)
        T(c, "end_t", "謝謝，來問問題", X0, 1.9, 9.5, 1.1, 54, INK, bold=True)
        T(c, "end_d", [f"資料截至 {S.CHECK_DATE}", "價格以各家官方頁為準，上課前請重查"], X0, 3.3, 9.5, 1.4, 30, SUB)
        for i, key in enumerate(LOGO_KEYS):
            c.picture(f"el{i}", art(key), X0 + i * 1.35, 5.1, 0.7, 0.7)
        T(c, "end_n", "Logo 為教學引用，商標屬各公司，與各公司無關聯", X0, 6.0, 9.7, 0.5, 24, MUTED)
    return draw


# ------------------------------------------------------------------------------------------------ deck order
def deck(art):
    """[(key, scene, draw, kind)]; kind = transition INTO the slide. Chapters alternate pan_right / pan_down, 'stay' inside."""
    out = []

    def add(scene, key, draw, kind=None):
        out.append((key, scene, draw, kind))

    def chapter_entry(scene, i):
        """Only the first scene of a chapter flips the camera; later scenes of the same chapter pan right."""
        if i:
            return "stay"
        ch = S.SCENE_CHAPTER[scene]
        if ch not in chapters_seen:
            chapters_seen.add(ch)
            return "pan_down" if len(chapters_seen) % 2 else "pan_right"
        return "pan_right"
    chapters_seen = set()

    add("cover", "cover0", cover(art, 0))
    add("cover", "cover1", cover(art, 1), "stay")
    add("menu", "menu", menu_page, "pan_right")
    for i, d in enumerate(rows("聊天機器人 vs Agent", [("聊天機器人", COPPER, "你問一句，它答一句"), ("Agent", COPPER, "你給目標，它分步驟做完"),
                                                   ("差在哪", COPPER, "會用工具、會檢查自己")], (None, 1, 2), label_w=3.4)):
        add("a_chat", f"chat{i}", d, chapter_entry("a_chat", i))
    for i in range(4):
        add("a_loop", f"loop{i}", loop(i), "pan_right" if i == 0 else "stay")
    do = [("改程式", COPPER, "修錯誤、加功能"), ("查資料", COPPER, "上網搜尋再整理"), ("整理檔案", COPPER, "批次改名、分類"), ("跑測試", COPPER, "自己執行、看結果")]
    risk = [("會出錯", BAD, "做錯也可能很有自信"), ("會花錢", BAD, "用量會被扣額度"), ("有權限", BAD, "能改檔案，要設邊界")]
    add("a_do", "do0", lambda c: Y.rows_page(c, "它能幹嗎", do, None, label_w=3.0, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")
    add("a_do", "do1", lambda c: Y.rows_page(c, "要小心什麼", risk, None, label_w=3.0, top=ROW_TOP, pitch=ROW_PITCH, x0=X0, x1=X1), "stay")

    add("b_four", "four", four, chapter_entry("b_four", 0))
    add("b_ctx", "ctx0", context(0), "pan_right")
    add("b_ctx", "ctx1", context(1), "stay")
    add("b_md", "md", md_file, "pan_right")
    add("b_skill", "skill0", skill(0), "pan_right")
    add("b_skill", "skill1", skill(1), "stay")
    mod = [("是什麼", COPPER, "改行為與畫面的小程式"), ("誰做的", COPPER, "Claude Code Mods"), ("例子", COPPER, "危險指令先提醒"), ("風險", BAD, "與電腦同權限，非沙盒")]
    add("b_mod", "mod", lambda c: Y.rows_page(c, "Mod：改行為的小程式", mod, None, label_w=2.8, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")
    summ = [(".md", COPPER, "規則，每次都讀"), ("Skill", COPPER, "做法，需要才讀"), ("MCP", COPPER, "接外部工具與資料"), ("Mod", COPPER, "改行為與畫面")]
    add("b_sum", "sum", lambda c: Y.rows_page(c, "四個名詞，一張圖", summ, None, label_w=2.8, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")

    for i in range(3):
        add("c_think", f"think{i}", slider(i), chapter_entry("c_think", i))
    names = [("OpenAI", COPPER, "Instant 到 Extra High"), ("Kimi・DeepSeek", COPPER, "low／high／max"), ("Claude", COPPER, "Adaptive：自動決定"),
             ("提醒", BAD, "更高不一定更好")]
    add("c_names", "names", lambda c: Y.rows_page(c, "各家怎麼叫", names, None, label_w=4.2, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")

    add("d_ring", "ring0", ring_menu(art, 0), chapter_entry("d_ring", 0))
    add("d_ring", "ring1", ring_menu(art, 1), "stay")
    role = [("模型公司", COPPER, "Claude、GPT、Gemini、Kimi、DeepSeek"), ("工具公司", COPPER, "Cursor、OpenCode：可接別人的模型"),
            ("兩邊都做", COPPER, "OpenAI 有 Codex，Anthropic 有 Claude Code")]
    add("d_role", "role", lambda c: stack(c, "誰做模型，誰做工具", role), "pan_right")

    scale = [("旗艦：最強也最貴", COPPER, "Opus 5.5・GPT-6 Astra・Gemini 4 Carbon"), ("主力：快又夠強", COPPER, "Sonnet 5.5・GPT-6.1 Sol・Kimi K3.1 Pro"),
             ("輕量：便宜快速", COPPER, "Haiku 5.5・GPT-6 Luna・Gemini 4 Hydrogen")]
    add("e_scale", "scale", lambda c: stack(c, "模型分三級（編輯分級，非官方）", scale), chapter_entry("e_scale", 0))
    claude = [("Fable 5.1", COPPER, "最高階，深度研究，較慢"), ("Opus 5.5", COPPER, "頂級：複雜改程式"), ("Sonnet 5.5", COPPER, "強而快：日常施工"), ("Haiku 5.5", COPPER, "輕量：摘要、小任務")]
    add("e_claude", "claude", lineup_logo(art, "claude", "Claude（Anthropic）", claude), "pan_right")
    oa = [("GPT-6 Astra", COPPER, "最高階，極難任務"), ("GPT-6.1 Sol", COPPER, "高階主力"), ("GPT-6.1 Terra", COPPER, "效率優先"), ("GPT-6 Luna", COPPER, "輕量便宜")]
    add("e_openai", "openai", lineup_logo(art, "openai", "OpenAI", oa), "pan_right")
    goo = [("gemini", "Gemini 4 Carbon", "新旗艦規劃者，Ultra 起"), ("gemini", "Gemini 4 Argon", "規劃者，付費 Pro 起"),
           ("gemini", "Gemini 4 Hydrogen", "11 月新：快、日常執行"), ("gemini", "Gemini 3.8 Flash", "快，免費版也有")]
    add("e_google", "google", google_page(art, goo), "pan_right")
    kd = [("kimi", "Kimi K3.1 Pro", "最強，只用思考模式"), ("kimi", "Kimi K3", "上一代旗艦"), ("deepseek", "V4.1 Flash", "便宜、快、大批量"),
          ("deepseek", "V4 Pro", "深度推理")]
    add("e_kd", "kd", lambda c: logo_rows(c, art, "Kimi 與 DeepSeek", kd, pitch=1.15, name_w=3.6, pt=26), "pan_right")
    co = [("cursor", "Grok 4.7", "Cursor 自家，寫程式"), ("cursor", "Composer 2.5", "改了就測，反覆快"),
          ("opencode", "OpenCode Go", "約 30 款模型，共用額度"), ("opencode", "Go+", "同機制，上限更高")]
    add("e_co", "co", lambda c: logo_rows(c, art, "Cursor 與 OpenCode", co, pitch=1.15, name_w=3.6, pt=26), "pan_right")
    add("e_bench", "bench0", bench(0), "pan_right")
    add("e_bench", "bench1", bench(1), "stay")
    read = [("同一把尺", COPPER, "同框架、同版本才能比"), ("輕量不是廢", COPPER, "便宜快，做小事剛好"), ("看任務", COPPER, "難題要旗艦，小事用輕量"), ("自己測", COPPER, "同一題跑三次")]
    add("e_read", "read", lambda c: Y.rows_page(c, "怎麼看「誰聰明」", read, None, label_w=3.4, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")

    kinds = [("月費訂閱", COPPER, "固定月費，額度有上限"), ("API 按量", COPPER, "用多少，算多少"), ("免費", COPPER, "額度小，功能有限")]
    add("f_kinds", "kinds", lambda c: Y.rows_page(c, "三種付費方式", kinds, None, label_w=3.4, top=ROW_TOP, pitch=ROW_PITCH, x0=X0, x1=X1), chapter_entry("f_kinds", 0))
    add("f_token", "token0", token(0), "pan_right")
    add("f_token", "token1", token(1), "stay")
    add("f_gates", "gate0", gates(0), "pan_right")
    add("f_gates", "gate1", gates(1), "stay")
    add("f_ladder", "ladder0", ladder(art, 0), "pan_right")
    add("f_ladder", "ladder1", ladder(art, 1), "stay")
    trap = [("Cursor $8", BAD, "只含自家模型"), ("Kimi Go ¥49", BAD, "不含 Kimi Code"), ("Argon", BAD, "有獨立每週額度"), ("倍率", BAD, "不是固定總量")]
    add("f_trap", "trap", lambda c: Y.rows_page(c, "價格以外要注意", trap, None, label_w=3.6, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")
    add("f_api", "api", api_calc, "pan_right")

    add("g_free", "free0", free_rows(art, 0), chapter_entry("g_free", 0))
    add("g_free", "free1", free_rows(art, 1), "stay")
    gk2 = [("聊天", COPPER, "免費版常有，額度小"), ("本機 Agent", COPPER, "部分免費，仍有上限"), ("雲端 Agent", COPPER, "多半要付費"), ("API", COPPER, "按量付費")]
    add("g_kinds", "gkinds", lambda c: Y.rows_page(c, "免費不等於無限，也不等於全包", gk2, None, label_w=3.6, top=ROW_TOP, pitch=1.15, x0=X0, x1=X1), "pan_right")

    pick = [("一般聊天", COPPER, "先用免費版"), ("一張 $20 全包", COPPER, "ChatGPT Plus"), ("認真寫程式", COPPER, "Claude Pro"),
            ("便宜接模型", COPPER, "OpenCode Go"), ("按量最省", COPPER, "DeepSeek API，設上限")]
    add("h_pick", "pick", lambda c: Y.rows_page(c, "怎麼選（依情境，不是排名）", pick, None, label_w=3.7, top=1.75, pitch=0.98, x0=X0, x1=X1), chapter_entry("h_pick", 0))
    chk = [[("功能有包含嗎", COPPER, "例如有沒有 Code"), ("額度何時重設", COPPER, "5 小時？每週？每月？"), ("超額會扣錢嗎", COPPER, "先設上限")],
           [("同一題", COPPER, "同專案、同條件"), ("跑三次", COPPER, "取中位數、記用量"), ("看結果", COPPER, "成功率、時間、花費")]]
    for i, titl in enumerate(("訂閱前三件事", "再自己測三次")):
        add("h_check", f"chk{i}", (lambda c, d=chk[i], t=titl: Y.rows_page(c, t, d, None, label_w=3.8, top=ROW_TOP, pitch=ROW_PITCH, x0=X0, x1=X1)),
            "pan_right" if i == 0 else "stay")
    myth = [("「官方把額度砍半」", BAD, "沒有官方公告，只有網友自述"), ("「問四句就沒了」", BAD, "模型與設定不明，不能推論"),
            ("「一億 token ＝ 包月」", BAD, "那是 API 的試算，不是訂閱額度")]
    add("h_myth", "myth", lambda c: stack(c, "三個常見誤解", myth), "pan_right")
    add("h_end", "end", closing(art), "pan_right")
    return out


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
    menu_j = next(j for j, (key, *_r) in enumerate(slides) if key == "menu")
    first_of_scene = {}
    for j, (_, scene, *_r) in enumerate(slides):
        first_of_scene.setdefault(scene, j)
    cx, cy = W / 2, 3.9

    def hud(c, j):
        c.rect("hud_track", 1.0, 0.25, 11.3, 0.05, "D9D4C6")
        c.rect("hud_fill", 1.0, 0.25, 11.3 * (j + 1) / n, 0.05, COPPER)
        T(c, "hud_foot", FOOT, 1.0, 6.85, 11.3, 0.26, 14, MUTED, align=PP_ALIGN.CENTER)
        if j == menu_j:
            c.oval("hub", cx, cy, 1.1, COPPER)
            T(c, "hub_t", "章節", cx - 0.8, cy - 0.25, 1.6, 0.5, 30, WHITE, bold=True, align=PP_ALIGN.CENTER)
            M.draw_menu(c, "rm", S.CHAPTERS, M.ring_layout(8, cx, cy, 2.5), None, label_dx=0.6, label_w=1.6)
        elif j > menu_j:
            ch = S.SCENE_CHAPTER[slides[j][1]]
            c.oval("hub", 0.95, 0.85, 0.15, COPPER)
            T(c, "hub_t", "", 0.9, 0.8, 0.1, 0.1, 14, WHITE)
            M.draw_menu(c, "rm", S.CHAPTERS, M.column_layout(8, 0.95, 1.45, 0.72), ch, r_idle=0.3, r_active=0.4, label_dx=0.55, pt=20,
                        label_w=1.5)

    def notes(j):
        key, scene = slides[j][0], slides[j][1]
        body = S.NOTES[scene] if first_of_scene[scene] == j else "（同一主題，點下一步繼續）"
        return f"[{key}] {body}\n\n點擊換頁（無自動換頁）。轉場：PowerPoint 原生 Morph 桌面放映 NOT RUN。\n資料截至 {S.CHECK_DATE}；來源清單見 docs/CLASSROOM-AI-AGENTS.md。"

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    readable = world.build(prs, hud=hud, notes=notes, hud_readable=False)
    durations = [0] + [DUR_STAY if k == "stay" else DUR_PAN for _, _, _, k in slides[1:]]
    with tempfile.TemporaryDirectory() as d:
        draft = Path(d) / "draft.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, output, durations[:1] + world.durations(DUR_PAN)[1:], None, dedupe=True)
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable, ensure_ascii=False, indent=1), encoding="utf-8")
    return world, slides


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assets", type=Path, default=Path("build/classroom/assets"))
    ap.add_argument("--output", type=Path, default=Path("build/classroom/classroom-ai-agents.pptx"))
    ap.add_argument("--font-sans", default=K.FONTS["sans"])
    ap.add_argument("--font-serif", default=K.FONTS["serif"])
    ap.add_argument("--font-mono", default=K.FONTS["mono"])
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world, slides = build(args.output, args.assets, (args.font_sans, args.font_serif, args.font_mono))
    count = Counter(k for *_, k in slides)
    print(f"{args.output}: {len(slides)} slides, {len(slides) - 1} Morph transitions {dict(count)} (click to advance; SPIKE; PowerPoint playback NOT RUN)")


if __name__ == "__main__":
    main()
