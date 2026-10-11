"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const sessions = new Map(); // id -> summary
  const drafts = new Map(); // id -> unsent answer text
  let current = null; // full session object
  let shownIds = new Set(); // message ids in the transcript on screen
  let tally = null;
  let es = null;
  let retryDelay = 1000;
  let offset = 0; // server clock minus this laptop's clock
  let sessionMinutes = 20;
  let typingSent = 0;
  let typingStop = null;
  let unread = 0;
  const obsDirty = new Set(); // observation fields changed since the last save
  let saveTimer = null;
  let saving = null; // promise of the save in flight

  const OUT_OF_SCOPE = "I don't have that in the TFG guidelines for your degree; that one is for your supervisor.";
  const CLARIFY = "Quick check before I answer: ";

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  };
  const newClientId = () => (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`);
  async function api(url, opts = {}) {
    const r = await fetch(url, { ...opts, headers: { "Content-Type": "application/json", ...(opts.headers || {}) } });
    if (r.status === 401) { showLogin(); throw new Error("unauthorised"); }
    return r;
  }
  const errorText = async (r) => { try { return (await r.json()).error || `error ${r.status}`; } catch { return `error ${r.status}`; } };
  const secs = (iso) => Math.max(0, Math.floor((Date.now() + offset - Date.parse(iso)) / 1000));
  const mmss = (n) => `${Math.floor(n / 60)}:${String(n % 60).padStart(2, "0")}`;
  const showErr = (id, text) => { $(id).textContent = text || ""; $(id).hidden = !text; };

  // ---- login --------------------------------------------------------------
  function showLogin() {
    if (es) { es.close(); es = null; }
    $("offline").hidden = true;
    $("app").hidden = true;
    $("login").hidden = false;
    $("key").focus();
  }
  $("login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const r = await fetch("/api/admin/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ key: $("key").value }) });
    if (!r.ok) return showErr("loginErr", r.status === 429 ? "Too many attempts. Wait a few minutes." : "Wrong key.");
    $("key").value = "";
    showErr("loginErr", "");
    start();
  });
  $("logout").addEventListener("click", async () => {
    await fetch("/api/admin/logout", { method: "POST" });
    showLogin();
  });

  // ---- session list -------------------------------------------------------
  function renderTally() {
    const t = $("tally");
    t.replaceChildren();
    if (!tally) return;
    const line = el("div");
    line.append("Completed in TFGPT without own AI: ", el("b", "", `${tally.completed} / ${tally.recorded}`), ` (threshold ${tally.threshold} of ${tally.sample})`);
    t.append(line, el("div", "dec", tally.decision));
  }

  function renderList() {
    const ul = $("list");
    ul.replaceChildren();
    const all = [...sessions.values()].sort((a, b) => (a.status === b.status ? b.number - a.number : a.status === "open" ? -1 : 1));
    for (const s of all) {
      const li = el("li");
      const b = el("button");
      b.type = "button";
      if (current && current.id === s.id) b.setAttribute("aria-current", "true");
      const l1 = el("span", "l1");
      l1.append(el("span", "", `#${s.number} ${s.firstName || "(name removed)"}${s.rehearsal ? " · rehearsal" : ""}`));
      if (s.waitingSince) {
        const w = el("span", "wait");
        w.dataset.waiting = s.waitingSince;
        l1.append(w);
      } else {
        l1.append(el("span", "tag", s.status === "open" ? (s.openedAt ? "live" : "not opened") : "closed"));
      }
      const l2 = el("span", "l2");
      const parts = [s.degree, `${s.turns} turns`];
      if (s.recorded) parts.push(s.completed ? "completed without own AI" : "recorded");
      l2.append(parts.join(" · "));
      if (s.clockAt && s.status === "open") {
        const c = el("span");
        c.dataset.clock = s.clockAt;
        l2.append(" · ", c);
      }
      b.append(l1, l2);
      b.addEventListener("click", () => select(s.id));
      li.append(b);
      ul.append(li);
    }
    tick();
  }

  // timers update in place every second, so clicks on the list are never lost
  function tick() {
    document.querySelectorAll("[data-waiting]").forEach((n) => {
      const w = secs(n.dataset.waiting);
      n.textContent = `waiting ${mmss(w)}`;
      n.className = `wait${w >= 60 ? " late" : ""}`;
    });
    document.querySelectorAll("[data-clock]").forEach((n) => {
      const c = secs(n.dataset.clock);
      n.textContent = `clock ${mmss(c)}`;
      n.className = c >= sessionMinutes * 60 ? "over" : "";
    });
  }

  // ---- conversation -------------------------------------------------------
  function renderHead() {
    if (!current) return;
    const s = sessions.get(current.id) || current.summary;
    $("convTitle").textContent = `#${current.number} ${current.firstName || "(name removed)"} · ${current.degree}`;
    const bits = [current.topic ? `Topic: ${current.topic}` : null];
    if (current.status === "open" && s.clockAt) bits.push(`clock ${mmss(secs(s.clockAt))}${secs(s.clockAt) >= sessionMinutes * 60 ? " (past the session length)" : ""}`);
    if (current.status === "open" && s.waitingSince) bits.push(`waiting ${mmss(secs(s.waitingSince))}`);
    if (current.status !== "open") bits.push(current.transcriptKept ? "closed, transcript kept" : "closed, transcript deleted");
    $("convMeta").textContent = bits.filter(Boolean).join(" · ");
  }

  function addBubble(m) {
    if (shownIds.has(m.id)) return;
    shownIds.add(m.id);
    const log = $("log");
    if (log.querySelector(".empty")) log.replaceChildren();
    const b = el("div", `msg ${m.role === "student" ? "student" : "tfgpt"}`, m.text);
    b.title = new Date(m.at).toLocaleTimeString();
    log.append(b);
    log.scrollTop = log.scrollHeight;
  }

  function renderConversation() {
    const log = $("log");
    log.replaceChildren();
    shownIds = new Set();
    if (!current.messages.length) log.append(el("p", "empty", current.status === "open" ? "No messages yet." : "Transcript deleted when the session closed."));
    current.messages.forEach(addBubble);
    const open = current.status === "open";
    $("reply").hidden = !open;
    $("linkbox").hidden = !open;
    $("link").textContent = current.link;
    $("endBox").hidden = false;
    $("close").disabled = !open;
    $("keep").disabled = !open;
    $("purge").hidden = open || !current.transcriptKept;
    $("tplBox").hidden = !open;
    showErr("endErr", "");
    renderHead();
  }

  function renderObservation() {
    const f = $("obs");
    f.hidden = false;
    const o = current.observation;
    const set = (name, apply) => { if (!obsDirty.has(name)) apply(); };
    set("degree", () => { f.degree.value = current.degree || ""; });
    set("started", () => { f.started.value = current.started || ""; });
    set("t0", () => { f.t0.checked = o.tasks[0]; });
    set("t1", () => { f.t1.checked = o.tasks[1]; });
    set("t2", () => { f.t2.checked = o.tasks[2]; });
    set("ownAI", () => { f.ownAI.value = o.ownAI === true ? "yes" : o.ownAI === false ? "no" : ""; });
    for (const k of ["ownAIMinute", "switchedFor", "note", "usedForEach", "insteadOrAlongside"]) set(k, () => { f[k].value = o[k]; });
    set("rehearsal", () => { f.rehearsal.checked = Boolean(current.rehearsal); });
    $("turns").textContent = `Turns (student messages): ${current.turns || 0}. Counts as completed only if all three tasks were done in TFGPT and their own AI was never opened.`;
  }

  function renderTemplates() {
    const f = $("tplForm");
    if (f.contains(document.activeElement)) return; // don't overwrite what the wizard is editing
    const t = current.templates || {};
    f.fit.value = t.fit || ""; f.structure.value = t.structure || ""; f.dates.value = t.dates || "";
  }

  async function flushObservation() {
    clearTimeout(saveTimer);
    saveTimer = null;
    if (obsDirty.size) await saveObservation();
    else if (saving) await saving;
  }

  async function load(id) {
    const r = await api(`/api/admin/sessions/${id}`);
    if (!r.ok) return null;
    return r.json();
  }

  async function select(id) {
    if (current && current.id === id) return;
    await flushObservation();
    if (current) drafts.set(current.id, $("answer").value);
    const s = await load(id);
    if (!s) return;
    current = s;
    obsDirty.clear();
    $("keep").checked = false; // consent is per student, never carried over
    renderConversation();
    renderObservation();
    renderTemplates();
    renderList();
    $("saved").textContent = "";
    $("answer").value = drafts.get(id) || "";
    showErr("endErr", "");
    if (current.status === "open") $("answer").focus();
  }

  // after a reconnect: pick up anything missed without touching the answer box or unsaved edits
  async function reloadCurrent() {
    if (!current) return;
    const s = await load(current.id);
    if (!s) return;
    const statusChanged = s.status !== current.status;
    current = s;
    if (statusChanged) renderConversation();
    else s.messages.forEach(addBubble);
    renderObservation();
    renderTemplates();
    renderHead();
  }

  // ---- answering ----------------------------------------------------------
  let sendingAnswer = false;
  async function sendAnswer(e) {
    e.preventDefault();
    if (sendingAnswer || !current) return;
    const text = $("answer").value.trim();
    if (!text) return;
    sendingAnswer = true;
    $("sendAnswer").disabled = true;
    const target = current;
    const body = JSON.stringify({ text, clientId: newClientId() });
    try {
      let r;
      for (let attempt = 0; attempt < 3; attempt++) {
        try { r = await api(`/api/admin/sessions/${target.id}/messages`, { method: "POST", body }); break; } catch (err) {
          if (err.message === "unauthorised" || attempt === 2) throw err;
          await new Promise((ok) => setTimeout(ok, 700 * (attempt + 1))); // same clientId, so no duplicate
        }
      }
      if (!r.ok) {
        $("replyMeta").textContent = `Not sent (${await errorText(r)}). Your text is still here.`;
        return;
      }
      const m = await r.json();
      if (current === target) { $("answer").value = ""; addBubble(m); current.messages.push(m); }
      drafts.delete(target.id);
      typingSent = 0;
      $("replyMeta").textContent = "Enter sends · Shift+Enter new line";
    } catch {
      $("replyMeta").textContent = "Not sent: connection problem. Your text is still here.";
    } finally {
      sendingAnswer = false;
      $("sendAnswer").disabled = false;
      $("answer").focus();
    }
  }
  $("reply").addEventListener("submit", sendAnswer);
  $("answer").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) sendAnswer(e);
  });
  $("answer").addEventListener("input", () => {
    if (!current) return;
    const id = current.id;
    const t = Date.now();
    if (t - typingSent > 2500) {
      typingSent = t;
      api(`/api/admin/sessions/${id}/typing`, { method: "POST", body: JSON.stringify({ typing: true }) }).catch(() => {});
    }
    clearTimeout(typingStop);
    typingStop = setTimeout(() => {
      typingSent = 0;
      api(`/api/admin/sessions/${id}/typing`, { method: "POST", body: JSON.stringify({ typing: false }) }).catch(() => {});
    }, 4000);
  });
  $("snips").addEventListener("click", (e) => {
    const k = e.target.dataset && e.target.dataset.snip;
    if (!k || !current) return;
    const tpl = k === "out" ? OUT_OF_SCOPE : k === "clarify" ? CLARIFY : (current.templates || {})[k];
    if (!tpl) { $("replyMeta").textContent = `No ${k} template for this session: write it, citing the guideline section, or add it under "Edit this session's templates".`; return; }
    const a = $("answer");
    a.value = a.value ? `${a.value}\n${tpl}` : tpl;
    a.focus();
  });
  async function copyText(text, button) {
    const label = button.textContent;
    try { await navigator.clipboard.writeText(text); button.textContent = "Copied"; } catch { button.textContent = "Select and copy by hand"; }
    setTimeout(() => { button.textContent = label; }, 1500);
  }
  $("copy").addEventListener("click", () => current && copyText(current.link, $("copy")));
  $("copyBrief").addEventListener("click", () => copyText($("brief").innerText.trim(), $("copyBrief")));
  $("clock").addEventListener("click", async () => {
    if (!current || !confirm(`Restart the clock for #${current.number} now?`)) return;
    const r = await api(`/api/admin/sessions/${current.id}/clock`, { method: "POST" });
    if (r.ok) { sessions.set(current.id, await r.json()); renderList(); renderHead(); }
  });

  // ---- observation sheet --------------------------------------------------
  $("obs").addEventListener("input", (e) => {
    if (!e.target.name) return;
    obsDirty.add(e.target.name);
    clearTimeout(saveTimer);
    $("saved").textContent = "…";
    saveTimer = setTimeout(saveObservation, 500);
  });
  $("obs").addEventListener("submit", (e) => e.preventDefault());

  async function saveObservation() {
    if (saving) await saving;
    if (!current || !obsDirty.size) return;
    const target = current;
    const f = $("obs");
    const fields = [...obsDirty];
    obsDirty.clear();
    const body = { observation: {} };
    for (const k of fields) {
      if (k === "degree") body.degree = f.degree.value;
      else if (k === "started") body.started = f.started.value;
      else if (k === "rehearsal") body.rehearsal = f.rehearsal.checked;
      else if (/^t[012]$/.test(k)) (body.observation.tasks = body.observation.tasks || {})[k[1]] = f[k].checked;
      else if (k === "ownAI") body.observation.ownAI = f.ownAI.value === "yes" ? true : f.ownAI.value === "no" ? false : null;
      else body.observation[k] = f[k].value;
    }
    saving = (async () => {
      try {
        const r = await api(`/api/admin/sessions/${target.id}`, { method: "PATCH", body: JSON.stringify(body) });
        if (!r.ok) throw new Error(await errorText(r));
        const d = await r.json();
        tally = d.tally;
        sessions.set(d.id, d);
        if (current && current.id === d.id) {
          Object.assign(current, { observation: d.observation, degree: d.degree, started: d.started, rehearsal: d.rehearsal });
          $("saved").textContent = obsDirty.size ? "…" : "saved";
        }
        renderTally();
        renderList();
        renderHead();
      } catch (err) {
        if (current === target) { fields.forEach((k) => obsDirty.add(k)); $("saved").textContent = "not saved, retrying"; saveTimer = setTimeout(saveObservation, 3000); }
      } finally {
        saving = null;
      }
    })();
    return saving;
  }
  window.addEventListener("beforeunload", (e) => {
    if (obsDirty.size || saving) { saveObservation(); e.preventDefault(); }
  });

  // ---- templates ----------------------------------------------------------
  $("tplForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!current) return;
    const f = e.target;
    const r = await api(`/api/admin/sessions/${current.id}`, { method: "PATCH", body: JSON.stringify({ templates: { fit: f.fit.value, structure: f.structure.value, dates: f.dates.value } }) });
    $("tplSaved").textContent = r.ok ? "saved" : "not saved";
    if (r.ok) current.templates = (await r.json()).templates;
  });

  // ---- close / delete -----------------------------------------------------
  $("close").addEventListener("click", async () => {
    if (!current) return;
    const keep = $("keep").checked;
    const who = `#${current.number} ${current.firstName}`;
    if (!confirm(`Close ${who}? Did you do the reveal and the two questions?\n\nTranscript, name and topic will be ${keep ? "KEPT (the student agreed)" : "DELETED"}.`)) return;
    await flushObservation();
    try {
      const r = await api(`/api/admin/sessions/${current.id}/close`, { method: "POST", body: JSON.stringify({ keepTranscript: keep }) });
      if (!r.ok) return showErr("endErr", `Not closed: ${await errorText(r)}`);
      current = await r.json();
      $("keep").checked = false;
      sessions.set(current.id, current.summary);
      renderConversation();
      renderObservation();
      renderList();
    } catch { showErr("endErr", "Not closed: connection problem."); }
  });
  $("purge").addEventListener("click", async () => {
    if (!current || !confirm(`Delete the kept transcript, name and topic of #${current.number}? The observation row stays.`)) return;
    const r = await api(`/api/admin/sessions/${current.id}/purge`, { method: "POST" });
    if (!r.ok) return showErr("endErr", `Not deleted: ${await errorText(r)}`);
    current = await r.json();
    renderConversation();
    renderList();
  });
  $("del").addEventListener("click", async () => {
    if (!current || !confirm(`Delete #${current.number} completely, including its observation row? This cannot be undone.`)) return;
    try {
      const r = await api(`/api/admin/sessions/${current.id}`, { method: "DELETE" });
      if (!r.ok) return showErr("endErr", `Not deleted: ${await errorText(r)}`);
      clearView("Session deleted.");
      refresh();
    } catch { showErr("endErr", "Not deleted: connection problem."); }
  });

  function clearView(text) {
    if (current) { sessions.delete(current.id); drafts.delete(current.id); }
    current = null;
    obsDirty.clear();
    $("log").replaceChildren(el("p", "empty", text));
    for (const id of ["reply", "linkbox", "obs", "endBox", "tplBox"]) $(id).hidden = true;
    $("convTitle").textContent = "No session selected";
    $("convMeta").textContent = "";
    renderList();
  }

  // ---- new session --------------------------------------------------------
  $("newBtn").addEventListener("click", () => { $("newForm").hidden = false; $("newForm").firstName.focus(); });
  $("cancelNew").addEventListener("click", () => { $("newForm").hidden = true; showErr("newErr", ""); });
  $("copyPrev").addEventListener("click", async () => {
    const candidates = [...sessions.values()].filter((s) => s.status === "open").sort((a, b) => b.number - a.number);
    for (const c of candidates) {
      const s = await load(c.id);
      const t = s && s.templates;
      if (t && (t.fit || t.structure || t.dates)) {
        const f = $("newForm");
        f.fit.value = t.fit; f.structure.value = t.structure; f.dates.value = t.dates;
        return showErr("newErr", `Copied from #${s.number}. Check the fit template fits this student's topic.`);
      }
    }
    showErr("newErr", "No open session has templates to copy.");
  });
  $("newForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = e.target;
    const v = (k) => f[k].value.trim();
    if (!v("firstName") || !v("degree") || !v("topic")) return showErr("newErr", "First name, degree and topic are required.");
    const body = {
      firstName: v("firstName"), degree: v("degree"), year: v("year"), started: v("started"), topic: v("topic"), notesName: v("notesName"),
      templates: { fit: f.fit.value, structure: f.structure.value, dates: f.dates.value },
    };
    try {
      const r = await api("/api/admin/sessions", { method: "POST", body: JSON.stringify(body) });
      if (!r.ok) return showErr("newErr", `Not created: ${await errorText(r)}`);
      const s = await r.json();
      f.reset();
      f.year.value = "2026-27";
      f.hidden = true;
      showErr("newErr", "");
      sessions.set(s.id, s.summary);
      await select(s.id);
    } catch { showErr("newErr", "Not created: connection problem."); }
  });

  // ---- live updates -------------------------------------------------------
  function beep() {
    try {
      const ctx = beep.ctx || (beep.ctx = new AudioContext());
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.frequency.value = 880;
      g.gain.setValueAtTime(0.08, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
      o.connect(g).connect(ctx.destination);
      o.start();
      o.stop(ctx.currentTime + 0.25);
    } catch { /* audio needs a user gesture first; the title counter still works */ }
  }
  const setTitle = () => { document.title = unread ? `(${unread}) TFGPT console` : "TFGPT console"; };
  window.addEventListener("focus", () => { unread = 0; setTitle(); });

  function listen() {
    if (es) es.close();
    es = new EventSource("/api/admin/stream");
    es.onopen = () => {
      retryDelay = 1000;
      $("offline").hidden = true;
      refresh();
      reloadCurrent(); // catch up on anything sent while disconnected
    };
    es.addEventListener("session", (e) => {
      const s = JSON.parse(e.data);
      sessions.set(s.id, s);
      if (current && current.id === s.id) {
        const statusChanged = s.status !== current.status;
        Object.assign(current, { status: s.status, firstName: s.firstName, degree: s.degree, started: s.started, observation: s.observation,
          rehearsal: s.rehearsal, transcriptKept: s.transcriptKept, templates: s.templates, turns: s.turns });
        if (statusChanged) {
          // closed from another console: reload, since the transcript may have been deleted
          const id = s.id;
          load(id).then((full) => { if (full && current && current.id === id) { current = full; renderConversation(); renderObservation(); } });
        }
        renderObservation();
        renderTemplates();
        renderHead();
      }
      renderList();
      refreshTally();
    });
    es.addEventListener("message", (e) => {
      const { sessionId, message, summary } = JSON.parse(e.data);
      sessions.set(sessionId, summary);
      if (current && current.id === sessionId) {
        if (!current.messages.some((m) => m.id === message.id)) current.messages.push(message);
        current.turns = summary.turns;
        addBubble(message);
        $("turns").textContent = `Turns (student messages): ${summary.turns}. Counts as completed only if all three tasks were done in TFGPT and their own AI was never opened.`;
      }
      if (message.role === "student") {
        beep();
        if (!document.hasFocus()) { unread += 1; setTitle(); }
      }
      renderList();
      renderHead();
    });
    es.addEventListener("removed", (e) => {
      const { id } = JSON.parse(e.data);
      if (current && current.id === id) clearView("This session was deleted from another console.");
      sessions.delete(id);
      renderList();
      refreshTally();
    });
    es.onerror = () => {
      $("offline").hidden = false;
      if (es.readyState !== EventSource.CLOSED) return; // the browser retries by itself
      es = null;
      setTimeout(async () => {
        try {
          const me = await (await fetch("/api/admin/me")).json();
          if (!me.admin) return showLogin();
        } catch { /* still offline */ }
        listen();
      }, retryDelay);
      retryDelay = Math.min(retryDelay * 2, 10000);
    };
  }

  let tallyTimer = null;
  function refreshTally() {
    clearTimeout(tallyTimer);
    tallyTimer = setTimeout(refresh, 400);
  }

  async function refresh() {
    try {
      const r = await api("/api/admin/sessions");
      if (!r.ok) return;
      const d = await r.json();
      offset = Date.parse(d.now) - Date.now();
      sessionMinutes = d.sessionMinutes;
      document.querySelectorAll("#brief .mins").forEach((n) => { n.textContent = String(d.sessionMinutes); });
      $("ephemeral").hidden = d.persistent;
      sessions.clear();
      d.sessions.forEach((s) => sessions.set(s.id, s));
      tally = d.tally;
      renderTally();
      renderList();
    } catch { /* shown by the offline banner */ }
  }

  async function start() {
    $("login").hidden = true;
    $("app").hidden = false;
    await refresh();
    listen();
  }

  setInterval(() => { tick(); renderHead(); }, 1000);
  setInterval(() => { if ($("app").hidden === false) refresh(); }, 60000);

  fetch("/api/admin/me").then((r) => r.json()).then((d) => (d.admin ? start() : showLogin())).catch(showLogin);
})();
