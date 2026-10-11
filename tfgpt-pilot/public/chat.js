"use strict";

(() => {
  const token = decodeURIComponent(location.pathname.split("/")[2] || "");
  const api = `/api/s/${encodeURIComponent(token)}`;
  const $ = (id) => document.getElementById(id);
  const log = $("log");
  const input = $("input");
  const send = $("send");
  const seen = new Set();
  let typingTimer = null;
  let es = null;
  let retryDelay = 1000;
  let closed = false;
  let rendered = false;

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text; // never innerHTML: messages are plain text
    return n;
  };
  const toBottom = () => { log.scrollTop = log.scrollHeight; };
  const newClientId = () => (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`);

  function addMessage(m) {
    if (m.id && seen.has(m.id)) return;
    if (m.id) seen.add(m.id);
    log.append(el("div", `msg ${m.role === "student" ? "student" : "tfgpt"}`, m.text));
    if (m.role !== "student") $("typing").hidden = true;
    toBottom();
  }

  function ended() {
    closed = true;
    if (es) { es.close(); es = null; }
    $("composer").hidden = true;
    $("suggest").hidden = true;
    $("typing").hidden = true;
    if (!document.querySelector(".ended")) log.after(el("p", "ended", "This pilot session has ended. Thank you for testing TFGPT."));
  }

  function notActive() {
    closed = true;
    $("chips").hidden = true;
    $("suggest").hidden = true;
    $("composer").hidden = true;
    log.replaceChildren(el("div", "msg tfgpt", "This pilot link is not active. Ask the person running the session for a new link."));
  }

  function showError(text) {
    $("err").textContent = text;
    $("err").hidden = !text;
  }

  function renderFrame(s) {
    $("badge").textContent = s.badge;
    $("who").textContent = [s.firstName, s.degree, s.year].filter(Boolean).join(" · ");
    const chips = $("chips");
    chips.replaceChildren();
    if (s.topic) chips.append(el("span", "chip", `Topic: ${s.topic}`));
    chips.append(el("span", "chip", `Guidelines: TFG ${s.year} (${s.degree}) loaded`));
    if (s.notesName) chips.append(el("span", "chip", `Your notes: ${s.notesName}`));
    const notes = s.notesName ? ", the TFG guidelines for your degree and the notes you sent" : " and the TFG guidelines for your degree";
    const hello = `Hi${s.firstName ? ` ${s.firstName}` : ""}. I have your TFG topic${notes}. ` +
      "Ask me whether your idea fits your topic, which sections and format the TFG needs, the key dates, " +
      "or paste a paragraph and I'll check it against the guidelines.";
    log.append(el("div", "msg tfgpt", hello));
    log.append(el("p", "hint", "Pilot: replies can take up to a minute."));
    rendered = true;
  }

  // fetch the whole session and add anything this page missed (used on load and after every reconnect)
  async function sync() {
    if (closed && rendered) return;
    let r;
    try {
      r = await fetch(api, { cache: "no-store" });
    } catch {
      showError(rendered ? "Connection lost. Reconnecting…" : "Loading… (retrying)");
      return false;
    }
    if (r.status === 404) { notActive(); return false; }
    if (!r.ok) { showError(rendered ? "Connection lost. Reconnecting…" : "Loading… (retrying)"); return false; }
    const s = await r.json();
    showError("");
    if (!rendered) renderFrame(s);
    s.messages.forEach(addMessage);
    if (s.status !== "open") ended();
    return true;
  }

  function listen() {
    if (closed) return;
    if (es) es.close();
    es = new EventSource(`${api}/stream`);
    es.onopen = () => { retryDelay = 1000; sync(); };
    es.addEventListener("message", (e) => addMessage(JSON.parse(e.data)));
    es.addEventListener("typing", (e) => {
      const { typing } = JSON.parse(e.data);
      $("typing").hidden = !typing;
      clearTimeout(typingTimer);
      if (typing) typingTimer = setTimeout(() => { $("typing").hidden = true; }, 9000);
      toBottom();
    });
    es.addEventListener("closed", ended);
    es.onerror = () => {
      if (closed || es.readyState !== EventSource.CLOSED) return; // the browser retries by itself
      es = null;
      setTimeout(async () => { if (await sync()) listen(); else setTimeout(listen, retryDelay); }, retryDelay);
      retryDelay = Math.min(retryDelay * 2, 10000);
    };
  }

  async function start() {
    while (!(await sync())) {
      if (closed) return;
      await new Promise((ok) => setTimeout(ok, retryDelay));
      retryDelay = Math.min(retryDelay * 2, 10000);
    }
    if (closed) return;
    listen();
    input.focus();
  }

  // a phone that slept or a tab that was in the background catches up when it comes back
  document.addEventListener("visibilitychange", () => { if (!document.hidden && rendered) sync(); });
  window.addEventListener("online", () => { if (rendered) { sync(); listen(); } });
  setInterval(() => { if (!document.hidden && rendered && !closed) sync(); }, 15000);

  function grow() {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 200)}px`;
    input.style.overflowY = input.scrollHeight > 200 ? "auto" : "hidden";
  }

  let pending = null; // { text, clientId } while a message is being sent
  async function submit(e) {
    e.preventDefault();
    const text = input.value.trim();
    if (!text || pending) return;
    pending = { text, clientId: newClientId() };
    send.disabled = true;
    input.value = "";
    grow();
    showError("");
    try {
      for (let attempt = 0; ; attempt++) {
        try {
          const r = await fetch(`${api}/messages`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pending),
          });
          if (r.status === 409) return ended();
          if (!r.ok) throw new Error(String(r.status));
          addMessage(await r.json());
          return;
        } catch (err) {
          if (attempt >= 2) throw err;
          await new Promise((ok) => setTimeout(ok, 800 * (attempt + 1))); // same clientId, so no duplicate
        }
      }
    } catch {
      if (!input.value) { input.value = pending.text; grow(); }
      showError("Couldn't send that. Check your connection and try again.");
    } finally {
      pending = null;
      send.disabled = false;
      input.focus();
    }
  }

  $("composer").addEventListener("submit", submit);
  input.addEventListener("input", grow);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) submit(e);
  });
  $("suggest").addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") return;
    input.value = e.target.textContent;
    grow();
    input.focus();
  });

  start();
})();
