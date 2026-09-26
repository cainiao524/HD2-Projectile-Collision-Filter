# P11-Enhanced — One mod, three self-hit scopes

Import one ZIP into Arsenal, then choose **P-11 only**, **Pistols + P-11**, or **Broad weapons + P-11** under its single Self-hit scope option. All choices include the unchanged P-11 0.2.1 healing addon.

[繁體中文](README.md) · [Download v0.3.0-preview.3](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.3) · [Install guide](docs/SELECTABLE.md) · [Scope details](docs/VARIANTS.md)

## Install

Close the game and install a compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately. Import **P11-Enhanced-Selectable-v0.3.0-preview.3-build25480438.zip** directly into Arsenal. Disable previous standalone self-hit packages, duplicate hooks and research addons. Choose one sub-option, enable the mod and deploy. P-11 only is initially selected; automatic mod activation follows manager preferences. Close the game and redeploy whenever changing scopes or disabling the mod.

| Choice | Scope | Evidence |
|---|---|---|
| P-11 only | Original P-11 0.2.1 | Basic healing confirmed by the user for the original implementation |
| Pistols + P-11 | Same P-11 plus eight candidate pistol resource IDs | Expanded gameplay, current IDs and combined coexistence unverified |
| Broad weapons + P-11 | Same P-11 plus local weapon-owned native projectiles | Expanded gameplay and mechanism coverage unverified |

Only the selected sub-option deploys. Broad weapons does not mean proven universal support for hitscan, beams, melee, explosions or entity projectiles. Target: **build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**. Unknown builds stop writes. This is a prerelease.

## Implementation and performance

Data-only addons clear the eligible projectile's source-collision exclusion flag. Native collision rules handle healing or damage. No native hooks, executable patches, health/stamina/ammo/damage writes. Expanded logic excludes P-11 and leaves it to the original healing addon.

This release changes packaging only: each choice deploys its complete previous archive byte for byte. Selection happens in the manager, with no added runtime menu or scan. Expanded 0.1.1 retains cached discovery within one update and fresh guards at every write. Fixed-slot scanning remains; no zero-overhead or stutter-free claim. [Performance evidence](docs/PERFORMANCE.md).

Recommended P-11 companion: [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/), downloaded separately. The user also reports first-person foot shots and effects from an already-active Experimental Infusion booster. [Details](docs/SELF_HIT.md) · [Verification](docs/VERIFICATION.md).

## Full kit and maintenance

**P11-Enhanced-Full-Kit-v0.3.0-preview.3.zip** contains the one selectable mod, source and portable Windows x64 diagnostic tool. Extract first and import the single ZIP in Mods; the outer kit is not an installable mod.

After updates, run **Collect-HD2-Update.cmd**. It collects offline files, compares deployed scopes and creates a repair handoff. No Python required, game launch, process access, deployment or upload. Automatic repair is not guaranteed. After a reviewed source port, **Rebuild-Mods.cmd** rebuilds the selectable mod and its three standalone inputs with Python 3.10+. Historical standalone downloads remain available in previous releases; do not enable them alongside the selectable mod.

[Build and porting](docs/PORTING.md) · [Sources](docs/THIRD_PARTY.md) · [License notice](LICENSE-NOTICE.md). No overall project license has been selected.
