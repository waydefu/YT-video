# PowerPoint 原生 Morph 電影式動態簡報研究與製作手冊

> 2026-11-06｜適用 `waydefu/YT-video`｜狀態：**OOXML 及靜態畫面經本地驗證；Microsoft PowerPoint Morph 實播未驗證**。與既有 Blender 片頭、Canva 技巧庫分開；不得把 MP4 冒充 PPTX 原生轉場。

## 目標與技術選擇

這個工作流交付真正的可編輯 `.pptx`：一張連續的大場景在相鄰投影片中透過同一物件名稱追蹤、平移和縮放；標題與資訊依然是 PowerPoint 原生文字框。**不產生替代的 HTML 動畫 / MP4 作為正式交付。**

| 工具 | 為何採用 | 無法證明的事 |
| --- | --- | --- |
| **PptxGenJS** | 可程式化 16:9、圖層、形狀、文字、圖片、講者備註 | 並非本流程的 Morph 寫入器 |
| **OOXML + Python 標準庫** | 注入 Microsoft Office Morph `p159:morph` + 舊版 fade fallback，配對 `p:cNvPr@name` | XML 正確 ≠ PowerPoint 每個版本實播必然無問題 |
| **LibreOffice / PDF 渲染** | 看投影片的靜態構圖、字型、錯字和裁切 | **不能拿來驗證 Morph 動畫速度或絲滑程度** |
| **Microsoft PowerPoint 365 / 2021 / 支援 Morph 的版本** | 正式打開、播放、檢查 Morph 與自動換頁 | 需要實際可用的 PowerPoint 播放環境 |
| **FFmpeg** | 可用於「實際 PowerPoint 錄製的」MP4 資料分析 | 單純轉碼不能證明原生 Morph |

### 微軟官方與實作研究來源

