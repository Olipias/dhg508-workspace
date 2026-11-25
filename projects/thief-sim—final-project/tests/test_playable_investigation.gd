extends "res://tests/test_input_flow.gd"
func _ready() -> void:
	Game.save_path = "/tmp/thief_playable_investigation_save.json"
	main = load("res://src/main.tscn").instantiate() as Main
	add_child(main)
	await _frames(4)
	await _test_computer_investigation()
	Audio.shutdown()
	await _wait(0.4)
	for line in _assertion_log:
		print(line)
	print("PLAYABLE_INVESTIGATION: %d/%d PASSED" % [_checks - _failures, _checks])
	get_tree().quit(0 if _failures == 0 else 1)
