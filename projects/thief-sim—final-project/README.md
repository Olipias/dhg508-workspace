# 《小偷模拟器》· Thief Simulator — DHG508 期末项目

DHG508 Critical Digital History · 2026-11-25 · Release `v0.26.16`

一款中文 2D 像素潜行与文物调查游戏。玩家调查馆藏记录清楚、但早期流转不明的真实文物，用确定性预演规划潜入路线，最后决定把文物交给恶魔契约，还是交还对应国家的接收人。

本目录是课程期末交付包：三个平台的可执行游戏、设计论文与 Overleaf 源包、完整源码、自动化测试和验收记录。

## 快速入口

| 想做什么 | 去哪里 |
| --- | --- |
| 直接玩 | [`releases/v0.26.16/`](releases/v0.26.16/) — 解压即运行，无需安装 Godot |
| 读设计论文 | [`paper/design-paper.pdf`](paper/design-paper.pdf) — 4 页，约 1,300 词 |
| 在 Overleaf 编译论文 | 上传 [`paper/overleaf-final.zip`](paper/overleaf-final.zip)，编译器选 **XeLaTeX** |
| 看证据表原始数据 | [`paper/evidence.csv`](paper/evidence.csv) → `make_evidence_table.py` → `evidence-table.tex` |
| 跑测试 | `tools/verify.sh --visual`（Godot 4.7） |
| 读史料登记 | [`docs/SOURCES.md`](docs/SOURCES.md) |

## 三个游戏包

`releases/v0.26.16/` 内含免安装桌面版，附中文说明与 SHA256：

| 平台 | 文件 | 架构 | SHA256 |
| --- | --- | --- | --- |
| Windows | `thief-sim-v0.26.16-windows.zip` | PE x86_64 | `2a215769…87428e` |
| Linux | `thief-sim-v0.26.16-linux.zip` | ELF x86_64 | `c150f747…ece3a` |
| macOS | `thief-sim-v0.26.16-macos.zip` | Universal 2（Intel + Apple Silicon） | `19167c66…4debacd2` |

完整哈希见 [`releases/v0.26.16/SHA256SUMS.txt`](releases/v0.26.16/SHA256SUMS.txt)，构建清单见 `source-manifest.json`。macOS 使用 Godot 内置 ad-hoc 签名，未做 Apple 公证。

本项目是原生桌面游戏，不提供网页版，也不需要 Cloudflare 或浏览器自动化。

## 游戏做了什么

**流程**：标题 → 六格签约分镜 → 面具教学 → 可走动的 2D 安全屋 → 电脑调查与手动推理 → 手机准备 → 房门出发 → 博物馆探索与取物 → 安全屋交付剧情。

- **可走动的安全屋**：书桌电脑、文物箱、手机、房门四处实体交互点，取代旧的顶部栏目菜单页。
- **手动推理板**：在电脑里检索馆藏编号、读邮件与聊天、把材料卡拖入证据框并手动选择结论。未确认同一件文物的「外貌特点」与「本次展区」，手机和房门都不放行。
- **确定性预演**：Tab/R 进入规划，人物、守卫、监控与噪音计时一起冻结；预演与执行共用同一固定 tick 内核，同快照逐 tick 一致，失败回退保留路线。
- **两类物品**：普通战利品走「存箱 → 手机预约 → 取货 → 门口交货」换钱买烟雾弹与跑鞋；三件主要文物只走恶魔或对应国家接收人的剧情。
- **长文分页**：对话与展签按字体像素宽度换行分页，640×360 下不越框。

## 史料边界

游戏内每一条历史陈述都归入三档：**据**（有直接文献支持）、**推断**（学界解释）、**设**（本作虚构）。完整声明与来源集中在标题页，正篇不反复插编辑标签。

| 文物 | 真实收藏地 / 记录 | 游戏内虚构部分 |
| --- | --- | --- |
| 商代双羊尊 | 大英博物馆 `1936,1118.1`，1930 年代购自 Eumorfopoulos 旧藏，出土地不明 | 同馆展出、守卫、交付剧情 |
| 心形圣甲虫 | 大都会艺术博物馆 `10.130.1650`，埃及晚期，1910 年 Gould 捐赠 | 同上 |
| 阿克罗蒂里彩绘注壶 | UNESCO `VM-GR-25-012`，锡拉岛阿克罗蒂里西屋出土，失窃经过与现藏不详 | 同上 |

已被移除、不作为史实的包括：1860 年圆明园劫掠传闻，以及早期版本的「文物器灵」对白。

## 测试与验收

`tools/verify.sh --visual` 共 25 个阶段，2026-11-25 在 `v0.26.16` 上全部通过，含 56 张视觉基线截图。

- 逻辑 2,552 项断言；史料边界 `pytest` 11 项
- 确定性预演与真实场景 133 项
- 真实键鼠输入流与长文分页 563 项
- 安全屋经济闭环 33 项；存档兼容 135 项

原始日志在 [`docs/qa/`](docs/qa/)，其中三平台发布记录见 [`docs/qa/desktop_release_2026-11-25/`](docs/qa/desktop_release_2026-11-25/)。

## 用源码运行

需要 Godot 4.7：

```bash
godot .                                        # 启动游戏
tools/verify.sh                                # 全量验证
tools/verify.sh --fast                         # 跳过冒烟与 monkey 的快速子集
godot --headless --script tests/test_logic.gd   # 纯逻辑单测
```

重新导出三平台包：`tools/export.sh --output build/my-release`。

## 目录结构

```
releases/v0.26.16/   三平台可执行包、SHA256、构建清单
paper/               设计论文 PDF、LaTeX 源、Overleaf 包、证据表与出处核查
src/                 游戏源码（场景、模拟内核、数据、UI）
tests/               逻辑/输入/模拟/存档测试与视觉基线
tools/               验证、导出、素材与地图生成脚本
assets/              游戏运行素材（像素图、音效、字体、开场分镜）
docs/                设计文档、史料登记、决策记录与各轮验收日志
data/evidence.csv    证据表副本，对应课程 data/ 约定
```

## 已知局限

Windows 与 macOS 只做了导出与包结构校验，未在对应宿主机实机运行；macOS 未公证，首次打开需按包内说明处理。正式的外部玩家研究尚未进行，论文中不报告学习效果。

## AI 工具使用

游戏机制、史料边界、论文写作与全部引文核查由作者完成。AI 工具用于辅助实现与文字处理：OpenCode、Codex、Claude Code 协助 GDScript 调试与测试脚手架，腾讯混元 3D 用于双羊尊离线转台与特写渲染，`stop-slop` 与 `Humanizer-zh` 清单用于英文润色。详细记录见 [`docs/DECISIONS.md`](docs/DECISIONS.md) 与 [`paper/SOURCE_CHECK.md`](paper/SOURCE_CHECK.md)。

## 更多文档

- [`CHANGELOG.md`](CHANGELOG.md) — 逐版本变更记录
- [`GDD.md`](GDD.md) — 一页纸设计摘要
- [`docs/CONFIRMED_DESIGN.md`](docs/CONFIRMED_DESIGN.md) — 确认方案与实现状态
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — 模块、数据流与不变量
- [`AGENTS.md`](AGENTS.md) — 协作规则与常用命令（面向 agent）
