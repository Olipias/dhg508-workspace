extends CanvasLayer
## All UI is built in code so the project has no editor-only .tscn dependencies.
## Palette: ink, bamboo, seal red.

const W := 1280
const H := 720
const INK := Color(0.09, 0.075, 0.06, 0.95)
const INK_SOFT := Color(0.13, 0.11, 0.085, 0.92)
const BORDER := Color(0.52, 0.40, 0.26)
const GOLD := Color(0.88, 0.78, 0.56)
const TEXT := Color(0.91, 0.87, 0.77)
const MUTED := Color(0.66, 0.62, 0.54)
const SEAL := Color(0.66, 0.25, 0.20)

var world: Node
var theme: Theme
var docs: Dictionary = {}
var sources: Dictionary = {}
var chain: Dictionary = {}
var npcs: Dictionary = {}
var form_layer: Control = null

var modal_open := false
var ai_busy := false
var current_npc := ""
var current_data: Dictionary = {}
var last_topic := "free"
var pending_topic := ""
var pending_free_text := ""
var doc_extra: Array = []

# nodes
var top_panel: Panel
var minimap: Control
var map_tex: Texture2D
var loc_label: Label
var time_label: Label
var obj_label: Label
var count_label: Label
var submit_btn: Button
var prompt_panel: Panel
var prompt_label: Label
var dlg_panel: Panel
var name_label: Label
var office_label: Label
var speech: RichTextLabel
var input: LineEdit
var hint_label: Label
var evidence_panel: Panel
var evidence_list: VBoxContainer
var modal_layer: Control
var modal_title: Label
var modal_sub: Label
var modal_body: RichTextLabel
var modal_source: Label
var btn_original: Button
var doc_plain_mode := true
var current_doc_id := ""
var modal_tabs: HBoxContainer
var intro_layer: Control
var end_layer: Control
var toast_label: Label

func _ready() -> void:
	var d: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/documents.json"))
	if d is Dictionary:
		docs = d
	var sr: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/sources.json"))
	if sr is Dictionary:
		sources = sr
	var ch: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/chain.json"))
	if ch is Dictionary:
		chain = ch
	var np: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/npcs.json"))
	if np is Dictionary:
		npcs = np
	_make_theme()
	_build_hud()
	_build_prompt()
	_build_dialogue()
	_build_evidence()
	_build_modal()
	_build_intro()
	_build_end()
	_build_toast()
	GameState.evidence_added.connect(_on_evidence_added)
	GameState.flag_added.connect(_on_flag_added)
	GameState.time_changed.connect(_refresh_hud)
	var ai := get_node("../AI")
	ai.replied.connect(_on_ai_replied)
	ai.failed.connect(_on_ai_failed)

func _make_theme() -> void:
	theme = Theme.new()
	var f := SystemFont.new()
	f.font_names = PackedStringArray(["Noto Serif CJK SC", "Noto Sans CJK SC", "Source Han Serif SC", "SimSun", "Microsoft YaHei", "Noto Serif", "serif"])
	theme.default_font = f
	theme.default_font_size = 18

func _style(bg: Color, border: Color, radius: int = 5, margin: int = 12) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.border_width_left = 2
	s.border_width_right = 2
	s.border_width_top = 2
	s.border_width_bottom = 2
	s.corner_radius_top_left = radius
	s.corner_radius_top_right = radius
	s.corner_radius_bottom_left = radius
	s.corner_radius_bottom_right = radius
	s.content_margin_left = margin
	s.content_margin_right = margin
	s.content_margin_top = margin * 0.5
	s.content_margin_bottom = margin * 0.5
	return s

