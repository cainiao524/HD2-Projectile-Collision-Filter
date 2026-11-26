# P-11 純資料自命中 0.2.1 實驗版

這是使用者要求直接製作的最小候選 addon。**程式已實作資料修改，遊戲內自療效果尚未驗證。**
只適用目前 build **25480438** 的精確 game.dll／EXE 指紋，以及 Bingus Shared Loader **API 1／內部 16**（已檢視的公開 v17）。

## 0.2.1 初始化修正

使用者的 0.2.0 日誌顯示 `Loaded section differs; data writes=0`：模組已被 loader 載入，
但在啟用前停住；這次沒有清除過飛鏢位元。0.2.0 日誌沒有記錄具體區段／欄位，因此不推定是哪個欄位變動。

0.2.1 保留相同遊戲指紋、資料位址、12 組 code anchors、Arsenal GUID 與 Lua 資源，修正初始化：

- 完整磁碟檔案用 SHA256 核對；載入後核對原始虛擬區段 1–4 的 RVA、大小及旗標，覆蓋全部使用的模組 RVA。
- `SizeOfRawData`／`PointerToRawData` 屬於磁碟佈局，不再作載入映像的相等條件；其磁碟內容仍由精確檔案雜湊固定。
- 既有 update 執行後才開始載入映像驗證；最多等待 600 次 update，每 120 次重試。通過前沒有資料寫入，持續失敗則停用。
- 所有原值、owner、記憶體頁面及 12 組指令檢查保留。失敗日誌會寫出區段、欄位、預期值及實際值。

檔案與載入佈局的區分依據：[Microsoft PE 格式說明](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#section-table-section-headers)。
這是初始化檢查修正；新版本尚未取得遊戲內啟用或治療成功的證據。

## 使用

1. 關閉遊戲，在 Arsenal 以 0.2.1 取代 0.2.0，並停用其他自療 hook／實驗包及 P-11 Observer、Code Capture 研究包。
2. 匯入 `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip`，啟用 **P-11 Self-Hit Data Only 0.2.1 - EXPERIMENTAL**，按 Arsenal 原流程部署。
3. 保留 Bingus Shared Loader。原作者追蹤模組仍由原有 Arsenal 項目控制；原 ZIP、F9 和追蹤邏輯未改。
4. 正常使用 P-11。這個 addon 沒有 F6／F8 選單或採集步驟，不會幫飛鏢轉向自己；只有实际飛鏢接觸自己的角色時，才有機會由原生流程治療。
5. 停用時關閉遊戲，在 Arsenal 取消該項目並重新部署。管理器的部署開關不是遊戲內熱切換。

## 最小實作

每次 Lua `update` 在轉交既有回呼前，確認本機角色、P-11 來源武器、附件所有者、彈頭類型 318 與 stim 定義身份。
對佔用且帶 `0x20` 的候選槽，重新核對來源、指標、原值及可寫資料頁，再執行：

```lua
desired[0] = bit.band(expected, 0xffdf)
```

唯一寫入目標是該槽的兩個旗標位元組，寫入後讀回。沒有修改 executable code、安裝原生 hook、
配置可執行記憶體、改頁面保護、改共享彈頭／武器定義，或寫生命、體力、彈藥與治療量。
不呼叫原生遊戲函式，不包含研究採集／分析工具。Windows API 僅用於版本核對及受限資料讀寫。

每幀重新定位，沒有跨幀保留飛鏢地址；關閉或資料失效後停止新修改，已射出的飛鏢交還原生生命週期。
因此不把舊地址當作還原目標。原值僅保留於本次寫入的區域變數，供比較和讀回確認。

## 已知限制

- Lua `update` 可能晚於碰撞查詢；成功清位元不代表自命中成功，也不能補回已消失的飛鏢。
- 本版只接受來源實體能核對為本機 P-11 武器的原生槽；原追蹤的其他生成路徑可能被跳過，兩者同開效果未驗證。
- 佔用旗標與 auxiliary ID 都不是已證實的物件世代；相同槽仍可能在檢查與寫入間重用。
- 原值比較和兩位元組寫入不是原子 compare-exchange。原生執行緒若同時改旗標，仍有競態；本版沒有宣稱已消除並行風險。
- 玩家尚未就緒或身份變動時略過當幀；版本不合、衝突、寫入／讀回失敗則停用。未知版本不放行。

日誌：`%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\P11StimSelfHit.log`。
`WAITING IMAGE` 表示尚未啟用；`ENABLED` 表示全部必要版本檢查通過；`FIRST DATA WRITE READ BACK` 只表示資料寫入讀回，不表示治療成功。
沒有要求重新進行遊戲內資料採集。

ZIP 的 `Source/p11_self_hit_dataonly.lua` 是完整可讀 Lua 原始碼；addon 使用獨立資源
`mods/p11/self_hit_dataonly`，不接管 loader 的 Wwise／boot 啟動資源。
