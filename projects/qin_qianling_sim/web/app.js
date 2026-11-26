/* 迁陵 · 廿六年五月 — web build.
   The world (movement, evidence, approval) is plain JS; the model only speaks. */

if (window.location.protocol === "file:") {
  document.body.innerHTML = `
    <div class="file-warning">
      <h1>这不是双击打开的文件</h1>
      <p>浏览器不允许 <code>file://</code> 页面读取 <code>data/*.json</code>，所以直接打开
      <code>web/index.html</code> 会变成一堆没有样式的文字。</p>
      <p>请在项目目录运行：</p>
      <pre>cd projects/qin_qianling_sim
export DEEPSEEK_API_KEY=sk-...
python3 server/web_server.py</pre>
      <p>然后打开 <a href="http://127.0.0.1:8788">http://127.0.0.1:8788</a>。
      没有 key 也能看：把最后一行换成 <code>python3 server/web_server.py --mock</code>。</p>
      <p class="muted">如果你在 Windows 上访问 WSL：先确认服务已启动；<code>localhost:8788</code>
      不通时，用 WSL 的 IP（在 WSL 里运行 <code>hostname -I</code>），并在启动时加
      <code>--host 0.0.0.0</code>。</p>
    </div>`;
  throw new Error("open through web_server.py, not file://");
}

const W = 1280, H = 720, ZOOM = 1.15;
const $ = (id) => document.getElementById(id);
const stage = $("stage");
const canvas = $("game");
const ctx = canvas.getContext("2d");
const mini = $("minimap");
const mctx = mini.getContext("2d");

const OBJ_DEFS = {
  death_report: { doc: "death_report", label: "里典的报案", sprite: "obj_slips",
    effect: { evidence: ["e_report"], flags: ["read_report"] } },
  law_shelf: { doc: "autopsy_law", label: "律令架", sprite: "obj_law",
    extra: ["homicide_law", "law_xingshu", "glossary"], effect: {} },
  body: { doc: "body_exam", label: "丙的尸身", sprite: "obj_body",
    effect: { evidence: ["e_autopsy"], flags: ["examined_body"] } },
  wound: { doc: "wound_note", label: "粮袋旁的血", sprite: "obj_wound",
    effect: { evidence: [], flags: ["saw_wound"] } },
  grain_ledger: { doc: "grain_ledger", label: "仓里的账", sprite: "obj_ledger",
    effect: { evidence: ["e_ledger"], flags: ["has_ledger"] } },
  register: { doc: "register", label: "丙的户籍", sprite: "obj_ledger",
    effect: { evidence: ["e_register"], flags: ["has_register"] } },
  post_slip: { doc: "post_slip", label: "送郡的案卷", sprite: "obj_seal",
    effect: { evidence: [], flags: ["has_qiling_reply"] } },
};

const LOCATIONS = [
  { name: "县廷", rect: [160, 150, 1040, 780] },
  { name: "仓", rect: [1700, 150, 2520, 780] },
  { name: "都乡", rect: [160, 1120, 1040, 1740] },
  { name: "邮亭", rect: [1700, 1120, 2520, 1740] },
];

const KE = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一"];
const STATUS_CN = { evidenced: "有据", inferred: "推拟", secondary: "二手研究" };
const BOOK_CN = { evidenced: "已核", inferred: "待核", secondary: "参考" };

const state = {
  started: false, modal: false, aiBusy: false,
  flags: new Set(), evidence: new Set(), ke: 3,
  loc: "县廷", npc: null, npcData: null, lastTopic: "free", pendingTopic: null, pendingFreeText: null,
  near: null, docExtra: [], postTruth: true, docPlain: true,
  player: { x: 620, y: 710, dir: "down", frame: 0, anim: 0 },
};

let DATA = {}, IMG = {}, entities = [], blockers = [], mapW = 2880, mapH = 1920;
const keys = {};

/* ---------- boot ---------- */
async function boot() {
  const files = ["map_meta", "npcs", "documents", "sources", "evidence", "chain"];
  const got = await Promise.all(files.map((f) =>
    fetch(`/data/${f}.json`).then((r) => r.json())));
  DATA = Object.fromEntries(files.map((f, i) => [f, got[i]]));
  mapW = DATA.map_meta.size[0];
  mapH = DATA.map_meta.size[1];
  blockers = DATA.map_meta.blockers;
  state.player.x = DATA.map_meta.spawn[0];
  state.player.y = DATA.map_meta.spawn[1];
  entities = buildEntities();
  await preload();
  bindUI();
  populateIntro();
  resize();
  if (new URLSearchParams(location.search).get("autostart") === "1") startGame();
  requestAnimationFrame(loop);
}

