# Week 4 · 数据库设计（schema）

主题：**公开来源称实行双休（或同类缩短工时）的中国消费品公司及其产品**。范围全品类。

## 设计原则

1. **关系化**：把"公司—产品—工时主张—来源"拆成主表 + 维度表 + 关联。
2. **每行可溯源**：每张表都有 `source_id`（→ `sources`）与 `source_locator`（文献中的位置），以及 `note`。
3. **原文与归一化并列**：`schedule_original`/`year_original` 照抄来源；`year_start` 为归一化年，`date_rule` 写明换算依据；`name_en` 只在来源有载时填写。
4. **证据分级**：`evidence_level` → `evidence_levels`（E-A/E-B/E-C）。
5. **可增长**：新增材料 = 往 `data/*.csv` 追加行，重跑 `code/build_db.py`；脚本重建库，行只增不减。

## 表与外键

| 表 | 主键 | 外键 |
|---|---|---|
| `sources` | source_id | — |
| `evidence_levels` | level_id | source_id→sources |
| `industries` | industry_id | source_id→sources |
| `cities` | city_id | source_id→sources |
| `categories` | category_id | source_id→sources |
| `companies` | company_id | industry_id, city_id, evidence_level, source_id |
| `products` | product_id | company_id, category_id, source_id |
| `claims` | claim_id | company_id, evidence_level, source_id |

共 8 表、11 条外键、1 个视图 `v_company_products`。`PRAGMA foreign_key_check` 通过。

## 行数（目标 ≥200）

sources 7 · industries 41 · cities 31 · categories 27 · evidence_levels 3 ·
companies 102 · products 181 · claims 102 = **494 行**。

## 增长流程

见 `research/build-steps.md`；实际增量口径见 `skills/shuangxiu-ingest/references/ingest-steps.md`。
