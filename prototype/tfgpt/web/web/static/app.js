"use strict";
// TFGPT front end. Vanilla JS, no build step. All server and model text goes in via textContent.

const $ = (id) => document.getElementById(id);
const JOB_KEY = "tfgpt.job";
const THEME_KEY = "tfgpt.theme";

const state = {
  messages: [],      // messages currently in the thread
  openFlags: 0,
  maxWords: 3000,
  busy: false,       // an ask or a job is running
  retry: null,       // function re-running the last failed action
};

/* ---------- helpers ---------- */

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

function sget(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
function sset(k, v) { try { if (v == null) sessionStorage.removeItem(k); else sessionStorage.setItem(k, v); } catch (e) { /* ignore */ } }
function lget(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function lset(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }

async function api(path, opts) {
  const o = opts || {};
  const method = o.method || "GET";
  const init = { method, headers: {}, credentials: "same-origin" };
  if (method !== "GET") init.headers["X-TFGPT"] = "1";
  if (o.form) {
    init.body = o.form;
  } else if (o.body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(o.body);
  }
  let res;
  try {
    res = await fetch(path, init);
  } catch (e) {
    throw apiError("network", "Could not reach TFGPT. Check your connection and try again.", 0);
  }
  if (o.raw) return res;
  return parseResponse(res);
}

function apiError(code, message, status) {
  const err = new Error(message);
  err.code = code;
  err.status = status;
  return err;
}

async function parseResponse(res) {
  let data = null;
  try { data = await res.json(); } catch (e) { /* not JSON */ }
  if (!res.ok) {
    throw apiError((data && data.error) || "http_" + res.status,
      (data && data.message) || "Something went wrong (" + res.status + ").", res.status);
  }
  return data;
}

function countWords(s) {
  const t = s.trim();
  return t ? t.split(/\s+/).length : 0;
}

function scrollEnd() {
  window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
}

function pad2(n) { return n < 10 ? "0" + n : String(n); }

/* ---------- theme toggle (IE Midnight Dark default / IE Daylight Light) ---------- */

function applyTheme(theme) {
  const light = theme === "light";
  if (light) document.documentElement.setAttribute("data-theme", "light");
  else document.documentElement.removeAttribute("data-theme");
  const icon = $("themeIcon");
  const btn = $("themeToggle");
  if (icon) icon.textContent = light ? "☾" : "☼";
  if (btn) btn.setAttribute("aria-label", light ? "Switch to dark IE Midnight theme" : "Switch to light IE Daylight theme");
}

function setupTheme() {
  const saved = lget(THEME_KEY);
  applyTheme(saved === "light" ? "light" : "dark");
  const btn = $("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(next);
      lset(THEME_KEY, next);
    });
  }
}

/* ---------- Bartholomew Bear Easter Egg (client-side only, 0 network calls) ---------- */

const BEAR_QUOTES = [
  "Bartholomew reviewed your capstone stress levels: 100% valid. Take a breath, sip some water, and tackle one flag at a time.",
  "No grades, no judgment — just soft toffee fur, verified citations, and steady progress toward M1.",
  "Even Bartholomew had to fix his APA commas before meeting his Segovia advisor. You have got this.",
  "Reminder from Bartholomew: your advisor wants a clear proposal, not perfection on draft one.",
  "Pro tip from Bartholomew: fix the missing-data flag first, celebrate with a coffee, then hit Check again."
];

const bearState = { hugs: 0, quoteIdx: 0, loaded: false };

function openBartholomew() {
  const modal = $("bearModal");
  if (!modal) return;
  if (!bearState.loaded) {
    $("bearImg").src = "/bartholomew.png";
    bearState.loaded = true;
  }
  $("bearQuote").textContent = BEAR_QUOTES[bearState.quoteIdx % BEAR_QUOTES.length];
  modal.hidden = false;
  $("bearClose").focus();
}

