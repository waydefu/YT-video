# YT-video — 治理盤點與執行入口

> 稽核快照：**2026-11-07**；取自 GitHub `main` at `c364c7c763f2392ac13a14c5cfb18cf084170107`，不是即時監控。PR 合併後如 GitHub 狀態改變，必須重新查證。本文件提供分類與待辦，不表示 Github Branch Protection 已設定。

## 一、目前應以哪份文件為準

| 工作類別 | 現行入口 | 身分與驗收界線 |
| --- | --- | --- |
| 全專案權限／品質門檻 | [`../AGENTS.md`](../AGENTS.md)、[`QUALITY-GATED-WORKFLOW.md`](QUALITY-GATED-WORKFLOW.md) | G0–G5；不得用 CI 代替實播 |
| 科普 PowerPoint 主線 | [`WORKFLOW-EXPLAINER-DECK.md`](WORKFLOW-EXPLAINER-DECK.md)、[`ANATOMY-EXPLAINER.md`](ANATOMY-EXPLAINER.md) | P0–P9；13 頁僅 PREVIEW，原生 Morph 實播與手機驗收未完成 |
| 片頭 **現行創意需求** | [`SHOTLIST.md`](SHOTLIST.md) | 左燈→右燈、兩次低音開燈聲、只有粉塵、地面灰塵逆向重組 Logo；尚未證明程式符合 |
| 片頭 V4 技術實驗 | [`V4-ASSETS.md`](V4-ASSETS.md)、`../blender/v4_opening.py` | 高品質 CC0 模型、3D smoke；不是最終已驗收的片頭 |
| Canva 研究 | [`CANVA-CINEMATIC-MOTION.md`](CANVA-CINEMATIC-MOTION.md) | 資料／研究，非 Canva 原生動畫作品 |
| AI 訂閱額度比較簡報 | [`AI-SUBSCRIPTIONS-DECK.md`](AI-SUBSCRIPTIONS-DECK.md) | 20 頁 PREVIEW；資料取自使用者文件（快照 11/03，未重新核對）；原創圖表，無第三方圖像；實播未驗 |
| 2D 環境循環技術 | [`PPTX-LIVE-MOTION.md`](PPTX-LIVE-MOTION.md) | 工具能力實驗，非 Anatomy 主線交付，也不等同 Live2D |
| 舊 Anatomy 四頁實驗 | [`ANATOMY-SPIKE-QA.md`](ANATOMY-SPIKE-QA.md)、[`ANATOMY-RAPTOR-V5-QA.md`](ANATOMY-RAPTOR-V5-QA.md) | 只留作歷史比對；不要當目前 Anatomy 作品 |
| 片頭 **V3 舊分鏡** | [`archive/SHOTLIST-V3-LEGACY.md`](archive/SHOTLIST-V3-LEGACY.md) | 歷史資料，含已取消的石裂／碎石；**禁止當現行規格** |

## 二、流程與證據分層

- **G0 → G1 → G2 → G3 → G4 → G5** 為權限及品質總流程，PowerPoint 另按 P0–P9 執行。
- CI / OOXML 只證明 **A 結構**；LibreOffice 靜態圖及 Morph 幾何代理是 **B**；實際 Microsoft PowerPoint 放映才是 **C**；桌機、手機觀看是 **D**；事實與授權是 **E**。
- 尚無 C/D 實播證據，不能把作品標示 `FINAL-APPROVED`。PR **合併**不代表作品**驗收通過**。
- 現有 9 條媒介專用 Actions 工作流（Blender ×3、Anatomy ×4、PPTX 實驗 ×2）依路徑／手動執行；新增 `.github/workflows/governance.yml` 做**所有 PR 的輕量基準測試**，但不代替媒介工作流或真正播放。
- 舊工作流和舊程式沒有在本 PR 刪掉：保留可重現性與歷史證據，日後依測試覆蓋、呼叫關係與授權紀錄決定是否封存。

## 三、GitHub 治理現況（2026-11-07 快照）

