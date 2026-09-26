# Projectile Collision Filter｜投射物碰撞過濾器・P-11 自療與四種範圍

![Projectile Collision Filter / 投射物碰撞過濾器](docs/assets/projectile-collision-filter-cover.png)

[English](README.en.md) · [下載 v0.3.0-preview.8](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8) · [安裝與切換](docs/SELECTABLE.md) · [副武器支援範圍](docs/SECONDARIES.md)

讓自己射出的 P-11 治療飛鏢能命中自己，由遊戲原生碰撞與治療處理效果。你仍然手動瞄準和射擊；同一個 Arsenal 模組可四選一，擴展到其他支援的武器投射物。傷害型武器也會保留原生傷害效果，可能造成自傷。

**preview.8 四個選項已有使用者「可用／正常」回報，版本仍為預覽版。** 這是整體基本使用回報，沒有逐武器、完整主客機或統一 FPS 測量紀錄；不代表所有傷害機制已支援。發布整理保持使用者測試包的四份 Lua 和遊戲資源不變。

## Arsenal 雙語四選一

配置頁為英文在前、中文在後，選擇欄 **Effect Scope / 生效範圍**。首次預選 P-11，模組總開關仍由 Arsenal 管理。

| Arsenal label / 配置選項 | Scope / 範圍 |
|---|---|
| **P-11 Only / 僅治療手槍** | P-11 healing darts only; recommended and initially selected. / 僅治療飛鏢，推薦且首次預選。 |
| **All Sidearms / 手槍全部** | P-11 and supported sidearm projectiles; excludes shotguns and multi-projectile types. / P-11 與支援的副武器投射物，排除霰彈與多彈丸。 |
| **All Weapons (No Shotguns) / 全部武器不包括霰彈槍** | P-11 and supported weapon projectiles; excludes shotguns and multi-projectile types. / P-11 與支援的武器投射物，排除霰彈與多彈丸。 |
| **All Weapons (Including Shotguns) / 全部武器包括霰彈槍** | Includes shotgun/multi-projectile types. **WARNING: May cause severe performance impact.** / 包含霰彈與多彈丸；**警告：可能造成嚴重性能影響。** |

## 只需選擇兩個下載之一

| 下載檔 | 用途 |
|---|---|
| [Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip) | **玩家下載這個**：匯入 Arsenal，在同一個模組內四選一。 |
| [HD2-Projectile-Collision-Filter-Update-Toolkit-1.3.2-win-x64.zip](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/HD2-Projectile-Collision-Filter-Update-Toolkit-1.3.2-win-x64.zip) | 遊戲更新後收集離線資料；附完整源碼、建置及維護指南。另行解壓，不匯入 Arsenal。 |

本版只有兩個手動 ZIP；不再額外發布四個獨立包。SHA-256 見 [Release 正文](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8)。GitHub 自動 Source code 下載是源碼，不能直接匯入 Arsenal。舊 Release 的標籤與資產保留供回退。

## 安裝、升級與切換

1. 完整關閉遊戲，等更新完成，另外安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 在 Arsenal 停用舊四選一包、P-11 0.2.3 測試包及其他自命中獨立包，清除舊部署。**一次只啟用一個自命中模組。**
3. 匯入上面的整合 ZIP；沿用既有 GUID，遇到身份重複提示就替換舊項目。
4. 在 **Effect Scope / 生效範圍** 選一項，確認總開關啟用，再重新部署和啟動遊戲。
5. 切換、停用或回退都先關閉遊戲，再清除舊部署並重新部署。

目標為 **Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17、API 1、internal 16**。未知遊戲／loader 版本停止修改；不要只替換雜湊強行啟用。

## 原理、性能與支援限制

四種選項共用一個核心，每次選擇只部署一個 addon。它跟隨投射物分配游標，處理近期候選和有限重查，取代舊版反覆遍歷全部 2,048 槽的方式。只有通过本機所有權、武器／彈種身份、原旗標及有效資料頁檢查的投射物，才清除來源碰撞排除位 `0x20`；寫前重檢、寫後讀回，實際效果由遊戲處理。

沒有 native hook、執行碼修補或直接寫入生命、體力、彈藥、傷害值。仍有逐候選工作量；大量投射物、待辦超限、延後生成或碰撞時機可能造成略過。不能保證零開銷或每一發都生效。

先前使用者回報 **P-11 0.2.3 約 70 → 130 FPS 且自療正常**；這屬於該次舊候選測試，並非 preview.8 四種範圍的固定提升。

- **All Sidearms / 手槍全部** 以副武器槽位參考清單識別來源，不再只限歷史八個 ID；分類完整性和實際機制支援仍分開記錄。
- Dagger 光束、Crisper 噴射尚未支援；Warrant、P33、內部 Hornet 的 entity 後續碰撞／效果未完成驗證。
- 電漿、榴彈的本體命中不等於後續爆炸、範圍效果均已驗證。「全部武器」指支援的原生投射物路徑。
- 第 2、3 項保守排除霰彈／多彈丸和參考表外類型；第 4 項**可能造成嚴重性能影響**。

[原理與四種範圍](docs/VARIANTS.md) · [性能說明](docs/PERFORMANCE.md) · [驗證記錄](docs/VERIFICATION.md)

## 搭配動作與隊友追蹤

推薦 P-11 搭配 [Raise Weapon: Aim at Yourself / 舉槍瞄準自己](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另行下載並依原頁裝備 Raise Weapon 表情。使用者也曾回報第一人稱朝自己腳部射擊的用法；仍需真正飛鏢命中角色。

動作包只改姿勢，投射物包處理自命中。隊友鎖定／追蹤保留原作者版本、獨立管理，本包不包含、不替你自動瞄準或開火。[P-11 用法](docs/SELF_HIT.md)

## 更新後一次收集與開發導航

完整解壓 **Toolkit 1.3.2**，雙擊 `Collect-HD2-Update.cmd`；Windows x64 收集入口不需另裝 Python。查看 `diagnostics/latest.json` 指向的中文摘要與維修交接。工具收集可取得的磁碟版本、部署資源、相關既有日誌及資料表；不啟動遊戲、不讀取執行中程序、不部署、不上傳，也不承諾每次更新自動修復。

完整對應源碼已在 `Source/HD2-Projectile-Collision-Filter/`，不用再解壓內層源碼 ZIP。

| 我要做的事 | 入口 |
|---|---|
| 安裝、切換、停用、回退 | [玩家操作指南](docs/SELECTABLE.md) |
| 遊戲更新後一次收集資料 | [離線更新工具](docs/UPDATE_TOOL.md) |
| 開發、判讀、修補、交接 | [AGENTS.md](AGENTS.md) → [逐步接手指南](docs/AGENT_GUIDE.md) → [建置與移植](docs/PORTING.md) |
| FileDiver、副武器與霰彈資料核對 | [固定來源、重播與更新交接教程](docs/FILEDIVER_HANDOFF.md) |
| 驗證與發布 | [驗證記錄](docs/VERIFICATION.md) · [發布指南](docs/PUBLISH.md) |
| 兩個 AyakaMods 頁面標題、介紹、BBCode、封面 | [發布素材導航](docs/PAGE-PUBLISHING.md) |

本倉庫已使用名稱 **HD2-Projectile-Collision-Filter**；舊版本保留歷史名稱。維護指南以中文為主，配置頁、首頁與發布文案提供雙語。社群作品，與 Arrowhead Game Studios 無隸屬關係；開發及文件由 OpenAI 工具協助製作。[來源與依賴](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)
