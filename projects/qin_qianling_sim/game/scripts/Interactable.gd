extends Area2D
## A person or a document rack the player can walk up to.

var id: String = ""
var kind: String = "npc"          # npc | object
var data: Dictionary = {}
var world: Node = null
var sprite: Sprite2D
var name_label: Label
var marker: Sprite2D
var base_y: float = 0.0

func setup(p_id: String, p_kind: String, p_data: Dictionary, p_world: Node, pos: Vector2) -> void:
	id = p_id
	kind = p_kind
	data = p_data
	world = p_world
	position = pos
	base_y = pos.y
	z_index = int(pos.y)

	sprite = Sprite2D.new()
	sprite.position = Vector2(0, -32)
	add_child(sprite)

	var tex_name: String = data.get("sprite", "player")
	var tex_path := ""
	if kind == "object":
		tex_path = "res://assets/sprites/%s.png" % tex_name
	else:
		tex_path = "res://assets/sprites/%s_down_0.png" % tex_name
	if ResourceLoader.exists(tex_path):
		sprite.texture = load(tex_path)

	name_label = Label.new()
	name_label.position = Vector2(-60, -92)
	name_label.size = Vector2(120, 24)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 15)
	name_label.add_theme_color_override("font_color", Color(0.93, 0.88, 0.76))
	name_label.add_theme_color_override("font_shadow_color", Color(0.08, 0.06, 0.04, 0.9))
	name_label.add_theme_constant_override("shadow_offset_x", 1)
	name_label.add_theme_constant_override("shadow_offset_y", 2)
	add_child(name_label)

	marker = Sprite2D.new()
	marker.position = Vector2(0, -78)
	marker.texture = load("res://assets/ui/prompt.png")
	marker.visible = false
	add_child(marker)

func set_highlight(on: bool) -> void:
	if marker:
		marker.visible = on

func _process(_delta: float) -> void:
	# a small idle bob keeps the scene from feeling frozen
	if sprite:
		sprite.position.y = -32.0 + sin(Time.get_ticks_msec() / 700.0 + base_y) * 1.2
