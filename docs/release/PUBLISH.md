# GitHub 發布與歷史版本管理

目前發布目標為 **v0.3.0-preview.5，prerelease**。五個模組 ZIP 與一個 Update Toolkit 1.3.0 ZIP 是唯一手動資產；不另外上傳 Full Kit、Source ZIP 或 SHA256SUMS。GitHub 自動 Source code 連結不算手動資產。

## 1. 先核對來源與本機六檔

在源碼根目錄按 [PORTING](PORTING.md) 完成測試、完整建置及隔離檢查。對外來源與文件由 publication-files.json 匯出，不能把私人上游根目錄整個推送。

```powershell
python tools/release_manager.py verify
```

預期退出碼 0 及成功 JSON。工具依 `dist/release/PUBLIC-ASSETS.json` 核對六個檔案、來源與封裝；不發布或修改遊戲。失敗時修原始檔再重建，不直接改 ZIP／資產清單逃避核驗。

確認無遊戲 EXE／DLL、完整參考表、捕捉、原始日誌、私人診斷、帳號路徑或其他作者的模組／管理器。保留 LICENSE-NOTICE：整體授權尚未選定，不自行替作者新增授權。

## 2. 固定提交與發布正文

正文原始檔是 `docs/release/RELEASE-v0.3.0-preview.5.md`，生成副本為 `releases/v0.3.0-preview.5.md`。文件改完先執行 `python tools/sync_docs.py --apply` 並檢查生成副本，再完整建置。將原始檔和更新的生成副本一起提交。由公開乾淨 checkout 發布時，先完成相關提交並推送同一目標分支；GitHub CLI 需已登入有權限的帳號。確認本次使用者授權包含公開發布；已有授權就不用反覆詢問。

本版仍是候選／預覽，不為了成為 Latest 而移除 prerelease 標示。README 的主要下載連結直接指向本版。

## 3. 明確發布並核對遠端

以下適用於公開源碼 checkout 根目錄：

```powershell
$releaseTarget = (git rev-parse HEAD).Trim()
python tools/release_manager.py publish --target "$releaseTarget" --notes releases/v0.3.0-preview.5.md
python tools/release_manager.py verify-remote --target "$releaseTarget"
```

每一步成功再執行下一步。publish 會核對六檔、當前來源及乾淨已提交的目標，使用 manifest 的版本建立 prerelease，並從核驗資產產生 SHA-256 表附在發布正文。原始正文不先寫入最終工具包自身的雜湊，以免形成來源與成品雜湊循環。verify-remote 檢查遠端提交／版本與六項資產名稱、大小、雜湊。

三個子命令均接受 `--release-dir`（預設 dist/release）與 `--repo`（預設 cainiao524/P11-Enhanced）。publish 另接受 `--git-dir`，用於上游工作區將乾淨 Git repo 匯出到 publication/P11-Enhanced 的情況。一般公開 checkout 無需設定。這些參數只改明確目標，不解除資產與來源檢查。

verify 與 verify-remote 是核驗；只有 publish 寫入 GitHub。收集器不呼叫發布工具。上傳中斷時先檢查實際 Release／資產與錯誤，不假定成功，不另創造新標籤掩蓋失敗。修復既有遠端資產須沿用已授權範圍和同一已核驗清單；不批量上傳整個 dist，也不覆蓋歷史回退包。

### 已建立 Release，但部分上傳中斷

不要重跑 `publish`：它建立新 Release，不能續傳已存在的 Release。以下在公開源碼 checkout 根目錄執行，沿用本次已授權的發布範圍。前半段核對本機源碼、tag、既有資產；全部相符後，最後一個迴圈才上傳清單中缺少的 ZIP。沒有伺服器 digest 時，先下載到忽略的 `build/release-recovery-checks/` 核對。沒有刪除、覆蓋或 `--clobber`。

