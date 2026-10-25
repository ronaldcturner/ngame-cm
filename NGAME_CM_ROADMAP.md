# NGAME-CM — Development Roadmap

**Kickoff** · 16 Sep 2026 · Decision state from NGAME-CM / appliance chats · WCARS 75 skipped

This file is the **storable planning copy** of the kickoff canvas. The live canvas beside chat is the working checklist. This document is what you reopen, print, or save as PDF.

Continuous monitoring engine on a dedicated always-on host. Detector stays. Operations change. Claim matches what is running.

| Job of NGAME-CM | What it does not claim | v1 cadence (honest CM) | Detector in v1 |
|-----------------|------------------------|------------------------|----------------|
| Notify | Not audit | 1 / day | Same CPI |

---

## Product sentence (do not exceed this)

NGAME-CM is automated ongoing snapshot surveillance. It notifies the FRP of meaningfully anomalous ledger-profile events. It does not see every QuickBooks save, does not ingest Audit Log, and does not perform a formal audit.

Do not wait for zero-caveat wiretap CM. Intuit does not offer an Audit Log event feed. The OS cannot see accounting events. Webhooks and CDC mean “this object changed,” not a forensic event log. The shippable ceiling is unattended, higher-cadence snapshots on a dedicated always-on host. The qualification is the product.

Zero-caveat wiretap is a nickname for a product that does not exist — and that this roadmap says we must not wait for, and must not claim.

Wiretap here is a metaphor, not a legal term. It means: NGAME is on the line with QuickBooks and hears every posting as it happens — who changed what, the instant it is saved, with nothing happening off-camera.

Zero-caveat means you can say that with no footnote. No “we sample once a day.” No “we do not see every save.” No “Audit Log stays in QuickBooks.” No “something could be posted and reversed between samples.”

Put together: a live, complete, no-gaps feed of every QuickBooks action, sold with no qualifications.

That is why the next sentences in the `.md` exist. Intuit does not give us an Audit Log firehose. The Mac or PC cannot see bookkeeping events. So the honest product is: unattended snapshots on a schedule, on a machine that stays on, plus notice when the ledger profile looks anomalous. The caveats are the product.

To a customer: “We do not wiretap QuickBooks. We take a scheduled picture of the books, compare it to the learned profile, and notify you if that picture looks meaningfully off. We do not see every save, and we do not replace the QuickBooks Audit Log.”

---

## Names — keep them distinct

| String | What it is | What it is not |
|--------|------------|----------------|
| Classic NGAME | Current product: FRP clicks once per business day; dashboard is the launcher | Not continuous monitoring |
| NGAME-CM | Capability: unattended snapshot surveillance + notify-on-anomaly | Not a formal audit engine; not every QBO save |
| NGAME-Appliance | The always-on host that makes CM operationally true | Not a new detector; not required before first software steps |
| Monitoring | Notify the FRP of meaningfully anomalous events | Not “auditing,” CA/CM literature shorthand, or Audit Log replacement |

---

## Says vs does not say

### Claim — honest CM sentence

Automated ongoing snapshot surveillance on a dedicated host. Scheduled pulls. No daily click. Alerts when risk is MEDIUM or HIGH, and when a scheduled run fails. Weeks of logs show it ran without the FRP.

Audit Log remains in the QuickBooks Online UI. NGAME still does not ingest it.

### Forbidden — do not say until architecture exists

Real-time. Every save. Wiretap. Continuous auditing. Nothing can be posted and erased between samples. NGAME reads who changed what. Replacement for QBO Audit Log.

A webhook, in this context, is a tap on the shoulder from Intuit: “a record changed — go look.” Later we may use that tap only to wake NGAME to take another snapshot. It is not a story of the change (who, what, old value), and it is not the QuickBooks Audit Log.

Forbidden to say, even after webhooks exist: that webhooks are a forensic event log; that they let NGAME see every save or who changed what; that webhooks are the v1 product or the proof that CM is “true.”

v1 is this: a dedicated machine takes the daily picture of the books by itself, at the scheduled hour, with no FRP click. That definition does not change if webhooks arrive later.

