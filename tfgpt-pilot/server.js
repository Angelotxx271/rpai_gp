"use strict";

// TFGPT Wizard-of-Oz pilot (prototype-v0 rebuilt).
// Student side: /s/<token>, a chat that looks automated.
// Wizard side: /admin, where the team reads each message and answers live,
// following the wizard protocol, and fills the observation sheet.

const express = require("express");
const path = require("path");
const crypto = require("crypto");
const { makeStore } = require("./store");

const PORT = process.env.PORT || 3000;
const PRODUCTION = Boolean(process.env.RAILWAY_ENVIRONMENT || process.env.RAILWAY_ENVIRONMENT_NAME) || process.env.NODE_ENV === "production";
const PILOT_BADGE = (process.env.PILOT_BADGE || "Pilot").slice(0, 24);
const PUBLIC_URL = (process.env.PUBLIC_URL || "").replace(/\/+$/, "");
const SESSION_MINUTES = Number(process.env.SESSION_MINUTES) || 20; // experiment-card.md: a 20-minute session
const PURGE_AFTER_HOURS = Number(process.env.PURGE_AFTER_HOURS) || 6;
const MAX_MESSAGES = 400;
const THRESHOLD = 6; // committed before the test (experiment-card.md)
const SAMPLE = 10;

let ADMIN_KEY = process.env.ADMIN_KEY || "";
if (PRODUCTION && ADMIN_KEY.length < 16) {
  console.error("Set ADMIN_KEY to a random string of at least 16 characters before deploying.");
  process.exit(1);
}
if (!ADMIN_KEY) {
  ADMIN_KEY = crypto.randomBytes(12).toString("base64url");
  console.warn(`ADMIN_KEY is not set, so one was generated for this local run: ${ADMIN_KEY}`);
}

const store = makeStore();
if (!store.persistent) {
  console.warn(`Sessions are stored in ${store.dir}, which is not a mounted volume. Mount one at /data on Railway, or they are lost on redeploy.`);
}

const app = express();
app.set("trust proxy", 1);
app.set("env", PRODUCTION ? "production" : "development");
app.disable("x-powered-by");

app.use((req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "no-referrer"); // student links carry their token
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; " +
      "font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
  );
  if (req.secure) res.setHeader("Strict-Transport-Security", "max-age=31536000");
  if (PRODUCTION && req.headers["x-forwarded-proto"] === "http") {
    return res.redirect(301, `https://${req.get("host")}${req.originalUrl}`);
  }
  next();
});
app.use("/api", (req, res, next) => {
  res.setHeader("Cache-Control", "no-store");
  next();
});
app.use(express.json({ limit: "32kb" }));
app.use(express.static(path.join(__dirname, "public"), {
  index: false,
  setHeaders: (res, file) => res.setHeader("Cache-Control",
    file.includes(`${path.sep}fonts${path.sep}`) ? "public, max-age=604800, immutable" : "no-cache"),
}));

const now = () => new Date().toISOString();
const clean = (v, max) => (typeof v === "string" ? v.replace(/\r\n?/g, "\n").trim().slice(0, max) : "");
const newId = () => crypto.randomBytes(5).toString("hex");
const page = (name) => (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  res.sendFile(path.join(__dirname, "public", name));
};
const sha = (v) => crypto.createHash("sha256").update(String(v)).digest();
const sameSecret = (a, b) => crypto.timingSafeEqual(sha(a), sha(b));

// ---- live updates (server-sent events) -----------------------------------
const studentStreams = new Map(); // session id -> Set of responses
const adminStreams = new Map(); // response -> admin token

