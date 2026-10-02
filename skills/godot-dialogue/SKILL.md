---
name: godot-dialogue
description: "Use when changing dialogue graphs, conditional choices, NPC conversation state, dialogue side effects, branching or exit paths in Godot. Not for dialogue-box padding, font styling, or prose-only editing. 适用于条件选项与对话状态机。"
license: Apache-2.0
---

# Godot 对话与场景交互

## 适用边界
处理对话状态、条件选项、跳转、交互效果和可继续路径。沿用已有 Dialogue Manager、Dialogic 或自定义系统，不因技能里有示例就更换对话框架。单纯修改文案或对话框边距不需要本技能。

## 先读什么
定位当前对话数据、运行器、条件读取、效果提交、UI 绑定和本地化 ID。确认对话由哪个场景/人物触发，以及允许取消、结束或返回的规则。

## 工作方法
1. 以稳定的行/节点/选项 ID 表达身份；文本只负责展示，数组下标不作为持久身份。检查跳转目标与可达性，但不要误把静态图验证当成运行时条件验证。
2. 选项过滤后显式处理零可用选项：按既定设计跳转到 fallback、返回上级或可结束状态。不能隐藏所有按钮，却因为原始列表非空而拒绝继续。
3. 选择提交时重新校验条件。UI 展示后世界状态可能已改变；失败要刷新选项或解释原因，不可部分扣款/发奖励。
4. 将“展示/进入一行”和“提交有副作用的动作”区分开。重复点击、跳过打字、关闭重开或读档不能重复执行一次性任务奖励。需要时用动作 ID/完成状态判重。
5. 为自动跳转和无交互循环设置明确终止条件或步数预算；合法等待玩家输入的循环不是错误。条件表达式使用项目可控解析方式，不对数据执行任意代码。

## 验证与交付
按变更选检查：选项过滤或跳转改动验证正常、零选项和退路；选择提交改动验证显示后条件变化；副作用改动验证重复提交，触及持久状态才加入相关读档。入口、绑定或焦点改动走真实交谈入口。其他内部修改运行受影响逻辑，不强制重复完整旅程；运行器单测不能证明玩家点得到 NPC。

## 按需参考
- 状态转移与边界案例：[对话契约](references/dialogue-contract.md)。
- 图与条件数据验证：[数据检查](references/content-validation.md)。
- 来源及改写：[来源记录](references/sources.md)。