A gate, in this document, is a pass/fail checkpoint you must clear before you may claim a step (or v1) is done.

A soak, in this document, is a long proving run with no babysitting: the dedicated machine stays on (it does not sleep), the daily picture of the books is taken by itself at the scheduled hour, nobody clicks the FRP button, and a written log shows that this succeeded for fourteen scheduled days in a row. That log is the proof. A soak is not a coding task and not a short demo on a laptop that sleeps.

The checkpoint that v1 is done is that 14-day soak plus the honest product sentence — not the arrival of webhooks. Do not wait for webhooks to declare v1 complete, and do not tell a customer that webhooks are what made CM real.

---

## What stays vs what moves

Classic NGAME — human-triggered daily sampler:

`FRP click → QBO snapshot → CPI / z / SCPI → Result files → FRP reads screen`

NGAME-CM v1 — unattended daily sampler (same detector):

`Clock → Scheduler + lock → QBO snapshot → CPI / z / SCPI → Journal + files → Lamp + (later) alert`

A lock, in this document, is a one-at-a-time rule: only one picture of the books may be in progress. If the scheduler is already pulling QuickBooks, a dashboard click or a second command must be refused. Without the lock, two pulls can run together and scramble the same day’s results. It is not a door lock and not encryption.

A lamp, in this document, is the dashboard used as a status light, not as the start button. The FRP reads last run, last result, how many scheduled days succeeded in a row, and when the next run is due. They do not click to make the daily picture happen. Email (later) may also notify; the lamp is what you see if you open the screen.

Source: current pipeline (`ngame_dual_mode.py`, dashboard subprocess launchers) vs planned CM orchestration. Detector boxes are the same code path.

| Layer | Classic (today) | NGAME-CM v1 |
|-------|-----------------|-------------|
| Detector | QBO full pull → TTL → CPI / z / SCPI → warnings | Unchanged. Do not retune μ/σ or day semantics to ship a scheduler. |
| Who starts a run | FRP green button (`app-simple.py` subprocess) | Scheduler. Button becomes consultant override. |
| Host | Surveillance PC; dashboard auto-starts at login; PC may sleep | Dedicated always-on box; sleep disabled; services at boot |
| Locking | In-memory Flask (web framework written in Python) lock only — CLI + dashboard can double-run | Cross-process file lock covering UI and scheduler |
| Evidence it ran | FRP memory + matrix column / fraud JSON | Append-only run journal + last-run lamp |
| Notify | FRP must open the local dashboard | Dashboard as lamp, then email (SMS later) on MEDIUM/HIGH and on miss |
| Audit Log | FRP protocol in QBO UI (attribution unreliable — internal only) | Same. Not ingested. |

A cron, in this document, is the computer’s own built-in alarm clock (macOS and Linux). You give it a silent list of times and a command to run. Windows calls the same idea Task Scheduler. Cron only starts a program; it does not take the picture of the books, keep the lock, or write the journal. It is not the NGAME scheduler (`ngame_scheduler.py`).

The Implementation Guide already has an unattended hook (`ngame_dual_mode.py` + cron / Task Scheduler) and then forbids it on dashboard sites because it can double-run the pipeline. CM productizes that path and makes it the default. Do not turn on OS cron against Classic until the file lock exists. *(Lock shipped in first-steps 2, 17 Sep 2026.)*

---

## High-level roadmap

v1 is Tier A from the appliance effort estimate: always-on periodic watchdog, not event-driven ingestion. Rough productization remains about 5–10 person-months for a small team. Hardware is phase 3, not phase 1. First engineering is orchestration on a never-sleep host.

