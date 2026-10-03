# 生命周期、类型与资源引用

## 查看实际工程，而不是建立第二份架构
从被修改的场景和脚本进入，查直接依赖、调用方及已确认文档。只有任务触及共享契约才扩大搜索。不要无理由创建新的 Autoload；一个全局入口不代表所有状态都应归它管理。

项目锁定版本优先于技能示例。遇到不确定 API，查询该版本的本地文档/官方类文档或用最小脚本核实。不要按名字猜测 `Signal.any()`、`Resource.make_unique()` 等接口存在。GDScript 的 preload 类型引用可用于合适场景，并非必须把所有类型注册为 class_name。

## 生命周期决策

| 情况 | 要确认的内容 |
|---|---|
| 构造与 `_init()` | 脚本初始化时依赖是否已被赋值，不能假定 PackedScene 子节点已可用 |
| `@onready`/`_ready()` | 读取的场景节点是否真实存在；嵌套实例和导出 Node 引用是否有效 |
| 退出场景/取消操作 | 谁持有对象、谁释放、是否还有延迟回调或后台结果等待写回 |
| `await` 返回 | 对象有效不等于操作仍有效；同时检查任务取消标记/请求世代 |
| 信号连接 | 是否重复初始化、是否使用不同 lambda 难以断开、接收者生命周期是否正确 |

`queue_free()` 是延迟释放。不能因为在同一帧仍可访问，就把节点当作长期有效。对象有效性检查是边界保护，不替代正确所有权。断连策略取决于连接与捕获关系，不能宣称所有信号都会泄漏或全部自动安全。

## 类型与身份
强类型用于稳定契约和发现错误；动态内容在边界校验。使用 `%Name` 需要对应唯一名称及所有者作用域，不能跨任意场景树全局查找，也不是目标重命名安全。改名后检查脚本、动画轨道、连接、导出路径与测试。

Resource 按路径缓存时可能共享引用。修改共享模板会影响实例；需要独立状态时明确复制深度和嵌套集合/子资源语义。`duplicate(true)` 的行为仍受对象结构及引擎版本影响，应测试具体对象图；它不是任意运行对象的通用深拷贝。改变内存状态并不自动持久化。

纯计算可位于 Resource、RefCounted、普通 C# 对象或现有服务；需要树事件时才选 Node。根据可测试性、状态归属和项目习惯选择，避免反向强制所有业务只许一种类型。

## 修改验收
验证与改动对应：修改场景初始化、导出引用、信号或生命周期时，实例化相关场景并检查受影响的绑定/回调；独立纯函数只做类型和相关逻辑检查，不为测试创建场景、Node 或 Autoload。未改变的机制不展开全量回归。必需依赖缺失应返回明确失败；格式化整个文件、重排所有节点和重写 UID 不是局部修复的默认动作。

官方核查：
- https://docs.godotengine.org/en/stable/classes/class_node.html
- https://docs.godotengine.org/en/stable/classes/class_resource.html
- https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/static_typing.html

## 独立脚本与异步生命周期的具体写法
小型纯规则函数沿用现有类型与数值契约；不为函数创建场景节点。不确定动态资源类型时 `var scene := load(path) as PackedScene` 并检查必需资源，不用猜测 API。`@onready var button: Button = %Button` 只适用于对应场景的唯一名称；独立纯脚本不要强行添加节点引用。

```gdscript
var _generation: int = 0

func invalidate_request() -> void:
    ## 关闭窗口或切换数据时使旧请求失效，即使窗口实例没有被释放。
    _generation += 1

func refresh_after_delay() -> void:
    ## 有效性与世代都通过才接受结果；销毁自身的情况沿用项目取消策略。
    _generation += 1
    var expected := _generation
    var target := get_node_or_null("ResultLabel") as Label
    await get_tree().create_timer(0.2).timeout
    if expected != _generation or not is_instance_valid(target):
        return
    target.text = "已刷新"
```

上述片段需要放入实际 Node/Control 脚本，不是独立可执行程序。它展示旧结果保护，不声称取消了底层 I/O；也不要在无异步行为的任务中引入请求世代。
