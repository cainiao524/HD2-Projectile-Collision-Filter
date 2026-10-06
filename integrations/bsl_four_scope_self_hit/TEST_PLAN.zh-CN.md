# Test plan

1. 运行 `python -B build.py`，确认 LuaJIT、归档和 ZIP 检查通过。
2. 在 Arsenal 只启用一个四范围选项，确认日志含 `LOADER: API=1`、`internal=16/17`、`BSL Lua only`、`ENABLED`。
3. 离线/solo 分别测试 P-11、普通手枪、无霰弹原生武器和含霰弹范围；记录自命中、治疗和 Watchdog。
4. 取消旧包后重复测试，确认没有冲突日志、长帧或全表扫描成本。
