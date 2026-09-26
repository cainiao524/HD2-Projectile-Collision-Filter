# P-11 Self-Hit Healing / P-11 治療手槍自療

## 繁體中文

**讓 P-11 治療手槍也能治療自己。**
本模組讓自己射出的 P-11 飛鏢可以命中自己的角色，再由遊戲原生碰撞與治療邏輯處理。
保留原本的彈藥消耗、射速、治療量與效果，採純資料修改，沒有原生 hook，也不直接寫入血量或體力。

### 功能

- 真正的飛鏢自命中治療，只處理通過本機玩家、P-11 武器及投射物身份檢查的飛鏢。
- 當 **Experimental Infusion（實驗性融合／實驗性注射劑）** 增益已啟用時，自命中治療可觸發其效果。
- 標準 **Bingus Shared Loader API 1 addon**，使用獨立 Lua 資源。
- 在 **Arsenal** 中獨立啟用／停用。

### 使用方法

1. 裝備 P-11 治療手槍。
2. **推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**；也可以直接切換至**第一人稱，朝自己的腳射擊**。
3. 飛鏢實際命中自己的角色後，觸發遊戲原生治療。若 Experimental Infusion 增益已啟用，也可觸發其效果。

本模組不會自動把飛鏢導向自己，仍需手動瞄準並射擊。
推薦搭配的模組為額外選配，請到原作者頁面另行下載，操作及適用版本以該頁說明為準。
Experimental Infusion 需在遊戲中啟用，本模組不會替你啟用該增益。

### 安裝與停用

1. 完整退出遊戲，單獨安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 將 `Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip` 匯入 Arsenal，選擇 **P-11 Only / 僅治療手槍**。
3. 停用舊自療 hook、重複版本及研究採集包，啟用本模組與 loader，依 loader 的優先順序說明部署後啟動遊戲。
4. 停用時，先關閉遊戲，在 Arsenal 取消本模組並重新部署。

### 相容版本與驗證

| 項目 | 目前版本 |
|---|---|
| 模組 | **v0.3.0-preview.8 整合版** |
| 遊戲 | Steam build **25480438** / EXE **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |

使用者於 2026-09-26 確認基本自命中治療有效，並補充 Experimental Infusion 與第一人稱射腳用法。
這些玩法說明以使用者回報為依據；完整主／客機、碰撞時機與並行情況尚未全數驗證。
遇到未知遊戲版本時，模組會停止資料修改，新版需重新核對布局與實際治療。

目前整合版的四個方案已有使用者正常回報。本次发布保持該已測整合候選的四份 Lua／遊戲資源不變；包裝檔名與雙語配置可更新。嵌入候選狀態反映建立當時狀態，後續證據另記發布文件和 maintenance。

## English

**Let the P-11 Stim Pistol heal its owner.**
This mod allows darts fired from your own P-11 to collide with your character and trigger the game's native healing.
Ammo consumption, fire rate, healing amount and effects retain their native behavior. The implementation changes data only: it installs no native hook and does not write health or stamina directly.

### Features

- Real self-hit healing from a fired dart. Only projectiles that pass local-player, P-11 weapon and projectile identity checks are modified.
- With the **Experimental Infusion** booster active, self-hit healing can trigger its effects.
- A standard **Bingus Shared Loader API 1 addon** with its own Lua resource.
- Enable or disable it independently through **Arsenal**.

### How to use

1. Equip the P-11 Stim Pistol.
2. **Recommended: pair it with [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/).** Alternatively, switch to **first-person view and shoot your own foot**.
3. A dart must actually hit your character to trigger native healing. If Experimental Infusion is active, the hit can trigger its effects as well.

You still aim and fire manually; this addon does not steer darts toward yourself.
The recommended companion is optional and must be downloaded separately from its author's page. Follow that page for its controls and supported versions.
Experimental Infusion must be activated in the game; this addon does not activate the booster for you.

### Installation and disabling

1. Close the game completely and install a compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately.
2. Import `Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip` into Arsenal and select **P-11 Only / 僅治療手槍**.
3. Disable old self-hit hooks, duplicate versions and research addons. Enable this addon and the loader, deploy according to the loader's priority instructions, then launch the game.
4. To disable it, close the game, disable its Arsenal entry and redeploy.

### Compatibility and validation

| Component | Current version |
|---|---|
| Mod | **v0.3.0-preview.8 integrated** |
| Game | Steam build **25480438** / EXE **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |

On 2026-09-26, the user confirmed basic self-hit healing and supplied the Experimental Infusion and first-person foot-shot behavior notes.
These gameplay descriptions are based on user reports; full host/client, collision-timing and concurrency coverage remains incomplete.
Unknown game versions are rejected. New versions need layout checks and actual healing confirmation.

All four current integrated choices have a user report of normal basic operation. This release preserves the tested integrated Lua/game-resource bytes while updating packaging and bilingual configuration. Embedded candidate labels reflect build-time state; later evidence is recorded separately in release documentation and maintenance data.

---

Loader: CowboyBingus. Helldivers 2 and its original assets: Arrowhead Game Studios and their respective rights holders.
HD2-Projectile-Collision-Filter is an independent community mod. Development and documentation were assisted by OpenAI tools.
