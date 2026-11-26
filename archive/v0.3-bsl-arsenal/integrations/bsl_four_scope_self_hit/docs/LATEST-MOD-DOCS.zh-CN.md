# 最新 HD2 Lua/BSL 资料

- [Bingus Shared Loader 技术说明](https://github.com/CowboyBingus/BingusSharedLoader/blob/main/docs/TECHNICAL.md)：API 1、声明式 addon、资源校验和重复加载保护。
- [Bingus Shared Loader v18](https://github.com/CowboyBingus/BingusSharedLoader/releases)：共享 LuaJIT cache 优化。
- [HD2Runtime](https://github.com/SkyeShade/HD2Runtime)：ModTemplate、语义化 API 和更新迁移。
- [Reinforcement Beacons Fixed](https://github.com/CowboyBingus/ReinforcementBeaconsFixed)：build 25480438 的 data-only BSL 参考。
- [hd2-lua-mod-skill](https://github.com/MrChengl11/hd2-lua-mod-skill)：LuaJIT FFI、离线模拟和写入回读验证。
- [Junze HD2 Lua Mod](https://github.com/junze0910/junze-hd2-lua-mod)：Scanner 和表定位研究参考。
- [hd2-mod-update-skill](https://github.com/starmatch666-droid/hd2-mod-update-skill)：构建锁、只读探针和 fail-closed 更新流程。

本项目采用这些资料的共同边界：单一 BSL Lua gameplay 模块、固定 build/SHA/锚点、无 game.dll 指令补丁、无全表 Scanner 扫描。
