# P11-Enhanced — 三種武器自命中範圍

讓自己射出的投射物有機會命中自己的角色，再由原生碰撞處理治療或傷害。純資料修改，沒有原生 hook，不寫血量、體力、彈藥或傷害數值。

[English](README.en.md) · [下載](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.2) · [三版本介绍](docs/VARIANTS.md) · [P-11 詳細介紹](docs/SELF_HIT.md) · [更新工具](docs/UPDATE_TOOL.md)

## 三個版本，擇一安裝

**三個 ZIP 都內建同一份已獲使用者基本成功回報的 P-11 0.2.1 自療程式。** 不需額外安裝 P-11。手槍／廣域部分避開 P-11，由各包內保留原始位元組的 P-11 addon 處理，避免互相改寫。

| 下載檔案 | 範圍 | 驗證狀態 |
|---|---|---|
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | 僅 P-11 治療槍 | 使用者確認基本自命中治療有效；原始成功 ZIP |
| `weapon_self_hit_pistols-0.1.1-build25480438-CANDIDATE.zip` | P-11 + 八個候選手槍資源 ID 的原生投射物 | 內建原 P-11；擴展玩法與組合共存未實測 |
| `weapon_self_hit_native-0.1.1-build25480438-CANDIDATE.zip` | P-11 + 廣泛本機武器的原生投射物 | 內建原 P-11；擴展玩法與組合共存未實測 |

「全部武器版」是廣域原生投射物候選的簡稱。射線、光束、近戰、爆炸機制和 entity 投射物未在此方案內驗證。手槍清單來自较早離線資源索引，不能當成八種已實測可用的武器。

目標：**Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**。未知版本停止修改。合集標為 **預覽版**；保留成功程式不等於已證明擴展套件在所有場景有效。

## 0.1.1 篩選修正

擴展版按來源武器共用同次更新的查詢，手槍模式更早排除非手槍；所有實際寫入保留逐顆依賴重檢。32 顆主武器彈丸的合成測試中，手槍模式讀取 427 → 50，廣域模式 1,515 → 985。這是邏輯讀取次數，**不代表 FPS 提升或已證明卡頓消失**。仍遍歷固定槽位；原 P-11 0.2.1 未修改。[詳細比較](docs/PERFORMANCE.md)

## 安裝與使用

1. 關閉遊戲，單獨安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。
2. 將三個版本中的 **一個 ZIP** 匯入 Arsenal，停用另兩版、舊自命中 hook、重複版本及研究採集 addon。
3. 在 Arsenal 啟用所選項目並按管理器／loader 說明部署。兩個擴展版的單一開關會一起控制內含的 P-11 與擴展功能。
4. 停用時也先關閉遊戲，再取消項目並重新部署。

P-11 推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)。動作模組另外下載。本模組不自動轉向飛鏢；使用者也回報可第一人稱朝自己的腳射擊，已啟用 Experimental Infusion 時可觸發效果。[驗證範圍](docs/VERIFICATION.md)

## 合集與更新工具

下載 **P11-Enhanced-Three-Variants-v0.3.0-preview.2.zip** 可取得三個獨立安裝 ZIP、完整來源和 Windows x64 工具。先解壓，再將 `Mods/` 裡所選 ZIP 匯入 Arsenal；外層合集不能直接當成模組安裝。

遊戲及 loader 更新完成後，雙擊 **Collect-HD2-Update.cmd**。portable 工具不需 Python，會產生中文摘要、三範圍相容性比較、互斥偵測與維修交接包。不啟動遊戲、不讀程序、不部署、不上傳。

工具負責一次收齊可取得的離線資料，**不保證每次更新全自動修復**。維修者修正版本相容性後，可在來源雙擊 **Rebuild-Mods.cmd** 一次重建三包（需 Python 3.10+）。[維修與建置](docs/PORTING.md)

[來源與依賴](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)。未選定整體授權；與 Arrowhead Game Studios 無隸屬關係。程式與文件使用 OpenAI 工具協助製作。
