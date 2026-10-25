# NGAME-CM — Directors and agents

**Companion to** [NGAME_CM_ROADMAP.md](NGAME_CM_ROADMAP.md) · 22 Sep 2026 · Same detector as Classic

This is the CM roster in the same form as the Classic agent table. Roles are **not** greatly expanded. The picture of the books, the CPI / z / SCPI math, and the FRP write-up are the same agents. What CM added sits **outside** that roster: who starts the day, the lock, the written log, and the lamp.

Product sentence (do not exceed this): NGAME-CM is automated ongoing snapshot surveillance. It notifies the FRP of meaningfully anomalous ledger-profile events. It does not see every QuickBooks save, does not ingest Audit Log, and does not perform a formal audit.

---

## The short answer

| Question | Answer |
|----------|--------|
| Are there new detector agents in CM? | No. |
| Did existing agents gain new fraud logic? | No. Do not retune μ/σ or the 30-day window to ship a scheduler. |
| What changed? | Who starts a run (scheduler, not the FRP click), plus lock, journal, and lamp. Those are orchestration. They are not directors or agents. |
| Who sequences the daily agents in production? | The same two flow managers as Classic. |

A **director** or **flow manager**, in this document, is a sequencer: it calls the specialized agents in order. It does not compute CPI and it does not talk to the FRP.

An **agent**, in this document, is one owned step in that sequence (pull the books, score CPI, write a matrix column, warn management, and so on).

---

## Who starts the day (CM change)

| Who | What it starts | Then who sequences the agents |
|-----|----------------|-------------------------------|
| NGAME scheduler (`ngame_scheduler.py`) | Today: `ngame_dual_mode.py` | Legacy directors inside dual-mode (see the wiring note below) |
| Dashboard **Consultant override** | `run_training_flow.py` or `run_fraud_analysis.py` | Training Flow Manager or Fraud Analysis Flow Manager |
| CLI, same scripts as the dashboard | Same as the override | Same flow managers |

The lock refuses a second start if one picture of the books is already in progress. The journal records who started it (`schedule`, `dashboard`, or `cli`).

---

## Directors and flow managers

| Name | File | Classic role | Role in CM |
|------|------|--------------|------------|
| Training Flow Manager | `ngame_training_flow_manager.py` | Sequences Phase I (training) agents for one calendar day | **Same sequence.** Started by the dashboard override or `run_training_flow.py`, not by the FRP as a daily duty. |
| Fraud Analysis Flow Manager | `ngame_fraud_analysis_flow_manager.py` | Sequences Phase II (monitoring) agents for one calendar day | **Same sequence.** Same launchers as Classic; the scheduler is supposed to be the unattended starter. |
| Enhanced Phase 1 Director | `phase1_director_agent_enhanced.py` | Older pull-and-TTL wrapper | Still used when `ngame_dual_mode.py` runs (the scheduler’s current child). Not the dashboard’s daily path. |
| Phase 2 Director | `phase2_director_agent.py` | Older CPI/report wrapper | Same: dual-mode only. Not the dashboard’s daily path. |
| Dual Mode | `ngame_dual_mode.py` | Chooses training vs fraud from matrix day count (`determine_mode()`) | **Same switch.** On a fraud night the scheduler’s child also runs the z-score ranking, loads the misappropriation taxonomy, calls Ollama, and writes the management warnings the dashboard colors. It does not pull QuickBooks a second time. |

---

## Phase I agents — training (same as Classic)

| Agent | File | One-line function | Role in CM |
|-------|------|-------------------|------------|
| Data Extraction Agent | `ngame_data_extraction_agent.py` | Read-only pull of the day’s ledger; writes `Yesterday.ttl` / `Today.ttl` | **Same.** Unattended OAuth (no browser) is an orchestration rule around this pull, not a new agent. |
| CPI Analysis Agent | `ngame_cpi_analysis_agent.py` | Yesterday vs today → today’s CPI array (one score per transaction type) | **Same.** |
| Matrix Management Agent | `ngame_matrix_management_agent.py` | Appends today’s CPI as the next training-matrix column; refreshes μ and σ | **Same.** Still at most one new column per calendar date. |

---

## Phase II agents — monitoring (same as Classic)

