extends RefCounted
## 最小只读暂存器：展示版本拒绝和候选副本，不是完整 SaveManager。
## 未包含项目的迁移链、实体恢复和磁盘替换；调用者只可提交 ok=true 的候选。

static func decode(text: String, current_version: int) -> Dictionary:
	## JSON 解析后先验证版本；任何失败不修改传入文本或当前世界。
	var parser := JSON.new()
	if parser.parse(text) != OK or not parser.data is Dictionary:
		return {"ok": false, "reason": "invalid_json"}
	var envelope: Dictionary = parser.data
	var version = envelope.get("version")
	if (not version is int and not version is float) or current_version < 1:
		return {"ok": false, "reason": "invalid_version"}
	if not is_finite(float(version)) or float(version) != floor(float(version)) or version < 1:
		return {"ok": false, "reason": "invalid_version"}
	if version > current_version:
		return {"ok": false, "reason": "future_version"}
	if version < current_version:
		return {"ok": false, "reason": "migration_required"}
	if not envelope.get("state") is Dictionary:
		return {"ok": false, "reason": "invalid_state"}
	return {"ok": true, "candidate": envelope.state.duplicate(true)}

static func stage_file(path: String, current_version: int) -> Dictionary:
	## 仅从选定文件读取；未来版本拒绝后不执行写回或自动创建新档。
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {"ok": false, "reason": "open_failed", "error": FileAccess.get_open_error()}
	var size := file.get_length()
	if size > 16 * 1024 * 1024:
		file.close()
		return {"ok": false, "reason": "too_large"}
	var bytes := file.get_buffer(size)
	var error := file.get_error()
	file.close()
	if error != OK or bytes.size() != size:
		return {"ok": false, "reason": "read_failed", "error": error}
	return decode(bytes.get_string_from_utf8(), current_version)
