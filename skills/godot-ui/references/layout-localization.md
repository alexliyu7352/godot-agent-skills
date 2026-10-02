# 布局、Theme 与中文显示

## 先找尺寸的控制者
Container 会按照自身规则分配子 Control 的尺寸/位置。检查最小尺寸、size flags、分离间距和 margin 所在层。父布局持续覆盖子节点位置时，不通过 `_process()` 不断写回坐标解决。

非 Container 管理的控件再检查 anchors、offsets、父尺寸、viewport 和 stretch 设置。局部边距问题不要先修改整个窗口缩放策略。

## Theme 与复用
找出样式来自全局 Theme、类型变体、父控件还是局部 override。修改共享资源会影响所有引用者；只有确实需要独立样式才复制，并验证嵌套子资源。局部问题不全工程换字体或调整所有按钮尺寸。

项目存在统一对话、交易、列表组件时优先复用；需要改变公共组件契约才审查影响面。重复页面、占位面板和解释性开发文字不能当成完成后的游戏内容。

## 中文与内容边界
使用真实长度的人名、地名、任务说明和数量值。验证字体包含相应字形、字体回退、汉字换行、标点、富文本和多行排版。动态文本使用项目的翻译参数方式，避免拼接使语序不可本地化。

字体许可属于资产管理；不要因为技能包示例而下载/发布未知许可字体。未获得真实资产时明确占位状态，不宣称视觉定稿。

## 检查矩阵
先根据变更选择下面的行，而不是执行整张表。项目已有且仍有效的验收证据可以复用。

| 改动 | 追加检查 |
|---|---|
| 单控件 margin/颜色/局部 override | 相关控件在当前目标尺寸与代表性内容下的布局和可见结果 |
| 公共 Theme/最小尺寸算法/stretch | 受影响组件及最小、常用、不同长宽比窗口；已有平台矩阵优先 |
| 字体/换行/文本容器 | 中文长文本、字体回退、富文本及相关最小尺寸 |
| 列表/数量表现 | 仅检查对应空列表、最大数量或滚动边界 |
| 弹窗/焦点/输入处理 | 打开、关闭、焦点恢复与真实事件路径 |

未改字体的局部边距不要求遍历全部语言；为相关控件使用真实中文长度，不用英文短占位符替代。

可见截断、交叠或点击区错位要记录具体控件与场景状态。需要截图时包含窗口尺寸、UI 缩放、语言和构建标识，避免无法复现。

官方核查：
- https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html
- https://docs.godotengine.org/en/stable/tutorials/ui/gui_using_theme_editor.html
- https://docs.godotengine.org/en/stable/tutorials/i18n/internationalizing_games.html

## 可运行的局部修改方法
[local_theme.gd](local_theme.gd) 用 MarginContainer 的 margin_* override 调整本地边距，用 StyleBoxFlat.duplicate() 后的局部 panel override 调整边框。对照面板继续引用原 Theme；不能对 get_theme_stylebox() 的返回值直接改共享数据。

布局例子：Control 下放满尺寸 MarginContainer，再放 VBoxContainer 和 Label/Button。MarginContainer 拥有子 VBox 的位置；VBox 拥有 Label/Button 的排列。修改后等待 Container 的布局更新，再读取子 rect 检查偏移；不在 _process 里反复写 position。窗口缩放或公共最小尺寸算法没有改变时，不自动扩大验证矩阵。

headless 可以检验 rect、局部 StyleBox 与焦点事件，不证明字体渲染、美观或设备实际点击。后者仍需相关窗口的真实画面/事件证据。
