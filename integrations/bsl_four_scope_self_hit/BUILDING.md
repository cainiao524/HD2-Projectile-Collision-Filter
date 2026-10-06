# Build

在此目录执行 `python -B build.py`。构建只编译 LuaJIT、生成四个 profile bundle、制作 resource archive 和确定性 ZIP，不访问游戏进程，也不部署到游戏目录。构建失败时不会生成可用包。

需要 Python、`lupa.luajit21` 和仓库内 `tools/resource_archive.py`。
