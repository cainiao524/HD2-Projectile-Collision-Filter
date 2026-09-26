# 建置與版本移植

先讀 [AGENTS.md](../AGENTS.md) 和 [逐步接手指南](AGENT_GUIDE.md)。以下命令均從源碼根目錄執行；工具包內是 `Source/P11-Enhanced/`。

## 環境與建置

模組封裝只需 Python 3.10+ 標準庫。Lua mock 需要 Lupa；用專案鎖定依賴安裝：

```powershell
python tools/sync_docs.py --apply
python -m pip install -r requirements-dev.txt
python mods/p11_self_hit_dataonly/test_lua.py
python mods/weapon_self_hit_candidate/test_lua.py
python -m unittest discover -s tests -v
python tools/build_release.py --mods-only
```

每條命令成功才執行下一條。五個模組 ZIP 位於 `dist/`：四個獨立版和四選一整合版。雙擊 `Rebuild-Mods.cmd` 等同模組封裝入口，不安裝依賴、不推算新地址、不部署。它可能更新對應 baseline 指紋，須檢查版本控制差異。

完整六檔 Release 需 Windows x64：

```powershell
python -m pip install -r requirements-build.txt
python tools/build_release.py
python tools/release_manager.py verify
```

輸出在 `dist/release/`；`PUBLIC-ASSETS.json` 是唯一發布清單。新版固定五個模組 ZIP 加 Toolkit 1.3.0 ZIP；源碼直接納入工具包，不另發來源或 Full Kit。完整建置會匯出 `publication/P11-Enhanced/`；`--reuse-portable` 只接受來源與 EXE 雜湊均吻合的舊建置，依賴改了就重建。

## 檔案與依據

| 位置 | 職責及移植時要核對的內容 |
|---|---|
| mods/p11_self_hit_dataonly | 原 P-11；profile.json、version.lua、core.lua、data_windows.lua、image_windows.lua、entry.lua 及 build.py |
| mods/weapon_self_hit_candidate | 三個擴展共用 core／writer／version／entry；build.py 產生各範圍並嵌入原 P-11 |
| tools/build_selectable_mod.py | 四個完整 archive 的 Arsenal 互斥選项、固定身份與首次預選 |
| maintenance/baselines.json | 已知遊戲／套件指紋、四項功能及證據範圍 |
| maintenance/loader-profiles.json | 已知 loader 公開版本、API、內部版本及識別依據 |
| maintenance/porting-map.json | 目前布局、所有權鏈與必要核對項目 |
| maintenance/projectile-exclusions-25480438.json | 固定參考表的來源指紋、38 個排除 ID 與分類依據 |
| patches/25480438/manifest.json | 離線版本比較與定位模式；不能當 runtime 寫入授權 |
| tools/offline_update.py／maintenance.py | 收集、四項功能比較與維修交接；收集器版本在 maintenance.py |
| tools/build_variants_release.py／publication-files.json | 可攜工具、六檔包裝、公開來源白名單、文件匯出 |
| tools/release_manager.py | 本機 verify、明確 publish、遠端 verify-remote |

新增公開來源／文件後必須更新 publication-files.json。所有當前文件在 docs/release 修改；對外根 README、docs 和 releases 是生成副本，執行 `python tools/sync_docs.py --apply` 更新，檢查生成差異後與原始檔一起提交。`python tools/sync_docs.py --check` 只驗證同步。已有獨立修改的追蹤副本會被拒絕覆寫，先比較並合併回來源；被替換的舊內容備份於忽略的 build/docs-sync-backup。原 P-11 包內 README／VALIDATION／profile 是歷史封裝輸入，不為了新版文件改動。

## 保留成功包

P-11 原始 ZIP SHA-256：
`73c8c1e85b9732b85e0324b45b19d2c8b6c104abcd394c0f82ac49b67f9da8c2`。

四種方案中的 P-11 Lua SHA-256：
`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。

文件／包裝更新必須重現四個原独立 ZIP。真正移植新 build 時保留舊版證據與成品，另建新版本／基準，重新審查 builder 的原包固定指紋保護，不能偷偷把舊版指紋替換成新值。P-11 位元組相同也不能證明新包中的原生共存或新版遊戲行為。

## 遊戲更新移植核對

版本常數分散在 profile、core、writer、version、builder；只修改 baseline 或雜湊不會形成有效移植。以診斷包和 porting-map 逐項確認：

1. EXE／DLL 身份、載入映像布局和 12 個原有指令錨點；磁碟 PE 不直接等於載入後布局。
2. 本機玩家、武器登記、來源／附件所有權、投射物類型與槽位有效性。
3. 來源碰撞排除位元、原旗標、寫入區域非執行／有效、每次寫前重檢及讀回。
4. 擴展仍排除 P-11；手槍 ID 清單和原生投射物機制覆蓋各自驗證。
5. 前三範圍排除霰彈；第 2、3 項先按彈種排除，再查來源／武器；表外類型跳過。
6. 比對原成功證據與新候選證據，更新測試及文檔；沒有新版玩法證據就保留候選狀態。

不能由離線資料確認碰撞生效時機或所有權時，明列缺口並保持受影響功能停用／候選。不要求新的遊戲內捕捉，不退回 native hook、不改生命／體力等數值。mock 不啟動遊戲，不能證明 native 碰撞或並行原子性。

## 霰彈資料表核對

先讀 maintenance/projectile-exclusions-25480438.json 的來源網址、提交、SHA-256、布局與分類。取得對應本機參考表後，在源碼根目錄執行：

```powershell
$referenceTable = Read-Host '輸入 generated_projectile_settings.dl_bin 完整路徑'
python tools/verify_projectile_filter.py --table "$referenceTable"
```

此命令只核對本機表，不下載、不修改遊戲。未知新表不能只換雜湊讓舊數字通過；需重新推導映射、全部多彈丸記錄、已知霰彈及 P-11 例外。目前表共 350 筆，38 個排除 ID；第 2、3 項跳過表外類型，第 4 項保留 1..4096 候選範圍。分類證據不等於當前玩法確認。

## Arsenal 隔離封裝測試

需 Node.js 和本機已解包的 Arsenal 0.36.2 應用內容，含 obfuscated_src/main 與 node_modules。這些管理器檔案不附在公開源碼中；缺依賴時明確記錄未執行，不把一般 Python 測試當替代。

在源碼根目錄使用剛建置的選擇包：

```powershell
$arsenalSource = Read-Host '輸入已解包 Arsenal 0.36.2 應用資料夾'
$selectorZip = (Resolve-Path 'dist/Projectile-Collision-Filter-v0.3.0-preview.5-build25480438.zip').Path
$isolatedChecks = Join-Path (Get-Location) 'build/arsenal-validation'
node tests/test_arsenal_selectable.cjs "$selectorZip" "$arsenalSource" "$isolatedChecks/enabled"
node tests/test_arsenal_selectable.cjs "$selectorZip" "$arsenalSource" "$isolatedChecks/disabled" off
```

測試使用全新隔離 profile／假遊戲目錄，檢查兩種匯入啟用偏好、首項預選、十六種切換、父項／模組停用、重新啟用及清除；部署 archive 必須與所選獨立包吻合。它不操作真實 UI、profile 或遊戲，不代表玩法共存驗證。

完成後依 [發布指南](PUBLISH.md) 核驗六項資產，並用 [交接模板](HANDOFF_TEMPLATE.md) 記錄所有已執行和未執行的檢查。
