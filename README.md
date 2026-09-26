# P11-Enhanced — 一個模組，四種自命中範圍

**前三個方案排除霰彈，第四個方案主動選用包含霰彈的處理。所有方案都內建同一份 P-11 0.2.1 自療程式。**

[English](README.en.md) · [下載 v0.3.0-preview.4](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.4) · [安裝與切換](docs/SELECTABLE.md) · [原理與範圍](docs/VARIANTS.md)

直接把 **P11-Enhanced-Selectable-v0.3.0-preview.4-build25480438.zip** 匯入 Arsenal，在「Self-hit scope」下四選一：

| 選項 | 內容 |
|---|---|
| 1. 僅 P-11，首次預選 | 只處理治療槍飛鏢，其他彈丸包含霰彈均略過 |
| 2. 手槍排除霰彈 + P-11 | 八個候選手槍 ID 範圍；排除已知霰彈、多彈丸及表外類型 |
| 3. 廣域排除霰彈 + P-11 | 本機原生武器投射物；使用相同前置排除 |
| 4. 全部含霰彈 + P-11 | 包含霰彈與多彈丸的原生投射物候選；可能造成卡頓 |

第 2、3 項按彈種直接排除，在讀來源武器和逐顆寫入之前跳過。排除表共有 38 個 ID，含已辨識霰彈家族（包括獨頭變體）與表內全部多彈丸；為保守控制效能，也跳過表外未知類型及其他一次多彈丸機制。P-11 未修改。擴展部分仍會核對本機所有者、武器身份、原值，寫前重檢及寫後讀回；沒有 native hook 或生命／體力／彈藥／傷害數值寫入。

32 顆霰彈的合成測試：排除版 **10 次讀取、0 寫入**，包含版 **985 次讀取、32 寫入**。仍遍歷槽位，不能把邏輯讀取量當成 FPS 或零卡頓證據。[效能與來源](docs/PERFORMANCE.md)

## 安裝

關閉遊戲，另外安裝相容 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。停用舊三選一／独立自命中版本，匯入新包、確認範圍、啟用並重新部署。選项互斥，遊戲只載入所選方案。切換或停用也先關閉遊戲，再重新部署。

對應 **Steam build 25480438 / EXE 1.8.46015.0 / loader v17 / API 1 / internal 16**。未知版本停止修改。

P-11 原實作已有使用者基本成功回報；三個擴展方案、霰彈覆蓋及效能仍缺少完整遊戲內驗證，保持預覽版。「全部」是廣域原生投射物，並不保證射線、光束、近戰、爆炸或 entity 投射物均受支援。[驗證記錄](docs/VERIFICATION.md)

P-11 推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。使用者也回報第一人稱朝自己的腳射擊及已啟用 Experimental Infusion 的效果。[P-11 詳情](docs/SELF_HIT.md)

## 完整工具包與更新

**P11-Enhanced-Full-Kit-v0.3.0-preview.4.zip** 含一個四選一模組、公開來源及 Windows x64 離線工具。先解壓，再匯入 `Mods/` 中的 ZIP，外層工具包不是模組。

更新後雙擊 **Collect-HD2-Update.cmd**，會辨識四種範圍、比較指紋及產生維修交接。工具不需 Python，不啟動遊戲、不讀程序、不部署、不上傳；不保證未知版本自動修復。霰彈排除表的來源與更新核對要求一併提供。

修正來源後，維修者可用 **Rebuild-Mods.cmd** 重建四選一包及四個獨立輸入包（Python 3.10+）。歷史 Release 保留。

[建置與移植](docs/PORTING.md) · [更新工具](docs/UPDATE_TOOL.md) · [來源](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)。未選定整體授權，與 Arrowhead Game Studios 無隸屬關係。程式與文件使用 OpenAI 工具協助製作。

升級提示：新包沿用相同模組身份。若 Arsenal 提示重複，使用管理器的替換功能，或先停用並移除舊三選一項目，再匯入新版；不要保留兩個同時啟用。 / Upgrade: the mod identity is unchanged. If Arsenal reports a duplicate, replace the old package or disable/remove its old entry before importing.
