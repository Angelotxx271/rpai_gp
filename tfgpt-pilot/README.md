# TFGPT pilot (Wizard of Oz)

The Wizard-of-Oz test from prototype-v0, rebuilt as a small web app under the TFGPT name. A student chats with what looks like TFGPT; a team member reads each message in the console and answers live from the IE TFG guidelines, following the wizard protocol. No AI runs behind the chat.

- **Student side:** `/s/<link>`: the chat from the prototype-v0 mockup (header, context chips, greeting, three suggested questions, pilot note)
- **Wizard side:** `/admin`: sessions, live transcript, answer templates, the protocol and task brief, the observation sheet, the 6-of-10 tally and a CSV export

Node 20 and Express, no build step, no database. Live updates use server-sent events, and both sides catch up on anything they missed after a dropped connection or a redeploy.

## Run locally

```
npm install
ADMIN_KEY=choose-a-key npm start      # http://localhost:3000/admin
```

Without `ADMIN_KEY` the server generates one at start-up and prints it in the log.

## Running a session (wizard protocol, prototype-v0 page 4)

The console shows the protocol (Before, During, After) and the task brief with a Copy button, both with TFGPT wording.

1. **Before:**
   - In `/admin`, press **New** and fill in the student's first name, degree, year, whether they've started, the assigned topic and an optional notes file name
   - Add the three answer templates (fit, structure and format, dates) with the guideline sections to cite. **Copy templates** reuses the last session's
   - Copy the student link
2. **During:**
   - The clock starts when the student opens the link, or when you press **Start clock now**. It turns red at the session length (20 minutes, `SESSION_MINUTES`)
   - A waiting timer counts from the oldest unanswered message and turns red after 60 seconds
   - Answer only from the guidelines, citing the section. **Not in the guidelines** inserts the "that one is for your supervisor" line
   - Never invent a date, write thesis text, or grade
3. **After:**
   - Do the reveal and ask the two questions, then fill the observation sheet: tasks done in TFGPT, opened own AI (and the minute), switched for, note, and the two answers. It saves as you type and is safe with two people on it
   - Tick **Rehearsal** for test sessions so they stay out of the tally
   - **Close session** deletes the transcript, first name, topic and templates, and removes the first name from the notes, unless the student agreed to keep the transcript. **Delete the kept transcript** removes it later. The observation row stays
4. **Results:**
   - The tally applies the rule committed in experiment-card.md, round by round: of the first 10 non-rehearsal sessions recorded in a round, at least 6 completed all three tasks in TFGPT without opening their own AI
   - **Start round N** begins a new round for a rerun; earlier rounds keep their tally
   - **CSV** downloads the observation sheet, with no names, and a tally line per round

## Earlier results (Round 1)

`seed/wizard-of-oz-round-1.json` holds the first Wizard-of-Oz test, copied from the Results table in `evidence-log/experiment-card.md`: 10 observation rows, no names, no transcripts.

- On its first start, the app imports them once as the closed sessions of Round 1. Its own tally reproduces the recorded result: 6 of 10, CONTINUE
- New sessions belong to Round 2
- Adding another JSON file in the same shape (`id`, `round`, `label`, `source`, `sessions`) imports it the same way

## Deploy on Railway

Deploy it as its own service in the existing `tfgpt` project, next to the landing page. From this folder:

```
railway link                 # pick the tfgpt project
railway add --service tfgpt-pilot
railway up --service tfgpt-pilot
```

Then, on the `tfgpt-pilot` service in the dashboard:
1. **Volumes:** add a volume mounted at `/data`. Sessions and the observation sheet live there; the console shows a red banner if there is no volume
2. **Variables:**
   - `ADMIN_KEY` (required): a random string of at least 16 characters. It is the console password, and the server refuses to start on Railway without it. Keep it out of the repo
   - `PUBLIC_URL` (optional): the public address, for example `https://tfgpt-pilot-production.up.railway.app`, used for the student links
   - `PILOT_BADGE` (optional): the label next to TFGPT in the header (default `Pilot`)
   - `SESSION_MINUTES` (optional): the session length (default 20)
   - `PURGE_AFTER_HOURS` (optional): open sessions with no activity for this long are closed and purged automatically (default 6)
3. **Networking:** generate a domain. Students get `https://<domain>/s/<link>`; the team uses `https://<domain>/admin`

## Privacy

- **Access:** students get an unguessable link. The console needs `ADMIN_KEY`; each login gets its own token, stored only as a hash and revoked on logout. HTTPS is enforced on Railway
- **What is kept:** only a first name, deleted when the session closes. Forgotten sessions are closed and purged automatically. The observation row is kept, including your own notes, so keep names and thesis text out of them
- **The CSV** holds no names, topics or transcripts
- **Browsers:** pages are not indexed or cached, and the links are never sent as referrers
