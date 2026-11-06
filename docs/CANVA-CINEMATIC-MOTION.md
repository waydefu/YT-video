# Canva 電影式動態簡報與 YouTube 製片手冊

> 更新：2026-11-06｜語言：繁體中文｜狀態：**官方功能已查證；進階鏡頭配方屬待實作驗證**。不是 Canva 專案成品或性能測試報告。

## 0. 目標與範圍

目標是製作「頁面像同一個世界的不同時間點」的動態簡報，參考片的長鏡頭、報紙→地圖→海報→畫框→房間連續變換；不以淡入淡出堆砌。內容仍必須能閱讀、操作示範必須真實、繁體字不能破版。

- **適用**：工具介紹、教學、科技科普、歷史敘事、產品對比、YouTube 正片段落、資訊型 Short。
- **非適用**：精確 3D 攝影機、真實物理破碎、可重建的流體煙霧、複雜逐影格角色動畫；交給 Blender / After Effects / 程式化影片工具。
- **權限**：此文件不授權下載他人素材、複製參考影片或發佈影片；遵守根目錄 `AGENTS.md` 與 `docs/ASSET-RIGHTS.md`。

## 1. 先選對 Canva 工作模式

| 模式 | 強項 | 限制 / 判斷 |
| --- | --- | --- |
| **Presentation / 逐頁簡報** | Match & Move 跨頁過渡、頁面切換、演講者備註、播放簡報；可設計每頁為一個視覺關鍵姿態 | 如果是影片，匯出後再做音樂 / 字幕 / 精剪；不等同新版連續影片時間軸 |
| **Video / 新版多軌時間軸** | 影片與音樂多軌、主軌片段轉場、修剪、分割、Slip、疊層、字幕 | 轉場必須作用於主軌片段；上層覆蓋素材之間不能直接套用同樣的片段轉場；不能把簡報 Match & Move 的每種行為預設為影片軌道支援 |
| **Blender + FFmpeg（現有 repo）** | 真實幾何、攝影機、煙霧、程序化動畫、獨立渲染 | 編輯成本高；電影級真 3D 不能由 Canva 假裝取代 |

**推薦工作流**：Canva Presentation 做複雜跨頁構圖 → 輸出 MP4 或分段 MP4 → Canva Video 精修配樂、B-roll、字幕；若轉場不連續或需精準軌道控制則外接 Blender / FFmpeg。勿把尚未測過的轉換稱為「無損」或「完全保留可編輯性」。

## 2. 官方可操作功能（查證到 2026-11-06）

