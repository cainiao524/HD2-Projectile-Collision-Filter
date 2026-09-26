# P11-Enhanced 完整工具包 / Full kit

此工具包包含 **一個三選一模組 ZIP**、Windows x64 離線更新工具，以及完整公開來源。

1. 解壓此工具包。外層 ZIP 不能直接匯入 Arsenal。
2. 關閉遊戲，把 `Mods/P11-Enhanced-Selectable-v0.3.0-preview.3-build25480438.zip` 匯入 Arsenal。
3. 停用舊自命中版本；在新模組內選「僅 P-11／手槍系列＋P-11／廣域武器＋P-11」其中一項，啟用並重新部署。
4. 首次匯入預選僅 P-11。所有方案含原 P-11 0.2.1；擴展 0.1.1 仍是候選。[使用說明](docs/SELECTABLE.md)

對應 build 25480438，需另裝 Bingus Shared Loader v17 / API 1 / internal 16。本次沒有改動任何遊戲內程式，選擇不增加掃描負擔；原方案的效能界限仍在。

推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，從原頁另行下載。動作、追蹤模組和 loader 沒有放入本包。

更新後雙擊 **Collect-HD2-Update.cmd**，查看 diagnostics 最新資料夾中的「摘要.md」和「維修交接.md」。不需 Python，不啟動遊戲、不讀程序、不部署、不上傳，不保證未知版本全自動修復。[工具說明](docs/UPDATE_TOOL.md)

Source 內為公開来源 ZIP。維修者修正相容性後，可用 Rebuild-Mods.cmd 重建單包及三個原始獨立輸入包（需 Python）。MOD-SHA256SUMS.txt 可核對 Mods。私人診斷和遊戲二進位檔不要公開上傳。

## English

Extract the full kit, then import the single selectable ZIP in Mods into Arsenal. Enable one of its three exclusive sub-options; every choice includes the original P-11. Disable older standalone variants. Install the compatible loader separately. Expanded gameplay remains unverified.

Collect-HD2-Update.cmd creates offline diagnostics and a repair handoff without Python, game launch, process access, deployment or upload. Automatic repair is not guaranteed. Source includes reproducible builders. The linked animation companion is optional and not bundled.
