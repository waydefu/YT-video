# BROKE TRIO — YT-video

繁中影音製作工作區。**目前沒有任何一條製作線完成最終美術與原生播放驗收**；工作流或 PR 合併不代表成品達標。

### 現行入口（先看這裡）

| 製作線 | 現況 | 主要阻擋點 |
| --- | --- | --- |
| **Anatomy 13 頁科普簡報** | **SPIKE / PREVIEW**；官方素材、Morph 結構與靜態代理已有建置證據 | **PowerPoint 未實播**、手機閱讀及事實人工複核未通過 |
| **AI Coding／Agent 七平台訂閱額度比較簡報（20 頁）** | **SPIKE / PREVIEW**；依使用者文件 v5.1（快照 2026-11-03）繪製的原創圖表（OpenCode、Cursor 標誌各有授權狀態紀錄，其餘平台純文字）+ 無縫 Morph；說明見 [`docs/AI-SUBSCRIPTIONS-DECK.md`](docs/AI-SUBSCRIPTIONS-DECK.md) | **PowerPoint 未實播**；價格與額度**未向供應商重新核對**，發布前必須更新 |
| **BROKE TRIO Blender V4 片頭** | 使用授權 CC0 雕像的 3D 技術預覽，**非最終成品** | 現行「低音開燈、只有粉塵、地面逆時間重組 Logo」尚未核實已實作 |
| **可重用科普 Morph 工具組** | 4 頁示範、轉場插補代理及 QA 腳本 | 只屬技術樣片；**PowerPoint 未實播** |

### 歷史研究／非當前交付物

| 類別 | 狀態 |
| --- | --- |
| Canva 電影式動畫技巧 | RESEARCH：文件與配方，不是已驗證的 Canva 原生動畫 |
| Anatomy #6 四頁展示牆、#7 單一 Raptor | 舊候選與失敗紀錄，保留可追溯性；現行內容以 13 頁簡報為準 |
| Living Scene 2D 循環工具 | SPIKE：技術能力研究，不等同 Live2D，也不是 Anatomy 正式作品 |
| Blender V3 程序化石像 | 歷史 blockout；**石裂／碎石方案已不符合現行要求** |

### 治理與目前規格

- [專案治理與分支／CI 盤點](docs/GOVERNANCE-STATUS.md)：現行／歷史入口、手動 GitHub `main` 保護步驟與仍待實播項目。
- [現行 BROKE TRIO 片頭分鏡](docs/SHOTLIST.md)：兩盞燈依序開／關，燈聲僅重低音；粉塵時間反轉重組 Logo，不做石裂／碎石。
- [V3 舊分鏡封存](docs/archive/SHOTLIST-V3-LEGACY.md)：僅供追溯，**不得作新影片標準**。
- [G0–G5 品質治理](docs/QUALITY-GATED-WORKFLOW.md) 與 [P0–P9 科普簡報製作流程](docs/WORKFLOW-EXPLAINER-DECK.md)。

以下 Blender 工程與設定部分仍可能反映 V3／V4 實驗，**更新分鏡不等於既有程式已改成粉塵版**。需要在獨立的製片 PR 裡修改、渲染和驗收。

## 現行片頭想達成什麼

10 秒、16:9、1920×1080、24 FPS：黑場體積霧 → 左燈亮／滅 → 右燈亮／滅 → 雕像於兩燈熄滅後出場、鏡頭推近 → **粉塵轉場（不裂石、不掉碎石）** → 地面粉塵如時間倒轉般匯聚成品牌 Logo → `BROKE TRIO` 定格。亮燈音效**只用重低音開燈聲**；分鏡順序以 `docs/SHOTLIST.md` 為準，秒數仍需實際樣片確認。

## Repo 導覽

