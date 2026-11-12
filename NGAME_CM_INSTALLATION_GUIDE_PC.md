# NGAME-CM — Installation Guide (Windows PC only)

**Hand this file to the site IT person who installs NGAME-CM.** Use it on the dedicated Windows mini PC. Do not use the Mac guide on that machine.

**Audience:** The installer. Windows 10 or Windows 11. The computer stays on. Use **PowerShell** (not Command Prompt, not Git Bash).

**Not for:** The Financially Responsible Person (FRP), and not for the bookkeeper. They do not install this, they do not open PowerShell, and they do not click once per business day. The bookkeeper keeps using QuickBooks Online in a browser. No NGAME software goes on that PC.

**Not in this file:** macOS, Wave, QuickBooks sandbox / Development keys, or any other NGAME document. This is the **customer go-live** path: live QuickBooks Online, Production keys, one ngrok Connect click, then an unattended daily picture.

**20 Oct 2026.** This roll-up is the procedure for the next Windows host. It does not narrate the first mini. A new install clones `https://github.com/ronaldcturner/ngame-cm.git` once, into `Documents\ngame-cm`. Do not copy program files from another computer, and do not clone Classic (`ngame.git`) onto this PC.

The steps below assume that clone already contains the scheduler, the lamp dashboard (four lines under **NGAME Operations**), and `ngame_notify.py`. Those pieces are in the working copy. They are not all on GitHub `main` yet. Do not point a test site at `git clone` until that working copy has been published. A machine that is already running must not `git pull`.

---

## How to use this file (read this once)

1. Keep **this** file open (or print the HTML). Start at **Step 1**. Do every step in order. Do not skip.
2. After each step: if it worked, go to the next numbered step. If it failed, use the **If this fails** table **under that same step**, then continue.
3. Do **not** open the Mac guide, the combined installation guide, `IMPLEMENTATION_GUIDE.md`, or `NGROK_COOKBOOK.md` while you are installing. ngrok is **in this file**.
4. There are no “go do section X then return here” links. There is no Track A / Track B choice. There is no Mac column.
5. Installing on a Mac is the other file. Reading this file on a Mac while the install happens on the Windows PC is fine.

**Where you read this guide**

Open the HTML on the Windows PC and switch between the browser and PowerShell, or read it on another computer. Either way is fine. This guide does not require a second machine, and it does not require you to type every line by hand.

When a step shows a block of commands, paste the whole block into PowerShell, or enter the lines one by one. The commands run on the mini PC. A dollar sign in a command is required. There are no parentheses around `$env:USERPROFILE`.

**The order you will follow**

1. PowerShell → 2. Sleep off → 3. Python → 4. Git → 5. Clone → 6. Virtual environment → 7–8. Production keys → 9–12. ngrok → 13–17. One Connect click → 18. Sandbox leftovers → 19–21. Ollama → 22. CM config (still off) → 23–25. Dashboard lamp → 26–28. Scheduler (idles) → 29. Lock → 30. One consultant picture → 31. Arm the 14-day clock → 32. What you say to the FRP → 33. Leave-site checklist. After `gate: PASSED`, the FRP may turn on Email, Text, or both.

You will **not** finish the 14 days during the visit. You leave the clock running. You do not tell the site CM is done until a later run of `python ngame_soak_check.py` prints `gate: PASSED`.

---

## What you are installing

NGAME-CM is automated ongoing snapshot surveillance. It notifies the FRP of meaningfully anomalous ledger-profile events. It does not see every QuickBooks save, does not ingest Audit Log, and does not perform a formal audit.

Each night is recorded on this PC: `logs\ngame_last_run.json` and `NGAME_Fraud_Analysis.json`. The dashboard at `http://localhost:5001/dashboard` is the lamp. Under **NGAME Operations** it shows **Last run**, **Last result**, **Scheduled successes**, and **Next scheduled**. Nobody clicks to take the picture.

With no training workbook in the folder, the same 6:00 PM clock adds one column each business day until 30 columns are on file. Saturday and Sunday during that build do not add a column. **Last result** in that period is OK or FAIL, not an anomaly grade. After the 30th business-day column, the clock stops adding columns and takes an anomaly picture every calendar day, weekends included.

A finished workbook may be placed in `Documents\ngame-cm` as `NGAME_Training_Matrix.xlsx` before the clock is armed, and only when this site is not building a new profile. That file is already trained. It is not this company’s new 30 days. The ordinary test site does not do this. It lets the clock build the matrix.

Email and Text stay off through the install and through the 14 nights. After `gate: PASSED`, the FRP may turn one or both on. A message goes out only for MEDIUM, HIGH, or a failed night. A quiet night sends nothing. Do not tell the site that mail is already sending.

Say this to a customer, and stop:

> We do not wiretap QuickBooks. We take a scheduled picture of the books, compare it to the learned profile, and notify you if that picture looks meaningfully off. We do not see every save, and we do not replace the QuickBooks Audit Log.

NGAME-CM runs on **one machine**: this mini PC, and it stays on. The bookkeeper’s PC gets **no** NGAME software.

```
Bookkeeper's computer
  └─ browser → QuickBooks Online (cloud)
                      ↑
This Windows mini PC (does not sleep)
  └─ Clock → scheduler + lock → Intuit API (read-only)
         → same CPI path as Classic → journal + files on this PC
```

| Component | Where |
|-----------|--------|
| This clone, Python, Ollama | This PC. Folder `Documents\ngame-cm` |
| ngrok | This PC, **only** for the one Connect click. Then you stop it |
| `quickbooks_config.json` | This PC. Secrets. Not in `ngame_cm_config.json` |
| Dashboard page | `http://localhost:5001/dashboard` on **this** PC. Four lamp lines. No daily click. |
| Bookkeeper / other PCs | **No NGAME install** |

The process listens on `0.0.0.0:5001`. There is no login yet. Do not treat a LAN address as a feature. Do not port-forward it. The bookmark is localhost on this PC.

Do not install by editing a Classic `Documents\ngame` folder or an NGAME-POC checkout. Clone **ngame-cm** into its own folder.

Do not change extraction, CPI, z-score thresholds, or the 30-day window. Aligning the Ollama model name in Step 20 is allowed. Retuning the detector is not.

| Task | You | FRP |
|------|-----|-----|
| Install, OAuth, sleep off, scheduler | Yes | No |
| Click to take the daily picture | **No** | **No** |
| Open the dashboard page | Optional | Only if they want to look. Not a daily click. |
| Audit Log | Advise | Still in the QuickBooks browser |
| Email / Text | After `gate: PASSED` only. Switches start off. | They type an address or a mobile number and click Save. They do not edit Python. |

**Production values you need before Step 8**

Audithentic sends two strings out of band (not GitHub, not the example JSON):

1. **Production Client ID**
2. **Production Client Secret**

The callback URL does not exist until Step 13 on this PC. You register it during the visit (Step 15), after ngrok shows Forwarding.

---

## What you need in hand (do not start Step 1 without these)

- [ ] This is the **Windows mini PC** (Windows 10 or 11), not the bookkeeper PC, not a Mac, not the FRP’s laptop
- [ ] It can stay plugged in and signed in
- [ ] Stable internet
- [ ] You will use **Windows PowerShell**
- [ ] Customer approved **read-only** API access to the **live** QBO company
- [ ] **Production Client ID and Production Client Secret** — not required at Step 1. **Required before Step 16.** Step 16 stops you if `quickbooks_config.json` still contains `YOUR_INTUIT_CLIENT_ID` or `YOUR_INTUIT_CLIENT_SECRET`. Do not invent keys.
- [ ] An **Audithentic owner** can add a Redirect URI during the visit
- [ ] A **Company Admin** or **Master Admin** of the **live** company will click Connect
- [ ] You have or will create a **free ngrok account** (that is not an Intuit account)

If any box is empty except the Production Client ID and Secret, stop and get it. Then start Step 1. Those two strings can wait through Step 15. They must be in `quickbooks_config.json` before the `python` command in Step 16.

---

