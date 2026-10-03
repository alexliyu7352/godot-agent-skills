# 性能定位：从一次卡顿找到可验证的改动

仅处理已经观察到的延迟、卡顿或规模问题。先复用项目 Profiler/监视器，不建立新性能平台，也不因看到循环、信号或 load 就重写代码。

## 记录能重现同一负载的条件
固定引擎/构建、渲染后端、分辨率、人物/数据规模、输入或随机种子。把冷加载、预热后操作、长时间反复进出分开。看帧时间与尖峰，而不仅平均 FPS；调试构建用于归因，目标发布构建用于确认实际改善。

Profiler 先区分函数自身耗时与包含被调用函数的耗时，再看调用次数：一个函数单次便宜却每帧调用几千次，与一个偶发重计算不是同一问题。Monitors 的节点、对象、内存和绘制统计辅助验证假设，具体可用指标依引擎和后端而定。

## 症状到下一步
| 症状 | 先观察 | 最小候选修正与回归边界 |
|---|---|---|
| 推进一天时顿一下 | 该次结算的调用次数、每类人物耗时、UI刷新次数 | 缓存不变定义、合并重复派生计算/通知；不能漏算离屏人物或期限事件 |
| 打开人物列表卡顿 | 创建节点、加载头像、文本排版分别耗时 | 只更新变化项；确为大列表时采用已有分页/虚拟化，不先造对象池 |
| 切换场所第一次慢、之后快 | 冷/热加载差异、资源加载与实例化/入树的分段耗时 | 确定是I/O/解码还是大量 `_ready()`；后台加载不能解决所有入树开销 |
| 脚本耗时低但画面慢 | 渲染统计，暂时关闭相关透明层/特效后的对照 | 减少实测过度绘制、过大纹理/特效；改变材质或层次后检查外观 |
| 每次进出对象数持续增加 | 相同基线状态下节点/对象数、未释放实例、订阅与资源引用 | 定位持有者；缓存预热后的稳定平台不是泄漏，持续增长才继续追查 |

临时关闭一个效果是定位手段，不是直接提交删掉玩法/美术。用 `Time.get_ticks_usec()` 差值可观察一段 CPU 路径经过的时间；不要把提交渲染命令耗时称为 GPU 渲染时间。采样日志避免每帧刷屏干扰测量。

## 已确认同步资源加载是热点时
沿用现有加载服务，先合并相同资源的重复请求，而不是每帧发一个新请求。Godot ResourceLoader 的调用顺序为：

```text
load_threaded_request(path) → 检查 Error 返回值
跨帧 load_threaded_get_status(path) → IN_PROGRESS 继续等
                                     FAILED/INVALID 明确失败
                                     LOADED 才 load_threaded_get(path)
资源返回 → 核对请求仍有效/类型正确 → 在主线程接入活跃场景
```

`load_threaded_get()` 在加载完成前调用仍会阻塞；一个紧循环反复查状态也会卡住主线程。异步加载完成与场景实例化/纹理上屏是不同阶段，分别测量。取消显示需求可以使旧结果失效，不应声称这就终止了底层加载；对象释放和队列行为沿用项目的生命周期契约。

## 优化必须保留原来的语义
缓存记录失效条件；合并通知不能让观察者看到部分结算。按事件推进或分批工作先确认顺序、随机序列和提交边界；不是只把每帧更新换成定时器就自动等价。对象池只用于实测高频创建/销毁，并重置全部可变状态；Node 不是都能靠 `visible=false` 停止处理。

C#、Server API、批处理和原生扩展不自动改变算法复杂度。GDScript 引用计数与 .NET GC 的分配/释放行为不同，不把其他引擎的 GC 建议原样套用。扩大线程数也不是默认修复，尤其不能随意从工作线程修改活跃 SceneTree。

## 接受改动
在相同负载下比较前后耗时、尖峰和行为；只改已定位的热点。低、中、实际目标规模用于检查趋势，不设与项目无关的固定人物数量。效果不明显就保留更容易维护的实现；报告条件和测量值，不承诺固定倍数提升。

来源：[GodotPrompter debugging](https://github.com/jame581/GodotPrompter/blob/3e8d0f005f9604e1dbdad3de693e39555384c5af/skills/godot-debugging/SKILL.md)、[awesome-gamedev performance-optimization](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/performance-optimization/SKILL.md)。只保留测量和瓶颈选择方法，不继承无条件对象池建议。API核对 [Godot 4.6 ResourceLoader](https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html) 与 [Performance](https://docs.godotengine.org/en/4.6/classes/class_performance.html)。
