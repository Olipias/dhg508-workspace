---
name: interaction
description: Answer from a small database — as a historian with citations, as an NPC with written rules, or by matching a photo against labelled image records. Use when a database is the source of truth and someone is asking it things.
---

# interaction

底线（三种方式共同）：答案只来自行，带 `id`；没有就说没有；模拟要标注。

- **historian**：结论 + `[id]`；保留 context（哪一年、哪批材料）和 reference（第几行）。
- **NPC**：先写一组 rules——它知道什么、库外怎么答、什么时候说「这是模拟」、怎么带路。
- **找图**：打开图片逐张对比，不靠文件名；答最匹配的 + `[id]` + 一句视觉理由，不像就说不像。
