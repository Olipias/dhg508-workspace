# 增量步骤（新增一家公司为例）

1. `data/sources.csv`：若来源是新的，追加一行（`source_id,title,publisher,url,pub_date,kind,note,accessed`）。
2. `data/companies.csv`：追加公司行。`industry_id`/`city_id` 必须已在 `industries.csv`/`cities.csv` 存在，否则先加维度行。
3. `data/products.csv`：每加一个产品一行，`company_id` 指向新公司，`category_id` 指向 `categories.csv`。
4. `data/claims.csv`：加一条工时主张，照抄 `schedule_original`；年份写 `year_original`，归一化写 `year_start`，并在 `date_rule` 说明换算。
5. 重建：
   ```bash
   python3 code/build_db.py
   python3 code/check_rows.py
   ```
6. 确认 `PRAGMA foreign_key_check` 与抽样核对均通过，且旧行未被破坏（行数只增不减）。

## 不要做

- 不写没有 `source_id` 的行。
- 不把第三方名单/企业自述当作已核实的用工事实。
- 不新增"某公司不双休/黑名单"这类判断。
