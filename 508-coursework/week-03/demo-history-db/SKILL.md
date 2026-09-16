---
name: history-db
description: Answer questions about the 1908 Canton Christian College page from the small database in this folder.
---

# history-db

这个文件所在目录里有：

- `data.db` —— SQLite，14 行；每行一件事：年份、日期、事件、地点、人物、出处、备注。
- `pages/` —— 那页 1908 年原件与它的文字。

用 Python 读库（没有 python3 就装上），自己写脚本。

规矩：

1. 答案只来自行，每条事实带 `[id]`。
2. 库里没有的就说没有，不用常识补；要补就标注「这不是库里的内容」。
3. 扮演人物：只用库里的行，注明「模拟」，不许编造原话。

`note` 里的存疑照实转述。
