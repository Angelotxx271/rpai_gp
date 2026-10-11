"use strict";

// Sessions live in memory and are mirrored to one JSON file each in DATA_DIR,
// so a redeploy keeps open sessions when a Railway volume is mounted at /data.

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

function dataDir() {
  if (process.env.DATA_DIR) return { dir: process.env.DATA_DIR, persistent: true };
  if (fs.existsSync("/data")) return { dir: "/data", persistent: true };
  return { dir: path.join(__dirname, "data"), persistent: false };
}

function writeAtomic(file, data) {
  fs.writeFileSync(`${file}.tmp`, data);
  fs.renameSync(`${file}.tmp`, file);
}

function makeStore() {
  const base = dataDir();
  const dir = path.join(base.dir, "sessions");
  const metaFile = path.join(base.dir, "meta.json");
  fs.mkdirSync(dir, { recursive: true });
  const sessions = new Map();
  const tokens = new Map(); // student token -> session id

  for (const f of fs.readdirSync(dir)) {
    const file = path.join(dir, f);
    if (f.endsWith(".tmp")) { fs.rmSync(file, { force: true }); continue; } // half-written copy from a crash
    if (!f.endsWith(".json")) continue;
    try {
      const s = JSON.parse(fs.readFileSync(file, "utf8"));
      sessions.set(s.id, s);
      tokens.set(s.token, s.id);
    } catch (err) {
      console.error("could not read session", f, err.message);
    }
  }

  let meta = { nextNumber: 1, currentRound: 1, importedSeeds: [] };
  try { meta = { ...meta, ...JSON.parse(fs.readFileSync(metaFile, "utf8")) }; } catch { /* first run */ }
  for (const s of sessions.values()) meta.nextNumber = Math.max(meta.nextNumber, s.number + 1);
  writeAtomic(metaFile, JSON.stringify(meta));

  const save = (s) => writeAtomic(path.join(dir, `${s.id}.json`), JSON.stringify(s));

  return {
    dir,
    persistent: base.persistent,
    meta: () => JSON.parse(JSON.stringify(meta)),
    setMeta(patch) {
      meta = { ...meta, ...patch };
      writeAtomic(metaFile, JSON.stringify(meta));
      return meta;
    },
    all: () => [...sessions.values()].sort((a, b) => a.number - b.number),
    get: (id) => sessions.get(id) || null,
    byToken: (token) => {
      const id = tokens.get(token);
      return id ? sessions.get(id) || null : null;
    },
    create(fields) {
      const number = meta.nextNumber++; // never reused, even after a delete
      writeAtomic(metaFile, JSON.stringify(meta));
      const s = {
        id: crypto.randomBytes(6).toString("hex"),
        token: crypto.randomBytes(18).toString("base64url"),
        number,
        status: "open",
        round: meta.currentRound,
        rehearsal: false,
        createdAt: new Date().toISOString(),
        openedAt: null,
        clockAt: null,
        closedAt: null,
        transcriptKept: false,
        turns: 0,
        ...fields,
        messages: [],
        observation: {
          tasks: [false, false, false],
          ownAI: null, // true / false / null (not recorded yet)
          ownAIMinute: "",
          switchedFor: "",
          note: "",
          usedForEach: "",
          insteadOrAlongside: "",
        },
      };
      save(s);
      sessions.set(s.id, s);
      tokens.set(s.token, s.id);
      return s;
    },
    update(s) {
      save(s);
      return s;
    },
    remove(id) {
      const s = sessions.get(id);
      if (s) tokens.delete(s.token);
      sessions.delete(id);
      const file = path.join(dir, `${id}.json`);
      fs.rmSync(file, { force: true });
      fs.rmSync(`${file}.tmp`, { force: true });
    },
  };
}

module.exports = { makeStore };
