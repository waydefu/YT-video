# 課堂簡報：AI 與 Agent 入門（53 頁，原生 Morph，點擊換頁）

> 狀態：**SPIKE／PREVIEW**。層 A（本地測試）與層 B（LibreOffice 靜態逐頁、Morph 代理幀）已做；**桌面 PowerPoint 放映、匯出、投影機實測：NOT RUN**。資料截至 **2026-11-10**，上課前必須重查官方頁。

## 1. G0 契約（2026-11-17，使用者回答）

- **交付物**：可編輯 PPTX，原生 Morph 的無縫鏡頭運動，橫式 16:9，**點擊換頁**（無自動換頁），講者備註含講稿。**不是**影片、不是角色動畫、不是只給網頁。
- **對象與時間**：非技術學生，約 45 分鐘（53 頁含逐步顯示，建議 45–50 分鐘；可跳過同主題的第二步）。
- **轉場**：沿用 Anatomy 的全 Morph 風格：章節之間鏡頭左右／下方交替，章節內原地重畫（列高亮、長條重排、滑桿、logo 由圓環擺到直欄）。
- **品牌圖**：使用者決定「盡量放各家 Logo，授權不明的標『教學引用』並列清單」。→ 見 §3，**這不是授權**。
- **題綱**（使用者列、我擴充）：Agent 是什麼／能幹嗎／要小心；上下文、.md、Skill、Mod、MCP；思考程度；有哪幾家；模型與強弱；怎麼收費（token、5 小時、週／月閘門、月費階梯、API 試算）；免費額度；怎麼選、常見誤解。

## 2. 事實台帳

資料來源都是**使用者自己的已核對文件**，本專案沒有重新向各家官網查證：

| 內容 | 來源（Google 文件） | 等級 |
| --- | --- | --- |
| 月費、倍率、閘門、DeepSeek 單價與試算、免費能做什麼 | 「AI 訂閱額度比較｜YouTube 分鏡 v2.1（官方來源複核 2026-11-10）」＋ v5.1 報告 §13–20 | A（官方頁，使用者於 11-10 複核） |
| Google／Antigravity 新模型（Gemini 4 Carbon、Argon、Hydrogen、Orchestrator）與 11/18 移除項目 | Antigravity 官方頁 models／plans、DeepMind models 頁，**2026-11-17 讀取（經頁面摘要擷取，非逐字核對）** | A（官方頁），但發表日期只到「2026 年 11 月」 |
| 模型陣容與定位、Terminal-Bench 4.0（Vals AI，2026-10-29，同一 Mini-SWE-agent 框架） | v5.1 報告 §8–9 | A／B（榜單為獨立測試，口徑已標示） |
| Skill、Mod、Hook、MCP 的差異與風險 | 「AI Coding Agent 工程品質研究｜Agent Skills × Claude Code Mods｜2026-11-13」 | A（Anthropic 公告與 GitHub 原文） |
| Agent、上下文、.md、思考程度的概念說明 | 教學性說明，無數字；.md 檔名差異採「依工具而定」 | C（說明，不是基準） |

**Google 更新（2026-11-17，使用者提醒）**：官方 Antigravity 模型表現在列 Gemini 4 Carbon（Ultra／Enterprise）、Gemini 4 Argon（付費 Pro 起）、Gemini 4 Hydrogen（11 月發表，快速輕量，Pro 起）、Orchestrator（規劃者＋Hydrogen，官方建議當預設）、Gemini 3.8 Flash（全方案）；Claude 4.6 與 GPT-OSS-120B 標示 11/18 移除。這**推翻 v5.1 報告的舊說法**「Carbon 不是 Antigravity 的模型」，簡報已改。未採用：第三方彙整頁提到的 Gemini Decision 1、Omni 1.2 Flash（官方頁找不到／無日期）；各模型確切發表日、價格也沒有（官方頁未列）。

**誠實界線**：模型「旗艦／主力／輕量」分級是**編輯判斷**（畫面標「非官方」）；沒有「廢」模型，只有適不適合；不同榜單分數不能換算；Gemini 4 Carbon ≠ Argon（兩者現在都在 Antigravity）；DeepSeek 試算僅限 92/7/1 比例；Antigravity 部分舊模型 11/18 下線屬待追蹤。測試：`tests/test_classroom_ai_agents.py` 重算 DeepSeek 四個金額並與 `ai_subscriptions_data.py` 對照（本地通過）。

## 3. Logo 權利紀錄（`scripts/classroom_logos.py`）