function openStream(res) {
  res.writeHead(200, {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache, no-transform",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
  });
  res.write("retry: 3000\n\n");
}
const send = (res, event, data) => {
  try { res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`); } catch { /* client gone */ }
};
const toStudent = (id, event, data) => (studentStreams.get(id) || new Set()).forEach((r) => send(r, event, data));
const toAdmins = (event, data) => adminStreams.forEach((t, r) => send(r, event, data));
function endStudentStreams(id) {
  (studentStreams.get(id) || new Set()).forEach((r) => r.end());
  studentStreams.delete(id);
}

// ---- views ------------------------------------------------------------------
const completedWithoutOwnAI = (s) => s.observation.tasks.every(Boolean) && s.observation.ownAI === false;

function waitingSince(s) {
  // the oldest student message that has no answer yet
  let since = null;
  for (let i = s.messages.length - 1; i >= 0 && s.messages[i].role === "student"; i--) since = s.messages[i].at;
  return since;
}

function summary(s) {
  const last = s.messages[s.messages.length - 1];
  return {
    id: s.id,
    number: s.number,
    status: s.status,
    rehearsal: Boolean(s.rehearsal),
    firstName: s.firstName,
    degree: s.degree,
    createdAt: s.createdAt,
    openedAt: s.openedAt,
    clockAt: s.clockAt || s.openedAt,
    closedAt: s.closedAt,
    turns: s.turns || 0,
    lastAt: last ? last.at : null,
    waitingSince: s.status === "open" ? waitingSince(s) : null,
    recorded: s.observation.ownAI !== null,
    completed: completedWithoutOwnAI(s),
  };
}

// what other consoles need to refresh an open session without reloading it
const sessionEvent = (s) => ({
  ...summary(s),
  started: s.started,
  observation: s.observation,
  transcriptKept: Boolean(s.transcriptKept),
  templates: s.templates,
});

function tally() {
  const recorded = store.all().filter((s) => !s.rehearsal && s.observation.ownAI !== null);
  const counted = recorded.slice(0, SAMPLE);
  const completed = counted.filter(completedWithoutOwnAI).length;
  let decision = `No decision yet: ${counted.length} of ${SAMPLE} students recorded`;
  if (counted.length >= SAMPLE) {
    decision = completed >= THRESHOLD
      ? "CONTINUE: build a working slice with the IE guidelines loaded"
      : "CHANGE: reframe TFGPT as a complement alongside their own AI, and rerun";
  }
  if (recorded.length > SAMPLE) decision += `. ${recorded.length - SAMPLE} later session(s) are not counted: the rule uses the first ${SAMPLE}`;
  return { completed, recorded: counted.length, threshold: THRESHOLD, sample: SAMPLE, decision };
}

const studentView = (s) => ({
  status: s.status,
  badge: PILOT_BADGE,
  firstName: s.firstName,
  degree: s.degree,
  year: s.year,
  topic: s.topic,
  notesName: s.notesName,
  messages: s.messages.map(({ id, role, text, at }) => ({ id, role, text, at })),
});

const baseUrl = (req) => PUBLIC_URL || `${req.protocol}://${req.get("host")}`;
const adminView = (s, req) => ({ ...s, link: `${baseUrl(req)}/s/${s.token}`, summary: summary(s) });

// ---- privacy: what closing a session removes --------------------------------
function redactName(text, name) {
  if (!text || !name) return text;
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return text.replace(new RegExp(`(?<![\\p{L}\\p{N}])${escaped}(?![\\p{L}\\p{N}])`, "giu"), "[name]");
}
function purge(s) {
  // the pilot note promises nothing is stored after the session
  for (const k of ["note", "switchedFor", "usedForEach"]) s.observation[k] = redactName(s.observation[k], s.firstName);
  s.started = redactName(s.started, s.firstName);
  s.messages = [];
  s.firstName = "";
  s.topic = "";
  s.notesName = "";
  s.templates = { fit: "", structure: "", dates: "" };
  s.transcriptKept = false;
}
function closeSession(s, keep) {
  s.status = "closed";
  s.closedAt = now();
  if (keep) s.transcriptKept = true;
  else purge(s);
  store.update(s);
  toStudent(s.id, "closed", {});
  endStudentStreams(s.id);
  toAdmins("session", sessionEvent(s));
}

// forgotten sessions close themselves and are purged
setInterval(() => {
  const cutoff = Date.now() - PURGE_AFTER_HOURS * 3600 * 1000;
  for (const s of store.all()) {
    if (s.status !== "open") continue;
    const last = s.messages.length ? s.messages[s.messages.length - 1].at : s.openedAt || s.createdAt;
    if (Date.parse(last) < cutoff) {
      console.log(`closing and purging session #${s.number}: no activity for ${PURGE_AFTER_HOURS} hours`);
      closeSession(s, false);
    }
  }
}, 10 * 60 * 1000).unref();

// ---- student side -----------------------------------------------------------
app.get("/", page("index.html"));
app.get("/s/:token", page("chat.html"));

app.get("/api/s/:token", (req, res) => {
  const s = store.byToken(req.params.token);
  if (!s) return res.status(404).json({ error: "not_found" });
  if (!s.openedAt && s.status === "open") {
    s.openedAt = now(); // the clock starts when the student opens the link (the console can restart it)
    store.update(s);
    toAdmins("session", sessionEvent(s));
  }
  res.json(studentView(s));
});

app.get("/api/s/:token/stream", (req, res) => {
  const s = store.byToken(req.params.token);
  if (!s) return res.status(404).end();
  if (s.status !== "open") return res.status(409).end();
  if (!studentStreams.has(s.id)) studentStreams.set(s.id, new Set());
  const set = studentStreams.get(s.id);
  if (set.size >= 5) { const oldest = set.values().next().value; oldest.end(); set.delete(oldest); }
  openStream(res);
  set.add(res);
  req.on("close", () => {
    set.delete(res);
    if (!set.size && studentStreams.get(s.id) === set) studentStreams.delete(s.id);
  });
});

const studentBurst = new Map(); // session id -> recent timestamps
app.post("/api/s/:token/messages", (req, res) => {
  const s = store.byToken(req.params.token);
  if (!s) return res.status(404).json({ error: "not_found" });
  if (s.status !== "open") return res.status(409).json({ error: "closed" });
  const b = req.body || {};
  const clientId = clean(b.clientId, 40);
  const dup = clientId && s.messages.find((m) => m.clientId === clientId);
  if (dup) return res.status(200).json(dup); // a retry of a message that already arrived
  const text = clean(b.text, 4000);
  if (!text) return res.status(400).json({ error: "empty" });
  if (s.messages.length >= MAX_MESSAGES) return res.status(413).json({ error: "session_full" });
  const t = Date.now();
  const recent = (studentBurst.get(s.id) || []).filter((x) => t - x < 60000);
  if (recent.length >= 30) return res.status(429).json({ error: "slow_down" });
  studentBurst.set(s.id, [...recent, t]);

  const m = { id: newId(), clientId: clientId || undefined, role: "student", text, at: now() };
  s.messages.push(m);
  s.turns = (s.turns || 0) + 1;
  store.update(s);
  toStudent(s.id, "message", m);
  toAdmins("message", { sessionId: s.id, message: m, summary: summary(s) });
  res.status(201).json(m);
});

// ---- wizard side ------------------------------------------------------------
const COOKIE = "tfgpt_admin";
const TOKEN_TTL = 12 * 3600 * 1000;
// random per-login tokens, kept only as sha256 hashes so a redeploy doesn't log the wizards out mid-session
const fs = require("fs");
const tokenFile = path.join(path.dirname(store.dir), "admin-tokens.json");
const adminTokens = new Map(); // sha256(token) hex -> expiry
try { Object.entries(JSON.parse(fs.readFileSync(tokenFile, "utf8"))).forEach(([h, exp]) => { if (exp > Date.now()) adminTokens.set(h, exp); }); } catch { /* none yet */ }
const saveTokens = () => {
  try { fs.writeFileSync(tokenFile, JSON.stringify(Object.fromEntries(adminTokens))); } catch (err) { console.error("could not save admin logins", err.message); }
};
const tokenHash = (t) => crypto.createHash("sha256").update(t).digest("hex");

function adminToken(req) {
  const pair = (req.headers.cookie || "").split(";").map((c) => c.trim()).find((c) => c.startsWith(`${COOKIE}=`));
  return pair ? pair.slice(COOKIE.length + 1) : null;
}
function isAdmin(req) {
  const t = adminToken(req);
  const h = t && tokenHash(t);
  const exp = h && adminTokens.get(h);
  if (!exp) return false;
  if (exp < Date.now()) { adminTokens.delete(h); saveTokens(); return false; }
  return true;
}
const requireAdmin = (req, res, next) => (isAdmin(req) ? next() : res.status(401).json({ error: "unauthorised" }));
const findSession = (req, res, next) => {
  req.pilotSession = store.get(req.params.id);
  return req.pilotSession ? next() : res.status(404).json({ error: "not_found" });
};

app.get("/admin", page("admin.html"));

const loginFailures = new Map(); // ip -> failure timestamps
let allFailures = [];
app.post("/api/admin/login", (req, res) => {
  const t = Date.now();
  const mine = (loginFailures.get(req.ip) || []).filter((x) => t - x < 600000);
  allFailures = allFailures.filter((x) => t - x < 600000);
  if (mine.length >= 10 || allFailures.length >= 300) return res.status(429).json({ error: "too_many_attempts" });
  if (!sameSecret((req.body || {}).key || "", ADMIN_KEY)) {
    loginFailures.set(req.ip, [...mine, t]);
    allFailures.push(t);
    return res.status(401).json({ error: "wrong_key" });
  }
  const token = crypto.randomBytes(32).toString("base64url");
  adminTokens.set(tokenHash(token), t + TOKEN_TTL);
  saveTokens();
  const secure = PRODUCTION || req.secure ? "; Secure" : "";
  res.setHeader("Set-Cookie", `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${TOKEN_TTL / 1000}${secure}`);
  res.json({ ok: true });
});

app.post("/api/admin/logout", (req, res) => {
  const t = adminToken(req);
  if (t) {
    adminTokens.delete(tokenHash(t));
    saveTokens();
    adminStreams.forEach((tok, r) => { if (tok === t) { r.end(); adminStreams.delete(r); } });
  }
  res.setHeader("Set-Cookie", `${COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0`);
  res.json({ ok: true });
});

app.get("/api/admin/me", (req, res) => res.json({ admin: isAdmin(req) }));

app.get("/api/admin/stream", requireAdmin, (req, res) => {
  openStream(res);
  adminStreams.set(res, adminToken(req));
  req.on("close", () => adminStreams.delete(res));
});

app.get("/api/admin/sessions", requireAdmin, (req, res) => {
  res.json({
    sessions: store.all().map(summary),
    tally: tally(),
    now: now(),
    persistent: store.persistent,
    sessionMinutes: SESSION_MINUTES,
    purgeAfterHours: PURGE_AFTER_HOURS,
  });
});

const cleanTemplates = (t = {}) => ({ fit: clean(t.fit, 2000), structure: clean(t.structure, 2000), dates: clean(t.dates, 2000) });

app.post("/api/admin/sessions", requireAdmin, (req, res) => {
  const b = req.body || {};
  const firstName = clean(b.firstName, 40);
  const degree = clean(b.degree, 40);
  const topic = clean(b.topic, 200);
  if (!firstName || !degree || !topic) return res.status(400).json({ error: "first name, degree and topic are required" });
  const s = store.create({
    firstName,
    degree,
    topic,
    year: clean(b.year, 12) || "2026-27",
    notesName: clean(b.notesName, 80),
    started: clean(b.started, 60),
    templates: cleanTemplates(b.templates),
  });
  toAdmins("session", sessionEvent(s));
  res.status(201).json(adminView(s, req));
});

app.get("/api/admin/sessions/:id", requireAdmin, findSession, (req, res) => res.json(adminView(req.pilotSession, req)));

app.post("/api/admin/sessions/:id/messages", requireAdmin, findSession, (req, res) => {
  const s = req.pilotSession;
  if (s.status !== "open") return res.status(409).json({ error: "closed" });
  const b = req.body || {};
  const clientId = clean(b.clientId, 40);
  const dup = clientId && s.messages.find((m) => m.clientId === clientId);
  if (dup) return res.status(200).json(dup);
  const text = clean(b.text, 4000);
  if (!text) return res.status(400).json({ error: "empty" });
  if (s.messages.length >= MAX_MESSAGES) return res.status(413).json({ error: "session_full" });
  const m = { id: newId(), clientId: clientId || undefined, role: "tfgpt", text, at: now() };
  s.messages.push(m);
  store.update(s);
  toStudent(s.id, "typing", { typing: false });
  toStudent(s.id, "message", m);
  toAdmins("message", { sessionId: s.id, message: m, summary: summary(s) });
  res.status(201).json(m);
});

app.post("/api/admin/sessions/:id/typing", requireAdmin, findSession, (req, res) => {
  toStudent(req.pilotSession.id, "typing", { typing: Boolean((req.body || {}).typing) });
  res.status(204).end();
});

app.post("/api/admin/sessions/:id/clock", requireAdmin, findSession, (req, res) => {
  const s = req.pilotSession;
  s.clockAt = now();
  store.update(s);
  toAdmins("session", sessionEvent(s));
  res.json(summary(s));
});

app.patch("/api/admin/sessions/:id", requireAdmin, findSession, (req, res) => {
  // only the fields sent are changed, so two consoles don't overwrite each other
  const s = req.pilotSession;
  const b = req.body || {};
  const o = b.observation || {};
  if (o.tasks && typeof o.tasks === "object") {
    for (const i of [0, 1, 2]) if (typeof o.tasks[i] === "boolean") s.observation.tasks[i] = o.tasks[i];
  }
  if ([true, false, null].includes(o.ownAI)) s.observation.ownAI = o.ownAI;
  for (const [k, max] of [["ownAIMinute", 8], ["switchedFor", 200], ["note", 600], ["usedForEach", 600]]) {
    if (typeof o[k] === "string") s.observation[k] = clean(o[k], max);
  }
  if (["instead", "alongside", "neither", ""].includes(o.insteadOrAlongside)) s.observation.insteadOrAlongside = o.insteadOrAlongside;
  if (typeof b.started === "string") s.started = clean(b.started, 60);
  if (typeof b.degree === "string" && clean(b.degree, 40)) s.degree = clean(b.degree, 40);
  if (typeof b.rehearsal === "boolean") s.rehearsal = b.rehearsal;
  if (b.templates && typeof b.templates === "object" && s.status === "open") s.templates = { ...s.templates, ...cleanTemplates({ ...s.templates, ...b.templates }) };
  store.update(s);
  toAdmins("session", sessionEvent(s));
  res.json({ ...sessionEvent(s), tally: tally() });
});

app.post("/api/admin/sessions/:id/close", requireAdmin, findSession, (req, res) => {
  const s = req.pilotSession;
  if (s.status !== "open") return res.status(409).json({ error: "already_closed" });
  closeSession(s, Boolean((req.body || {}).keepTranscript));
  res.json(adminView(s, req));
});

app.post("/api/admin/sessions/:id/purge", requireAdmin, findSession, (req, res) => {
  const s = req.pilotSession;
  if (s.status === "open") return res.status(409).json({ error: "close_it_first" });
  purge(s);
  store.update(s);
  toAdmins("session", sessionEvent(s));
  res.json(adminView(s, req));
});

app.delete("/api/admin/sessions/:id", requireAdmin, findSession, (req, res) => {
  const id = req.pilotSession.id;
  toStudent(id, "closed", {});
  endStudentStreams(id);
  studentBurst.delete(id);
  store.remove(id);
  toAdmins("removed", { id });
  res.status(204).end();
});

const csvCell = (v) => {
  const s = v === null || v === undefined ? "" : String(v);
  const safe = /^[=+\-@\t\r]/.test(s) ? `'${s}` : s; // keep spreadsheet formulas out
  return /[",\n]/.test(safe) ? `"${safe.replace(/"/g, '""')}"` : safe;
};

app.get("/api/admin/export.csv", requireAdmin, (req, res) => {
  const head = ["number", "rehearsal", "degree", "started", "task_1_fit", "task_2_structure", "task_3_dates", "opened_own_ai",
    "own_ai_minute", "turns", "switched_for", "note", "used_for_each", "instead_or_alongside", "completed_without_own_ai", "status"];
  const yn = (v) => (v === true ? "y" : v === false ? "n" : "");
  const rows = store.all().map((s) => {
    const o = s.observation;
    return [s.number, s.rehearsal ? "y" : "", s.degree, s.started, yn(o.tasks[0]), yn(o.tasks[1]), yn(o.tasks[2]), yn(o.ownAI),
      o.ownAIMinute, s.turns || 0, o.switchedFor, o.note, o.usedForEach, o.insteadOrAlongside, completedWithoutOwnAI(s) ? "y" : "n", s.status];
  });
  const t = tally();
  const lines = [head, ...rows].map((r) => r.map(csvCell).join(","));
  lines.push("", csvCell(`Completed all three tasks in TFGPT without opening own AI: ${t.completed} / ${t.recorded} (threshold ${t.threshold} of ${t.sample}; rehearsals excluded)`), csvCell(t.decision));
  res.setHeader("Content-Type", "text/csv; charset=utf-8");
  res.setHeader("Content-Disposition", 'attachment; filename="tfgpt-observation-sheet.csv"');
  res.send(`﻿${lines.join("\n")}\n`); // BOM so Excel shows accents correctly
});

app.get("/healthz", (req, res) => res.json({ ok: true }));
app.use((req, res) => res.status(404).sendFile(path.join(__dirname, "public", "index.html")));
// no stack traces to the browser, ever
app.use((err, req, res, next) => { // eslint-disable-line no-unused-vars
  if (err.status !== 400 && err.type !== "entity.parse.failed") console.error(err);
  res.status(err.status && err.status < 500 ? err.status : 500).json({ error: err.status && err.status < 500 ? "bad_request" : "server_error" });
});

// housekeeping: expire old logins and rate-limit entries
setInterval(() => {
  const t = Date.now();
  let expired = false;
  adminTokens.forEach((exp, h) => { if (exp < t) { adminTokens.delete(h); expired = true; } });
  if (expired) saveTokens();
  loginFailures.forEach((list, ip) => { const keep = list.filter((x) => t - x < 600000); if (keep.length) loginFailures.set(ip, keep); else loginFailures.delete(ip); });
  studentBurst.forEach((list, id) => { const keep = list.filter((x) => t - x < 60000); if (keep.length) studentBurst.set(id, keep); else studentBurst.delete(id); });
}, 60000).unref();

setInterval(() => {
  studentStreams.forEach((set) => set.forEach((r) => r.write(": ping\n\n")));
  adminStreams.forEach((t, r) => r.write(": ping\n\n"));
}, 20000).unref();

const server = app.listen(PORT, () => console.log(`TFGPT pilot on :${PORT} (sessions in ${store.dir})`));
process.on("SIGTERM", () => {
  studentStreams.forEach((set) => set.forEach((r) => r.end()));
  adminStreams.forEach((t, r) => r.end());
  server.close(() => process.exit(0));
  if (server.closeAllConnections) server.closeAllConnections();
  setTimeout(() => process.exit(0), 3000).unref();
});
