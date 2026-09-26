# 兩個模組頁面的發布資料 / Mod-page publishing kit

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

本批次的 GitHub 發布入口為 [Projectile Collision Filter v0.3.0-preview.6](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6)，維持預覽版。依使用者選擇，**兩個 AyakaMods 頁面目前尚未更新**；以下標題、摘要、正文與封面已備妥，供之後登入並確認發布時使用。

所有路徑以專案根目錄為起點。在工具包內，專案根目錄是 `Source/P11-Enhanced/`。

### 1. 投射物碰撞過濾器

**目標頁面：** [P-11 Self-Hit Healing / P-11 治療手槍自療](https://ayakamods.com/mods/p-11-self-hit-healing-p-11-%E6%B2%BB%E7%99%82%E6%89%8B%E6%A7%8D%E8%87%AA%E7%99%82.4166/)

**雙語標題：** `Projectile Collision Filter / 投射物碰撞過濾器（預覽版）`

**中文摘要：** 讓自己的 P-11 飛鏢透過原生碰撞命中並治療自己。Arsenal 四選一；副武器與廣域範圍仍為候選，包含霰彈的第四項可能造成嚴重性能影響。附離線更新工具與源碼。

**英文摘要：** Let your P-11 darts heal you through native collision. Four Arsenal scopes; expanded scopes remain candidates. Including shotguns may cause severe performance impact. Offline update tools and source included.

| 用途 | 專案相對路徑 |
|---|---|
| 封面 | [`docs/assets/projectile-collision-filter-cover.png`](assets/projectile-collision-filter-cover.png) |
| 中文 Markdown | [`docs/release/MOD-PAGE.zh-TW.md`](MOD-PAGE.zh-TW.md) |
| 英文 Markdown | [`docs/release/MOD-PAGE.en.md`](MOD-PAGE.en.md) |
| 可貼入網站的完整雙語 BBCode 正文 | [`docs/release/MOD-PAGE.bilingual.bbcode`](release/MOD-PAGE.bilingual.bbcode) |

四選一整合版、四個獨立版與維護工具包共六個下載檔，均由 GitHub Release 導航。正文保留 P-11 既有成功回報與其他範圍的證據限制；不要將「手槍全部」改寫成所有副武器機制均已完成。

### 2. 舉槍瞄準自己

**目標頁面：** [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)

**雙語標題：** `Raise Weapon: Aim at Yourself / 舉槍瞄準自己`

**中文摘要：** 將 Raise Weapon／舉槍表情替換為瞄準自己的持槍姿勢。動作包獨立使用；需要 P-11 自療時，另搭配 Projectile Collision Filter。衝刺、射擊與表情同時使用可能卡住。

**英文摘要：** Replaces the Raise Weapon emote with a self-aim pose. Pair separately with Projectile Collision Filter for P-11 self-healing. Combining sprinting, shooting and the emote may cause a softlock.

| 用途 | 專案相對路徑 |
|---|---|
| 封面 | [`docs/assets/raise-weapon-aim-at-yourself-cover.png`](assets/raise-weapon-aim-at-yourself-cover.png) |
| 中文 Markdown | [`docs/release/RAISE-WEAPON.zh-TW.md`](RAISE-WEAPON.zh-TW.md) |
| 英文 Markdown | [`docs/release/RAISE-WEAPON.en.md`](RAISE-WEAPON.en.md) |
| 可貼入網站的完整雙語 BBCode 正文 | [`docs/release/RAISE-WEAPON.bilingual.bbcode`](release/RAISE-WEAPON.bilingual.bbcode) |

本次只準備介紹與封面，保留原動作版本 `2026-09-18` 及原下載檔。封面採用參考 P3R 召喚姿勢的宣傳構圖，不代表動作包新增了 P3R 資源或功能。原有卡住問題仍存在：遇到時取消衝刺或切換武器。

### 3. 之後更新 AyakaMods 的操作

1. 登入有權編輯目標頁面的帳戶，開啟對應頁面的編輯介面。
2. 將上面的雙語標題與摘要填入相應欄位。中英文完整介紹已包含在 BBCode 正文，不需把兩個 Markdown 檔再次拼接。
3. 切到編輯器的 **BBCode／原始碼模式**，開啟對應 `.bbcode` 檔，完整複製內容並替換舊正文。不要把 Markdown 標題或表格直接貼入 BBCode 模式。
4. 上傳對應 PNG 作為頁面封面。正文中的封面連結使用 GitHub 固定版本來源，與封面上傳分開處理。
5. 預覽並核對中英標題、列表、圖片、六檔下載入口與搭配模組連結。動畫頁保留原版本／附件；此文案操作不會更新任何模組二進位檔。
6. 確认有此次發布授權後儲存頁面，再重新開啟公開頁檢查顯示結果。目前只完成本機資料準備，不以檔案存在代替網站已更新。

**維護來源：** 修改 `docs/release/` 中的 Markdown 與 BBCode 原始檔；`docs/` 下的 Markdown 是匯出副本，不要單獨修改。修改正文時，同步調整對應的中文、英文與 BBCode，再執行 `python tools/sync_docs.py --apply`。圖片生成記錄見 [COVER-PROMPTS](COVER-PROMPTS.md)。

## English

The GitHub release for this batch is [Projectile Collision Filter v0.3.0-preview.6](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6), a prerelease. **Both AyakaMods pages remain unchanged at the user's request.** The titles, summaries, descriptions and covers above are ready for a later authorized website update.

All paths are relative to the project root, which is `Source/P11-Enhanced/` inside the toolkit.

| Page | Bilingual title | Cover | Ready-to-paste body |
|---|---|---|---|
| [Projectile Collision Filter / P-11](https://ayakamods.com/mods/p-11-self-hit-healing-p-11-%E6%B2%BB%E7%99%82%E6%89%8B%E6%A7%8D%E8%87%AA%E7%99%82.4166/) | `Projectile Collision Filter / 投射物碰撞過濾器（預覽版）` | [`docs/assets/projectile-collision-filter-cover.png`](assets/projectile-collision-filter-cover.png) | [`docs/release/MOD-PAGE.bilingual.bbcode`](release/MOD-PAGE.bilingual.bbcode) |
| [Raise Weapon: Aim at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/) | `Raise Weapon: Aim at Yourself / 舉槍瞄準自己` | [`docs/assets/raise-weapon-aim-at-yourself-cover.png`](assets/raise-weapon-aim-at-yourself-cover.png) | [`docs/release/RAISE-WEAPON.bilingual.bbcode`](release/RAISE-WEAPON.bilingual.bbcode) |

The Chinese and English summaries are provided above. Complete Markdown versions are [PCF Chinese](MOD-PAGE.zh-TW.md), [PCF English](MOD-PAGE.en.md), [animation Chinese](RAISE-WEAPON.zh-TW.md) and [animation English](RAISE-WEAPON.en.md); their editable sources are under `docs/release/`.

To update the pages later:

1. Sign in to an account that can edit each target page.
2. Enter its bilingual title and summary in the relevant fields. Each BBCode file already contains both languages.
3. Switch the description editor to **BBCode/source mode** and replace the old body with the complete matching `.bbcode` file. Do not paste Markdown tables or headings into that mode.
4. Upload the matching PNG as the page cover. The cover link inside the description uses the fixed GitHub tag and is separate from this upload.
5. Preview both languages, images, lists, the six-file download link and companion links. Keep the animation mod's existing `2026-09-18` version and attachment. This description update changes no mod binary.
6. Save only when the website update is authorized, then reopen the public page and verify the result. Local files alone do not mean the website was updated.

The animation cover references the P3R summoning pose for promotional composition; it does not claim that P3R assets or functionality were added to the animation package. The existing sprint/shoot/emote softlock remains documented; cancel sprinting or switch weapons if it occurs. The PCF copy retains the original P-11 success report and the unverified or unsupported parts of the expanded scopes.

Edit the Markdown and BBCode sources under `docs/release/`, keep both languages and BBCode in sync, then run `python tools/sync_docs.py --apply`. Markdown files directly under `docs/` are generated copies. Image-generation records are in [COVER-PROMPTS](COVER-PROMPTS.md).
