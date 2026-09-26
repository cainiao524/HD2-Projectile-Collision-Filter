# HD2-Projectile-Collision-Filter Update Toolkit 1.3.2

**離線更新與維護工具，不匯入 Arsenal。** 這是 preview.8 的第二個 ZIP；第一個 ZIP 是四選一整合模組。完整源碼已直接放在 `Source/HD2-Projectile-Collision-Filter/`。

## 一次收集

1. 等遊戲、loader 更新和 Arsenal 部署結束。
2. 完整解壓後雙擊 **Collect-HD2-Update.cmd**。Windows x64 已包含 `P11-Update.exe`，不需另裝 Python。
3. 開啟 `diagnostics/latest.json` 指向的新資料夾，先讀摘要.md，再讀維修交接.md；同時保存本次 ZIP。
4. 先解決 complete／errors 中的缺檔或收集中變動，再查看 gaps、受影響功能和下一步。診斷留本機，不公開遊戲二進位和私人日誌。

辨識不到遊戲時在此資料夾開 PowerShell：

```powershell
$gameDirectory = Read-Host '輸入 Helldivers 2 安裝資料夾'
.\P11-Update.exe --game "$gameDirectory"
```

工具讀磁碟版本、部署資源、本機套件、相關既有日誌，以及安裝中的實體／差量／結構／武器自訂／彈頭五份資料表。安裝來源和舊快取分开，保存來源與缺口。四個整合 scope 用精確 Lua 指紋辨識；符合基本成功基準需要遊戲、部署、loader 來源和無衝突共同支持。

不啟動遊戲、不讀執行中程序、不修改或部署模組、不上傳；也不自動修復。完整收集表示磁碟檔案穩定，不是玩法成功。

## 包內導航

| 工具包相對路徑 | 用途 |
|---|---|
| Collect-HD2-Update.cmd / P11-Update.exe | 一鍵收集；不需 Python |
| Source/HD2-Projectile-Collision-Filter/README.md | 完整專案導航 |
| Source/HD2-Projectile-Collision-Filter/AGENTS.md | AI／Agent 先讀 |
| Source/HD2-Projectile-Collision-Filter/docs/AGENT_GUIDE.md | 逐步輸入、操作、輸出、繼續條件和失敗處理 |
| Source/HD2-Projectile-Collision-Filter/docs/UPDATE_TOOL.md | 指定遊戲、資料表和套件，報告判讀 |
| Source/HD2-Projectile-Collision-Filter/docs/PORTING.md | 移植、測試和建置 |
| Source/HD2-Projectile-Collision-Filter/docs/PUBLISH.md | 兩資產發布與遠端核驗 |
| Source/HD2-Projectile-Collision-Filter/docs/PAGE-PUBLISHING.md | 兩個模組頁介紹與封面 |
| MOD-SHA256SUMS.txt | 同版整合模組 ZIP 校驗；模組本體另下載 |
| runtime-licenses/ | 可攜執行環境授權文件 |

開發時以 Source 專案為根，修改來源再重建，不能只改工具包外層 EXE 或 metadata。`Rebuild-Mods.cmd` 重建整合模組需 Python 3.10+；完整工具包另需 Windows x64 和 requirements-build.txt。任何建置都不推算新地址或部署。

[當前兩檔 Release](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8) · [操作指南](SELECTABLE.md) · [副武器限制](SECONDARIES.md)

## English

Fully extract this toolkit and run Collect-HD2-Update.cmd after updates/deployment finish. P11-Update.exe needs no Python. If discovery fails, use the PowerShell prompt above to pass your installation to --game. Read the latest summary and repair handoff under diagnostics.

The collector performs no game launch, process reads, deployment or upload. It matches exact game, deployed-mod and loader identities, distinguishes all four integrated scopes, collects five installed data files and reports missing evidence. Complete collection is not gameplay verification or an automatic repair guarantee.

The mod is a separate release ZIP. Full matching source is already extracted under Source/HD2-Projectile-Collision-Filter; start with AGENTS.md and docs/AGENT_GUIDE.md. Keep private diagnostics and game binaries out of public releases.
