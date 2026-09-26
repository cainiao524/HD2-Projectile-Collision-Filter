# P11-Enhanced — Three self-hit variants

Data-only addons allowing eligible local projectiles to collide with their source. Native game logic handles healing or damage. No native hooks, executable patches, direct health/stamina writes, ammo or damage changes.

[繁體中文](README.md) · [Downloads](https://github.com/cainiao524/P11-Enhanced/releases/tag/v0.3.0-preview.1) · [P-11 details](docs/SELF_HIT.md) · [Variants](docs/VARIANTS.md)

## Choose one ZIP

**Every variant includes the same byte-preserved P-11 0.2.1 Lua with user-confirmed basic healing. No separate P-11 install is needed.** Expanded logic excludes P-11 and leaves its darts to the included original addon.

| ZIP | Scope | Evidence |
|---|---|---|
| `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip` | P-11 only | Original tested package; basic healing confirmed by user |
| `weapon_self_hit_pistols-0.1.0-build25480438-CANDIDATE.zip` | P-11 + native projectiles from eight candidate pistol resource IDs | Expanded gameplay and combined coexistence unverified |
| `weapon_self_hit_native-0.1.0-build25480438-CANDIDATE.zip` | P-11 + broad local weapon-owned native projectiles | Expanded gameplay and combined coexistence unverified |

“All weapons” means a broad candidate within the identified native projectile subsystem, not proven hitscan, beams, melee, explosion or entity-projectile coverage. Pistol IDs are from an older offline resource index, not eight gameplay-tested weapons.

Target: **build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17 / API 1 / internal 16**. Unknown builds stop writes. This collection is a **prerelease**: byte-identical P-11 inclusion is not proof of every combined runtime scenario.

## Install

Close the game. Install a compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately. Import **one** variant into Arsenal and disable the other variants, duplicate self-hit hooks and research addons. Enable and deploy using the manager/loader instructions. The expanded packages each have one Arsenal option controlling both included resources.

Recommended P-11 companion: [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/), downloaded separately. The user also reports shooting their own foot in first person and triggering an already-active Experimental Infusion booster. See [verification](docs/VERIFICATION.md). This project does not steer projectiles or bundle animation/homing mods.

## Collection and maintenance

The Three-Variants collection includes all three installable ZIPs, source and a self-contained Windows x64 diagnostic tool. Extract first; import the selected ZIP inside Mods, not the outer collection.

After updates finish, run **Collect-HD2-Update.cmd**. It collects offline evidence and creates three-scope comparisons and a repair handoff without launching the game, inspecting processes, deploying changes or uploading. It does not guarantee automatic repair. Developers can run **Rebuild-Mods.cmd** after a reviewed source port; this requires Python 3.10+.

[Build and porting](docs/PORTING.md) · [Sources](docs/THIRD_PARTY.md) · [License notice](LICENSE-NOTICE.md). No overall project license has been selected.
