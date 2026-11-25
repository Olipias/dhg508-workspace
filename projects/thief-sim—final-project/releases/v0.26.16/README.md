# 《小偷模拟器》最终桌面发布包（v0.26.16 · 2026-11-25）

本目录包含《小偷模拟器》（*Thief Simulator*）DHG508 期末提交的三个平台免安装可执行游戏包（无需安装 Godot 引擎，解压即可运行）：

| 平台 | 文件名 | 架构 | SHA256 |
| --- | --- | --- | --- |
| **Windows** | `thief-sim-v0.26.16-windows.zip` | `PE x86_64` | `2a215769d439f2c6f919dde8d0703683f9f8281bba2c8e5dc06c91d74887428e` |
| **Linux** | `thief-sim-v0.26.16-linux.zip` | `ELF x86_64` | `c150f747abbef54391448fea58d26040caad9fbde1cf45def2008a4d178ece3a` |
| **macOS** | `thief-sim-v0.26.16-macos.zip` | `Universal 2` (`x86_64` + `arm64` Apple Silicon) | `19167c6637259813d9b8f84aa970358230ef97c95c408353fdb4fd944debacd2` |

## 校验与复现

- 校验文件：`SHA256SUMS.txt`
- 构建源码清单：`source-manifest.json`
- 重新导出命令（在项目根目录）：`./tools/export.sh --output build/release-v0.26.16-20261125`
- 验收记录：见 `../../docs/qa/desktop_release_2026-11-25/README.md`
