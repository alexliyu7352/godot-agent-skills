# 小型 Godot 工程验收夹具

这些夹具检验真实引擎行为，不是模拟 Agent，也不是完整游戏。
`tools/check_fixtures.py` 把五个按需实现复制到独立工程，先运行正确版本，再逐个注入五种可复现故障；只有真实断言失败且测试正常结束才认定故障被捕获，解析失败不能冒充回归有效。

```bash
python3 tools/check_fixtures.py --godot /absolute/path/to/godot --out /tmp/fresh-fixture-evidence
python3 tools/check_fixtures.py --prepare-only --variant dialogue-empty --out /tmp/new-agent-workspace
```

运行器使用标准 Godot 4.x GDScript，不修改引擎。支持版本以实际 CI 日志为准。构建与重载是两个独立进程；所有磁盘写入只发生在导出的 fixture 内。

| 变体 | 给 Agent 的任务，不提示技能名称 | 独立验收 |
|---|---|---|
| scene-owner | 程序保存后交谈按钮丢失，修复后保证属性和连接保留 | 磁盘重载后的路径、导出 Node 引用、持久信号 |
| resource-alias | 两名人物独立计数互相污染，但外观定义允许共享 | 嵌套字典/数组分离，外观仍共享 |
| ui-shared-theme | 只把一个面板边框改为 4，不影响共享 Theme 的另一面板 | 原 StyleBox 不变、局部 override 生效 |
| dialogue-empty | 条件均不满足时玩家没有可选项，需要可返回 | 过滤后存在返回路由，过期选择被拒绝 |
| future-save | 新版本存档被旧程序接受并改变当前世界 | 明确拒绝，原文件和旧状态不变 |

宿主对照时使用相同变体、模型/推理设置和初始工程；有包/无包各自新上下文，记录真正的技能加载、完整改动和命令轨迹。独立验收从可信的仓库测试副本执行；不接受 Agent 修改 checks.gd、删除断言来满足验收。

局部间距额外任务：在 baseline 上把 MarginContainer 的边距改到明确的新值，验收只更新对应期望并检查相关控件。不要用整套夹具强迫普通游戏局部任务跑全矩阵；本工具的全矩阵是技能包维护回归。

`Viewport.notify_mouse_entered()` 后通过 `Viewport.push_input()` 注入位置/按下/释放，测试引擎 GUI 分发；直接 pressed.emit 只用于序列化连接测试。headless 没有实际画面审查，也不是 OS 设备输入。仅靠这里通过，不能更新 Agent 选择/任务收益/视觉结果为 PASS。

首次 CI 曾因 headless 中模拟点击未到达按钮而失败；保留完整失败证据，改为明确的 viewport 坐标与鼠标进入通知后重测。没有把此断言改成调用处理函数。官方接口说明：https://docs.godotengine.org/en/4.6/classes/class_viewport.html#class-viewport-method-push-input
