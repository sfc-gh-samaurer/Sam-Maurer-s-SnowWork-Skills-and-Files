# SD Dashboard — Build Guide

A Streamlit app for Services Delivery Program Managers to track capacity contracts, use cases, active SD projects, PS&T pipeline, and generate AI-powered use case action plans. Built by Sam Maurer, Enterprise Expansion NW.

---

## Overview

**4 tabs:**
| Tab | Purpose |
|-----|---------|
| Capacity & Renewals | Active capacity contracts, overage/underage predictions, renewal pipeline |
| Use Cases | Full use case pipeline with filters, SFDC links, PS engagement flag |
| SD Projects | Active projects, expiring projects, open PS&T pipeline, historical sold services |
| Use Case Action Plan | AI-generated action plans per account using Cortex LLM |

**Tech stack:** Streamlit · Snowpark (via `st.connection`) · Snowflake Cortex (`SNOWFLAKE.CORTEX.COMPLETE`) · pandas · Python 3.11

---

## File Structure

```
account_dashboard/
├── streamlit_app.py              # Entry point — layout, tabs, global styles
├── data.py                       # All Snowflake queries, caching, helper utilities
├── app_pages/
│   ├── capacity_renewals.py      # Tab 1: Capacity & Renewals
│   ├── use_cases_tab.py          # Tab 2: Use Cases
│   ├── pst_tab.py                # Tab 3: SD Projects
│   └── action_planner_tab.py    # Tab 4: Use Case Action Plan
├── .streamlit/
│   ├── secrets.toml              # Snowflake connection credentials (local only)
│   └── config.toml               # Streamlit server config
├── snowflake.yml                 # Snowflake SiS deployment config
├── pyproject.toml                # Python dependencies
└── environment.yml               # Conda environment spec
```

---

## Prerequisites

### Snowflake Access
You need access to the following databases/schemas. All queries run under `ROLE = SALES_ENGINEER` with `USE SECONDARY ROLES ALL`.

| Database | Schema | Objects Used |
|----------|--------|--------------|
| `SALES` | `RAVEN` | `ACCOUNT`, `DD_SALESFORCE_ACCOUNT_A360`, `SDA_OPPORTUNITY_VIEW`, `SDA_OPPORTUNITY_PS_VIEW`, `A360_PRODUCT_CATEGORY_VIEW` |
| `SALES` | `SE_REPORTING` | `VIVUN_DELIVERABLE_USE_CASE` |
| `MDM` | `MDM_INTERFACES` | `DIM_USE_CASE` |
| `FIVETRAN` | `SALESFORCE` | `OPPORTUNITY`, `OPPORTUNITY_LINE_ITEM`, `PSE_PROJ_C`, `PSE_ASSIGNMENT_C`, `PSE_PRACTICE_C`, `CONTACT`, `USER`, `ACCOUNT` |

### Snowflake Connection
Locally, the app uses a named connection. Set up `~/.snowflake/connections.toml` with a connection named `snowhouse` (or update the name throughout).

Alternatively, configure `.streamlit/secrets.toml`:

```toml
[connections.snowflake]
account = "your_account"
user = "your_user"
authenticator = "externalbrowser"
warehouse = "SNOWADHOC"
role = "SALES_ENGINEER"
```

### Python Dependencies
```
streamlit>=1.40
snowflake-snowpark-python
pandas
```

---

## Setup & Running Locally

```bash
# Clone or copy the account_dashboard/ directory to your machine

# Run the app
SNOWFLAKE_CONNECTION_NAME=snowhouse python3 -m streamlit run streamlit_app.py \
  --server.port 8501 --server.headless true
```

Open `http://localhost:8501`.

> **Note:** The first load triggers `USE SECONDARY ROLES ALL` to ensure access to SALES.RAVEN tables. This requires the role `SALES_ENGINEER` to be granted to your user and secondary roles to be enabled.

---

## Adapting to Your Team

The DMs are hardcoded in `data.py`. To adapt for your territory, search and replace every occurrence of:

```python
'Erik Schneider', 'Raymond Navarro'
```

with your own DM names. These appear in all `WHERE` clauses across every `load_*` function.

For the Action Planner tab, also update the district filter in `action_planner_tab.py`:

```python
WHERE u.DISTRICT_C IN ('EntBayAreaTech1', 'EntPacNorthwest')
```

Replace with your Salesforce district values (from `FIVETRAN.SALESFORCE.USER.DISTRICT_C`).

---

## Architecture Notes

