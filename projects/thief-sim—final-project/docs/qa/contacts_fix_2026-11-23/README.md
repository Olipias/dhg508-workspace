# 通讯录身份串用修复（v0.26.13）

根因：v0.26.12的二分文案判断把所有非恶魔联系人都赋成阿岚介绍。

改动：MissionPhone.CONTACT_LINES逐人维护独立留言，按钮通过bind传入具体联系人；增加阿岚入口。保留原contact_存档键、老猫/希腊联络的原线索效果；留言自动换行，不新增历史主张。

真实事件回归：tests/test_input_flow从手机联系人App进入，先点阿岚，依次点恶魔、老猫、中国追索者、埃及裔学者、希腊文化基金会，再回到阿岚；断言姓名/独立身份/仅阿岚自称阿岚/对应旗标/六份内容不同。专项完整输入流367项通过，日志input-flow.log。

六人实际窗口截图已目视检查，正文均在640×360内；contacts-overview.png为检查合图。截图不是盲测或真人反馈。

试玩：退出旧游戏进程再运行当前源码./play.sh --audio-driver Dummy，或使用build/contacts-fix-v0.26.13中的新桌面包；旧包及已打开的进程不热更新。存档无需重置。

最终tools/verify.sh --visual全部25阶段通过，50张截图在原阈值内通过。Windows/Linux修复包已导出，Linux程序headless启动检查退出0；Windows宿主未执行实机测试。