func _label(parent: Node, text: String, pos: Vector2, size: Vector2, fs: int = 18,
		color: Color = TEXT, align: int = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	l.position = pos
	l.size = size
	l.add_theme_font_size_override("font_size", fs)
	l.add_theme_color_override("font_color", color)
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	parent.add_child(l)
	return l

func _button(parent: Node, text: String, pos: Vector2, size: Vector2,
		cb: Callable, fs: int = 15) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = size
	b.add_theme_font_size_override("font_size", fs)
	b.add_theme_color_override("font_color", TEXT)
	b.add_theme_color_override("font_hover_color", GOLD)
	b.add_theme_stylebox_override("normal", _style(Color(0.20, 0.16, 0.12, 0.96), BORDER, 4, 8))
	b.add_theme_stylebox_override("hover", _style(Color(0.28, 0.22, 0.15, 0.98), GOLD, 4, 8))
	b.add_theme_stylebox_override("pressed", _style(Color(0.16, 0.12, 0.09, 1.0), BORDER, 4, 8))
	b.pressed.connect(cb)
	parent.add_child(b)
	return b

func _build_hud() -> void:
	top_panel = Panel.new()
	top_panel.position = Vector2(0, 0)
	top_panel.size = Vector2(W, 64)
	top_panel.add_theme_stylebox_override("panel", _style(INK, BORDER, 0, 14))
	add_child(top_panel)
	loc_label = _label(top_panel, "迁陵县 · 县廷", Vector2(16, 4), Vector2(280, 56), 24, GOLD)
	time_label = _label(top_panel, "廿六年五月庚子 · 水下三刻", Vector2(296, 4), Vector2(340, 56), 18, TEXT)
	count_label = _label(top_panel, "案卷 0/6", Vector2(636, 4), Vector2(120, 56), 18, TEXT)
	submit_btn = _button(top_panel, "交案卷", Vector2(756, 12), Vector2(115, 40), _on_submit_pressed, 17)
	_button(top_panel, "材料 Tab", Vector2(881, 12), Vector2(110, 40), _toggle_evidence, 16)
	_button(top_panel, "名词", Vector2(1001, 12), Vector2(80, 40), _show_glossary, 16)
	_button(top_panel, "律令", Vector2(1091, 12), Vector2(90, 40), _show_help, 16)
	var obj_bg := Panel.new()
	obj_bg.position = Vector2(0, 64)
	obj_bg.size = Vector2(W, 32)
	obj_bg.add_theme_stylebox_override("panel", _style(Color(0.10, 0.08, 0.06, 0.72), Color(0, 0, 0, 0), 0, 0))
	add_child(obj_bg)
	obj_label = _label(self, "", Vector2(0, 66), Vector2(W, 28), 16, MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	obj_bg.visible = false
	obj_bg.name = "ObjectiveBG"
	top_panel.visible = false
	obj_label.visible = false

	# A schematic minimap: navigation aid, not an archaeological reconstruction.
	minimap = Control.new()
	minimap.position = Vector2(1046, 72)
	minimap.size = Vector2(220, 147)
	minimap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	minimap.visible = false
	add_child(minimap)
	minimap.draw.connect(_draw_minimap)
	map_tex = load("res://assets/tiles/map_base.png")

func _build_prompt() -> void:
	prompt_panel = Panel.new()
	prompt_panel.position = Vector2(410, 590)
	prompt_panel.size = Vector2(460, 44)
	prompt_panel.add_theme_stylebox_override("panel", _style(Color(0.10, 0.08, 0.06, 0.93), BORDER, 22, 12))
	prompt_panel.visible = false
	add_child(prompt_panel)
	prompt_label = _label(prompt_panel, "", Vector2(12, 2), Vector2(436, 40), 16, TEXT, HORIZONTAL_ALIGNMENT_CENTER)

func _build_dialogue() -> void:
	dlg_panel = Panel.new()
	dlg_panel.position = Vector2(36, 446)
	dlg_panel.size = Vector2(1208, 258)
	dlg_panel.add_theme_stylebox_override("panel", _style(INK_SOFT, BORDER, 6, 16))
	dlg_panel.visible = false
	add_child(dlg_panel)

	name_label = _label(dlg_panel, "", Vector2(18, 6), Vector2(500, 32), 23, GOLD)
	office_label = _label(dlg_panel, "", Vector2(18, 38), Vector2(500, 20), 14, MUTED)
	_button(dlg_panel, "×", Vector2(1162, 8), Vector2(32, 32), _close_dialogue, 18)

	speech = RichTextLabel.new()
	speech.position = Vector2(18, 66)
	speech.size = Vector2(1170, 86)
	speech.bbcode_enabled = false
	speech.scroll_active = true
	speech.add_theme_font_size_override("normal_font_size", 18)
	speech.add_theme_color_override("default_color", TEXT)
	dlg_panel.add_child(speech)

	input = LineEdit.new()
	input.position = Vector2(18, 162)
	input.size = Vector2(700, 38)
	input.placeholder_text = "说些什么……"
	input.add_theme_font_size_override("font_size", 16)
	input.add_theme_color_override("font_color", TEXT)
	input.add_theme_color_override("font_placeholder_color", MUTED)
	input.add_theme_stylebox_override("normal", _style(Color(0.16, 0.13, 0.10), BORDER, 4, 10))
	input.add_theme_stylebox_override("focus", _style(Color(0.18, 0.15, 0.11), GOLD, 4, 10))
	input.text_submitted.connect(_on_free_text)
	dlg_panel.add_child(input)

	_button(dlg_panel, "询问", Vector2(730, 162), Vector2(92, 38), _on_quick.bind("ask"))
	_button(dlg_panel, "追问", Vector2(830, 162), Vector2(92, 38), _on_quick.bind("press"))
	_button(dlg_panel, "旁敲侧击", Vector2(930, 162), Vector2(108, 38), _on_quick.bind("sideways"))
	_button(dlg_panel, "考据", Vector2(1046, 162), Vector2(100, 38), _show_current_refs)
	hint_label = _label(dlg_panel, "回车发送 · Esc 关闭 · Tab 材料 · H 名词", Vector2(18, 208), Vector2(760, 22), 13, MUTED)

func _build_evidence() -> void:
	evidence_panel = Panel.new()
	evidence_panel.position = Vector2(958, 232)
	evidence_panel.size = Vector2(304, 472)
	evidence_panel.add_theme_stylebox_override("panel", _style(INK_SOFT, BORDER, 6, 12))
	evidence_panel.visible = false
	add_child(evidence_panel)
	_label(evidence_panel, "案卷 · 已得", Vector2(14, 8), Vector2(200, 28), 19, GOLD)
	_button(evidence_panel, "×", Vector2(264, 6), Vector2(30, 30), _toggle_evidence, 16)
	var sc := ScrollContainer.new()
	sc.position = Vector2(10, 44)
	sc.size = Vector2(284, 416)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	evidence_panel.add_child(sc)
	evidence_list = VBoxContainer.new()
	evidence_list.custom_minimum_size = Vector2(264, 0)
	evidence_list.add_theme_constant_override("separation", 8)
	sc.add_child(evidence_list)

func _build_modal() -> void:
	modal_layer = Control.new()
	modal_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	modal_layer.visible = false
	modal_layer.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(modal_layer)
	var dim := ColorRect.new()
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0.03, 0.025, 0.02, 0.72)
	modal_layer.add_child(dim)
	var frame := TextureRect.new()
	frame.texture = load("res://assets/ui/slips_panel.png")
	frame.position = Vector2(186, 38)
	frame.size = Vector2(908, 644)
	frame.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	frame.stretch_mode = TextureRect.STRETCH_SCALE
	modal_layer.add_child(frame)
	modal_title = _label(modal_layer, "", Vector2(232, 58), Vector2(760, 34), 26, Color(0.20, 0.14, 0.09))
	modal_sub = _label(modal_layer, "", Vector2(232, 94), Vector2(760, 22), 14, Color(0.38, 0.29, 0.19))
	modal_body = RichTextLabel.new()
	modal_body.position = Vector2(232, 128)
	modal_body.size = Vector2(816, 382)
	modal_body.bbcode_enabled = false
	modal_body.scroll_active = true
	modal_body.add_theme_font_size_override("normal_font_size", 18)
	modal_body.add_theme_color_override("default_color", Color(0.17, 0.12, 0.08))
	modal_layer.add_child(modal_body)
	modal_source = _label(modal_layer, "", Vector2(232, 516), Vector2(816, 64), 13, Color(0.34, 0.25, 0.16))
	modal_source.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	modal_source.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	modal_source.visible = false
	modal_tabs = HBoxContainer.new()
	modal_tabs.position = Vector2(232, 596)
	modal_tabs.size = Vector2(640, 40)
	modal_tabs.add_theme_constant_override("separation", 8)
	modal_layer.add_child(modal_tabs)
	btn_original = _button(modal_layer, "看原文", Vector2(700, 596), Vector2(120, 38), _toggle_original)
	_button(modal_layer, "考据", Vector2(830, 596), Vector2(100, 38), _toggle_source)
	_button(modal_layer, "合上", Vector2(950, 596), Vector2(100, 38), _close_modal)

func _build_intro() -> void:
	intro_layer = Control.new()
	intro_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(intro_layer)
	var bg := ColorRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.055, 0.048, 0.04, 1.0)
	intro_layer.add_child(bg)
	_label(intro_layer, "迁陵 · 廿六年五月", Vector2(0, 74), Vector2(W, 64), 44, GOLD, HORIZONTAL_ALIGNMENT_CENTER)
	_label(intro_layer, chain.get("subtitle", "新令史的第一天"), Vector2(0, 138), Vector2(W, 32), 20, MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	var body := _label(intro_layer, chain.get("intro", ""), Vector2(250, 206), Vector2(780, 300), 19, TEXT)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_label(intro_layer, "操作：WASD / 方向键行走　E 交谈或查看　Tab 材料　H 名词　Esc 关闭",
		Vector2(0, 528), Vector2(W, 26), 14, MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	_button(intro_layer, "进门报到", Vector2(540, 584), Vector2(200, 52), _start_game, 20)

func _build_end() -> void:
	end_layer = Control.new()
	end_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	end_layer.visible = false
	add_child(end_layer)
	var bg := ColorRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.045, 0.04, 0.033, 1.0)
	end_layer.add_child(bg)

func _build_toast() -> void:
	toast_label = _label(self, "", Vector2(300, 104), Vector2(680, 30), 16, GOLD, HORIZONTAL_ALIGNMENT_CENTER)
	toast_label.modulate.a = 0.0

func _process(_delta: float) -> void:
	if minimap != null and minimap.visible:
		minimap.queue_redraw()

func _draw_minimap() -> void:
	if world == null or not minimap.visible:
		return
	var mw := 220.0
	var mh := 147.0
	minimap.draw_rect(Rect2(0, 0, mw, mh), Color(0.06, 0.05, 0.04, 0.94))
	minimap.draw_string(theme.default_font, Vector2(8, 14), "迁陵县 · 示意图",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 12, GOLD)
	var x0 := 5.0
	var y0 := 21.0
	var w := 210.0
	var h := 121.0
	if map_tex:
		minimap.draw_texture_rect(map_tex, Rect2(x0, y0, w, h), false, Color(1, 1, 1, 0.86))
	else:
		minimap.draw_rect(Rect2(x0, y0, w, h), Color(0.14, 0.11, 0.08, 1))
	var size: Array = world.meta.get("size", [2880, 1920])
	var sx := w / float(size[0])
	var sy := h / float(size[1])
	for l in world.locations:
		var r: Rect2 = l["rect"]
		var rr := Rect2(x0 + r.position.x * sx, y0 + r.position.y * sy,
			r.size.x * sx, r.size.y * sy)
		minimap.draw_rect(rr, Color(0.88, 0.78, 0.56, 0.07))
		minimap.draw_rect(rr, Color(0.88, 0.78, 0.56, 0.42), false, 1.0)
		minimap.draw_string(theme.default_font, Vector2(rr.position.x + 4, rr.position.y + 13),
			str(l["name"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(0.91, 0.87, 0.77, 0.92))
	for n in world.interactables:
		if n.kind != "npc":
			continue
		var np := Vector2(x0 + n.position.x * sx, y0 + n.position.y * sy)
		minimap.draw_circle(np, 2.2, Color(0.88, 0.78, 0.56, 0.85))
	var pp := Vector2(x0 + world.player.position.x * sx, y0 + world.player.position.y * sy)
	minimap.draw_circle(pp, 5.0, Color(0.66, 0.25, 0.20, 0.35))
	minimap.draw_circle(pp, 3.0, Color(0.82, 0.35, 0.28, 1))
	minimap.draw_circle(pp, 3.0, Color(0.96, 0.90, 0.78, 1), false, 1.0)
	minimap.draw_rect(Rect2(1, 1, mw - 2, mh - 2), BORDER, false, 2.0)

func setup(p_world: Node) -> void:
	world = p_world
	GameState.objective = chain.get("objective", "")
	_refresh_hud()
	_refresh_evidence()

func _start_game() -> void:
	intro_layer.visible = false
	top_panel.visible = true
	minimap.visible = true
	obj_label.visible = true
	get_node("ObjectiveBG").visible = true
	world.start_game()
	GameState.set_flag("briefed")
	_toast("敦狐把一捆竹简推到你面前。")
	_refresh_hud()

func set_location(loc: String) -> void:
	loc_label.text = "迁陵县 · " + loc

func show_prompt(target: Node) -> void:
	if target.kind == "npc":
		prompt_label.text = "E  与 %s·%s 交谈" % [target.data.get("name", ""), target.data.get("office", "")]
	else:
		prompt_label.text = "E  查看 %s" % target.data.get("label", "")
	prompt_panel.visible = true

func hide_prompt() -> void:
	prompt_panel.visible = false

func _refresh_hud() -> void:
	time_label.text = "%s · %s" % [GameState.day, GameState.ke_name()]
	count_label.text = "案卷 %d/%d" % [GameState.required_found(), GameState.required_count()]
	obj_label.text = "事由：" + GameState.objective

func _on_evidence_added(_id: String) -> void:
	_refresh_hud()
	_refresh_evidence()

func _on_flag_added(_id: String) -> void:
	pass

func _refresh_evidence() -> void:
	if evidence_list == null:
		return
	for c in evidence_list.get_children():
		c.queue_free()
	if GameState.evidence.is_empty():
		var l := _label(evidence_list, "尚无。走一遍县廷、都乡、仓、邮亭。", Vector2(0, 0), Vector2(264, 60), 14, MUTED)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		return
	for id in GameState.evidence.keys():
		var d: Dictionary = GameState.evidence_defs.get(id, {})
		var status: String = d.get("status", "inferred")
		var col: Color = GOLD if status == "evidenced" else Color(0.62, 0.72, 0.75)
		var status_cn: String = {"evidenced": "已核", "inferred": "待核", "secondary": "参考"}.get(status, status)
		var l := _label(evidence_list, "【%s】%s" % [status_cn, d.get("title", id)],
			Vector2(0, 0), Vector2(264, 48), 12, col)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(264, 48)
		l.vertical_alignment = VERTICAL_ALIGNMENT_TOP

func _toggle_evidence() -> void:
	if modal_open:
		return
	evidence_panel.visible = not evidence_panel.visible
	if evidence_panel.visible:
		_refresh_evidence()

func _show_glossary() -> void:
	open_document("glossary", [])

func _show_help() -> void:
	open_document("law_cang", ["law_xingshu", "law_fengzhen"])

func _build_evidence_form() -> Control:
	var form := Control.new()
	form.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.04, 0.035, 0.03, 0.97)
	form.add_child(bg)
	var frame := Panel.new()
	frame.position = Vector2(280, 30)
	frame.size = Vector2(720, 660)
	frame.add_theme_stylebox_override("panel", _style(INK, BORDER, 8, 22))
	form.add_child(frame)
	_label(frame, "交案卷", Vector2(24, 12), Vector2(400, 34), 26, GOLD)
	_label(frame, "守丞先看四样：报案、验尸、账、送郡时间。再问你：这条命，算哪一种死？", Vector2(24, 48), Vector2(660, 24), 14, MUTED)

	var y := 84
	var all_ids: Array = []
	for id in chain.get("required", []): all_ids.append(id)
	for id in chain.get("optional", []): all_ids.append(id)
	for id in all_ids:
		var d: Dictionary = GameState.evidence_defs.get(id, {})
		var must: bool = id in chain.get("required", [])
		var cb := CheckBox.new()
		cb.position = Vector2(24, y)
		cb.size = Vector2(650, 28)
		cb.text = "%s  [%s]%s" % [d.get("title", id), {"evidenced": "已核", "inferred": "待核"}.get(d.get("status", ""), d.get("status", "")), "（必须）" if must else "（可选）"]
		cb.add_theme_font_size_override("font_size", 14)
		cb.add_theme_color_override("font_color", TEXT)
		cb.button_pressed = GameState.has_evidence(id)
		cb.disabled = not GameState.has_evidence(id)
		frame.add_child(cb)
		y += 28

	_label(frame, "怎么定这条命？", Vector2(24, y + 6), Vector2(200, 30), 16, GOLD)
	var verdict := OptionButton.new()
	verdict.position = Vector2(210, y + 2)
	verdict.size = Vector2(360, 36)
	verdict.add_item("自杀（上吊）")
	verdict.add_item("贼杀（故意杀人）")
	verdict.add_item("斗杀（斗殴杀人）")
	verdict.add_item("死难审（验不明白）")
	verdict.selected = 0
	verdict.add_theme_font_size_override("font_size", 15)
	frame.add_child(verdict)
	y += 48

	_label(frame, "要连累谁？（可以不写）", Vector2(24, y), Vector2(300, 26), 16, GOLD)
	var blame_lidian := CheckBox.new()
	blame_lidian.text = "把里典/四邻写进案卷（知情不报）"
	blame_lidian.position = Vector2(24, y + 28)
	blame_lidian.size = Vector2(500, 28)
	blame_lidian.add_theme_font_size_override("font_size", 14)
	blame_lidian.add_theme_color_override("font_color", TEXT)
	frame.add_child(blame_lidian)
	var blame_cang := CheckBox.new()
	blame_cang.text = "把仓啬夫写进案卷（账目不清）"
	blame_cang.position = Vector2(24, y + 54)
	blame_cang.size = Vector2(500, 28)
	blame_cang.add_theme_font_size_override("font_size", 14)
	blame_cang.add_theme_color_override("font_color", TEXT)
	frame.add_child(blame_cang)
	y += 88

	_label(frame, "送郡时间", Vector2(24, y), Vector2(200, 26), 16, GOLD)
	var opt1 := CheckBox.new()
	opt1.text = "照实写：水下三刻"
	opt1.position = Vector2(24, y + 28)
	opt1.size = Vector2(300, 28)
	opt1.button_pressed = true
	opt1.add_theme_font_size_override("font_size", 14)
	opt1.add_theme_color_override("font_color", TEXT)
	frame.add_child(opt1)
	var opt2 := CheckBox.new()
	opt2.text = "听邮人的：写早一刻"
	opt2.position = Vector2(330, y + 28)
	opt2.size = Vector2(320, 28)
	opt2.add_theme_font_size_override("font_size", 14)
	opt2.add_theme_color_override("font_color", TEXT)
	frame.add_child(opt2)
	opt1.toggled.connect(func(on):
		if on: opt2.button_pressed = false
	)
	opt2.toggled.connect(func(on):
		if on: opt1.button_pressed = false
	)

	var submit := _button(frame, "交  上", Vector2(240, 590), Vector2(180, 44), func(): pass, 19)
	submit.pressed.connect(func():
		var missing: Array = []
		for id in chain.get("required", []):
			if not GameState.has_evidence(id):
				missing.append(id)
		if not missing.is_empty():
			_show_end("rejected", missing)
			return
		if opt2.button_pressed:
			_show_end("falsified_post", [])
			return
		var note := ""
		if blame_lidian.button_pressed:
			note += "你把里典和四邻写进了案卷。"
		if blame_cang.button_pressed:
			note += "你把仓啬夫的账翻了出来。"
		var v := verdict.selected
		var has_wound := GameState.has_evidence("e_wound")
		var has_wife := GameState.has_evidence("e_wife")
		var has_neighbor := GameState.has_evidence("e_neighbor")
		var has_ledger := GameState.has_evidence("e_ledger")
		if v == 0:
			if has_wound or has_wife:
				_show_end("falsified_autopsy", [], note)
			else:
				_show_end("suicide", [], note)
		elif v == 1:
			if has_wound and (has_wife or has_ledger):
				_show_end("homicide", [], note)
			else:
				_show_end("rejected", [], str(chain.get("verdict_reject", {}).get("homicide", "")))
		elif v == 2:
			if has_neighbor:
				_show_end("fight", [], note)
			else:
				_show_end("rejected", [], str(chain.get("verdict_reject", {}).get("fight", "")))
		else:
			if has_wound:
				_show_end("uncertain", [], note)
			else:
				_show_end("rejected", [], str(chain.get("verdict_reject", {}).get("uncertain", "")))
	)
	_button(frame, "再想想", Vector2(440, 590), Vector2(150, 44), func(): _close_modal(), 16)
	return form

func _on_submit_pressed() -> void:
	if modal_open:
		return
	if form_layer != null:
		form_layer.queue_free()
	var form := _build_evidence_form()
	form_layer = form
	add_child(form)
	modal_layer.visible = false
	modal_open = true
	world.lock_player(true)
	modal_title.text = ""
	modal_sub.text = ""
	modal_body.text = ""
	modal_source.text = ""
	for c in modal_tabs.get_children():
		c.queue_free()

func open_dialogue(npc_id: String, data: Dictionary) -> void:
	if modal_open:
		return
	current_npc = npc_id
	current_data = data
	last_topic = "free"
	dlg_panel.visible = true
	modal_open = true
	world.lock_player(true)
	name_label.text = "%s · %s" % [data.get("name", ""), data.get("office", "")]
	office_label.text = "迁陵县 · " + GameState.location
	speech.text = data.get("greeting", "……")
	hint_label.text = "回车发送 · Esc 关闭 · Tab 材料 · H 名词"
	input.text = ""
	input.grab_focus()
	toast_label.modulate.a = 0.0
	GameState.advance(1)
	_refresh_hud()

func _close_dialogue() -> void:
	dlg_panel.visible = false
	modal_open = false
	world.lock_player(false)
	ai_busy = false
	pending_topic = ""
	pending_free_text = ""
	input.release_focus()

func _on_quick(topic: String) -> void:
	if ai_busy or not dlg_panel.visible:
		return
	last_topic = topic
	pending_topic = topic
	var text := ""
	match topic:
		"ask":
			text = "我直接问你：这事你到底知道多少？"
		"press":
			text = "我追问你：文书和规矩都在这儿，你照实说，别绕。"
		"sideways":
			text = "我不直接问，先从旁边打听一句。"
	_ask_ai(text)

func _on_free_text(text: String) -> void:
	if ai_busy or text.strip_edges() == "":
		return
	last_topic = "free"
	pending_free_text = text
	_ask_ai(text)
	input.text = ""

func _apply_pending_answer() -> void:
	if not dlg_panel.visible:
		return
	if pending_topic != "":
		var t := pending_topic
		pending_topic = ""
		var added: Array = _apply_topic(t)
		if not added.is_empty():
			var titles: Array = []
			for id in added:
				var d: Dictionary = GameState.evidence_defs.get(id, {})
				titles.append(d.get("title", id))
			speech.text += "\n\n〔记入案卷〕" + "；".join(titles)
	if pending_free_text != "":
		var ft := pending_free_text
		pending_free_text = ""
		_apply_free_text(ft)

func _apply_topic(topic: String) -> Array:
	var t: Dictionary = current_data.get("topics", {}).get(topic, {})
	var added: Array = []
	for e in t.get("evidence", []):
		if not GameState.has_evidence(e):
			added.append(e)
		GameState.add_evidence(e)
	for f in t.get("flags", []):
		GameState.set_flag(f)
	return added

func _apply_free_text(text: String) -> void:
	var t := text
	if current_npc == "xiang":
		if "年籍" in t or "年数" in t:
			GameState.add_evidence("e_age_missing")
		if "亡" in t or "死" in t:
			GameState.add_evidence("e_escape")
		if "户" in t or "名单" in t or "十七" in t:
			GameState.add_evidence("e_17")
	elif current_npc == "lidian":
		if "亡" in t or "灶" in t:
			GameState.add_evidence("e_escape")
		if "高" in t or "五尺" in t or "作" in t or "名籍" in t or "底册" in t:
			GameState.add_evidence("e_grain")
	elif current_npc == "cang":
		if "稟" in t or "粮" in t or "底册" in t or "标准" in t or "不备" in t:
			GameState.add_evidence("e_grain")
	elif current_npc == "you":
		if "时" in t or "刻" in t or "封" in t or "邮" in t:
			GameState.add_evidence("e_post")
	elif current_npc == "cheng":
		if "簿" in t or "驳" in t or "律" in t:
			GameState.set_flag("knows_criteria")

func _ask_ai(text: String) -> void:
	ai_busy = true
	speech.text = "……"
	input.editable = false
	var ctx: Dictionary = world.current_context()
	ctx["npc_id"] = current_npc
	get_node("../AI").ask(current_npc, text, ctx)

func _on_ai_replied(npc_id: String, text: String, refs: Array) -> void:
	if npc_id != current_npc:
		return
	ai_busy = false
	input.editable = true
	input.grab_focus()
	speech.text = text
	_apply_pending_answer()
	hint_label.text = "回车发送 · Esc 关闭 · Tab 材料 · H 名词"
	GameState.ai_calls += 1

func _on_ai_failed(npc_id: String) -> void:
	if npc_id != current_npc:
		return
	ai_busy = false
	input.editable = true
	var fb: Dictionary = current_data.get("fallback", {})
	speech.text = fb.get(last_topic, fb.get("free", "……"))
	_apply_pending_answer()
	hint_label.text = "（此句为脚本回退：本地模型服务未响应）"

func _show_current_refs() -> void:
	var refs: Array = current_data.get("knowledge", [])
	var lines: Array = []
	for k in refs:
		var sid: String = k.get("source", "")
		var src: Dictionary = sources.get(sid, {})
		lines.append("%s · %s" % [sid, src.get("title", k.get("fact", ""))])
	hint_label.text = " ▪ ".join(lines)

func _show_refs(refs: Array) -> void:
	if refs.is_empty():
		return
	hint_label.text = "依据：" + ", ".join(refs)

func open_document(doc_id: String, extra: Array = []) -> void:
	if not docs.has(doc_id):
		return
	if dlg_panel != null and dlg_panel.visible:
		_close_dialogue()
	doc_extra = extra
	current_doc_id = doc_id
	doc_plain_mode = true
	if btn_original:
		btn_original.text = "看原文"
	modal_open = true
	toast_label.modulate.a = 0.0
	modal_layer.visible = true
	world.lock_player(true)
	_display_doc(doc_id)
	for c in modal_tabs.get_children():
		c.queue_free()
	var ids: Array = [doc_id] + extra
	for id in ids:
		if not docs.has(id):
			continue
		var b := _button(modal_tabs, docs[id].get("title", id).substr(0, 10),
			Vector2(0, 0), Vector2(150, 34), _display_doc.bind(id), 13)
		b.custom_minimum_size = Vector2(150, 34)
	modal_title.visible = true
	modal_sub.visible = true
	modal_source.visible = false

func _display_doc(doc_id: String) -> void:
	if not docs.has(doc_id):
		return
	current_doc_id = doc_id
	var d: Dictionary = docs[doc_id]
	modal_title.text = d.get("title", "")
	modal_sub.text = d.get("subtitle", "")
	modal_body.text = d.get("plain", d.get("body", "")) if doc_plain_mode else d.get("body", "")
	var status: String = d.get("status", "")
	var status_cn: String = {"evidenced": "有据", "inferred": "推拟", "secondary": "二手研究"}.get(status, status)
	var sid: String = d.get("source", "")
	var src: Dictionary = {}
	src = sources.get(sid, {})
	modal_source.text = "考据 · %s · %s\n%s\n%s" % [status_cn, src.get("title", sid), d.get("note", ""), src.get("url", "")]
	modal_body.scroll_to_line(0)
	modal_title.visible = true
	modal_sub.visible = true
	modal_source.visible = false

func _toggle_original() -> void:
	doc_plain_mode = not doc_plain_mode
	if btn_original:
		btn_original.text = "看原文" if doc_plain_mode else "看人话"
	if current_doc_id != "":
		_display_doc(current_doc_id)

func _toggle_source() -> void:
	modal_source.visible = not modal_source.visible

func _close_modal() -> void:
	# close the evidence form first if it is open
	for c in modal_layer.get_children():
		if c is Control and c.get_script() == null and c.get_child_count() > 0:
			pass
	if form_layer != null:
		form_layer.queue_free()
		form_layer = null
	modal_layer.visible = false
	modal_open = false
	world.lock_player(false)

func _show_end(kind: String, missing: Array, extra_msg: String = "") -> void:
	if form_layer != null:
		form_layer.queue_free()
		form_layer = null
	modal_layer.visible = false
	top_panel.visible = false
	minimap.visible = false
	obj_label.visible = false
	get_node("ObjectiveBG").visible = false
	modal_open = true
	world.lock_player(true)
	GameState.submitted = true
	GameState.result = kind
	var endings: Dictionary = chain.get("endings", {})
	var e: Dictionary = endings.get(kind, {})
	for c in end_layer.get_children():
		if c is Control and c != end_layer.get_child(0):
			c.queue_free()
	_label(end_layer, e.get("title", kind), Vector2(0, 66), Vector2(W, 56), 40, GOLD, HORIZONTAL_ALIGNMENT_CENTER)
	var body_text: String = e.get("body", "")
	if kind != "rejected" and extra_msg != "":
		body_text += "\n\n" + extra_msg
	var body := _label(end_layer, body_text, Vector2(220, 140), Vector2(840, 310), 19, TEXT)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	var extra := ""
	if kind == "rejected":
		if not missing.is_empty():
			for id in missing:
				extra += "· " + str(chain.get("reject", {}).get(id, id)) + "\n"
		elif extra_msg != "":
			extra = extra_msg
		var ml := _label(end_layer, extra, Vector2(250, 460), Vector2(780, 70), 15, Color(0.86, 0.66, 0.55))
		ml.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ml.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	var lesson := _label(end_layer, "【案后记】" + str(chain.get("lesson", "")), Vector2(180, 540), Vector2(920, 80), 14, MUTED)
	lesson.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	lesson.custom_minimum_size = Vector2(920, 80)
	lesson.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_button(end_layer, "再值一天班", Vector2(540, 640), Vector2(200, 46), func(): get_tree().reload_current_scene(), 18)
	end_layer.visible = true

func _on_evidence_added_toast(id: String) -> void:
	pass

func _toast(text: String) -> void:
	toast_label.text = text
	toast_label.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_interval(2.4)
	tw.tween_property(toast_label, "modulate:a", 0.0, 0.8)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_evidence"):
		_toggle_evidence()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("glossary"):
		if not modal_open and world != null and world.started:
			_show_glossary()
		get_viewport().set_input_as_handled()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		if modal_layer.visible:
			_close_modal()
		elif dlg_panel.visible:
			_close_dialogue()

