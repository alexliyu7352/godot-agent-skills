extends RefCounted
## 只演示可选路由与条件重验；条件 Callable 无副作用，奖励由现有提交层处理。
## 保留 __return__ 给退出路由。可选 ID 必须是唯一的非空 String。

static func available_routes(options: Array[Dictionary], eligible: Callable) -> Dictionary:
	## 根据实时条件过滤；全部不可用时仍返回一个可退出的显式路由。
	var routes: Array[Dictionary] = []
	var seen: Dictionary = {}
	for option in options:
		var id = option.get("id")
		if not id is String or id.is_empty() or id == "__return__" or seen.has(id):
			return {"ok": false, "reason": "invalid_option_id"}
		seen[id] = true
		if eligible.call(id):
			routes.append({"id": id, "kind": "choice"})
	if routes.is_empty():
		routes.append({"id": "__return__", "kind": "return"})
	return {"ok": true, "routes": routes}

static func choose(id: String, options: Array[Dictionary], eligible: Callable) -> Dictionary:
	## 点击时重新构造允许集合，拒绝已过期选项；不在展示阶段扣款或发奖。
	var current := available_routes(options, eligible)
	if not current.ok:
		return current
	for route in current.routes:
		if route.id == id:
			return {"ok": true, "route": route}
	return {"ok": false, "reason": "stale_choice"}
