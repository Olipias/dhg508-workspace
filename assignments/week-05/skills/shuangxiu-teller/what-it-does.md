# 它做什么：怎么从数据库回答问题

## 数据地图

库：`assignments/week-04/artifacts/shuangxiu.db`（SQLite，8 表 + 1 视图）。
读库用 Python 标准库 `sqlite3` 自己写小脚本，不要臆造查询工具。

| 表 | 主键 | 关键字段 | 外键 |
|---|---|---|---|
| `sources` | source_id | title, publisher, url, pub_date, kind | — |
| `evidence_levels` | level_id | label, description | source_id |
| `industries` | industry_id | name | source_id |
| `cities` | city_id | name, province | source_id |
| `categories` | category_id | name | source_id |
| `companies` | company_id | name_zh, name_en, schedule_type, evidence_level, schedule_original | industry_id, city_id, evidence_level, source_id |
| `products` | product_id | name, category_id | company_id, category_id, source_id |
| `claims` | claim_id | schedule_type, schedule_original, year_original, year_start, date_rule, evidence_level | company_id, evidence_level, source_id |

视图 `v_company_products`：公司 × 行业 × 城市 × 产品 × 品类一次连表，最快。
每张表都有 `source_id`、`source_locator`（文献位置）、`note`（存疑照实转述）。

## 回答流程

1. **落点**：把用户问题里的公司名/品牌/产品/品类拿去查库（公司查 `name_zh`，
   产品查 `products.name`，也可按 `categories`/`industries` 反查公司）。
2. **取证**：命中后取出 `schedule_type`、`evidence_level`、`schedule_original`、
   `source_id` 与 `sources.url`；产品再连 `categories`。
3. **成答**：先给结论，再给**证据等级**，最后给代表产品与来源链接。
   公司/产品都要带 `[company_id]`/`[product_id]`。

## 证据等级（回答必须声明）

| 等级 | 含义 | 怎么说 |
|---|---|---|
| E-A | 官方通知/媒体交叉验证 | 证据最强，仍注明"以其官方最新说明为准" |
| E-B | 名义双休（员工反馈较稳） | 提醒"双休 ≠ 不加班" |
| E-C | 企业自述/第三方名单/用户提交 | 必须提示"未经独立核实，仅作参考" |

## 查询示例

```python
import sqlite3
con = sqlite3.connect("assignments/week-04/artifacts/shuangxiu.db")
con.row_factory = sqlite3.Row
# 某公司是双休吗
con.execute("""SELECT c.name_zh, c.schedule_type, c.evidence_level,
       c.schedule_original, s.url FROM companies c JOIN sources s USING(source_id)
       WHERE c.name_zh LIKE ?""", ("%安克%",))
```

更多按"公司 / 产品 / 品类 / 等级"的查询模板见 `how-to-maintain.md` 的
"核对查询"一节；边界与拒答口径见 `principles.md`。