function closeBartholomew() {
  const modal = $("bearModal");
  if (modal) modal.hidden = true;
}

function setupEasterEgg() {
  // Trigger 1: Click the TFGPT logo 5 times within 3 seconds
  let clicks = [];
  const brand = $("brandEaster");
  if (brand) {
    brand.addEventListener("click", () => {
      const now = Date.now();
      clicks = clicks.filter((t) => now - t < 3000);
      clicks.push(now);
      if (clicks.length >= 5) {
        clicks = [];
        openBartholomew();
      }
    });
  }

  // Trigger 2: Type "bartholomew" anywhere outside inputs/textareas/selects
  let typed = "";
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && $("bearModal") && !$("bearModal").hidden) {
      closeBartholomew();
      return;
    }
    const tag = (ev.target && ev.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || ev.metaKey || ev.ctrlKey || ev.altKey) return;
    if (ev.key.length === 1 && /[a-z]/i.test(ev.key)) {
      typed = (typed + ev.key.toLowerCase()).slice(-11);
      if (typed === "bartholomew") {
        typed = "";
        openBartholomew();
      }
    }
  });

  const modal = $("bearModal");
  const closeBtn = $("bearClose");
  const hugBtn = $("bearHug");
  if (closeBtn) closeBtn.addEventListener("click", closeBartholomew);
  if (modal) {
    modal.addEventListener("click", (ev) => {
      if (ev.target === modal) closeBartholomew();
    });
  }
  if (hugBtn) {
    hugBtn.addEventListener("click", () => {
      bearState.hugs += 1;
      bearState.quoteIdx += 1;
      $("bearQuote").textContent = BEAR_QUOTES[bearState.quoteIdx % BEAR_QUOTES.length];
      $("bearHugs").textContent = bearState.hugs === 1 ? "1 warm bear hug given" : bearState.hugs + " warm bear hugs given";
      const img = $("bearImg");
      img.classList.remove("hugged");
      void img.offsetWidth;
      img.classList.add("hugged");
      setTimeout(() => img.classList.remove("hugged"), 320);
    });
  }
}

/* ---------- views and errors ---------- */

function showOnboarding() {
  $("onboard").hidden = false;
  $("chatView").hidden = true;
  $("dock").hidden = true;
  $("barTools").hidden = true;
  if ($("navInfo")) $("navInfo").hidden = false;
  $("topicLine").hidden = true;
  sset(JOB_KEY, null);
}

function showChat() {
  $("onboard").hidden = true;
  $("chatView").hidden = false;
  $("dock").hidden = false;
  $("barTools").hidden = false;
  if ($("navInfo")) $("navInfo").hidden = true;
}

function showError(text, retryFn) {
  $("errText").textContent = text;
  $("err").hidden = false;
  state.retry = retryFn || null;
  $("errRetry").hidden = !retryFn;
}

function clearError() {
  $("err").hidden = true;
  $("errText").textContent = "";
  state.retry = null;
}

function handleError(err, retryFn) {
  if (err.code === "no_student") { showOnboarding(); return true; }
  if (err.code === "choose_model") {
    const sel = $("engine");
    sel.classList.add("needs");
    sel.focus();
    showError("Choose an AI model in the top bar first.");
    return true;
  }
  showError(err.message, err.code === "upstream" || err.code === "network" ? retryFn : null);
  return true;
}

function setBusy(b) {
  state.busy = b;
  $("send").disabled = b;
  $("checkBtn").disabled = b;
  $("upload").disabled = b;
}

function updateOpenLedger(n) {
  state.openFlags = n;
  const num = $("openNum");
  const cap = $("openCount");
  if (!num || !cap) return;
  if (!hasCheck()) {
    num.textContent = "—";
    num.className = "ledger-num";
    cap.textContent = "No check run yet";
    return;
  }
  num.textContent = pad2(n);
  num.className = "ledger-num " + (n > 0 ? "has-open" : "all-clear");
  cap.textContent = n === 0 ? "All flags resolved" : plural(n, "open flag", "open flags");
}

