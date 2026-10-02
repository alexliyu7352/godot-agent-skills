# 安装、旧库迁移与恢复

## 安装前
保留现有项目备份/版本记录。在游戏工程外克隆或解压此包，执行 validator 和 dry-run。目标必须有 project.godot；安装器拒绝目标路径中已有符号链接，需使用实际物理路径，不进行全局安装。

按照宿主检查全部可发现来源：项目、父目录、个人、插件和管理员/系统。仅移除或禁用已经决定淘汰的 Godot 包；保留其他用途技能。安装器不会自动修改它们，也不能穷尽扫描宿主内部插件目录。

若保留原库作研究参考，放在未加入该宿主技能搜索范围的独立整理目录，不放在技能根目录的 backup/unused 子目录。迁移后重启或刷新宿主，并核对实际技能目录/菜单，避免旧上下文继续带入原入口。

## 宿主映射
Codex 的项目路径为 `.agents/skills`；Claude Code 为 `.claude/skills`。本包只复制共同标准文件，不生成 hooks、agents、settings 或模型覆盖。默认允许七个领域技能按窄描述隐式选择。

需要某项仅手动触发时，属于用户的宿主策略，而不是本包偷偷改变默认值：
- Claude Code 支持 `disable-model-invocation: true`；`user-invocable: false` 是禁用户手动调用，不是禁模型自动调用。
- Codex 支持技能 `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false`；`[[skills.config]] enabled=false` 则是禁用技能。

直接改安装后的文件/添加配置会被收据检测为本地修改；请保留你的补丁，审查后在源版本进行对应更新，或先按下述方式备份并解除受管安装。不要期待 --update 静默覆盖这些设置。本包 validator 有意只接受本版三个 scalar 元数据字段；要维护自有宿主策略版，需同时审查验证规则与新清单，而非跳过验证。

## 更新
比较 sources.lock 和 CURATION 的实际变化，运行本包测试，更新 pack 清单，然后 --update。更新只接受旧收据记录的内容仍全部未改；任一文件缺失、编辑或新加都拒绝。未知同名技能永远不是 --update 的接管对象。

本版没有 force 选项。发现冲突后备份整个冲突技能到搜索范围外，核对变更，再由用户选择移走旧版本。不要删除整套 .agents/.claude 目录。其他技能和根指令文件不属于本包。

## 卸载和中断
--uninstall 只删除收据拥有且未修改的七个目录与收据，保留宿主目录和其他技能。收据丢失时不猜测归属。

安装/更新时使用宿主目录里的 `.godot-agent-skills.lock` 合作锁；正常失败尝试回滚。kill -9/断电可能留下锁和 `.godot-agent-skills-stage-*`，不要直接重跑强制覆盖。先确认进程停止，保存 staging、原目录和收据，比较内容/哈希后恢复一致状态；确认无未恢复资料才移除锁。它不是跨文件系统崩溃事务或敌对并发防护。

官方依据（本轮查阅 2026-10-02）：
- https://agentskills.io/specification
- https://developers.openai.com/codex/skills/
- https://code.claude.com/docs/en/skills