### Data Loading Pattern
All data functions live in `data.py` and are decorated with `@st.cache_data(ttl=86400)` (24hr cache). Tab files are loaded via `exec()` so they hot-reload without restarting the process. However, **`data.py` changes require a full process restart** (kill + relaunch) since it is an imported module.

### Session Init
`_init_session()` runs once per browser session and clears all caches on new load, ensuring fresh data on each visit.

### HTML Table Renderer
`render_html_table()` in `data.py` renders a custom HTML/JS table with:
- Clickable column-sort (ascending/descending)
- Fullscreen button
- Dollar, percent, date, number, and hyperlink formatters
- Snowflake blue styling

**Column spec format:**
```python
{"col": "COLUMN_NAME", "label": "Display Label", "fmt": "dollar"}
# fmt options: dollar | number | pct | decimal1 | date | link | text (default)
# For link columns: add "display_text": "Open" or "display_col": "COL_WITH_TEXT"
# Add "highlight": True for green-tinted column
```

---

## Tab Reference

### Tab 1 — Capacity & Renewals (`capacity_renewals.py`)

**Data functions:** `load_capacity_renewals()`, `load_capacity_pipeline()`

**Sections:**
1. **Active Capacity Contracts** — one row per account with contract dates, capacity purchased/used/remaining, overage/underage prediction, overage date. Filters: DM, AE, Total Capacity band, account search.
2. **Capacity Conversion Candidates** — auto-computed: accounts ending within 24mo with negative overage prediction (predicted underburn). SD opportunity to convert unused capacity into services.
3. **Capacity & Renewal Pipeline** — open Salesforce opportunities (renewals + expansion). Filters: DM, Opp Type, AE, Stage, Forecast, Close Date range, search.

**Key SQL tables:**
- `SALES.RAVEN.ACCOUNT` — account metadata, AE/DM assignment
- `SALES.RAVEN.DD_SALESFORCE_ACCOUNT_A360` — capacity contract data (purchased, remaining, predictions)
- `SALES.RAVEN.SDA_OPPORTUNITY_VIEW` — open opportunity pipeline

---

### Tab 2 — Use Cases (`use_cases_tab.py`)

**Data function:** `load_use_cases()`

**What it shows:** All active use cases (not lost) for the territory. Filters: Account, AE, Status, Stage, PS Engaged, search. KPIs: total UCs, In Pursuit count, Implementation count, Total EACV, Stuck >90 days.

**Key SQL table:** `MDM.MDM_INTERFACES.DIM_USE_CASE`

**Columns shown:** Account, Use Case name (with SFDC link), Status, EACV, Stage, Decision Date, Created, Modified, Days Since Modified, AE, Next Steps, PS Engaged.

---

### Tab 3 — SD Projects (`pst_tab.py`)

**Data functions:** `load_ps_projects_active()`, `load_ps_pipeline()`, `load_ps_history()`, `load_product_usage()`

**Sections:**

1. **Active SD Projects** — all active PSE projects tied to the territory. Filters: Account, Stage, Practice, DM, AE, Hide Past End Dates, search. Includes resources, PM, billing type, revenue, status notes.

2. **Expiring SD Projects — No Extension** — projects ending within N months (slider: 1-24mo) that have no later project with the same base name at the same account. Identifies renewal/extension opportunities.
   - Uses regex to normalize project names: strips "Year 2", "Yr3", "Phase 1", etc. before matching.

3. **SD Pipeline (Open Opportunities)** — open PS&T-tagged opportunities. Source: `SDA_OPPORTUNITY_VIEW` UNION ALL `FIVETRAN.SALESFORCE.OPPORTUNITY` (fallback for recently-created opps not yet in SDA view). Filters: Account, AE, Stage, Type, Forecast, search. Shows MEDDPICC score, PS TCV, Education TCV, forecast categories.

4. **Historical Sold Services & Training** — closed-won opportunities with Technical Services or Education Services line items. Filters: Account, DM, AE, Product Family, Opp Type, search. KPIs: count, PS $, Edu $, Total PST $.

**Product Usage expanders** appear inline in Active Projects and Pipeline sections — shows credit consumption by product category for the filtered accounts (last 3 months from `SALES.RAVEN.A360_PRODUCT_CATEGORY_VIEW`).

---

### Tab 4 — Use Case Action Plan (`action_planner_tab.py`)

**Data functions:** `load_action_planner_pipeline()`, `load_account_consumption_summary()`, `load_accounts_base()`, `load_capacity_renewals()`, `generate_cortex_response()`

