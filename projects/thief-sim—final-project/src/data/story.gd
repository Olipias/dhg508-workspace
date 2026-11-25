class_name Story
extends RefCounted
## 接入STORY_TEXT_V1的直白人物/契约说明，并按EXPLORATION_PATCH_V2改为名字和文字资料。
const ENTRIES := {
	"p01_door_in_rain": {
		"cards": {
			"target_list": {
				"title": "恶魔留下的清单",
				"body": "商代双羊尊、埃及心形圣甲虫、阿克罗蒂里彩绘注壶。选择一件调查，没有照片。"
			}
		},
		"script": [
			{
				"speaker": "我",
				"text": "面具带回来了。接下来要找哪件？"
			},
			{
				"speaker": "恶魔",
				"text": "面具放下。从清单里选一件，再交到我手上，契约就解除。"
			},
			{
				"card": "target_list"
			},
			{
				"speaker": "我",
				"text": "只有名字，怎么找？"
			},
			{
				"speaker": "老猫",
				"text": "我是给你介绍零活的老猫。戒指是我收来的旧货，我不知道里面有东西。"
			},
			{
				"speaker": "老猫",
				"text": "我把阿岚的联系方式发给你。她替文物接收方核对资料，能帮你查这几个名字。"
			},
			{
				"speaker": "阿岚",
				"text": "我是阿岚。先用桌上的电脑搜索文物名称，读馆藏档案和研究摘记。需要本次布展信息，就在电脑聊天里把名字发给我。"
			},
			{
				"speaker": "我",
				"text": "双羊尊的两只羊托着中间的壶。研究还说，羊角先铸好，再与器身锁接。"
			},
			{
				"speaker": "阿岚",
				"text": "这些特征能帮你认物。它以前在哪里制作，和今晚摆在哪个展柜，是两件事。布展信息我发邮件给你。"
			},
			{
				"speaker": "阿岚",
				"text": "把材料拖到推理板右侧，先确认外貌，再确认本次展区。查清一件就够，不用做完三个目标。"
			},
			{
				"speaker": "老猫",
				"text": "推理完成后用手机准备行动，再走到房门出发。普通东西带回后先存箱，在手机预约买家。"
			},
			{
				"set_flag": "saw_p01"
			},
			{
				"speaker": "任务提示",
				"text": "现在去书桌按 E。浏览器搜索“双羊尊”，再给阿岚发“双羊尊”，最后在推理板整理材料。"
			}
		]
	},
	"h01_label_lesson": {
		"cards": {
			"card_1936": {
				"title": "双羊尊馆藏记录",
				"body": "1936,1118.1，乔治·尤摩弗帕勒斯（George Eumorfopoulos）旧藏。入藏记录不能补齐此前的出境经过。"
			}
		},
		"script": [
			{
				"speaker": "阿岚",
				"text": "馆藏编号可以帮助查找同一件文物。资料没写清的流转经过，就先留空。"
			},
			{
				"card": "card_1936"
			},
			{
				"speaker": "我",
				"text": "先核对身份和布展信息，再去现场找。"
			}
		]
	},
	"h02_two_addresses": {
		"cards": {},
		"script": [
			{
				"speaker": "阿岚",
				"text": "我替接收方核对文物身份和交接记录。带回主要文物后，你可以联系我。"
			},
			{
				"speaker": "我",
				"text": "接收方会直接买走吗？"
			},
			{
				"speaker": "阿岚",
				"text": "主要文物不走普通买卖。选择交接时，我们按对应国家安排接收。"
			}
		]
	},
	"p00_devil_contract": {
		"cards": {
			"contract_clause": {
				"title": "戒指上的契约",
				"body": "先带回青铜面具，再从三个名字中选一件交给恶魔。交付后解除契约；拒交会遭到反噬。"
			}
		},
		"script": [
			{
				"speaker": "我",
				"text": "老猫把这枚戒指当欠款给了我。"
			},
			{
				"speaker": "恶魔",
				"text": "你收下戒指，契约就生效了。"
			},
			{
				"card": "contract_clause"
			},
			{
				"speaker": "我",
				"text": "先找面具，然后查下一件。"
			}
		]
	},
	"p05_devil_demand": {
		"cards": {
			"wrath_scene": {
				"title": "戒指发烫",
				"body": "你按住包口。戒指越来越烫，灯光随之暗下去。"
			},
			"ending_comply_card": {
				"title": "结局：履行契约",
				"body": "你把%TARGET%交给恶魔。戒指冷却，契约字迹消失。你保住了自己的生活，也失去了再决定这件文物去向的机会。"
			},
			"ending_rebel_return_card": {
				"title": "结局：交给接收方",
				"body": "阿岚先处理你手上的烫伤，再与%COUNTRY%接收方核对%TARGET%的交接记录。文物交了出去，戒指上的痕迹仍在。这次你承担了拒交的后果。"
			}
		},
		"script": [
			{
				"speaker": "我",
				"text": "%TARGET%带回来了。"
			},
			{
				"speaker": "恶魔",
				"text": "给我。交付后，契约解除。"
			},
			{
				"choices": [
					{
						"text": "把文物交给恶魔。",
						"goto": "p05_hand_over"
					},
					{
						"text": "拒绝，联系对应国家的接收方。",
						"goto": "p05_refuse"
					}
				]
			},
			{
				"label": "p05_hand_over"
			},
			{
				"set_flag": "ending_id",
				"value": "comply"
			},
			{
				"speaker": "恶魔",
				"text": "收到了。契约到此结束。"
			},
			{
				"card": "ending_comply_card"
			},
			{
				"goto": "p05_end"
			},
			{
				"label": "p05_refuse"
			},
			{
				"card": "wrath_scene"
			},
			{
				"speaker": "恶魔",
				"text": "文物还没交给我。你现在交出，契约仍然作数。"
			},
			{
				"choices": [
					{
						"text": "改主意，交给恶魔。",
						"goto": "p05_submit_late"
					},
					{
						"text": "继续拒交，交给接收方。",
						"goto": "p05_rebel_return"
					}
				]
			},
			{
				"label": "p05_submit_late"
			},
			{
				"set_flag": "ending_id",
				"value": "comply"
			},
			{
				"speaker": "我",
				"text": "拿去。"
			},
			{
				"card": "ending_comply_card"
			},
			{
				"goto": "p05_end"
			},
			{
				"label": "p05_rebel_return"
			},
			{
				"set_flag": "ending_id",
				"value": "return"
			},
			{
				"speaker": "阿岚",
				"text": "先坐下，我给你处理烫伤。%COUNTRY%接收方已准备好，我们再核对实物。"
			},
			{
				"card": "ending_rebel_return_card"
			},
			{
				"label": "p05_end"
			},
			{
				"set_flag": "saw_p05"
			},
			{
				"speaker": "任务提示",
				"text": "本次行动结束。结算页可以返回交付前的检查点，重新选择。"
			}
		]
	}
}

static func has_entry(entry_id: String) -> bool:
	return ENTRIES.has(entry_id)

static func _resolve(value: Variant, target_id: String) -> Variant:
	var names := {"ram_zun": "商代双羊尊", "egypt_heart_scarab": "心形圣甲虫", "akrotiri_askos": "阿克罗蒂里彩绘注壶"}
	var countries := {"ram_zun": "中国", "egypt_heart_scarab": "埃及", "akrotiri_askos": "希腊"}
	if value is String:
		return value.replace("%TARGET%", names.get(target_id, "带回的文物")).replace("%COUNTRY%", countries.get(target_id, "对应国家"))
	if value is Array:
		var out: Array = []
		for item in value:
			out.append(_resolve(item, target_id))
		return out
	if value is Dictionary:
		var out := {}
		for key in value:
			out[key] = _resolve(value[key], target_id)
		return out
	return value

static func script(entry_id: String, target_id := "ram_zun") -> Array:
	return _resolve(ENTRIES.get(entry_id, {}).get("script", []), target_id)

static func cards(entry_id: String, target_id := "ram_zun") -> Dictionary:
	return _resolve(ENTRIES.get(entry_id, {}).get("cards", {}), target_id)