| 位置 | 作用 |
| --- | --- |
| `blender/scene.py` | 程序化石像、4D 噪聲體積霧、兩盞聚光燈、鏡頭、3D 粒子、排版與合成 |
| `scripts/soundtrack.py` | V3 原創聲效腳本（含已淘汰的碎裂效果）；不得直接視為現行聲音契約 |
| `scripts/render.sh` | Smoke 五幀驗證、Preview/Final 渲染、FFmpeg 輸出 |
| `scripts/validate_media.py` | 影片寬高、比例、FPS、編碼、音訊、時長驗證 |
| `config/production.json` | 比例、安全邊界、時間線規格 |
| `docs/SHOTLIST.md` | 分鏡時間和視覺驗收 |
| `docs/ASSET-RIGHTS.md` | 素材來源與授權 |
| `docs/TECH-REUSE.md` | 對照 `waydefu/Research-` 可用／不可直接用的研究 |
| `.agents/skills/cinematic-intro/SKILL.md` | 製片代理工作流程 |
| `.github/workflows/render.yml` | PR 靜態檢查；Actions 手動觸發真 Blender 渲染 |

## 執行方式

需 **Blender 4.x**、**FFmpeg/FFprobe** 與 Python 3。Blender 工程由 Python 腳本自動生成，不必安裝第三方 Blender 插件。

```bash
python3 -m unittest discover -s tests -v
bash scripts/render.sh smoke
bash scripts/render.sh preview
bash scripts/render.sh final
```

`smoke` 產生 5 張預覽幀；`preview` 為 960×540 / 24fps MP4；`final` 為 1920×1080 / 24fps MP4。GitHub Actions 預設僅執行靜態檢查；進入 **Actions → BROKE TRIO original 3D checks / rendering → Run workflow** 並選 `smoke`、`preview` 或 `final` 才會啟動 Blender。成品下載自該次 workflow 的 Artifacts。

## 目前明確限制

- 3D 石像是原創程序化幾何的**預演模型**，不是高精度雕塑掃描。
- 煙霧是 Blender 3D volumetric shader，不是 Mantaflow 流體模擬。
- **歷史 V3** 崩解採 deterministic 粒子拋物運動而非 rigid-body 碰撞；**此設計已被現行「僅粉塵」要求取代，相關程式尚待修改**。
- CI 靜態檢查不能證明畫質達標；需先跑 smoke、人工檢視構圖、修飾角色臉部與碎片，完整渲染後再手動驗收。
- 不使用對話中的他人圖片作最終影片素材，Research- 裡的技術連結也不代表可複製其影像、音樂或模型。

不自動合併 PR、不自動公開上傳 YouTube，正式發布須另外核准。

## Canva 動態簡報 / YouTube 技巧庫（研究版）

此庫與 Blender 3D 片頭**並行**：Canva 適合連續構圖與快速資訊呈現，真 3D / 煙霧 / 物理破碎仍使用 Blender。研究檔案列出官方來源、費用 / 授權限制與未實測項目；**文件完成不等於動畫完成**。

| 位置 | 功能 |
| --- | --- |
| [`docs/CANVA-CINEMATIC-MOTION.md`](docs/CANVA-CINEMATIC-MOTION.md) | Canva 動態簡報／YouTube 原生實作指南：轉場、視差、音訊、字幕、輸出與常見限制 |
| [`docs/CANVA-TECHNIQUE-INDEX.md`](docs/CANVA-TECHNIQUE-INDEX.md) | **40+ 項技巧索引**；官方功能 F / 待驗證的鏡頭設計 R / 方案待確認 C，附官方來源 |
| [`docs/CANVA-REFERENCE-RECIPE.md`](docs/CANVA-REFERENCE-RECIPE.md) | 使用者提供參考片的時間段拆解、Anatomy 動態簡報示範分鏡（未製作影片） |
| [`docs/CANVA-QA.md`](docs/CANVA-QA.md) | 分段預覽、逐格驗收、繁中與安全區、音畫與合法授權、ffprobe／FFmpeg 範例 |
| [`.agents/skills/canva-cinematic/SKILL.md`](.agents/skills/canva-cinematic/SKILL.md) | 後續 AI 代理製作或審查 Canva 影片時使用的標準流程 |

