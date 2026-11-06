# BROKE TRIO — YT-video

繁中影音製作工作區，使用 **原創 3D 場景 + 音訊腳本 + FFmpeg** 產生可反覆維護的 YouTube 片頭。此 PR 包含可編輯的 Blender 程式化場景，**目前是未在 Blender 真正渲染／人工驗收的 V3 blockout**，不能當成已完成電影級作品。

## 這一版要做什麼

10 秒、16:9、1920×1080、24 FPS，黑場體積霧 → **左燈亮／滅** → **右燈亮／滅** → 石像穿煙而出 → 同一鏡頭推至臉部 → 龜裂碎石 → 3D 粒子落下重組三尊雕像 → 片名定格。**兩盞燈不重疊；兩盞皆熄滅後雕像才出場。**

## Repo 導覽

| 位置 | 作用 |
| --- | --- |
| `blender/scene.py` | 程序化石像、4D 噪聲體積霧、兩盞聚光燈、鏡頭、3D 粒子、排版與合成 |
| `scripts/soundtrack.py` | 自製立體聲低頻、煙霧、打光與破碎音效，不使用外部樣本 |
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
- 崩解採 deterministic 粒子拋物運動，不是烘焙的 rigid-body 碰撞物理。
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
- [共用 AI 技能：`.agents/skills/quality-gated-production/SKILL.md`](.agents/skills/quality-gated-production/SKILL.md)
- [PR 驗收表：`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)

**驗收準則**：CI／檔案結構檢查、靜態畫格、原生動畫實播、桌機／手機體驗、素材授權各自分開回報。沒有目標軟體能播放，就只能標記未驗證，不能宣稱已達到參考影片品質。先做 10–15 秒最難轉場，通過後才擴張長片；純文件改動則使用比例適當的文字／連結檢查。

