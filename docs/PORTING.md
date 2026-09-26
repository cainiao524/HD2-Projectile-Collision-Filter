# 建置與版本移植 / Build and porting

Python 3.10+；模組封裝只需標準庫，Lua 模擬需 Lupa 2.8。

```powershell
python -m pip install -r requirements-dev.txt
python mods/p11_self_hit_dataonly/test_lua.py
python mods/weapon_self_hit_candidate/test_lua.py
python -m unittest discover -s tests -v
python tools/build_release.py --mods-only
```

也可雙擊 **Rebuild-Mods.cmd**。這重建三選一包及三個原始獨立输入包，不安裝依賴、不部署、不自動修改版本保護。

Windows x64 完整發布建置：

```powershell
python -m pip install -r requirements-build.txt
python tools/build_release.py
```

輸出 dist/release；PUBLIC-ASSETS.json 是唯一可發布資產清單。publication-files.json 選取來源並匯出 publication/P11-Enhanced。--reuse-portable 僅接受符合目前來源指紋的 EXE。

- mods/p11_self_hit_dataonly：P-11 0.2.1、profile、writer、入口與模擬。
- mods/weapon_self_hit_candidate：兩個候選共用核心，build.py 在各包嵌入未更改的 P-11。
- maintenance/baselines.json：三範圍身份與證據；porting-map.json：布局與必要檢查。
- patches/25480438/manifest.json：離線比較與候選模式，不授權執行時寫入。
- tools/offline_update.py、maintenance.py：收集和維修交接。
- tools/build_variants_release.py：單包、portable、來源與完整工具包建置。
- tools/build_selectable_mod.py：三個完整既有 archive 對應一個父選項的三個互斥 SubOptions，P-11 排第一。

## 保留成功實作

P-11 原始 ZIP SHA256：`73c8c1e85b9732b85e0324b45b19d2c8b6c104abcd394c0f82ac49b67f9da8c2`。
三包的 P-11 Lua SHA256：`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。

P-11 README、VALIDATION、profile 是封裝輸入，保留原始位元組及當時 experimental 字樣；後續成功記錄另寫 baseline。候選封裝有兩個獨立資源，Arsenal 同一開關控制。不能因 P-11 bytes 相同就宣稱新包已遊戲實測。

## Arsenal 封裝檢查

```powershell
node tests/test_arsenal_selectable.cjs <selectable.zip> <unpacked-Arsenal-app> <isolated-output-dir>
node tests/test_arsenal_selectable.cjs <selectable.zip> <unpacked-Arsenal-app> <isolated-output-dir> off
```

需本機 Arsenal 0.36.2 應用程式解包內容，包含 obfuscated_src/main 與 node_modules；不分發管理器程式。測試建立全新隔離 profile／假遊戲目錄，檢查匯入預選、九種切換、停用與清除，不碰真實遊戲。

## 更新檢查

版本常數同時存在 profile、core、writer、version、builder；新版本須共同核對，不只改雜湊。核對載入布局、12 個錨點、玩家與武器／附件所有權、槽位原值、寫前重檢及寫後讀回。擴展部分仍需排除 P-11，手槍 ID 和廣域機制需分別驗證。

保留成功舊包並新增版本。離線不足時列明缺口，不要求新遊戲內捕捉；沒有新玩法證據就維持候選。模擬不啟動遊戲，不能證明 native 碰撞或並行原子性。
