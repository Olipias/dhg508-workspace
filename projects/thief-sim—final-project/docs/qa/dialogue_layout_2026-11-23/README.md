# 长对话越界修复（v0.26.15）

普通对话与剧情对话共用dialogue_pages.gd：按实际字体像素宽度换行，每页至多3行对白或8行展签；保留原文字和标点，正常长度的英文单词/编号优先整体换行，超长串可折行。不缩小正文，不用裁切隐藏越界文本。

DialogueBox按页显示打字机文本；DialogueTree保持剧本索引与标签不变，读完当前条目的各页才推进goto/set_flag/后续选项。每页提示E/Enter下一页或继续及页码。长选项按同字体换行。底部面板留出姓名、正文与操作提示空间。

真实输入专项75项通过，覆盖长中文、英文姓名、超长ASCII串、馆藏编号和显式换行；检查每行实际字宽、正文/面板/选项视口边界、逐页完整文本、后续旗标不提前触发、结束回调仅一次。分页过程不新增存档字段。

长对白、剧情对白、展签第一页和第二页截图已在640×360布局下目视检查；截图由固定测试状态生成，按键路径由test_input_flow单独覆盖。未将机器检查算作真人阅读体验验收。

涉及文件：src/ui/dialogue_pages.gd、dialogue_box.gd/.tscn、dialogue_tree.gd/.tscn、tests/test_input_flow.gd、tests/test_dialogue_paging.gd/.tscn、tests/screenshot.gd。

新版打包目录：build/dialogue-fix-v0.26.15。退出旧游戏后再启动新包，存档无需重置。Windows宿主实机运行未验证；Linux包另做启动检查。

最终tools/verify.sh --visual全部25阶段通过：真实输入448项（含分页回归75项），56张截图在原阈值内通过；Linux导出程序启动60帧退出0。未放宽测试门槛。
