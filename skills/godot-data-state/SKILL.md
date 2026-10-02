---
name: godot-data-state
description: "Use when defining Godot game data, stable entity IDs, off-screen simulation, time progression, or transactions spanning quests, inventory, currency and relationships. Not for cosmetic UI edits or standalone scene layout. 适用于世界状态与跨系统一致性。"
license: Apache-2.0
---

# Godot 数据与世界状态

## 适用边界
处理数据定义、权威运行状态、离屏模拟和跨系统结算。先沿用项目的数据契约与时间模型；没有必要时不引入 ECS、事件溯源、全局总线或新的框架。

## 先读什么
定位本次改动涉及的数据定义、状态所有者、读取方和写入方。查询项目对实体 ID、时间单位、随机性、任务结算的已有约定。规则尚未确定时指出需要决策的具体语义，不替用户扩展玩法。

## 工作方法
1. 区分静态定义、可变实例状态、派生显示数据。共享 Resource 的内存修改可能影响其他引用，但并不自动写盘；复制边界以实际版本的 API 和数据结构为准。
2. 用稳定实体/定义 ID 连接持久状态，不将场景路径、节点地址或列表位置当作长期身份。世界状态的生命期不等于当前场所节点的生命期。
3. 对跨系统动作列出前置条件、变更集合、提交时刻、失败结果和重试语义。先校验全部条件，再一次提交应共同成功的变更；完成后再通知 UI。
4. 时间推进采用项目定义的离散步进或事件调度，说明顺序和结算边界。显示帧数不应偷偷改变离屏世界规则。性能改造以实际采样为依据。
5. 需要确定性复现时记录输入、随机种子/状态和事件顺序；不能假定不同引擎版本的随机实现或浮点运行会自动保持一致。

## 验证与交付
检查重复输入、取消、条件变化、重新进入场景，以及离屏实体仍参与规则计算。交易示例应同时核对玩家钱、物品和商人库存，不能只看其中一项。只针对本次修改补关联验证，不无差别重写全部系统。

## 按需参考
- 数据分层与依赖：[状态所有权](references/state-ownership.md)。
- 多系统动作与时间推进：[结算契约](references/transactions-time.md)。
- 来源及改写：[来源记录](references/sources.md)。
