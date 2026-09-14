"use strict";

const express = require("express");
const path = require("path");
const { makeStore, EVENTS, INTENTS } = require("./store");

const PORT = process.env.PORT || 3000;
const STATS_KEY = process.env.STATS_KEY || "tfg2026"; // change this on Railway
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const store = makeStore();
const app = express();

app.disable("x-powered-by");
app.use(express.json({ limit: "8kb" }));
app.use((req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  next();
});
app.use(express.static(path.join(__dirname, "public"), { maxAge: "1h", extensions: ["html"] }));

const clean = (v, max = 120) => (typeof v === "string" ? v.trim().slice(0, max) : null) || null;

// ---- funnel events -------------------------------------------------------
app.post("/api/event", async (req, res) => {
  const { session_id, event, meta } = req.body || {};
  if (!EVENTS.has(event)) return res.status(400).json({ error: "unknown event" });
  try {
    await store.addEvent({
      session_id: clean(session_id, 64),
      event,
      meta: meta && typeof meta === "object" ? { button: clean(meta.button, 20) } : {},
    });
  } catch (err) {
    console.error("event error", err);
  }
  res.status(204).end(); // never block the UI over analytics
});

// ---- signups -------------------------------------------------------------
app.post("/api/signup", async (req, res) => {
  const b = req.body || {};
  if (b.website) return res.status(201).json({ ok: true }); // honeypot: bots fill this, humans can't see it

  const email = (clean(b.email, 254) || "").toLowerCase();
  if (!EMAIL_RE.test(email)) return res.status(400).json({ error: "invalid_email" });

  const usage_intent = INTENTS.has(b.usage_intent) ? b.usage_intent : null;
  const source = ["hero", "bottom"].includes(b.source) ? b.source : null;

  try {
    const result = await store.addSignup({
      email,
      programme: clean(b.programme, 80),
      usage_intent,
      source,
      session_id: clean(b.session_id, 64),
    });
    if (result.duplicate) return res.status(409).json({ error: "duplicate" });
    store.addEvent({ session_id: clean(b.session_id, 64), event: "signup_submitted", meta: { button: source } }).catch(() => {});
    res.status(201).json({ ok: true });
  } catch (err) {
    console.error("signup error", err);
    res.status(500).json({ error: "server" });
  }
});

// ---- stats (counts only) -------------------------------------------------
const guard = (req, res, next) => (req.query.key === STATS_KEY ? next() : res.status(404).send("Not found"));
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pct = (a, b) => (b ? `${Math.round((100 * a) / b)}%` : "–");

app.get("/stats", guard, async (req, res) => {
  const [events, signups] = await Promise.all([store.events(), store.signups()]);
  const count = (fn) => events.filter(fn).length;
  const views = count((e) => e.event === "page_view");
  const sessions = new Set(events.filter((e) => e.event === "page_view").map((e) => e.session_id)).size;
  const clicks = count((e) => e.event === "cta_click");
  const clicksHero = count((e) => e.event === "cta_click" && e.meta && e.meta.button === "hero");
  const clicksBottom = count((e) => e.event === "cta_click" && e.meta && e.meta.button === "bottom");
  const clickSessions = new Set(events.filter((e) => e.event === "cta_click").map((e) => e.session_id)).size;
  const intents = { instead: 0, alongside: 0, probably_not: 0, unanswered: 0 };
  for (const s of signups) intents[s.usage_intent || "unanswered"]++;
  const programmes = {};
  for (const s of signups) programmes[s.programme || "(blank)"] = (programmes[s.programme || "(blank)"] || 0) + 1;

  const row = (k, v) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`;
  res.type("html").send(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TFGPT stats</title>
<style>
  body{font:16px/1.5 system-ui,sans-serif;color:#1b2437;max-width:560px;margin:40px auto;padding:0 20px}
  h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 8px;color:#5c6478}
  table{border-collapse:collapse;width:100%}td{padding:8px 0;border-bottom:1px solid #e3e6ec}td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
  a{color:#1b2437}small{color:#5c6478}
</style>
<h1>TFGPT fake-door funnel</h1><small>${esc(store.kind)} · ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC</small>
<h2>Funnel</h2><table>
${row("Page views", views)}${row("Unique sessions", sessions)}
${row("CTA clicks (total)", clicks)}${row("  from hero button", clicksHero)}${row("  from bottom button", clicksBottom)}
${row("Sessions that clicked", clickSessions)}${row("Signups", signups.length)}
${row("Sessions → click", pct(clickSessions, sessions))}${row("Sessions → signup", pct(signups.length, sessions))}${row("Click → signup", pct(signups.length, clickSessions))}
</table>
<h2>"Would you use it…"</h2><table>
${row("instead of the AI I use now", intents.instead)}${row("alongside it", intents.alongside)}${row("probably not", intents.probably_not)}${row("(unanswered)", intents.unanswered)}
</table>
<h2>Programmes</h2><table>${Object.entries(programmes).sort((a, b) => b[1] - a[1]).map(([k, v]) => row(k, v)).join("")}</table>
<p><a href="/export.csv?key=${encodeURIComponent(STATS_KEY)}">Download signups as CSV</a></p>`);
});

app.get("/export.csv", guard, async (req, res) => {
  const rows = await store.signups();
  const q = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = ["email,programme,usage_intent,source,created_at"]
    .concat(rows.map((s) => [s.email, s.programme, s.usage_intent, s.source, s.created_at].map(q).join(",")))
    .join("\n");
  res.setHeader("Content-Disposition", "attachment; filename=tfgpt-signups.csv");
  res.type("text/csv").send(csv);
});

app.get("/healthz", (req, res) => res.send("ok"));

store.init().then(() => {
  app.listen(PORT, () => console.log(`TFGPT landing on :${PORT} using ${store.kind}`));
}).catch((err) => {
  console.error("store init failed", err);
  process.exit(1);
});
