import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from decimal import Decimal
import html as html_mod
import json
import os
import datetime

_ROLE = "TECHNICAL_ACCOUNT_MANAGER"
_WAREHOUSE = "PST_STEAMLIT_APPS"

_ACCOUNT_SQL = """(
    SELECT
        a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
        a.ACCOUNT_NAME AS NAME,
        a.REP_NAME AS ACCOUNT_OWNER_NAME,
        COALESCE(dm_user.NAME, a.DM) AS ACCOUNT_OWNER_MANAGER_C,
        CAST(a.ARR AS FLOAT) AS ARR_C,
        a.INDUSTRY,
        a.ACCOUNT_TIER AS TIER_C,
        lead_se.NAME AS LEAD_SALES_ENGINEER_NAME_C,
        a.ACCOUNT_STATUS AS ACCOUNT_STATUS_C
    FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
    JOIN FIVETRAN.SALESFORCE.ACCOUNT fa ON a.ACCOUNT_ID = fa.ID
    LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) ae_user ON a.REP_NAME = ae_user.NAME
    LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
    LEFT JOIN FIVETRAN.SALESFORCE.USER lead_se ON fa.LEAD_SALES_ENGINEER_C = lead_se.ID
    WHERE a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
)"""

import re as _re

_DM_PLACEHOLDER = "IN ('__DM_SCOPE_PLACEHOLDER__')"




def _scope_key():
    dms = tuple(sorted(st.session_state.get("selected_dms") or []))
    districts = tuple(sorted(st.session_state.get("selected_districts") or []))
    return (dms, districts)


def _get_dm_in_clause():
    dms = st.session_state.get("selected_dms") or []
    if not dms:
        return "('__no_scope__')"
    escaped = ", ".join(f"'{d.replace(chr(39), chr(39)*2)}'" for d in sorted(dms))
    return f"({escaped})"


def _get_district_in_clause():
    districts = st.session_state.get("selected_districts") or []
    if not districts:
        return None
    escaped = ", ".join(f"'{d.replace(chr(39), chr(39)*2)}'" for d in sorted(districts))
    return f"({escaped})"


def _sql(query):
    q = query.replace("SALES.RAVEN.ACCOUNT", _ACCOUNT_SQL)
    q = q.replace(_DM_PLACEHOLDER, f"IN {_get_dm_in_clause()}")
    district_clause = _get_district_in_clause()
    if district_clause:
        q = _re.sub(
            r'(\w+)\.DM IN \(([^)]+)\)',
            lambda m: f"{m.group(1)}.DM IN ({m.group(2)}) AND {m.group(1)}.DISTRICT_NAME IN {district_clause}",
            q
        )
    return q


class _SessionWrapper:
    def __init__(self, session):
        self._s = session

    def sql(self, query):
        return self._s.sql(_sql(query))

    def __getattr__(self, name):
        return getattr(self._s, name)


def _local_session():
    from snowflake.snowpark import Session
    conn = os.getenv("SNOWFLAKE_CONNECTION_NAME", "sfcogsops-snowhouse_aws_us_west_2")
    return Session.builder.config("connection_name", conn).create()


def _get_session():
    try:
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
    except Exception:
        session = _local_session()
    if not st.session_state.get("_session_initialized"):
        try:
            session.sql(f"USE ROLE {_ROLE}").collect()
        except Exception:
            pass
        try:
            session.sql(f"USE WAREHOUSE {_WAREHOUSE}").collect()
        except Exception:
            pass
        try:
            session.sql("USE SECONDARY ROLES ALL").collect()
        except Exception:
            pass
        st.session_state["_session_initialized"] = True
    return _SessionWrapper(session)


def _init_session():
    if "_data_initialized" not in st.session_state:
        clear_all_caches()
        st.session_state._data_initialized = True


def _fix_decimals(df):
    for col in df.columns:
        if df[col].dtype == object and len(df) > 0 and isinstance(df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None, Decimal):
            df[col] = df[col].astype(float)
    return df


@st.cache_data(ttl=86400)
def load_milestone_acv(_scope=None):
    districts = st.session_state.get("selected_districts") or []
    if not districts:
        return pd.DataFrame()
    df = _read_cache("SD_CACHE_MILESTONE_ACV")
    return df[df["DISTRICT"].isin(districts)].reset_index(drop=True)


