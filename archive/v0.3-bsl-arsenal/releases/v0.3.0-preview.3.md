# 一個模組，三選一 / One mod, three choices

下載 **P11-Enhanced-Selectable-v0.3.0-preview.3-build25480438.zip**，直接匯入 Arsenal。
同一個模組項目内，選 **僅 P-11／手槍系列＋P-11／廣域武器＋P-11**；子選項互斥，首次匯入預選僅 P-11。停用舊獨立版，關閉遊戲後選擇並重新部署。

這次只改封裝：三個方案各自部署的完整 archive 與前一版完全相同，全部保留原 P-11 0.2.1，擴展仍為 0.1.1。管理器負責選擇，不增加遊戲內掃描。

Arsenal 0.36.2 隔離後端驗證：一個模組、一個父選項、三個子選項；兩種匯入偏好、所有九種切換、無選項／父項停用／模組停用、重新啟用與清除通過，部署 bytes 與原包一致。這是管理器後端及離線測試，未新增遊戲內實測。

P-11 原實作已有基本治療成功回報；手槍、廣域擴展及組合共存仍缺少玩法證據。廣域不等於全部傷害機制支援，原有槽位扫描與效能界限保留。
目標 build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16。

- **Selectable**：唯一需要匯入 Arsenal 的模組 ZIP。
- **Full-Kit**：先解壓；内含上述模組、公開來源、Windows x64 離線工具。
- **Update-Toolkit 1.1.2**：更新診斷，修正文案以對應三選一；收集與比對邏輯不變。
- **Source**：可重現建置來源及測試。
- **SHA256SUMS**：校驗下載。

遊戲更新後雙擊工具包中的 Collect-HD2-Update.cmd。只做離線收集與維修交接，不啟動遊戲、不讀程序、不部署、不上傳，也不承諾自動修復未知版本。
推薦 P-11 搭配 [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)，另外下載。

## English

Import the Selectable ZIP directly into Arsenal and choose one exclusive sub-option: P-11 only, Pistols + P-11, or Broad weapons + P-11. P-11 is initially selected. Disable previous standalone variants; close the game and redeploy when switching.

Packaging only: every choice deploys its previous complete archive byte for byte. No added runtime scan. Arsenal 0.36.2 backend import/deployment, all nine transitions, disabled states and cleanup passed in isolated fixtures. Expanded gameplay and combined native behavior remain unverified; broad scope is not universal weapon coverage.

Full-Kit contains the one installable mod, source and offline update tool. Extract the kit before use. Diagnostic collection never launches the game, reads processes, deploys changes or uploads. It does not guarantee automatic repair. The animation companion above is optional and separately downloaded.
