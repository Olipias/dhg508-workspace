# G13 预演终点与完整记录

复现：无守卫/监控，原地等待2tick，max_ticks=100。旧预演返回100tick，而实际执行在2tick结束；空路线亦会推进世界；起点tick77而预算5时旧循环0tick。旧摘要无法区分move_counter/take_progress/unlock_progress及smoke_count。新增9条断言全部复现失败（before.log）。

修复：预演与执行都在路线完成/首次发现时停止；max_ticks为本次步数预算。完整摘要用var_to_str保留全部快照，按需的steps还包含动作路线与游标。实际Museum.sim_tick_completed在每个权威tick发独立记录，采样不依赖渲染/物理帧轮询。幽灵轨迹重放遵循相同终点。

验证：Godot --headless --log-file /tmp/thief_g13_after_engine.log --script tests/test_sim_preview.gd，56/56（after.log）；真实鼠标/空格动作test_plan_actions.tscn 14/14（actions.log），包括空动作原地路线拒绝执行、不凭空推进世界。测试夹具不是真人游玩或全流程通关。

源修改在并行code提交e2c5e1d中被一并暂存，原提交标题未描述G13；后续版本记录补明。此处专项通过，不用作A批整体通过：test负责接signal与完整steps，继续长路线/多实体/帧率抖动验证；共享总验待统一实跑。
