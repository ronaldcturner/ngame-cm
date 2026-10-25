# From Classic NGAME to NGAME-CM

**For the partnering test site** · 20 Oct 2026 · Read this first. The steps are in `NGAME_CM_INSTALLATION_GUIDE_PC.html`.

NGAME-CM is an autonomous watchdog. It stays on. It takes the picture of the books by itself. Nobody presses a button to make that happen.

## What Classic required

Classic NGAME used the same way of reading the books. A person opened a page on a work computer and pressed a button once each business day. If that person was away, or the computer was asleep, that day was missed. The bookkeeper’s own PC was doing two jobs: QuickBooks, and the daily NGAME click.

## What NGAME-CM does instead

The click is gone. A small computer, used for this purpose only, takes one picture of the QuickBooks Online ledger each evening, at an hour chosen for the site. A usual hour is 6:00 PM, after the day’s posting is done.

That picture is compared with the organization’s own profile. If the picture is meaningfully off, the result is MEDIUM or HIGH. If the night fails, the result is FAIL. A quiet night is simply quiet.

The page on that computer is a status light, not a start button. It shows four lines: last run, last result, how many scheduled nights have succeeded in a row, and the next scheduled time. Opening the page does not start a picture. On a night the profile marks as off, that same page shows the warning colors: overall risk, the flagged categories, the management warnings written after the misappropriation taxonomy is given to the local model, any credit-card watch flags, and the multi-day pattern once five nights are on file.

## The surveillance machine

This job needs a computer that can be left on. Sleep must be set to Never. The power cord stays in. The machine stays signed in. A monitor may go dark. That is fine. Pulling the power cord stops the watchdog until someone signs in again. The records already written stay on the disk.

A suitable machine is a small, inexpensive mini PC. The first host is a GEEKOM A5, with 16 GB of memory and a 1 TB drive. The brand is an example, not a requirement. What matters is: Windows 10 or 11, always powered, never sleeping, on the network at the scheduled hour, and not the bookkeeper’s everyday computer.

No NGAME software is installed on the bookkeeper’s PC. The bookkeeper keeps using QuickBooks Online in a browser. The watchdog reads that same cloud ledger, once each evening, through a read-only connection.

## Who does what

| Person | Role |
|--------|------|
| Site IT | Installs NGAME-CM once, from the Windows guide. Leaves the mini on. |
| Bookkeeper | Uses QuickBooks Online, as before. Does not run NGAME. |
| Financially Responsible Person | Does not press a daily button. May look at the four status lines. After the proving run, may turn on Email, Text, or both. |

## The first weeks, then the watchdog proper

On a new site there is no finished profile yet. The same evening clock builds one. Each business day it adds one column, for 30 business days. Saturday and Sunday during those weeks do not add a column. In that period the status line says OK when the night finished, or FAIL when it did not. It does not yet grade anomalies.

After the 30th business-day column is on file, the clock stops adding columns. From then on it takes an anomaly picture every calendar day, including Saturday and Sunday.

## What a message is, and what it is not

Email and Text stay off during installation and during the proving run. When that run has passed, the responsible person may turn on either switch, or both, and type an address or a mobile number. A message goes out only when the result is MEDIUM or HIGH, or when that night failed. A quiet night sends nothing.

The message says the night’s result. It does not list every transaction. The detail is on the status page.

## The sentence to keep

NGAME-CM is automated ongoing snapshot surveillance. It notifies the responsible person of meaningfully anomalous ledger-profile events. It does not see every QuickBooks save. It does not read the QuickBooks Audit Log. It does not perform a formal audit. The Audit Log stays in QuickBooks, and the organization still reviews it there.

Something posted and reversed between two evenings is not in the picture. That limit is part of the product. The installation guide is the procedure. This page is the change from Classic.
