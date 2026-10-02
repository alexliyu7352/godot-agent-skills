---
name: godot-code-scenes
description: "Use when changing Godot GDScript or C# scene integration, node ownership, lifecycle, scene instantiation, resource references, or .tscn serialization. Not for UI-only styling, narrative text, or unrelated code. 适用于场景结构与脚本集成。"
license: Apache-2.0
---

# Godot 代码与场景

## 适用边界
处理脚本与场景协作、节点生命周期、实例化和序列化。已有明确改动时直接工作；不因调用本技能重新规划整个游戏。只改文本、Theme 或间距时不需要本技能。

## 先读什么
查看实际受影响脚本、场景、项目入口和项目已有规范。确认工程锁定的 Godot 版本、语言、主场景、相关 Autoload 与节点契约；已有有效上下文就复用，不重复扫描仓库。项目使用 C# 就沿用对应 .NET 流程，不转换为 GDScript。

## 工作方法
1. 保留现有编辑方式。手工维护的场景做最小差异修改；仅对已决定程序生成的场景采用构建器。避免多个执行者或编辑器未保存状态同时改同一个场景文件。
2. 先明确谁创建、持有和释放对象，再选 Node、Resource、RefCounted 或现有服务。需要场景生命周期才使用对应节点回调；纯规则不必依赖场景树。
3. 检查节点路径、唯一名称作用域、导出属性和信号签名。`%Name` 减少祖先路径耦合，但目标节点重命名仍要改引用。必需节点缺失应暴露配置错误，不能用空值分支吞掉错误。
4. 对 `await` 后继续使用的对象检查生命周期和取消/过期请求条件。连接信号的职责应明确；用连接计数掩盖重复初始化通常不是修复。
5. 保存场景时检查 `PackedScene.pack()` 和 `ResourceSaver.save()` 的结果；重载验证预期节点、类型和关键属性。节点数相同不证明保存正确。

## 验证与交付
运行受影响脚本/场景的适当检查，查看实际加载错误。结构检查不证明 `_ready()`、运行交互或画面通过；涉及这些行为就补对应运行。给出改动位置、验证范围和未验证项，不展开无关架构讲解。

## 按需参考
- 生命周期、类型、资源边界：[工程检查表](references/lifecycle.md)。
- 场景生成、owner、重载验证：[场景保存检查](references/scene-roundtrip.md)。
- 来源及改写：[来源记录](references/sources.md)。
