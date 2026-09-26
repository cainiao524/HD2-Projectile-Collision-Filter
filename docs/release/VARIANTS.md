# 四種生效範圍與實現原理 / Scopes and Implementation

**目前版本：preview.6 預覽版／手槍 0.1.3 candidate。** 手槍範圍改以裝備副武器槽位 catalog 產生 16 個原生處理來源候選，尚未完成所有可射擊副武器。Dagger beam／Crisper spray 未支援，Warrant／P33／Hornet entity 後續鏈未證明。歷史 preview.5 保留舊八個候選 ID。[副武器分類與機制支援](SECONDARIES.md)

四個方案互斥，全部包含同一份 P-11 0.2.1。P-11 Lua SHA-256：
`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。

| 選項 | 程式實際處理範圍 |
|---|---|
| **僅治療手槍** | 僅本機 P-11 的 type 318 飛鏢；其他武器包括霰彈均略過 |
| **手槍全部** | 同一份 P-11 加副武器候選；preview.5 為八個 ID，preview.6 以固定槽位 catalog 產生部分原生／entity 來源 lookup；先排除霰彈與多彈丸，再檢查來源武器和所有權 |
| **全部武器不包括霰彈槍** | 同一份 P-11 加支援的本機原生武器投射物；同樣先排除霰彈 |
| **全部武器包括霰彈槍** | 同一份 P-11 加包含霰彈、多彈丸的原生投射物候選；**可能造成嚴重性能影響** |

整合版與同版對應獨立版使用相同遊戲資源。名稱不等於覆蓋證據；「手槍全部」的目標雖包含雷射、電漿與榴彈等可射擊副武器，目前仍不是全部機制已實現或已驗證。「全部武器」也不是所有傷害機制；第 4 項未因新的副武器分類增加射線、光束、近戰、爆炸或 entity 投射物支援。

## 投射物資料修改

只識別本機玩家射出的有效武器投射物。核對槽位仍有效、來源與所有者、武器登記／附件、類型、原旗標和版本後，才清除旗標中的來源碰撞排除位元 `0x20`，保留其他位元。寫前重新檢查依據，寫後讀回確認；實際碰撞和效果由遊戲原生邏輯處理。

不修改全域武器定義、生命值、體力、彈藥或傷害數值，也沒有 native hook。關閉功能後不再處理新彈丸，既有投射物保留原生生命週期，不把失效槽位當作可還原物件。

擴展核心排除 P-11 資源與 type 318，由同包獨立的原始 P-11 addon 處理。這避免兩套核心重複修改 P-11。仍需對每顆適用投射物做身份與寫前核對，不能把一次分類視為永久授權。

## 霰彈與手槍分類

第 2、3 項的 38 個排除 ID 是 27 個已辨識霰彈記錄與參考表內全部 32 個多彈丸記錄的聯集。霰彈包括獨頭變體；其他一次多彈丸機制亦保守排除，參考表外類型略過。排除發生在來源／武器查詢之前，主武器和手槍使用同一規則。第 1 項只認 P-11，天然不處理霰彈。

preview.5 的歷史手槍清單為 P-2 Peacemaker、P-4 Senator、P-19 Redeemer、P-69 Veto、P-92 Warrant、P-113 Verdict、P/40-K Bolt Pistol、M6C SOCOM Pistol；它不構成完整副武器分類。preview.6 的 maintenance/secondary-catalog-25480438.json 完整保留固定參考的 27 個槽位記錄，其中 20 個有已知射擊元件、排除 Bushwhacker 後 19 個含 P-11；16 個來源 lookup 是候選，不等於各機制已實現。這不是當前遊戲可取得清單的證明。EquipmentType 是 AI 分類，不能代替副武器槽位。完整 roster 與機制狀態見 SECONDARIES；霰彈策略排除與機制未支援分開記錄。

排除資料來源與指紋記錄於 `maintenance/projectile-exclusions-25480438.json`；名稱對照使用三個名稱雜湊、口徑及彈丸數。數字匹配是離線證據，不能代表当前版本玩法已驗證。[效能與來源界限](PERFORMANCE.md)

## 更新界限

未知版本停止修改。更新必須重新核對資料布局、身份與所有權、寫入條件、霰彈分類和碰撞時機；不能只換雜湊或套用候選地址。

P-11 有既有基本自療成功回報。三種擴展方案的自傷、武器覆蓋、與 P-11 的原生共存及並行時序仍是候選。固定槽位掃描仍存在，排除霰彈不等於零性能開銷。[驗證記錄](VERIFICATION.md) · [逐步接手指南](AGENT_GUIDE.md)

## English

The four exclusive scopes all include original P-11 0.2.1. They correspond to **Stim pistol only**, **All handguns**, **All weapons excluding shotguns**, and **All weapons including shotguns**. The first three exclude shotgun and multishot types; the fourth may cause severe performance impact. See the [player guide](SELECTABLE.md) for the exact Chinese Arsenal labels and installation steps.

Preview.6 replaces the historical eight-ID pistol list with 16 source candidates derived from pinned sidearm-slot data. This includes native candidates for plasma and grenade weapons. The catalog records 27 sidearm entries, 20 with known firing components and 19 after excluding Bushwhacker, including P-11. These counts describe reference data, not confirmed current-game availability or successful self-hit behavior. Dagger beam and Crisper spray are unsupported; Warrant, P33 and Hornet entity follow-up paths remain unresolved. The broad fourth scope does not add those missing mechanisms.

For eligible local native projectile slots, the addon checks game identity, source weapon, local ownership, live slot state and original flags, then clears only the runtime source-collision exclusion bit 0x20. It repeats dependency checks before writing and reads the result back. Native collision and effects remain responsible for actual hits. It does not patch executable code or write global weapon definitions, health, stamina, ammunition or damage values. P-11 is delegated to the unchanged original addon to avoid overlapping writes.

Shotgun/multishot rejection happens before source and weapon lookups; filtered scopes also skip unknown types outside the reference table. A fixed slot scan remains, so this is not a zero-overhead or stutter-free claim. Unknown versions stop modification. Offline matches, catalog validation and mock tests do not verify native collision timing, healing, damage, multiplayer coexistence or game FPS.
