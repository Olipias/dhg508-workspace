extends Control
## E 批独立验收：推理板真实拖卡/连线/关系/纠错/双材料/读档保留。
## 运行：godot --headless res://tests/test_investigation_board.tscn

const SAVE := "/tmp/thief_sim_investigation_board_save.json"

var _checks := 0
var _failures := 0
var board: InvestigationBoard


func check(cond: bool, msg: String) -> void:
	_checks += 1
	if not cond:
		_failures += 1
		printerr("FAIL - " + msg)
	else:
		print("PASS - " + msg)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _mouse_button(pos: Vector2, pressed: bool) -> void:
	var ev := InputEventMouseButton.new()
	ev.position = pos
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	Input.parse_input_event(ev)


func _mouse_motion(pos: Vector2, held: bool = true) -> void:
	var ev := InputEventMouseMotion.new()
	ev.position = pos
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if held else 0
	Input.parse_input_event(ev)


func _drag_to(card: Control, target: Vector2) -> void:
	var scroller := card.get_parent().get_parent() as ScrollContainer
	for i in 30:
		if scroller.get_global_rect().encloses(card.get_global_rect()):
			break
		var hover := InputEventMouseMotion.new()
		hover.position = scroller.get_global_rect().get_center()
		Input.parse_input_event(hover)
		await _frames(1)
		var wheel := InputEventMouseButton.new()
		wheel.position = scroller.get_global_rect().get_center()
		wheel.button_index = MOUSE_BUTTON_WHEEL_UP if card.get_global_rect().get_center().y < scroller.get_global_rect().position.y else MOUSE_BUTTON_WHEEL_DOWN
		wheel.factor = 0.3
		wheel.pressed = true
		Input.parse_input_event(wheel)
		await _frames(2)
	var start := card.get_global_rect().get_center()
	_mouse_button(start, true)
	await _frames(2)
	_mouse_motion(target)
	await _frames(2)
	_mouse_button(target, false)
	await _frames(3)


func _find_button(root: Node, needle: String) -> Button:
	for child in root.get_children():
		if child is Button and (child as Button).text.replace("\n", "").contains(needle):
			return child
		if child is Node:
			var inner := _find_button(child, needle)
			if inner != null:
				return inner
	return null


func _test_other_target(target_id: String, archive_id: String, type_id: String, correct_text: String, flag: String, label: String) -> void:
	var b := InvestigationBoard.new()
	b.set_anchors_preset(Control.PRESET_TOP_LEFT)
	b.size = Vector2(600, 300)
	add_child(b)
	b.set_target(target_id)
	await _frames(4)
	check(b.card_ids().size() == 5, "%s：显示 5 份已获得材料" % label)
	var central := b.get_central_panel().get_global_rect().get_center()
	await _drag_to(b.get_card(archive_id), central)
	await _drag_to(b.get_card(type_id), central)
	var rel_box := b.get_relation_box()
	var btn := _find_button(rel_box, correct_text)
	check(btn != null, "%s：联合判断选项存在" % label)
	if btn != null:
		_mouse_button(btn.get_global_rect().get_center(), true)
		await _frames(2)
		_mouse_button(btn.get_global_rect().get_center(), false)
		await _frames(3)
	check(Game.story_flag(flag), "%s：联合判断通过" % label)
	var delivery_id := archive_id.replace("archive", "delivery")
	await _drag_to(b.get_card(delivery_id), central)
	var area_btn := _find_button(b.get_relation_box(), "布展单")
	check(area_btn != null, "%s：展区关系可选" % label)
	if area_btn != null:
		_mouse_button(area_btn.get_global_rect().get_center(), true)
		await _frames(2)
		_mouse_button(area_btn.get_global_rect().get_center(), false)
		await _frames(3)
	check(Game.bm_selected_target == target_id, "%s：推理完成自动选择相应行动目标" % label)
	check(Game.can_prepare_mission("british_museum"), "%s：单线完成可准备出发" % label)
	b.queue_free()
	await _frames(2)


