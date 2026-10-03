---
name: godot-ui
description: "Use when designing or restyling a Godot game's visual identity, HUD, dialogue presentation, portraits, backgrounds or cohesive 2D art assets; or changing Control layouts, Theme, localization and UI input. Not for dialogue graph rules, save formats or unrelated web design. 适用于游戏美术、场景界面表现与控件工程。"
license: Apache-2.0
---

# Godot 游戏表现与界面

## 适用边界
处理游戏视觉表达与 Control 工程，二者不互相代替。局部间距、颜色或焦点修复沿用已批准方向；新场景、新素材家族或明确重设计才使用美术生产参考。不把任何游戏默认改成历史绘景或固定镜头。

## 先读什么
读取项目已批准的实机画面、视觉目标、素材、镜头与交互约定；实际查看相关图像，不用读过文字冒充看过画面。复用已有上下文；确认目标显示尺寸、输入方式、引擎版本。缺少参考时明确缺口，用户已委托选择则提出并记录候选，不假定已获美术批准。

## 按任务工作
1. **新画面或重设计**：先确定玩家看哪里、面对谁、做什么。把环境、人物与必要 UI 组成一个代表性目标，检查主次、尺度、光向与材质，再扩展成套素材。不要先铺满功能卡片再找背景。
2. **成套资产**：使用现有可用素材或实际图像/DCC工具，以同一视觉种子锁定身份、视角、比例、边缘与细节密度。动态文字、数值与交互由引擎实现；占位图和候选图不作为完成品。
3. **情境连续性**：项目采用场所/NPC交互时，入口来自在场人物或物件，关闭后保留同一场所及状态；贴背景和头像不等于完成场景化。设置、手记等仍可采用非场景界面，不为沉浸增加无意义点击。
4. **局部工程修改**：找出 Container、anchors/offsets、最小尺寸或脚本中的真正尺寸控制者。复用 Theme，局部 override 不污染共享样式；局部间距只检查相关内容与画面，公共布局/字体变化再扩展矩阵。
5. **输入与反馈**：检查焦点、遮挡、禁用与返回。装饰层不拦截操作；动画能被后续操作打断，不能先播放成功反馈再提交失败。绘制形状与热点采用同一坐标变换。

## 交付
分别报告技术正确性、实际游戏画面和美术评价。无溢出不等于美观，概念图不等于可玩，真实截图也不是自动获批的美术。查看本次目标场景；缺图形能力则保留未验证状态。局部修复不自动调用完整美术验收。

## 按需参考
- 新方向或整幅画面：[美术方向](references/art-direction.md)。
- 素材家族、修整与导入：[资产生产](references/asset-production.md)。
- 场景与 HUD、对话、动效：[游戏化呈现](references/game-presentation.md)。
- 布局与中文：[布局检查](references/layout-localization.md)。
- 焦点与输入：[交互检查](references/input-visual.md)。
- [来源记录](references/sources.md)。只读当前任务需要的参考。
