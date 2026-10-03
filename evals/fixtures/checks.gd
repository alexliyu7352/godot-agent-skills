extends SceneTree
## Independent assertions over the bundled helpers; run in a disposable project.
const SceneSnapshot = preload("res://examples/scene_snapshot.gd")
const RuntimeState = preload("res://examples/runtime_state.gd")
const LocalTheme = preload("res://examples/local_theme.gd")
const Choices = preload("res://examples/choice_routes.gd")
const SaveEnvelope = preload("res://examples/save_envelope.gd")
const Actor = preload("res://actor.gd")
var failures: int = 0
var returned: bool = false
var counts: int = 0

func _initialize() -> void:
	## Defer until the scene tree is ready for GUI/layout operations.
	call_deferred("run_checks")

func check(condition: bool, name: String) -> void:
	## Always emit an explicit failed assertion and track nonzero process exit.
	counts += 1
	if not condition:
		failures += 1
		printerr("ASSERT FAIL: " + name)

func run_checks() -> void:
	## Each mode is a separate process, including disk write versus restoration.
	var args := OS.get_cmdline_user_args()
	if "build" in args:
		build_scene()
		write_save()
	elif "reload" in args:
		reload_scene()
		reload_save()
	else:
		test_resources()
		test_dialogue()
		await test_gui()
	print("FIXTURE_DONE checks=%d failures=%d" % [counts, failures])
	quit(1 if failures else 0)

func verify_actor(instance: Node) -> void:
	## Assert content and bindings, not only counts or a successful pack call.
	var button := instance.get_node_or_null("Button") as Button
	check(button != null, "scene/button retained")
	check(instance.get("label") == "官署", "scene/export retained")
	if button == null:
		return
	check(instance.get("target") == button, "scene/export points at reloaded child")
	button.pressed.emit()
	check(instance.get("presses") == 1, "scene/persistent signal targets new receiver")

func build_scene() -> void:
	## Build owned descendants and a persistent connection into a disk scene.
	var actor := Actor.new()
	actor.name = "Official"
	var button := Button.new()
	button.name = "Button"
	button.text = "交谈"
	actor.add_child(button)
	button.owner = actor
	actor.target = button
	button.pressed.connect(actor.on_pressed, Object.CONNECT_PERSIST)
	var result := SceneSnapshot.save_and_reload(actor, "res://roundtrip.tscn")
	check(result.ok, "scene/saved and reloaded")
	if result.ok:
		verify_actor(result.instance)
		result.instance.free()
	actor.free()

func reload_scene() -> void:
	## New process: exported references and signals must survive without old cache.
	var packed := load("res://roundtrip.tscn") as PackedScene
	check(packed != null, "scene/disk load")
	if packed == null:
		return
	var instance := packed.instantiate()
	verify_actor(instance)
	instance.free()

func write_save() -> void:
	## Create isolated supported and future files; no player files are touched.
	for item in [["current.json", 2], ["future.json", 5]]:
		var file := FileAccess.open("res://" + item[0], FileAccess.WRITE)
		check(file != null, "save/write fixture")
		if file != null:
			file.store_string(JSON.stringify({"version": item[1], "state": {"coins": 70, "quest": "done"}}))
			file.close()

func reload_save() -> void:
	## Assert process-independent restore and refusal without overwriting source/live state.
	var before := FileAccess.get_file_as_bytes("res://future.json")
	var world := {"coins": 100, "quest": "open"}
	var rejected := SaveEnvelope.stage_file("res://future.json", 2)
	if rejected.ok:
		world = rejected.candidate
	check(not rejected.ok and rejected.reason == "future_version", "save/future refused")
	check(world.coins == 100 and world.quest == "open", "save/live state unchanged")
	check(FileAccess.get_file_as_bytes("res://future.json") == before, "save/original bytes unchanged")
	var current := SaveEnvelope.stage_file("res://current.json", 2)
	check(current.ok, "save/current accepted after restart")
	if current.ok:
		check(current.candidate.coins == 70 and current.candidate.quest == "done", "save/restored values")
	for text in ["{", '{"version":2.5,"state":{}}', '{"version":true,"state":{}}', '{"version":2}']:
		check(not SaveEnvelope.decode(text, 2).ok, "save/invalid rejected")
	check(SaveEnvelope.decode('{"version":1,"state":{}}', 2).reason == "migration_required", "save/no fabricated migration")

