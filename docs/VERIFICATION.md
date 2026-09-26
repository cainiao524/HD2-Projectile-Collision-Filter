# 自療驗證範圍

2026-09-26：使用者確認自療 0.2.1 可用，對應 Steam build 25480438 / EXE 1.8.46015.0、loader v17 / API 1。
部署 Lua 與交付來源一致。既有日誌另確認啟用、版本／錨點檢查及至少一次資料寫入讀回。
原始日誌保留於本機，公開來源僅記錄必要指紋與驗證範圍。

| 檢查 | 結論 |
|---|---|
| 基本自命中治療 | 使用者實測確認 |
| Experimental Infusion 增益效果 | 使用者於 2026-09-26 補充可觸發；需先啟用該增益，未新增獨立實測 |
| 第一人稱朝自己的腳射擊 | 使用者於 2026-09-26 提供的用法，未新增獨立實測 |
| 原生 hook／執行碼修改 | 沒有；窄化為非執行 heap 的兩個位元組旗標 |
| 成品 ZIP 及 runtime Lua | 保留使用者測試成功的原始位元組 |
| Lua 模擬 | 429 個斷言；完整 addon 僅編譯，不在測試中執行 |
| 公開原始碼重建 | 可重建出與成功模組 ZIP 完全相同的 SHA256 |
| 主客機、切槍、死亡、槽位重用、碰撞時機與並行 | 完整覆蓋尚未完成 |
| Raise Weapon Aims at Yourself 搭配 | 使用者指定的推薦，未新增共存實測記錄 |

「已載入」「寫入讀回」各自只能證明對應事件。治療成功來自使用者回報。
目前的基本成功不能推廣為未來版本或所有聯機／並行條件均已驗證。

## English

Basic self-hit healing on the listed build is confirmed by the user's report. Existing logs corroborate activation and data-write readback only.
The Experimental Infusion effect and first-person foot-shot method were supplied by the user on 2026-09-26; no additional independent gameplay test was performed for this documentation update.
The booster must already be active in the game. The companion-mod recommendation is user-requested, with no additional coexistence test recorded.
The tested gameplay ZIP and Lua remain unchanged. Passing 429 Lua mock assertions and reproducing the ZIP do not establish all host/client, timing or concurrency cases.

## 三版本預覽 / Three-variant preview

三包讀回檢查：每個安裝 archive 都包含且只包含一份原始 P-11 Lua，SHA256 b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a。兩個擴展包另含各自獨立資源，不改 loader 啟動資源。P-11 原 ZIP 的 SHA256 保持不變。

擴展 core / entry 有 24 個 mock 斷言，另以 test_combined.lua 檢查兩種範圍、兩種載入順序、擴展正常／故障時 P-11 回呼繼續運行、nil 參數／回傳及關閉流程。全部只使用 mock adapter，不啟動 native addon。

封裝、回呼組合與離線檢測通過不等於遊戲內命中。擴展自傷、八個手槍 ID 的目前版本有效性、廣域機制覆蓋、新封裝中 P-11 的實際共存和完整主客機／並行矩陣都未新增玩法驗證。

Every variant includes the exact P-11 Lua; packaging checks and mocked callback composition cover both load orders and expanded failures. Neither expanded gameplay nor the new packages' native coexistence is established by those tests.

## 發布離線驗收 / Release offline checks

2026-09-26：53 項 Python 測試通過；P-11 429 個 Lua mock 斷言、候選核心／入口 24 個，以及新包回呼组合 84 個斷言通過。三包皆從乾淨 Source ZIP 重建成相同位元組，P-11 原 ZIP 和三包內 P-11 Lua 指紋不變。

兩個多資源 archive 與 loader 作者本機封裝器輸出逐位元組相符。Windows portable 在 PATH 不含 Python 時啟動成功，並對 build 25480438 的本機磁碟資料完成離線收集。沒有啟動遊戲或新增玩法驗證。公開資產排除本機診斷、遊戲二進位檔和私人日誌。

## 0.1.1 擴展篩選修正

候選 Lua 共 153 個斷言：核心 17、篩選／重用 45、入口 7、P-11 回呼组合 84。P-11 原 429 個斷言及成功 ZIP/Lua 不變。新增測試逐一改動快取所依賴的 23 個共同欄位，後續彈丸均拒絕使用舊依據寫入；另測試槽位與來源改變、不同來源武器共用彈種、跨更新重新分類。

benchmark_reads.py 僅記錄合成資料下的邏輯讀取量，不是 Windows API 實測或遊戲 FPS。未新增遊戲內測試；效能改善幅度、卡頓是否消失與擴展玩法仍待確認。

## v0.3.0-preview.3 三選一封裝

2026-09-26：54 項 Python 測試通過。新包的一個父選項含三個互斥子選項；三個完整 archive、sidecar 及其中 P-11 bytes 與上一版相同。沒有變更 Lua，所以沿用上一版 runtime 測試記錄，未新增玩法測試。

以本機 Arsenal **0.36.2** 的實際匯入／部署／清除後端在隔離假遊戲目錄測試：自動啟用偏好開／關兩種設定、預選 P-11、所有 9 種前後方案切換、無選项、父項停用、模組停用、重新啟用、清除皆通過。每次部署與所選原始 archive 的 SHA256 一致，未選方案無殘留。僅有一個父選項時，該父選項會自動開啟；模組總開關仍遵從匯入偏好。

測試使用 purge 後重新 deploy 的管理器流程，沒有操作真實 UI、真實 profile 或遊戲目錄。官方互斥子選項格式見 [Arsenal 文件](https://docs.rsnl.gg/mod-builder/options)。UI 點選操作與遊戲內原生共存沒有新增實測。

## v0.3.0-preview.4 四方案與排除篩選

56 項 Python 測試通過，候選 Lua 638 個斷言（17 核心、45 原篩選、437 霰彈／多彈丸／混合爆量／未知型號、13 入口與全部互斥配對、126 P-11 回呼組合）。P-11 成功 ZIP/Lua SHA256 和 Windows 兩位元組 writer 保持不變。

固定離線參考表共 350 記錄，以三個名稱雜湊、口徑和彈丸數核對 27 個霰彈記錄；連同表內全部 32 個多彈丸記錄，聯集為 38 個排除 ID。P-11 type 318、單發及 unit hash 另外核對，不在排除集合。可用 verify_projectile_filter.py 重驗。資料表與模擬不代表目前遊戲所有武器均已實測。

Arsenal 0.36.2 隔離後端通過四選一匯入、首項預選、兩種匯入啟用偏好、全部 16 種切換、停用／重新啟用及清除，所選 archive 原樣部署。測試不操作真實 UI/profile 或遊戲目錄。

32 顆 type 179 合成情境中，排除版只做 10 次共用／類型頁讀取且不寫入；第四版為 985 次、32 寫入。原有普通 type 22 的讀取／寫入量與 0.1.1 相同。仍遍歷槽位，沒有遊戲 FPS、不卡頓或完整新玩法的成功聲明。
