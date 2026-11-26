# Week 8 · A Historical Simulation

## 我做了什么

**《迁陵 · 廿六年五月》**：新令史喜的第一天。公元前 221 年，迁陵县。仓里死了个吏，叫丙——一个用《封诊式·经死》模板虚构的案子；里典说是上吊。守丞敦狐把报案拍在你桌上：「你去验。验成自杀，他老婆孩子没事；验成他杀，整个里都要脱层皮。可你要是验错了，脱皮的是你。」你连尸首都没见过。

> **历史教训**：现代法医想弄清「怎么死的」；秦代令史先要弄清「该写成哪一类死」。同一具尸体，写成自杀、贼杀、斗杀、死难审，决定了谁被抓、谁被连坐、谁的账被翻。

> **语言说明**：NPC 说的是现代白话，不是秦代口语；文书保留简牍原文，游戏默认显示「人话版」，点「看原文」随时切回。这样不了解秦制的人也能玩进去，但不会把台词冒充成史料。

![县廷](<../../projects/qin_qianling_sim/docs/03_county.jpg>)

## 先看什么

| 顺序 | 文件 | 看什么 |
|---|---|---|
| 1 | [项目 README](../../projects/qin_qianling_sim/README.md) | 模拟是什么、怎么跑、AI 怎么接 |
| 2 | [为什么不是电影](<../../projects/qin_qianling_sim/research/why-not-film.md>) | 电影拍不出的“跑腿顺序” |
| 3 | [部件—状态—出处表](<../../projects/qin_qianling_sim/research/evidence.md>) | 哪些是 evidenced / inferred / invented |
| 4 | [史料核对日志](<../../projects/qin_qianling_sim/research/verification-log.md>) | 16:9 的校正；经死/法律答问的出处 |
| 5 | [困难与修法](<../../projects/qin_qianling_sim/research/difficulties.md>) | 九个真实卡点，带例子 |
| 6 | [工具分工](<../../projects/qin_qianling_sim/research/tools.md>) | 每个工具做了什么、我核了什么 |
| 7 | [未解决问题](<../../projects/qin_qianling_sim/research/questions.md>) | 还没做完/没核完的 |

## 三分钟路线

1. **县廷**：看里典的报案（`E`）；读《封诊式·经死》的验尸清单。
2. **仓**：验尸（舌出、绳痕、矢溺、后脑淤伤、粮袋血），查账（少了三十石），问仓啬夫。
3. **都乡**：问丙妻（他说「账对不上，他们要拿我顶」）、问里典（他那晚进过仓）、调丙的户籍。
4. **邮亭**：封好案卷，记送郡时间。邮递员得会请你把时间写早半刻——你写不写？
5. **回县廷**：点「交案卷」。选 **自杀 / 贼杀 / 斗杀 / 死难审**；写不写里典/四邻、仓啬夫，也由你。

不懂名词就按 `H` 看「名词小抄」；每一步的「考据」按钮能看原文/出处；`Tab` 看已得材料。

## 网页版（不需要 Godot）

```bash
cd projects/qin_qianling_sim
export DEEPSEEK_API_KEY=sk-...
python3 server/web_server.py --host 0.0.0.0
# 浏览器打开 http://127.0.0.1:8788
```

**不要双击 `web/index.html`**：浏览器会禁止 `file://` 页面读取 `data/*.json`，只会显示一堆没样式的文字。必须通过服务器打开。

同一个 `game/data/*.json`、同一张地图、同一套 NPC prompt；`web/` 是纯 HTML/CSS/JS 的行走/对话/文书/具簿版本。没有 key 时加 `--mock`，回退台词也能走完主链。部署到 Render/Fly 时服务器读 `PORT`，`render.yaml` 已备好。

## 会不会出戏

