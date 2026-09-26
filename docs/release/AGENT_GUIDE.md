# AI／Agent 與維修者逐步接手指南

先讀根 [AGENTS.md](../AGENTS.md)。目前為 preview.8 / Toolkit 1.3.2，四選一單 addon、兩個公開 ZIP；四項有使用者正常回報，仍維持預覽與機制限制。

副武器、霰彈分類或 FileDiver 資料工作另讀 [FileDiver 逐步教程](FILEDIVER_HANDOFF.md)。教程包括固定三表取得／重播、彈頭排除核對、收集器格式限制及新 build 移植；目前的「手槍全部」仍排除霰彈／多彈丸，完整分類不等於所有機制已支援。

## 0. 確认根目錄與任務

**輸入：** GitHub checkout，或解壓工具包 `Source/HD2-Projectile-Collision-Filter/`；移植時另備本機診斷資料。

**操作：** 進入有 AGENTS.md、mods、tools、publication-files.json 的資料夾。按 [安裝](SELECTABLE.md)、[原理](VARIANTS.md)、[驗證](VERIFICATION.md) 分辨文案／包裝、部署問題還是新 build 移植。用 [交接模板](HANDOFF_TEMPLATE.md) 記錄提交、版本、目標、證據與缺口。

**預期輸出／繼續條件：** 確认修改來源與 runtime 保留要求。文件編輯 docs/release，再以 `python tools/sync_docs.py --apply` 匯出；源碼和副本一起提交。**失敗處理：** 缺源碼取得同一 Release 工具包或源碼，缺診斷進入第 1 步；不用舊聊天猜偏移或私人路徑。

## 1. 一次收集可取得的離線資料

**輸入：** 更新、部署已結束的遊戲與 loader，Toolkit 1.3.2，已有的套件和參考資料。

**操作：** 在完整解壓工具包外層雙擊 `Collect-HD2-Update.cmd`。找不到／多份安裝時明確指定：

```powershell
$gameDirectory = Read-Host '輸入 Helldivers 2 安裝資料夾'
.\P11-Update.exe --game "$gameDirectory"
```

源碼入口為 `python tools/offline_update.py`；相同參數，另可重複 `--package`、`--schema-dir`，見 [工具指南](UPDATE_TOOL.md)。不要求遊戲內捕捉。

**預期輸出：** `diagnostics/latest.json` 指向新的診斷資料夾和 ZIP，有摘要.md、report.json、維修交接.md、porting-map.json。退出 0 是穩定完整收集，2 是不完整／錯誤；不是玩法結論。

**繼續條件：** 先讀 complete／errors，再看 build、deployed、feature_assessment、profiles、schema_sources、gaps。五份安裝表和快取分別保留來源，完整收集也可能有分析缺口；observed build 不會自動證明 matches_game_build。

**失敗處理：** 更新中等完成後重收；缺檔列出並取得正確安裝檔，不用舊副本冒充新版本；先處理部署衝突和 loader 不相容。原始診斷留本機。

## 2. 判讀：身份、部署和玩法分開

**輸入：** 診斷包與同版源碼。**操作：** 精確比對遊戲、loader 和部署 Lua。新四個 scope 共用資源名，用精確 Lua 指紋識別實際選項；不能僅匹配遊戲 build 就套用舊 P-11 成功基準。

| 結果 | 操作／繼續條件 | 失敗處理或界限 |
|---|---|---|
| collection_incomplete | 解決 errors 後重新收集 | 不使用不完整證據判定可用 |
| matches_confirmed_baseline | 保留該基準記錄的基本使用範圍，核對部署／loader／衝突 | 不表示當次遊戲已成功 |
| matches_unverified_candidate | 保持候選，檢查對應資料位置 | 不把指紋吻合當玩法確認 |
| port_candidates_available | 記錄候選依據並逐項審查 | 候選地址不是寫入授權 |
| offline_evidence_insufficient | 明列缺檔、受阻功能和下一份可取得資料 | 不猜偏移、不換 hash、不改 hook |

