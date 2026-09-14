// Two interchangeable stores. Both expose the same async API.
//   - pgStore(DATABASE_URL): Postgres (Railway "Add Database → PostgreSQL")
//   - fileStore(dir):        newline-delimited JSON files (mount a Railway volume at /data)
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const EVENTS = new Set(["page_view", "cta_click", "signup_submitted"]);
const INTENTS = new Set(["instead", "alongside", "probably_not"]);

function fileStore(dir) {
  fs.mkdirSync(dir, { recursive: true });
  const file = (name) => path.join(dir, `${name}.ndjson`);
  const read = (name) =>
    fs.existsSync(file(name))
      ? fs.readFileSync(file(name), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l))
      : [];
  const append = (name, row) => fs.appendFileSync(file(name), JSON.stringify(row) + "\n");

  return {
    kind: `files (${dir})`,
    async init() {},
    async addEvent(e) {
      append("events", { id: crypto.randomUUID(), created_at: new Date().toISOString(), ...e });
    },
    async addSignup(s) {
      if (read("signups").some((x) => x.email === s.email)) return { duplicate: true };
      append("signups", { id: crypto.randomUUID(), created_at: new Date().toISOString(), ...s });
      return { ok: true };
    },
    async signups() { return read("signups"); },
    async events() { return read("events"); },
  };
}

function pgStore(url) {
  const { Pool } = require("pg");
  const pool = new Pool({
    connectionString: url,
    ssl: process.env.PGSSL ? { rejectUnauthorized: false } : undefined,
  });

  return {
    kind: "postgres",
    async init() {
      await pool.query(`
        create table if not exists signups (
          id uuid primary key,
          email text unique not null,
          programme text,
          usage_intent text,
          source text,
          session_id text,
          created_at timestamptz not null default now()
        );
        create table if not exists events (
          id uuid primary key,
          session_id text,
          event text not null,
          meta jsonb,
          created_at timestamptz not null default now()
        );
      `);
    },
    async addEvent(e) {
      await pool.query(
        "insert into events (id, session_id, event, meta) values ($1, $2, $3, $4)",
        [crypto.randomUUID(), e.session_id, e.event, e.meta || {}]
      );
    },
    async addSignup(s) {
      try {
        await pool.query(
          "insert into signups (id, email, programme, usage_intent, source, session_id) values ($1, $2, $3, $4, $5, $6)",
          [crypto.randomUUID(), s.email, s.programme, s.usage_intent, s.source, s.session_id]
        );
        return { ok: true };
      } catch (err) {
        if (err.code === "23505") return { duplicate: true }; // unique_violation
        throw err;
      }
    },
    async signups() {
      return (await pool.query("select * from signups order by created_at")).rows;
    },
    async events() {
      return (await pool.query("select * from events order by created_at")).rows;
    },
  };
}

function makeStore() {
  if (process.env.DATABASE_URL) return pgStore(process.env.DATABASE_URL);
  // Railway volume mounted at /data is picked up automatically; otherwise ./data
  const dir = process.env.DATA_DIR || (fs.existsSync("/data") ? "/data" : path.join(__dirname, "data"));
  return fileStore(dir);
}

module.exports = { makeStore, EVENTS, INTENTS };