func test_resources() -> void:
	## Mutable nested containers separate; intended immutable styles stay shared.
	var template := RuntimeState.new()
	template.counters = {"stats": {"coins": 100}, "quests": ["open"]}
	template.style = StyleBoxFlat.new()
	var first = template.fork_runtime()
	var second = template.fork_runtime()
	first.counters.stats.coins = 3
	first.counters.quests.append("another")
	check(second.counters.stats.coins == 100 and template.counters.stats.coins == 100, "resource/nested state isolated")
	check(second.counters.quests.size() == 1, "resource/nested array isolated")
	check(first.style == second.style and first.style == template.style, "resource/definition intentionally shared")

func test_dialogue() -> void:
	## An unavailable or stale choice must not leave an unresolvable interaction.
	var options: Array[Dictionary] = [{"id": "deliver"}]
	var eligibility := {"ready": true}
	var eligible := func(_id): return eligibility.ready
	var shown := Choices.available_routes(options, eligible)
	check(shown.ok and shown.routes.size() == 1, "dialogue/available choice")
	eligibility.ready = false
	var empty := Choices.available_routes(options, eligible)
	check(empty.ok and empty.routes.size() == 1, "dialogue/zero choices has route")
	if empty.routes.size() == 1:
		check(empty.routes[0].kind == "return", "dialogue/return route")
	check(not Choices.choose("deliver", options, eligible).ok, "dialogue/stale choice refused")
	check(Choices.choose("__return__", options, eligible).ok, "dialogue/can leave")
	eligibility.ready = true
	check(Choices.choose("__return__", options, eligible).ok, "dialogue/shown return survives topic change")

func on_return() -> void:
	## Observe actual Button event handling; tests do not call this handler directly.
	returned = true

func test_gui() -> void:
	## Test layout, aliasing and GUI event dispatch; this is not pixel/OS-device QA.
	root.size = Vector2i(640, 360)
	var screen := Control.new()
	screen.size = Vector2(640, 360)
	root.add_child(screen)
	var margin := MarginContainer.new()
	margin.size = Vector2(240, 100)
	screen.add_child(margin)
	var button := Button.new()
	button.text = "返回官署"
	margin.add_child(button)
	check(LocalTheme.set_padding(margin, 12) == OK, "ui/local margin accepted")
	var theme := Theme.new()
	var shared := StyleBoxFlat.new()
	shared.set_border_width_all(1)
	theme.set_stylebox("panel", "PanelContainer", shared)
	var first := PanelContainer.new()
	var second := PanelContainer.new()
	first.theme = theme
	second.theme = theme
	screen.add_child(first)
	screen.add_child(second)
	check(LocalTheme.set_panel_border(first, 4) == OK, "ui/local border accepted")
	check(shared.border_width_left == 1 and second.get_theme_stylebox("panel").border_width_left == 1,
		"ui/shared theme unchanged")
	check(first.get_theme_stylebox("panel").border_width_left == 4, "ui/local style changed")
	first.hide()
	second.hide()
	button.pressed.connect(on_return)
	await process_frame
	await process_frame
	check(button.position == Vector2(12, 12), "ui/container owns expected inset")
	button.grab_focus()
	check(button.has_focus(), "ui/focus received")
	# Headless has no OS mouse-enter callback. Inject into the viewport explicitly.
	root.notify_mouse_entered()
	var motion := InputEventMouseMotion.new()
	motion.position = button.global_position + button.size / 2
	motion.global_position = motion.position
	root.push_input(motion, true)
	await process_frame
	check(root.gui_get_hovered_control() == button, "ui/mouse hits expected control")
	var press := InputEventMouseButton.new()
	press.button_index = MOUSE_BUTTON_LEFT
	press.pressed = true
	press.button_mask = MOUSE_BUTTON_MASK_LEFT
	press.position = button.global_position + button.size / 2
	press.global_position = press.position
	root.push_input(press, true)
	await process_frame
	var release := press.duplicate() as InputEventMouseButton
	release.pressed = false
	release.button_mask = 0
	root.push_input(release, true)
	await process_frame
	check(returned, "ui/mouse event reaches return button")
	screen.queue_free()
	await process_frame
