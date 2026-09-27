# Week 4 · 数据构建与增长步骤

目标：**新增材料 = 重复同样几步，只加行，不破坏旧行。**

## 目录

```text
assignments/week-04/
├── data/            # 建库源数据（CSV，唯一真源）
├── code/            # seed_data.py / build_db.py / check_rows.py
├── artifacts/       # shuangxiu.db（生成物，.gitignore 忽略 *.db）
├── skills/          # 渐进 skill：shuangxiu-teller / shuangxiu-ingest
├── research/        # 本文件、schema.md、checks.md
├── rubric.md / test-questions.md / improvement-log.md / questions.md
```

## 从零重建

```bash
python3 code/seed_data.py    # 由公开来源生成/刷新 data/*.csv（含出处与换算）
python3 code/build_db.py     # data/*.csv → artifacts/shuangxiu.db（建表+外键检查）
python3 code/check_rows.py   # 随机抽 20 行 → research/checks.md
```

## 新增一家公司/产品

1. `data/sources.csv` 追加来源（若无）。
2. `data/companies.csv`、`data/products.csv`、`data/claims.csv` 追加行；
   维度（行业/城市/品类）先在对应 CSV 补齐。
3. 每行都要有 `source_id`、`source_locator`、`note`；年份照抄原文并给 `date_rule`。
4. 重跑 `build_db.py` 与 `check_rows.py`；确认外键通过、旧行未被破坏。
5. 详细步骤见 `skills/shuangxiu-ingest/references/ingest-steps.md`。

## 数据来源

S1 即答侠《双休公司推荐名单 2026》· S2 新黄河/极目新闻 · S3 新浪 · S4 sxgo.cc 双休购名单 ·
S5 双休购平台 · S6 世界日报 · S7 楚天都市报。链接与日期见 `data/sources.csv`。

## 口径与免责

- 本库只反映**公开来源的描述**，非用工事实认定，且**非穷举**。
- 涉及具体企业作息，以其官方最新说明为准；不作否定评价。