function buildEntities() {
  const out = [];
  for (const [id, n] of Object.entries(DATA.npcs)) {
    out.push({ kind: "npc", id, x: n.position[0], y: n.position[1], data: n, sprite: n.sprite });
  }
  for (const [id, def] of Object.entries(OBJ_DEFS)) {
    const pos = DATA.map_meta.objects[id];
    if (pos) out.push({ kind: "object", id, x: pos[0], y: pos[1], data: def, sprite: def.sprite });
  }
  return out;
}

function preload() {
  const srcs = new Set([
    "/assets/tiles/map_base.png", "/assets/ui/slips_panel.png",
    ...Object.values(DATA.npcs).map((n) => `/assets/sprites/${n.sprite}_down_0.png`),
    ...Object.values(OBJ_DEFS).map((o) => `/assets/sprites/${o.sprite}.png`),
  ]);
  for (const dir of ["down", "up", "left", "right"]) {
    for (const f of [0, 1]) srcs.add(`/assets/sprites/player_${dir}_${f}.png`);
  }
  return Promise.all([...srcs].map((src) => new Promise((resolve) => {
    const img = new Image();
    img.onload = () => { IMG[src] = img; resolve(); };
    img.onerror = () => resolve();
    img.src = src;
  })));
}

/* ---------- render ---------- */
function resize() {
  const s = Math.min(window.innerWidth / W, window.innerHeight / H);
  stage.style.transform = `scale(${s})`;
}
window.addEventListener("resize", resize);

function loop(t) {
  const dt = Math.min((t - (loop.last || t)) / 1000, 0.05);
  loop.last = t;
  if (state.started && !state.modal) update(dt);
  draw();
  requestAnimationFrame(loop);
}

function update(dt) {
  let dx = 0, dy = 0;
  if (keys["w"] || keys["arrowup"]) dy -= 1;
  if (keys["s"] || keys["arrowdown"]) dy += 1;
  if (keys["a"] || keys["arrowleft"]) dx -= 1;
  if (keys["d"] || keys["arrowright"]) dx += 1;
  if (dx || dy) {
    const len = Math.hypot(dx, dy);
    dx /= len; dy /= len;
    const step = 235 * dt;
    const nx = state.player.x + dx * step;
    const ny = state.player.y + dy * step;
    if (!blocked(nx, state.player.y)) state.player.x = nx;
    if (!blocked(state.player.x, ny)) state.player.y = ny;
    state.player.x = Math.max(20, Math.min(mapW - 20, state.player.x));
    state.player.y = Math.max(20, Math.min(mapH - 20, state.player.y));
    if (Math.abs(dx) > Math.abs(dy)) state.player.dir = dx > 0 ? "right" : "left";
    else state.player.dir = dy > 0 ? "down" : "up";
    state.player.anim += dt;
    if (state.player.anim > 0.16) {
      state.player.anim = 0;
      state.player.frame = 1 - state.player.frame;
    }
  } else {
    state.player.frame = 0;
  }
  updateLocation();
  state.near = nearest();
  updatePrompt();
}

function blocked(x, y) {
  const r = 10;
  for (const b of blockers) {
    if (x + r > b[0] && x - r < b[2] && y + r > b[1] && y - r < b[3]) return true;
  }
  for (const e of entities) {
    if (e.kind === "npc" && Math.hypot(x - e.x, y - e.y) < 50) return true;
  }
  return false;
}

function camera() {
  const vw = W / ZOOM, vh = H / ZOOM;
  return {
    x: Math.max(0, Math.min(mapW - vw, state.player.x - vw / 2)),
    y: Math.max(0, Math.min(mapH - vh, state.player.y - vh / 2)),
  };
}