**使用順序**：先讀手冊與技巧索引 → 選 1–2 個轉場配方做短片段 → Canva 預覽 / MP4 輸出 → 桌面及手機實測 → 資產權利檢查 → 使用者批准。不能把參考片影格、未經授權的音樂或字型上傳到此專案。

## 品質優先的統一製作流程（所有媒介）

本 repo 後續影像、Canva / PPTX 動態簡報、Blender、網站／互動及相關程式的共同工作流程：

**交付契約 → 品質與授權素材 → 最小可驗證樣片 → 自己先實際驗收 → 不合格重做 → 通過才擴大 → 提交可查證 PR。**

- [完整規範：`docs/QUALITY-GATED-WORKFLOW.md`](docs/QUALITY-GATED-WORKFLOW.md)
- [簡報完整工作流（P0–P9，含官方素材、轉場規則、踩坑紀錄）：`docs/WORKFLOW-EXPLAINER-DECK.md`](docs/WORKFLOW-EXPLAINER-DECK.md)
- [共用 AI 技能：`.agents/skills/quality-gated-production/SKILL.md`](.agents/skills/quality-gated-production/SKILL.md)
- [PR 驗收表：`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)

**驗收準則**：CI／檔案結構檢查、靜態畫格、原生動畫實播、桌機／手機體驗、素材授權各自分開回報。沒有目標軟體能播放，就只能標記未驗證，不能宣稱已達到參考影片品質。先做 10–15 秒最難轉場，通過後才擴張長片；純文件改動則使用比例適當的文字／連結檢查。

## 原生 PowerPoint 動態簡報（Morph）

這條路線用 **PptxGenJS + PowerPoint OOXML** 製作可編輯的 `.pptx`，透過跨頁相同 `!!` 物件名稱實現鏡頭推進、平移、拉遠和空間揭露。**不是把外部 MP4 當作 PPT 動畫**。與 Blender 片頭及 Canva 研究獨立運作。

| 檔案 | 用途 |
| --- | --- |
| [`docs/PPTX-CINEMATIC-MORPH.md`](docs/PPTX-CINEMATIC-MORPH.md) | 25 個電影式 Morph 製作配方、官方來源、授權、靜態與實播品質驗收 |
| [`scripts/pptx_morph_patch.py`](scripts/pptx_morph_patch.py) | 無第三方 Python 依賴的 Office 原生 `p159:morph` / fade fallback 寫入器；可去重重複媒體 |
| [`scripts/build_morph_example.js`](scripts/build_morph_example.js) | PptxGenJS 五鏡頭可編輯示範產生器；可改用已授權的 `WORLD_IMAGE` |
| [`tests/test_pptx_morph_patch.py`](tests/test_pptx_morph_patch.py) | XML 物件名稱、13 範例相關流程的核心 Morph、Fallback、圖片去重單元測試 |
| [`.agents/skills/powerpoint-cinematic/SKILL.md`](.agents/skills/powerpoint-cinematic/SKILL.md) | 後續 AI 製作／審查 PowerPoint 轉場時的技能流程 |

```bash
npm install --no-save pptxgenjs
node scripts/build_morph_example.js
python3 scripts/pptx_morph_patch.py morph-draft.pptx morph-native.pptx --duration 1350 --hold 4700
python3 -m unittest discover -s tests -v
```

**限制**：PPTX OOXML 結構可在 CI 驗證，但真正的 Morph 影格品質仍須在支援 Morph 的 PowerPoint 播放檢查；LibreOffice 靜態輸出不等於 Morph 通過。Anatomy **4 頁 / 3 段 Morph spike 為歷史樣片**（`scripts/anatomy_official_morph_spike.py`，見 `docs/ANATOMY-SPIKE-QA.md`）；**現行主線是 13 頁 Anatomy 科普簡報**，同樣尚未實播驗收。較早對話的 14 頁研究樣片不在此 repo。

## Anatomy 科普簡報（官方原始資料圖 + 無縫 Morph 轉場）

13 頁正式簡報，說明 Anatomy 是什麼、能做什麼、怎麼安裝與使用、適合誰、優缺點、不適合誰；圖像全部取自上游官方（固定 commit、SHA256 核對、MIT 授權隨檔）。內容、授權、事實台帳與已知問題見 [`docs/ANATOMY-EXPLAINER.md`](docs/ANATOMY-EXPLAINER.md)。

```bash
python3 scripts/anatomy_assets.py            # 下載並核對官方素材（需要 poppler-utils、Node + playwright）
python3 scripts/build_anatomy_explainer.py   # --hold 依旁白長度設定；字型需已安裝（見文件）
python3 scripts/pptx_validate.py build/anatomy/anatomy-explainer.pptx --min-loops 0 --strict \
  --readable build/anatomy/anatomy-explainer.readable.json
```

## 科普 YouTube 正式簡報：無縫 Morph 轉場（方法與範例）

正式可編輯 PPT，頁與頁之間是連續的鏡頭式轉場（鑽進視窗、平移、拉遠揭露）。方法、規則、流程與狀態見 [`docs/PPTX-SEAMLESS-EXPLAINER.md`](docs/PPTX-SEAMLESS-EXPLAINER.md)。

```bash
pip install python-pptx==1.0.2
python3 scripts/build_science_explainer.py
python3 scripts/pptx_validate.py build/science-explainer/science-explainer-spike.pptx --min-loops 3 --hold-ms 4800 --strict \
  --readable build/science-explainer/science-explainer-spike.readable.json
python3 scripts/pptx_morph_proxy.py build/science-explainer/science-explainer-spike.pptx build/science-explainer/proxy.pptx
```

**驗證狀態**：A 結構與 B 靜態／轉場代理（幾何插值，只能否決不能證明）已自查；**C PowerPoint 實播與匯出影片 NOT RUN**；科普事實為草稿待審。

## 選用：自動播放環境動態層（「Live 2D 式」誤讀留下的工具）

簡報一開始播放，所有圖層就持續微動（呼吸、眨眼、髮絲擺動、漂浮、粒子、旋轉光芒），搭配 Morph 鏡頭與視差。**這是剛體 2D 變換，不是 Live2D 網格變形**；完整研究、能力邊界與工作流見 [`docs/PPTX-LIVE-MOTION.md`](docs/PPTX-LIVE-MOTION.md)。

| 檔案 | 用途 |
| --- | --- |
| [`scripts/pptx_motion.py`](scripts/pptx_motion.py) | 標準庫工具：依名稱把 `breathe / sway / blink / float / orbit / spin` 寫成自動啟動、重複到投影片結束的 `p:timing` |
| [`scripts/pptx_validate.py`](scripts/pptx_validate.py) | A 層驗證：XML 順序、ID 唯一、Morph 錨點、循環覆蓋率、換頁相位、文字安全區 |
| [`scripts/build_living_scene.py`](scripts/build_living_scene.py) | 原創向量分層角色 + 3 鏡頭最小樣片（G2） |
| [`tests/test_pptx_motion.py`](tests/test_pptx_motion.py) | 動態層與驗證器單元測試 |

```bash
pip install python-pptx==1.0.2
python3 scripts/build_living_scene.py
python3 scripts/pptx_validate.py build/living-scene/living-scene-spike.pptx --hold-ms 2400 --spin-symmetry-deg 22.5 --strict
python3 scripts/build_living_scene.py --static --output build/living-scene/living-scene-static.pptx   # 降級版：無循環動態
python3 -m unittest discover -s tests -v
```

**驗證狀態**：A 結構已本地測試；B 靜態已自查；**C 原生實播 NOT RUN（無 Microsoft PowerPoint）**。在 PowerPoint 實播並由使用者觀看前，一律只能稱 SPIKE。
