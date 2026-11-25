#!/usr/bin/env python3
"""为Godot三平台导出附中文说明，保留Mac ZIP中的可执行权限与签名。"""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

root = Path(sys.argv[1])
version = sys.argv[2]
common = f"""小偷模拟器 v{version} / 桌面试玩版
三个版本均包含游戏运行环境，无需安装Godot。

操作：WASD/方向键移动，E交互，P手机，B背包，Esc返回。
开场Space/E推进，Skip跳过；长对白和展签E/Enter翻页。
Tab/R进入规划，人物与守卫一起暂停；空格执行，方向键/E接管。
被发现后按E/空格回退，保留路线供修改。

流程：教学带面具撤离→安全屋书桌E→电脑搜索文物名称和编号→
聊天给阿岚发名字索取布展资料→推理板手动连材料并选结论→
同一目标外貌/展区两项完成后，手机委托准备→房门E出发。
双羊尊检索编号1936,1118.1；WSL关键词可用shuangyangzun+空格选词。
普通物品存箱、手机预约买家、取出后到门口交货；主要文物仅走剧情交付。

保留旧存档，不用重置；请退出旧进程再启动新版。
标题“声明与说明”集中列出史料来源、虚构边界和许可。
学生原型，不将本次打包或自动检查等同于所有设计/真人验收完成。
"""
platform_notes = {
    "windows": "Windows x86_64：解压后双击thief-sim.exe。\n",
    "linux": "Linux x86_64：解压后执行 chmod +x thief-sim.x86_64，再 ./thief-sim.x86_64。\n无音频服务的WSL可加 --audio-driver Dummy。\n",
    "macos": "macOS通用包（Intel x86_64 / Apple Silicon arm64）：解压后将.app拖入“应用程序”再打开。\n本包使用临时签名、未经Apple公证；首次拦截时可在系统设置→隐私与安全性选择“仍要打开”，或在Finder中Control点击应用→打开。\n不需要关闭整个Gatekeeper。参考：https://docs.godotengine.org/en/stable/tutorials/export/running_on_macos.html\n",
}
archives = []
for platform in ("windows", "linux", "macos"):
    note = common + "\n" + platform_notes[platform]
    (root / platform / "试玩说明.txt").write_text(note, encoding="utf-8")
    output = root / f"thief-sim-v{version}-{platform}.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as dest:
        if platform == "macos":
            with zipfile.ZipFile(root / platform / "thief-sim-macos.zip") as source:
                assert source.testzip() is None
                for info in source.infolist():
                    dest.writestr(info, source.read(info.filename))
        else:
            binary = "thief-sim.exe" if platform == "windows" else "thief-sim.x86_64"
            dest.write(root / platform / binary, binary)
        dest.writestr("试玩说明.txt", note)
    with zipfile.ZipFile(output) as check:
        assert check.testzip() is None
    archives.append(output)
(root / "SHA256SUMS.txt").write_text("".join(
    hashlib.sha256(f.read_bytes()).hexdigest() + "  " + f.name + "\n" for f in archives
))
files = [Path("project.godot"), Path("export_presets.cfg")] + sorted(Path("src").rglob("*.gd")) + sorted(Path("src").rglob("*.tscn"))
(root / "source-manifest.json").write_text(json.dumps({
    "release": version,
    "source": "current working tree including authorized uncommitted changes",
    "sha256": {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
}, ensure_ascii=False, indent=2) + "\n")
for f in archives:
    print(f"{f}: {f.stat().st_size / 1048576:.1f} MiB")
