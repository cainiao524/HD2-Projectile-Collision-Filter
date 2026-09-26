# 模組網站發布文案（繁體中文）

## 標題

Projectile Collision Filter｜P-11 自療・四選一投射物自命中（預覽版）

## 簡介

讓 P-11 飛鏢能擊中自己並觸發原生治療。一個 Arsenal 模組四選一，前三項排除霰彈；包含霰彈的第四項可能造成嚴重性能影響。附離線更新工具、完整源碼與接手指南；副武器擴展仍為候選，未支援全部機制。

## 正文

![Projectile Collision Filter（投射物碰撞過濾器）封面](https://raw.githubusercontent.com/cainiao524/P11-Enhanced/v0.3.0-preview.6/docs/assets/projectile-collision-filter-cover.png)

### 讓治療飛鏢也能幫到自己

讓自己射出的 P-11 治療飛鏢能夠擊中自己，由遊戲原生碰撞與治療邏輯處理效果。你仍然手動瞄準、手動射擊；同一個 Arsenal 模組可選擇只處理治療手槍，或擴展到其他武器投射物。

**P-11 原版已有基本自療的使用者成功回報；擴展範圍仍為候選。** 所有方案包含同一份 P-11 0.2.1。其他武器沿用各自原生效果，傷害型武器可能造成自傷。前三項排除霰彈與多彈丸；第四項包含它們，**可能造成嚴重性能影響**。

**版本：v0.3.0-preview.6，預覽版。** [GitHub 六檔下載](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6) · [完整原始碼](https://github.com/cainiao524/P11-Enhanced/tree/v0.3.0-preview.6) · [English mod-page copy](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/MOD-PAGE.en.md)

### 一個模組，四種生效範圍

| Arsenal 選項 | 生效範圍 |
|---|---|
| **僅治療手槍** | 僅 P-11；推薦，首次預選。 |
| **手槍全部** | P-11 加副武器原生投射物候選，包含電漿／榴彈類型的資料識別；排除霰彈與多彈丸。不是全部副武器機制已完成。 |
| **全部武器不包括霰彈槍** | P-11 加支援的本機原生武器投射物；排除霰彈與多彈丸。 |
| **全部武器包括霰彈槍** | 包含霰彈與多彈丸的廣域原生投射物候選；**可能造成嚴重性能影響**。 |

整體開關由 Arsenal 管理，首次預選 P-11。切換前關閉遊戲，選好後重新部署。若主要需要自療，直接使用「僅治療手槍」。

### 副武器與廣域範圍的實際狀態

「手槍全部」的目標是全部可射擊副武器，目前收錄 **16 個來源識別候選：13 個原生路徑、3 個 entity 分支**，另保留 P-11。這是參考資料與識別範圍，**不代表 16 把武器都已能對自己生效**。

- **Dagger 光束、Crisper 噴射：目前未支援。**
- **Warrant、P33、Hornet 的 entity 後續碰撞／效果：尚未驗證。** Hornet 是內部資源名稱，正式名稱與可取得狀態未確認。
- 電漿與榴彈仍屬候選；榴彈本體碰撞不等於爆炸或範圍效果已驗證。
- 「全部武器」只指目前支援的原生投射物路徑；不保證所有射線、光束、噴射、近戰、爆炸或 entity 機制。
- 第 2、3 項也保守略過參考表外類型及其他多彈丸機制。仍有槽位掃描，不承諾零開銷或零卡頓。

完整清單與每種機制的證據見 [副武器支援表](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SECONDARIES.md)，範圍與原理見 [VARIANTS](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/VARIANTS.md)。

### 下載哪一個檔案

**推薦整合版。** 四個獨立版是固定方案，與整合版互為替代；只啟用一個自命中模組。工具包用於更新後收集與開發，不能匯入 Arsenal。

| 下載檔 | 選擇方式 |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.6-build25480438.zip` | **推薦**：整合版，在 Arsenal 內四選一 |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | 固定僅治療手槍；保留原始 P-11 成功包 |
| `weapon_self_hit_pistols-0.1.3-build25480438-CANDIDATE.zip` | 固定手槍範圍；0.1.3 副武器候選，排除霰彈 |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | 固定支援的原生武器投射物範圍，排除霰彈 |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | 包含霰彈的廣域候選；**可能造成嚴重性能影響** |
| `P11-Enhanced-Update-Toolkit-1.3.1-win-x64.zip` | Windows x64 離線收集、完整源碼與維護指南 |

六項 SHA-256 列在 [Release 正文](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6)。工具包的源碼已放在 `Source/P11-Enhanced/`，不需再解壓來源 ZIP。歷史 Release 保留供回退。

### 環境要求與安裝

| 項目 | 本版目標 |
|---|---|
| 遊戲 | Steam build **25480438** |
| 遊戲 EXE | **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |
| 模組管理 | Arsenal；已使用 0.36.2 隔離後端檢查 |
| 收集工具 | Windows x64；可攜 EXE 不需另裝 Python |

1. 關閉遊戲，確認更新完成，另外安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 在 Arsenal 停用舊版與其他重複自命中模組。**五個自命中 ZIP 只啟用一個。**
3. 匯入整合版 ZIP，在「**生效範圍**」選一項；首次預選「僅治療手槍」。確認模組總開關已啟用。
4. 清除舊部署並重新部署，再啟動遊戲。切換、停用或回退也先關閉遊戲，再重新部署。
5. 整合版沿用原 GUID。遇到重複身份提示，使用 Arsenal 的替換功能，或停用／移除舊項目後匯入；不要同時保留兩份啟用。

未知版本會停止修改；不要只替換雜湊強行啟用。

[完整安裝、停用與回退指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SELECTABLE.md)

### 推薦搭配

**推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**，從原作者頁面另外下載，操作與適用版本以該頁為準。也可嘗試使用者回報的第一人稱朝自己腳部射擊方式；仍需實際飛鏢命中角色。

隊友鎖定／追蹤保持原作者模組獨立管理，功能未改動，也未附帶在本包內。這個自命中包不替你自動瞄準或開火。

[P-11 用法與使用者回報](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SELF_HIT.md)

### 遊戲更新後怎麼繼續

遊戲或 loader 更新後，完整解壓 **Update Toolkit 1.3.1**，雙擊 `Collect-HD2-Update.cmd`。工具會收集版本、部署資料、既有相關日誌，以及目標安裝中的五份實體／結構／武器／彈頭資料表，記錄來源、雜湊和缺口。查看 `diagnostics` 中的中文摘要與維修交接。

工具不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳。它一次收齊可取得的離線資料，**不承諾每次更新都能自動修復**；收集完整或指紋吻合不等於玩法已驗證。

完整對應源碼已解壓在 `Source/P11-Enhanced/`。開發者與 AI／Agents 從 `AGENTS.md` 開始，依指南完成判讀、修補、測試、重建及發布；重建模組需 Python 3.10+，一般玩家收集資料不需要。

[收集工具操作](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/UPDATE_TOOL.md) · [AI／Agent 入口](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/AGENTS.md) · [逐步維護指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/AGENT_GUIDE.md) · [建置與修補](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PORTING.md) · [發布流程](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PUBLISH.md)

詳細維護文件與診斷摘要以中文為主；本模組介紹、GitHub 首頁與 Release 提供完整中英版本。

### 這一版更新了什麼

- **副武器候選 0.1.3**：以固定資料中的副武器裝備槽位補齊參考清單，替換舊八項識別範圍；16 個來源候選分成原生與 entity 機制，逐項標示限制。
- **保留成功 P-11**：原 0.2.1 ZIP／Lua 不變；兩個廣域 0.1.2 包也保留。原生資料修改與身份、所有權及寫入檢查未為擴大清單而放寬。
- **Toolkit 1.3.1**：直接收集五份安裝資料表，區分安裝來源與快取，補齊缺檔與版本對應缺口。
- **交付與文件**：一個四選一整合版、四個獨立版、一個含完整源碼的工具包，附雙語介紹、操作導航及 AI／Agent 接手指南。

### 驗證情況

本候選通過 **120 項 Python 檢查、429 項 P-11 Lua 模擬斷言、3,322 項擴展 Lua 模擬斷言**，並完成固定參考資料重驗與 Arsenal 隔離後端檢查。這些是離線、封裝和合成資料測試，**不是新增的遊戲自命中實測或 FPS 測量**。P-11 的基本成功來自既有使用者回報；新增副武器、主客機、碰撞時機、完整共存與效能仍不能視為已全面驗證。

實作只改變經身份與所有權檢查的本機投射物來源碰撞排除，命中後由遊戲處理原生效果。沒有 native hook、執行碼修補或直接寫入生命／體力／彈藥／傷害數值。

[詳細驗證記錄](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/VERIFICATION.md) · [效能與證據界限](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PERFORMANCE.md)

GitHub 專案名稱為 **P11-Enhanced**。本模組與 Arrowhead Game Studios 無隸屬關係，程式與文件使用 OpenAI 工具協助製作。整體授權尚未選定；請查看 [來源聲明](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/THIRD_PARTY.md) 與 [授權聲明](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/LICENSE-NOTICE.md)。
