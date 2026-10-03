extends Control
## Synthetic UI fixture, not proposed game art or a new dialogue framework.
const LocalTheme = preload("res://examples/local_theme.gd")
const Choices = preload("res://examples/choice_routes.gd")
const LONG_TEXT := "宛城近日往来商旅渐多，主簿正在核对各处送来的文书。若要领取这份差事，请先确认行程、携带物品与交付期限。途中即使离开城镇，也应保留任务状态；返回官署后，与发布差事的办事人员交谈，查看条件是否仍然满足。这里使用较长的中文句子、人名、地名和全角标点，检查窄窗口下的换行、内边距和按钮位置，而不是用几个英文单词代替实际内容。"
var body: Label
var panel: PanelContainer
var control_panel: PanelContainer
var choice_box: VBoxContainer
var open_button: Button
var status: Label
var font: SystemFont
var shared_style: StyleBoxFlat
var routes: Array[Dictionary] = [{"id": "accept"}, {"id": "ask"}]
var no_choices: bool = false
var accepted: Array[String] = []

func _ready() -> void:
	## Containers own sizing; the optional overlay exists to test click interception.
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	font = SystemFont.new()
	font.font_names = PackedStringArray(["Noto Sans CJK SC"])
	var theme_resource := Theme.new()
	theme_resource.default_font = font
	theme_resource.default_font_size = 18
	shared_style = StyleBoxFlat.new()
	shared_style.bg_color = Color(0.10, 0.13, 0.19)
	shared_style.border_color = Color(0.68, 0.62, 0.44)
	shared_style.set_border_width_all(2)
	shared_style.set_content_margin_all(14)
	theme_resource.set_stylebox("panel", "PanelContainer", shared_style)
	theme = theme_resource
	var outer := MarginContainer.new()
	add_child(outer)
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	LocalTheme.set_padding(outer, 24)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 12)
	outer.add_child(column)
	var title := Label.new()
	title.text = "官署交互 · 验收测试场景"
	title.add_theme_font_size_override("font_size", 24)
	column.add_child(title)
	status = Label.new()
	status.text = "窄窗口、中文长文本、局部样式与返回路径"
	status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(status)
	open_button = Button.new()
	open_button.text = "与主簿交谈"
	open_button.pressed.connect(reopen)
	column.add_child(open_button)
	open_button.hide()
	panel = PanelContainer.new()
	panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(panel)
	LocalTheme.set_panel_border(panel, 4)
	var inner := VBoxContainer.new()
	inner.add_theme_constant_override("separation", 12)
	panel.add_child(inner)
	var speaker := Label.new()
	speaker.text = "主簿 · 陈文    南阳郡宛城"
	speaker.add_theme_color_override("font_color", Color(0.94, 0.80, 0.48))
	inner.add_child(speaker)
	body = Label.new()
	body.text = LONG_TEXT
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	inner.add_child(body)
	choice_box = VBoxContainer.new()
	choice_box.add_theme_constant_override("separation", 8)
	inner.add_child(choice_box)
	control_panel = PanelContainer.new()
	column.add_child(control_panel)
	var control_text := Label.new()
	control_text.text = "共享样式对照：此面板边框保持 2 像素。"
	control_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	control_panel.add_child(control_text)
	var blocker := ColorRect.new()
	blocker.color = Color(0, 0, 0, 0)
	blocker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(blocker)
	blocker.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	show_state(false)

func eligible(_id: String) -> bool:
	## Conditions are side-effect free and are checked again when selected.
	return not no_choices

func show_state(empty: bool) -> void:
	## Rebuild only visible routes; zero choices must still expose an exit.
	no_choices = empty
	panel.show()
	open_button.hide()
	status.text = "当前无可领取事项，仍可返回。" if empty else "两项可交互选项；点击时会重新确认条件。"
	for child in choice_box.get_children():
		choice_box.remove_child(child)
		child.free()
	var available := Choices.available_routes(routes, eligible)
	for route in available.routes:
		var button := Button.new()
		button.text = "返回官署" if route.kind == "return" else ("领取差事" if route.id == "accept" else "询问缘由")
		button.pressed.connect(on_route.bind(String(route.id)))
		choice_box.add_child(button)
	if choice_box.get_child_count() > 0:
		(choice_box.get_child(0) as Button).grab_focus()

func can_return() -> bool:
	## This fixture has no transactions; hidden/closed panels invalidate return.
	return is_instance_valid(panel) and panel.is_visible_in_tree()

func on_route(id: String) -> void:
	## Observe the actual Button signal; no test calls this function directly.
	var selected := Choices.choose(id, routes, eligible, can_return)
	if not selected.ok:
		status.text = "条件已变化，请重新选择。"
		return
	accepted.append(id)
	if selected.route.kind == "return":
		panel.hide()
		open_button.show()
		open_button.grab_focus()
		status.text = "已返回官署，可以再次交谈。"

func reopen() -> void:
	## Restore interaction through the displayed entry button.
	show_state(no_choices)
