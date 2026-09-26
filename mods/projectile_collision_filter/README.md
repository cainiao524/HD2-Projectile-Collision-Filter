# Projectile Collision Filter / 投射物碰撞過濾器

v0.3.0-preview.8 — Steam build **25480438** / EXE **1.8.46015.0** / Bingus Shared Loader **v17 / API 1 / internal 16**.

## 安裝與配置 / Install and configure

Close the game, disable other self-hit packages (including old P-11, 0.2.3 and old selector versions), purge the deployment, import this ZIP and replace the old GUID entry if prompted. Select one scope, enable the overall mod and redeploy. Close and redeploy when switching, disabling or rolling back; keep only one self-hit package enabled.

完整關閉遊戲，停用其他自命中包（含舊 P-11、0.2.3 與舊整合版），清除部署，再匯入本 ZIP；GUID 相同時替換舊項目。選一範圍、啟用總開關並重新部署。切換、停用或回退都先關閉遊戲，一次只啟用一個自命中包。

**Effect Scope / 生效範圍**

- **P-11 Only / 僅治療手槍** — P-11 healing darts; recommended and initially selected. / 僅治療飛鏢，推薦且首次預選。
- **All Sidearms / 手槍全部** — Supported sidearm projectiles; excludes shotguns/multishot. / 支援的副武器投射物，排除霰彈／多彈丸。
- **All Weapons (No Shotguns) / 全部武器不包括霰彈槍** — Supported native projectiles; excludes shotguns/multishot. / 支援的原生投射物，排除霰彈／多彈丸。
- **All Weapons (Including Shotguns) / 全部武器包括霰彈槍** — **WARNING: May cause severe performance impact. / 警告：可能造成嚴重性能影響。**

All four choices include P-11 and use one shared cursor-based addon. Do not manually deploy all four archives. Every checked projectile keeps native effects: P-11 heals after an actual self-hit; damaging weapons may hurt you. Aiming and firing remain manual.

四項均含 P-11，使用同一游標核心和單一 addon，不要手動部署四份 archive。真正的飛鏢命中後由原生邏輯處理治療；傷害型武器可能自傷，仍需手動瞄準和射擊。

## Evidence and limits / 證據與限制

The user reports normal basic operation with all four preview.8 choices. Packaging preserves those four Lua/game-resource payloads. This is not complete per-weapon, host/client or performance verification. The earlier approximately 70-to-130 FPS result belongs to P-11 0.2.3, not a guaranteed gain for this release.

使用者已回報 preview.8 四項基本使用正常，本次包裝保持四份 Lua／遊戲資源不變。此回報不代表逐武器、完整主客機或性能驗證。先前約 70 → 130 FPS 屬 P-11 0.2.3，不是本版固定增幅。

The addon follows the allocation cursor and performs bounded retries. Ownership, identity, original-value, guarded-write and readback checks remain; only source-collision exclusion bit 0x20 is cleared. No native hook, executable patch, global-definition change or direct health/stamina/ammo/damage write is used. Queue limits and collision timing can skip shots. Unknown versions stop modification.

跟隨分配游標和有限重查，保留所有權、身份、原值、寫前重檢與讀回，只清除来源碰撞排除位 0x20。沒有 native hook、執行碼修改、全域定義改寫或直接生命／體力／彈藥／傷害值寫入。待辦上限和碰撞時機可能造成略過，未知版本停止修改。

Dagger beam and Crisper spray remain unsupported; Warrant/P33/internal Hornet entity follow-up and explosion/area effects remain unverified. “All Weapons” means currently supported native projectile paths, not every damage mechanism.

Dagger 光束與 Crisper 噴射未支援；Warrant／P33／內部 Hornet 後續 entity 和爆炸／範圍效果未全面驗證。「全部武器」指目前支援的原生投射物路徑。

Recommended separate companion / 推薦另裝：[Raise Weapon: Aim at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/). Animation and original teammate homing remain separately managed, not included. / 動作及原作者隊友追蹤獨立管理，未附帶。

Toolkit 1.3.2 is a separate release ZIP with complete source under Source/HD2-Projectile-Collision-Filter. It collects offline evidence without game launch, process reading, deployment or uploading; it does not guarantee automatic repair.

Toolkit 1.3.2 為另一個 Release ZIP，完整源碼在 Source/HD2-Projectile-Collision-Filter。只收集離線證據，不啟動遊戲、不讀程序、不部署、不上傳，也不保證自動修復。

[Release / 下載](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8) · [Guides / 操作指南](https://github.com/cainiao524/HD2-Projectile-Collision-Filter) · [Validation / 驗證](VALIDATION.md)
