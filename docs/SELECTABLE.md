# P11-Enhanced — 一個模組，三種範圍

將 `P11-Enhanced-Selectable-v0.3.0-preview.3-build25480438.zip` 直接匯入 Arsenal。
在同一個模組項目內啟用「Self-hit scope」，再從子選項中選擇一個範圍：

| 方案 | 內容 |
|---|---|
| 僅 P-11 / P-11 only | 原始 P-11 0.2.1 自命中治療；建議先選此項 |
| 手槍系列 + P-11 / Pistols | 同一份 P-11，加上八個候選手槍資源 ID 的投射物 |
| 廣域武器 + P-11 / Broad weapons | 同一份 P-11，加上本機武器的原生投射物；不代表所有傷害系統 |

這是 Arsenal 的互斥子選項：只有選中的方案參與部署。關閉遊戲後切換，再重新部署並啟動遊戲。
首次匯入後請確認子選項及主開關；管理器的匯入啟用偏好由使用者設定控制。
要全部關閉，停用此模組並重新部署。停用舊的三個獨立版本及其他重複自命中 addon，避免重複載入。

目標：Steam build **25480438** / EXE **1.8.46015.0** / Bingus Shared Loader **v17 / API 1 / internal 16**。
Loader 需另外安裝。遊戲版本不符時功能停止修改。

三個方案均保留同一份 P-11 Lua，SHA256：
`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。
本次只改封裝，使用原 P-11 0.2.1 與擴展 0.1.1，沒有增加遊戲內選單或掃描程式。
P-11 已有使用者基本自療成功回報；手槍／廣域擴展與組合共存仍缺少玩法驗證，所以此包是預覽版。
手槍範圍使用離線候選 ID；廣域範圍不涵蓋已驗證的射線、光束、近戰、爆炸及 entity 投射物支援。
效能與各原始方案相同；擴展版仍遍歷槽位，不能承諾消除卡頓。

推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。
本包沒有動作、追蹤或 loader 資源；隊友追蹤保持原作者模組獨立管理。

遊戲更新後使用完整工具包中的 `Collect-HD2-Update.cmd` 收集離線診斷。
它不啟動遊戲、不讀程序、不部署、不上傳，不能保證每次更新自動修復。

## English

Import this selectable ZIP directly into Arsenal. Enable **Self-hit scope** and choose one sub-option:
P-11 only, Pistols + P-11, or Broad weapons + P-11. Close the game before changing the choice and redeploy.
Disable previous standalone self-hit variants. Install the compatible loader separately.
Every choice preserves the original P-11 Lua and the complete corresponding archive byte for byte.
The expanded scopes remain gameplay-unverified candidates; this packaging change adds no runtime work.
The recommended animation mod is linked above and is not bundled.

Manifest format: [Arsenal Sub-options](https://docs.rsnl.gg/mod-builder/options),
[Version 1 schema](https://docs.rsnl.gg/mod-builder/manifest).