- 文书默认显示**人话版**，点「看原文」才看简牍原文；`[evidenced]/[inferred]`、简号、URL 全部收进「考据」按钮。
- NPC 说人话，不拽文言文。prompt 明令「不要敢言之、伏惟、之乎者也；短句，像县衙同事」；服务器返回后再查「敢言之/矣/焉得」等腔调，命中就换成回退台词（日志记 `style:*`）。
- NPC 嘴里不会出现「根据史料记载」「简牍记载」「秦代」「秦始皇」「公元前」这类词；命中即换成回退台词（日志记 `meta:*`）。
- 案卷面板只写「已核/待核」；三分表留在 `research/evidence.md`。
- 文书默认「人话版」，点「看原文」切回简牍原文；两张对照图：`docs/02_document.jpg` / `docs/02b_document_original.jpg`。
- 实测：问都乡守嘉「史料上是怎么记你这件案子的？」——模型原本会说「史料是什么」，被守卫换成「你问的是户、是年籍，还是粮？一件一件来。」；问「秦始皇什么时候统一六国」，模型自称「今王」，不提后世。

## 链接

- **模拟工程**：[`projects/qin_qianling_sim/`](../../projects/qin_qianling_sim/)
- **网页版**：[`web/`](../../projects/qin_qianling_sim/web/)
- **运行**：`godot --path projects/qin_qianling_sim/game`；NPC 服务见 README
- **截图**：[`docs/`](../../projects/qin_qianling_sim/docs/)
- **代码**：`game/scripts/`（Godot/GDScript）、`server/npc_server.py`、`tools/gen_art.py`
- **调用日志**：[`logs/npc_calls.jsonl`](../../projects/qin_qianling_sim/logs/npc_calls.jsonl)（121 次计费调用，约 US$0.0510）

## 交付清单

- [x] 仓库链接，带索引（本页）
- [x] 模拟本体：Godot 4.7 工程；`--playtest` 全链通过；截图 8 张 + 地图
- [x] “为什么不是电影”：[why-not-film.md](<../../projects/qin_qianling_sim/research/why-not-film.md>)
- [x] 来源列表 + evidenced/inferred/invented 表：[evidence.md](<../../projects/qin_qianling_sim/research/evidence.md>)
- [x] 每个工具做了什么、AI 做了什么、我核了什么：[tools.md](<../../projects/qin_qianling_sim/research/tools.md>)
- [x] 至少一个真实困难，带例子：[difficulties.md](<../../projects/qin_qianling_sim/research/difficulties.md>)
- [x] 保留 prompt/输入/输出/费用：`logs/npc_calls.jsonl`；API key 只在环境变量，未入 Git
- [x] 大文件在 `artifacts/`（Git 忽略）；截图另放 `docs/`
- [x] 未解决问题：[questions.md](<../../projects/qin_qianling_sim/research/questions.md>)

## 一句话的困难

最难的不是写 Godot，是**把“验尸模板”变成可玩的判断**：《封诊式·经死》只给验尸要点，不给答案；你要自己决定哪些矛盾足够写“死难审”，哪些不够。第二难的是**让模型说人话、又只知道它该知道的**：第一版它开口就是“敢言之”“伏惟”，玩家像在讀另一门课；改完白话 `knowledge` 和 prompt，又加了“文言腔守卫”，它才会说“人确实在我这儿，可户口档案没跟着来，这可不能赖我”。它还会忍不住讲“秦始皇”“编户齐民”，要靠 prompt、`forbidden`、`meta` 守卫、世界判定和回退台词兜住。

## 截图

| | |
|---|---|
| ![开篇](<../../projects/qin_qianling_sim/docs/01_intro.jpg>) | ![里典的报案](<../../projects/qin_qianling_sim/docs/02_document.jpg>) |
| ![AI 对话](<../../projects/qin_qianling_sim/docs/04_dialogue_ai.jpg>) | ![具簿](<../../projects/qin_qianling_sim/docs/05_submission.jpg>) |
| ![网页版](<../../projects/qin_qianling_sim/docs/web_02_game.jpg>) | ![网页版对话](<../../projects/qin_qianling_sim/docs/web_03_dialogue.jpg>) |
