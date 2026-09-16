---
name: extraction
description: Turn one source — a page, a scan, or its OCR text — into a small database. Use when someone has material and wants structured data out of it.
---

# extraction

从一份材料到一个能查的小库。

- schema 跟着材料走，只留回答问题需要的列；一行一个事实。
- 每行都要有 `source`（哪一页、哪一行）和 `note`（存疑处）。
- 不确定的照实写，不猜；抽完抽几行回原文核对。
- 建库与读取都用 Python（标准库 sqlite3；机器上没装就先装 python3），让 agent 自己写小脚本。
- 最后用 `interaction` 那套规矩回答问题。
