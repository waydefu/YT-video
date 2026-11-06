# PowerPoint「Live 2D 式」動態簡報：研究、能力邊界與完整工作流

> 版本 2026-11-06｜狀態：**RESEARCH + SPIKE**。結構（A）與靜態畫面（B）已自行檢查；**Microsoft PowerPoint 實際播放（C）未執行 = BLOCKED**。本文件不是任何成品通過驗收的證據。

## 0. 先釐清交付契約（G0）

使用者要求：**簡報一開始播放，感覺就像 Live 2D 動畫**，並提供一支參考影片（Canva 簡報播放的手機錄影）。

| 項目 | 本專案的解讀 | 是否已確認 |
| --- | --- | --- |
| 媒介 | 原生可編輯 `.pptx`；Morph 轉場 + 原生動畫時間軸；**不以 MP4 / HTML 替代** | 沿用既有契約 |
| 「Live 2D 感」 | 播放起每一格都有微動（呼吸、眨眼、擺動、漂浮、旋轉）＋連續鏡頭推拉平移＋多層視差 | **這是我的解讀，需使用者確認** |
| 真正的 Live2D（網格變形、物理、參數互動） | PowerPoint **做不到**（見 §2）；若必須，需 Live2D Cubism 執行階段（網頁／Unity），屬另一個媒介 | **需使用者決定** |
| 參考影片比例 | 9:16 直式（720×1280、30 fps、18.27 秒）；專案規範是 16:9 1920×1080 / 24 fps | **未決：是否另做 9:16 版** |

## 1. 參考影片分析（只用來定品質基準，影格不入庫）

檔案為**手機拍攝螢幕**的錄影（含 AAC 音訊），字幕 "pov: you couldn't afford powerpoint"。以 1 fps 與每 6 格抽樣的低解析接觸表**自行檢視**（未逐格量測運動曲線，下列僅為觀察，不是測量）：

- 前段約 7 秒是 Canva 編輯器：選取物件並顯示**彎折的動態路徑線**，即「物件沿著路徑連續移動」的設計思路。
- 後段播放簡報：報紙標題頁 → 鏡頭向畫面推進 → **紙張撕裂**露出紅白構圖 → 地圖與人像 → **紅白放射狀太陽旋光** → 畫框牆房間。
- 共通特徵：**大膽高對比圖形語言、分層紙質感、轉場之間鏡頭持續移動、沒有明顯「靜止等待」的長停格**（後者為目視印象，未量化）。

**這給我們的設計要求**：不是「每頁漂亮」，而是「**連續運動 + 圖層深度 + 轉場即鏡頭**」。

## 2. Live2D 與 PowerPoint 能力對照（誠實版）

