# 純資料自命中 0.2.1 實驗版驗證

2026-09-26：使用者停止額外遊戲內採集後，明確要求直接實作最小 loader addon。
本版依此要求交付候選程式，沒有將未驗證玩法標成完成。

## 0.2.0 實際失敗與修正範圍

使用者回報沒有作用。最新日誌證實 loader 載入成功，但版本檢查報 `Loaded section differs`，資料寫入為零。
磁碟已部署 Lua SHA256 與 0.2.0 交付一致；當前磁碟檔案和先前完整採集的 PE header 均符合原 profile。
日誌沒有區段索引或欄位值，無法確認差異屬於 raw metadata、未使用區段或載入階段。
失敗證據保存在工作區 `work/p11-dataonly-0.2.0-failure-20260926-092209/`。

0.2.1 分開磁碟檔案和載入映像驗證。固定模組位址与全部 anchors 都落在檢查的原始區段 1–4，
打包器會核對這點；未使用的額外區段不參與資料定位。raw size／offset 的磁碟語義見
[Microsoft PE 格式](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#section-table-section-headers)。
啟用移到既有 update 之後；持續錯誤最多等待 600 次 update，絕不因逾時而跳過驗證。

新增測試：raw metadata 與虛擬 geometry 分開、12 個必要虛擬欄位逐一拒絕、具體錯誤值、
短暫不就緒恢復、持續錯誤保持零寫入、啟用前雜湊重新核對、初始化期間保留原 callback。
這些是合成回歸測試，不能將模擬的 header 差異宣稱為實際失敗的具體欄位。

## 已執行

- LuaJIT 模擬測試 **429 個斷言**：核心 31、Windows 資料 adapter 329、入口 35、版本檢查 34。
- 核心與實際 adapter 組合執行時，所有 Windows API 由測試函式替代；只讀寫合成記憶體表。
- 核對本機磁碟 game.dll／EXE SHA256 仍符合 build 25480438 profile。
- 版本檢查使用已取得的離線程式碼採集：PE header 與 12 組 anchors 全部一致，改變指紋／header／anchor 的測試會拒絕。
- 最終 Lua bundle 僅編譯，不執行其 Windows adapter；沒有啟動遊戲、讀取執行中遊戲程序或部署 addon。
- 封裝 round-trip 檢查單一獨立 Lua 資源、宣告、hash、envelope、manifest 與空 sidecars。
- 打包器拒絕 executable patch／allocation／protection 等能力及研究輸出格式；唯一遊戲記憶體寫入呼叫固定為 2 bytes。

## 有意義的覆蓋

合格本機 P-11 清除 0x20；其他旗標保留原快照值；不處理外來射手、其他彈頭、
未佔用槽、不同武器、錯誤附件所有者／角色／registry／定義或已清除位元。
相同索引換成其他 owner、檢查期間來源／aux／指標／類型／原值變動時不寫入。
執行頁面、共享 image 或 mapped 頁面、短讀、短寫及讀回不符均拒絕或停止。
沒有對舊槽做回復寫入。保留原 callback 參數、含 nil 返回值及錯誤；不覆蓋後續 addon 安裝的 wrapper。
啟動時映像尚未通過檢查會有限次重試；通過後玩家資料尚未建立會略過當幀。磁碟版本或寫入錯誤則停用。

## 尚未通過

實際飛鏢自命中／原生治療、生成到碰撞的先後時機、可靠 generation 身份、
原生執行緒並行寫入安全、與原追蹤同開、切槍／死亡／離開任務時的實際行為。
讀取—檢查—寫入不是原子交易，測試不能證明競態不存在。

這是 **資料寫入已實作、玩法未驗證** 的實驗包。最終驗收仍未完成；
不以寫入計數、讀回成功、套件可載入或匹配雜湊代替治療成功。
