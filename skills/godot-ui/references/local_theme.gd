extends RefCounted
## Container 继续拥有布局；通过正确层级的 override 修改局部外观。

static func set_padding(container: MarginContainer, pixels: int) -> Error:
	## 为本 MarginContainer 设置四边边距，不修改共享 Theme 或写子节点位置。
	if container == null or pixels < 0:
		return ERR_INVALID_PARAMETER
	for side in ["left", "right", "top", "bottom"]:
		container.add_theme_constant_override("margin_" + side, pixels)
	return OK

static func set_panel_border(panel: PanelContainer, pixels: int) -> Error:
	## 复制后只覆盖当前面板；其他 StyleBox 类型返回错误，不擅自更换风格。
	if panel == null or pixels < 0:
		return ERR_INVALID_PARAMETER
	var original := panel.get_theme_stylebox("panel") as StyleBoxFlat
	if original == null:
		return ERR_INVALID_DATA
	var local := original.duplicate() as StyleBoxFlat
	local.set_border_width_all(pixels)
	panel.add_theme_stylebox_override("panel", local)
	return OK