function updateEmptyGuide() {
  const empty = $("emptyGuide");
  if (empty) empty.hidden = state.messages.length > 0;
}

/* ---------- session ---------- */

function applyMe(me) {
  if (!me || !me.student) { showOnboarding(); return false; }
  $("code").textContent = me.resume_code || "";
  $("topicEdit").value = me.student.topic || "";
  const who = me.student.alias ? me.student.alias + " — " : "";
  $("topicLine").textContent = who + me.student.topic;
  $("topicLine").hidden = false;
  return true;
}

async function loadSession(me) {
  if (!applyMe(me)) return;
  showChat();
  await Promise.all([loadEngines(), loadThread()]);
  reattachJob();
}

async function boot() {
  api("/api/meta").then((m) => {
    $("version").textContent = "REV " + m.version;
    if (m.max_words) state.maxWords = m.max_words;
    updateWords();
  }).catch(() => { /* footer version is optional */ });
  try {
    const me = await api("/api/me");
    await loadSession(me);
  } catch (e) {
    showOnboarding();
    $("startErr").textContent = e.message;
    $("startErr").hidden = false;
  }
}

/* ---------- onboarding ---------- */

function setupOnboarding() {
  $("startForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const topic = $("topic").value.trim();
    if (!topic) return;
    const alias = $("alias").value.trim();
    $("startErr").hidden = true;
    try {
      const me = await api("/api/start", { method: "POST", body: { topic, alias: alias || null } });
      await loadSession(me);
    } catch (e) {
      $("startErr").textContent = e.message;
      $("startErr").hidden = false;
    }
  });

  $("resumeToggle").addEventListener("click", () => {
    const form = $("resumeForm");
    form.hidden = !form.hidden;
    $("resumeToggle").setAttribute("aria-expanded", String(!form.hidden));
    if (!form.hidden) $("resumeCode").focus();
  });

  $("resumeForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const code = $("resumeCode").value.trim().toUpperCase();
    if (!code) return;
    $("resumeErr").hidden = true;
    try {
      const me = await api("/api/resume", { method: "POST", body: { code } });
      await loadSession(me);
    } catch (e) {
      $("resumeErr").textContent = e.code === "unknown_code" ? "That code was not recognised. Check it and try again." : e.message;
      $("resumeErr").hidden = false;
    }
  });
}

/* ---------- header: engines, code, topic ---------- */

async function loadEngines() {
  try {
    renderEngines(await api("/api/engines"));
  } catch (e) {
    if (e.code === "no_student") showOnboarding();
  }
}

function renderEngines(data) {
  const sel = $("engine");
  sel.textContent = "";
  if (!data.chosen) {
    const ph = el("option", null, "Choose AI model…");
    ph.value = "";
    ph.disabled = true;
    sel.appendChild(ph);
  }
  data.engines.forEach((e) => {
    let label = e.label + " · " + e.vendor;
    if (!e.available) label += e.note ? " (" + e.note + ")" : " (unavailable)";
    const o = el("option", null, label);
    o.value = e.name;
    o.disabled = !e.available;
    sel.appendChild(o);
  });
  sel.value = data.chosen || "";
  const hint = $("assigned");
  if (data.assigned) {
    const found = data.engines.find((e) => e.name === data.assigned);
    hint.textContent = "Assigned: " + (found ? found.label : data.assigned);
    hint.hidden = false;
  } else {
    hint.hidden = true;
  }
}

