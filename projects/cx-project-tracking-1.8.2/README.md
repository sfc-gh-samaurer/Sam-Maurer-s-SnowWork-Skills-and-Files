# Cortex Code — Project Tracking (cx-project-tracking)

**Build v1.8.2**

Track **who** is using Cortex Code (CLI or SnowWork), for **which customer, project, and milestone**, with session identity — all visible in Snowflake `QUERY_HISTORY`. One beacon row per session with a JSON query tag containing project info and session ID.

See [CHANGELOG.md](CHANGELOG.md) for release history, [FAQ.md](docs/FAQ.md) for troubleshooting, [USER_FLOW_PSEUDOCODE.md](docs/USER_FLOW_PSEUDOCODE.md) for the authoritative flow pseudocode, and [CONTRIBUTING.md](CONTRIBUTING.md) for developer guidelines.

## Folder Structure

```
cx-project-tracking/
├── README.md                        ← this file
├── CHANGELOG.md                     ← release history (v1.6+)
├── CONTRIBUTING.md                  ← developer guidelines and PR process
├── .github/
│   └── CODEOWNERS                   ← required reviewers for all files
├── docs/
│   ├── FAQ.md                       ← common questions and self-service steps
│   ├── USER_FLOW_PSEUDOCODE.md      ← master flow pseudocode (CLI + SnowWork)
│   ├── GAP_ANALYSIS.md              ← pseudocode vs code gap tracker
│   └── USER_OPERATIONAL_PATTERNS.md ← known + potential user activity patterns
├── install.sh                       ← bash installer (macOS/Linux)
├── install.ps1                      ← full PowerShell installer (Windows, includes CLI auto-install)
├── diagnose-tracking.sh             ← setup diagnostic (10 checks + log capture)
├── diagnose-tracking.ps1            ← setup diagnostic (Windows PowerShell)
├── cli/
│   ├── session-tag-init.sh          ← CLI SessionStart hook
│   └── user-prompt-check.sh         ← CLI UserPromptSubmit hook
├── snowwork/
│   ├── session-tag-init.sh          ← SnowWork SessionStart hook
│   └── user-prompt-check.sh         ← SnowWork UserPromptSubmit hook
├── dashboard/
│   ├── app.py                       ← Streamlit dashboard for tag history
│   └── .streamlit/secrets.toml.example  ← Snowflake connection template
├── test/
│   ├── docker-compose.yml           ← orchestrates all test containers
│   ├── run-tests.sh                 ← test runner (bash/crlf/ps1/all)
│   ├── Dockerfile.bash              ← Ubuntu container for install.sh tests
│   ├── Dockerfile.crlf              ← Ubuntu container for CRLF tests
│   ├── Dockerfile.powershell        ← PowerShell container for install.ps1 tests
│   ├── test-install-sh.sh           ← bash installer test suite
│   ├── test-install-ps1.ps1         ← PowerShell installer test suite
│   └── test-crlf.sh                 ← CRLF injection + auto-fix tests
└── skills/
    ├── sd-project-list-setup/
    │   └── SKILL.md                 ← generates sd_projects.txt from Snowhouse
    ├── sd-verify-tracking/
    │   └── SKILL.md                 ← verifies installation is complete
    └── sd-submit-info/
        └── SKILL.md                 ← fires session tag via active connection
```

## How It Works

### CLI Flow (Cortex Code CLI with hooks)

```
cortex -c my_connection
┌────────────────────────────────────────────┐
│  SessionStart hook fires                   │
│  → saves session_id + connection to /tmp   │
└─────────────────────┬──────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  UserPromptSubmit hook fires (each prompt) │
│  → if untagged: appends warning to output  │
│  → after 5 untagged: auto-tags as UNTAGGED │
│  → if tagged: re-fires beacon in background│
└─────────────────────┬──────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  User runs: /sd-submit-info                │
│  → skill presents project menu             │
│  → fires ALTER SESSION SET QUERY_TAG       │
│    + SELECT 1 beacon                       │
└─────────────────────┬──────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  Normal Cortex session (prompts pass thru) │
└────────────────────────────────────────────┘
```

