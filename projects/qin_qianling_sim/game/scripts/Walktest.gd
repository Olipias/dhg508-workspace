extends Node
## Gate/collision smoke test.  Run:
##   godot --path game -- --walktest

var world: Node

func _ready() -> void:
	if not ("--walktest" in OS.get_cmdline_user_args()):
		return
	world = get_parent().get_node("World")
	await get_tree().create_timer(0.3).timeout
	get_parent().get_node("UI")._start_game()
	await _wait(0.2)
	var ok := true
	ok = await _check_gate("县廷南门", Vector2(620, 800), "ui_up", 1.2, func(p): return p.y < 750)
	ok = await _check_gate("都乡东门", Vector2(1100, 1400), "ui_left", 1.2, func(p): return p.x < 1010)
	ok = await _check_gate("仓西门", Vector2(1620, 470), "ui_right", 1.2, func(p): return p.x > 1730)
	ok = await _check_gate("邮亭北门", Vector2(2110, 1080), "ui_down", 1.2, func(p): return p.y > 1150)
	print("WALKTEST ", "PASS" if ok else "FAIL")
	get_tree().quit()

func _wait(t: float) -> void:
	await get_tree().create_timer(t).timeout

func _check_gate(name: String, start: Vector2, action: String, seconds: float, pred: Callable) -> bool:
	world.player.position = start
	await _wait(0.1)
	Input.action_press(action)
	await _wait(seconds)
	Input.action_release(action)
	await _wait(0.1)
	var p: Vector2 = world.player.position
	var ok: bool = pred.call(p)
	print("GATE ", name, " ", "OK" if ok else "BLOCKED", " at ", p)
	return ok