function setupHeader() {
  $("engine").addEventListener("change", async () => {
    const name = $("engine").value;
    try {
      await api("/api/engine", { method: "POST", body: { name } });
      $("engine").classList.remove("needs");
      clearError();
      await loadEngines();
    } catch (e) {
      handleError(e);
      await loadEngines();
    }
  });

  $("copyCode").addEventListener("click", async () => {
    const note = $("copyNote");
    try {
      await navigator.clipboard.writeText($("code").textContent);
      note.textContent = "Copied. Save it to reopen your session on another device.";
    } catch (e) {
      const range = document.createRange();
      range.selectNodeContents($("code"));
      const s = window.getSelection();
      s.removeAllRanges();
      s.addRange(range);
      note.textContent = "Select and copy the code above.";
    }
  });

  $("topicForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const topic = $("topicEdit").value.trim();
    if (!topic) return;
    try {
      const me = await api("/api/me", { method: "PATCH", body: { topic } });
      applyMe(me);
      $("topicNote").textContent = "Topic updated.";
    } catch (e) {
      if (e.code === "no_student") showOnboarding();
      else $("topicNote").textContent = e.message;
    }
  });
}

/* ---------- thread rendering ---------- */

async function loadThread() {
  try {
    const t = await api("/api/thread");
    const note = $("summaryNote");
    note.textContent = t.summary_note ? "Session resumed: " + t.summary_note : "";
    note.hidden = !t.summary_note;
    renderThread(t.messages);
    updateOpenLedger(t.open_flags || 0);
  } catch (e) {
    handleError(e);
  }
}

function renderThread(messages) {
  state.messages = messages.slice();
  const log = $("log");
  log.textContent = "";
  messages.forEach((m) => log.appendChild(renderMessage(m)));
  updateCheckLabel();
  updateEmptyGuide();
  if (messages.length) scrollEnd();
}

function updateCheckLabel() {
  const has = state.messages.some((m) => m.kind === "check" || m.kind === "recheck");
  $("checkBtn").textContent = has ? "Check again →" : "Check proposal →";
}

function hasCheck() {
  return state.messages.some((m) => m.kind === "check" || m.kind === "recheck");
}

function renderMessage(m) {
  let node;
  switch (m.kind) {
    case "check": node = renderCheck(m); break;
    case "recheck": node = renderRecheck(m); break;
    case "answer": node = renderAnswer(m); break;
    case "work": node = el("div", "chip", "Draft submitted · " + workWords(m)); break;
    case "notice": node = renderNotice(m); break;
    default: node = el("div", "msg " + (m.role === "student" ? "student" : "tfgpt"), m.text);
  }
  node.dataset.id = String(m.id);
  return node;
}

function workWords(m) {
  const found = /(\d[\d,]*)\s*words?/i.exec(m.text || "");
  return found ? found[1] + " words" : (m.text || "");
}

function addMessage(m) {
  const log = $("log");
  if (log.querySelector('[data-id="' + m.id + '"]')) return;
  state.messages.push(m);
  log.appendChild(renderMessage(m));
  updateCheckLabel();
  updateEmptyGuide();
  scrollEnd();
}

function replaceWithMessage(node, m) {
  const log = $("log");
  const dup = log.querySelector('[data-id="' + m.id + '"]');
  if (dup && dup !== node) { node.remove(); return; }
  state.messages.push(m);
  node.replaceWith(renderMessage(m));
  updateCheckLabel();
  updateEmptyGuide();
  scrollEnd();
}

function engineLine(d) {
  let text = "Model: " + (d.engine || "unknown");
  if (d.fallback_from) text += " (fallback from " + d.fallback_from + ")";
  return el("p", "engine-line", text);
}

function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

function hiddenNote(n) {
  const word = n === 1 ? "flag was" : "flags were";
  return el("p", "hidden-note", n + " unverified " + word + " hidden automatically because the quote or guideline section could not be confirmed in code.");
}

