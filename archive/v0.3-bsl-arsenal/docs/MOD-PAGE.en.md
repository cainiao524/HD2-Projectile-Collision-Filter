# Projectile Collision Filter page copy (English)

## Title

Projectile Collision Filter — P-11 Self-Healing & Four Selectable Scopes

## Short description

Let your P-11 darts heal you through native collision. Four bilingual Arsenal scopes share one cursor-based core. Offline update tools and complete source included. Including shotguns may cause severe performance impact.

## Body

![Projectile Collision Filter / 投射物碰撞過濾器](https://raw.githubusercontent.com/cainiao524/HD2-Projectile-Collision-Filter/v0.3.0-preview.8/docs/assets/projectile-collision-filter-cover.png)

## Let your P-11 darts heal their owner

An actual P-11 dart fired by you can hit your own character and trigger native collision and healing. You aim and fire manually; native ammo consumption, fire rate, healing amount and effects remain. No direct health or stamina writing is used.

**v0.3.0-preview.8 is a four-choice integrated prerelease.** The user reports normal basic operation with all four choices. Release packaging preserves the tested four Lua payloads and game resources while updating bilingual configuration, copy, tools and artwork. Full per-weapon, host/client, concurrency and performance coverage is still incomplete.

## One Arsenal mod, four scopes

Configuration is English first, followed by Traditional Chinese. Choose one under **Effect Scope / 生效範圍**:

- **P-11 Only / 僅治療手槍**: P-11 healing darts only. Recommended and initially selected.
- **All Sidearms / 手槍全部**: P-11 and supported sidearm projectiles; excludes shotgun and multi-projectile types.
- **All Weapons (No Shotguns) / 全部武器不包括霰彈槍**: P-11 and supported weapon projectiles; excludes shotgun and multi-projectile types.
- **All Weapons (Including Shotguns) / 全部武器包括霰彈槍**: Includes shotgun and multi-projectile types. **WARNING: May cause severe performance impact. 警告：可能造成嚴重性能影響。**

Arsenal controls overall enable/disable. Close the game before changing the scope, then redeploy. Do not manually copy all four resource variants together.

## Performance changes

One shared core and addon follows the allocation cursor, checking recent projectile candidates with bounded retries instead of the historical repeated traversal of all 2,048 slots. Local ownership, weapon/projectile identity, original-value checks, fresh write guards and readback remain mandatory.

An earlier user report confirmed healing and roughly **70 → 130 FPS with P-11 0.2.3**. It was a single older-candidate report without a complete benchmark setup, **not a fixed gain for the four preview.8 scopes**. Candidate checks still have a cost; heavy traffic, expired hints or collision timing can cause skipped projectiles. Zero overhead, no stutter and success on every shot are not promised.

## Downloads: two ZIPs

- [Four-choice integrated mod ZIP](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438.zip): import into Arsenal.
- [Update Toolkit 1.3.2](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/download/v0.3.0-preview.8/HD2-Projectile-Collision-Filter-Update-Toolkit-1.3.2-win-x64.zip): extract separately for one-click offline evidence collection after game/loader updates. Includes complete matching source, build tools and AI/Agent handoff guides. Do not import into Arsenal.

[Release and SHA-256 checksums](https://github.com/cainiao524/HD2-Projectile-Collision-Filter/releases/tag/v0.3.0-preview.8) · [GitHub source](https://github.com/cainiao524/HD2-Projectile-Collision-Filter)

Four standalone mod ZIPs are no longer separately published. Historical releases remain available for rollback. GitHub's automatic Source code archives are not installable mods.

## Install and use

1. Close the game and finish updates. Install a compatible [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately.
2. Disable old self-hit/healing versions, the 0.2.3 test package, duplicate self-hit packages and research addons in Arsenal, then purge the old deployment.
3. Import the integrated ZIP; replace the old entry if the preserved GUID is detected. **Enable only one self-hit package.**
4. Select one Effect Scope, enable the overall mod, redeploy and launch the game.
5. Equip P-11, aim and fire manually. The dart must actually hit your character; enabling the mod alone does not heal you.
6. Close, purge and redeploy before switching, disabling or rolling back.

Target: **Steam build 25480438 / EXE 1.8.46015.0 / Bingus Shared Loader v17, API 1, internal 16**. Unknown versions stop writes; swapping hashes alone is not a valid port.

## Recommended companion: Raise Weapon: Aim at Yourself

Download [Raise Weapon: Aim at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/) separately, equip the Raise Weapon emote and follow its page. That mod changes the pose; this package changes eligible projectile self-collision. A user also reported first-person shots toward their own feet.

Experimental Infusion must already be active in the game. Earlier user feedback reports its effects can trigger with a P-11 self-hit; this mod does not activate the booster. Teammate homing remains the original separately managed mod, not bundled or modified here. This package does not aim or fire automatically.

## Support limits

- All Sidearms uses pinned secondary-slot reference data beyond the historical eight-ID list. This does not establish support for every secondary firing mechanism.
- Dagger beam and Crisper spray are unsupported. Warrant, P33 and internal Hornet entity follow-up collisions/effects remain unverified.
- Plasma/grenade-body hits and later explosions or area effects require separate evidence. All Weapons means supported native projectile paths, not every damage mechanism. Damaging weapons may hurt you.
- The first three choices exclude shotgun/multishot types; choices 2 and 3 also conservatively skip out-of-reference types. Including shotguns may cause severe performance impact.
- Offline diagnostics do not launch the game, read processes, deploy or upload. Complete collection, candidates, historical logs and matching hashes do not establish new gameplay success.

[Full usage and maintenance navigation](https://github.com/cainiao524/HD2-Projectile-Collision-Filter). The addon clears only source-collision exclusion on checked local projectiles. It uses no native hook, executable patch, global-definition change or direct health/stamina/ammo/damage write.

Cover artwork is promotional, not a gameplay screenshot. Community mod unaffiliated with Arrowhead Game Studios; OpenAI tools assisted development and documentation.
