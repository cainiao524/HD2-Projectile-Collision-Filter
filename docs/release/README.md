# Projectile Collision Filter｜P-11 自療・四選一投射物自命中（預覽版）

![Projectile Collision Filter（投射物碰撞過濾器）封面](docs/assets/projectile-collision-filter-cover.png)

[English](README.en.md) · [下載 v0.3.0-preview.6](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6) · [安裝與切換](docs/SELECTABLE.md) · [支援範圍](docs/SECONDARIES.md)

讓自己射出的 P-11 治療飛鏢能夠擊中自己，由遊戲原生碰撞與治療邏輯處理效果。你仍然手動瞄準、手動射擊；同一個 Arsenal 模組可選擇只處理治療手槍，或擴展到其他武器投射物。

**P-11 原版已有基本自療的使用者成功回報；擴展範圍仍為候選。** 所有方案包含同一份 P-11 0.2.1。其他武器沿用各自原生效果，傷害型武器可能造成自傷。前三項排除霰彈與多彈丸；第四項包含它們，**可能造成嚴重性能影響**。

## 四選一，預設從 P-11 開始

| Arsenal 選項 | 生效範圍 |
|---|---|
| **僅治療手槍** | 僅 P-11；推薦，首次預選。 |
| **手槍全部** | P-11 加副武器原生投射物候選，包含電漿／榴彈類型的資料識別；排除霰彈與多彈丸。不是全部副武器機制已完成。 |
| **全部武器不包括霰彈槍** | P-11 加支援的本機原生武器投射物；排除霰彈與多彈丸。 |
| **全部武器包括霰彈槍** | 包含霰彈與多彈丸的廣域原生投射物候選；**可能造成嚴重性能影響**。 |

## 下載：一個整合版、四個獨立版、一個工具包

**一般玩家推薦整合版。** 四個獨立版提供固定範圍；與整合版互為替代，**只啟用一個自命中模組包**。工具包另行解壓，不匯入 Arsenal。