function renderCheck(m) {
  const d = m.data || {};
  const flags = d.flags || [];
  const box = el("section", "msg tfgpt wide");
  const head = el("div", "sheet-head");
  head.appendChild(el("h2", null, plural(flags.length, "point", "points") + " to review"));
  head.appendChild(engineLine(d));
  box.appendChild(head);

  const strip = el("div", "meta-strip");
  strip.appendChild(el("span", "meta-item open", pad2(flags.length) + " flagged"));
  strip.appendChild(el("span", "meta-item verified", d.hidden > 0 ? d.hidden + " unverified hidden" : "✓ All quotes code-verified"));
  box.appendChild(strip);

  const stack = el("div", "flag-stack");
  flags.forEach((f) => stack.appendChild(renderFlag(f)));
  box.appendChild(stack);
  if (d.hidden > 0) box.appendChild(hiddenNote(d.hidden));
  return box;
}

function flagList(title, flags, compact) {
  const wrap = el("div");
  wrap.appendChild(el("h3", null, title + " (" + flags.length + ")"));
  if (!flags.length) {
    wrap.appendChild(el("p", "none-note", "None."));
    return wrap;
  }
  const stack = el("div", "flag-stack");
  flags.forEach((f) => stack.appendChild(renderFlag(f, compact)));
  wrap.appendChild(stack);
  return wrap;
}

function renderRecheck(m) {
  const d = m.data || {};
  const box = el("section", "msg tfgpt wide");
  const head = el("div", "sheet-head");
  head.appendChild(el("h2", null, "Re-check results"));
  head.appendChild(engineLine(d));
  box.appendChild(head);

  const solved = (d.solved || []).map((f) => Object.assign({}, f, { status: "solved" }));
  const remaining = d.remaining || [];
  const added = d.new || [];

  const strip = el("div", "meta-strip");
  strip.appendChild(el("span", "meta-item solved", "✓ " + solved.length + " solved"));
  strip.appendChild(el("span", "meta-item open", remaining.length + " still open"));
  strip.appendChild(el("span", "meta-item new", added.length + " new"));
  strip.appendChild(el("span", "meta-item verified", d.hidden > 0 ? d.hidden + " hidden" : "✓ Sources verified"));
  box.appendChild(strip);

  box.appendChild(flagList("Solved", solved, true));
  box.appendChild(flagList("Still open", remaining, false));
  box.appendChild(flagList("New", added, false));
  if (d.hidden > 0) box.appendChild(hiddenNote(d.hidden));
  return box;
}

function renderFlag(f, compact) {
  const card = el("article", "flag");
  card.dataset.flag = String(f.id);
  fillFlag(card, f, compact);
  return card;
}

function fillFlag(card, f, compact) {
  card.textContent = "";
  card.classList.toggle("solved", f.status === "solved");
  card.classList.toggle("dismissed", f.status === "dismissed");

  const top = el("div", "flag-top");
  const ref = el("div", "flag-ref");
  ref.appendChild(el("span", "sec-id", "§ " + f.section_id));
  ref.appendChild(el("span", "sec-title", f.section));
  top.appendChild(ref);

  const right = el("div", "flag-right");
  const statusLabel = f.status === "solved" ? "✓ Solved" : (f.status === "dismissed" ? "Dismissed" : "Open");
  right.appendChild(el("span", "flag-status", statusLabel));

  if (f.status === "open" && !compact) {
    const btn = el("button", "dismiss-btn", "Dismiss");
    btn.type = "button";
    btn.addEventListener("click", () => dismissFlag(card, f, btn));
    right.appendChild(btn);
  } else if (f.status === "dismissed") {
    right.appendChild(el("span", "dismissed-tag", "Excluded from next check"));
  }
  top.appendChild(right);
  card.appendChild(top);

  if (compact && f.status === "solved") {
    if (f.problem) card.appendChild(el("p", "problem", f.problem));
    return;
  }
  if (f.missing) card.appendChild(el("blockquote", "missing", "Missing from your draft"));
  else if (f.quote) card.appendChild(el("blockquote", null, "“" + f.quote + "”"));
  card.appendChild(el("p", "problem", f.problem));
  if (f.route) {
    const r = el("p", "route");
    r.appendChild(el("span", "route-tag", "How to fix:"));
    r.appendChild(document.createTextNode(f.route));
    card.appendChild(r);
  }
}

