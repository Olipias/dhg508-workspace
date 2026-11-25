extends RefCounted
## 依实际字体测量换行；不截断原文，不依赖中文字符数估算宽度。
static func lines(text: String, label: Label, width: float) -> Array[String]:
	var result: Array[String] = []
	var current := ""
	var font := label.get_theme_font("font")
	var font_size := label.get_theme_font_size("font_size")
	for ch in text:
		if ch == "\n":
			result.append(current)
			current = ""
			continue
		while not current.is_empty() and font.get_string_size(current + ch, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > width:
			var boundary := current.length()
			# 英文单词/馆藏编号能放进一行时整体移到下一行，超长串才按字符折行。
			if _ascii_token(ch):
				while boundary > 0 and _ascii_token(current.substr(boundary - 1, 1)):
					boundary -= 1
			if boundary == 0:
				boundary = current.length()
			result.append(current.substr(0, boundary))
			current = current.substr(boundary)
		current += ch
	result.append(current)
	return result

static func split(text: String, label: Label, width: float, max_lines: int) -> Array[String]:
	var wrapped := lines(text, label, width)
	var pages: Array[String] = []
	for at in range(0, wrapped.size(), max_lines):
		pages.append("\n".join(wrapped.slice(at, mini(at + max_lines, wrapped.size()))))
	return pages

static func hint(page: int, count: int) -> String:
	return "E / Enter %s（%d/%d）" % ["下一页" if page + 1 < count else "继续", page + 1, count]

static func _ascii_token(ch: String) -> bool:
	var code := ch.unicode_at(0)
	return code >= 33 and code <= 126
