# Week 5 · 双休购 app

把 week-04 的「双休公司/产品」skill 做成一个**谁都能在浏览器打开**的小应用：
一个网页 + 一台本地 Python 服务器；服务器**真实调用 DeepSeek**，让模型用
function calling 去查 `week-04/artifacts/shuangxiu.db`，再据查到的行作答。

## 它长什么样

- 打开页面先看到库的规模与证据分布。
- 输入品牌 / 产品 / 问题（如「安克是双休吗？」「咖啡有哪些双休公司？」）。
- **📷 拍照 / 上传产品**：手机拍照或选图，浏览器端先压缩到 ≤1280px，
  必要时用 `BarcodeDetector` 读条码/二维码；服务器把图交给 DeepSeek 的
  **视觉能力**识别包装上的产品名与公司名，再走查库流程。
- 回来三块：**结论**（模型基于库作答）、**查库动作**（它调了哪些工具）、
  **命中记录**（公司卡片：作息、证据等级、原话、产品、来源链接）。
- 离题问题（如「帮我点一份汉堡王」）按 skill 原则回「前面的区域以后再来探索吧!」。

这不是 demo 的 fixture：`server.py` 里没有写死的答案，每个回答都要先查库。

## 跑起来

```bash
# 1. 先有库（week-04 的生成物，*.db 不入 Git）
python3 ../week-04/code/build_db.py

# 2. 设密钥（见 .env.example；绝不写进会提交的文件）
export DEEPSEEK_API_KEY=sk-...

# 3. 起服务
python3 server.py            # http://127.0.0.1:8000
python3 server.py --selftest # 只测库和工具，不联网
python3 server.py --ask "安克是双休吗？"   # 命令行问一次（联网，真实调用）
```

## 文件

| 文件 | 作用 |
|---|---|
| `server.py` | 标准库 HTTP 服务 + DeepSeek function calling + 只读查库 |
| `index.html` | 唯一网页（原生 HTML/CSS/JS，无框架） |
| `skills/shuangxiu-teller/` | 重组后的 skill：`SKILL.md` 索引 + `what-it-does.md` / `how-to-maintain.md` / `principles.md` |
| `.env.example` | 环境变量样例，不含真实密钥 |

## 数据流

网页 → `POST /api/ask` → 服务器带工具清单调 DeepSeek → 模型请求工具
（`search_shuangxiu` / `company_detail` / `list_by_category` / `list_by_evidence` /
`db_stats`）→ 服务器只读查 `shuangxiu.db` 并把行回给模型 → 模型给结论，
服务器把命中的公司同时作为引用卡片返回给页面。

## 边界

只反映**公开来源的描述**，非用工事实认定、非穷举；企业作息以其官方最新说明为准。
`DEEPSEEK_API_KEY` 只从环境变量读取，`.env` 已被 `.gitignore` 忽略。

## 部署（公网，任何人有链接即可打开）

这是一台普通服务器 + 一个网页，与 opencode 无关。上云后，手机打开链接，
用**系统相机**拍照上传 → 服务器调用 DeepSeek 视觉识别产品/公司 → 查库判别是否双休。

密钥只放平台的环境变量/Secret，**绝不进 Git**；数据库 `*.db` 不入库，
由构建命令或启动时的 `ensure_db()` 从 `week-04/data/*.csv` 重建。

### 方案 A · Vercel Hobby（免卡，推荐）

免信用卡、免费公网 HTTPS。做法：静态 `index.html` + **Python serverless 函数**
（`api/ask.py`、`api/stats.py`、`api/health.py`），数据库以 base64 内嵌进
`api/_db.py`（随函数打包，免文件路径问题）。

1. 生成内嵌数据库与页面（数据变更后重跑）：
   ```bash
   python3 code/build_vercel.py     # 生成 vercel/api/_db.py + vercel/index.html
   ```
2. 推送到 GitHub（`vercel/` 已提交）。
3. Vercel 控制台 → Add New → **Project** → Import 本仓库。
4. **Root Directory** 选 `assignments/week-05/vercel`；Framework 选 **Other**（无需构建命令）。
5. Settings → Environment Variables 加 `DEEPSEEK_API_KEY`（可选 `RATE_LIMIT_PER_MIN=20`）。
6. Deploy → 得到 `https://<project>.vercel.app`，任何人可打开。

也可以用 CLI（需 Node）：`npm i -g vercel && cd assignments/week-05/vercel && vercel --prod`。
函数最长 60 秒（`vercel.json` 已设），超时前会返回。

**已部署（Hobby，免卡）**：https://shuangxiu-app.vercel.app
- 注意：Vercel 新项目默认开启「部署保护（Vercel Authentication）」，需在
  Project → Settings → Deployment Protection 关掉，或由 `deploy_vercel.py` 里
  那样把 `ssoProtection` 置空，公网才能访问。
