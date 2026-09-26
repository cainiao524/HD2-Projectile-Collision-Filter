# P11-Enhanced — 四選一，前三項排除霰彈

直接把 **P11-Enhanced-Selectable-v0.3.0-preview.4-build25480438.zip** 匯入 Arsenal。啟用「Self-hit scope」，選一個互斥子選項：

| 順序 | 方案 | 霰彈處理 |
|---|---|---|
| 1，首次預選 | 僅 P-11 | 只處理 P-11 飛鏢，其他彈丸一律略過 |
| 2 | 手槍排除霰彈 + P-11 | 候選手槍範圍，先排除霰彈與多彈丸 |
| 3 | 廣域排除霰彈 + P-11 | 本機原生武器投射物，先排除霰彈與多彈丸 |
| 4，需主動選擇 | 全部含霰彈 + P-11 | 保留包含霰彈的廣域原生投射物處理，可能造成卡頓 |

第 2、3 項在來源／武器查詢之前，排除固定離線表中的 **38 個類型**：已辨識的霰彈家族（含獨頭等單彈變體）及表內全部多彈丸種類。為避免未分類的新彈種繞過過濾，表外類型也略過。因此其他一次多彈丸機制亦可能被排除，不只傳統霰彈槍。這是按彈種過濾，主武器與手槍使用同一排除規則。

每項都內建相同 P-11 0.2.1 Lua，SHA256：
`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。
P-11 程式未改；擴展升為 0.1.2。只有所選方案部署到遊戲。

## 安裝與切換

1. 關閉遊戲，另行安裝相容的 Bingus Shared Loader。
2. 在 Arsenal 停用舊版與其他重複自命中 addon，再匯入此 ZIP。
3. 確認所選範圍，啟用並重新部署。首次匯入預選第 1 項；模組總開關遵從管理器偏好。從三選一升級時也請重新確認選項。
4. 切換或停用都先關閉遊戲，修改後重新部署，再啟動遊戲。

對應 **build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**。未知版本停止修改。

第四項的「全部」指此 addon 支援的本機原生投射物範圍；射線、光束、近戰、爆炸及 entity 投射物不是已驗證支援項目。P-11 有使用者基本成功回報；擴展、霰彈排除在目前遊戲中的完整覆蓋與效能改善仍缺少實測，所以維持預覽版。

排除發生在每顆來源讀取和寫前檢查之前；依然遍歷 2048 個槽位，不能承諾零開銷。32 顆 type 179 的合成測試：第 2、3 項為 10 次邏輯讀取、0 寫入；第 4 項為 985 次讀取、32 寫入。這不是 FPS 測量。

推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。隊友追蹤保持原作者模組獨立管理。

更新後使用 Full-Kit 中的 `Collect-HD2-Update.cmd`。只收集離線資料及準備維修，不啟動遊戲、不讀程序、不部署、不上傳，不保證全自動修復。

## English

Import this ZIP directly into Arsenal and choose one of four exclusive sub-options. P-11 only is initially selected. The first three choices exclude shotguns: P-11 is intrinsically limited to its own dart; pistol and filtered-broad scopes reject 38 pinned shotgun/multishot types and types outside the reference table before source lookup. This conservatively excludes other multishot mechanisms too. The fourth choice explicitly opts into shotguns and can cause additional per-pellet load.

Close the game before switching and redeploy. Disable older standalone/selectable versions and confirm the selected scope after upgrading. All choices preserve original P-11 0.2.1. Expanded 0.1.2 and shotgun coverage/performance remain gameplay-unverified candidates. Broad scope is not universal damage-system support.

[Arsenal Sub-options](https://docs.rsnl.gg/mod-builder/options) · [Version 1 schema](https://docs.rsnl.gg/mod-builder/manifest).

升級提示：新包沿用相同模組身份。若 Arsenal 提示重複，使用管理器的替換功能，或先停用並移除舊三選一項目，再匯入新版；不要保留兩個同時啟用。 / Upgrade: the mod identity is unchanged. If Arsenal reports a duplicate, replace the old package or disable/remove its old entry before importing.
