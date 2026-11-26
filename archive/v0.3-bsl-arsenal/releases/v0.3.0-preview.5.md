# Projectile Collision Filter：四選一、六檔下載與完整維護指南

本版整理選項文案、下載結構和 AI／Agent 接手流程。**自命中實作與霰彈排除規則不變，四個獨立模組包保持原始內容。**

四選一整合模組更名為 **Projectile Collision Filter（投射物碰撞過濾器）**；GitHub 專案仍為 P11-Enhanced，原模組身份不變，可替換舊整合包升級。四個選項名稱與獨立包保持以下內容。

## 選擇「生效範圍」

| 選項 | 說明 |
|---|---|
| **僅治療手槍** | 僅讓 P-11 治療飛鏢對自己生效。推薦，首次預選。 |
| **手槍全部** | 包含 P-11 與目前支援的手槍；排除霰彈及多彈丸類型。 |
| **全部武器不包括霰彈槍** | 包含 P-11 與支援的武器投射物；排除霰彈及多彈丸類型。 |
| **全部武器包括霰彈槍** | 包含霰彈及多彈丸類型，**可能造成嚴重性能影響**。 |

前三項排除霰彈；第四項需主動選用。「手槍全部」受現有八個候選手槍 ID 限制；「全部武器」指目前支援的原生投射物，沒有宣稱支援全部射線、光束、近戰、爆炸或 entity 投射物。

## 六個下載檔

**模組五選一啟用；工具包另行解壓，不匯入 Arsenal。**

| 檔案 | 用途 |
|---|---|
| Projectile-Collision-Filter-v0.3.0-preview.5-build25480438.zip | 推薦：整合版，Arsenal 內四選一 |
| P11-Self-Hit-DataOnly-0.2.1-build25480438.zip | 僅治療手槍，原成功包不變 |
| weapon_self_hit_pistols-0.1.2-build25480438-CANDIDATE.zip | 手槍全部，排除霰彈 |
| weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip | 全部武器不包括霰彈槍 |
| weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip | 全部武器包括霰彈槍；**可能造成嚴重性能影響** |
| P11-Enhanced-Update-Toolkit-1.3.0-win-x64.zip | 可攜離線收集、完整源碼與接手／修補／發布指南 |

工具包中的源碼直接位於 Source/P11-Enhanced/，沒有內層 Source ZIP；不另發 Full Kit、Source ZIP 或校驗文字檔。六項校驗值附在本頁。GitHub 自動的 Source code 連結是額外來源下載。

## 安裝與維護導航

關閉遊戲，停用舊整合版／獨立自命中包，匯入一個新版模組、確認選項、啟用並重新部署。相同模組身份提示重複時，使用替換功能或停用／移除舊項目後匯入。切換和停用亦先關閉遊戲，再重新部署。

- [玩家操作指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/docs/SELECTABLE.md)
- [離線更新工具](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/docs/UPDATE_TOOL.md)
- [AI／Agent 接手入口](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/AGENTS.md)
- [逐步維修指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/docs/AGENT_GUIDE.md)
- [建置與移植](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/docs/PORTING.md)
- [驗證與發布](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/docs/PUBLISH.md)

Update Toolkit 1.3.0 會一次收集可取得的離線資料、比較四項功能並產生維修交接。不啟動遊戲、不讀程序、不部署、不上傳，不保證未知版本全自動修復。未知／加密資料不足時列明缺口，不以候選地址或換雜湊强行啟用。

對應 **Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**。P-11 原始基本自療有使用者成功回報；擴展、分類完整覆蓋、共存及效能仍未全面玩法驗證，因此繼續標為預覽版。仍有槽位掃描，不保證零開銷。

推薦另外下載 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)。隊友追蹤及動作模組保持獨立，不附帶、不改動。舊 Release 保留供回退。

## English

This preview simplifies four Arsenal labels, publishes five alternative mod ZIPs plus one maintenance toolkit, and adds a complete developer/AI-agent runbook. Runtime behavior, original P-11 and all four standalone package bytes are unchanged.

The selectable mod is renamed Projectile Collision Filter; the P11-Enhanced repository and the mod identity stay unchanged.

Enable only one mod package. The first three scopes exclude shotguns; the fourth includes them and may cause severe performance impact. Toolkit 1.3.0 includes directly accessible source under Source/P11-Enhanced and offline diagnostics with a repair handoff. It does not launch the game, read processes, deploy, upload or guarantee automatic repair.

Only original P-11 basic healing has user confirmation. Expanded behavior, full current-game coverage and performance remain unverified candidates. Historical release assets remain available.
