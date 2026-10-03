# 来源与改写

本技能是重新组织的适配内容，不是原库的完整技能或原流程。

## 锁定来源
- jame581/GodotPrompter @ `3e8d0f005f9604e1dbdad3de693e39555384c5af`：[skills/godot-debugging/SKILL.md](https://github.com/jame581/GodotPrompter/blob/3e8d0f005f9604e1dbdad3de693e39555384c5af/skills/godot-debugging/SKILL.md)

## 本地处理
保留远程场景树、信号诊断、Profiler 与复现方法；删除强制跨技能流程，不以 has_method 或空值返回掩盖必需接口错误。

所有入口和参考正文均经重新组织、纠错和中文改写。Python 工具为本包新实现。相关原作者许可与 NOTICE 保存在同技能目录的 `LICENSE.txt` 中；新整合部分采用 Apache-2.0。资料按任务读取，不要求加载任何上游 Skills。

记录日期：2026-10-02。上游后续修复需人工审阅后合并，不自动追随默认分支。

## preview.4 内容审查补齐

- [skills/disciplines/performance-optimization/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/performance-optimization/SKILL.md)。

补回瓶颈分型、测量步骤与同条件比较；不采用无条件对象池，后台资源加载按官方 API 说明。
仍按需读取，不注册该上游入口；源码与官方文档审读不代表已完成真实宿主使用对照。
