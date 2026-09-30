#!/usr/bin/env python3
"""把「双休购」app 打包上传到 Hugging Face Space（Docker SDK，免卡公网）。

前置：
  1) HF 账号 + 写权限 token：https://huggingface.co/settings/tokens
  2) export HF_TOKEN=hf_...           （只放环境变量/.env，不进 Git）
  3) export DEEPSEEK_API_KEY=sk-...   （作为 Space Secret 注入，不打印）
  4) 本机安装：pip install huggingface_hub

用法：
  python3 code/deploy_hf.py                 # 创建/更新 Space 并上传
  HF_SPACE_NAME=shuangxiu-app python3 code/deploy_hf.py

产物：https://huggingface.co/spaces/<user>/<name>
     https://<user>-<name>.hf.space
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
W5 = HERE.parent
W4 = W5.parent / "week-04"


def assemble(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    # HF 模板
    shutil.copy(W5 / "hf_space" / "README.md", dest / "README.md")
    shutil.copy(W5 / "hf_space" / "Dockerfile", dest / "Dockerfile")
    # 应用
    app = dest / "app"
    app.mkdir()
    shutil.copy(W5 / "server.py", app / "server.py")
    shutil.copy(W5 / "index.html", app / "index.html")
    shutil.copytree(W5 / "skills", app / "skills")
    # week-04 建库输入（只用 CSV + build_db.py，不需要 seed_data）
    (dest / "week-04" / "code").mkdir(parents=True)
    shutil.copy(W4 / "code" / "build_db.py", dest / "week-04" / "code" / "build_db.py")
    (dest / "week-04" / "data").mkdir()
    for f in sorted((W4 / "data").glob("*.csv")):
        shutil.copy(f, dest / "week-04" / "data" / f.name)


def main() -> int:
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        sys.exit("缺少 HF_TOKEN（见文件头注释）")
    deepseek = os.environ.get("DEEPSEEK_API_KEY", "")
    if not deepseek:
        sys.exit("缺少 DEEPSEEK_API_KEY（将作为 Space Secret 注入）")
    name = os.environ.get("HF_SPACE_NAME", "shuangxiu-app")

    try:
        from huggingface_hub import HfApi
    except ImportError:
        sys.exit("请先安装：pip install huggingface_hub")
    api = HfApi(token=token)
    user = api.whoami()["name"]
    repo_id = f"{user}/{name}"
    print("Space:", repo_id)

    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker",
                    exist_ok=True)

    build = Path(tempfile.mkdtemp(prefix="hf_space_"))
    assemble(build)
    print("上传文件：", ", ".join(sorted(p.name for p in build.iterdir())))
    api.upload_folder(repo_id=repo_id, repo_type="space",
                      folder_path=str(build), commit_message="Deploy 双休购 app")

    for key, val in (("DEEPSEEK_API_KEY", deepseek), ("HOST", "0.0.0.0")):
        try:
            api.add_space_secret(repo_id=repo_id, key=key, value=val)
            print("已设置 secret:", key)
        except Exception as e:  # noqa: BLE001
            print(f"设置 secret {key} 失败（可在 Space 设置里手动加）：{e}")

    print("页面: https://huggingface.co/spaces/" + repo_id)
    print("应用: https://" + f"{user}-{name}".replace("_", "-") + ".hf.space")
    print("首次构建约 1–2 分钟；免费 Space 空闲一段时间后会休眠，首次访问冷启动。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
