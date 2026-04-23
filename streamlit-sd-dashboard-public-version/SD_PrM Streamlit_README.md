# SD Dashboard — Services Delivery

Streamlit app for the Snowflake Services Delivery team. Surfaces capacity contracts, renewals pipeline, use cases, active SD projects, and an AI-powered action plan generator across all districts.

---

## Prerequisites

- Python 3.11+
- Snowflake account: `SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2`
- Warehouse: `SNOWADHOC`
- Snowflake CLI configured (`snow connection list` should return a valid connection)
- A role with SELECT access on all required databases (see [Required Snowflake Access](#required-snowflake-access))

---

## File Structure

```
Streamlit SD Dashboard/
├── streamlit_app.py          # Entry point — layout, tabs, DM selector, styling
├── data.py                   # All Snowflake queries and shared utilities
├── app_pages/
│   ├── capacity_renewals.py  # Tab 1 — Capacity contracts & renewal pipeline
│   ├── use_cases_tab.py      # Tab 2 — Use case pipeline
│   ├── pst_tab.py            # Tab 3 — Active SD projects & pipeline
│   └── action_planner_tab.py # Tab 4 — AI action plan generator (Cortex)
├── snowflake.yml             # SiS deployment manifest
└── pyproject.toml            # Python dependencies
```

---

## Setup

### 1. Install dependencies

```bash
pip install streamlit "snowflake-snowpark-python[pandas]" snowflake-connector-python pandas
```

### 2. Configure Snowflake connection

Create `.streamlit/secrets.toml` in the project root:

```toml
[connections.snowflake]
account = "SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2"
user = "<YOUR_SNOWFLAKE_USERNAME>"
authenticator = "externalbrowser"
warehouse = "SNOWADHOC"
role = "<YOUR_ROLE_WITH_DATA_ACCESS>"
```

The role specified here must have SELECT on all tables listed in [Required Snowflake Access](#required-snowflake-access).

### 3. Run the app locally

```bash
SNOWFLAKE_CONNECTION_NAME=SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2 python3 -m streamlit run streamlit_app.py
```

### 4. Deploy to Snowflake (SiS)

```bash
snow streamlit deploy --replace --connection <connection_name>
```

After deployment, the app is available in Snowsight under **Projects > Streamlit**.

---

## Required Snowflake Access

The role configured for the app (locally in `secrets.toml`, or the deployment role in `snowflake.yml`) must have SELECT on:

| Database | Schema | Tables / Views |
|---|---|---|
| `SALES` | `RAVEN` | `ACCOUNT`, `SDA_OPPORTUNITY_VIEW`, `SDA_OPPORTUNITY_PS_VIEW`, `DD_SALESFORCE_ACCOUNT_A360`, `BOB_CONTRACTS`, `A360_PRODUCT_CATEGORY_VIEW` |
| `SALES` | `SE_REPORTING` | `VIVUN_DELIVERABLE_USE_CASE` |
| `FIVETRAN` | `SALESFORCE` | `ACCOUNT`, `USER`, `CONTRACT`, `OPPORTUNITY`, `OPPORTUNITY_LINE_ITEM`, `PSE_PROJ_C`, `PSE_ASSIGNMENT_C`, `PSE_PRACTICE_C`, `CONTACT` |
| `MDM` | `MDM_INTERFACES` | `DIM_USE_CASE` |

The role also needs USAGE on `SNOWFLAKE.CORTEX` for the AI action plan tab.

If any table is inaccessible, the relevant tab shows an empty state — other tabs are unaffected.

---

## Architecture

### Connection
The app uses `st.connection("snowflake").session()` exclusively. No runtime role switching (`USE ROLE`) occurs — the session runs under whichever role is configured in `secrets.toml` (local) or `snowflake.yml` (SiS deployment). Ensure that role has the access listed above before running.

### Tab loading
Each `app_pages/*.py` file exposes a `render(dms: tuple)` function. `streamlit_app.py` imports and calls each function directly — no `exec()` or file reads at runtime.

### DM filter
On load, `load_dm_list()` queries distinct DM values from `SALES.RAVEN.ACCOUNT`. A sidebar multiselect (default: all DMs) stores the selection in `st.session_state["selected_dms"]`, which is passed as a `dms` parameter to every data function.

### Caching
All data load functions use `@st.cache_data(ttl=86400)` (24-hour cache). The **Refresh** button in the header calls `clear_all_caches()` and reruns the app.

---

## Configuration

The only hardcoded value shared across tab files is the Salesforce base URL:

```python
SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"
```

All other filtering (DMs, stages, accounts, etc.) is dynamic via UI controls.

---

## Deployment (snowflake.yml)

```yaml
definition_version: 2
entities:
  sd_dashboard:
    type: streamlit
    identifier:
      name: SD_DASHBOARD
      database: <YOUR_DATABASE>
      schema: <YOUR_SCHEMA>
    query_warehouse: SNOWADHOC
    runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11
    external_access_integrations:
      - PYPI_ACCESS_INTEGRATION
    main_file: streamlit_app.py
    artifacts:
      - streamlit_app.py
      - data.py
      - pyproject.toml
      - app_pages/capacity_renewals.py
      - app_pages/use_cases_tab.py
      - app_pages/pst_tab.py
      - app_pages/action_planner_tab.py
```

The deployment role must have all grants listed in [Required Snowflake Access](#required-snowflake-access). No additional role switching is performed at runtime.

---

## Tabs

### Tab 1 — Capacity & Renewals
- **Active Capacity Contracts** — all accounts with active capacity, contract dates, usage, remaining capacity, overage/underage predictions
- **Capacity Conversion Candidates** — accounts ending within 24 months with predicted underburn (auto-surfaced)
- **Capacity & Renewal Pipeline** — open renewal and growth opportunities

Data functions: `load_capacity_renewals(dms)`, `load_capacity_pipeline(dms)`

### Tab 2 — Use Cases
- Full use case pipeline filtered by account, AE, status, stage, and PS engagement
- KPIs: total UCs, In Pursuit count, Implementation count, total EACV, stuck >90 days
- Sortable HTML table with SFDC links; CSV export

Data function: `load_use_cases(dms)`

### Tab 3 — SD Projects
- **Active SD Projects** — all in-progress Certinia PSA projects with resources, billing, revenue
- **Expiring SD Projects** — projects ending within N months with no detected follow-on project (configurable slider)
- **SD Pipeline** — open opportunities with PS/Education services line items
- **Historical Sold Services** — closed-won opportunities with PS/Education revenue
- **Product Usage expanders** — last-3-months credit usage by product category for accounts in each section

Data functions: `load_ps_projects_active(dms)`, `load_ps_pipeline(dms)`, `load_ps_history(dms)`, `load_product_usage(dms)`

### Tab 4 — Use Case Action Plan (AI)
- Select a DM and account → review pipeline use cases → generate an SD action plan via Cortex
- Filters: DM, stage, account search
- Uses `SNOWFLAKE.CORTEX.COMPLETE()` — model is selectable (default: `claude-3-5-sonnet`)
- Optional SE notes field to inject additional context into the prompt
- Output is formatted markdown; downloadable as `.md` file

Data functions: `load_action_planner_pipeline(dms)`, `generate_cortex_response()`, `load_account_consumption_summary()`, `load_accounts_base(dms)`, `load_capacity_renewals(dms)`

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Tab shows empty / "No data found" | Role lacks SELECT on that database | Grant the required role SELECT on the relevant tables (see Required Snowflake Access) |
| Cortex tab errors on generate | Role lacks USAGE on `SNOWFLAKE.CORTEX` | Grant `USAGE ON SNOWFLAKE.CORTEX` to the deployment role |
| App loads but data is stale | 24h cache hasn't expired | Click the **Refresh** button in the top-right header |
| DM list is empty | Role lacks access to `SALES.RAVEN.ACCOUNT` | Grant SELECT on `SALES.RAVEN.ACCOUNT` to the deployment role |
| `streamlit: command not found` | Streamlit not installed | `pip install streamlit` |
