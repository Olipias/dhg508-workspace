# 网页版

纯 HTML/CSS/JS，无框架；地图、人物、文书数据与 Godot 版共用 `../game/`。

**不要双击 `index.html`**；必须通过服务器打开。

```bash
cd projects/qin_qianling_sim
export DEEPSEEK_API_KEY=sk-...
python3 server/web_server.py --host 0.0.0.0
# http://127.0.0.1:8788
```

- `--mock`：不调模型，用每个 NPC 的脚本回退台词；主链仍可完成。
- `PORT` / `HOST` 环境变量可直接用于 Render/Fly。
- `/npc` 与 Godot 版共用 `server/npc_server.py` 的 prompt、守卫和日志。

文件：

| 文件 | 作用 |
|---|---|
| `index.html` | 画布 + 全部 DOM 面板 |
| `style.css` | 墨色/简牍/印章配色 |
| `app.js` | 行走、碰撞、交互、对话、文书、证据、驳/准 |
