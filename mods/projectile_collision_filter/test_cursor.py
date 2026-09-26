"""Bounded scheduler regressions; only synthetic Lua memory is used."""
from pathlib import Path
import json

from lupa.luajit21 import LuaRuntime

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "p11_self_hit_dataonly"


def main():
    lua = LuaRuntime(encoding=None, unpack_returned_tuples=True)
    lua.globals()[b"Core"] = lua.execute((HERE / "core.lua").read_bytes())
    lua.globals()[b"Fixture"] = lua.execute((ORIGINAL / "test_fixture.lua").read_bytes())
    checks = lua.execute((HERE / "test_cursor.lua").read_bytes())
    print(json.dumps({"cursor_assertions": checks, "live_process_access": False,
                      "gameplay_verified": False}, indent=2))


if __name__ == "__main__":
    main()
