"""Narration and timing of the Anatomy YouTube cut, transcribed from the user's Google Doc
"Anatomy 科普影片｜旁白與分鏡 v2（官方展示版）" (2026-11-14). The Doc is the source of truth; edit it there and re-sync.

Positioning fixed by the Doc: a third-party explainer of an open-source project, narrated as "官方展示／依 README 說明";
nothing here claims a hands-on test. Facts come from the upstream README at the pinned commit 1482e84 (re-read 2026-11-14).
"""

CHAPTERS = ["拆開", "是什麼", "輸出", "功能", "安裝", "適合", "限制", "結語"]  # rail / ring labels (YouTube chapters)

# id, chapter index, seconds, narration
SCENES = [
    ("s01", 0, 30,
     "一張精密機械圖，不只是畫出外觀，還能展示內部結構。Anatomy 官方的 Raptor 2 範例，就展示了火箭引擎由完整狀態拆成十一組總成的效果。"
     "這些畫面不是我們的實測，而是開源專案提供的範例。今天一起看看，它是怎麼做出這類互動技術圖的。"),
    ("s02", 1, 40,
     "Anatomy 是一個 Claude 技能，也可以用在 Antigravity、OpenCode、Codex 和 MiniMax Code。它最特別的地方，是用「發明一個實體物件」來解釋概念。"
     "比方說，快取鍵被畫成彈子鎖；一個 GPU context 同時服務很多畫布，被畫成龍門繪圖機，單一印頭走訪十六個井。"),
    ("s03", 2, 35,
     "Anatomy 可以輸出獨立 HTML 網頁、帶內嵌樣式的單一 SVG 檔，以及 React 或 Next.js 元件。官方也提供亮色和暗色主題。"
     "需要印刷時，還可以另外要求產生 A4 海報、技術圖或詳解頁；這不是每次生成都自動附贈的輸出。"),
    ("s04", 2, 45,
     "圖本身有三種。核心是 SVG；再往上是 SVG 加 WebGL，可以做火焰、排氣、水、焦散、燈光和蒸氣；還有 3D 版本，目前是 beta。"
     "官方範例裡有 dial-indicator、ripple-tank 和 turning-dial 這類一眼看得出結構的圖。"),
    ("s05", 3, 40,
     "官方的 Raptor 2 範例，在滑鼠懸停時會拆成十一組總成。作者也針對這個範例進行幾何稽核，檢查管線在靜止、拆解及動畫過渡時是否穿過其他結構。"
     "這是特定範例的驗證結果，不代表所有 AI 生成的圖都自動正確。官方另提供標有組件編號的 A4 海報。"),
    ("s06", 3, 40,
     "官方範例表裡，規模從幾百行程式到上百個實體都有：dial-indicator 約三百行，desk-computer 約八十五個實體，"
     "arcade-cabinet 約兩百四十個實體、十五條線纜。"),
    ("s07", 4, 45,
     "官方提供一行安裝指令，也能用參數指定 Claude Code、Codex 等工具。Anatomy 本身採用 Node.js 內建模組，不需要另裝它的運行依賴，"
     "也不用為工具本身另外申請 API 金鑰；但 AI Agent 的帳號或服務權限仍要自己準備。官方工具要求 Node.js 20.10 以上，"
     "而使用特定版本的 skills CLI 可能需要 Node 22.20 以上。完整指令與瀏覽器、React 需求會放在畫面及說明欄。"),
    ("s08", 4, 30,
     "在 Claude Code 輸入 /anatomy，Codex 使用 $anatomy。官方建議三個習慣：先講清楚要解釋的概念與真實數字；"
     "如果已有具體機器，就說明哪部分要動；最後指定輸出 HTML、SVG 或 React 元件，以及亮色或暗色主題。"),
    ("s09", 5, 35,
     "誰適合用？這是我依官方定位整理的，不是官方名單：需要把機器、儀器或工具的運作原理講清楚的人，像是做科普影片、寫技術文章、教學或產品說明。"
     "重點是你的主題有零件、有結構。"),
    ("s10", 5, 35,
     "從官方文件來看，Anatomy 的優點是安裝方式簡單，繪圖工具使用 Node 內建模組，輸出又是 HTML、SVG 或 React 等可繼續編輯的檔案。"
     "它還提供幾何稽核和瀏覽器檢查流程。不過，這些是工具提供的能力，不能因此保證每個生成作品都通過檢查；需要另外執行驗證。"),
    ("s11", 6, 45,
     "限制也重要：Anatomy 不是統計圖表庫，主要處理機械、儀器與工具，建構流程刻意比較慢。火焰或水面等特效需要 WebGL，缺少它時 SVG 主體仍可閱讀。"
     "3D 還在 beta。作者的特定壓力測試中，380 個零件約每秒二十格，模擬降速手機則更低；這不是所有裝置的效能保證。"
     "完整測試條件留在畫面。Codex 沙盒也可能阻擋 Chrome 自動檢查。"),
    ("s12", 6, 30,
     "哪些情境不適合？以下是依官方限制整理的判斷，不是官方名單：如果要統計圖表、精確地圖或人物插畫，Anatomy 不是適合的工具；"
     "需要立即出圖也不符合它偏慢的製作流程。沒有 WebGL 的環境仍可看 SVG 主體，但無法呈現需要 WebGL 的特效。"),
    ("s13", 7, 25,
     "Anatomy 官方倉庫採 MIT 授權，著作權標示是二〇二六年的 Ryan。影片中的示意圖片都取自官方倉庫或範例，來源與授權資訊會附在說明欄。"
     "這是一支第三方科普介紹，不代表作者認可或參與製作。"),
]

SCENE_SECONDS = {sid: sec for sid, _, sec, _ in SCENES}
NARRATION = {sid: text for sid, _, _, text in SCENES}
SCENE_CHAPTER = {sid: ch for sid, ch, _, _ in SCENES}
TOTAL_SECONDS = sum(SCENE_SECONDS.values())
