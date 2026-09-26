# P11-Enhanced — Projectile Collision Filter

四選一整合模組名稱為 **Projectile Collision Filter（投射物碰撞過濾器）**。GitHub 專案仍名為 P11-Enhanced；原模組身份不變，升級時可替換既有整合包。

**一個 Arsenal 模組、四種生效範圍。前三項排除霰彈，第四項可能造成嚴重性能影響。所有方案都包含同一份 P-11 0.2.1 自療程式。**

[English](README.en.md) · [下載 v0.3.0-preview.5](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.5)

## 從這裡開始

| 我要做的事 | 入口 |
|---|---|
| 安裝、升級、切換範圍或回退 | [玩家操作指南](docs/SELECTABLE.md) |
| 遊戲或 loader 更新後一次收集資料 | [離線更新工具](docs/UPDATE_TOOL.md) |
| 交給 AI／Agent 接手、分析與修補 | [AGENTS.md](AGENTS.md) → [逐步接手指南](docs/AGENT_GUIDE.md) → [建置與移植](docs/PORTING.md) |
| 驗證、建置與發布 | [驗證記錄](docs/VERIFICATION.md) · [發布指南](docs/PUBLISH.md) |

## 選擇生效範圍

將整合版 ZIP 直接匯入 Arsenal，在「**生效範圍**」中四選一：

| 選項 | 說明 |
|---|---|
| **僅治療手槍** | 僅讓 P-11 治療飛鏢對自己生效。推薦，首次預選。 |
| **手槍全部** | 包含 P-11 與目前支援的手槍；排除霰彈及多彈丸類型。 |
| **全部武器不包括霰彈槍** | 包含 P-11 與支援的武器投射物；排除霰彈及多彈丸類型。 |
| **全部武器包括霰彈槍** | 包含霰彈及多彈丸類型，**可能造成嚴重性能影響**。 |

「手槍全部」目前限八個候選手槍識別 ID；「全部武器」指目前支援的原生投射物，並不代表射線、光束、近戰、爆炸或 entity 投射物均已驗證。第 2、3 項也保守略過其他多彈丸機制及參考表外類型。[完整範圍與原理](docs/VARIANTS.md)

## 六個下載檔

[Release](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.5) 提供以下六個 ZIP。**模組只選一個啟用；工具包另行解壓，不匯入 Arsenal。**

| 下載檔 | 用途 |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.5-build25480438.zip` | **推薦**：整合版，Arsenal 內四選一 |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | 固定「僅治療手槍」；保留已使用成功的原始包 |
| `weapon_self_hit_pistols-0.1.2-build25480438-CANDIDATE.zip` | 固定「手槍全部」；排除霰彈 |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | 固定「全部武器不包括霰彈槍」 |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | 固定「全部武器包括霰彈槍」；**可能造成嚴重性能影響** |
| `P11-Enhanced-Update-Toolkit-1.3.0-win-x64.zip` | 離線收集工具、完整源碼、建置工具與接手指南 |

工具包包含可直接開啟的 `Source/P11-Enhanced/`，不必再解壓一層來源 ZIP。六個檔案的 SHA-256 見 Release 正文。GitHub 自動產生的 Source code 連結是額外的原始碼下載入口，不是可直接安裝的模組。舊 Release 保留供回退。

## 安裝與更新

關閉遊戲，另外安裝相容的 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。停用舊版或其他重複自命中包，匯入一個模組 ZIP、確認範圍、啟用並重新部署。切換、停用及回退也先關閉遊戲，再重新部署。若 Arsenal 提示相同模組身份，使用替換功能，或停用並移除舊項目後匯入。

目前目標為 **Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**。未知版本停止修改。遊戲更新後，完整解壓工具包，雙擊 `Collect-HD2-Update.cmd`，查看 `diagnostics` 的中文摘要及維修交接。工具不需 Python，不啟動遊戲、不讀程序、不部署、不上傳；一次收齊可取得的離線資料，不保證未知版本全自動修復。

P-11 推薦搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。隊友追蹤與動作模組由各自原模組管理，本包沒有改動或附帶它們。[P-11 用法](docs/SELF_HIT.md)

P-11 原實作有使用者基本成功回報；擴展範圍、目前遊戲的完整霰彈覆蓋、組合共存及效能仍未全面實測，因此維持預覽版。程式只對經身份與所有權檢查的投射物清除來源碰撞排除位元，讓原生碰撞處理效果，沒有 native hook 或生命／體力／彈藥／傷害數值寫入。仍有槽位掃描，不能承諾零開銷。[效能與證據](docs/PERFORMANCE.md)

[來源聲明](docs/THIRD_PARTY.md) · [授權聲明](LICENSE-NOTICE.md)。整體授權尚未選定；與 Arrowhead Game Studios 無隸屬關係。程式與文件使用 OpenAI 工具協助製作。
