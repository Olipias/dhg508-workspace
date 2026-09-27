---
name: shuangxiu-ingest
description: Add new companies, products, claims or sources to the week-04 双休 consumer-goods database, then rebuild and re-check it. Use when someone wants to grow the dataset (加一家公司 / 加一个产品 / 补来源) rather than answer questions.
---

# shuangxiu-ingest

## 何时用

要给"双休公司/产品"库**加数据**时。回答问题的 skill 是 `shuangxiu-teller`，两者交接：本 skill 加完并验证后，交给 teller 使用。

## 数据流向

`data/*.csv`（唯一真源）→ `code/build_db.py` → `artifacts/shuangxiu.db`。

## 步骤

1. 先读 `references/tables.md` 了解字段；`data/` 下每个表一个 CSV。
2. 追加行（**只加不改旧行**）：
   - 先确认/新增 `sources` 行（文献、链接、日期、位置）。
   - 公司写 `companies.csv`（含 `source_id`、`source_locator`、`note`、`evidence_level`）。
   - 产品写 `products.csv`；若要记日期，写 `claims.csv` 并保留 `year_original`。
   - 每条都要有 `source_id` 与 `note`；不确定处照实写。
3. 重建并自检：
   ```bash
   python3 code/build_db.py     # 建库 + 外键检查
   python3 code/check_rows.py   # 抽样回源核对
   ```
4. 若改了建库逻辑，同步更新 `research/schema.md` 与 `research/build-steps.md`。
5. 把改动记入 `improvement-log.md`（若是因某个坏答案而改）。

详细字段清单见 `references/tables.md`（与 teller 共用）；增量流程见 `references/ingest-steps.md`。
