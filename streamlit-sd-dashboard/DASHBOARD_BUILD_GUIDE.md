# Enterprise Expansion, Northwest — SD Dashboard: Setup & Build Guide

> Complete guide to set up, run, and understand the SD Account Dashboard. Source of truth is the GitHub repo. This document covers prerequisites, Snowflake connection setup, architecture, all data sources, and launch/auto-start instructions.

---

## Table of Contents

1. [Overview](#1-overview)
2. [File Structure](#2-file-structure)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
4. [Snowflake Connection & Permissions](#4-snowflake-connection--permissions)
5. [First-Time Setup](#5-first-time-setup)
6. [Running the App](#6-running-the-app)
7. [Auto-Start on Mac Login (launchd)](#7-auto-start-on-mac-login-launchd)
8. [Data Sources & Schema Reference](#8-data-sources--schema-reference)
9. [Architecture & Technical Design](#9-architecture--technical-design)
10. [Tab-by-Tab Feature Reference](#10-tab-by-tab-feature-reference)
11. [Styling & Branding](#11-styling--branding)
12. [Known Limitations](#12-known-limitations)

---

## 1. Overview

A **local Streamlit dashboard** for managing accounts owned by two District Managers: **Erik Schneider** (EntBayAreaTech1) and **Raymond Navarro** (EntPacNorthwest). Used by a Solutions Director (PM: Sam Maurer) to track capacity, renewals, use cases, professional services projects, and generate AI-powered SD action plans.

**Key characteristics:**
- 5 horizontal tabs via `st.tabs()`
- Snowflake brand styling (#29B5E8, #1E88E5, #11567F)
- SFDC hyperlinks to Account, Opportunity, and Use Case records
- Manual refresh button with 24-hour cache (`st.cache_data(ttl=86400)`)
- Custom HTML table renderer with client-side JavaScript sorting and fullscreen mode
- AI action plan generation via `SNOWFLAKE.CORTEX.COMPLETE()`
- Runs locally (not deployed to Snowflake Streamlit-in-Snowflake)

---

## 2. File Structure

```
streamlit-sd-dashboard/
├── streamlit_app.py              # Main app shell (5 tabs, header, refresh button)
├── data.py                       # All SQL queries, caching, HTML table renderer, Cortex
├── .streamlit/
│   ├── config.toml               # Snowflake brand theme
│   └── secrets.toml              # Snowflake connection config (create this — see below)
└── app_pages/
    ├── exec_summary_tab.py       # Tab 0: Executive Summary
    ├── capacity_renewals.py      # Tab 1: Capacity & Renewals
    ├── use_cases_tab.py          # Tab 2: Use Cases
    ├── pst_tab.py                # Tab 3: SD Projects
    └── action_planner_tab.py     # Tab 4: Use Case Action Plan (Cortex AI)
```

**How tabs load:** The main app uses `exec(f.read())` to load each tab file into the current Streamlit context. Tab files (`app_pages/*.py`) hot-reload on save. Changes to `data.py` require a full process restart.

---

## 3. Prerequisites & Environment Setup

### Python
- Python 3.11+

### Install Dependencies

```bash
pip install streamlit snowflake-snowpark-python pandas
```

Or using the included `pyproject.toml`:

```bash
pip install -e .
```

### Snowflake CLI Connection

You need a named connection in `~/.snowflake/connections.toml`. Use `externalbrowser` (SSO) authenticator:

```toml
[your-connection-name]
account = "<YOUR_SNOWFLAKE_ACCOUNT>"
user = "<YOUR_USERNAME>"
authenticator = "externalbrowser"
warehouse = "SNOWADHOC"
role = "SALES_ENGINEER"
```

> **Snowflake account for this deployment:** `SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2`  
> **Connection name used:** `sfcogsops-snowhouse_aws_us_west_2`

### Streamlit Secrets File

Create `.streamlit/secrets.toml` in the project directory (this file is gitignored — each user must create it locally):

```toml
[connections.snowflake]
connection_name = "your-connection-name"
```

Replace `your-connection-name` with your entry from `~/.snowflake/connections.toml`.

---

## 4. Snowflake Connection & Permissions

### Role & Warehouse
- **Role:** `SALES_ENGINEER`
- **Warehouse:** `SNOWADHOC`

### Critical Permission Detail
`SALES_ENGINEER` does **not** have direct access to `SALES.RAVEN` schema. Access comes through a secondary role (`SALES_BASIC_RO`). Every session must run:

```sql
USE SECONDARY ROLES ALL;
```

This is handled automatically in `data.py`'s `_get_session()`.

### Required Schema Access

| Schema | Access Method | Used For |
|--------|--------------|----------|
| `SALES.RAVEN` | Via secondary role | ACCOUNT, SDA_OPPORTUNITY_VIEW, SDA_OPPORTUNITY_PS_VIEW, DD_SALESFORCE_ACCOUNT_A360, BOB_CONTRACTS, A360_PRODUCT_CATEGORY_VIEW |
| `FIVETRAN.SALESFORCE` | Direct grant | PSE_PROJ_C, PSE_ASSIGNMENT_C, PSE_PRACTICE_C, CONTACT, OPPORTUNITY, OPPORTUNITY_LINE_ITEM, USER, ACCOUNT, CONTRACT |
| `MDM.MDM_INTERFACES` | Direct grant | DIM_USE_CASE |
| `SALES.SE_REPORTING` | Direct grant | VIVUN_DELIVERABLE_USE_CASE (Action Planner tab) |

### Why This App Runs Locally (Not Snowflake Streamlit-in-Snowflake)
SiS uses owner's rights mode, which does **not** support secondary roles. `SALES.RAVEN` is only accessible via `SALES_BASIC_RO` secondary role. To deploy to SiS, an admin would need to grant direct access:

```sql
GRANT USAGE ON SCHEMA SALES.RAVEN TO ROLE SALES_ENGINEER;
GRANT SELECT ON ALL TABLES IN SCHEMA SALES.RAVEN TO ROLE SALES_ENGINEER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SALES.RAVEN TO ROLE SALES_ENGINEER;
```

---

## 5. First-Time Setup

```bash
# 1. Clone the repo (or pull latest)
git clone <repo-url> streamlit-sd-dashboard
cd streamlit-sd-dashboard

# 2. Install dependencies
pip install streamlit snowflake-snowpark-python pandas

# 3. Create secrets.toml (NOT committed to git)
cat > .streamlit/secrets.toml << 'EOF'
[connections.snowflake]
connection_name = "your-connection-name"
EOF

# 4. Run the app
SNOWFLAKE_CONNECTION_NAME=your-connection-name python3 -m streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

Open `http://localhost:8501` in your browser. On first load, Snowflake will prompt for SSO authentication.

---

## 6. Running the App

### Standard Launch

```bash
SNOWFLAKE_CONNECTION_NAME=your-connection-name python3 -m streamlit run /path/to/streamlit-sd-dashboard/streamlit_app.py --server.port 8501 --server.headless true
```

### Restart After `data.py` Changes

Tab files hot-reload automatically. Core modules (`data.py`) require a restart:

```bash
pkill -f "streamlit run"
SNOWFLAKE_CONNECTION_NAME=your-connection-name python3 -m streamlit run /path/to/streamlit-sd-dashboard/streamlit_app.py --server.port 8501 --server.headless true
```

### Check Logs

```bash
tail -f /tmp/sd-dashboard.log   # if using launchd (see below)
```

---

## 7. Auto-Start on Mac Login (launchd)

To keep the app running persistently without CoCo or a terminal session, register it as a macOS launch agent. This auto-starts on login and restarts on crash.

### Create the plist

Save as `~/Library/LaunchAgents/com.<yourname>.sd-dashboard.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.<yourname>.sd-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>-m</string>
        <string>streamlit</string>
        <string>run</string>
        <string>/path/to/streamlit-sd-dashboard/streamlit_app.py</string>
        <string>--server.port</string>
        <string>8501</string>
        <string>--server.headless</string>
        <string>true</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>SNOWFLAKE_CONNECTION_NAME</key>
        <string>your-connection-name</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/sd-dashboard.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/sd-dashboard.log</string>
</dict>
</plist>
```

### Register & Manage

```bash
# Load (starts immediately + on every login)
launchctl load ~/Library/LaunchAgents/com.<yourname>.sd-dashboard.plist

# Stop
launchctl unload ~/Library/LaunchAgents/com.<yourname>.sd-dashboard.plist

# Start
launchctl load ~/Library/LaunchAgents/com.<yourname>.sd-dashboard.plist

# Verify running
launchctl list | grep sd-dashboard

# View logs
tail -f /tmp/sd-dashboard.log
```

---

## 8. Data Sources & Schema Reference

### Cached Query Functions in `data.py`

All functions use `@st.cache_data(ttl=86400)` (24-hour cache). Cleared via the Refresh button.

| Function | Purpose |
|----------|---------|
| `load_accounts_base()` | Active accounts for the two DMs (base list) |
| `load_capacity_renewals()` | Capacity contracts with BOB fallback + open renewal opp |
| `load_capacity_pipeline()` | All open opportunities for the territory |
| `load_use_cases()` | All non-lost use cases from MDM |
| `load_ps_projects_active()` | Active PS&T projects with resources and opportunity details |
| `load_ps_pipeline()` | Open PS/Education opps (SDA + Fivetran fallback merge) |
| `load_ps_history()` | Closed-won opps with PS/Education line items |
| `load_product_usage()` | Product category usage (last 3 months) |
| `load_action_planner_pipeline()` | Use cases from VIVUN + MDM join for Action Planner |
| `load_account_consumption_summary(name)` | Per-account 6-month credit consumption for Action Planner |
| `load_exec_software_renewals()` | Open renewal opps closing in next 6 months |
| `load_exec_services_renewals()` | Active PS projects ending in next 6 months |
| `load_exec_new_opps()` | Opportunities created in last N days |
| `load_exec_new_use_cases()` | Use cases created in last N days |
| `generate_cortex_response(prompt, model)` | Calls `SNOWFLAKE.CORTEX.COMPLETE()` for Action Planner |

### Key Data Source Behaviors

**`SDA_OPPORTUNITY_VIEW`** is a daily snapshot. Always filter with `DS = CURRENT_DATE()`. Reflects current DM assignments only — for historical data, use `FIVETRAN.SALESFORCE.OPPORTUNITY` directly.

**`load_capacity_renewals()` uses a 3-tier contract fallback:**
1. `DD_SALESFORCE_ACCOUNT_A360` (A360 capacity data — most accurate)
2. `BOB_CONTRACTS` (for accounts not in A360)
3. `FIVETRAN.SALESFORCE.CONTRACT` (last resort for accounts in neither)

Accounts are pre-filtered with `CAPACITY_COUNTER_C > 0` from `FIVETRAN.SALESFORCE.ACCOUNT`.

**`load_ps_pipeline()` merges two sources:**
- `SDA_OPPORTUNITY_VIEW` (primary — has MEDDPICC, SE Comments, forecast data)
- `FIVETRAN.SALESFORCE.OPPORTUNITY` (fallback for opps not yet in SDA snapshot)

**SFDC URL patterns:**
- Account: `https://snowforce.lightning.force.com/lightning/r/Account/{ID}/view`
- Opportunity: `https://snowforce.lightning.force.com/lightning/r/Opportunity/{ID}/view`
- Use Case: `https://snowforce.lightning.force.com/lightning/r/{USE_CASE_ID}/view`

### Territory Filter (hardcoded in all queries)
```sql
WHERE ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
AND ACCOUNT_STATUS_C = 'Active'
```

To adapt for a different territory, update these DM names across `data.py` and update the header in `streamlit_app.py`.

---

## 9. Architecture & Technical Design

### Connection Pattern

`data.py` connects via `st.connection("snowflake")` which reads from `.streamlit/secrets.toml`. On each session start, `_get_session()` sets role, warehouse, and secondary roles:

```python
def _get_session():
    session = st.connection("snowflake").session()
    session.sql(f"USE ROLE SALES_ENGINEER").collect()
    session.sql(f"USE WAREHOUSE SNOWADHOC").collect()
    session.sql("USE SECONDARY ROLES ALL").collect()
    return session
```

### HTML Table Renderer

Standard `st.dataframe()` doesn't support clickable SFDC links. `render_html_table(df, columns, height)` generates a full HTML document rendered in an isolated iframe via `st.components.v1.html()`. Features:
- Clickable SFDC links
- Client-side JavaScript column sorting (click any column header)
- **Fullscreen button** (⛶) on every table
- Sticky headers
- Custom cell formatting: `dollar`, `number`, `pct`, `date`, `link`, `decimal1`, `text`
- Column highlight support (green background via `"highlight": True`)
- `display_col` parameter: for link columns, use another column's value as link text

`columns` parameter format:
```python
[
    {"col": "DF_COLUMN", "label": "Header Text", "fmt": "dollar"},
    {"col": "URL_COL",   "label": "SFDC",        "fmt": "link", "display_col": "NAME_COL"},
    {"col": "NOTES_COL", "label": "Notes",        "highlight": True},
]
```

### Cortex AI (Action Planner)

`generate_cortex_response(prompt, model)` calls `SNOWFLAKE.CORTEX.COMPLETE()` directly via Snowpark:

```python
result = session.sql(
    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}') AS response"
).to_pandas()
```

Supported models (selectable in UI): `claude-3-5-sonnet`, `llama3.1-405b`, `mistral-large2`, `llama3.1-70b`, `mixtral-8x7b`.

### Decimal Type Fix
Snowpark returns numeric columns as Python `Decimal` objects, which Pandas can't chart or compare. `_fix_decimals(df)` converts these to `float`. All SQL queries also use explicit `CAST(... AS FLOAT)` to prevent this at the source.

### Cache Strategy
- All data queries: `@st.cache_data(ttl=86400)` (24 hours)
- Refresh button calls `clear_all_caches()` which calls `.clear()` on every cached function
- `_init_session()` calls `clear_all_caches()` once per app session (on first load) to ensure fresh data after overnight restarts

---

## 10. Tab-by-Tab Feature Reference

### Tab 0: Executive Summary
- **KPI bar:** SW Renewals (next 6mo), Svc Renewals (next 6mo), New Opps, New Use Cases, Conversion Candidates
- **Adjustable window:** Last 30 / 60 / 90 days for New Opps + New Use Cases
- **5 expandable sections:**
  - Upcoming Software Renewals (open renewal opps closing next 6mo)
  - Upcoming Services Renewals (active PS projects ending next 6mo)
  - New Opportunities (created in last N days)
  - New Use Cases (created in last N days)
  - Top Capacity Conversion Candidates (underburn accounts ending <24mo)

### Tab 1: Capacity & Renewals
- **Active Capacity Contracts table** — capacity metrics, overage/underage prediction, nearest open renewal opp
- Data source uses 3-tier fallback: A360 → BOB Contracts → SFDC Contract
- **Filters:** DM, AE, Total Capacity band, account search
- **KPIs:** Account count, Total Capacity $, Total Remaining $
- **Capacity Conversion Candidates expander:** accounts ending ≤18mo with `OVERAGE_UNDERAGE_PREDICTION < 0`
- **Capacity & Renewal Pipeline table** — all open opps
- **CSV export** for both tables

### Tab 2: Use Cases
- All non-lost use cases from `MDM.MDM_INTERFACES.DIM_USE_CASE`
- **Filters:** Account, AE, Status, Stage, PS Engaged (Yes/No), search
- **KPIs:** Total UCs, In Pursuit, Implementation, Total EACV, Stuck >90d
- Use Case # column links to SFDC record
- **CSV export**

### Tab 3: SD Projects
- **Top-level KPIs:** Active Projects, Active Revenue, Billable Hours, Pipeline Opps, Pipeline TCV, Stalled Projects
- **Active PS&T Projects** — filters: Account, Stage, Practice, DM, AE, search
- **Product Usage expander** (last 3 months) per account
- **PS&T Pipeline** — merges SDA + Fivetran opps, filters: Account, AE, Stage, Forecast, search
- **Historical Sold Services & Training** — closed-won opps with PS/Education line items
- **CSV export** for all three sections

### Tab 4: Use Case Action Plan (Cortex AI)
- **Left panel:** District / Stage / Account filters; shows account list with UC count + EACV when no account selected
- **Right panel (when account selected):**
  - 4 KPI metrics: AE, SE, Pipeline UCs, Pipeline EACV
  - Editable use case table with Select checkboxes (deselect UCs to exclude from plan)
  - Optional SE notes text area (free-form context to add to prompt)
  - Model selector (claude-3-5-sonnet default)
  - Generate button → calls `SNOWFLAKE.CORTEX.COMPLETE()`
  - Plan renders as markdown with structured sections: The Story → What SD Can Do Here → How AE Should Talk About This → Recommended Play → Next Steps
  - Download plan as `.md` file
  - Clear plan button

**Action Planner data sources:** Joins `VIVUN_DELIVERABLE_USE_CASE` + `DIM_USE_CASE` for full use case detail. Enriches prompt with account ARR/tier/capacity context and 6-month consumption trends by product category.

---

## 11. Styling & Branding

### Snowflake Brand Colors
- **Primary Blue:** `#29B5E8` (header bar, active tab underline)
- **Action Blue:** `#1E88E5` (links, interactive elements)
- **Dark Navy:** `#11567F` (headings, table header text, sort arrows)

### Global CSS (in `streamlit_app.py`)
- App background: `#f8fafc`
- Header bar: `#29B5E8`, height `2rem`
- Metric cards: white, `#e2e8f0` border, 8px radius
- Tab buttons: 16px, weight 600; active tab has 3px `#29B5E8` bottom border

### HTML Table CSS (in `render_html_table`)
- Font: Source Sans Pro, 13px body, 12px uppercase headers
- Header background: `#f1f5f9`, `#cbd5e1` bottom border
- Row hover: `#f0f9ff`
- Highlighted columns: header `#e6f4e6`, cells `#f0faf0`
- Sticky headers (z-index 1 normal, z-index 10 fullscreen)
- Max cell width: 350px with `word-wrap: break-word`

### Theme Config (`.streamlit/config.toml`)
```toml
[theme]
base = "light"
primaryColor = "#29B5E8"
backgroundColor = "#f8fafc"
secondaryBackgroundColor = "#e2e8f0"
textColor = "#11567F"
```

---

## 12. Known Limitations

- **Local only** — cannot deploy to Snowflake Streamlit-in-Snowflake without direct grants on `SALES.RAVEN` (see Section 4)
- **SSO re-authentication** — `externalbrowser` auth may prompt for SSO login on cache misses or after long idle periods; complete the browser popup to proceed
- **Tab 2 (Use Cases) `DECISION_DATE` column** — fetched from `DIM_USE_CASE` but not currently displayed in the table (available in the DataFrame if needed)
- **Action Planner SE Comments parsing** — parses `[MM/DD/YYYY]` date prefixes to extract latest comments; differently formatted comments fall back to raw text
- **`load_account_consumption_summary()`** — uses f-string SQL with account name interpolation; account names with single quotes are escaped (`replace("'", "''")`) but this is not a parameterized query
