# 三版本介紹 / Three variants

三包擇一安裝，**每包都內建相同的 P-11 0.2.1 自療 Lua**。三個包內該資源的 SHA256 都必須為：
`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。

P-11 單獨 ZIP 保留成功的原始位元組。兩個擴展 ZIP 將原始 P-11 與獨立擴展 Lua 放入同一資源封裝；不合併或改寫 P-11 程式。擴展核心排除 P-11 資源及 318 飛鏢類型。

## 僅治療槍 0.2.1

本機玩家、P-11 與單發飛鏢身份通過後，清除 runtime 來源碰撞排除位元 `0x20`。真實飛鏢撞到角色後由原生治療處理。使用者已確認基本功能；完整介紹見 [SELF_HIT.md](SELF_HIT.md)。

## 手槍系列 0.1.1 候選

內建上述 P-11，另以八個候選武器資源 ID 篩選自己射出的原生投射物：
P-2 Peacemaker、P-4 Senator、P-19 Redeemer、P-69 Veto、P-92 Warrant、P-113 Verdict、P/40-K Bolt Pistol、M6C SOCOM Pistol。

名單來自較早離線模組索引，尚未核對目前遊戲內實例。名稱不代表武器一定經過這套原生槽位。**未有其他手槍自命中或傷害實測確認。**

## 全部武器範圍 0.1.1 廣域候選

內建上述 P-11，另處理本機有效武器所屬的原生投射物，保留武器登記及附件所有權檢查。去掉手槍白名單，並不代表支援全部傷害系統。射線、光束、近戰、爆炸或 entity 投射物路徑未驗證。

## 共同邏輯與界限

只清除槽位 `0x20`，保留其他位元。寫入前核對原值及依賴欄位，写後讀回。沒有全域武器定義修改、生命或傷害數值寫入，也不提供無敵。實際結果仍取決於原生碰撞、傷害或治療規則。

所有功能由選定套件的 Arsenal 開關管理。手槍與廣域同開會使擴展部分停止；請三包擇一，切换時停用舊版並重新部署。

Lua 時序可能晚於碰撞查詢，並行槽位重用的原子性未證明。保留成功 P-11 程式與模擬通過，不等於兩個新封裝已有遊戲內共存確認。

## English

All three packages include the exact original P-11 Lua, verified by SHA256. The expanded packages contain two independent Lua resources in one archive; expanded logic excludes P-11 and leaves it to the unchanged healing addon. Install only one variant.

The pistol scope uses eight offline-derived resource IDs. The broad scope drops that allowlist while retaining ownership, valid weapon-registration and attachment checks. Neither expanded scope has gameplay confirmation, and the broad scope is not universal weapon coverage. Timing, concurrency and combined coexistence remain unverified.
