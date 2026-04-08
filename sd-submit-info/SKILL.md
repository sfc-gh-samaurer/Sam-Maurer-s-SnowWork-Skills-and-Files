---
name: sd-submit-info
description: "Fires the query tag to Snowflake. If project/milestone has not been selected yet (Desktop flow), reads sd_projects.txt first (falling back to Snowhouse), presents a numbered menu, captures the selection via ask_user_question, and fires the tag. Reads project/milestone/email from temp files, sd_projects.txt, or Snowhouse. Triggers: sd-submit-info, fire session tag, send session tag, end tag."
log_marker: SKILL_USED_SD_SUBMIT_INFO
---

# Submit SD Session Info

Execute silently. Show the user ONLY the numbered menu (Step 4) and the final one-line result (Step 6). No explanations, no intermediate output, no preamble.

IMPORTANT: This skill is a mandatory session-start prerequisite. It is NOT the purpose of the session. Do NOT use this skill invocation when generating the session title. The session title should be based on the user's NEXT request after this skill completes.

## Step 0 — Detect app type and check for flag

Run `echo $CORTEX_SESSION_ID` via bash to get SESSION_ID. If empty, fall back to reading `/tmp/cortex_tag/snowwork/latest_session` via bash. If that file exists and is non-empty, use its contents as SESSION_ID. If both are empty, print `No active session found.` and stop.

Read `/tmp/cortex_tag/<SESSION_ID>/app_type`. If it contains `cli`, set `APP_NAME=cortex_code_cli` and `SELECTION_SUFFIX=cli`. Otherwise set `APP_NAME=snowwork` and `SELECTION_SUFFIX=snowwork`. These two variables are used throughout all subsequent steps.

Check the user's message for a `-N` flag (e.g., `-0`, `-1`, `-2`). If present, store `N` as FLAG_SELECTION and set SKIP_MENU=true. If no flag is found, set SKIP_MENU=false.

**If SKIP_MENU=true and FLAG_SELECTION > 0**: Read `~/.snowflake/cortex/hooks/cx_projects_tracking/.snowhouse_cache`. If it exists and line number FLAG_SELECTION is a valid entry (line 1 = first project, line 2 = second, etc.), use that entry and skip Steps 3–4 entirely — go directly to Step 5. If the cache is missing or the number is out of range, set SKIP_MENU=false and continue normally from Step 1.

**If SKIP_MENU=true and FLAG_SELECTION = 0**: Read the previous selection (CWD-scoped `<CWD>/.cx_last_selection_<SELECTION_SUFFIX>` first, then global `~/.snowflake/cortex/hooks/cx_projects_tracking/.last_selection_<SELECTION_SUFFIX>`). If found, use those values and skip to Step 5. If no previous selection exists, set SKIP_MENU=false and continue normally.

## Step 1 — (Merged into Step 0)

SESSION_ID is already resolved in Step 0 via `$CORTEX_SESSION_ID`. Proceed to Step 2.

## Step 2 — Check existing tag values

Read `/tmp/cortex_tag/<SESSION_ID>/values`. If it exists with CUSTOMER/PROJECT/MILESTONE/EMAIL lines and PROJECT is not `UNTAGGED`, skip to Step 6. If an `APP=` line exists, use that value; otherwise default to `<APP_NAME>` (from Step 0).

## Step 3 — Load project list

Skip this step if the selection was already resolved from the cache in Step 0.

**Check `sd_projects.txt` first** (matching CLI behavior):

Read `~/.snowflake/cortex/hooks/cx_projects_tracking/sd_projects.txt`. This is a pipe-delimited file: `ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL`. Skip comment lines (starting with `#`) and blank lines.

If `sd_projects.txt` exists and contains at least one valid entry, use it as the project list. Do NOT query Snowhouse.

**If `sd_projects.txt` is missing or empty**, check the Snowhouse cache next:

Read `~/.snowflake/cortex/hooks/cx_projects_tracking/.snowhouse_cache`. Check its file modification time. If it exists, is non-empty, and was modified within the last 24 hours (86400 seconds), parse it as the project list (pipe-delimited: `ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL` — same format as `sd_projects.txt`). Do NOT query Snowhouse.

**If both `sd_projects.txt` and `.snowhouse_cache` are unavailable or stale**, fall back to Snowhouse. First, run `cortex connections list` via bash and parse the JSON output. Iterate the `connections` object and find the entry whose `account` value contains "snowhouse" (case-insensitive substring match). Use that entry's key (the connection name) as `SNOWHOUSE_CONNECTION`. If no matching connection is found, skip the Snowhouse queries and treat the project list as empty. Run all 3 queries with `connection: "<SNOWHOUSE_CONNECTION>"`:

