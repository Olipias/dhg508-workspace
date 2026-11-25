class_name InvestigationBoard
extends Control
## 材料在左、连线与判断在右；拖动预览不占布局，关系区可滚动。
signal feedback_changed(text: String)
const POS_KEY := "inv_board_positions" # 保留旧布局字段，不删除旧档内容。
const LINK_KEY := "inv_board_links"
var target_id := "ram_zun"
var _central: PanelContainer
var _central_text: Label
var _cards: Dictionary = {}
var _linked: Array[String] = []
var _drag_id := ""
var _drag_preview: Label
var _relation_box: VBoxContainer
var _feedback: Label
var _materials: VBoxContainer
var _question: OptionButton
var _detail: RichTextLabel

func _ready() -> void:
	custom_minimum_size = Vector2(0, 194)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	clip_contents = true
	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.add_theme_constant_override("separation", 10)
	add_child(row)
	var left := VBoxContainer.new()
	left.custom_minimum_size.x = 190
	row.add_child(left)
	var guide := Label.new()
	guide.text = "材料：点一下阅读，按住拖动"
	guide.add_theme_font_size_override("font_size", 10)
	left.add_child(guide)
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	left.add_child(scroll)
	_materials = VBoxContainer.new()
	_materials.mouse_filter = Control.MOUSE_FILTER_PASS
	_materials.add_theme_constant_override("separation", 2)
	_materials.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_materials)
	_detail = RichTextLabel.new()
	_detail.custom_minimum_size = Vector2(180, 40)
	_detail.add_theme_font_size_override("normal_font_size", 10)
	left.add_child(_detail)
	var right := VBoxContainer.new()
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.add_theme_constant_override("separation", 4)
	row.add_child(right)
	_central = PanelContainer.new()
	_central.name = "CentralArchive"
	_central.custom_minimum_size.y = 48
	var drop_style := StyleBoxFlat.new()
	drop_style.bg_color = Color("23221c")
	drop_style.border_color = Color("bc974b")
	drop_style.set_border_width_all(2)
	drop_style.set_content_margin_all(4)
	_central.add_theme_stylebox_override("panel", drop_style)
	right.add_child(_central)
	_central_text = Label.new()
	_central_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_central_text.add_theme_font_size_override("font_size", 10)
	_central.add_child(_central_text)
	_question = OptionButton.new()
	_question.name = "Question"
	_question.clip_text = true
	_question.add_theme_font_size_override("font_size", 11)
	_question.item_selected.connect(func(_i: int) -> void:
		_rebuild_relation_options("")
		_queue_feedback(_guidance_text())
	)
	right.add_child(_question)
	var relations_scroll := ScrollContainer.new()
	relations_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	relations_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	right.add_child(relations_scroll)
	_relation_box = VBoxContainer.new()
	_relation_box.name = "RelationBox"
	_relation_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	relations_scroll.add_child(_relation_box)
	_feedback = Label.new()
	_feedback.name = "Feedback"
	_feedback.custom_minimum_size.y = 40
	_feedback.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_feedback.add_theme_font_size_override("font_size", 10)
	right.add_child(_feedback)
	_drag_preview = Label.new()
	_drag_preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_drag_preview.add_theme_font_size_override("font_size", 11)
	_drag_preview.visible = false
	add_child(_drag_preview)

func set_target(id: String) -> void:
	if not Investigation.TARGETS.has(id):
		return
	target_id = id
	_drag_id = ""
	_drag_preview.hide()
	for child in _materials.get_children():
		child.free()
	_cards.clear()
	_linked.clear()
	_question.clear()
	for q in Investigation.questions(id):
		_question.add_item(_question_title(q["id"]))
	for mid in Investigation.unlocked_materials(id):
		_make_card(String(mid), Investigation.material(id, mid))
	for key in _saved_links():
		var prefix := id + ":"
		var mid: String = key.trim_prefix(prefix)
		if key.begins_with(prefix) and _cards.has(mid) and not _linked.has(mid):
			_linked.append(mid)
	_question.select(1 if Investigation.is_question_answered(id, "features") else 0)
	_detail.text = "点左侧材料读正文；绿色表示已连入。\n必须点选结论，只有连线不算完成。"
	_update_conclusions()
	_rebuild_relation_options("")
	_queue_feedback(_guidance_text())

