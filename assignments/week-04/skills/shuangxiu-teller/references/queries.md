# 示例查询

用 Python + sqlite3 自己写；下面按问题给最小 SQL（库路径 `assignments/week-04/artifacts/shuangxiu.db`）。

```python
import sqlite3
con = sqlite3.connect("assignments/week-04/artifacts/shuangxiu.db")
con.row_factory = sqlite3.Row
```

- **某公司是不是双休 / 什么证据？**
  ```sql
  SELECT c.name_zh, c.schedule_type, c.evidence_level, c.schedule_original,
         s.url FROM companies c JOIN sources s USING(source_id)
  WHERE c.name_zh LIKE '%关键词%';
  ```
- **某产品是哪家公司做的？**
  ```sql
  SELECT p.name, c.name_zh, cat.name, p.note
  FROM products p JOIN companies c USING(company_id)
  JOIN categories cat USING(category_id)
  WHERE p.name LIKE '%关键词%';
  ```
- **某品类下有哪些双休公司？**
  ```sql
  SELECT DISTINCT c.name_zh, c.evidence_level, cat.name
  FROM companies c JOIN products p USING(company_id)
  JOIN categories cat USING(category_id)
  WHERE cat.name=? ORDER BY c.evidence_level;
  ```
- **只看证据最硬的（E-A）**
  ```sql
  SELECT name_zh, schedule_original FROM companies
  WHERE evidence_level='E-A';
  ```
- **按证据等级统计**
  ```sql
  SELECT evidence_level, COUNT(*) FROM companies GROUP BY 1;
  ```
- **一条产品连带来源，用于引用**
  ```sql
  SELECT * FROM v_company_products WHERE product LIKE '%关键词%';
  ```

回答时必须回带命中的 `company_id`/`product_id` 与 `sources.url`。
