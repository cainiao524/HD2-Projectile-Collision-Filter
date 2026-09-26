# P11-Enhanced — Three self-hit variants / 三種自命中範圍

**三個版本都內建同一份使用者確認基本有效的 P-11 0.2.1 自療程式，擇一安裝，不需額外加裝 P-11。**

| 模組 | 範圍及狀態 |
|---|---|
| P-11 Self-Hit 0.2.1 | 僅治療槍，保留成功原始 ZIP |
| Pistol Self-Hit 0.1.0 Candidate | P-11 + 八個候選手槍資源 ID，擴展玩法及共存未實測 |
| All Native Weapon Projectiles 0.1.0 Candidate | P-11 + 廣域原生投射物，擴展玩法及共存未實測；不代表全武器機制 |

目標 build 25480438 / EXE 1.8.46015.0 / loader v17、API 1、internal 16。純資料修改，沒有原生 hook 或直接血量寫入。

**P11-Enhanced-Three-Variants-v0.3.0-preview.1.zip** 一次取得所有模組、來源及 Windows x64 portable 工具。解壓後從 Mods 選一個 ZIP 匯入 Arsenal。SHA256SUMS.txt 校驗六個 ZIP。

遊戲更新後雙擊 Collect-HD2-Update.cmd：中文摘要、三範圍相容性檢測、衝突報告和維修交接。不需 Python，不部署或上傳，不承諾每次全自動修復。維修者完成程式／版本移植後可用 Rebuild-Mods.cmd 重建（需 Python）。

推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)。動作模組和 loader 另行下載；沒有包含隊友追蹤程式。P-11 另有使用者回報第一人稱朝腳射擊、已啟用 Experimental Infusion 時觸發效果，證據界限見倉庫文件。

## English

All three ZIPs include the **unchanged P-11 0.2.1 healing Lua**. Choose one in Arsenal: P-11 only, pistols plus P-11, or broad native projectiles plus P-11. No separate P-11 install is needed. Expanded logic excludes P-11 to avoid overlapping writes.

P-11 basic healing is user-confirmed. Both broader scopes and combined gameplay coexistence are **unverified candidates**; byte-identical inclusion is not a new gameplay test. “All weapons” refers to the identified native-projectile subsystem, not universal weapon mechanics. The pistol IDs are offline-derived.

The collection includes three installable ZIPs, source and a self-contained offline Windows x64 update tool. It generates diagnostics and a repair handoff without launching the game, accessing processes, deploying or uploading. It is not guaranteed automatic repair. Rebuild-Mods.cmd packages a reviewed source port.

No native hooks, executable patches, direct health writes, animation packages or teammate-homing code are included. Loader and the recommended companion above are separate downloads.
