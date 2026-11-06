# Anatomy 10–15 秒 PowerPoint 原生 Morph 樣片 — 品質紀錄

**狀態：SPIKE / CANDIDATE；非 FINAL。** 不影響原 Blender 片頭，不能以 MP4 或靜態 Canva 假扮原生 PPT 動畫。

## 交付契約

- 16:9、4 頁可編輯 PowerPoint、3 段原生 Office Morph byObject，非影片嵌入。
- 單一連續橫向展示牆：Raptor 引擎特寫 → 拉遠揭露文字及全圖 → 平移 Turning Dial → 平移 Ripple Tank。
- 影像物件 across slides 使用相同且唯一的 !!RAPTOR_IMAGE、!!DIAL_IMAGE、!!RIPPLE_IMAGE 名稱；其餘標題與輔助線也是原生可編輯 PowerPoint 物件。
- XML 轉場時長 1450 ms、每頁自動換頁 2050 ms；**不是實際播放器測量的時長**。
- 這些是作者的**官方靜態範例截圖**，畫面被 PowerPoint 推拉／平移；不會因此保有原 HTML 的 WebGL、3D 或鼠標互動。

## 素材授權及來源

- 作者原始 repo：https://github.com/wheresryan22/anatomy
- 上游固定 commit：1482e8469b0a9e0d8cc18ea2740a01423d29ae80
- 官方相片位置：.github/assets/raptor-engine-firing.webp、turning-dial.webp、ripple-tank.webp。
- 授權：MIT License；Copyright (c) 2026 Ryan。CI 建置產物**須一併保留原始 LICENSE 全文**。
- 參考 Canva 影片僅用來確定品質期待，不複製其影格。
- 不將自行製作的背景或程序插畫冒充 Anatomy 官方產出。

## 產生與查驗

工作流：.github/workflows/anatomy-morph-spike.yml
建置程式：scripts/anatomy_official_morph_spike.py

1. GitHub Actions 從固定官方 commit 下載 WebP；下載失敗就停，不以 placeholder 自動代替。
2. 使用 python-pptx 與 Pillow 製作原生 PPTX。
3. 驗證四頁、三個 p159:morph、跨頁相同 !! 元素名稱、ZIP/XML 結構。
4. LibreOffice 只渲染四個**靜態終點畫面**，輸出四宮格作構圖審查。
5. Actions 上傳 PPTX、官方原圖、MIT LICENSE、逐頁 PNG 和四宮格預覽；不合併 PR、不可自動公開上傳 YouTube。

## G0–G5 品質門檻

| Gate | 證據與狀態 |
| --- | --- |
| G0 格式 | 已指定為原生 PPTX Morph，不准偷換媒介 |
| G1 素材 | 官方來源與 MIT 授權已查證；等候 CI 實際下載 |
| G2 最小樣片 | 本地以占位圖完成 4 頁 / 3 Morph 結構測試；官方素材候選由 Actions 建置 |
| A 結構 | 本地占位版 PASS；真實素材版待 Actions |
| B 靜態畫面 | 官方素材版須**人眼檢視四張輸出**；未看不准 PASS |
| C **實際原生播放** | **BLOCKED / NOT RUN：無 Microsoft PowerPoint 播放環境** |
| D 桌面／手機 | NOT RUN |
| E 來源授權及事實 | MIT 和官方產品分類已確認；打包結果待 Actions |
| G4 擴充長片 | NOT STARTED；B/C/D 未通過不得擴展 |
| G5 成品交付 | NOT APPROVED；以使用者實際觀看為準 |

## 本地測試紀錄（2026-11-06）

**只針對結構／排版**，使用明確標示的 placeholder 進行四鏡頭驗證；ZIP/XML 檢查得到 4 頁 / 3 Morph，LibreOffice 能渲染四頁。這不代表官方原圖版已經建置，也不代表 Microsoft PowerPoint 播放成功。

## 阻擋條件

- 任一張影像不來自固定官方來源、授權文字缺失：FAIL。
- 任一頁文字被切、卡片主體被裁得無法辨認：FAIL，修鏡頭不擴頁。
- 原生 Morph 配對出現跳位／閃爍、未實播或無目標播放器：FAIL 或 BLOCKED，**不能標 FINAL**。
- CI PASS、PR 成立、靜態畫格通過只是分層證據，不得宣稱「電影級已完成」。
