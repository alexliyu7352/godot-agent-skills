# Godot Agent Skills — 精简整合版

面向**已经在开发中的 Godot 4 游戏**，尤其是长期策略／角色扮演项目。它是七个按任务使用的领域技能，不是游戏内 AI，也不是新的项目总控或游戏生成器。

**安装包版本：0.1.0-preview.5。** 本版定点修复 preview.4 review 的五项问题：参考层验证范围、对话返回策略、参考复用评测定位、缓存说明与结果状态检查。保留现有组件复用、美术和素材指导，不增加入口、游戏内容或评测平台。详见 [审查修订](docs/REVIEW_PREVIEW4_FIXES.md)；上一版的内容依据见 [内容审查](docs/CONTENT_AUDIT.md)。

此前的 15 张合成界面截图仅用于布局和输入故障检查，**不是《汉末行记》的美术目标或界面成品**。不以无溢出、能点击或 CI 通过代替美术评价。[官署视觉目标](examples/han-office/VISUAL_TARGET.md)只保留为历史参考，不再作为本包后续制作或发布前置任务。

真实 Codex/Claude 自动触发及 [46 个 Agent 案例](evals/README.md)仍为 `NOT_RUN`。最新回归以 [main CI](https://github.com/alexliyu7352/godot-agent-skills/actions/workflows/validate.yml?query=branch%3Amain) 和对应提交日志为准；旧版 [验证报告](docs/TEST_REPORT.md)与[截图查看记录](docs/VISUAL_REVIEW.md)保留历史范围，不改写成真实 Agent 或美术已经通过。

## 七个入口

| 技能 | 内容 |
|---|---|
| `godot-code-scenes` | 已有组件/插件复用、初始化、场景集成、owner、分层场所与热点坐标 |
| `godot-data-state` | 数据定义、离屏状态、稳定 ID、跨系统结算与时间 |
| `godot-ui` | 游戏美术、素材家族与导入、场景与 HUD、Control/Theme、中文布局与输入 |
| `godot-dialogue` | 现有运行器适配、选择身份、零选项、重入/重复效果与退出 |
| `godot-save-load` | 一致快照、迁移、未来版本拒绝、暂存恢复、I/O 失败 |
| `godot-debugging` | 错误复现、运行树/信号、分段性能测量与线程加载诊断 |
| `godot-verification` | 按风险选择证据、假通过诊断、明确美术审查与实际交互 |

每个入口只链接自己的按需参考。没有第八个总路由器，没有 hooks、预授权工具、自动安装依赖、固定模型/服务、强制子 Agent 或全任务 TDD。小修改沿用已批准美术，不重新出图；也不会改变已有语言/架构/项目流程。

## 安装：只安装这一套

要求 Python 3.10+（仅标准库）与一个已有 `project.godot` 的项目。把本仓库/解压目录放在游戏项目之外，从本仓库根目录执行：

```bash
# 先验证包本身。
python3 tools/validate.py

# Codex：预览后安装到项目 .agents/skills。
python3 tools/install.py --host codex --project /absolute/path/to/game --dry-run
python3 tools/install.py --host codex --project /absolute/path/to/game

# 使用 Claude Code 时，以这个命令替代上面的 Codex 安装。
python3 tools/install.py --host claude --project /absolute/path/to/game --dry-run
python3 tools/install.py --host claude --project /absolute/path/to/game
```

不需要同时安装两个宿主版本。两者是同一份源内容的不同项目目标目录。安装后重新启动/刷新宿主并查看实际可用技能清单。旧的全局、插件、父目录技能不会因本次安装自动消失，先按 [安装与迁移](docs/INSTALL.md) 审查旧入口，否则仍可能误触发。

安装前检查全部目标冲突。未经本包收据管理的同名目录，即使看起来相同也拒绝覆盖；已安装内容有本地改动或额外文件时，更新/卸载同样拒绝。不会覆盖 `AGENTS.md`、`CLAUDE.md`、`.gitignore` 或其他技能。

```bash
# 从旧版更新未经本地修改的受管文件；Claude 用户替换 host 值。
python3 tools/install.py --host codex --project /absolute/path/to/game --update --dry-run
python3 tools/install.py --host codex --project /absolute/path/to/game --update

# 仅移除本包收据拥有、且未经修改的七个技能。
python3 tools/install.py --host codex --project /absolute/path/to/game --uninstall
```

**示例调用变化：**已复制使用 `choice_routes.gd` 的项目，返回调用需补 `choose("__return__", options, eligible, can_return)` 的第四个 Callable。该回调检查项目已有会话与退出规则；普通业务选择的三参数调用不变。安装器不会修改用户游戏代码，详见 [对话契约](skills/godot-dialogue/references/dialogue-contract.md)。

## 验证工具

优先使用工程现有运行器。附带 `run_check.py` 只包装一条明确命令，保存新 stdout/stderr、退出码、超时、常见错误摘要和可选完成标记；不使用网络或 LLM。详细限制见 [命令检查](skills/godot-verification/references/commands.md)。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/validate.py
```

[46 个真实 Agent 评估案例](evals/README.md)已定义，没有冒充实际运行结果。结果状态不再被测试永久锁定，但报告执行或成绩必须关联证据；结构检查不能认证证据真实性。

## 小型引擎验收与审查修订

[早期修订清单](docs/REVIEW_FIXES.md)对应原 R1–R8；[preview.4 review 修订](docs/REVIEW_PREVIEW4_FIXES.md)对应本轮五项。五个按需 GDScript 示例位于相关技能 references 中，不增加入口。

```bash
python3 tools/check_fixtures.py --godot /absolute/path/to/godot --out /tmp/fresh-fixture-evidence
```

运行器在独立副本验证场景磁盘重载、资源隔离、UI 布局与合成事件、对话退路、未来存档拒绝，同时注入指定缺陷验证断言。不是实际 Agent 使用收益测试，边界见 [fixture 说明](evals/fixtures/README.md)。

## 渲染与参考复用试验

渲染命令、CI 依赖与输入范围见 [视觉夹具说明](evals/visual/README.md)。实际渲染 PNG 不等于美术评价；此合成夹具保留技术用途，不作为美术标杆。

[参考复用说明](evals/HOST_TRIALS.md)保留有/无包两组的相同初始任务、轨迹和固定检查器。**五个任务均由包内正确示例制造故障，实验组可直接获得完整答案，因此只测参考发现与复用，不据此推导陌生工程的净提效。**独立工程收益需另行定义没有整份答案的任务和验收；本轮不扩建平台。准备工具不调用模型、不登录账号、不更改推理设置。

## 合并范围与维护

以 awesome-gamedev 的领域知识为主要基础，提取 GodotPrompter 的专项调试方法和 Godogen 的场景保存/验证实践，重新编排与纠错。美术生产与素材导入方法仍来自锁定版本；不注册原总路由。

- [审查修订](docs/REVIEW_PREVIEW4_FIXES.md)、[内容审查](docs/CONTENT_AUDIT.md)
- [设计与边界](docs/DESIGN.md)、[取舍与局限](docs/CURATION.md)
- [来源锁定](sources.lock.json)、[许可说明](THIRD_PARTY_NOTICES.md)
- [更新维护](docs/MAINTENANCE.md)、[GitHub 发布说明](docs/PUBLISH.md)

新整合部分采用 Apache-2.0，保留相关上游 MIT/Apache 许可与 NOTICE。每个可安装技能附带完整法律文本，普通开发任务无需全部读取。
