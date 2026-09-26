# 自療原始碼、建置與版本維護

## 來源結構

| 檔案 | 用途 |
|---|---|
| `mods/p11_self_hit_dataonly/core.lua` | 97 行玩法核心，本機玩家／來源武器／單發投射物身份檢查 |
| `data_windows.lua`（同目錄） | 僅允許非執行 heap 上特定兩個位元組的旗標修改及讀回 |
| `image_windows.lua` | 唯讀模組身份與檔案指紋；名稱中的 Capture 為歷史沿用 |
| `version.lua`、`entry.lua` | 指紋、虛擬區段、12 個錨點、API 1 啟動與回呼管理 |
| `profile.json` | 0.2.1 的確切遊戲身份及布局 |
| `maintenance/baselines.json` | 自療成功套件指紋及基本玩法回報範圍 |
| `maintenance/porting-map.json` | 自療資料位置、所有權链及維修檢查點 |
| `tools/resource_archive.py` | 獨立 Lua 資源封裝／讀取 |
| `tools/build_release.py` | 自療成品、來源 ZIP 與公開資產清單 |

## 模擬測試

Python 3.10+，使用 `lupa==2.8` 進行 LuaJIT mock 測試。

```powershell
python -m pip install -r requirements-dev.txt
python mods/p11_self_hit_dataonly/test_lua.py
```

共 429 個模擬斷言。PE 布局 fixture 為合成資料，不需要私人遊戲捕捉。
測試不啟動遊戲、不執行完整 native addon；它驗證保護邏輯，不能代替實際玩法確認。

## 建置

```powershell
# 重現成功的模組 ZIP，只有 Python 標準庫依賴：
python mods/p11_self_hit_dataonly/build.py
# 產生自療發布資產與乾淨原始碼副本：
python tools/build_release.py
```

成品 ZIP SHA256：`73c8c1e85b9732b85e0324b45b19d2c8b6c104abcd394c0f82ac49b67f9da8c2`。
Lua SHA256：`b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a`。

輸出位於 `dist/release/`，`PUBLIC-ASSETS.json` 是唯一的公開資產清單。
來源副本位於 `publication/P11-Enhanced/`；由 `publication-files.json` 明確選取。

模組資料夾的 README、VALIDATION 及 profile 是原 ZIP 的直接輸入，保留原位元組及封裝時狀態。
後續成功的記錄另外寫在發布文件與 baselines。不要改動歷史輸入後仍宣稱是同一份 0.2.1 ZIP。

## 遊戲更新

1. 核對新 EXE／DLL 與 loader 的身份。
2. 依 porting-map 檢查本機玩家、來源武器、槽位、排除位元及碰撞處理。
3. profile 以外，core／writer／version／builder 也含版本常數，必須一併檢查。
4. 保存 0.2.1 成功 ZIP，新增版本設定及必要程式修正，再跑模擬與封裝核對。
5. 未取得新版實際自命中治療證據前，將新版標為候選。

日常維護可使用另行保存在本機的一鍵離線收集工具。
磁碟資料不足時應具體記錄缺口，不改用原生 hook，也不只換雜湊略過保護。
候選位置、舊日誌與一次資料寫入都不能直接當成新版治療成功。
