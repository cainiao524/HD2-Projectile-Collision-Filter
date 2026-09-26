# P11-Enhanced — Projectile Collision Filter

The four-choice mod is named **Projectile Collision Filter（投射物碰撞過濾器）**. The repository remains P11-Enhanced. The mod identity is unchanged, so replace the existing selectable package when upgrading.

**One Arsenal mod, four exclusive scopes. The first three exclude shotguns; the fourth may cause severe performance impact. All preserve original P-11 0.2.1.**

[繁體中文](README.md) · [Download v0.3.0-preview.5](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.5)

| Task | Start here |
|---|---|
| Install, switch, upgrade or roll back | [Player guide](docs/SELECTABLE.md) |
| Collect evidence after a game/loader update | [Offline diagnostics](docs/UPDATE_TOOL.md) |
| Hand over to another developer or AI agent | [AGENTS.md](AGENTS.md), then [step-by-step runbook](docs/AGENT_GUIDE.md) and [porting guide](docs/PORTING.md) |
| Validate, build and publish | [Verification](docs/VERIFICATION.md) · [Publishing](docs/PUBLISH.md) |

The detailed operating and maintenance guides are in Traditional Chinese. Commands, file names and report fields retain their original spelling.

## Choices and downloads

Import the selectable ZIP into Arsenal. Under **生效範圍** (scope), select one:

| Exact option label | Meaning |
|---|---|
| 僅治療手槍 | P-11 only; recommended and initially selected |
| 手槍全部 | Supported pistols plus P-11; excludes shotguns and multishot types |
| 全部武器不包括霰彈槍 | Supported native weapon projectiles plus P-11; excludes shotguns and multishot types |
| 全部武器包括霰彈槍 | Includes shotguns and multishot types; **may cause severe performance impact** |

“All pistols” is limited to the existing eight candidate pistol IDs. “All weapons” means the supported native projectile subsystem, not verified universal hitscan, beam, melee, explosion or entity-projectile support. Filtered scopes also conservatively skip other multishot mechanisms and types outside the pinned table. [Scope and implementation](docs/VARIANTS.md).

The release has exactly six manually uploaded ZIPs:

| File | Purpose |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.5-build25480438.zip` | Recommended four-choice mod |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | Unchanged original P-11-only mod |
| `weapon_self_hit_pistols-0.1.2-build25480438-CANDIDATE.zip` | Fixed pistol scope, excluding shotguns |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | Fixed native scope, excluding shotguns |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | Fixed inclusive scope; **potentially severe performance impact** |
| `P11-Enhanced-Update-Toolkit-1.3.0-win-x64.zip` | Portable offline collector, complete matching source and maintenance guides |

**Enable only one of the five mod packages.** The toolkit is extracted separately and is not imported into Arsenal. Source is directly available under `Source/P11-Enhanced/`. All six SHA-256 values are in the release body; GitHub's automatic Source code links are additional source downloads. Historical releases remain available.

## Installation and maintenance

Close the game. Install compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately, disable old selectable/standalone self-hit packages, import one new ZIP, confirm scope, enable and redeploy. Close and redeploy when switching or disabling too. If Arsenal detects the unchanged mod identity, replace the old package or disable/remove its old entry before importing.

Target: **build 25480438 / EXE 1.8.46015.0 / loader v17 / API 1 / internal 16**. Unknown versions stop writes. After updates finish, extract the toolkit and run `Collect-HD2-Update.cmd`; inspect the summary and repair handoff in `diagnostics`. No Python is required for collection. It does not launch the game, read running processes, deploy, upload or promise automatic repair.

Recommended companion: [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/), downloaded separately. Teammate homing and animation mods remain independently managed and are not bundled or changed.

Only original P-11 basic healing has user confirmation. Expanded gameplay, complete current-game shotgun coverage, coexistence and performance remain candidates. The implementation clears a checked projectile's source-collision exclusion flag, with native collision handling the effect; no native hooks or health/stamina/ammo/damage writes. Fixed-slot scanning still exists, so zero overhead is not promised. [Evidence and performance](docs/PERFORMANCE.md).

[Third-party sources](docs/THIRD_PARTY.md) · [License notice](LICENSE-NOTICE.md). No overall project license has been selected. Unaffiliated with Arrowhead Game Studios; made with assistance from OpenAI tools.
