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

## v0.3.0-preview.5：Projectile Collision Filter 與六檔發布

2026-09-26：93 項 Python 測試通過；P-11 429 個及擴展 638 個 Lua 模擬斷言通過。四個獨立 ZIP、31 個模組實作與內嵌文件的位元組均與整理前一致。四選一整合包改名為 Projectile Collision Filter，保留 GUID 與方案順序；沒有修改自命中、霰彈排除或寫入保護。

Arsenal 0.36.2 的隔離後端再次通過兩種匯入啟用偏好、四項互斥與首項預選、全部 16 種切換、無選項、父項停用、模組停用／重新啟用及清除。所有所選 archive 的雜湊與原始包一致；沒有操作真實管理器 profile 或遊戲。

六項發布資產的大小、SHA-256、ZIP 結構、源碼清單與私人資料界限通過本機核對。從解壓工具包內的乾淨源碼重建五個模組 ZIP，全部與待發布檔案逐位元組相同。當前主要指南的 51 個本機文件連結可解析；文件同步工具覆蓋非 Git 備份、已有編輯、暫存修改及不安全路徑等情境。

Update Toolkit 1.3.0 在 PATH 沒有 Python 的環境可啟動；已封裝 EXE 對合成未知 build 完成離線收集，記錄工具版本並產生交接，仍正確顯示離線證據不足與玩法未驗證。測試亦覆蓋缺 DLL、Steam 更新中、複製期間檔案變動、loader 不相容、部署衝突及改名後下載包辨識。固定參考表重新核對 38 個排除 ID、全部 32 個多彈丸類型及 P-11 例外。

以上是源碼、封裝、模擬與隔離工具驗證，沒有新增實際遊戲自命中、擴展自傷、共存或 FPS 測試。原 P-11 成功範圍及擴展候選狀態維持原記錄。


## v0.3.0-preview.6：副武器分類擴展的初始本機驗證

本節記錄發布整理前的開發候選驗證，並未完成全部可射擊副武器機制。P-11 保留既有回報；新增副武器沒有新的玩法或 FPS 證據。

- 116 項 Python 檢查通過，包含副武器 catalog 完整性、身份篡改拒絕、來源指紋、政策限制，以及安裝資料表收集／中途變更／前後比較。
- P-11 Lua：429 項既有模擬檢查通過；擴展 Lua：3,322 項通過，其中 2,684 項使用真正編入套件的副武器清單，涵蓋每個來源、38 個排除彈種、所有權與物件重用。
- 固定 Filediver 三表完整重播，27 個副武器記錄的身份、元件、差量、位置及統計與 catalog proof 相符。這不證明與目前安裝的加密表等價。
- 新舊來源清單在 0／1／32／64 個相同有效槽位的測試中，遊戲記憶體讀取次數相同。這是讀取次數回歸，不是零效能成本或實際 FPS 測試。
- Arsenal 0.36.2 隔離後端檢查：匯入的啟用／停用偏好、P-11 預選、16 種切換、總開關、清除及四份部署內容一致；未改使用者 profile 或真實部署。
- 原 P-11 ZIP／Lua 和兩個 0.1.2 廣泛範圍 ZIP 雜湊保持不變。擴展核心的五個 runtime Lua 檔保持不變，手槍範圍改為 0.1.3 的生成設定。
- Toolkit 1.3.1 已對目標 build 25480438 完成一次穩定的實際離線收集，取得五份安裝資料表，沒有收集錯誤；`runtime_verified` 和各表 `matches_game_build` 均為 false。

Dagger 光束與 Crisper 噴射沒有實作；Warrant、P33、Hornet 的 entity 後續鏈未驗證。來源清單的 16 個 ID 只是原生槽位候選，不是 16 把已證明能自命中的武器。完整限制與資料來源見 [副武器狀態](SECONDARIES.md)。此初始候選驗證不改變 preview.5 的歷史玩法驗證結論。


## v0.3.0-preview.6：雙語發布頁與封面整理

發布前完整回歸通過 120 項 Python 測試、429 項 P-11 Lua 斷言及 3,322 項擴展 Lua 斷言。新增發布檢查只允許兩張經核對的 PNG 封面，驗證結構、大小、解析度、CRC 及 SHA-256；其他二進位檔仍不屬於公開源碼。BBCode 與 Markdown 同樣通過私人路徑／憑證檢查。

Arsenal 選項說明補上英文，保留四個中文名稱、選項顺序及 GUID。中英首頁、Release 介紹、兩個模組的網站文案與封面同步準備；動作封面參考 P3R 召喚姿勢，但原動作包未更動。封面都是宣傳插畫，不是遊戲截圖。

維持預覽版狀態，擴展機制、共存與實際效能未新增玩法證據；Dagger／Crisper 及 entity 分支限制維持不變。AyakaMods 網站尚未更新，本次只準備可直接複製的本機資料。

Pre-publication regression passed 120 Python tests, 429 P-11 Lua assertions and 3,322 expanded Lua assertions. Artwork and BBCode are checked against the public source allowlist. Bilingual packaging and promotional artwork do not establish additional gameplay or performance verification. The original animation package is unchanged; AyakaMods editing remains deferred.
