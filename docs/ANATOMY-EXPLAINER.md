# Anatomy 科普簡報（13 頁，無縫 Morph 轉場）

> 版本 2026-11-06｜階段：**SPIKE / PREVIEW**。結構（A）、靜態畫面與轉場代理（B）已自行檢查；**Microsoft PowerPoint 實播、匯出影片、手機觀看（C/D）未執行 = BLOCKED / NOT RUN**。內容事實取自上游 README，**發布前需人工核對**。

## 1. 交付契約

| 項目 | 內容 |
| --- | --- |
| 交付物 | 正式、可編輯的 `.pptx`（13 頁，原生 Office Morph 12 段），用於科普 YouTube 影片 |
| 主題 | Anatomy：是什麼、能做什麼、怎麼安裝與使用、適合誰、優缺點、不適合誰 |
| 圖像 | **盡量使用官方原始資料圖**（見 §3），不重繪、不仿製 |
| 轉場 | 一個連續世界上的鏡頭運動：鑽進視窗、拉遠揭露、平移（見 §2） |
| 不是 | 角色動畫／Live2D |

## 2. 內容與轉場

| # | 頁面 | 轉場進入 | 主要官方圖像 | 事實來源（上游 README 節） |
| --- | --- | --- | --- | --- |
| 1 | 封面 | — | Raptor 2 開火（README 首圖） | 標題與簡介 |
| 2 | 它是什麼 | **鑽進視窗**（Zoom-through） | Raptor 2 拆解圖 | 開場說明（快取鍵→彈子鎖；GPU context→龍門繪圖機） |
| 3 | 輸出形式 | **拉遠揭露**：第 2 頁原來是牆上的畫框 | A4 海報／技術圖／詳解頁 | Install 前的輸出說明、Examples 節末列印說明 |
| 4 | 三種圖 | 平移 | dial-indicator、ripple-tank、turning-dial（官方頁面擷取） | What it makes |
| 5 | 功能 | 平移 | Raptor A4 海報的零件編號圖 | 開場說明、How it works（稽核、驗證）、Limits |
| 6 | 官方範例一覽 | **鑽進視窗** | 6 個範例縮圖 | Examples 表 |
| 7 | 安裝 | **拉遠揭露** | — | Quick start、Install、Requirements |
| 8 | 使用 | 平移 | — | Usage |
| 9 | 適合誰 | 平移 | desk-computer（官方頁面擷取） | **依官方定位整理（非官方明列）** |
| 10 | 優點 | **鑽進視窗** | — | Quick start、Install、How it works、Limits |
| 11 | 缺點與限制 | **拉遠揭露** | — | Limits、3D beta 說明 |
| 12 | 不適合誰 | 平移 | — | **依官方 Limits 整理（非官方明列）** |
| 13 | 結語 | 向下平移 | Raptor 2 拆解圖 | License、連結 |

**設計規則（見 `PPTX-SEAMLESS-EXPLAINER.md`）**：每頁的內容像一般 13.33×7.5 英吋投影片一樣設計；`scripts/pptx_world.py` 把這些頁放進同一個世界，窗框與畫框的寬度相同（3.9 英吋），所以拉遠揭露後縮放回到 1，不會越走越小。鑽進視窗之後**必須**接拉遠揭露（直接平移會落在父頁內）。每段轉場的縮放比約 3.4×。

## 3. 官方素材與授權

來源：<https://github.com/wheresryan22/anatomy>，固定 commit `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`，**MIT License，Copyright (c) 2026 Ryan**。

`scripts/anatomy_assets.py` 從該 commit 下載、以 SHA256 逐一核對（不符即停止，不替代），再產生（**不提交進 repo**，輸出在 `build/anatomy/assets/`）：

| 產物 | 做法 | 用在 |
| --- | --- | --- |
| `fig_*.png` | README 的 WebP 官方圖轉 PNG | 封面、拆解圖、範例縮圖 |
| `cap_*.png` | 以無頭 Chromium 在 3× 擷取官方範例頁的圖卡（`.iso-plate`），頁面不修改 | 三種圖、範例一覽、適合誰 |
| `poster_*_figure.png` | 官方向量 A4 海報 PDF 以 300 dpi 光柵化後，依墨跡範圍自動裁切 | 功能頁 |
| `sheet_*.png` | 官方 A4 海報／技術圖／詳解頁，150 dpi | 輸出形式頁 |
| `LICENSE_ANATOMY.txt`、`manifest.json` | 授權全文；輸入／輸出 SHA256 與來源 | 隨檔 |

授權落實：每頁講者備註附完整 MIT 授權全文與來源；每頁畫面右下角有「圖與資料：wheresryan22/anatomy · MIT © 2026 Ryan」；CI 產物附授權與 manifest。**本簡報不改動、不重繪官方圖像**；PDF 裁切與頁面擷取是對官方成品的機械式取景。

## 4. 重現

```bash
python3 scripts/anatomy_assets.py                 # 需要 poppler-utils、Node + playwright（擷取官方頁面）
python3 scripts/build_anatomy_explainer.py        # --hold 8000 --duration 1500 --font-sans ... 
python3 scripts/pptx_validate.py build/anatomy/anatomy-explainer.pptx --min-loops 0 --strict \
  --readable build/anatomy/anatomy-explainer.readable.json
python3 scripts/pptx_morph_proxy.py build/anatomy/anatomy-explainer.pptx build/anatomy/proxy.pptx --steps 3
```

