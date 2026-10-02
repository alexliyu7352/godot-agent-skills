# Godot Agent Skills — 精简整合版

面向**已经在开发中的 Godot 4 游戏**，尤其是长期策略／角色扮演项目。它是七个按任务使用的领域技能，不是游戏内 AI，也不是新的项目总控或游戏生成器。

**安装包版本：0.1.0-preview.2。** 完整包已在 `main`；本轮只增加验证材料和准备工具，七个技能与 `pack.json` 的安装内容未改变。源码、参考实现、工具、来源与许可证均保存在 GitHub，不依赖会话下载。

**验证进展：**离线回归增加到 60 项；Godot 4.6 的 15 个原始合同步骤继续通过；新增真实 X11/OpenGL 中文界面渲染，三个窗口各 34 条断言通过，并抓住两种故意 UI 错误。[运行 37068020868](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37068020868)还校准了五组已知坏/已知好候选的独立评分器。后续提交以 [main CI](https://github.com/alexliyu7352/godot-agent-skills/actions/workflows/validate.yml?query=branch%3Amain) 为准。

[15 张原始截图与摘要](docs/evidence/visual-37067190631/)已纳入 Git；[实际图像查看记录](docs/VISUAL_REVIEW.md)明确区分已看过的图片、合成事件和真实游戏。真实 Codex/Claude 自动触发及 38 个 Agent 案例仍为 `NOT_RUN`；CI 和评分器通过不能证明 Agent 提效或保证游戏质量。

## 七个入口

| 技能 | 内容 |
|---|---|
| `godot-code-scenes` | 脚本/场景集成、生命周期、owner、打包和重载 |
| `godot-data-state` | 数据定义、离屏状态、稳定 ID、跨系统结算与时间 |
| `godot-ui` | Control/Theme、中文布局、焦点与真实输入 |
| `godot-dialogue` | 条件分支、零选项、重入/重复效果、可退出路径 |
| `godot-save-load` | 一致快照、迁移、未来版本拒绝、暂存恢复、I/O 失败 |
| `godot-debugging` | 错误复现、运行树/信号、异步生命周期、性能定位 |
| `godot-verification` | 按风险选择证据、假通过诊断、实际交互/视觉边界 |

每个入口只链接自己的按需参考。没有第八个总路由器，没有 hooks、预授权工具、自动安装依赖、固定模型/服务、强制子 Agent 或全任务 TDD。不会改变已有语言/架构/项目流程，不包含原上游的发布安装器。

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
# 阅读来源变化后，更新未被本地修改的受管文件。
python3 tools/install.py --host codex --project /absolute/path/to/game --update

# 仅移除本包收据拥有、且未经修改的七个技能。
python3 tools/install.py --host codex --project /absolute/path/to/game --uninstall
```

## 验证工具

优先使用工程现有运行器。附带 `run_check.py` 只包装一条明确命令，保存新 stdout/stderr、退出码、超时、常见错误摘要和可选完成标记；不使用网络或 LLM。详细限制见 [命令检查](skills/godot-verification/references/commands.md)。

运行本包离线测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/validate.py
```

[38 个真实 Agent 评估案例](evals/README.md) 已定义，但没有冒充实际运行结果。

## 小型引擎验收与审查修订

[修订清单](docs/REVIEW_FIXES.md) 对应 R1–R8。五个按需 GDScript 示例位于对应技能 references 中，不添加新 Skill 入口。

```bash
python3 tools/check_fixtures.py --godot /absolute/path/to/godot --out /tmp/fresh-fixture-evidence
```

运行器在独立副本验证场景磁盘重载、资源隔离、UI 布局与合成事件、对话退路、未来存档拒绝；同时注入五种缺陷验证测试能发现错误。不是实际 Agent 使用收益测试。准备方法与独立验收边界见 [fixture 说明](evals/fixtures/README.md)。

## 真实渲染与有/无技能包对照

渲染命令、CI 依赖与输入范围见 [视觉夹具说明](evals/visual/README.md)。代码通过真实渲染获取 PNG，不以 headless 退出成功代替看图。

[宿主对照说明](evals/HOST_TRIALS.md)提供相同初始任务的对照/安装两组、任务文本、起始提交和独立评分器。准备工具不调用模型，不替用户登录，不改变模型和推理设置。没有真实宿主轨迹时保持 `NOT_RUN`。

## 合并范围与维护

以 awesome-gamedev 的领域知识为主要基础，提取 GodotPrompter 的专项调试方法和 Godogen 的场景保存/验证实践，重新编排与纠错。不是原文件机械拼接，也不是把三个原库当成运行时依赖。

- [设计与边界](docs/DESIGN.md)
- [逐项取舍与已知局限](docs/CURATION.md)
- [来源锁定](sources.lock.json)、[许可说明](THIRD_PARTY_NOTICES.md)
- [更新维护](docs/MAINTENANCE.md)
- [GitHub 发布/恢复说明](docs/PUBLISH.md)

新整合部分采用 Apache-2.0，保留相关上游 MIT/Apache 许可与 NOTICE。每个独立可安装技能附带完整法律文本，Agent 无需为普通开发任务读取它们。