async function dismissFlag(card, f, btn) {
  btn.disabled = true;
  try {
    const res = await api("/api/flags/" + f.id + "/dismiss", { method: "POST" });
    fillFlag(card, res.flag);
    updateOpenLedger(Math.max(0, state.openFlags - 1));
  } catch (e) {
    btn.disabled = false;
    handleError(e);
  }
}

function renderAnswer(m) {
  const d = m.data || {};
  const box = el("section", "msg tfgpt wide");
  if (d.for_supervisor) {
    box.appendChild(el("p", "supervisor", "That one is for your supervisor"));
  }
  if (m.text) box.appendChild(el("p", "answer-text", m.text));
  const cites = d.citations || [];
  if (cites.length) {
    const src = el("div", "sources");
    src.appendChild(el("h3", null, "Verified guideline quotes"));
    const ul = el("ul");
    cites.forEach((c) => {
      const li = el("li");
      li.appendChild(el("span", "sec-id", "§ " + c.section_id));
      li.appendChild(el("span", "sec-title", c.section));
      if (c.quote) li.appendChild(el("q", null, "“" + c.quote + "”"));
      ul.appendChild(li);
    });
    src.appendChild(ul);
    box.appendChild(src);
  }
  const foot = el("div", "answer-foot");
  foot.appendChild(renderFeedback(m));
  if (d.engine) foot.appendChild(el("p", "engine-line", "Answered by " + d.engine));
  box.appendChild(foot);
  return box;
}

function renderFeedback(m) {
  const row = el("div", "fb");
  const up = el("button", null, "Helpful");
  const down = el("button", null, "Not helpful");
  up.type = down.type = "button";
  up.setAttribute("aria-label", "This answer helped");
  down.setAttribute("aria-label", "This answer did not help");
  const note = el("span", "thanks");
  note.setAttribute("role", "status");
  const mark = (v) => {
    up.setAttribute("aria-pressed", String(v === "up"));
    down.setAttribute("aria-pressed", String(v === "down"));
  };
  mark(m.feedback);
  const send = async (v) => {
    try {
      await api("/api/messages/" + m.id + "/feedback", { method: "POST", body: { value: v } });
      mark(v);
      note.textContent = "Saved";
    } catch (e) { handleError(e); }
  };
  up.addEventListener("click", () => send("up"));
  down.addEventListener("click", () => send("down"));
  row.append(up, down, note);
  return row;
}

function renderNotice(m) {
  const box = el("div", "notice");
  box.appendChild(el("span", null, m.text));
  const retry = m.data && m.data.retry;
  if (retry) {
    const btn = el("button", "btn quiet small", "Retry");
    btn.type = "button";
    btn.addEventListener("click", () => retryCheck(retry));
    box.appendChild(btn);
  }
  return box;
}

function retryCheck(kind) {
  setMode("check");
  if (!$("work").value.trim()) {
    showError("Paste your proposal again, then press the button to retry.");
    $("work").focus();
    return;
  }
  runCheck(kind === "recheck");
}

/* ---------- composer ---------- */

function setMode(mode) {
  const ask = mode === "ask";
  $("tabAsk").setAttribute("aria-selected", String(ask));
  $("tabCheck").setAttribute("aria-selected", String(!ask));
  $("tabAsk").tabIndex = ask ? 0 : -1;
  $("tabCheck").tabIndex = ask ? -1 : 0;
  $("askPanel").hidden = !ask;
  $("checkPanel").hidden = ask;
}

function autoGrow(t) {
  t.style.height = "auto";
  t.style.height = Math.min(t.scrollHeight, 150) + "px";
}

function updateWords() {
  const n = countWords($("work").value);
  const w = $("words");
  w.textContent = n + " / " + state.maxWords + " words" + (n > state.maxWords ? " (over limit)" : "");
  w.classList.toggle("over", n > state.maxWords);
}

