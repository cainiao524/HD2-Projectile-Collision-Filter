# Projectile Self Hit — HellForge v1

![Projectile Collision Filter / 投射物碰撞過濾器](docs/assets/projectile-collision-filter-cover.png)

[繁體中文](README.md) · [Download v1.0.0](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v1.0.0) · [How it works](docs/HOW-IT-WORKS.md) · [Changelog](CHANGELOG.md) · [Archived versions](archive/README.md)

Lets your Helldiver's own projectiles hit you. It started as **P-11 Stim Pistol self-healing** and now offers four scopes up to every Helldiver weapon. The game's own collision and hit logic does the rest: this mod writes no health and simulates no healing. It only makes the chosen projectile types spawn without the "exclude owner" flag.

**This is the HellForge edition.** The old Arsenal/BSL edition (v0.3.0-preview.8 and earlier) cleared the flag shot by shot after each projectile spawned, which dropped frames with shotguns and heavy fire. v1 decides at the source of the flag: each projectile costs one table lookup, whatever the scope or pellet count.

## Two downloads

| File | What it is |
|---|---|
| `Projectile-Self-Hit-HellForge-v1.0.0-build25480438.zip` | **The mod (required)**: HellForge code mod `local.p11-self-hit-fast`, as sources; HellForge builds it. |
| `Projectile-Self-Hit-Options-MOM-v1.0.0.zip` | **In-game menu (optional)**: pick the scope under ESC > MODS (Mod Options Menu); APPLY takes effect at once. |

SHA-256 sums are in the [release notes](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v1.0.0). GitHub's automatic Source code archives are the whole repository, not an install package.

## Scopes (pick one)

| Choice | Covers |
|---|---|
| **P-11 Only / 僅治療手槍** | The P-11 stim dart only. Recommended, default. |
| **All Sidearms / 手槍全部** | P-11 and sidearm projectiles; no shotguns or multi-pellet rounds. |
| **All Weapons (No Shotguns) / 全部武器不包括霰彈槍** | Primary, support and sidearm projectiles; no shotguns or multi-pellet rounds. |
| **All Weapons (Including Shotguns) / 全部武器包括霰彈槍** | Everything, shotguns included. Pellets can hit you at the muzzle; the mod itself costs nothing more. |

Damaging weapons that hit you deal their native damage: you can hurt yourself.

## Install

1. Close the game. On HellForge's Mods page, drop `Projectile-Self-Hit-HellForge-v1.0.0-build25480438.zip` into the mods folder (or unpack it there) and switch on **Projectile Self Hit / 子彈能擊中自己**.
2. **Run one self-hit mod at a time**: switch off `cainiao524.p11-self-hit` (0.5.x), the BSL four-scope build and the Arsenal Projectile Collision Filter.
3. For the in-game menu, also install [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) and [Mod Options Menu](https://github.com/CowboyBingus/ModOptionsMenu), then add and enable `Projectile-Self-Hit-Options-MOM-v1.0.0.zip`. In game: **ESC > MODS > PROJECTILE SELF HIT**, choose **Effect Scope / 生效範圍**, press APPLY (Tab).
4. Without the menu: edit `self-hit.ini` in the mod's folder (created on first run), `scope=1` to `4`; a saved change applies within about 2 seconds. With the menu, the file follows the menu.

Targets **Steam build 25480438** (the build HellForge supports). On another build, or when the bytes at the patch site are not the expected vanilla code, the mod changes nothing and says why in `mod-local.p11-self-hit-fast.log`.

## How it works (short)

The projectile constructor (`game.dll+0x13a9830`) composes a flags word for every projectile; bit `0x20` is "exclude owner", and the hit test (`+0x13ac6a1`) skips the shooter while it is set. v1 replaces the 20 bytes that choose that bit (`+0x13a9bbd`) with an absolute jump to a small stub of its own: it looks the projectile type up in a 1024-byte table, leaves `0x20` off for listed types, runs the vanilla choice for the rest, and jumps back.

- No hook, no per-frame scan of the projectile pool, no heap writes; changing the scope only rebuilds the table.
- The table comes from the projectile types the weapons' records name (primary/support/sidearm catalogue from the HellForge SDK); shotguns are recognised by name and by pellets per shot.
- The menu pack is a tiny BSL Lua addon: it registers one option with Mod Options Menu and hands the applied value to the loaded DLL (`p11_self_hit_set_scope`). It touches no projectile and no game memory.

Addresses, assembly and checks: [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md).

## Known limits

- The rule is per **projectile type**: a sentry, vehicle or enemy that fires the same type as a chosen weapon also stops excluding its own shooter (not checked one by one).
- Multiplayer: each machine patches only its own simulation. Teammates without the mod are unaffected; their projectiles of a chosen type, simulated on your machine, also spawn without owner exclusion, and how that plays out is not fully verified.
- Projectile weapons only; beams, sprays and arcs are outside every scope.
- The author has tested it in game; there is no full per-weapon or host/client test matrix yet.

## Pairs well with

[Raise Weapon: Aim at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/) for the P-11 (separate download), or shoot at your own feet in first person.

## Building from source

- The mod: copy `hellforge/p11-self-hit-fast` into HellForge's `mods` folder and press **Build now**, or run `HellForge.Cli build-mod --mod <that folder>` (game closed).
- The menu pack: `python -I tools/build_options_pack.py` rebuilds `hellforge/p11-self-hit-options` from `hellforge/options-addon/p11_self_hit_options.lua`.
- Release ZIPs: `python -I tools/package_release.py` → `dist/` (reproducible, with SHA256SUMS).
- Menu integration test (no game): `luajit tests/test_options_addon.lua <p11_self_hit_fast.dll> hellforge/options-addon/p11_self_hit_options.lua`.

## Credits and licence

[HellForge](https://github.com/SkyeShade/HellForge) (SkyeShade) provides the mod SDK. [Mod Options Menu](https://github.com/CowboyBingus/ModOptionsMenu) and [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) (CowboyBingus) are external dependencies; this repository neither contains nor redistributes them. See [LICENSE-NOTICE.md](LICENSE-NOTICE.md).