- **字型**：簡報指定 Noto Sans / Serif CJK TC 與 DejaVu Sans Mono，**播放的電腦必須已安裝**，否則 PowerPoint 會替換字型而使排版變動。可用 `--font-sans/--font-serif/--font-mono` 改成已安裝的字型。本專案不隨附字型檔。
- **停留時間**：預設每頁 8 秒只是展示；請依旁白長度設定（`--hold`）。
- 官方素材需要網路（下載與頁面擷取）；擷取約 3 分鐘。

## 5. 驗證狀態

| 層 | 狀態 | 證據 |
| --- | --- | --- |
| A 結構 | PASS（本地） | 26 個單元測試；驗證器 `--strict`：13 頁 / 12 Morph、跨頁 `!!` 錨點、字級 ≥14 pt、5% 安全區（只檢查該頁要讀的文字） |
| B 靜態 | 自查完成（本地 LibreOffice，字型為替代字型） | 13 頁逐頁檢視；已修：文字溢出、框線壓標題、視窗壓頁尾、右緣越界 |
| B 轉場代理 | 完成（49 張，12 段 × 3 中間幀） | 三種手法的中間畫面無空洞或閃現；拉遠揭露中途舊頁暫時透出（淡入造成），結束後消失。**代理不含真實緩動與文字處理** |
| C PowerPoint 實播／匯出影片 | **BLOCKED / NOT RUN** | 無 Microsoft PowerPoint |
| D 桌面／手機 | NOT RUN | — |
| E 內容與授權 | 授權 PASS；**事實待人工核對** | 見 §6 |
| CI | 工作流 `anatomy-explainer.yml` 已提供，**尚未執行** | — |

**自查發現的主要問題**：
1. **內文偏小**：密集頁的說明文字是 16–20 pt。1080p 桌面可讀，**手機觀看會偏小**；若要手機友善，需拆頁或放大（會增加頁數）。
2. **官方圖線條很淡**：官方淺色主題以細線與低對比表現；縮圖頁（範例一覽、A4 縮圖）在影片中接近氛圍而非細節。
3. **每頁 40–140 個物件**：Morph 在低階電腦放映時是否順暢未知，只有實播能判定。
4. **字型相依**（§4）。
5. 「適合誰／不適合誰」是我依官方定位與限制整理，**不是官方明列名單**（頁面右上角已標註）。

## 6. 事實台帳（取自上游 README，commit 1482e84，核對 2026-11-06）

| 陳述 | 上游依據 |
| --- | --- |
| Claude 技能；也可在 Antigravity、OpenCode、Codex、MiniMax Code 使用 | 首段與 Requirements |
| 用「發明物件」解釋概念：快取鍵→彈子鎖；一個 GPU context 服務多個 canvas→龍門繪圖機（單一印頭走訪 16 個井） | 開場說明 |
| 三種圖：SVG（核心）、SVG+WebGL（火焰、排氣、水、焦散、燈光、蒸氣）、3D（beta） | What it makes |
| 輸出：獨立 HTML、單一 .svg（樣式內嵌）、React/Next.js 元件；亮／暗主題；可列印 A4（海報、技術圖、詳解） | What it makes、Examples |
| Raptor 2：滑過即拆成 11 個組件；稽核證明沒有管線穿過任何東西 | Gallery、Examples、How it works |
| 範例：dial-indicator（約 300 行）、desk-computer（約 85 個實體）、arcade-cabinet（約 240 個實體、15 條線纜）等 | Examples 表 |
| `npx skills add wheresryan22/anatomy -g`，可加 `-a claude-code｜antigravity｜opencode｜codex｜minimax-code` | Quick start、Install |
| Node.js 20.10+，只用內建模組，不需 npm install 與 API 金鑰；Chrome/Chromium 供檢查；React 18+ 僅 React 輸出 | Quick start、Requirements |
| skills CLI 1.7.1 版要求 Node 22.20 以上 | Install（With the skills CLI） |
| `/anatomy …`（Codex 用 `$anatomy`）；三個習慣 | Usage |
| 不是圖表庫；畫機器、儀器、工具、家具而非人物或精確地圖；刻意很慢；shader 需要 WebGL | Limits |
| 3D 為 beta；380 零件壓力測試約 20 fps（1440 px 寬）、節流手機約 13–15 fps；30 零件 3D 軌道稽核約 15–20 分鐘 | Limits、NOTE |
| Codex 沙盒可能擋住無頭 Chrome（圖仍會建出，只有檢查失敗） | Install（Codex 折疊段） |
| MIT © 2026 Ryan | License |

**未做的核實**：我沒有實際安裝或執行 Anatomy，所有「能做什麼」都是上游文件與其官方圖像的說法，不是我的實測。上游之後若更新，需重新核對。

## 7. 需要使用者決定

- 實際口白與每頁停留時間（`--hold`）。
- 密集頁是否拆頁以利手機觀看。
- 播放用字型（安裝 Noto，或改指定已安裝字型）。
- 16:9 之外是否另做 9:16。
- 事實與「適合／不適合」措辭的人工審核。
