# E 批电脑调查链 · 交接与证据（2026-11-21）

## 已实现范围

- `src/data/investigation.gd`：三条主线资料、问题、关系与事实元数据；双羊尊/圣甲虫/注壶均 `ready=true`。
- `src/ui/computer_screen.gd`：浏览器 / 档案库 / 邮件 / 聊天 / 推理板标签页。
- `src/ui/investigation_board.gd`：真实鼠标拖卡 → 中央文字档案连线 → 关系选择 → 错误反馈/重试；位置与连线写入 `story_flags` 字符串，读档恢复。
- `tests/test_investigation_board.tscn`：**34/34**。
- `test_input_flow`：**316/316**（含电脑 E 打开、浏览器/档案检索、三线聊天邮件、现场便条不赠送、板面挂载、ESC 关闭）。

## 三线资料链

| 线 | 档案检索 | 类型/研究网页 | 布展邮件（聊天） | 现场便条 |
|---|---|---|---|---|
| 双羊尊 | `1936,1118.1` → `zun_archive` | 搜索“双羊尊” → `zun_tech` | “双羊尊 / 1936,1118.1 / C-17” → `inv_zun_delivery` | `inv_zun_service`（不在电脑赠送） |
| 圣甲虫 | `10.130.1650` → `scarab_archive` | 搜索“圣甲虫” → `scarab_type` | “圣甲虫 / 10.130.1650 / E-09” → `inv_scarab_delivery` | `inv_scarab_service`（不在电脑赠送） |
| 注壶 | `VM-GR-25-012` → `askos_archive` | 搜索“注壶”或“阿克罗蒂里” → `askos_type` | “注壶 / VM-GR-25-012 / G-04” → `inv_askos_delivery` | `inv_askos_service`（不在电脑赠送） |

事实元数据：双羊尊 C-001-F01~F05；圣甲虫 C-002-F01~F03；注壶 C-003-F01~F04 + 矩阵 AK-04/05/06。游戏内布展/便条用 X-* 映射，不显示给玩家。

## 现场挂接接口（交给 museum/Main 接线，不在本批改）

建议在 museum 的现场交互点读取后调用：

```gdscript
Game.set_story_flag("inv_zun_service")     # 东侧装卸道 C-17 搬运小车/服务门门牌
Game.set_story_flag("inv_scarab_service")  # 北侧服务门 E-09 展柜门牌
Game.set_story_flag("inv_askos_service")   # 西侧服务门 G-04 展柜门牌
```

点位清单（与布展单一致）：

- 双羊尊：东门内侧 C-17 搬运小车；东侧装卸道；任务提示“下一处：青铜厅内侧临时展位”。
- 圣甲虫：北侧服务门 E-09；任务提示“下一处：埃及厅 E-09 展柜”。
- 注壶：西侧服务门 G-04；任务提示“下一处：希腊厅 G-04 展柜”。

接线约束：

- 现场便条/门牌只能由实际探索交互设置，聊天/电脑不得赠送。
- 读到门牌只落下“待找地点/已知门牌”，不自动生成全图或目标位置。
- 布展单只给局部关系；未知区域仍受迷雾与规划门禁限制。
- 实际点位接入前，三线在安全屋电脑内可独立运行，不阻塞彼此。

## 未完成

- museum/Main 现场触发、门牌实体与点位接入（需与地图生成/F 批稳定 ID 一起做）。
- 三线视觉截图与 `--visual` 人眼检查。
- 新对白按 `stop-slop` / Humanizer-zh 的实际读取审校记录；本文件不声称整稿已确认。