Live2D Cubism 的核心（[官方術語表](https://docs.live2d.com/4.2/en/cubism-editor-manual/glossary)）：圖像指派**網格（ArtMesh）**；**變形器（Warp / Rotation Deformer）**帶動網格頂點；**參數 + 關鍵形狀（keyform）**之間內插形成動作；再疊加物理與待機動作。

| Live2D 能力 | PowerPoint 原生可行性 | 本專案做法 |
| --- | --- | --- |
| 旋轉變形器（頭、髮絲繞軸擺動） | **可行**：`animRot`；樞軸在形狀中心，用「不可見配重」群組把中心移到頸部/髮根 | `!!HEAD`、`!!HAIR_*`（`PIVOT_WEIGHT`） |
| 縮放（呼吸、眨眼） | **可行**：`animScale`，眨眼用 `autoRev` 做閉眼再睜眼 | `!!BODY`、`!!EYE_*` |
| 位移（漂浮、粒子） | **可行**：`animMotion` 路徑（直線 / 閉合橢圓） | `float`、`orbit` |
| 無限待機循環 | **可行**：`repeatCount="indefinite"`（= 重複直到投影片結束）＋播放時自動啟動 | `pptx_motion.py` |
| 鏡頭推拉平移 / 視差 | **可行**：Morph 配對 `!!` 物件，不同深度層用不同位移倍率 | `build_living_scene.py` 的 `depth` |
| 網格變形（臉頰、布料彎曲） | **不可行**；僅**向量自由形狀**頂點數相同時 Morph 可變形，且有限制（見下） | 不宣稱 |
| 物理（頭髮慣性、彈簧） | **不可行**；只能用循環近似 | 標示為「近似待機動作」 |
| 即時參數 / 互動 / 視線追蹤 / 對嘴 | **不可行** | 不宣稱 |

**結論**：PowerPoint 的上限是「**剛體 2D 變換 + 連續鏡頭 + 圖層視差**」＝**類 Live2D 的待機動畫手感（2.5D 動態拼貼）**，**不等於** Live2D。對外一律如此標示。

### 研究所得的關鍵事實與限制

1. **Morph 配對規則**：物件名稱前綴 `!!` 才會強制配對、同頁名稱需唯一；形狀應同方向（皆順時針或逆時針）；**含多個孔洞的形狀不能做幾何變形**；部分舊版只能播放不能編輯 Morph（[Microsoft 官方：Morph 技巧](https://support.microsoft.com/en-us/office/bc7f48ff-f152-4ee8-9081-d3121788024f)）。
2. **自由形狀 Morph**：搜尋摘要指出社群回報 Morph 可變形自由形狀，但編輯點數需大致對應；Merge Shapes 會產生過多頂點；用編輯點改形後 Morph 偶爾退化成淡出（來源為社群／部落格頁面，例如 [PPT Crafter](https://pptcrafter.wordpress.com/2019/02/08/powerpoint-secrets-the-morph-transition/)、[Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/4939399/morph-transition)，**我只讀到搜尋摘要、未逐頁核對，視為未驗證**）。本專案尚未使用，列為進階手法。
3. **連續 Morph 的速度曲線**：搜尋摘要提到有文章指出預設 Smooth Start/Stop 會讓串接的 Morph 在每個接縫減速（**出處未能指認，視為待驗證的風險**）。**待 C 層實測；風險：鏡頭在每頁交界略有停頓感。**
4. **動畫 XML 結構**：`p:timing` → `tmRoot` → `mainSeq` →（`onBegin` 自動啟動的 `par`）→ 效果列。效果列範本取自 PowerPoint 16 實際匯出資料（[ppt-master 預設資料](https://github.com/hugohe3/ppt-master/blob/main/skills/ppt-master/scripts/pptx_animation_presets.json)，其 metadata 標明 `application: Microsoft PowerPoint 16`；該 repo 的授權未在本專案評估，**我們只參照結構、未複製程式碼**）。
5. **未能從 Microsoft 官方文件確認的項目**（誠實列出）：Morph 時長上限；「直到投影片結束」在 XML 中是否一律寫成 `repeatCount="indefinite"`（我們依 OOXML 的 `indefinite` 語意採用，**需用 PowerPoint 另存比對**）；`autoRev` 用在子行為節點（眨眼）的相容性。
6. **匯出成 MP4**（只有在使用者同意作旁路預覽時）：搜尋到的多篇非官方教學文章一致提醒：Morph／複雜動畫匯出可能失敗或掉格、點擊觸發的動畫不會被錄入、4K 僅限較新的 Microsoft 365，建議先做小段試匯出（**未找到 Microsoft 官方佐證，可信度低**）。**匯出的 MP4 只能是預覽，不得取代 PPTX 原生交付。**

## 3. 動態詞彙（`scripts/pptx_motion.py`）

| 效果 | OOXML | 用途 | 注意 |
| --- | --- | --- | --- |
| `breathe` | `animScale` + `autoRev` + 緩入緩出 | 胸口、物件脈動 | 幅度 ≤ 2% 才像呼吸 |
| `sway` | `animRot` + `autoRev`；工具自動把目標**預先反向旋轉**一半幅度，使擺動以原姿態為中心 | 頭、髮絲 | 樞軸 = 形狀中心；用配重移樞軸 |
| `blink` | `animScale`(Y) 子行為 `autoRev`；整個迭代由一個不改變外觀的墊底行為撐長，作為「眨眼間隔」 | 眼睛群組 | `period ≥ 4×close` |
| `float` | `animMotion` 直線 + `autoRev` | 招牌、漂浮物 | 幅度需隨鏡頭縮放（腳本已處理） |
| `orbit` | `animMotion` 閉合三次貝茲橢圓 | 粒子、光點 | 起點在原位 |
| `spin` | `animRot` 360° 線性 | 太陽放射 | 對稱圖案的週期應使每次換頁時角度等價 |

自動啟動的條件：群組的 `<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>`，首個效果為 After Previous，其餘 With Previous。

## 4. 完整工作流（比既有 G0–G5 多了「動態層」）

1. **G0 契約**（§0 的表）：確認原生 PPTX、16:9 或 9:16、「類 Live2D」的定義。
2. **G1 美術與權利**：優先官方授權素材；原創向量只有在**目視審查通過**才可用（`docs/ASSET-RIGHTS.md` 登錄）。**本 spike 的角色是簡單的扁平向量，美術等級遠低於 Live2D 作品**，若要接近參考片的質感需另行取得高品質、可商用的分層插畫（PSD 分層）。
3. **G2 最小樣片**：`python3 scripts/build_living_scene.py`（3 鏡頭、約 14 秒）。先驗最難的三件事：Morph 鏡頭連續、循環動畫自動啟動、換頁時不跳。
4. **骨架（rig）命名規則**：所有會 Morph 或有動畫的物件以 `!!NAME` 命名，同頁唯一；會擺動的部位先群組並加不可見配重移樞軸；眼睛等需縮放的部位自成群組。
5. **時間規則**：每頁停留 `hold`（預設 4800 ms）；循環週期盡量為 `hold` 的因數（2400、1600、4800），使換頁瞬間角色回到原姿態，避免 Morph 起點與動畫姿態不一致造成「跳一下」（`pptx_validate.py --hold-ms` 會警告）。
6. **A 結構**：`python3 -m unittest discover -s tests -v`；`python3 scripts/pptx_validate.py deck.pptx --hold-ms 4800 --strict`。
7. **B 靜態**：LibreOffice 轉 PDF/PNG，逐鏡頭**人眼**檢查構圖、字被裁、安全區（CI 會附圖）。
8. **C 實播（必要，現為 BLOCKED）**：在支援 Morph 的 PowerPoint（桌面版）開 `.pptx` 全程放映：
   - 開檔**不得跳出修復提示**（若跳出 = FAIL，動畫 XML 要改）；
   - 放映後**不點擊**即自動開始所有循環；
   - 螢幕錄影（建議 60 fps），以 FFmpeg 量化「是否有凍結段」：
     `ffmpeg -i rec.mp4 -vf freezedetect=n=-55dB:d=0.4 -an -f null - 2>&1 | grep freeze`
     **通過標準（暫定，待使用者核可）**：整段沒有 ≥ 0.4 秒的完全靜止畫面（轉場邊界除外要逐一目視）。
9. **D 裝置**：桌面與手機（PowerPoint 行動版 / 預覽）檢視可讀性；注意行動版對 Morph 與循環的支援可能不同。
10. **E 權利**：素材、字型（不隨附字型檔）、引用事實。
11. **G5 交付**：附源碼、驗證結果與 `SPIKE/CANDIDATE` 標籤；使用者看過才可升級；**不自動合併／發布**。

## 5. 本次成果與驗證狀態

| 層 | 狀態 | 證據 |
| --- | --- | --- |
| A 結構 | PASS（本地） | `tests/test_pptx_motion.py` 8 項；`pptx_validate.py`：3 頁 / 2 Morph / 每頁 14 個循環效果 |
| B 靜態 | 自查完成（本地 LibreOffice） | 見下方缺陷；CI 會再產出 PNG |
| C 原生實播 | **BLOCKED / NOT RUN** | 無 Microsoft PowerPoint；LibreOffice 不會播放這些動畫與 Morph |
| D 桌面／手機 | NOT RUN | — |
| E 授權 | PASS（原創幾何，無第三方素材） | `docs/ASSET-RIGHTS.md` |

**自查發現的三個最可能降低品質的缺陷**：
1. 美術為簡單扁平向量，**遠不及參考影片的紙質拼貼質感**，更不是 Live2D 級插畫；僅證明「動畫管線」可行。
2. 第 3 鏡頭人物被畫面左緣裁切、左上標題小字與頭髮略有重疊（可調鏡頭或 HUD 位置）。
3. Morph 預設緩入緩出與循環動畫的相位在換頁時是否產生「跳動」——**只有實播才能判定**。

**狀態：SPIKE（不是 CANDIDATE，更不是 FINAL-APPROVED）。**
