# 2026-11-25 三平台桌面发布（v0.26.16）

使用当前工作区全部已授权游戏修改，包含中文搜索、联系人、推理引导、单线门禁、小地图迷雾和长文本分页。未回退、统一提交或清理之前的未提交修改，旧版本包保留。

复现命令：`tools/export.sh --output build/release-v0.26.16-20261125`。

产物目录：build/release-v0.26.16-20261125，三个thief-sim-v0.26.16-{windows,linux,macos}.zip。每包含中文说明，不需要安装Godot；SHA256SUMS和source-manifest记录文件及工作区指纹。

| 平台 | 交付 | 实际核验 | 尚未核验 |
| --- | --- | --- | --- |
| Windows | x86_64 exe | 官方模板导出、ZIP CRC、PE机器类型与哈希 | Windows宿主运行 |
| Linux | x86_64 ELF | 导出、ZIP CRC、ELF机器类型、执行权限；导出程序headless启动90帧退出0 | 发行版/桌面差异与音频听感 |
| macOS | Universal 2 .app，Intel+Apple Silicon | 导出、ZIP CRC、Info.plist版本/标识、两架构Mach-O、执行权限、两架构签名载荷及CodeResources | macOS宿主运行、系统签名验证与Gatekeeper首次打开 |

macOS使用Godot内置ad-hoc临时签名，未使用开发者证书、未提交Apple公证。原Godot ZIP条目信息原样保留后再加入包外中文说明，避免丢失.app内可执行权限；不修改已签名.app内容。首次打开方式见包内说明，不建议关闭全局Gatekeeper。

启用rendering/textures/vram_compression/import_etc2_astc是Godot通用/ARM导出的必需条件；首次预检因缺少该配置失败，补齐后重新导出成功。不修改玩法/美术、不更换资源或降低测试门槛。

依据：Godot[macOS导出文档](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html)与[运行说明](https://docs.godotengine.org/en/stable/tutorials/export/running_on_macos.html)。

原始导出日志、结构检查package-checks.json、Linux启动日志及最终verify日志分别保存。本记录不把交叉导出成功当成Windows/macOS实机验收通过。

最终tools/verify.sh --visual全部25阶段通过，56张截图在既有阈值内通过；未改动视觉基线。