function draw() {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = "#0a0807";
  ctx.fillRect(0, 0, W, H);
  const cam = camera();
  ctx.setTransform(ZOOM, 0, 0, ZOOM, -cam.x * ZOOM, -cam.y * ZOOM);
  if (IMG["/assets/tiles/map_base.png"]) {
    ctx.drawImage(IMG["/assets/tiles/map_base.png"], 0, 0);
  }
  const all = [...entities, { kind: "player", x: state.player.x, y: state.player.y }];
  all.sort((a, b) => a.y - b.y);
  for (const e of all) {
    if (e.kind === "player") drawPlayer(e);
    else if (e.kind === "npc") drawNPC(e);
    else drawObject(e);
  }
  if (state.near) {
    ctx.beginPath();
    ctx.arc(state.near.x, state.near.y - 8, 26, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(224,201,142,.85)";
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  drawMinimap();
}

function drawMinimap() {
  const mw = 220, mh = 147;
  mctx.setTransform(2, 0, 0, 2, 0, 0);
  mctx.clearRect(0, 0, mw, mh);
  mctx.fillStyle = "rgba(16,13,10,.94)";
  mctx.fillRect(0, 0, mw, mh);

  mctx.fillStyle = "#e0c98e";
  mctx.font = 'bold 12px "Noto Serif CJK SC","Source Han Serif SC",serif';
  mctx.textBaseline = "middle";
  mctx.fillText("迁陵县 · 示意图", 8, 11);

  const x0 = 5, y0 = 21, w = mw - 10, h = mh - 26;
  const img = IMG["/assets/tiles/map_base.png"];
  if (img) {
    mctx.globalAlpha = 0.86;
    mctx.drawImage(img, x0, y0, w, h);
    mctx.globalAlpha = 1;
  } else {
    mctx.fillStyle = "#241c14";
    mctx.fillRect(x0, y0, w, h);
  }

  const sx = w / mapW, sy = h / mapH;
  mctx.lineWidth = 1;
  for (const loc of LOCATIONS) {
    const [lx, ly, rw, rh] = loc.rect;
    const rx = x0 + lx * sx, ry = y0 + ly * sy;
    mctx.fillStyle = "rgba(224,201,142,.07)";
    mctx.fillRect(rx, ry, rw * sx, rh * sy);
    mctx.strokeStyle = "rgba(224,201,142,.42)";
    mctx.strokeRect(rx, ry, rw * sx, rh * sy);
    mctx.fillStyle = "rgba(233,226,207,.92)";
    mctx.font = '11px "Noto Serif CJK SC","Source Han Serif SC",serif';
    mctx.fillText(loc.name, rx + 4, ry + 10);
  }

  for (const e of entities) {
    if (e.kind !== "npc") continue;
    mctx.beginPath();
    mctx.arc(x0 + e.x * sx, y0 + e.y * sy, 2.2, 0, Math.PI * 2);
    mctx.fillStyle = "rgba(224,201,142,.85)";
    mctx.fill();
  }

  const px = x0 + state.player.x * sx, py = y0 + state.player.y * sy;
  mctx.beginPath();
  mctx.arc(px, py, 5, 0, Math.PI * 2);
  mctx.fillStyle = "rgba(168,64,52,.35)";
  mctx.fill();
  mctx.beginPath();
  mctx.arc(px, py, 3, 0, Math.PI * 2);
  mctx.fillStyle = "#d05a48";
  mctx.fill();
  mctx.strokeStyle = "#f4e6c8";
  mctx.lineWidth = 1;
  mctx.stroke();

  mctx.strokeStyle = "#85673f";
  mctx.lineWidth = 2;
  mctx.strokeRect(1, 1, mw - 2, mh - 2);
}

function drawPlayer(e) {
  const src = `/assets/sprites/player_${state.player.dir}_${state.player.frame}.png`;
  const img = IMG[src] || IMG["/assets/sprites/player_down_0.png"];
  if (img) ctx.drawImage(img, e.x - 24, e.y - 64, 48, 64);
}

function drawNPC(e) {
  const img = IMG[`/assets/sprites/${e.sprite}_down_0.png`];
  if (img) ctx.drawImage(img, e.x - 24, e.y - 64, 48, 64);
  label(`${e.data.name}·${e.data.office}`, e.x, e.y - 78, 15, "#e8d9b8");
}

function drawObject(e) {
  const img = IMG[`/assets/sprites/${e.sprite}.png`];
  if (img) ctx.drawImage(img, e.x - 22, e.y - 44, 44, 44);
  label(e.data.label, e.x, e.y - 56, 13, "#d9c9a6");
}

function label(text, x, y, size, color) {
  ctx.font = `600 ${size}px "Noto Serif CJK SC","Songti SC",serif`;
  ctx.textAlign = "center";
  ctx.lineWidth = 4;
  ctx.strokeStyle = "rgba(18,13,9,.9)";
  ctx.strokeText(text, x, y);
  ctx.fillStyle = color;
  ctx.fillText(text, x, y);
}

function nearest() {
  let best = null, bestD = 96;
  for (const e of entities) {
    const d = Math.hypot(e.x - state.player.x, e.y - state.player.y);
    if (d < bestD) { bestD = d; best = e; }
  }
  return best;
}

function updatePrompt() {
  const el = $("prompt");
  if (!state.near || state.modal) { el.classList.add("hidden"); return; }
  const text = state.near.kind === "npc"
    ? `E  与 ${state.near.data.name}·${state.near.data.office} 交谈`
    : `E  查看 ${state.near.data.label}`;
  el.textContent = text;
  el.classList.remove("hidden");
}

function updateLocation() {
  let loc = "街道";
  for (const l of LOCATIONS) {
    const [x0, y0, x1, y1] = l.rect;
    if (state.player.x >= x0 && state.player.x <= x1 && state.player.y >= y0 && state.player.y <= y1) {
      loc = l.name; break;
    }
  }
  if (loc !== state.loc) {
    state.loc = loc;
    $("loc").textContent = "迁陵县 · " + loc;
  }
}

/* ---------- interaction ---------- */
function interact() {
  if (!state.started || state.modal || !state.near) return;
  if (state.near.kind === "npc") openDialogue(state.near.id);
  else {
    applyEffect(state.near.data.effect || {});
    openDoc(state.near.data.doc, state.near.data.extra || []);
  }
}

function applyEffect(effect) {
  for (const e of effect.evidence || []) addEvidence(e);
  for (const f of effect.flags || []) state.flags.add(f);
}

function openDialogue(id) {
  const n = DATA.npcs[id];
  state.npc = id; state.npcData = n; state.modal = true; state.lastTopic = "free";
  $("npc-name").textContent = n.name;
  $("npc-office").textContent = n.office;
  $("speech").textContent = n.greeting;
  $("player-input").value = "";
  $("dialogue").classList.remove("hidden");
  $("prompt").classList.add("hidden");
  $("player-input").focus();
  state.ke = state.ke % 11 + 1;
  refreshHUD();
}

function closeDialogue() {
  $("dialogue").classList.add("hidden");
  state.modal = false;
  state.aiBusy = false;
  state.pendingTopic = null;
  state.pendingFreeText = null;
}

function quick(topic) {
  if (state.aiBusy) return;
  state.lastTopic = topic;
  state.pendingTopic = topic;
  const text = {
    ask: "我直接问你：这事你到底知道多少？",
    press: "我追问你：文书和规矩都在这儿，你照实说，别绕。",
    sideways: "我不直接问，先从旁边打听一句。",
  }[topic];
  askAI(text);
}

function applyTopic(topic) {
  const t = (state.npcData.topics || {})[topic] || {};
  const added = [];
  for (const e of t.evidence || []) {
    if (!state.evidence.has(e)) added.push(e);
    addEvidence(e);
  }
  for (const f of t.flags || []) state.flags.add(f);
  return added;
}

function applyPendingAnswer() {
  if (state.pendingTopic) {
    const topic = state.pendingTopic;
    state.pendingTopic = null;
    const added = applyTopic(topic);
    if (added.length) {
      const titles = added.map((id) => (DATA.evidence[id] || {}).title || id);
      $("speech").textContent += "\n\n〔记入案卷〕" + titles.join("；");
    }
  }
  if (state.pendingFreeText) {
    const text = state.pendingFreeText;
    state.pendingFreeText = null;
    applyFreeText(text);
  }
}

function freeText(text) {
  if (state.aiBusy || !text.trim()) return;
  state.lastTopic = "free";
  state.pendingFreeText = text;
  askAI(text);
  $("player-input").value = "";
}

function applyFreeText(text) {
  const id = state.npc;
  if (id === "xiang") {
    if (/年籍|年数/.test(text)) addEvidence("e_age_missing");
    if (/亡|死/.test(text)) addEvidence("e_escape");
    if (/户|名单|十七/.test(text)) addEvidence("e_17");
  } else if (id === "lidian") {
    if (/亡|灶/.test(text)) addEvidence("e_escape");
    if (/高|五尺|作|名籍|底册/.test(text)) addEvidence("e_grain");
  } else if (id === "cang") {
    if (/稟|粮|底册|标准|不备/.test(text)) addEvidence("e_grain");
  } else if (id === "you") {
    if (/时|刻|封|邮/.test(text)) addEvidence("e_post");
  } else if (id === "cheng") {
    if (/簿|驳|律/.test(text)) state.flags.add("knows_criteria");
  }
}

async function askAI(text) {
  state.aiBusy = true;
  $("speech").textContent = "……";
  $("player-input").disabled = true;
  const ctx = {
    location: state.loc, day: "廿六年五月庚子", ke: `水下${KE[state.ke - 1]}刻`,
    present: entities.filter((e) => e.kind === "npc" &&
      Math.hypot(e.x - state.player.x, e.y - state.player.y) < 220).map((e) => e.data.name),
    evidence: [...state.evidence], flags: [...state.flags],
  };
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 25000);
  try {
    const res = await fetch("/npc", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ npc_id: state.npc, text, context: ctx }),
      signal: ctrl.signal,
    });
    if (!res.ok) throw new Error("http " + res.status);
    const j = await res.json();
    $("speech").textContent = j.speech || fallbackLine();
  } catch (err) {
    $("speech").textContent = fallbackLine();
  } finally {
    clearTimeout(timer);
    applyPendingAnswer();
    state.aiBusy = false;
    $("player-input").disabled = false;
    $("player-input").focus();
  }
}

