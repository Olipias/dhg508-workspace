# 表结构（shuangxiu.db）

8 张表。每张表都有 `source_id`（→ sources）、`source_locator`（文献中的位置）与 `note`（存疑/说明）。

| 表 | 主键 | 关键字段 | 外键 |
|---|---|---|---|
| `sources` | `source_id` | title, publisher, url, pub_date, kind | — |
| `evidence_levels` | `level_id` | label, description | source_id |
| `industries` | `industry_id` | name | source_id |
| `cities` | `city_id` | name, province | source_id |
| `categories` | `category_id` | name | source_id |
| `companies` | `company_id` | name_zh, name_en, schedule_type, evidence_level, schedule_original | industry_id, city_id, evidence_level, source_id |
| `products` | `product_id` | name, category_id | company_id, category_id, source_id |
| `claims` | `claim_id` | schedule_type, schedule_original, year_original, year_start, date_rule, evidence_level | company_id, evidence_level, source_id |

外键 11 条；`PRAGMA foreign_key_check` 通过。

## 视图

`v_company_products`：公司 × 行业 × 城市 × 产品 × 品类的一次性连表，最方便回答问题。

## 字段约定

- `schedule_type`：`双休` / `名义双休` / `上四休三` / `每周二闭店` / `周休二`。
- `evidence_level`：见 `evidence_levels` 表，E-A > E-B > E-C。
- `schedule_original`：来源里的原话（不得改写）。
- `year_original` / `year_start` / `date_rule`：原文年份字样 / 归一化年 / 换算依据；无年份时 `year_start` 为空、`date_rule` 说明。
