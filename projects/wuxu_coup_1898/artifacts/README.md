# artifacts/（本目录默认不入 git）

- `NLC416_wuxu_zhengbian_ji.pdf` — 国图扫描《戊戌政變記》整本（8.1 MB，163 页，无文本层）。
  来源：Wikimedia Commons `File:NLC416-13jh000245-44411 戊戌政變記.pdf`。
- `pages/` — 目标页 150 DPI 渲染图（p065/p066/p067/p068/p090/p091/p097/p099）与定位用拼贴图（strips/rstrips/toc/thumbs 页眉条、缩略图网格），均为重建产物。
- 重建：`pymupdf` 渲染 `dpi=150`；缩略图拼贴用 Pillow 生成（每张 42 页缩略图，用于视觉定位章节起始页）。
