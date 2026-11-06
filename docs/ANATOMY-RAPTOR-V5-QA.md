# Anatomy — 單一場景原生 Morph 自驗報告（v5 CANDIDATE）

**2026-11-06：修復已合併 PR #6 的視覺失敗，不宣稱成品品質通過。**

## 修正前後

| 使用者提供的舊版失敗證據 | 本次處置 |
| --- | --- |
| 第二張 IDEAS, MADE TANGIBLE 被截斷 | 移除整幅橫向展示牆，所有可編輯文字固定在安全區 |
| 第三／四張左邊殘留前一張被裁開的裝置 | **四張都使用同一台 Raptor 引擎**，只對同一影像做攝影機推拉 |
| 大塊深色模板、白色截圖卡片，不像動畫 | 改成米白紙張材質＋深色中文字＋銅色標線，去掉貼圖 UI 及外框 |
| 交付前沒有自行看完整畫面 | 本地逐頁渲染、檢視 4 頁四宮格，數輪自我淘汰並重做 |
| 假裝靜態 XML 通過等於 Morph 達標 | 明確紀錄 PowerPoint 原生播放 **BLOCKED**，不稱 FINAL |

## 本次產物契約

- 原生可編輯 PPTX、16:9、4 頁、3 段 Office Morph byObject，**不是內嵌 MP4**。
- 一個不換場的官方 Raptor 引擎：局部特寫 → 拉遠完整裝置 → 重新聚焦結構 → 全貌。
- 同一物件跨頁固定使用 !!ENGINE 與 !!PAPER；原生文字仍可修改。
- 四個 shot 的移動時長由 OOXML 設定；尚未經 PowerPoint 播放測量。
- 來源：https://github.com/wheresryan22/anatomy。原始圖像並不隨 PPTX 保留作者 HTML 的互動效果。

## 來源權利

固定原作者 revision：1482e8469b0a9e0d8cc18ea2740a01423d29ae80

官方圖：.github/assets/raptor-engine-firing.webp

圖像 SHA256：c42a9eb6aacb506f7baf0fd91d4fbb04649999e9615f9847585daff595a62d55

授權：MIT License © 2026 Ryan；完整授權文字由 CI 下載且放在 PPTX 每頁講者備註。原創紙張底紋與標線由建置程式產生。不使用使用者參考影片影格當成品素材。

## 重現與 CI

建置程式：scripts/anatomy_raptor_morph.py

GitHub 工作流：.github/workflows/anatomy-raptor-morph.yml

建置命令：

    python scripts/anatomy_raptor_morph.py \
      --image build/anatomy-raptor/raptor-engine-firing.webp \
      --license build/anatomy-raptor/LICENSE_ANATOMY.txt \
      --output build/anatomy-raptor/Anatomy_Raptor_Morph_Candidate.pptx

CI 下載固定官方素材 → SHA256 校驗 → 產出 PPTX → XML / ZIP 與可編輯文字位置檢查 → LibreOffice **靜態** PNG 預覽 → 上傳候選原稿及 MIT LICENSE。

## 品質門檻

| 層級 | 當前結果 | 證據與限制 |
| --- | --- | --- |
| G0 原生輸出契約 | PASS | PPTX + Morph，不以 MP4 取代 |
| G1 來源和授權 | 本地 PASS；CI 待驗 | 固定原圖 SHA 與 MIT © 2026 Ryan |
| G2 最小場景 | 本地 PASS | 4 頁／3 段原生 Morph 結構 |
| A 結構 | 本地 PASS | 每頁 !!ENGINE、3 個 Morph、3 個 fade fallback、文字在畫布內、ZIP 與 XML 可解析 |
| B 靜態視覺 | **局部修復 PASS；對參考品質仍 FAIL** | v3、v4、v5 重排，四頁無切字或上一頁殘圖；但官方 900px 圖放大後欠缺參考片的精細運鏡與美術層次，尚不應交付 |
| B 場景連續 | 代理插補模擬已檢 | 12 張幾何姿態，**並非** PowerPoint 影片 |
| C PowerPoint **原生實播** | **BLOCKED / NOT RUN** | 目前無 Microsoft PowerPoint 播放環境；不能宣稱絲滑 |
| D 手機靜態可讀性／實播 | **390px 靜態檢視；實播 BLOCKED** | 本地 390×219 縮圖檢查主要文字，並調整摘要成 21pt 短句；仍沒有 Microsoft PowerPoint 行動端實播證據 |
| E 內容正確與權利 | 本地 PASS | 官方圖、授權、官方 SVG / WebGL / 3D beta 用語 |

### 尚未消除的風險

1. 官方來源圖片只有 900×940 像素，局部特寫會放大且細節較軟；不能稱 3D 動畫或高畫質向量。
2. PPTX 是**用原生 Morph 推拉的靜態官方展示圖**，沒有原網頁的鼠標互動。
3. PowerPoint 的真正 Morph 影格和時間曲線未實測。

### Gate 決策

- G3-C 及 G3-D 未驗證，所以狀態仍為 **CANDIDATE / NOT FINAL**。
- 不把單頁靜態檢查當成 Morph 實播；不因 CI 綠就判定符合使用者提供的參考影片。
- 本 PR 應保留待驗，**不得未經另行實播證據就合併或交付為正式成品**。
- 只有實播成功且品質符合參考後才可進入長片製作。
