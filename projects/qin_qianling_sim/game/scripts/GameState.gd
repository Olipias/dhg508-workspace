extends Node
## Global world state.  The model never writes here directly: every flag and
## every piece of evidence is set by the Godot world after an interaction.

signal evidence_added(id: String)
signal flag_added(id: String)
signal time_changed

var flags: Dictionary = {}
var evidence: Dictionary = {}
var evidence_defs: Dictionary = {}
var day: String = "廿六年五月庚子"
var ke: int = 3
var location: String = "县廷"
var objective: String = ""
var chain_data: Dictionary = {}
var submitted: bool = false
var result: String = ""
var ai_calls: int = 0
var ai_tokens_in: int = 0
var ai_tokens_out: int = 0

func _ready() -> void:
	_ensure_actions()
	var txt := FileAccess.get_file_as_string("res://data/evidence.json")
	var parsed: Variant = JSON.parse_string(txt)
	if parsed is Dictionary:
		evidence_defs = parsed
	var chain: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/chain.json"))
	if chain is Dictionary:
		chain_data = chain
		objective = chain.get("objective", "")

func _ensure_actions() -> void:
	if not InputMap.has_action("interact"):
		InputMap.add_action("interact")
		for k in [KEY_E, KEY_SPACE]:
			var ev := InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event("interact", ev)
	if not InputMap.has_action("toggle_evidence"):
		InputMap.add_action("toggle_evidence")
		var ev2 := InputEventKey.new()
		ev2.physical_keycode = KEY_TAB
		InputMap.action_add_event("toggle_evidence", ev2)
	if not InputMap.has_action("glossary"):
		InputMap.add_action("glossary")
		var ev3 := InputEventKey.new()
		ev3.physical_keycode = KEY_H
		InputMap.action_add_event("glossary", ev3)

func reset() -> void:
	flags.clear()
	evidence.clear()
	ke = 3
	location = "县廷"
	submitted = false
	result = ""
	ai_calls = 0
	ai_tokens_in = 0
	ai_tokens_out = 0

func set_flag(id: String) -> void:
	if id == "" or flags.has(id):
		return
	flags[id] = true
	flag_added.emit(id)

func has_flag(id: String) -> bool:
	return flags.has(id)

func add_evidence(id: String) -> void:
	if id == "" or evidence.has(id):
		return
	evidence[id] = true
	evidence_added.emit(id)

func has_evidence(id: String) -> bool:
	return evidence.has(id)

func advance(steps: int = 1) -> void:
	ke += steps
	if ke > 11:
		ke = 1
	time_changed.emit()

func ke_name() -> String:
	return "水下%s刻" % ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一"][clamp(ke - 1, 0, 10)]

func evidence_count() -> int:
	return evidence.size()

func required_count() -> int:
	return chain_data.get("required", []).size()

func required_found() -> int:
	var n := 0
	for id in chain_data.get("required", []):
		if evidence.has(id):
			n += 1
	return n
