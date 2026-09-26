# P11-Enhanced — 一個模組，三種自命中範圍

一個可直接匯入 Arsenal 的模組 ZIP，在同一項目內選擇 **僅 P-11／手槍系列＋P-11／廣域武器＋P-11**。三個方案均內建同一份 P-11 0.2.1 自療程式。

[English](README.en.md) · [下載 v0.3.0-preview.3](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.3) · [使用說明](docs/SELECTABLE.md) · [範圍介紹](docs/VARIANTS.md) · [更新工具](docs/UPDATE_TOOL.md)

## 安裝

1. 關閉遊戲，單獨安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 將 **P11-Enhanced-Selectable-v0.3.0-preview.3-build25480438.zip** 直接匯入 Arsenal。
3. 停用舊的三個獨立自命中版本、重複 hook 和研究採集 addon。
4. 在此模組的「Self-hit scope」下選一個子選項，啟用模組並重新部署。首次匯入預選「僅 P-11」；模組是否自動啟用取決於管理器設定。
5. 切換範圍或停用時，先關閉遊戲，改好選項後重新部署，再啟動遊戲。

| 子選項 | 內容 | 狀態 |
|---|---|---|
| 僅 P-11 / P-11 only | 原 P-11 0.2.1 自命中治療 | 原實作有使用者基本成功回報 |
| 手槍系列 + P-11 / Pistols | 同一份 P-11 + 八個候選手槍資源 ID 的原生投射物 | 擴展玩法、目前 ID 與組合共存未實測 |
| 廣域武器 + P-11 / Broad weapons | 同一份 P-11 + 本機武器的原生投射物 | 擴展玩法與機制覆蓋未實測 |

三個子選項互斥，未選方案不部署到遊戲。「全部武器」的廣域方案不代表已支援射線、光束、近戰、爆炸或 entity 投射物等全部系統。

目標：**Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**。未知版本停止修改。此包維持預覽版，不把封裝檢查當成玩法驗證。

## 實作與效能

純資料修改：允許合格的本機投射物碰撞發射者，實際命中後由原生規則處理治療或傷害。沒有原生 hook，不寫血量、體力、彈藥或傷害數值。擴展部分排除 P-11，由原始 P-11 addon 處理。

本次只改封裝，三個方案各自的完整資源與之前完全相同。管理器在部署時選方案，不新增遊戲內選單或掃描。擴展 0.1.1 保留同次更新的武器查詢共用和每次寫入重檢；仍遍歷槽位，不能承諾消除卡頓。[效能測試界限](docs/PERFORMANCE.md)

P-11 推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。使用者也回報可第一人稱朝自己的腳射擊，已啟用 Experimental Infusion 時可觸發效果。[P-11 詳情](docs/SELF_HIT.md) · [驗證記錄](docs/VERIFICATION.md)

## 完整工具包

**P11-Enhanced-Full-Kit-v0.3.0-preview.3.zip** 包含一個三選一模組 ZIP、公開來源和 Windows x64 更新工具。先解壓，再將 `Mods/` 中唯一的模組 ZIP 匯入 Arsenal；外層工具包不是可安裝模組。

遊戲及 loader 更新完成後，雙擊 **Collect-HD2-Update.cmd**，收集離線資料、比對三個範圍並產生中文摘要與維修交接。工具不需 Python，不啟動遊戲、不讀程序、不部署、不上傳，也不承諾每次更新全自動修復。

維修者修正版本相容性後，可在來源執行 **Rebuild-Mods.cmd** 重建三選一包及三個原始獨立包（Python 3.10+）。舊獨立 ZIP 仍可在歷史 Release 取得，不要與新包同開。

[建置與移植](docs/PORTING.md) · [來源與依賴](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)。未選定整體授權；與 Arrowhead Game Studios 無隸屬關係。程式與文件使用 OpenAI 工具協助製作。