```powershell
python tools/release_manager.py verify
if ($LASTEXITCODE -ne 0) { throw '本機六檔核驗失敗，先修正來源並重建。' }
$releaseManifest = Get-Content -LiteralPath 'dist/release/PUBLIC-ASSETS.json' -Raw | ConvertFrom-Json -ErrorAction Stop
$releaseRepo = 'cainiao524/P11-Enhanced'
$releaseTag = $releaseManifest.release
$releaseNames = @($releaseManifest.public_assets)
$releaseTarget = (git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw '無法取得公開源碼 HEAD。' }
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'tools'); from release_manager import verify_release, check_git_source; check_git_source(Path.cwd(), sys.argv[1], verify_release(Path('dist/release')))" "$releaseTarget"
if ($LASTEXITCODE -ne 0) { throw '提交或乾淨源碼與封裝不符，停止續傳。' }
$remoteRelease = gh api "repos/$releaseRepo/releases/tags/$releaseTag" | ConvertFrom-Json -ErrorAction Stop
if ($LASTEXITCODE -ne 0) { throw '無法取得既有 Release；先確認是否已建立。' }
$remoteCommit = gh api "repos/$releaseRepo/commits/$releaseTag" | ConvertFrom-Json -ErrorAction Stop
if ($LASTEXITCODE -ne 0 -or $remoteCommit.sha -ne $releaseTarget) { throw '遠端 tag 不是本次 HEAD，停止。' }
if ($remoteRelease.tag_name -ne $releaseTag -or $remoteRelease.prerelease -ne $true -or $remoteRelease.draft -ne $false) {
    throw '既有 Release 的版本或預覽／草稿狀態不符，停止。'
}
$recoveryFolder = Join-Path 'build/release-recovery-checks' ([guid]::NewGuid().ToString('N'))
$checkedAssets = @{}
foreach ($asset in $remoteRelease.assets) {
    if ($asset.name -notin $releaseNames -or $checkedAssets.ContainsKey($asset.name)) { throw "多餘或重複資產：$($asset.name)" }
    $expectedAsset = $releaseManifest.assets.PSObject.Properties[$asset.name].Value
    if ($asset.state -ne 'uploaded' -or $asset.size -ne $expectedAsset.bytes) { throw "既有資產未完成或大小不符：$($asset.name)" }
    if ($asset.digest) {
        if ($asset.digest -ne "sha256:$($expectedAsset.sha256)") { throw "既有資產雜湊不符：$($asset.name)" }
    } else {
        New-Item -ItemType Directory -Path $recoveryFolder -Force -ErrorAction Stop | Out-Null
        gh release download "$releaseTag" --repo "$releaseRepo" --pattern "$($asset.name)" --dir "$recoveryFolder"
        if ($LASTEXITCODE -ne 0) { throw "無法下載核對：$($asset.name)" }
        $downloadedHash = (Get-FileHash -LiteralPath (Join-Path $recoveryFolder $asset.name) -Algorithm SHA256 -ErrorAction Stop).Hash
        if ($downloadedHash -ne $expectedAsset.sha256) { throw "下載內容雜湊不符：$($asset.name)" }
    }
    $checkedAssets[$asset.name] = $true
}
# 只有前面全部通過後，才補上缺少的清單資產；不覆蓋已存在的檔案。
foreach ($assetName in $releaseNames) {
    if (-not $checkedAssets.ContainsKey($assetName)) {
        gh release upload "$releaseTag" (Join-Path 'dist/release' $assetName) --repo "$releaseRepo"
        if ($LASTEXITCODE -ne 0) { throw "上傳仍失敗：$assetName；保留現況，重新核對後再續傳。" }
    }
}
python tools/release_manager.py verify-remote --repo "$releaseRepo" --target "$releaseTarget"
if ($LASTEXITCODE -ne 0) { throw '遠端核驗失敗，不能標示發布完成。' }
```

若既有資產未完成、大小／雜湊不符，或出現額外資產，上述流程會停止並指出名稱。先保存遠端 ID、名稱、狀態及本機預期雜湊，確定錯誤來源；需要替換或移除既有資產時，另走符合使用者授權範圍的明確修復流程，不用覆蓋參數繞過本核對。已通過的資產與歷史版本保持原樣。

## 4. 保留歷史 Release

本版成功發布且遠端核驗通過後，對目前較舊的 preview.1、preview.2、preview.3、preview.4：

1. 保留原始標籤、提交及全部下載資產。
2. 在標題加上「歷史版本」標示，正文頂部加入指向 v0.3.0-preview.5 的主要下載連結。
3. 原正文保留，避免重寫當時的玩法或測試結論。
4. 已有歷史標示就更新指向，不重複疊加提示。

此步不由 release_manager.py 自動修改。可用 `gh release view` 先讀取每版 title／body，再把加入提示的完整正文寫入本機 UTF-8 暫存檔，以 `gh release edit --title ... --notes-file ...` 更新。正文使用檔案傳入，避免引號與換行損壞；不執行刪除標籤或資產命令。

## 5. 交付記錄

記錄新 Release 連結、目標提交、六個資產的 SHA-256、verify／verify-remote 結果及歷史版本整理結果。保留本機診斷與離線分析證據，不將它們上傳。

GitHub 有六個檔案、來源能重建、mock／管理器隔離測試通過，均不能作為新版玩法或無卡頓證明。P-11 保留原使用者成功回報，擴展與性能仍按 [驗證記錄](VERIFICATION.md) 如實標示。