function fallbackLine() {
  const fb = (state.npcData && state.npcData.fallback) || {};
  return fb[state.lastTopic] || fb.free || "……";
}

/* ---------- documents ---------- */
function openDoc(docId, extra = []) {
  if (!DATA.documents[docId]) return;
  state.modal = true; state.docExtra = extra; state.currentDocId = docId;
  state.docPlain = true;
  $("btn-original").textContent = "看原文";
  $("dialogue").classList.add("hidden");
  const toastEl = $("toast"); toastEl.classList.remove("show"); toastEl.classList.add("hidden");
  $("modal").classList.remove("hidden");
  $("doc-source").classList.add("hidden");
  displayDoc(docId);
  const tabs = $("doc-tabs");
  tabs.innerHTML = "";
  for (const id of [docId, ...extra]) {
    if (!DATA.documents[id]) continue;
    const b = document.createElement("button");
    b.textContent = DATA.documents[id].title.slice(0, 10);
    b.onclick = () => displayDoc(id);
    tabs.appendChild(b);
  }
}

function displayDoc(id) {
  const d = DATA.documents[id];
  if (!d) return;
  state.currentDocId = id;
  $("doc-title").textContent = d.title;
  $("doc-sub").textContent = d.subtitle || "";
  $("doc-body").textContent = state.docPlain ? (d.plain || d.body) : d.body;
  $("doc-body").scrollTop = 0;
  const src = DATA.sources[d.source] || {};
  $("doc-source").textContent =
    `考据 · ${STATUS_CN[d.status] || d.status} · ${src.title || d.source}\n${d.note || ""}\n${src.url || ""}`;
}