**預期輸出：** 各功能有證據、缺口和下一步。未選範圍 not_deployed 可以正常；舊日誌只證明當時事件，activated／readback 不是原生命中。**失敗處理：** 對加密 DLL、所有權或碰撞時機不足保留具體未決問題，受影響功能停用／候選。

資料表工作先做 [FileDiver 教程第 1–4 步](FILEDIVER_HANDOFF.md)：catalog 的 `--check` 沒有讀原始三表；完整 replay 仍不會把 `matches_game_build` 或 `gameplay_verified` 改成 true。`.gz` 可交給三表校驗器，但離線收集器不會自動解壓或遞迴收集，必須按其檔名白名單提供來源。

## 3. 移植與保護

**輸入：** 上一步逐項證據和影響清單。**操作：** 按 [PORTING](PORTING.md) 核對 15 錨點、分配游標／回繞／初始化、玩家／武器／附件鏈、槽位和 guarded writer。所有範圍共用核心與 P-11 分支，不加回歷史第二 addon。重新核對霰彈表和副武器槽位 catalog；[SECONDARIES](SECONDARIES.md) 的 beam／spray／entity 缺口不能只靠來源 hash 消除。

**預期輸出：** 可審查差異，每項有來源／指紋和測試，新 build 另立版本。**繼續條件：** 身份、所有權、原值、有效頁面、寫前重檢、寫後讀回和有限排程全部保留。**失敗處理：** 保持未證明功能停用／候選；不放鬆保護換取效果、不改全域定義／血量、不新增 native hook。

本次 preview.8 發布只改包裝和文件，四份已測 runtime 必须完全不變；嵌入 profile 的舊候選旗標保留，後續使用者證據另存 maintenance/evidence 和文件。

## 4. 驗證與建置

**輸入：** 完整源碼、Python 3.10+；Lua 依賴 requirements-dev.txt。**操作：** 按 [PORTING](PORTING.md) 逐條執行 sync、catalog、runtime、cursor、Python tests、mods-only、package 檢查。需要完整工具包時加 requirements-build.txt，再完整 build_release 和 release_manager verify。

**預期輸出：** 模組建置產生一個整合 ZIP；完整建置產生兩資產 PUBLIC-ASSETS.json 與 Windows Toolkit。內部四獨立 QA 包不公開。**繼續條件：** 資源固定指紋一致、測試通過、兩檔核驗通過；Arsenal 隔離檢查與實際 UI 顯示分別記錄。

**失敗處理：** 停在首個失敗並修來源，不直接改輸出過關。缺 Arsenal 外部依賴就記錄未執行。Windows EXE 在無 Python PATH 下測試收集入口；乾淨公開 checkout 與工具包 Source 各走一次流程，確認沒有私人檔案依賴。

## 5. 發布和交接

**輸入：** 通過核驗的兩 ZIP、乾淨已提交源碼、雙語 Release 正文、既有發布授權。**操作：** [PUBLISH](PUBLISH.md) 的本機 verify → publish → verify-remote，下載回來核對大小、SHA-256、tag 提交；保留 prerelease。舊標籤／資產不刪，頂部加歷史導航。

**預期輸出：** Release 恰好兩個手動 ZIP；工具從已驗資產產生 SHA-256 表，不能先把 Toolkit 自身最終 hash 寫回其源碼造成循環。GitHub 自動 Source code 另保留。

**繼續條件：** 遠端核驗通過。**失敗處理：** 部分上傳中斷先讀實際遠端狀態，按 PUBLISH 只補缺少檔案；不另建假成功版本、不刪歷史、不批量上傳 dist。既有授權涵蓋的工作不重複詢問。

交付填完模板：提交／版本、改動、執行與未執行檢查、使用者玩法範圍、缺口、資產連結和下一個步驟。不得上傳遊戲二進位、完整表、私人日誌／診斷或本機帳號路徑。
