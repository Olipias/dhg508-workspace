#!/usr/bin/env python3
"""Build the week-04 SQLite database from the CSVs in data/.

- Relational schema: 8 tables, many foreign keys (see research/schema.md).
- Every row carries source_id + source_locator + note.
- Idempotent: drops and rebuilds from data/, so adding rows to the CSVs and
  re-running is safe and never corrupts existing rows.
"""
import csv
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
ART = os.path.join(ROOT, "artifacts")
DB = os.path.join(ART, "shuangxiu.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
  source_id      TEXT PRIMARY KEY,
  title          TEXT NOT NULL,
  publisher      TEXT,
  url            TEXT,
  pub_date       TEXT,
  kind           TEXT,
  accessed       TEXT,
  note           TEXT
);

CREATE TABLE industries (
  industry_id    TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  note           TEXT,
  source_id      TEXT NOT NULL,
  source_locator TEXT,
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE cities (
  city_id        TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  province       TEXT,
  note           TEXT,
  source_id      TEXT NOT NULL,
  source_locator TEXT,
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE categories (
  category_id    TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  note           TEXT,
  source_id      TEXT NOT NULL,
  source_locator TEXT,
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE evidence_levels (
  level_id       TEXT PRIMARY KEY,
  label          TEXT NOT NULL,
  description    TEXT,
  source_id      TEXT NOT NULL,
  note           TEXT,
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE companies (
  company_id       TEXT PRIMARY KEY,
  name_zh          TEXT NOT NULL,
  name_en          TEXT,
  industry_id      TEXT NOT NULL,
  city_id          TEXT NOT NULL,
  schedule_type    TEXT NOT NULL,
  evidence_level   TEXT NOT NULL,
  schedule_original TEXT,
  source_id        TEXT NOT NULL,
  source_locator   TEXT,
  note             TEXT,
  FOREIGN KEY (industry_id)   REFERENCES industries(industry_id),
  FOREIGN KEY (city_id)       REFERENCES cities(city_id),
  FOREIGN KEY (evidence_level) REFERENCES evidence_levels(level_id),
  FOREIGN KEY (source_id)     REFERENCES sources(source_id)
);

CREATE TABLE products (
  product_id     TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  category_id    TEXT NOT NULL,
  company_id     TEXT NOT NULL,
  source_id      TEXT NOT NULL,
  source_locator TEXT,
  note           TEXT,
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (company_id)  REFERENCES companies(company_id),
  FOREIGN KEY (source_id)   REFERENCES sources(source_id)
);

CREATE TABLE claims (
  claim_id         TEXT PRIMARY KEY,
  company_id       TEXT NOT NULL,
  schedule_type    TEXT NOT NULL,
  schedule_original TEXT,
  year_original    TEXT,
  year_start       INTEGER,
  date_rule        TEXT,
  evidence_level   TEXT NOT NULL,
  source_id        TEXT NOT NULL,
  source_locator   TEXT,
  note             TEXT,
  FOREIGN KEY (company_id)     REFERENCES companies(company_id),
  FOREIGN KEY (evidence_level) REFERENCES evidence_levels(level_id),
  FOREIGN KEY (source_id)      REFERENCES sources(source_id)
);

CREATE VIEW v_company_products AS
SELECT c.company_id, c.name_zh, c.schedule_type, c.evidence_level,
       i.name AS industry, ci.name AS city,
       p.product_id, p.name AS product, cat.name AS category
FROM companies c
JOIN industries i   ON i.industry_id = c.industry_id
JOIN cities ci      ON ci.city_id = c.city_id
LEFT JOIN products p ON p.company_id = c.company_id
LEFT JOIN categories cat ON cat.category_id = p.category_id;
"""


def read_csv(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    os.makedirs(ART, exist_ok=True)
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    plan = [
        ("sources.csv", "sources"),
        ("industries.csv", "industries"),
        ("cities.csv", "cities"),
        ("categories.csv", "categories"),
        ("evidence_levels.csv", "evidence_levels"),
        ("companies.csv", "companies"),
        ("products.csv", "products"),
        ("claims.csv", "claims"),
    ]
    total = 0
    for fname, table in plan:
        rows = read_csv(fname)
        if not rows:
            print(f"WARN {fname} empty")
            continue
        cols = list(rows[0].keys())
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})"
        con.executemany(sql, [[r[c] or None for c in cols] for r in rows])
        total += len(rows)
        print(f"{table:16s} {len(rows):4d} rows")
    con.commit()

    # ---- integrity checks ----
    problems = []
    for (table,) in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        cnt = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        bad_src = con.execute(
            f"SELECT COUNT(*) FROM {table} "
            "WHERE source_id IS NULL OR source_id=''").fetchone()[0] \
            if "source_id" in [c[1] for c in con.execute(f"PRAGMA table_info({table})")] else 0
        if bad_src:
            problems.append(f"{table}: {bad_src} rows without source_id")
    fk_bad = list(con.execute("PRAGMA foreign_key_check"))
    if fk_bad:
        problems.append(f"foreign_key_check: {len(fk_bad)} violations")

    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'")]
    print(f"\ntotal rows inserted: {total}")
    print(f"tables: {len(tables)} -> {', '.join(tables)}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        con.close()
        sys.exit(1)
    print("foreign_key_check: OK")
    print(f"database: {DB}")
    con.close()


if __name__ == "__main__":
    main()
