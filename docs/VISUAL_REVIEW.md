# 已查看的渲染证据与真实 Agent 验证边界

## 固定来源

2026-10-02 对提交 `da69b3de583724aa4ccb7f8e6cfffda5bf9db54e` 的[运行 37067190631](https://github.com/alexliyu7352/godot-agent-skills/actions/runs/37067190631)返回图片进行查看。环境为 Godot `4.6.stable.official.89cea1439`、X11、OpenGL compatibility、Mesa llvmpipe（LLVM 20.1.2），字体由 CI 系统 `Noto Sans CJK SC` 提供。仓库不包含字体文件。

原 artifact ZIP SHA-256：`d8fe4fcc5226c4065f9b2ef03f090e622e700404354c4ab102aadcc86e40acfb`。

[原始 summary 和全部 15 张 PNG](evidence/visual-37067190631/)在 Git 中保留，图片字节由 summary 的 SHA-256 验证。这里不只依赖会过期的 Actions artifact。自动 summary 中 `visual_pixels_reviewed: false` 保留原值；本文件是另一次实际查看记录，不倒填自动执行结果。

## 实际查看的范围

查看方式是本会话中的图像查看工具，由作者 Agent 读取真实 PNG；不是第二名审查者，也不是已执行的 Codex/Claude 用户任务。

| 图片集合 | 实际查看 | 观察 |
|---|---|---|
| baseline-800x600 | long-text、no-choices、returned 三张 | 中文正文完整换行；没有观察到边界裁切；零可选项有返回按钮；返回后原面板关闭，交谈入口与焦点边框出现 |
| baseline-1280x720 | 同上三张 | 正文缩为三行，按钮和同级样式面板仍在视口内；状态切换对应截图一致 |
| baseline-1600x900 | 同上三张 | 正文为两行；没有观察到按钮越界或叠字；较大留白是合成夹具结果，不应视为游戏 UI 设计通过 |
| text-clipping-800x600 | long-text | 关闭换行后只留下被横向裁切的一行，确实能看到内容缺失；`text/wrapped` 断言失败 |
| pointer-blocker-800x600 | returned | 尝试返回后依然停在对话面板；与正常无选项截图外观近似，说明截图存在不能证明可点击。`input/click-delivered` 和焦点恢复断言失败 |

九张正常图片对应三次各 34 条断言，均零失败。两个故意错误变体都正常完成捕获，并由指定断言报告失败；不是把解析崩溃或没有截图算成抓住问题。其余四张故障变体图片保留，但未声称逐张查看。

## 证明与未证明

已验证：实际渲染出的合成中文控件、这段文本在三个尺寸下的布局、局部 Theme 示例、通过 Viewport 分发的合成点击、返回与重新进入、两类指定反例检测。

未验证：用户真实游戏、人物立绘和地图、所有中文字符和语言、操作系统鼠标硬件路径、真实 GPU 性能、审美定稿，以及真正的编码 Agent 是否正确自动选择技能或降低返工。

[任务对照准备工具](../evals/HOST_TRIALS.md)建立相同故障工程和任务文本的有/无技能包两组，并把可信检查器留在 Agent 工作树之外。仓库执行的已知坏/已知好候选测试只是校准评分器，不是 AI 修复结果。

## 当前宿主阻塞

本次检查时，授权设备 `alex-MS-7C37` 的 Desktop Commander Remote 离线；执行环境中没有已安装且认证的 Codex/Claude Code。38 个 Agent 案例继续是 `NOT_RUN`，不手动改为通过。

后续只需要让已有授权设备在线，并提供其本地已登录的开发 Agent；不应在聊天、仓库或 CI 日志中提供 API 密钥。实际测试固定用户选择的模型及推理设置、使用新会话和限定工程目录，并记录技能调用、修改差异、最终验收与耗时。
