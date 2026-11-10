"""Narration and timing of the YouTube cut, transcribed from the user's Google Doc
"AI 訂閱額度比較｜YouTube 旁白與分鏡優化稿 v2.1" (2026-11-10). The Doc is the source of truth; edit it there and re-sync.

Pure data (stdlib only) so tests can check timing and wording against the numbers in ai_subscriptions_data.py.
Facts were cross-checked by the user against official pages on 2026-11-10; they were NOT independently verified by this repo.
"""

# id, chapter label, seconds, narration
SCENES = [
    ("s01", "為什麼用量差很多", 30,
     "同樣付月費，為什麼有人能讓 AI 寫程式一整天，有人改幾個檔案就用完？原因未必是問太多，而是各家計算額度的方法不同。"
     "這支影片比較七個 AI 平台，讓你看懂哪些限制會先擋住你，才不會花了錢卻買錯功能。"),
    ("s02", "先說結論", 40,
     "先講結論：沒有哪家對所有人都最划算。聊天幾分鐘，和讓 AI 搜尋整個專案、改檔、跑測試，消耗根本不同。"
     "訂閱前應比較三件事：目標功能有沒有包含、哪條限制會先到頂、最後能完成多少工作。"
     "我們今天不做萬用排行榜，而是教你依照自己的使用方式選。"),
    ("s03", "四種額度", 45,
     "先分清四個數字。token 是模型處理內容的單位，不是發問次數；五小時額度，限制某個時間視窗裡能用多少；"
     "每週或每月額度，可能跟短期限制同時存在；API 則依輸入、輸出、快取和額外工具結帳。"
     "這四種單位不能互換，也不能看到一億 token，就說一定值多少月費。"),
    ("s04", "三道閘門", 35,
     "想像每次工作都要穿過幾道門：短時間額度、每週額度，以及有些平台才有的每月額度。"
     "只要一道關上，即使其他進度條還顯示很多，也可能暫時不能用。"
     "五小時限制不是一天只能使用五個小時，而是每段五小時視窗各有一份用量上限。"),
    ("s05", "七平台類型", 40,
     "先把七家分成三類。Claude、ChatGPT、Kimi 有結合聊天和部分 Coding 的訂閱；"
     "Cursor、Antigravity、OpenCode 是把 AI 接入開發流程的工具或平台；"
     "DeepSeek 這次主要比較 API，它不是另一張固定二十美元的 Coding 月票。不同計價方式直接排名，很容易比錯。"),
    ("s06", "Claude", 45,
     "Claude Pro 月付二十美元，包含 Claude Code。更高級的 Max、Ultra 主要增加容量；"
     "Ultra 官方規則是每週約 Pro 十倍，符合驗證條件的帳號目前沒有五小時限制，但仍有每週額度。"
     "長上下文、較重推理和代理多輪工作會讓消耗不同。要不要升級，先看你這週究竟撞限幾次，而不是聽別人說能問幾則。"),
    ("s07", "ChatGPT", 40,
     "ChatGPT Plus 常見月費二十美元，但一般聊天與 Codex、Work 的程式代理任務不要混算。"
     "官方說 Work 和 Codex 共用方案額度，部分方案同時受五小時與每週限制。"
     "看到官方的「每五小時可傳幾則」，那也只是估計，不是保證。外部 API 另外計費；剩餘額度應看帳號裡的 Usage。"),
    ("s08", "Cursor", 40,
     "Cursor 新制叫 The X Subscription，整合 X、Grok 和 Cursor。Plus 月費八美元，Premium 三十美元，"
     "Super、Ultra 則有更高的共享週池倍率。不過月費主要包含 Cursor 自家與 Grok 相關模型。"
     "Premium 以上可另購預付額度，選用 Claude、GPT 或 Gemini 等第三方模型時，依 API 定價扣費。"
     "舊版 Cursor Pro 用不同的月度池，不能和新版直接換算。"),
    ("s09", "Antigravity", 45,
     "Antigravity 的付費 Pro 一般有五小時視窗與每週限制，但不是每句 prompt 都固定扣一格，而是跟 Agent 做了多少工作有關。"
     "例如付費 Pro 的 Gemini 4 Argon 另有獨立的每週額度，不能和 Flash 畫成同一個池。"
     "也別把 Gemini App 的會員權益，直接當成 Antigravity 所有模型的權限。訂閱前請查看自己帳號的模型選單與 Usage。"),
    ("s10", "OpenCode", 45,
     "OpenCode 工具本身可以免費裝，模型不一定免費。Go 每月十美元，Go Plus 四十美元。"
     "它不是三十個模型就送三十份額度，而是按照模型的參考價格，共同計算消耗比例。"
     "例如某模型月參考額十五美元，使用等值一美元，約佔月池百分之六點七。"
     "五小時、每週和每月又會分別檢查，換模型不等於換新錢包。"),
    ("s11", "Kimi", 50,
     "Kimi 新版 Go 是人民幣四十九元，但不包含 Kimi Code；要用它寫程式，Plus 每月九十九元才是起點。"
     "新版 Kimi Code 有五小時滾動限制，沒有額外週上限，卻和 Kimi Work、PPT、研究、Agent 等共用月度額度。"
     "所以別的功能用很多，也可能影響 Code。舊版會員可能還有每週限制。少一道閘門，並不代表無限使用。"),
    ("s12", "API", 25,
     "DeepSeek 有免費聊天入口，但透過 API 讓自己的工具大量呼叫模型，就會按用量收費。"
     "它不是固定月票：用得少可能很省，工作不中斷地一直跑，費用也會繼續累積。"),
    ("s13", "API", 40,
     "用原報告的高快取例子：假設一億 token 中，九成二是已命中快取、百分之七是新輸入、百分之一是輸出。"
     "按官方 V4.1 Flash 離峰費率，大約是一點九二六美元。但這只是特定比例的試算，不是一億 token 的包月票。"
     "快取失效、輸出更長，或另用 Search、Fetch 工具，費用都會變；V4 Pro 也要分開計算。"),
    ("s14", "常見誤解", 35,
     "三種誤解最常見。第一，官方沒公開固定 token 總額，卻有人保證每月能用幾億。"
     "第二，看到「問四句就沒額度」，卻不知道模型、上下文和工具設定，就推論人人如此。"
     "第三，把 API 的美元試算當成訂閱內含用量。社群回報能提醒風險，卻不能取代官方規則或自己的帳單。"),
    ("s15", "情境選擇", 40,
     "偶爾聊天或小改程式，先試免費或低價方案。每天讓 AI 讀 repo、修改程式、跑測試，"
     "就比較 Claude Code、Codex、Cursor、Antigravity 的實際完成率和額度。"
     "如果有大量重複、高快取的工作，OpenCode 搭配低價模型，或 DeepSeek API 可能更省，但要算進失敗重跑與額外工具費。"
     "適合你的方案，不一定是排行榜第一名。"),
    ("s16", "自己測", 30,
     "拿同一份 repo、同一個版本和題目，固定工具與推理條件，每個方案至少重跑三次。"
     "記錄用量變化、時間、實際額外支出，以及驗收是否成功。再觀察七十二小時的短期和每週限制。"
     "真正重要的，是每次成功完成任務，要花多少時間和錢。"),
    ("s17", "結語", 20,
     "訂閱前確認三件事：你要的功能是否包含、額度何時重設、超額會不會另外扣錢。"
     "選 AI 工具，不是追最高分，而是找到能穩定完成你的工作、又符合預算的方法。"),
]

SCENE_SECONDS = {sid: sec for sid, _, sec, _ in SCENES}
NARRATION = {sid: text for sid, _, _, text in SCENES}
CHAPTER = {sid: ch for sid, ch, _, _ in SCENES}
TOTAL_SECONDS = sum(SCENE_SECONDS.values())