func _ready() -> void:
	if FileAccess.file_exists(SAVE):
		DirAccess.remove_absolute(SAVE)
	Game.save_path = SAVE
	Game.reset_progress()
	Game.set_story_flag("saw_p00")
	Game.set_story_flag("completed_museum")
	for flag in [
		"inv_zun_archive", "inv_zun_tech", "inv_zun_delivery", "inv_zun_service",
		"inv_scarab_archive", "inv_scarab_type", "inv_scarab_delivery", "inv_scarab_service",
		"inv_askos_archive", "inv_askos_type", "inv_askos_delivery", "inv_askos_service",
	]:
		Game.set_story_flag(flag)

	board = InvestigationBoard.new()
	board.set_anchors_preset(Control.PRESET_TOP_LEFT)
	board.size = Vector2(600, 300)
	add_child(board)
	board.set_target("ram_zun")
	await _frames(4)

	check(board.card_ids().size() == 5, "推理板：只显示已获得 5 份双羊尊材料（实际 %d）" % board.card_ids().size())
	check(board.get_card("zun_archive") != null, "推理板：馆藏档案卡存在")
	check(board.get_card("zun_tech") != null, "推理板：技术研究卡存在")
	var ready := Investigation.ready_target_ids()
	check(ready.size() == 3 and ready.has("ram_zun") and ready.has("egypt_heart_scarab") and ready.has("akrotiri_askos"),
		"推理板：三条线均进入可选目标")
	check(Investigation.search_web("圣甲虫").size() == 1, "调查数据：圣甲虫网页检索唯一")
	check(Investigation.search_archive("10.130.1650").size() == 1, "调查数据：圣甲虫编号检索唯一")
	check(Investigation.search_web("注壶").size() == 1, "调查数据：注壶网页检索唯一")
	check(Investigation.search_archive("VM-GR-25-012").size() == 1, "调查数据：注壶编号检索唯一")
	for mid in ["zun_archive", "zun_tech", "zun_delivery", "zun_service"]:
		var mat := Investigation.material("ram_zun", mid)
		check(mat.has("facts") and mat.has("source"), "推理板：%s 有事实ID/来源元数据" % mid)

	# 1) 拖档案卡到中央：建立连线，但只有一份材料时不能完成联合判断。
	var archive := board.get_card("zun_archive")
	var tech := board.get_card("zun_tech")
	var central_center := board.get_central_panel().get_global_rect().get_center()
	await _drag_to(archive, central_center)
	check("zun_archive" in board.linked_materials(), "推理板：拖到中央后档案已连线")
	var rel_box := board.get_relation_box()
	check(rel_box.get_child_count() > 0, "推理板：连线后出现关系选项")

	# 先点错误关系：只有档案形制，没有工艺研究，应给出材料缺口反馈且可重试。
	var wrong_btn := _find_button(rel_box, "只有档案形制")
	check(wrong_btn != null, "推理板：存在可选的错误关系")
	if wrong_btn != null:
		_mouse_button(wrong_btn.get_global_rect().get_center(), true)
		await _frames(2)
		_mouse_button(wrong_btn.get_global_rect().get_center(), false)
		await _frames(3)
	check(board.get_feedback_label().text.contains("另一份"), "推理板：错误关系给出材料缺口反馈")
	check(not Game.story_flag("inv_ram_zun_features_ok"), "推理板：错误关系不置通过")

	var correct_btn := _find_button(rel_box, "档案形制与工艺研究共同表明")
	check(correct_btn != null, "推理板：关系选项包含联合结论")
	if correct_btn != null:
		_mouse_button(correct_btn.get_global_rect().get_center(), true)
		await _frames(2)
		_mouse_button(correct_btn.get_global_rect().get_center(), false)
		await _frames(3)
	check(not Game.story_flag("inv_ram_zun_features_ok"), "推理板：缺技术材料时联合结论不通过")
	check(board.get_feedback_label().text.contains("缺少"), "推理板：缺材料给出明确反馈（实际 %s）" % board.get_feedback_label().text)

	# 2) 再拖技术卡到中央：两份材料齐备后联合结论通过。
	await _drag_to(tech, central_center)
	check("zun_tech" in board.linked_materials(), "推理板：技术卡已连线")
	rel_box = board.get_relation_box()
	correct_btn = _find_button(rel_box, "档案形制与工艺研究共同表明")
	check(correct_btn != null, "推理板：两卡连线后仍有联合结论")
	if correct_btn != null:
		_mouse_button(correct_btn.get_global_rect().get_center(), true)
		await _frames(2)
		_mouse_button(correct_btn.get_global_rect().get_center(), false)
		await _frames(3)
	check(Game.story_flag("inv_ram_zun_features_ok"), "推理板：两份材料齐备后联合结论通过")

	# 4) 拖动卡片位置并写 story_flags；新板子读回位置/连线。
	# tech 卡在最后一次连线时被提到最上层，用它验证拖动不会被其他卡遮挡。
	var old_pos := tech.position
	await _drag_to(tech, board.get_global_rect().position + Vector2(40, 40))
	check(tech.position == old_pos, "推理板：拖动预览不移动材料栏、不会遮住关系区")
	var pos_raw := String(Game.story_flags.get(InvestigationBoard.POS_KEY, ""))
	check(board.get_global_rect().encloses(board.get_relation_box().get_global_rect()), "推理板：关系区位于板面范围内")
	var link_raw := String(Game.story_flags.get(InvestigationBoard.LINK_KEY, ""))
	check(link_raw.contains("ram_zun:zun_archive") and link_raw.contains("ram_zun:zun_tech"), "推理板：连线写入 story_flags")

	Game.save_game()
	# 模拟读档：清空内存后从磁盘恢复，再建新板。
	Game.story_flags.clear()
	Game.load_game()
	var board2 := InvestigationBoard.new()
	board2.set_anchors_preset(Control.PRESET_TOP_LEFT)
	board2.size = board.size
	add_child(board2)
	board2.set_target("ram_zun")
	await _frames(4)
	check("zun_archive" in board2.linked_materials(), "推理板：读档后连线保留")
	var card2 := board2.get_card("zun_tech")
	check(card2 != null and card2.position.distance_to(tech.position) < 6.0, "推理板：读档后卡片位置保留")
	board2.queue_free()
	await _frames(2)

	# 另两条线：各自走 档案+类型研究 的联合判断；互不阻塞。
	await _test_other_target("egypt_heart_scarab", "scarab_archive", "scarab_type",
		"馆藏记录：埃及晚期、深绿色石", "inv_egypt_heart_scarab_features_ok", "圣甲虫线")
	await _test_other_target("akrotiri_askos", "askos_archive", "askos_type",
		"约前 1650—1615 年，圆腹平底", "inv_akrotiri_askos_features_ok", "注壶线")

	print("\nALL %d CHECKS PASSED" % _checks if _failures == 0 else "\nFAILED %d / %d checks" % [_failures, _checks])
	get_tree().quit(0 if _failures == 0 else 1)
