# 期末简单版封版计划

日期：2026-11-21。依据用户最新指令：其他agent额度耗尽，时间与token紧张；剩余先做简单版，以整个流程能跑通为目标，同时准备课程设计论文。此指令取代OPENCODE_NEXT_PLAN的本轮全量开发排期；完整设计保留为以后待办，不改写为已完成。

## 当前约束

- 范围冻结：不新增模块、不扩馆、不新增工具/美术，不继续向其他付费agent派任务。agent-link worker已停止，Claude仍不调用。
- 保留已有安全屋、交易采购、调查和确定性预演；只修阻断流程、丢档/重复物品、失效按钮和明显文字问题。
- 最小交付优先跑通一条双羊尊主线和至少一个实际可达结局。另两文物及更多结局只保留已能正常工作的部分；未接入入口明确关闭，不显示TODO/占位答案，不用未实现分支卡主线。
- 本轮不以30–50分钟、三人盲测、扩大地图或完整九条结局作为封版开发前置。完整原目标保留为后续工作，不声称通过。

## 简单版必须通的流程

标题指定封面 → q6开场（自动/手动/跳过）→ 教学 → 独立安全屋 → 电脑查看基本资料 → 手机准备 → 房门出发 → 现有展馆取得双羊尊 → 撤离 → 安全屋交付 → 可正常结束。

现有普通战利品 → 入箱 → 手机预约 → 取货 → 门口确认出售 → 手机采购 → 再出门的循环保留并回归，不为简单版重写。现场线索与剧情按最小必要接线完成，复杂调查问题不作为硬门槛。

## 当前证据与仍需核实

- 最近一次独立全量tools/verify.sh：23项返回通过，原始日志/tmp/thief_goal_serial3_verify.log。其Python工具测试曾有ResourceWarning，后续已交修，须复核清洁结果；此日志不证明之后所有工作区修改。
- 安全屋经济真实输入集成33项通过；测试使用传送安排馆内位置，不能充作真人从入口步行完整通关。
- 预演灰盒56、真实动作14、真实场景87、三线板面34项在该次全量中通过；局部绿灯不代表结局、现场接线或论文完成。
- 收尾必须实际从新游戏走通一条完整主线、检查旧档、跑相关回归、检查关键画面、导出干净目录可启动的桌面包，并记录版本。
- 两位外部用户反馈、本人体验与论文中的结果必须真实。未提供的反馈不得补写。

## 课程论文与交付

课程原文：https://github.com/boan-anbo/dhg508-workspace/blob/main/508-coursework/week-11/instructions.md
查阅日期：2026-11-21；原文截止：2026-11-25。

- 约1500–2500英文词、3–6页；Overleaf用XeLaTeX，biblatex-chicago注释书目制，Biber。
- 六部分：Historical Question & Medium；Sources & Scholarly Conversation；Architecture & Boundaries；Evidence Table；Verification & Playtesting；Post-Mortem。
- 至少3项学术研究，另加一手来源；引用与页码实际核查，不把馆藏网页都算作学术研究。
- paper/evidence.csv含claim,evidence,locator,level,limit；level为据/推断/设；脚本生成evidence-table.tex，不能手敲表格行。
- 交付paper/main.tex、references.bib、make_evidence_table.py、evidence.csv、evidence-table.tex、design-paper.pdf；docs/schematic.png和docs/user-feedback.md。
- 至少两位真实外部用户的原始反馈、修复与回归测试；现有开发者反馈不能冒充两位外部用户。
- Post-Mortem可如实讨论规划冻结、预演终点不一致、自动测试漏输入、AI并行协作和范围扩张的困难，以及如何定位、修复和封版。

用户已明确本项目为原生桌面游戏，不需要HTTPS和Playwright。论文按实际Godot与原生测试架构书写，不另开Web模块，也不虚构部署或浏览器测试。

## 2026-11-23用户裁定

用户明确本项目不需要HTTPS和Playwright。本轮交付与paper按原生Godot桌面游戏及原生输入/逻辑测试叙述，不将Web部署/浏览器测试列为开发或论文前置；不虚构这些服务的实施情况。当前请求为打开最新游戏并起草paper，不恢复多agent派单。
