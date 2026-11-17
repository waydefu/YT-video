"""Content of the classroom deck "AI 與 Agent 入門" (non-technical students, ~45-50 min, click to advance).

Facts come from the user's own verified Google Docs (not re-verified here against the vendors' live pages):
  - "AI 訂閱額度比較｜YouTube 分鏡 v2.1（官方來源複核 2026-11-10）"  -> prices, gates, API examples   (codes OFFICIAL-1110)
  - "AI訂閱額度比較_2026-11-03.docx" v5.1 sections 8, 9, 13, 15-20      -> model line-ups, Terminal-Bench 4.0 (Vals AI)
  - "AI Coding Agent 工程品質研究｜Agent Skills × Claude Code Mods｜2026-11-13" -> skills, mods, hooks, MCP
Concept slides (agent, context, .md, effort) are teaching explanations, not benchmarks; no numbers are invented.
Everything price-like carries CHECK_DATE and must be re-checked on the vendors' pages before class.
"""

CHECK_DATE = "2026-11-10"
GOOGLE_CHECK_DATE = "2026-11-17"  # Google / Antigravity rows re-read from the official docs pages (via a page summary, not verbatim)
CHAPTERS = ["Agent", "材料", "思考", "公司", "模型", "收費", "免費", "選擇"]

# scene id -> chapter index (None = before the chapter navigation)
SCENE_CHAPTER = {
    "cover": None, "menu": None,
    "a_chat": 0, "a_loop": 0, "a_do": 0,
    "b_four": 1, "b_ctx": 1, "b_md": 1, "b_skill": 1, "b_mod": 1, "b_sum": 1,
    "c_think": 2, "c_names": 2,
    "d_ring": 3, "d_role": 3,
    "e_scale": 4, "e_claude": 4, "e_openai": 4, "e_google": 4, "e_kd": 4, "e_co": 4, "e_bench": 4, "e_read": 4,
    "f_kinds": 5, "f_token": 5, "f_gates": 5, "f_ladder": 5, "f_trap": 5, "f_api": 5,
    "g_free": 6, "g_kinds": 6,
    "h_pick": 7, "h_check": 7, "h_myth": 7, "h_end": 7,
}

