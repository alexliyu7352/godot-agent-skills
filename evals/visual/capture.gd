extends SceneTree
## Render under X11/OpenGL, validate the UI contract, and save fresh PNG evidence.
const View = preload("res://ui_fixture.gd")
var failures: Array[String] = []
var checks: int = 0
var captures: Array[Dictionary] = []
var screen: Control

func _initialize() -> void:
	## Wait for the root Window to enter the tree before building Controls.
	call_deferred("run_capture")

func check(condition: bool, label: String) -> void:
	## Failed assertions are observable both in logs and the process exit code.
	checks += 1
	if not condition:
		failures.append(label)
		printerr("ASSERT FAIL: " + label)

func settle() -> void:
	## Layout is deferred; capture only after a real rendered frame has completed.
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw

func screenshot(name: String) -> void:
	## A nonempty render target and successful PNG write are required, not assumed.
	await settle()
	var image := root.get_texture().get_image()
	check(image != null and not image.is_empty(), "render/nonempty-" + name)
	if image == null or image.is_empty():
		return
	var path := "res://captures/" + name + ".png"
	check(image.save_png(path) == OK, "render/write-" + name)
	captures.append({"name": name, "file": "captures/" + name + ".png",
		"width": image.get_width(), "height": image.get_height()})

func layout_checks() -> void:
	## Check actual text layout and peer styles, not only property existence.
	var bounds := Rect2(Vector2.ZERO, Vector2(root.size))
	check(bounds.encloses(screen.panel.get_global_rect()), "layout/panel-in-window")
	check(bounds.encloses(screen.control_panel.get_global_rect()), "layout/peer-in-window")
	check(screen.panel.get_global_rect().encloses(screen.body.get_global_rect()), "layout/text-in-panel")
	check(screen.body.get_line_count() > 1, "text/wrapped")
	check(screen.body.size.y + 1 >= screen.body.get_minimum_size().y, "text/full-height")
	check(screen.panel.get_theme_stylebox("panel").border_width_left == 4, "theme/local-border")
	check(screen.control_panel.get_theme_stylebox("panel").border_width_left == 2, "theme/peer-border")
	for character in "官署主簿陈文南阳郡宛城，。":
		check(screen.font.has_char(character.unicode_at(0)), "font/glyph-" + character)
	for child in screen.choice_box.get_children():
		check(bounds.encloses(child.get_global_rect()), "layout/button-in-window")

func click_button(button: Button) -> void:
	## Use Viewport event dispatch; do not emit pressed or invoke its receiver.
	root.notify_mouse_entered()
	var location := button.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = location
	motion.global_position = location
	root.push_input(motion, true)
	await process_frame
	var press := InputEventMouseButton.new()
	press.button_index = MOUSE_BUTTON_LEFT
	press.button_mask = MOUSE_BUTTON_MASK_LEFT
	press.pressed = true
	press.position = location
	press.global_position = location
	root.push_input(press, true)
	await process_frame
	var release := press.duplicate() as InputEventMouseButton
	release.pressed = false
	release.button_mask = 0
	root.push_input(release, true)
	await settle()

func run_capture() -> void:
	## Exercise long text, zero choices, return focus, and reopening in one window.
	check(DisplayServer.get_name() != "headless", "render/not-headless")
	root.content_scale_size = Vector2i.ZERO
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://captures"))
	screen = View.new()
	root.add_child(screen)
	await settle()
	layout_checks()
	await screenshot("long-text")
	screen.show_state(true)
	await settle()
	check(screen.choice_box.get_child_count() == 1, "dialogue/exit-present")
	if screen.choice_box.get_child_count() == 1:
		var exit_button := screen.choice_box.get_child(0) as Button
		check(exit_button.has_focus(), "input/exit-focused")
		await screenshot("no-choices")
		await click_button(exit_button)
		check(screen.accepted.has("__return__"), "input/click-delivered")
		check(not screen.panel.visible and screen.open_button.has_focus(), "input/return-restores-focus")
		await screenshot("returned")
		if screen.open_button.visible:
			await click_button(screen.open_button)
			check(screen.panel.visible, "input/reopen-through-entry")
	var summary := {"checks": checks, "failures": failures, "captures": captures,
		"display": DisplayServer.get_name(), "renderer": RenderingServer.get_current_rendering_method(),
		"adapter": RenderingServer.get_video_adapter_name(), "window": [root.size.x, root.size.y],
		"capture_complete": captures.size() == 3, "visual_pixels_reviewed": false,
		"input_scope": "Viewport synthetic events, not OS hardware", "agent_behavior_tested": false}
	var file := FileAccess.open("res://capture.json", FileAccess.WRITE)
	if file == null:
		check(false, "render/report-write")
	else:
		file.store_string(JSON.stringify(summary, "  "))
		file.close()
	print("VISUAL_DONE checks=%d failures=%d" % [checks, failures.size()])
	screen.queue_free()
	await process_frame
	quit(1 if failures else 0)