function closeDoc() {
  $("modal").classList.add("hidden");
  state.modal = false;
}

/* ---------- evidence ---------- */
function addEvidence(id) {
  if (!id || state.evidence.has(id)) return;
  state.evidence.add(id);
  refreshHUD();
  refreshEvidence();
  const d = DATA.evidence[id] || {};
  toast("记入簿书：" + (d.title || id));
}

function refreshHUD() {
  $("clock").textContent = `廿六年五月庚子 · 水下${KE[state.ke - 1]}刻`;
  const found = DATA.chain.required.filter((e) => state.evidence.has(e)).length;
  $("count").textContent = `案卷 ${found}/${DATA.chain.required.length}`;
  $("objective").textContent = "事由：" + DATA.chain.objective;
}

function refreshEvidence() {
  const box = $("evidence-list");
  box.innerHTML = "";
  if (!state.evidence.size) {
    box.innerHTML = '<div class="ev-item inferred">尚无。走一遍县廷、都乡、仓、邮亭。</div>';
    return;
  }
  for (const id of state.evidence) {
    const d = DATA.evidence[id] || {};
    const div = document.createElement("div");
    div.className = "ev-item " + (d.status === "evidenced" ? "" : "inferred");
    div.innerHTML = `【${BOOK_CN[d.status] || d.status}】${escapeHtml(d.title || id)}`;
    box.appendChild(div);
  }
}

