# Harvest Automation

## Main Features
 - Synchronises Google Calendar (or any ICS feed) with Harvest.
 - Compares meeting start and end times to ensure tracked time is not duplicated.
 - Any approved/submitted days will be skipped.
 - Defaults to most recently occuring Monday (12:00 AM EST) for start date, and current day for end date (11:59 PM EST).

**Be sure to always include the Jira Ticket/Issue (AA-12345) somewhere in the title of EVERY meeting.**

**Update your regex pattern if your Jira Ticket/Issue naming pattern is different than `_JIRA_RE = re.compile(r"\b[A-Z]{2,}-\d+\b")`**



---

## 1 - Quick-start (2 mins)

```bash
# 1. Clone & enter the repo
git clone https://github.com/austin-lcm/harvest-sync.git
cd harvest-sync

# 2. Create an isolated env and install in editable mode (Python ≥ 3.13)
uv venv
uv pip install -e .
source .venv/bin/activate # Linux/Mac Os terminals

# 3. Copy the config template and fill in your secrets
cp config-template.toml config.toml

# 4. Dry-run a sync for the current week
uv run harvest-sync --dry-run
```

---

## 2 - Configuration

`harvest-sync` **`config.toml`** needs to be set here:

`./config.toml` (repository root)  


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

## 3 - Running the sync

| Command                                                                                        | Action                                    |
|------------------------------------------------------------------------------------------------|-------------------------------------------|
| `uv run python -c "from harvest_automation.helpers import fetch_entries_pretty as f; print(f())"`| Query Harvest to easily determine task and project ids. |
| `uv run harvest-sync`                                                                             | Sync **Mon → today** (EST)                |
| `uv run harvest-sync --start-date 2025-06-01 --end-date 2025-06-07`                               | Sync the explicit range                   |
| `uv run harvest-sync -n`                                                                          | *Dry-run* - log actions, no writes        |
| `uv run harvest-sync --help`                                                                      | Full CLI reference                        |

---

## 4 - Updating dependencies

```bash
uv pip install -e . -U   # upgrade everything permitted by pyproject.toml
uv pip list --outdated   # show what would change
```

---

## 5 - Troubleshooting

| Symptom                                                                  | Likely cause                                                        |
|--------------------------------------------------------------------------|---------------------------------------------------------------------|
| `No config.toml found`                                                   | Copy `config-template.toml` or set `CONFIG_PATH`.                   |
| HTTP 401/403 from Harvest API                                            | Invalid `harvest_token` or token lacks API access.                  |

---