- [Microsoft：Morph 使用與相容版本](https://support.microsoft.com/zh-tw/powerpoint/training/use-the-morph-transition-in-powerpoint)
- [Microsoft：Morph matching object 的 !! 名稱技巧](https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks)
- [PowerPoint-emitted OOXML Morph + Fallback 範例](https://github.com/BramAlkema/svg2ooxml/blob/main/src/svg2ooxml/assets/animation_oracle/README.md)
- [PptxGenJS](https://github.com/gitbrent/PptxGenJS)；採可編輯文字、原生圖形及圖片編排
- [Anatomy 官方 repo / MIT 許可](https://github.com/wheresryan22/anatomy)；功能與安裝內容來源

## 可用技巧索引：**25 個工作配方**

| ID | 技巧 | 實作邏輯 | 狀態 |
| --- | --- | --- | --- |
| T01 | 穩定物件身份 | 相鄰頁 `p:cNvPr@name` 使用相同且唯一的 `!!NAME` | **OOXML 驗證** |
| T02 | `!!` 物件配對 | PptxGenJS 設 `altText: '!!MURAL'`，patch 後轉 `name` | **OOXML 驗證** |
| T03 | **Morph byObject** | `<p159:morph option="byObject"/>` | **OOXML 驗證** |
| T04 | 兼容型過渡 | `mc:AlternateContent`，新版選 Morph，舊版 fade | **OOXML 驗證** |
| T05 | 時長控制 | `p14:dur` 為轉場毫秒、`advTm` 為自動換頁時間 | **OOXML 驗證** |
| T06 | 同圖推鏡 | 同一張圖以不同 `x/y/w/h` 在前後頁連續放大 | **設計配方** |
| T07 | 拉遠揭露 | 主體從局部特寫回到全景，觀眾才發現所在場景 | **設計配方** |
| T08 | 漸進平移 | 相鄰頁保留同一場景，以同方向攝影機位移 | **設計配方** |
| T09 | 方向連續 | 一次鏡頭運動避免突然反轉方向或失去地標 | **設計配方** |
| T10 | 2.5D 視差 | 近中遠景分層並各自命名，分別指定相對速度 | **待實播** |
| T11 | 共同背景 | 同一大幅壁畫跨頁，降低場景跳位、色彩跳變 | **靜態畫面驗證** |
| T12 | 報紙／畫框揭露 | 主視覺拉遠成為空間內某個物件的局部 | **待實播** |
| T13 | 遮擋式換景 | 前景物件遮蔽視線以協助鏡頭換場 | **待實播** |
| T14 | 物件內縮放 | 保留可辨識的錨點，避免突然換新素材造成 Morph 匹配失敗 | **設計配方** |
| T15 | 原生文字分層 | 字、背景、框、圖形分開；文字仍可在 PPTX 編輯 | **已驗證** |
| T16 | 延遲資訊揭示 | 鏡頭停止後再讓觀眾閱讀安裝指令，少做花哨字體飛入 | **設計配方** |
| T17 | 技術指令等寬 | 終端機使用 `DejaVu Sans Mono` 等真等寬字型 | **本地渲染驗證** |
| T18 | 視覺安全區 | 16:9，主體遠離邊緣，標題與關鍵資訊避免裁切 | **本地靜態檢視** |
| T19 | 自動播放節奏 | 每頁 `advTm` 保留閱讀停留，Morph 用 0.8–1.9 秒起試 | **XML 設定完成；實播待測** |
| T20 | 解說頁主題一致 | 同色票、字型、細線、物件與視覺錨點連續 | **靜態畫面驗證** |
| T21 | 二維 / 三維誠實標示 | 2.5D 不寫成真 3D；官方 WebGL / 3D beta 分開 | **來源查證** |
| T22 | 圖像權利索引 | 官方 MIT repo、原創 SVG、第三方照片各自記錄 | **流程規範** |
| T23 | 大圖去重 | 相同 PNG / WEBP 嵌入多頁時 SHA256 去重、重寫 media rels | **OOXML 驗證** |
| T24 | XML 靜態契約 | 驗證 PPTX ZIP、14 頁、13 Morph、`!!` 跨頁命名 | **本地執行** |
| T25 | 手機／電腦實播 QA | 桌面 PowerPoint 逐段觀看並測錄，手機檢查可讀性 | **待使用者或支援環境實測** |

> 「設計配方」是合理且可實作的視覺方法，不是這次已在 Microsoft PowerPoint 實播通過的證據。

## 可重複執行的產製流程

先依實際目標設計關鍵姿態（scene pose），並以**同一張**授權、原創或官方允許重用的圖片作為世界底圖。PptxGenJS 在每頁加入**同一個 altText** 的主圖，移動座標 / 改變大小：

```javascript
slide.addImage({
  path: imagePath,
  x: cameraX,
  y: cameraY,
  w: cameraWidth,
  h: cameraHeight,
  altText: '!!ANATOMY_WORLD'
});
```

然後產生未加 Morph 的 PPTX，最後執行：

```bash
npm install --no-save pptxgenjs
node scripts/build_morph_example.js
python3 scripts/pptx_morph_patch.py morph-draft.pptx morph-native.pptx --duration 1350 --hold 4700
python3 -m unittest discover -s tests -v
```

用 PowerPoint 打開 `morph-native.pptx` → 投影片放映 → 測試從第 1 頁進到第 2 頁是否按預期連續拉遠，繼續看所有頁面。**不要在沒有這個檢查的情況下把 QA 寫成完成。**

## Anatomy 範例內容契約

| 段落 | 內容 | 轉場用途 |
| --- | --- | --- |
| 1–3 開場 / 是什麼 | Anatomy 是製作互動等角技術圖解的 Agent Skill | 機械特寫→拉遠→解釋 |
| 4–6 三類圖解 | SVG、SVG + WebGL、3D beta | 儀表→水波裝置→轉盤 |
| 7–8 安裝 / 使用 | 官方安裝指令與 Codex 呼叫 | 鏡頭推至終端機，停留閱讀 |
| 9–10 優缺點 | 結構可讀、動作和讀值聯動；費時、不擅長人像與一般圖表、3D beta | 分析面板左右移動 |
| 11–12 人群判斷 | 適合開發文件／技術教學；不適合只要快速靜態圖者 | 同場景反向重新構圖 |
| 13–14 結論與出處 | 條件式推薦與官方連結 | 最後拉遠完整場景 |

**官方資訊**：`https://github.com/wheresryan22/anatomy`。實際支援 Claude Code、Antigravity、OpenCode、Codex、MiniMax Code。Codex 安裝為 `npx skills add wheresryan22/anatomy -g -a codex`、呼叫為 `$anatomy`；其他多種代理使用 `/anatomy`。原作者明確列出 3D 模式為 beta，並指出製圖成本與用途限制。**不能拿影片中原創儀表視覺宣稱是 Anatomy 的真實產出。**

## 素材權利與來源

| 素材 | 來源 | 使用決策 |
| --- | --- | --- |
| 工業機械長廊／儀表／終端機概念 SVG | 本專案原創程序圖，並非 Anatomy 示範圖 | 可以隨 source 分發，但不得稱作 Anatomy 工具實測 |
| 原作者 README / 命令 | `wheresryan22/anatomy` repo | 事實引用、附回原始網址 |
| 原作者官方範例截圖 `.github/assets/*.webp` | 官方 GitHub repo，MIT © 2026 Ryan | 需要保留 MIT 版權與許可通知、標示來源；本次簡報**未嵌入**官方截圖 |
| 使用者提供的 Canva 參考影片 | 目前對話附件 | **僅比較設計語言**，不加入此 repo 或公開成品 |
| 第三方照片、音樂、字型檔 | 未加入 | 來源授權不明不得直接打包；不要分發字型檔 |

## 品質驗收：絕對不能偷換概念

- 本地已檢查：`.pptx` 可解包、14 頁存在、13 段 Morph、14 個跨頁 `!!ANATOMY_WORLD`、XML 可解析、原生文字存在、LibreOffice 能產生靜態投影片縮圖。
- 對單張場景使用 2D 大幅圖片以實現推拉，會刻意超出投影片邊界；通用「所有元素不可超界」檢查會報警。需**只允許已標註的世界底圖超界**，其餘文字 / 資訊框不得超界。
- 程式渲染的單頁照片不能證實 Morph 在 PowerPoint 實播正常；**需要使用支援 Morph 的 PowerPoint 觀察實際播放**。
- PPTX 是可以編輯文字 / native shapes 的原稿，但場景主圖是嵌入式 PNG，不可將每一個像素當成 PPT 圖層單獨編輯；保留 SVG source。
- 製作人仍須檢查轉場跳幀、物件錯配、文字遮擋、繁體字缺字、旁白與音訊授權；沒有這些驗收，狀態只能寫 **Preview / Pending**。
- 此 PR 不變更 Blender 原片頭，也不自動合併，不發布影片。

**本地測試記錄（2026-11-06）**：14 slides、13 `p159:morph`、14 主視覺配對名稱；ZIP 媒體去重從 15 個媒體檔減少為 2；`LibreOffice` 靜態渲染成功；`slides_test.py` 報告 14 頁存在越界物件，原因是跨頁大壁畫故意超出投影片畫框，不能將其當作整份無視覺問題的通過證據；真正 PowerPoint 動畫實播未執行。
