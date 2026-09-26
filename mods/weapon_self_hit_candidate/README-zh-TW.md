# 全武器自傷／手槍系列：獨立候選版 0.1.1

本機提供兩個 Arsenal ZIP，**二選一啟用**：

| 套件 | 候選處理範圍 |
| --- | --- |
| `weapon_self_hit_pistols-0.1.1-build25480438-CANDIDATE.zip` | P-2 Peacemaker、P-4 Senator、P-19 Redeemer、P-69 Veto、P-92 Warrant、P-113 Verdict、P/40-K Bolt Pistol、M6C SOCOM Pistol 的已定位物件資源；僅處理這些武器產生且通過身份檢查的原生投射物 |
| `weapon_self_hit_native-0.1.1-build25480438-CANDIDATE.zip` | 本機角色持有、武器登記表與附件所有者均匹配的原生投射物；**不代表所有武器類型均受支援** |

這兩個 ZIP 是**未經遊戲內驗證的候選模組**。離線測試只確認它們在模擬資料中篩選、清除 `0x20` 位元並拒絕錯誤身份。**未驗證任何其他武器確實能打中自己或造成自傷**。不同武器可能使用射線、光束、近戰、爆炸或 entity 投射物，並不經過這套 2048 槽的原生投射物系統；即使改到槽位，Lua 更新時序也可能太晚。

已成功使用的 **P-11 自療 0.2.1** 以原始 Lua 位元組內建於這兩包。擴展核心會排除 P-11 資源及其已知的 318 類型，由同包的獨立 P-11 addon 處理；沒有改寫成功程式。候選版只改自己射出的、仍有效的投射物槽位旗標，不直接寫角色生命／體力、武器傷害值或彈藥。它不包含 hook、不改 executable code、不接管 loader 啟動或音效資源。追蹤與瞄準動作模組不屬於此套件。

## 啟用方式

1. 對照遊戲與 loader 版本。此候選版只接受遊戲 build `25480438` 的精確 DLL／EXE 雜湊，以及 Bingus Shared Loader API 1／內部版本 16。版本不符會停用。
2. 在 Arsenal 匯入**其中一個**候選 ZIP，啟用其唯一選項，再依 Arsenal 流程部署。不要同時啟用這兩個候選項目；它們會互相檢出並停用。兩個候選包都已內建原始 P-11 0.2.1，不需額外安裝；三個自命中套件擇一。
3. 日誌在 `%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\WeaponSelfHitCandidate.log`。`ENABLED` 僅表示版本與載入映像檢查通過；`FIRST DATA WRITE READ BACK` 僅表示一次資料寫入讀回，**不是**命中或傷害證據。
4. 若不再使用，在遊戲關閉時於 Arsenal 停用候選項目並重新部署。已發射投射物由遊戲原生生命週期處理，模組不從舊槽位回寫。

## 原理與來源限制

從本機玩家身份取到來源 unit，再用武器登記表、有效武器物件與附件所有者核對每個候選槽；手槍模式還比對武器物件資源 ID。要求投射物旗標同時帶有佔用 `0x2` 和來源排除 `0x20`，且其定義 ID 能在本版定義表讀回。通過後才對該槽的兩個旗標位元組清除 `0x20`，寫入前再次比較依賴欄位與原值，寫後讀回。每幀重新定位，沒有跨幀保存槽位地址。

手槍名單源於本機較早的模組資源索引，並以 P-11 的已知物件路徑雜湊作交叉檢查；這些 ID **尚未用目前遊戲內的手槍實例驗證**。來源資源名也不能單獨證明該武器使用原生投射物槽。版本核對不能替代玩法驗證。

兩個候選 ZIP 都包含 `Source/weapon_self_hit_candidate.lua`、`Source/profile.json` 和 `Source/VALIDATION.md`。作為 P11-Enhanced 的公開預覽候選提供；未新增遊戲內驗證或自動部署。

## 每包均含 P-11 / P-11 included in both packages

三個版本擇一安裝。兩個擴展包各自包含兩個獨立 Lua 資源，同一 Arsenal 開關控制。P-11 Lua SHA256 固定為 b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a；新包的遊戲內共存仍未驗證。

Both expanded ZIPs include the exact P-11 0.2.1 Lua as a separate resource alongside the candidate. No separate P-11 install is needed. Choose one of the three variants in Arsenal. Expanded gameplay and combined coexistence remain unverified; preserved bytes and mock callback tests are not native gameplay proof.

## 0.1.1 篩選修正 / Filtering update

同一次更新內按来源武器 ID 共用查詢結果。手槍模式先判斷武器範圍，再查附件與彈種定義；同一不合格武器的其餘彈丸只需確認來源便略過。合格來源共用武器及定義的發現結果，但每顆寫入仍重新讀回所有依賴欄位、自己的來源與槽位，拒絕回收重用或所有者變動。快取不跨更新保存。槽位類型與旗標改用直接位元組解碼，減少反覆建立 FFI 值。

依然遍歷 2,048 個原生槽位；沒有增加未驗證的手槍彈種表。零開銷、FPS 提升或實際卡頓消失尚未驗證。P-11 0.2.1 與資料 writer 保持原始位元組。

0.1.1 reuses weapon/definition discovery only within one update. Every write still rechecks the complete dependency chain and its own source/slot; cached discovery never authorizes a write on its own. Rejected weapons skip attachment/definition lookup. The fixed slot scan remains; no zero-overhead or in-game FPS claim is made.
