# 自療單獨版 GitHub 發布準備

倉庫名稱沿用 **P11-Enhanced**，發布標題為 **P11-Enhanced v0.2.1 — P-11 Self-Hit Healing**。
本次只準備 P-11 自命中治療，使用者選擇先留在本機，尚未建立遠端或上傳。

## 倉庫內容

- 自療 Lua、版本設定、資源封裝工具及模擬測試。
- 中英文首頁、完整雙語自療介紹與 Release 正文、安裝、建置、驗證與來源說明。
- Raise Weapon Aims at Yourself 的選配推薦及原頁連結。
- Experimental Infusion 及第一人稱射腳用法；玩法依據與限制記錄於驗證說明。

## 封面狀態

內建圖片生成服務於 2026-09-26 回傳驗證錯誤（401），尚未產生封面。
使用者選擇保留內建方案、稍後再生成。提示詞與設計要求保存在 `docs/COVER-BRIEF.md`，
目前資產清單沒有封面圖片，也沒有占位圖片；圖片完成後再加入來源及公開資產清單。

## Release

標籤：`v0.2.1`；正文：`releases/v0.2.1.md`。
公開資產清單：`dist/release/PUBLIC-ASSETS.json`。

1. `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip`
2. `P11-Self-Hit-Source-v0.2.1.zip`
3. `SHA256SUMS.txt`

僅上傳清單內的檔案。來源由明確清單匯出，成功成品維持原指紋。
整體授權尚未選定；參見 LICENSE-NOTICE.md。