- 实现注意：Vercel 只把项目根加入 `sys.path`，`/api` 不在其中；各 handler 顶部
  已 `sys.path.insert(0, 所在目录)` 后才能 `from _lib import ...`。

> 说明：Vercel Hobby 声明为个人/非商业用途；课程演示适用。函数冷启动约 1–2 秒。

### 方案 B · Hugging Face Spaces（2026 起 Docker Space 需 PRO）

> 注意：2026 年 HF 政策变更——**Docker/Gradio Space 的免费 `cpu-basic` 需要 PRO 订阅**，
> 只有 Static Space 免费。想用 Space 跑本应用（Python 服务器）需付费。
> 本方案保留给有 HF PRO 的情况；免卡请见下面的替代方案。

Space 用 Docker SDK，端口 7860。
1. 在 https://huggingface.co/settings/tokens 建一个 **write** 权限 token。
2. 放进 `assignments/week-05/.env`：`export HF_TOKEN=hf_...`
3. 部署：
   ```bash
   pip install huggingface_hub
   cd assignments/week-05
   set -a; . .env; set +a
   python3 code/deploy_hf.py
   ```
   脚本自动：建 Space → 上传 `hf_space/`（server + index + skill + week-04 的 CSV）
   → 把 `DEEPSEEK_API_KEY` 设为 Space Secret。
4. 得到 `https://<user>-shuangxiu-app.hf.space`。免费 Space 空闲会休眠，首次访问冷启动几秒。

模板在 `hf_space/`（`README.md` 元数据 + `Dockerfile`）。数据库在镜像构建时由 CSV 重建。

### 方案 C · Render（免费层可用，但别走 Blueprint）

Render 免费层（Hobby）本身 **$0**，但要注意：
- **Blueprint 和公共 API 都会要求先绑一张卡**（API 实测返回 `402 Payment information is required`）。免费层不会扣费，但卡要在档。
- 想完全免卡，可试 **Dashboard → New → Web Service 手动创建**（有时不强制绑卡）；若也被拦，就换免卡平台。
- Render **免费层不支持 Docker 服务**，只支持原生运行时（Python/Node…）。本应用正好是纯 Python。
- 用脚本创建：`assignments/week-05/code/deploy_render.py`（`RENDER_API_KEY` + `DEEPSEEK_API_KEY` 走环境变量）。

手动创建步骤（免卡）：
1. Render → New → **Web Service** → 选本仓库。
2. Runtime：**Python**（不要选 Docker）。
3. Build Command：`python3 assignments/week-04/code/seed_data.py && python3 assignments/week-04/code/build_db.py`
4. Start Command：`python3 assignments/week-05/server.py`（Render 会注入 `PORT`）
5. Instance Type：**Free**。
6. Environment 加：`DEEPSEEK_API_KEY=sk-...`、`HOST=0.0.0.0`、`RATE_LIMIT_PER_MIN=20`。
7. 部署后得到 `https://<name>.onrender.com`，任何人可打开。免费层 15 分钟空闲会休眠，首次访问冷启动约 30–60 秒。

> `render.yaml` 保留作参考；若改用 Blueprint，会被要求绑卡，且要用 `plan: free` + 不挂磁盘。

**其它免卡免费选项**（都支持 Python/容器）：Koyeb 免费实例（0.1 vCPU / 256–512MB，scale-to-zero）、SnapDeploy（512MB，日限部署次数，免卡）、Hugging Face Spaces（Docker，端口改 7860）。免费层通常会休眠/限资源，适合演示。

### 方案 D · Fly.io（Docker）

仓库根已有 `Dockerfile` 与 `fly.toml`：
```bash
# 在仓库根目录
fly launch --no-deploy           # app 名改成全局唯一
fly secrets set DEEPSEEK_API_KEY=sk-...
fly deploy
```
`Dockerfile` 在构建期用 CSV 重建数据库；`fly.toml` 里 `internal_port=8080`。

### 方案 E · 任意 VPS / 自建 Docker

```bash
docker build -t shuangxiu-app .
docker run -d -p 8000:8000 -e DEEPSEEK_API_KEY=sk-... --name shuangxiu shuangxiu-app
# 反代（Nginx/Caddy）到 https 域名即可让任何人访问
```

### 公网安全

- `RATE_LIMIT_PER_MIN`（默认 20）按 IP 限流，避免额度被刷爆；可用环境变量调低。
- 请求体上限 12MB，图片在浏览器端已压到 ≤1280px。
- 如需，可加访问口令或改用带鉴权的网关（未内置，按需扩展）。
