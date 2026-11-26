# 「手槍全部」：副武器分類與機制支援 / Secondary Coverage

**本頁對應 v0.3.0-preview.8 預覽版，沿用 preview.6 的固定分類依據；四項基本成功回報不提高逐武器機制證據。「全部可射擊副武器」是功能目標；目前只具備部分原生投射物路徑，並未完成全部機制。** GitHub 主要下載為 [preview.8](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8)。[歷史 preview.5](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.5) 保留舊的有限手槍識別清單、正文及資產。

## 目標範圍與判定來源

Arsenal 雙語選項為「All Sidearms / 手槍全部」。開發目標是裝備槽位中**全部可射擊副武器**，包含一般彈丸、電漿、榴彈、雷射及噴射武器；霰彈與多彈丸繼續按使用者要求排除，P-11 由共用單一 addon 內的專用身份分支處理。

副武器身份以固定版本的裝備槽位資料及其武器資源關聯為依據，不以名稱中的「Pistol」或外觀猜測。參考資料以 `LoadoutEntryComponentData` 的 `LoadoutItemType=3`（SidearmWeapon）判定副武器槽位；`EquipmentType` 是 AI 分類，不能代替裝備槽位。分類完整也不能證明遊戲機制已支援。

來源入口：

- `maintenance/secondary-catalog-25480438.json`：副武器 catalog、来源指紋、資源關聯、排除與機制狀態；清單及統計以完成核對的內容為準。
- `tools/verify_secondary_catalog.py`：核對完整固定參考 roster 與來源指紋；`--check` 核對附帶 catalog，可另提供三份固定原始資料重做解析比對。此工具不下載、不讀程序、不寫檔或自動產生新版本。
- `maintenance/projectile-exclusions-25480438.json`：目前霰彈／多彈丸排除依據。副武器屬性不能繞過這份排除規則。

目前參考資料固定於 Filediver 提交 `bf0ce329db3cf0043994eb717ea86433c303cb36`。它的副武器槽位共有 **27 個記錄**，其中 **20 個帶 Projectile／Beam／Spray／Arc 射擊元件**；其餘 7 個分類為 `no_known_firing_component`，包含 6 個已命名近戰資源及 1 個含 MeleeAttack 元件的未命名記錄。這不代表這些資源在任何版本永遠不可射擊。排除 Bushwhacker 後，目標參考集合為 **19 個已辨識可射擊副武器記錄，包含 P-11**。

這 19 個記錄分為：P-11 專用分支處理、16 個擴展原生／entity 來源 hash 候選、Dagger beam 和 Crisper spray 兩個未支援機制。**16 個 lookup hash 不等於 16 把武器均可生效**；其中的 entity 後續鏈仍有缺口。

以上數量只描述該固定參考資料，不表示目前遊戲實際可取得／已上架武器完整性。三份資料表與兩份名稱參考的來源網址、大小和 SHA-256，以及各記錄的偏移／差量證據，完整保留在 [catalog](../maintenance/secondary-catalog-25480438.json)。Hornet Pistol 僅辨識到內部資源名，正式名稱與可取得狀態未確認。目標安裝的加密包裝檔尚未建立直接內容／雜湊對應，`matches_game_build` 保持 false，不能因大小相近就視為同版明文資料。

## 完整固定參考清單

下表由 catalog 的 27 筆記錄整理。名稱可以是內部名稱；不代表目前可解鎖、已正式推出或已有玩法驗證。資源欄一般為 entity＝unit；不同時另列 unit。