| 下載檔 | 選擇方式 |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.6-build25480438.zip` | **推薦**：整合版，在 Arsenal 內四選一 |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | 固定僅治療手槍；保留原始 P-11 成功包 |
| `weapon_self_hit_pistols-0.1.3-build25480438-CANDIDATE.zip` | 固定手槍範圍；0.1.3 副武器候選，排除霰彈 |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | 固定支援的原生武器投射物範圍，排除霰彈 |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | 包含霰彈的廣域候選；**可能造成嚴重性能影響** |
| `P11-Enhanced-Update-Toolkit-1.3.1-win-x64.zip` | Windows x64 離線收集、完整源碼與維護指南 |

六個 ZIP 的 SHA-256 見 [Release 正文](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6)。GitHub 自動的 Source code 連結另供下載源碼，不是可直接安裝的模組。歷史版本保留供回退。

## 本版支援到哪裡

「手槍全部」的目標是全部可射擊副武器，目前收錄 **16 個來源識別候選：13 個原生路徑、3 個 entity 分支**，另保留 P-11。這是參考資料與識別範圍，**不代表 16 把武器都已能對自己生效**。

- **Dagger 光束、Crisper 噴射：目前未支援。**
- **Warrant、P33、Hornet 的 entity 後續碰撞／效果：尚未驗證。** Hornet 是內部資源名稱，正式名稱與可取得狀態未確認。
- 電漿與榴彈仍屬候選；榴彈本體碰撞不等於爆炸或範圍效果已驗證。
- 「全部武器」只指目前支援的原生投射物路徑；不保證所有射線、光束、噴射、近戰、爆炸或 entity 機制。
- 第 2、3 項也保守略過參考表外類型及其他多彈丸機制。仍有槽位掃描，不承諾零開銷或零卡頓。

[完整副武器清單與證據](docs/SECONDARIES.md) · [原理與範圍](docs/VARIANTS.md) · [性能說明](docs/PERFORMANCE.md)

## 環境要求

| 項目 | 本版目標 |
|---|---|
| 遊戲 | Steam build **25480438** |
| 遊戲 EXE | **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |
| 模組管理 | Arsenal；已使用 0.36.2 隔離後端檢查 |
| 收集工具 | Windows x64；可攜 EXE 不需另裝 Python |

## 安裝、切換與升級

1. 關閉遊戲，確認更新完成，另外安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 在 Arsenal 停用舊版與其他重複自命中模組。**五個自命中 ZIP 只啟用一個。**
3. 匯入整合版 ZIP，在「**生效範圍**」選一項；首次預選「僅治療手槍」。確認模組總開關已啟用。
4. 清除舊部署並重新部署，再啟動遊戲。切換、停用或回退也先關閉遊戲，再重新部署。
5. 整合版沿用原 GUID。遇到重複身份提示，使用 Arsenal 的替換功能，或停用／移除舊項目後匯入；不要同時保留兩份啟用。

未知版本會停止修改；不要只替換雜湊強行啟用。

## 推薦搭配與隊友追蹤

**推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**，從原作者頁面另外下載，操作與適用版本以該頁為準。也可嘗試使用者回報的第一人稱朝自己腳部射擊方式；仍需實際飛鏢命中角色。

隊友鎖定／追蹤保持原作者模組獨立管理，功能未改動，也未附帶在本包內。這個自命中包不替你自動瞄準或開火。

[P-11 用法與既有回報](docs/SELF_HIT.md)

## 更新後收集資料，附完整源碼

遊戲或 loader 更新後，完整解壓 **Update Toolkit 1.3.1**，雙擊 `Collect-HD2-Update.cmd`。工具會收集版本、部署資料、既有相關日誌，以及目標安裝中的五份實體／結構／武器／彈頭資料表，記錄來源、雜湊和缺口。查看 `diagnostics` 中的中文摘要與維修交接。

工具不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳。它一次收齊可取得的離線資料，**不承諾每次更新都能自動修復**；收集完整或指紋吻合不等於玩法已驗證。

完整對應源碼已解壓在 `Source/P11-Enhanced/`。開發者與 AI／Agents 從 `AGENTS.md` 開始，依指南完成判讀、修補、測試、重建及發布；重建模組需 Python 3.10+，一般玩家收集資料不需要。

| 我要做的事 | 入口 |
|---|---|
| 安裝、切換、停用、回退 | [玩家操作指南](docs/SELECTABLE.md) |
| 遊戲更新後一次收集 | [離線更新工具](docs/UPDATE_TOOL.md) |
| 交給開發者或 AI／Agent | [AGENTS.md](AGENTS.md) → [逐步接手指南](docs/AGENT_GUIDE.md) |
| 修補與重建 | [建置與移植](docs/PORTING.md) · [工作交接模板](docs/HANDOFF_TEMPLATE.md) |
| 驗證與發布 | [驗證記錄](docs/VERIFICATION.md) · [發布指南](docs/PUBLISH.md) |
| 複製自命中模組網站介紹 | [中文發布文案](docs/MOD-PAGE.zh-TW.md) · [English release copy](docs/MOD-PAGE.en.md) |
| 複製動作模組網站介紹 | [舉槍瞄準自己](docs/RAISE-WEAPON.zh-TW.md) · [English animation copy](docs/RAISE-WEAPON.en.md) |
| 網站標題、摘要、封面與貼上操作 | [兩個模組頁面發布資料](docs/PAGE-PUBLISHING.md) |

詳細維護文件及診斷摘要目前以中文為主；本首頁、Release 介紹與模組網站文案提供完整中英對照。

## preview.6 更新內容

- **副武器候選 0.1.3**：以固定資料中的副武器裝備槽位補齊參考清單，替換舊八項識別範圍；16 個來源候選分成原生與 entity 機制，逐項標示限制。
- **保留成功 P-11**：原 0.2.1 ZIP／Lua 不變；兩個廣域 0.1.2 包也保留。原生資料修改與身份、所有權及寫入檢查未為擴大清單而放寬。
- **Toolkit 1.3.1**：直接收集五份安裝資料表，區分安裝來源與快取，補齊缺檔與版本對應缺口。
- **交付與文件**：一個四選一整合版、四個獨立版、一個含完整源碼的工具包，附雙語介紹、操作導航及 AI／Agent 接手指南。

## 驗證與實現方式

本候選通過 **120 項 Python 檢查、429 項 P-11 Lua 模擬斷言、3,322 項擴展 Lua 模擬斷言**，並完成固定參考資料重驗與 Arsenal 隔離後端檢查。這些是離線、封裝和合成資料測試，**不是新增的遊戲自命中實測或 FPS 測量**。P-11 的基本成功來自既有使用者回報；新增副武器、主客機、碰撞時機、完整共存與效能仍不能視為已全面驗證。

實作只改變經身份與所有權檢查的本機投射物來源碰撞排除，命中後由遊戲處理原生效果。沒有 native hook、執行碼修補或直接寫入生命／體力／彈藥／傷害數值。

GitHub 專案仍名為 **P11-Enhanced**。本模組與 Arrowhead Game Studios 無隸屬關係，程式與文件使用 OpenAI 工具協助製作。整體授權尚未選定；[來源與依賴](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)。