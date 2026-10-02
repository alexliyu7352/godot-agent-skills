extends Resource
## counters 仅含 JSON 风格的标量、Array 和 Dictionary；style 是共享只读定义。
## 这是复制边界示例，不是任何 Resource 图的通用深拷贝器。

@export var counters: Dictionary = {}
@export var style: Resource

func fork_runtime() -> Resource:
	## 复制可变数值容器，保留有意共享的只读外观；不用全局 class_name。
	var copy = get_script().new()
	copy.counters = counters.duplicate(true)
	copy.style = style
	return copy
