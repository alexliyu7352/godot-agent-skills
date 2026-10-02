# 发布状态与恢复

## 当前状态：完整 preview.2 已保存到 GitHub

2026-10-02，完整版本已正常写入 `alexliyu7352/godot-agent-skills`，并在完整分支 CI 通过后，以非强制快进方式推进 `main`。不再只保存在会话 ZIP / bundle 中；未改动其他仓库或用户游戏。

- 完整恢复提交：[0804e625518516a1436c62d36654823b5054af31](https://github.com/alexliyu7352/godot-agent-skills/commit/0804e625518516a1436c62d36654823b5054af31)。
- 完整目录树：`36a82209ed451779ea4857f18f369f8319ed7ffb`，87 个文件，与原始 preview.2 恢复包一致。
- 完整版本验证：[37064506770](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37064506770)，Python 3.11 与 3.13 各 52 项通过，Godot 合同/故障检测 15 步符合预期。
- 发布说明修订仅更新文档，后续结果见 [main CI](https://github.com/alexliyu7352/godot-agent-skills/actions/workflows/validate.yml?query=branch%3Amain)。

## 获取与更新

```bash
git clone https://github.com/alexliyu7352/godot-agent-skills.git
cd godot-agent-skills
python3 tools/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

已有工作副本先检查未提交修改，再使用 `git pull --ff-only`；不要用强制重置覆盖本地内容。具体项目安装与受管更新见 [安装说明](INSTALL.md)。

## 保留的发布历史

preview.1 基线为 `c3b29e54abe930fd10abd8d15389e4b58d5e6a1e`。首次发布 preview.2 时，GitHub 工具写入校验器受阻，所以只创建了明确标记的 `test/review-godot-contracts` 分支；该历史分支并非完整产品版本。

首次引擎运行 [37060055103](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37060055103) 因鼠标事件未到达按钮而失败，之后通过 Viewport 事件注入修正，在 [37060512022](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37060512022) 通过。没有删除断言、跳过失败测试或抹除历史红灯。

本次在用户继续要求发布后，正常的校验器写入成功。随后补齐所有文件、核对目录树、运行完整版本 CI 并推进 main；原工具阻塞已经解除，不需要重新授权。

## 本地恢复包仍可用于灾备

原 bundle 提交 `e8d8bfb04982b869bb943e94737dd950f17c46dc` 与 GitHub 恢复提交的目录树相同，但提交历史不同。它只是原始快照备份；之后发布说明等变更以 GitHub 为准。不要为匹配本地 bundle 的提交 ID 强推覆盖远端。

所有发布文件为技能、工具、测试、来源与非敏感证据；未上传账户凭据或游戏源码。真实宿主触发/视觉验证仍为 NOT_RUN，详见 [验证报告](TEST_REPORT.md)。