### SnowWork Flow (Desktop app with non-blocking hooks)

```
User types: run skill sd-submit-info
┌────────────────────────────────────────────┐
│  sd-submit-info skill fires                │
│  → reads sd_projects.txt (if available)    │
│    falls back to .snowhouse_cache / live   │
│  → shows numbered menu                     │
│  → user picks a project                    │
│  → fires ALTER SESSION SET QUERY_TAG       │
│    + SELECT 1 beacon                        │
└─────────────────────┬──────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  Normal SnowWork session                   │
└────────────────────────────────────────────┘
```

## Session Submission

### CLI (Cortex Code CLI)

The `user-prompt-check.sh` hook runs on every prompt. Before tagging, it appends a warning reminding the user to run `sd-submit-info`. After 5 untagged prompts, it silently fires a default tag (`PROJECT=UNTAGGED`). Once the user runs `sd-submit-info`, the skill presents a project menu and fires `ALTER SESSION SET QUERY_TAG` + `SELECT 1` via `snowflake_sql_execute`. Every subsequent prompt re-fires the tag in the background (beacon). No additional steps required.

### SnowWork (Desktop)

The user must type `run skill sd-submit-info` to trigger the submission skill, which queries Snowhouse for the project list, presents a menu, and fires `ALTER SESSION SET QUERY_TAG` + `SELECT 1` via `snowflake_sql_execute`. A `-N` flag can be passed to auto-select a project by number (e.g., `run skill sd-submit-info -0` reuses the previous session selection). Every subsequent prompt re-fires the tag in the background (beacon).

## Data Sources

The project menu is built from three tiers (tried in order):

1. **sd_projects.txt** (checked first) — local pipe-delimited file with 7-day TTL. Generated by the `sd-project-list-setup` skill. Used when present and fresh, or when Snowhouse is unreachable (e.g., customer VDI/laptop). This is the recommended source for day-to-day use.
2. **.snowhouse_cache** (checked second) — shared cache file with 24-hour TTL, written automatically when a live Snowhouse query runs. Both CLI and SnowWork read and write this file.
3. **Snowhouse live query** (last resort) — queries `SD_APPS_DB.COCO_USAGE.SD_CONSULTANT_ASSIGNMENTS` joined with `SD_APPS_DB.COCO_USAGE.SD_INTERNAL_PROJECTS` via UNION ALL. Results are written to `.snowhouse_cache` for subsequent sessions. Email resolved from `CURRENT_USER()` → `MDM.MDM_INTERFACES.DIM_EMPLOYEE`.

Running `sd-project-list-setup` once after installation ensures tier 1 is populated, avoiding the Snowhouse dependency for most sessions.

### sd_projects.txt Format

```
ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL
```

Example:
```
ACME_CORP|PRJ-001|Data_Migration|MS-001|Phase_1|jane.doe@snowflake.com
INTERNAL|INT-042|PERSONAL_ACTIVITY|MS-000|NONE|jane.doe@snowflake.com
```

## Query Tag Schema

Each session produces one beacon `ALTER SESSION` with a JSON `QUERY_TAG`:

```json
{
  "app": "cortex_code_cli",
  "customer": "ACME_CORP",
  "project_id": "PRJ-001",
  "project": "Data_Migration",
  "milestone_id": "MS-001",
  "milestone": "Phase_1",
  "email": "jane.doe@snowflake.com",
  "session_id": "abc123-def456"
}
```

## Quick Start

**You must do a local install before installing on a customer asset.**

### Prerequisites

- **`connections.toml` format**: All connection sections must use the same format — either all bare `[name]` or all `[connections.name]`. Mixed formats will break the Snowflake CLI. Run `snow connection list` to verify; if it errors, fix the format first.

### Local Install (Snowflake laptop with Snowhouse access)