| Phase | Outcome | Gate to next | Not in this phase |
|-------|---------|--------------|-------------------|
| 0 · Claim freeze | This document / canvas. Monitoring not auditing. WCARS 75 skipped. | Language agreed; no code yet | Marketing copy beyond the product sentence |
| 1 · Unattended sampler | One scheduled successful snapshot per calendar day; lock; journal; dashboard lamp | 14 consecutive scheduled successes, no FRP click | Hardware SKU, email, LAN auth, hourly cadence |
| 2 · Notify | Push on MEDIUM/HIGH and on failed/missed run; FRP guide rewritten as exception response | Supervised alert test at a friendly site | SMS required; cloud portal |
| 3 · Appliance | Dedicated box, boot services (dashboard + Ollama + scheduler), sleep off, LAN URL + auth | Weeks of journal on that box, not a laptop | Hourly sampling; webhooks |
| 4 · Denser cadence | Phase II every N hours (6–12). Training still one column per calendar day. | API-quota and same-day semantics documented | Calling it real-time |
| 5 · Optional later | Webhook as wake-up to run a snapshot; property-mutation signal from v1.1 backlog | Only if v1 is in the field | Audit Log API; “who changed what”; zero-caveat CM |
| 6 · Field + WCARS | JFAR in print + appliance running + one precise sentence | Re-enter a later WCARS only then | WCARS 75 (6–7 Nov 2026) |

### Cadence rules that protect the published method

| Mode | When the scheduler fires | What it writes |
|------|--------------------------|----------------|
| Phase I training | Default: business days only, one hour you choose | At most one training-matrix column per calendar date. Quiet weekends stay out of μ/σ. |
| Phase II monitoring | Every calendar day including weekends (v1). Denser in phase 4. | Fraud JSON + journal. Never a new training column. |
| Already succeeded today | Scheduler no-ops | Journal note: skipped, already ran. Consultant override still allowed behind the lock. |
| Run failed | Do not count it as a training day | Journal FAIL. Later: push alert. FRP is not asked to click-retry blindly. |

Weekend sampling is the reason Classic hid a hole (FRP PC off). Put it in Phase II, not in the 30-day baseline, or you change the JFAR-evaluated training design.

---

## First steps — detailed instruction

Do not buy hardware yet. Do not add webhooks. Do not retune CPI. The first shippable increment is an unattended daily sampler with proof it ran. Use any never-sleep machine you already control (lab mini PC or a Mac/PC set to never sleep). That host is a stand-in for the appliance.

**Stop condition:** if a step would change extraction, Jaccard/CPI, z-score thresholds, or training-window length, it is out of scope for first steps. Park it on the v1.1 backlog.

### Step 0 — Freeze language (this kickoff) — done

Treat the product sentence at the top of this document as the claims guide. Future chats, IG copy, and FRP copy must not exceed it. Optional follow-on: a Cursor rule so a new chat cannot “helpfully” call Classic NGAME continuous monitoring.

### Step 1 — Config surface (no scheduler yet) — done (17 Sep 2026)

Add a small JSON file at repo root, for example `ngame_cm_config.json`, read only by new code. Keep secrets out of it.

| Field | v1 value | Why |
|-------|----------|-----|
| enabled | false until soak starts | Classic sites must not flip by accident |
| timezone | org local tz | “Today” is calendar date in that zone |
| run_hour_local | integer 0–23, consultant-chosen | After typical bookkeeper posting |
| phase1_weekdays_only | true | Protect 30-day μ/σ |
| phase2_every_calendar_day | true | Catch weekend/after-hours posts |
| dashboard_is_launcher | true until lamp ships | Cut over in step 5, not step 1 |

Shipped: `ngame_cm_config.json` + `ngame_cm_config.py`. Default timezone `America/Los_Angeles`, `run_hour_local` 18, `enabled` false.

### Step 2 — Cross-process run lock — done (17 Sep 2026)

Today `app-simple.py` holds an in-memory `threading.Lock`. That does not serialize a cron job against the dashboard. Implement `ngame_run_lock.py` using a lock file under `logs/ngame_pipeline.lock` (POSIX `fcntl` / Windows `msvcrt` or an equivalent exclusive open). Acquire in:

| Caller | File today | Change |
|--------|------------|--------|
| Dashboard training / fraud / dual-mode subprocess | `ngame_ui/app-simple.py` (around the operation lock + Popen) | Acquire file lock before Popen; release when the child exits |
| CLI dual mode | `ngame_dual_mode.py` / `run_training_flow.py` / `run_fraud_analysis.py` | Same lock. If busy, exit 2 with a clear message; do not start a second pull |
| New scheduler | does not exist yet | Acquire, run, release. Never bypass. |