| 參考名稱 | 資源識別值 | 資料機制 | 本次狀態 |
|---|---|---|---|
| P-2 Peacemaker | 05e4e5c2db6e44a2 | Projectile；基底 type 0，待自訂／附件解析 | 原生槽位候選，玩法未驗證 |
| P-35 Re-Educator | 0b882808c6f498e8 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| P-33 Missile Pistol（內部名稱） | 14d5d4506056c7a4 | Projectile；entity 分支 | 僅收錄來源；entity 後續處理未完成 |
| P-113 Verdict | 1a437158e1b8d2a1 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| SG-22 Bushwhacker | 2b28e17ffed05f7c | Projectile；基底 type 0，待自訂／附件解析 | 按霰彈策略排除 |
| 未命名副武器項目（含近戰組件） | 2ec9cd598e31930f；unit 64cdb52aca152be1 | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |
| P-19 Redeemer | 3575aabc5f1f9326 | Projectile；基底 type 0，待自訂／附件解析 | 原生槽位候選，玩法未驗證 |
| P-72 Crisper | 3f92ba65ef65cca9 | Spray | 目前未支援此機制 |
| LAS-58 Talon | 416d053372c4e433 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| M6C SOCOM Pistol | 4d58c77087b774c5 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| CQC-30 Stun Baton | 52cdbfbaca3cb397；unit c5793b23852109f0 | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |
| GP-31 Grenade Pistol | 52e4334e6a128caf | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| CQC-5 Combat Hatchet | 75816077c139c850 | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |
| CQC-42 Machete | 792d5d2a340fd6e6 | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |
| LAS-7 Dagger | 7b06196e90154c88 | Beam | 目前未支援此機制 |
| Entrenchment Tool（內部資源） | 7e1f76163c667e4b | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |
| P-4 Senator | 8d3d52a3b2f19402 | Projectile；基底 type 0，待自訂／附件解析 | 原生槽位候選，玩法未驗證 |
| GP-20 Ultimatum | 9eb160830321bfd6 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| PLAS-15 Loyalist | aa69a60d74a3ec54 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| P-41 Ombudsman | bde1f2534280300d | Projectile；基底 type 0，待自訂／附件解析 | 原生槽位候選，玩法未驗證 |
| P-69 Veto | c780bcd79547da0f | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| P-92 Warrant | cf8934ff6567a42d | Projectile；entity 分支 | 僅收錄來源；entity 後續處理未完成 |
| P-11 Stim Pistol | d6b1fb05b9109353 | Projectile；原生候選 | 共用核心內的 P-11 專用分支；四項基本成功回報 |
| P/40-K Bolt Pistol | dbb6c961c59fadc1 | Projectile；原生候選 | 原生槽位候選，玩法未驗證 |
| CQC-19 Stun Lance | e3b6aedd07fcb464 | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |
| Hornet Pistol（內部資源名稱，正式名稱未確認） | e91f569c2ad8af01 | Projectile；entity 分支 | 僅收錄來源；entity 後續處理未完成 |
| CQC-2 Saber | fcd8a6e67eac635a | no_known_firing_component | 未辨識射擊元件，不纳入本次射擊範圍 |

基底 Projectile type 0 不代表實際發射的彈種是 0，仍需武器自訂／附件解析。entity 來源加入 lookup 也沒有新增 entity 後續碰撞處理；只有實際符合現有原生槽位與全部保護的情況才可能進入候選路徑。

## 三件必須分開的事

| 層次 | 可證明什麼 | 不能證明什麼 |
|---|---|---|
| 副武器分類 | 武器由資料中的副武器槽位引用，是否可射擊及是否按策略排除 | 自命中效果已實現 |
| 機制與程式路徑 | 哪種投射物／碰撞路徑可被目前程式識別與處理 | 實際命中、傷害、治療或副效果正常 |
| 遊戲玩法證據 | 特定版本、武器、場景下觀察到的行為 | 其他武器、主客機、碰撞時機與未來版本也成功 |

新增一把武器 ID 到清單，只能擴大「准許辨識」範圍。若它不使用現有原生投射物槽位，修改這個槽位的 `0x20` 位元不會自動支援它。

## 目前按機制的狀態

| 武器／機制 | 目前狀態 | 還缺什麼 |
|---|---|---|
| P-11 原始治療飛鏢 | 已測 preview.8 的 P-11 專用分支；本次保留其 Lua／資源 | 原驗證記錄以外的共存、主客機與時序覆蓋 |
| 通過身份與所有權檢查的原生單投射物副武器 | 部分資料修改候選路徑 | 完整槽位清單核對及各武器實際自命中證據 |
| 電漿／榴彈 | 依實際資料判定路徑，不憑名稱直接算成支援 | 原生／entity 路徑、直接碰撞與後續效果各自的依據 |
| Dagger 的 beam | **目前未支援** | 光束自身的來源排除及碰撞處理資料方案 |
| Crisper 的 spray | **目前未支援** | 噴射／持續傷害自身的資料與碰撞路徑 |
| Warrant、P33、Hornet Pistol（內部名）的 entity 分支 | **後續鏈未證明，不能標為已支援** | entity 生成後的投射物／碰撞處理、身份與所有權鏈；部分正式名稱／可取得狀態未確認 |
| 霰彈、多彈丸副武器 | **按範圍策略排除** | 不是此次要補齊的功能 |
| 無法解析、來源不明或表外類型 | **未知／略過，不視為已支援** | 具體來源、版本對應及路徑證據 |

榴彈本體碰撞與爆炸範圍傷害不是同一個驗收項目。不能因本體排除位元可改就宣稱爆炸、範圍效果或 entity 後續機制也對自己生效。第 4 項「全部武器包括霰彈槍」同樣沒有因這份分類文件獲得光束或噴射支援。

## 更新時如何使用

完整的來源取得、校驗命令、`.gz` 與收集器差異、新舊版本分析及交接欄位見 [FileDiver 資料交接教程](FILEDIVER_HANDOFF.md)。