## Step 1 — Open PowerShell the right way

1. Click Start, type `PowerShell`, open **Windows PowerShell**.
2. Do **not** open Command Prompt (`cmd.exe`).
3. Leave this window open. Every command in this guide goes in PowerShell unless a step says to open a second window.

**If this fails**

| You see | Do this |
|---------|---------|
| Only Command Prompt | Close it. Start → `PowerShell`. The commands below will not work in `cmd`. |

**Done when:** The prompt looks like `PS C:\Users\…>`.

---

## Step 2 — This PC must not sleep

The daily picture happens only if this machine is awake at the hour you choose in Step 22. Screen off is fine. Sleep is not.

1. Plug the mini PC into mains power. Leave it plugged in.
2. Open **Settings**. Click **System**. Click **Power**. On a PC that has a battery this item may instead say **Power & battery**. On Windows 10 it may say **Power & sleep**.
3. Open **Screen, sleep & hibernate timeouts**.
4. Set **Make my device sleep after** to **Never**. If there is only one sleep choice, set that to **Never**. If a hibernate timeout is listed, set that to **Never** too.
5. **When plugged in, turn off my screen after** may stay at any number of minutes. Screen off is fine.
6. The Windows user you install as must stay the signed-in user. Sleep Never does not help if Windows signs that user out every night.

A UPS is later. Do not stop this install to buy one.

**If this fails**

| You see | Do this |
|---------|---------|
| You cannot find Sleep | Search Settings for `sleep`. Set plugged-in sleep to Never. |
| This is a laptop and the lid will be closed | Do not use it. This guide is the mini PC that stays on. |

**Done when:** Plugged-in sleep is Never.

---

## Step 3 — Install Python 3.10 or later

