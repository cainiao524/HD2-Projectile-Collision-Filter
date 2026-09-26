# P11-Enhanced — P-11 自命中治療

**讓自己射出的 P-11 飛鏢可以命中自己的角色，觸發遊戲原生治療。**
這是獨立的自療 addon：純資料修改、沒有原生 hook，不直接寫入血量或體力。

[English](README.en.md) · [模組介紹](docs/SELF_HIT.md) · [維護與建置](docs/PORTING.md) · [驗證範圍](docs/VERIFICATION.md)

## 功能

- 只處理通過本機玩家、P-11 武器及單發飛鏢身份檢查的投射物。
- 保留原本彈藥、射速、治療量與效果；由真實碰撞觸發原生治療。
- 當 **Experimental Infusion（實驗性融合／實驗性注射劑）** 增益已啟用時，自命中治療可觸發其效果。
- 標準 Bingus Shared Loader API 1 addon，使用獨立 Lua 資源。
- 在 Arsenal 啟用／停用，變更後按管理器流程重新部署。

## 目前版本

| 項目 | 已知狀態 |
|---|---|
| 自療版本 | **0.2.1**，使用者於 2026-09-26 確認基本自命中治療有效 |
| 遊戲 | Steam build **25480438** / EXE **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |

治療有效的證據來自使用者實測；日誌另確認啟用與資料寫入。
這項確認對應上述版本，完整主客機、碰撞時機及並行情況尚未全數驗證。

## 下載

- **玩家安裝**：`P11-Self-Hit-DataOnly-0.2.1-build25480438.zip`。
- **原始碼**：`P11-Self-Hit-Source-v0.2.1.zip`，包含自療程式、建置工具、Lua 模擬測試及文件。
- **校驗**：`SHA256SUMS.txt`。

玩家 ZIP 保留實測成功的原始位元組。包內的 `EXPERIMENTAL`／`unverified` 為封裝當時狀態；
後續基本成功的記錄在本頁、[驗證說明](docs/VERIFICATION.md) 及 `maintenance/baselines.json`。

## 安裝

1. 完整退出遊戲，單獨安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 將自療 ZIP 匯入 Arsenal，停用舊自療 hook、重複版本及研究採集包。
3. 啟用自療與 loader，按照 loader 的優先順序說明部署後啟動遊戲。
4. 裝備 P-11，依照下方方式讓真正射出的飛鏢命中自己的角色，觸發原生治療。

停用時關閉遊戲，在 Arsenal 取消自療項目並重新部署。本模組不會自動把飛鏢轉向自己。

## 使用方法與推薦搭配

**推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/) 一起使用 P-11 自療功能。**
此模組為額外選配，請從原作者頁面另行下載；安裝、操作及適用版本以該頁說明為準。

也可以直接切換至**第一人稱，朝自己的腳射擊**。飛鏢實際命中角色後，才會觸發原生治療。
若要使用 Experimental Infusion 的附加效果，請先在遊戲中啟用該增益；本模組本身不會替你啟用增益。
Experimental Infusion 與第一人稱射腳的說明來自使用者補充回報，詳見[驗證範圍](docs/VERIFICATION.md)。

## 原始碼與更新

玩法核心為 [`core.lua`](mods/p11_self_hit_dataonly/core.lua) 的 97 行 Lua。
身份與所有權檢查、受限資料寫入、版本檢查及 loader 生命周期各自分開。
公開原始碼能重建出與成功版本完全相同的 ZIP，建置方法見 [維護文件](docs/PORTING.md)。

遊戲更新造成版本不符時，模組會停止修改資料。新版本需要確認資料布局與實際治療，不能只替換雜湊強行啟用。
問題回報請提供遊戲 build、自療版本及 loader 版本；私人遊戲檔案與診斷包不屬於公開 Issue 附件。

[來源說明](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)。
本專案與 Arrowhead Game Studios 無隸屬關係；尚未選定專案整體授權。
程式及文件使用 OpenAI 工具協助製作。
