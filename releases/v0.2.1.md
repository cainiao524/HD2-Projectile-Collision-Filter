# P11-Enhanced v0.2.1 — P-11 自命中治療

**讓自己射出的 P-11 飛鏢可以命中自己，觸發遊戲原生治療。**
0.2.1 的基本自療功能已由使用者實測確認，對應 Steam build **25480438** / EXE **1.8.46015.0**。
需要單獨安裝 **Bingus Shared Loader v17 / API 1 / internal 16**。

自療採純資料修改，沒有原生 hook，不直接寫入血量／體力；彈藥、射速及治療量保持原生規則。
可在 Arsenal 獨立啟用／停用。實際效果需要真正射出的飛鏢命中自己的角色。

**推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/) 一起使用。**
這是另行下載的選配模組，安裝及操作請參閱原作者頁面。

## 下載與安裝

- **模組成品**：`P11-Self-Hit-DataOnly-0.2.1-build25480438.zip`。
- **完整自療原始碼**：`P11-Self-Hit-Source-v0.2.1.zip`。
- **檔案校驗**：`SHA256SUMS.txt`。

完整退出遊戲，在 Arsenal 匯入模組成品 ZIP，停用舊自療 hook／重複版本／研究包，
啟用本模組及相容 loader，依 loader 的優先順序說明部署後啟動遊戲。

## 驗證範圍

成功的自療 ZIP 與 Lua 原樣保存；包內實驗版文字保留封裝時狀態，後續基本成功已另行記錄。
Lua 模擬通過 429 個斷言；乾淨原始碼能重建同一份成功 ZIP。
完整主／客機、碰撞時機、槽位重用及並行情況尚未全數驗證。
