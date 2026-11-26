extends CharacterBody2D
## 令史喜.  Top-down walker with a four-direction sprite and a small camera.

const SPEED := 235.0
const SPRITE_NAMES := ["down", "up", "left", "right"]

var sprite: Sprite2D
var facing: String = "down"
var frame: int = 0
var anim_time: float = 0.0
var can_move: bool = true
var map_size := Vector2(2880, 1920)

func _ready() -> void:
	sprite = Sprite2D.new()
	sprite.position = Vector2(0, -32)
	add_child(sprite)

	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 9.0
	shape.shape = circle
	shape.position = Vector2(0, -6)
	add_child(shape)

	var cam := Camera2D.new()
	cam.position = Vector2(0, -60)
	cam.zoom = Vector2(1.25, 1.25)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = int(map_size.x)
	cam.limit_bottom = int(map_size.y)
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 6.0
	add_child(cam)
	_update_texture()

func _physics_process(delta: float) -> void:
	var dir := Vector2.ZERO
	if can_move:
		dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = dir * SPEED
	move_and_slide()
	position.x = clamp(position.x, 20, map_size.x - 20)
	position.y = clamp(position.y, 20, map_size.y - 20)

	if dir.length() > 0.1:
		if abs(dir.x) > abs(dir.y):
			facing = "right" if dir.x > 0 else "left"
		else:
			facing = "down" if dir.y > 0 else "up"
		anim_time += delta
		if anim_time > 0.16:
			anim_time = 0.0
			frame = 1 - frame
			_update_texture()
	else:
		frame = 0
		_update_texture()

func _update_texture() -> void:
	var path := "res://assets/sprites/player_%s_%d.png" % [facing, frame]
	if ResourceLoader.exists(path):
		sprite.texture = load(path)
