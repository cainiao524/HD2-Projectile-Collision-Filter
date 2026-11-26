# Projectile Collision Filter｜P-11 自療・四選一投射物自命中（預覽版）

![Projectile Collision Filter cover](https://raw.githubusercontent.com/cainiao524/P11-Enhanced/v0.3.0-preview.6/docs/assets/projectile-collision-filter-cover.png)

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

**v0.3.0-preview.6 · 預覽版**

讓自己射出的 P-11 治療飛鏢能夠擊中自己，由遊戲原生碰撞與治療邏輯處理效果。你仍然手動瞄準、手動射擊；同一個 Arsenal 模組可選擇只處理治療手槍，或擴展到其他武器投射物。

**P-11 原版已有基本自療的使用者成功回報；擴展範圍仍為候選。** 所有方案包含同一份 P-11 0.2.1。其他武器沿用各自原生效果，傷害型武器可能造成自傷。前三項排除霰彈與多彈丸；第四項包含它們，**可能造成嚴重性能影響**。

### 選擇生效範圍

| Arsenal 選項 | 生效範圍 |
|---|---|
| **僅治療手槍** | 僅 P-11；推薦，首次預選。 |
| **手槍全部** | P-11 加副武器原生投射物候選，包含電漿／榴彈類型的資料識別；排除霰彈與多彈丸。不是全部副武器機制已完成。 |
| **全部武器不包括霰彈槍** | P-11 加支援的本機原生武器投射物；排除霰彈與多彈丸。 |
| **全部武器包括霰彈槍** | 包含霰彈與多彈丸的廣域原生投射物候選；**可能造成嚴重性能影響**。 |

「手槍全部」的目標是全部可射擊副武器，目前收錄 **16 個來源識別候選：13 個原生路徑、3 個 entity 分支**，另保留 P-11。這是參考資料與識別範圍，**不代表 16 把武器都已能對自己生效**。

- **Dagger 光束、Crisper 噴射：目前未支援。**
- **Warrant、P33、Hornet 的 entity 後續碰撞／效果：尚未驗證。** Hornet 是內部資源名稱，正式名稱與可取得狀態未確認。
- 電漿與榴彈仍屬候選；榴彈本體碰撞不等於爆炸或範圍效果已驗證。
- 「全部武器」只指目前支援的原生投射物路徑；不保證所有射線、光束、噴射、近戰、爆炸或 entity 機制。
- 第 2、3 項也保守略過參考表外類型及其他多彈丸機制。仍有槽位掃描，不承諾零開銷或零卡頓。

[完整副武器清單與機制狀態](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SECONDARIES.md) · [原理與性能](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PERFORMANCE.md)

### 六個下載檔

整合版適合一般玩家，四個獨立版提供固定範圍。**五個模組 ZIP 只啟用一個；工具包另行解壓，不匯入 Arsenal。**

| 下載檔 | 選擇方式 |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.6-build25480438.zip` | **推薦**：整合版，在 Arsenal 內四選一 |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | 固定僅治療手槍；保留原始 P-11 成功包 |
| `weapon_self_hit_pistols-0.1.3-build25480438-CANDIDATE.zip` | 固定手槍範圍；0.1.3 副武器候選，排除霰彈 |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | 固定支援的原生武器投射物範圍，排除霰彈 |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | 包含霰彈的廣域候選；**可能造成嚴重性能影響** |
| `P11-Enhanced-Update-Toolkit-1.3.1-win-x64.zip` | Windows x64 離線收集、完整源碼與維護指南 |

本頁末尾列出六項 SHA-256。GitHub 自動產生的 Source code 連結是額外源碼下載，不是可直接安裝的模組；歷史版本保留供回退。

### 要求與安裝

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

**推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**，從原作者頁面另外下載，操作與適用版本以該頁為準。也可嘗試使用者回報的第一人稱朝自己腳部射擊方式；仍需實際飛鏢命中角色。

隊友鎖定／追蹤保持原作者模組獨立管理，功能未改動，也未附帶在本包內。這個自命中包不替你自動瞄準或開火。

[安裝、切換與回退指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SELECTABLE.md) · [P-11 使用方式](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SELF_HIT.md)

### preview.6 更新內容

- **副武器候選 0.1.3**：以固定資料中的副武器裝備槽位補齊參考清單，替換舊八項識別範圍；16 個來源候選分成原生與 entity 機制，逐項標示限制。
- **保留成功 P-11**：原 0.2.1 ZIP／Lua 不變；兩個廣域 0.1.2 包也保留。原生資料修改與身份、所有權及寫入檢查未為擴大清單而放寬。
- **Toolkit 1.3.1**：直接收集五份安裝資料表，區分安裝來源與快取，補齊缺檔與版本對應缺口。
- **交付與文件**：一個四選一整合版、四個獨立版、一個含完整源碼的工具包，附雙語介紹、操作導航及 AI／Agent 接手指南。

### 更新後的收集與接手

遊戲或 loader 更新後，完整解壓 **Update Toolkit 1.3.1**，雙擊 `Collect-HD2-Update.cmd`。工具會收集版本、部署資料、既有相關日誌，以及目標安裝中的五份實體／結構／武器／彈頭資料表，記錄來源、雜湊和缺口。查看 `diagnostics` 中的中文摘要與維修交接。

工具不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳。它一次收齊可取得的離線資料，**不承諾每次更新都能自動修復**；收集完整或指紋吻合不等於玩法已驗證。

完整對應源碼已解壓在 `Source/P11-Enhanced/`。開發者與 AI／Agents 從 `AGENTS.md` 開始，依指南完成判讀、修補、測試、重建及發布；重建模組需 Python 3.10+，一般玩家收集資料不需要。

[離線工具指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/UPDATE_TOOL.md) · [AI／Agent 入口](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/AGENTS.md) · [逐步接手](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/AGENT_GUIDE.md) · [建置與移植](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PORTING.md) · [發布流程](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PUBLISH.md)

詳細維護指南與診斷摘要以中文為主；本 Release、專案首頁及模組網站文案提供完整中英版本。

### 驗證與限制

本候選通過 **120 項 Python 檢查、429 項 P-11 Lua 模擬斷言、3,322 項擴展 Lua 模擬斷言**，並完成固定參考資料重驗與 Arsenal 隔離後端檢查。這些是離線、封裝和合成資料測試，**不是新增的遊戲自命中實測或 FPS 測量**。P-11 的基本成功來自既有使用者回報；新增副武器、主客機、碰撞時機、完整共存與效能仍不能視為已全面驗證。

實作只改變經身份與所有權檢查的本機投射物來源碰撞排除，命中後由遊戲處理原生效果。沒有 native hook、執行碼修補或直接寫入生命／體力／彈藥／傷害數值。

[驗證記錄](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/VERIFICATION.md) · [中文模組頁文案](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/MOD-PAGE.zh-TW.md)

---

## English

### Projectile Collision Filter — P-11 Self-Heal & Selectable Self-Hit (Preview)

**v0.3.0-preview.6 · Prerelease**

Let your own P-11 healing darts hit you, with the game's native collision and healing logic handling the effect. You still aim and fire manually. One Arsenal mod lets you stay with the healing pistol or choose a broader weapon-projectile scope.

**Original P-11 basic self-healing has a successful user report; expanded scopes remain candidates.** Every choice includes the same P-11 0.2.1 addon. Other weapons retain their native effects, so damaging weapons may cause self-damage. The first three choices exclude shotguns and multishot types; the fourth includes them and **may cause severe performance impact**.

### Choose a scope

| Exact Arsenal label | Scope |
|---|---|
| **僅治療手槍 — P-11 only** | P-11 only; recommended and initially selected. |
| **手槍全部 — All pistols** | P-11 plus native-projectile secondary candidates, with plasma/grenade types represented in the data; excludes shotguns and multishot. Not every secondary mechanism is implemented. |
| **全部武器不包括霰彈槍 — All weapons, excluding shotguns** | P-11 plus supported local native weapon projectiles; excludes shotguns and multishot. |
| **全部武器包括霰彈槍 — All weapons, including shotguns** | Broad native-projectile candidate including shotguns and multishot; **may cause severe performance impact**. |

“All pistols” targets all shootable secondaries. The current catalog supplies **16 source-identity candidates: 13 native-path entries and 3 entity branches**, with P-11 retained separately. This describes reference data and recognition scope; **it does not mean all 16 weapons can already hit their owner**.

- **Dagger beam and Crisper spray are currently unsupported.**
- **Warrant, P33 and Hornet entity follow-up collisions/effects are unverified.** Hornet is an internal resource name; its final name and availability are unconfirmed.
- Plasma and grenade types remain candidates; grenade-body collision does not establish explosion or area-effect support.
- “All weapons” means the currently supported native projectile path, not guaranteed coverage of every hitscan, beam, spray, melee, explosion or entity mechanism.
- Choices 2 and 3 also conservatively skip out-of-table types and other multishot mechanisms. Slot scanning remains; zero overhead or zero stutter is not promised.

[Complete secondary catalog and mechanism status](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SECONDARIES.md) · [Implementation and performance](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PERFORMANCE.md)

### Six downloads

The selector is recommended for most players; four standalone mods provide fixed scopes. **Enable only one of the five mod ZIPs. Extract the toolkit separately; do not import it into Arsenal.**

| Download | Use |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.6-build25480438.zip` | **Recommended:** one Arsenal mod with four exclusive choices |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | Fixed P-11-only scope; unchanged original healing package |
| `weapon_self_hit_pistols-0.1.3-build25480438-CANDIDATE.zip` | Fixed pistol scope; 0.1.3 secondary candidate, excluding shotguns |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | Fixed supported native-weapon scope, excluding shotguns |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | Broad candidate including shotguns; **may cause severe performance impact** |
| `P11-Enhanced-Update-Toolkit-1.3.1-win-x64.zip` | Windows x64 offline collector, complete source and maintenance guides |

All six SHA-256 values appear at the end of this page. GitHub's automatic Source code links are additional source downloads, not directly installable mods. Historical versions remain available for rollback.

### Requirements and installation

| Item | Release target |
|---|---|
| Game | Steam build **25480438** |
| Game EXE | **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |
| Mod manager | Arsenal; isolated backend checks used 0.36.2 |
| Collector | Windows x64; the portable EXE needs no separate Python installation |

1. Close the game, let updates finish, and install a compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately.
2. Disable older versions and duplicate self-hit mods in Arsenal. **Enable only one of the five self-hit ZIPs.**
3. Import the selectable ZIP and choose one option under **生效範圍**. P-11 only is initially selected; confirm the mod's overall switch is enabled.
4. Clear the old deployment and redeploy before launching the game. Close and redeploy when switching, disabling or rolling back too.
5. The selectable mod keeps its original GUID. If Arsenal reports a duplicate identity, replace the old package or disable/remove its old entry before importing; do not leave both enabled.

Unknown versions stop writes. Do not bypass that check by replacing hashes.

**Recommended P-11 companion: [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**. Download it separately from its author's page and follow that page for controls and supported versions. A user also reported firing toward their own feet in first-person view; an actual dart hit on the character is still required.

Teammate locking/homing remains independently managed by the original mod, unchanged and not bundled here. This self-hit package does not aim or fire for you.

[Install, switch and roll back](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SELECTABLE.md) · [P-11 usage](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/SELF_HIT.md)

### Changes in preview.6

- **Secondary candidate 0.1.3:** a pinned loadout-slot catalog replaces the old eight-entry recognition scope. Sixteen source candidates are split into native and entity mechanisms with explicit limits.
- **Original P-11 preserved:** the 0.2.1 ZIP/Lua and both broad 0.1.2 packages stay unchanged. Expanding the catalog does not weaken identity, ownership or write checks.
- **Toolkit 1.3.1:** directly collects five installed data files, distinguishes installed evidence from caches, and reports missing files and unresolved build correspondence.
- **Delivery and documentation:** one selectable mod, four standalone alternatives and one toolkit containing complete source, with bilingual introductions, operating navigation and an AI-agent handoff guide.

### Diagnostics and developer handoff

After a game or loader update, fully extract **Update Toolkit 1.3.1** and run `Collect-HD2-Update.cmd`. It collects versions, deployed resources, relevant existing log events and five installed entity/structure/weapon/projectile data files, recording provenance, hashes and gaps. Read the Chinese summary and repair handoff under `diagnostics`.

The tool does not launch the game, read running processes, modify or deploy mods, or upload data. It gathers available offline evidence in one run; **automatic repair after every update is not guaranteed**. Complete collection or matching fingerprints do not establish gameplay success.

Complete matching source is already extracted under `Source/P11-Enhanced/`. Developers and AI agents start with `AGENTS.md` and follow the triage, porting, testing, rebuild and publishing guides. Mod rebuilding needs Python 3.10+; ordinary evidence collection does not.

[Offline tool guide](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/UPDATE_TOOL.md) · [AI-agent entry point](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/AGENTS.md) · [Step-by-step handoff](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/AGENT_GUIDE.md) · [Build and porting](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PORTING.md) · [Publishing workflow](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/PUBLISH.md)

Detailed maintenance guides and diagnostic summaries are primarily in Chinese. This release, the project homepage and mod-site copy have complete Chinese and English versions.

### Verification and limitations

This candidate passed **120 Python checks, 429 P-11 Lua mock assertions and 3,322 expanded Lua mock assertions**, plus pinned-reference replay and isolated Arsenal backend checks. These are offline, packaging and synthetic-data checks, **not new in-game self-hit tests or FPS measurements**. Basic P-11 success comes from an earlier user report; new secondary behavior, host/client cases, collision timing, full coexistence and performance are not comprehensively verified.

The implementation changes source-collision exclusion only for checked, locally owned projectiles; the game handles the native effect after a hit. It uses no native hook, executable-code patch or direct health, stamina, ammo or damage-value writes.

[Verification record](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/VERIFICATION.md) · [English mod-page copy](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/MOD-PAGE.en.md)

---

GitHub 專案／project: **P11-Enhanced**. 獨立社群模組，與 Arrowhead Game Studios 無隸屬關係／An independent community mod, unaffiliated with Arrowhead Game Studios. 程式與文件使用 OpenAI 工具協助製作／Code and documentation made with assistance from OpenAI tools. 整體授權尚未選定／No overall project license selected. [來源與依賴 / Sources](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/docs/THIRD_PARTY.md) · [授權聲明 / License notice](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.6/LICENSE-NOTICE.md).