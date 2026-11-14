#!/usr/bin/env python3
"""YouTube cut of the AI-subscriptions deck: ~50 mobile-first slides (main text >= 30 pt, one idea per slide), native
Morph transitions chosen per content, per-slide hold times derived from the narration seconds.

Follows the user's storyboard v2.1 (Google Doc; scripts/ai_subscriptions_script.py). Transitions used: in-place redraw with
shared names (`stay`: guided highlight, bar growth), a board tour of the six subscription platforms (`nest`/`zoom_out`),
pans. Platforms are text + colour chips only (no logos). Visuals are original editable shapes.

STATUS: SPIKE/PREVIEW. Layers A and B only; PowerPoint playback, video export and phone viewing are NOT RUN.
Figures: the user's verified storyboard v2.1 (official pages, 2026-11-10); not independently verified here.
Usage: python scripts/build_ai_subscriptions_youtube.py [--output ...] [--font-sans ...]
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
import ai_subscriptions_data as D  # noqa: E402
import ai_subscriptions_script as S  # noqa: E402
import deck_kit as K  # noqa: E402
import pptx_morph_patch  # noqa: E402
from deck_kit import BAD, CARD, COPPER, GOOD, INK, LINE, MUTED, SUB, WALL, WHITE, T  # noqa: E402
from pptx_world import EMU, H, W, World  # noqa: E402

PLAT = {"Claude": "C35F3F", "ChatGPT": "2E7D5B", "Cursor": "3B6EA5", "Antigravity": "7A5BB0",
        "OpenCode": "A37A12", "Kimi": "237F94", "DeepSeek": "55647A"}
HL_FILL = "FBEBDD"
MIN_PT = 30  # main text on screen; the HUD (chapter, date, progress) is exempt
MORPH_MS = 1500


# ------------------------------------------------------------------------------------------------ building blocks
def page(c, headline, tint=CARD, x0=1.0, x1=12.3):
    c.card("card", 0, 0, W, H, tint, shadow=True)
    if headline:
        T(c, "headline", headline, x0, 0.75, x1 - x0, 0.8, 40, INK, bold=True)


def chip(c, name, x, y, w, h, label, color=INK, fill=WHITE, pt=30, line=LINE):
    c.rect(name, x, y, w, h, fill, line=(line, 1.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.25)
    T(c, name + "_t", label, x + .12, y + (h - 0.55) / 2, w - .24, 0.55, pt, color, bold=True, align=PP_ALIGN.CENTER)


def rows_page(c, headline, rows, hl=None, label_w=3.4, top=1.95, pitch=None, tint=CARD, x0=1.0, x1=12.3):
    """Rows of (label, colour, detail[, detail_colour]); `hl` moves a highlight box over one row (same names on every
    slide of a series, so Morph glides the box and recolours the dimmed rows)."""
    page(c, headline, tint, x0, x1)
    n = len(rows)
    pitch = pitch or (1.5 if n <= 3 else 1.15)
    if hl is not None:
        c.rect("hl", x0 - 0.2, top + hl * pitch, x1 - x0 + 0.4, pitch - 0.1, HL_FILL, line=(COPPER, 2.5),
               kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.12)
    dx = x0 + label_w + 0.2
    for i, row in enumerate(rows):
        label, color, detail = row[:3]
        dcolor = row[3] if len(row) > 3 else INK
        dim = hl is not None and i != hl and dcolor == INK
        y = top + i * pitch
        # both texts share the row's box and are centred in it, so label and detail sit on one line and inside the highlight
        T(c, f"rl{i}", label, x0, y, label_w, pitch - 0.1, 34, MUTED if dim else color, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        T(c, f"rd{i}", detail, dx, y, x1 - dx, pitch - 0.1, MIN_PT, MUTED if dim else dcolor, anchor=MSO_ANCHOR.MIDDLE)


def series(headline, rows_by_step, **kw):
    """One draw function per step of a highlight series: rows_by_step = [(rows, hl), ...]."""
    out = []
    for rows, hl in rows_by_step:
        def draw(c, rows=rows, hl=hl):
            rows_page(c, headline, rows, hl, **kw)
        out.append(draw)
    return out


# ------------------------------------------------------------------------------------------------ scene pages
def hook(stage):
    def draw(c):
        page(c, "月費一樣，額度差很多？")
        for i, (label, a, b) in enumerate([("輕度聊天", 0.95, 0.82), ("讓 AI 改整個專案", 0.95, 0.12)]):
            y = 2.2 + i * 1.5
            T(c, f"hk{i}", label, 1.0, y, 4.2, 0.6, 34, INK, bold=True)
            c.rect(f"hk{i}t", 5.3, y + .08, 6.7, 0.5, "E3DFD2", kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
            c.rect(f"hk{i}f", 5.3, y + .08, max(0.25, 6.7 * (a if stage == 0 else b)), 0.5, COPPER,
                   kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
        T(c, "hk_tag", "同樣的月費", 1.0, 5.2 if stage == 0 else 4.9, 11.3, 0.6, 34, SUB, bold=True)
        if stage:
            T(c, "hk_names", ["Claude · ChatGPT · Cursor ·", "Antigravity · OpenCode · Kimi · DeepSeek"],
              1.0, 5.55, 11.3, 1.1, MIN_PT, SUB)
    return draw


def gates(stage):
    def draw(c):
        page(c, "三道閘門")
        for i, label in enumerate(["5 小時", "每週", "每月"]):
            x = 1.0 + i * 3.85
            closed = stage == 1 and i == 1
            c.rect(f"gt{i}", x, 2.1, 3.5, 0.95, BAD if closed else GOOD, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.2)
            T(c, f"gl{i}", label, x, 2.27, 3.5, 0.6, 34, WHITE, bold=True, align=PP_ALIGN.CENTER)
            c.rect(f"gb{i}", x, 3.4, 3.5, 0.5, "E3DFD2", kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
            level = (0.7, 0.0, 0.6)[i] if stage else 0.6
            c.rect(f"gf{i}", x, 3.4, max(0.2, 3.5 * level), 0.5, COPPER, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
        T(c, "g_cap", "一道關上，就先停下" if stage else "三道門都要通過", 1.0, 4.5, 11.3, 0.6, 34, INK, bold=True)
        T(c, "g_note", "各平台規則不同", 1.0, 5.4, 11.3, 0.6, MIN_PT, SUB)
    return draw


PLAT_NAMES = ["Claude", "ChatGPT", "Cursor", "Antigravity", "OpenCode", "Kimi"]
HUB_W, HUB_H = 3.5, 3.5 * H / W
COLS, ROWS_Y = (1.0, 5.0, 9.0), (2.0, 4.6)
SLOTS = [(COLS[0], ROWS_Y[0]), (COLS[1], ROWS_Y[0]), (COLS[2], ROWS_Y[0]),
         (COLS[2], ROWS_Y[1]), (COLS[1], ROWS_Y[1]), (COLS[0], ROWS_Y[1])]  # snake: across, down, back


def hub(done):
    def draw(c):
        page(c, None, WALL)
        T(c, "headline", "六個訂閱平台，一張地圖", 1.0, 0.7, 11.3, 0.7, 36, INK, bold=True)
        for i, ((x, y), name) in enumerate(zip(SLOTS, PLAT_NAMES)):
            c.rect(f"wf{i}", x - .05, y - .05, HUB_W + .1, HUB_H + .1, None, line=(GOOD if done else INK, 2.0 if done else 1.5))
            T(c, f"wl{i}", name, x, y - .52, HUB_W - .6, 0.5, MIN_PT, PLAT[name], bold=True)
            T(c, f"wk{i}", "✓" if done else str(i + 1), x + HUB_W - .6, y - .52, 0.6, 0.5, MIN_PT, GOOD if done else MUTED,
              bold=True, align=PP_ALIGN.RIGHT)
    return draw


def cursor(stage):
    def draw(c):
        page(c, "Cursor：週池倍率")
        for n, (tier, price, mult) in enumerate(D.CURSOR_MULTIPLIERS):
            y = 1.85 + n * 0.75
            T(c, f"cm{n}", f"{tier} ${price}", 1.0, y, 3.4, 0.6, MIN_PT, MUTED if stage else PLAT["Cursor"], bold=True)
            c.rect(f"cmb{n}", 4.5, y + .06, max(0.1, 6.0 * mult / 50), 0.42, "B9C9DD" if stage else PLAT["Cursor"])
            T(c, f"cmv{n}", f"{mult}×", 10.7, y, 1.5, 0.6, MIN_PT, MUTED if stage else INK, bold=True)
        if stage:
            T(c, "ccap", ["第三方模型另購預付額度，", "依 API 定價扣費", "舊版 Pro：另有雙月池"], 1.0, 4.95, 11.3, 1.6, MIN_PT, INK)
        else:
            T(c, "ccap", ["The X Subscription", "＝ X ＋ Grok ＋ Cursor"], 1.0, 4.95, 11.3, 1.6, MIN_PT, INK)
    return draw


def opencode(stage):
    def draw(c):
        page(c, "OpenCode Go：一個共享池")
        if stage < 2:
            chip(c, "oc_a", 1.0, 2.1, 3.9, 0.9, "模型 A　$15", PLAT["OpenCode"])
            chip(c, "oc_b", 1.0, 3.3, 3.9, 0.9, "模型 B　$60", PLAT["OpenCode"])
            c.rect("pool", 5.7, 2.1, 6.6, 2.1, "E3DFD2", line=(LINE, 1.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.12)
            c.rect("pool_f", 5.7, 2.1, 6.6 * (0.067 if stage else 0.0) + 0.001, 2.1, COPPER, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.12)
            T(c, "pool_t", "共享月池", 5.7, 2.65, 6.6, 0.6, 34, INK, bold=True, align=PP_ALIGN.CENTER)
            if stage:
                T(c, "oc_cap", ["花 $1 ÷ 月參考額 $15", "≈ 6.7% 的月池"], 1.0, 4.6, 11.3, 1.2, 34, INK, bold=True)
            else:
                T(c, "oc_cap", ["Go $10／Go Plus $40", "不是每個模型各一份額度"], 1.0, 4.6, 11.3, 1.2, 34, INK, bold=True)
        else:
            for i, (label, frac) in enumerate([("5 小時", 0.2), ("每週", 0.5), ("每月", 1.0)]):
                y = 2.1 + i * 0.95
                T(c, f"oc_l{i}", label, 1.0, y, 2.6, 0.6, 34, INK, bold=True)
                c.rect(f"oc_t{i}", 3.8, y + .08, 6.5, 0.5, "E3DFD2", kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
                c.rect(f"oc_f{i}", 3.8, y + .08, 6.5 * frac, 0.5, COPPER, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
                T(c, f"oc_v{i}", f"{int(frac * 100)}%", 10.5, y, 1.8, 0.6, 34, INK, bold=True)
            T(c, "oc_cap2", ["每一層分別檢查", "換模型不等於換新錢包"], 1.0, 5.1, 11.3, 1.2, 34, INK, bold=True)
    return draw


def kimi(stage):
    def draw(c):
        page(c, "Kimi：沒有週限，不是無限")
        if stage == 0:
            for i, (name, price, note, color) in enumerate([("Go", D.KIMI_TIERS_CNY["Go"], "沒有 Kimi Code", BAD),
                                                             ("Plus", D.KIMI_TIERS_CNY["Plus"], "含 Kimi Code", GOOD)]):
                x = 1.0 + i * 5.8
                c.rect(f"kc{i}", x, 2.0, 5.4, 2.6, WHITE, line=(color, 3.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
                T(c, f"kc{i}n", f"{name}　¥{price}", x + .3, 2.3, 4.8, 0.7, 40, INK, bold=True)
                T(c, f"kc{i}d", note, x + .3, 3.4, 4.8, 0.7, 36, color, bold=True)
            T(c, "kcap", "寫程式，Plus 才是起點", 1.0, 5.1, 11.3, 0.7, 36, INK, bold=True)
        elif stage == 1:
            for i, label in enumerate(["Code", "Work", "PPT", "研究", "Agent"]):
                chip(c, f"kp{i}", 1.0 + (i % 2) * 2.2, 2.0 + (i // 2) * 1.05, 2.0, 0.9, label, PLAT["Kimi"])
            c.rect("kpool", 6.2, 2.0, 6.1, 3.0, "E3DFD2", line=(LINE, 1.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.1)
            T(c, "kpool_t", "共用月度額度", 6.2, 3.1, 6.1, 0.7, 36, INK, bold=True, align=PP_ALIGN.CENTER)
            T(c, "kcap1", ["Code：滾動五小時限制，", "沒有額外週上限"], 1.0, 5.2, 11.3, 1.2, MIN_PT, INK)
        else:
            T(c, "kcap2", ["舊版會員", "可能另有每週限制"], 1.0, 2.3, 11.3, 1.6, 40, INK, bold=True)
            T(c, "kcap3", ["少一道閘門", "≠ 無限使用"], 1.0, 4.3, 11.3, 1.6, 40, BAD, bold=True)
    return draw


def dsapi():
    def draw(c):
        page(c, "DeepSeek：API 不是月票")
        chip(c, "ds_free", 1.0, 2.0, 4.2, 0.9, "免費聊天", GOOD)
        for i, label in enumerate(["快取輸入", "新輸入", "輸出"]):
            y = 3.25 + i * 1.05
            chip(c, f"ds_f{i}", 1.0, y, 3.4, 0.9, label, PLAT["DeepSeek"])
            c.rect(f"ds_ln{i}", 4.4, y + .42, 3.4, 0.06, LINE)
        c.rect("ds_bill", 7.8, 3.25, 4.5, 3.0, WHITE, line=(COPPER, 3.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08)
        T(c, "ds_bill_t", ["帳單", "按用量計費"], 8.0, 3.9, 4.1, 1.6, 36, INK, bold=True, align=PP_ALIGN.CENTER)
    return draw


def cost(stage):
    flash = D.cost_per_100m(D.DEEPSEEK["V4.1 Flash"]["offpeak"])
    pro = D.cost_per_100m(D.DEEPSEEK["V4 Pro"]["offpeak"])
    u = D.DEEPSEEK["V4.1 Flash"]["offpeak"]

    def draw(c):
        page(c, "DeepSeek：高快取試算")
        x = 1.0
        for i, (share, color) in enumerate([(D.MIX["cache"], COPPER), (D.MIX["input"], "C9A227"), (D.MIX["output"], INK)]):
            w = 11.3 * share / 100
            c.rect(f"cs{i}", x, 1.9, w, 0.6, color)
            x += w
        if stage < 2:
            for i, (label, qty, price) in enumerate([("快取輸入", D.MIX["cache"], u["cache"]), ("新輸入", D.MIX["input"], u["input"]),
                                                      ("輸出", D.MIX["output"], u["output"])]):
                T(c, f"cl{i}", f"{label} {qty:g}M × ${price:g}", 1.0, 2.8 + i * 0.6, 11.3, 0.6, MIN_PT, MUTED if stage else INK)
            if stage:
                T(c, "cres", f"＝ US${flash:.3f}", 1.0, 4.85, 11.3, 0.95, 54, COPPER, bold=True)
                T(c, "ccap", "V4.1 Flash · 離峰 · 每 1 億 tokens", 1.0, 5.85, 11.3, 0.6, MIN_PT, SUB)
            else:
                T(c, "ccap", "92％ 快取　7％ 新輸入　1％ 輸出", 1.0, 5.0, 11.3, 0.6, MIN_PT, SUB)
        else:
            T(c, "cn", [f"不含 Search／Fetch（每千次 US${D.SEARCH_FETCH_PER_1000_USD}）", "不含稅與第三方加價",
                        f"V4 Pro 離峰 US${pro:.3f}；尖峰為 2 倍"], 1.0, 3.0, 11.3, 2.4, MIN_PT, INK, after=8)
    return draw


def closing(stage):
    rows = [("功能包含嗎？", INK, "你要的功能在方案內嗎？"), ("何時重設？", INK, "五小時、每週、每月"),
            ("超額怎麼算？", INK, "會不會另外扣錢？")]

    def draw(c):
        rows_page(c, "訂閱前，確認三件事", rows, None, label_w=4.2, top=1.85, pitch=1.2)
        if stage:
            for i in range(3):
                T(c, f"tk{i}", "✓", 11.4, 1.85 + i * 1.2, 0.9, 0.7, 40, GOOD, bold=True, align=PP_ALIGN.CENTER)
            T(c, "date", f"資料查核截至 {D.CHECK_DATE}；價格依發布日官方頁", 1.0, 5.75, 11.3, 0.6, MIN_PT, SUB)
    return draw


# ------------------------------------------------------------------------------------------------ rows content
R = {
    "s02": [("能用的功能", INK, "目標功能有包含嗎？"), ("先撞哪條限制", INK, "短期、每週，還是每月？"),
            ("完成多少工作", INK, "不是問了幾句")],
    "s03": [("token", INK, "處理內容的單位，不是問幾次"), ("五小時", INK, "每段視窗各有一份用量"),
            ("週／月", INK, "更長期的上限，可並存"), ("API", INK, "按輸入、輸出、快取結帳")],
    "s05": [("聊天＋Coding", PLAT["Claude"], "Claude／ChatGPT／Kimi"), ("開發工具", PLAT["Cursor"], "Cursor／Antigravity／OpenCode"),
            ("API 按量", PLAT["DeepSeek"], "DeepSeek")],
    "s15": [("輕度聊天", INK, "先試免費或低價方案"), ("日常 Coding", INK, "比完成率與額度"),
            ("高吞吐自動化", INK, "OpenCode／DeepSeek，算重跑")],
    "s16": [("同一份 repo", INK, "同題目、同工具、同設定"), ("重跑三次", INK, "取中位數，記錄失敗"),
            ("看三個數字", INK, "完成率、用時、用量；觀察 72 小時")],
}
CLAIMS = ["保證每月能用幾億 token", "問四句就沒額度，人人一樣", "API 試算＝訂閱內含用量"]
FIXES = ["未公開：官方沒有固定總額", "條件不足：模型、上下文會變", "不同計價：API 美元不是月票"]
CLAUDE_ROWS = [(f"{n} ${p}", PLAT["Claude"], d) for n, p, d in D.CLAUDE_TIERS]
CHATGPT_ROWS = [("Chat", PLAT["ChatGPT"], "一般聊天，另外算"), ("Codex／Work", PLAT["ChatGPT"], "共用額度；五小時＋每週"),
                ("API", PLAT["ChatGPT"], "按量另外計費")]
ANTI_ROWS = [("付費 Pro", PLAT["Antigravity"], "五小時視窗＋每週上限"), ("Argon", PLAT["Antigravity"], "獨立每週額度，不與 Flash 同池"),
             ("你的帳號", PLAT["Antigravity"], "模型選單與 Usage 才算數")]


def myth_rows(k):
    rows = []
    for i in range(3):
        fixed = i < k
        rows.append((f"迷思 {i + 1}", INK if not fixed else GOOD, FIXES[i] if fixed else CLAIMS[i], GOOD if fixed else INK))
    return rows


def with_detail(rows, idx, text):
    out = list(rows)
    out[idx] = (out[idx][0], out[idx][1], text) + tuple(out[idx][3:])
    return out


# ------------------------------------------------------------------------------------------------ deck order
def deck():
    """[(key, scene, draw, device, kwargs)] in slide order. Device = transition into that slide."""
    out = []

    def add(scene, key, draw, kind=None, **kw):
        out.append((key, scene, draw, kind, kw))

    add("s01", "hook0", hook(0))
    add("s01", "hook1", hook(1), "stay")
    s02 = series("沒有哪家，對所有人最划算", [(R["s02"], None), (R["s02"], 0), (R["s02"], 1), (R["s02"], 2)])
    for i, d in enumerate(s02):
        add("s02", f"concl{i}", d, "pan_right" if i == 0 else "stay")
    s03 = series("四種額度，不是一種貨幣", [(R["s03"], h) for h in (None, 0, 1, 2, 3)], label_w=2.6)
    for i, d in enumerate(s03):
        add("s03", f"quota{i}", d, "pan_right" if i == 0 else "stay")
    add("s04", "gate0", gates(0), "pan_right")
    add("s04", "gate1", gates(1), "stay")
    s05 = series("七家，三種生意", [(R["s05"], h) for h in (None, 0, 1, 2)], label_w=3.8)
    for i, d in enumerate(s05):
        add("s05", f"group{i}", d, "pan_right" if i == 0 else "stay")
    add("s06", "hub", hub(False), "pan_right")
    hub_i = len(out) - 1
    children = [
        ("s06", "claude", series("Claude：重度工作不只看五小時", [(CLAUDE_ROWS, None), (with_detail(CLAUDE_ROWS, 2, "已驗證帳號無五小時限制，仍有每週額度"), 2)])),
        ("s07", "chatgpt", series("ChatGPT：聊天與 Agent 分開算", [(CHATGPT_ROWS, None), (with_detail(CHATGPT_ROWS, 1, "每五小時幾則＝官方估計，不是保證"), 1)], label_w=4.2)),
        ("s08", "cursor", [cursor(0), cursor(1)]),
        ("s09", "anti", series("Antigravity：先看模型，再看配額", [(ANTI_ROWS, None), (ANTI_ROWS, 1)])),
        ("s10", "opencode", [opencode(0), opencode(1), opencode(2)]),
        ("s11", "kimi", [kimi(0), kimi(1), kimi(2)]),
    ]
    for slot, (scene, key, draws) in enumerate(children):
        for j, d in enumerate(draws):
            add(scene, f"{key}{j}", d, "nest" if j == 0 else "stay", slot=slot, hub=hub_i)
    add("s11", "hub_done", hub(True), "zoom_out", hub=hub_i)
    add("s12", "dsapi", dsapi(), "pan_right")
    for i in range(3):
        add("s13", f"cost{i}", cost(i), "pan_right" if i == 0 else "stay")
    for k in range(4):
        add("s14", f"myth{k}", series("三種最容易相信的說法", [(myth_rows(k), k - 1 if k else None)], label_w=2.6)[0],
            "pan_right" if k == 0 else "stay")
    s15 = series("誰比較適合你？", [(R["s15"], h) for h in (None, 0, 1, 2)], label_w=3.8)
    for i, d in enumerate(s15):
        add("s15", f"fit{i}", d, "pan_right" if i == 0 else "stay")
    s16 = series("自己測，才有意義", [(R["s16"], h) for h in (0, 1, 2)], label_w=3.8)
    for i, d in enumerate(s16):
        add("s16", f"test{i}", d, "pan_right" if i == 0 else "stay")
    add("s17", "close0", closing(0), "pan_right")
    add("s17", "close1", closing(1), "stay")
    return out


def slot_ms(slides):
    """Time each slide should occupy in the finished video: the scene's narration seconds shared by its slides."""
    count = Counter(scene for _, scene, *_ in slides)
    return [S.SCENE_SECONDS[scene] * 1000 / count[scene] for _, scene, *_ in slides]


