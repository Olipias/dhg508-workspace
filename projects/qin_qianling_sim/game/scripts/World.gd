extends Node2D
## Builds the town, the player and every interactable from the JSON data.

const InteractableScript = preload("res://scripts/Interactable.gd")
const PlayerScript = preload("res://scripts/Player.gd")

const OBJECT_DEFS := {
	"death_report": {
		"doc": "death_report", "label": "里典的报案", "sprite": "obj_slips",
		"effect": {"evidence": ["e_report"], "flags": ["read_report"]}
	},
	"law_shelf": {
		"doc": "autopsy_law", "label": "律令架", "sprite": "obj_law",
		"extra": ["homicide_law", "law_xingshu", "glossary"], "effect": {}
	},
	"body": {
		"doc": "body_exam", "label": "丙的尸身", "sprite": "obj_body",
		"effect": {"evidence": ["e_autopsy"], "flags": ["examined_body"]}
	},
	"wound": {
		"doc": "wound_note", "label": "粮袋旁的血", "sprite": "obj_wound",
		"effect": {"evidence": [], "flags": ["saw_wound"]}
	},
	"grain_ledger": {
		"doc": "grain_ledger", "label": "仓里的账", "sprite": "obj_ledger",
		"effect": {"evidence": ["e_ledger"], "flags": ["has_ledger"]}
	},
	"register": {
		"doc": "register", "label": "丙的户籍", "sprite": "obj_ledger",
		"effect": {"evidence": ["e_register"], "flags": ["has_register"]}
	},
	"post_slip": {
		"doc": "post_slip", "label": "送郡的案卷", "sprite": "obj_seal",
		"effect": {"evidence": [], "flags": ["has_qiling_reply"]}
	}
}

const LOCATIONS := [
	{"name": "县廷", "rect": Rect2(160, 150, 880, 630)},
	{"name": "仓", "rect": Rect2(1700, 150, 820, 630)},
	{"name": "都乡", "rect": Rect2(160, 1120, 880, 620)},
	{"name": "邮亭", "rect": Rect2(1700, 1120, 820, 620)},
]

var meta: Dictionary = {}
var locations: Array = LOCATIONS
var npcs_data: Dictionary = {}
var player: CharacterBody2D
var ui: Node
var interactables: Array = []
var current_target: Node = null
var last_location := ""
var started := false

func _ready() -> void:
	var m: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/map_meta.json"))
	if m is Dictionary:
		meta = m
	var n: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/npcs.json"))
	if n is Dictionary:
		npcs_data = n
	_build_background()
	_build_collisions()
	_build_player()
	_build_npcs()
	_build_objects()
	await get_tree().process_frame
	ui = get_node("../UI")
	ui.setup(self)
	_set_location("县廷")

func _build_background() -> void:
	var bg := Sprite2D.new()
	bg.texture = load("res://assets/tiles/map_base.png")
	bg.centered = false
	bg.z_index = -100
	add_child(bg)

func _build_collisions() -> void:
	var body := StaticBody2D.new()
	body.z_index = -50
	for b in meta.get("blockers", []):
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = Vector2(float(b[2]) - float(b[0]), float(b[3]) - float(b[1]))
		shape.shape = rect
		shape.position = Vector2((float(b[0]) + float(b[2])) * 0.5,
			(float(b[1]) + float(b[3])) * 0.5)
		body.add_child(shape)
	add_child(body)

func _build_player() -> void:
	player = PlayerScript.new()
	player.name = "Player"
	var spawn: Array = meta.get("spawn", [600, 680])
	player.position = Vector2(spawn[0], spawn[1])
	player.can_move = false
	add_child(player)

func _build_npcs() -> void:
	for id in npcs_data.keys():
		var data: Dictionary = npcs_data[id]
		var pos_arr: Array = data.get("position", [600, 600])
		var n = InteractableScript.new()
		n.setup(id, "npc", data, self, Vector2(pos_arr[0], pos_arr[1]))
		n.name_label.text = "%s·%s" % [data.get("name", ""), data.get("office", "")]
		add_child(n)
		interactables.append(n)

func _build_objects() -> void:
	var positions: Dictionary = meta.get("objects", {})
	for id in OBJECT_DEFS.keys():
		if not positions.has(id):
			continue
		var def: Dictionary = OBJECT_DEFS[id]
		var pos_arr: Array = positions[id]
		var d := def.duplicate(true)
		d["label"] = def.get("label", id)
		var n = InteractableScript.new()
		n.setup(id, "object", d, self, Vector2(pos_arr[0], pos_arr[1]))
		n.name_label.text = def.get("label", "")
		n.name_label.add_theme_font_size_override("font_size", 13)
		add_child(n)
		interactables.append(n)

func _process(_delta: float) -> void:
	if ui == null or not started:
		return
	_update_location()
	if ui.modal_open:
		_clear_highlight()
		return

	var nearest: Node = null
	var best := 96.0
	for n in interactables:
		var d: float = player.position.distance_to(n.position)
		if d < best:
			best = d
			nearest = n
	if nearest != current_target:
		_clear_highlight()
		current_target = nearest
		if current_target:
			current_target.set_highlight(true)
			ui.show_prompt(current_target)
		else:
			ui.hide_prompt()
	if current_target and Input.is_action_just_pressed("interact"):
		_activate(current_target)

func _clear_highlight() -> void:
	for n in interactables:
		n.set_highlight(false)
	current_target = null

func _activate(target: Node) -> void:
	if target.kind == "npc":
		ui.open_dialogue(target.id, target.data)
	else:
		_apply_effect(target.data.get("effect", {}))
		ui.open_document(target.data.get("doc", ""), target.data.get("extra", []))

func _apply_effect(effect: Dictionary) -> void:
	for e in effect.get("evidence", []):
		GameState.add_evidence(e)
	for f in effect.get("flags", []):
		GameState.set_flag(f)

func _update_location() -> void:
	var loc := "街道"
	for l in LOCATIONS:
		if l["rect"].has_point(player.position):
			loc = l["name"]
			break
	if loc != last_location:
		last_location = loc
		GameState.location = loc
		if ui:
			ui.set_location(loc)

func _set_location(loc: String) -> void:
	last_location = loc
	GameState.location = loc
	if ui:
		ui.set_location(loc)

func start_game() -> void:
	started = true
	player.can_move = true

func lock_player(locked: bool) -> void:
	if player:
		player.can_move = not locked

func current_context() -> Dictionary:
	var present: Array = []
	for n in interactables:
		if n.kind == "npc" and player.position.distance_to(n.position) < 220:
			present.append(n.data.get("name", n.id))
	var ev: Array = []
	for e in GameState.evidence.keys():
		ev.append(e)
	return {
		"location": GameState.location,
		"day": GameState.day,
		"ke": GameState.ke_name(),
		"present": present,
		"evidence": ev,
		"flags": GameState.flags.keys(),
	}