function toggleEvidence() {
  const el = $("evidence");
  if (!el.classList.contains("hidden")) { el.classList.add("hidden"); return; }
  if (state.modal) return;
  el.classList.remove("hidden");
  refreshEvidence();
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ---------- submission ---------- */
function openForm() {
  if (state.modal) return;
  state.modal = true;
  $("dialogue").classList.add("hidden");
  const box = $("form-checks");
  box.innerHTML = "";
  const ids = [...DATA.chain.required, ...(DATA.chain.optional || [])];
  for (const id of ids) {
    const d = DATA.evidence[id] || {};
    const has = state.evidence.has(id);
    const must = DATA.chain.required.includes(id);
    const label = document.createElement("label");
    label.innerHTML = `<input type="checkbox" ${has ? "checked" : ""} ${has ? "" : "disabled"}>
      <span>${escapeHtml(d.title || id)} <span class="tag">[${BOOK_CN[d.status] || d.status}] ${must ? "（必须）" : "（可选）"}</span></span>`;
    box.appendChild(label);
  }
  $("form").classList.remove("hidden");
}

function closeForm() {
  $("form").classList.add("hidden");
  state.modal = false;
}

function submitForm() {
  const missing = DATA.chain.required.filter((id) => !state.evidence.has(id));
  const truth = document.querySelector('input[name="posttime"]:checked').value === "true";
  if (missing.length) { showEnd("rejected", missing); return; }
  if (!truth) { showEnd("falsified_post", []); return; }
  const has = (id) => state.evidence.has(id);
  const note = [
    $("blame-lidian").checked ? "你把里典和四邻写进了案卷。" : "",
    $("blame-cang").checked ? "你把仓啬夫的账翻了出来。" : "",
  ].join("");
  const v = $("verdict").value;
  const hasWound = has("e_wound"), hasWife = has("e_wife"), hasNeighbor = has("e_neighbor");
  if (v === "suicide") {
    if (hasWound || hasWife) showEnd("falsified_autopsy", [], note);
    else showEnd("suicide", [], note);
  } else if (v === "homicide") {
    if (hasWound && (hasWife || has("e_ledger"))) showEnd("homicide", [], note);
    else showEnd("rejected", [], DATA.chain.verdict_reject.homicide);
  } else if (v === "fight") {
    if (hasNeighbor) showEnd("fight", [], note);
    else showEnd("rejected", [], DATA.chain.verdict_reject.fight);
  } else {
    if (hasWound) showEnd("uncertain", [], note);
    else showEnd("rejected", [], DATA.chain.verdict_reject.uncertain);
  }
}

function showEnd(kind, missing, note = "") {
  $("form").classList.add("hidden");
  $("modal").classList.add("hidden");
  $("dialogue").classList.add("hidden");
  $("hud").classList.add("hidden");
  $("objective").classList.add("hidden");
  $("prompt").classList.add("hidden");
  state.modal = true;
  const e = DATA.chain.endings[kind];
  $("end-title").textContent = e.title;
  const isRejected = kind === "rejected";
  $("end-body").textContent = e.body + (!isRejected && note ? "\n\n" + note : "");
  let extra = "";
  if (isRejected) {
    if (missing && missing.length) {
      for (const id of missing) extra += "· " + (DATA.chain.reject[id] || id) + "\n";
    } else {
      extra = note || "";
    }
  }
  $("end-missing").textContent = extra;
  $("end-lesson").textContent = "【案后记】" + DATA.chain.lesson;
  $("end").classList.remove("hidden");
}

/* ---------- intro / toast ---------- */
function populateIntro() {
  $("intro-body").textContent = DATA.chain.intro;
  $("intro-sub").textContent = DATA.chain.subtitle || "新令史的第一天";
  $("end-lesson").textContent = "";
}

function startGame() {
  $("intro").classList.add("hidden");
  $("hud").classList.remove("hidden");
  $("objective").classList.remove("hidden");
  state.started = true;
  state.flags.add("briefed");
  refreshHUD();
  toast("敦狐把一份报案拍在你桌上。");
}

function toast(text) {
  const el = $("toast");
  el.textContent = text;
  el.classList.remove("hidden");
  el.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.classList.add("hidden"), 400);
  }, 2600);
}

