# TFGPT landing page (fake-door test)

One static page (`public/index.html`) plus a tiny Express API that records the funnel
(page views → "I'd use this" clicks → signups). No build step, no framework.

- `GET /` — the page
- `POST /api/event` — funnel events (`page_view`, `cta_click`, `signup_submitted`)
- `POST /api/signup` — email (+ optional programme and "instead / alongside / probably not")
- `GET /stats?key=STATS_KEY` — counts only (no emails)
- `GET /export.csv?key=STATS_KEY` — the signup list as CSV

Storage: Postgres if `DATABASE_URL` is set, otherwise newline-delimited JSON files in `DATA_DIR`
(defaults to `/data` when that folder exists, e.g. a Railway volume, else `./data`).

## Run locally

```
npm install
npm start            # http://localhost:3000
```
Stats: http://localhost:3000/stats?key=tfg2026

## Deploy on Railway (dashboard, ~5 minutes)

1. Push this folder to a GitHub repo (private is fine).
2. railway.app → **New Project → Deploy from GitHub repo** → pick the repo. Railway detects Node and runs `npm start`.
3. Click the service → **Settings → Volumes → Add Volume**, mount path `/data`.
   This is where signups are saved. Without it a redeploy wipes them.
4. **Variables** → add `STATS_KEY` = any random string (this replaces the default `tfg2026`).
5. **Settings → Networking → Generate Domain**. That URL is what goes in the QR code.
6. Numbers: `https://<your-domain>/stats?key=<STATS_KEY>` · emails: `/export.csv?key=<STATS_KEY>`

Prefer Postgres instead of the volume? **+ New → Database → PostgreSQL**, then on the web service add the
variable `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`. Tables are created automatically on boot.

## Deploy with Claude Code instead

Prerequisites on your machine (one-time, each opens a browser login):
```
gh auth login                       # GitHub CLI
npm i -g @railway/cli && railway login
```
Then, inside this folder, run `claude` and paste:

```
This folder is a finished Node/Express landing page. Read README.md first. Do not change any copy, layout or design.
1. Run `npm install` and `npm start`, hit http://localhost:3000/healthz and POST a test signup to /api/signup to confirm it works, then stop the server and delete ./data.
2. git init, commit everything respecting .gitignore, and create a private GitHub repo called tfgpt-landing from it (`gh repo create tfgpt-landing --private --source=. --push`).
3. Deploy with the Railway CLI (check `railway --help` for exact flags): create a new project called tfgpt from this folder, deploy it, add a volume mounted at /data, set the variable STATS_KEY to a random 12-character string, redeploy, and generate a public domain.
4. Open the public URL, confirm the page loads and that /stats?key=<STATS_KEY> returns the funnel table.
5. Report back: the public URL, the STATS_KEY, and the repo URL.
```

## Editing

- All visible text and styling: `public/index.html`. If you want a contact address in the footer, add it there.
- Fonts are self-hosted in `public/fonts` (Newsreader and Instrument Sans, SIL Open Font License).
- Keep the drift diagram's `pathLength="1"` on the red path; the draw-on animation depends on it.