1. Run `bash install.sh`
2. Run `sd-project-list-setup` in a Cortex Code or SnowWork session to generate your project list (`sd_projects.txt`). This is a one-time step that caches your Snowhouse assignments locally so future sessions load instantly without a live Snowhouse query.
3. Start a new Cortex Code session — the project menu appears on first prompt
4. Select a project/milestone — the session is tagged automatically

> **Why run `sd-project-list-setup` first?** Without it, every session queries Snowhouse live to build the project menu. This works, but is slower and requires the Snowhouse connection to be available. Once `sd_projects.txt` exists, both CLI and SnowWork read it directly (7-day TTL). Re-run the skill any time your assignments change or the file goes stale.

### Customer VDI / Laptop Deploy

1. On your Snowflake laptop, run the `sd-project-list-setup` skill to generate `sd_projects.txt`
2. Copy `sd_projects.txt` into this directory
3. Zip this directory and transfer to the customer laptop/VDI
4. Unzip and run `bash install.sh`
5. Start a new Cortex Code session, select a project — the session is tagged automatically

### Windows Install

For native Windows, use the full PowerShell installer:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

This does everything `install.sh` does: copies hooks, merges `hooks.json` and `settings.json`, installs skills, normalizes line endings, and tests the connection.

If you only need the Snowflake CLI binary and will run `install.sh` via Git Bash or WSL:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

## Tips and Tricks

**Tag early.** Run `/sd-submit-info` as your first action in every session. If you skip it, an auto-tag fires after 5 prompts with `PROJECT=UNTAGGED` and `CUSTOMER=UNKNOWN` — your work still shows up in reporting, but attributed to a generic placeholder instead of your actual project.

**Use shortcuts to tag in seconds.** Once you've tagged at least one session, you can skip the menu entirely:

| Command | What it does |
|---|---|
| `/sd-submit-info -0` | Reuses your previous project selection (fastest option) |
| `/sd-submit-info -3` | Picks project #3 from the cached menu by number |
| `/sd-submit-info` | Full menu — use when switching projects or on first run |

**Run `sd-project-list-setup` once.** This caches your Snowhouse assignments locally in `sd_projects.txt`. Without it, every `/sd-submit-info` call queries Snowhouse live, which is slower and requires the connection to be available. The file has a 7-day TTL — re-run the skill when your assignments change.

**Folder-per-customer works best.** If you launch sessions from different directories per customer (e.g., `~/projects/acme/`), the `-0` shortcut automatically remembers the right project for each folder.

**You can re-tag after auto-tag.** If you see `PROJECT=UNTAGGED` in your session, running `/sd-submit-info` at any point overwrites it with the real project. The corrected tag applies to all subsequent queries in that session.

## Querying Results

Find tagged rows in Snowflake:

```sql
SELECT
    PARSE_JSON(QUERY_TAG):app::STRING          AS app,
    PARSE_JSON(QUERY_TAG):customer::STRING     AS customer,
    PARSE_JSON(QUERY_TAG):project_id::STRING   AS project_id,
    PARSE_JSON(QUERY_TAG):project::STRING      AS project,
    PARSE_JSON(QUERY_TAG):milestone_id::STRING AS milestone_id,
    PARSE_JSON(QUERY_TAG):milestone::STRING    AS milestone,
    PARSE_JSON(QUERY_TAG):email::STRING        AS email,
    PARSE_JSON(QUERY_TAG):session_id::STRING   AS session_id,
    START_TIME,
    USER_NAME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE TRY_PARSE_JSON(QUERY_TAG):app::STRING IN ('cortex_code_cli', 'snowwork')
  AND TRY_PARSE_JSON(QUERY_TAG):project_id IS NOT NULL
ORDER BY START_TIME DESC;
```

Note: `ACCOUNT_USAGE.QUERY_HISTORY` has up to 45 minutes latency.

## Reporting

A Snowflake task (`SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS_LOAD`) runs every 30 minutes to MERGE tagged rows from `QUERY_HISTORY` into `SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS`. The task uses `TRY_PARSE_JSON` to safely skip any non-JSON query tags.

Supporting views:

| View | Purpose |
|------|---------|
| `V_SESSION_TAG_SUMMARY` | Single-row KPI summary (total employees, with/without tags, unique projects, total sessions, last refresh) |
| `V_SESSION_TAG_PROJECTS` | Customer projects grouped by customer/project with session/consultant counts |
| `V_SESSION_TAG_MISSING_EMPLOYEES` | SD employees from Salesforce who have no matching tags |

A local Streamlit dashboard (`dashboard/app.py`) displays these views. Run with:

```bash
SNOWFLAKE_CONNECTION_NAME=SNOWHOUSE streamlit run dashboard/app.py
```

## Debugging

Run `diagnose-tracking.sh` for a 10-check diagnostic (see Troubleshooting below).

## install.sh Behavior

- Checks for the Snowflake CLI (`snow`) and auto-installs if missing:
  - **macOS**: Homebrew (`brew tap snowflakedb/snowflake-cli && brew install snowflake-cli`), falls back to pip/pipx
  - **Linux**: pipx → pip3 → pip, with deb/rpm instructions as fallback
  - **Windows (Git Bash/MSYS)**: pip, with MSI installer and PowerShell script as fallback
- If `snow` is installed but not on PATH, probes common locations (`/opt/homebrew/bin`, `/usr/local/bin`, `~/.local/bin`, `~/Library/Python/3.*/bin`) and saves the discovered path to `.snow_path` for hooks to use at runtime
- Copies hook scripts from `cli/` and `snowwork/` subdirectories to `~/.snowflake/cortex/hooks/cx_projects_tracking/`
- Merges CLI hook entries (`SessionStart`, `UserPromptSubmit`) into `~/.snowflake/cortex/hooks.json` (does not overwrite existing hooks)
- Merges SnowWork hook entries into `~/.snowflake/cortex/settings.json` for Cortex Code Desktop
- Session tagging is handled directly by the `user-prompt-check.sh` hook (CLI) or the `sd-submit-info` skill (SnowWork)
- Checks `~/.snowflake/connections.toml` first for a connection with `snowhouse` in the account value (e.g. `account = "SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2"`)
- If not found, checks `~/.snowflake/config.toml` and automatically copies the matching entry into `connections.toml` (the `snow` CLI only resolves `--connection` names from `connections.toml`)
- Installs `sd-project-list-setup` skill only when a Snowhouse account is detected
- Installs `sd-verify-tracking` skill unconditionally
- Installs `sd-submit-info` skill unconditionally

## CLI PATH Resolution

Hook scripts resolve the `snow` binary at runtime without modifying PATH:

1. `.snow_path` file written by `install.sh` at install time
2. Fallback: `command -v snow`

The same approach is used for `python3` via `.python3_path`.

## Skills

| Skill | Purpose | Installed When |
|-------|---------|----------------|
| `sd-project-list-setup` | Generates `sd_projects.txt` by querying Snowhouse | Snowhouse account detected |
| `sd-verify-tracking` | Verifies installation is complete and working | Always |
| `sd-submit-info` | Fires session tag via active connection (SnowWork flow) | Always |

## Concurrency

Each session uses a dedicated temporary directory (`/tmp/cortex_tag/<session_id>/`) so multiple concurrent sessions do not interfere with each other.

## Troubleshooting

Run the diagnostic script to validate your setup:

```bash
# Full checklist (10 checks — CLI, connections, hooks, warehouse, etc.)
zsh diagnose-tracking.sh

# Checklist + live log capture and analysis
zsh diagnose-tracking.sh --logs

# Log capture only (skip checklist)
zsh diagnose-tracking.sh --logs-only
```

