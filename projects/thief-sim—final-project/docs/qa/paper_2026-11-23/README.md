# 2026-11-23试玩与论文初稿验证

当前工作区HEAD f555224，含此前未提交修改；源码摘要见source-state.json，不能把HEAD当成全部来源。

- 游戏：play.sh --audio-driver Dummy --log-file /tmp/thief-paper/game.log，在DISPLAY=:0打开最新源码可见窗口；启动后核实Godot进程2313，未跑旧导出包。静音启动，不改存档或自动开始新游戏。
- 全量：TMPDIR=/tmp/thief-paper/verify tools/verify.sh，退出0，23阶段通过，完整verify.log；包含编译、逻辑、原生输入、存档、进度、预演、经济闭环、推理板、场景、monkey和冒烟。故意损坏JSON输出按原门禁既有规则处理，无新增允许项。
- 论文：正文生成器报告1973英文词；证据表由CSV生成7行；XeLaTeX→Biber→XeLaTeX编译并复跑，最终6页。日志latex-final.log/biber.log，无未定义引文、缺字或越界行。pypdf核对六节、书目与末页内容；结构图单独目视检查。
- PDF未安装额外渲染器，未把文本提取检查冒充逐页截图目视校对；作者仍需审阅PDF全文。Overleaf源包已备，不声称已上传账户。
- 没有本轮游戏代码/画面修改，不以论文或引擎单测推断真人学习效果。未导出新试玩包、未完成新档完整通关或两位外部试玩，不标这些通过。
