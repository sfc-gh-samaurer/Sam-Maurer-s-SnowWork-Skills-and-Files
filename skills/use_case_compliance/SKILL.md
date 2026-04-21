---
name: use_case_compliance
description: PSA milestone data quality audit — identifies Professional Services milestones of type Use Case that are missing or have an invalid Salesforce use case ID, and generates a sortable HTML report. Triggers include PS milestone compliance, PSA use case linkage, missing use case ID on milestone, milestone use case validation, PS milestone audit, blank use case ID, invalid use case ID on PS milestone, PSA data quality, PS milestone data hygiene.
created_date: 2026-03-30
last_updated: "2026-04-02"

owner_name: Yuthika Agarwalla
version: 1.0.0
---

# Use Case Compliance

Monitors Professional Services milestone compliance by identifying milestones with type "Use Case" that are missing a valid Salesforce use case ID. A milestone is non-compliant if its `SALESFORCE_USE_CASE_ID` is blank (NULL or empty string) or contains an ID that does not exist in the canonical use case table. The report includes milestone ID, milestone name, project name, project manager, account name, milestone status, and the specific reason for non-compliance.

## Table of Contents

1. [When to Activate](#when-to-activate)
2. [Core Concepts](#core-concepts)
3. [Data Sources](#data-sources)
4. [Prerequisites](#prerequisites)
5. [Workflow](#workflow)
6. [Query Reference](#query-reference)
7. [Output Format](#output-format)
8. [Guidelines](#guidelines)
9. [Error Handling](#error-handling)
10. [References](#references)

## When to Activate

Activate this skill when the user is asking about **PSA / Professional Services milestone data quality** — specifically whether Use Case type milestones have a valid `SALESFORCE_USE_CASE_ID` linked.

> **Note:** This skill is distinct from `use_case_monitoring`, which tracks SE use case hygiene (MEDDPICC completeness, stage staleness, go-live consumption) in the sales pipeline. If the user mentions "my use cases" or "SE use case compliance", route to `use_case_monitoring` instead.

## Core Concepts

Professional Services milestones in Salesforce PSA can have a type of "Use Case". When a milestone is typed as "Use Case", it should be linked to a valid Salesforce use case record via the `SALESFORCE_USE_CASE_ID` field.

**Blank Use Case ID**: The milestone's `SALESFORCE_USE_CASE_ID` is NULL or an empty string. This means the PM has not linked the milestone to any use case record.

**Invalid Use Case ID**: The milestone's `SALESFORCE_USE_CASE_ID` contains a value, but that value does not match any `SALESFORCE_USE_CASE_ID` in the canonical use case table (`DD_SALESFORCE_USE_CASE`). This could indicate a deleted use case, a typo, or stale data.

**Active vs Inactive Projects**: The denormalized milestone table includes `IS_SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_ACTIVE` which indicates whether the parent project is currently active. The default query returns all non-compliant milestones but sorts active projects first, since those are most actionable.

## Data Sources

| Table | Description |
|---|---|
| `SNOW_CERTIFIED.PROFESSIONAL_SERVICES.DD_PROFESSIONAL_SERVICES_MILESTONE` | Denormalized milestone dimension with embedded project, opportunity, and account attributes. Contains `SALESFORCE_USE_CASE_ID` and `SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_TYPE` |
| `SNOW_CERTIFIED.SALESFORCE_USE_CASE.DD_SALESFORCE_USE_CASE` | Denormalized use case dimension. Used to validate that a milestone's use case ID references a real use case record |
| `SNOW_CERTIFIED.SALESFORCE_USER.DD_SALESFORCE_USER` | Salesforce user dimension. Joined on `SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_OWNER_ID` to resolve owner name, role, and email |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (for `uv run --script`)
- Snowflake connection named `default` configured in `~/.snowflake/connections.toml`
- Role `SD_USER_RO_RL` and warehouse `SNOWADHOC` are set automatically by the script

## Workflow

Generate the HTML dashboard report by running:

```bash
SNOWFLAKE_CONNECTION_NAME=default uv run --script <skill_dir>/scripts/generate_report.py --output ~/Desktop/use_case_compliance_report.html
```

This will:
1. Connect to Snowflake (opens browser for auth if needed)
2. Run the compliance query (all non-compliant milestones, active projects first)
3. Run the summary statistics query
4. Generate a self-contained HTML file at `output/use_case_compliance_report.html`
5. Print the file path — open it in a browser to view

Optional flags:
- `--output /path/to/report.html` — custom output location
- `--dump-json /path/to/data.json` — save intermediate query results as JSON

To re-render from cached JSON (no Snowflake connection needed):

```bash
python3 <skill_dir>/scripts/render_report.py --data /path/to/data.json
```

## Query Reference

### Query 1: Use Case Compliance (All Non-Compliant Milestones)

Returns all milestones of type "Use Case" where the use case ID is either blank or does not match any record in the use case table. Results are sorted with active projects first, then alphabetically by project name and milestone name.

```sql
USE ROLE SD_USER_RO_RL;
USE WAREHOUSE SNOWADHOC;

SELECT
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_ID AS milestone_id,
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_NAME AS milestone_name,
    m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_NAME AS project_name,
    m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_MANAGER_NAME AS project_manager,
    u.SALESFORCE_USER_NAME AS owner_name,
    u.SALESFORCE_USER_ROLE_NAME AS owner_role,
    u.SALESFORCE_USER_EMAIL AS owner_email,
    m.SALESFORCE_ACCOUNT_NAME AS account_name,
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_STATUS AS milestone_status,
    m.SALESFORCE_USE_CASE_ID AS use_case_id,
    m.IS_SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_ACTIVE AS is_project_active,
    CASE
        WHEN m.SALESFORCE_USE_CASE_ID IS NULL OR TRIM(m.SALESFORCE_USE_CASE_ID) = '' THEN 'Blank Use Case ID'
        WHEN uc.SALESFORCE_USE_CASE_ID IS NULL THEN 'Invalid Use Case ID'
    END AS reason
FROM SNOW_CERTIFIED.PROFESSIONAL_SERVICES.DD_PROFESSIONAL_SERVICES_MILESTONE m
LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USE_CASE.DD_SALESFORCE_USE_CASE uc
    ON uc.SALESFORCE_USE_CASE_ID = m.SALESFORCE_USE_CASE_ID
LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USER.DD_SALESFORCE_USER u
    ON u.SALESFORCE_USER_ID = m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_OWNER_ID
WHERE m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_TYPE = 'Use Case'
  AND (
      m.SALESFORCE_USE_CASE_ID IS NULL
      OR TRIM(m.SALESFORCE_USE_CASE_ID) = ''
      OR uc.SALESFORCE_USE_CASE_ID IS NULL
  )
ORDER BY
    m.IS_SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_ACTIVE DESC,
    m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_NAME,
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_NAME;
```

### Query 2: Active Projects Only

Same logic scoped to active projects for immediate action.

```sql
USE ROLE SD_USER_RO_RL;
USE WAREHOUSE SNOWADHOC;

SELECT
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_ID AS milestone_id,
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_NAME AS milestone_name,
    m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_NAME AS project_name,
    m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_MANAGER_NAME AS project_manager,
    m.SALESFORCE_USE_CASE_ID AS use_case_id,
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_STATUS AS milestone_status,
    m.SALESFORCE_ACCOUNT_NAME AS account_name,
    CASE
        WHEN m.SALESFORCE_USE_CASE_ID IS NULL OR TRIM(m.SALESFORCE_USE_CASE_ID) = '' THEN 'Blank Use Case ID'
        WHEN uc.SALESFORCE_USE_CASE_ID IS NULL THEN 'Invalid Use Case ID'
    END AS reason
FROM SNOW_CERTIFIED.PROFESSIONAL_SERVICES.DD_PROFESSIONAL_SERVICES_MILESTONE m
LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USE_CASE.DD_SALESFORCE_USE_CASE uc
    ON uc.SALESFORCE_USE_CASE_ID = m.SALESFORCE_USE_CASE_ID
WHERE m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_TYPE = 'Use Case'
  AND m.IS_SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_ACTIVE = TRUE
  AND (
      m.SALESFORCE_USE_CASE_ID IS NULL
      OR TRIM(m.SALESFORCE_USE_CASE_ID) = ''
      OR uc.SALESFORCE_USE_CASE_ID IS NULL
  )
ORDER BY
    m.SALESFORCE_PROFESSIONAL_SERVICES_PROJECT_NAME,
    m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_NAME;
```

### Query 3: Summary Statistics

Blank and invalid counts across all "Use Case" milestones (used to seed KPI cards).

```sql
USE ROLE SD_USER_RO_RL;
USE WAREHOUSE SNOWADHOC;

SELECT
    SUM(CASE WHEN m.SALESFORCE_USE_CASE_ID IS NULL OR TRIM(m.SALESFORCE_USE_CASE_ID) = '' THEN 1 ELSE 0 END) AS blank_use_case_id,
    SUM(CASE WHEN m.SALESFORCE_USE_CASE_ID IS NOT NULL AND TRIM(m.SALESFORCE_USE_CASE_ID) != '' AND uc.SALESFORCE_USE_CASE_ID IS NULL THEN 1 ELSE 0 END) AS invalid_use_case_id
FROM SNOW_CERTIFIED.PROFESSIONAL_SERVICES.DD_PROFESSIONAL_SERVICES_MILESTONE m
LEFT JOIN SNOW_CERTIFIED.SALESFORCE_USE_CASE.DD_SALESFORCE_USE_CASE uc
    ON uc.SALESFORCE_USE_CASE_ID = m.SALESFORCE_USE_CASE_ID
WHERE m.SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_TYPE = 'Use Case';
```

## Output Format

The report is a self-contained HTML file with a single table showing all non-compliant milestones:

| Column | Description |
|---|---|
| Milestone ID | Salesforce ID of the PS milestone |
| Milestone Name | Human-readable milestone name |
| Project Name | Parent project name (denormalized) |
| Project Manager | Project manager name (denormalized) |
| Owner Name | Milestone owner name (from `DD_SALESFORCE_USER` via owner ID) |
| Owner Role | Milestone owner's Salesforce role name |
| Owner Email | Milestone owner's email address |
| Account Name | Customer account name (denormalized) |
| Milestone Status | Current milestone status (In Progress, Completed, Planned, etc.) |
| Use Case ID | The use case ID value (blank or invalid) |
| Reason | "Blank Use Case ID" or "Invalid Use Case ID" |
| Active Project | Whether the parent project is active (True/False) |

Features:
- KPI bar: Non-Compliant count, Blank ID count, Invalid ID count (updates dynamically with PM filter)
- PM filter dropdown — filter by project manager name
- Dark/light theme toggle
- Sortable columns (click any header)
- Active projects shown first, with True/False color-coded

## Guidelines

1. The milestone type filter is exact match: `'Use Case'` (case-sensitive). Other milestone types like "Fixed Fee - upon milestone completion" or "Time_and_Materials" are not checked.
2. Active projects are prioritized in the sort order because they represent actionable issues. Inactive project milestones are included for completeness but are less urgent.
3. The `DD_PROFESSIONAL_SERVICES_MILESTONE` table is denormalized — project name, project manager, account name, and other attributes are embedded directly. The only additional join needed is `DD_SALESFORCE_USER` for owner name, role, and email via `SALESFORCE_PROFESSIONAL_SERVICES_MILESTONE_OWNER_ID`.
4. The validation join uses `DD_SALESFORCE_USE_CASE` as the source of truth for valid use case IDs.

## Error Handling

| Situation | Action |
|---|---|
| "Table does not exist" or access denied | Verify role is set to SD_USER_RO_RL |
| No results returned | All "Use Case" milestones have valid use case IDs — full compliance |
| Authentication failure | Ensure `default` connection is configured in `~/.snowflake/connections.toml` |
| `uv` not found | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

## References

### Internal

- [CHANGELOG.md](CHANGELOG.md) — Version history
- [generate_report.py](scripts/generate_report.py) — PEP 723 script; connects to Snowflake, runs queries, generates HTML report
- [render_report.py](scripts/render_report.py) — Offline re-render from cached JSON; no Snowflake connection required
- [_report_utils.py](scripts/_report_utils.py) — Shared HTML rendering utilities (`_esc`, `build_table_rows`, `build_html`)
- `output/` — Generated HTML reports; git-ignored via `output/.gitignore`