/* ---------- events ---------- */
function bindUI() {
  $("btn-start").onclick = startGame;
  $("btn-submit").onclick = openForm;
  $("btn-evidence").onclick = toggleEvidence;
  $("ev-close").onclick = toggleEvidence;
  $("btn-law").onclick = () => openDoc("autopsy_law", ["homicide_law", "law_xingshu", "glossary"]);
  $("btn-glossary").onclick = () => openDoc("glossary", []);
  $("btn-original").onclick = () => {
    state.docPlain = !state.docPlain;
    $("btn-original").textContent = state.docPlain ? "看原文" : "看人话";
    displayDoc(state.currentDocId);
  };
  $("dlg-close").onclick = closeDialogue;
  $("btn-doc-close").onclick = closeDoc;
  $("btn-kaoju").onclick = () => $("doc-source").classList.toggle("hidden");
  $("btn-submit-form").onclick = submitForm;
  $("btn-cancel-form").onclick = closeForm;
  $("btn-restart").onclick = () => location.reload();
  $("btn-refs").onclick = showRefs;
  $("player-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); freeText(e.target.value); }
  });
  document.querySelectorAll("[data-topic]").forEach((b) => {
    b.onclick = () => quick(b.dataset.topic);
  });
  canvas.addEventListener("click", (e) => {
    if (!state.started || state.modal) return;
    const r = canvas.getBoundingClientRect();
    const sx = (e.clientX - r.left) * (W / r.width);
    const sy = (e.clientY - r.top) * (H / r.height);
    const cam = camera();
    const wx = sx / ZOOM + cam.x;
    const wy = sy / ZOOM + cam.y;
    let hit = null, best = 48;
    for (const ent of entities) {
      const d = Math.hypot(ent.x - wx, ent.y - wy);
      if (d < best) { best = d; hit = ent; }
    }
    if (hit) { state.near = hit; interact(); }
  });
  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });
}

function onKeyDown(e) {
  const k = e.key.toLowerCase();
  if (k === "escape") {
    e.preventDefault();
    if (!$("form").classList.contains("hidden")) closeForm();
    else if (!$("modal").classList.contains("hidden")) closeDoc();
    else if (!$("dialogue").classList.contains("hidden")) closeDialogue();
    else if (!$("evidence").classList.contains("hidden")) toggleEvidence();
    return;
  }
  if (k === "tab") {
    e.preventDefault();
    toggleEvidence();
    return;
  }
  if (e.target && e.target.tagName === "INPUT" && e.target.type === "text") return;
  if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(k)) e.preventDefault();
  keys[k] = true;
  if (k === "e" && !state.modal) { e.preventDefault(); interact(); }
  if (k === "h" && !state.modal && state.started) { e.preventDefault(); openDoc("glossary", []); }
}

function showRefs() {
  const n = state.npcData;
  if (!n) return;
  const refs = (n.knowledge || []).map((k) => {
    const src = DATA.sources[k.source] || {};
    return `${k.source} · ${src.title || ""}`;
  });
  $("dlg-hint").textContent = "所知出处：" + [...new Set(refs)].join("  |  ");
}

boot().catch((err) => {
  console.error(err);
  document.body.innerHTML = `<div class="file-warning"><h1>载入失败</h1><pre>${err}</pre>
    <p>确认你是通过 <code>python3 server/web_server.py</code> 打开的
    <code>http://127.0.0.1:8788</code>，而不是双击 <code>index.html</code>。</p></div>`;
});

/* debug hook for local UI checks; harmless in production */
window.__qin = { state, DATA, entities, OBJ_DEFS, openDoc, openDialogue, openForm, showEnd,
  addEvidence, applyEffect, applyTopic, quick, closeDialogue, closeDoc, interact, submitForm };
