# Week 11 · Final End-to-End Run, Overleaf Design Paper & Post-Mortem

本项目独立仓库地址：<https://github.com/Olipias/thief-sim>  
本工作区期末交付总目录：[`projects/thief-sim—final-project/`](../../projects/thief-sim—final-project/)（Release `v0.26.16`，2026-11-25）

## 期末交付快速入口

| 交付项 | 文件路径 | 说明 |
|---|---|---|
| **项目总览 README** | [`projects/thief-sim—final-project/README.md`](../../projects/thief-sim—final-project/README.md) | 运行方式、测试结果、史料边界与 AI 使用说明 |
| **三平台免安装可执行包** | [`releases/v0.26.16/`](../../projects/thief-sim—final-project/releases/v0.26.16/) | Windows / Linux / macOS 封版发行包 + `SHA256SUMS.txt` |
| **设计论文 PDF（最终版）** | [`paper/design-paper.pdf`](../../projects/thief-sim—final-project/paper/design-paper.pdf) | 4 页、约 1,300 词，`biblatex-chicago` + XeLaTeX 编译，含 6 个小节与 Post-Mortem |
| **Overleaf 完整源包** | [`paper/overleaf-final.zip`](../../projects/thief-sim—final-project/paper/overleaf-final.zip) | 直接上传 Overleaf，Compiler 选 **XeLaTeX** 即可一键重编 |
| **LaTeX 源码与参考文献** | [`paper/main.tex`](../../projects/thief-sim—final-project/paper/main.tex)、[`paper/references.bib`](../../projects/thief-sim—final-project/paper/references.bib) | 含学术文献与一手馆藏史料，人工核查见 [`paper/SOURCE_CHECK.md`](../../projects/thief-sim—final-project/paper/SOURCE_CHECK.md) |
| **单一事实源证据表（CSV → TeX）** | [`paper/evidence.csv`](../../projects/thief-sim—final-project/paper/evidence.csv) → [`make_evidence_table.py`](../../projects/thief-sim—final-project/paper/make_evidence_table.py) → [`evidence-table.tex`](../../projects/thief-sim—final-project/paper/evidence-table.tex) | 同步副本位于 [`data/evidence.csv`](../../projects/thief-sim—final-project/data/evidence.csv) |
| **架构示意图** | [`paper/schematic.png`](../../projects/thief-sim—final-project/paper/schematic.png) / [`docs/schematic.png`](../../projects/thief-sim—final-project/docs/schematic.png) | 已嵌入 `main.tex` |
| **自动化验收与文档** | [`docs/plan.md`](../../projects/thief-sim—final-project/docs/plan.md)、[`docs/user-feedback.md`](../../projects/thief-sim—final-project/docs/user-feedback.md)、[`docs/SOURCES.md`](../../projects/thief-sim—final-project/docs/SOURCES.md) | `tools/verify.sh --visual` 25 阶段全绿（含 56 张视觉基线截图） |

## 对应 Week 11 最终储存库检查清单

- [x] `README.md`：包含免安装包入口、源码运行与一键测试指令、史料边界与 AI 工具说明
- [x] `docs/plan.md`、`docs/schematic.png`、`docs/user-feedback.md`、`docs/SOURCES.md`
- [x] `data/evidence.csv` 与 `paper/evidence.csv` 单一事实源，经 `make_evidence_table.py` 自动生成 `paper/evidence-table.tex`
- [x] `src/` & `tests/`：干净源码与全量通过的 25 阶段自动化测试套件
- [x] `paper/`：`main.tex`（`biblatex-chicago`）、`references.bib`、`design-paper.pdf`、`overleaf-final.zip`
- [x] 独立开发仓库：<https://github.com/Olipias/thief-sim>（本工作区 `projects/thief-sim—final-project/` 为期末封版与论文整合提交版）
