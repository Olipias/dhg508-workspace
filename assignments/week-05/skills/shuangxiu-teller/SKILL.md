---
name: shuangxiu-teller
description: Answer questions about Chinese consumer companies/brands that public sources describe as practising a two-day weekend (双休), and about the daily goods and food they make, using the relational database in assignments/week-04/artifacts/shuangxiu.db. Use for 双休购 / 双休公司 / 用消费投票 / 这个牌子是不是双休 / 哪家公司做某产品.
---

# shuangxiu-teller · 索引

一句话：回答"某公司/品牌是不是公开说双休、它做什么产品"，答案只来自
`assignments/week-04/artifacts/shuangxiu.db`。

## 读哪个文件

| 你的任务 | 读这个 |
|---|---|
| 想知道它怎么从库里回答问题（流程、证据等级、引用方式） | [`what-it-does.md`](what-it-does.md) |
| 想加公司/产品/来源，或重建、核对数据库 | [`how-to-maintain.md`](how-to-maintain.md) |
| 回答前必须遵守的硬规矩、边界、拒答口径 | [`principles.md`](principles.md) |

不要在本文件堆细节；细节都写明在对应文件里。表结构与字段名在
[`what-it-does.md`](what-it-does.md) 的"数据地图"一节；加数据只改
`data/*.csv`，步骤在 [`how-to-maintain.md`](how-to-maintain.md)。

## 交付物

本目录给 **opencode 里的 agent** 用；`assignments/week-05/` 的
`server.py` + `index.html` 把这套规矩做成网页 app（见 `README.md`）。
