# Projectile Collision Filter v0.3.0-preview.8 — Four Scopes, One Mod / 四種範圍，一個模組

![Projectile Collision Filter / 投射物碰撞過濾器](https://raw.githubusercontent.com/cainiao524/HD2-Projectile-Collision-Filter/v0.3.0-preview.8/docs/assets/projectile-collision-filter-cover.png)

**Prerelease / 預覽版** · Steam build **25480438** · EXE **1.8.46015.0** · Bingus Shared Loader **v17 / API 1 / internal 16**

## English

Let your own P-11 darts hit and heal you through native collision. Choose one of four scopes in a single Arsenal mod. **The user reports normal basic operation with all four choices.** This packaging release preserves the tested preview.8 Lua payloads and game resources byte for byte; it updates bilingual configuration, maintenance tools, source, page copy and cover artwork.

The repository is now **HD2-Projectile-Collision-Filter**. Historical releases and their assets remain available.

### Two downloads

| Asset | Use |
|---|---|
| [Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip) | **For players:** import into Arsenal and choose one scope. |
| [HD2-Projectile-Collision-Filter-Update-Toolkit-1.3.2-win-x64.zip](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/HD2-Projectile-Collision-Filter-Update-Toolkit-1.3.2-win-x64.zip) | Windows x64 offline collection, full matching source, build and Agent maintenance guides. Extract separately; do not import into Arsenal. |

There are no separate standalone mod ZIPs in this release. GitHub's automatic Source code links remain available; they are not installable mods. Asset SHA-256 values are appended below by the publishing verifier.

### Four bilingual choices

- **P-11 Only / 僅治療手槍** — healing darts only; recommended and initially selected.
- **All Sidearms / 手槍全部** — P-11 and supported sidearm projectiles, excluding shotgun/multi-projectile types.
- **All Weapons (No Shotguns) / 全部武器不包括霰彈槍** — supported native weapon projectiles, excluding shotgun/multi-projectile types.
- **All Weapons (Including Shotguns) / 全部武器包括霰彈槍** — **WARNING: May cause severe performance impact.**

The selector is **Effect Scope / 生效範圍**, with English-first bilingual names and descriptions. Close the game, disable and purge old self-hit versions, replace/import this ZIP, select one scope, enable and redeploy. Always close and redeploy when switching or rolling back. Enable only one self-hit mod.

### What changed

- One cursor-based core and a single deployed addon per choice replace the old repeated full-slot traversal and separate P-11/expanded processing. Recent candidates use bounded rechecks; all identity, ownership and guarded-write protections remain.
- Toolkit **1.3.2** distinguishes the four integrated scopes using exact deployed Lua fingerprints. Game, deployed mod, loader fingerprint/API and conflict state all contribute to compatibility assessment; matching a game hash alone is insufficient.
- Full source is already unpacked at **Source/HD2-Projectile-Collision-Filter/**. Updated runbooks cover collection, evidence gaps, 15 anchors, porting, tests, rebuilds, two-asset publishing and remote verification.
- Bilingual page copy and two new covers are included in source. The animation mod and original teammate homing remain separate, unchanged downloads.

### Evidence and limits

The four-choice user report is basic confirmation, not a complete weapon-by-weapon, multiplayer or performance matrix. The approximately **70 → 130 FPS** report belongs to the earlier **P-11 0.2.3** test, not a fixed gain for all preview.8 choices. Queue limits and collision timing can skip projectiles; zero overhead and success on every shot are not guaranteed.

“All Sidearms” uses the pinned secondary-slot catalog beyond the historical eight IDs, but Dagger beam and Crisper spray remain unsupported. Warrant/P33/internal Hornet entity follow-up paths and later explosion/area effects remain unresolved. “All Weapons” means supported native projectiles. Damaging weapons can hurt you; the inclusive shotgun choice may cause severe performance impact.

No native hook, executable patch, global-definition change or direct health/stamina/ammo/damage-value write is used. Unknown game/loader identities stop modification. Diagnostics do not launch the game, read processes, deploy or upload, and do not automatically repair every update.

[Install and switch](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/blob/v0.3.0-preview.8/docs/SELECTABLE.md) · [Coverage](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/blob/v0.3.0-preview.8/docs/SECONDARIES.md) · [Maintenance](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/blob/v0.3.0-preview.8/AGENTS.md) · [Both mod-page publishing kits](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/blob/v0.3.0-preview.8/docs/PAGE-PUBLISHING.md)

Recommended separate companion: [Raise Weapon: Aim at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/). Actual fired darts must hit you; aiming and firing remain manual.

## 繁體中文

讓自己射出的 P-11 飛鏢真正命中角色，再由原生碰撞和治療產生效果。在同一個 Arsenal 模組內四選一。**使用者已回報四個選項基本使用正常**；本次整理保持已測 preview.8 的四份 Lua 和遊戲資源不變，更新雙語配置、維護工具、源碼、介紹與封面。

倉庫改名為 **HD2-Projectile-Collision-Filter**，歷史 Release 標籤與全部資產保留。

### 本版只有兩個 ZIP

- **整合模組 ZIP**：玩家下載，匯入 Arsenal，在 **Effect Scope / 生效範圍** 選一項。配置頁英文在前、中文在後；首次預選 P-11。
- **Update Toolkit 1.3.2 ZIP**：遊戲更新後一次收集可取得的離線資料；完整源碼已在 **Source/HD2-Projectile-Collision-Filter/**。工具包另行解壓，不匯入 Arsenal。

不再額外發布四個獨立包。四項依序是 **P-11 Only / 僅治療手槍**、**All Sidearms / 手槍全部**、**All Weapons (No Shotguns) / 全部武器不包括霰彈槍**、**All Weapons (Including Shotguns) / 全部武器包括霰彈槍**。前三項排除霰彈／多彈丸，第四項 **警告：可能造成嚴重性能影響。**

安裝前完整關閉遊戲，停用舊自命中版本並清除部署，再替換／匯入整合包、選範圍、確認總開關及重新部署。切換、停用或回退也先關閉遊戲。**一次只啟用一個自命中包。**

### 核心與工具

四範圍共用游標核心、每次只載入一個 addon，檢查近期候選和有限重查，取代舊版反覆全槽遍歷。身份、所有權、原值、非執行資料頁、寫前重檢和讀回保護全部保留。只修改投射物來源碰撞排除位，沒有 native hook 或直接改生命／體力／彈藥／傷害數值。

Toolkit 1.3.2 用四份精確 Lua 指紋識別實際範圍，遊戲、部署、loader 來源／API 和衝突一起判定，避免只匹配遊戲 hash 就沿用舊成功基準。收集器不啟動遊戲、不讀取執行中程序、不部署、不上傳；不承諾每次更新自動修復。完整指引涵蓋資料缺口、15 錨點、移植、測試、建置和兩檔發布核驗。

### 驗證與限制

四項正常回報不等於逐武器、完整聯機或性能矩陣。約 **70 → 130 FPS** 只屬先前 **P-11 0.2.3** 測試，不是本版四項固定提升。有限待辦和碰撞時機仍可能漏處理；不保證零開銷或每一發生效。

手槍識別已擴展出歷史八個 ID，但 Dagger 光束、Crisper 噴射仍未支援，Warrant／P33／內部 Hornet 的 entity 後續鏈、爆炸和範圍效果未全面驗證。「全部武器」指支援的原生投射物；傷害型武器可能自傷，第四項可能造成嚴重性能影響。

推薦另裝 [Raise Weapon: Aim at Yourself / 舉槍瞄準自己](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)。隊友追蹤與動作模組保持原樣，獨立管理。兩頁雙語介紹、BBCode 和新封面已放在源碼；封面為宣傳插畫，不是玩法截圖。
