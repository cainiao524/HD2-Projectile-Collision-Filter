# BSL 四范围自命中脚本候选

这是针对 build `25480438` 的 Bingus Shared Loader API 1 Lua addon。它不修改 `game.dll` 可执行指令，不安装 native hook，也不扫描整张 projectile 表。每个范围使用同一个 cursor 增量处理器：先读 type，再读本机 owner，最后在完整 guard 和回读验证下清除运行时 `0x20` 排除 owner 位。

## 四个范围

- **P-11 Only**：只接受 projectile type 318，使用最小预算。
- **All Sidearms**：P-11 与已分类副武器，排除霰弹/多弹丸类型。
- **Native Weapons (No Shotguns)**：原生武器范围，排除已知霰弹/多弹丸类型。
- **Native Weapons (Including Shotguns)**：允许霰弹/多弹丸，但使用更紧的每次更新预算；高 burst 时可能延迟或丢弃提示。

四个选项互斥，只启用一个。P-11 范围和其它范围使用不同 marker 但共享冲突检查，会拒绝旧的自命中实验包。

## 性能边界

没有 projectile-create 回调时，Lua 必须通过 cursor 变化发现新槽位，因此不能承诺绝对零额外读取。空闲时采用 system/cursor 快速路径，每 30 个空闲更新才刷新完整身份；cursor 变化后只处理有界队列。预算为：P-11 64 pending/32 inspect/4 writes，普通范围 128/64/16，含霰弹范围 64/32/8。超出预算会延后或丢弃候选，不会扩展为全表扫描。

## 兼容性和安装

目标游戏 build 为 `25480438`，EXE/game SHA-256 在 profile 中锁定；Loader API 1、internal 16/17（对应 v17/v18）。Arsenal 中只导入本 ZIP，选择一个范围，停用旧 native、旧 test8 和 P-11-only 包。日志应出现 `BSL Lua only`、`scope=...`、`ENABLED`；出现 `STOPPED` 或 `WAITING IMAGE` 时保持停用。

玩法、自伤和实机帧时间目前仍标记为未验证。
