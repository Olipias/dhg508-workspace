# DHG508 终版设计论文与 Overleaf 源码包（v0.26.16）

日期：2026-11-25。对应最终游戏发布包 `v0.26.16`（Windows / Linux / macOS 三平台桌面版）及 DHG508 Week 11 期末论文要求。正文已通过 `stop-slop` 与 `Humanizer-zh` 双重审校，消除空泛铺垫、假对比、被动无主语和机械排比，保留准确的证据层级（`据 / 推断 / 设`）与工程实现细节。

## 文件清单

- `design-paper.pdf`（及同步副本 `design-paper-draft.pdf`）：XeLaTeX + Biber 编译生成的 4 页美化版最终 PDF（正文约 1,250 英文词，芝加哥注释—书目制 `biblatex-chicago`）。
- `overleaf-final.zip`（及同步副本 `overleaf-draft.zip`）：可直接上传 Overleaf 编译的完整源码压缩包（含 `main.tex`、`references.bib`、`evidence.csv`、`make_evidence_table.py`、`evidence-table.tex`、`schematic.png`）。
- `main.tex`：LaTeX 主文档（含全部六个章节、架构图 Figure 1、自动生成的证据表 Table 1、芝加哥脚注与参考文献列表）。
- `draft.md`：与 `main.tex` 完全同步的英文 Markdown 源稿（由 `build_draft.py` 自动转换为 `main.tex`）。
- `references.bib`：3 项真实可查的学术文献（Chapman 2012、McCall 2012、Wang & Priewe 2013）+ 2 项一手机构馆藏档案（大都会博物馆 `10.130.1650`、UNESCO `VM-GR-25-012`）。
- `evidence.csv` → `make_evidence_table.py` → `evidence-table.tex`：五栏结构化证据表（`claim,evidence,locator,level,limit`），由官方脚本自动生成，不手敲 LaTeX 表格行。
- `schematic.png`：系统模块与史料边界架构图（同步保存在 `docs/schematic.png`）。
- `SOURCE_CHECK.md`：全部文献与一手档案的真实性核查与定位记录。

## 在 Overleaf 上编译与美化指南

1. 打开 [Overleaf](https://www.overleaf.com/project) → 点击 **New Project** → **Upload Project**。
2. 上传 `paper/overleaf-final.zip`。
3. 点击左上角 **Menu** → 将 **Compiler** 设为 **`XeLaTeX`**（必选，以支持 `xeCJK` 中文“据/推断/设”及 `biblatex-chicago`）。
4. 点击 **Recompile**，即可生成与本地 `paper/design-paper.pdf` 一致的 4 页学术排版 PDF。

## 本地一键重编译命令

在仓库根目录执行：

```bash
python3 paper/make_evidence_table.py
python3 paper/build_draft.py
cd paper
mkdir -p .build
xelatex -interaction=nonstopmode -halt-on-error -output-directory=.build main.tex
biber .build/main
xelatex -interaction=nonstopmode -halt-on-error -output-directory=.build main.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=.build main.tex
cp .build/main.pdf design-paper.pdf
```
