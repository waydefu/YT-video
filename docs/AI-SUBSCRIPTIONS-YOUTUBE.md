# AI 訂閱額度比較：YouTube 版簡報（約 50 頁，手機優先）

> 版本 2026-11-10｜階段：**SPIKE / PREVIEW**。結構（A）、靜態與轉場代理（B）已自行檢查；**Microsoft PowerPoint 實播、匯出影片、手機觀看（C/D）未執行 = BLOCKED / NOT RUN**。**數字取自使用者的分鏡 v2.1（Google 文件，使用者以官方頁面於 2026-11-10 交叉核對），本 repo 沒有獨立查證。**

## 1. 來源與契約

| 項目 | 內容 |
| --- | --- |
| 旁白與分鏡 | 使用者的 Google 文件「AI 訂閱額度比較｜YouTube 旁白與分鏡」v2.1（17 個分鏡，10:45）；旁白逐字放在 `scripts/ai_subscriptions_script.py`，**以 Google 文件為準** |
| 交付物 | 可編輯 `.pptx`（50 頁、原生 Morph 49 段），之後由 PowerPoint 匯出 1080p 影片 |
| 手機優先 | 主文字 **30 pt 以上**（驗證器 `--min-font 30`），一頁一個重點；章節名、資料日期、進度條屬抬頭（HUD）不受此限 |
| 視覺 | 原創可編輯形狀；七個平台一律文字＋色塊，**不用 Logo**，不用人物素材 |
| 停留時間 | 每段旁白秒數平均分配到該段的頁數（寫入每頁 `advTm`）；實錄後再調 |
| 安全區 | 內容在左右 1.0 英吋、底部 0.9 英吋以內（底部留給字幕與播放控制列） |

## 2. 轉場（依內容選，不是整份同一種）

- **導讀高亮（stay）**：同名列留在原處，一個高亮框逐列滑動，其餘列變灰（結論三點、四種額度、七家分類、誤解、情境、自己測）。
- **共享元素**：長條寬度、閘門顏色、迷思文字就地變化（開場、三道閘門、OpenCode 共享池、DeepSeek 試算、迷思更正）。
- **地圖巡覽**：六個訂閱平台各一張卡片，放大進 Claude，卡片間平移，縮回地圖並打勾（`nest`／`zoom_out`，縮放約 3.8×，需實播確認）。
- **平移**：章節之間。

## 3. 重現與驗證

```bash
python3 scripts/build_ai_subscriptions_youtube.py
python3 scripts/pptx_validate.py build/ai-subscriptions/youtube/ai-subscriptions-youtube.pptx --min-loops 0 --strict \
  --min-font 30 --readable build/ai-subscriptions/youtube/ai-subscriptions-youtube.readable.json
python3 scripts/pptx_morph_proxy.py build/ai-subscriptions/youtube/ai-subscriptions-youtube.pptx build/ai-subscriptions/youtube/proxy.pptx --steps 2
```

字型：Noto Sans CJK TC 等需在匯出的電腦上已安裝，或用 `--font-sans` 改成已安裝字型。

| 層 | 狀態 | 證據 |
| --- | --- | --- |
| A | PASS（本地） | 60 個單元測試（含旁白秒數合計 645、語速合理、停留加總＝旁白、數字與資料一致）；驗證器 `--strict --min-font 30` 通過 |
| B 靜態 | 自查完成（LibreOffice，替代字型） | 50 頁逐頁檢視；已修「Codex／Work」換行、第 15 頁換行 |
| B 轉場代理 | 抽樣檢視（開場長條變形、進入地圖、導讀高亮、平移） | 148 張中間幀（2 步），抽樣無空洞或閃現；開場長條變形時說明文字短暫重疊（代理不淡入，真實 Morph 是否如此未知）；**代理只能否決設計** |
| C PowerPoint 實播／匯出影片 | **BLOCKED / NOT RUN** | 無 Microsoft PowerPoint；**請先匯出一小段含地圖放大與導讀高亮的 1080p 測試片** |
| D 手機 | NOT RUN | 30 pt 門檻為估算 |
| E 內容 | 事實待發布前再核 | 數字由使用者核對；台灣結帳價、帳號權限、模型清單會變（例如 Antigravity 部分模型 11/18 移除） |

## 4. 已知問題與待決定

1. 每頁停留是平均分配，未計 Morph 時間是否包含在內；實錄後以實際旁白調整。
2. DeepSeek 試算第三頁畫面文字較多，手機是否仍可讀需實測。
3. 地圖頁標籤與縮圖在影片中只是導覽，縮圖文字會很小（預期）。
4. 旁白由使用者錄或合成語音尚未決定；字幕（SRT）、縮圖尚未製作。
5. 舊的 22 頁研究版（`build_ai_subscriptions_deck.py`）保留，兩者互不取代。