| Agent | File | One-line function | Role in CM |
|-------|------|-------------------|------------|
| Data Extraction Agent | `ngame_data_extraction_agent.py` | Same live pull and TTL rotation as Phase I | **Same.** |
| CPI Analysis Agent | `ngame_cpi_analysis_agent.py` | Today’s CPI (and dollar-weighted wCPI) profile | **Same.** |
| Credit Card Watch Agent | `ngame_credit_card_watch_agent.py` | Rule scan of credit-card charges in `Today.ttl` (not the training matrix) | **Same.** |
| Churn Comparison Agent | `ngame_churn_comparison_agent.py` | z-scores vs trained μ / σ; HIGH / MEDIUM / LOW | **Same.** |
| Sequence CPI Agent | `ngame_sequence_cpi_agent.py` | SCPI over the last *L* days — slow-burn signal | **Same.** |
| Anomaly Identification Agent | `ngame_anomaly_identification_agent.py` | Picks the top ranked transaction-type dimensions to escalate | **Same.** |
| Account Mapping Agent | `ngame_account_mapping_agent.py` | Maps those dimensions to accounts and records in `Today.ttl` | **Same.** |
| LLM Analysis Agent | `ngame_llm_analysis_agent.py` | Narrative vs asset-misappropriation taxonomy (needs Ollama) | **Same.** Scheduler journals `ollama_unavailable` if this cannot run; it does not invent a fake fraud check. |
| Management Warning Agent | `ngame_management_warning_agent.py` | FRP write-up (`management_dashboard.json`, optional email) | **Same write-up.** CM lamp reads last-run facts from the journal; email-on-MEDIUM/HIGH/FAIL is Step 7, after soak. |

---

## Validation agent (same as Classic; not daily CM)

| Agent | File | One-line function | Role in CM |
|-------|------|-------------------|------------|
| Anomaly Injection Agent | `ngame_anomaly_injection_agent.py` | Arms a one-shot synthetic spike in `Today.ttl` after the live pull — does not write to QuickBooks | **Same.** Still a consultant/CLI test, not the soak and not the FRP daily path. |

---

## Not directors or agents (CM orchestration)

These are new. They do not compute CPI. Do not call them agents when talking to a customer.

| Name | File | Job |
|------|------|-----|
| CM config | `ngame_cm_config.json` / `ngame_cm_config.py` | On/off, timezone, run hour, weekday rule. No secrets. |
| Lock | `ngame_run_lock.py` | One picture of the books at a time. |
| Pipeline guard | `ngame_pipeline_guard.py` | CLI refuses if the lock is held. |
| Journal / lamp numbers | `ngame_run_journal.py` | Written log of each attempt; four lamp fields. |
| Scheduler | `ngame_scheduler.py` | Clock. May start one run at the scheduled hour. Not cron. |
| Soak checker | `ngame_soak_check.py` | Scores the journal against the 14-day soak. Does not start a run. |
| Dashboard lamp | `ngame_ui/app-simple.py` + dashboard template | Status light. Consultant override still starts a flow-manager run. |

---

## Wiring note — two stacks

The roadmap says the detector stays and the scheduler wraps dual-mode. The dashboard’s Classic path is the **flow managers** and the agents in the tables above.

Today those are **not the same child process**:

| Starter | Child | Agent stack |
|---------|-------|-------------|
| Scheduler | `ngame_dual_mode.py` | Enhanced Phase 1 Director + Phase 2 Director. On a fraud night, the tail continues through z-score ranking, taxonomy, Ollama, and management warnings. Training nights still only add the next column. |
| Dashboard override / `run_training_flow.py` / `run_fraud_analysis.py` | Flow managers | Full Phase I or Phase II agent tables above |

Until the scheduler starts the same scripts the dashboard uses, a consultant fraud flow and the nightly clock both cover the same FRP-facing reports: z-score anomalies, the taxonomy verdict, credit-card watch, and the multi-day pattern. The clock does not pull QuickBooks a second time to produce them.

---

## What to tell a customer

“The same specialists still take the picture of the books and score it. Continuous monitoring did not add a new fraud brain. What we added is a clock, a one-at-a-time rule, a written log, and a status light, so the FRP does not have to click every day.”
