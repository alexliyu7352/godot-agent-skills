# Godot 命令检查与包装器

## 选择真实运行器
先查项目已有测试命令，保持 GUT、GdUnit4 或自有运行器。Godot 可执行文件从项目配置/明确参数取得，别猜固定安装路径。使用绝对路径或正确的 cwd，记录 `--version`。

新检出工程可按对应版本支持的选项执行 `godot --headless --path /absolute/project --editor --import` 完成导入。导入可执行插件/工具脚本且写 `.godot`，不是只读安全扫描；请在合适的工作副本运行。

`godot --headless --path /absolute/project --check-only --script res://path/to/script.gd` 检查指定脚本及实际触达依赖，并不枚举全项目。C# 工程还需要项目相应 .NET build 流程。

`godot --headless --path /absolute/project --quit` 是有限启动冒烟。需要覆盖主循环/场景操作时运行适当帧数、测试场景或真实流程；不要把这条命令命名成“所有脚本完整测试”。

## 包装已有命令
从本技能根目录执行：

```bash
python3 scripts/run_check.py --out /tmp/godot-check-unique \
  --cwd /absolute/project --timeout 120 \
  --require-text YOUR_RUNNER_FINISHED_MARKER \
  -- /absolute/path/to/godot --headless --path /absolute/project \
  --script res://tests/your_existing_runner.gd
```

上例路径和标记是需要替换的参数，不是本包提供的游戏测试。优先使用现有运行器的完成报告。没有唯一完成标记时可不传 `--require-text`，但报告明确只证明进程/日志契约，不证明测试实际全部执行。

包装器不使用 shell，不修改命令参数，不下载依赖，不选择模型，不调用外部服务。用户显式传入 shell 或带副作用命令时依旧会执行；它不是沙箱。

## 判定范围
非零退出、超时、启动失败、匹配到常见 Godot 错误前缀或缺少指定完成标记均返回失败。错误匹配是启发式：不同测试框架的 JSON/JUnit 或自定义日志需要自己的解析，未知错误格式可能漏报；被打印的错误示例可能误报。不可为了过关删除检查，应核实后使用匹配实际运行器的验证契约。

报告 `command_passed` 不表示游戏完成或视觉通过。完整 stdout/stderr 保存在磁盘；JSON 只保留有限摘要。输出可能包含秘密或个人路径，分享前审查，不默认上传。

完成条件为直接子进程退出、stdout/stderr 都读到 EOF、退出码/日志/所需完成标记满足契约。父命令退出而继承输出的工作进程仍运行时，继续在同一个超时预算内读取；不额外固定 sleep。只有包装器主线程写日志文件，迟到进程拿不到日志文件句柄。

超时在 POSIX 终止本次进程组，再进行有限清理排空；Windows 只终止直接子进程。主动脱离进程组的进程可能无法清理；未关闭的管道会在清理预算后停止捕获，报告 `streams_complete=false`，不能成功。失败报告的日志是截止时刻已捕获内容，不宣称完整。

EOF 不能证明重定向到其他文件的后台工作已经成功。被包装运行器必须等待它自己的所有工作并汇总失败；包装器不是作业调度器。输出/错误前缀仍是启发式，不负责修改任意进程或操作系统。

官方核查：
- https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html
- https://docs.godotengine.org/en/stable/classes/class_scenetree.html
