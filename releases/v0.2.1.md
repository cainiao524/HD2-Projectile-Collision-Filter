# P11-Enhanced v0.2.1 — P-11 Self-Hit Healing / 治療手槍自療

## 繁體中文

**讓自己射出的 P-11 飛鏢可以命中自己，觸發遊戲原生治療。**
純資料修改、沒有原生 hook，不直接寫入血量／體力；保留原生彈藥消耗、射速及治療量。
可透過 Arsenal 獨立啟用／停用。

**當 Experimental Infusion（實驗性融合／實驗性注射劑）增益已啟用時，自命中治療可觸發其效果。**

### 使用方式

裝備 P-11，**推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**，
或直接切換至**第一人稱，朝自己的腳射擊**。實際飛鏢命中自己的角色後才會觸發治療。
推薦模組請至原作者頁面另行下載；Experimental Infusion 需在遊戲中啟用。

### 安裝與版本

完整退出遊戲，在 Arsenal 匯入成品 ZIP，停用舊自療 hook、重複版本及研究包。
啟用本模組與相容 loader，按 loader 的優先順序說明部署後啟動遊戲。
停用時關閉遊戲，在 Arsenal 取消本模組後重新部署。

目前版本：模組 **0.2.1**、Steam build **25480438** / EXE **1.8.46015.0**、
**Bingus Shared Loader v17 / API 1 / internal 16**。Loader 請[另行安裝](https://github.com/CowboyBingus/BingusSharedLoader)。

基本自療已由使用者實測確認；Experimental Infusion 與第一人稱射腳方法也來自使用者補充。
完整主／客機、碰撞時機與並行情況尚未全數驗證。未知版本會停止資料修改。

## English

**Allow your own P-11 darts to hit your character and trigger native healing.**
Data changes only, with no native hook or direct health/stamina writes. Native ammo consumption, fire rate and healing amount are preserved.
Enable or disable the addon independently through Arsenal.

**With the Experimental Infusion booster active, self-hit healing can trigger its effects.**

### How to use

Equip the P-11. **We recommend pairing it with [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**,
or switch to **first-person view and shoot your own foot**. The dart must actually hit your character to trigger healing.
Download the optional companion separately from its author's page. Experimental Infusion must be active in the game.

### Installation and compatibility

Close the game completely, import the gameplay ZIP into Arsenal and disable old self-hit hooks, duplicate versions and research addons.
Enable this addon and a compatible loader, deploy according to the loader's priority instructions, then launch the game.
To disable it, close the game, disable its Arsenal entry and redeploy.

Current versions: mod **0.2.1**, Steam build **25480438** / EXE **1.8.46015.0**,
**Bingus Shared Loader v17 / API 1 / internal 16**. [Install the loader separately](https://github.com/CowboyBingus/BingusSharedLoader).

Basic self-hit healing was confirmed by the user. Experimental Infusion and the first-person foot-shot method are also user-reported.
Full host/client, collision-timing and concurrency coverage remains incomplete. Unknown game versions are rejected.

## Downloads / 下載

- **Mod / 模組成品**: `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip`
- **Source / 自療原始碼**: `P11-Self-Hit-Source-v0.2.1.zip`
- **Checksums / 檔案校驗**: `SHA256SUMS.txt`

The tested gameplay ZIP and Lua remain unchanged. 429 Lua mock assertions pass, and the clean source reproduces the original gameplay ZIP.
已測成功的 ZIP 與 Lua 原樣保存；429 個 Lua 模擬斷言通過，乾淨原始碼可重建同一份成品 ZIP。
