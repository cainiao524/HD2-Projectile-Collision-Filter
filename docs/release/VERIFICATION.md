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
