# Week 5 · 双休购 app

把 week-04 的「双休公司/产品」skill 做成一个**谁都能在浏览器打开**的小应用：
一个网页 + 一台本地 Python 服务器；服务器**真实调用 DeepSeek**，让模型用
function calling 去查 `week-04/artifacts/shuangxiu.db`，再据查到的行作答。

## 它长什么样

- 打开页面先看到库的规模与证据分布。
- 输入品牌 / 产品 / 问题（如「安克是双休吗？」「咖啡有哪些双休公司？」）。
- 回来三块：**结论**（模型基于库作答）、**查库动作**（它调了哪些工具）、
  **命中记录**（公司卡片：作息、证据等级、原话、产品、来源链接）。
- 离题问题（如「帮我点一份汉堡王」）按 skill 原则回「前面的区域以后再来探索吧!」。

这不是 demo 的 fixture：`server.py` 里没有写死的答案，每个回答都要先查库。

## 跑起来

```bash
# 1. 先有库（week-04 的生成物，*.db 不入 Git）
python3 ../week-04/code/build_db.py

# 2. 设密钥（见 .env.example；绝不写进会提交的文件）
export DEEPSEEK_API_KEY=sk-...

# 3. 起服务
python3 server.py            # http://127.0.0.1:8000
python3 server.py --selftest # 只测库和工具，不联网
```

## 文件

| 文件 | 作用 |
|---|---|
| `server.py` | 标准库 HTTP 服务 + DeepSeek function calling + 只读查库 |
| `index.html` | 唯一网页（原生 HTML/CSS/JS，无框架） |
| `skills/shuangxiu-teller/` | 重组后的 skill：`SKILL.md` 索引 + `what-it-does.md` / `how-to-maintain.md` / `principles.md` |
| `.env.example` | 环境变量样例，不含真实密钥 |

## 数据流

网页 → `POST /api/ask` → 服务器带工具清单调 DeepSeek → 模型请求工具
（`search_shuangxiu` / `company_detail` / `list_by_category` / `list_by_evidence` /
`db_stats`）→ 服务器只读查 `shuangxiu.db` 并把行回给模型 → 模型给结论，
服务器把命中的公司同时作为引用卡片返回给页面。

## 边界

只反映**公开来源的描述**，非用工事实认定、非穷举；企业作息以其官方最新说明为准。
`DEEPSEEK_API_KEY` 只从环境变量读取，`.env` 已被 `.gitignore` 忽略。
