"""Data for the AI-subscription comparison deck, transcribed from the user's document
"AI Coding / Agent 七平台訂閱比較：官方與社群深度查驗 v5.1" (snapshot 2026-11-03).

Source of truth is that document, NOT this repository: figures were NOT re-verified against the vendors'
pages (prices, quotas and model lists change; the deck must carry the snapshot date). Source codes such as
[C1] or [D2] refer to the document's own source index and are kept so every slide can be traced back.
Pure data + arithmetic (stdlib only) so tests can recompute every derived number.
"""

SNAPSHOT = "2026-11-03"
VERSION = "v5.1"

# ---- DeepSeek API unit prices, US$ per 1M tokens [D2] ----------------------------------------------------
DEEPSEEK = {
    "V4.1 Flash": {"offpeak": {"cache": 0.003, "input": 0.15, "output": 0.60},
                   "peak": {"cache": 0.006, "input": 0.30, "output": 1.20}},
    "V4 Pro": {"offpeak": {"cache": 0.022, "input": 0.66, "output": 1.98},
               "peak": {"cache": 0.044, "input": 1.32, "output": 3.96}},
}

# ---- Kimi API unit prices, CNY per 1M tokens: implied by the document's own table [K4] ---------------------
KIMI_API = {
    "K3.1 Pro": {"cache": 1.30, "input": 13.0, "output": 68.0},
    "K3.1 Pro Highspeed": {"cache": 1.30, "input": 26.0, "output": 136.0},
    "K3": {"cache": 2.00, "input": 20.0, "output": 100.0},
}

# Workload assumption used by the document: per 100M tokens (millions below).
MIX = {"cache": 92.0, "input": 7.0, "output": 1.0}


def cost_per_100m(unit):
    """Cost of one 100M-token mix at the given per-1M unit prices."""
    return sum(MIX[k] * unit[k] for k in MIX)


# Values as printed in the document (2A / 23.4) – the tests recompute them.
DOC_COST_100M_USD = {("V4.1 Flash", "offpeak"): 1.926, ("V4.1 Flash", "peak"): 3.852,
                     ("V4 Pro", "offpeak"): 8.624, ("V4 Pro", "peak"): 17.248}
DOC_COST_1B_USD = {("V4.1 Flash", "offpeak"): 19.26, ("V4.1 Flash", "peak"): 38.52,
                   ("V4 Pro", "offpeak"): 86.24, ("V4 Pro", "peak"): 172.48}
DOC_COST_100M_CNY = {"K3.1 Pro": 278.60, "K3.1 Pro Highspeed": 437.60, "K3": 424.00}

# ---- OpenCode Go reference limits, US$ per model: (5h, week, month) [P1] ----------------------------------
GO_FRACTIONS = (0.20, 0.50, 1.00)  # 5h = 20 %, week = 50 %, month = 100 % of the monthly reference
GO_MODELS = {
    "GPT-6 Luna": {"go": (3, 7.5, 15), "go_plus": (12, 30, 60)},
    "Claude Haiku 5.5": {"go": (3, 7.5, 15), "go_plus": (12, 30, 60)},
    "Muse Spark 1.3 Contributor": {"go": (12, 30, 60), "go_plus": (24, 60, 120)},
    "Gemini 4 Argon Contributor": {"go": (12, 30, 60), "go_plus": (48, 120, 240)},
}

# ---- Terminal-Bench 4.0, same Mini-SWE-agent framework (Vals AI, observed 2026-10-29) [M01] -----------------
TB4_INDEPENDENT = [("Claude Opus 5.5", 65.15, 13.20), ("Claude Sonnet 5.5", 64.14, 16.51),
                   ("Kimi K3.1 Pro", 63.64, 4.57), ("Gemini 4 Carbon（非 Argon）", 63.13, 7.45),
                   ("GPT-6 Astra", 59.60, 9.58), ("Claude Fable 5.1", 58.08, 17.18)]

# ---- 100-point private evaluation weights (section 11) -----------------------------------------------------
EVAL_WEIGHTS = [("Repo 理解／定位", 20), ("實作正確性", 20), ("Agent 工具效率", 15), ("長任務穩定性", 15),
                ("設計與實際可用性", 10), ("中文與指令遵循", 10), ("成本／速度／可用額度", 10)]

# ---- Plan ladders as printed in the document (price, currency) ---------------------------------------------
LADDER = [
    ("Claude", "USD", [("Pro", 20), ("Max", 100), ("Ultra", 200)]),
    ("ChatGPT／Codex", "USD", [("Go", 8), ("Plus", 20), ("Pro 100", 100), ("Pro 200", 200), ("Pro 500", 500)]),
    ("Cursor", "USD", [("Plus", 8), ("Premium", 30), ("Super", 100), ("Ultra", 200)]),
    ("Antigravity", "USD", [("AI Pro 約", 20), ("Ultra 5×", 100), ("Ultra 20×", 200)]),
    ("OpenCode", "USD", [("Go", 10), ("Go+", 40)]),
    ("Kimi", "CNY", [("Go", 49), ("Plus", 99), ("Pro", 199), ("Max", 699), ("Ultra", 1399)]),
]
CURSOR_MULTIPLIERS = [("Plus", 8, 1), ("Premium", 30, 4), ("Super", 100, 15), ("Ultra", 200, 50)]

# ---- Added 2026-11-10 for the YouTube deck: values from the user's verified storyboard v2.1 (official pages, 2026-11-10) ----
CHECK_DATE = "2026-11-10"
CLAUDE_TIERS = [("Pro", 20, "含 Claude Code"), ("Max", 100, "約 Pro 的 5 倍"), ("Ultra", 200, "每週約 Pro 的 10 倍")]
KIMI_TIERS_CNY = {"Go": 49, "Plus": 99}  # Go has no Kimi Code; Plus includes it (mainland-China CNY prices)
SEARCH_FETCH_PER_1000_USD = 0.75  # DeepSeek Search / Fetch, per 1,000 successful requests, on top of token cost
OPENCODE_EXAMPLE = (1, 15)  # US$1 spent on a model whose monthly reference is US$15 -> 6.67 % of the monthly pool
