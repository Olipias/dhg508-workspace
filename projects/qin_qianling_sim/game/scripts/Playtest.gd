extends Node
## End-to-end logic test.  Run:
##   godot --path game -- --playtest
## It walks the player to each node (by teleporting to a legal spot), opens the
## interactable through the world's own nearest-target path, presses the quick
## dialogue options, and checks that all six evidence items can be collected.

var world: Node
var ui: Node
var ok := true
var npcs: Dictionary

func _ready() -> void:
	if not ("--playtest" in OS.get_cmdline_user_args()):
		return
	world = get_parent().get_node("World")
	ui = get_parent().get_node("UI")
	npcs = JSON.parse_string(FileAccess.get_file_as_string("res://data/npcs.json"))
	await get_tree().create_timer(0.3).timeout
	ui._start_game()
	await _wait(0.2)

	await _use_object("death_report", Vector2(800, 740), "e_report")
	await _talk("cheng", Vector2(480, 730))
	await _talk("cang", Vector2(1880, 660), ["press", "sideways"])
	await _use_object("body", Vector2(2000, 740), "e_autopsy")
	await _use_object("wound", Vector2(2150, 740), "e_wound")
	await _use_object("grain_ledger", Vector2(2300, 740), "e_ledger")
	await _talk("xiang", Vector2(430, 1540), ["ask", "press", "sideways"])
	await _use_object("register", Vector2(650, 1580), "e_register")
	await _talk("lidian", Vector2(760, 1680), ["ask", "press"])
	await _talk("wife", Vector2(520, 1660), ["ask", "press"])
	await _talk("you", Vector2(2000, 1620), ["press"])
	await _use_object("post_slip", Vector2(2300, 1560), "e_post")

	var required: Array = ["e_report", "e_autopsy", "e_ledger", "e_post", "e_wound", "e_wife", "e_register", "e_neighbor"]
	for e in required:
		if not GameState.has_evidence(e):
			ok = false
			print("MISSING ", e)
	print("PLAYTEST ", "PASS" if ok else "FAIL", " evidence=", GameState.evidence.keys())
	# Form smoke test: default verdict is suicide; with bruise/wife this must be "falsified_autopsy".
	ui._on_submit_pressed()
	await _wait(0.4)
	print("FORM OPEN ", ui.form_layer != null)
	var btn := _find_button(ui.form_layer, "交  上")
	if btn != null:
		btn.pressed.emit()
		await _wait(0.4)
		print("FORM RESULT ", GameState.result)
	else:
		print("FORM RESULT no-submit-button")
	await _wait(0.2)
	get_tree().quit()

func _find_button(node: Node, text: String) -> Button:
	if node is Button and (node as Button).text == text:
		return node
	for c in node.get_children():
		var found := _find_button(c, text)
		if found != null:
			return found
	return null

func _wait(t: float) -> void:
	await get_tree().create_timer(t).timeout

func _talk(id: String, pos: Vector2, topics: Array = []) -> void:
	world.player.position = pos
	await _wait(0.25)
	if world.current_target == null or world.current_target.id != id:
		ok = false
		print("NO TARGET ", id, " got ", world.current_target.id if world.current_target else "null")
		return
	world._activate(world.current_target)
	await _wait(0.3)
	for t in topics:
		ui._on_quick(t)
		await _wait_ai()
	ui._close_dialogue()
	await _wait(0.2)

func _wait_ai() -> void:
	var t := 0.0
	while ui.ai_busy and t < 25.0:
		await get_tree().create_timer(0.2).timeout
		t += 0.2
	await _wait(0.2)

func _use_object(id: String, pos: Vector2, evidence: String) -> void:
	world.player.position = pos
	await _wait(0.25)
	if world.current_target == null or world.current_target.id != id:
		ok = false
		print("NO TARGET ", id, " got ", world.current_target.id if world.current_target else "null")
		return
	world._activate(world.current_target)
	await _wait(0.3)
	if not GameState.has_evidence(evidence):
		ok = false
		print("NO EVIDENCE ", evidence)
	ui._close_modal()
	await _wait(0.2)