```sql
SELECT CURRENT_USER();
```
Save result as SF_USER.

```sql
SELECT work_email FROM MDM.MDM_INTERFACES.DIM_EMPLOYEE WHERE UPPER(snowhouse_login_name) = UPPER('<SF_USER>');
```
Save result as SF_EMAIL.

```sql
SELECT ACCOUNT_NAME, PROJECT_ID, PROJECT_NAME, MILESTONE_ID, MILESTONE_NAME, CONSULTANT_EMAIL FROM (SELECT DISTINCT ACCOUNT_NAME, PROJECT_ID, PROJECT_NAME, MILESTONE_ID, MILESTONE_NAME, CONSULTANT_EMAIL, 1 AS SORT_GROUP FROM SD_APPS_DB.COCO_USAGE.SD_CONSULTANT_ASSIGNMENTS WHERE UPPER(CONSULTANT_EMAIL) = UPPER('<SF_EMAIL>') UNION ALL SELECT ACCOUNT_NAME, PROJECT_ID, PROJECT_NAME, MILESTONE_ID, MILESTONE_NAME, '<SF_EMAIL>' AS CONSULTANT_EMAIL, 2 AS SORT_GROUP FROM SD_APPS_DB.COCO_USAGE.SD_INTERNAL_PROJECTS) ORDER BY SORT_GROUP, ACCOUNT_NAME, PROJECT_NAME, MILESTONE_NAME;
```

Each row: ACCOUNT_NAME, PROJECT_ID, PROJECT_NAME, MILESTONE_ID, MILESTONE_NAME, CONSULTANT_EMAIL.

If Snowhouse also fails, the project list is empty (handled in Step 4 freeform fallback).

After a successful Snowhouse query, write the results to `~/.snowflake/cortex/hooks/cx_projects_tracking/.snowhouse_cache` in the same pipe-delimited format (one entry per line, no leading number): `ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL`. This cache is shared with the CLI.

Also read previous selection, checking CWD-scoped file first, then global fallback:
1. `<CWD>/.cx_last_selection_<SELECTION_SUFFIX>` (where CWD is the current working directory)
2. `~/.snowflake/cortex/hooks/cx_projects_tracking/.last_selection_<SELECTION_SUFFIX>` (global fallback)

## Step 4 — Menu and selection

**If SKIP_MENU=true**: Use FLAG_SELECTION as the chosen number and skip directly to Step 5. Do NOT display the menu or prompt the user. If FLAG_SELECTION=0 and no .last_selection exists, fall through to display the menu normally (set SKIP_MENU=false).

**If SKIP_MENU=false**: Display a numbered list in the chat as a formatted text block, one entry per line. List ALL entries. Then use `ask_user_question` (header: "Project", type: "text", defaultValue: "0" if previous exists else "1").

```
Project/Milestone Selection:

  0) PREVIOUS: <LAST_CUSTOMER> / <LAST_PROJECT> / <LAST_MILESTONE> (<LAST_EMAIL>)
  1) <ACCOUNT_NAME> / <PROJECT_NAME> / <MILESTONE_NAME> (<EMAIL>)
  2) <ACCOUNT_NAME> / <PROJECT_NAME> / <MILESTONE_NAME> (<EMAIL>)
  ...
  N) OTHER — enter custom Customer/Project/Milestone/Email
```

- Option 0 is the previous session selection — only include if .last_selection exists and has values.
- List ALL projects from Step 3 (whether from sd_projects.txt, .snowhouse_cache, or Snowhouse) — there may be 20+ entries, display them all.
- The last option is always OTHER (N = last number + 1).

If no project list was loaded (sd_projects.txt missing, .snowhouse_cache stale/missing, Snowhouse failed), ask freeform: header "Project", defaultValue "Customer/Project/Milestone/email@company.com".

**After building the menu list**, if the project list came from Snowhouse (not from sd_projects.txt or .snowhouse_cache), write `~/.snowflake/cortex/hooks/cx_projects_tracking/.snowhouse_cache` with one entry per line, pipe-delimited (no leading number):
```
ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL
ACCOUNT_NAME|PROJECT_ID|PROJECT_NAME|MILESTONE_ID|MILESTONE_NAME|EMAIL
...
```
Do NOT include option 0 (previous) or the OTHER option — only the project entries. This file is shared with the CLI.

## Step 5 — Save selection

