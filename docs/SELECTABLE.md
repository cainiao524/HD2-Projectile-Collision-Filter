# 玩家操作指南：安裝、切換與回退

四選一整合模組名稱為 **Projectile Collision Filter（投射物碰撞過濾器）**。本次只改整合包名稱與說明，GitHub 專案名、模組身份及四個選項的功能不變。

一般使用者下載 **Projectile-Collision-Filter-v0.3.0-preview.5-build25480438.zip**，直接匯入 Arsenal。固定範圍的四個獨立 ZIP 與整合版效果對應；**五個模組包只啟用一個**。Update Toolkit 是離線工具，不能當模組匯入。[六檔下載表](../README.md)

## 安裝前

目前支援 **Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**。Loader 另外安裝；未知遊戲或 loader 版本會停止修改，不能只改雜湊繞過。先關閉遊戲，確認 Steam 更新完成。

P-11 推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。隊友追蹤和動作模組保持原作者模組獨立管理，沒有附在本包內。[P-11 實際用法](SELF_HIT.md)

## 首次安裝

1. 在 Arsenal 停用舊版 P-11 自命中、手槍／全部武器自命中及舊整合包。
2. 匯入一個模組 ZIP。整合版沿用既有身份；遇到重複身份提示時使用替換，或停用並移除舊項目後重新匯入。
3. 整合版打開「**生效範圍**」，確認以下四個選項之一。首次預選第 1 項；模組總開關遵從 Arsenal 匯入偏好，請自己確認已啟用。
4. 啟用並重新部署，再啟動遊戲。只應有所選範圍的自命中 addon 生效。

| 選項 | 說明 |
|---|---|
| **僅治療手槍** | 僅讓 P-11 治療飛鏢對自己生效。推薦，首次預選。 |
| **手槍全部** | 包含 P-11 與目前支援的手槍；排除霰彈及多彈丸類型。 |
| **全部武器不包括霰彈槍** | 包含 P-11 與支援的武器投射物；排除霰彈及多彈丸類型。 |
| **全部武器包括霰彈槍** | 包含霰彈及多彈丸類型，**可能造成嚴重性能影響**。 |

四項均包含相同 P-11 0.2.1。獨立包維持原始檔案與當時說明；新版選項短文案顯示在整合包中。三個擴展包版本仍為 0.1.2。

## 切換、停用與回退

- **切換範圍**：關閉遊戲 → Arsenal 選擇另一項 → 清除舊部署並重新部署 → 再啟動遊戲。不要在遊戲運行中期待選項立即生效。
- **改用獨立版**：關閉遊戲 → 停用整合版 → 匯入一個對應獨立 ZIP → 啟用並重新部署。
- **停用**：關閉遊戲 → 在 Arsenal 停用這個自命中模組 → 重新部署。讓管理器移除其部署內容，不手動刪除其他模組的檔案。
- **回退**：關閉遊戲 → 停用／替換新版 → 從歷史 Release 取回相容的舊包 → 確認只有一個版本啟用 → 重新部署。舊包不會因此支援新版遊戲；版本不相容時保持停用並收集資料。

## 出現問題時

| 現象 | 處理 |
|---|---|
| 匯入時提示重複 | 替換既有相同身份，或停用／移除舊項目後匯入 |
| 同時啟用了整合版與獨立版 | 關閉遊戲，只保留一個自命中包，再重新部署 |
| 第四項明顯卡頓 | 關閉遊戲，改為前三項之一並重新部署；建議先用「僅治療手槍」 |
| 更新後沒有效果／不相容 | 完整解壓工具包，執行 Collect-HD2-Update.cmd，查看摘要和維修交接；不要沿用舊成功記錄啟用未知版本 |
| 收集顯示缺少 P-11、重複資源或 loader 不相容 | 依摘要核對管理器已啟用項目及部署結果；工具不會代為部署，修正後再收集 |
| 檔案仍在更新或收集不完整 | 等 Steam 與部署完成後重新收集；保留失敗報告供比對 |

## 範圍與驗證界限

「手槍全部」目前限八個候選手槍 ID。「全部武器」只指目前支援的原生投射物系統，並未驗證所有射線、光束、近戰、爆炸及 entity 投射物。

第 2、3 項在來源／武器查詢之前排除固定表中的 38 個霰彈／多彈丸類型，也跳過表外未知類型。包含霰彈的獨頭變體；其他多彈丸機制也可能被排除。P-11 原程式只處理自己的 type 318，其他彈丸直接略過。

P-11 原實作已有使用者基本成功回報；擴展、目前遊戲的完整分類覆蓋、組合共存及效能仍未全面實測。仍有槽位掃描，合成測試讀取量不是 FPS 或零卡頓保證。[原理與範圍](VARIANTS.md) · [驗證記錄](VERIFICATION.md) · [更新工具](UPDATE_TOOL.md)

## English

Import one of the five mod ZIPs and enable only that package. The selectable package offers four exclusive scopes under 生效範圍; P-11 only is initially selected. Overall enablement follows Arsenal preferences. Close the game before changing scope, disabling or rolling back, and redeploy afterward. Replace the existing identical identity if Arsenal reports a duplicate.

The first three choices exclude shotguns. The fourth includes them and may cause severe performance impact. All include original P-11. Broader behavior remains a candidate; “all” is limited to supported native projectiles. The separate toolkit collects offline evidence and does not install or repair the mod automatically.

[Arsenal Sub-options](https://docs.rsnl.gg/mod-builder/options) · [Version 1 schema](https://docs.rsnl.gg/mod-builder/manifest).
