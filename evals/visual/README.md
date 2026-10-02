# 渲染验证夹具（不是游戏 UI 定稿）

使用仓库已发布的 `choice_routes.gd` 与 `local_theme.gd`，在真实 X11 窗口、OpenGL compatibility 渲染下检查中文长文本、布局、局部 Theme、零选项退路与返回后的焦点。不是 `--headless`，也不调用任何视觉模型。

```bash
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1920x1080x24' \
  python3 tools/check_visual.py --godot /absolute/path/to/godot --out /tmp/new-visual-evidence
```

需要机器已有 Xvfb、Mesa 和系统 `Noto Sans CJK SC` 字体；本工具不安装依赖、不附字体文件，CI 在独立 runner 安装这些依赖。生成的 PNG 不含字体文件。

默认运行 800×600、1280×720、1600×900，各捕获长文本、零选项、返回后三种状态。测试还在临时副本中分别引入“关闭中文换行”和“透明覆盖层截获输入”；只有出现指定断言失败且捕获阶段正常结束，才承认测试抓住了对应问题。

`summary.json` 的 passed 仅表示渲染/布局/输入契约与反例检测符合预期。自动结果中的 `visual_pixels_reviewed` 固定为 false；只有实际打开图片并记录检查范围后，才能另写查看结果。CI 不会替作者声称图片已经被看过。

输入经 `Viewport.push_input` 进入 Godot 的 GUI 分发，不是直接调用回调；也不是操作系统鼠标设备测试。没有游戏立绘或地图，不代表用户真实游戏已经经过验收。

技术依据：Godot 4.6 [Viewport 捕获说明](https://docs.godotengine.org/en/4.6/tutorials/rendering/viewports.html)，截图等待 `RenderingServer.frame_post_draw` 后读取纹理；[Viewport API](https://docs.godotengine.org/en/4.6/classes/class_viewport.html) 说明输入分发范围。
