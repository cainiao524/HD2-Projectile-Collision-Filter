# HD2 BSL Four-Scope Self-Hit

Helldivers 2 的 Bingus Shared Loader Lua addon，用于让本机 projectile 命中本机玩家。最终包提供四个互斥范围：P-11、全部手枪、排除霰弹的原生武器、包含霰弹的全部原生武器。

P-11 是推荐范围。全部原生武器（含霰弹）只适合诊断，可能增加 update 成本。项目不修改 `game.dll` 指令、不安装 native hook、不扫描整张弹头表。

- 中文说明：[README.zh-CN.md](README.zh-CN.md)
- 项目总结：[docs/PROJECT-SUMMARY.zh-CN.md](docs/PROJECT-SUMMARY.zh-CN.md)
- 最新资料：[docs/LATEST-MOD-DOCS.zh-CN.md](docs/LATEST-MOD-DOCS.zh-CN.md)
- 构建：`python -B build.py`
- 验证：`python -B tests/test_package.py`
- 发布 ZIP：`dist/Projectile-Collision-Filter-BSL-Four-0.3.2-bsl-four-build25480438.zip`
- SHA-256：`F5DF9FCA30D0A28712A4F3835D2537B082703A8BF240E4CD3E2A96A7F2343BE1`

目标游戏 build：`25480438`。当前版本的玩法、自命中、多人同步和实机性能仍需独立测试。
