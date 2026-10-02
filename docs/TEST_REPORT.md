# 验证报告 — 0.1.0-preview.2

## 新增：完整版本的 GitHub CI（2026-10-02）

完整恢复提交 `0804e625518516a1436c62d36654823b5054af31` 已保存并推进 main，目录树 `36a82209ed451779ea4857f18f369f8319ed7ffb` 与 87 文件恢复包一致。
[完整版本运行 37064506770](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37064506770) 的三个作业全部成功，已读取实际日志：

| 作业 | 结果 |
|---|---|
| Python 3.11.16 | 静态校验通过；52 项测试通过，5.140 秒 |
| Python 3.13.15 | 静态校验通过；52 项测试通过，5.592 秒 |
| Godot 4.6 | 正确基线与五个故障变体共 15 步符合预期；证据 artifact 11251811790 |

这次运行针对完整版本，不再把早期测试分支的 41 项当成完整 52 项。CI 保留 Node.js action 运行时弃用警告；该警告没有导致作业失败，也没有被隐藏。后续文档提交的状态以 [main CI](https://github.com/alexliyu7352/godot-agent-skills/actions/workflows/validate.yml?query=branch%3Amain) 为准。

下面的本地测试、初次引擎验证及对应 JSON / 文本日志是先前实测快照，保留原时间、环境与范围，不改写成新一次运行。真实 Agent / 视觉状态不因这次 CI 变成通过。

## 原始实测：Python 工具与分发回归

Linux / 系统 Python 3.13.5，非 root（UID 1000），命令 `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s tests -v`。
**52 项测试通过，0 失败，退出码 0**。完整输出见 [日志](tests-unittest.txt) 和 [环境记录](test-environment.json)。
`python3 tools/validate.py` 通过，结果见 [静态报告](validation-static.json)。

原始 41 项保留，新增 11 项方法（内部包含多个故障子案例）：真实 Git `core.autocrlf=true` 克隆、提交后 install/update/uninstall 清理失败、回滚后的清理失败、正常父退出但仍有输出写入者、未关闭/逃逸写入者超时、负例/来源校验、fixture 准备边界及元数据静态防退化。
这些测试不以字符串匹配结果冒充真实模型的触发行为。

额外运行说明：托管 Python 工具的 `/opt/pyvenv` 非 root 环境，在解释器启动时自动预热表格运行时并报 `hydrateCrdtFromProto` / daemon 错误，导致 8 个检查受到启动超时或附加输出影响。该次失败完整保存在交付证据包 `tool-runtime-startup-failure.txt`，没有冒充通过。随后使用不带该预热钩子的系统解释器，在同一份源码、同一非 root 用户下重跑完整 52 项，全部通过；没有修改测试断言或延长产品超时。另有 root 环境 52 项通过的完整日志。

## 原审查反例复测

原复现脚本未改判定，六个反例在旧版失败后，于修订版 **6/6 通过**。见 [原探针输出](review-probes-after.txt) 和 [实际观察值](review-probe-observations.json)。这六项不是把同一测试换名称计入 52 项，而是独立复核。

## 原始实测：独立测试分支的 Godot 工程验证

已加入五份可执行参考、独立工程和故障注入。GitHub CI 使用官方 Godot 4.6-stable；这不会改变使用者游戏的引擎版本。
**已实际运行通过**：官方 `4.6.stable.official.89cea1439`，Linux GitHub Actions，运行 [37060512022](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37060512022)，测试分支提交 `1af8d6bd3f9bffdf0d66cf9589eee6d4ae812002`。

共 **15 个进程检查步骤通过**（含导入），正确基线的 build/reload/logic 分别执行 **7 / 15 / 16 条断言**且失败数为零；五种定点缺陷各自被期望断言抓住。首轮运行 37060055103 的 GUI 注入失败记录保留，随后补全 viewport 输入注入而没有删除断言或直接调用按钮回调。

这是独立测试分支，不是完整 preview.2 的远端发布。已下载 CI artifact，核对五个参考实现及三个 fixture 文件与完整本地候选逐字节一致，并校验所有日志的大小与 SHA-256。记录见 [引擎摘要](engine-summary.json)、[来源和字节比对](engine-evidence.json)。同一分支两个 Python 作业仍运行旧 41 项测试并通过；本地完整修订的 52 项结果不能当作远端 52 项。

GUI 输入由 `Viewport.push_input()` 经过 Control 分发，包含 hover、focus、click 断言。没有操作系统窗口输入或图像判断，因此不称为完整视觉/玩家体验验收。

基线覆盖磁盘保存/跨进程重载的导出引用和持久信号、嵌套运行数据隔离、局部 Theme 与 Container 布局、GUI 合成鼠标事件、零选项退路、未来版本存档拒绝及不修改原件。
五种变异必须被对应断言抓住；仅语法错误、超时或任意非零码不算抓住目标缺陷。

## 明确未执行

| 范围 | 状态 |
|---|---|
| Codex / Claude Code 自动触发、参考读取、任务收益 | NOT_RUN：没有已认证的可用运行器，远程设备离线 |
| 38 个真实 Agent 案例 | 已定义，NOT_RUN；有/无本包对照尚无轨迹 |
| 用户游戏集成 | NOT_RUN；没有修改或运行用户游戏 |
| 真实渲染截图、动画、OS 设备输入和体验评估 | NOT_RUN；headless GUI 分发不是视觉验收 |
| Windows/macOS 实机 | NOT_RUN；Git 换行在 Linux 真实克隆中验证 |

## 边界

命令包装器不是沙箱；同时等待直接进程退出及双输出 EOF，不能证明主动重定向/脱离的工作完成。超时后的清理/排空有有限宽限，未完整捕获不能通过。
安装器保留常规异常回滚，不承诺断电或恶意并发环境下原子事务。成功但清理待处理明确返回 `committed_cleanup_pending`。
本版仍为 preview，不宣称零误触发、提升效率比例或保证游戏质量。逐项修订见 [审查修复](REVIEW_FIXES.md)。

## 发布状态

此前校验器写入受阻、仅有局部测试分支的状态已解除。完整恢复提交与完整 CI 见本报告开头，[发布说明](PUBLISH.md) 保留失败及恢复经过。下载包不再是唯一保存位置；原独立测试分支仍不是完整安装入口。