# Talking points for the speaker notes (plain spoken Chinese). Sources are in docs/CLASSROOM-AI-AGENTS.md.
NOTES = {
    "cover": "今天不教寫程式。目標是讓大家聽得懂新聞和朋友在聊的「Agent」是什麼、有哪幾家、怎麼付錢。右上的圈圈會一直擴散，是轉場動畫的示範，不代表內容。",
    "menu": "今天八個章節：Agent 是什麼、它需要什麼、思考程度、有哪幾家公司、模型強弱、怎麼收費、免費額度、怎麼選。左邊會一直顯示我們講到哪。",
    "a_chat": "聊天機器人是你問一句它答一句。Agent 是你給一個目標，它自己拆步驟、用工具去做。差別不在聰明，而在它能動手、能檢查。",
    "a_loop": "Agent 的工作循環：看（讀檔案、搜尋）、想（決定下一步）、做（改檔、下指令）、檢查（結果對嗎）。不對就回到『看』再來一輪。每一步點一下。",
    "a_do": "它能幹嗎：改程式、查資料、整理檔案、跑測試。但也要小心：它會出錯，而且做錯時可能很有自信；用量會被扣額度；它有權限改檔案，所以要設邊界。",
    "b_four": "把 Agent 想成四塊拼起來：模型是大腦，工具是雙手，上下文是桌面，說明書是規則。接下來逐個講後三個。",
    "b_ctx": "上下文就是它這次工作『桌面上』的東西：說明書、對話、讀過的檔案、工具的結果。桌面有上限，用 token 計算；主流模型約在二十五萬到一百萬 token 之間（依模型）。快滿時它會把舊的內容壓成摘要，所以長任務中途可能『忘記』細節。",
    "b_md": ".md 是 Markdown 純文字檔。專案裡放一份，工具名稱不同：Claude Code 叫 CLAUDE.md，很多工具用 AGENTS.md。每次開工它都先讀，等於給新同事的一張規則便條。",
    "b_skill": "Skill（技能包）是一個資料夾，裡面的 SKILL.md 寫某件事的做法，Anthropic 在 2025 年 10 月提出。差別是：說明書每次都讀、放通用規則；Skill 要用到才載入，放專門做法，所以不佔桌面。",
    "b_mod": "Mod 是 Claude Code 在 2026 年 10 月公開的功能：用 TypeScript 寫的小程式，可以在事件前後介入、改行為和畫面。官方範例有 blast-radius（危險指令先提醒）。重點風險：Mod 和 Claude Code 共用你電腦的權限，不是沙盒，陌生來源不要亂裝。",
    "b_sum": "一張圖分清：.md 是規則（每次都讀）、Skill 是做法（需要才讀）、MCP 是接外部工具和資料、Mod 是改行為和畫面。四個互補，不是同一個東西。",
    "c_think": "思考程度就是它『想多久』。像考試：簡單題憑直覺，難題要打草稿。想得多通常更準，但更慢、更花額度。所以改錯字用低檔，難題才開高檔。",
    "c_names": "各家叫法不同：OpenAI 從 Instant 到 Extra High；Kimi K3.1 Pro 和 DeepSeek 是 low、high、max；Claude 的 Fable、Opus 是 Adaptive，由模型自己決定。更高不等於更好。另外換模式或換模型可能失去快取，成本會變。",
    "d_ring": "今天介紹七家：Anthropic 的 Claude、OpenAI 的 ChatGPT 與 Codex、Google 的 Gemini 與 Antigravity、月之暗面的 Kimi、DeepSeek、Cursor、OpenCode。每家通常有三層：聊天 App、寫程式的 Agent、給開發者的 API。Logo 是教學引用，商標屬各公司。",
    "d_role": "有人做模型，有人做工具。Cursor 和 OpenCode 是工具，可以接別人的模型；OpenAI 和 Anthropic 兩邊都做，各有自己的 Agent（Codex、Claude Code）。",
    "e_scale": "模型通常分三級：旗艦最強最貴、主力快又夠強、輕量便宜快速。這個分級是我的編輯判斷，不是官方分數；Gemini 4 Hydrogen 官方說是快速輕量、日常執行用，所以放輕量。",
    "e_claude": "Claude：Fable 5.1 最高階、慢；Opus 5.5 頂級，適合複雜改程式；Sonnet 5.5 強而快；Haiku 5.5 輕量。Mythos 只開放給審核過的組織，這裡不講。",
    "e_openai": "OpenAI：GPT-6 Astra 最高階；GPT-6.1 Sol 是高階主力；Terra 偏效率；Luna 輕量便宜。聊天裡的 GPT-6 Sol 和 Codex 裡的 GPT-6.1 Sol 名字很像，不要混。",
    "e_google": f"Google 最近更新很快，這頁是 {GOOGLE_CHECK_DATE} 讀 Antigravity 官方頁的結果。Gemini 4 Carbon 是 10 月預告的新一代旗艦，11 月開放，Antigravity 要 Ultra 才能選；Gemini 4 Argon 同樣當『規劃者』，付費 Pro 起就能用；Gemini 4 Hydrogen 是 11 月新發表的快速輕量模型，負責日常執行，Pro 起可選。Antigravity 還有 Orchestrator：由規劃者（Carbon 或 Argon）加 Hydrogen 搭配，官方建議當大多數開發工作的預設。Gemini 3.8 Flash 全方案都有。提醒：Claude 4.6 與 GPT-OSS-120B 官方說 11 月 18 日移除。",
    "e_kd": "Kimi 的 K3.1 Pro 最強，只用思考模式；K3 是上一代旗艦。DeepSeek 現役主力有兩個：V4.1 Flash 便宜快，V4 Pro 做深度推理。",
    "e_co": "Cursor 自家模型是 Grok 4.7 與 Composer 2.5。OpenCode 是工具，Go 方案可選約三十款模型，共用一個加權額度，這裡不一一列。",
    "e_bench": "這是 Vals AI 在 2026 年 10 月 29 日用同一套 Mini-SWE-agent 框架跑的 Terminal-Bench 4.0，只比『寫程式 Agent 任務』。先看分數：Opus 5.5 最高，但前三名只差約 1 分，不要過度解讀。再點一下，同一批模型換成『平均每題花多少美元』，順序整個變了：Kimi K3.1 Pro 每題只要約 4.6 美元。Carbon 和 Argon 是不同模型（Antigravity 現在兩個都有，Carbon 只有 Ultra）。",
    "e_read": "怎麼看『誰聰明』：一、同框架同版本才能比，不同榜單分數不能換算；二、輕量模型不是廢，是便宜快、適合小事，不適合最難的長任務；三、看你的任務；四、最後自己測三次。",
    "f_kinds": "付費有三種：月費訂閱，額度有上限；API 按量，用多少算多少；免費，額度小功能有限。三種不能直接比較哪個『便宜』。",
    "f_token": "token 是模型計算文字量的單位，不是『問了幾次』。API 把 token 分三種價：快取輸入（之前讀過的，最便宜）、新輸入、輸出。例子是 DeepSeek V4.1 Flash 離峰價，每一百萬 token：快取 0.003、新輸入 0.15、輸出 0.60 美元。",
    "f_gates": "月費訂閱常有三道閘門：五小時、每週、每月。要三道都過。注意：五小時不是『一天只能用五小時』，而是每段五小時有一份用量上限。一道關上就先停，即使別的進度條還有。各平台規則不同。",
    "f_ladder": "各家月費階梯（美元；Kimi 是人民幣，不換算）。重點是階梯越貴，多給的通常是倍率，不是無限。價格以官方頁為準，台灣結帳價可能不同。",
    "f_trap": "四個容易誤會的地方：Cursor 八美元只含自家模型，第三方另外付；Kimi Go 不含 Kimi Code，Plus 起才有；Antigravity 的 Argon 有獨立每週額度；倍率不是固定總量。",
    "f_api": "API 算給你看：假設一億 token，其中 9,200 萬是快取輸入、700 萬新輸入、100 萬輸出，DeepSeek V4.1 Flash 離峰約 1.926 美元。尖峰是兩倍，V4 Pro 更貴。這只是特定比例的試算，不是包月，也不含 Search、Fetch 另計。",
    "g_free": "免費能做什麼：Claude 有受限聊天但不含 Claude Code；ChatGPT 有 GPT-5.6 Luna 聊天和本機 Codex；Google 的 Antigravity 免費能用 Gemini 3.8 Flash（4 系列要付費 Pro 起）；Kimi 網頁有限量；DeepSeek 聊天免費；Cursor 有限量 Agent；OpenCode 工具免費，部分模型限時免費。額度多少多半沒公開固定數字。",
    "g_kinds": "免費不等於無限，也不等於全包。聊天、本機 Agent、雲端 Agent、API 是四種不同的『可用』，免費聊天不代表能用 API 或雲端 Agent。",
    "h_pick": "怎麼選要看情境，不是排名：一般聊天先用免費；要一張二十美元的全包看 ChatGPT Plus；認真寫程式看 Claude Pro；想用便宜模型接工具看 OpenCode Go；按量最省的是 DeepSeek API，但一定要設支付上限。",
    "h_check": "訂閱前三件事：功能有沒有包含、額度何時重設、超額會不會扣錢。再來自己測三次：同一題、同條件，取中位數，看成功率、時間和花費。",
    "h_myth": "三個常見誤解：『官方把額度砍半』沒有官方公告；『問四句就沒了』不知道模型和設定不能推論；『一億 token 等於包月』那是 API 試算。社群經驗能提醒風險，但不能取代官方規則。",
    "h_end": f"資料截至 {CHECK_DATE}，價格以各家官方頁為準，上課前請重查。Logo 為教學引用，商標屬各公司，與各公司無關聯。",
}