Prove this on one machine: start a dashboard run, then invoke the CLI. CLI must refuse. Reverse the order. Dashboard must show “already running.”

Shipped: `ngame_run_lock.py`, `ngame_pipeline_guard.py`, wired into dashboard and CLI launchers.

### Step 3 — Run journal — done (17 Sep 2026)

Two files, both gitignored if they contain site paths; schema is part of the product:

| File | Shape | Who reads it |
|------|-------|--------------|
| `logs/ngame_runs.jsonl` | One JSON object per attempt: utc_ts, local_date, phase, trigger (schedule\|dashboard\|cli), ok, exit_code, skipped_reason, matrix_days, risk | Consultant, soak evidence, later WCARS “it ran without you” |
| `logs/ngame_last_run.json` | Latest record plus next_scheduled_local | Dashboard lamp; health check |

Write the journal from a single helper, `ngame_run_journal.py`, called after every attempt including skips and lock-busy. A skipped “already ran today” is success for uptime evidence, not a training day. A lock-busy from an overlapping dashboard click is not a missed schedule.

Shipped: `ngame_run_journal.py`. `logs/` is gitignored.

### Step 4 — Scheduler wrapping dual mode — done (17 Sep 2026)

New entry point `ngame_scheduler.py`. It is a long-running process or a once-per-minute poller started at login/boot — not an undocumented crontab on the FRP machine. Behavior:

| Check | Action |
|-------|--------|
| enabled is false | Sleep; do nothing |
| Wrong weekday in Phase I | No-op; optional journal skip |
| last_run.local_date is today and ok | Skip; journal skipped_reason=already_ran |
| Otherwise | Lock → ngame_dual_mode (or the existing training/fraud launcher) → journal |
| OAuth invalid_grant | FAIL journal reconnect_required. Do not open a browser unattended. |
| Phase II and Ollama down | FAIL journal ollama_unavailable. Do not pretend the fraud check ran. |

Reuse `NGameDualMode.determine_mode()`. Do not invent a second phase switch. Tee stdout to `logs/ngame_daily.log` the way the IG cron example already sketches, so a bad TTL build is still reconstructable.

macOS LaunchAgent / Windows service for the scheduler can wait until the soak host is chosen. For the first lab prove, a Terminal-kept process or a developer LaunchAgent on your machine is enough. Product installers come in phase 3.

Shipped: `ngame_scheduler.py`. `enabled` stays false, so a running scheduler **idles** (no QuickBooks pull). Lab: `python3 ngame_scheduler.py` (leave the Terminal open) or `python3 ngame_scheduler.py --once`. Unattended runs set `NGAME_UNATTENDED=1` so a dead refresh token is journaled as `reconnect_required` instead of opening a browser. Dual-mode stdout is appended to `logs/ngame_daily.log` when a pull actually happens.

### Step 5 — Dashboard becomes a lamp — done (19 Sep 2026)

After the journal exists, the FRP view should answer four questions without a click: last run time, last result (LOW/MEDIUM/HIGH or FAIL), consecutive successful scheduled days, next scheduled time. Keep the green button as a labeled **consultant override** until Classic sites are migrated; hide it from FRP mode once `dashboard_is_launcher` is false.

The dashboard already polls `/api/consolidated-dashboard`. Add last-run fields there from `ngame_last_run.json`. Do not require the FRP to watch live TTL output on a scheduled run. Live output stays for consultant diagnosis.

Shipped: `cm_lamp` on `/api/consolidated-dashboard` (last run, last result, scheduled-success streak, next scheduled). FRP operations panel shows those four fields. The green button is labeled **Consultant override**. It stays visible while `dashboard_is_launcher` is true; set that flag false to hide it in FRP mode. `enabled` is still false — the lamp will show dashes until a journal exists.

### Step 6 — Fourteen-day soak (software gate) — tooling ready (19 Sep 2026); gate pending

Pick a never-sleep host with a working Track A or Track B company. Enable the scheduler. Do not click the FRP button. Pass only if:

| Evidence | Pass rule |
|----------|-----------|
| Journal | 14 consecutive scheduled successes on the intended calendar rule |
| Matrix / fraud JSON | Phase I: at most one new column per date. Phase II: fraud file updates, matrix day count unchanged |
| Lock test | Manual overlap still refused |
| Failure injection | Kill Ollama or pull the network once; journal records FAIL; next day recovers without a click |
| Human | You can show a 14-day log that you did not babysit |

This step cannot be completed in a coding session. The 14-day clock is calendar evidence on a never-sleep host.

Shipped: `ngame_soak_check.py`. It reads `logs/ngame_runs.jsonl` and scores the five rules above. Exit 0 only when all five are evidenced. It does **not** start the soak and does **not** flip `enabled`. Lab run today: checker reports **NOT PASSED** (no journal yet; `enabled` is still false).

How to run the soak, when a host is chosen:

1. Never-sleep machine, working Track A or Track B company.
2. Set `"enabled": true` in `ngame_cm_config.json`.
3. `python3 ngame_scheduler.py` and leave it running.
4. Do not click the FRP button. The dashboard is a lamp.
5. Once during the window: start a dashboard or CLI run while the scheduler holds the lock — it must refuse (`lock_busy`).
6. Once during the window: stop Ollama or unplug the network; the journal must record FAIL; the next scheduled day must recover without a click.
7. After 14 consecutive scheduled successes: `python3 ngame_soak_check.py`. Mark this step completed only when that command prints `gate: PASSED`.

### Step 7 — Only after soak — pending

Then, and not as a bundle with steps 2–5: (a) email on MEDIUM/HIGH and FAIL, (b) hardware SKU + UPS + sleep policy, (c) bind already is `0.0.0.0:5001` so add dashboard auth before treating LAN as a feature, (d) FRP_OPERATIONS_GUIDE rewritten from “click daily” to “respond to notices; Audit Log still in QBO,” (e) IG split Classic vs Appliance. Hourly cadence is still later.

### First-steps checklist

| Step | Item | Status |
|------|------|--------|
| 0 | Freeze claim language (this document) | completed |
| 1 | `ngame_cm_config.json` (enabled=false) | completed |
| 2 | Cross-process file lock on dashboard + CLI | completed |
| 3 | Run journal + last-run JSON | completed |
| 4 | `ngame_scheduler.py` wrapping dual_mode | completed |
| 5 | Dashboard last-run lamp; button → override | completed |
| 6 | 14-day unattended soak | tooling ready — gate pending |
| 7 | Alerts, appliance hardware, LAN auth, docs split | pending |

---

## Out of scope until v1 is running

### Do not start

- QBO Audit Log ingestion (no API; stay hidden from Intuit).
- Webhook/CDC as the CM architecture.
- Changing z thresholds or the 30-day window to “make it more continuous.”
- WCARS 75 (6–7 November 2026).
- Claim-language edits to JFAR, IG, or FRP guide ahead of a running appliance — except internal planning docs.

### Parked on other backlogs

- wCPI and property mutations (v1.1 detection, not CM ops).
- Premium lookback L dropdown.
- Cloud license portal.
- User-attribution in NGAME output (C1) — still Audit Log in QBO.

---

## WCARS re-entry gate

Skip the 75th symposium. Re-enter a later WCARS only after all three:

| # | Condition | Why |
|---|-----------|-----|
| 1 | JFAR article is in print | Cite the published method; talk about what came after. No exclusivity hedge. |
| 2 | NGAME-Appliance in the field: always-on, scheduled, no daily click, alerts, weeks of logs | “Not to be released later.” The qualification is the running product. |
| 3 | One precise sentence: automated ongoing snapshot surveillance; not every QBO save; Audit Log still in the QBO UI | Do not make the gate “true CM with nothing left to explain.” |

---

Related: sequence architecture canvas · nonprofit deployment canvas · v1.1 backlog · FRP_OPERATIONS_GUIDE.md (Classic daily click) · README.md optional CLI/cron (forbidden alongside dashboard until lock)

**Print / PDF:** open `NGAME_CM_ROADMAP.html` in a browser → File → Print → Save as PDF.
