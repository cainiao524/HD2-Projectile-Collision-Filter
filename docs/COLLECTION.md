# P11-Enhanced Update Toolkit 1.3.0

**這是遊戲更新與維護工具包，不是可匯入 Arsenal 的模組。** 完整解壓後使用；模組整合版及四個獨立版請從同一 Release 分別下載，只啟用一個。

## 遊戲更新後，一次收集

1. 等遊戲／loader 更新及管理器部署完成。
2. 在工具包根目錄雙擊 **Collect-HD2-Update.cmd**。Windows x64 已包含 P11-Update.exe，收集不需安裝 Python。
3. 查看工具旁 diagnostics 中最新資料夾的 **摘要.md** 和 **維修交接.md**。同時產生 ZIP；有缺檔或檔案變動時按摘要處理後重收。
4. 將診斷包留在本機，與隨附源碼一起交給維修者分析。不要把遊戲二進位檔、私人診斷或原始日誌上傳公開倉庫。

工具不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳。收集完整只代表資料穩定，不代表新版玩法已成功，也不保證自動修復。

## 包內導航

| 相對工具包根目錄的位置 | 用途 |
|---|---|
| Collect-HD2-Update.cmd / P11-Update.exe | 一鍵離線收集入口 |
| Source/P11-Enhanced/README.md | 與本版對應的完整專案導航 |
| Source/P11-Enhanced/AGENTS.md | AI／Agent 接手先讀 |
| Source/P11-Enhanced/docs/AGENT_GUIDE.md | 輸入 → 操作 → 預期結果 → 失敗處理 |
| Source/P11-Enhanced/docs/UPDATE_TOOL.md | 指定遊戲、額外套件／資料表及診斷欄位 |
| Source/P11-Enhanced/docs/PORTING.md | 修補位置、測試及建置 |
| Source/P11-Enhanced/docs/PUBLISH.md | 六檔發布、雜湊與遠端核驗 |
| Source/P11-Enhanced/docs/HANDOFF_TEMPLATE.md | 維修工作交接模板 |
| MOD-SHA256SUMS.txt | 同版五個模組 ZIP 的校驗值；模組本體另下載 |
| runtime-licenses/ | 已封裝執行環境的授權文件 |

源碼已是資料夾，不需要解壓內層 ZIP。修改源碼後，在 Source/P11-Enhanced 執行 Rebuild-Mods.cmd 可重建五個模組 ZIP；需要 Python 3.10+。完整工具包重建另需 Windows x64 和 requirements-build.txt 的依賴。這些命令只建置，不會推算新地址或部署遊戲。

收集器旁的 tools、maintenance、patches 是本次可攜版的固定依賴。開發時修改 **Source/P11-Enhanced/** 中的來源再重新建置，不能只修改外層某份 metadata 就當作工具或模組已更新。

## 下載與範圍提示

[本版六檔 Release](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.5) · [線上操作指南](https://github.com/cainiao524/P11-Enhanced/blob/v0.3.0-preview.5/docs/SELECTABLE.md)

四項名稱：**僅治療手槍／手槍全部／全部武器不包括霰彈槍／全部武器包括霰彈槍**。前三項排除霰彈，第四項**可能造成嚴重性能影響**。所有項目保留原 P-11 0.2.1；擴展 0.1.2 仍是候選。現有基準為 build 25480438、loader v17 / API 1 / internal 16，未知版本不沿用已成功結論。

推薦另外下載 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)。隊友追蹤與動作模組保持獨立，未附帶、未修改。

## English

Extract the toolkit and run Collect-HD2-Update.cmd. Collection needs no Python and performs no game launch, process reads, deployment or upload. Read the latest diagnostics summary and handoff. Complete collection is not gameplay verification or an automatic repair guarantee.

The five mod ZIPs are separate release assets; enable only one. Full matching source is already extracted under Source/P11-Enhanced. Read its AGENTS.md and docs/AGENT_GUIDE.md to maintain or rebuild it. The inclusive shotgun scope may cause severe performance impact. Private diagnostics and game binaries must stay out of public releases.