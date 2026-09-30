#!/usr/bin/env python3
"""用 Render 公共 API 创建「双休购」Web Service（原生 Python，free 计划）。

前置：
  1) 已在 Render 用 GitHub 登录，并授权 Render 访问本仓库（fork）。
  2) export RENDER_API_KEY=rnd_...   （https://dashboard.render.com/u/settings?add-api-key）
  3) export DEEPSEEK_API_KEY=sk-...  （用于注入服务环境变量；不会打印）

用法：
  python3 code/deploy_render.py --check                 # 只看 owners/repos 是否可达
  python3 code/deploy_render.py                         # 创建（默认仓库/分支/名称）
  python3 code/deploy_render.py --region singapore --name shuangxiu-app --wait

环境变量：RENDER_API_KEY(必填)、DEEPSEEK_API_KEY(必填)、
          RENDER_REPO(可选，默认本仓库 fork)、RENDER_BRANCH(默认 main)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.render.com/v1"
KEY = os.environ.get("RENDER_API_KEY", "")
DEFAULT_REPO = os.environ.get(
    "RENDER_REPO", "https://github.com/Olipias/dhg508-workspace"
)
BUILD = (
    "python3 assignments/week-04/code/seed_data.py && "
    "python3 assignments/week-04/code/build_db.py"
)
START = "python3 assignments/week-05/server.py"


def call(method: str, path: str, body: dict | None = None):
    if not KEY:
        sys.exit("缺少 RENDER_API_KEY（见文件头注释）")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode() or "null"
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"Render API HTTP {e.code} {path}: {detail[:800]}") from e


def owners() -> list[dict]:
    out = call("GET", "/owners?limit=20")
    return out


def repos(owner_id: str) -> list[str]:
    out = call("GET", f"/repos?ownerId={owner_id}&limit=100")
    return [item["repo"] for item in out]


def existing_services(owner_id: str) -> list[dict]:
    out = call("GET", f"/services?ownerId={owner_id}&limit=100")
    return [item["service"] for item in out]


def create_service(owner_id: str, name: str, repo: str, branch: str, region: str) -> dict:
    deepseek = os.environ.get("DEEPSEEK_API_KEY", "")
    if not deepseek:
        sys.exit("缺少 DEEPSEEK_API_KEY（用于注入服务环境变量）")
    env = [
        {"key": "HOST", "value": "0.0.0.0"},
        {"key": "RATE_LIMIT_PER_MIN", "value": "20"},
        {"key": "DEEPSEEK_API_KEY", "value": deepseek},
    ]
    body = {
        "type": "web_service",
        "name": name,
        "ownerId": owner_id,
        "repo": repo,
        "branch": branch,
        "autoDeploy": "yes",
        "serviceDetails": {
            "runtime": "python",
            "plan": "free",          # 关键：不写会默认成付费
            "region": region,
            "envSpecificDetails": {"buildCommand": BUILD, "startCommand": START},
            "envVars": env,
        },
    }
    return call("POST", "/services", body)


def wait_for_deploy(service_id: str, deploy_id: str, timeout: int = 600) -> str:
    start = time.time()
    last = ""
    while time.time() - start < timeout:
        d = call("GET", f"/services/{service_id}/deploys/{deploy_id}")
        status = d.get("status", "?")
        if status != last:
            print(f"  deploy status: {status}")
            last = status
        if status in ("live", "build_failed", "update_failed", "canceled", "pre_deploy_failed"):
            return status
        time.sleep(8)
    return "timeout"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--owner", default="")
    ap.add_argument("--name", default="shuangxiu-app")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--branch", default=os.environ.get("RENDER_BRANCH", "main"))
    ap.add_argument("--region", default="singapore",
                    choices=["singapore", "oregon", "ohio", "virginia", "frankfurt"])
    ap.add_argument("--wait", action="store_true")
    args = ap.parse_args()

    own = owners()
    if not own:
        sys.exit("该账号没有可用的 workspace（owner）。")
    owner_id = args.owner or own[0]["owner"]["id"]
    print(f"owner: {owner_id}  ({own[0]['owner'].get('name','')})")

    if args.check:
        rs = repos(owner_id)
        print(f"可访问的仓库 {len(rs)} 个；本仓库在列？ {args.repo in rs}")
        for r in rs[:20]:
            print("  -", r)
        return 0

    if args.repo not in repos(owner_id):
        sys.exit(
            "该仓库未授权给 Render。请到 Render Dashboard → Account Settings → "
            "GitHub，授予对本 fork 仓库的访问权限后重试。"
        )

    for s in existing_services(owner_id):
        if s["name"] == args.name:
            url = (s.get("serviceDetails") or {}).get("url", "")
            print(f"已存在同名服务：{args.name}  {url}\n{s.get('dashboardUrl','')}")
            return 0

    print(f"创建服务 {args.name}（runtime=python, plan=free, region={args.region}）…")
    res = create_service(owner_id, args.name, args.repo, args.branch, args.region)
    svc = res.get("service", {})
    dep = res.get("deployId", "")
    print("serviceId:", svc.get("id"))
    print("dashboard:", svc.get("dashboardUrl"))
    print("url:", (svc.get("serviceDetails") or {}).get("url"))
    if args.wait and dep:
        st = wait_for_deploy(svc["id"], dep)
        print("final:", st)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(e, file=sys.stderr)
        raise SystemExit(1)
