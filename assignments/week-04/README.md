# Week 4 · 双休公司消费品库（Shuangxiu Goods）

一个**有来源、证据分级、可增长**的关系数据库 + 渐进式 skill：回答"哪些公司被公开来源描述为实行双休、它们生产哪些生活用品/食品"。

> 口径：只反映**公开来源的描述**，非用工事实认定，且**非穷举**；涉及企业作息以其官方最新说明为准。

## 交付物

| 文件 | 是什么 |
|---|---|
| `data/*.csv` | 建库源数据（唯一真源），每行带 `source_id`/`source_locator`/`note` |
| `artifacts/shuangxiu.db` | SQLite：8 表、11 外键、**519 行**（生成物，`.gitignore` 忽略） |
| `code/seed_data.py` | 从公开来源生成 CSV（含日期换算） |
| `code/build_db.py` | CSV → SQLite，建表 + 外键检查 |
| `code/check_rows.py` | 随机抽 20 行回源核对 → `research/checks.md` |
| `skills/shuangxiu-teller/` | 回答问题的渐进 skill（SKILL.md + 4 个 references） |
| `skills/shuangxiu-ingest/` | 加数据/增长库的 skill（交接给 teller） |
| `rubric.md` | 6 维评分表 |
| `test-questions.md` | 15 题（含 6 类 corner case）及逐题得分 |
| `improvement-log.md` | 5 条"坏答案 → 改动 → 新答案" |
| `research/` | `schema.md`、`build-steps.md`、`checks.md` |

## 怎么跑

```bash
python3 code/seed_data.py
python3 code/build_db.py
python3 code/check_rows.py
```

读库用 Python 标准库 `sqlite3`（无需额外工具）。skill 使用见
`skills/shuangxiu-teller/SKILL.md`；增长见 `skills/shuangxiu-ingest/SKILL.md`。
