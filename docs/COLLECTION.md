# P11-Enhanced 三版本合集 / Three-variant collection

**三個版本都內建同一份已確認基本有效的 P-11 0.2.1 自療程式；擇一安裝即可。**

1. 解壓合集。外層合集 ZIP 不能直接匯入 Arsenal。
2. 從 Mods 中選一個：P11-Self-Hit 為僅治療槍；weapon_self_hit_pistols 為手槍 + P-11；weapon_self_hit_native 為廣域原生武器投射物 + P-11。
3. 關閉遊戲，在 Arsenal 停用其他自命中版本，匯入並啟用所選 ZIP，依管理器流程部署。Bingus Shared Loader v17 / API 1 / internal 16 另行安裝。
4. 所有版本對應 build 25480438；擴展玩法與新包共存未实測，因此標為預覽候選。[範圍說明](docs/VARIANTS.md)

推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，從原頁另行下載。沒有把動作模組、追蹤模組或 loader 放進本合集。

更新後雙擊 **Collect-HD2-Update.cmd**，開啟 diagnostics 最新資料夾中的「摘要.md」和「維修交接.md」。portable 不需 Python；不會啟動遊戲、讀取程序、部署或上傳，也不會假裝自動修好未知版本。[工具說明](docs/UPDATE_TOOL.md)

Source 內為完整公開來源 ZIP，修正相容性後可用其中的 Rebuild-Mods.cmd 重建三包（需 Python）。MOD-SHA256SUMS.txt 核對 Mods。診斷包、遊戲二進位檔與私人資料不要公開上傳。

## English

Every variant includes the unchanged P-11 healing addon. Extract first and install **one** ZIP from Mods in Arsenal: P-11 only, pistols plus P-11, or broad native projectiles plus P-11. Expanded gameplay/coexistence remains unverified. Install the compatible loader separately.

Collect-HD2-Update.cmd creates offline evidence and a repair handoff; it needs no Python, never installs changes or uploads, and does not guarantee automatic repair. Source contains a developer rebuild command. The optional animation companion is linked above and not bundled.
