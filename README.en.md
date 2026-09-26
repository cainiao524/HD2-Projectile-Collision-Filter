# Projectile Collision Filter — P-11 Self-Heal & Selectable Self-Hit (Preview)

![Projectile Collision Filter cover](docs/assets/projectile-collision-filter-cover.png)

[繁體中文](README.md) · [Download v0.3.0-preview.6](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6) · [Install and switch](docs/SELECTABLE.md) · [Supported scope](docs/SECONDARIES.md)

Let your own P-11 healing darts hit you, with the game's native collision and healing logic handling the effect. You still aim and fire manually. One Arsenal mod lets you stay with the healing pistol or choose a broader weapon-projectile scope.

**Original P-11 basic self-healing has a successful user report; expanded scopes remain candidates.** Every choice includes the same P-11 0.2.1 addon. Other weapons retain their native effects, so damaging weapons may cause self-damage. The first three choices exclude shotguns and multishot types; the fourth includes them and **may cause severe performance impact**.

## Four choices, starting with P-11

| Exact Arsenal label | Scope |
|---|---|
| **僅治療手槍 — P-11 only** | P-11 only; recommended and initially selected. |
| **手槍全部 — All pistols** | P-11 plus native-projectile secondary candidates, with plasma/grenade types represented in the data; excludes shotguns and multishot. Not every secondary mechanism is implemented. |
| **全部武器不包括霰彈槍 — All weapons, excluding shotguns** | P-11 plus supported local native weapon projectiles; excludes shotguns and multishot. |
| **全部武器包括霰彈槍 — All weapons, including shotguns** | Broad native-projectile candidate including shotguns and multishot; **may cause severe performance impact**. |

## Downloads: one selector, four standalone mods, one toolkit

**The selectable mod is recommended for most players.** The four standalone mods provide fixed scopes and are alternatives to the selector. **Enable only one self-hit mod package.** Extract the toolkit separately; do not import it into Arsenal.

| Download | Use |
|---|---|
| `Projectile-Collision-Filter-v0.3.0-preview.6-build25480438.zip` | **Recommended:** one Arsenal mod with four exclusive choices |
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | Fixed P-11-only scope; unchanged original healing package |
| `weapon_self_hit_pistols-0.1.3-build25480438-CANDIDATE.zip` | Fixed pistol scope; 0.1.3 secondary candidate, excluding shotguns |
| `weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip` | Fixed supported native-weapon scope, excluding shotguns |
| `weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip` | Broad candidate including shotguns; **may cause severe performance impact** |
| `P11-Enhanced-Update-Toolkit-1.3.1-win-x64.zip` | Windows x64 offline collector, complete source and maintenance guides |

SHA-256 values for all six ZIPs are in the [release body](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.6). GitHub's automatic Source code links are additional source downloads, not directly installable mods. Historical versions remain available for rollback.

## What this preview covers

“All pistols” targets all shootable secondaries. The current catalog supplies **16 source-identity candidates: 13 native-path entries and 3 entity branches**, with P-11 retained separately. This describes reference data and recognition scope; **it does not mean all 16 weapons can already hit their owner**.

- **Dagger beam and Crisper spray are currently unsupported.**
- **Warrant, P33 and Hornet entity follow-up collisions/effects are unverified.** Hornet is an internal resource name; its final name and availability are unconfirmed.
- Plasma and grenade types remain candidates; grenade-body collision does not establish explosion or area-effect support.
- “All weapons” means the currently supported native projectile path, not guaranteed coverage of every hitscan, beam, spray, melee, explosion or entity mechanism.
- Choices 2 and 3 also conservatively skip out-of-table types and other multishot mechanisms. Slot scanning remains; zero overhead or zero stutter is not promised.

[Complete secondary catalog and evidence](docs/SECONDARIES.md) · [Implementation and scope](docs/VARIANTS.md) · [Performance notes](docs/PERFORMANCE.md)

## Requirements

| Item | Release target |
|---|---|
| Game | Steam build **25480438** |
| Game EXE | **1.8.46015.0** |
| Loader | **Bingus Shared Loader v17 / API 1 / internal 16** |
| Mod manager | Arsenal; isolated backend checks used 0.36.2 |
| Collector | Windows x64; the portable EXE needs no separate Python installation |

## Install, switch and upgrade

