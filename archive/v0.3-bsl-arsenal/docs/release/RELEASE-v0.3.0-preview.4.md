# 四選一：前三项排除霰彈，第四項包含霰彈

**P11-Enhanced-Selectable-v0.3.0-preview.4-build25480438.zip** 可直接匯入 Arsenal。同一個模組內四選一：

1. 僅 P-11，首次預選。
2. 手槍排除霰彈 + P-11。
3. 廣域排除霰彈 + P-11。
4. 全部含霰彈 + P-11，可能造成卡頓，需主動選用。

全部保留原 P-11 0.2.1。擴展升為 0.1.2：排除版按彈種在來源／武器查詢前跳過 38 個已知霰彈與多彈丸類型，同時跳過表外未知型號。霰彈含獨頭變體，其他一次多彈丸機制亦保守排除。包含版保留逐顆處理；沒有新 hook，沒有放寬所有權或寫前重檢。

32 顆霰彈的合成測試：排除版 10 次邏輯讀取、0 寫入；包含版 985 次讀取、32 寫入。仍遍歷固定槽位；不是 FPS 或不卡頓保證。P-11 已有使用者基本成功回報，擴展及目前遊戲完整霰彈覆蓋仍未實測。「全部」仍限已支援的原生投射物系統。

關閉遊戲，停用舊三選一／独立包，匯入新版後重新確認範圍並部署。需 build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16。

Full-Kit 含此模組、來源和 Update-Toolkit 1.2.0；先解壓。更新工具增加第四範圍及排除表維修要求，只做離線收集與交接，不啟動遊戲、不讀程序、不部署、不上傳、不保證自動修復。

候選 Lua 638 個斷言，P-11 原 bytes 與資料 writer 保留。參考表分類可使用來源中 verify_projectile_filter.py 離線重驗。所有玩法狀態仍如實保留候選。

## English

Four exclusive Arsenal choices: P-11 only; pistols without shotguns; broad without shotguns; broad including shotguns. All preserve original P-11. Filtered scopes reject 38 pinned shotgun/multishot types and out-of-table types before source/weapon lookup. This also conservatively skips other multishot mechanisms and shotgun slug variants. The fourth choice opts into additional per-pellet load.

Synthetic 32-pellet results: 10 reads/no writes when excluded, versus 985 reads/32 writes when included. No FPS or zero-stutter claim. Expanded behavior, classification coverage and native coexistence remain gameplay-unverified. Broad is not universal damage-system support.

Disable older variants, close the game, import, confirm the choice and redeploy. The full kit includes source and offline diagnostics; it never launches the game, reads processes, deploys or uploads and does not guarantee automatic repair.

升級提示：新包沿用相同模組身份。若 Arsenal 提示重複，使用管理器的替換功能，或先停用並移除舊三選一項目，再匯入新版；不要保留兩個同時啟用。 / Upgrade: the mod identity is unchanged. If Arsenal reports a duplicate, replace the old package or disable/remove its old entry before importing.

離線驗收：56 項 Python、638 個候選 Lua 斷言及 Arsenal 0.36.2 全部 16 種切換通過。新增廣域排除方案與其他擴展的任兩者同開均由診斷報衝突，模擬入口在寫入前停止。
