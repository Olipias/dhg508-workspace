# 课内 demo：BuildingTeller（这是岭南哪座建筑）

同样机制的"找图"，换成岭南大学的老建筑。库里 6 条记录：照片 + 中英文名 + `description`（machine description）+ `history`（缩过的史事）。把一张照片放进 `query/`，问它这是哪座建筑。

| 文件 | 是什么 |
|---|---|
| `buildings.db` | SQLite：马丁堂、格兰堂、爪哇堂、惺亭、自来水塔、木板屋 6 条记录 |
| `images/` | 六张老照片（Digital Commons @ Lingnan，LUAR_PIC） |
| `records.json` | 建库用的源数据（含 `history_source`） |
| `query/` | 查询图放这里（默认 `query.jpg`） |
| `query-hard.jpg` | 加难用：怀士堂（库里没有） |
| `skills/buildingteller/` | 可以读图（query + 库里照片） |
| `skills/buildingteller-blind/` | 只许看 query 图，**不许打开库里照片**，只能靠文字匹配 |

## 怎么用

让 agent **用 Python 读** `buildings.db`（没装 python3 就先装上），自己写小脚本；不要给它任何查询工具。

**A/B 测试**（两个 skill 各跑一次同一个问题）：
1. 有图版：能打开图片对比，答案应带 `id`。
2. 盲版：只能看 query 图 + 文字；检验"machine description 够不够用"。

**加难**：把 `query-hard.jpg` 换进 `query/`（怀士堂，不在这 6 座里），两个版本都应该拒绝而不是硬塞名字。