def holds_ms(slides):
    """Auto-advance time (`advTm`). Observed in a user's phone recording of a demo deck (2026-11-14): the Morph time is
    ADDED to the hold, so a slide's slot is (transition into it) + hold; subtract the transition from the slot."""
    return [int(slot - (MORPH_MS if j else 0)) for j, slot in enumerate(slot_ms(slides))]


def build(output, fonts=None):
    if fonts:
        K.set_fonts(*fonts)
    slides = deck()
    world = World(gap=0.6)
    for idx, (key, scene, draw, kind, kw) in enumerate(slides):
        if kind is None:
            world.first(draw)
        elif kind == "nest":
            x, y = SLOTS[kw["slot"]]
            world.add(draw, "nest", window=(x, y, HUB_W), parent=kw["hub"])
        elif kind == "zoom_out":
            world.add(draw, "zoom_out", to=kw["hub"])
        else:
            world.add(draw, kind)
    n = len(slides)

    def hud(c, j):
        scene = slides[j][1]
        T(c, "hud_ch", S.CHAPTER[scene], 1.0, 0.18, 5.0, 0.4, 20, MUTED, bold=True)
        T(c, "hud_date", f"資料查核 {D.CHECK_DATE}", 8.3, 0.18, 4.0, 0.4, 20, MUTED, align=PP_ALIGN.RIGHT)
        c.rect("hud_track", 1.0, 0.62, 11.3, 0.05, "D9D4C6")
        c.rect("hud_fill", 1.0, 0.62, 11.3 * (j + 1) / n, 0.05, COPPER)

    first_of_scene = {}
    for j, (_, scene, *_) in enumerate(slides):
        first_of_scene.setdefault(scene, j)

    def notes(j):
        key, scene = slides[j][0], slides[j][1]
        head = f"[{key}] " + (S.NARRATION[scene] if first_of_scene[scene] == j else "（同一段旁白，延續上一頁）")
        return (f"{head}\n\n本頁約 {slot_ms(slides)[j] / 1000:g} 秒（旁白秒數平均分配到該段頁數；其中轉場 {MORPH_MS / 1000:g} 秒，停留 {holds_ms(slides)[j] / 1000:g} 秒）。\n"
                f"資料：使用者的分鏡 v2.1（官方頁面，查核 {D.CHECK_DATE}），本 repo 未獨立查證。"
                "\nPowerPoint 原生 Morph 實播狀態：NOT RUN。")

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
    readable = world.build(prs, hud=hud, notes=notes, hud_readable=False)
    with tempfile.TemporaryDirectory() as d:
        draft = Path(d) / "draft.pptx"
        prs.save(draft)
        pptx_morph_patch.apply(draft, output, MORPH_MS, holds_ms(slides), dedupe=True)
    Path(output).with_suffix(".readable.json").write_text(json.dumps(readable, ensure_ascii=False, indent=1), encoding="utf-8")
    return world, slides


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, default=Path("build/ai-subscriptions/youtube/ai-subscriptions-youtube.pptx"))
    ap.add_argument("--font-sans", default=K.FONTS["sans"], help="must be installed where the deck is played/exported")
    ap.add_argument("--font-serif", default=K.FONTS["serif"])
    ap.add_argument("--font-mono", default=K.FONTS["mono"])
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world, slides = build(args.output, (args.font_sans, args.font_serif, args.font_mono))
    print(f"{args.output}: {len(slides)} slides, {len(slides) - 1} native Morph transitions "
          f"(~{(sum(holds_ms(slides)) + (len(slides) - 1) * MORPH_MS) / 1000:g} s of video; SPIKE; PowerPoint playback NOT RUN)")
    print("zoom ratios:", sorted({round(z, 2) for _, _, _, z in world.describe()}))


if __name__ == "__main__":
    main()