func _make_card(mid: String, mat: Dictionary) -> void:
	var card := PanelContainer.new()
	card.name = "Card_" + mid
	card.custom_minimum_size = Vector2(175, 26)
	card.mouse_filter = Control.MOUSE_FILTER_PASS
	card.tooltip_text = String(mat.get("body", ""))
	var label := Label.new()
	label.text = String(mat.get("title", mid))
	label.custom_minimum_size.x = 170
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 10)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.add_child(label)
	_materials.add_child(card)
	_cards[mid] = card
	card.gui_input.connect(func(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed:
			if event.button_index == MOUSE_BUTTON_LEFT:
				_drag_id = mid
				_detail.text = String(mat.get("body", ""))
				_drag_preview.text = String(mat.get("title", mid))
				_drag_preview.position = get_local_mouse_position() + Vector2(8, 8)
				_drag_preview.show()
				card.accept_event()
			elif event.button_index == MOUSE_BUTTON_RIGHT:
				_unlink_material(mid)
				card.accept_event()
	)

func _input(event: InputEvent) -> void:
	if _drag_id.is_empty() or not is_visible_in_tree():
		return
	if event is InputEventMouseMotion:
		_drag_preview.position = get_global_transform().affine_inverse() * event.position + Vector2(8, 8)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and not event.pressed:
		var mid := _drag_id
		_drag_id = ""
		_drag_preview.hide()
		if _central.get_global_rect().has_point(event.position):
			_link_material(mid)
		else:
			_queue_feedback("还没连上：按住左侧材料，拖进右上方“材料放这里”框再松开。")
		get_viewport().set_input_as_handled()

func _link_material(mid: String) -> void:
	if not _cards.has(mid):
		return
	if not _linked.has(mid):
		_linked.append(mid)
	_save_links()
	var answers: Array = Investigation.material(target_id, mid).get("answers", [])
	for i in Investigation.questions(target_id).size():
		if Investigation.questions(target_id)[i]["id"] in answers:
			_question.select(i)
			break
	_rebuild_relation_options("")
	_update_conclusions()
	_queue_feedback(_guidance_text())

func _unlink_material(mid: String) -> void:
	_linked.erase(mid)
	_save_links()
	_update_conclusions()
	_queue_feedback("已断开材料。" + _guidance_text())

func _rebuild_relation_options(_mid: String) -> void:
	for child in _relation_box.get_children():
		child.free()
	if _question.selected < 0:
		return
	var qid: String = Investigation.questions(target_id)[_question.selected]["id"]
	var rels := Investigation.relations(target_id, qid)
	for i in rels.size():
		var button := Button.new()
		var answer := String(rels[i]["text"])
		var chunks: Array[String] = []
		for at in range(0, answer.length(), 26):
			chunks.append(answer.substr(at, 26))
		button.text = "\n".join(chunks)
		button.tooltip_text = button.text
		button.clip_text = true
		button.custom_minimum_size.y = 12 + 14 * max(1, chunks.size())
		button.add_theme_font_size_override("font_size", 10)
		button.pressed.connect(_on_relation_pressed.bind(qid, i))
		_relation_box.add_child(button)

func _on_relation_pressed(qid: String, index: int) -> void:
	var result := Investigation.record_relation(target_id, qid, index, _linked)
	if result["ok"]:
		if qid == "features":
			_question.select(1)
		_rebuild_relation_options.call_deferred("") # 等当前按钮的pressed信号返回后再替换选项。
		_update_conclusions()
		_queue_feedback(("外貌已确认。" if qid == "features" else "") + _guidance_text())
	else:
		_queue_feedback(String(result["feedback"]) + "\n" + _guidance_text())

func _queue_feedback(text: String) -> void:
	_feedback.text = text
	feedback_changed.emit(text)

func _update_conclusions() -> void:
	var features := Investigation.is_question_answered(target_id, "features")
	var area := Investigation.is_question_answered(target_id, "area")
	for i in _question.item_count:
		_question.set_item_text(i, _question_title(Investigation.questions(target_id)[i]["id"]))
	_central_text.text = "出发准备：外貌%s｜展区%s（%d/2）\n材料放这里：按住左键拖入 → 松开连线" % [
		"✓" if features else "□", "✓" if area else "□", int(features) + int(area)]
	for mid in _cards:
		_cards[mid].modulate = Color(0.65, 0.95, 0.75) if _linked.has(mid) else Color.WHITE
	queue_redraw()

func _question_title(qid: String) -> String:
	var names := {"features": "第1步：确认外貌", "area": "第2步：确认本次展区", "spot": "可选：进馆后核对柜号"}
	return String(names.get(qid, qid)) + (" ✓" if Investigation.is_question_answered(target_id, qid) else "")

func _guidance_text() -> String:
	if Game.investigation_ready(target_id):
		return "两项已完成！Esc关闭电脑 → P手机「委托」准备出发 → 到房门按E。柜号可进馆后再查。"
	if _question.selected < 0:
		return "先确认外貌，再确认本次展区；下拉框可以切换问题。"
	var q: Dictionary = Investigation.questions(target_id)[_question.selected]
	var qid := String(q["id"])
	if qid == "spot":
		return "这是进馆后的可选核对。首次出发只需要完成外貌和展区；用下拉框切回第1或第2步。"
	if Investigation.is_question_answered(target_id, qid):
		return "这一步已完成。用下拉框切换另一项，完成外貌和展区后才能出发。"
	for req in q.get("requires", []):
		if not _cards.has(req):
			var mat := Investigation.material(target_id, req)
			match String(mat.get("type", "")):
				"archive": return "缺馆藏档案：去浏览器搜编号 %s，再回推理板。" % Investigation.target_code(target_id)
				"web": return "缺研究材料：去浏览器搜“%s”，再回推理板。" % Investigation.target_name(target_id)
				"mail": return "缺布展材料：去电脑「聊天」给阿岚发“%s”，收到邮件后回这里。" % Investigation.target_name(target_id)
	for req in q.get("requires", []):
		if not _linked.has(req):
			return "下一步：按住左侧“%s”，拖进右上框后松开；然后在下方点选结论。" % Investigation.material(target_id, req).get("title", req)
	return "材料已齐，连线还不算完成！阅读材料，在下方点击你认为正确的结论；选项可滚动。"

func _draw() -> void:
	if _central == null:
		return
	var to := _central.get_global_rect().get_center() - global_position
	for mid in _linked:
		if _cards.has(mid):
			var from: Vector2 = _cards[mid].get_global_rect().get_center() - global_position
			if Rect2(Vector2.ZERO, size).has_point(from):
				draw_line(from, to, Color(0.8, 0.65, 0.3, 0.5), 1.0)

func _saved_links() -> Array[String]:
	var out: Array[String] = []
	var raw: Variant = Game.story_flags.get(LINK_KEY, "")
	if typeof(raw) == TYPE_STRING:
		for key in String(raw).split(";", false):
			if not out.has(key):
				out.append(key)
	return out

func _save_links() -> void:
	var all: Array[String] = []
	for key in _saved_links():
		if not key.begins_with(target_id + ":"):
			all.append(key)
	for mid in _linked:
		all.append(target_id + ":" + mid)
	Game.story_flags[LINK_KEY] = ";".join(all)
	Game.save_game()

func card_ids() -> Array[String]:
	var out: Array[String] = []
	for mid in _cards:
		out.append(String(mid))
	return out

func linked_materials() -> Array[String]:
	return _linked.duplicate()

func get_card(mid: String) -> PanelContainer:
	return _cards.get(mid)

func get_central_panel() -> PanelContainer:
	return _central

func get_relation_box() -> VBoxContainer:
	return _relation_box

func get_feedback_label() -> Label:
	return _feedback