| 項目 | 查得狀態 | 決策 |
| --- | --- | --- |
| PR / Issues | 0 筆 open PR；0 筆 open issue（稽核時） | 不新增無意義的空 Issue；目前 PR 會讓數字改變 |
| `main` | API 顯示 `protected: false` | **P0：由 repo 管理員設定分支保護或 Ruleset**；本 PR 無法代替 GitHub 設定 |
| Rulesets | GET 返回空陣列 | 建議正式設定，啟用後再次核對生效範圍 |
| 分支 | main + 8 條非 main 分支 | **先保留**；不得因 PR 已合併就盲刪（squash merge 下可能不是 Git commit 祖先） |
| 最新 Anatomy CI | [Actions #42230737798](https://github.com/waydefu/YT-video/actions/runs/42230737798) 成功，來源提交 `7626cf5` | **A/B 自動建置成功**；不得寫成 C/D 播放成功 |
| `main` CI | 最新 merge commit `c364c7c` 無可確認的同 SHA PR workflow run | 增加每次 push main 都執行的基準；首次執行須在新 PR merge 後驗證 |

### 待 repo 管理員在 GitHub 設定的 P0 保護（不可用文件替代）

1. 進入 **Settings → Rules → Rulesets**（或 **Settings → Branches**），建立套用在 `main` 的 Active 保護規則。一般建議：禁止 force push / 刪除主分支、要求 PR、要求必要 CI 通過；是否要求審核人數由權限與協作方式決定。
2. 在此 PR 合併、`governance / docs-and-policy` job **實際出現過且穩定**之後，才能把該檢查選為 Required status check；不可填未曾出現的名稱。媒介專用檢查若有 `paths` 過濾，**不要**在未處理「Skipped = pending」風險前直接列為全域 Required。
3. 若 repo 所有者只有一人，注意必要 Approving review 設定可能造成無法自行合併；依實際權限選擇，避免自鎖。
4. 本連接器對保護設定的查詢／修改權限有限；**未實際更新 GitHub 設定，不能標成已保護**。

### 歷史分支盤點（尚未逐支比對／未刪除）

| 分支（2026-11-07 查到） | 暫定分類 |
| --- | --- |
| `ccr-dc643977-odpk8z` | Claude 工作分支；需核對 PR #8–#10 對應提交 |
| `docs/canva-cinematic-motion-research-20261106` | Canva 研究歷史分支（PR #3） |
| `docs/quality-gated-production-workflow-20261106` | 治理規範歷史分支（PR #5） |
| `feat/anatomy-official-morph-spike-20261106` | Anatomy 四頁歷史分支（PR #6） |
| `feat/broke-trio-blender-cinematic-intro` | Blender 初始片頭開發分支；需檢查未合併改動 |
| `feat/native-pptx-morph-production-20261106` | Morph 工具歷史分支（PR #4） |
| `feat/v4-sculpted-bust-sequential-spotlights` | V4 石像燈光開發分支；需檢查未合併改動 |
| `fix/anatomy-single-scene-morph-qa-20261106` | 單一 Raptor 場景歷史分支（PR #7） |

**刪除前必做**：對各分支進行 `main...branch` 的檔案差異檢查，核對相關 PR 是否已完成且原始提交可在主線追溯；squash merge 造成的提交圖差異不可單憑 `git branch --merged` 判斷。刪除遠端分支需獨立授權／審核。

## 四、仍未關閉的技術債

- 現行 [`SHOTLIST.md`](SHOTLIST.md) 已同步最新創意要求，**但** `config/production.json`、`blender/scene.py` 與音效腳本可能仍是 V3 石裂／碎石版本；這是**程式／素材與規格未同步**，應另開製作 PR 重構，不能把本次文件整理說成片頭已修好。
- Anatomy 13 頁有 A/B 證據，C/D 仍未驗。字級小、官方線條低對比及實際 Morph 效能是已知風險。
- GitHub Actions 成功不是視覺品質 PASS；需要播放環境與影片／互動畫面證據。
- README 曾以多行混寫現行主線與歷史樣片；本次提供此導覽，不刪除研究或原有來源資料。

## 五、治理變更原則

這個 PR 只改**規範、索引、文件狀態與輕量 CI**，不改影片美術、不刪 GitHub 分支、不合併 PR、不更動分享／存取權限。所有改動依 `AGENTS.md` 維持最小化。任何「完成」必須有對應測試證據。
