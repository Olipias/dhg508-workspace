---
name: BuildingTeller
description: Name the Lingnan building in a photo. Use when someone shows an old campus building photo and asks which building it is.
---

# BuildingTeller

这个文件的上两级目录里有：

- `buildings.db` —— SQLite，6 条记录：每座建筑的名字、年代、`description`（machine description：照片里能看到什么）、`history`、照片路径。
- `images/` —— 那 6 张照片。
- `query/` —— 用户拿来的照片。

用 Python 读库（没有 python3 就装上），自己写脚本。

规矩：

1. 答案带记录的 `id`。
2. 看图对比，或用你自己的描述去搜库里的文字；但不许靠文件名、元数据或记忆。
3. 都不像就说都不像。
