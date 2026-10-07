#!/usr/bin/env python3
"""生成 Vercel 部署所需文件：

  vercel/api/_db.py     —— 数据库 base64 + skill 原则（内嵌，随函数打包）
  vercel/index.html     —— 从 week-05/index.html 复制

运行前先有数据库：python3 week-04/code/build_db.py（或本脚本自动建）。
"""
from __future__ import annotations

import base64
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W5 = HERE.parent
W4 = W5.parent / "week-04"
DB = W4 / "artifacts" / "shuangxiu.db"
VERCEL = W5 / "vercel"


def ensure_db() -> None:
    if DB.exists():
        return
    code = W4 / "code"
    for script in ("seed_data.py", "build_db.py"):
        subprocess.run([sys.executable, str(code / script)], check=True)


def main() -> int:
    ensure_db()
    principles = (W5 / "skills" / "shuangxiu-teller" / "principles.md").read_text(encoding="utf-8")
    db_b64 = base64.b64encode(DB.read_bytes()).decode()

    (VERCEL / "api").mkdir(parents=True, exist_ok=True)
    out = (
        '"""自动生成，请勿手改；运行 code/build_vercel.py 重新生成。"""\n\n'
        f"DB_B64 = {db_b64!r}\n\n"
        f"PRINCIPLES = {principles!r}\n"
    )
    (VERCEL / "api" / "_db.py").write_text(out, encoding="utf-8")

    (VERCEL / "index.html").write_text(
        (W5 / "index.html").read_text(encoding="utf-8"), encoding="utf-8")

    # PWA：manifest、service worker、图标
    for f in ("manifest.webmanifest", "sw.js"):
        shutil.copy(W5 / f, VERCEL / f)
    (VERCEL / "icons").mkdir(exist_ok=True)
    for f in (W5 / "icons").glob("*.png"):
        shutil.copy(f, VERCEL / "icons" / f.name)

    kb = len(out) / 1024
    print(f"wrote vercel/api/_db.py ({kb:.0f} KB) and vercel/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
