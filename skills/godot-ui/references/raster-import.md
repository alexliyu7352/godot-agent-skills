# 二维素材接入：过滤、切片、锚点与界面状态

仅在新增/替换素材、调整显示尺度或调查贴图问题时读取；不为一次文字修改重新导入全部图片。先复用项目既有导入预设和组件，再根据具体缺陷调整。

## 把视觉问题定位到正确的一层
| 用途/症状 | 实际检查与处理 | 常见误判 |
|---|---|---|
| 绘画背景、立绘放大有锯齿 | 查看绘制节点的 `texture_filter` 及继承来源；比较目标尺度的线性过滤结果 | 给绘画素材套像素画的 nearest |
| 像素画发糊/像素宽度跳变 | 检查 nearest、相机/节点缩放和像素对齐；优先整数显示尺度 | 只改源 PNG 分辨率 |
| 远处或缩小的绘景闪烁 | 按需生成 mipmaps，并使用支持 mipmap 的采样方式，在实际缩放下比较 | 给所有固定尺寸 UI 无条件开启 mipmaps |
| 文件变小但显存未降 | 区分磁盘压缩、解码后尺寸、GPU 压缩；Lossy 不等于降低显存 | 把 JPEG/WebP 文件大小当纹理显存 |
| 透明人物出现黑/白边 | 先查真实 alpha 和边缘颜色，再查 Fix Alpha Border、过滤和混合设置 | 用发光描边隐藏错误抠图 |
| 换表情/动作时人物跳动 | 按眼线、坐席或脚底对齐帧的逻辑画布，记录裁切偏移 | 每帧按非透明包围盒独立居中 |

Godot 4 的二维 filter/repeat 位于 CanvasItem 与相应默认设置，不是旧版 Import 页中的过滤开关；自定义 shader 的 sampler 提示或 CanvasTexture 覆盖也可能改变最终采样。压缩、mipmap 生成、alpha 处理则属于导入设置，修改后实际 Reimport 并保留工程的导入配置。不要编辑 `.godot/imported` 缓存作为源文件。

Lossless 可作为高保真二维素材的起点。大量大图需要衡量显存时，再按目标后端和可见损失选择尺寸或 GPU 压缩，不默认让低分辨率 UI 承担明显压缩块。Premult Alpha 必须与支持预乘透明的材质/混合方式配对，不能只勾选导入选项。

## 帧表与图集不是一回事
先确认源图真的满足固定网格。尺寸能整除不证明每帧人物落在正确格内；生成图尤其要逐格检查身份、接地点、边缘与遗漏肢体。

等距帧表可沿用 Sprite2D 的 `hframes`/`vframes`/`frame`，或在 SpriteFrames 中创建动画交给 AnimatedSprite2D。不规则裁切用各自 AtlasTexture 的 `region`，同时恢复逻辑画布和偏移。SpriteFrames 属于帧内容；真实时序、循环和结束事件仍由项目的动画/状态逻辑控制。

图集打包时在相邻区域之间留足边缘扩展与间隔，避免缩小采样串色。AtlasTexture 的 `filter_clip` 可防区域外采样，但不能修复缺失的像素或错误的帧网格；`margin` 不等于生成了图集的挤出边缘。检查目标缩放/过滤下的实际结果，不凭图集存在宣称 draw calls 必然下降。

## 面板与按钮的资产契约
NinePatchRect/StyleBoxTexture 的四角保持形状，边与中心只拉伸可拉伸部分；切分线不要穿过徽记、脸或文字。内容边距与纹理切分边距分别确定，正文由 Label/RichTextLabel 实时渲染，不烘焙在图片中。

沿用项目已有的 normal、hover、pressed、disabled、focus 等状态。状态可由同一底图、颜色/线条覆盖组合，不要求每个状态一张新图。焦点与鼠标悬停可能同时出现；支持键盘/手柄的项目要看可辨认的焦点，不能只靠 hover。不要为只支持鼠标的项目擅自增加完整手柄方案。

## 交付检查
把一组有代表性的素材放回已有场景，检查常用尺度、实际背景、需要的状态和热点。比较同一角色/图标家族的基线与颜色职责；只在本次涉及的缩放/动画范围扩展检查。正式源图、运行副本与导入配置各自可追溯，缺原图或 alpha 就记录缺口，不以重新画一间房代替技能任务。

来源：[awesome-gamedev raster-pipeline（固定版本）](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/references/raster-pipeline.md)。Godot 细节核对 [4.6 图像导入](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/importing_images.html)、[CanvasItem](https://docs.godotengine.org/en/4.6/classes/class_canvasitem.html)、[AtlasTexture](https://docs.godotengine.org/en/4.6/classes/class_atlastexture.html)；这不是要求升级项目版本。