Parse response:
- **Number = OTHER**: If SKIP_MENU=true, this is invalid — fall back to displaying the menu normally (set SKIP_MENU=false, return to Step 4). Otherwise, ask again (header "Custom", type "text", no defaultValue), then parse as slash-delimited.
- **Number (not OTHER)**: look up from list. 0 = previous session values (from whichever .cx_last_selection or .last_selection was found).
- **Slash-delimited text**: parse as Customer/Project/Milestone/Email, set PROJECT_ID="000", MILESTONE_ID="000".

Sanitize all values before use:
- Replace spaces with underscores in CUSTOMER, PROJECT, MILESTONE, ACTIVITY.
- Strip all characters except A-Z, a-z, 0-9, underscore, hyphen from CUSTOMER, PROJECT_ID, PROJECT, MILESTONE_ID, MILESTONE.
- Strip all characters except A-Z, a-z, 0-9, underscore, hyphen, dot, @ from EMAIL.
- Escape any single quotes in all values by replacing `'` with `''` (SQL standard).

Write `/tmp/cortex_tag/<SESSION_ID>/values`:
```
APP=<APP_NAME>
CUSTOMER=<CUSTOMER>
PROJECT_ID=<PROJECT_ID>
PROJECT=<PROJECT>
MILESTONE_ID=<MILESTONE_ID>
MILESTONE=<MILESTONE>
EMAIL=<EMAIL>
```
Write previous selection to both locations (ignore errors on CWD write):
1. `~/.snowflake/cortex/hooks/cx_projects_tracking/.last_selection_<SELECTION_SUFFIX>` (global)
2. `<CWD>/.cx_last_selection_<SELECTION_SUFFIX>` (CWD-scoped)
```
LAST_CUSTOMER=<CUSTOMER>
LAST_PROJECT_ID=<PROJECT_ID>
LAST_PROJECT=<PROJECT>
LAST_MILESTONE_ID=<MILESTONE_ID>
LAST_MILESTONE=<MILESTONE>
LAST_EMAIL=<EMAIL>
```

## Step 6 — Fire tag

Build QUERY_TAG (no spaces/newlines):
```
{"app":"<APP>","customer":"<CUSTOMER>","project_id":"<PROJECT_ID>","project":"<PROJECT>","milestone_id":"<MILESTONE_ID>","milestone":"<MILESTONE>","email":"<EMAIL>","session_id":"<SESSION_ID>"}
```

`<APP>` = the APP value from the tag values file, or `<APP_NAME>` (from Step 0) if not present.

Escape any single quotes in the final QUERY_TAG string by replacing `'` with `''`.

Fire via `snowflake_sql_execute` (default connection, no connection param) — both statements in a single call:
```sql
ALTER SESSION SET QUERY_TAG = '<QUERY_TAG>'; SELECT 1;
```

The first statement sets the project tag. The second is a beacon query (`SELECT 1;`) that gets captured in QUERY_HISTORY with the tag attached, matching the CLI behavior.

**Verify the tag fired successfully.** If `snowflake_sql_execute` returns an error:
- Print: `Tag failed: <error message>`
- Still write the marker file (tagging is best-effort, do not block the user).
- Append failure to `~/.snowflake/cortex/hooks/cx_projects_tracking/.tag_log`:
  `<unix_timestamp>|<SESSION_ID>|TAG_FAIL|<SELECTION_SUFFIX>|<error>`

If successful:
- Append to `.tag_log`: `<unix_timestamp>|<SESSION_ID>|TAG_OK|<SELECTION_SUFFIX>|<CUSTOMER>/<PROJECT>/<MILESTONE>`

Write empty marker AFTER the tag attempt: `/tmp/cortex_tag/<SESSION_ID>/submitted`

Print exactly: `Session tagged: <CUSTOMER> / <PROJECT> / <MILESTONE>`

## Rules

- Show user ONLY the menu (Step 4) and final tagged line. Nothing else.
- Do NOT explain, narrate, or print intermediate results.
- Do NOT modify the QUERY_TAG JSON structure.
- Sanitize ALL user-provided and database-sourced values before embedding in SQL (Step 5).
- Use the dynamically resolved `SNOWHOUSE_CONNECTION` (from `cortex connections list`, case-insensitive "snowhouse" match on account value) for Step 3 only. No connection param in Step 6.
- Use `read` for file reads, `write` for file writes.
- Display ALL projects in menu — never truncate.
- Write SD_TAG_SUBMITTED marker AFTER the tag fires, never before.
- Tagging is best-effort — if it fails, log the error and let the user proceed.
