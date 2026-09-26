# 投射物模組發布文案（繁體中文）

## 標題

Projectile Collision Filter｜投射物碰撞過濾器・P-11 自療與四種範圍

## 短摘要

讓自己的 P-11 飛鏢透過原生碰撞命中並治療自己。Arsenal 雙語四選一，共用游標核心。附離線更新工具與完整源碼；包含霰彈的第四項可能造成嚴重性能影響。

## 正文

![Projectile Collision Filter / 投射物碰撞過濾器](https://raw.githubusercontent.com/cainiao524/HD2-Projectile-Collision-Filter/v0.3.0-preview.8/docs/assets/projectile-collision-filter-cover.png)

## 讓 P-11 治療飛鏢也能命中自己

自己射出的 P-11 飛鏢實際擊中角色後，使用遊戲原生碰撞與治療逻輯產生效果。保留手動瞄準、手動射擊、原本彈藥消耗、射速、治療量和效果；不直接寫入血量或體力。

**v0.3.0-preview.8 是四選一整合預覽版。** 使用者已回報四個選項基本使用正常；本次發布保持其測試包的四份 Lua 和遊戲資源不變，整理雙語配置、介紹、工具與封面。完整逐武器、主客機、並行與效能驗證仍有缺口。

## 同一個 Arsenal 模組，四種生效範圍

配置頁英文在前、中文在後，在 **Effect Scope / 生效範圍** 四選一：

- **P-11 Only / 僅治療手槍**：僅 P-11 治療飛鏢。推薦，首次預選。
- **All Sidearms / 手槍全部**：P-11 與目前支援的副武器投射物，排除霰彈／多彈丸。
- **All Weapons (No Shotguns) / 全部武器不包括霰彈槍**：P-11 與支援的武器投射物，排除霰彈／多彈丸。
- **All Weapons (Including Shotguns) / 全部武器包括霰彈槍**：包含霰彈／多彈丸，**警告：可能造成嚴重性能影響。WARNING: May cause severe performance impact.**

整體啟用／停用由 Arsenal 管理。切換前關閉遊戲，選好後重新部署；不要手動同時複製四份資源。

## 本版效能處理

四個方案共用一個核心與 addon，跟隨投射物分配游標，只檢查近期候選並有限重查，取代歷史版本反覆遍歷全部 2,048 槽位的方式。候選仍需本機所有權、武器／投射物身份、原值、寫前重檢與寫後讀回。

先前使用者對 **P-11 0.2.3** 回報自療正常、約 **70 → 130 FPS**；這是舊候選的一次回報，沒有完整量測條件，**不是 preview.8 四個方案的固定提升**。新版仍有候選處理成本；大量彈丸、過期提示或碰撞時機可能導致略過，不承諾零開銷、零卡頓或每發成功。

## 下載：兩個 ZIP

- [四選一整合模組 ZIP](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip)：玩家下載並匯入 Arsenal。
- [Update Toolkit 1.3.2](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/HD2-Projectile-Collision-Filter-Update-Toolkit-1.3.2-win-x64.zip)：另行解壓，用於遊戲／loader 更新後的一鍵離線收集，附完整對應源碼、建置工具和 AI／Agent 接手指南。不匯入 Arsenal。

[完整 Release 與 SHA-256](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8) · [GitHub 源碼](https://github.com/cainiao524/HD2-Projectile-Collision-Filter)

不再另發四個獨立 Mod 包。歷史版本仍可回退；GitHub 自動 Source code 下載是源碼，不是安裝包。

## 安裝與使用

1. 完整關閉遊戲並完成更新，另行安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 在 Arsenal 停用舊自命中／自療版本、0.2.3 測試包、其他重複自命中包及研究模組，清除舊部署。
3. 匯入整合 ZIP；相同 GUID 的舊項目使用替換流程。**一次只啟用一個自命中包。**
4. 在 Effect Scope / 生效範圍 選一項，確認模組總開關啟用，重新部署後啟動遊戲。
5. 裝備 P-11，手動瞄準和射擊。飛鏢必須真正命中自己的角色；只有開啟模組不會自動治療。
6. 切換、停用或回退都先關閉遊戲，清除舊部署再重新部署。

本版目標：**Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17、API 1、internal 16**。未知版本停止修改，不可只更換雜湊強行啟用。

## 推薦搭配「舉槍瞄準自己」

推薦另裝 [Raise Weapon: Aim at Yourself / 舉槍瞄準自己](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，裝備 Raise Weapon 表情並依原頁操作。它負責姿勢，本包負責投射物自命中；兩個模組分別管理。使用者也曾回報第一人稱朝腳部射擊的方式。

Experimental Infusion 必須先在遊戲中啟用；既有使用者回報 P-11 自命中可觸發其效果，本包不替你啟用增益。隊友追蹤保持原作者模組獨立管理，未附帶或修改，也沒有自動瞄準／開火。

## 支援限制

- All Sidearms 以副武器裝備槽位參考清單識別，已擴展出歷史八個 ID；不表示全部副武器機制均已完成。
- Dagger 光束、Crisper 噴射未支援；Warrant、P33、內部 Hornet 的 entity 後續碰撞／效果尚未驗證。
- 電漿／榴彈本體命中與爆炸、範圍效果分開看。「All Weapons」指支援的原生投射物路徑，不含所有傷害機制。傷害型武器可能傷害自己。
- 前三項排除霰彈與多彈丸；第 2、3 項也保守略過參考表外類型。第四項包含霰彈，可能造成嚴重性能影響。
- 更新診斷不啟動遊戲、不讀程序、不部署、不上傳；收集完整、候選地址、舊日誌或雜湊吻合都不是新版玩法成功證明。

[完整操作與維護導航](https://github.com/cainiao524/HD2-Projectile-Collision-Filter)。只修改經核對本機投射物的來源碰撞排除位；沒有 native hook、執行碼修補、全域定義改寫或直接生命／體力／彈藥／傷害值寫入。

封面為宣傳插畫，非遊戲實測截圖。社群模組，與 Arrowhead Game Studios 無隸屬關係；開發和文件由 OpenAI 工具協助製作。
