# Godot review engine probe — NOT a complete skill-pack release

本分支仅用于独立运行审查修订中的 Godot 示例和故障注入。不要把它安装到游戏项目，也不要合入 main。

完整 0.1.0-preview.2 修订已在本地完成，但 GitHub 工具在上传 tools/validate.py 时被拦截；本分支没有绕过该写入，也没有包含该文件的修订。main 保持不变。

这里保留原有 Python/分发测试，并增加固定官方 Godot 4.6 的 godot-contracts 作业。五个新参考示例、fixtures、引擎检查器和命令捕获脚本与本地候选内容相同。Python 校验器及多数技能文档仍是旧版，不能据此称 R1–R8 全部发布。

实际引擎结果以本分支 Actions 的 godot-contracts 日志和 godot-contract-evidence artifact 为准。该作业不运行收费模型，不代表 Codex/Claude 自动触发或视觉像素验收。历史 docs/TEST_REPORT.md 不是本次测试结果。
