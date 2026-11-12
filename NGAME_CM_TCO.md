# NGAME-CM — First TCO estimate

**Order of magnitude** · 17 Sep 2026 · Not a quote · Not a license price · USD

Site cost to own and run, versus the tester invitation that said $0 and very low effort. Hardware BOM from the appliance estimate ($400–800 class). Classic first-site labor from three long on-site visits.

| What the tester heading claimed | Classic first site, actual labor | CM new cash: dedicated host + UPS | First CM site, consultant time |
|--------------------------------|----------------------------------|-----------------------------------|--------------------------------|
| $0 | 3 visits | $500–1,000 | 5–8 days |

Classic was never zero-cost. The invitation waived hardware and license for testers. You paid in person: three very long on-site visits. CM adds a real hardware bill and, until the installer exists, does not make the first install simpler than Classic.

Print / PDF: open `NGAME_CM_TCO.html` → File → Print → Save as PDF.

---

## Keep two books

| Book | Who pays | What belongs here | What does not |
|------|----------|-------------------|---------------|
| Site TCO | The organization (or you, if still subsidizing testers) | Box, UPS, power, install days, yearly keep-alive, FRP time | The 5–10 person-months to productize CM |
| Vendor / R&D | Audithentic | Scheduler, lamp, soak tooling, later alerts/auth/docs (roadmap 4–7) | A per-site invoice line |

Mixing them makes CM look like a $50k+ product when the customer is really buying a box plus install labor.

---

## Classic advertised vs Classic actual vs CM

| Line | Tester invitation (Classic) | First Classic site (what happened) | NGAME-CM v1 (first estimate) |
|------|-----------------------------|------------------------------------|------------------------------|
| Hardware | Repurpose an office PC; no purchase | Existing surveillance PC (sleep/off still allowed) | Dedicated always-on mini PC + UPS. Do not use the FRP laptop. |
| Cash to the org | $0 | $0 hardware; labor unbilled | $500–1,000 capex + ~$40–90/year electricity |
| Install complexity | Very low effort | Not easy: OAuth/Track B, three long visits | Same OAuth hardness plus never-sleep, scheduler, 14-day soak. First sites: similar or harder. |
| FRP daily load | One dashboard click per business day | Click + live output + Audit Log in QBO | No daily click after soak. Exception response to notices. Audit Log still in QBO. |
| Who must stay on | PC on when FRP clicks | If the PC slept, NGAME saw nothing (weekend hole) | The box, 24/7. That is the new operating cost. |

### Site cash — year 1 (one surveillance host, no license fee)

| Item | Low | High | Notes |
|------|-----|------|-------|
| Mini PC (16 GB RAM, enough disk for Ollama) | $400 | $800 | Windows mini PC class at the low end; Mac mini toward the high end. Prior appliance BOM. |
| UPS | $50 | $150 | Roadmap Step 7. Cheap insurance against dirty power. |
| Display / keyboard | $0 | $150 | $0 if headless + occasional laptop; budget if the FRP uses that box in person. |
| Electricity (always-on, ~25–40 W) | $40/yr | $90/yr | Rough U.S. small-office rates. Not a generator study. |
| Internet / QBO / Ollama | $0 extra | $0 extra | Already required for Classic. Local model, no cloud LLM fee. |
| Software license | TBD | TBD | Testers were $0. Do not reuse “zero cost” once hardware is required. |

Hardware subtotal to stand up the host: about **$500–1,000 once**, then tens of dollars a year in power. That is the part Classic could honestly call optional. CM cannot.

### Labor — the larger TCO, still

| Who | Classic first site | CM first site (now) | CM after installer + soak playbook |
|-----|--------------------|---------------------|------------------------------------|
| Consultant on-site / on-call | 3 very long visits (treat as ~4–6 person-days) | Same OAuth + host policy + scheduler prove + start of soak: ~5–8 person-days | Target 1–2 days on site + remote. Not true until Step 7 docs exist. |
| Site IT | Little: a PC that can sleep | Owns power, Ethernet, no-sleep, physical placement, who gets “run failed” | Same, but scripted |
| FRP, year 1 | Daily click, ~2–10 min, plus Audit Log protocol | 14-day hands-off soak, then glance at lamp / mail; Audit Log still required | Exception-driven. Minutes fall; responsibility does not disappear. |

If those consultant days were billed (they were not, for testers), Classic first-site labor at $150–250/hour is already several thousand dollars. CM does not erase that. It adds the box on top, and the first CM installs will not be shorter than Classic until the product is boring to install.

---

## Is the CM install more complicated?

Yes, for the implementer. No, eventually, for the FRP’s daily ritual.

**Harder than Classic (install / IT)**

- Dedicated host that must not sleep.
- NGAME scheduler kept alive at boot — not a silent OS task that calls dual_mode.
- File lock + journal as proof it ran.
- Fourteen-day unattended soak before you claim CM.
- Later: dashboard auth on the LAN, UPS, alerts, reconnect-without-a-browser.
- OAuth is still the Classic pain. CM does not delete Track B.

**Easier than Classic (steady state)**

- No green-button religion every business day.
- Weekend and after-hours samples without the FRP PC being awake.
- FRP work becomes: respond when risk is MEDIUM/HIGH or a run failed.
- Bookkeeper PC still has no NGAME software.

---

## Year-1 site TCO — rolled up

| Scenario | Cash outlay | Consultant labor (unbilled or billed) | Honest one-liner |
|----------|-------------|------------------------------|------------------|
| Classic as advertised | $0 | “Very low effort” | Do not reuse this sentence for CM. |
| Classic as lived | ~$0 hardware | 3 long visits | Zero cash, high founder labor. |
| CM, tester still subsidized | $500–1,000 (you or they buy the box) | 5–8 days first site | Invitation can waive license, not physics: something must stay on. |
| CM, org pays its way (no license yet) | $550–1,100 year 1 including power | Plus install days if you invoice | Small-capex appliance + professional services. |

---

## Vendor TCO (do not put on the customer one-pager)

Productizing Tier A (always-on periodic watchdog) remains about **5–10 person-months** for a small team. That is how CM becomes installable without three heroic visits. It is not a per-site hardware number.

Related: NGAME-CM roadmap (Step 7 hardware SKU) · nonprofit partnership proposal ($0 / repurpose PC) · appliance effort estimate (BOM $400–800, 5–10 person-months). Refresh this estimate after the first CM soak host is purchased.