On Windows (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File diagnose-tracking.ps1
```

The checklist validates: Snowflake CLI install, `.snow_path`, `connections.toml` format and fields, `config.toml` duplicates, `hooks.json` registration, hook scripts, old install cleanup, connection test, warehouse accessibility, and `sd_projects.txt`.

Log capture mode clears the CoCo logs, prompts you to reproduce the issue in a separate terminal, then analyzes `SessionStart`/`UserPromptSubmit` execution, warehouse errors, permission denials, and auth failures.

## Testing

Docker-based tests validate the installers and CRLF fix logic on Linux containers without requiring Snowflake connectivity.

**Prerequisites**: Docker Desktop running.

```bash
# Run all tests (bash installer, CRLF, PowerShell installer)
bash test/run-tests.sh

# Run individual suites
bash test/run-tests.sh bash      # install.sh on Ubuntu
bash test/run-tests.sh crlf      # CRLF injection + auto-fix
bash test/run-tests.sh ps1       # install.ps1 on PowerShell
```

| Container | Base image | What it tests |
|-----------|-----------|---------------|
| `test-bash` | `ubuntu:22.04` | `install.sh` — directory creation, file copies, hooks.json/settings.json merge, idempotency, skills |
| `test-crlf` | `ubuntu:22.04` | CRLF injection → detection → auto-fix → syntax check, `dos2unix` vs `sed` fallback |
| `test-powershell` | `mcr.microsoft.com/powershell` | `install.ps1` — same coverage as bash but in PowerShell, plus CRLF round-trip |

## Known Issues

- **Query tag fires on wrong account (or not at all)**: Previously, `snow sql` ran without `--connection`, causing it to look for a literal `[default]` section in `connections.toml` — not the `default_connection_name` value. Users with multiple connections and no `[default]` section see a silent "Connection default is not configured" error, and the tag never reaches Snowflake. **Fixed**: the hook now reads the session connection detected by `session-tag-init.sh` and passes it via `--connection`.
- **Mixed `connections.toml` section formats**: The Snowflake CLI (`snow`) cannot parse `connections.toml` when it contains both `[connections.xxx]` and bare `[xxx]` section headers. This causes `snow sql` to fail silently inside the hooks, producing misleading errors like "SNOWADHOC is not available". **Fix**: use one consistent format (bare `[name]` recommended). The installer now detects this and warns.
- **Snowhouse connection in config.toml only**: The `snow` CLI resolves `--connection` names from `connections.toml`, not `config.toml`. If your Snowhouse entry is only in `config.toml`, the hook will automatically copy it into `connections.toml` on first run.
- **ID_TOKEN not cached**: The user must connect via `externalbrowser` at least once (e.g. `snow connection test -c SNOWHOUSE`) to populate the macOS keychain. The account must have `ALLOW_ID_TOKEN=TRUE`.
- **Linux**: The ID_TOKEN keychain path is macOS-only. Linux users need key-pair, PAT, or password auth configured in their connection.
- **Special characters in project data**: Project/customer/milestone names containing apostrophes or special characters are handled safely (whitespace trimming uses `sed` instead of `xargs`).
- **Windows**: The bash installer (`install.sh`) requires Git Bash, WSL, or similar. Use `install.ps1` for a full native PowerShell install.
- **CRLF line endings (WSL)**: If scripts were transferred through Windows (email, Edge download, Git clone on Windows), CRLF line endings break bash execution. Both `install.sh` and `install.ps1` auto-detect and fix this. A `.gitattributes` file also enforces LF on checkout.
- **Python keychain popup (macOS)**: When using `externalbrowser` auth, the Snowflake Python connector stores an ID_TOKEN in the macOS keychain. On first use (and periodically after), macOS prompts for your laptop password to authorize Python access. This popup is expected but can be alarming. Choose "Always Allow" to avoid repeated prompts. If denied, the connection falls back to browser auth each time.
- **SnowWork double-run (CoCo CLI limitation)**: On a fresh SnowWork session, the first `/sd-submit-info` invocation fails with "Unknown command" because CoCo CLI does not pre-load skills. This triggers automatic skill attachment (`[Skill Attached: sd-submit-info]`), after which a second invocation works normally. This is a known CoCo CLI behavior, not a bug in the hooks. **Workaround**: run `/sd-submit-info` once to attach the skill, then run `/sd-submit-info -0` (or your preferred flag) to execute.
