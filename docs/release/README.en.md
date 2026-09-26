# P11-Enhanced — One mod, four self-hit scopes

**The first three choices exclude shotguns; the fourth explicitly includes them. Every choice preserves original P-11 0.2.1 healing.**

[繁體中文](README.md) · [Download v0.3.0-preview.4](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.4) · [Install guide](docs/SELECTABLE.md)

Import **P11-Enhanced-Selectable-v0.3.0-preview.4-build25480438.zip** directly into Arsenal, then select one exclusive sub-option:

| Choice | Scope |
|---|---|
| 1. P-11 only, initially selected | Only original healing darts; other projectiles are skipped |
| 2. Pistols, no shotguns + P-11 | Eight candidate pistol resource IDs with early projectile filtering |
| 3. Broad, no shotguns + P-11 | Local native weapon projectiles with the same early filter |
| 4. Include shotguns + P-11 | Broad native projectile scope including shotguns; potentially heavy |

Filtered scopes skip 38 pinned shotgun/multishot types before source or weapon lookup. Named shotgun families include single-projectile variants; all multishot rows in the reference table and out-of-table types are excluded conservatively. Other multishot mechanisms can therefore be skipped too. The P-11 implementation is unchanged.

Synthetic 32-pellet results: filtered scopes make 10 logical reads and no writes; inclusive scope makes 985 reads and 32 writes. The fixed-slot scan remains. These are not game FPS measurements or proof of stutter elimination. [Performance and evidence](docs/PERFORMANCE.md).

Close the game, install the compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately, disable old selectable/standalone variants, import, confirm the scope and redeploy. Repeat the close-and-redeploy cycle when switching. Confirm the choice after upgrading from the three-way selector.

Target: build 25480438 / EXE 1.8.46015.0 / loader v17 / API 1 / internal 16. Unknown versions stop writes. Expanded scopes, current-game shotgun coverage and performance remain unverified candidates. “All” refers to the supported native subsystem, not universal hitscan/beam/melee/explosion/entity-projectile support. [Verification](docs/VERIFICATION.md).

Recommended companion: [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/), separately downloaded. Native collision performs healing/damage; no native hooks or health/stamina/ammo/damage writes.

**P11-Enhanced-Full-Kit-v0.3.0-preview.4.zip** contains the one mod, source and portable offline tool. Extract first; import the ZIP inside Mods. Run Collect-HD2-Update.cmd after updates for four-scope diagnostics and a repair handoff. No Python, game launch, process access, deployment or upload; automatic repair is not guaranteed. Rebuild-Mods.cmd rebuilds edited sources with Python 3.10+.

[Build and porting](docs/PORTING.md) · [Sources](docs/THIRD_PARTY.md) · [License notice](LICENSE-NOTICE.md). No overall project license has been selected.

升級提示：新包沿用相同模組身份。若 Arsenal 提示重複，使用管理器的替換功能，或先停用並移除舊三選一項目，再匯入新版；不要保留兩個同時啟用。 / Upgrade: the mod identity is unchanged. If Arsenal reports a duplicate, replace the old package or disable/remove its old entry before importing.
