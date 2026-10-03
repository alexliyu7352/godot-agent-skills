# preview.4 内容完整性与实用性审查

日期：2026-10-03。审查基线：`ec6eb4d0a91af363e9713146aee1a6893687d356`（preview.3）。本轮只改知识内容、来源映射、发布清单及相应说明；不新增技能入口、模型调用、游戏资产、执行器或测试平台。

## 结论与边界

七入口结构可保留。问题不是所有正文都无用，而是部分内容从“怎样做”退化为“注意检查”，以及入口的轻量要求没有贯穿参考层。preview.3 补回的美术方向也应保留，但不再继续制作官署作为主交付。

这是作者对实际内容的再次审读与任务推演，不是第二个独立模型评测，也不是已运行的有/无技能对照。本轮没有用文件长度、安装量或CI数量评分技能收益。固定来源范围见文末；不声称逐字审完三个库全部目录。

## 七个领域的取舍

| 领域 | 已有内容保留 | 本轮确认的缺口/冲突 | 处理 |
|---|---|---|---|
| 代码与场景 | 类型、对象生命周期、owner、保存后重载、热点变换 | 缺少寻找现有组件与接入的方法；上游组合建议含过度规则 | 加 `reuse-integration.md`：实际调用链、配置/组合/继承、插件版本、注入时机；不引入15节点拆分阈值或强制总线 |
| 数据与时间 | 定义/运行/派生状态区分、离屏状态、动作提交边界 | `transactions-time.md` 的“最少测试”仍像每任务整套要求 | 依据写集合、等待、期限、恢复分别选择；只改呈现不展开交易回归 |
| 对话 | 零有效选项、提交重验、过期会话与一次性结果 | “沿用插件”没有接入点；把所有对话脚本一概当不可执行数据过严；验收列表未分范围 | 补开始/行/选项/效果/结束的接缝与显示身份映射；保留可信插件能力；按变更选择检查 |
| 存档 | 一致快照、迁移/未来版本、暂存恢复、I/O故障处理 | 本轮没有发现需要再加一套运行器的缺口 | 不重写 SaveManager，不改已测 `.gd` 示例；保留当前明确的能力边界 |
| UI与美术 | 视觉目标、家族一致性、场所连续性、原生文字与输入 | 素材工程细节不足；参考无条件要求键盘/手柄支持 | 加 `raster-import.md`：Godot4过滤位置、alpha、帧对齐、图集、九宫格/状态；设备遵循项目范围 |
| 调试与性能 | 实际场景树、连接检查、最小复现 | `performance.md` 列了候选热点却没有下一步诊断 | 改成症状→观测→最小修正；细分冷加载/入树、线程加载状态和CPU/GPU证据 |
| 验证 | 解析/逻辑/输入/渲染/美术证据分开，失败不改判定 | 缺真实宿主环境不能靠继续造测试平台解决 | 不扩建 runner/CI，不新增案例；46个真实宿主案例保持 NOT_RUN |

## 为什么这不是简单恢复上游模板

`GodotPrompter/scene-organization` 的组合/继承判断能帮助实际复用，但“约15节点即需拆分”和“平级通信一律EventBus”不适合作为硬规则。新的参考保留决策方法，拒绝阈值与唯一通信方式。

实例化、普通依赖赋值和 `_ready()` 不是可任意交换的步骤。按 Godot 官方 Node 生命周期明确：加入运行树会触发回调，子 `_ready()` 早于父；不能在父就绪时才提供孩子已经使用的依赖。具体场景仍以代码、导出配置与目标版本为准。

素材流水线保留同一家族、共同基线、图集边缘和状态设计，但不照搬其他引擎的导入参数。Godot4的二维采样设置与导入压缩分属不同位置，图集不会自动修复人物跳动或保证批次降低。

性能技能保留测量和验证方法，不照搬“总是池化”或给任意 Node 设置 visible 的例子。线程加载若过早调用 get 仍会阻塞；异步I/O不代表场景实例化也无耗时。没有本轮新跑的性能基准，因此不报告提升比例。

