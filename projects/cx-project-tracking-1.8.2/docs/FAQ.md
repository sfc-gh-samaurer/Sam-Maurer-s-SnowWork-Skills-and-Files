# FAQ

Common questions and self-service steps for cx-project-tracking.

---

## Installation

### Where do I get the installer?

- **GitHub access**: clone the repo or download the latest release zip.
- **No GitHub access**: download the release zip from the shared Google Drive folder. The link is pinned in [#sd-coco-project-tracking-help](https://snowflake.slack.com/archives/C0AMJ8X8L9X) on Slack.

The zip contains the same files as the repo release. Unzip and run `bash install.sh`.

### What should I do right after installing?

Run `sd-project-list-setup` in your first Cortex Code or SnowWork session. This queries Snowhouse once and generates `sd_projects.txt`, a local project list that both CLI and SnowWork use as their primary data source. Without it, every session falls back to a live Snowhouse query, which is slower and requires the connection to be available.

The file has a 7-day TTL. Re-run the skill when your project assignments change or after the file goes stale.

### Can I run this on a customer VDI or laptop?

Yes. On your Snowflake laptop first:

1. Run `sd-project-list-setup` inside a Cortex Code session to generate `sd_projects.txt`
2. Copy the generated file (from `~/.snowflake/cortex/hooks/cx_projects_tracking/`) into the `cx-project-tracking` folder
3. Zip and transfer to the customer device
4. Unzip and run `bash install.sh`

The installer detects `sd_projects.txt` and uses it as the project menu source.

### How do I update an existing install?

Re-run `bash install.sh` from a newer release. It overwrites hook scripts and re-merges `hooks.json` entries without losing your connection settings or project list.

---

## Project List

### I ran `sd-submit-info` but no projects appeared.

Run `zsh diagnose-tracking.sh` first — checks 3, 8, 9, and 10 cover the most common causes.

The `sd-submit-info` skill builds the project menu from three sources (tried in order): `sd_projects.txt`, `.snowhouse_cache`, and a live Snowhouse query. If none are available, the skill falls back to a freeform prompt (`customer/project/milestone/email`).

Common causes:

1. **No Snowhouse connection**: The skill queries Snowhouse using `connection: "SNOWHOUSE"`. If your Snowhouse connection is only in `config.toml` (not `connections.toml`), the query may fail. Copy the connection into `connections.toml`.
2. **No `sd_projects.txt`**: Run `sd-project-list-setup` to generate the local project list. This avoids the Snowhouse dependency for most sessions.
3. **Freeform fallback**: If all sources are unavailable, the skill asks you to type `customer/project/milestone/email` directly. Your session still gets tagged.

### The menu shows but my project is missing.

- **Snowhouse source**: verify your assignments in `SD_APPS_DB.COCO_USAGE.SD_CONSULTANT_ASSIGNMENTS`. The query joins on your email resolved from `CURRENT_USER()` via `MDM.MDM_INTERFACES.DIM_EMPLOYEE`.
- **sd_projects.txt source**: regenerate with `sd-project-list-setup` or add a line manually using the pipe-delimited format: `ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL`.

### I selected a project but I'm not sure the tag fired.

Check `~/.snowflake/cortex/hooks/cx_projects_tracking/.tag_log` for `TAG_OK` or `TAG_FAIL` entries. Each line includes the session_id, connection, and project context.

To verify in Snowflake (after ~45 minutes for `ACCOUNT_USAGE` latency):

```sql
SELECT PARSE_JSON(QUERY_TAG) AS tag, START_TIME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE TRY_PARSE_JSON(QUERY_TAG):app::STRING IN ('cortex_code_cli', 'snowwork')
  AND USER_NAME = CURRENT_USER()
ORDER BY START_TIME DESC
LIMIT 5;
```

---

## Multiple Sessions

### Can I run multiple Cortex Code sessions at the same time?

Yes. Each session gets its own temp directory (`/tmp/cortex_tag/<session_id>/`), so sessions don't interfere with each other. Tags are recorded independently per session.

Two sets of shared files use last-writer-wins, but neither affects tag accuracy:

| File | What happens | Impact |
|------|-------------|--------|
| `.cx_last_selection_cli` / `.cx_last_selection_snowwork` | Stores the previous project choice for the "0" shortcut, scoped to the IDE's working directory and app type | Each project directory remembers its own last selection per app. Two sessions of the same app type in the same directory may overwrite each other. Cosmetic only. |
| `.last_selection_cli` / `.last_selection_snowwork` | Global fallback for CWD-scoped files, written to the hooks directory | Used when no CWD-scoped file exists. Same last-writer-wins behavior. Cosmetic only. |

`.tag_log` is append-only. Lines from concurrent sessions may interleave, but each line is self-contained with its own session_id.

---

## Diagnostics

### Something isn't working. Where do I start?

Run the diagnostic script:

```bash
zsh diagnose-tracking.sh
```

It performs 10 checks:

| Check | What it validates |
|-------|------------------|
| 1 | Snowflake CLI installed, version >= 3.16 |
| 2 | `.snow_path` points to a valid `snow` binary |
| 3 | `connections.toml` format, permissions (600), Snowhouse entry, required fields |
| 4 | `config.toml` format consistency, duplicate detection |
| 5 | `hooks.json` has SessionStart + UserPromptSubmit + SessionEnd for CLI and SnowWork |
| 6 | Hook scripts present and match expected version |
| 7 | Old install directory (`cx-project-tracking`) cleaned up |
| 8 | Live `snow connection test` against the detected connection |
| 9 | Warehouse accessible on the Snowhouse connection |
| 10 | `sd_projects.txt` exists and has valid format |

### I need deeper log analysis.

```bash
zsh diagnose-tracking.sh --logs
```

This runs the 10-check checklist, then clears the Cortex Code logs and prompts you to reproduce the issue in a separate terminal. After you return, it analyzes:

- SessionStart / UserPromptSubmit hook execution
- Warehouse errors
- Error log entries
- Permission issues
- Connection and auth failures
- Session timeline

To skip the checklist and go straight to log capture:

```bash
zsh diagnose-tracking.sh --logs-only
```

### How do I read the .tag_log?

Each line in `~/.snowflake/cortex/hooks/cx_projects_tracking/.tag_log` follows this format:

```
<unix_timestamp>|<session_id>|TAG_OK|<app>|<customer>/<project>/<milestone>
<unix_timestamp>|<session_id>|TAG_AUTO|<app>|UNTAGGED/<email>|conn=<connection>(<source>)
<unix_timestamp>|<session_id>|TAG_FAIL|<app>|auto_tag_rc=<exit_code>|conn=<connection>(<source>)
```

See [USER_FLOW_PSEUDOCODE.md](USER_FLOW_PSEUDOCODE.md#tag-log-entry-types) for the full reference.

- `TAG_OK`: skill successfully fired the tag
- `TAG_AUTO`: silent auto-tag fired after 5 untagged prompts (user never ran the skill)
- `TAG_FAIL`: tag attempt failed — the error context is in the trailing fields

---

## SnowWork (Desktop)

### How do I tag my session on SnowWork?

Type `run skill sd-submit-info` at the start of your session. The skill presents a project menu and fires the tag on your active connection.

Shortcuts:
- `sd-submit-info -0` reuses your previous selection
- `sd-submit-info -N` picks project number N from the cached menu (e.g., `-3` for project 3)

### How does SnowWork handle untagged sessions?

Hooks never block prompts. On CLI, a `systemMessage` JSON warning is injected into the LLM context on each untagged prompt. On SnowWork, a plain `echo` text warning is emitted instead, which the LLM reads and surfaces directly. After 5 untagged prompts, the hooks silently fire a default tag (`PROJECT=UNTAGGED`, `CUSTOMER=UNKNOWN`) and log a `TAG_AUTO` entry.

To avoid your work being attributed to a generic placeholder, run `/sd-submit-info` as your first action. Use `/sd-submit-info -0` to reuse your previous selection in one step. You can also re-tag after auto-tag — running the skill at any point overwrites the default with your real project.

---

## Fixing an UNTAGGED Session

### I exited my session without tagging. Can I fix it?

**CLI**: Yes. Resume the session and run the skill:

```bash
cortex --continue                  # resumes your last session
# or
cortex --resume <session_id>       # resumes a specific session
```

Then run `/sd-submit-info` to select your actual project and milestone. The next prompt fires a properly-tagged beacon. You can also use `/resume` from inside an active session to switch to the untagged one.

Your session ID is shown in the startup banner and at exit. Past session IDs are stored in `~/.snowflake/cortex/conversations/`.

**SnowWork**: Open the untagged conversation from chat history and run `/sd-submit-info`. This works as long as SnowWork preserves the same session identity when you reopen a conversation — if it assigns a new session ID, the hooks treat it as a fresh session (which still gets tagged correctly, just as a new session rather than a fix of the old one).

### Does this fix the old UNTAGGED rows in QUERY_HISTORY?

No. `QUERY_HISTORY` rows are immutable. The `SELECT 1` beacons that already fired with `PROJECT=UNTAGGED` stay that way. Resuming and retagging only fixes **future** beacons in that conversation.

For reporting, you can correlate UNTAGGED sessions with adjacent properly-tagged sessions from the same user:

```sql
SELECT
    TRY_PARSE_JSON(QUERY_TAG):project::STRING AS project,
    TRY_PARSE_JSON(QUERY_TAG):session_id::STRING AS session_id,
    MIN(START_TIME) AS first_query,
    MAX(START_TIME) AS last_query,
    COUNT(*) AS beacon_count
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE TRY_PARSE_JSON(QUERY_TAG):app::STRING IN ('cortex_code_cli', 'snowwork')
  AND USER_NAME = CURRENT_USER()
  AND START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY first_query DESC;
```

### What if I rebooted before resuming?

`/tmp/cortex_tag/<session_id>/` is cleared on reboot. When you resume, `SessionStart` recreates the directory from scratch — no `submitted` marker, no `values` file. The 5-prompt countdown starts fresh, and you can tag normally with `/sd-submit-info` on the first prompt. No data is lost; the session just behaves like a new one.

---

## Distribution

### How do I distribute this to my team without GitHub access?

1. Download or build the release zip from the repo (or ask your team lead)
2. Upload the zip to the shared Google Drive folder
3. Share the Google Drive link in [#sd-coco-project-tracking-help](https://snowflake.slack.com/archives/C0AMJ8X8L9X)

Recipients unzip and run `bash install.sh`. For customer VDI deployments, include a pre-generated `sd_projects.txt` in the zip.

### Where is the Google Drive folder?

The link is pinned in the [#sd-coco-project-tracking-help](https://snowflake.slack.com/archives/C0AMJ8X8L9X) Slack channel.
