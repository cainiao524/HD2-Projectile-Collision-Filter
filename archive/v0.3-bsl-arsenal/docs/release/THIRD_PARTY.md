# 來源與依賴

## Bingus Shared Loader

作者 CowboyBingus，官方來源：[GitHub](https://github.com/CowboyBingus/BingusSharedLoader)。
本模組採 API 1 addon、獨立 Lua 資源與共用日誌，loader 需單獨安裝。
本發布包沒有重分發 loader 啟動或音效資源。

## 推薦的選配模組

[Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)
為使用者指定的自療搭配推薦。由原作者頁面另行下載；安裝、操作及適用版本以該頁為準。
這項推薦沒有新增共存玩法驗證。

## 遊戲與開發依賴

Helldivers 2 與其原始資產屬 Arrowhead Game Studios 及相關權利人。
模組 ZIP 包含自行封裝的 Lua 資源與空 sidecar，沒有遊戲 EXE／DLL、私人捕捉或日誌。
原自命中參考包的封裝格式曾用於理解 Lua 資源工具；其原生 hook 不在本發布中。

Lupa／LuaJIT 僅用於開發時的模擬測試，沒有隨模組成品分發。
程式與文件使用 OpenAI 工具協助製作。尚未選定專案整體授權。

## Portable runtime

Windows 工具包含 Python 與 PyInstaller runtime；各自的授權文字隨 toolkit 的 runtime-licenses 提供。它們不屬於遊戲模組 runtime。歷史 preview.5 的手槍候選 ID 取自較早本機模組索引；歷史兩個廣域包保留當時封裝 metadata；本版改用共用單 addon，仍保留必要來源限制。只發布必要識別值與來源限制，不重分發索引、遊戲碼流或其他作者模組。

preview.8 沿用 preview.6 建立的副武器候選分類，使用固定 Filediver 提交 bf0ce329db3cf0043994eb717ea86433c303cb36 的裝備副武器槽位及武器引用；maintenance/secondary-catalog-25480438.json 記錄三份資料表與兩份名稱參考的來源、SHA-256、完整 27 筆 roster 和結構證據。目標安裝資料與快取分開記錄，尚未證明加密安裝表等同此明文參考。不以 AI 的 EquipmentType 代替裝備槽位，也不把完整參考分類宣稱為當前可取得清單或完整機制支援。公開內容僅保留必要識別事實、來源與驗證範圍，不附完整遊戲二進位表。[副武器狀態](SECONDARIES.md)

霰彈分類參考 [Filediver](https://github.com/xypwn/filediver) 固定提交 bf0ce329db3cf0043994eb717ea86433c303cb36 的 projectile settings 表與結構。僅分發必要衍生類型／欄位識別事實及來源指紋，不分發完整二進位資料表。較早的本機命名表 SHA256 也記錄在排除表中；不把舊快取當成當前玩法驗證。
