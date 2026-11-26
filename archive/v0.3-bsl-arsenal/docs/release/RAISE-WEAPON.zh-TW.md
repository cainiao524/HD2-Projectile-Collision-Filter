# 動作模組網站發布文案（繁體中文）

## 標題

Raise Weapon: Aim at Yourself｜舉槍瞄準自己

雙語標題：Raise Weapon: Aim at Yourself / 舉槍瞄準自己

## 簡介

把「Raise Weapon／舉槍」表情動作替換為瞄準自己的持槍姿勢。這是動作替換；需要 P-11 對自己生效時，可另外搭配投射物碰撞過濾器的自命中治療功能。

## 正文

![Raise Weapon: Aim at Yourself／舉槍瞄準自己封面](https://raw.githubusercontent.com/cainiao524/HD2-Projectile-Collision-Filter/v0.3.0-preview.8/docs/assets/raise-weapon-aim-at-yourself-cover.png)

### 把「舉槍」換成瞄準自己的姿勢

此模組替換 **Raise Weapon／舉槍** 表情動作，讓角色在播放該動作時擺出向自己瞄準的持槍姿勢。裝備這個表情，使用你自己的表情操作綁定播放即可。

**已知問題：一邊衝刺、一邊射擊時播放這個表情，可能造成角色卡住（softlock）。遇到時取消衝刺，或切換武器。這項既有問題仍保留，未標示為已修復。**

[動作模組原頁與下載](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/) · [搭配 Projectile Collision Filter／P-11 自療](https://ayakamods.com/mods/p-11-self-hit-healing-p-11-%E6%B2%BB%E7%99%82%E6%89%8B%E6%A7%8D%E8%87%AA%E7%99%82.4166/)

### 這個包提供什麼

- 替換 Raise Weapon 表情的動作與瞄準姿勢。
- 保留你自己的按鍵綁定；沒有指定固定的預設鍵。
- 由 Arsenal 管理啟用與停用。
- 動作包本身不修改投射物碰撞、治療量、生命值或其他傷害效果，也不會自動讓 P-11 對自己生效。

只有動作替換不等於飛鏢已能命中自己。若要自療，需要另外安裝相容的投射物自命中模組，並讓實際射出的 P-11 飛鏢擊中角色。

### 安裝與使用

1. 關閉遊戲，從本頁下載原有動作包。
2. 將原包匯入 Arsenal。若已有另一個替換相同 Raise Weapon 動作的模組，先停用其中一個，避免同一資源互相覆蓋。
3. 啟用此動作模組並重新部署。
4. 啟動遊戲，在遊戲內裝備 **Raise Weapon／舉槍** 表情。
5. 使用自己設定的表情操作播放。避免同時衝刺、射擊和播放此動作；若卡住，取消衝刺或切換武器。
6. 要停用或改換動作包，先關閉遊戲，在 Arsenal 調整後重新部署。

如果動作未改變，先確認裝備的是 Raise Weapon 表情，再檢查同一動作資源是否被其他模組覆蓋。沒有固定鍵位要求；依你的遊戲設定操作。

### 搭配 P-11 自命中治療

推薦另外下載 [Projectile Collision Filter（投射物碰撞過濾器）／P-11 自療](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8)，選擇其中的「**P-11 Only / 僅治療手槍**」方案作為起點。

兩個模組分別管理：本包負責表情姿勢，Projectile Collision Filter 負責讓符合條件的本機 P-11 飛鏢可與射手碰撞。治療仍依賴真正的飛鏢命中與遊戲原生邏輯，保留手動瞄準和射擊。自命中模組的 loader、遊戲版本與安裝要求請依它自己的頁面。

搭配模組沒有附在本動作包內。隊友追蹤也屬於其他獨立模組，本包沒有新增鎖定或自動射擊功能。

### 版本、相容性與已知限制

| 項目 | 內容 |
|---|---|
| 作者 | **losa** |
| 原模組名稱 | **Raise weapon aims at yourself** |
| 原動作版本 | **2026-09-18** |
| 頁面分類 | **Characters** |
| 既有附件大小 | **328.9 KB**，以頁面實際下載為準 |
| 本次頁面更新 | 中文／英文介紹與獨立封面；保留原下載和版本 |

本次更新封面與操作說明，沒有修改動作成品，也沒有新增玩法測試。衝刺＋射擊時播放表情的卡住問題仍是已知限制。

目前沒有完整的全部武器姿勢、每個遊戲版本或聯機顯示測試，因此不保證所有武器都能得到相同姿勢，也不保證其他玩家一定能看到替換後的動作。使用者留言不作為這些情況已驗證的證據。

本模組為社群作品，與 Arrowhead Game Studios 無隸屬關係。需要的是動作替換就使用本頁原包；需要 P-11 自療時，另外依相容性要求安裝搭配模組。

新版投射物整合模組與更新工具見 [GitHub Release](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8)。封面採藍色碎片和持槍科幻角色構圖，槍口朝上且遠離頭部；是宣傳插畫，非遊戲內動作的精確示範。這次只更新介紹和封面，動作成品不變。