function setupComposer() {
  $("tabAsk").addEventListener("click", () => setMode("ask"));
  $("tabCheck").addEventListener("click", () => setMode("check"));
  [$("tabCheck"), $("tabAsk")].forEach((t) => t.addEventListener("keydown", (ev) => {
    if (ev.key === "ArrowLeft" || ev.key === "ArrowRight") {
      const next = t === $("tabAsk") ? "check" : "ask";
      setMode(next);
      (next === "ask" ? $("tabAsk") : $("tabCheck")).focus();
    }
  }));

  const q = $("question");
  q.addEventListener("input", () => autoGrow(q));
  q.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey && !ev.isComposing) {
      ev.preventDefault();
      $("askPanel").requestSubmit();
    }
  });
  $("askPanel").addEventListener("submit", (ev) => { ev.preventDefault(); sendQuestion(); });

  $("work").addEventListener("input", updateWords);
  $("checkPanel").addEventListener("submit", (ev) => { ev.preventDefault(); runCheck(hasCheck()); });
  $("upload").addEventListener("click", () => $("file").click());
  $("file").addEventListener("change", () => uploadFile($("file").files && $("file").files[0]));
  $("errRetry").addEventListener("click", () => { const fn = state.retry; clearError(); if (fn) fn(); });

  const dz = $("dropzone");
  if (dz) {
    ["dragenter", "dragover"].forEach((evName) => dz.addEventListener(evName, (ev) => {
      ev.preventDefault();
      dz.classList.add("drag");
    }));
    ["dragleave", "drop"].forEach((evName) => dz.addEventListener(evName, (ev) => {
      ev.preventDefault();
      dz.classList.remove("drag");
    }));
    dz.addEventListener("drop", (ev) => {
      const f = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
      if (f) uploadFile(f);
    });
  }

  document.querySelectorAll(".starter-card").forEach((card) => {
    card.addEventListener("click", () => {
      if (card.dataset.action === "check") {
        setMode("check");
        $("work").focus();
      } else if (card.dataset.ask) {
        setMode("ask");
        $("question").value = card.dataset.ask;
        autoGrow($("question"));
        sendQuestion();
      }
    });
  });
}

async function uploadFile(file) {
  if (!file) return;
  clearError();
  const form = new FormData();
  form.append("file", file);
  $("upload").disabled = true;
  try {
    const res = await api("/api/extract", { method: "POST", form });
    $("work").value = res.text;
    $("words").textContent = res.words + " / " + state.maxWords + " words";
    $("words").classList.toggle("over", res.words > state.maxWords);
    $("work").focus();
  } catch (e) {
    handleError(e);
  } finally {
    $("upload").disabled = state.busy;
    $("file").value = "";
  }
}

/* ---------- ask (SSE over POST) ---------- */

function drainSSE(buffer, onEvent) {
  buffer = buffer.replace(/\r\n/g, "\n");
  let i;
  while ((i = buffer.indexOf("\n\n")) >= 0) {
    const block = buffer.slice(0, i);
    buffer = buffer.slice(i + 2);
    let name = "message";
    const data = [];
    block.split("\n").forEach((line) => {
      if (line.startsWith(":")) return;
      if (line.startsWith("event:")) name = line.slice(6).trim();
      else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^ /, ""));
    });
    if (!data.length) continue;
    try { onEvent(name, JSON.parse(data.join("\n"))); } catch (e) { /* ignore malformed event */ }
  }
  return buffer;
}

