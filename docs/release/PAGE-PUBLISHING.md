# 兩個模組頁發布素材 / Mod-page publishing kit

[GitHub preview.8 Release](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8) · [倉庫](https://github.com/cainiao524/HD2-Projectile-Collision-Filter)。本批次交付 GitHub 和可貼用的 AyakaMods 素材，**不以本機文案存在代表兩個 AyakaMods 頁面已更新**。

以下檔案以專案根為準；Toolkit 中專案根為 `Source/HD2-Projectile-Collision-Filter/`。完整 BBCode 已包含英文在前、繁體中文在後的正文，不需再把兩份 Markdown 拼接。

## 1. Projectile Collision Filter

**目標頁面：** [P-11 Self-Hit Healing](https://ayakamods.com/mods/p-11-self-hit-healing-p-11-%E6%B2%BB%E7%99%82%E6%89%8B%E6%A7%8D%E8%87%AA%E7%99%82.4166/)

**英文標題：** `Projectile Collision Filter — P-11 Self-Healing & Four Selectable Scopes`

**中文標題：** `Projectile Collision Filter｜投射物碰撞過濾器・P-11 自療與四種範圍`

**雙語短標題（標題欄較短時）：** `Projectile Collision Filter / 投射物碰撞過濾器`

**中文摘要：** 讓自己的 P-11 飛鏢透過原生碰撞命中並治療自己。Arsenal 雙語四選一，共用游標核心。附離線更新工具與完整源碼；包含霰彈的第四項可能造成嚴重性能影響。

**English summary:** Let your P-11 darts heal you through native collision. Four bilingual Arsenal scopes share one cursor-based core. Offline update tools and complete source included. Including shotguns may cause severe performance impact.

| 素材 | 可直接使用的檔案 |
|---|---|
| 新封面 PNG | [projectile-collision-filter-cover.png](assets/projectile-collision-filter-cover.png) |
| 繁體中文 Markdown | [MOD-PAGE.zh-TW.md](MOD-PAGE.zh-TW.md) |
| English Markdown | [MOD-PAGE.en.md](MOD-PAGE.en.md) |
| 完整雙語 BBCode | [MOD-PAGE.bilingual.bbcode](MOD-PAGE.bilingual.bbcode) |

下載導航只有整合 Mod 和 Toolkit 兩個 ZIP。四種範圍在同一模組中選擇，不再列四個獨立下載；第四項的性能警告不得省略。四項使用者基本回報不代表所有副武器機制或性能已全面測試。

## 2. Raise Weapon: Aim at Yourself

**目標頁面：** [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)

**英文標題：** `Raise Weapon: Aim at Yourself — Animation Mod`

**中文標題：** `Raise Weapon: Aim at Yourself｜舉槍瞄準自己`

**雙語短標題：** `Raise Weapon: Aim at Yourself / 舉槍瞄準自己`

**中文摘要：** 將 Raise Weapon／舉槍表情替換為瞄準自己的持槍姿勢。動作包獨立使用；需要 P-11 自療時，另搭配 Projectile Collision Filter。衝刺、射擊與表情同時使用可能卡住。

**English summary:** Replaces the Raise Weapon emote with a self-aim pose. Pair separately with Projectile Collision Filter for P-11 self-healing. Combining sprinting, shooting and the emote may cause a softlock.

| 素材 | 可直接使用的檔案 |
|---|---|
| 新封面 PNG | [raise-weapon-aim-at-yourself-cover.png](assets/raise-weapon-aim-at-yourself-cover.png) |
| 繁體中文 Markdown | [RAISE-WEAPON.zh-TW.md](RAISE-WEAPON.zh-TW.md) |
| English Markdown | [RAISE-WEAPON.en.md](RAISE-WEAPON.en.md) |
| 完整雙語 BBCode | [RAISE-WEAPON.bilingual.bbcode](RAISE-WEAPON.bilingual.bbcode) |

保留原動作版本 **2026-09-18** 和原下載附件。本次只整理文案與封面，不修改動作檔、不宣稱修復原有 sprint／shoot／emote 卡住問題；遇到時取消衝刺或切換武器。

新封面以藍色碎片、角色豎持手槍呈現，槍口朝上且遠離頭部。它是宣傳構圖，並非 P3R 召喚姿勢或遊戲內自瞄準動作的精確重現；不表示新增 P3R 資源或功能。

## 貼到 AyakaMods / Paste workflow

1. 登入有權編輯相應頁面的帳戶，開啟該頁編輯。Sign in to an account with edit access.
2. 填入選定的標題和摘要；若網站限制標題長度，使用上面的雙語短標題。Enter title and summary; use the supplied shorter bilingual title if needed.
3. 切到 **BBCode／source 模式**，完整貼上相應 `.bbcode` 內容。不要把 Markdown 表格貼入 BBCode。Paste the matching complete BBCode file in source mode.
4. 上傳該模組的新 PNG 作封面；正文固定版本圖片 URL 與頁面封面欄是兩個位置。Upload the matching PNG as the page cover.
5. 預覽英文與繁中、列表、圖片、兩 ZIP 下載和搭配連結；動畫頁保留舊附件／版本。Preview both languages, cover, links and download counts; keep the animation package unchanged.
6. 在實際進行已授權網站編輯時儲存，重新開公開頁核對。Save during the authorized website-editing task and reopen the public page to verify.

可編輯來源是 `docs/release/` 的 Markdown／BBCode；根 README、`docs/` 及 `releases/` 是 document_exports 生成副本。原始檔修改後執行 `python tools/sync_docs.py --apply`，檢查差異並一起提交。封面來源見 [COVER-PROMPTS](COVER-PROMPTS.md)。

## English

This kit supplies both complete AyakaMods page bodies, titles, summaries and replacement covers. The GitHub prerelease has exactly two manually uploaded ZIPs: the selectable mod and the offline source-inclusive toolkit. Local copy does not mean either AyakaMods page has been edited.

The animation page keeps its existing 2026-09-18 download and documented softlock. Its new blue cover holds the pistol upright away from the helmet; it is promotional artwork rather than an exact rendering of the in-game pose. For maintenance, edit docs/release sources and regenerate docs copies using tools/sync_docs.py --apply.
