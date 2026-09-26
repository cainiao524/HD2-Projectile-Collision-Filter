# Changelog

## v0.3.0-preview.8 — Unified cursor mod, bilingual configuration, two downloads

- Publish the user-tested four-scope unified cursor package. Preserve all four accepted Lua/game-resource payloads while updating packaging and English-first Traditional Chinese configuration.
- Keep one addon per selected scope, P-11 initially selected, first-three shotgun/multishot exclusion and a bilingual severe-performance warning on the inclusive fourth choice.
- Record normal basic operation reported for all four choices. Do not promote that report to complete per-weapon/multiplayer/performance coverage; the earlier 70-to-130 FPS report belongs only to P-11 0.2.3.
- Rename the repository to HD2-Projectile-Collision-Filter. Publish exactly two ZIPs: the selectable mod and Update Toolkit 1.3.2; retain historical assets and stop publishing four standalone alternatives.
- Diagnose integrated scopes by exact Lua fingerprints; jointly require game, deployed-mod and loader identity plus conflict-free deployment for a confirmed baseline. Preserve historical identities and explicit gaps.
- Include complete source under Source/HD2-Projectile-Collision-Filter, updated Agent/runbook/publishing guides, bilingual page copy and two replacement promotional covers. Animation and homing packages remain separate.

## v0.3.0-preview.6 — 副武器分類擴展預覽 / Expanded Secondary Catalog Prerelease

- Target all shootable secondary-slot weapons while keeping shotgun/multishot exclusions. Pistol candidate 0.1.3 uses catalog-backed work; this does not establish support for all firing mechanisms.
- Separate pinned-reference classification, runtime lookup/handler coverage and gameplay evidence. Do not use AI EquipmentType as a loadout-slot classifier.
- Dagger beam and Crisper spray remain unsupported; Warrant, P33 and Hornet Pistol (internal resource name) entity follow-up paths remain unresolved. Keep original P-11 0.2.1.
- Toolkit 1.3.1 collects five installed entity/structure/weapon/projectile data files, records installed-versus-cache provenance and reports specific gaps without asserting game-build equivalence.
- Add SECONDARIES and update maintenance instructions, bilingual player guidance and release presentation. Preview.6 becomes the main prerelease download; preview.5 remains available as a historical release with its original assets and evidence.
- Keep the six-ZIP layout, unchanged original P-11 and broad-scope packages. Expanded secondary coverage remains incomplete and unverified despite public prerelease availability.

## v0.3.0-preview.5 — Clear choices, six downloads and maintenance handoff

- Rename the selectable mod to Projectile Collision Filter（投射物碰撞過濾器） while retaining the P11-Enhanced repository, mod identity and runtime.
- Simplify the four Arsenal labels under 生效範圍; preserve the first-three shotgun exclusion and explicitly warn that the inclusive fourth scope may cause severe performance impact.
- Preserve original P-11 0.2.1, expanded runtime 0.1.2 and all four standalone package bytes; no gameplay change.
- Publish five alternative mod ZIPs plus Update Toolkit 1.3.0. Source is directly available under Source/P11-Enhanced; no additional Full Kit, Source ZIP or checksum asset.
- Add AGENTS.md, player/developer navigation, a step-by-step collect/triage/port/test/publish runbook and a handoff template. Define canonical documentation and explicit alias synchronization.
- Improve diagnostic handoff and record collector version; publish a six-asset validation/publishing/remote-verification CLI.
- Retain historical releases and gameplay evidence limits. Hash matches, offline tests and clearer packaging do not establish new gameplay or FPS results.

## v0.3.0-preview.4 — Early shotgun exclusion and fourth opt-in scope

- Add a broad no-shotgun scope; first three selector choices exclude shotguns, fourth includes them.
- Filter 38 pinned shotgun/multishot types before source lookup; filtered scopes skip out-of-table types.
- Preserve P-11 bytes, ownership checks and all per-write guards; candidate 0.1.2.
- Track four scopes and all expanded conflicts in toolkit 1.2.0; include filter provenance and offline verification.
- Add shotgun/burst/policy tests; expanded Lua now has 638 mock assertions.


## v0.3.0-preview.3 — Arsenal three-way selector

- One importable mod with a single parent and three exclusive sub-options; P-11 is listed first.
- Preserve each previous complete archive byte for byte; no runtime code change.
- Full kit contains one selectable mod, source and diagnostic toolkit 1.1.2.
- Add an isolated Arsenal backend harness for import preferences, all transitions and disabled states.
- Update offline-tool wording; collection and compatibility logic remain unchanged.


## v0.3.0-preview.2 — Candidate 0.1.1 filtering

- Reject non-pistol weapons before attachment/definition lookup; reuse source-weapon and definition discovery within one update.
- Keep the full dependency chain fresh at each write, plus each projectile source, type, auxiliary reference and original flags. No cross-update pointer cache.
- Decode slot types/flags directly from bytes. Preserve the original P-11 0.2.1 addon in all three packages.
- Add 45 cache invalidation/filtering mock assertions and a reproducible synthetic read-count comparison. No in-game performance claim.
- Update package fingerprints in the shared maintenance toolkit; its runtime is unchanged.


## v0.3.0-preview.1 — Three variants

- Three Arsenal packages, each containing the identical original P-11 0.2.1 Lua. Expanded packages add pistol/native-projectile candidate logic as a separate resource, with a single manager option.
- Expanded scopes and combined gameplay remain unverified; only original P-11 basic healing has user confirmation.
- Portable offline toolkit 1.1.0 compares all three scopes, flags mutual exclusion, preserves candidate status and produces a repair handoff.
- One-command mod rebuilding, explicit public source/asset lists, checksums and a complete collection.


## v0.2.1 — P-11 自命中治療單獨發布

- 保存使用者確認基本自命中治療有效的原始 0.2.1 ZIP 及 Lua。
- 純資料修改、API 1 addon、Arsenal 獨立開關，沒有原生 hook。
- 提供完整自療原始碼、可重現封裝及 429 個 Lua 模擬斷言。
- 發布內容聚焦自療成品、來源與文件。
- 保留 Raise Weapon Aims at Yourself 的選配推薦與原頁連結。
- 提供完整中英雙語模組介紹及 Release 正文。
- 根據使用者補充，加入已啟用 Experimental Infusion 時可觸發增益效果，以及第一人稱朝自己腳射擊的用法。
- 以上為發布文件更新，已測成功的安裝 ZIP 與 runtime Lua 保持原樣。

## 0.2.1 初始化修正

- 檔案指紋與載入後虛擬區段分開檢查。
- 在既有更新回呼之後進行有限次重試，通過全部保護前不修改資料。
- 修正 0.2.0 啟動區段拒絕造成零寫入的問題，其後獲使用者確認有效。
- 玩法核心與資料 writer 沒有因初始化修正改變。
