# 一鍵離線檢測與維修準備 / Offline diagnostics and repair handoff

**完整解壓後雙擊 Collect-HD2-Update.cmd。** Windows x64 工具包內建 P11-Update.exe，不需安裝 Python；若直接使用原始碼則需 Python 3.10+。

更新完成後執行。自動找 Steam 安裝；有多份或找不到時要求選擇／提供遊戲目錄。每次在工具旁 diagnostics 建立新資料夾和 ZIP。

收集 EXE/DLL 版本、雜湊、PE 結構與本機副本，Steam 更新狀態、實際部署資源覆蓋順序、四範圍 Lua、loader 版本及既有相關日誌的結構化結果。原始日誌中的帳號或私人文字不複製進報告。

自動納入合集 Mods 的套件、Downloads 裡符合名稱的最近最多 12 個 ZIP，以及 reference-data、已設定目錄與 Filediver Go 快取中的彈頭表／結構。記錄每份指紋及來源類型，不假定舊快取對應目前 build。

與上次收集和已知基準比較，對三個功能範圍區分：符合 P-11 舊確認基準、符合未驗證候選、需移植且找到候選、離線不足。比對六個長指令模式只產生候選，不啟用功能。任兩個擴展資源並存會報互斥衝突；擴展資源存在但缺少 P-11 時也會提示舊版／不完整部署；原始日誌不是本次成功證據。

## 產物

- 摘要.md：中文結果、部署／loader 狀態與具體缺口。
- report.json：完整指紋、差異、錯誤與候選。
- 維修交接.md、porting-map.json：原布局與不得省略的修復檢查。
- binaries、packages、deployed：本機或私人分析副本，不是 GitHub 公開資產。

工具不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳。檔案在收集期間改動、缺失或 Steam 還在更新時標為不完整。收集完整只代表檔案穩定。

## 修復流程

1. 一鍵檢測，先處理缺檔、中途更新、loader 不符或互斥項目。
2. 用公開來源與診斷包核對新布局、所有權、12 個錨點及武器範圍。加密磁碟資料不足時列明缺口，不要求新的遊戲內捕捉。
3. 修正程式與版本設定；不能只換雜湊、直接採用候選地址或退回原生 hook。
4. 在來源雙擊 **Rebuild-Mods.cmd** 一次重建四選一 ZIP 及四個原始獨立 ZIP（Python 3.10+）。它只封裝已修正的來源，不會推算新地址。
5. 跑模擬和封裝檢查，沒有新版玩法確認前保持候選狀態。

**此工具一次收齊可取得的離線資料並準備維修交接，不承諾每次更新全自動修復。**

進階用法：

```powershell
.\P11-Update.exe --game "D:\SteamLibrary\steamapps\common\Helldivers 2" --schema-dir "D:\ModReference" --package "D:\ModPackages\example.zip"
```

--schema-dir / --package 可重複使用；--no-auto-packages 不搜尋 Downloads。診斷資料保留本機，不應上傳公開 Issue。

## English

Extract and run Collect-HD2-Update.cmd after updates finish. The portable Windows x64 executable needs no Python. It gathers offline identities, deployed resources, selected local packages, parsed logs and available schemas. It distinguishes historical P-11 confirmation from unverified expanded candidates and flags conflicting scopes.

No game launch, process access, modification, deployment or upload occurs. Changing/missing files make collection incomplete. The generated handoff supports a reviewed port; Rebuild-Mods.cmd packages that edited source, not an automatic address fix or gameplay proof.

1.2.0 增加廣域排除霰彈的獨立識別、三種擴展任兩者互斥診斷，維修交接包含彈種排除表核對要求。收藏 ZIP 中含四方案不代表四方案已部署；以遊戲 data 中的有效資源為準。
