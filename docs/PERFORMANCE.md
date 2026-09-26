# 游標處理與性能 / Cursor processing and performance

preview.8 四種範圍共用一個 addon。旧版本反覆遍歷全部 2,048 個原生投射物槽位；新版跟隨分配游標，檢查近期候選及有限待辦，不再由原 P-11 與擴展 addon 分別掃描全部槽位。游標不是免費的射擊事件，也不免除每顆候選的身份及寫入核對。

## 有限工作量

| 項目 | 上限或行為 |
|---|---|
| 待辦槽位 | 256 |
| 每次更新檢查 | 128 槽 |
| 每次更新寫入嘗試 | 64 |
| 待辦生命期 | 最多 8 次有效排程更新 |
| 新槽重檢 | 至少兩次不同更新，避免游標已前進但仍讀到前一發資料 |
| 核心邏輯讀取預算 | 12,000 次／262,144 位元組；不是完整 Windows API 計數 |

快取限同次更新的發現結果；每次寫入仍重讀完整依賴。跨更新只保留槽號提示和排程狀態，不保留有效記憶體快照。游標增量也可能是探測距離，不能當發射數。待辦超限、游標超過一圈、過期與依賴變化時保守丟棄或重查，不以盲寫維持處理數量。

前三項排除霰彈／多彈丸，但依然有版本和候選核對成本。第四項包含多彈丸，更多投射物會放大檢查和原生碰撞負擔，**可能造成嚴重性能影響**。游標方案不代表零開銷、零卡頓或每顆都能趕在首次碰撞之前修改。

## 目前性能證據

使用者對 **P-11 0.2.3** 回報自療正常，場景 FPS 約 **70 → 130**。硬體、場景和量測方法未單獨記錄；此數字不歸屬 preview.8 的四種範圍，不用於封面或固定增幅宣傳。

之後使用者回報 **preview.8 四個選項正常可用**，未新增逐項 FPS 數據或完整負載矩陣。Lua 合成資料的讀取數、Arsenal 部署一致性及版本錨點通過，均不能代替遊戲 FPS。

遇到性能問題時，先完整退出遊戲，關閉其他重複自命中模組，改成 P-11 Only 並重新部署。記錄相同場景、武器、所選範圍、啟用前後 FPS／幀時間和相關日誌。第四項不適合把「全部包括」當成無條件預設。

## 重現離線檢查

在源碼根目錄安裝 requirements-dev.txt 後：

```powershell
python mods/projectile_collision_filter/test_runtime.py
python mods/projectile_collision_filter/test_cursor.py
```

測試包括延後生成、65 槽跨度、超限、槽位重用、拒寫後重查、前三項排除及 P-11 專用身份。測試不啟動 native addon 或遊戲。[驗證](VERIFICATION.md)

## English

The integrated core follows projectile allocation progress and performs bounded candidate checks, replacing the historical full 2,048-slot traversal. All four scopes share one addon. Pending hints are not cached ownership proof: fresh identity, dependency and writer checks remain mandatory.

At most 256 hints are pending, 128 slots are inspected and 64 writes attempted per update; hints expire after eight scheduling updates. Overload and timing can cause skipped shots. Including shotgun/multi-projectile types may cause severe performance impact. Zero overhead, zero stutter and modification before every first collision are not guaranteed.

The user's roughly 70-to-130 FPS report belongs to P-11 0.2.3. A later report confirms normal basic use of all four preview.8 choices without a new FPS benchmark. Synthetic counters are not frame-time measurements.
