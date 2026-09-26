# P11-Enhanced — P-11 Self-Hit Healing

[繁體中文](README.md)

**Allow your own P-11 darts to hit your character and trigger native healing.**
This standalone addon makes a narrow data change. It installs no native hook, patches no executable code, and does not write health or stamina directly.

## Features and supported version

Eligible darts must pass local-player, P-11 weapon and projectile identity checks. Ammo, fire rate, healing amount and effects retain their native behavior. The addon uses Bingus Shared Loader API 1 and is enabled or disabled through Arsenal.

**Version 0.2.1 was confirmed working by the user on Steam build 25480438 / EXE 1.8.46015.0, with Shared Loader v17 / API 1 / internal 16.** Logs corroborate activation and data-write readback; actual healing is confirmed by the user's report. Full host/client, collision-timing and concurrency coverage remains incomplete.

## Downloads

- `P11-Self-Hit-DataOnly-0.2.1-build25480438.zip`: the exact tested gameplay ZIP; import into Arsenal.
- `P11-Self-Hit-Source-v0.2.1.zip`: self-hit source, packaging tools, Lua mock tests and documentation.
- `SHA256SUMS.txt`: checksums for both ZIPs.

The tested ZIP is preserved byte for byte. Its original experimental labels reflect the packaging date; the later basic-healing confirmation is recorded in this release documentation and maintenance/baselines.json.

## Installation

Close the game. Install [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) separately, import the self-hit ZIP into Arsenal, disable older self-hit hooks/duplicate versions/research addons, then enable and deploy the addon and loader. Follow the loader's priority instructions. To disable the addon, close the game, disable its Arsenal entry and redeploy.

Healing requires a real P-11 dart to hit your character. This addon does not steer darts toward yourself.

## Recommended companion

**We recommend pairing P-11 self-hit healing with [Raise Weapon Aims at Yourself](https://ayakamods.com/mods/raise-weapon-aims-at-yourself.3946/).**
This optional mod is available separately from its author's page. Follow that page for installation, controls and supported versions.

## Source and maintenance

The gameplay core is 97 lines of Lua. See [reproducible builds and maintenance](docs/PORTING.md), [validation scope](docs/VERIFICATION.md), [provenance](docs/THIRD_PARTY.md) and [licensing notice](LICENSE-NOTICE.md).

Unknown game versions are rejected. Updating hashes alone does not establish the validity of native layouts or healing behavior. No repository-wide license has been selected. Development and documentation were assisted by OpenAI tools.
