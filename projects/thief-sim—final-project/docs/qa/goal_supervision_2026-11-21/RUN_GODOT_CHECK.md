# run_godot_check 实现说明与验证（G12，#910）

日期：2026-11-21。作者：art。范围：`tools/run_godot_check.py`、`tests/test_run_godot_check.py`。未修改 `verify.sh`、共享 `src/`、CHANGELOG。未启动 Godot，未运行全量 verify。

## 行为
- 命令输出（stdout 与 stderr 合并）逐行实时转发，并保留原退出码。
- 清理以整个进程组为准（#924）：组长收到 SIGTERM 退出后，仍检查同组成员；孙进程若忽略 TERM，则升级为 SIGKILL。
- 检测到致命标记 `SCRIPT ERROR:` 或 `ERROR: Failed to load script` 后，命令还可输出 `--fatal-grace` 秒（默认 2 秒）的上下文，然后只清理自己的进程组（`start_new_session`，pgid == pid）：先 SIGTERM，等 1 秒，仍未退出则 SIGKILL。
- 致命后返回非零：子进程自身非零则原样返回，否则返回 3（`FATAL_EXIT`），即使子进程以 0 退出也不算通过。
- 不匹配 `Parse JSON failed` 等其他错误，不误杀。
- 不使用普通超时，慢测试不会被截断。
- 异常与中断（#924）：转发过程中的任何异常，或包装进程收到 SIGINT，都会在 `finally` 中只清理自己的进程组，回收读线程与管道；CLI 对 SIGINT 返回 130，命令无法启动返回 127。
- SIGTERM（#933）：CLI 在主线程内临时安装自己的 SIGTERM 处理器，收到后转入同一清理路径并返回 143；退出前恢复原处理器，不改变调用者的全局信号行为。清理阶段收到的 TERM 被忽略，避免清理被打断。

## 测试（真实启动 Python 子进程，不启动 Godot）
| 用例 | 预期 |
|---|---|
| 正常输出 + 0 退出 | 返回 0，输出转发 |
| 非零退出 | 原样返回 5 |
| `Parse JSON failed` + 0 退出 | 返回 0，未标记致命 |
| 致命标记 + 永睡 | 返回非零，上下文保留，耗时 < 10 秒，子进程已终止 |
| 致命标记 + 0 退出 | 返回 3 |
| 致命标记 + 自身退出 7 | 原样返回 7 |
| 组外同伴进程 | 不被杀 |
| 组内孙进程 | 被清理 |
| CLI 缺少命令 | 报错退出 |
| 组长正常退出、同组孙进程忽略 TERM | 孙进程被 SIGKILL 清理；组外同伴存活 |
| 转发时输出异常 | 异常向上抛出，子进程组被清理 |
| 包装进程收到 SIGINT | 返回 130，子进程被清理 |
| 包装进程收到 SIGTERM（外层 timeout 常用） | 返回 143，子进程被清理，组外同伴存活 |
| 命令不存在 | 返回 127 |

## 验证记录
- 命令：`PYTHONPATH=tools/demo_lib python3 -m pytest tests/test_run_godot_check.py -v`
- 结果：14 passed，约 3.5 秒。原始日志：`run_godot_check_pytest.log`（以 `-W error::ResourceWarning` 运行）。
- 无 pytest 的系统解释器：`python3 -X dev -W default -m unittest discover -s tests -p test_run_godot_check.py -v`，14 项通过，0 条警告。日志：`run_godot_check_unittest.log`。
- 稳定性：pytest 连续 3 次通过；测试结束后无残留子进程。

## 限制
- 只识别两个致命标记。其他新出现的引擎错误格式需要单独加入 `FATAL_MARKERS`。
- 依赖 POSIX 的进程组语义（`os.killpg`）；Windows 下未验证。
