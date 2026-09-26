# 安裝與切換 / Install and switch

[主要下載：v0.3.0-preview.8](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8)。玩家只需整合模組 ZIP；Toolkit 1.3.2 用於离線收集和維護，不匯入 Arsenal。沒有另附四個獨立模組下載。

## 輸入與環境 / Input and requirements

- `Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip`。
- Helldivers 2 Steam build **25480438** / EXE **1.8.46015.0**。
- 另行安裝 Bingus Shared Loader **v17 / API 1 / internal 16**，以 Arsenal 管理。

## 配置 / Configuration

模組：**Projectile Collision Filter / 投射物碰撞過濾器**。選擇欄：**Effect Scope / 生效範圍**。所有欄位英文在前、繁體中文在後。

> Choose one scope. P-11 Only is selected by default. Close the game before changing options, then redeploy.  
> 四選一，首次預選「僅治療手槍」。切換前關閉遊戲，選好後重新部署。

| Arsenal label / 配置選項 | Scope / 範圍 |
|---|---|
| **P-11 Only / 僅治療手槍** | P-11 healing darts only; recommended and initially selected. / 僅治療飛鏢，推薦且首次預選。 |
| **All Sidearms / 手槍全部** | P-11 and supported sidearm projectiles; excludes shotguns and multi-projectile types. / P-11 與支援的副武器投射物，排除霰彈與多彈丸。 |
| **All Weapons (No Shotguns) / 全部武器不包括霰彈槍** | P-11 and supported weapon projectiles; excludes shotguns and multi-projectile types. / P-11 與支援的武器投射物，排除霰彈與多彈丸。 |
| **All Weapons (Including Shotguns) / 全部武器包括霰彈槍** | Includes shotgun/multi-projectile types. **WARNING: May cause severe performance impact.** / 包含霰彈與多彈丸；**警告：可能造成嚴重性能影響。** |

“Supported” 表示目前實作的原生投射物路徑，不包含每種光束、噴射或後續 entity 效果；[完整機制限制](SECONDARIES.md)。配置選項不會自動加入隊友追蹤或動作模組。

## 操作 / Steps

1. 完整關閉遊戲，等待更新及部署完成。Close the game and finish updates first.
2. Arsenal 停用舊版四選一、自療 0.2.3、舊自療 hook、其他自命中獨立版與研究模組，清除旧部署。Disable old/duplicate self-hit and research packages, then purge the old deployment.
3. 匯入整合 ZIP。GUID 保持不變，若遇重複身份，替換旧項目或先移除旧項目再匯入；不要同時啟用兩份。Import the ZIP and replace the previous entry with the same GUID.
4. 在 Effect Scope / 生效範圍 四選一，確認模組總開關啟用，重新部署。Choose one scope, enable the mod and redeploy.
5. 啟動遊戲，裝備 P-11 手動射擊；飛鏢必須實際命中自己才有原生治療。Launch and test an actual P-11 self-hit; manual aiming and firing remain necessary.

**預期輸出：** 只部署所選範圍的一個 addon，未選的資源不殘留。P-11 預選和模組總開關是兩件事：Arsenal 匯入偏好可能令整體初始停用，需自行確認。

**繼續條件：** 版本相容、沒有重複自命中包，且部署所選方案。四項有使用者正常回報，但不能由匯入成功判斷當次原生碰撞、每把武器或效能已驗證。

**失敗處理：** 遊戲無效果時先核對已部署／啟用、loader 和版本，查看 `ProjectileCollisionFilter.log`，再用 Toolkit 收集。日誌只是對應歷史事件；不要把 activated／readback 當作治療成功。

## 切換、停用與回退 / Switching and rollback

每次都先關閉遊戲，再變更選擇或總開關、清除部署並重新部署；不要在運行中替換檔案。回退時停用並移除目前部署，再選用保存的舊成功包或歷史 Release，只啟用一個自命中版本。Close before every change, purge and redeploy; keep a single self-hit package enabled.

第四項 **WARNING: May cause severe performance impact. / 警告：可能造成嚴重性能影響。** 發生卡頓先回到 P-11 Only，記錄場景與前後幀率；不能以降低身份／寫入保護解決。

推薦另裝 [Raise Weapon: Aim at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)。隊友追蹤另行管理，保持原作者版本。[更新後收集](UPDATE_TOOL.md) · [性能說明](PERFORMANCE.md)