**How it works:**
1. User selects a district and account from the left filter panel.
2. The app loads all active use cases for that account (sourced from `VIVUN_DELIVERABLE_USE_CASE` joined with `DIM_USE_CASE` for authoritative stage data).
3. User can check/uncheck individual use cases to include in the plan.
4. An optional free-text "SE Notes" field lets the SE add ad-hoc context.
5. Clicking **Generate** builds a detailed prompt and calls `SNOWFLAKE.CORTEX.COMPLETE(model, prompt)`.
6. The generated plan persists in `st.session_state` (survives widget interactions). Can be downloaded as `.md`.

**Prompt structure:**
The prompt instructs the LLM to act as an SD strategist writing a 2-minute AE-facing brief with 5 sections:
- **The Story** — account narrative grounded in use case data, ARR, capacity, consumption
- **What SD Can Do Here** — 2-4 strategic areas (not one per offering)
- **How [AE] Should Talk About This** — conversational talking points, no jargon
- **Recommended Play** — sequenced engagement recommendation
- **Next Steps** — 3-4 concrete actions with owners (AE/SE/SD)

**Context injected into prompt:**
- All use case fields: name, stage, EACV, workloads, description, technical UC, competitors, incumbent, implementer, next steps, risk, latest 3 SE comments
- Account context: ARR, tier, industry, contract end date, capacity remaining, overage prediction
- Consumption trends: last 6 months of credit usage by product category with trend direction
- SD offerings catalog: 12 offerings with descriptions (background context only — not a checklist)
- SE Notes (free text)

**Available models (SFCOGSOPS account):**
| Model | Notes |
|-------|-------|
| `claude-3-5-sonnet` | Default, best quality |
| `llama3.1-405b` | Good alternative |
| `mistral-large2` | Fast |
| `llama3.1-70b` | Lightweight |
| `mixtral-8x7b` | Lightweight |

> `claude-opus-4`, `claude-sonnet-4`, `snowflake-llama3.3-70b` are **not available** in this account.

**Data source for use cases:**
```sql
SELECT v.*, d.USE_CASE_STAGE, d.USE_CASE_STATUS, d.SE_COMMENTS
FROM SALES.SE_REPORTING.VIVUN_DELIVERABLE_USE_CASE v
JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON v.ACCOUNT_ID = a.ID
JOIN FIVETRAN.SALESFORCE.USER u ON a.OWNER_ID = u.ID
LEFT JOIN MDM.MDM_INTERFACES.DIM_USE_CASE d ON v.USE_CASE_NUMBER = d.USE_CASE_NUMBER
WHERE u.DISTRICT_C IN ('EntBayAreaTech1', 'EntPacNorthwest')
```
- Stage is sourced from `DIM_USE_CASE` first (authoritative), falling back to `VIVUN_DELIVERABLE_USE_CASE`
- SE Comments (with dates) come from `DIM_USE_CASE.SE_COMMENTS` — the planner extracts the latest 3 dated entries

---

## Snowflake SiS Deployment

To deploy to Snowsight (Streamlit in Snowflake):

```bash
/Library/Frameworks/Python.framework/Versions/3.11/bin/snow streamlit deploy \
  --replace \
  --connection snowhouse \
  --role SALES_ENGINEER
```

**Deployed URL:** `https://app.snowflake.com/SFCOGSOPS/snowhouse_aws_us_west_2/#/streamlit-apps/TEMP.SAMAURER.SD_ACCOUNT_DASHBOARD`

> **Known SiS limitation:** The app runs under a service account, not as the logged-in user. `USE SECONDARY ROLES ALL` only activates roles granted to the service account. If `SALES_ENGINEER` role lacks SELECT on `SALES.RAVEN.ACCOUNT`, an admin must run:
> ```sql
> GRANT ROLE SALES_RAVEN_RO_RL TO ROLE SALES_ENGINEER;
> ```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Data not refreshing | Click the **Refresh** button top-right, or restart the process |
| `data.py` changes not taking effect | Kill and relaunch the process — `data.py` is an imported module, not exec'd |
| "Invalid connection_name" error | Connection names are case-sensitive; use lowercase (e.g., `snowhouse`) |
| `SALES.RAVEN.ACCOUNT` access denied in SiS | Grant `SALES_RAVEN_RO_RL` to `SALES_ENGINEER` role (requires admin) |
| LLM model error in Action Planner | Model may not be available in your account — switch to `llama3.1-405b` |
| Tab file changes auto-reload | Yes — tab files use `exec()` and reload on each Streamlit rerun |