1. Close the game, let updates finish, and install a compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately.
2. Disable older versions and duplicate self-hit mods in Arsenal. **Enable only one of the five self-hit ZIPs.**
3. Import the selectable ZIP and choose one option under **生效範圍**. P-11 only is initially selected; confirm the mod's overall switch is enabled.
4. Clear the old deployment and redeploy before launching the game. Close and redeploy when switching, disabling or rolling back too.
5. The selectable mod keeps its original GUID. If Arsenal reports a duplicate identity, replace the old package or disable/remove its old entry before importing; do not leave both enabled.

Unknown versions stop writes. Do not bypass that check by replacing hashes.

## Recommended companion and teammate homing

**Recommended P-11 companion: [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/)**. Download it separately from its author's page and follow that page for controls and supported versions. A user also reported firing toward their own feet in first-person view; an actual dart hit on the character is still required.

Teammate locking/homing remains independently managed by the original mod, unchanged and not bundled here. This self-hit package does not aim or fire for you.

[P-11 usage and earlier reports](docs/SELF_HIT.md)

## Update diagnostics and complete source

After a game or loader update, fully extract **Update Toolkit 1.3.1** and run `Collect-HD2-Update.cmd`. It collects versions, deployed resources, relevant existing log events and five installed entity/structure/weapon/projectile data files, recording provenance, hashes and gaps. Read the Chinese summary and repair handoff under `diagnostics`.

The tool does not launch the game, read running processes, modify or deploy mods, or upload data. It gathers available offline evidence in one run; **automatic repair after every update is not guaranteed**. Complete collection or matching fingerprints do not establish gameplay success.

Complete matching source is already extracted under `Source/P11-Enhanced/`. Developers and AI agents start with `AGENTS.md` and follow the triage, porting, testing, rebuild and publishing guides. Mod rebuilding needs Python 3.10+; ordinary evidence collection does not.

| Task | Start here |
|---|---|
| Install, switch, disable or roll back | [Player guide](docs/SELECTABLE.md) |
| Collect evidence after an update | [Offline update tool](docs/UPDATE_TOOL.md) |
| Hand over to a developer or AI agent | [AGENTS.md](AGENTS.md) → [Step-by-step runbook](docs/AGENT_GUIDE.md) |
| Port and rebuild | [Build and porting](docs/PORTING.md) · [Handoff template](docs/HANDOFF_TEMPLATE.md) |
| Validate and publish | [Verification](docs/VERIFICATION.md) · [Publishing guide](docs/PUBLISH.md) |
| Copy the self-hit mod description | [Traditional Chinese copy](docs/MOD-PAGE.zh-TW.md) · [English release copy](docs/MOD-PAGE.en.md) |
| Copy the animation mod description | [Traditional Chinese animation copy](docs/RAISE-WEAPON.zh-TW.md) · [English animation copy](docs/RAISE-WEAPON.en.md) |
| Page titles, summaries, covers and paste instructions | [Mod-page publishing kit](docs/PAGE-PUBLISHING.md) |

Detailed maintenance guides and diagnostic summaries are currently primarily in Chinese. This homepage, release introduction and mod-site copy have complete Chinese and English versions.

## Changes in preview.6

- **Secondary candidate 0.1.3:** a pinned loadout-slot catalog replaces the old eight-entry recognition scope. Sixteen source candidates are split into native and entity mechanisms with explicit limits.
- **Original P-11 preserved:** the 0.2.1 ZIP/Lua and both broad 0.1.2 packages stay unchanged. Expanding the catalog does not weaken identity, ownership or write checks.
- **Toolkit 1.3.1:** directly collects five installed data files, distinguishes installed evidence from caches, and reports missing files and unresolved build correspondence.
- **Delivery and documentation:** one selectable mod, four standalone alternatives and one toolkit containing complete source, with bilingual introductions, operating navigation and an AI-agent handoff guide.

## Evidence and implementation

This candidate passed **120 Python checks, 429 P-11 Lua mock assertions and 3,322 expanded Lua mock assertions**, plus pinned-reference replay and isolated Arsenal backend checks. These are offline, packaging and synthetic-data checks, **not new in-game self-hit tests or FPS measurements**. Basic P-11 success comes from an earlier user report; new secondary behavior, host/client cases, collision timing, full coexistence and performance are not comprehensively verified.

The implementation changes source-collision exclusion only for checked, locally owned projectiles; the game handles the native effect after a hit. It uses no native hook, executable-code patch or direct health, stamina, ammo or damage-value writes.

The GitHub project remains **P11-Enhanced**. This community mod is unaffiliated with Arrowhead Game Studios; code and documentation were made with assistance from OpenAI tools. No overall project license has been selected. [Sources and dependencies](docs/THIRD_PARTY.md) · [License notice](LICENSE-NOTICE.md).