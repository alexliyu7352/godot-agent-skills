---
name: godot-debugging
description: "Use when a Godot error, crash, missing node, duplicate signal, asynchronous lifecycle bug, resource load failure, or measured performance regression needs diagnosis. Not for routine implementation or hypothetical optimization. 适用于可复现故障与性能回退。"
license: Apache-2.0
---

# Godot 定位与修复

## 适用边界
针对具体故障或可测量性能回退。已有明确根因时直接修复和验证，不为满足模板重做调查；没有问题证据时不启动全工程优化。

## 工作方法
1. 记录失败操作、实际错误、引擎/构建版本、相关场景和最小复现。区分解析、导入、初始化、运行时、渲染和退出阶段，先修最早的原因，避免逐条压制连锁报错。
2. 用日志、调用栈、Remote 场景树、断点或已有测试验证一个具体假设。缺节点时确认真实路径/owner/初始化时机；类型错误时核对实际类型和对应版本 API，不先加 `has_method()` 掩盖必需接口缺失。
3. 重复回调检查连接来源、生命周期和重复进入场景；异步问题检查对象是否已释放、结果是否过期、等待是否可取消。不要在每次出错位置增加无意义的空值返回。
4. 物理回调中的状态修改，按具体报错使用 deferred 等合法时机；不要把所有更新都延迟。Resource 缓存共享与写盘是不同问题。
5. 性能问题在目标场景测量帧时间、调用次数、对象增长和资源加载。先找热点再改，保持相同输入/规模比较；不凭语言、节点数或接口名称宣称固定倍数提升。
6. 修复后重跑原复现和受影响路径，保留必要的回归检查，清除临时噪音日志。遇到相同失败循环时检查假设与工具证据，不继续重复同一命令。

## 交付
说明根因证据、最小修复、实际通过的复现/检查和残余限制。严重级别以实际损害和触发条件确定，代码风格建议不自动等于阻断合并。

## 按需参考
- 症状到证据：[排错矩阵](references/diagnosis.md)。
- 采样与回归：[性能定位](references/performance.md)。
- 来源及改写：[来源记录](references/sources.md)。
