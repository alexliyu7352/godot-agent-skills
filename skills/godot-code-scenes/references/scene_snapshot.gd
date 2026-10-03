extends RefCounted
## 最小场景 roundtrip 工具。调用者决定输出路径和 owner，不重写整个项目。

static func save_and_reload(root: Node, path: String) -> Dictionary:
	## 保存并从磁盘重新载入；成功时调用者负责释放返回的 instance。
	if root == null or not path.ends_with(".tscn"):
		return {"ok": false, "reason": "invalid_input"}
	var packed := PackedScene.new()
	var error := packed.pack(root)
	if error != OK:
		return {"ok": false, "reason": "pack_failed", "error": error}
	error = ResourceSaver.save(packed, path)
	if error != OK:
		return {"ok": false, "reason": "save_failed", "error": error}
	# IGNORE 绕过主场景与内嵌子资源缓存；外部依赖仍可能按 REUSE 取缓存。
	# 本 helper 不证明整个依赖图均来自磁盘；需要该证据时使用干净进程，
	# 或在锁定版本支持时明确采用 IGNORE_DEEP，并测试外部依赖。
	var reloaded := ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	if reloaded == null:
		return {"ok": false, "reason": "reload_failed"}
	var instance := reloaded.instantiate()
	if instance == null:
		return {"ok": false, "reason": "instantiate_failed"}
	return {"ok": true, "instance": instance}
