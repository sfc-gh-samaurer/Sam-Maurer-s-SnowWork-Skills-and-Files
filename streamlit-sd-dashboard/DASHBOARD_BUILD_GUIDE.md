# Enterprise Expansion, Northwest - SD Dashboard: Complete Build Guide

> This document contains everything needed to recreate the SD Account Dashboard from scratch. It includes architecture, Snowflake connection setup, all SQL queries, complete source code for every file, styling details, technical decisions/gotchas, and launch instructions.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture & File Structure](#2-architecture--file-structure)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
4. [Snowflake Connection & Permissions](#4-snowflake-connection--permissions)
5. [Data Sources & Schema Reference](#5-data-sources--schema-reference)
6. [Technical Design Decisions & Gotchas](#6-technical-design-decisions--gotchas)
7. [Source Code - Core Modules](#7-source-code---core-modules)
8. [Source Code - Tab Pages](#8-source-code---tab-pages)
9. [Tab-by-Tab Feature Reference](#9-tab-by-tab-feature-reference)
10. [Styling & Branding](#10-styling--branding)
11. [Launch Instructions](#11-launch-instructions)
12. [Known Limitations & Deferred Items](#12-known-limitations--deferred-items)

---

## 1. Overview

A **local Streamlit dashboard** for managing accounts owned by two District Managers (DMs): **Erik Schneider** (EntBayAreaTech1) and **Raymond Navarro** (EntPacNorthwest). The dashboard is used by a Solutions Director (PM: Sam Maurer) to track capacity, renewals, use cases, professional services projects, and to maintain project management notes.

**Key characteristics:**
- 5 horizontal tabs via `st.tabs()`
- Snowflake brand styling (#29B5E8, #1E88E5, #11567F)
- SFDC hyperlinks to Account, Opportunity, and Use Case records
- Manual refresh button with 24-hour cache (`st.cache_data(ttl=86400)`)
- Local SQLite database for project management notes (date-stamped)
- Custom HTML table renderer with client-side JavaScript sorting
- Runs locally (not deployed to Snowflake Streamlit-in-Snowflake)

---

## 2. Architecture & File Structure

```
~/account_dashboard/
├── streamlit_app.py              # Main app shell (5 tabs, header, refresh)
├── data.py                       # All SQL queries, caching, HTML table renderer
├── pm_db.py                      # SQLite persistence for PM notes
├── pm_notes.db                   # SQLite database file (auto-created)
├── .streamlit/
│   └── secrets.toml              # Snowflake connection config
└── app_pages/
    ├── capacity_renewals.py      # Tab 1: Capacity & Renewals
    ├── use_cases_tab.py          # Tab 2: Use Cases
    ├── pst_tab.py                # Tab 3: SD Projects
    ├── sd_opp_generator.py       # Tab 4: SD Opp Generator
    └── pm_tab.py                 # Tab 5: Project Management
```

**How tabs load:** The main app uses `exec()` to load each tab file's content into the current Streamlit context. This means tab files reload automatically on save, but changes to `data.py` or `pm_db.py` require a full process restart (`pkill -f "streamlit run"` then relaunch).

---

## 3. Prerequisites & Environment Setup

### Python Dependencies
- Python 3.11+
- `streamlit` (tested with 1.38+)
- `snowflake-snowpark-python`
- `pandas`

### Snowflake CLI Connection
You need a named connection in `~/.snowflake/connections.toml`:

```toml
[snowhouse]
account = "<YOUR_SNOWFLAKE_ACCOUNT>"
user = "<YOUR_USERNAME>"
authenticator = "externalbrowser"
warehouse = "SNOWADHOC"
role = "SALES_ENGINEER"
```

### Streamlit Secrets File
Create `~/account_dashboard/.streamlit/secrets.toml`:

```toml
[connections.snowflake]
connection_name = "snowhouse"
```

This tells `st.connection("snowflake")` which named connection to use.

---

## 4. Snowflake Connection & Permissions

### Role & Warehouse
- **Role:** `SALES_ENGINEER`
- **Warehouse:** `SNOWADHOC`

### Critical Permission Detail
`SALES_ENGINEER` does **not** have direct access to `SALES.RAVEN` schema. Access comes through a secondary role (`SALES_BASIC_RO`). Every Snowflake session must run:

```sql
USE SECONDARY ROLES ALL;
```

This is handled automatically in `data.py`'s `_get_session()` function.

### Required Schema Access

| Schema | Access Method | Tables/Views Used |
|--------|--------------|-------------------|
| `SALES.RAVEN` | Via secondary role | ACCOUNT, SDA_OPPORTUNITY_VIEW, SDA_OPPORTUNITY_PS_VIEW, DD_SALESFORCE_ACCOUNT_A360, A360_PRODUCT_CATEGORY_VIEW |
| `FIVETRAN.SALESFORCE` | Direct grant | PSE_PROJ_C, PSE_ASSIGNMENT_C, PSE_PRACTICE_C, CONTACT, OPPORTUNITY, OPPORTUNITY_LINE_ITEM, USER |
| `MDM.MDM_INTERFACES` | Direct grant | DIM_USE_CASE |

---

## 5. Data Sources & Schema Reference

### Key Data Source Behaviors

**`SDA_OPPORTUNITY_VIEW`** is a daily snapshot table. You must filter with `DS = CURRENT_DATE()` to get today's snapshot. This view only reflects **current** DM assignments -- if an account was reassigned, historical opps under the old DM won't appear. For historical closed-won data, use `FIVETRAN.SALESFORCE.OPPORTUNITY` directly.

**`ACCOUNT` table key columns:**
- `ACCOUNT_OWNER_NAME` = AE name
- `ACCOUNT_OWNER_MANAGER_C` = DM name
- `SUBINDUSTRY` (not `ACCOUNT_SUB_INDUSTRY`)
- `TIER_C` = account tier
- `LEAD_SALES_ENGINEER_NAME_C` = lead SE

**SFDC URL patterns:**
- Account: `https://snowforce.lightning.force.com/lightning/r/Account/{SALESFORCE_ACCOUNT_ID}/view`
- Opportunity: `https://snowforce.lightning.force.com/lightning/r/Opportunity/{OPPORTUNITY_ID}/view`
- Use Case: `https://snowforce.lightning.force.com/lightning/r/{USE_CASE_ID}/view`

### All SQL Queries

There are 9 cached query functions in `data.py`. Each uses `@st.cache_data(ttl=86400)` (24-hour cache). All numeric columns use `CAST(... AS FLOAT)` to avoid Python `Decimal` type issues. A `_fix_decimals()` helper catches any remaining Decimal values.

The queries and their purposes:

1. **`load_accounts_base()`** - Base account list for PM tab
2. **`load_capacity_renewals()`** - Accounts with capacity contracts + nearest open renewal (3-CTE join)
3. **`load_capacity_pipeline()`** - All open opportunities for capacity/renewal pipeline
4. **`load_use_cases()`** - All active use cases from MDM
5. **`load_ps_projects_active()`** - Active PS&T projects with assignments, resources, opportunity details
6. **`load_ps_pipeline()`** - Open opportunities with PS/Education services TCV
7. **`load_ps_opportunity_scores()`** - Computed in Python (not SQL) - PS opportunity scoring algorithm
8. **`load_ps_history()`** - Historical closed-won PS/Education services from `FIVETRAN.SALESFORCE.OPPORTUNITY`
9. **`load_product_usage()`** - Product category usage (last 3 months)

---

## 6. Technical Design Decisions & Gotchas

### HTML Table Renderer
Standard `st.dataframe()` doesn't support SFDC hyperlinks or custom formatting well. Instead, a custom `render_html_table()` function generates a full HTML document rendered via `st.components.v1.html()` in an isolated iframe. This gives:
- Clickable SFDC links
- Client-side JavaScript column sorting
- Sticky headers
- Custom cell formatting (dollar, number, pct, date, link, decimal1)
- Column highlight support (green background via `"highlight": True`)

The `columns` parameter is a list of dicts with keys:
- `col`: DataFrame column name
- `label`: display header text
- `fmt`: one of `"dollar"`, `"number"`, `"pct"`, `"progress"`, `"date"`, `"link"`, `"decimal1"`, `"text"` (default)
- `display_text`: for link columns, static text to show (default "Open")
- `display_col`: for link columns, a DataFrame column whose value becomes the link text
- `highlight`: boolean, if True applies green highlight CSS to the column

### PS Opportunity Scoring Algorithm
A weighted composite score per account combining:
- **Contract urgency (35pts):** Linear scale based on days to contract end (<=365 days)
- **EACV of non-PS use cases (40pts):** Normalized against max EACV across all accounts
- **UC count without PS (25pts):** Normalized against max UC count

Only accounts with score > 0 are shown, sorted descending.

### SQLite for PM Notes
Uses Python's built-in `sqlite3` module. WAL journal mode for concurrent reads. Stored at `~/account_dashboard/pm_notes.db`. Date-stamp logic: when saving notes, each line that doesn't already start with `[20` gets `[YYYY-MM-DD] ` prepended.

### Tab Loading via exec()
Tab files are loaded via `exec(f.read())` which means they share the main app's namespace. File path resolution uses `os.path.dirname(os.path.abspath(__file__))` in the main app.

---

## 7. Source Code - Core Modules

### `streamlit_app.py`

```python
import streamlit as st
from data import clear_all_caches, _init_session
from datetime import datetime
import os

_APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Enterprise Expansion, Northwest - SD Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_init_session()

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
    [data-testid="stHeader"] { background-color: #29B5E8; height: 2rem; }
    .block-container { padding-top: 2.5rem; padding-bottom: 0rem; }
    h1, h2, h3 { color: #11567F; }
    div[data-testid="stTabs"] button { font-size: 16px; font-weight: 600; }
    div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom: 3px solid #29B5E8; color: #11567F; }
    .stDataFrame { border-radius: 8px; }
    div[data-testid="stMetric"] { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; }
</style>
""", unsafe_allow_html=True)

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown("## :material/dashboard: Enterprise Expansion, Northwest - SD Dashboard")
    st.caption("DMs: Erik Schneider, EntBayAreaTech1 & Raymond Navarro, EntPacNorthwest — PM: Sam Maurer")
with header_right:
    col_ts, col_btn = st.columns([2, 1])
    with col_ts:
        if "last_refresh" not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%b %d, %Y %I:%M %p')}")
    with col_btn:
        if st.button(":material/refresh: Refresh", type="primary", use_container_width=True):
            clear_all_caches()
            st.session_state.last_refresh = datetime.now()
            st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    ":material/trending_up: Capacity & Renewals",
    ":material/rocket_launch: Use Cases",
    ":material/support_agent: SD Projects",
    ":material/military_tech: SD Opp Generator",
    ":material/task_alt: Project Management",
])

with tab1:
    with open(os.path.join(_APP_DIR, "app_pages/capacity_renewals.py")) as f:
        exec(f.read())

with tab2:
    with open(os.path.join(_APP_DIR, "app_pages/use_cases_tab.py")) as f:
        exec(f.read())

with tab3:
    with open(os.path.join(_APP_DIR, "app_pages/pst_tab.py")) as f:
        exec(f.read())

with tab4:
    with open(os.path.join(_APP_DIR, "app_pages/sd_opp_generator.py")) as f:
        exec(f.read())

with tab5:
    with open(os.path.join(_APP_DIR, "app_pages/pm_tab.py")) as f:
        exec(f.read())
```

### `data.py`

```python
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from decimal import Decimal
import html as html_mod

_ROLE = "SALES_ENGINEER"
_WAREHOUSE = "SNOWADHOC"


def _get_session():
    session = st.connection("snowflake").session()
    session.sql("USE SECONDARY ROLES ALL").collect()
    return session


def _init_session():
    pass


def _fix_decimals(df):
    for col in df.columns:
        if df[col].dtype == object and len(df) > 0 and isinstance(df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None, Decimal):
            df[col] = df[col].astype(float)
    return df


def render_html_table(df, columns, height=500):
    """Render a DataFrame as a scrollable HTML table with text wrapping.

    columns: list of dicts with keys:
        - col: DataFrame column name
        - label: display header
        - fmt: "dollar" | "number" | "pct" | "progress" | "date" | "link" | "text" (default)
        - display_text: for link columns, static text to show (default "Open")
    """
    def fmt_cell(val, spec, row=None):
        if pd.isna(val) or val is None:
            return ""
        f = spec.get("fmt", "text")
        if f == "link":
            dt = spec.get("display_text", "Open")
            display_col = spec.get("display_col")
            if display_col and row is not None:
                dt_val = row.get(display_col)
                if pd.notna(dt_val) and dt_val:
                    dt = str(dt_val)
            return f'<a href="{html_mod.escape(str(val))}" target="_blank" style="color:#1E88E5;text-decoration:none;">{html_mod.escape(dt)}</a>'
        if f == "dollar":
            try:
                return f"${float(val):,.0f}"
            except (ValueError, TypeError):
                return html_mod.escape(str(val))
        if f in ("pct", "progress"):
            try:
                return f"{float(val):.0f}%"
            except (ValueError, TypeError):
                return html_mod.escape(str(val))
        if f == "number":
            try:
                return f"{float(val):,.0f}"
            except (ValueError, TypeError):
                return html_mod.escape(str(val))
        if f == "decimal1":
            try:
                return f"{float(val):.1f}"
            except (ValueError, TypeError):
                return html_mod.escape(str(val))
        if f == "date":
            try:
                if hasattr(val, 'strftime'):
                    return val.strftime('%m/%d/%Y')
                s = str(val)
                return s[:10] if len(s) >= 10 else s
            except Exception:
                return html_mod.escape(str(val))
        return html_mod.escape(str(val))

    headers = "".join(
        f'<th class="{"hl" if c.get("highlight") else ""}" onclick="sortTable({i})">'
        f'{html_mod.escape(c["label"])} <span class="sort-arrow" id="arrow_{i}">⇅</span></th>'
        for i, c in enumerate(columns)
    )
    col_types = []
    for c in columns:
        f = c.get("fmt", "text")
        if f in ("dollar", "number", "pct", "progress", "decimal1"):
            col_types.append("num")
        elif f == "date":
            col_types.append("date")
        else:
            col_types.append("str")

    def _raw_val(v):
        try:
            if pd.isna(v):
                return ""
        except (ValueError, TypeError):
            pass
        return html_mod.escape(str(v)).replace('"', '&quot;') if v is not None else ""

    rows_html = []
    for _, row in df.iterrows():
        cells = "".join(
            f'<td class="{"hl" if c.get("highlight") else ""}" data-val="{_raw_val(row.get(c["col"]))}">'
            f'{fmt_cell(row.get(c["col"]), c, row)}</td>' for c in columns
        )
        rows_html.append(f"<tr>{cells}</tr>")

    col_types_js = str(col_types).replace("'", '"')
    table_html = f"""
    <html><head><style>
    body {{ margin:0;padding:0;font-family:'Source Sans Pro',sans-serif; }}
    table {{ width:100%;border-collapse:collapse;font-size:13px; }}
    th {{
        padding:8px 10px;text-align:left;font-weight:600;color:#11567F;
        white-space:nowrap;font-size:12px;text-transform:uppercase;
        background:#f1f5f9;position:sticky;top:0;z-index:1;
        border-bottom:2px solid #cbd5e1;user-select:none;cursor:pointer;
    }}
    th:hover {{ background:#e2e8f0; }}
    th .sort-arrow {{ font-size:10px;color:#94a3b8;margin-left:2px; }}
    td {{
        padding:6px 10px;border-bottom:1px solid #f1f5f9;
        white-space:normal;word-wrap:break-word;overflow-wrap:break-word;
        max-width:350px;line-height:1.4;vertical-align:top;
    }}
    tr:hover {{ background-color:#f0f9ff; }}
    a {{ color:#1E88E5;text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    th.hl {{ background:#e6f4e6; }}
    td.hl {{ background:#f0faf0; }}
    </style></head><body>
    <table>
    <thead><tr>{headers}</tr></thead>
    <tbody>{"".join(rows_html)}</tbody>
    </table>
    <script>
    var sortDir = {{}};
    var colTypes = {col_types_js};
    function sortTable(colIdx) {{
        var tbody = document.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var asc = !sortDir[colIdx];
        sortDir = {{}};
        sortDir[colIdx] = asc;
        var ctype = colTypes[colIdx];
        rows.sort(function(a, b) {{
            var av = a.cells[colIdx].getAttribute('data-val') || '';
            var bv = b.cells[colIdx].getAttribute('data-val') || '';
            if (ctype === 'num') {{
                var an = parseFloat(av.replace(/[$,%]/g, '')) || 0;
                var bn = parseFloat(bv.replace(/[$,%]/g, '')) || 0;
                return asc ? an - bn : bn - an;
            }}
            if (ctype === 'date') {{
                var ad = new Date(av) || 0;
                var bd = new Date(bv) || 0;
                return asc ? ad - bd : bd - ad;
            }}
            return asc ? av.localeCompare(bv) : bv.localeCompare(av);
        }});
        rows.forEach(function(r) {{ tbody.appendChild(r); }});
        var arrows = document.querySelectorAll('.sort-arrow');
        arrows.forEach(function(a) {{ a.textContent = '\\u21C5'; a.style.color = '#94a3b8'; }});
        var arrow = document.getElementById('arrow_' + colIdx);
        if (arrow) {{
            arrow.textContent = asc ? '\\u2191' : '\\u2193';
            arrow.style.color = '#11567F';
        }}
    }}
    </script>
    </body></html>
    """
    components.html(table_html, height=height, scrolling=True)


def clear_all_caches():
    load_capacity_renewals.clear()
    load_capacity_pipeline.clear()
    load_use_cases.clear()
    load_ps_projects_active.clear()
    load_ps_pipeline.clear()
    load_accounts_base.clear()
    load_product_usage.clear()
    load_ps_opportunity_scores.clear()
    load_ps_history.clear()


@st.cache_data(ttl=86400)
def load_accounts_base():
    session = _get_session()
    df = session.sql("""
        SELECT
            NAME AS ACCOUNT_NAME,
            SALESFORCE_ACCOUNT_ID,
            ACCOUNT_OWNER_NAME AS ACCOUNT_OWNER,
            ACCOUNT_OWNER_MANAGER_C AS DM,
            CAST(ARR_C AS FLOAT) AS ARR,
            INDUSTRY,
            SUBINDUSTRY,
            TIER_C AS TIER,
            LEAD_SALES_ENGINEER_NAME_C AS LEAD_SE
        FROM SALES.RAVEN.ACCOUNT
        WHERE ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND ACCOUNT_STATUS_C = 'Active'
        ORDER BY ARR_C DESC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_capacity_renewals():
    session = _get_session()
    df = session.sql("""
        WITH base AS (
            SELECT
                a.NAME AS ACCOUNT_NAME,
                a.SALESFORCE_ACCOUNT_ID,
                a.ACCOUNT_OWNER_NAME AS ACCOUNT_OWNER,
                a.ACCOUNT_OWNER_MANAGER_C AS DM,
                CAST(a.ARR_C AS FLOAT) AS ARR,
                a.TIER_C AS TIER,
                a.LEAD_SALES_ENGINEER_NAME_C AS LEAD_SE
            FROM SALES.RAVEN.ACCOUNT a
            WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
            AND a.ACCOUNT_STATUS_C = 'Active'
        ),
        capacity AS (
            SELECT
                a3.SALESFORCE_ACCOUNT_ID,
                CAST(SUM(a3.CAPACITY_PURCHASED) AS FLOAT) AS CAPACITY_PURCHASED,
                CAST(SUM(a3.TOTAL_CAPACITY) AS FLOAT) AS TOTAL_CAPACITY,
                CAST(SUM(a3.TOTAL_CAPACITY) - SUM(a3.CAPACITY_USAGE_REMAINING) AS FLOAT) AS CAPACITY_USED,
                CAST(SUM(a3.CAPACITY_USAGE_REMAINING) AS FLOAT) AS CAPACITY_REMAINING,
                CAST(SUM(a3.OVERAGE_UNDERAGE_PREDICTION) AS FLOAT) AS OVERAGE_UNDERAGE_PREDICTION,
                MIN(a3.CONTRACT_START_DATE) AS CONTRACT_START_DATE,
                MAX(a3.CONTRACT_END_DATE) AS CONTRACT_END_DATE
            FROM SALES.RAVEN.DD_SALESFORCE_ACCOUNT_A360 a3
            WHERE a3.SALESFORCE_ACCOUNT_ID IN (
                SELECT SALESFORCE_ACCOUNT_ID FROM SALES.RAVEN.ACCOUNT
                WHERE ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
                AND ACCOUNT_STATUS_C = 'Active'
            )
            AND a3.CAPACITY_PURCHASED > 0
            GROUP BY a3.SALESFORCE_ACCOUNT_ID
        ),
        renewals AS (
            SELECT
                o.SALESFORCE_ACCOUNT_ID,
                o.OPPORTUNITY_NAME AS RENEWAL_OPP_NAME,
                o.OPPORTUNITY_ID AS RENEWAL_OPP_ID,
                o.STAGE_NAME AS RENEWAL_OPP_STAGE,
                o.FORECAST_STATUS AS RENEWAL_FORECAST_STATUS,
                CAST(o.TOTAL_ACV AS FLOAT) AS RENEWAL_OPP_ACV,
                o.CLOSE_DATE AS RENEWAL_CLOSE_DATE,
                o.NEXT_STEPS AS RENEWAL_NEXT_STEPS,
                ROW_NUMBER() OVER (PARTITION BY o.SALESFORCE_ACCOUNT_ID ORDER BY o.CLOSE_DATE ASC) AS rn
            FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
            WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
            AND o.DS = CURRENT_DATE()
            AND o.OPPORTUNITY_TYPE = 'Renewal'
            AND o.IS_OPEN = 1
        )
        SELECT
            b.ACCOUNT_NAME,
            b.SALESFORCE_ACCOUNT_ID,
            b.ACCOUNT_OWNER,
            b.DM,
            b.ARR,
            b.TIER,
            b.LEAD_SE,
            cap.CONTRACT_START_DATE,
            cap.CONTRACT_END_DATE,
            cap.CAPACITY_PURCHASED,
            cap.TOTAL_CAPACITY,
            cap.CAPACITY_USED,
            cap.CAPACITY_REMAINING,
            cap.OVERAGE_UNDERAGE_PREDICTION,
            r.RENEWAL_OPP_NAME,
            r.RENEWAL_OPP_ID,
            r.RENEWAL_OPP_STAGE,
            r.RENEWAL_FORECAST_STATUS,
            r.RENEWAL_OPP_ACV,
            r.RENEWAL_CLOSE_DATE,
            r.RENEWAL_NEXT_STEPS
        FROM base b
        LEFT JOIN capacity cap ON b.SALESFORCE_ACCOUNT_ID = cap.SALESFORCE_ACCOUNT_ID
        LEFT JOIN renewals r ON b.SALESFORCE_ACCOUNT_ID = r.SALESFORCE_ACCOUNT_ID AND r.rn = 1
        ORDER BY cap.OVERAGE_UNDERAGE_PREDICTION ASC NULLS LAST
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_capacity_pipeline():
    session = _get_session()
    df = session.sql("""
        SELECT
            o.ACCOUNT_NAME,
            o.SALESFORCE_ACCOUNT_ID,
            o.OPPORTUNITY_NAME,
            o.OPPORTUNITY_ID,
            o.OPPORTUNITY_TYPE,
            o.STAGE_NAME,
            o.FORECAST_STATUS,
            CAST(o.TOTAL_ACV AS FLOAT) AS TOTAL_ACV,
            CAST(o.RENEWAL_ACV AS FLOAT) AS RENEWAL_ACV,
            CAST(o.GROWTH_ACV AS FLOAT) AS GROWTH_ACV,
            CAST(o.TCV AS FLOAT) AS TCV,
            o.CLOSE_DATE,
            o.FISCAL_QUARTER,
            o.DAYS_IN_STAGE,
            o.OPPORTUNITY_OWNER_NAME AS OWNER,
            o.SE_COMMENTS,
            o.NEXT_STEPS,
            o.DM
        FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
        WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
        AND o.DS = CURRENT_DATE()
        AND o.IS_OPEN = 1
        AND o.IS_CLOSED = FALSE
        ORDER BY o.CLOSE_DATE ASC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_use_cases():
    session = _get_session()
    df = session.sql("""
        SELECT
            uc.ACCOUNT_NAME,
            uc.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
            uc.USE_CASE_NAME,
            uc.USE_CASE_STATUS,
            CAST(uc.USE_CASE_EACV AS FLOAT) AS ACV,
            uc.USE_CASE_STAGE AS STAGE,
            uc.CREATED_DATE,
            uc.LAST_MODIFIED_DATE,
            uc.DAYS_IN_STAGE,
            uc.OWNER_NAME AS OWNER,
            uc.NEXT_STEPS,
            uc.IS_PS_ENGAGED,
            uc.PS_ENGAGEMENT,
            uc.PS_DESCRIPTION,
            uc.ACCOUNT_DM AS DM,
            uc.ACCOUNT_SUB_INDUSTRY,
            uc.COMPETITORS,
            uc.MISSION_CRITICAL,
            uc.TECHNICAL_USE_CASE,
            uc.USE_CASE_ID,
            uc.USE_CASE_NUMBER
        FROM MDM.MDM_INTERFACES.DIM_USE_CASE uc
        WHERE uc.ACCOUNT_DM IN ('Erik Schneider', 'Raymond Navarro')
        AND uc.USE_CASE_STAGE IS NOT NULL
        AND uc.IS_LOST = FALSE
        ORDER BY uc.DAYS_IN_STAGE DESC NULLS LAST
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_projects_active():
    session = _get_session()
    df = session.sql("""
        WITH assignments AS (
            SELECT
                asgn.PSE_PROJECT_C AS PROJECT_ID,
                COUNT(asgn.ID) AS ASSIGNMENT_COUNT,
                LISTAGG(DISTINCT r.NAME, ', ') WITHIN GROUP (ORDER BY r.NAME) AS RESOURCES,
                LISTAGG(DISTINCT asgn.PSE_ROLE_C, ', ') WITHIN GROUP (ORDER BY asgn.PSE_ROLE_C) AS ROLES
            FROM FIVETRAN.SALESFORCE.PSE_ASSIGNMENT_C asgn
            LEFT JOIN FIVETRAN.SALESFORCE.CONTACT r ON asgn.PSE_RESOURCE_C = r.ID
            WHERE asgn.IS_DELETED = FALSE
            GROUP BY asgn.PSE_PROJECT_C
        )
        SELECT
            p.NAME AS PROJECT_NAME,
            p.ID AS PROJECT_ID,
            a.NAME AS ACCOUNT_NAME,
            a.SALESFORCE_ACCOUNT_ID,
            p.PSE_PROJECT_STATUS_C AS PROJECT_STATUS,
            p.PSE_STAGE_C AS PROJECT_STAGE,
            pr.NAME AS PRACTICE,
            p.SERVICE_TYPE_C AS SERVICE_TYPE,
            p.PSE_BILLING_TYPE_C AS BILLING_TYPE,
            p.PROJECT_SKU_TYPE_C AS SKU_TYPE,
            p.INVESTMENT_TYPE_C AS INVESTMENT_TYPE,
            p.PSE_START_DATE_C AS START_DATE,
            p.PSE_END_DATE_C AS END_DATE,
            CAST(p.PSE_PLANNED_HOURS_C AS FLOAT) AS PLANNED_HOURS,
            CAST(p.PSE_BILLABLE_INTERNAL_HOURS_C AS FLOAT) AS BILLABLE_HOURS,
            CAST(p.PSE_PERCENT_HOURS_COMPLETE_C AS FLOAT) AS PCT_HOURS_COMPLETE,
            CAST(p.PROJECT_REVENUE_AMOUNT_C AS FLOAT) AS REVENUE_AMOUNT,
            p.ENGAGEMENT_MODEL_C AS ENGAGEMENT_MODEL,
            p.DELIVERY_MANAGER_ENGAGEMENT_C AS DELIVERY_MANAGER,
            p.SUB_AGREEMENT_TYPE_C AS AGREEMENT_TYPE,
            p.CHANNEL_TYPE_C AS CHANNEL_TYPE,
            p.PSE_PROJECT_STATUS_NOTES_C AS STATUS_NOTES,
            p.PRODUCT_TECHNOLOGY_STATUS_C AS PRODUCT_TECH_STATUS,
            p.PSE_OPPORTUNITY_C AS OPPORTUNITY_ID,
            c.NAME AS PROJECT_MANAGER,
            COALESCE(asn.ASSIGNMENT_COUNT, 0) AS ASSIGNMENT_COUNT,
            asn.RESOURCES AS ASSIGNED_RESOURCES,
            asn.ROLES AS ASSIGNED_ROLES,
            ps.PS_SELLER_NAME,
            ps.PS_FORECAST_CATEGORY,
            ps.PS_COMMENTS,
            ps.OPPORTUNITY_USE_CASES,
            ps.IS_PS_CROSS_SELL,
            ps.ETL_TOOL,
            ps.BI_TOOL,
            ps.DW_TOOL,
            o.OPPORTUNITY_NAME,
            o.STAGE_NAME AS OPP_STAGE,
            o.FISCAL_QUARTER,
            o.OPPORTUNITY_OWNER_NAME AS OPP_OWNER,
            a.ACCOUNT_OWNER_MANAGER_C AS DM,
            a.ACCOUNT_OWNER_NAME AS AE
        FROM FIVETRAN.SALESFORCE.PSE_PROJ_C p
        JOIN SALES.RAVEN.ACCOUNT a ON p.PSE_ACCOUNT_C = a.SALESFORCE_ACCOUNT_ID
        LEFT JOIN FIVETRAN.SALESFORCE.PSE_PRACTICE_C pr ON p.PSE_PRACTICE_C = pr.ID
        LEFT JOIN FIVETRAN.SALESFORCE.CONTACT c ON p.PSE_PROJECT_MANAGER_C = c.ID
        LEFT JOIN assignments asn ON p.ID = asn.PROJECT_ID
        LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_PS_VIEW ps ON p.PSE_OPPORTUNITY_C = ps.OPPORTUNITY_ID
        LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_VIEW o ON p.PSE_OPPORTUNITY_C = o.OPPORTUNITY_ID AND o.DS = CURRENT_DATE()
        WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS_C = 'Active'
        AND p.IS_DELETED = FALSE
        AND p.PSE_IS_ACTIVE_C = TRUE
        AND p.PSE_STAGE_C IN ('In Progress', 'Stalled', 'Stalled - Expiring', 'Pipeline', 'Out Year')
        ORDER BY a.NAME, p.NAME
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_pipeline():
    session = _get_session()
    df = session.sql("""
        WITH products AS (
            SELECT
                oli.OPPORTUNITY_ID,
                LISTAGG(DISTINCT oli.OPPORTUNITY_PRODUCT_NAME_C, ', ') WITHIN GROUP (ORDER BY oli.OPPORTUNITY_PRODUCT_NAME_C) AS PRODUCT_NAMES
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY_LINE_ITEM oli
            WHERE oli.IS_DELETED = FALSE
            AND oli.OPPORTUNITY_PRODUCT_NAME_C IS NOT NULL
            GROUP BY oli.OPPORTUNITY_ID
        )
        SELECT
            o.ACCOUNT_NAME,
            o.SALESFORCE_ACCOUNT_ID,
            o.OPPORTUNITY_NAME,
            o.OPPORTUNITY_ID,
            ps.PS_SERVICE_TYPE,
            ps.PS_SELLER_NAME,
            ps.PS_INVESTMENT_TYPE,
            CAST(ps.PS_SERVICES_TCV AS FLOAT) AS PS_SERVICES_TCV,
            CAST(ps.EDUCATION_SERVICES_TCV AS FLOAT) AS EDUCATION_SERVICES_TCV,
            CAST(ps.PS_SERVICES_TCV AS FLOAT) + CAST(ps.EDUCATION_SERVICES_TCV AS FLOAT) AS TOTAL_PST_TCV,
            CAST(ps.PS_SERVICES_FORECAST AS FLOAT) AS PS_SERVICES_FORECAST,
            CAST(ps.EDUCATION_SERVICES_FORECAST AS FLOAT) AS EDUCATION_SERVICES_FORECAST,
            ps.PS_FORECAST_CATEGORY,
            ps.QUOTE_SUB_AGREEMENT_TYPE,
            o.STAGE_NAME,
            o.CREATED_DATE,
            o.CLOSE_DATE,
            o.DAYS_IN_STAGE,
            o.FISCAL_QUARTER,
            o.FORECAST_STATUS,
            o.OPPORTUNITY_OWNER_NAME AS OWNER,
            o.DM,
            CAST(o.OPP_PROBABILITY AS FLOAT) AS OPP_PROBABILITY,
            CAST(o.MEDDPICC_OVERALL_SCORE AS FLOAT) AS MEDDPICC_SCORE,
            o.SALES_QUALIFIED_DATE,
            pr.PRODUCT_NAMES
        FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
        JOIN SALES.RAVEN.SDA_OPPORTUNITY_PS_VIEW ps ON o.OPPORTUNITY_ID = ps.OPPORTUNITY_ID
        LEFT JOIN products pr ON o.OPPORTUNITY_ID = pr.OPPORTUNITY_ID
        WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
        AND o.DS = CURRENT_DATE()
        AND o.IS_OPEN = 1
        AND o.IS_CLOSED = FALSE
        AND (ps.PS_SERVICES_TCV > 0 OR ps.EDUCATION_SERVICES_TCV > 0
             OR ps.PS_SERVICES_FORECAST > 0 OR ps.EDUCATION_SERVICES_FORECAST > 0)
        ORDER BY o.CLOSE_DATE ASC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_opportunity_scores():
    cap_df = load_capacity_renewals()
    uc_df = load_use_cases()
    today = pd.Timestamp.now().normalize()

    target_ucs = uc_df[
        (uc_df["USE_CASE_STATUS"].isin(["In Pursuit", "Implementation"]))
        & (uc_df["IS_PS_ENGAGED"] == False)
    ].copy()

    uc_agg = target_ucs.groupby("SALESFORCE_ACCOUNT_ID").agg(
        UC_COUNT_NO_PS=("USE_CASE_NAME", "count"),
        EACV_NO_PS=("ACV", "sum"),
    ).reset_index()

    all_target = uc_df[uc_df["USE_CASE_STATUS"].isin(["In Pursuit", "Implementation"])].copy()
    uc_total = all_target.groupby("SALESFORCE_ACCOUNT_ID").agg(
        UC_COUNT_TOTAL=("USE_CASE_NAME", "count"),
    ).reset_index()

    scores = cap_df[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                      "CONTRACT_START_DATE", "CONTRACT_END_DATE", "TOTAL_CAPACITY",
                      "OVERAGE_UNDERAGE_PREDICTION"]].copy()

    scores = scores.merge(uc_agg, on="SALESFORCE_ACCOUNT_ID", how="left")
    scores = scores.merge(uc_total, on="SALESFORCE_ACCOUNT_ID", how="left")
    scores["UC_COUNT_NO_PS"] = scores["UC_COUNT_NO_PS"].fillna(0).astype(int)
    scores["EACV_NO_PS"] = scores["EACV_NO_PS"].fillna(0)
    scores["UC_COUNT_TOTAL"] = scores["UC_COUNT_TOTAL"].fillna(0).astype(int)

    scores["CONTRACT_START_DATE"] = pd.to_datetime(scores["CONTRACT_START_DATE"])
    scores["CONTRACT_END_DATE"] = pd.to_datetime(scores["CONTRACT_END_DATE"])
    scores["DAYS_TO_END"] = (scores["CONTRACT_END_DATE"] - today).dt.days

    max_eacv = scores["EACV_NO_PS"].max()
    max_uc = scores["UC_COUNT_NO_PS"].max()

    def calc_score(row):
        s = 0.0
        days = row["DAYS_TO_END"]
        if pd.notna(days) and 0 < days <= 365:
            s += 35 * (1 - days / 365)
        if max_eacv > 0:
            s += 40 * (row["EACV_NO_PS"] / max_eacv)
        if max_uc > 0:
            s += 25 * (row["UC_COUNT_NO_PS"] / max_uc)
        return round(s, 1)

    scores["PS_OPP_SCORE"] = scores.apply(calc_score, axis=1)
    scores = scores[scores["PS_OPP_SCORE"] > 0].sort_values("PS_OPP_SCORE", ascending=False)
    return scores


@st.cache_data(ttl=86400)
def load_ps_history():
    session = _get_session()
    df = session.sql("""
        WITH opp_ps_summary AS (
            SELECT
                oli.OPPORTUNITY_ID,
                CAST(SUM(CASE WHEN oli.PRODUCT_FAMILY_C = 'Technical Services' THEN oli.TOTAL_PRICE ELSE 0 END) AS FLOAT) AS PS_SERVICES_ACV,
                CAST(SUM(CASE WHEN oli.PRODUCT_FAMILY_C = 'Education Services' THEN oli.TOTAL_PRICE ELSE 0 END) AS FLOAT) AS EDU_SERVICES_ACV,
                CAST(SUM(oli.TOTAL_PRICE) AS FLOAT) AS TOTAL_PST_AMOUNT,
                LISTAGG(DISTINCT oli.PRODUCT_FAMILY_C, ', ') WITHIN GROUP (ORDER BY oli.PRODUCT_FAMILY_C) AS PRODUCT_FAMILIES
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY_LINE_ITEM oli
            WHERE oli.IS_DELETED = FALSE
            AND oli.PRODUCT_FAMILY_C IN ('Education Services', 'Technical Services')
            GROUP BY oli.OPPORTUNITY_ID
        )
        SELECT
            a.NAME AS ACCOUNT_NAME,
            opp.NAME AS OPPORTUNITY_NAME,
            opp.ID AS OPPORTUNITY_ID,
            a.ACCOUNT_OWNER_MANAGER_C AS DM,
            a.ACCOUNT_OWNER_NAME AS AE,
            u.NAME AS OPP_OWNER,
            opp.STAGE_NAME,
            opp.TYPE AS OPPORTUNITY_TYPE,
            opp.CLOSE_DATE,
            ps_view.PS_SERVICE_TYPE,
            ps_view.PS_INVESTMENT_TYPE,
            CAST(ps_view.PS_INVESTMENT_AMOUNT_USD AS FLOAT) AS PS_INVESTMENT_AMOUNT,
            ps_view.PS_SELLER_NAME,
            ops.PS_SERVICES_ACV,
            ops.EDU_SERVICES_ACV,
            ops.TOTAL_PST_AMOUNT,
            ops.PRODUCT_FAMILIES
        FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
        JOIN SALES.RAVEN.ACCOUNT a ON opp.ACCOUNT_ID = a.SALESFORCE_ACCOUNT_ID
        JOIN opp_ps_summary ops ON opp.ID = ops.OPPORTUNITY_ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
        LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_PS_VIEW ps_view ON opp.ID = ps_view.OPPORTUNITY_ID
        WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS_C = 'Active'
        AND opp.IS_WON = TRUE
        AND opp.IS_DELETED = FALSE
        ORDER BY opp.CLOSE_DATE DESC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_product_usage():
    session = _get_session()
    df = session.sql("""
        SELECT
            p.SALESFORCE_ACCOUNT_ID,
            p.SALESFORCE_ACCOUNT_NAME AS ACCOUNT_NAME,
            p.PRODUCT_CATEGORY,
            p.USE_CASE,
            p.PRIMARY_FEATURE,
            CAST(SUM(p.TOTAL_CREDITS) AS FLOAT) AS TOTAL_CREDITS,
            CAST(SUM(p.TOTAL_JOBS) AS FLOAT) AS TOTAL_JOBS
        FROM SALES.RAVEN.A360_PRODUCT_CATEGORY_VIEW p
        WHERE p.SALESFORCE_ACCOUNT_ID IN (
            SELECT SALESFORCE_ACCOUNT_ID
            FROM SALES.RAVEN.ACCOUNT
            WHERE ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
            AND ACCOUNT_STATUS_C = 'Active'
        )
        AND p.MONTH >= DATEADD(MONTH, -3, CURRENT_DATE())
        GROUP BY p.SALESFORCE_ACCOUNT_ID, p.SALESFORCE_ACCOUNT_NAME,
                 p.PRODUCT_CATEGORY, p.USE_CASE, p.PRIMARY_FEATURE
        HAVING SUM(p.TOTAL_CREDITS) > 0
        ORDER BY p.SALESFORCE_ACCOUNT_NAME, SUM(p.TOTAL_CREDITS) DESC
    """).to_pandas()
    return _fix_decimals(df)
```

### `pm_db.py`

```python
import sqlite3
import os
from datetime import datetime

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pm_notes.db")


def _get_conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS pm_entries (
            entity_type TEXT NOT NULL,
            entity_key TEXT NOT NULL,
            notes_next_steps TEXT DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (entity_type, entity_key)
        );
    """)
    conn.commit()
    conn.close()


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_entry(entity_type, entity_key):
    conn = _get_conn()
    row = conn.execute(
        "SELECT notes_next_steps, updated_at FROM pm_entries WHERE entity_type = ? AND entity_key = ?",
        (entity_type, entity_key),
    ).fetchone()
    conn.close()
    if row:
        return {"notes_next_steps": row["notes_next_steps"], "updated_at": row["updated_at"]}
    return None


def save_entry(entity_type, entity_key, notes_next_steps):
    stamp = datetime.now().strftime("[%Y-%m-%d] ")
    lines = notes_next_steps.strip().splitlines()
    stamped = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("[20"):
            stamped.append(stamp + stripped)
        else:
            stamped.append(line)
    notes_next_steps = "\n".join(stamped)
    conn = _get_conn()
    conn.execute(
        "INSERT INTO pm_entries (entity_type, entity_key, notes_next_steps, updated_at) VALUES (?,?,?,?) "
        "ON CONFLICT(entity_type, entity_key) DO UPDATE SET notes_next_steps = excluded.notes_next_steps, updated_at = excluded.updated_at",
        (entity_type, entity_key, notes_next_steps, _now()),
    )
    conn.commit()
    conn.close()


def get_all_entries(entity_type=None):
    conn = _get_conn()
    q = "SELECT * FROM pm_entries WHERE 1=1"
    params = []
    if entity_type:
        q += " AND entity_type = ?"
        params.append(entity_type)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return {(r["entity_type"], r["entity_key"]): {"notes_next_steps": r["notes_next_steps"], "updated_at": r["updated_at"]} for r in rows}


init_db()
```

### `.streamlit/secrets.toml`

```toml
[connections.snowflake]
connection_name = "snowhouse"
```

---

## 8. Source Code - Tab Pages

### `app_pages/capacity_renewals.py` (Tab 1)

```python
import streamlit as st
import pandas as pd
from datetime import datetime
from data import load_capacity_renewals, load_capacity_pipeline, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

df = load_capacity_renewals()
cap_pipe_df = load_capacity_pipeline()

today = pd.Timestamp.now().normalize()

# --- FILTERS ---
st.markdown("### :material/table_chart: Active Capacity Contracts")

if not df.empty:
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        dm_filter = st.multiselect("DM", options=sorted(df["DM"].dropna().unique()), default=[], key="cap_dm")
    with fc2:
        ae_filter = st.multiselect("AE", options=sorted(df["ACCOUNT_OWNER"].dropna().unique()), default=[], key="cap_ae")
    with fc3:
        cap_filter = st.multiselect("Total Capacity", options=["$0 (No Contract)", "< $1M", "$1M - $5M", "$5M - $10M", "> $10M"], default=[], key="cap_band")
    with fc4:
        search = st.text_input("Search account", "", key="cap_search")

    filtered = df.copy()
    if dm_filter:
        filtered = filtered[filtered["DM"].isin(dm_filter)]
    if ae_filter:
        filtered = filtered[filtered["ACCOUNT_OWNER"].isin(ae_filter)]
    if cap_filter:
        cap_masks = []
        if "$0 (No Contract)" in cap_filter:
            cap_masks.append(filtered["TOTAL_CAPACITY"].fillna(0) == 0)
        if "< $1M" in cap_filter:
            cap_masks.append((filtered["TOTAL_CAPACITY"].fillna(0) > 0) & (filtered["TOTAL_CAPACITY"].fillna(0) < 1_000_000))
        if "$1M - $5M" in cap_filter:
            cap_masks.append((filtered["TOTAL_CAPACITY"].fillna(0) >= 1_000_000) & (filtered["TOTAL_CAPACITY"].fillna(0) < 5_000_000))
        if "$5M - $10M" in cap_filter:
            cap_masks.append((filtered["TOTAL_CAPACITY"].fillna(0) >= 5_000_000) & (filtered["TOTAL_CAPACITY"].fillna(0) < 10_000_000))
        if "> $10M" in cap_filter:
            cap_masks.append(filtered["TOTAL_CAPACITY"].fillna(0) >= 10_000_000)
        if cap_masks:
            combined_cap = cap_masks[0]
            for m in cap_masks[1:]:
                combined_cap = combined_cap | m
            filtered = filtered[combined_cap]
    if search:
        filtered = filtered[filtered["ACCOUNT_NAME"].str.contains(search, case=False, na=False)]

    def sfdc_account_link(name, sfdc_id):
        if pd.notna(sfdc_id) and sfdc_id:
            return f"{SFDC_BASE}/Account/{sfdc_id}/view"
        return None

    display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                        "LEAD_SE",
                        "CONTRACT_START_DATE", "CONTRACT_END_DATE",
                        "CAPACITY_PURCHASED", "TOTAL_CAPACITY", "CAPACITY_USED", "CAPACITY_REMAINING",
                        "OVERAGE_UNDERAGE_PREDICTION"]].copy()

    display["ACCOUNT_LINK"] = display.apply(lambda r: sfdc_account_link(r["ACCOUNT_NAME"], r["SALESFORCE_ACCOUNT_ID"]), axis=1)

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Accounts", len(filtered))
    with kpi2:
        total_cap = filtered["TOTAL_CAPACITY"].sum()
        st.metric("Total Capacity", f"${total_cap:,.0f}")
    with kpi3:
        remaining = filtered["CAPACITY_REMAINING"].sum()
        st.metric("Total Remaining", f"${remaining:,.0f}")

    render_html_table(display, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "ACCOUNT_LINK", "label": "SFDC", "fmt": "link"},
        {"col": "ACCOUNT_OWNER", "label": "AE"},
        {"col": "DM", "label": "DM"},
        {"col": "LEAD_SE", "label": "Lead SE"},
        {"col": "CONTRACT_START_DATE", "label": "Start", "fmt": "date"},
        {"col": "CONTRACT_END_DATE", "label": "End", "fmt": "date"},
        {"col": "CAPACITY_PURCHASED", "label": "Cap Purch", "fmt": "dollar"},
        {"col": "TOTAL_CAPACITY", "label": "Total Cap", "fmt": "dollar"},
        {"col": "CAPACITY_USED", "label": "Cap Used", "fmt": "dollar"},
        {"col": "CAPACITY_REMAINING", "label": "Cap Remain", "fmt": "dollar"},
        {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Over/Under", "fmt": "dollar"},
    ], height=600)

    csv = filtered.to_csv(index=False)
    st.download_button(":material/download: Export CSV", csv, "capacity_contracts.csv", "text/csv", key="cap_csv")

    candidates = filtered[
        (filtered["CONTRACT_END_DATE"].notna())
    ].copy()
    candidates["DAYS_LEFT"] = (pd.to_datetime(candidates["CONTRACT_END_DATE"]) - today).dt.days
    candidates["PCT_REMAINING"] = (candidates["CAPACITY_REMAINING"] / candidates["TOTAL_CAPACITY"] * 100).round(1)
    candidates = candidates[
        (candidates["DAYS_LEFT"] <= 548)
        & (candidates["DAYS_LEFT"] > 0)
        & (candidates["OVERAGE_UNDERAGE_PREDICTION"] < 0)
    ].sort_values("OVERAGE_UNDERAGE_PREDICTION", ascending=True)

    if not candidates.empty:
        with st.expander(f":material/swap_horiz: **Capacity Conversion Candidates** — {len(candidates)} accounts ending within 18mo with predicted underburn", expanded=True):
            st.caption("These accounts are predicted to have significant unused capacity at contract end — consider converting remaining capacity into services contracts.")
            conv_display = candidates[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                                       "CONTRACT_END_DATE", "DAYS_LEFT", "TOTAL_CAPACITY",
                                       "CAPACITY_REMAINING", "PCT_REMAINING",
                                       "OVERAGE_UNDERAGE_PREDICTION"]].copy()
            conv_display["ACCOUNT_LINK"] = conv_display.apply(
                lambda r: f'{SFDC_BASE}/Account/{r["SALESFORCE_ACCOUNT_ID"]}/view' if pd.notna(r.get("SALESFORCE_ACCOUNT_ID")) else None, axis=1)
            render_html_table(conv_display, columns=[
                {"col": "ACCOUNT_NAME", "label": "Account"},
                {"col": "ACCOUNT_LINK", "label": "SFDC", "fmt": "link"},
                {"col": "ACCOUNT_OWNER", "label": "AE"},
                {"col": "DM", "label": "DM"},
                {"col": "CONTRACT_END_DATE", "label": "End Date", "fmt": "date"},
                {"col": "DAYS_LEFT", "label": "Days Left", "fmt": "number"},
                {"col": "TOTAL_CAPACITY", "label": "Total Cap", "fmt": "dollar"},
                {"col": "CAPACITY_REMAINING", "label": "Cap Remain", "fmt": "dollar"},
                {"col": "PCT_REMAINING", "label": "% Remain", "fmt": "pct"},
                {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Pred Under", "fmt": "dollar"},
            ])

else:
    st.info("No capacity data found.")

st.divider()

# --- CAPACITY & RENEWAL PIPELINE ---
st.markdown("### :material/timeline: Capacity & Renewal Pipeline")

if not cap_pipe_df.empty:
    fp1, fp2, fp3, fp4, fp5 = st.columns(5)
    with fp1:
        type_filter = st.multiselect("Opp Type", options=sorted(cap_pipe_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="cpipe_type")
    with fp2:
        ae_filter_p = st.multiselect("AE", options=sorted(cap_pipe_df["OWNER"].dropna().unique()), default=[], key="cpipe_ae")
    with fp3:
        stage_filter_p = st.multiselect("Stage", options=sorted(cap_pipe_df["STAGE_NAME"].dropna().unique()), default=[], key="cpipe_stage")
    with fp4:
        fc_filter_p = st.multiselect("Forecast", options=sorted(cap_pipe_df["FORECAST_STATUS"].dropna().unique()), default=[], key="cpipe_fc")
    with fp5:
        search_p = st.text_input("Search opportunity", "", key="cpipe_search")

    filtered_p = cap_pipe_df.copy()
    if type_filter:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_TYPE"].isin(type_filter)]
    if ae_filter_p:
        filtered_p = filtered_p[filtered_p["OWNER"].isin(ae_filter_p)]
    if stage_filter_p:
        filtered_p = filtered_p[filtered_p["STAGE_NAME"].isin(stage_filter_p)]
    if fc_filter_p:
        filtered_p = filtered_p[filtered_p["FORECAST_STATUS"].isin(fc_filter_p)]
    if search_p:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_NAME"].str.contains(search_p, case=False, na=False) | filtered_p["ACCOUNT_NAME"].str.contains(search_p, case=False, na=False)]

    pk1, pk2, pk3, pk4 = st.columns(4)
    with pk1:
        st.metric("Open Opps", len(filtered_p))
    with pk2:
        total_acv = filtered_p["TOTAL_ACV"].sum()
        st.metric("Total ACV", f"${total_acv:,.0f}")
    with pk3:
        total_tcv = filtered_p["TCV"].sum()
        st.metric("Total TCV", f"${total_tcv:,.0f}")
    with pk4:
        renewals_ct = len(filtered_p[filtered_p["OPPORTUNITY_TYPE"] == "Renewal"])
        st.metric("Renewals", renewals_ct)

    display_p = filtered_p.copy()
    display_p["OPP_LINK"] = display_p.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    render_html_table(display_p, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
        {"col": "OPPORTUNITY_TYPE", "label": "Type"},
        {"col": "STAGE_NAME", "label": "Stage"},
        {"col": "FORECAST_STATUS", "label": "Forecast"},
        {"col": "TOTAL_ACV", "label": "Total ACV", "fmt": "dollar"},
        {"col": "RENEWAL_ACV", "label": "Rnwl ACV", "fmt": "dollar"},
        {"col": "GROWTH_ACV", "label": "Growth ACV", "fmt": "dollar"},
        {"col": "TCV", "label": "TCV", "fmt": "dollar"},
        {"col": "CLOSE_DATE", "label": "Close Date"},
        {"col": "OWNER", "label": "Owner"},
        {"col": "DM", "label": "DM"},

    ], height=500)

    csv_p = filtered_p.to_csv(index=False)
    st.download_button(":material/download: Export Pipeline CSV", csv_p, "capacity_pipeline.csv", "text/csv", key="cpipe_csv")
else:
    st.info("No capacity pipeline opportunities found.")
```

### `app_pages/use_cases_tab.py` (Tab 2)

```python
import streamlit as st
import pandas as pd
from data import load_use_cases, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

df = load_use_cases()

st.markdown("### :material/rocket_launch: All Use Cases")

if not df.empty:
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
    with fc1:
        acct_filter = st.multiselect("Account", options=sorted(df["ACCOUNT_NAME"].dropna().unique()), default=[], key="uc_acct")
    with fc2:
        ae_filter = st.multiselect("AE", options=sorted(df["OWNER"].dropna().unique()), default=[], key="uc_ae")
    with fc3:
        status_filter = st.multiselect("Status", options=sorted(df["USE_CASE_STATUS"].dropna().unique()), default=[], key="uc_status")
    with fc4:
        stage_filter = st.multiselect("Stage", options=sorted(df["STAGE"].dropna().unique()), default=[], key="uc_stage")
    with fc5:
        ps_filter = st.multiselect("PS Engaged", options=["Yes", "No"], default=[], key="uc_ps")
    with fc6:
        search = st.text_input("Search use case", "", key="uc_search")

    filtered = df.copy()
    if acct_filter:
        filtered = filtered[filtered["ACCOUNT_NAME"].isin(acct_filter)]
    if ae_filter:
        filtered = filtered[filtered["OWNER"].isin(ae_filter)]
    if status_filter:
        filtered = filtered[filtered["USE_CASE_STATUS"].isin(status_filter)]
    if stage_filter:
        filtered = filtered[filtered["STAGE"].isin(stage_filter)]
    if ps_filter:
        ps_vals = []
        if "Yes" in ps_filter:
            ps_vals.append(True)
        if "No" in ps_filter:
            ps_vals.append(False)
        filtered = filtered[filtered["IS_PS_ENGAGED"].isin(ps_vals)]
    if search:
        filtered = filtered[filtered["USE_CASE_NAME"].str.contains(search, case=False, na=False)]

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Total Use Cases", len(filtered))
    with kpi2:
        in_pursuit = len(filtered[filtered["USE_CASE_STATUS"] == "In Pursuit"])
        st.metric("In Pursuit", in_pursuit)
    with kpi3:
        in_impl = len(filtered[filtered["USE_CASE_STATUS"] == "Implementation"])
        st.metric("Implementation", in_impl)
    with kpi4:
        total_eacv = filtered["ACV"].sum()
        st.metric("Total EACV", f"${total_eacv:,.0f}")
    with kpi5:
        stuck_count = len(filtered[filtered["DAYS_IN_STAGE"] > 90])
        st.metric("Stuck >90d", stuck_count)

    display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "USE_CASE_NAME", "USE_CASE_ID", "USE_CASE_NUMBER", "USE_CASE_STATUS",
                        "ACV", "STAGE", "CREATED_DATE", "LAST_MODIFIED_DATE",
                        "DAYS_IN_STAGE", "OWNER", "NEXT_STEPS", "IS_PS_ENGAGED"]].copy()

    display["UC_LINK"] = display.apply(
        lambda r: f'{SFDC_BASE}/{r["USE_CASE_ID"]}/view' if pd.notna(r.get("USE_CASE_ID")) else None,
        axis=1
    )
    display["UC_DISPLAY"] = display["USE_CASE_NUMBER"].fillna("")
    display["PS_ENGAGED"] = display["IS_PS_ENGAGED"].map({True: "Yes", False: "No"})

    render_html_table(display, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "USE_CASE_NAME", "label": "Use Case"},
        {"col": "UC_LINK", "label": "UC #", "fmt": "link", "display_col": "UC_DISPLAY"},
        {"col": "USE_CASE_STATUS", "label": "Status"},
        {"col": "ACV", "label": "EACV", "fmt": "dollar"},
        {"col": "STAGE", "label": "Stage"},
        {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
        {"col": "LAST_MODIFIED_DATE", "label": "Modified", "fmt": "date"},
        {"col": "DAYS_IN_STAGE", "label": "Days", "fmt": "number"},
        {"col": "OWNER", "label": "AE"},
        {"col": "NEXT_STEPS", "label": "Next Steps"},
        {"col": "PS_ENGAGED", "label": "PS Engaged"},
    ], height=600)

    csv = filtered.to_csv(index=False)
    st.download_button(":material/download: Export CSV", csv, "use_cases.csv", "text/csv", key="uc_csv")
else:
    st.info("No use case data found.")
```

### `app_pages/pst_tab.py` (Tab 3)

```python
import streamlit as st
import pandas as pd
from data import load_ps_projects_active, load_ps_pipeline, load_ps_history, load_product_usage, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

active_df = load_ps_projects_active()
pipeline_df = load_ps_pipeline()
history_df = load_ps_history()
product_df = load_product_usage()

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
with kpi1:
    st.metric("Active Projects", len(active_df))
with kpi2:
    active_rev = active_df["REVENUE_AMOUNT"].sum() if not active_df.empty else 0
    st.metric("Active Revenue", f"${active_rev:,.0f}")
with kpi3:
    total_hours = active_df["BILLABLE_HOURS"].sum() if not active_df.empty else 0
    st.metric("Billable Hours", f"{total_hours:,.0f}")
with kpi4:
    st.metric("Pipeline Opps", len(pipeline_df))
with kpi5:
    pipe_tcv = pipeline_df["TOTAL_PST_TCV"].sum() if not pipeline_df.empty else 0
    st.metric("Pipeline TCV", f"${pipe_tcv:,.0f}")
with kpi6:
    stalled = len(active_df[active_df["PROJECT_STAGE"].isin(["Stalled", "Stalled - Expiring"])]) if not active_df.empty else 0
    st.metric("Stalled Projects", stalled)


def render_product_expanders(sfdc_acct_ids, product_data, section_key):
    if product_data.empty or len(sfdc_acct_ids) == 0:
        return
    acct_products = product_data[product_data["SALESFORCE_ACCOUNT_ID"].isin(sfdc_acct_ids)]
    if acct_products.empty:
        return
    summary = acct_products.groupby(["ACCOUNT_NAME", "PRODUCT_CATEGORY"]).agg(
        TOTAL_CREDITS=("TOTAL_CREDITS", "sum"),
        TOTAL_JOBS=("TOTAL_JOBS", "sum"),
        FEATURES=("PRIMARY_FEATURE", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index().sort_values(["ACCOUNT_NAME", "TOTAL_CREDITS"], ascending=[True, False])

    with st.expander(f":material/category: Product Usage (Last 3 Months) — {len(acct_products)} products across {acct_products['SALESFORCE_ACCOUNT_ID'].nunique()} accounts", expanded=False):
        render_html_table(summary, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "PRODUCT_CATEGORY", "label": "Category"},
            {"col": "TOTAL_CREDITS", "label": "Credits", "fmt": "number"},
            {"col": "TOTAL_JOBS", "label": "Jobs", "fmt": "number"},
            {"col": "FEATURES", "label": "Features"},
        ])


st.markdown("### :material/check_circle: Active PS&T Projects")

if not active_df.empty:
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
    with fc1:
        acct_filter_a = st.multiselect("Account", options=sorted(active_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psa_acct")
    with fc2:
        stage_filter_a = st.multiselect("Project Stage", options=sorted(active_df["PROJECT_STAGE"].dropna().unique()), default=[], key="psa_stage")
    with fc3:
        practice_filter_a = st.multiselect("Practice", options=sorted(active_df["PRACTICE"].dropna().unique()), default=[], key="psa_practice")
    with fc4:
        dm_filter_a = st.multiselect("DM", options=sorted(active_df["DM"].dropna().unique()), default=[], key="psa_dm")
    with fc5:
        ae_filter_a = st.multiselect("AE", options=sorted(active_df["AE"].dropna().unique()), default=[], key="psa_ae")
    with fc6:
        search_a = st.text_input("Search project", "", key="psa_search")

    filtered_a = active_df.copy()
    if acct_filter_a:
        filtered_a = filtered_a[filtered_a["ACCOUNT_NAME"].isin(acct_filter_a)]
    if stage_filter_a:
        filtered_a = filtered_a[filtered_a["PROJECT_STAGE"].isin(stage_filter_a)]
    if practice_filter_a:
        filtered_a = filtered_a[filtered_a["PRACTICE"].isin(practice_filter_a)]
    if dm_filter_a:
        filtered_a = filtered_a[filtered_a["DM"].isin(dm_filter_a)]
    if ae_filter_a:
        filtered_a = filtered_a[filtered_a["AE"].isin(ae_filter_a)]
    if search_a:
        filtered_a = filtered_a[filtered_a["PROJECT_NAME"].str.contains(search_a, case=False, na=False)]

    display_a = filtered_a.copy()
    display_a["OPP_LINK"] = display_a.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    render_html_table(display_a, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
        {"col": "PROJECT_NAME", "label": "Project"},
        {"col": "PRACTICE", "label": "Practice"},
        {"col": "DM", "label": "DM"},
        {"col": "AE", "label": "AE"},
        {"col": "PROJECT_STAGE", "label": "Stage"},
        {"col": "BILLING_TYPE", "label": "Billing"},
        {"col": "SKU_TYPE", "label": "SKU"},
        {"col": "INVESTMENT_TYPE", "label": "Invest"},
        {"col": "START_DATE", "label": "Start", "fmt": "date"},
        {"col": "END_DATE", "label": "End", "fmt": "date"},
        {"col": "BILLABLE_HOURS", "label": "Bill Hrs", "fmt": "number"},
        {"col": "REVENUE_AMOUNT", "label": "Revenue", "fmt": "dollar"},
        {"col": "PROJECT_MANAGER", "label": "PM"},
        {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        {"col": "ASSIGNMENT_COUNT", "label": "Assignments", "fmt": "number"},
        {"col": "ASSIGNED_RESOURCES", "label": "Resources"},
        {"col": "ASSIGNED_ROLES", "label": "Roles"},
        {"col": "PS_FORECAST_CATEGORY", "label": "Fcast Cat"},
        {"col": "STATUS_NOTES", "label": "Status Notes"},
    ], height=500)

    render_product_expanders(filtered_a["SALESFORCE_ACCOUNT_ID"].unique(), product_df, "active")

    csv_a = filtered_a.to_csv(index=False)
    st.download_button(":material/download: Export Active CSV", csv_a, "pst_active_projects.csv", "text/csv", key="psa_csv")
else:
    st.info("No active PS&T projects found.")

st.divider()

st.markdown("### :material/timeline: PS&T Pipeline (Open Opportunities)")

if not pipeline_df.empty:
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    with fc1:
        acct_filter_p = st.multiselect("Account", options=sorted(pipeline_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psp_acct")
    with fc2:
        ae_filter_p = st.multiselect("AE", options=sorted(pipeline_df["OWNER"].dropna().unique()), default=[], key="psp_ae")
    with fc3:
        stage_filter_p = st.multiselect("Stage", options=sorted(pipeline_df["STAGE_NAME"].dropna().unique()), default=[], key="psp_stage")
    with fc4:
        fc_filter_p = st.multiselect("Forecast", options=sorted(pipeline_df["FORECAST_STATUS"].dropna().unique()), default=[], key="psp_fc")
    with fc5:
        search_p = st.text_input("Search opportunity", "", key="psp_search")

    filtered_p = pipeline_df.copy()
    if acct_filter_p:
        filtered_p = filtered_p[filtered_p["ACCOUNT_NAME"].isin(acct_filter_p)]
    if ae_filter_p:
        filtered_p = filtered_p[filtered_p["OWNER"].isin(ae_filter_p)]
    if stage_filter_p:
        filtered_p = filtered_p[filtered_p["STAGE_NAME"].isin(stage_filter_p)]
    if fc_filter_p:
        filtered_p = filtered_p[filtered_p["FORECAST_STATUS"].isin(fc_filter_p)]
    if search_p:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_NAME"].str.contains(search_p, case=False, na=False)]

    display_p = filtered_p.copy()
    display_p["OPP_LINK"] = display_p.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)
    render_html_table(display_p, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
        {"col": "PRODUCT_NAMES", "label": "Products"},
        {"col": "PS_SERVICE_TYPE", "label": "Svc Type"},
        {"col": "STAGE_NAME", "label": "Stage"},
        {"col": "FORECAST_STATUS", "label": "Forecast"},
        {"col": "PS_INVESTMENT_TYPE", "label": "Invest"},
        {"col": "QUOTE_SUB_AGREEMENT_TYPE", "label": "Agreement"},
        {"col": "CLOSE_DATE", "label": "Close", "fmt": "date"},
        {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
        {"col": "SALES_QUALIFIED_DATE", "label": "SQ Date", "fmt": "date"},
        {"col": "FISCAL_QUARTER", "label": "FQ"},
        {"col": "DAYS_IN_STAGE", "label": "Days", "fmt": "number"},
        {"col": "TOTAL_PST_TCV", "label": "Total TCV", "fmt": "dollar"},
        {"col": "PS_SERVICES_TCV", "label": "PS TCV", "fmt": "dollar"},
        {"col": "EDUCATION_SERVICES_TCV", "label": "Edu TCV", "fmt": "dollar"},
        {"col": "PS_SERVICES_FORECAST", "label": "PS Fcast $", "fmt": "dollar"},
        {"col": "EDUCATION_SERVICES_FORECAST", "label": "Edu Fcast $", "fmt": "dollar"},
        {"col": "DM", "label": "DM"},
        {"col": "OWNER", "label": "AE"},
        {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        {"col": "OPP_PROBABILITY", "label": "Prob %", "fmt": "pct"},
        {"col": "MEDDPICC_SCORE", "label": "MEDDPICC", "fmt": "decimal1"},
        {"col": "PS_FORECAST_CATEGORY", "label": "PS Fcast Cat"},
    ], height=450)

    render_product_expanders(filtered_p["SALESFORCE_ACCOUNT_ID"].unique(), product_df, "pipeline")

    csv_p = filtered_p.to_csv(index=False)
    st.download_button(":material/download: Export Pipeline CSV", csv_p, "pst_pipeline.csv", "text/csv", key="psp_csv")
else:
    st.info("No PS&T pipeline opportunities found.")

st.divider()

st.markdown("### :material/history: Historical Sold Services & Training")

if not history_df.empty:
    hc1, hc2, hc3, hc4, hc5, hc6 = st.columns(6)
    with hc1:
        acct_filter_h = st.multiselect("Account", options=sorted(history_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psh_acct")
    with hc2:
        dm_filter_h = st.multiselect("DM", options=sorted(history_df["DM"].dropna().unique()), default=[], key="psh_dm")
    with hc3:
        ae_filter_h = st.multiselect("AE", options=sorted(history_df["AE"].dropna().unique()), default=[], key="psh_ae")
    with hc4:
        pf_filter_h = st.multiselect("Product Family", options=sorted(history_df["PRODUCT_FAMILIES"].dropna().unique()), default=[], key="psh_pf")
    with hc5:
        type_filter_h = st.multiselect("Opp Type", options=sorted(history_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="psh_type")
    with hc6:
        search_h = st.text_input("Search opportunity", "", key="psh_search")

    filtered_h = history_df.copy()
    if acct_filter_h:
        filtered_h = filtered_h[filtered_h["ACCOUNT_NAME"].isin(acct_filter_h)]
    if dm_filter_h:
        filtered_h = filtered_h[filtered_h["DM"].isin(dm_filter_h)]
    if ae_filter_h:
        filtered_h = filtered_h[filtered_h["AE"].isin(ae_filter_h)]
    if pf_filter_h:
        filtered_h = filtered_h[filtered_h["PRODUCT_FAMILIES"].isin(pf_filter_h)]
    if type_filter_h:
        filtered_h = filtered_h[filtered_h["OPPORTUNITY_TYPE"].isin(type_filter_h)]
    if search_h:
        filtered_h = filtered_h[filtered_h["OPPORTUNITY_NAME"].str.contains(search_h, case=False, na=False) | filtered_h["ACCOUNT_NAME"].str.contains(search_h, case=False, na=False)]

    hk1, hk2, hk3, hk4 = st.columns(4)
    with hk1:
        st.metric("Closed Won Opps", len(filtered_h))
    with hk2:
        st.metric("PS Services $", f"${filtered_h['PS_SERVICES_ACV'].sum():,.0f}")
    with hk3:
        st.metric("Edu Services $", f"${filtered_h['EDU_SERVICES_ACV'].sum():,.0f}")
    with hk4:
        st.metric("Total PST $", f"${filtered_h['TOTAL_PST_AMOUNT'].sum():,.0f}")

    display_h = filtered_h.copy()
    display_h["OPP_LINK"] = display_h.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    render_html_table(display_h, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "SFDC", "fmt": "link"},
        {"col": "DM", "label": "DM"},
        {"col": "AE", "label": "AE"},
        {"col": "OPP_OWNER", "label": "Opp Owner"},
        {"col": "OPPORTUNITY_TYPE", "label": "Type"},
        {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
        {"col": "PRODUCT_FAMILIES", "label": "Product Family"},
        {"col": "PS_SERVICES_ACV", "label": "PS Svc $", "fmt": "dollar"},
        {"col": "EDU_SERVICES_ACV", "label": "Edu Svc $", "fmt": "dollar"},
        {"col": "TOTAL_PST_AMOUNT", "label": "Total PST $", "fmt": "dollar"},
        {"col": "PS_SERVICE_TYPE", "label": "Svc Type"},
        {"col": "PS_INVESTMENT_TYPE", "label": "Invest Type"},
        {"col": "PS_INVESTMENT_AMOUNT", "label": "Invest $", "fmt": "dollar"},
        {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        {"col": "STAGE_NAME", "label": "Stage"},
    ], height=600)

    csv_h = filtered_h.to_csv(index=False)
    st.download_button(":material/download: Export History CSV", csv_h, "pst_history.csv", "text/csv", key="psh_csv")
else:
    st.info("No historical PS&T opportunities found.")
```

### `app_pages/sd_opp_generator.py` (Tab 4)

```python
import streamlit as st
import pandas as pd
from data import load_ps_opportunity_scores, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

ps_opp = load_ps_opportunity_scores()

st.markdown("### :material/military_tech: SD Opp Generator")
st.caption("Accounts ranked by services opportunity — based on use cases without PS engagement (In Pursuit + Implementation) and contract end proximity (<12mo).")

if not ps_opp.empty:
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        dm_filter = st.multiselect("DM", options=sorted(ps_opp["DM"].dropna().unique()), default=[], key="sdopp_dm")
    with fc2:
        ae_filter = st.multiselect("AE", options=sorted(ps_opp["ACCOUNT_OWNER"].dropna().unique()), default=[], key="sdopp_ae")
    with fc3:
        search = st.text_input("Search account", "", key="sdopp_search")

    filtered = ps_opp.copy()
    if dm_filter:
        filtered = filtered[filtered["DM"].isin(dm_filter)]
    if ae_filter:
        filtered = filtered[filtered["ACCOUNT_OWNER"].isin(ae_filter)]
    if search:
        filtered = filtered[filtered["ACCOUNT_NAME"].str.contains(search, case=False, na=False)]

    filtered = filtered.head(30)

    st.caption(f"Showing top {len(filtered)} accounts")

    filtered["RANK"] = range(1, len(filtered) + 1)
    filtered["ACCT_LINK"] = filtered["SALESFORCE_ACCOUNT_ID"].apply(
        lambda x: f'{SFDC_BASE}/Account/{x}/view' if pd.notna(x) and x else "")
    filtered["CONTRACT_START_DATE"] = pd.to_datetime(filtered["CONTRACT_START_DATE"])
    filtered["CONTRACT_END_DATE"] = pd.to_datetime(filtered["CONTRACT_END_DATE"])

    render_html_table(filtered, columns=[
        {"col": "RANK", "label": "#", "fmt": "number"},
        {"col": "ACCT_LINK", "label": "Account", "fmt": "link", "display_col": "ACCOUNT_NAME"},
        {"col": "ACCOUNT_OWNER", "label": "AE"},
        {"col": "DM", "label": "DM"},
        {"col": "PS_OPP_SCORE", "label": "Score", "fmt": "decimal1"},
        {"col": "UC_COUNT_NO_PS", "label": "UCs w/o PS", "fmt": "number"},
        {"col": "UC_COUNT_TOTAL", "label": "UCs Total", "fmt": "number"},
        {"col": "EACV_NO_PS", "label": "EACV (No PS)", "fmt": "dollar"},
        {"col": "CONTRACT_START_DATE", "label": "Contract Start", "fmt": "date"},
        {"col": "CONTRACT_END_DATE", "label": "Contract End", "fmt": "date"},
        {"col": "DAYS_TO_END", "label": "Days to End", "fmt": "number"},
    ], height=800)

    csv = filtered.to_csv(index=False)
    st.download_button(":material/download: Export CSV", csv, "sd_opp_generator.csv", "text/csv", key="sdopp_csv")
else:
    st.info("No PS opportunity data found.")
```

### `app_pages/pm_tab.py` (Tab 5)

```python
import streamlit as st
import pandas as pd
from data import (
    load_accounts_base,
    load_ps_projects_active,
    load_capacity_pipeline,
    render_html_table,
)
from pm_db import get_all_entries, save_entry, get_entry

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

accounts_df = load_accounts_base()
active_df = load_ps_projects_active()
pipeline_df = load_capacity_pipeline()

acct_entries = get_all_entries("Account")
proj_entries = get_all_entries("Active Project")
pipe_entries = get_all_entries("Pipeline")

view = st.radio(
    "View",
    ["Accounts", "Active Projects", "Pipeline Opportunities"],
    horizontal=True,
    key="pm_view",
)

st.divider()

# ---------- ACCOUNTS ----------
if view == "Accounts":
    st.markdown("### :material/business: Accounts")

    if not accounts_df.empty:
        df = accounts_df.copy()
        df["NOTES_NEXT_STEPS"] = df["ACCOUNT_NAME"].apply(
            lambda n: acct_entries.get(("Account", n), {}).get("notes_next_steps", "")
        )
        df["ACCT_LINK"] = df.apply(
            lambda r: f'{SFDC_BASE}/Account/{r["SALESFORCE_ACCOUNT_ID"]}/view'
            if pd.notna(r.get("SALESFORCE_ACCOUNT_ID")) else None, axis=1
        )

        fc1, fc2 = st.columns(2)
        with fc1:
            dm_f = st.multiselect("DM", sorted(df["DM"].dropna().unique()), default=[], key="pm_a_dm")
        with fc2:
            ae_f = st.multiselect("AE", sorted(df["ACCOUNT_OWNER"].dropna().unique()), default=[], key="pm_a_ae")

        has_notes_f = st.checkbox("Only rows with notes", key="pm_a_has_notes")

        filt = df.copy()
        if dm_f:
            filt = filt[filt["DM"].isin(dm_f)]
        if ae_f:
            filt = filt[filt["ACCOUNT_OWNER"].isin(ae_f)]
        if has_notes_f:
            filt = filt[filt["NOTES_NEXT_STEPS"].str.strip() != ""]

        st.caption(f"{len(filt)} accounts")

        with st.expander(":material/edit_note: Edit Notes & Next Steps", expanded=False):
            sel = st.selectbox("Select Account", filt["ACCOUNT_NAME"].tolist(), key="pm_a_sel")
            if sel:
                existing = get_entry("Account", sel)
                current_val = existing["notes_next_steps"] if existing else ""
                new_val = st.text_area("Notes & Next Steps", value=current_val, height=120, key="pm_a_notes")
                if st.button(":material/save: Save", key="pm_a_save"):
                    save_entry("Account", sel, new_val)
                    st.success(f"Saved notes for {sel}")
                    st.rerun()

        render_html_table(filt, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCT_LINK", "label": "SFDC", "fmt": "link"},
            {"col": "NOTES_NEXT_STEPS", "label": "Notes & Next Steps", "highlight": True},
            {"col": "ACCOUNT_OWNER", "label": "AE"},
            {"col": "DM", "label": "DM"},
            {"col": "LEAD_SE", "label": "Lead SE"},
            {"col": "INDUSTRY", "label": "Industry"},
            {"col": "SUBINDUSTRY", "label": "Sub-Industry"},
        ], height=500)
    else:
        st.info("No accounts found.")

# ---------- ACTIVE PROJECTS ----------
elif view == "Active Projects":
    st.markdown("### :material/support_agent: Active Projects")

    if not active_df.empty:
        df = active_df.copy()
        df["NOTES_NEXT_STEPS"] = df["PROJECT_NAME"].apply(
            lambda n: proj_entries.get(("Active Project", n), {}).get("notes_next_steps", "")
        )
        df["ACCT_LINK"] = df.apply(
            lambda r: f'{SFDC_BASE}/Account/{r["SALESFORCE_ACCOUNT_ID"]}/view'
            if pd.notna(r.get("SALESFORCE_ACCOUNT_ID")) else None, axis=1
        )
        df["OPP_LINK"] = df.apply(
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view'
            if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            dm_f = st.multiselect("DM", sorted(df["DM"].dropna().unique()), default=[], key="pm_p_dm")
        with fc2:
            ae_f = st.multiselect("AE", sorted(df["AE"].dropna().unique()), default=[], key="pm_p_ae")
        with fc3:
            stage_f = st.multiselect("Project Stage", sorted(df["PROJECT_STAGE"].dropna().unique()), default=[], key="pm_p_stage")
        with fc4:
            svc_f = st.multiselect("Service Type", sorted(df["SERVICE_TYPE"].dropna().unique()), default=[], key="pm_p_svc")

        has_notes_f = st.checkbox("Only rows with notes", key="pm_p_has_notes")

        filt = df.copy()
        if dm_f:
            filt = filt[filt["DM"].isin(dm_f)]
        if ae_f:
            filt = filt[filt["AE"].isin(ae_f)]
        if stage_f:
            filt = filt[filt["PROJECT_STAGE"].isin(stage_f)]
        if svc_f:
            filt = filt[filt["SERVICE_TYPE"].isin(svc_f)]
        if has_notes_f:
            filt = filt[filt["NOTES_NEXT_STEPS"].str.strip() != ""]

        st.caption(f"{len(filt)} active projects")

        with st.expander(":material/edit_note: Edit Notes & Next Steps", expanded=False):
            sel = st.selectbox("Select Project", filt["PROJECT_NAME"].tolist(), key="pm_p_sel")
            if sel:
                existing = get_entry("Active Project", sel)
                current_val = existing["notes_next_steps"] if existing else ""
                new_val = st.text_area("Notes & Next Steps", value=current_val, height=120, key="pm_p_notes")
                if st.button(":material/save: Save", key="pm_p_save"):
                    save_entry("Active Project", sel, new_val)
                    st.success(f"Saved notes for {sel}")
                    st.rerun()

        render_html_table(filt, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "PROJECT_NAME", "label": "Project"},
            {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
            {"col": "NOTES_NEXT_STEPS", "label": "Notes & Next Steps", "highlight": True},
            {"col": "AE", "label": "AE"},
            {"col": "DM", "label": "DM"},
            {"col": "PROJECT_STAGE", "label": "Stage"},
            {"col": "SERVICE_TYPE", "label": "Svc Type"},
            {"col": "INVESTMENT_TYPE", "label": "Invest Type"},
            {"col": "START_DATE", "label": "Start", "fmt": "date"},
            {"col": "END_DATE", "label": "End", "fmt": "date"},
            {"col": "BILLABLE_HOURS", "label": "Billed Hrs", "fmt": "number"},
            {"col": "REVENUE_AMOUNT", "label": "Revenue", "fmt": "dollar"},
            {"col": "PROJECT_MANAGER", "label": "PM"},
            {"col": "ASSIGNED_RESOURCES", "label": "Resources"},
            {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        ], height=500)
    else:
        st.info("No active projects found.")

# ---------- PIPELINE OPPORTUNITIES ----------
elif view == "Pipeline Opportunities":
    st.markdown("### :material/trending_up: Pipeline Opportunities")

    if not pipeline_df.empty:
        df = pipeline_df.copy()
        df["NOTES_NEXT_STEPS"] = df["OPPORTUNITY_NAME"].apply(
            lambda n: pipe_entries.get(("Pipeline", n), {}).get("notes_next_steps", "")
        )
        df["ACCT_LINK"] = df.apply(
            lambda r: f'{SFDC_BASE}/Account/{r["SALESFORCE_ACCOUNT_ID"]}/view'
            if pd.notna(r.get("SALESFORCE_ACCOUNT_ID")) else None, axis=1
        )
        df["OPP_LINK"] = df.apply(
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view'
            if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            dm_f = st.multiselect("DM", sorted(df["DM"].dropna().unique()), default=[], key="pm_o_dm")
        with fc2:
            owner_f = st.multiselect("Opp Owner", sorted(df["OWNER"].dropna().unique()), default=[], key="pm_o_owner")
        with fc3:
            stage_f = st.multiselect("Stage", sorted(df["STAGE_NAME"].dropna().unique()), default=[], key="pm_o_stage")
        with fc4:
            type_f = st.multiselect("Opp Type", sorted(df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="pm_o_type")

        has_notes_f = st.checkbox("Only rows with notes", key="pm_o_has_notes")

        filt = df.copy()
        if dm_f:
            filt = filt[filt["DM"].isin(dm_f)]
        if owner_f:
            filt = filt[filt["OWNER"].isin(owner_f)]
        if stage_f:
            filt = filt[filt["STAGE_NAME"].isin(stage_f)]
        if type_f:
            filt = filt[filt["OPPORTUNITY_TYPE"].isin(type_f)]
        if has_notes_f:
            filt = filt[filt["NOTES_NEXT_STEPS"].str.strip() != ""]

        st.caption(f"{len(filt)} open opportunities")

        with st.expander(":material/edit_note: Edit Notes & Next Steps", expanded=False):
            sel = st.selectbox("Select Opportunity", filt["OPPORTUNITY_NAME"].tolist(), key="pm_o_sel")
            if sel:
                existing = get_entry("Pipeline", sel)
                current_val = existing["notes_next_steps"] if existing else ""
                new_val = st.text_area("Notes & Next Steps", value=current_val, height=120, key="pm_o_notes")
                if st.button(":material/save: Save", key="pm_o_save"):
                    save_entry("Pipeline", sel, new_val)
                    st.success(f"Saved notes for {sel}")
                    st.rerun()

        render_html_table(filt, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
            {"col": "NOTES_NEXT_STEPS", "label": "Notes & Next Steps", "highlight": True},
            {"col": "OWNER", "label": "Opp Owner"},
            {"col": "DM", "label": "DM"},
            {"col": "OPPORTUNITY_TYPE", "label": "Type"},
            {"col": "STAGE_NAME", "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
            {"col": "FISCAL_QUARTER", "label": "FQ"},
            {"col": "DAYS_IN_STAGE", "label": "Days in Stage", "fmt": "number"},
            {"col": "TOTAL_ACV", "label": "Total ACV", "fmt": "dollar"},
            {"col": "RENEWAL_ACV", "label": "Renewal ACV", "fmt": "dollar"},
            {"col": "GROWTH_ACV", "label": "Growth ACV", "fmt": "dollar"},
            {"col": "TCV", "label": "TCV", "fmt": "dollar"},
            {"col": "SE_COMMENTS", "label": "SE Comments"},
            {"col": "NEXT_STEPS", "label": "SFDC Next Steps"},
        ], height=500)
    else:
        st.info("No open pipeline opportunities found.")
```

---

## 9. Tab-by-Tab Feature Reference

### Tab 1: Capacity & Renewals
- **Active Capacity Contracts table** with account SFDC links, capacity metrics, overage/underage prediction
- **Filters:** DM, AE, Total Capacity band ($0/$1M/$5M/$10M+), account search
- **KPIs:** Account count, Total Capacity $, Total Remaining $
- **Capacity Conversion Candidates expander:** Accounts ending within 18 months with predicted underburn (OVERAGE_UNDERAGE_PREDICTION < 0 and DAYS_LEFT <= 548)
- **Capacity & Renewal Pipeline table** with opportunity SFDC links
- **Filters:** Opp Type, AE, Stage, Forecast, search
- **KPIs:** Open Opps, Total ACV, Total TCV, Renewals count
- **CSV export** for both tables

### Tab 2: Use Cases
- **All Use Cases table** from MDM.MDM_INTERFACES.DIM_USE_CASE
- **Filters:** Account, AE, Status, Stage, PS Engaged (Yes/No), search
- **KPIs:** Total UCs, In Pursuit, Implementation, Total EACV, Stuck >90d
- **Use Case # column** links to SFDC Use Case record (displays USE_CASE_NUMBER)
- **CSV export**

### Tab 3: SD Projects
- **Top-level KPIs:** Active Projects, Active Revenue, Billable Hours, Pipeline Opps, Pipeline TCV, Stalled Projects
- **Active PS&T Projects** section with filters (Account, Stage, Practice, DM, AE, search)
- **Product Usage expander** (last 3 months, grouped by account + category)
- **PS&T Pipeline** section with filters (Account, AE, Stage, Forecast, search)
- **Historical Sold Services & Training** section - closed-won opps with PS/Education line items from FIVETRAN.SALESFORCE.OPPORTUNITY (not the daily snapshot view)
- **Filters for historical:** Account, DM, AE, Product Family, Opp Type, search
- **KPIs for historical:** Closed Won Opps, PS Services $, Edu Services $, Total PST $
- **CSV export** for all three sections

### Tab 4: SD Opp Generator
- **PS Opportunity Scoring** - ranks accounts by composite score (contract urgency 35pts + EACV without PS 40pts + UC count without PS 25pts)
- **Filters:** DM, AE, search
- **Shows top 30** accounts, linked to SFDC Account records
- **CSV export**

### Tab 5: Project Management
- **3 sub-views** via horizontal radio buttons: Accounts, Active Projects, Pipeline Opportunities
- Each view has:
  - Relevant filters
  - "Only rows with notes" checkbox
  - Row count caption
  - Editable "Notes & Next Steps" via collapsed expander with selectbox + text_area + Save button
  - "Notes & Next Steps" column highlighted in green in the table
  - Date-stamping on save: lines without `[20...` prefix get `[YYYY-MM-DD] ` prepended
- **Accounts view:** SFDC link, Notes, AE, DM, Lead SE, Industry, Sub-Industry
- **Active Projects view:** Account, Project, Opp SFDC link, Notes, AE, DM, Stage, Svc Type, Invest Type, Start/End dates, Billed Hrs, Revenue, PM, Resources, PS Seller
- **Pipeline Opportunities view:** Account, Opportunity, Opp SFDC link, Notes, Opp Owner, DM, Type, Stage, Forecast, Close Date, FQ, Days in Stage, ACV breakdowns, SE Comments, SFDC Next Steps

---

## 10. Styling & Branding

### Snowflake Brand Colors
- **Primary Blue:** `#29B5E8` (header bar, active tab underline)
- **Action Blue:** `#1E88E5` (links, interactive elements)
- **Dark Navy:** `#11567F` (headings, table header text, sort arrows)

### CSS Applied (in streamlit_app.py)
- Light background: `#f8fafc`
- Header bar: `#29B5E8`
- Metric cards: white with `#e2e8f0` border, 8px radius
- Tab buttons: 16px, 600 weight, active tab has 3px `#29B5E8` bottom border

### HTML Table Styling (in render_html_table)
- Font: Source Sans Pro, 13px body, 12px uppercase headers
- Header background: `#f1f5f9` with `#cbd5e1` bottom border
- Row hover: `#f0f9ff`
- Highlighted columns: header `#e6f4e6`, cells `#f0faf0`
- Links: `#1E88E5`, no underline, underline on hover
- Sticky headers with z-index for scroll
- Max cell width: 350px with word-wrap

---

## 11. Launch Instructions

```bash
# From the project directory
cd ~/account_dashboard

# Launch (connection name must match your ~/.snowflake/connections.toml entry)
SNOWFLAKE_CONNECTION_NAME=snowhouse python3 -m streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

The app will be available at `http://localhost:8501`.

On first load, Snowflake will prompt for SSO authentication via your browser (externalbrowser authenticator).

### Restarting After Core Module Changes
If you modify `data.py` or `pm_db.py`, you must restart the process:

```bash
pkill -f "streamlit run"
SNOWFLAKE_CONNECTION_NAME=snowhouse python3 -m streamlit run ~/account_dashboard/streamlit_app.py --server.port 8501 --server.headless true
```

Tab files (`app_pages/*.py`) reload automatically on save -- no restart needed.

---

## 12. Known Limitations & Deferred Items

### Current Limitations
- **Local only** -- not deployed to Snowflake Streamlit-in-Snowflake (SiS) because `SALES_ENGINEER` role lacks direct grants on `SALES.RAVEN` schema. SiS owner's rights mode doesn't support secondary roles. To unblock SiS, an admin must run:
  ```sql
  GRANT USAGE ON SCHEMA SALES.RAVEN TO ROLE SALES_ENGINEER;
  GRANT SELECT ON ALL TABLES IN SCHEMA SALES.RAVEN TO ROLE SALES_ENGINEER;
  GRANT SELECT ON ALL VIEWS IN SCHEMA SALES.RAVEN TO ROLE SALES_ENGINEER;
  ```
- **PM notes are local-only** -- stored in SQLite on disk, not synced across machines
- **Pipeline Opportunities view on PM tab** uses `OPPORTUNITY_OWNER_NAME` (not AE from Account), since `load_capacity_pipeline()` doesn't join to the Account table for AE

### Deferred Feature Ideas
- Use Case Recommendations engine
- Row-level CSS highlighting (conditional formatting)
- Full Excel workbook export (multi-sheet)
- Pagination for large datasets
- Territory fields (not available in `FIVETRAN.SALESFORCE.OPPORTUNITY`)
