# 来源与改写

本技能是重新组织的适配内容，不是原库的完整技能或原流程。

## 锁定来源
- gamedev-skills/awesome-gamedev-agent-skills @ `d4b0e35550c55ae70bdfcab4ef5a0e94610438a9`：[skills/godot/godot-ui-control/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/godot/godot-ui-control/SKILL.md)

## 本地处理
保留 Container/Theme/焦点/本地化知识；补齐真实输入与视觉证据边界，限制局部修改范围。

所有入口和参考正文均经重新组织、纠错和中文改写。Python 工具为本包新实现。相关原作者许可与 NOTICE 保存在同技能目录的 `LICENSE.txt` 中；新整合部分采用 Apache-2.0。资料按任务读取，不要求加载任何上游 Skills。

记录日期：2026-10-02。上游后续修复需人工审阅后合并，不自动追随默认分支。

preview.2：补充的 .gd 示例为本包针对审查反例重新实现，遵循上列来源的一般方法与官方 API；没有恢复上游总控或原示例缺陷。实际引擎版本与测试结果见仓库 TEST_REPORT/CI，不能由此推导宿主自动触发通过。

## preview.3 美术能力补齐

- [skills/disciplines/create-game-assets/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/SKILL.md)：已阅读固定版本，保留视觉目标、家族一致性与实际呈现检查。
- [skills/disciplines/create-game-assets/references/art-direction.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/references/art-direction.md)：已阅读固定版本，保留视觉目标、家族一致性与实际呈现检查。

新增参考由本包针对 Godot 重组；场所连续性来自用户目标，不是对上游原文的逐字结论。没有导入原跨引擎总入口、外部模型脚本或字体资产。

## preview.4 内容审查补齐

- [skills/disciplines/create-game-assets/references/raster-pipeline.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/references/raster-pipeline.md)。

补回帧对齐、图集边缘、UI状态和素材上屏检查，增加 Godot 4 采样/导入的具体区分；不制作场景资产。
仍按需读取，不注册该上游入口；源码与官方文档审读不代表已完成真实宿主使用对照。
