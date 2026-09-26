# FileDiver：副武器、彈頭分類與更新交接

先讀 [AGENTS.md](../AGENTS.md) → [Agent 接手指南](AGENT_GUIDE.md)，再按本頁核對離線資料。本文適用於 preview.8 / Toolkit 1.3.2 的現有工具；命令在有 `publication-files.json` 的專案根目錄執行，使用 Python 3.10+ 和 PowerShell。

## 先分清楚要解決的問題

[FileDiver](https://github.com/xypwn/FileDiver) 是 Helldivers 2 資產提取工具；本專案已引用其固定提交的資料表與結構，作為副武器分類和霰彈排除的離線參考。FileDiver 不是模組 runtime 的依賴，本專案收集器也不會自動執行或下載它。若另用其 GUI／CLI 提取資產，依[上游 CLI 文件](https://github.com/xypwn/filediver/wiki/10-CLI-Basics)及該版本的 `filediver -h` 選擇參數，記錄使用的版本、參數和輸出來源；不要假設任意版本都能輸出本頁要求的表，也不要虛構 datalibrary 匯出選項。

| 任務 | 可取得的證據 | 仍不能據此宣稱 |
|---|---|---|
| 列出副武器 | 裝備槽位 → 武器 entity／unit → 發射元件 | 每一把目前可取得，或每一種機制已支援 |
| 排除霰彈 | 彈頭類型、發射數、命名與武器引用 | 單彈丸一定不是霰彈；霰彈副武器可以繞過排除 |
| 更新後比較 | 新舊來源、結構、引用和分類差異 | 新遊戲的 runtime 偏移、所有權鏈或碰撞時機已確認 |
| 減少重複分類成本 | 在開發時建立固定查表資料 | 零開銷，或不再需要驗證實際生成的投射物 |

目前效果仍由 runtime 在身份與本機所有權檢查後清除原生投射物的 `0x20` 來源碰撞排除位元，再由真實命中觸發原生效果。固定彈頭定義的旗標不能直接代替這個生成後狀態；沒有證据時，不宣稱靜態表修改已解決自命中或碰撞前生效時機。

## 1. 固定基準與資料來源

**輸入：** 同版源碼與本機診斷包。**操作：** 先核對下列來源；不要用 FileDiver 的 `master` 或另一個遊戲 build 的快取覆蓋舊基準。

| 檔案 | 角色 |
|---|---|
| `maintenance/secondary-catalog-25480438.json` | FileDiver 提交、三表 URL／解壓後大小／SHA-256、名稱來源、27 筆副武器槽位記錄與證據 |
| `maintenance/projectile-exclusions-25480438.json` | 彈頭表 URL／SHA-256、38 個排除類型、舊命名表來源指紋及 P-11 例外 |
| `tools/verify_secondary_catalog.py` | 固定三表的解析／proof 核對，不是通用新版本產生器 |
| `tools/verify_projectile_filter.py` | 固定彈頭表的排除事實核對，不是新表自動移植器 |

現有參考提交為 `bf0ce329db3cf0043994eb717ea86433c303cb36`。catalog 的 `target_build: 25480438` 是目標標籤；`matches_game_build: false` 明確表示尚未證明目標安裝的加密資料等同這份明文參考。`gameplay_verified: false` 也不因離線核對成功而改變。

**預期輸出／繼續條件：** 交接記錄分別列出遊戲指紋、FileDiver 提交、資料檔指紋、來源種類、加密／壓縮狀態及版本對應證據。**失敗處理：** 來源或對應不明，標為參考／缺口；不可用時間、檔名、大小接近或能解析來推定同版。

## 2. 重驗現有副武器分類

### 2A. 先核對附帶 catalog

**輸入：** 源碼即可。**操作：**

```powershell
python tools/verify_secondary_catalog.py --check
if ($LASTEXITCODE -ne 0) { throw '副武器 catalog 核對失敗；先處理錯誤。' }
```

**預期輸出：** `ok: true`、`raw_reference_replayed: false`；27 個副武器記錄、20 個已辨識可射擊記錄、16 個擴展 runtime 來源候選。排除 Bushwhacker 後的目標參考集合為 19 個，包含由專用分支處理的 P-11。數字不是目前可取得武器數，也不是已生效武器數。

**繼續條件：** 退出 0。**失敗處理：** 退出 2 時讀 `error`；修復源碼／catalog 不一致或缺檔，不改常數跳過 proof。

### 2B. 取得並重播固定原始三表

**輸入：** catalog 指定的三份明文表或 `.gz`。已有正確本機檔案可跳過下載，直接把下方三個參數改為其路徑。

**操作：** 以下是維護者主動執行的可選網路下載，與日常「離線收集」分開。只下載 catalog 已固定的 URL 到被 Git 忽略的 `build/`，不放進公開源碼清單。

```powershell
$referenceDirectory = Join-Path 'build' 'filediver-pinned-reference'
New-Item -ItemType Directory -Force -Path $referenceDirectory | Out-Null
$catalog = Get-Content 'maintenance/secondary-catalog-25480438.json' -Raw | ConvertFrom-Json
foreach ($source in $catalog.sources.PSObject.Properties) {
    $referenceFile = Join-Path $referenceDirectory ($source.Name + '.gz')
    Invoke-WebRequest -Uri $source.Value.url -OutFile $referenceFile -ErrorAction Stop
}
python tools/verify_secondary_catalog.py --entities "$referenceDirectory/generated_entities.dl_bin.gz" --schema "$referenceDirectory/dl_library.dl_typelib.gz" --deltas "$referenceDirectory/generated_entity_deltas.dl_bin.gz"
if ($LASTEXITCODE -ne 0) { throw '固定三表重播失敗；不可當成有效來源。' }
```

**預期輸出：** `ok: true`、`raw_reference_replayed: true`，但 `matches_game_build` 和 `gameplay_verified` 仍為 false。校驗器會解壓 `.gz`，以明文長度／SHA-256 及重建的 proof 核對；不能拿壓縮檔 hash 與 catalog 的明文 hash 直接比較。

**繼續條件：** 三個參數一起提供，退出 0。**失敗處理：** 下載失敗、加密安裝表、錯誤指紋、缺少任一表或 proof 不一致都要保留具體錯誤。不要修改 hash 讓舊解析器接受新表。此步不需要安裝 FileDiver、Go 或啟動遊戲。

## 3. 重驗霰彈／多彈丸排除

**輸入：** 排除表指定的未壓縮 `generated_projectile_settings.dl_bin`。**操作：** 已有本機檔案時直接指定 `--table`；需要取得固定參考時可執行：

```powershell
$referenceDirectory = Join-Path 'build' 'filediver-pinned-reference'
New-Item -ItemType Directory -Force -Path $referenceDirectory | Out-Null
$exclusions = Get-Content 'maintenance/projectile-exclusions-25480438.json' -Raw | ConvertFrom-Json
$projectileTable = Join-Path $referenceDirectory 'generated_projectile_settings.dl_bin'
Invoke-WebRequest -Uri $exclusions.table_source.url -OutFile $projectileTable -ErrorAction Stop
python tools/verify_projectile_filter.py --table "$projectileTable"
if ($LASTEXITCODE -ne 0) { throw '彈頭排除事實核對失敗；保留錯誤及來源。' }
```

**預期輸出：** 38 個排除類型、32 個多彈丸類型、`offline_table_verified: true`、`gameplay_verified: false`。`p11_excluded_from_filter: true` 的意思是 P-11 不在排除清單中，四種 scope 仍含 P-11。

**繼續條件：** 退出 0，350 筆固定記錄的結構／指紋與 P-11 type 318 核對通過。**失敗處理：** 此工具只接受未壓縮表，失敗可能為 traceback／非零退出碼，不保證與副武器工具一樣退出 2。不要使用 `python -O`，因現有檢查使用 assert。

排除策略同時包含「已辨識的霰彈類型」和「多彈丸類型」；不能改成只判斷彈丸數大於 1。`All Sidearms` 仍排除 Bushwhacker 等霰彈副武器；前三項排除，第 4 項保留包含霰彈與雙語性能警告。

## 4. 把本機參考資料納入離線診斷

**輸入：** 更新完畢的遊戲安裝、已取得的未壓縮參考資料資料夾。收集器會記錄安裝中的五表：entities、entity_deltas、typelib、weapon_customization_settings、projectile_settings；完整檔名見 `tools/offline_update.py` 的 `INSTALLED_SCHEMA_NAMES`。

**操作：** 在源碼根目錄執行；`--schema-dir` 可重複指定不同來源資料夾，不要混放不同版本：

```powershell
$gameDirectory = Read-Host '輸入 Helldivers 2 安裝資料夾'
$schemaDirectory = Read-Host '輸入已有未壓縮參考表的資料夾'
python tools/offline_update.py --game "$gameDirectory" --schema-dir "$schemaDirectory" --output diagnostics
```

無 Python 的使用者，在完整工具包外層使用 `P11-Update.exe` 加相同參數，或日常雙擊 `Collect-HD2-Update.cmd`。手動參考目錄可放入自己的 `local-settings.json` 的 `schema_dirs` 陣列，不能提交該私人設定檔。

**預期輸出：** `diagnostics/latest.json` 指向診斷 ZIP；`report.json` 的 `schema_sources` 區分 `installed_game_data` 和 `local_cache`。額外來源可來自 `--schema-dir`、本機設定、`reference-data/` 和既有 Go module cache；不會啟動 FileDiver，也不會下載資料。

**繼續條件：** 先讀 `complete`／`errors`，再看 `schema_sources`／`gaps`。`--schema-dir` 不遞迴搜尋，只收指定目錄直接下、符合白名單的檔名；應指定實際含表的資料夾。三表校驗器能接受 `.gz`，收集器卻不會自動解壓 `.gz`，名稱字典也不在其表格收集白名單。需要時在本機解壓到獨立來源目錄，記錄壓縮來源及解壓後 hash。

**失敗處理：** 缺表、仍在更新、來源加密或版本不符，逐項寫入交接。收集退出 0 只表示穩定收集完成；即使完整，也可能缺少可解析明文、武器自訂映射或版本對應。離線工具不讀程序、不部署、不上傳；不得以新增遊戲內捕捉補這些缺口。

## 5. 遊戲更新後的人工分析順序

**輸入：** 舊固定參考、新版本本機資料、FileDiver／解析器版本及診斷結果。**操作：**

1. 分別保留新舊檔案及 hash，先確認資料可解析及來源，不覆寫舊成功基準。
2. 以 `LoadoutEntryComponentData` 的 `LoadoutItemType=3` 找副武器，追到 entity／unit；不能用 AI `EquipmentType`、武器名字或外觀代替裝備槽位。
3. 解析基底及 delta，逐筆記錄 Projectile／Beam／Spray／Arc 或無已知射擊元件。未知項不能直接刪除；基底 projectile type 0 需追武器自訂／附件引用，不能當成實際彈種。
4. 建立「副武器槽位 → 武器 → 發射機制 → 實際彈頭／entity → 霰彈排除」對照，列出新增、移除及改變的引用。核對已命名霰彈、多彈丸與所有匹配變體，保留 P-11 專用分支。
5. 分開記錄分類結果、程式處理路徑及玩法證據。Dagger beam、Crisper spray 目前未支援；Warrant／P33／Hornet 的 entity 後續鏈未完成，新增來源 hash 不會補上碰撞實作。榴彈本體命中與爆炸／範圍效果也要分開。
6. 遇到 runtime 版本、游標、15 錨點、物件有效性或碰撞時機問題，按 [PORTING](PORTING.md) 的證據要求处理；FileDiver 靜態表不能單獨證明這些條件。未決項列出所需資料，保持停用／候選，不改 native hook 或生命值。

**預期輸出：** 可審查的新舊差異表，以及每個未完成機制的具體缺口。**繼續條件：** 新來源、解析器、分類政策及證據可重現後，才提出新版本程式／設定變更。**失敗處理：** 現有兩個校驗器是固定基準重播工具，不支援任意新 build 自動重建；先擴充並審查解析和測試，不能只更新預期 hash 或複製舊偏移。

## 6. 修改來源、驗證與交接

| 變更內容 | 要核對的原始檔／入口 |
|---|---|
| 副武器來源與 proof | `maintenance/secondary-catalog-25480438.json`、`tools/verify_secondary_catalog.py`、`tests/test_secondary_catalog.py`；新 build 保留舊檔並新增版本依據 |
| 霰彈類型與來源 | `maintenance/projectile-exclusions-25480438.json`、`tools/verify_projectile_filter.py`，以及 builder 實際使用的 profile 產生路徑 |
| 分類如何進入已部署 Lua | `mods/projectile_collision_filter/build.py` 的 profile 組裝與其匯入的 builder、`core.lua` 的 scope／排除檢查；只改 JSON 不代表 runtime 已改 |
| 版本、定位與診斷 | `mods/projectile_collision_filter/version.lua`、`maintenance/porting-map.json`、`maintenance/baselines.json`，按實際改動同步，不能以已知表代替 runtime 證據 |
| 說明與交接 | `docs/release/SECONDARIES.md`、本頁、`AGENT_GUIDE.md`、`HANDOFF_TEMPLATE.md`；根 `AGENTS.md` 直接編輯 |

**操作：** 文件改 `docs/release/`，執行 `python tools/sync_docs.py --apply` 再 `--check`；新公開文件加入 `publication-files.json` 的 files／document_exports。按照 [Agent 指南第 4 步](AGENT_GUIDE.md#4-驗證與建置)檢查實際受影響的程式。文件更新不需要重建或覆蓋已發布 ZIP；新版 Toolkit 的 Source 會按公開清單帶入新教程，已發布 1.3.2 仍是其原始快照。

**預期輸出／繼續條件：** 提交包括編輯來源、生成副本和公開清單；記錄本次執行與未執行的命令、退出碼、固定三表是否重播，以及仍為 false 的版本／玩法證據。既有 preview.8 已測 runtime 不因文件更新而改寫；真正移植另建版本、完成回歸並維持資料寫入保護。

**失敗處理：** 停在首個不一致並修正來源，不手改生成副本或成功包。只發布必要識別值、來源及分析摘要；原始遊戲表、遊戲 EXE／DLL、私人診斷／日誌與本機絕對路徑留本機。將下一位 Agent 所需的具體輸入和下一條命令填入 [交接模板](HANDOFF_TEMPLATE.md)。
