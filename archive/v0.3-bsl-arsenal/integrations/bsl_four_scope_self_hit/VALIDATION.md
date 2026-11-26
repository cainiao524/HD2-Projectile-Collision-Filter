# Validation

构建脚本会验证四个 profile 的 build、game/exe hash、12 个代码锚点、3 个 cursor 锚点、8 个研究锚点、resource/GUID/version 和 Loader API 1 internal 16/17。每个 Lua bundle 会先用 LuaJIT 编译，再进行 resource archive round-trip 和 ZIP CRC/readback。

本候选明确 `native_patch=false`、`native_hook=false`。`data_windows.lua` 只对已授权的运行时 slot 写入两字节 flags，并在写入前后重新读取全部 guards。脚本没有 Native executable patch capability。

玩法、自命中和性能字段保持 false，等待离线/solo 实测。
