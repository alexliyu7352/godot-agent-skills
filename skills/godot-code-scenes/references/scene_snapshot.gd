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
	# 绕过已有缓存，不能只实例化上面的内存 packed 后宣称磁盘重载通过。
	var reloaded := ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	if reloaded == null:
		return {"ok": false, "reason": "reload_failed"}
	var instance := reloaded.instantiate()
	if instance == null:
		return {"ok": false, "reason": "instantiate_failed"}
	return {"ok": true, "instance": instance}
