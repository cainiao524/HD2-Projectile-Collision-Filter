# How it works / 原理

Game build 25480438. Offsets are from `game.dll`'s image base. 以下位址皆為 `game.dll` 映像基址的偏移。

## Where owner exclusion comes from / 「排除擁有者」從哪來

| Offset | Code | Meaning |
|---|---|---|
| `0x13a9830` | projectile constructor `spawn(pool, descriptor, options)` | `options` arrives in `r8`, kept in `r13` |
| `0x13a9a5b` | `test r13, r13` | its flags are still live at `0x13a9bbd` |
| `0x13a9bb3` | `mov ecx, [rax]` / `mov [rsi+r12*4+0E5040h], ecx` | `ecx` = the new projectile's type, stored in the pool's type column |
| `0x13a9bbd`–`0x13a9bd1` | 20 bytes choosing `r8w` = 0 or `0x20` | `0x20` unless `options` is non-NULL and `options+0x18` is 0 |
| `0x6165c2` | `mov byte [rbp+38h], 1` | the gun route always asks for owner exclusion |
| `0x13a9c49` | `mov [rsi+r12*2+203Ch], dx` | the per-slot flags word |
| `0x13ac68f` | compare with `pool+0x3b04c` | hits on the firing weapon's own entity are always skipped |
| `0x13ac6a1` | `test byte [..+203Ch], 20h` | hits on the owner unit are skipped while `0x20` is set |
| `0x13ae71a` | `and word [..+203Ch], 0FFDFh` | vanilla clears `0x20` when a projectile ricochets |

Nothing outside `0x13a9bbd`–`0x13a9bd1` jumps into it (checked by disassembling the whole constructor).

## The patch / 補丁

At `HF_EVENT_GAME_LOADED` the mod checks the 30 bytes at `0x13a9bb3` against the vanilla code and the bytes at `0x13a9a5b`, `0x13a9c49` and `0x13ac6a1` (`code_matches`), then writes a 14-byte absolute jump (`FF 25 00000000 <stub>`) plus 6 × `CC` over `0x13a9bbd`. The stub, in a page it allocates and makes read-execute:

```
     je   L20                 ; options NULL -> 0x20 (vanilla)
     cmp  ecx, 1024
     jae  VAN
     mov  r8, <table>         ; one byte per projectile type, read-write page
     cmp  byte [r8+rcx], 0
     jne  SELF
VAN: cmp  byte [r13+18h], bl  ; vanilla test
     jne  L20
     movzx r8d, bx            ; vanilla: option 0
     jmp  BACK
SELF: xor r8d, r8d            ; no "exclude owner"
     jmp  BACK
L20: mov  r8d, 20h
BACK: jmp [rip+0] -> game.dll+0x13a9bd1
```

The code after `0x13a9bd1` sets the flags (`and ax, 10h`) before any branch reads them. Each projectile pays two jumps and one byte read; nothing runs per frame for shots.

## The table / 查表

Built on the game thread (`on_game_thread`) only when the scope changes or the weapons' data loads:

- scope 1: type 318 (the P-11 stim dart: `apply_stim_on_target`, `projectile_auto_attach`).
- scopes 2–4: plus the projectile types the armory weapons' records name, read with `get_live` (`ProjectileWeapon.projectile`, `weapon_function_projectile_type`, `WeaponMagazine.first_projectile` and `pattern[32]`, `WeaponHeat` / `WeaponCharge` level 1–3, `WeaponRounds` primary/alternate). Scope 2 takes sidearms only. The weapon catalogue (`src/weapon_catalog.h`) is generated from the HellForge SDK's `hellforge_content.h` by `tools/gen_weapon_catalog.py`.
- scopes 2–3 skip shotguns: a weapon named `SG-…` or "shotgun", and any type whose settings row says more than one projectile per shot (`ProjectileSettings +0x1C`).

The log lists every type in the table after each rebuild.

## The menu / 選單

`hellforge/options-addon/p11_self_hit_options.lua` is a Bingus Shared Loader addon (first line `-- HD2-Addon: mods/local/p11_self_hit_options`). `tools/build_options_pack.py` stores it as the one `lua` resource (name = murmur64 of that path; data = u32 length, u32 2, the source) of `Addon/9ba626afa44a3aa3.patch_0`.

On each game update until it is done, it looks for `p11_self_hit_fast.dll` among the loaded modules (`GetModuleHandleA` / `GetProcAddress`; it never loads a DLL from disk) and for the global `ModOptionsMenu`. It then registers the choice `local_p11_self_hit.scope` (mod_id `local.p11-self-hit-fast`, default = the DLL's current scope), sends the saved value, and sends every applied change. `p11_self_hit_set_scope` only records the request; the next game-thread tick rebuilds the table and writes `self-hit.ini`, so the next session starts with the same scope before the menu registers.
