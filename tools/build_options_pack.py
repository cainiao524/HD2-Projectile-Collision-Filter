"""Builds the options pack: a manifest-only pack (no hellforge-mod.json) holding one Bingus Shared Loader addon,
hellforge/options-addon/p11_self_hit_options.lua, which registers the scope choice in Mod Options Menu.

  python -I tools/build_options_pack.py [out_dir]      (default: hellforge/p11-self-hit-options/)

The addon is a stingray patch (9ba626afa44a3aa3.patch_0) with one lua resource named murmur64 of the path in its
first line ("-- HD2-Addon: mods/local/p11_self_hit_options"), data = u32 text length, u32 2, then the source text:
the layout of the third-party addons Bingus Shared Loader v20 discovers (e.g. mods/suzuka/extra_slot).
"""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import patchwriter  # noqa: E402  (tools/patchwriter.py)

LUA_TYPE = "a14e8dfa2cd117e2"  # murmur64("lua")
GUID = "5e1f7a2c-3b9d-4c6e-8a01-7d2f4b9c0e35"


def murmur64(data, seed=0):
    m, mask = 0xC6A4A7935BD1E995, (1 << 64) - 1
    h = (seed ^ (len(data) * m)) & mask
    n = len(data) // 8
    for i in range(n):
        k = int.from_bytes(data[i * 8:i * 8 + 8], "little")
        k = (k * m) & mask; k ^= k >> 47; k = (k * m) & mask
        h ^= k; h = (h * m) & mask
    tail = data[n * 8:]
    if tail:
        h ^= int.from_bytes(tail, "little"); h = (h * m) & mask
    h ^= h >> 47; h = (h * m) & mask; h ^= h >> 47
    return h


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "hellforge", "p11-self-hit-options")
    src = open(os.path.join(ROOT, "hellforge", "options-addon", "p11_self_hit_options.lua"), "rb").read()
    first = src.split(b"\n", 1)[0].decode()
    path = re.match(r"^-- HD2-Addon: (mods/[A-Za-z0-9_]+/[A-Za-z0-9_/]+)$", first.strip()).group(1)
    assert murmur64(b"lua") == int(LUA_TYPE, 16)
    name = f"{murmur64(path.encode()):016x}"
    data = struct.pack("<II", len(src), 2) + src
    n = patchwriter.write_patch(os.path.join(out, "Addon", "9ba626afa44a3aa3.patch_0"), [(LUA_TYPE, name, data, b"", b"")])
    manifest = {
        "Version": 1,
        "Guid": GUID,
        "Name": "Projectile Self Hit Options / 子彈能擊中自己 選單",
        "Description": "Puts the scope of local.p11-self-hit-fast in game under ESC > MODS (Mod Options Menu). Needs "
                       "Bingus Shared Loader, Mod Options Menu and the code mod enabled. Applies at once on APPLY.\n"
                       "把 local.p11-self-hit-fast 的生效範圍放進遊戲內 ESC > MODS（Mod Options Menu）。需要 Bingus Shared "
                       "Loader、Mod Options Menu 與本體 code mod 都啟用。按 APPLY 立即生效。",
        "Options": [{"Name": "Projectile Self Hit Options / 子彈能擊中自己 選單",
                     "Description": "Mod Options Menu addon (mods/local/p11_self_hit_options).", "Include": ["Addon"]}],
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"{out}: {path} -> lua {name}, {len(src)} bytes source, {n} resource")


if __name__ == "__main__":
    main()
