# 参考复用试验：准备工作与实际执行严格分开

当前没有真实宿主结果；`status.json` 保持 NOT_RUN。下列五个任务用于**参考发现与复用**，不是对陌生游戏工程的泛化能力或净提效评测。

## 先明确答案来源
准备器从本包的五份正确 `.gd` 示例复制工程，再定点制造故障；安装技能的一组仍可读取同名、完整的正确示例。把 grader 放在工作区之外并没有隐藏这些合法参考答案。找到并复用参考是有价值的行为，但这里的通过率/耗时不能单独证明未知工程开发能力提高。

因此，既有 CI 的已知坏/已知好校准只证明 helper 断言有效；真实 Agent 在这五个任务中的记录也只能标为“参考复用”。`task_contract_passed` 是指定 helper 合同通过，不是游戏质量或泛化收益通过。旧记录同样按此范围解读，不改写旧日志。

后续要检验实际收益，应另选少量独立的已有工程任务，其结构和实现不由本包正确示例直接变异而来，安装包中也不包含整份答案；先固定验收，再交错执行有/无包对照。本轮不新造任务平台、不新增游戏场景。

## 准备一份参考复用任务
在技能包 checkout 外选择新目录。五种变体沿用已通过引擎反例验证的 scene-owner、resource-alias、ui-shared-theme、dialogue-empty、future-save。

```bash
python3 tools/prepare_agent_trial.py prepare --variant dialogue-empty --host codex --out /tmp/trial-control
python3 tools/prepare_agent_trial.py prepare --variant dialogue-empty --host codex --with-skills --out /tmp/trial-treatment
```

每份输出有 `project/`（Agent 工作目录）、`task.txt`（不含技能名的任务）、`grader/`（不交给 Agent 的验收材料）和 `trial.json`。两组的项目源码哈希、任务文本哈希必须相同；技能目录是唯一有意差异。工具为每个 project 建立起始 Git 提交，便于取得改动 diff。

检查器和故障说明不进入 project；同一文件系统的兄弟目录不构成安全隔离。操作员应限定工具授权目录或使用现有隔离容器，避免读取另一组项目和 grader。安装包内的参考保持可读；不要假称已经做到答案隔离。

## 运行前检查
固定并记录宿主版本、模型、推理设置、可发现技能来源和权限；有/无两组使用同一配置。核查全局/插件/父目录的旧库；每例使用新会话，不 resume 前一例。

先做一种变体的小规模 smoke，再按 evals/README.md 交错重复。不要为了评测打开全盘或无审批权限。设备离线或未登录时保留 NOT_RUN，不创建假轨迹。

在已验证登录和权限的 Codex 中，可使用非交互形式：

```bash
trial=/tmp/trial-treatment
codex exec --json --sandbox workspace-write -C "$trial/project" - \
  < "$trial/task.txt" > "$trial/events.jsonl" 2> "$trial/agent-stderr.log"
git -C "$trial/project" diff HEAD > "$trial/changes.diff"
git -C "$trial/project" status --porcelain > "$trial/worktree-status.txt"
```

新文件未必出现在 git diff 中，同时保存状态和项目源码快照。检查真实退出状态与事件内容；自行打印技能名称不是调用证据，正则命中 SKILL.md 不是质量评测。Claude 按其当前版本支持的非交互与事件输出方式单独验证。本工具不登录账号、不选模型。

## 固定验收

```bash
python3 tools/prepare_agent_trial.py grade --trial /tmp/trial-treatment \
  --godot /absolute/path/to/godot --out /tmp/new-grade-evidence
```

grader 复制候选到新目录，用受信任 checkout 的原断言覆盖检查器，不改变候选 examples。版本哈希不一致直接拒绝。未修复项目应失败；通过后还要审查轨迹、范围、人工介入和成本。技能包本身的正确示例属于试验输入，不是未知工程成功证据。

`cases.jsonl` 当前定义 46 个选择/行为案例；五个复用工程不是全部案例的可运行版本。技能选择、参考复用、独立工程收益、视觉评价分开记录。

方法参考：[技能评估](https://developers.openai.com/blog/eval-skills)、[非交互执行](https://developers.openai.com/codex/noninteractive/)。这些是方法/命令说明，不是本仓库已经执行过宿主测试的证明。
