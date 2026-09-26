# P11-Enhanced 四選一完整工具包 / Four-choice full kit

先解壓工具包，把 `Mods/P11-Enhanced-Selectable-v0.3.0-preview.4-build25480438.zip` 匯入 Arsenal。
關閉遊戲，停用舊版，確認範圍並重新部署。首次匯入預選僅 P-11。

四個方案：**僅 P-11／手槍排除霰彈＋P-11／廣域排除霰彈＋P-11／全部含霰彈＋P-11**。
前三項不處理霰彈，第四項需主動選用且可能造成卡頓。第 2、3 項也排除其他表內多彈丸及表外類型。所有方案含原 P-11 0.2.1，擴展 0.1.2 仍為候選。[操作與限制](docs/SELECTABLE.md)

對應 build 25480438、Bingus Shared Loader v17 / API 1 / internal 16。Loader 另外安裝。
推薦 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。追蹤與動作模組未改。

更新後雙擊 **Collect-HD2-Update.cmd**，查看 diagnostics 內「摘要.md」及「維修交接.md」。工具不需 Python，不啟動遊戲、不讀程序、不部署、不上傳，不保證自動修復。
Source 含來源 ZIP，維修後可重建四選一包及四個獨立輸入包（需 Python）。MOD-SHA256SUMS.txt 可核對模組。私人診斷和遊戲二進位檔不要公開上傳。

## English

Extract first, import the one ZIP in Mods into Arsenal and select one of four scopes. The first three exclude shotguns; the fourth opts in. Filtered scopes conservatively exclude all pinned multishot types and unknown types too. All preserve P-11; expanded behavior remains unverified. Disable older variants and redeploy with the game closed.

The offline tool collects evidence and a repair handoff without Python, game launch, process reads, deployment or upload. It does not guarantee automatic repair. Source and checksums are included.

升級提示：新包沿用相同模組身份。若 Arsenal 提示重複，使用管理器的替換功能，或先停用並移除舊三選一項目，再匯入新版；不要保留兩個同時啟用。 / Upgrade: the mod identity is unchanged. If Arsenal reports a duplicate, replace the old package or disable/remove its old entry before importing.