def render_html_table(df, columns, height=500, row_style_fn=None):
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
        if f == "html":
            return str(val)
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
        row_bg = row_style_fn(row) if row_style_fn else None
        row_attr = f' style="background:{row_bg};"' if row_bg else ""
        rows_html.append(f"<tr{row_attr}>{cells}</tr>")

    col_types_js = str(col_types).replace("'", '"')
    table_html = f"""
    <html><head><style>
    body {{ margin:0;padding:0;font-family:'Source Sans Pro',sans-serif; }}
    .table-wrapper {{ position:relative; }}
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
    <div class="table-wrapper" id="tableWrapper">
    <table>
    <thead><tr>{headers}</tr></thead>
    <tbody>{"".join(rows_html)}</tbody>
    </table>
    </div>
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


def get_current_user():
    try:
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
    except Exception:
        session = _local_session()
    try:
        result = session.sql("SELECT CURRENT_USER() AS U").collect()
        return result[0]["U"]
    except Exception:
        return "UNKNOWN"


def load_user_prefs():
    try:
        user = get_current_user()
        from snowflake.snowpark.context import get_active_session
        try:
            session = get_active_session()
        except Exception:
            session = _local_session()
        try:
            session.sql(f"USE ROLE {_ROLE}").collect()
            session.sql(f"USE WAREHOUSE {_WAREHOUSE}").collect()
        except Exception:
            pass
        rows = session.sql(
            f"SELECT PREF_JSON FROM TEMP.PPACHENCE.SD_DASHBOARD_USER_PREFS "
            f"WHERE USER_NAME = '{user.replace(chr(39), chr(39)*2)}'"
        ).collect()
        if rows and rows[0]["PREF_JSON"]:
            return json.loads(rows[0]["PREF_JSON"])
    except Exception:
        pass
    return {}


def save_user_prefs(prefs_dict):
    try:
        user = get_current_user()
        from snowflake.snowpark.context import get_active_session
        try:
            session = get_active_session()
        except Exception:
            session = _local_session()
        try:
            session.sql(f"USE ROLE {_ROLE}").collect()
            session.sql(f"USE WAREHOUSE {_WAREHOUSE}").collect()
        except Exception:
            pass
        pref_json = json.dumps(prefs_dict).replace("'", "''")
        user_esc = user.replace("'", "''")
        session.sql(f"""
            MERGE INTO TEMP.PPACHENCE.SD_DASHBOARD_USER_PREFS t
            USING (SELECT '{user_esc}' AS USER_NAME, '{pref_json}' AS PREF_JSON) s
            ON t.USER_NAME = s.USER_NAME
            WHEN MATCHED THEN UPDATE SET PREF_JSON = s.PREF_JSON, UPDATED_AT = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN INSERT (USER_NAME, PREF_JSON, UPDATED_AT)
                VALUES (s.USER_NAME, s.PREF_JSON, CURRENT_TIMESTAMP())
        """).collect()
    except Exception:
        pass


def clear_all_caches():
    load_capacity_renewals.clear()
    load_capacity_pipeline.clear()
    load_use_cases.clear()
    load_ps_projects_active.clear()
    load_ps_pipeline.clear()
    load_accounts_base.clear()
    load_ps_history.clear()
    load_action_planner_pipeline.clear()
    load_exec_software_renewals.clear()
    load_exec_services_renewals.clear()
    load_exec_new_opps.clear()
    load_exec_new_use_cases.clear()
    load_wow_use_cases.clear()
    load_wow_projects.clear()
    load_milestone_acv.clear()
    load_hierarchy.clear()
    load_org_hierarchy.clear()
    load_account_search_list.clear()


# ── Cache helpers ─────────────────────────────────────────────────────────────

def get_cache_last_updated() -> dict:
    """Return {table_name: 'YYYY-MM-DD HH:MM'} from SD_CACHE_METADATA."""
    try:
        from snowflake.snowpark.context import get_active_session
        try:
            session = get_active_session()
        except Exception:
            session = _local_session()
        rows = session.sql("""
            SELECT TABLE_NAME, LAST_REFRESHED_AT
            FROM SD_APPS_DB.SD_CENTER.SD_CACHE_METADATA
        """).collect()
        return {r["TABLE_NAME"]: str(r["LAST_REFRESHED_AT"])[:16] for r in rows}
    except Exception:
        return {}


def trigger_cache_refresh():
    """Call REFRESH_CACHE_ALL() SP in Snowflake. Blocks until done (~1-2 min)."""
    _get_session().sql("CALL SD_APPS_DB.SD_CENTER.REFRESH_CACHE_ALL()").collect()


def trigger_cache_refresh_async():
    """Start REFRESH_CACHE_ALL() asynchronously. Returns AsyncJob."""
    return _get_session().sql("CALL SD_APPS_DB.SD_CENTER.REFRESH_CACHE_ALL()").collect_nowait()


def get_cache_max_staleness_hours():
    """Age (in hours) of the OLDEST cache table, computed entirely in Snowflake
    time so it is timezone-safe. Returns float, or None if unavailable."""
    try:
        from snowflake.snowpark.context import get_active_session
        try:
            session = get_active_session()
        except Exception:
            session = _local_session()
        rows = session.sql("""
            SELECT DATEDIFF('minute', MIN(LAST_REFRESHED_AT), CURRENT_TIMESTAMP()) / 60.0 AS HRS
            FROM SD_APPS_DB.SD_CENTER.SD_CACHE_METADATA
            WHERE LAST_REFRESHED_AT IS NOT NULL
        """).collect()
        return float(rows[0]["HRS"]) if rows and rows[0]["HRS"] is not None else None
    except Exception:
        return None


def get_cache_failed_tables() -> list:
    """Cache tables whose most recent refresh failed (STATUS='FAILED').
    Returns [] if the STATUS column is absent (older deployments) or on error."""
    try:
        from snowflake.snowpark.context import get_active_session
        try:
            session = get_active_session()
        except Exception:
            session = _local_session()
        rows = session.sql("""
            SELECT TABLE_NAME
            FROM SD_APPS_DB.SD_CENTER.SD_CACHE_METADATA
            WHERE STATUS = 'FAILED'
            ORDER BY TABLE_NAME
        """).collect()
        return [r["TABLE_NAME"] for r in rows]
    except Exception:
        return []


def get_refreshed_table_count_since(since_ts: str) -> int:
    """Count cache tables that have been refreshed at or after since_ts (UTC ISO string)."""
    try:
        rows = _get_session().sql(f"""
            SELECT COUNT(*) AS CNT
            FROM SD_APPS_DB.SD_CENTER.SD_CACHE_METADATA
            WHERE LAST_REFRESHED_AT >= '{since_ts}'
        """).collect()
        return rows[0]["CNT"]
    except Exception:
        return 0


def _read_cache(table: str) -> pd.DataFrame:
    """Read a pre-materialized cache table (fast: no complex joins)."""
    session = _get_session()
    qualified = f"SD_APPS_DB.SD_CENTER.{table}"
    try:
        return _fix_decimals(session.sql(f"SELECT * FROM {qualified}").to_pandas())
    except Exception as e:
        if "out of range" not in str(e):
            raise
        # Some rows contain out-of-range dates (e.g. year < 1677) that pandas
        # cannot represent as Timestamps. Re-fetch with date/timestamp columns
        # cast to VARCHAR strings, then re-parse with errors='coerce' so bad
        # values become NaT instead of crashing.
        try:
            schema_rows = session.sql(f"DESCRIBE TABLE {qualified}").collect()
            date_cols = [
                r["name"] for r in schema_rows
                if any(t in r["type"].upper() for t in ("DATE", "TIMESTAMP"))
            ]
            col_exprs = ", ".join(
                f'TRY_TO_CHAR("{c}") AS "{c}"' if c in date_cols else f'"{c}"'
                for c in [r["name"] for r in schema_rows]
            )
            df = _fix_decimals(session.sql(
                f"SELECT {col_exprs} FROM {qualified}"
            ).to_pandas())
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            return df
        except Exception:
            raise e


def _apply_scope(df: pd.DataFrame, dm_col: str = "DM", district_col: str = "DISTRICT_NAME") -> pd.DataFrame:
    """Filter a full-dataset DataFrame to the user's selected DMs/districts.

    District-primary: when districts are in scope and the frame carries a district column,
    filter by district so accounts whose derived DM is null/mismatched are not dropped.
    Falls back to DM filtering only when no district column is available.
    """
    selected_dms = st.session_state.get("selected_dms") or []
    selected_districts = st.session_state.get("selected_districts") or []
    if not selected_dms and not selected_districts:
        return pd.DataFrame(columns=df.columns)
    if selected_districts and district_col in df.columns:
        return df[df[district_col].isin(selected_districts)].reset_index(drop=True)
    if dm_col in df.columns:
        return df[df[dm_col].isin(selected_dms)].reset_index(drop=True)
    return df.reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_wow_use_cases(days: int = 7, _scope=None):
    df = _read_cache("SD_CACHE_WOW_USE_CASES")
    df = _apply_scope(df)
    if not df.empty:
        days_safe = max(1, int(days))
        df["CHANGED_AT"] = pd.to_datetime(df["CHANGED_AT"], errors="coerce")
        cutoff = datetime.date.today() - datetime.timedelta(days=days_safe)
        df = df[df["CHANGED_AT"].dt.date >= cutoff]
    return df.reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_wow_projects(days: int = 7, _scope=None):
    df = _read_cache("SD_CACHE_WOW_PROJECTS")
    df = _apply_scope(df)
    if not df.empty:
        days_safe = max(1, int(days))
        df["CHANGED_AT"] = pd.to_datetime(df["CHANGED_AT"], errors="coerce")
        cutoff = datetime.date.today() - datetime.timedelta(days=days_safe)
        df = df[df["CHANGED_AT"].dt.date >= cutoff]
    return df.reset_index(drop=True)






@st.cache_data(ttl=3600)
def load_data_freshness():
    session = _get_session()
    try:
        row = session.sql("""
            SELECT
                MAX(DS)                              AS ACCOUNTS_DAILY_DATE,
                COUNT_IF(DS = CURRENT_DATE())::INT   AS TODAY_LOADED
            FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY
        """).to_pandas().iloc[0]
        return {
            "accounts_date": str(row["ACCOUNTS_DAILY_DATE"])[:10] if row["ACCOUNTS_DAILY_DATE"] else "Unknown",
            "today_loaded":  bool(row["TODAY_LOADED"]),
        }
    except Exception:
        return {"accounts_date": "Unknown", "today_loaded": False}


@st.cache_data(ttl=86400)
def load_accounts_base(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_ACCOUNTS_BASE"))


@st.cache_data(ttl=86400)
def load_capacity_renewals(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_CAPACITY_RENEWALS"))


def _load_capacity_renewals_ORIG(_scope=None):  # kept for SQL reference only
    session = _get_session()
    df = session.sql(_sql("""
        WITH base AS (
            SELECT
                a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
                a.ACCOUNT_NAME,
                a.REP_NAME AS ACCOUNT_OWNER,
                COALESCE(dm_user.NAME, a.DM) AS DM,
                a.ACCOUNT_TIER AS TIER
            FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
            LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) ae_user ON a.REP_NAME = ae_user.NAME
            LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
            WHERE a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
            AND (
                COALESCE(dm_user.NAME, a.DM) IN ('__DM_SCOPE_PLACEHOLDER__')
                OR a.ACCOUNT_ID IN (
                    SELECT DISTINCT o.ACCOUNT_ID FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY o
                    WHERE o.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY) AND o.DM IN ('__DM_SCOPE_PLACEHOLDER__')
                )
            )
            AND a.ACCOUNT_STATUS = 'Active'
        ),
        capacity AS (
            SELECT
                dc.SALESFORCE_ACCOUNT_ID,
                MAX(dc.CONTRACT_START_DATE) AS CONTRACT_START_DATE,
                MAX(dc.CONTRACT_END_DATE) AS CONTRACT_END_DATE,
                CAST(SUM(dc.CAPACITY_PURCHASED) AS FLOAT) AS CAP_PURCHASED,
                CAST(SUM(dc.TOTAL_CAPACITY) AS FLOAT) AS TOTAL_CAP,
                CAST(SUM(dc.TOTAL_CAPACITY - dc.CAPACITY_USAGE_REMAINING) AS FLOAT) AS CAP_USED,
                CAST(SUM(dc.CAPACITY_USAGE_REMAINING) AS FLOAT) AS CAP_REMAINING
            FROM SALES.RAVEN.DIM_CONTRACT_VIEW dc
            WHERE dc.AGREEMENT_TYPE = 'Capacity'
            AND dc.CAPACITY_PURCHASED > 0
            AND dc.CONTRACT_END_DATE = (
                SELECT MAX(dc2.CONTRACT_END_DATE)
                FROM SALES.RAVEN.DIM_CONTRACT_VIEW dc2
                WHERE dc2.SALESFORCE_ACCOUNT_ID = dc.SALESFORCE_ACCOUNT_ID
                AND dc2.AGREEMENT_TYPE = 'Capacity' AND dc2.CAPACITY_PURCHASED > 0
            )
            GROUP BY dc.SALESFORCE_ACCOUNT_ID
        ),
        capacity_fallback AS (
            SELECT
                f.SALESFORCE_ACCOUNT_ID,
                f.SEGMENT_CONTRACT_START_DATE AS CONTRACT_START_DATE,
                f.SEGMENT_CONTRACT_END_DATE AS CONTRACT_END_DATE,
                CAST(NULL AS FLOAT) AS CAP_PURCHASED,
                CAST(NULL AS FLOAT) AS TOTAL_CAP,
                CAST(NULL AS FLOAT) AS CAP_USED,
                CAST(f.SEGMENT_CONTRACT_CAPACITY_REMAINING_ AS FLOAT) AS CAP_REMAINING
            FROM SNOWHOUSE.SALES.FUTURE_CONTRACT_SEGMENT_OVERAGE f
            WHERE f._DATE = f.DS
            AND f.SALESFORCE_ACCOUNT_ID IN (SELECT SALESFORCE_ACCOUNT_ID FROM base)
            AND f.SALESFORCE_ACCOUNT_ID NOT IN (SELECT SALESFORCE_ACCOUNT_ID FROM capacity)
            QUALIFY ROW_NUMBER() OVER (PARTITION BY f.SALESFORCE_ACCOUNT_ID ORDER BY f.SEGMENT_CONTRACT_END_DATE DESC) = 1
        ),
        capacity_combined AS (
            SELECT * FROM capacity
            UNION ALL
            SELECT * FROM capacity_fallback
        ),
        overage AS (
            SELECT
                ov.SALESFORCE_ACCOUNT_ID,
                CAST(SUM(ov.OVERAGE_UNDERAGE_PREDICTION) AS FLOAT) AS OVERAGE_UNDERAGE_PREDICTION,
                MAX(ov.DAY_OF_OVERAGE) AS OVERAGE_DATE
            FROM SALES.RAVEN.A360_OVERAGE_UNDERAGE_PREDICTION_VIEW ov
            WHERE ov.CONTRACT_END_DATE = (
                SELECT MAX(ov2.CONTRACT_END_DATE)
                FROM SALES.RAVEN.A360_OVERAGE_UNDERAGE_PREDICTION_VIEW ov2
                WHERE ov2.SALESFORCE_ACCOUNT_ID = ov.SALESFORCE_ACCOUNT_ID
            )
            GROUP BY ov.SALESFORCE_ACCOUNT_ID
        ),
        overage_fallback AS (
            SELECT
                f.SALESFORCE_ACCOUNT_ID,
                CAST(f.SEGMENT_CONTRACT_CAPACITY_REMAINING_ AS FLOAT) AS OVERAGE_UNDERAGE_PREDICTION,
                f.OVERAGE_DATE
            FROM SNOWHOUSE.SALES.FUTURE_CONTRACT_SEGMENT_OVERAGE f
            WHERE f._DATE = f.DS
            AND f.SALESFORCE_ACCOUNT_ID IN (SELECT SALESFORCE_ACCOUNT_ID FROM base)
            AND f.SALESFORCE_ACCOUNT_ID NOT IN (SELECT SALESFORCE_ACCOUNT_ID FROM overage)
            QUALIFY ROW_NUMBER() OVER (PARTITION BY f.SALESFORCE_ACCOUNT_ID ORDER BY f.SEGMENT_CONTRACT_END_DATE DESC) = 1
        ),
        overage_combined AS (
            SELECT * FROM overage
            UNION ALL
            SELECT * FROM overage_fallback
        ),
        lead_se AS (
            SELECT fa.ID AS SALESFORCE_ACCOUNT_ID, u.NAME AS LEAD_SE
            FROM FIVETRAN.SALESFORCE.ACCOUNT fa
            LEFT JOIN FIVETRAN.SALESFORCE.USER u ON fa.LEAD_SALES_ENGINEER_C = u.ID
            WHERE fa.ID IN (SELECT SALESFORCE_ACCOUNT_ID FROM base)
        )
        SELECT
            b.ACCOUNT_NAME,
            b.SALESFORCE_ACCOUNT_ID,
            b.ACCOUNT_OWNER,
            b.DM,
            b.TIER,
            ls.LEAD_SE,
            c.CONTRACT_START_DATE,
            c.CONTRACT_END_DATE,
            c.CAP_PURCHASED,
            c.TOTAL_CAP,
            c.CAP_USED,
            c.CAP_REMAINING,
            ov.OVERAGE_UNDERAGE_PREDICTION,
            ov.OVERAGE_DATE
        FROM base b
        LEFT JOIN capacity_combined c ON b.SALESFORCE_ACCOUNT_ID = c.SALESFORCE_ACCOUNT_ID
        LEFT JOIN overage_combined ov ON b.SALESFORCE_ACCOUNT_ID = ov.SALESFORCE_ACCOUNT_ID
        LEFT JOIN lead_se ls ON b.SALESFORCE_ACCOUNT_ID = ls.SALESFORCE_ACCOUNT_ID
        WHERE c.CONTRACT_END_DATE IS NOT NULL
        ORDER BY c.CAP_PURCHASED DESC NULLS LAST
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_capacity_pipeline(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_CAPACITY_PIPELINE"))


@st.cache_data(ttl=3600)
def load_hierarchy():
    session = _get_session()
    df = session.sql("""
        WITH derived_dm AS (
            SELECT a.ACCOUNT_ID, a.DISTRICT_NAME, a.REGION_NAME, a.GEO_NAME,
                COALESCE(dm_user.NAME, a.DM) AS DM
            FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
            LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) ae_user ON a.REP_NAME = ae_user.NAME
            LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
            WHERE a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY) AND a.ACCOUNT_STATUS = 'Active'
        ),
        district_top_dm AS (
            SELECT DISTRICT_NAME, REGION_NAME, GEO_NAME, DM,
                RANK() OVER (PARTITION BY DISTRICT_NAME ORDER BY COUNT(DISTINCT ACCOUNT_ID) DESC) AS rk
            FROM derived_dm
            WHERE DM IS NOT NULL
            GROUP BY DISTRICT_NAME, REGION_NAME, GEO_NAME, DM
        )
        SELECT DISTINCT
            t.GEO_NAME  AS THEATER,
            t.REGION_NAME AS REGION,
            t.DISTRICT_NAME AS DISTRICT,
            t.DM
        FROM district_top_dm t
        JOIN (SELECT DISTINCT NAME FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true) active_dms
            ON t.DM = active_dms.NAME
        WHERE t.rk = 1
        AND t.GEO_NAME IS NOT NULL AND t.DISTRICT_NAME IS NOT NULL
        ORDER BY THEATER, REGION, DISTRICT
    """).to_pandas()
    return df


@st.cache_data(ttl=86400)
def load_account_search_list():
    session = _get_session()
    df = session.sql("""
        SELECT DISTINCT
            a.ACCOUNT_NAME,
            a.DISTRICT_NAME,
            a.REGION_NAME,
            a.GEO_NAME AS THEATER,
            COALESCE(dm_user.NAME, a.DM) AS DM
        FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
        LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) ae_user ON a.REP_NAME = ae_user.NAME
        LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
        WHERE a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
        AND a.ACCOUNT_STATUS = 'Active'
        AND COALESCE(a.GEO_NAME, '') NOT ILIKE 'acctstodelete'
        ORDER BY ACCOUNT_NAME
    """).to_pandas()
    return df


@st.cache_data(ttl=86400)
def load_accounts_for_scope(district_name: str):
    session = _get_session()
    df = session.sql(f"""
        SELECT
            a.ACCOUNT_NAME,
            a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
            a.REP_NAME AS ACCOUNT_OWNER,
            a.DM,
            a.RVP,
            CAST(a.ARR AS FLOAT) AS ARR,
            CAST(a.APS AS FLOAT) AS APS,
            a.INDUSTRY,
            a.SUB_INDUSTRY AS SUBINDUSTRY,
            a.ACCOUNT_TIER AS TIER,
            a.SEGMENT,
            a.BILLING_CITY,
            a.BILLING_STATE,
            a.BILLING_COUNTRY,
            a.NUMBER_OF_EMPLOYEES,
            a.LAST_ACTIVITY_DATE,
            lead_se.NAME AS LEAD_SE,
            a.MATURITY_SCORE_C,
            a.CONSUMPTION_RISK_C,
            a.ACCOUNT_STRATEGY_C,
            a.ACCOUNT_RISK_C,
            a.ACCOUNT_COMMENTS_C,
            a.CONSUMPTION_RISK_MITIGATION_STEPS_C,
            CAST(a.PREDICTED_1_YV_C AS FLOAT) AS PREDICTED_1YV,
            CAST(a.PREDICTED_3_YV_C AS FLOAT) AS PREDICTED_3YV,
            a.TOTAL_ACCOUNTS,
            a.AWS_ACCOUNTS,
            a.AZURE_ACCOUNTS,
            a.GCP_ACCOUNTS
        FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
        JOIN FIVETRAN.SALESFORCE.ACCOUNT fa ON a.ACCOUNT_ID = fa.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER lead_se ON fa.LEAD_SALES_ENGINEER_C = lead_se.ID
        WHERE a.DISTRICT_NAME = '{district_name.replace(chr(39), chr(39)*2)}'
        AND a.ACCOUNT_STATUS = 'Active'
        AND a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
        ORDER BY a.ARR DESC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_use_cases(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_USE_CASES"))


@st.cache_data(ttl=86400)
def load_ps_projects_active(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_PS_PROJECTS_ACTIVE"))


def _load_ps_projects_active_ORIG(_scope=None):  # kept for SQL reference only
    session = _get_session()
    df = session.sql(_sql("""
        WITH assignments AS (
            SELECT
                asgn.PSE_PROJECT_C AS PROJECT_ID,
                COUNT(asgn.ID) AS ASSIGNMENT_COUNT,
                LISTAGG(DISTINCT r.NAME, ', ') WITHIN GROUP (ORDER BY r.NAME) AS RESOURCES,
                LISTAGG(DISTINCT asgn.PSE_ROLE_C, ', ') WITHIN GROUP (ORDER BY asgn.PSE_ROLE_C) AS ROLES,
                MAX(asgn.PSE_END_DATE_C) AS LAST_RESOURCE_END_DATE
            FROM FIVETRAN.SALESFORCE.PSE_ASSIGNMENT_C asgn
            LEFT JOIN FIVETRAN.SALESFORCE.CONTACT r ON asgn.PSE_RESOURCE_C = r.ID
            WHERE asgn.IS_DELETED = FALSE
            GROUP BY asgn.PSE_PROJECT_C
        )
        SELECT
            p.NAME AS PROJECT_NAME,
            p.ID AS PROJECT_ID,
            a.ACCOUNT_NAME AS ACCOUNT_NAME,
            a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
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
            asn.LAST_RESOURCE_END_DATE,
            fo.PS_T_SELLER_C AS PS_SELLER_ID,
            ps_seller.NAME AS PS_SELLER_NAME,
            fo.PS_FORECAST_CATEGORY_C AS PS_FORECAST_CATEGORY,
            fo.PS_T_COMMENTS_C AS PS_COMMENTS,
            o.OPP_NAME AS OPPORTUNITY_NAME,
            o.STAGE_NAME AS OPP_STAGE,
            fc2.FISCAL_PERIOD AS FISCAL_QUARTER,
            o.REP_NAME AS OPP_OWNER,
            a.DM AS DM,
            a.REP_NAME AS AE
        FROM FIVETRAN.SALESFORCE.PSE_PROJ_C p
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON p.PSE_ACCOUNT_C = a.ACCOUNT_ID AND a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
        LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) _ae ON a.REP_NAME = _ae.NAME
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        LEFT JOIN FIVETRAN.SALESFORCE.PSE_PRACTICE_C pr ON p.PSE_PRACTICE_C = pr.ID
        LEFT JOIN FIVETRAN.SALESFORCE.CONTACT c ON p.PSE_PROJECT_MANAGER_C = c.ID
        LEFT JOIN assignments asn ON p.ID = asn.PROJECT_ID
        LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY fo ON p.PSE_OPPORTUNITY_C = fo.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER ps_seller ON fo.PS_T_SELLER_C = ps_seller.ID
        LEFT JOIN SNOWHOUSE.SALES.OPPORTUNITIES_DAILY o ON p.PSE_OPPORTUNITY_C = o.OPP_ID AND o.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY)
        LEFT JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc2 ON fc2._DATE = o.CLOSE_DATE
        WHERE COALESCE(_dm.NAME, a.DM) IN ('__DM_SCOPE_PLACEHOLDER__')
        AND a.ACCOUNT_STATUS = 'Active'
        AND p.IS_DELETED = FALSE
        AND p.PSE_IS_ACTIVE_C = TRUE
        AND p.PSE_STAGE_C IN ('In Progress', 'Stalled', 'Stalled - Expiring', 'Pipeline', 'Out Year')
        AND (p.PSE_END_DATE_C IS NULL OR p.PSE_END_DATE_C >= CURRENT_DATE())
        ORDER BY a.ACCOUNT_NAME, p.NAME
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_pipeline(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_PS_PIPELINE"))


def _load_ps_pipeline_ORIG(_scope=None):  # kept for SQL reference only
    session = _get_session()
    df = session.sql(_sql("""
        WITH sda_opps AS (
            SELECT
                o.ACCOUNT_NAME,
                o.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
                o.OPP_NAME AS OPPORTUNITY_NAME,
                o.OPP_ID AS OPPORTUNITY_ID,
                o.TYPE AS OPPORTUNITY_TYPE,
                o.AGREEMENT_TYPE AS AGREEMENT_TYPE,
                o.STAGE_NAME,
                o.FORECAST_STATUS,
                CAST(COALESCE(fv.PRODUCT_ACV_LOOKER_C, fv.ACV_C, o.OPPORTUNITY_PRODUCT_ACV_TOTAL) AS FLOAT) AS TOTAL_ACV,
                o.CLOSE_DATE,
                fc.FISCAL_PERIOD AS FISCAL_QUARTER,
                NULL AS DAYS_IN_STAGE,
                o.REP_NAME AS OWNER,
                o.DM,
                o.CREATED_DATE,
                CAST(o.PROBABILITY AS FLOAT) AS OPP_PROBABILITY,
                o.SALES_QUALIFIED_DATE,
                o.SE_COMMENTS_C AS SE_COMMENTS,
                o.NEXT_STEPS
            FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY o
            LEFT JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc ON fc._DATE = o.CLOSE_DATE
            LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY fv ON fv.ID = o.OPP_ID
            LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) _ae ON o.REP_NAME = _ae.NAME
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            WHERE COALESCE(_dm.NAME, o.DM) IN ('__DM_SCOPE_PLACEHOLDER__')
            AND o.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY)
            AND o.IS_CLOSED = FALSE
        ),
        fivetran_opps AS (
            SELECT
                a.ACCOUNT_NAME AS ACCOUNT_NAME,
                a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
                opp.NAME AS OPPORTUNITY_NAME,
                opp.ID AS OPPORTUNITY_ID,
                opp.TYPE AS OPPORTUNITY_TYPE,
                opp.AGREEMENT_TYPE_C AS AGREEMENT_TYPE,
                opp.STAGE_NAME,
                opp.FORECAST_CATEGORY_NAME AS FORECAST_STATUS,
                CAST(opp.AMOUNT AS FLOAT) AS TOTAL_ACV,
                opp.CLOSE_DATE,
                fc2.FISCAL_PERIOD AS FISCAL_QUARTER,
                opp.LEAN_DATA_DAYS_IN_STAGE_C AS DAYS_IN_STAGE,
                u.NAME AS OWNER,
                a.DM AS DM,
                opp.CREATED_DATE,
                CAST(opp.PROBABILITY AS FLOAT) AS OPP_PROBABILITY,
                NULL AS SALES_QUALIFIED_DATE,
                NULL AS SE_COMMENTS,
                opp.NEXT_STEP AS NEXT_STEPS
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
            JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON opp.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
            LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) _ae ON a.REP_NAME = _ae.NAME
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
            LEFT JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc2 ON fc2._DATE = opp.CLOSE_DATE
            LEFT JOIN (SELECT OPPORTUNITY_ID FROM sda_opps) sda_excl ON opp.ID = sda_excl.OPPORTUNITY_ID
            WHERE COALESCE(_dm.NAME, a.DM) IN ('__DM_SCOPE_PLACEHOLDER__')
            AND a.ACCOUNT_STATUS = 'Active'
            AND opp.IS_CLOSED = FALSE
            AND opp.IS_DELETED = FALSE
            AND sda_excl.OPPORTUNITY_ID IS NULL
        ),
        all_opps AS (
            SELECT * FROM sda_opps
            UNION ALL
            SELECT * FROM fivetran_opps
        ),
        ts_opps AS (
            SELECT DISTINCT oli.OPPORTUNITY_ID
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY_LINE_ITEM oli
            WHERE oli.IS_DELETED = FALSE
            AND oli.PRODUCT_FAMILY_C IN ('Technical Services', 'Education Services')
        ),
        ts_filtered AS (
            SELECT ao.*
            FROM all_opps ao
            WHERE ao.OPPORTUNITY_ID IN (SELECT OPPORTUNITY_ID FROM ts_opps)
               OR ao.OPPORTUNITY_NAME ILIKE '%PS&T%'
               OR ao.OPPORTUNITY_NAME ILIKE '%PS_T%'
        ),
        products AS (
            SELECT
                oli.OPPORTUNITY_ID,
                LISTAGG(DISTINCT oli.OPPORTUNITY_PRODUCT_NAME_C, ', ') WITHIN GROUP (ORDER BY oli.OPPORTUNITY_PRODUCT_NAME_C) AS PRODUCT_NAMES
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY_LINE_ITEM oli
            WHERE oli.IS_DELETED = FALSE
            AND oli.OPPORTUNITY_PRODUCT_NAME_C IS NOT NULL
            GROUP BY oli.OPPORTUNITY_ID
        )
        SELECT
            tf.ACCOUNT_NAME,
            tf.SALESFORCE_ACCOUNT_ID,
            tf.OPPORTUNITY_NAME,
            tf.OPPORTUNITY_ID,
            tf.OPPORTUNITY_TYPE,
            tf.STAGE_NAME,
            tf.FORECAST_STATUS,
            tf.TOTAL_ACV,
            tf.CLOSE_DATE,
            tf.FISCAL_QUARTER,
            tf.DAYS_IN_STAGE,
            tf.OWNER,
            tf.DM,
            tf.CREATED_DATE,
            tf.OPP_PROBABILITY,
            tf.SALES_QUALIFIED_DATE,
            tf.SE_COMMENTS,
            tf.NEXT_STEPS,
            fo.SERVICE_TYPE_C AS PS_SERVICE_TYPE,
            fo.PS_T_SELLER_C AS PS_SELLER_ID,
            ps_seller.NAME AS PS_SELLER_NAME,
            fo.PS_T_COMMENTS_C AS PS_COMMENTS,
            fo.INVESTMENT_TYPE_C AS PS_INVESTMENT_TYPE,
            CAST(fo.SERVICES_TCV_LOOKER_C AS FLOAT) AS PS_SERVICES_TCV,
            CAST(fo.EDUCATION_SERVICES_TCV_LOOKER_C AS FLOAT) AS EDUCATION_SERVICES_TCV,
            CAST(COALESCE(fo.SERVICES_TCV_LOOKER_C, 0) AS FLOAT) + CAST(COALESCE(fo.EDUCATION_SERVICES_TCV_LOOKER_C, 0) AS FLOAT) AS TOTAL_PST_TCV,
            CAST(fo.SERVICES_FORECAST_C AS FLOAT) AS PS_SERVICES_FORECAST,
            CAST(fo.EDUCATION_SERVICES_FORECAST_C AS FLOAT) AS EDUCATION_SERVICES_FORECAST,
            fo.PS_FORECAST_CATEGORY_C AS PS_FORECAST_CATEGORY,
            fo.SUB_AGREEMENT_TYPE_C AS QUOTE_SUB_AGREEMENT_TYPE,
            pr.PRODUCT_NAMES
        FROM ts_filtered tf
        LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY fo ON tf.OPPORTUNITY_ID = fo.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER ps_seller ON fo.PS_T_SELLER_C = ps_seller.ID
        LEFT JOIN products pr ON tf.OPPORTUNITY_ID = pr.OPPORTUNITY_ID
        ORDER BY tf.CLOSE_DATE ASC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_history(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_PS_HISTORY"))


def _load_ps_history_ORIG(_scope=None):  # kept for SQL reference only
    session = _get_session()
    df = session.sql(_sql("""
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
            a.ACCOUNT_NAME AS ACCOUNT_NAME,
            opp.NAME AS OPPORTUNITY_NAME,
            opp.ID AS OPPORTUNITY_ID,
            a.DM AS DM,
            a.REP_NAME AS AE,
            u.NAME AS OPP_OWNER,
            opp.STAGE_NAME,
            opp.TYPE AS OPPORTUNITY_TYPE,
            opp.AGREEMENT_TYPE_C AS AGREEMENT_TYPE,
            opp.CLOSE_DATE,
            opp.SERVICE_TYPE_C AS PS_SERVICE_TYPE,
            opp.INVESTMENT_TYPE_C AS PS_INVESTMENT_TYPE,
            CAST(opp.PS_INVESTMENT_AMOUNT_C AS FLOAT) AS PS_INVESTMENT_AMOUNT,
            opp.PS_T_SELLER_C AS PS_SELLER_ID,
            ps_seller.NAME AS PS_SELLER_NAME,
            ops.PS_SERVICES_ACV,
            ops.EDU_SERVICES_ACV,
            ops.TOTAL_PST_AMOUNT,
            ops.PRODUCT_FAMILIES
        FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON opp.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY)
        LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) _ae ON a.REP_NAME = _ae.NAME
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        JOIN opp_ps_summary ops ON opp.ID = ops.OPPORTUNITY_ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER ps_seller ON opp.PS_T_SELLER_C = ps_seller.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('__DM_SCOPE_PLACEHOLDER__')
        AND a.ACCOUNT_STATUS = 'Active'
        AND opp.IS_WON = TRUE
        AND opp.IS_DELETED = FALSE
        ORDER BY opp.CLOSE_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_action_planner_pipeline(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_ACTION_PLANNER"))




@st.cache_data(ttl=86400)
def load_exec_software_renewals(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_EXEC_SW_RENEWALS"))


@st.cache_data(ttl=86400)
def load_exec_services_renewals(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_EXEC_SVC_RENEWALS"))


@st.cache_data(ttl=86400)
def load_exec_new_opps(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_EXEC_NEW_OPPS"))


def _load_exec_new_opps_ORIG(_scope=None):  # kept for SQL reference only
    session = _get_session()
    df = session.sql(_sql("""
        WITH sda_new AS (
            SELECT
                o.ACCOUNT_NAME,
                o.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
                o.OPP_NAME AS OPPORTUNITY_NAME,
                o.OPP_ID AS OPPORTUNITY_ID,
                o.TYPE AS OPPORTUNITY_TYPE,
                o.AGREEMENT_TYPE AS AGREEMENT_TYPE,
                o.STAGE_NAME,
                o.FORECAST_STATUS,
                CAST(COALESCE(fv.PRODUCT_ACV_LOOKER_C, fv.ACV_C, o.OPPORTUNITY_PRODUCT_ACV_TOTAL) AS FLOAT) AS TOTAL_ACV,
                o.CLOSE_DATE,
                o.CREATED_DATE,
                o.REP_NAME AS OWNER,
                o.DM
            FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY o
            LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY fv ON fv.ID = o.OPP_ID
            LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) _ae ON o.REP_NAME = _ae.NAME
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            WHERE COALESCE(_dm.NAME, o.DM) IN ('__DM_SCOPE_PLACEHOLDER__')
            AND o.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY)
            AND o.CREATED_DATE >= DATEADD('day', -90, CURRENT_DATE())
        ),
        fivetran_new AS (
            SELECT
                a.NAME AS ACCOUNT_NAME,
                a.SALESFORCE_ACCOUNT_ID,
                opp.NAME AS OPPORTUNITY_NAME,
                opp.ID AS OPPORTUNITY_ID,
                opp.TYPE AS OPPORTUNITY_TYPE,
                opp.AGREEMENT_TYPE_C AS AGREEMENT_TYPE,
                opp.STAGE_NAME,
                opp.FORECAST_CATEGORY_NAME AS FORECAST_STATUS,
                CAST(opp.AMOUNT AS FLOAT) AS TOTAL_ACV,
                opp.CLOSE_DATE,
                opp.CREATED_DATE,
                u.NAME AS OWNER,
                a.ACCOUNT_OWNER_MANAGER_C AS DM
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
            JOIN SALES.RAVEN.ACCOUNT a ON opp.ACCOUNT_ID = a.SALESFORCE_ACCOUNT_ID
            LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
            WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('__DM_SCOPE_PLACEHOLDER__')
            AND a.ACCOUNT_STATUS_C = 'Active'
            AND opp.IS_DELETED = FALSE
            AND opp.CREATED_DATE >= DATEADD('day', -90, CURRENT_DATE())
            AND opp.ID NOT IN (SELECT OPPORTUNITY_ID FROM sda_new)
        )
        SELECT * FROM sda_new
        UNION ALL
        SELECT * FROM fivetran_new
        ORDER BY CREATED_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_new_use_cases(_scope=None):
    return _apply_scope(_read_cache("SD_CACHE_EXEC_NEW_UCS"))


@st.cache_data(ttl=86400)
def load_org_hierarchy():
    session = _get_session()
    df = session.sql("""
        WITH derived_dm AS (
            SELECT a.DISTRICT_NAME, a.REGION_NAME, a.GEO_NAME,
                COALESCE(dm_user.NAME, a.DM) AS DM
            FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
            LEFT JOIN (SELECT NAME, MANAGER_ID FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true QUALIFY ROW_NUMBER() OVER (PARTITION BY NAME ORDER BY ID) = 1) ae_user ON a.REP_NAME = ae_user.NAME
            LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
            WHERE a.DS = (SELECT MAX(DS) FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY) AND a.ACCOUNT_STATUS = 'Active'
        )
        SELECT DISTINCT
            t.GEO_NAME      AS THEATRE,
            t.REGION_NAME   AS REGION,
            t.DISTRICT_NAME AS DISTRICT,
            t.DM            AS DISTRICT_MANAGER,
            COALESCE(u.IS_ACTIVE, false) AS DM_IS_ACTIVE
        FROM derived_dm t
        LEFT JOIN (SELECT DISTINCT NAME, IS_ACTIVE FROM FIVETRAN.SALESFORCE.USER) u
            ON t.DM = u.NAME
        WHERE t.GEO_NAME IS NOT NULL AND t.DISTRICT_NAME IS NOT NULL
        AND TRIM(t.GEO_NAME) <> '' AND t.GEO_NAME NOT ILIKE 'acctstodelete'
        ORDER BY THEATRE, REGION, DISTRICT, DISTRICT_MANAGER
    """).to_pandas()
    return df