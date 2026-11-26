# Changelog

## v1.0.0 — HellForge edition, two packages / HellForge 版・雙包

- New HellForge code mod `local.p11-self-hit-fast` ("Projectile Self Hit / 子彈能擊中自己"). It patches the projectile constructor where the "exclude owner" flag `0x20` is chosen (`game.dll+0x13a9bbd`, a jump to a table-lookup stub), so the chosen projectile types spawn able to hit their shooter. No hook, no per-frame pool scan, no heap writes: one table lookup per projectile in every scope, which removes the frame drops the shot-by-shot flag clearing of the older builds had with shotguns and heavy fire.
- Same four scopes as before: P-11 Only / All Sidearms / All Weapons (No Shotguns) / All Weapons (Including Shotguns); the first three skip shotguns and multi-pellet rounds.
- New optional pack `Projectile-Self-Hit-Options-MOM`: a Bingus Shared Loader addon that puts the scope in game under ESC > MODS (Mod Options Menu); APPLY takes effect at once. Without it, `self-hit.ini` in the mod folder sets the scope.
- Repository reorganised: HellForge v1 at the root; the Arsenal/BSL line (v0.2.1 – v0.3.0-preview.8, toolkit, BSL four-scope candidate, docs and evidence) moved unchanged to `archive/v0.3-bsl-arsenal/`. Historical tags and release assets stay.

Earlier versions: [archive/v0.3-bsl-arsenal/CHANGELOG.md](archive/v0.3-bsl-arsenal/CHANGELOG.md).
