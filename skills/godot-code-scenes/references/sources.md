# 来源与改写

本技能是重新组织的适配内容，不是原库的完整技能或原流程。

## 锁定来源
- gamedev-skills/awesome-gamedev-agent-skills @ `d4b0e35550c55ae70bdfcab4ef5a0e94610438a9`：[skills/godot/godot-gdscript/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/godot/godot-gdscript/SKILL.md)
- gamedev-skills/awesome-gamedev-agent-skills @ `d4b0e35550c55ae70bdfcab4ef5a0e94610438a9`：[skills/godot/godot-nodes-scenes/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/godot/godot-nodes-scenes/SKILL.md)
- liangdabiao/Godogen @ `8f315780bf50eea1875e08c8b614930e9d6e8450`：[.claude/skills/godogen/scene-generation.md](https://github.com/liangdabiao/Godogen/blob/8f315780bf50eea1875e08c8b614930e9d6e8450/.claude/skills/godogen/scene-generation.md)

## 本地处理
保留类型/生命周期和场景所有权检查；改正唯一名称不是目标重命名安全；不继承强制生成场景、禁止 preload 或递归展开子场景规则。

所有入口和参考正文均经重新组织、纠错和中文改写。Python 工具为本包新实现。相关原作者许可与 NOTICE 保存在同技能目录的 `LICENSE.txt` 中；新整合部分采用 Apache-2.0。资料按任务读取，不要求加载任何上游 Skills。

记录日期：2026-10-02。上游后续修复需人工审阅后合并，不自动追随默认分支。

preview.2：补充的 .gd 示例为本包针对审查反例重新实现，遵循上列来源的一般方法与官方 API；没有恢复上游总控或原示例缺陷。实际引擎版本与测试结果见仓库 TEST_REPORT/CI，不能由此推导宿主自动触发通过。
