# 项目总结

## 目标

让本机生成的 Helldivers 2 projectile 能命中本机玩家，重点支持 P-11 治疗手枪，并提供四个互斥范围。

## 最终方案

项目从 native constructor 一字节补丁改为 BSL Lua runtime。脚本不修改 `game.dll` 指令，不安装 native hook，也不使用 Junze Scanner 全表扫描。它通过 projectile cursor 增量发现候选，先按 projectile type 过滤，再验证本机 owner、武器资源、本机 avatar 挂接、definition、slot generation 和 system 指针，最后只清除当前槽位运行时 `0x20` 排除 owner 位并回读验证。

空闲时只读取 system pointer 和 cursor；每 30 次刷新完整身份。每个范围都有 pending、inspect、write、read 和 byte 上限，超出后延迟或放弃，避免扩展为无界扫描。

## 四个范围

| 范围 | 行为 | 建议 |
|---|---|---|
| P-11 Only | 仅 projectile type 318 | 首选，开销最低 |
| All Sidearms | 登记副武器，排除霰弹/多弹头 | 需要全部手枪时使用 |
| Native Weapons No Shotguns | 原生武器，排除已知霰弹/多弹头 | 普通武器测试 |
| Native Weapons Including Shotguns | 包含霰弹和多弹头 | 仅诊断，开销最高 |

## 兼容边界

目标 build 为 `25480438`，锁定 game/exe SHA-256、PE section 和代码锚点，支持 Loader API 1、internal 16/17。任何 build、文件、锚点或 owner route 不匹配都会 fail-closed。

## 验证状态

已通过 LuaJIT 编译、四个 bundle 编译、资源归档 round-trip、ZIP CRC、资源名哈希、确定性构建和更新工具 `inspect/verify`。尚未宣称实机自命中、多人同步或 Watchdog FPS 结果。BSL 没有公开 projectile-create 回调，因此 Lua 方案不能保证绝对零额外读取。

## 历史问题

早期 native 版本会在启动阶段修改可执行代码，曾出现游戏启动异常；该路径已退出最终包。旧 test8 的离线测试 pin 仍锁定旧 GUID/资源名，不能作为本项目最终包的测试入口。
