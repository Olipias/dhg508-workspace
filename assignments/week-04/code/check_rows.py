#!/usr/bin/env python3
"""Sample 20 rows from the database and print them next to their source.

Used for the week-04 requirement: compare 20 random rows with the originals.
Writes a scaffold to research/checks.md that is then filled in by hand with the
error, its cause, and the fix.
"""
import os
import random
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "artifacts", "shuangxiu.db")
OUT = os.path.join(ROOT, "research", "checks.md")

# table -> how many to sample
PLAN = {
    "companies": 6, "products": 6, "claims": 4, "industries": 1,
    "cities": 1, "categories": 1, "sources": 1,
}

# Manual review of each sampled row, keyed by its primary-key value.
# (result, error_cause_fix)
FINDINGS = {
    "C070": ("与 S1「家电小家电/家居」一致：办公岗双休。城市/行业为公开资料整理，非原文",
             "无"),
    "C101": ("与 S4 快照一致（味事达｜酱油与调味汁｜江门）",
             "错误：name_en 曾填 “Zhongshan Masters”，来源未载。成因：擅自补英文名。"
             "修复：name_en 清空，并在 note 注明“英文名未核实”"),
    "C085": ("与 S1「金融/医药」一致：销售岗双休为主", "无"),
    "C054": ("与 S1「快消/食品饮料」一致：职能岗双休，销售岗周六常出勤", "无"),
    "C064": ("与 S1「美妆/日化/服饰」一致：职能岗双休", "无"),
    "C009": ("与 S1「明星案例」一致：夜洁计划。城市成都为公开资料，非原文", "无"),
    "P026": ("与 S1「明星案例」一致：vivo X/S 手机", "无"),
    "P067": ("与 S1 一致：心动网络 → TapTap", "无"),
    "P094": ("与 S1 一致：安克 → soundcore 子品牌", "无"),
    "P171": ("与 S4 快照一致：仟人｜饮料｜广东", "无"),
    "P021": ("与 S1「明星案例」一致：长城炮", "无"),
    "P178": ("与 S4 快照一致：PLAYMOBIL｜儿童玩具｜上海", "无"),
    "CL082": ("与 S1 一致：中国银联 双休为主；原文未给年份，year_start 留空", "无"),
    "CL068": ("与 S1 一致：森马 双休为主", "无"),
    "CL048": ("与 S1 一致：韦尔 双休为主", "无"),
    "CL083": ("与 S1 一致：财付通 双休为主", "无"),
    "IND32": ("服饰分类无误", "无"),
    "CITY19": ("厦门属福建，无误", "无"),
    "CAT20": ("茶饮分类无误", "无"),
    "S6": ("来源信息本应正确，但抽样发现列错位",
            "错误：sources.csv 中 note 与 accessed 两列值互换。"
            "成因：seed_data.py 按 (…,note)+[ACCESSED] 追加，而表头写作 accessed,note，错位。"
            "修复：调整表头为 note,accessed；重建后 S6 的 accessed=2026-09-23、"
            "note=双休购由重庆文化传播公司7月14日上线，后暂停服务"),
}


def find(table, d):
    """Look up a finding by any plausible primary-key field."""
    for key in ("company_id", "product_id", "claim_id", "industry_id",
                "city_id", "category_id", "source_id"):
        if key in d and d[key] in FINDINGS:
            return FINDINGS[d[key]]
    return ("", "")


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    random.seed(508)
    lines = ["# Week 4 · 20 行抽样核对", "",
             "随机种子 `508`，`code/check_rows.py` 可复现。逐行回原来源核对，"
             "记录错误、成因、修复。", ""]
    n = 0
    for table, k in PLAN.items():
        ids = [r[0] for r in con.execute(
            f"SELECT rowid FROM {table} ORDER BY rowid")]
        for rowid in random.sample(ids, min(k, len(ids))):
            n += 1
            row = con.execute(
                f"SELECT * FROM {table} WHERE rowid=?", (rowid,)).fetchone()
            d = dict(row)
            src = ""
            sid = d.get("source_id")
            if sid:
                s = con.execute(
                    "SELECT title,publisher,url FROM sources WHERE source_id=?",
                    (sid,)).fetchone()
                if s:
                    src = f"{s['title']}｜{s['publisher']}｜{s['url']}"
            lines.append(f"## {n}. `{table}` rowid={rowid}")
            lines.append("")
            for key, val in d.items():
                lines.append(f"- **{key}**: {val}")
            lines.append(f"- **来源**: {src or '（该表无 source_id）'}")
            lines.append(f"- **出处位置**: {d.get('source_locator','')}")
            result, fix = find(table, d)
            lines.append(f"- **核对结果**: {result}")
            lines.append(f"- **错误/成因/修复**: {fix}")
            lines.append("")
    con.close()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"sampled {n} rows -> {OUT}")


if __name__ == "__main__":
    main()
