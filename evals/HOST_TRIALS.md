# 真实宿主对照：准备工作与实际执行严格分开

当前没有真实宿主结果；`status.json` 保持 NOT_RUN。此工具解决的是“相同初始任务、技能有/无、可信验收与结果留存”，不是替代 Codex/Claude 的模拟评测器。

## 准备一份任务

在技能包 checkout 外选择新目录。五种变体沿用已通过引擎反例验证的 scene-owner、resource-alias、ui-shared-theme、dialogue-empty、future-save。

```bash
python3 tools/prepare_agent_trial.py prepare --variant dialogue-empty --host codex --out /tmp/trial-control
python3 tools/prepare_agent_trial.py prepare --variant dialogue-empty --host codex --with-skills --out /tmp/trial-treatment
```

每份输出有 `project/`（Agent 唯一工作目录）、`task.txt`（不含技能名的任务）、`grader/`（不可交给 Agent 的验收材料）和 `trial.json`。两组的项目源码哈希、任务文本哈希必须相同；技能目录是唯一有意差异。工具为每个 project 建立起始 Git 提交，便于取得改动 diff。

检查器和故障说明不会进入 project；但同一文件系统上的兄弟目录不是安全隔离。操作员应把 project 作为唯一工具授权目录，或分别挂载到隔离容器。避免 Agent 读取技能包仓库、另一组项目和 grader，从而泄露测试答案。

## 运行前检查

固定并记录宿主版本、模型、推理设置、所有可发现技能来源和权限；不让本包覆盖这些设置。有/无两组必须使用同一模型配置。特别检查全局/插件/父目录残留的原库，不然“无本包”不是干净对照。使用新会话，不 resume 前一个案例。

先做一种变体的小规模 smoke，再按 evals/README.md 的重复次数交错两组执行。除 project 工作范围外，不为了评测打开全盘或无审批权限。远程设备离线或账号未登录时保留 NOT_RUN，不创建假轨迹。

以官方支持的 Codex 非交互形式为例，在操作员已验证登录及项目写入权限后：

```bash
trial=/tmp/trial-treatment
codex exec --json --sandbox workspace-write -C "$trial/project" - \
  < "$trial/task.txt" > "$trial/events.jsonl" 2> "$trial/agent-stderr.log"
git -C "$trial/project" diff HEAD > "$trial/changes.diff"
git -C "$trial/project" status --porcelain > "$trial/worktree-status.txt"
```

新文件不一定出现在 git diff 中，需同时保存状态和项目源码快照；检查与任务相关的新文件。命令并不证明已执行；必须检查真实退出状态及事件内容。不要把自行打印技能名称算作调用，也不要只用正则统计对 SKILL.md 的引用。Claude 使用其当前版本支持的非交互与事件输出方式，在相同 project、任务和配置下单独验证；本工具不代用户登录或指定模型。

## 独立验收

```bash
python3 tools/prepare_agent_trial.py grade --trial /tmp/trial-treatment \
  --godot /absolute/path/to/godot --out /tmp/new-grade-evidence
```

grader 把候选工程复制到新目录，覆盖其中的检查器为当前受信任 checkout 的原始断言；不复制标准答案，不改变候选的 examples。版本哈希不一致直接拒绝。对未经修复的故障项目应得到失败，修复后才可以得到 `task_contract_passed`。这仍不是 Agent 总体成功：还要审查真实调用轨迹、超范围改动、测试删改、人工介入和总成本。

38 个 cases.jsonl 用于技能选择/行为规则；本轮五个工程任务只覆盖其中部分风险，不是全部 38 个案例的可运行工程。选择准确率、任务通过率、视觉审查分别记录，禁止以 fixture 通过推导模型收益。

方法依据：OpenAI [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills) 区分显式、隐式、负向控制及过程/结果证据；[非交互执行](https://developers.openai.com/codex/noninteractive/) 说明 JSON 事件输出方式。