先在源碼根目錄核對附帶 catalog：

```powershell
python tools/verify_secondary_catalog.py --check
```

退出碼 0 表示附帶 catalog 的固定來源／政策／27 筆證據與統計核對通過，輸出 `raw_reference_replayed: false`；這一步沒有重新讀取原始三表。若已在本機取得 catalog 中指定的三份明文或 .gz 參考表，可重做解析：

```powershell
$entityReference = Read-Host '輸入固定 generated_entities.dl_bin 或 .gz 路徑'
$schemaReference = Read-Host '輸入固定 dl_library.dl_typelib 或 .gz 路徑'
$deltaReference = Read-Host '輸入固定 generated_entity_deltas.dl_bin 或 .gz 路徑'
python tools/verify_secondary_catalog.py --entities "$entityReference" --schema "$schemaReference" --deltas "$deltaReference"
```

三個參數必須一起提供；通過時 `raw_reference_replayed: true`，但 `matches_game_build` 和 `gameplay_verified` 仍為 false。加密安裝表、錯誤指紋或缺少任一輸入會拒絕，退出碼 2。這不是通用自動重建工具；新版本必須重新審查解析器、來源、完整 proof 和測試，不能只換三個檔案雜湊讓舊映射通過。

1. 使用 Toolkit 1.3.2 收集目標安裝中的實體、實體差量、型別結構、武器自訂設定及彈頭設定五份資料。比對安裝來源與舊快取，缺檔就記錄缺口。
2. 核對來源提交／SHA-256、装備槽位映射、每把武器的資源引用及機制。不能只依 EquipmentType、武器名稱或舊八槍清單判定。
3. 將分類新增／移除、排除策略和機制狀態的變更分開記錄。未解析記錄不能消失。
4. 對原生候選保留本機所有權、原值、有效槽位、寫前重檢、非執行資料寫入及讀回；不為覆蓋數字放寬檢查。
5. 分開報告 catalog 核對、程式路徑測試及玩法驗證。未支援機制維持明示未完成，不用 native hook、血量寫入或猜測位址代替。

[逐步接手指南](AGENT_GUIDE.md) · [建置與移植](PORTING.md) · [離線收集](UPDATE_TOOL.md) · [既有驗證記錄](VERIFICATION.md)

## English

The **preview.8 prerelease** targets every shootable secondary-slot weapon, excluding shotguns and multishot types. This goal is not fully implemented. Loadout-slot membership, runtime mechanism coverage and gameplay evidence are separate claims; public prerelease status does not establish complete support. [Download preview.8](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8); preview.5 remains available as a historical version with its old eight-ID pistol list.

The pinned reference has 27 secondary-slot records, 20 with shooting components and 19 after the Bushwhacker exclusion, including P-11. These are reference counts, not proven current-game availability. The seven no-known-firing-component records are not declared universally non-shootable. Sixteen source hashes are lookup candidates, not sixteen verified working weapons. Dagger beam and Crisper spray are unsupported; Warrant/P33/Hornet entity follow-up paths are unresolved. Hornet is an internal resource name, not confirmed retail availability. Grenade impact and explosion effects need separate evidence. Installed encrypted files are not proven equivalent to this reference, and complete classification does not establish complete self-hit support.

| Mechanism | Preview.8 status |
|---|---|
| P-11 dart | Dedicated identity branch in the unified core; all four preview.8 choices have a basic user success report |
| Eligible local native projectile | Candidate handler with source identity, ownership and fresh write guards; individual gameplay remains unverified |
| Plasma or grenade source | Classification includes these sources, but direct hits and later explosion/effect behavior require separate evidence |
| Dagger beam / Crisper spray | Unsupported; a native projectile hash lookup does not add these collision systems |
| Warrant / P33 / Hornet entity branch | Source identities recorded; downstream collision handling and complete shot coverage remain unverified |
| Shotgun or multishot secondary | Excluded by the selected scope policy |

From the source root, run `python tools/verify_secondary_catalog.py --check` to validate the shipped catalog against its pinned proof and policy. It does not replay the raw data by default. The `--entities`, `--schema` and `--deltas` arguments must be supplied together to replay the three pinned plaintext or gzip sources. Incorrect fingerprints and encrypted installed files are rejected. Successful replay still leaves matches_game_build and gameplay_verified false.

For a new game build, use Toolkit 1.3.2 to collect the installed tables, retain missing-file and version-correspondence gaps, then review loadout membership, source identities, shotgun exclusions and each firing mechanism separately. Preserve unknown records. Do not merely replace hashes, guess offsets or add a native hook to claim completeness. See the [player guide](SELECTABLE.md) for English installation and the [Agent guide](AGENT_GUIDE.md) for the maintenance sequence.
