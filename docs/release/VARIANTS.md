# 四種範圍與資料修改原理 / Scopes and implementation

目前為 **v0.3.0-preview.8**。四種方案使用同一個游標核心，各自僅部署一份 addon；P-11 在共用核心內保留專用身份分支。歷史 preview.6 的「原 P-11 addon 加另一個擴展 addon」結構不適用此版，不可重新加回舊遍歷 addon。

| Arsenal label / 配置選項 | Scope / 範圍 |
|---|---|
| **P-11 Only / 僅治療手槍** | P-11 healing darts only; recommended and initially selected. / 僅治療飛鏢，推薦且首次預選。 |
| **All Sidearms / 手槍全部** | P-11 and supported sidearm projectiles; excludes shotguns and multi-projectile types. / P-11 與支援的副武器投射物，排除霰彈與多彈丸。 |
| **All Weapons (No Shotguns) / 全部武器不包括霰彈槍** | P-11 and supported weapon projectiles; excludes shotguns and multi-projectile types. / P-11 與支援的武器投射物，排除霰彈與多彈丸。 |
| **All Weapons (Including Shotguns) / 全部武器包括霰彈槍** | Includes shotgun/multi-projectile types. **WARNING: May cause severe performance impact.** / 包含霰彈與多彈丸；**警告：可能造成嚴重性能影響。** |

## 資料如何生效

1. 讀取原生投射物分配游標，定位近期槽位並維護有限重查提示。游標步幅可能包含已佔用槽位的探測，不等於發射數量。
2. 重新核對本機玩家、來源 unit、武器登記與附件所有權、投射物 type／auxiliary、旗標與資料頁。P-11 另需符合 stim 定義與來源武器。
3. 通過版本、原值及完整依賴重檢後，對兩位元組旗標清除 `0x20` 來源碰撞排除位，保留其他位元並讀回確認。
4. 實際飛鏢命中後由原生碰撞和治療／傷害產生效果。不直接改生命、體力、彈藥、射速或傷害，不改全域定義或執行碼，沒有 native hook。

待辦只保存槽號與有限生命期，不保存跨更新可直接使用的記憶體快照或寫入授權。同一次更新可以共用發現結果，但其全部依賴會帶入每次寫前重檢。物件失效、身份改變、版本未知就略過或停止，不能在被回收的地址盲目寫回。

## 分類與有限處理

前三項排除霰彈與多彈丸。P-11 Only 只接受治療飛鏢；第 2、3 項在來源／武器查詢之前拒絕 38 個排除 type 和參考表外類型。第四項包含霰彈，可能造成嚴重性能影響。

38 個排除 ID 來自 27 個已辨識霰彈記錄（含獨頭）與全部 32 個參考多彈丸記錄的聯集。來源及指紋見 `maintenance/projectile-exclusions-25480438.json`。副武器來源使用固定裝備槽位 catalog，不以 AI EquipmentType 或武器名稱猜測。16 個來源 lookup 候選不是 16 把都已驗證；光束、噴射與後續 entity 缺口見 [SECONDARIES](SECONDARIES.md)。

每次更新最多檢查 128 個提示槽位、64 次寫入嘗試；待辦最多 256 槽、8 次有效排程更新。新提示至少跨兩次更新檢查，過載／過期記錄略過。這些界限會限制成本，也可能錯過處理；不保證每發在首次碰撞之前完成。[性能說明](PERFORMANCE.md)

使用者回報四個選項正常，仍缺逐武器、完整主客機、碰撞時序和並行覆蓋。未知新 build 必須重新核對，不能只替換雜湊。[驗證](VERIFICATION.md) · [移植](PORTING.md)

## English

Preview.8 uses one shared cursor-based core and a single deployed addon per scope. P-11 has a dedicated identity branch inside that core. The old two-addon layout is historical and must not be restored into this package.

The addon follows allocation progress, checks fresh local ownership and projectile identity, then uses the guarded data writer to clear only the two-byte flags' source-collision exclusion bit 0x20. Every write rechecks its dependencies and reads the result back. Native collisions and effects handle hits; no executable patch, native hook, global-definition change or direct health/stamina/ammo/damage write is used.

Bounded pending slots are hints, never retained write authorization. Queue limits, delayed initialization and collision timing can skip projectiles. All four choices have a user report of normal basic operation; this is not full per-weapon, host/client or performance validation. Classification and unsupported mechanisms remain documented separately.
