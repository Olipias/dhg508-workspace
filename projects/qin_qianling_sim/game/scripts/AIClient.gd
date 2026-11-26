extends Node
## Thin client for the local NPC server.  The server holds the API key and
## logs every call; the game only sends the NPC id, the player's words and a
## small perception snapshot.

signal replied(npc_id: String, speech: String, refs: Array)
signal failed(npc_id: String)

const ENDPOINT := "http://127.0.0.1:8787/npc"

var http: HTTPRequest
var pending_id: String = ""
var busy: bool = false

func _ready() -> void:
	http = HTTPRequest.new()
	http.timeout = 28.0
	add_child(http)
	http.request_completed.connect(_on_request_completed)

func ask(npc_id: String, text: String, context: Dictionary) -> void:
	if busy:
		return
	busy = true
	pending_id = npc_id
	var body := JSON.stringify({
		"npc_id": npc_id,
		"text": text,
		"context": context,
	})
	var err := http.request(ENDPOINT, ["Content-Type: application/json"],
		HTTPClient.METHOD_POST, body)
	if err != OK:
		busy = false
		failed.emit(npc_id)

func _on_request_completed(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	busy = false
	var id := pending_id
	pending_id = ""
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		failed.emit(id)
		return
	var parsed: Variant = JSON.parse_string(body.get_string_from_utf8())
	if not parsed is Dictionary:
		failed.emit(id)
		return
	var speech: String = str(parsed.get("speech", "")).strip_edges()
	if speech == "":
		failed.emit(id)
		return
	var refs: Array = parsed.get("source_refs", [])
	replied.emit(id, speech, refs)
