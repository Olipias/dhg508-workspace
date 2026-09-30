# 怎么维护：加新材料，一步步来

数据流向：`week-04/data/*.csv`（唯一真源）→ `week-04/code/build_db.py`
→ `week-04/artifacts/shuangxiu.db`。**只改 CSV，不手改库**。

## 加一家公司（或一个产品）

1. 读 `week-04/skills/shuangxiu-ingest/references/tables.md` 确认字段。
2. 先补来源：`data/sources.csv` 追加一行（`source_id,title,publisher,url,pub_date,kind,note,accessed`）。
   来源是新的才加，已有就引用旧 `source_id`。
3. 写公司：`data/companies.csv` 追加行，带 `source_id`、`source_locator`、`note`、
   `evidence_level`。`industry_id`/`city_id` 必须已存在，否则先加维度行。
4. 写产品：`data/products.csv` 每个产品一行，`company_id` 指向新公司，
   `category_id` 指向 `categories.csv`。
5. 写主张：`data/claims.csv` 照抄 `schedule_original`，年份写 `year_original`，
   归一化写 `year_start`，并在 `date_rule` 说明换算依据。
6. 重建并自检：
   ```bash
   python3 week-04/code/build_db.py     # 建库 + 外键检查
   python3 week-04/code/check_rows.py   # 抽样回源核对
   ```
7. 确认 `PRAGMA foreign_key_check` 通过、抽样核对通过、旧行未被破坏（行数只增不减）。
8. 若因某个坏答案而改，记入 `week-04/improvement-log.md`；若改了建库逻辑，
   同步 `week-04/research/schema.md` 与 `research/build-steps.md`。

## 核对查询

```sql
-- 某产品是哪家公司做的
SELECT p.name, c.name_zh, cat.name FROM products p
  JOIN companies c USING(company_id) JOIN categories cat USING(category_id)
  WHERE p.name LIKE '%关键词%';
-- 某品类下有哪些双休公司
SELECT DISTINCT c.name_zh, c.evidence_level FROM companies c
  JOIN products p USING(company_id) JOIN categories cat USING(category_id)
  WHERE cat.name = ?;
-- 抽一条带来源
SELECT * FROM v_company_products WHERE product LIKE '%关键词%';
```

## 不要做

- 不写没有 `source_id` 的行。
- 不把第三方名单/企业自述当作已核实的用工事实。
- 不新增"某公司不双休/黑名单"这类判断。
- 不擅自补来源没有的字段（如英文名），没有就留空并注明未核实。

硬规矩见 `principles.md`；回答流程见 `what-it-does.md`。
