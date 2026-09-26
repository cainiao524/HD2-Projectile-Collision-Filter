# P11-Enhanced preview.2 — 擴展版 0.1.1 篩選修正

修正手槍／廣域候選對同一来源武器逐顆重複查詢的問題。**每包仍內建原始 P-11 0.2.1 自療 Lua；P-11 單獨 ZIP 完全不變。三個版本擇一安裝。**

- 手槍模式先排除非手槍與 P-11，再查附件與定義。
- 同一更新內共用武器與定義的發現結果；實際寫入仍逐顆核對完整依賴欄位、來源、槽位與原值。
- 不跨更新沿用快取，保留回收重用防護；槽位解碼減少 FFI 值建立。
- 32 顆主武器彈丸的合成測試中，手槍模式讀取 427 → 50，廣域模式 1,515 → 985。**這些是模擬讀取量，不是 FPS 測量，也不能證明卡頓已消失。**
- 候選 Lua 153 個斷言與原 P-11 429 個斷言通過；套件保留未知版本停用、無 hook、無直接血量寫入。
- 更新工具 1.1.1 更新了模組指紋，工具 runtime 沿用已驗證來源。

遊戲 build 25480438 / EXE 1.8.46015.0；loader v17 / API 1 / internal 16。手槍名單、廣域機制覆蓋和擴展共存仍是候選，沒有新增玩法實測。依然掃描 2,048 個原生槽位。

下載 Three-Variants 合集後解壓，再從 Mods 選一個 ZIP 匯入 Arsenal。關閉遊戲，停用舊自命中版本，啟用新版並重新部署。沒有自動替你安裝。

遊戲更新後仍可用 Collect-HD2-Update.cmd 產生本機離線診斷與維修交接。工具不保證未知版本全自動修復，不啟動遊戲、不讀程序、不部署、不上傳。

[完整比較與重現方法](https://github.com/cainiao524/P11-Enhanced/blob/main/docs/PERFORMANCE.md) · P-11 推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)（另行下載）。

## English

Candidate 0.1.1 reduces redundant discovery for multi-projectile weapons. It rejects non-pistols before attachment/definition lookup and reuses discovery only within one update. Every write still rechecks its complete dependency chain and its own source/slot; no cross-update authorization cache is used.

All packages retain byte-identical P-11 0.2.1. Choose one variant. Synthetic 32-pellet logical reads fall from 427 to 50 for pistol-mode rejection and from 1,515 to 985 for accepted broad-mode shots. These are not native timing/FPS measurements or proof that stutter is fixed. The 2,048-slot scan remains.

153 candidate and 429 original P-11 Lua assertions pass. Expanded gameplay/coexistence and pistol coverage are still unverified. The offline toolkit updates package fingerprints; it does not install mods or automatically repair unknown builds.