1. **Match & Move**：在簡報中複製頁面、微調位置 / 大小 / 顏色 / 透明度，再在頁面之間加入「Match and move」。用於連續物件的運動插補。官方範例包含拖放、橫向輪播、遮擋揭露。[教學](https://www.canva.com/design-school/resources/how-to-create-animations-with-match-and-move/)
2. **頁面轉場**：在縮圖頁面間選「Add transition」；官方列可調持續 **0.1–2.5 秒**，以及依樣式可調方向。[說明](https://www.canva.com/help/page-transitions/)
3. **元素 / 文字 / 整頁動畫**：選元素→「Animate」→ Page / Element / Text；部分樣式支援速度和進出場秒數。[說明](https://www.canva.com/help/animate-designs/)
4. **自訂運動路徑**：選物件→Animate→Create an Animation→拖動畫出路徑→調 Movement Style；官方列**單一自訂動畫最長 10 秒、每份設計最多 50 個自訂動畫**（依其當前說明）。[說明](https://www.canva.com/help/animate-designs/)
5. **時序調整**：元素→More→Show element timing；可調元素顯示起訖、順序；簡報也能用 Appear on click / Click order。**元素顯示時間與進出場動畫長度是不同控制項**。[說明](https://www.canva.com/help/animate-designs/)
6. **多軌影片時間軸**：主軌、上軌圖文 / B-roll、音軌；分割 `S`、修剪邊緣、Slip 改用原片哪個區段，時間尺縮放可精準對位。[說明](https://www.canva.com/help/creating-and-editing-videos/)
7. **影片主軌轉場**：在主軌兩個片段間 Add transition；頁面模式不能加此種影片轉場，上層軌道間亦不能直接加主軌片段轉場。[說明](https://www.canva.com/help/creating-and-editing-videos/)
8. **Beat Sync**：免費方案可顯示節拍標記並手動貼齊；自動「Sync now」為 Pro 功能。它對齊**音樂節拍，不是語音發話內容**。[說明](https://www.canva.com/features/beat-sync/)
9. **音量與淡入淡出**：音軌選取後調整 volume、Fade、Trim；可對音訊與影片聲音分別處理；影像的 Fade 動畫不等於音訊 Fade。[說明](https://www.canva.com/help/trim-audio-and-adjust-volume/)
10. **字幕**：Text→Dynamic text→Captions 或 Apps→Captions；可指定辨識語言、翻譯及修改字幕。繁中內容逐字校對，不能假定 AI 轉寫正確。[說明](https://www.canva.com/help/generate-edit-captions-on-videos/)
11. **圖層、群組、對齊**：Position→Layers 檢視疊層順序；`Ctrl/Cmd+G` 群組。第三方 App 產生的元素未必可直接跟普通圖層群組。[說明](https://www.canva.com/help/layer-group-align/)／[圖層](https://www.canva.com/en_gb/help/finding-and-arranging-layers/)
12. **框架 / 裁切 / 遮罩**：Elements→Frames，拖入圖片 / 影片；雙擊重新裁切；只允許圖片與影片放入框架。[說明](https://www.canva.com/help/using-frames/)
13. **去背**：照片與影片去背屬付費功能；官方列影片**原始片長需小於 10 分鐘**，照片批次另有尺寸與數量限制。[說明](https://www.canva.com/help/background-remover/)
14. **影片播放速度**：支援 **0.25×–2×**，並可在某些設計類型設定播放自動開始 / 重播；影片設計不支援影片 Loop 的同一用法。[說明](https://www.canva.com/help/adjust-video-playback/)
15. **調色、裁切、透明度**：Edit→Adjust，裁切、Perspective、亮度 / 對比 / 飽和度，以及選取物件後透明度調整。[調色](https://www.canva.com/help/image-settings/)／[裁切](https://www.canva.com/help/resize-and-crop/)／[透明度](https://www.canva.com/help/transparency/)
16. **匯出**：Share→Download→MP4；免費方案在官方規格中為預設 1080p、最長 30 分鐘；付費適用方案可選最高 4K、最長 2 小時（取決於方案 / 裝置）。**未確認 Canva 匯出原生 FPS 可指定**，必須以 ffprobe 驗證。[說明](https://www.canva.com/en_in/help/download-as-video/)
17. **講者視圖 / 錄製**：Presentation 可用 Presenter view、Autoplay、Present and record；錄製簡報目前需電腦端。[簡報模式](https://www.canva.com/en_gb/help/presentation-modes/)／[錄製](https://www.canva.com/en_gb/help/talking-presentations/)

## 3. 電影式轉場核心配方（**設計方法，尚非實際 Canva 驗收**）

### A. 無縫推鏡：同一張圖，三個「鏡頭姿態」

1. 第 1 頁：全景照片 / 高解析主視覺，文字在安全區；用固定邊緣作參考錨點。
2. 複製頁面：第 2 頁將**相同物件**等比放大（建議 1.3–1.8× 起試）、位移到特寫區；用 Match & Move 插補。
3. 第 3 頁延續同一視覺物件，以錨點從特寫平移到新的內容；不可每頁重新匯入不同裁切版本再假裝連續。
4. 調整每段時長、按 100% 播放觀察。若主體跳躍、遮罩閃爍，改成先匯出定格層或轉入影片工具精修。

### B. 「海報其實在畫框裡」的空間揭露（參考片最有價值）

1. 頁 A：海報放到滿版，只留畫框邊極少一部分；背景事先包含牆面、畫框、室內。
2. 複製頁至 B，縮小**同一套分層構圖**，讓畫框和牆面進入視野；Match & Move。
3. 頁 C：焦點向右平移到人物 / 下一個敘事物件；保留牆面的顏色、光源與空間方位。
4. 避免「A 是平面海報、B 突然換成不同圖片的畫框」，會導致硬切而非揭露。

### C. 虛擬視差（不是 3D 攝影機）

1. 拆成近景 PNG / SVG、主體、中景、遠景與霧層；近景移動距離較大、遠景較小。
2. 兩到四個關鍵頁，在同方向做幅度不同的位移；只用少數大動作，避免畫面散亂。
3. 主體避免被文字遮住，必要時先用 Frames / 局部裁切隱藏物件。
4. **只是 2.5D 視覺模擬**，非透視幾何或光照正確的真 3D。

### D. 遮擋揭露 / 轉場匹配

- 讓黑色圓形、海報紅底、視窗邊框或報紙欄位**經過鏡頭前方**，下一頁延用同位置、同色的物件；比普通 Fade 更像長鏡頭。
- 比例與中心需一致；在轉場前後取影格，檢查遮擋輪廓是否跳位。
- 不要對每一段都套全頁推入 / 縮放；移動需服務敘事。

### E. 鏡頭運動的速度節奏（建議初始值，非 Canva 官方標準）

- 資訊揭露：轉場試 **0.45–0.9 秒**；大幅鏡頭推進：試 **0.9–1.5 秒**；觀眾需要閱讀的定格：至少依文字量調整。
- 不在每頁同時讓標題、背景、圖片以不同方向高速飛入；主體移動時，次要元素保持安靜。
- 音效與動作高潮對齊，避免每次切頁都加巨響 / Whoosh。
- Canva 的可用 easing / 路徑樣式依物件與方案而異；不宣稱可逐曲線精細控制如 After Effects。

## 4. 字體、視覺、資訊的約束

- **先資訊架構再動畫**：每一鏡頭只有一個要傳達的主論點；教學步驟要能暫停閱讀。
- 建議繁中為主；選字體要檢查「體、術、畫、與」等複雜字在全畫質輸出是否缺字。
- 在 1920×1080 設計採專案安全區：主體 x/y 10–90%，標題 x/y 15–85%（沿用 `config/production.json`）。
- 長段落不要塞在 2–3 秒鏡頭；參考片有出色轉場，但它的細字 / 樣板內容不值得模仿。
- 字體尺寸、色彩對比、留白需在手機實機看；沒有實際渲染與手機驗收前，不宣稱「毫無破版」。

## 5. YouTube 端到端流程

1. **腳本 / 引用**：每項工具功能說明先記官方來源；優缺點、費用、實測與個人觀點分開。
2. **畫面設計**：先寫 8–12 個鏡頭狀態；給每個核心視覺一個可持續追蹤的空間錨點。
3. **資產管理**：建立 `來源 / 授權 / 允許商用 / 是否可再散布 / 是否可公開 / 檔案版本` 紀錄；參考影片僅供內部學習。
4. **Canva 原生**：先完成 15–30 秒無聲動態片段，逐段檢查 Match & Move，再加音效與字幕。
5. **匯出與精修**：下載 MP4；用 `ffprobe` 驗證尺寸 / FPS / 聲道，依 `AGENTS.md` 要求視需要轉成 1920×1080、24fps、H.264 / AAC；**重編碼不會憑空增加動畫的中間幀**。
6. **人工 QC**：連續看兩遍；每段邊界前後逐格檢查；手機全螢幕確認標題、中文字體、音量與構圖。
7. **交付**：保留可編輯 Canva 原稿連結或權限安全的設計紀錄、匯出檔、引用 / 授權表、版本與 QA 結論。不發布未獲使用者審核的成品。

## 6. 授權與費用陷阱

- Canva 的 Free / Pro 圖片、素材、音樂不是全部同一套使用條件；**Popular Music 不可用於商業用途**，包含廣告；Pro 庫存音樂則另有授權條件。[官方授權說明](https://www.canva.com/licensing-explained/)
- Canva for Education 的 Pro 內容限教育、非商業用途；不能因帳號能下載就推論 YouTube 營利合法。
- Canva 素材可在符合條款的設計中使用，但不得將獨立素材原封再散布或冒稱自有版權。
- 使用付費音訊上傳 YouTube 前先檢查授權與帳號驗證，並保留授權證明。[官方音訊授權](https://www.canva.com/help/verify-music/)
- 原創 / 已授權素材優先；任何外部作品及音效必須先登錄到 `docs/ASSET-RIGHTS.md` 再納入發佈內容。

## 7. 限制、風險與未驗證項目

- 不將 **Match & Move** 說成完整 3D 攝影機或真實骨骼動畫。
- Canva 新版 Video UI 正逐步推出，帳號、裝置與設計類型可能有差異。[官方說明](https://www.canva.com/help/creating-and-editing-videos/)
- 沒有驗證「同一動畫匯出後與編輯時完全一致」「每種格式保留可編輯圖層」「精確指定原生 24fps」「每個元素都有相同進出場參數」。
- **尚未使用 Canva 專案實際建立或匯出這套參考片重現**；這份是官方功能研究與專業製作方法，不能當成通過的視覺驗收。
- 若單段場景非常複雜，建議直接改用 Blender / After Effects；避免為了只使用 Canva 犧牲最終品質。

延伸閱讀：`docs/CANVA-TECHNIQUE-INDEX.md`、`docs/CANVA-REFERENCE-RECIPE.md`、`docs/CANVA-QA.md`。