- 來源：jsDelivr 上的 `simple-icons`（Claude、Gemini、Kimi、DeepSeek、Cursor、OpenCode 用 16.38.0；OpenAI 在新版已移除，用 13.0.0），**逐檔釘版本與 SHA256**，不符就停止。
- 該套件的圖示資料是 CC0，但**商標仍屬各公司**。manifest 逐筆標為 `NOMINATIVE-CLASSROOM-USE`（教學引用）；**不是** `GUIDELINE-PERMITTED`。畫面頁尾與結語頁都標「Logo 為教學引用，商標屬各公司，與各公司無關聯」。
- 先前研究（Anthropic、Google、DeepSeek 偏向只用文字）的疑慮仍在。**課堂內部使用由使用者判斷；若要公開上傳或散布，請換成各公司品牌套件的官方檔案，或改成文字標籤。**
- 輸出在 `build/classroom/assets/`（已 gitignore），repo 只放腳本與雜湊。

| 項目 | 擁有者 | 狀態 | 公開散布前 |
| --- | --- | --- | --- |
| Claude | Anthropic | 教學引用 | 改官方品牌套件或文字 |
| OpenAI | OpenAI | 教學引用 | 同上 |
| Gemini | Google | 教學引用 | 同上 |
| Kimi | Moonshot AI | 教學引用 | 同上 |
| DeepSeek | DeepSeek | 教學引用 | 同上 |
| Cursor | Anysphere | 教學引用 | 同上 |
| OpenCode | OpenCode（SST／Anomaly） | 教學引用 | 同上 |

## 4. 頁面與轉場（`scripts/build_classroom_ai_agents.py`）

| 章 | 頁 | 內容與手法 |
| --- | --- | --- |
| 封面、章節 | 1–3 | 漣漪擴散＋logo 浮現；環形選單 → 左側章節欄 |
| A Agent | 4–12 | 列高亮；四節點循環（看→想→做→檢查）高亮移動；它能幹嗎／要小心 |
| B 材料 | 13–20 | 四塊拼圖；上下文長條裝滿→壓成摘要；.md 範例；Skill vs .md；Mod；四名詞總表 |
| C 思考 | 21–24 | 滑桿旋鈕（低／高／最高）；各家叫法 |
| D 公司 | 25–27 | 七家 logo 圓環 → 直欄（Morph 擺動）；模型公司 vs 工具公司 |
| E 模型 | 28–37 | 三級分類；Claude、OpenAI、Google（含 11 月新模型）、Kimi＋DeepSeek、Cursor＋OpenCode 陣容；Terminal-Bench 分數長條 → 同批長條依每題成本重排（共享元素）；怎麼看「誰聰明」 |
| F 收費 | 38–46 | 三種付費；token 三種價；三道閘門（每週閘門關上）；月費階梯；價格以外要注意；DeepSeek 一億 token 試算 |
| G 免費 | 47–49 | 各家免費能做什麼；免費≠無限 |
| H 選擇 | 50–53 | 依情境怎麼選；訂閱前三件事 → 自己測三次；三個誤解；結語與日期 |

字級：主文 ≥ 24 pt（驗證器 `--min-font 24`，投影用）；左側章節欄與頁尾 14–20 pt 屬導航，不計。每頁講者備註有講稿與資料日期。

## 5. 重現與驗證

```bash
python3 scripts/classroom_logos.py                      # 需網路與 Node playwright（預裝 Chromium）
python3 scripts/build_classroom_ai_agents.py
python3 scripts/pptx_validate.py build/classroom/classroom-ai-agents.pptx --min-loops 0 --strict --min-font 24 \
  --readable build/classroom/classroom-ai-agents.readable.json
python3 -m unittest discover -s tests
```

| 層 | 狀態 | 證據 |
| --- | --- | --- |
| A | PASS（本地） | 89 項單元測試（含本分支）；驗證器 `--strict --min-font 24`（僅導航小字警告）；檔案無 `advTm`（點擊換頁） |
| B 靜態 | 自查完成（LibreOffice、替代字型） | 53 頁逐頁檢視；已修：封面與圓環名稱換行／重疊、長條圖標籤與數值超出右緣、階梯與誤解頁換行、標題與列重疊 |
| B 轉場代理 | 抽樣 | 圓環→直欄、分數長條→成本長條（只能否決設計；中途疊字屬線性插值假象） |
| C/D | **NOT RUN** | 桌面 PowerPoint 放映、旋轉與縮放補間、投影機與教室後排可讀性 |

## 6. 已知問題與待辦

1. 上課前**逐項重查官方頁**（Google 更新最快；Hydrogen／Carbon 的確切發表日期與價格未取得）（價格、模型選單、Antigravity 11/18 移除、Kimi 新舊會員、地區售價），並更新 `CHECK_DATE`。
2. 資料未向各家官網重新查證，只轉錄使用者已核對的文件。
3. 圓環→直欄的 logo 擺動、長條重排在 PowerPoint 的實際觀感未驗。
4. 左側章節欄 20 pt，後排可能偏小；需要時可放大或收起。
5. 53 頁對 45 分鐘偏滿：標為同主題第二步的頁可跳過。
