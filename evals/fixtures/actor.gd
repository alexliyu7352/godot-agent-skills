extends Node
## Scene serialization fixture: exported Node reference plus persistent signal.
@export var target: Button
@export var label: String = "官署"
var presses: int = 0

func on_pressed() -> void:
	## Count calls on this instance, never on the pre-save original.
	presses += 1
