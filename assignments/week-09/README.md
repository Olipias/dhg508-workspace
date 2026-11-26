# Week 9 · Situate and Explain Your AI Design

## 我做了什么

把 week 8 的迁陵模拟改成一个**验尸定案**的模拟：新令史喜第一天上班，仓里死了个吏，叫丙；里典说是上吊。玩家要验尸、查账、问丙妻和里典，最后在 **自杀 / 贼杀 / 斗杀 / 死难审** 里选一个，写一份守丞能接受的案卷。

这个星期的作业不是再做一遍模拟，而是把它放进学术讨论，做 **10 分钟 Reslides 展示**，并解释技术栈。

**证据门**：物件只给线索；后脑伤要问仓啬夫，送郡时间要问邮人，丙妻/里典的口供也各有 NPC；证据在 NPC 回答后才入案卷。每个判法都至少要和一个 NPC 问到关键证据。

最终论证是一条递进：**秦代勘验有程序**（周敏華）→ **游戏用 configurative / procedural rhetoric 让规则成为历史论证**（Clyde, Hopkins & Wilkinson）→ **把程序的可争议性做成玩法**（Gluzman）。

## 链接

- **模拟**：[`projects/qin_qianling_sim/`](../../projects/qin_qianling_sim/)
- **网页版**：`python3 server/web_server.py --host 0.0.0.0` → `http://127.0.0.1:8788`
- **展示大纲**：[`slides.md`](slides.md)
- **PDF 版**：[`deck.pdf`](deck.pdf)
- **演讲稿**：[`speech-script.md`](speech-script.md)
- **设计文件**：[`design-document.md`](design-document.md)
- **研究日志**：[`research-journal.md`](research-journal.md)
- **书目**：[`bibliography.md`](bibliography.md)

## 三篇核心文献

1. **周敏華 (2009)**，《封診式‧經死》爰書試探，《東吳中文學報》17: 1–18。DOI：<https://doi.org/10.29460/SJCS.200905.0001>。核心：秦代勘验有细致的程序，每一项都有目的，而且勘验过程已经与司法程序相结合（摘要 p.1）。用来支撑「验尸不是看一眼，是一套必须逐项执行的程序」。
2. **Jerremie Clyde, Howard Hopkins & Glenn Wilkinson (2012)**，“Beyond the ‘Historical’ Simulation: Using Theories of History to Inform Scholarly Game Design,” *Loading...* 6(9): 3–16。OpenAlex：<https://openalex.org/W131687738>。核心：gamic mode of history / procedural rhetoric——游戏通过规则和程序来建构历史叙事，而不是只做“历史主题的模拟”。用来支撑「案卷格式、证据门槛、驳回规则本身就是论证」。
3. **Renard Gluzman (2025)**，“Those Who Do Not Learn History Are Doomed to Play It,” *Proceedings of the 3rd International Conference of the ACM Greek SIGCHI Chapter*。DOI：<https://doi.org/10.1145/3749012.3749043>。核心：contestability 应成为游戏认识论框架里的结构性条件；证据是碎片化的、可能误导的，结论始终是暂定的。用来支撑「可选证据互相矛盾、死难审、翻案/送郡结局」。

> 说明：你提到的**王均平**那句“秦时犯罪侦查已经有了比较细致的分工和比较科学的程序、方法”，我没有找到可核验的篇名、期刊、年份和页码，所以这次没有引用；周敏華的摘要已经能支撑“秦代勘验有程序”这个史学命题。Clyde & Wilkinson 的完整作者是 Clyde、Hopkins、Wilkinson 三人。Aarseth 1997 只作为 interpretative/configurative 区分的理论脚注。

## 10 分钟结构

| 时间 | 内容 |
|---|---|
| 0:00–0:30 | 封面：这条命被写成哪一种死 |
| 0:30–1:45 | 历史问题与材料 + 史学前提（周敏華） |
| 1:45–3:00 | 玩家流程 + 《经死》“死难审” |
| 3:00–4:45 | 现场 demo：先打开交案卷看空项，再验尸 |
| 4:45–5:55 | 史学命题：秦代勘验是程序 |
| 5:55–7:05 | 媒介论证：电影看 / 游戏配置 |
| 7:05–8:00 | 设计：不可跳过的操作 |
| 8:00–8:45 | 可争议性：结论暂定 |
| 8:45–9:25 | **学术意义：三个递进** |
| 9:25–9:45 | 技术栈 |
| 9:45–10:00 | 贡献、限制、收尾 |

## 现在跑起来了

本机已装 **Node v22.23.4**，Reslides 在 `~/.cache/opencode-tools/reslides`，dev server 在：

- 幻灯片：`http://localhost:3030/`
- 讲者模式：`http://localhost:3030/#/presenter/`
- 概览：`http://localhost:3030/#/overview/`

预览图在 [`preview/`](preview/)：`01_cover.jpg`（封面）、`02_route.jpg`（流程/不可跳过）、`03_verdicts.jpg`（四种判法/可争议性）、`04_demo.jpg`（iframe demo）、`05_program.jpg`（设计：程序逼你操作）、`06_academic.jpg`（学术意义：三个递进）。dev server 直接读仓库里的 `slides.md`，改完自动热更新。

## 怎么放 Reslides

```bash
git clone https://github.com/boan-anbo/reslides.git
cd reslides
npm run setup
npm run dev
```

把本目录的 `slides.md` 放到 `examples/starter/slides.md`（或按 README 用 `node .../reslides.mjs slides.md --open`），打开 `http://localhost:3030/`；讲者模式 `/#/presenter/`。

## 备注

- 三篇文献的页码/精确位置见 `bibliography.md`；引用以 PDF 页为准。
- 网页 demo 用 `<iframe src="http://localhost:8788/?autostart=1">`；如果现场网络/端口不通，用 `docs/web_02_game.jpg` 截图兜底。
- 本次作业**没有**使用 OpenCode 的简单网页搜索；文献检索走 OpenAlex API，查询记录在 `research-journal.md`。
