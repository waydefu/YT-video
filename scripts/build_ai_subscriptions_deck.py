#!/usr/bin/env python3
"""AI Coding / Agent subscription-comparison deck: 20 slides, native Morph camera transitions, original charts.

Source: the user's document "AI Coding / Agent 七平台訂閱比較 v5.1" (snapshot 2026-11-03). Figures are transcribed in
scripts/ai_subscriptions_data.py; they were NOT re-verified against vendor pages and every slide carries the
snapshot date. Visuals are charts and diagrams drawn from the document's numbers as editable shapes. Only two
third-party marks are used: the OpenCode wordmark (slide 8, GUIDELINE-PERMITTED) and the Cursor lockup (slide 7,
NOMINATIVE-USE-ASSESSMENT); statuses in docs/ASSET-RIGHTS.md. They are fetched by scripts/brand_assets.py, SHA256-checked,
and skipped if absent. All other platforms stay text-only (approval needed, or the official file/terms were not obtainable).

Transitions (one continuous world, scripts/pptx_world.py): zoom-through -> pull-back reveal triples with pans between.
STATUS: SPIKE/PREVIEW. Layers A and B only; PowerPoint playback and video export are NOT RUN.
Usage: python scripts/build_ai_subscriptions_deck.py [--hold 8000] [--font-sans ...]
Requires: python-pptx, Pillow
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_subscriptions_data as D  # noqa: E402
import deck_kit as K  # noqa: E402
import brand_assets  # noqa: E402
import pptx_morph_patch  # noqa: E402
from deck_kit import (BAD, CARD, COPPER, DARK, DARKSUB, DARKTXT, FRAME, GOOD, INK, LINE, MUTED, SUB, WALL, WHITE,  # noqa: E402
                      WIN_W, T, base, frame, hbar, line, para_list, row_cells, window)
from pptx_world import EMU, H, W, World  # noqa: E402

HOLD_MS, MORPH_MS = 8000, 1500
OPENCODE_MARK = "opencode-wordmark-light.png"
CURSOR_MARK = "cursor-lockup-horizontal-2d-light.png"
BRAND = {"dir": None}  # set by build(); the mark is used only if present and matching its pinned SHA256
CURSOR_CREDIT = "Cursor 標誌取自官方品牌頁 cursor.com/brand；商標屬 Anysphere, Inc.，本簡報與其無關聯、非其背書。"
OPENCODE_CREDIT = "OpenCode 標誌取自官方品牌頁 opencode.ai/brand；商標屬 Anomaly，本簡報與其無關聯、非其背書。"
N = 20
FOOTER = f"資料快照 {D.SNAPSHOT}（{D.VERSION}）· 取自提供文件，未重新核對"
PLAT = {"Claude": "C35F3F", "ChatGPT": "2E7D5B", "Cursor": "3B6EA5", "Antigravity": "7A5BB0",
        "OpenCode": "A37A12", "Kimi": "237F94", "DeepSeek": "55647A"}
KICKERS = ["AI CODING / AGENT · 訂閱額度研究", "01 / 額度是什麼", "02 / 七平台總覽", "03 / 價格階梯", "04 / 計量機制",
           "05 / Claude 與 ChatGPT", "06 / Cursor", "07 / Antigravity 與 OpenCode", "08 / Kimi", "09 / DeepSeek 單價",
           "10 / 高快取成本試算", "11 / API 贈額", "12 / 模型能力", "13 / 「可用」的四種意思", "14 / 官方可量化 vs 未公開",
           "15 / 情境選擇", "16 / 自己測", "17 / 不能證實的說法", "18 / 訂閱前確認", "19 / 一句話"]


def price_str(v):
    """Unit price as printed in the source (3 decimals, one trailing zero dropped): 0.003, 0.15, 0.60, 1.98."""
    t = f"{v:.3f}"
    return t[:-1] if t.endswith("0") else t


# ------------------------------------------------------------------------------------------------ panels
def p01():
    def draw(c):
        base(c, KICKERS[0], None)
        T(c, "t1", "AI Coding / Agent", 0.85, 0.95, 7.0, 0.95, 44, INK, face="serif", bold=True)
        T(c, "t2", "七平台訂閱額度比較", 0.9, 1.95, 7.0, 0.95, 44, INK, bold=True)
        T(c, "plat", "Claude · ChatGPT／Codex · Cursor · Antigravity · OpenCode · Kimi · DeepSeek", 0.9, 3.0, 6.5, 0.8, 16, SUB)
        T(c, "snap", f"資料快照 {D.SNAPSHOT}（{D.VERSION}）· 價格與額度之後可能已變動", 0.9, 3.85, 6.5, 0.6, 14, MUTED)
        for n, (label, fill) in enumerate([("5 小時", 0.72), ("每週", 0.45), ("每月", 0.2)]):
            y = 1.45 + n * 1.35
            T(c, f"g{n}l", label, 8.0, y, 3.0, 0.4, 18, INK, bold=True)
            c.rect(f"g{n}t", 8.0, y + .5, 4.4, 0.42, "E3DFD2", kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
            c.rect(f"g{n}f", 8.0, y + .5, 4.4 * fill, 0.42, COPPER, kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.5)
        T(c, "gcap", "三道閘門的示意圖（非實際數據）", 8.0, 5.55, 4.6, 0.3, 14, MUTED)
        window(c, 0.9, 4.8)
    return draw


def p02():
    cards = [("Token 總量", "顯示的 token 不等於可用的新 token：快取、推理強度與工具回合都會改變結果。"),
             ("5 小時訊息估算", "官方的估計值，不是保證的訊息數，也不是固定的 token 上限。"),
             ("每週扣額百分比", "官方多半只公布倍率或百分比，絕對額度未公開。"),
             ("API 等價美元", "成本試算，不是任何訂閱的保證額度。")]

    def draw(c):
        base(c, KICKERS[1], "「額度」其實是四種不同的東西")
        for n, (head, body) in enumerate(cards):
            x = 0.9 + n * 2.99
            c.card(f"q{n}", x, 1.95, 2.8, 3.05, WHITE, border=LINE, shadow=False)
            T(c, f"q{n}n", str(n + 1), x + .22, 2.05, 0.7, 0.6, 30, COPPER, bold=True)
            T(c, f"q{n}h", head, x + .22, 2.75, 2.4, 0.7, 20, INK, bold=True)
            T(c, f"q{n}b", body, x + .22, 3.5, 2.4, 1.45, 15, SUB)
        c.card("key", 0.9, 5.25, 11.7, 1.3, WALL, border=LINE, shadow=False)
        T(c, "key_t", "真正決定能跑多久的，是：模型加權 · 快取占比 · 單次上下文 · 工具／子代理工作量 · 5 小時／週／月上限",
          1.2, 5.45, 11.2, 0.9, 20, INK, bold=True)
    return draw


def p03():
    rows = [("Claude", "Pro US$20／月", "5h＋週；Ultra 驗證帳戶免 5h"), ("ChatGPT", "Plus US$20／月", "Work＋Codex 共用 5h＋週"),
            ("Cursor", "Plus $8／Premium $30", "第一方週池；第三方另收費"), ("Antigravity", "AI Pro 約 US$20", "5h＋週；Argon 獨立週池"),
            ("OpenCode", "Go $10／Go+ $40", "5h＋週＋月 加權共享池"), ("Kimi", "Plus ¥99（Go ¥49 無 Code）", "5h＋月共享池；無週上限"),
            ("DeepSeek", "聊天免費；API 按量", "依 token、快取、峰離峰計費")]

    def draw(c):
        base(c, KICKERS[2], "七個平台，七種算法", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛的「四種額度」。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        T(c, "h0", "平台", 5.6, 1.78, 1.7, 0.3, 14, MUTED)
        T(c, "h1", "入門價", 7.3, 1.78, 2.6, 0.3, 14, MUTED)
        T(c, "h2", "最關鍵的額度規則", 10.0, 1.78, 2.6, 0.3, 14, MUTED)
        for n, (name, price, rule) in enumerate(rows):
            y = 2.12 + n * 0.64
            line(c, f"ln{n}", 5.6, y - .06, 7.0)
            row_cells(c, f"r{n}", y, [(5.6, 1.7, name, {"color": PLAT[name.split('／')[0]]}), (7.3, 2.6, price, {}),
                                      (10.0, 2.6, rule, {"pt": 14})], pt=16, h=0.6)
    return draw


def p04():
    def draw(c):
        base(c, KICKERS[3], "價格階梯", hint="長條＝美元月價（US$500 為滿格）；人民幣方案不換算")
        names = {"Claude": "Claude", "ChatGPT／Codex": "ChatGPT", "Cursor": "Cursor", "Antigravity": "Antigravity",
                 "OpenCode": "OpenCode", "Kimi": "Kimi"}
        for n, (plat, cur, tiers) in enumerate(D.LADDER):
            y = 1.9 + n * 0.74
            color = PLAT[names[plat]]
            T(c, f"p{n}", plat, 0.9, y + .08, 2.0, 0.45, 16, color, bold=True)
            for m, (tier, price) in enumerate(tiers):
                x = 3.0 + m * 1.88
                label = f"{tier} {'$' if cur == 'USD' else '¥'}{price:,}"
                c.card(f"p{n}c{m}", x, y, 1.76, 0.5, WHITE, border=LINE, shadow=False)
                T(c, f"p{n}c{m}t", label, x + .1, y + .08, 1.58, 0.34, 14, INK, bold=True)
                if cur == "USD":
                    hbar(c, f"p{n}c{m}b", x, y + .53, 1.76, 0.07, price, 500, color)
        y = 1.9 + 6 * 0.74
        T(c, "pds", "DeepSeek", 0.9, y + .08, 2.0, 0.45, 16, PLAT["DeepSeek"], bold=True)
        for m, label in enumerate(["聊天 免費", "API 按量計費"]):
            x = 3.0 + m * 1.88
            c.card(f"pdc{m}", x, y, 1.76, 0.5, WHITE, border=LINE, shadow=False)
            T(c, f"pdc{m}t", label, x + .1, y + .08, 1.58, 0.34, 14, INK, bold=True)
    return draw


def p05():
    gates = [("Claude", "●●—"), ("ChatGPT", "●●—"), ("Cursor", "—●—"), ("Antigravity", "●●—"), ("OpenCode", "●●●"),
             ("Kimi", "●—●"), ("DeepSeek", "———")]

    def draw(c):
        base(c, KICKERS[4], "各平台的「閘門」不同")
        T(c, "lead", ["同樣叫「月費」，限制的時間尺度並不相同。", "有的是 5 小時＋週，有的多一道月池，API 則是按量計費。"],
          0.9, 1.95, 5.1, 2.4, 18, SUB, after=8)
        x0 = 6.6
        for i, h in enumerate(["5 小時", "每週", "每月"]):
            T(c, f"mh{i}", h, x0 + 2.0 + i * 1.3, 1.5, 1.2, 0.3, 14, MUTED, align=PP_ALIGN.CENTER)
        for n, (name, marks) in enumerate(gates):
            y = 1.9 + n * 0.5
            line(c, f"mln{n}", x0, y - .04, 6.0)
            T(c, f"mn{n}", name, x0, y, 1.9, 0.42, 16, PLAT[name], bold=True)
            for i, ch in enumerate(marks):
                T(c, f"m{n}_{i}", ch, x0 + 2.0 + i * 1.3, y, 1.2, 0.42, 20, COPPER if ch == "●" else MUTED,
                  bold=True, align=PP_ALIGN.CENTER)
        T(c, "mfoot", "Claude Ultra 驗證帳戶免 5h；ChatGPT Pro 100／200／500 目前無 5h 但有總額度；Cursor 舊制為雙月池；"
                      "Antigravity Pro 的 Argon 為獨立 weekly-only；Kimi 舊會員仍為 5h＋週＋月。", x0, 5.5, 6.0, 1.25, 14, MUTED)
        window(c, 0.9, 4.75)
    return draw


def brand_mark(name):
    """Path of a verified vendor mark, or None (the deck then shows text only)."""
    if not BRAND["dir"]:
        return None
    path = Path(BRAND["dir"]) / name
    return path if brand_assets.verify(path, brand_assets.ASSETS[name]["sha256"]) else None


def opencode_mark():
    return brand_mark(OPENCODE_MARK)


def two_cards(c, left, right, tag_l, tag_r, kicker, mark=None):
    for x, (title, items), color in ((0.9, left, PLAT[tag_l]), (6.8, right, PLAT[tag_r])):
        c.card(f"card{int(x)}", x, 1.8, 5.87, 4.85, WHITE, border=LINE, shadow=False)
        c.rect(f"bar{int(x)}", x, 1.8, 5.87, 0.09, color)
        has_mark = mark is not None and x > 6
        T(c, f"ttl{int(x)}", title, x + .3, 2.05, 3.0 if has_mark else 5.3, 0.55, 26, color, bold=True)
        body_h = 3.15 if has_mark else 3.75
        T(c, f"body{int(x)}", para_list(items), x + .3, 2.8, 5.35, body_h, 16, SUB, after=7)
        if has_mark:
            # wordmark alone (no words beside it); box keeps >= 2 strokes of clear space on every side
            c.picture("brand_opencode", mark, x + 3.55, 2.1, 2.0, 0.5)
            T(c, "brand_credit", OPENCODE_CREDIT, x + .3, 6.0, 5.35, 0.6, 14, MUTED)


def p06():
    left = ("Claude", [("Pro US$20／月（年付 US$200）：", "5h＋每週；Claude Code 共用額度；Fable 需另走 Usage Credits"),
                       ("Max US$100：", "5h 與週均約 Pro 的 5×"),
                       ("Ultra US$200：", "每週約 Pro 的 10×；驗證帳戶免 5h"),
                       ("", "每月 API credits（Max US$100／Ultra US$200）≠ Usage Credits（超額按 API 價計費）")])
    right = ("ChatGPT／Codex", [("Plus US$20／月：", "5h＋週；Work 與 Codex 共用"),
                              ("Pro 100／200／500：", "目前無 5h，但有總額度"),
                              ("Plus 每 5 小時 local message 官方估計：", "Astra 5–45；GPT-6.1 Sol 15–160；GPT-6 Sol 15–150；GPT-6 Luna 350–3,000"),
                              ("", "這是估計，不是保證的訊息數或固定 token 上限")])

    def draw(c):
        base(c, KICKERS[5], None)
        two_cards(c, left, right, "Claude", "ChatGPT", KICKERS[5])
    return draw


def p07():
    def draw(c):
        base(c, KICKERS[6], "Cursor：週池倍率", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛的「Claude 與 ChatGPT」。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        for n, (tier, price, mult) in enumerate(D.CURSOR_MULTIPLIERS):
            y = 1.85 + n * 0.58
            T(c, f"cm{n}", f"{tier} ${price}", 5.6, y, 1.8, 0.45, 16, PLAT["Cursor"], bold=True)
            hbar(c, f"cmb{n}", 7.5, y + .04, 3.9, 0.36, mult, 50, PLAT["Cursor"])
            T(c, f"cmv{n}", f"{mult}×", 11.55, y, 1.1, 0.45, 16, INK, bold=True)
        items = [("", "第一方模型週池，由 Cursor Agent／CLI、Cloud Agents、Grok Bot、Grok Chat／Voice／Imagine 共用"),
                 ("", "第三方模型：Plus 不支援；Premium 起另購預付 credit，按 API list price"),
                 ("", "舊制 Pro／Pro+／Ultra：兩個月池（Cursor Models／Other Models）；切換新制可選但永久")]
        T(c, "cnotes", para_list(items), 5.6, 4.35, 7.0, 2.4, 15, SUB, after=6)
        mark = brand_mark(CURSOR_MARK)
        if mark:  # lockup alone, unaltered, right of the headline; credit sits in the free band under the notes
            c.picture("brand_cursor", mark, 9.9, 1.0, 2.7, 0.64, align="right")
            T(c, "brand_credit", CURSOR_CREDIT, 5.6, 6.2, 7.0, 0.5, 14, MUTED)
    return draw


def p08():
    left = ("Google Antigravity", [("Google AI Pro 約 US$20／月：", "5h＋weekly；付費 Pro 另有 Argon 獨立 weekly-only 額度"),
                                  ("Ultra 5× US$100／Ultra 20× US$200：", "相對 Pro 的 token-worth 倍率；仍有 weekly"),
                                  ("", "Claude 5.5 須付費、非試用"),
                                  ("", "超額 AI Credits 可設 Never／Always；尚不支援 BYOK 增加額度")])
    right = ("OpenCode Go", [("Go US$10／Go+ US$40：", "5h、週、月三層加權共享限制；僅單成員 workspace"),
                            ("每模型參考額度：", "5h＝月額的 20%、週＝50%、月＝100%"),
                            ("例：", "在月額 US$15 的模型花 US$1，約用掉全月池 6.67%；在 US$60 的模型約 1.67%"),
                            ("", "「每模型月額」是共享池的消耗權重，不是可疊加的獨立錢包")])

    def draw(c):
        base(c, KICKERS[7], None)
        two_cards(c, left, right, "Antigravity", "OpenCode", KICKERS[7], mark=opencode_mark())
    return draw


def p09():
    tiers = [("Free／Adagio", "¥0", "無 Code", "網頁基本／限量使用"), ("Go", "¥49", "沒有", "網頁 K3.1 Pro；不能當 Coding Plan"),
             ("Plus", "¥99", "有", "K3.1 Pro 與 K3；K3.1 Pro 最高 256K"), ("Pro", "¥199", "有", "K3.1 Pro 最高 1M；含 Highspeed 模型"),
             ("Max", "¥699", "有", "更高 Agent credits、併發"), ("Ultra", "¥1,399", "有", "最高等級 credits；以購買頁為準")]

    def draw(c):
        base(c, KICKERS[8], "Kimi 新制：Plus 起才有 Code")
        for i, h in enumerate(["方案", "月費", "Code", "模型／權益"]):
            T(c, f"kh{i}", h, [0.9, 2.7, 3.9, 5.0][i], 1.78, 2.0, 0.3, 14, MUTED)
        for n, (name, price, code, note) in enumerate(tiers):
            y = 2.12 + n * 0.7
            line(c, f"kln{n}", 0.9, y - .06, 7.5)
            row_cells(c, f"kr{n}", y, [(0.9, 1.75, name, {"color": PLAT["Kimi"]}), (2.7, 1.1, price, {}),
                                       (3.9, 1.0, code, {"color": GOOD if code == "有" else MUTED, "bold": True}),
                                       (5.0, 3.4, note, {"pt": 14})], pt=16, h=0.62)
        items = [("新會員 Kimi Code：", "滾動 5 小時限額＋月度共享額度；沒有每週限額（5h 桶大小未公開）"),
                 ("額度共用：", "Code、Work、PPT、Deep Research、Agent、Claw 同一池；未使用不結轉")]
        T(c, "knotes", para_list(items), 8.7, 1.75, 3.9, 2.55, 15, SUB, after=6)
        window(c, 8.7, 4.4)
    return draw


def p10():
    rows = [("快取輸入（離峰）", "cache", "offpeak"), ("一般輸入（離峰）", "input", "offpeak"), ("輸出（離峰）", "output", "offpeak"),
            ("快取輸入（尖峰）", "cache", "peak"), ("一般輸入（尖峰）", "input", "peak"), ("輸出（尖峰）", "output", "peak")]

    def draw(c):
        base(c, KICKERS[9], "DeepSeek API：公開單價")
        for x, w, h in ((0.9, 3.3, "US$／1M tokens"), (4.3, 2.3, "V4.1 Flash"), (6.8, 2.3, "V4 Pro")):
            T(c, f"dh{x}", h, x, 1.78, w, 0.3, 14, MUTED)
        for n, (label, kind, per) in enumerate(rows):
            y = 2.12 + n * 0.66
            line(c, f"dln{n}", 0.9, y - .06, 8.2)
            row_cells(c, f"dr{n}", y, [(0.9, 3.3, label, {}), (4.3, 2.3, price_str(D.DEEPSEEK['V4.1 Flash'][per][kind]),
                                                                 {"color": INK, "bold": True}),
                                       (6.8, 2.3, price_str(D.DEEPSEEK['V4 Pro'][per][kind]),
                                        {"color": INK, "bold": True})], pt=16, h=0.5)
        T(c, "dctx", "上下文約 1M tokens；兩款皆支援 Thinking（low／high／max）", 0.9, 6.15, 8.2, 0.4, 14, MUTED)
        items = [("尖峰＝離峰價 ×2；", "UTC 週一至五 01:00–04:00、06:00–10:00（台灣約 09:00–12:00、14:00–18:00）"),
                 ("Search／Fetch 另計：", "每 1,000 次成功呼叫 US$0.75（11/01 起）"),
                 ("", "沒有可證實的「API 包月無限」方案")]
        T(c, "dnotes", para_list(items), 9.4, 1.85, 3.2, 4.6, 14, SUB, after=8)
    return draw


def p11():
    bars = [("Flash 離峰", ("V4.1 Flash", "offpeak")), ("Flash 尖峰", ("V4.1 Flash", "peak")),
            ("Pro 離峰", ("V4 Pro", "offpeak")), ("Pro 尖峰", ("V4 Pro", "peak"))]

    def draw(c):
        base(c, KICKERS[10], "高快取 Agent：每 1 億 tokens 要多少錢", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛的「DeepSeek 公開單價」。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        for n, (label, key) in enumerate(bars):
            y = 1.85 + n * 0.52
            v = D.DOC_COST_100M_USD[key]
            T(c, f"cb{n}", label, 5.6, y, 1.8, 0.42, 16, PLAT["DeepSeek"], bold=True)
            hbar(c, f"cbb{n}", 7.45, y + .04, 3.5, 0.34, v, 17.248, PLAT["DeepSeek"])
            T(c, f"cbv{n}", f"US${v:g}", 7.45 + 3.5 * v / 17.248 + .1, y, 1.3, 0.42, 16, INK, bold=True)
        items = [("假設：", "每 100M＝92M 快取輸入＋7M 新輸入＋1M 輸出；不含 cache write、搜尋與稅"),
                 ("月量 1B tokens（同比例）：", "Flash 離峰約 US$19.26／尖峰 38.52；Pro 離峰 86.24／尖峰 172.48"),
                 ("Kimi API（人民幣，每 100M）：", "K3.1 Pro ¥278.60；Highspeed ¥437.60；K3 ¥424.00"),
                 ("", "這是 API 成本試算，不是任何訂閱的保證額度")]
        T(c, "cnotes", para_list(items), 5.6, 4.05, 7.0, 2.7, 14, SUB, after=5)
    return draw


def p12():
    head = ("", "Claude Max／Ultra", "ChatGPT Pro 100／200／500")
    rows = [("每月可申領", "US$100／US$200", "US$100／US$200／US$500"),
            ("新訂閱資格", "滿 7 天；須啟用連結 Console 組織", "滿 7 天；須連結 API 組織"),
            ("可用於", "Claude API、Managed Agents、Agent SDK", "OpenAI API 的合資格模型／工具"),
            ("不可用於", "互動式 Claude Code、訂閱超額 Usage Credits", "登入版 Work／Codex 額度；API Key 的 Codex 用量"),
            ("未使用", "不累積到下一帳單週期", "不累積；首月可能按剩餘期間比例發放"),
            ("注意", "Usage Credits（超額按 API 價）≠ 每月 API Credits", "Chat／Work／Codex allowance 與 API 金額要分開看")]

    def draw(c):
        base(c, KICKERS[11], "API 贈額 ≠ 訂閱版 Agent 額度")
        T(c, "ah1", head[1], 3.1, 1.78, 4.5, 0.3, 14, PLAT["Claude"], bold=True)
        T(c, "ah2", head[2], 7.8, 1.78, 4.8, 0.3, 14, PLAT["ChatGPT"], bold=True)
        for n, (label, a, b) in enumerate(rows):
            y = 2.12 + n * 0.75
            line(c, f"aln{n}", 0.9, y - .06, 11.7)
            row_cells(c, f"ar{n}", y, [(0.9, 2.0, label, {}), (3.1, 4.5, a, {"pt": 16}), (7.8, 4.8, b, {"pt": 16})], pt=16, h=0.7)
    return draw


def p13():
    def draw(c):
        base(c, KICKERS[12], "同一框架下的模型比較", hint="Terminal-Bench 4.0 · Mini-SWE-agent · Vals AI 2026-10-29")
        top = max(s for _, s, _ in D.TB4_INDEPENDENT)
        for n, (name, score, cost) in enumerate(D.TB4_INDEPENDENT):
            y = 1.9 + n * 0.62
            T(c, f"tn{n}", name, 0.9, y, 2.9, 0.45, 15, INK, bold=True)
            hbar(c, f"tb{n}", 3.85, y + .05, 2.5, 0.34, score, 70, COPPER if score == top else "B8B2A2")
            T(c, f"tv{n}", f"{score:.2f}%｜US${cost:.2f}", 3.85 + 2.5 * score / 70 + .08, y, 2.1, 0.45, 14, SUB)
        T(c, "tfoot", "Gemini 4 Carbon 不等於 Antigravity 的 Gemini 4 Argon；廠商自測分數另列，口徑不同。", 0.9, 5.75, 7.4, 0.8, 14, MUTED)
        items = [("", "分差很小時不要過度解讀（抽樣與評測環境）"),
                 ("", "廠商自測的分數口徑不同，不能直接排進這個榜"),
                 ("", "Terminal-Bench 2.0／3.0／4.0 不可互相換算")]
        T(c, "tnotes", para_list(items), 8.7, 1.85, 3.9, 2.4, 15, SUB, after=6)
        window(c, 8.7, 4.4)
    return draw


def p14():
    rows = [("聊天可選模型", "只在網頁／App 模型選單回答問題", "免費聊天 ≠ 免費 CLI、IDE、自動化或模型 API"),
            ("Coding Agent／CLI", "可讀 repo、用工具、下指令；可能需本機運行或綁帳號", "有 Claude 模型 ≠ 自動包含 Claude Code 服務"),
            ("雲端 Agent", "在服務端跑 repo／Browser／排程，電腦關閉後仍可工作", "免費 Codex 本機版 ≠ 免費 Codex Cloud"),
            ("API 模型", "API Key 依每百萬 tokens 計費，部分支援第三方 harness", "聊天訂閱 ≠ 送同款模型的外部 API Key")]

    def draw(c):
        base(c, KICKERS[13], "「可用」有四種意思")
        for x, w, h in ((0.9, 2.3, "名詞"), (3.4, 4.6, "實際權限"), (8.2, 4.4, "常見誤判")):
            T(c, f"vh{x}", h, x, 1.78, w, 0.3, 14, MUTED)
        for n, (a, b, d) in enumerate(rows):
            y = 2.15 + n * 1.1
            c.card(f"v{n}", 0.9, y, 11.7, 0.98, WHITE, border=LINE, shadow=False)
            c.rect(f"v{n}bar", 0.9, y, 0.08, 0.98, COPPER)
            row_cells(c, f"vr{n}", y + .12, [(1.2, 2.1, a, {"pt": 17}), (3.4, 4.6, b, {"pt": 15}),
                                              (8.2, 4.3, d, {"pt": 15, "color": BAD})], pt=16, h=0.85)
    return draw


def p15():
    rows = [("Claude", "Pro 5h 至少 Free 的 5×；Max 5×、Ultra 10×（週）", "Pro 週額與絕對 token 量"),
            ("ChatGPT", "Plus 每 5 小時 local message 估計", "週上限；Pro 的絕對額度"),
            ("Cursor", "Plus 1×／Premium 4×／Super 15×／Ultra 50×", "週池的絕對美元容量"),
            ("Antigravity", "Ultra 5×／20×（相對 Pro）", "固定 token／月"),
            ("OpenCode", "模型參考價；5h 20%／週 50%／月 100%", "（可重算；模型調價會變）"),
            ("Kimi", "Plus 2×／Pro 4×／Max 14×／Ultra 28× Agent Credits", "5h、月的絕對值"),
            ("DeepSeek", "官方單價（快取／峰離峰）", "（用量固定時可精算）")]

    def draw(c):
        base(c, KICKERS[14], "官方確值，與官方未公開的", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛的「可用的四種意思」。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        T(c, "uh1", "官方可量化", 7.3, 1.78, 2.9, 0.3, 14, MUTED)
        T(c, "uh2", "官方未公開", 10.3, 1.78, 2.3, 0.3, 14, MUTED)
        for n, (name, a, b) in enumerate(rows):
            y = 2.12 + n * 0.64
            line(c, f"uln{n}", 5.6, y - .06, 7.0)
            row_cells(c, f"ur{n}", y, [(5.6, 1.6, name, {"color": PLAT[name]}), (7.3, 2.9, a, {"pt": 14}),
                                       (10.3, 2.3, b, {"pt": 14, "color": BAD})], pt=15, h=0.6)
    return draw


def p16():
    rows = [("單一約 US$20 綜合訂閱", "ChatGPT Plus", "兼顧 Chat 與 Codex／Work；Agent 仍有 5h＋週限制"),
            ("高品質 Claude Code", "Claude Pro US$20", "5h＋週雙重門檻；Fable 不含於一般 Pro 額度"),
            ("已有舊版 Cursor Pro", "先保留並實測新制", "舊制兩個月池；新制為跨 Grok／Cursor 共用週池"),
            ("Gemini 4 Argon／Agent IDE", "Google AI Pro US$20", "Argon 另有獨立週額度；總上限不公開"),
            ("用 agent harness 接便宜模型", "OpenCode Go $10／Go+ $40", "共享加權池；Contributor 模型有訓練與區域限制"),
            ("訂閱式 coding（Kimi K3.1 Pro）", "Kimi Plus ¥99／Pro ¥199", "5h 滾動＋月共享池；新訂戶無週上限"),
            ("低成本按量使用", "DeepSeek API（Flash／Pro）", "依峰離峰、快取與輸出計費；必須設支付限額")]

    def draw(c):
        base(c, KICKERS[15], "依情境選，不是一刀切")
        for x, h in ((0.9, "你的目標"), (4.6, "較合理的選擇"), (8.0, "主要代價")):
            T(c, f"sh{x}", h, x, 1.78, 3.0, 0.3, 14, MUTED)
        for n, (a, b, d) in enumerate(rows):
            y = 2.12 + n * 0.64
            line(c, f"sln{n}", 0.9, y - .06, 11.7)
            row_cells(c, f"sr{n}", y, [(0.9, 3.6, a, {"pt": 15}), (4.6, 3.3, b, {"pt": 15, "color": COPPER, "bold": True}),
                                       (8.0, 4.6, d, {"pt": 14})], pt=15, h=0.6)
    return draw


def p17():
    def draw(c):
        base(c, KICKERS[16], "不要信排名，自己測")
        items = [("條件一致：", "同一 repo commit、授權範圍、tool set 與問題；記錄 effort"),
                 ("至少重跑 3 次：", "取中位數並記錄失敗原因"),
                 ("72 小時 A/B：", "記錄每輪前後的 5h／週／月配額百分比、cache hit、新輸入、output、耗時與驗收")]
        T(c, "tsteps", para_list(items), 0.9, 1.95, 5.2, 2.6, 16, SUB, after=7)
        T(c, "wcap", "100 分工作流評估的權重", 6.6, 1.6, 6.0, 0.35, 14, MUTED)
        for n, (label, wgt) in enumerate(D.EVAL_WEIGHTS):
            y = 2.05 + n * 0.58
            T(c, f"w{n}", label, 6.6, y, 3.0, 0.42, 15, INK, bold=True)
            hbar(c, f"wb{n}", 9.7, y + .05, 2.2, 0.32, wgt, 20, COPPER)
            T(c, f"wv{n}", str(wgt), 9.7 + 2.2 * wgt / 20 + .1, y, 0.6, 0.42, 15, INK, bold=True)
        window(c, 0.9, 4.75)
    return draw


def p18():
    rows = [("「Claude 整體配額被官方砍半」", "大量自述，但沒有同條件對照與官方降額公告；判定為未證實"),
            ("「Antigravity Pro Argon 一律只有 4 次 prompt」", "上下文、工具回合與 effort 差異很大，不能推算固定次數"),
            ("「Kimi ¥199／¥699 一定比 Claude US$20 更不耐用」", "負載、新舊制與模型加權不同，無法得出定量結論"),
            ("「DeepSeek 10 億 token 試算＝US$20 包月」", "只是費率乘法；實際帳單仍按量計費"),
            ("「Terminal-Bench 差 1% 就有確定高下」", "抽樣與評測環境有誤差；榜單的 $／題是測試成本，不是訂閱扣費")]

    def draw(c):
        base(c, KICKERS[17], "不能直接證實的說法")
        for n, (claim, why) in enumerate(rows):
            y = 1.85 + n * 0.95
            c.card(f"x{n}", 0.9, y, 11.7, 0.82, WHITE, border=LINE, shadow=False)
            c.rect(f"x{n}bar", 0.9, y, 0.08, 0.82, BAD)
            T(c, f"x{n}c", claim, 1.2, y + .08, 11.2, 0.4, 18, INK, bold=True)
            T(c, f"x{n}w", why, 1.2, y + .46, 11.2, 0.32, 15, SUB)
    return draw


def p19():
    rows = [("Claude", "到 Usage 確認 5h、weekly 與 Fable 限額；Claude Code 與網頁共用額度"),
            ("OpenAI", "Free／Go 可用本機 Codex；Codex Cloud 需 Plus 以上；從 Settings→Usage 讀剩額"),
            ("Cursor", "先辨識舊 Pro 是 usage-based 還是更舊的 request-based；不要為試 Bot 直接切換"),
            ("Antigravity", "區分試用與正式付費；在 App／CLI／IDE 選單分別確認 Argon 是否已推送"),
            ("OpenCode", "看 5h／weekly／monthly 三個共用指標；免費模型只當備援"),
            ("Kimi", "先分清新 Plus／Pro 或舊會員；用 Code /usage 重複測同一模型與 effort"),
            ("DeepSeek", "官方 API 與第三方代管分開計費；先設預算上限，記錄 cache hit 與 Search／Fetch 量")]

    def draw(c):
        base(c, KICKERS[18], "訂閱前，先逐項確認", tint=WALL)
        frame(c, *FRAME)
        T(c, "frame_cap", "剛剛的「不能直接證實的說法」。", 0.9, 4.75, 4.4, 0.3, 14, SUB)
        for n, (name, text) in enumerate(rows):
            y = 1.8 + n * 0.7
            line(c, f"cln{n}", 5.6, y - .06, 7.0)
            T(c, f"cn{n}", name, 5.6, y, 1.5, 0.6, 15, PLAT[name if name in PLAT else "ChatGPT"], bold=True)
            T(c, f"ct{n}", text, 7.15, y, 5.5, 0.62, 14, SUB)
    return draw


def p20():
    levels = [("A", "官方現行條款、產品頁、官方回覆"), ("B", "獨立榜單；可重現的 GitHub issue"), ("C", "社群自述、小樣本（只作情境參考）")]

    def draw(c):
        base(c, KICKERS[19], None)
        T(c, "big1", "先分清是哪一種額度，再談 CP 值。", 0.9, 1.3, 11.6, 0.9, 38, INK, bold=True)
        T(c, "big2", "官方規則優先；社群與實測只用來評估風險，不能當成配額承諾。", 0.9, 2.35, 11.6, 0.6, 20, SUB)
        for n, (lv, text) in enumerate(levels):
            x = 0.9 + n * 3.99
            c.card(f"lv{n}", x, 3.35, 3.8, 1.35, WHITE, border=LINE, shadow=False)
            T(c, f"lv{n}a", f"證據 {lv}", x + .25, 3.5, 3.3, 0.45, 20, COPPER, bold=True)
            T(c, f"lv{n}b", text, x + .25, 4.0, 3.3, 0.6, 15, SUB)
        T(c, "caveat", [f"資料快照 {D.SNAPSHOT}（{D.VERSION}）；來源文件並未登入各供應商帳戶做端到端額度測試。",
                        "價格與額度以結帳頁與 Usage dashboard 為準；本簡報不是保證額度或投資建議。"],
          0.9, 5.05, 11.7, 1.5, 16, MUTED, after=6)
    return draw


# ------------------------------------------------------------------------------------------------ deck
SRC = [("", ""), ("[決策摘要]", ""), ("[C1–C3][O1][X1][G1][P1][K1][D2]", ""), ("[C1][O1][X3][G1][P1][K1][D2]", ""),
       ("[C1][O1][X1][G1][P1][K2][D2]", ""), ("[C1–C4][O1–O2]", ""), ("[X1–X3]", ""), ("[G1–G4][P1–P3]", ""),
       ("[K1–K3]", ""), ("[D2–D4]", ""), ("[D2][K4]；23.4 重算", ""), ("[C3–C4][O2]", ""), ("[M01]；8.2", ""),
       ("13.1", ""), ("21", ""), ("決策摘要、第 5／21.1 節", ""), ("第 11／21.2 節", ""), ("23.3", ""), ("23.5", ""), ("23.6 證據等級", "")]
TALK = ["封面：七個平台、七種額度算法。", "先分清四種不同的「額度」。", "七平台的入門價與最關鍵的額度規則。",
        "價格階梯；長條只比較美元，人民幣不換算。", "各平台的閘門：5 小時、週、月。", "Claude 與 ChatGPT／Codex 的方案與官方估計。",
        "Cursor 新制週池倍率；舊制雙月池。", "Antigravity 與 OpenCode Go 的規則。", "Kimi 新制：Plus 起才有 Kimi Code。",
        "DeepSeek 公開單價與峰離峰。", "同一種高快取用法下，每 1 億 tokens 的 API 成本試算。", "API 贈額不等於訂閱版 Agent 額度。",
        "同框架的獨立比較；不跨口徑排名。", "「可用」的四種意思。", "官方確值與未公開項目。", "依情境選擇。", "自己測：統一條件的 A/B。",
        "不能直接證實的說法。", "訂閱前逐項確認。", "結語與證據等級。"]


def build(output, hold=HOLD_MS, duration=MORPH_MS, fonts=None, brand_dir=None):
    BRAND["dir"] = brand_dir
    if fonts:
        K.set_fonts(*fonts)
    win_tl, win_br = (0.9, 4.8, WIN_W), (8.7, 4.4, WIN_W)
    world = World(gap=0.6)
    world.first(p01())
    world.add(p02(), "zoom_in", window=win_tl)
    world.add(p03(), "pull_back", frame=FRAME)
    world.add(p04(), "pan_right")
    world.add(p05(), "pan_right")
    world.add(p06(), "zoom_in", window=(0.9, 4.75, WIN_W))
    world.add(p07(), "pull_back", frame=FRAME)
    world.add(p08(), "pan_right")
    world.add(p09(), "pan_right")
    world.add(p10(), "zoom_in", window=win_br)
    world.add(p11(), "pull_back", frame=FRAME)
    world.add(p12(), "pan_right")
    world.add(p13(), "pan_right")
    world.add(p14(), "zoom_in", window=win_br)
    world.add(p15(), "pull_back", frame=FRAME)
    world.add(p16(), "pan_right")
    world.add(p17(), "pan_right")
    world.add(p18(), "zoom_in", window=(0.9, 4.75, WIN_W))
    world.add(p19(), "pull_back", frame=FRAME)
    world.add(p20(), "pan_down")

    def hud(c, j):
        for n in range(N):
            c.rect(f"pip{n}", 0.9 + n * 0.3, 0.3, 0.24, 0.04, COPPER if n == j else "CFCABB")
        T(c, "foot", FOOTER, 4.6, 6.84, 8.0, 0.26, 14, MUTED, align=PP_ALIGN.RIGHT)

    def notes(j):
        return (f"{TALK[j]}\n\n來源碼（對應使用者文件 {D.VERSION} 的原始來源索引）：{SRC[j][0]}\n"
                f"資料快照 {D.SNAPSHOT}；價格與額度可能已變動，發布前需重新核對。數字取自使用者提供的文件，未獨立查證。"
                + ("\n" + CURSOR_CREDIT + "（官方品牌頁，存取日 2026-11-07；依指認性使用評估，非個別授權。）" if j == 6 and brand_mark(CURSOR_MARK) else "")
                + ("\n" + OPENCODE_CREDIT + "（Logo 使用規則：官方品牌頁，存取日 2026-11-07。）" if j == 7 and opencode_mark() else "")
                + "\nPowerPoint 原生 Morph 實播狀態：NOT RUN。")

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
    ap.add_argument("--output", type=Path, default=Path("build/ai-subscriptions/ai-subscriptions-deck.pptx"))
    ap.add_argument("--hold", type=int, default=HOLD_MS, help="per-slide hold (ms); set from narration length")
    ap.add_argument("--duration", type=int, default=MORPH_MS, help="Morph transition (ms)")
    ap.add_argument("--font-sans", default=K.FONTS["sans"], help="must be installed where the deck is played")
    ap.add_argument("--font-serif", default=K.FONTS["serif"])
    ap.add_argument("--font-mono", default=K.FONTS["mono"])
    ap.add_argument("--brand-dir", type=Path, default=Path("build/ai-subscriptions/brand"),
                    help="where scripts/brand_assets.py wrote the OpenCode wordmark (used only if SHA256 matches)")
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    world = build(args.output, args.hold, args.duration, (args.font_sans, args.font_serif, args.font_mono),
                  args.brand_dir)
    print(f"{args.output}: {N} slides, {N - 1} native Morph transitions (SPIKE; PowerPoint playback NOT RUN)")
    print("zoom ratios:", sorted({round(z, 2) for _, _, _, z in world.describe()}))


if __name__ == "__main__":
    main()
