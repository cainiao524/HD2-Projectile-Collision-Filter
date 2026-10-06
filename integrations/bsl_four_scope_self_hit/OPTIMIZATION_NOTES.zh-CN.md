# 四范围版本的优化说明

四个选项共用同一套安全核心，只改变候选分类：P-11、全部手枪、排除霰弹的原生武器、包含霰弹的原生武器。

- 保留 cursor 增量队列，不回到每帧全环扫描。
- 在读取 owner、flags、weapon 和 definition 之前，先读取 4 字节 projectile type；P-11 与“不含霰弹”范围遇到非目标类型或霰弹／多弹丸类型时立即丢弃，不再继续读取该候选。
- 保留每枚候选的来源 unit/entity、武器资源、owner、definition、slot type 和 flags 写前复核。
- 将指针读取从 `uint64_t[1]` cdata 临时值改成 LuaJIT 可精确表示范围内的两个 32 位半部解码。
- 将 map bucket 的 uint64 临时乘法改成 16 位 limb 的低 32 位计算。
- 继续排除光束、喷雾和未经确认的特殊 entity 路径；包含霰弹的范围可能有较高开销。

参考方法来自 [hd2-lua-mod-skill](https://github.com/MrChengl11/hd2-lua-mod-skill)、[junze-hd2-lua-mod](https://github.com/junze0910/junze-hd2-lua-mod) 和 [hd2-mod-update-skill](https://github.com/starmatch666-droid/hd2-mod-update-skill)。这些仓库用于离线回归、缓冲/工作量边界和资源身份核验；没有直接复制它们的地址或部署脚本。


## test.8 类型预筛选与批量读取

在 burst queue 达到 8 个以上时，连续 64 个 slot 的 projectile type 使用一个连续读取块，连续 32 个 slot 的 source owner 再使用一个连续读取块；单发仍使用小范围读取。类型批量数据只用于快速筛选，每个本机候选在写入前重新读取 owner、flags 并通过 guards/readback。Junze Scanner 只作为静态表定位参考，没有接入每帧动态弹头处理。

这不能把 cursor 遍历本身变成零成本，因为当前 Lua 接口没有提供“只枚举本机 owner 弹头”的索引；它避免的是对霰弹多弹头和其他明显不匹配候选继续做 owner、flags、武器与定义读取。
