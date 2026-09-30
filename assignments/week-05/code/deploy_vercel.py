#!/usr/bin/env python3
"""用 Vercel REST API 部署「双休购」app（免卡 Hobby，内联上传文件，无需 Git 授权）。

前置：
  1) Vercel 账号（Hobby 免卡）+ token：https://vercel.com/account/tokens
  2) export VERCEL_TOKEN=...
  3) export DEEPSEEK_API_KEY=sk-...      （作为项目环境变量注入，不打印）
  4) 先跑 code/build_vercel.py 生成 vercel/api/_db.py 与 vercel/index.html

用法：
  python3 code/deploy_vercel.py
  VERCEL_PROJECT=shuangxiu-app VERCEL_TEAM_ID=team_xxx python3 code/deploy_vercel.py
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
W5 = HERE.parent
ROOT = W5 / "vercel"
API = "https://api.vercel.com"


def call(method: str, path: str, token: str, body: dict | None = None):
    team = os.environ.get("VERCEL_TEAM_ID", "")
    url = API + path
    if team:
        url += ("&" if "?" in path else "?") + "teamId=" + urllib.parse.quote(team)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"Vercel API HTTP {e.code} {path}: {detail[:600]}") from e


def collect_files() -> list[dict]:
    files = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.name in (".DS_Store",):
            continue
        rel = p.relative_to(ROOT).as_posix()
        files.append({
            "file": rel,
            "data": base64.b64encode(p.read_bytes()).decode(),
            "encoding": "base64",
        })
    return files


def main() -> int:
    token = os.environ.get("VERCEL_TOKEN", "")
    if not token:
        sys.exit("缺少 VERCEL_TOKEN（见文件头注释）")
    deepseek = os.environ.get("DEEPSEEK_API_KEY", "")
    if not deepseek:
        sys.exit("缺少 DEEPSEEK_API_KEY（将作为项目环境变量注入）")
    name = os.environ.get("VERCEL_PROJECT", "shuangxiu-app")

    # 1) 项目（已存在则忽略）
    try:
        call("POST", "/v10/projects", token, {"name": name, "framework": None})
        print("已创建项目:", name)
    except RuntimeError as e:
        if "already exists" in str(e) or "409" in str(e):
            print("项目已存在，复用:", name)
        else:
            raise

    # 2) 环境变量（upsert）
    for k, v in (("DEEPSEEK_API_KEY", deepseek),
                 ("RATE_LIMIT_PER_MIN", os.environ.get("RATE_LIMIT_PER_MIN", "20"))):
        try:
            call("POST", f"/v10/projects/{name}/env?upsert=true", token,
                 {"key": k, "value": v, "type": "encrypted",
                  "target": ["production", "preview", "development"]})
            print("已设置环境变量:", k)
        except RuntimeError as e:
            print(f"设置环境变量 {k} 失败：{e}")

    # 3) 部署（内联文件）
    files = collect_files()
    print(f"上传 {len(files)} 个文件，创建部署…")
    dep = call("POST", "/v13/deployments?forceNew=1&skipAutoDetectionConfirmation=1",
               token, {"name": name, "target": "production", "files": files,
                       "projectSettings": {"framework": None}})
    did = dep.get("id")
    print("deploymentId:", did)

    # 4) 轮询
    st, url = dep.get("readyState", "?"), dep.get("url", "")
    for _ in range(72):
        d = call("GET", f"/v13/deployments/{did}", token)
        st = d.get("readyState", st)
        url = d.get("url", url)
        if st in ("READY", "ERROR", "CANCELED"):
            break
        time.sleep(5)
    print("状态:", st)
    if st != "READY":
        print("部署未成功，可到 Vercel 控制台看构建日志。")
        return 1
    print("应用地址: https://" + url)
    print("健康检查: https://" + url + "/api/health")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
