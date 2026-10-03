extends RefCounted
## 只演示可选路由与条件重验；条件 Callable 无副作用，奖励由现有提交层处理。
## 保留 __return__ 给退出路由。可选 ID 必须是唯一的非空 String。

static func available_routes(options: Array[Dictionary], eligible: Callable) -> Dictionary:
	## 根据实时条件过滤；零选项返回导航候选，实际退出仍由会话策略决定。
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

static func choose(id: String, options: Array[Dictionary], eligible: Callable, can_return: Callable = Callable()) -> Dictionary:
	## 业务选项重验资格；导航只检查独立退出策略，不因话题资格变化作废。
	if id == "__return__":
		if not can_return.is_valid():
			return {"ok": false, "reason": "return_policy_required"}
		var permitted = can_return.call()
		if not permitted is bool or not permitted:
			return {"ok": false, "reason": "return_blocked"}
		return {"ok": true, "route": {"id": "__return__", "kind": "return"}}
	var current := available_routes(options, eligible)
	if not current.ok:
		return current
	for route in current.routes:
		if route.id == id:
			return {"ok": true, "route": route}
	return {"ok": false, "reason": "stale_choice"}
