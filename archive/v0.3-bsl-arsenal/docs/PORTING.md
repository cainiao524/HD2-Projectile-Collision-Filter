# 建置與版本移植 / Build and port

先讀 [AGENTS.md](../AGENTS.md) 和 [逐步接手指南](AGENT_GUIDE.md)。以下命令都以專案根為工作目錄；Toolkit 內為 `Source/HD2-Projectile-Collision-Filter/`。當前公開目標是 preview.8 / Toolkit 1.3.2。

## 模組建置與完整工具包不同

**輸入：** Python 3.10+、完整源碼。模組封裝使用標準庫，Lua mock 另需 requirements-dev.txt。

```powershell
python tools/sync_docs.py --apply
python tools/verify_secondary_catalog.py --check
python -m pip install -r requirements-dev.txt
python mods/projectile_collision_filter/test_runtime.py
python mods/projectile_collision_filter/test_cursor.py
python -m unittest discover -s tests -v
python tools/build_release.py --mods-only
python mods/projectile_collision_filter/test_package.py
```

**預期輸出：** `dist/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip`；四種 scope 的部署資源和已測 preview.8 指紋一致。`Rebuild-Mods.cmd` 是模組建置入口，不部署、不裝依賴、不推算新地址。診斷／包裝測試會在 build 或臨時目錄使用合成資料。

**繼續條件：** 每條命令退出 0、原始檔和匯出副本同步、套件測試通過。PowerShell 不會因上一條失敗而自動阻止下一條，請逐步確認。

完整 Windows x64 工具包另需：

```powershell
python -m pip install -r requirements-build.txt
python tools/build_release.py
python tools/release_manager.py verify
```

**預期輸出：** `dist/release/PUBLIC-ASSETS.json` 恰好列整合模組和 Toolkit 兩個 ZIP。源碼匯出在 `publication/P11-Enhanced/`，Toolkit 已展開 `Source/HD2-Projectile-Collision-Filter/`。一般玩家直接使用可攜 EXE 收集不需 Python；從源碼建置才需要。

**失敗處理：** 停在第一項失敗，修來源並重新建置，不直接改 ZIP／manifest／校驗逃過核驗。`--reuse-portable` 只允許來源、依賴和 EXE 指紋均符合的舊建置；否則完整重建。若需內部比較包，`python mods/projectile_collision_filter/build.py --local-standalones` 只產生本機 QA 輸入，不把它們加入公開 Release。

## 程式和版本入口

| 原始檔位置 | 職責 |
|---|---|
| `mods/projectile_collision_filter/` | core.lua 共用游標／分類／P-11 分支；entry.lua loader API 和回呼；version.lua 15 錨點；image_windows.lua／data_windows.lua 身份與兩位元組 guarded writer；build.py profile 與四選一包裝 |
| `maintenance/baselines.json`、loader-profiles.json、porting-map.json | 遊戲、loader、部署 Lua 與已記錄玩法範圍；候選定位和維修問題 |
| `maintenance/projectile-exclusions-25480438.json`、secondary-catalog-25480438.json | 霰彈／多彈丸排除來源、副武器槽位 catalog 及機制缺口 |
| `patches/25480438/manifest.json` | 離線比較／定位模式；不是 runtime 寫入授權 |
| `tools/offline_update.py`、maintenance.py、log_parser.py | 磁碟收集、四功能診斷、既有日誌與交接 |
| `tools/build_variants_release.py`、publication-files.json | 完整工具包、公開白名單、文件匯出和兩資產清單 |
| `tools/release_manager.py` | 本機 verify、明確 publish、遠端 verify-remote |

封裝和文案工作不得改已測 runtime。序列化 profile 中的候選旗標是建立當時狀態，新使用者證據寫在 maintenance 和文件，不能只為顯示成功改四份 Lua。真正移植新 build 另立版本和證據，不覆寫舊包。

## 遊戲更新後逐項核對

**輸入：** Toolkit 診斷包、同版源碼及受影響功能列表。以 porting-map 對照，不從舊聊天猜偏移。

1. 核對遊戲 EXE／DLL、loader API／內部版本及已部署 Lua。新四選項共用同一資源名稱，必須用精確指紋辨識 scope，不能由檔名判斷。
2. 重驗映像布局和 **15 錨點**（原 12 + 游標 3），分配游標、索引回繞和初始化順序。磁碟 PE 不直接等於載入映像。
3. 重驗本機玩家、來源 unit、武器登記、附件所有權、槽位 type／auxiliary／flags 及無執行權資料頁。
4. 保留寫前依賴重檢、只清 `0x20` 和寫後讀回。游標與快取不是寫入授權；新槽至少跨更新重查、超限和異常處理不可取消。
5. 每種方案保留 P-11 專用分支；第 2、3 項在來源查詢前排除霰彈／多彈丸及表外類型，第 4 項保留性能警告。
6. 更新版本位置、測試、離線基準、來源和文件，區分已取得證據、候選與缺口。無新玩法證據就保持未確認／候選。

**預期輸出：** 每個修改都能對應來源、指紋與欄位／時機證據。**繼續條件：** 沒有猜測位址成為可寫授權，原保護保留。**失敗處理：** 無法確認碰撞時機／身份時列出確切缺口，停止受影響功能；不新增遊戲內捕捉、不改成 hook／直接血量修改、不只換雜湊。

## 分類表重驗

```powershell
python tools/verify_secondary_catalog.py --check
$referenceTable = Read-Host '輸入固定 generated_projectile_settings.dl_bin 路徑'
python tools/verify_projectile_filter.py --table "$referenceTable"
```

固定霰彈參考為 350 筆／38 個排除 ID；副武器 catalog 的三表重驗命令見 [SECONDARIES](SECONDARIES.md)。以 LoadoutEntryComponentData／SidearmWeapon 判定，不用 AI EquipmentType。這些數量是固定參考，不是當前可取得武器或機制全支援。新資料需審查解析器、映射、proof 和未知條目，不只換雜湊。

## Arsenal 隔離核對

**輸入：** Node.js、本機合法取得並解包的 Arsenal 0.36.2（含 obfuscated_src/main 與 node_modules）。管理器不附在公開源碼。

```powershell
$arsenalSource = Read-Host '輸入已解包 Arsenal 0.36.2 應用資料夾'
$selectorZip = (Resolve-Path 'dist/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip').Path
node tests/test_arsenal_selectable.cjs "$selectorZip" "$arsenalSource" build/arsenal-validation/enabled
node tests/test_arsenal_selectable.cjs "$selectorZip" "$arsenalSource" build/arsenal-validation/disabled off
```

**預期輸出：** 隔離假遊戲 profile 的兩種匯入偏好、P-11 預選、16 種切換、父項／總開關停用、重新啟用與 purge 通過；每次部署內容與所選 archive 相同。它不操作真實 UI/profile 或遊戲，不證明長文顯示或玩法。**失敗處理：** 缺依賴記錄未執行，不以一般 Python 測試冒充通過。實際 UI 檢查另確認中英長標籤、換行和第四項警告可讀。

完成後按 [發布指南](PUBLISH.md) 處理兩項資產，以 [交接模板](HANDOFF_TEMPLATE.md) 記錄所有執行／未執行檢查。