## 修改后内容能怎样指导任务（静态推演，不是运行结果）

| 任务 | 以前容易缺少的决策 | 现在参考给出的具体做法 |
|---|---|---|
| 新增一个商人交互 | 只说复用，随后仍写第二套管理器 | 追已有目标→交易视图→唯一结算服务；优先配置/适配，只填确认缺口 |
| 调整一个对话框间距 | 把所有分辨率、设备、存档都加入验收 | 沿用当前美术，检查相关控件/显示与项目已有输入，不读新资产流程 |
| 同人物多表情在游戏中跳动 | 再生成更多立绘，仍逐张居中 | 检查逻辑画布、眼线/脚底和裁切偏移，按同一基线导入 |
| 条件过滤后选中错误话题 | 把显示序号交回原选项列表 | 保存显示项到真实选择身份的映射，仍使用现有运行器 |
| 切换城镇首帧卡顿 | 泛泛改异步或线程数 | 分别测资源加载与实例化/入树，状态为LOADED才取结果 |
| 旧存档恢复异常 | 又写一份万能存档模板 | 保留既有迁移与暂存提交方法；只修改已发现的恢复边界 |

这些推演检查了文本中是否确有解决方法，不产生成功率或触发准确率。能力较强的Agent可能原本就能完成；是否净提效仍需要真实对照。

## 固定来源与本轮阅读范围

awesome-gamedev 固定 `d4b0e35550c55ae70bdfcab4ef5a0e94610438a9`。本轮直接对照 `godot-gdscript`、`godot-nodes-scenes`、`dialogue-systems`、`save-systems` 的正文，以及新增吸收的 [raster-pipeline](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/references/raster-pipeline.md) 和 [performance-optimization](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/performance-optimization/SKILL.md)。现有 Resource/UI 与基础美术来源沿用此前锁定审读结果，本轮不宣称重新完整阅读未取得的文件。

GodotPrompter 固定 `3e8d0f005f9604e1dbdad3de693e39555384c5af`。本轮读取 [scene-organization](https://github.com/jame581/GodotPrompter/blob/3e8d0f005f9604e1dbdad3de693e39555384c5af/skills/scene-organization/SKILL.md) 和 [godot-debugging](https://github.com/jame581/GodotPrompter/blob/3e8d0f005f9604e1dbdad3de693e39555384c5af/skills/godot-debugging/SKILL.md) 正文；未宣称递归读完其全部 references。

Godogen 固定 `8f315780bf50eea1875e08c8b614930e9d6e8450`，保留此前已吸收的场景保存检查，本轮不增加其实现或总控。新增来源写入 `sources.lock.json` 和对应技能来源页；许可证不变。

关键 API 用官方4.6文档复核：[Node](https://docs.godotengine.org/en/4.6/classes/class_node.html)、[ResourceLoader](https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html)、[图像导入](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/importing_images.html)、[CanvasItem](https://docs.godotengine.org/en/4.6/classes/class_canvasitem.html)、[AtlasTexture](https://docs.godotengine.org/en/4.6/classes/class_atlastexture.html)。不以 latest 文档假定项目小版本支持同一 API。

## 发布与验证约束

只增加两份按需参考，不扩大为新框架；只有实际变更文件进入此次Git提交，原工具、工作流、测试和五份可执行GDScript示例保持不变。新增指导中的文字/API步骤是文档核查，不冒充新执行过的引擎程序。

当前可用本地恢复工作树早于远端，不能覆盖整个仓库；发布使用固定远端树加明确修改清单，保留远端已有内容。文件哈希、来源和引用做静态核对；完整回归以本提交的远端CI为准。既有63项测试只检查对应结构/工具，不证明语义和美术收益。

不新增音频、战斗、导航、网络等领域来凑“完整”。它们是否需要额外技能由项目实际任务决定，本包不声称涵盖Godot全部专业能力。缺真实宿主执行环境仍明确记录；不以另做游戏或新增截图替代。
