# 0.1.1 篩選與讀取量比較 / Filtering and read counts

這次修正只影響兩個擴展候選，三包內的 P-11 0.2.1 Lua 和原 P-11 單獨 ZIP 完全不變。資料 writer 也未改動。

0.1.0 會對每個符合初步条件的本機投射物，重複查武器登記、武器身份、附件和定義。手槍範圍在較後面才排除主武器；霰彈等多投射物情境會放大這些查詢。

0.1.1 的變更：

- 先檢查佔用與来源排除旗標（0x22）。只有遇到候選時才載入需要的彈種類型頁；沒有候選就不讀類型頁。旗標不是本機所有權證據。

- 依来源武器 ID 在同一次更新內保存發現結果。非手槍／P-11 先被排除，不查不需要的附件與定義。
- 其餘同來源的不合格彈丸略過武器重複查詢；不同武器即使使用同彈種，也分別分類。
- 合格武器與定義共用發現結果，但完整依賴欄位仍帶到每顆投射物的 writer 重新讀回比較。
- 每顆來源、槽位類型、auxiliary 參考、原旗標和寫後讀回保持檢查。auxiliary 不當成 generation ID。
- 快取不跨更新保存；前一更新的接受／拒絕結果不會成為新更新的依據。
- 槽位類型與旗標用直接位元組解碼，避免每個槽位反覆建立 FFI 值及切片。

仍遍歷固定 2,048 個原生槽位；沒有新增未经驗證的彈種白名單、發射通知或跨更新槽位地址快取。不是零開銷方案。

## 合成資料比較

以同一來源武器、相同可讀布局與 mock writer 執行新舊核心。數字包含 fixture 的依賴重檢讀取，但不代表完整 Windows API 呼叫數、CPU 時間、FPS 或原生碰撞工作量。

| 同次更新情境 | 彈丸數 | 0.1.0 讀取 | 0.1.1 讀取 | 減少 |
|---|---:|---:|---:|---:|
| 手槍模式排除自己的主武器 | 12 | 167 | 30 | 82.04% |
| 手槍模式排除自己的主武器 | 32 | 427 | 50 | 88.29% |
| 手槍模式排除自己的主武器 | 64 | 843 | 82 | 90.27% |
| 白名單手槍／廣域模式處理自己的合格彈丸 | 12 | 575 | 385 | 33.04% |
| 白名單手槍／廣域模式處理自己的合格彈丸 | 32 | 1,515 | 985 | 34.98% |
| 白名單手槍／廣域模式處理自己的合格彈丸 | 64 | 3,019 | 1,945 | 35.57% |
| 廣域模式排除其他來源的彈丸 | 32 | 43 | 42 | 2.33% |

兩個核心在上述合成情境中的寫入數相同。合格來源仍受每次更新最多 64 次寫入嘗試的保護；此更新未調高限制。

## 重現

安裝 requirements-dev.txt 後：

```powershell
python mods/weapon_self_hit_candidate/test_lua.py
python mods/weapon_self_hit_candidate/benchmark_reads.py
```

對比舊版時，取 Git 提交 `f0afd5d4ce307dade34622034eaa80a1eeba6674` 的 `mods/weapon_self_hit_candidate/core.lua` 保存為獨立檔案，然後：

```powershell
python mods/weapon_self_hit_candidate/benchmark_reads.py --baseline-core old-core.lua --output read-comparison.json
```

新增 45 個篩選測試斷言，逐一變更快取依賴的 23 個共同欄位，確認後續投射物不能沿用舊資料寫入。另涵蓋不同武器、不同定義、外來來源、跨更新重新分類、槽位改成 P-11，以及來源在處理前改變。沒有執行 native addon 或收集遊戲程序資料。

## English

This update reuses discovery work within a single update and rejects non-pistols earlier. It preserves every cached dependency in the writer's fresh per-projectile validation chain. Discovery reuse is never write authorization, and nothing is cached across updates. Slot decoding no longer creates an FFI scalar for every type/flag.

Original P-11 0.2.1 and the narrow Windows writer are unchanged. The fixed 2,048-slot scan remains. The table measures synthetic logical reads, not full native API counts, frame times or FPS; no claim is made that stutter is eliminated. Expanded gameplay and current-build pistol coverage remain unverified.

## 0.1.2：霰彈在來源讀取之前略過

排除模式依 profile 內建的數字型別集合做常數時間查表，不新增遠端記憶體讀取、不每幀建立分類表。38 種排除集合涵蓋已辨識霰彈與參考表全部 32 個多彈丸種類；另外拒絕表外類型。來源／武器／附件與逐顆寫前重檢只對剩下候選執行。包含版仍保留原完整檢查。

| 32 顆 type 179 的合成情境 | 邏輯讀取 | 寫入 |
|---|---:|---:|
| 手槍排除霰彈（即使武器在白名單） | 10 | 0 |
| 廣域排除霰彈 | 10 | 0 |
| 第四項廣域包含霰彈 | 985 | 32 |

仍需遍歷 2048 槽位，還會讀旗標及需要的類型頁；沒有零效能成本、FPS 或不卡頓保證。大量排除彈丸不消耗寫入數上限，混合的普通投射物仍可處理。

參考表固定於 [Filediver bf0ce329 的 projectile settings](https://github.com/xypwn/filediver/blob/bf0ce329db3cf0043994eb717ea86433c303cb36/datalibrary/projectile_settings.go)，數字資料指紋及 URL 保存於 maintenance/projectile-exclusions-25480438.json。舊命名資料以名稱雜湊、口徑和彈丸數交叉匹配；參考表中原 P-11 對應 type 318 且單彈丸。這些都是離線分類依據，不證明所有當前遊戲武器或其他模組改寫後仍採用同一分類。新 build 必須重新核對。