OFFICIAL_SOURCES = [
    ("Claude 定價", "https://claude.com/pricing"),
    ("OpenAI Work／Codex 用量", "https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex"),
    ("Cursor 定價", "https://cursor.com/pricing"),
    ("Antigravity 方案", "https://antigravity.google/docs/plans"),
    ("OpenCode Go", "https://opencode.ai/v2/docs/console/go/"),
    ("Kimi 會員定價", "https://www.kimi.com/help/membership/membership-pricing"),
    ("DeepSeek API 費率", "https://api-docs.deepseek.com/quick_start/pricing/"),
    ("Claude Code Mods", "https://claude.com/resources/articles/claude-code-mods"),
]

# Terminal-Bench 4.0, same Mini-SWE-agent framework (Vals AI, observed 2026-10-29): (display name, score %, US$ per task)
BENCH = [("Opus 5.5", 65.15, 13.20), ("Sonnet 5.5", 64.14, 16.51), ("Kimi K3.1 Pro", 63.64, 4.57),
         ("Gemini 4 Carbon*", 63.13, 7.45), ("GPT-6 Astra", 59.60, 9.58), ("Fable 5.1", 58.08, 17.18)]

# DeepSeek, 100M tokens = 92M cache hit + 7M new input + 1M output (US$): (label, value)
DEEPSEEK_100M = [("V4.1 Flash 離峰", 1.926), ("V4.1 Flash 尖峰", 3.852), ("V4 Pro 離峰", 8.624), ("V4 Pro 尖峰", 17.248)]
DEEPSEEK_UNIT = {"cache": 0.003, "input": 0.15, "output": 0.60}  # V4.1 Flash off-peak, US$ per 1M tokens
