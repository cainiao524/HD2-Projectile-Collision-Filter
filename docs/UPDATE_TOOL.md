# Update Toolkit 1.3.0：一鍵離線檢測與維修交接

**完整解壓後雙擊 Collect-HD2-Update.cmd。** Windows x64 工具包已包含 P11-Update.exe，收集不需 Python。完整對應源碼和操作指南在 `Source/P11-Enhanced/`；工具包不是 Arsenal 模組。

## 一次收集操作

1. 等 Steam 遊戲更新、loader 更新及管理器部署結束。
2. 從解壓後的工具包執行 Collect-HD2-Update.cmd。會自動辨識 Steam 安裝；多份或找不到時，要求選擇／提供遊戲資料夾。
3. 開啟工具旁 `diagnostics/latest.json` 指向的新資料夾，先讀「摘要.md」，再讀「維修交接.md」。
4. 結果不完整時先解決列出的缺檔／變動再重收。完整時保留診斷 ZIP，按 [Agent 接手指南](AGENT_GUIDE.md) 進行離線判讀。

每次建立獨立資料夾及 ZIP，不覆寫上次收集。結束碼 0 表示收集完整，2 表示不完整或錯誤；都不是遊戲玩法測試結果。

## 收集內容及界限

| 內容 | 如何使用 |
|---|---|
| EXE／DLL 版本、SHA-256、PE 結構與本機副本 | 辨識版本、比較離線布局；檔案加密時可能仍不足以定位 |
| Steam 更新狀態、部署 archive 和有效資源覆蓋順序 | 判斷是否更新中及磁碟上最後覆蓋的資源來源；不能證明執行時已載入，收藏 ZIP 也不代表已部署 |
| 四種功能身份、loader 版本／API | 區分 P-11 舊確認基準、擴展候選、缺內建 P-11 與互斥衝突 |
| 相關既有日誌的結構化事件 | 僅作歷史事件依據；原始私人文字不複製進報告 |
| 本機模組 ZIP、彈頭資料與結構定義 | 保留來源與指紋，不把旧快取自動視為目前 build |
| 上次收集與既有基準差異 | 將變更對應到功能；上次收集本身不是已驗證版本 |

自動搜尋工具旁的 `Mods/`、Downloads 中符合名稱的最近最多 12 個 ZIP，以及 `reference-data/`、已設定目錄、Filediver Go 快取中的資料表／結構。工具包本身不附模組 ZIP；自動搜尋不到時可明確提供 `--package`。未知快取的 `matches_game_build` 保持 false。

任兩個擴展資源並存會報互斥衝突；擴展已部署但沒有內建 P-11 也會提示。未選的方案 `not_deployed` 可以是正常情況，請與 Arsenal 所選範圍一起看。

## 報告與判讀順序

| 檔案／欄位 | 檢查重點 |
|---|---|
| 摘要.md | 中文完整性、功能、部署、loader 與缺口 |
| 維修交接.md | 證據、候選、未決問題及下一步 |
| report.json 的 collector | 本次收集器名稱與版本；1.3.0 不代表模組 runtime 升版 |
| complete／errors | 檔案是否穩定；不完整就先處理收集問題 |
| build／deployed／feature_assessment | 遊戲指紋、有效資源、四個功能、loader 與衝突 |
| profiles／schema_sources／gaps | 離線候選、資料表來源及無法確認的問題 |
| porting-map.json | 舊布局和不得省略的核對要求 |
| binaries／packages／deployed／schemas | 私人離線分析副本，不能當公開發布資產 |

四個功能結果會區分：符合既有已確認基準、符合尚未驗證候選、需要移植且找到候選、離線資料不足、收集不完整。符合基準仍需檢查部署和 loader；長指令模式只產生候選，不會啟用功能。

工具不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳。EXE／DLL／部署檔案在收集期間改動、缺失或 Steam 仍在更新時，結果標為不完整。**收集完整只代表取得穩定檔案，不代表新版自療或自傷已成功。**

## 指定本機輸入

在工具包根目錄打開 PowerShell。以下使用互動輸入，避免複製別人的電腦路徑：

```powershell
$gameDirectory = Read-Host '輸入 Helldivers 2 安裝資料夾'
.\P11-Update.exe --game "$gameDirectory"
```

明確加入一個模組 ZIP 及參考表所在資料夾：

```powershell
$packageFile = Read-Host '輸入本機模組 ZIP 完整路徑'
$schemaDirectory = Read-Host '輸入參考表與結構所在資料夾'
.\P11-Update.exe --game "$gameDirectory" --package "$packageFile" --schema-dir "$schemaDirectory" --no-auto-packages
```

`--package`／`--schema-dir` 可重複提供。`--no-auto-packages` 停止搜尋 Downloads，但仍可使用明確提供的包與工具旁 Mods。`--output` 可指定遊戲資料夾外的輸出位置，`--logs` 可指定既有日誌目錄。

只使用公開源碼時，在源碼根目錄執行 `python tools/offline_update.py`，參數相同，需 Python 3.10+。若從工具包內 Source 執行，預設輸出位於 `Source/P11-Enhanced/diagnostics/`，在該源碼專案內；一般收集建議使用外層 portable 入口。

## 下一步

先依摘要解決缺檔、更新中、部署衝突或 loader 不符；真正的新 build 移植按 [逐步接手指南](AGENT_GUIDE.md) 和 [PORTING](PORTING.md) 處理。修正來源後，`Rebuild-Mods.cmd` 只會封裝已修改的程式，不會自動推算新位址。

不能只换雜湊、直接採用候選地址或改用 native hook。離線不足時列出具體未決欄位，不要求額外遊戲內捕捉；没有新玩法證據仍保持候選。**工具一次收齊可取得的離線資料，減少反覆補檔，不承諾每次更新都能全自動修復。**

## English

Extract and run Collect-HD2-Update.cmd after updates and deployment finish. The Windows x64 executable needs no Python. It collects stable offline identities, deployed resources, selected packages, parsed historical logs and available reference data, then writes a Chinese summary and repair handoff.

The report distinguishes collection completeness, known identities, candidate evidence and missing information. It does not launch the game, read processes, deploy, upload or prove gameplay. Toolkit 1.3.0 includes matching source under Source/P11-Enhanced. Keep diagnostic binaries and private evidence out of public issues and releases.