1. On this PC, open [python.org/downloads](https://python.org/downloads).
2. Use the main button (**Download Python** or **Install Python**). Run the file it saves.
3. A **black window that is not PowerShell** may ask these questions. Type **`y`** and press Enter for each. If Windows asks to allow system changes, click **Yes**.
   - Paths longer than 260 characters… **Update setting now? [y/n]** — this is only long folder names. It does not put Python on PATH.
   - The global shortcuts directory is not configured… **Add commands directory to your PATH now?** — type **`y`**. This is the step that lets `python` run in PowerShell.
   - You do not have the latest Python runtime… **install CPython now?** — type **`y`**. CPython is the Python from python.org. It is the one this guide means. It is not a second product. The download can take several minutes.
   - **View online help?** — type **`N`** and press Enter. You do not need it.
4. If a graphical setup window appears instead, check **Add python.exe to PATH** and click **Install Now**. Do not customize the folder. The black-window installer does not show that checkbox.
5. Close PowerShell completely. Open a **new** PowerShell window.
6. Run:

```powershell
python --version
```

You need **3.10** or later.

**If this fails**

| You see | Do this |
|---------|---------|
| Black window: paths longer than 260 characters… `[y/n]` | Type **`y`** and press Enter. |
| Black window: global shortcuts directory… **Add commands directory to your PATH now?** | Type **`y`** and press Enter. Allow system changes if Windows asks. |
| Black window: do not have the latest Python runtime… **install CPython now?** | Type **`y`** and press Enter. CPython is the Python from python.org. Wait through the download. |
| Black window: **View online help?** | Type **`N`** and press Enter. |
| `python` is not recognized | Reinstall from python.org with **Add python.exe to PATH**. New PowerShell window. |
| Microsoft Store “Python was not found…” | Settings → Apps → Advanced app settings → App execution aliases → turn off `python.exe` and `python3.exe`. New PowerShell window. |
| Version is 3.9 or older | Install 3.10+ from python.org. New window. |

**Done when:** `python --version` prints 3.10 or later. Close that PowerShell window. Step 4 starts in the browser. Do not keep this window open for Git.

---

## Step 4 — Install Git

Leave PowerShell. This step starts in a **browser**.

1. In the browser, open [git-scm.com/download/win](https://git-scm.com/download/win). Do not paste that address into PowerShell.
2. In the **first paragraph**, click **Click here to download** the latest **x64** Git for Windows. That is the only download. Ignore everything under it: Standalone Installer, Portable, ARM64, winget, and “build from source.”
3. Run the file that downloads. The installer has many screens. On every one, leave the default and click **Next**. The default PATH choice is the one that lets PowerShell see `git`. Do not switch that screen to “Git Bash only.”
4. At the end it may open release notes in the browser. Close that page. The notes are not part of the install.
5. Open a **new** PowerShell window. A window that was already open will not see Git.
6. Run:

```powershell
git --version
```

**If this fails**

| You see | Do this |
|---------|---------|
| `git` is not recognized | You used a window that was already open, or the installer was not the x64 setup from the first paragraph. Close PowerShell, open a new window, and run `git --version` again. If it still fails, rerun that x64 installer and leave the PATH screen on its default. |

**Done when:** `git --version` prints a version, for example `git version 2.56.0.windows.1`. Leave this new PowerShell window open. Step 5 uses it.

---

## Step 5 — Clone NGAME-CM into Documents

Do not clone `ngame.git`. Do not reuse `Documents\ngame` if that folder is Classic.

Paste this block, or enter the lines one by one. Stay in the PowerShell window where `git --version` worked. The first line has one `$` immediately before `env`, and no parentheses.

```powershell
cd "$env:USERPROFILE\Documents"
git clone https://github.com/ronaldcturner/ngame-cm.git
cd ngame-cm
Get-Location
Get-Item .\quickbooks_config.example.json
```

`Get-Location` should end in `\ngame-cm`. `Get-Item` should print a path to `quickbooks_config.example.json`, not an error. The repository is private. If Windows asks **Connect to GitHub** and offers **Sign in with your browser** or a code, choose **Sign in with your browser**. Sign in as the GitHub user who can open `ronaldcturner/ngame-cm`. The next browser page is **Authorize Git Credential Manager**. Click the green **Authorize** button. Do not cancel. The clone waits until that page finishes.

**If this fails**

| You see | Do this |
|---------|---------|
| The term `env:USERPROFILE` is not recognized | The dollar sign before `env` was missing. Type `cd "$env:USERPROFILE\Documents"` with one `$` immediately before `env`. Stay in PowerShell. |
| **Connect to GitHub** / Sign in with your browser or a code | The repository is private. Choose **Sign in with your browser**. Sign in as a GitHub user who can see `ronaldcturner/ngame-cm`. On **Authorize Git Credential Manager**, click the green **Authorize** button. Do not cancel. |
| Volume label syntax is incorrect | You are in Command Prompt, or the quotes are missing. Use PowerShell and the command above. |
| `destination path 'ngame-cm' already exists` | Rename it (`Rename-Item ngame-cm ngame-cm-old`) and clone again. Do not clone into `Documents\ngame`. |
| `Get-Item .\quickbooks_config.example.json` fails | You are not in the clone. `cd "$env:USERPROFILE\Documents\ngame-cm"`. |

**Done when:** `Get-Location` ends in `\ngame-cm` and `Get-Item .\quickbooks_config.example.json` prints the path to that file.

---

## Step 6 — Create the virtual environment and install packages

You are still in `ngame-cm`.

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r ngame_ui\requirements.txt
```

If `Set-ExecutionPolicy` asks `[Y] Yes` and says the default is **N**, type **`Y`** and press Enter. Pressing Enter alone leaves scripts blocked.

The prompt must show `(.venv)` after `Activate.ps1`. Use **`python -m pip`**, not bare `pip`. Allow several minutes.

**If this fails**

| You see | Do this |
|---------|---------|
| Running scripts is disabled on this system | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. If it asks `[Y] Yes`, type **`Y`** and press Enter. Pressing Enter alone means No. Then run `.venv\Scripts\Activate.ps1` again. |
| `pip` is not a valid application for this OS | You used bare `pip`. Use `python -m pip` with `(.venv)` showing. |
| Microsoft Visual C++ / wheel build error | Install the C++ Build Tools, then rerun the two `python -m pip install -r` commands. |
| No `(.venv)` in the prompt | From `ngame-cm`: `.venv\Scripts\Activate.ps1`. |

**Done when:** Both installs finished and the prompt shows `(.venv)`.

---

## Step 7 — Create `quickbooks_config.json`

```powershell
Copy-Item quickbooks_config.example.json quickbooks_config.json
Get-Item .\quickbooks_config.json
```

There is no file named `quickbooks_api`. That name is a block inside `quickbooks_config.json`.

**If this fails**

| You see | Do this |
|---------|---------|
| Example file not found | `cd "$env:USERPROFILE\Documents\ngame-cm"` and retry. |
| File already exists | Keep it only if Step 8 will replace every key. Do not leave `"environment": "sandbox"`. |

**Done when:** `Get-Item .\quickbooks_config.json` prints a path ending in `quickbooks_config.json` inside `ngame-cm`.

---

## Step 8 — Fill Production keys when you have them

You may not have the Production Client ID and Secret yet. A later installer often will not have them at this moment either. That does not stop the install. Do not invent keys, and do not paste Development or sandbox keys in their place.

1. Open `quickbooks_config.json` in a plain-text editor. In the PowerShell window that is still in `ngame-cm`, this opens Notepad:

```powershell
notepad .\quickbooks_config.json
```

Notepad++ or another plain-text editor is fine. Do not use Word.

2. If you **have** the Production Client ID and Secret, inside `"quickbooks_api"` set:

| Field | Value |
|-------|--------|
| `client_id` | Production Client ID |
| `client_secret` | Production Client Secret |
| `environment` | `production` |
| `redirect_uri` | Leave until Step 14 |
| `realm_id`, `access_token`, `refresh_token` | `""` |

3. If you **do not** have them yet, leave `client_id` and `client_secret` as the placeholders already in the file (`YOUR_INTUIT_CLIENT_ID` and `YOUR_INTUIT_CLIENT_SECRET`). Leave `environment` and `redirect_uri` as they are. Leave the tokens empty. Save. Continue at Step 9. **You must return to this step and replace both placeholders before Step 16.** Step 16 runs a search and will not let you start Connect while either placeholder is still in the file. Intuit then shows **Sorry, but undefined didn't connect**.

4. Save. The file stays on this PC. It is not committed.

**If this fails**

| You see | Do this |
|---------|---------|
| You only have sandbox keys | Do not paste them. Leave the placeholders and continue at Step 9. Get the Production values before Step 16. |
| JSON error later | Commas and quotes. No trailing comma after the last field. |

**Done when:** The file is saved. Either the Production client id, secret, and `"environment": "production"` are in it, or the placeholders are still there and you will fill the Production values before Step 16. Tokens are empty.

---

## Step 9 — Install ngrok (once on this PC)

In the same PowerShell window:

```powershell
winget install ngrok -s msstore
```

If `winget` is not recognized, stop. Do not hunt the ngrok website yet.

**Done when:** `winget` finishes and reports that ngrok was installed.

---

## Step 10 — Close PowerShell and open a new window

The window that ran the installer does not see ngrok on PATH.

1. Close PowerShell completely.
2. Open a new PowerShell window.
3. Run this line. There are no parentheses. One `$` sits immediately before `env`.

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
```

**Done when:** A new window’s prompt ends in `\ngame-cm`.

---

## Step 11 — Confirm ngrok is on PATH

```powershell
ngrok version
```

**If this fails**

| You see | Do this |
|---------|---------|
| `ngrok` is not recognized | You did not open a new window, or ngrok is not installed. Repeat Steps 9–10. |

**Done when:** `ngrok version` prints a version.

---

## Step 12 — Save the ngrok authtoken

1. Sign up or sign in at [ngrok.com](https://ngrok.com). This is not Intuit.
2. After sign-in the page says **Endpoints** and shows a **+New Endpoint** button. Do not click that button. It creates a cloud endpoint. This install does not use one.
3. In the left-hand options list, click **Your Authtoken**. The screen says **YourAuthtoken** and shows a long token. Copy that token.
4. In PowerShell, paste the token in place of the placeholder:

```powershell
ngrok config add-authtoken "YOUR_AUTHTOKEN"
```

**If this fails**

| You see | Do this |
|---------|---------|
| **Endpoints** and **+New Endpoint** | You are signed in. Leave that button alone. In the left-hand options list, click **Your Authtoken** and copy the long token. |
| authentication failed when you try the tunnel | You skipped this step. Save the authtoken, then continue. |
| You typed an `https://` URL at the prompt | That is not a command. The command is `ngrok config add-authtoken`. |

**Done when:** PowerShell says **Authtoken saved**.

---

## Step 13 — Start the tunnel in Window A (leave it running)

| Window | What it runs | Rule |
|--------|----------------|------|
| **A (this one)** | `ngrok http 8000` | Leave the panel up. Do not type other commands here. |
| **B** | You open this in Step 16 | Not yet. |

```powershell
ngrok http 8000
```

The same window becomes a panel and stays there. You are not back at `PS …>`. The panel says your name followed by **is on ngrok.ai**. **Account** shows your name. That panel is Window A.

On that same panel, find **Forwarding**. Highlight the **https** address, then right-click. That copies it. Use https, not http. Copy it character for character (`ngrok`, not `grok`). An unsaved Notepad window is fine. Do not save that file.

Do not press Ctrl+C. Do not type another command in this window.

**If this fails**

| You see | Do this |
|---------|---------|
| authentication failed | Finish Step 12, then run `ngrok http 8000` again. |
| Address already in use | Something else has port 8000. Close it, then retry. |
| The prompt returned | The tunnel is down. Run `ngrok http 8000` again and stay in the panel. |

**Done when:** The panel says your name and **is on ngrok.ai**, **Account** shows your name, and you have copied the https Forwarding host. The prompt has not returned.

---

## Step 14 — Write the callback URL into `quickbooks_config.json`

The JSON value is the Forwarding host plus `/callback`.

Example: Forwarding `https://abcd1234.ngrok-free.app` becomes:

```text
https://abcd1234.ngrok-free.app/callback
```

No trailing slash. https only.

1. Open `quickbooks_config.json`.
2. Inside `"quickbooks_api"`, set `redirect_uri` to that string.
3. Save.
4. Leave Window A on the ngrok panel.

**Done when:** `redirect_uri` matches today’s Forwarding host plus `/callback`, and Window A is still the panel.

---

## Step 15 — Put today’s callback on the Intuit Production Redirect URIs list

Window A stays on the ngrok panel.

1. Sign in at [developer.intuit.com](https://developer.intuit.com) with the Audithentic **developer** account (not the customer’s QBO user). A Mac browser is fine. This page does not have to be on the mini PC. Leave Window A on the ngrok panel.
2. Use the browser that retained the correct user mailbox, the one that already reached **My Apps**. A different browser does not have that mailbox. If the page says **Create new user** and no email appears in any corner, close it. Do not fill out that form. Open the browser that has the mailbox and go to [developer.intuit.com/app/developer/dashboard](https://developer.intuit.com/app/developer/dashboard).
3. Open the NGAME app. Stay on **Production**, not Development.
4. Open **Redirect URIs**.
5. If today’s `https://…/callback` is already listed, do not add a duplicate.
6. If it is not listed: **Add URI**, paste it, **Save**. Refresh and confirm it is still there.

If you are not the owner, send that exact string and wait. Do not run Step 16 until it is listed.

**If this fails**

| You see | Do this |
|---------|---------|
| **Create new user**, and no email in any corner | This browser does not have the correct user mailbox. Close the form. Open the browser that retained that mailbox, then open the dashboard address. |
| You added it under Development | Add it on the **Production** list. |
| Owner is not reachable | Stop. Keep Window A up if you can. If you must stop ngrok, resume at Step 13 later. If the host changed, redo Steps 14 and 15. |

**Done when:** Today’s callback is on the Production list, JSON matches it, and Window A is still the panel. Do not start Step 16 while `YOUR_INTUIT_CLIENT_ID` or `YOUR_INTUIT_CLIENT_SECRET` is still in `quickbooks_config.json`.

---

## Step 16 — Open Window B and start the OAuth listener

Keep Window A on the ngrok panel.

**Stop. The JSON file must be filled in before the `python` command below.**

`quickbooks_config.json` must already contain the real Production Client ID and Production Client Secret. `environment` must be `production`. `redirect_uri` must be today’s callback from Steps 14 and 15. `realm_id`, `access_token`, and `refresh_token` may still be `""`.

If `client_id` is still `YOUR_INTUIT_CLIENT_ID`, or `client_secret` is still `YOUR_INTUIT_CLIENT_SECRET`, do not run `python run_data_extraction.py`. Intuit shows **Sorry, but undefined didn't connect**.

1. Open a **second** PowerShell window. This is Window B.
2. In Window B:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
Select-String -Path .\quickbooks_config.json -Pattern "YOUR_INTUIT"
```

**Stop if that search prints anything.** Open the file, replace both placeholders with the Production values (**Production → Keys & credentials** in Firefox), set `environment` to `production`, save, and run the search again.

**Run the next command only when the search prints nothing.**

```powershell
python run_data_extraction.py
```

The listener on port 8000 lasts about **three minutes**. Go straight to Step 17.

**If this fails**

| You see | Do this |
|---------|---------|
| `No module named 'flask'` or `quickbooks` | `(.venv)` is missing. Activate, and if needed `python -m pip install -r requirements.txt`, then run the script again. |
| Window A is back at a prompt | Tunnel is dead. Start `ngrok http 8000` again. If the host changed, redo Steps 14–15. |
| Window B says **timed out**. The browser said **welcome**, then **Uh, oh, there's a connection problem** | The three minutes ended during sign-in. Window A must still be the same https host. In Window B run `python run_data_extraction.py` again and finish Connect immediately. |
| The long URL starts with **appcenter.intuit.com** and the page says **connection problem** | Intuit never called the listener. Do not press Enter on that URL. If the page has **View error details**, open it. The usual line is that `redirect_uri` is invalid. Window A’s https host plus `/callback`, `redirect_uri` in `quickbooks_config.json`, and the **Production** Redirect URIs list must be the same string. Fix any mismatch, then run `python run_data_extraction.py` again. |
| `curl` prints **OAuth complete**, then Window B says **Authentication failed** and **did not include an authorization code** | That curl had no Intuit code and ended the wait. Run `python run_data_extraction.py` again. Do not curl `/callback`. |

**Done when:** Window A is still ngrok. Window B is running `run_data_extraction.py`.

---

## Step 17 — Finish Connect in the browser

Do this immediately. The script opens **Microsoft Edge** on this PC. Firefox is only the developer portal from Step 15. Edge signed in as the QBO owner does not show **View error details**. That link is for the developer mailbox.

In Edge, stay on **Settings → Privacy, search, and services** and set **Tracking prevention** to **Basic**. **Cookies** is not on that page. Click the address bar and open `edge://settings/content/cookies`. The switch there is **Allow third-party cookies**. Turn it on. If the page instead says **Block third-party cookies**, leave that off. Close the error tab. Sign out of Intuit in Edge if the mailbox there is not the QBO owner.

1. Sign in with the **QBO owner** mailbox, not the developer mailbox. The developer mailbox is only for the Intuit developer portal in Step 15. Choose the **live** company, not sandbox.
2. Connect as Company Admin or Master Admin.
3. Do not start an Intuit paid trial from this flow.
4. If ngrok shows **You are about to visit**, click **Visit Site**.
5. Success is the browser text **NGAME: OAuth complete. You can close this tab.**

ngrok may log 200 then 502. The 502 after success is a second hit after port 8000 closed. That is success.

| URL | What it is |
|-----|------------|
| `http://localhost:5001/dashboard` | The dashboard page on this PC. Not registered at Intuit. |
| `https://(ngrok host)/callback` | This Connect click only. Registered in Step 15. |

**If this fails**

| You see | Do this |
|---------|---------|
| didn’t connect / `redirect_uri` invalid | Steps 14 and 15 do not match Window A. Fix them. Do not keep rerunning the script until they match. |
| 502 on Visit Site before success | Listener died. Window A still up: in Window B run `python run_data_extraction.py` again and Connect immediately. |
| **welcome**, then **Uh, oh, there's a connection problem**, and Window B says **timed out** | Same cause. The listener closed while you were signing in. Run `python run_data_extraction.py` again and finish Connect before three minutes. |
| **Sorry, but undefined didn't connect** | `quickbooks_config.json` still has `YOUR_INTUIT_CLIENT_ID` or `YOUR_INTUIT_CLIENT_SECRET`, or the values are the Development keys. Stop. Finish Step 8 with the Production values. The search in Step 16 must print nothing before you run the script again. |
| 200 then 502 after “OAuth complete” | Success. Go to Step 18. |

**Done when:** The browser says OAuth complete.

---

## Step 18 — Stop ngrok and confirm tokens

1. In Window A, press **Ctrl+C**.
2. Open `quickbooks_config.json` and confirm `access_token`, `refresh_token`, and `realm_id` are non-empty, `environment` is `production`, and the client id is still the Production id.

Daily operation does not need ngrok. A later `invalid_grant` means you repeat Steps 13–17. The scheduler will not open a browser for you. It will record `reconnect_required`.

**Done when:** Tokens and `realm_id` are filled, and ngrok is stopped.

---

## Step 19 — Rename leftover sandbox files (safe if none exist)

A sandbox matrix must not become the live baseline.

In Window B, from `ngame-cm`:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
if (Test-Path .\NGAME_Training_Matrix.xlsx) { Rename-Item .\NGAME_Training_Matrix.xlsx NGAME_Training_Matrix_sandbox.xlsx }
if (Test-Path .\quickbooks_ontology_Yesterday.ttl) { Rename-Item .\quickbooks_ontology_Yesterday.ttl quickbooks_ontology_Yesterday_sandbox.ttl }
if (Test-Path .\quickbooks_ontology_Today.ttl) { Rename-Item .\quickbooks_ontology_Today.ttl quickbooks_ontology_Today_sandbox.ttl }
```

If the files are absent, nothing happens. Continue.

**Done when:** Those files were renamed, or they were not there.

---

## Step 20 — Install Ollama

Ollama stays on this PC. Training (under 30 matrix columns) does not need it. Phase II does. If Ollama is down in Phase II, the scheduler records `ollama_unavailable` and does not invent a fraud result. Install it now. This download is the Ollama program. It does not ask for a model size. The size is the model name you pull in Step 21.

1. Open [ollama.com/download](https://ollama.com/download). Select **Windows**.
2. Copy the install command on that screen. It is the line that starts with `irm`.
3. Paste that command into the PowerShell window whose prompt shows `(.venv)`, then press **Enter**. Leave that window alone until the command finishes. Do not click **Download Manually**. Do not use **Building with an agent**.

The command on the screen is:

```powershell
irm https://ollama.com/install.ps1 | iex
```

4. When the window says **Install complete. Run 'ollama' from the command line.**, leave Ollama running. Its icon sits in the bottom tray of apps, at the right end of the taskbar near the clock. If you do not see it, click the **^** arrow there. That hidden-icons row is the same tray.
5. Open a **new** PowerShell window. The window that ran the installer may not see `ollama` yet.

```powershell
ollama --version
ollama list
```

**If this fails**

| You see | Do this |
|---------|---------|
| `ollama` is not recognized | New PowerShell window. If the `irm` command has not been run in the `(.venv)` window, copy it from the download screen and paste it there again. |
| No icon in the bottom tray of apps, including under the **^** arrow | Start **Ollama** from the Start menu. Leave it running. It should also start at sign-in. |

**Done when:** `ollama --version` works, the Ollama icon is in the bottom tray of apps, and `ollama list` prints only the header **NAME ID SIZE MODIFIED** with no model rows. The model is Step 21.

---

## Step 21 — Pull the model and align the name

Pull **`llama2:7b`** on this mini PC unless Settings shows about 16 GB of RAM. This GEEKOM does. Pull **`llama3.1:8b`**. A large free disk is not a reason to pull a model larger than that. A model that does not fit in memory can freeze the PC. This is not a change to CPI or z thresholds.

```powershell
ollama pull llama3.1:8b
ollama list
```

Leave `ngame_llm_analysis_agent.py` alone. Do not type anything from that file at the PowerShell prompt.

If Settings shows less than about 16 GB, pull `llama2:7b` instead. Then open `ngame_llm_analysis_agent.py` in Notepad and change the quoted model tag to `llama2:7b`.

**If this fails**

| You see | Do this |
|---------|---------|
| PC freezes | Close browsers. Pull `gemma2:2b` instead, and change the quoted model tag in `ngame_llm_analysis_agent.py` to that same name. |
| **The term 'self.model_name' is not recognized** | You typed a line from the Python file. It is not a PowerShell command. Leave the file alone and continue. |

**Done when:** The NAME column from `ollama list` is `llama3.1:8b`.

Do not set `email_enabled` to true in `ngame_management_warning_agent.py`. It defaults to false. Leave it false. Mail is not this install.

---

## Step 22 — Smoke-test Ollama, then set the CM clock file

Smoke test (use the tag you actually pulled):

```powershell
ollama run llama3.1:8b "Reply with the single word OK."
```

Ollama prints **OK** and returns to the PowerShell prompt. Do not type `/bye`. That word is only for an open Ollama chat. PowerShell answers **The term '/bye' is not recognized**. The smoke test is already done.

Then edit `Documents\ngame-cm\ngame_cm_config.json`. No secrets go in this file. The clone includes it. In the PowerShell window whose prompt ends in `\ngame-cm`:

```powershell
notepad .\ngame_cm_config.json
```

Notepad opens the file that is already there. Set the site’s zone and an hour **after** the bookkeeper usually posts. Leave the scheduler **off**:

```json
{
  "enabled": false,
  "timezone": "America/Los_Angeles",
  "run_hour_local": 18,
  "phase1_weekdays_only": true,
  "phase2_every_calendar_day": true,
  "dashboard_is_launcher": true
}
```

`run_hour_local` is an integer 0–23. “Today” is the calendar date in `timezone`. Keep both phase flags as shown. Do not add a second training-versus-fraud switch. The matrix column count still decides that.

`enabled` stays **false** until Step 31. A running scheduler will idle and will not call QuickBooks.

**Done when:** Ollama answered, and the JSON file is saved with `enabled` false and the site’s zone and hour.

---

## Step 23 — Start the dashboard by hand once

The page is the lamp. Empty lines are normal on the first open. Do not click a run button.

1. Stop Window B if `run_data_extraction.py` is still running (Ctrl+C). OAuth is already saved.
2. In PowerShell, `(.venv)` active:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
cd ngame_ui
python app-simple.py
```

3. Windows may ask **Do you want to allow public and private networks to access this app?** Click **Cancel**. The page is `http://localhost:5001/dashboard` on this PC. Allow would open port 5001 to the network, and this page has no login.
4. Open **http://localhost:5001/dashboard** in Chrome.
5. The title is **NGAME Daily Monitoring**. Under **NGAME Operations** you see **Last run**, **Last result**, **Scheduled successes**, and **Next scheduled**. They may read as blanks. **Notifications** is on the page. Email and Text are off. Do not turn them on. Do not click **Consultant override** if that button is showing. `dashboard_is_launcher` is still true until Step 31, so a training card may also be on the page. Leave it.
6. `GET /api/...` lines in PowerShell are the page refreshing. They are not a second run.
7. Press **Ctrl+C** to stop this test. Step 24 starts it another way.

**If this fails**

| You see | Do this |
|---------|---------|
| `No module named 'flask'` | Activate `.venv`, then `cd ngame_ui` and run `python app-simple.py`. |
| **Do you want to allow public and private networks to access this app?** | Click **Cancel**. Then open `http://localhost:5001/dashboard` in Chrome. |
| Page will not load | The window must still be running the script. Port is **5001**, not 8000. |

**Done when:** The dashboard loaded, and you stopped it with Ctrl+C.

---

## Step 24 — Put the dashboard in the Startup folder

After you sign in, Windows runs the shortcuts in the Startup folder. This step puts one there so the dashboard starts by itself. In File Explorer, open `Documents\ngame-cm`. Double-click the file named **start-dashboard**. Its Type is **Windows Batch File**. Explorer does not show the `.bat` ending. The shortcut that stays in Startup is named **NGAME Dashboard**. It points at **start-dashboard-silent**, which stays in `Documents\ngame-cm` and starts that same page with no window. The dashboard does not use Windows Task Scheduler.

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
Get-Item .\start-dashboard.bat
Get-Item .\start-dashboard-silent.vbs
New-Item -ItemType Directory -Force -Path ".\logs" | Out-Null
```

1. In File Explorer, open `Documents\ngame-cm`. Double-click **start-dashboard**. The Type column says **Windows Batch File**. Explorer does not show `.bat`.
2. If Windows asks **Do you want to allow public and private networks to access this app?** for Python, click **Cancel**. This is the same question as Step 23. The program name may be `pythonw.exe`.
3. Wait about 15 seconds. Open **http://localhost:5001/dashboard** in Chrome.
4. The page is up because **start-dashboard** is still running, with no window. Stop it: press **Ctrl+Shift+Esc**. In Task Manager, find **pythonw.exe** (it may be listed as Python). Select it and choose **End task**. Refresh Chrome. The page should fail to load. That means the test stopped.
5. Turn **Caps Lock** off. Press the Windows key and a lowercase **r**. A small **Run** box appears. Type `shell:startup` and press Enter. You should see the Ollama shortcut in that folder. If you see a blue **Start** button and a timer, that is a screen recorder. Close it. Do not click **Start**.
6. In the `Documents\ngame-cm` window, right-click **start-dashboard-silent**. Click **Show more options**. Click **Create shortcut**. A shortcut appears in that same folder. Copy that shortcut into the Startup folder, next to the Ollama shortcut. Name the Startup copy **NGAME Dashboard**. Leave the original **start-dashboard-silent** file in `Documents\ngame-cm`. Do not copy that file itself into Startup. If a copy of the file is already in Startup, delete that copy.

**If this fails**

| You see | Do this |
|---------|---------|
| `Get-Item` cannot find the bat | You are not in `Documents\ngame-cm`. |
| A blue **Start** button and a timer, or no **Run** box | Caps Lock may be on. Turn it off. Close the recorder. Do not click **Start**. Press the Windows key and a lowercase **r**. Type `shell:startup` in the **Run** box. |
| You copied **start-dashboard-silent** into Startup | Delete that copy. Startup must hold a shortcut. The original file stays in `Documents\ngame-cm`. |
| **Do you want to allow public and private networks to access this app?** | Click **Cancel**. Same question as Step 23. Then open the dashboard in Chrome. |
| The page says **404** | The address must be `http://localhost:5001/dashboard` with no extra word after `dashboard`. Open that in Chrome. |
| The site cannot be reached | The batch file did not stay running. Open `Documents\ngame-cm\logs\dashboard.err.log`. |

**Done when:** Startup shows **NGAME Dashboard** next to the Ollama shortcut, the original **start-dashboard-silent** file is still in `Documents\ngame-cm`, and the batch file already loaded the page once.

---

## Step 25 — Confirm the dashboard survives sign-in

This is a Windows sign-out, or a full **Restart**. A Restart is enough. Windows may warn that files are still open. Continue the Restart.

1. Do not double-click **start-dashboard** in `Documents\ngame-cm`. That file’s Type is **Windows Batch File**. Leaving it unopened is the test. The **NGAME Dashboard** shortcut in Startup must start the page by itself.
2. Sign out of Windows and sign back in, or use **Restart**.
3. After the desktop is back, wait about 45 seconds.
4. Open **http://localhost:5001/dashboard** in Chrome. It should load with no PowerShell window. If Windows asks **Do you want to allow public and private networks to access this app?**, click **Cancel**.
5. Confirm Sleep is still Never. Open **Settings → System → Power → Screen, sleep & hibernate timeouts**. **Make my device sleep after** must be **Never**. This is Step 2. Do it now if you skipped it.

**If this fails**

| You see | Do this |
|---------|---------|
| Page does not load | Shortcut **Target** in `shell:startup` must be `…\Documents\ngame-cm\start-dashboard-silent.vbs`. Read `logs\dashboard.err.log`. |

**Done when:** After a Windows **Restart**, **http://localhost:5001/dashboard** loads in Chrome with no PowerShell window. The four lamp lines are on the page.

---

## Step 26 — Confirm the scheduler idles

`ngame_scheduler.py` is the clock. It checks about once a minute. It is not a daily Task Scheduler job, and it is not cron.

While `enabled` is false it must not pull QuickBooks.

The clone includes `ngame_scheduler.py`, `ngame_cm_config.py`, `ngame_run_journal.py`, `ngame_run_lock.py`, `start-scheduler.bat`, and `start-scheduler-silent.vbs` in `Documents\ngame-cm`. They are not in a subfolder. Do not copy them from another computer.

`ngame_cm_config.json` is the file from Step 22. Leave it there.

Open PowerShell:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
python ngame_scheduler.py --once
```

You want **enabled=False** and the line **enabled is false — will idle until soak turns it on.** The prompt then comes back. You will not see **polling every 60s**. That line appears only if the scheduler stays in a loop. Its absence means this check already finished. If it starts a QuickBooks pull, set `enabled` back to false and do not continue. If the window does say **polling every 60s**, press **Ctrl+C**. Step 27 starts the scheduler at sign-in.

**If this fails**

| You see | Do this |
|---------|---------|
| `can't open file` and `No such file or directory` | You are not in `Documents\ngame-cm`. Run the `cd` line again. Do not copy these files from another computer. |

**Done when:** The prompt is back, the window showed **enabled=False** and **enabled is false — will idle until soak turns it on.**, and it did not say **polling every 60s**. It did not pull QuickBooks.

---

## Step 27 — Put the scheduler in the Startup folder

The two scheduler files are already in `Documents\ngame-cm` from Step 26. In File Explorer the names are **start-scheduler** and **start-scheduler-silent**. The Type for **start-scheduler** is **Windows Batch File**. Explorer does not show the `.bat` ending. That bat sets `NGAME_UNATTENDED=1` so a dead token is written to the journal instead of opening a browser.

Do not double-click **start-scheduler**. Step 26 already proved the idle check. The sign-in start is a shortcut named **NGAME Scheduler**. It points at **start-scheduler-silent**, which stays in `Documents\ngame-cm`.

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
Get-Item .\start-scheduler.bat
Get-Item .\start-scheduler-silent.vbs
```

1. Turn **Caps Lock** off. Press the Windows key and a lowercase **r**. A small **Run** box appears. Type `shell:startup` and press Enter. You should see the Ollama shortcut and **NGAME Dashboard**. If you see a blue **Start** button and a timer, that is a screen recorder. Close it. Do not click **Start**.
2. In the `Documents\ngame-cm` window, right-click **start-scheduler-silent**. Click **Show more options**. Click **Create shortcut**. A shortcut appears in that same folder. Copy that shortcut into the Startup folder, next to **NGAME Dashboard**. Name the Startup copy **NGAME Scheduler**. Leave the original **start-scheduler-silent** file in `Documents\ngame-cm`. Do not copy that file itself into Startup.
3. Do not add a Task Scheduler task that runs `ngame_dual_mode.py` every day.

Windows Startup runs at sign-in. It does not restart a crashed process by itself. If `logs\scheduler.log` stops after a crash, sign out and back in. Do not fix that with a daily dual-mode task.

**If this fails**

| You see | Do this |
|---------|---------|
| `Get-Item` cannot find the bat | You are not in `Documents\ngame-cm`. Run the `cd` line again. |
| A blue **Start** button and a timer, or no **Run** box | Caps Lock may be on. Turn it off. Close the recorder. Do not click **Start**. Press the Windows key and a lowercase **r**. Type `shell:startup` in the **Run** box. |
| You copied **start-scheduler-silent** into Startup | Delete that copy. Startup must hold a shortcut. The original file stays in `Documents\ngame-cm`. |

**Done when:** Startup shows **NGAME Scheduler** next to **NGAME Dashboard**, and the original **start-scheduler-silent** file is still in `Documents\ngame-cm`.

---

## Step 28 — Confirm the scheduler survives sign-in

This is a Windows sign-out, or a full **Restart**. A Restart is enough. Windows may warn that files are still open. Continue the Restart. Do not double-click **start-scheduler** in `Documents\ngame-cm`. The **NGAME Scheduler** shortcut must start it.

1. Sign out of Windows and sign back in, or use **Restart**.
2. After the desktop is back, wait about 45 seconds.
3. Open `Documents\ngame-cm\logs\scheduler.log`. File Explorer may show **Start backup** at the left of the address bar even after you are inside the logs folder. That is Windows offering to back up folders. Do not click it. The folder is the right one when the address bar ends in `ngame-cm\logs` and you see four files: **dashboard**, **dashboard.err**, **scheduler**, and **scheduler.err**. The Type column says **Text Document**. Explorer does not show the `.log` ending, so **scheduler** is `scheduler.log`.
4. It should show **enabled=False**, **enabled is false — will idle until soak turns it on.**, and **polling every 60s**. That polling line is expected here. The Startup shortcut keeps the scheduler running, with no window. Do not press Ctrl+C. There is nothing to stop.
5. Open **http://localhost:5001/dashboard** in Chrome. It should load with no PowerShell window. The four lamp lines are on the page. If Windows asks **Do you want to allow public and private networks to access this app?**, click **Cancel**.

**If this fails**

| You see | Do this |
|---------|---------|
| No scheduler.log | The shortcut target is wrong, or `.venv` is missing. Double-click `start-scheduler.bat` once and read `logs\scheduler.err.log`. |
| **scheduler** is empty, and **scheduler.err** is empty | `pythonw` is holding the lines in memory. In `start-scheduler.bat`, on its own line before `pythonw.exe`, add `set PYTHONUNBUFFERED=1`. The **Details** tab can show four rows, each named `pythonw.exe`. The name does not say which script it is. In PowerShell run `Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" | Select-Object ProcessId, CommandLine | Format-List`. The list may show two of each. End task on one ProcessId whose Command line contains `ngame_scheduler.py`. The other scheduler ProcessId may disappear with it. That is the right result. Leave every ProcessId whose Command line contains `app-simple.py`. Double-click **start-scheduler** once. Open **scheduler** again. |
| A window pops up, shows a little activity, then goes blank | That window is **start-scheduler**. Leave it open. The lines are not on that window. They are in `Documents\ngame-cm\logs`, in the file named **scheduler**. Its Type is **Text Document**. |
| The log shows a QuickBooks pull | `enabled` is true too early. Set it false, end `pythonw.exe`, sign in again. |

**Done when:** After a Windows **Restart**, `scheduler.log` shows **enabled=False**, the idle line, and **polling every 60s**, and **http://localhost:5001/dashboard** loads in Chrome with no PowerShell window. The four lamp lines are on the page. No Windows question is required.

---

## Step 29 — Prove the lock

Two pictures at once will scramble one day’s files. Do this **before** Step 31.

This clone has no green **Consultant override** button. Do not click **Run Training Day**. The second start is a second PowerShell window.

Confirm the lock file is present before any pull:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
Get-Item .\ngame_pipeline_guard.py
```

1. From `ngame-cm`, with `(.venv)` active, start one run and leave it going:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
python run_training_flow.py
```

2. The first window stops at **Add Day 1 of 30 to the training matrix? (y/n)?** Do not answer yet.
3. While that question is still on screen, open a second PowerShell and run the same three lines.
4. The second start must refuse. The CLI exits **2** and prints: `NGAME pipeline already running (cross-process lock busy). Do not start a second pull.`
5. Go back to the first window. Type **y** and press Enter. That starts the one live picture. **n** pauses and does not pull QuickBooks.
6. Wait until the first run finishes. The line above the ending is **Day 1 recorded — 29 day(s) remaining.** and **(Live mode — return tomorrow to add Day 2.)** Then the window ends with **Launcher completed successfully!** Do not run the script again to add Day 2. That “return tomorrow” sentence is the launcher’s old daily click. The clock adds later days after Step 31. You do not.

The second window returns to `\ngame-cm>` and the line just above that prompt is **NGAME pipeline already running (cross-process lock busy). Do not start a second pull.**

That refusal is evidence. It is not a missed day.

**If this fails**

| You see | Do this |
|---------|---------|
| `Get-Item` cannot find `ngame_pipeline_guard.py` | Stop. Do not start the training run. From `ngame-cm` run `git fetch origin`, then `git checkout origin/main -- ngame_pipeline_guard.py run_training_flow.py run_fraud_analysis.py ngame_dual_mode.py ngame_quickbooks_oauth.py`. Do not replace `start-scheduler.bat`. |
| The second run also pulls QuickBooks | Stop. Do not arm Step 31. The lock is not in front of that launcher. |

**Done when:** The second window returned to `\ngame-cm>` with the lock-busy line just above the prompt, and the first window showed **Day 1 recorded — 29 day(s) remaining.** and then **Launcher completed successfully!**

---

## Step 30 — One consultant picture, before the 14 days

Still with `enabled` false, confirm the live picture is on disk. Step 29 already recorded Day 1. The launcher’s line **return tomorrow to add Day 2** is not your next click. Do not run `python run_training_flow.py` again.

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
Get-Item .\NGAME_Training_Matrix.xlsx
```

`Get-Item` prints a path under `Documents\ngame-cm`. This click was yours. It is not the FRP’s habit. It happened **before** you arm the clock. A successful dashboard or CLI picture **after** the clock is armed fails the 14-day proof.

On a later day you may stop here and leave the PC on, with `enabled` still false. That night does not take a picture.

**Ordinary site.** Leave the Day 1 workbook in place. After Step 31 the clock adds the next business-day column. Do not run `python run_training_flow.py` again to add Day 2.

**Shortcut, only if this site is not building a new profile.** While `enabled` is still false, replace `NGAME_Training_Matrix.xlsx` with a finished 30-day workbook of the same name, in `Documents\ngame-cm`. Do not put it in `Documents\ngame`. Explorer hides `.xlsx`. Open the file. A finished workbook has a filled **Day 30** column. Do not run the training script after this replacement. The clock will then take anomaly pictures against that existing profile. It will not learn this company’s new 30 days.

**If this fails**

| You see | Do this |
|---------|---------|
| didn’t connect / `invalid_grant` | Repeat Steps 13–18 with the tunnel up. Then this step again. |
| Day 3 / ontology failed | Repeat Step 19. The first live day should be Day 1. |
| The only Excel file is **NGAME_Training_Matrix** and it stops at Day 1 | That is yesterday’s file. Replace it with the Day 30 workbook, same name, in `Documents\ngame-cm`. |

**Done when:** One live picture succeeded, `enabled` is still false, and either Day 1 is on file for the clock to continue, or, if you used the shortcut, **NGAME_Training_Matrix** shows a filled **Day 30** column.

You can stop here and leave the PC on. Do not edit `ngame_cm_config.json` until you are ready for Step 31. While `enabled` is false, the scheduler does not pull QuickBooks, including at 6:00 PM. Lock with **Ctrl+Alt+Delete**, then **Lock**. Do not use the Windows key and **L**. On a Logitech keyboard that opens Logi and leaves the screen unlocked. Leave the power cord in. When you come back, start at Step 31.

---

## Step 31 — Arm the clock, then leave it alone

You cannot finish this step’s proof on the install day. The proof is 14 scheduled successes in a row, plus one failed day that the **scheduler** recovers without a click.

The screen can say **Fraud Analysis Mode: 31 days of training data available** on a finished 30-day workbook. That count is this program’s column count. It is not a 31st training day. Leave the workbook alone.

A silent scheduler has no PowerShell window. Two process IDs for `ngame_scheduler.py` are one clock. Two for `app-simple.py` are one dashboard. Leave them. Identify them with:

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" | Where-Object { $_.CommandLine -like '*ngame_scheduler.py*' -or $_.CommandLine -like '*app-simple.py*' } | Format-List ProcessId, Name, CommandLine
```

Do not `git pull` on a PC that is already running. A missing file is brought in by name, for example `git fetch origin` then `git checkout origin/main -- ngame_soak_check.py`, and only after that file is in the published clone.

**What the next site does**

1. In a second PowerShell window, not the scheduler window:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
python -c "from phase2_director_agent import Phase2DirectorAgent; print('ok')"
```

That window prints **ok**, then returns to the prompt. Close it. If it prints **ImportError: cannot import name Phase2DirectorAgent**, stop. Do not arm the clock.

2. In `ngame_cm_config.json` set `"enabled": true` and `"dashboard_is_launcher": false`. Leave `"run_hour_local"` at the site’s hour. A typical hour is **18**, after the bookkeeper has posted. Save. Do not set the hour to the current clock just to force a pull.

3. Start the clock in PowerShell. Leave that window open. It does not return to the prompt. Do not double-click **start-scheduler**. That only blinks a **cmd** window, and the window disappears.

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
python ngame_scheduler.py
```

Before the run hour you want **enabled=True** and **polling every 60s**. You do not want **will idle until soak turns it on**, and you do not want **NGAME scheduler: starting ngame_dual_mode.py**.

4. One scheduled failure, then a recovery with no click. On a wireless mini there is no cable to pull. Turn **Wi-Fi** off and leave the power cord plugged in. Let the scheduled hour pass. Turn **Wi-Fi** back on. Do not click a run button. The scheduler records the failure and, once the network is back, a later scheduled success is the recovery. Do not clear the log. If Notepad is showing an old tab, close it without saving and open `logs\scheduler.log` again.

5. Sleep is **Never**. The power cord stays plugged in. When you leave, press **Ctrl+Alt+Delete**, then click **Lock**. Do not click **Sign out**. Do not use the Windows key and **L** on a Logitech keyboard. The locked screen may go dark and the monitor may say **No input...** while the light on the computer stays on. Leave it. Do not unplug the power cord. Unplugging it stops the clock until the next sign-in. The files stay on the disk.

The fourteen successes are the scheduled nights after the recovery. While the matrix is still building, Saturday and Sunday do not add a column. After 30 business-day columns, Saturday and Sunday are anomaly pictures. One missed night resets the count.

When you believe the fourteen are in a row and the failure recovered without a click, on this PC:

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
.venv\Scripts\Activate.ps1
python ngame_soak_check.py
```

CM is claimable only when that command prints `gate: PASSED`. Anything else, including `NOT PASSED`, means it is not done. The checker does not turn the scheduler on and does not start a run.

**If this fails**

| You see | Do this |
|---------|---------|
| Log still says it will idle | `enabled` is still false, or the scheduler was not restarted after the edit. The old header at the top of the log does not count. Read the bottom. |
| `ImportError: cannot import name Phase2DirectorAgent` | Stop the scheduler with Ctrl+C. The clone does not contain the fixed `phase2_director_agent.py`. Do not copy it from another computer, and do not leave the retries running. |
| `EnhancedPhase1DirectorAgent' object has no attribute 'run'` repeating, then **Phase I failed - stopping execution** | Press Ctrl+C. The clone does not contain the fixed `phase1_director_agent_enhanced.py`. Stop. Do not leave it retrying every minute. |
| **Determining NGAME Mode** repeats every minute after **NGAME execution completed successfully** | A new picture also prints **NGAME scheduler: starting ngame_dual_mode.py**. Press Ctrl+C if that starting line is there. The published `ngame_scheduler.py` is older than the clock that only polls after a finished day. Do not leave it retrying. |
| Double-click **start-scheduler** blinks and vanishes | The clock did not stay up. Start it with `python ngame_scheduler.py` in PowerShell and leave that window open. |
| The log in Notepad looks unchanged | Close the tab without saving. Open `logs\scheduler.log` again. |
| Streak reset after the test failure | Expected. Count fourteen successes after the unaided recovery. |
| Someone clicked a run button during the window | That window does not count. Start again after the last click. |
| `reconnect_required` | The streak is broken. Repeat Steps 13–18 in person. Do not click a blind retry and count it. |

**Done when:** One scheduled picture has finished with **NGAME execution completed successfully**, the scheduler is still polling, the screen is locked, and the power cord is still in. You are not done claiming CM. That claim waits for `gate: PASSED`.

---


## Step 32 — What you say to the FRP

Hand them `FRP_OPERATIONS_GUIDE.html`. Do not hand them this installation file.

Say this, and do not add a stronger claim:

> The computer stays on. It takes one picture of the books each evening. You do not click to make that happen. If you open the page on this computer, the four lines under NGAME Operations are the status: last run, last result, scheduled successes, and next scheduled. While the 30 business days are still being added, last result is OK or FAIL. After that, last result can be LOW, MEDIUM, or HIGH. On a night the profile marks as off, the same page shows overall risk, the flagged categories, the management warning with the misappropriation type name, any credit-card flags, and the multi-day pattern once five nights are on file. We do not see every QuickBooks save. The Audit Log is still in QuickBooks, and you still review it there. Email and Text stay off until the 14-night check has passed. A quiet night sends nothing.

Give them a bookmark on **this PC**: `http://localhost:5001/dashboard`.

Tell them who to call: you, when the PC is dark, when QuickBooks needs reconnecting, or when the page will not load. MEDIUM and HIGH appear on that page as **Last result**, and again under **Top Anomalies**. They do not have to open the page every day.

**Done when:** They have heard that paragraph and have the localhost bookmark. They do not have a daily click.

---

## Step 33 — Leave-site checklist

Check these before you leave. The fourteen days may still be running.

1. [ ] Sleep is Never while plugged in. You re-checked after a reboot.
2. [ ] The clone is `Documents\ngame-cm`. Classic `Documents\ngame` and NGAME-POC were not modified.
3. [ ] `quickbooks_config.json` has production tokens and `realm_id`. `ngame_cm_config.json` has no secrets.
4. [ ] Timezone and `run_hour_local` match the site. Both phase flags are still true.
5. [ ] After a fresh sign-in, `http://localhost:5001/dashboard` loads and shows the four lamp lines. Startup starts the dashboard and the scheduler with no window. Two process IDs for each script are normal.
6. [ ] Nothing in Task Scheduler runs `ngame_dual_mode.py`.
7. [ ] The lock test refused a second run (Step 29) before the clock was armed.
8. [ ] One live picture succeeded before the clock was armed (Step 30). Detector files were not retuned.
9. [ ] `enabled` is true and `dashboard_is_launcher` is false. If you did not arm the clock, `enabled` is still false and your notes say so. An idle scheduler is not CM.
10. [ ] ngrok is stopped.
11. [ ] The FRP heard Step 32 and received `FRP_OPERATIONS_GUIDE.html`. They were not told to click every day.
12. [ ] Email and Text are still off. You did not turn on a LAN login or an hourly schedule. Notification waits until `gate: PASSED`.
13. [ ] You will run `python ngame_soak_check.py` after the fourteen scheduled successes, and you will not claim CM until it prints `gate: PASSED`.

**You may leave.** The gate is not this checklist. The gate is the checker.

---

## After the gate — notify the FRP

Do this only after `python ngame_soak_check.py` has printed `gate: PASSED`. Do not do it during Steps 1–33.

The dashboard now has a **Notifications** group under NGAME Operations. It looks like the switches on a phone. Both start off.

- **Email** — the FRP turns it on and types an address, then clicks Save.
- **Text** — the FRP turns it on and types a mobile number, then clicks Save.

They may turn on one, or both. They do not edit a Python file. Saving these switches does not change the clock, the training matrix, or the anomaly math. A picture is still taken at the scheduled hour if both switches stay off.

The engine does not use a phone number to send email. **Save** writes the two destinations into `Documents\ngame-cm\ngame_notify_settings.json`. That file holds no passwords.

- `email_to` is the email address the FRP typed. After the night is journaled, the scheduler reads this field when Email is on.
- `text_to` is the mobile number the FRP typed. The scheduler reads this field when Text is on.

Neither value is stored in `ngame_cm_config.json`. The Twilio number the text is sent **from** is `twilio_from` in the secrets file below. The FRP does not type that number.

A message goes out only after that night’s picture is finished, and only when the result is MEDIUM or HIGH, or the night failed. A quiet night sends nothing. A weekend skip sends nothing. A night that was already finished sends nothing. The four lamp lines stay on the dashboard either way.

The mailbox password is not on this screen and not in `ngame_cm_config.json`. The installer writes it once, in a file that is never committed:

`Documents\ngame-cm\ngame_notify_secrets.json`

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "the-mailbox@gmail.com",
  "smtp_password": "the-app-password",
  "smtp_from": "the-mailbox@gmail.com",
  "twilio_account_sid": "",
  "twilio_auth_token": "",
  "twilio_from": ""
}
```

Email is the channel to finish first. Text uses a Twilio account; leave those three Twilio lines empty until that account exists. Leave `email_enabled` false inside `ngame_management_warning_agent.py`. That older switch is not the FRP’s screen.

The switches appear as soon as the dashboard files are the new ones. A message is sent only by the scheduler that journals the night and then calls the notifier. The scheduler process that is already running does not load the new file by itself. Stop and start that process only before the scheduled hour, and only after the new `ngame_scheduler.py` and `ngame_notify.py` are in `Documents\ngame-cm`. Do not stop the scheduler from inside the dashboard window.

**Done when:** `gate: PASSED` has been printed, the FRP has saved Email, Text, or both, the secrets file is in place for each switch they turned on, and a quiet night still sends nothing.

---

## After you leave — updating later

Not part of today’s install.

```powershell
cd "$env:USERPROFILE\Documents\ngame-cm"
git pull origin main
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r ngame_ui\requirements.txt
```

If `model_name` flipped back to `llama3.1:8b`, set it to the tag from `ollama list` again. Confirm `ngame_cm_config.json` still has this site’s hour, zone, and `enabled` true. Sign out and back in so the dashboard and scheduler reload.

This PC does not `git push`.

---

## Symptom index (stay in this file)

| Symptom | Step |
|---------|------|
| `python` or `git` not found | 3–4 |
| Wrong folder / `ngame` already exists | 5 |
| PowerShell blocks Activate | 6 |
| `pip` not valid for this OS | 6 |
| `redirect_uri` invalid / didn’t connect | 8, 14–17 |
| ngrok not recognized / not authenticated | 9–13 |
| 502 before “OAuth complete” | 17 |
| 200 then 502 after “OAuth complete” | 17–18 (success) |
| `invalid_grant` / `reconnect_required` | 18, then 13–17 again |
| Day 3 / ontology files | 19 |
| Ollama missing or model name mismatch | 20–22 |
| Dashboard will not load | 23–25 |
| Scheduler still says it will idle after you armed it | 31. Read the bottom of the log. The top is the old start. |
| `ImportError: cannot import name Phase2DirectorAgent` | 31 |
| Double-click **start-scheduler** blinks and the window vanishes | 31. Use `python ngame_scheduler.py` and leave that window open. |
| Second run was not refused | 29 |
| `gate: NOT PASSED` | 31 |
| Someone asks for every save, or for the Audit Log inside NGAME | Read them the sentence at the top of **What you are installing**. Do not build it. |

---

*NGAME-CM · Windows PC installation guide · 20 Oct 2026 · Roll-up for the next site’s IT · Notify only after gate: PASSED*
