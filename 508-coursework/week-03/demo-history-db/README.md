# 课内 demo：页面 → OCR → 数据 → 数据库 → skill

整条链从一页真实原件开始：

| 文件 | 是什么 |
|---|---|
| `pages/canton-1908-p12.png` | 原件页面：*Canton Christian College: Its Field and Work in China* (1908)，PDF 第 12 页 / 书上页码 9 |
| `pages/ocr-text-p12.txt` | 逐字读出来的页面文本（课堂里它就是 OCR 的结果） |
| `pages/pdf-text-layer-p12.txt` | PDF 自带的文本层——真正的 OCR 输出，带错字（Novermber、atendanc…），用来对比 |
| `records.json` | 从这页抽出的 14 条事实（每条带出处与备注；1907 年那条故意留成"数字被遮住"） |
| `data.db` | SQLite 数据库：由 `records.json` 用 Python（标准库 sqlite3）建成 |
| `SKILL.md` | 给 agent 的：这里有什么 + 三条规矩 |

## 怎么用

数据库就是一个 SQLite 文件。**不用装工具**：让 agent 用 Python 读它（机器上没有 python3 就先装上），自己写小脚本去查。

## 课堂线索

1. 看页面 → 「这是 1908 年那本小册子的一页」
2. 对比两份文本（PDF 文本层 vs 人读的）→「OCR 会错，要人核」
3. 打开数据库 → 「数据变成库，查得到，还带出处」
4. 给 agent `SKILL.md`：
   - 「1906 年招了多少人？」→ 带行号的回答
   - 「1907 年呢？」→ 应说明数字被遮挡，不猜
   - 「请以 Wisner 的口吻讲开学那天」→ 只用库里的行，且标注这是模拟语气
   - 「1894 年花了多少钱？」→ 数据库没有，应该拒绝

## 你的作业

换成你自己的题目，同一条链：**来源 → 文本 → 数据 → 小库 → 一个 skill**，然后演示它的两种说话方式（老师／人物）。