async function sendQuestion() {
  const q = $("question");
  const question = q.value.trim();
  if (!question || state.busy) return;

  // Trigger 3 (client-side only): /bartholomew or /bear opens the hidden study buddy with 0 API calls
  if (/^\/(bartholomew|bear)\b/i.test(question)) {
    q.value = "";
    autoGrow(q);
    openBartholomew();
    return;
  }

  clearError();
  setBusy(true);
  if ($("emptyGuide")) $("emptyGuide").hidden = true;

  const mine = el("div", "msg student", question);
  $("log").appendChild(mine);
  q.value = "";
  autoGrow(q);

  const draft = el("div", "msg tfgpt");
  const label = el("span", "draft-label", "Checking BDBA guidelines…");
  const body = el("span", "draft-text");
  draft.append(label, body);
  $("log").appendChild(draft);
  scrollEnd();

  const fail = (err) => {
    draft.remove();
    mine.remove();
    q.value = question;
    updateEmptyGuide();
    handleError(err, () => { q.value = question; sendQuestion(); });
  };

  try {
    const res = await api("/api/ask", { method: "POST", body: { question }, raw: true });
    if (!res.ok) { await parseResponse(res); return; }
    await readAskStream(res, draft, body, fail);
  } catch (e) {
    fail(e);
  } finally {
    setBusy(false);
  }
}

async function readAskStream(res, draft, body, fail) {
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finished = false;
  const onEvent = (name, data) => {
    if (name === "delta") { body.textContent += data.text || ""; scrollEnd(); }
    else if (name === "done" || name === "failed") {
      finished = true;
      replaceWithMessage(draft, data.message);
    }
  };
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer = drainSSE(buffer + decoder.decode(value, { stream: true }), onEvent);
  }
  buffer = drainSSE(buffer + decoder.decode() + "\n\n", onEvent);
  if (!finished) fail(apiError("upstream", "The answer was cut off. Please try again.", 502));
}

/* ---------- check and recheck (job + EventSource) ---------- */

async function runCheck(isRecheck) {
  if (state.busy) return;
  const work = $("work").value.trim();
  if (!work) { showError("Paste your proposal or upload a file first."); $("work").focus(); return; }
  clearError();
  setBusy(true);
  try {
    const res = await api(isRecheck ? "/api/recheck" : "/api/check", { method: "POST", body: { work } });
    await loadThread();
    watchJob(res.job_id);
  } catch (e) {
    setBusy(false);
    if (e.code === "no_check_yet") { runCheck(false); return; }
    handleError(e, () => runCheck(isRecheck));
  }
}

function progressCard() {
  const card = el("div", "progress");
  card.setAttribute("role", "status");
  card.appendChild(el("strong", null, "CHECKING PROPOSAL · 0 s (USUALLY 1–3 MIN)"));
  card.appendChild(el("span", "step", "Queued for guideline comparison"));
  const track = el("div", "bar-track");
  track.appendChild(el("span"));
  card.appendChild(track);
  return card;
}

function watchJob(jobId) {
  sset(JOB_KEY, String(jobId));
  setBusy(true);
  const card = progressCard();
  $("log").appendChild(card);
  scrollEnd();

  const src = new EventSource("/api/jobs/" + jobId + "/events");
  const finish = (m) => {
    src.close();
    sset(JOB_KEY, null);
    setBusy(false);
    if (m) {
      replaceWithMessage(card, m);
      loadThread();
    } else {
      card.remove();
      loadThread();
    }
  };
  src.addEventListener("progress", (ev) => {
    const d = JSON.parse(ev.data);
    card.firstChild.textContent = "CHECKING PROPOSAL · " + d.seconds + " s (USUALLY 1–3 MIN)";
    card.querySelector(".step").textContent = d.status === "queued" ? "Queued for guideline comparison" : (d.step || "Verifying verbatim quotes & guideline sections");
  });
  src.addEventListener("done", (ev) => finish(JSON.parse(ev.data).message));
  src.addEventListener("failed", (ev) => finish(JSON.parse(ev.data).message));
  src.onerror = () => {
    if (src.readyState === EventSource.CLOSED) finish(null);
  };
}

function reattachJob() {
  const id = sget(JOB_KEY);
  if (id) watchJob(id);
}

/* ---------- start ---------- */

setupTheme();
setupEasterEgg();
setupOnboarding();
setupHeader();
setupComposer();
boot();
