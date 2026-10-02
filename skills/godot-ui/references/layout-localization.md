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
至少检查目标最小窗口、常用窗口、一个不同长宽比；已有目标平台矩阵优先。对当前改动使用中文长文本、空列表、最大数量/负例提示、滚动到末尾和弹窗。仅改一个边距不意味着必须测试全部语言，但不能继续只用两个英文单词证明中文支持。

可见截断、交叠或点击区错位要记录具体控件与场景状态。需要截图时包含窗口尺寸、UI 缩放、语言和构建标识，避免无法复现。

官方核查：
- https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html
- https://docs.godotengine.org/en/stable/tutorials/ui/gui_using_theme_editor.html
- https://docs.godotengine.org/en/stable/tutorials/i18n/internationalizing_games.html
