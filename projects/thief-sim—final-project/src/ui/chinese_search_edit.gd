class_name ChineseSearchEdit
extends LineEdit
## 系统IME照常工作；WSL无法共享宿主输入法时，提供项目关键词拼音选词。
signal candidate_changed(candidate: String)
const WORDS := {
	"shuangyangzun": "双羊尊", "syz": "双羊尊", "qingtong": "青铜",
	"shengjiachong": "圣甲虫", "sjc": "圣甲虫", "xinxingshengjiachong": "心形圣甲虫",
	"zhuhu": "注壶", "zh": "注壶", "akeluodili": "阿克罗蒂里",
	"buzhandan": "布展单", "alan": "阿岚",
}

func _ready() -> void:
	focus_entered.connect(_enable_ime)
	focus_exited.connect(_disable_ime)
	text_changed.connect(func(_text: String) -> void: candidate_changed.emit(candidate()))
	keep_editing_on_text_submit = true

func _enable_ime() -> void:
	edit.call_deferred()
	if DisplayServer.get_name() != "headless":
		DisplayServer.window_set_ime_active(true, get_window().get_window_id())
		var at := get_viewport().get_screen_transform() * get_global_rect().end
		DisplayServer.window_set_ime_position(Vector2i(at), get_window().get_window_id())

func _disable_ime() -> void:
	if DisplayServer.get_name() != "headless":
		DisplayServer.window_set_ime_active(false, get_window().get_window_id())

func candidate() -> String:
	return String(WORDS.get(text.strip_edges().to_lower().replace(" ", "").replace("'", ""), ""))

func commit_candidate() -> void:
	var value := candidate()
	if value.is_empty():
		return
	text = value
	caret_column = text.length()
	candidate_changed.emit("")
	grab_focus()
	edit()

func _gui_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_SPACE:
		if not candidate().is_empty():
			commit_candidate()
			accept_event()

func _exit_tree() -> void:
	if has_focus():
		_disable_ime()
