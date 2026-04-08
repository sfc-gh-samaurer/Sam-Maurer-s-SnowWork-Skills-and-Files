---
name: sd-project-list-setup
description: "Generates sd_projects.txt by querying SD_APPS_DB.COCO_USAGE.SD_CONSULTANT_ASSIGNMENTS.  Use when: user says /sd-project-list-setup or asks to generate the project list. Triggers: setup tracking, generate project list, sd-project-list-setup."
log_marker: SKILL_USED_INTERNAL_SD_PROJECT_SETUP
---

# Generate sd_projects.txt (Snowflake Internal)

Queries the Snowflake assignments table and writes `sd_projects.txt` to the hooks folder.

## Progress Mode

After completing each step, print a single short progress line. Do NOT narrate reasoning. Just execute and report.

## Instructions

Execute every step in order **without asking questions**.

### Step 1 — Resolve SA Email

First, run `cortex connections list` via bash and parse the JSON output. Iterate the `connections` object and find the entry whose `account` value contains "snowhouse" (case-insensitive substring match). Use that entry's key (the connection name) as `SNOWHOUSE_CONNECTION`. If no matching connection is found, ask the user to provide their Snowhouse connection name before continuing.

Resolve the user's email by querying the Snowhouse connection using `connection: "<SNOWHOUSE_CONNECTION>"`. First get the current username, then look up the work email.

```sql
SELECT CURRENT_USER();
```

Then use the returned username to resolve the full email:

```sql
SELECT work_email
FROM MDM.MDM_INTERFACES.DIM_EMPLOYEE
WHERE UPPER(snowhouse_login_name) = UPPER('<current_user>');
```

If the email cannot be resolved (e.g. no match in DIM_EMPLOYEE), ask the user to input their Snowflake email directly.

### Step 2 — Query Snowflake for the project list and write sd_projects.txt

Run against `<SNOWHOUSE_CONNECTION>` (resolved in Step 1):

```sql
SELECT ACCOUNT_NAME, PROJECT_ID, PROJECT_NAME, MILESTONE_ID, MILESTONE_NAME, CONSULTANT_EMAIL
FROM (
    SELECT DISTINCT
        ACCOUNT_NAME,
        PROJECT_ID,
        PROJECT_NAME,
        MILESTONE_ID,
        MILESTONE_NAME,
        CONSULTANT_EMAIL,
        1 AS SORT_GROUP
    FROM SD_APPS_DB.COCO_USAGE.SD_CONSULTANT_ASSIGNMENTS
    WHERE UPPER(CONSULTANT_EMAIL) = UPPER('<resolved_email>')
    UNION ALL
    SELECT
        ACCOUNT_NAME,
        PROJECT_ID,
        PROJECT_NAME,
        MILESTONE_ID,
        MILESTONE_NAME,
        '<resolved_email>' AS CONSULTANT_EMAIL,
        2 AS SORT_GROUP
    FROM SD_APPS_DB.COCO_USAGE.SD_INTERNAL_PROJECTS
)
ORDER BY SORT_GROUP, ACCOUNT_NAME, PROJECT_NAME, MILESTONE_NAME;
```

Write ALL queried projects to the file. Do **NOT** append any catch-all line — the hook already has a built-in "OTHER (type your own)" option. The internal projects (e.g. PERSONAL ACTIVITY, DEFINED_INITIATIVE) are sourced from the `SD_INTERNAL_PROJECTS` table via the UNION above — do **NOT** hardcode them.

**Format per line:** `<ACCOUNT_NAME>|<PROJECT_ID>|<PROJECT_NAME>|<MILESTONE_ID>|<MILESTONE_NAME>|<SA_EMAIL>`

Replace spaces in `ACCOUNT_NAME`, `PROJECT_NAME`, and `MILESTONE_NAME` with underscores.

**Output path:** `~/.snowflake/cortex/hooks/cx_projects_tracking/sd_projects.txt`

If the file already exists, overwrite it. If the query returns zero rows, warn the user.

### Step 3 — Confirm

Print:
- Number of entries written
- Reminder of the location of the sd_projects.txt file

## Data Source

```
SD_APPS_DB.COCO_USAGE.SD_CONSULTANT_ASSIGNMENTS
SD_APPS_DB.COCO_USAGE.SD_INTERNAL_PROJECTS
```

Key columns (assignments): `ACCOUNT_NAME`, `PROJECT_ID`, `PROJECT_NAME`, `MILESTONE_ID`, `MILESTONE_NAME`,`CONSULTANT_EMAIL`

Key columns (internal projects): `ACCOUNT_NAME`, `PROJECT_ID`, `PROJECT_NAME`, `MILESTONE_ID`, `MILESTONE_NAME`

Email format: `firstname.lastname@snowflake.com` (NOT `ldap@snowflake.com`)

## Important

- Do NOT ask for input — run everything automatically.
- Do NOT hardcode project values — always query the Snowflake table.
- Do NOT write hook scripts or update hooks.json — install.sh handles that.
