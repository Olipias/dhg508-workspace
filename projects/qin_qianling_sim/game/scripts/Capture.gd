extends Node
## Development-only capture walkthrough.  Run with:
##   godot --path game -- --demo
## It saves screenshots under ../artifacts/shots so the layout can be checked
## without a human at the keyboard.

var world: Node
var ui: Node
var out_dir := ""

func _ready() -> void:
	if not ("--demo" in OS.get_cmdline_user_args()):
		return
	out_dir = ProjectSettings.globalize_path("res://").path_join("../artifacts/shots")
	DirAccess.make_dir_recursive_absolute(out_dir)
	world = get_parent().get_node("World")
	ui = get_parent().get_node("UI")
	await get_tree().create_timer(0.8).timeout
	await _shot("01_intro")

	ui._start_game()
	await _wait(0.3)
	await _shot("02_county")

	world.player.position = Vector2(800, 740)
	await _wait(0.2)
	ui.open_document("death_report")
	await _wait(0.3)
	await _shot("03_death_report")
	ui._toggle_original()
	await _wait(0.2)
	await _shot("03b_doc_original")
	ui._toggle_original()
	ui._close_modal()
	await _wait(0.2)

	world.player.position = Vector2(560, 650)
	await _wait(0.2)
	ui.open_dialogue("cheng", JSON.parse_string(FileAccess.get_file_as_string("res://data/npcs.json"))["cheng"])
	await _wait(0.3)
	await _shot("04_dialogue_cheng")
	ui._close_dialogue()
	await _wait(0.2)

	world.player.position = Vector2(430, 1540)
	await _wait(0.3)
	ui.open_dialogue("xiang", JSON.parse_string(FileAccess.get_file_as_string("res://data/npcs.json"))["xiang"])
	await _wait(0.3)
	await _shot("05_dialogue_xiang")
	ui._on_quick("press")
	await _wait(8.0)
	await _shot("05b_dialogue_xiang_ai")
	ui._close_dialogue()
	await _wait(0.2)

	world.player.position = Vector2(2000, 740)
	await _wait(0.3)
	ui.open_document("body_exam")
	await _wait(0.3)
	await _shot("06_body_exam")
	ui._close_modal()
	await _wait(0.2)

	world.player.position = Vector2(1950, 1580)
	await _wait(0.3)
	ui.open_dialogue("you", JSON.parse_string(FileAccess.get_file_as_string("res://data/npcs.json"))["you"])
	await _wait(0.3)
	await _shot("07_dialogue_you")
	ui._close_dialogue()
	await _wait(0.2)

	# pretend the player collected everything, then show the form
	for e in ["e_report", "e_autopsy", "e_ledger", "e_post", "e_wound", "e_wife", "e_register", "e_neighbor"]:
		GameState.add_evidence(e)
	ui._on_submit_pressed()
	await _wait(0.4)
	await _shot("08_submission")
	ui._close_modal()
	await _wait(0.3)
	ui._toggle_evidence()
	await _wait(0.3)
	await _shot("10_evidence")
	ui._toggle_evidence()
	ui._show_end("homicide", [])
	await _wait(0.4)
	await _shot("09_end")
	await _wait(0.2)
	get_tree().quit()

func _wait(t: float) -> void:
	await get_tree().create_timer(t).timeout

func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var path := out_dir.path_join(name + ".png")
	img.save_png(path)
	print("SHOT ", path)
