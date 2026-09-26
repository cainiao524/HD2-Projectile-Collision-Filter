# 四方案範圍與原理

四個互斥方案均內建同一份 P-11 0.2.1，Lua SHA256：
`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。

1. **僅 P-11**：只處理本機 P-11 的 type 318 飛鏢；霰彈與其他武器原本就不會進入修改流程，成功程式未更改。
2. **手槍排除霰彈**：P-11 加八個候選手槍 ID；先按彈丸種類排除霰彈，再做原本的武器／所有權篩選。
3. **廣域排除霰彈**：P-11 加本機武器原生投射物；同樣先排除霰彈。
4. **全部含霰彈**：P-11 加包含霰彈與多彈丸的廣域候選，逐顆保留完整身份與寫前重檢；可能造成較高負擔。

第 2、3 項的 38 個排除 ID 包含 27 個可由舊名稱與當前參考表欄位對上的霰彈記錄，以及表內全部 32 個多彈丸記錄的聯集。名稱匹配使用三個名稱雜湊、口徑、彈丸數；不同數字 ID 可共用同名資料。包括霰彈的獨頭變體；其他一次多彈丸機制也保守略過。表外類型不進入後續查詢。詳見 maintenance/projectile-exclusions-25480438.json 與 [來源界限](PERFORMANCE.md)。

手槍資源候選：P-2 Peacemaker、P-4 Senator、P-19 Redeemer、P-69 Veto、P-92 Warrant、P-113 Verdict、P/40-K Bolt Pistol、M6C SOCOM Pistol。清單來自較早離線索引，尚未驗證目前遊戲內所有實例。霰彈排除優先於這份武器清單，因此即使合格手槍發出排除彈種也不修改。

擴展核心始終排除 P-11 資源及 type 318，由同包原 P-11 addon 處理。只有本機來源、有效武器登記與附件所有者核對通過後，才清除槽位 0x20；保留其他位元、寫前完整依賴核對和寫後讀回。沒有全域定義、血量、體力、彈藥或傷害數值寫入。

第四項並不擴展到其他原生機制：射線、光束、近戰、爆炸和 entity 投射物仍未驗證。所有擴展、組合共存與並行時序仍是候選。未知遊戲版本停止修改，不能只替換雜湊。

## English

Four exclusive choices: original P-11; pistols excluding shotguns; broad native projectiles excluding shotguns; or broad including shotguns. Every choice includes unchanged P-11. The filtered scopes reject the union of known shotgun records and every multishot record in the pinned table, plus out-of-table types, before source lookup. This also conservatively skips other multishot mechanisms.

Expanded guards remain unchanged, and the fourth choice retains per-projectile work. Pinned offline classification does not prove complete current-game weapon coverage, timing, native collisions or FPS. Broad is not universal damage-system support.
