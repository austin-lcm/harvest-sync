# Harvest Automation

Synchronise Google Calendar (or any ICS feed) into Harvest on **duration-mode** accounts.
Main improvement comes from using either Google or Microsoft Teams calendars.  
Be sure to always include the Jira Ticket/Issue (DP-12345) or update regex pattern to accomodate different patterns.
Workflow change, when pairing or working on specific issues, send over a "meeting" to other participants, and everyone can symbiotically help others create time entries.

---

## 1 — Quick-start (2 mins)

```bash
# 1. Clone & enter the repo
git clone https://github.com/your-org/harvest-automation.git
cd harvest-automation

# 2. Create an isolated env and install in editable mode (Python ≥ 3.13)
uv venv
uv pip install -e .

# 3. Copy the config template and fill in your secrets
cp config-template.toml config.toml
$EDITOR config.toml

# 4. Dry-run a sync for the current week
harvest-sync run --dry-run
```

---

## 2 — Configuration

`harvest-automation` searches for **`config.toml`** in this order:

1. `CONFIG_PATH=/abs/path/to/your.toml`  
2. `./config.toml` (repository root)  
3. `~/.config/harvest_automation/config.toml`

`config-template.toml` lists every key with sample values:

```toml
###############################################################################
# Harvest Automation - Runtime Configuration
###############################################################################
# Create and access Harvest Developer Access Tokens here: https://id.getharvest.com/developers
# 🔑  Authentication
harvest_token     = "harvest_pat_XXXXXXXXXXXXXXXXXXXXXXXX"
harvest_account   = 12345678
# Access and find your Google Calendar Private ICS URL here after selecting My calendars > {Your Name}: https://calendar.google.com/calendar/u/0/r
# 📅  Calendar feed
ics_url           = "https://calendar.google.com/calendar/ical/your-feed.ics"

# 🏗  Project/task mappings
default_project   = 111111      # billable
default_task      = 222222
nonbill_project   = 333333      # non-billable
nonbill_task      = 444444
billable_keywords = ["Client", "Project"]
nonbill_keywords  = ["internal"]
default_billable  = true

# 🪄  Filters & defaults
default_jira      = "DP-00000"
clone_tag         = "(clone)"
skip_keywords     = ["PTO", "OOO", "Holiday"]
note_template     = "{jira} | {title} | {date} | {start} | {end}"
date_format       = "%Y-%m-%d"
time_format       = "%I:%M %p"
key_separator     = " | "

# 🌍  Time-zone
timezone          = "America/New_York"
```

---

## 3 — Running the sync

| Command                                                                                        | Action                                    |
|------------------------------------------------------------------------------------------------|-------------------------------------------|
| `uv run python -c "from harvest_automation.helpers import fetch_entries_pretty as f; print(f())"`| Query Harvest to easily determine task and project ids. |
| `uv run harvest-sync`                                                                             | Sync **Mon → today** (EST)                |
| `uv run harvest-sync --start-date 2025-06-01 --end-date 2025-06-07`                               | Sync the explicit range                   |
| `uv run harvest-sync -n`                                                                          | *Dry-run* — log actions, no writes        |
| `uv run harvest-sync --help`                                                                      | Full CLI reference                        |

---

## 4 — Updating dependencies

```bash
uv pip install -e . -U   # upgrade everything permitted by pyproject.toml
uv pip list --outdated   # show what would change
```

---

## 5 — Troubleshooting

| Symptom                                                                  | Likely cause                                                        |
|--------------------------------------------------------------------------|---------------------------------------------------------------------|
| `RuntimeError: Harvest account is configured for start/end timers.`      | Switch Harvest to **Duration** mode (`Settings › Time & expenses`). |
| `No config.toml found`                                                   | Copy `config-template.toml` or set `CONFIG_PATH`.                   |
| HTTP 401/403 from Harvest API                                            | Invalid `harvest_token` or token lacks API access.                  |

---
