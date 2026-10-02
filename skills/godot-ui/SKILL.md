---
name: godot-ui
description: "Use when changing Godot Control layouts, Theme, containers, localization display, focus, mouse/keyboard/gamepad UI input, or checking actual interface appearance. Not for dialogue graph rules, save formats, or backend code. 适用于界面、中文排版与输入焦点。"
license: Apache-2.0
---

# Godot 界面与输入

## 适用边界
处理 Control、布局、Theme、文本、焦点和实际界面操作。调整一个控件时保持局部范围，不自动加载存档、对话逻辑或完整工程规划。

## 先读什么
查看实际场景层级、父 Container、Theme 来源、布局/拉伸设置、字体和输入处理。以游戏已经批准的交互设计为准，不能把场景中的人物交互改成一个更省事的全局功能按钮。

## 工作方法
1. 先判断尺寸由 Container、anchors/offsets、最小尺寸还是脚本决定，再改正确的一层。Container 管理的子节点不要靠每帧强制位置与布局竞争。
2. 优先使用现有 Theme/组件；局部改动用适当的局部覆盖，避免无关界面随全局样式改变。不要创建重复功能入口填充画面。
3. 检查中文长文本、字体回退、换行、最小尺寸、不同窗口比例和 UI 缩放。不要只用英文短占位符验证真实内容。
4. 明确鼠标事件穿透/阻挡与键盘、手柄焦点路径。弹窗打开后焦点应进入有效控件，关闭后按项目交互约定恢复；隐藏或禁用的控件不应留下不可达路径。
5. 输入测试使用与实际入口对应的事件。`Input.action_press()` 改变动作状态，不等同于完整 GUI 事件分发或真实点击；逻辑函数直接调用只能证明逻辑层。

## 验证与交付
可见改动在实际渲染路径检查；记录相关窗口尺寸、语言、入口与状态。截图必须来自本次目标场景并实际查看。无图形/输入能力时明确视觉或交互未验证，不能拿 headless 启动替代。

## 按需参考
- 布局、Theme 和中文显示：[布局检查](references/layout-localization.md)。
- 焦点、真实输入与视觉证据：[交互检查](references/input-visual.md)。
- 来源及改写：[来源记录](references/sources.md)。
