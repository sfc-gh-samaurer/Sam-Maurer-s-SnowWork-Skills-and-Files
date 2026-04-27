import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from decimal import Decimal
import html as html_mod
import json
import os

_ROLE = "TECHNICAL_ACCOUNT_MANAGER"
_WAREHOUSE = "SNOWADHOC"

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
    LEFT JOIN FIVETRAN.SALESFORCE.USER ae_user ON a.REP_NAME = ae_user.NAME AND ae_user.IS_ACTIVE = true
    LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
    LEFT JOIN FIVETRAN.SALESFORCE.USER lead_se ON fa.LEAD_SALES_ENGINEER_C = lead_se.ID
    WHERE a.DS = CURRENT_DATE()
)"""

import re as _re

_DM_FILTER_HARDCODED = "IN ('Erik Schneider', 'Raymond Navarro')"


def render_nav_bar(links):
    buttons_html = "".join(
        f'<button class="nav-btn" onclick="scrollParent(\'{anchor_id}\')">{label}</button>'
        for label, anchor_id in links
    )
    html = f"""<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;overflow:hidden;}}
.nav-container{{display:flex;align-items:center;gap:10px;background:white;
  border:1px solid #e2e8f0;border-radius:12px;padding:10px 18px;flex-wrap:wrap;
  box-shadow:0 2px 8px rgba(0,0,0,0.06);}}
.nav-label{{color:#11567F;font-weight:700;font-size:0.82rem;text-transform:uppercase;
  letter-spacing:0.08em;white-space:nowrap;margin-right:2px;
  font-family:"Source Sans Pro",sans-serif;}}
.nav-btn{{background:#d45b90;color:white;
  border:none;cursor:pointer;padding:5px 14px;border-radius:20px;font-size:0.80rem;
  font-weight:600;white-space:nowrap;font-family:"Source Sans Pro",sans-serif;
  transition:background 0.15s ease;}}
.nav-btn:hover{{background:#b84079;}}
</style>
<div class="nav-container">
  <span class="nav-label">Page Navigation</span>
  {buttons_html}
</div>
<script>
function scrollParent(id){{
  try{{
    var el=window.parent.document.getElementById(id);
    if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});
  }}catch(e){{console.warn('Scroll error:',e);}}
}}
</script>"""
    components.html(html, height=68)


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
    q = q.replace(_DM_FILTER_HARDCODED, f"IN {_get_dm_in_clause()}")
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
        rows_html.append(f"<tr>{cells}</tr>")

    col_types_js = str(col_types).replace("'", '"')
    table_html = f"""
    <html><head><style>
    body {{ margin:0;padding:0;font-family:'Source Sans Pro',sans-serif; }}
    .table-wrapper {{ position:relative; }}
    .fs-bar {{
        display:flex;justify-content:flex-end;padding:2px 4px 4px 0;
    }}
    .fs-btn {{
        background:#f1f5f9;border:1px solid #cbd5e1;border-radius:4px;
        padding:4px 8px;cursor:pointer;font-size:12px;color:#11567F;
        font-family:'Source Sans Pro',sans-serif;
    }}
    .fs-btn:hover {{ background:#e2e8f0; }}
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
    :fullscreen {{ background:#fff; overflow:auto; padding:10px; }}
    :fullscreen .fs-bar {{ position:sticky;top:0;z-index:10;background:#fff; }}
    </style></head><body>
    <div class="table-wrapper" id="tableWrapper">
    <div class="fs-bar"><button class="fs-btn" onclick="toggleFullscreen()" id="fsBtn">⛶ Fullscreen</button></div>
    <table>
    <thead><tr>{headers}</tr></thead>
    <tbody>{"".join(rows_html)}</tbody>
    </table>
    </div>
    <script>
    function toggleFullscreen() {{
        var el = document.getElementById('tableWrapper');
        if (!document.fullscreenElement) {{
            el.requestFullscreen().catch(function(e) {{}});
        }} else {{
            document.exitFullscreen();
        }}
    }}
    document.addEventListener('fullscreenchange', function() {{
        var btn = document.getElementById('fsBtn');
        if (document.fullscreenElement) {{
            btn.textContent = '✕ Exit Fullscreen';
        }} else {{
            btn.textContent = '⛶ Fullscreen';
        }}
    }});
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
    load_product_usage.clear()
    load_ps_history.clear()
    load_action_planner_pipeline.clear()
    load_exec_software_renewals.clear()
    load_exec_services_renewals.clear()
    load_exec_new_opps.clear()
    load_exec_new_use_cases.clear()
    load_wow_use_cases.clear()
    load_wow_projects.clear()
    load_fq_closed_sd.clear()
    load_hierarchy.clear()
    load_org_hierarchy.clear()
    load_account_search_list.clear()


@st.cache_data(ttl=3600)
def load_wow_use_cases(days: int = 7):
    session = _get_session()
    days_safe = max(1, int(days))
    df = session.sql(_sql(f"""
        SELECT
            a.ACCOUNT_NAME,
            uc.NAME_C                        AS USE_CASE_NAME,
            uc.ID                            AS USE_CASE_ID,
            uc.NAME                          AS USE_CASE_NUMBER,
            uc.STAGE_C                       AS CURRENT_STAGE,
            CAST(uc.ESTIMATED_ANNUAL_CREDIT_CONSUMPTION_C AS FLOAT) AS ACV,
            uc.DECISION_DATE_C               AS DECISION_DATE,
            uc.TECHNICAL_WIN_DATE_FORECAST_C AS TARGET_GO_LIVE,
            uc.USE_CASE_STATUS_C             AS UC_STATUS,
            h.FIELD,
            h.OLD_VALUE,
            h.NEW_VALUE,
            h.CREATED_DATE AS CHANGED_AT
        FROM FIVETRAN.SALESFORCE.USE_CASE_HISTORY h
        JOIN FIVETRAN.SALESFORCE.USE_CASE_C uc ON h.PARENT_ID = uc.ID
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON uc.ACCOUNT_C = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND h.FIELD IN ('Stage__c', 'Technical_Win__c', 'Actual_Go_Live_Date__c')
        AND h.CREATED_DATE >= DATEADD('day', -{days_safe}, CURRENT_DATE())
        AND h._FIVETRAN_DELETED = FALSE
        ORDER BY h.CREATED_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=3600)
def load_wow_projects(days: int = 7):
    session = _get_session()
    days_safe = max(1, int(days))
    df = session.sql(_sql(f"""
        SELECT
            a.ACCOUNT_NAME,
            p.NAME                               AS PROJECT_NAME,
            p.ID                                 AS PROJECT_ID,
            p.PSE_STAGE_C                        AS CURRENT_STAGE,
            p.PSE_PROJECT_STATUS_C               AS PROJECT_STATUS,
            p.PSE_BILLING_TYPE_C                 AS BILLING_TYPE,
            p.SERVICE_TYPE_C                     AS SERVICE_TYPE,
            p.PSE_START_DATE_C                   AS START_DATE,
            p.PSE_END_DATE_C                     AS END_DATE,
            CAST(p.PROJECT_REVENUE_AMOUNT_C AS FLOAT) AS REVENUE_AMOUNT,
            CAST(p.PSE_PERCENT_HOURS_COMPLETE_C AS FLOAT) AS PCT_COMPLETE,
            h.FIELD,
            h.OLD_VALUE,
            h.NEW_VALUE,
            h.CREATED_DATE AS CHANGED_AT
        FROM FIVETRAN.SALESFORCE.PSE_PROJ_HISTORY h
        JOIN FIVETRAN.SALESFORCE.PSE_PROJ_C p ON h.PARENT_ID = p.ID
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON p.PSE_ACCOUNT_C = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND h.FIELD IN ('pse__Stage__c', 'pse__Project_Status__c')
        AND h.CREATED_DATE >= DATEADD('day', -{days_safe}, CURRENT_DATE())
        AND h._FIVETRAN_DELETED = FALSE
        ORDER BY h.CREATED_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=3600)
def load_fq_closed_sd(fiscal_quarter: str):
    session = _get_session()
    fq_safe = fiscal_quarter.replace("'", "''")
    df = session.sql(_sql(f"""
        SELECT
            opp.ID            AS OPPORTUNITY_ID,
            opp.NAME          AS OPPORTUNITY_NAME,
            a.ACCOUNT_NAME,
            a.REP_NAME        AS AE,
            opp.CLOSE_DATE,
            opp.TYPE          AS OPP_TYPE,
            opp.AGREEMENT_TYPE_C AS AGREEMENT_TYPE,
            CAST(COALESCE(NULLIF(opp.SERVICES_FORECAST_C, 0), opp.SERVICES_TCV_LOOKER_C, 0) AS FLOAT) AS PS_SERVICES_ACV,
            CAST(COALESCE(NULLIF(opp.SERVICES_FORECAST_C, 0), opp.SERVICES_TCV_LOOKER_C, 0) AS FLOAT) AS TOTAL_PST
        FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON opp.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc ON fc._DATE = opp.CLOSE_DATE AND fc.FISCAL_PERIOD = '{fq_safe}'
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND opp.IS_WON = TRUE
        AND opp.IS_DELETED = FALSE
        AND (opp.SERVICES_TCV_LOOKER_C > 0 OR opp.SERVICES_FORECAST_C > 0)
        ORDER BY opp.CLOSE_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


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
def load_accounts_base():
    session = _get_session()
    df = session.sql(_sql("""
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
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS = 'Active'
        AND a.DS = CURRENT_DATE()
        ORDER BY a.ARR DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_capacity_renewals():
    session = _get_session()
    df = session.sql(_sql("""
        WITH base AS (
            SELECT
                a.NAME AS ACCOUNT_NAME,
                a.SALESFORCE_ACCOUNT_ID,
                a.ACCOUNT_OWNER_NAME AS ACCOUNT_OWNER,
                a.ACCOUNT_OWNER_MANAGER_C AS DM,
                CAST(a.ARR_C AS FLOAT) AS ARR,
                a.TIER_C AS TIER,
                a.LEAD_SALES_ENGINEER_NAME_C AS LEAD_SE,
                CAST(fa.OVERAGE_UNDERAGE_AMOUNT_C AS FLOAT) AS OVERAGE_UNDERAGE_AMOUNT_C,
                fa.OVERAGE_DATE_C,
                CAST(fa.DAYS_TO_CAPACITY_C AS FLOAT) AS DAYS_TO_CAPACITY,
                CAST(fa.CURRENT_CAPACITY_VALUE_C AS FLOAT) AS CURRENT_CAPACITY_VALUE_C,
                CAST(fa.ACTUAL_CONSUMPTION_YTD_C AS FLOAT) AS ACTUAL_CONSUMPTION_YTD_C
            FROM SALES.RAVEN.ACCOUNT a
            JOIN FIVETRAN.SALESFORCE.ACCOUNT fa ON a.SALESFORCE_ACCOUNT_ID = fa.ID
            WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
            AND a.ACCOUNT_STATUS_C = 'Active'
            AND fa.CAPACITY_COUNTER_C > 0
            AND fa.CURRENT_CAPACITY_VALUE_C > 0
        ),
        contracts AS (
            SELECT
                c.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
                MIN(c.START_DATE) AS CONTRACT_START_DATE,
                MAX(c.END_DATE) AS CONTRACT_END_DATE
            FROM FIVETRAN.SALESFORCE.CONTRACT c
            WHERE c.IS_DELETED = FALSE
            AND c.STATUS = 'Activated'
            AND c.ACCOUNT_ID IN (SELECT SALESFORCE_ACCOUNT_ID FROM base)
            GROUP BY c.ACCOUNT_ID
        ),
        renewals AS (
            SELECT
                o.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
                o.NAME AS RENEWAL_OPP_NAME,
                o.ID AS RENEWAL_OPP_ID,
                o.STAGE_NAME AS RENEWAL_OPP_STAGE,
                o.FORECAST_CATEGORY_NAME AS RENEWAL_FORECAST_STATUS,
                CAST(COALESCE(o.RENEWAL_ACV_LOOKER_C, o.ACV_C, o.AMOUNT) AS FLOAT) AS RENEWAL_OPP_ACV,
                o.CLOSE_DATE AS RENEWAL_CLOSE_DATE,
                o.NEXT_STEPS_C AS RENEWAL_NEXT_STEPS,
                ROW_NUMBER() OVER (PARTITION BY o.ACCOUNT_ID ORDER BY o.CLOSE_DATE ASC) AS rn
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY o
            JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON o.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
            LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
            AND o.TYPE = 'Renewal'
            AND o.IS_CLOSED = FALSE
            AND o.IS_DELETED = FALSE
            AND o.AMOUNT > 0
        )
        SELECT
            b.ACCOUNT_NAME,
            b.SALESFORCE_ACCOUNT_ID,
            b.ACCOUNT_OWNER,
            b.DM,
            b.ARR,
            b.TIER,
            b.LEAD_SE,
            contracts.CONTRACT_START_DATE AS CONTRACT_START_DATE,
            contracts.CONTRACT_END_DATE AS CONTRACT_END_DATE,
            b.CURRENT_CAPACITY_VALUE_C AS TOTAL_CAP,
            b.ACTUAL_CONSUMPTION_YTD_C AS ACTUAL_CONSUMPTION_YTD_C,
            b.CURRENT_CAPACITY_VALUE_C - b.ACTUAL_CONSUMPTION_YTD_C AS CAPACITY_REMAINING,
            b.OVERAGE_UNDERAGE_AMOUNT_C AS OVERAGE_UNDERAGE_PREDICTION,
            b.OVERAGE_DATE_C AS OVERAGE_DATE,
            b.DAYS_TO_CAPACITY AS DAYS_TO_CAPACITY,
            r.RENEWAL_OPP_NAME,
            r.RENEWAL_OPP_ID,
            r.RENEWAL_OPP_STAGE,
            r.RENEWAL_FORECAST_STATUS,
            r.RENEWAL_OPP_ACV,
            r.RENEWAL_CLOSE_DATE,
            r.RENEWAL_NEXT_STEPS
        FROM base b
        LEFT JOIN contracts ON b.SALESFORCE_ACCOUNT_ID = contracts.SALESFORCE_ACCOUNT_ID
        LEFT JOIN renewals r ON b.SALESFORCE_ACCOUNT_ID = r.SALESFORCE_ACCOUNT_ID AND r.rn = 1
        ORDER BY contracts.CONTRACT_END_DATE ASC NULLS LAST
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_capacity_pipeline():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            o.ACCOUNT_NAME,
            o.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
            o.OPP_NAME AS OPPORTUNITY_NAME,
            o.OPP_ID AS OPPORTUNITY_ID,
            o.TYPE AS OPPORTUNITY_TYPE,
            o.AGREEMENT_TYPE AS AGREEMENT_TYPE,
            o.STAGE_NAME,
            o.FORECAST_STATUS,
            CAST(COALESCE(sf.FORECAST_ACV_C, 0) AS FLOAT) AS PRODUCT_FORECAST_ACV,
            CAST(COALESCE(sf.PRODUCT_FORECAST_TCV_C, 0) AS FLOAT) AS PRODUCT_FORECAST_TCV,
            CAST(
                CASE WHEN COALESCE(sf.PRODUCT_FORECAST_TCV_C, 0) > 0
                     THEN sf.PRODUCT_FORECAST_TCV_C
                     ELSE COALESCE(sf.FORECAST_ACV_C, 0)
                END AS FLOAT
            ) AS CALCULATED_TCV,
            o.CLOSE_DATE,
            fc.FISCAL_PERIOD AS FISCAL_QUARTER,
            o.REP_NAME AS OWNER,
            o.SE_COMMENTS_C AS SE_COMMENTS,
            o.NEXT_STEPS,
            o.DM
        FROM SNOWHOUSE.SALES.OPPORTUNITIES_DAILY o
        LEFT JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc ON fc._DATE = o.CLOSE_DATE
        LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY sf ON sf.ID = o.OPP_ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON o.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE COALESCE(_dm.NAME, o.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND o.DS = CURRENT_DATE()
        AND o.IS_CLOSED = FALSE
        ORDER BY o.CLOSE_DATE ASC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=3600)
def load_hierarchy():
    session = _get_session()
    df = session.sql("""
        WITH derived_dm AS (
            SELECT a.ACCOUNT_ID, a.DISTRICT_NAME, a.REGION_NAME, a.GEO_NAME,
                COALESCE(dm_user.NAME, a.DM) AS DM
            FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
            LEFT JOIN FIVETRAN.SALESFORCE.USER ae_user ON a.REP_NAME = ae_user.NAME AND ae_user.IS_ACTIVE = true
            LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
            WHERE a.DS = CURRENT_DATE() AND a.ACCOUNT_STATUS = 'Active'
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
        LEFT JOIN FIVETRAN.SALESFORCE.USER ae_user ON a.REP_NAME = ae_user.NAME AND ae_user.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
        JOIN (SELECT DISTINCT NAME FROM FIVETRAN.SALESFORCE.USER WHERE IS_ACTIVE = true) active_dms
            ON COALESCE(dm_user.NAME, a.DM) = active_dms.NAME
        WHERE a.DS = CURRENT_DATE()
        AND a.ACCOUNT_STATUS = 'Active'
        AND a.REGION_NAME IN (
            'LATAM','MajorsAcq','CommAcqEast','CommAcqWest',
            'EntAcqCentral','EntAcqEast','EntAcqWest',
            'NortheastExp','SoutheastExp','CentralExp','Commercial',
            'SouthwestExp','CanadaExp','NorthwestExp','USGrowthExp'
        )
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
        AND a.DS = CURRENT_DATE()
        ORDER BY a.ARR DESC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_use_cases():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            a.ACCOUNT_NAME,
            a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
            uc.NAME_C AS USE_CASE_NAME,
            uc.USE_CASE_STATUS_C AS USE_CASE_STATUS,
            CAST(uc.ESTIMATED_ANNUAL_CREDIT_CONSUMPTION_C AS FLOAT) AS ACV,
            uc.STAGE_C AS STAGE,
            uc.TECHNICAL_WIN_C          AS TECHNICAL_WIN,
            uc.ACTUAL_GO_LIVE_DATE_C    AS ACTUAL_GO_LIVE,
            uc.CREATED_DATE,
            uc.LAST_MODIFIED_DATE,
            uc.LAST_STAGE_CHANGE_IN_DAYS_C AS DAYS_IN_STAGE,
            u.NAME AS OWNER,
            uc.NEXT_STEPS_C AS NEXT_STEPS,
            (uc.PS_ENGAGEMENT_C IS NOT NULL AND uc.PS_ENGAGEMENT_C != 'Not Yet Known') AS IS_PS_ENGAGED,
            uc.PS_ENGAGEMENT_C AS PS_ENGAGEMENT,
            NULL AS PS_DESCRIPTION,
            a.DM,
            a.SUB_INDUSTRY AS ACCOUNT_SUB_INDUSTRY,
            uc.COMPETITORS_C AS COMPETITORS,
            uc.MISSION_CRITICAL_C AS MISSION_CRITICAL,
            uc.TECHNICAL_USE_CASE_C AS TECHNICAL_USE_CASE,
            uc.ID AS USE_CASE_ID,
            uc.NAME AS USE_CASE_NUMBER,
            uc.DECISION_DATE_C AS DECISION_DATE,
            uc.IMPLEMENTER_C AS IMPLEMENTER,
            uc.TECHNICAL_WIN_DATE_FORECAST_C AS TARGET_GO_LIVE,
            uc.USE_CASE_COMMENTS_C AS KEY_NOTES
        FROM FIVETRAN.SALESFORCE.USE_CASE_C uc
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON uc.ACCOUNT_C = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER u ON uc.OWNER_ID = u.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND uc.STAGE_C IS NOT NULL
        AND uc.STAGE_C != '8 - Use Case Lost'
        AND uc._FIVETRAN_DELETED = FALSE
        ORDER BY uc.LAST_STAGE_CHANGE_IN_DAYS_C DESC NULLS LAST
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_projects_active():
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
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON p.PSE_ACCOUNT_C = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        LEFT JOIN FIVETRAN.SALESFORCE.PSE_PRACTICE_C pr ON p.PSE_PRACTICE_C = pr.ID
        LEFT JOIN FIVETRAN.SALESFORCE.CONTACT c ON p.PSE_PROJECT_MANAGER_C = c.ID
        LEFT JOIN assignments asn ON p.ID = asn.PROJECT_ID
        LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY fo ON p.PSE_OPPORTUNITY_C = fo.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER ps_seller ON fo.PS_T_SELLER_C = ps_seller.ID
        LEFT JOIN SNOWHOUSE.SALES.OPPORTUNITIES_DAILY o ON p.PSE_OPPORTUNITY_C = o.OPP_ID AND o.DS = CURRENT_DATE()
        LEFT JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc2 ON fc2._DATE = o.CLOSE_DATE
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS = 'Active'
        AND p.IS_DELETED = FALSE
        AND p.PSE_IS_ACTIVE_C = TRUE
        AND p.PSE_STAGE_C IN ('In Progress', 'Stalled', 'Stalled - Expiring', 'Pipeline', 'Out Year')
        ORDER BY a.ACCOUNT_NAME, p.NAME
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_ps_pipeline():
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
            LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON o.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            WHERE COALESCE(_dm.NAME, o.DM) IN ('Erik Schneider', 'Raymond Navarro')
            AND o.DS = CURRENT_DATE()
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
            JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON opp.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
            LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
            LEFT JOIN SNOWHOUSE.UTILS.FISCAL_CALENDAR fc2 ON fc2._DATE = opp.CLOSE_DATE
            LEFT JOIN (SELECT OPPORTUNITY_ID FROM sda_opps) sda_excl ON opp.ID = sda_excl.OPPORTUNITY_ID
            WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
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
def load_ps_history():
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
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON opp.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        JOIN opp_ps_summary ops ON opp.ID = ops.OPPORTUNITY_ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER ps_seller ON opp.PS_T_SELLER_C = ps_seller.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS = 'Active'
        AND opp.IS_WON = TRUE
        AND opp.IS_DELETED = FALSE
        ORDER BY opp.CLOSE_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_action_planner_pipeline():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            sa.ACCOUNT_NAME,
            sa.ACCOUNT_ID AS ACCOUNT_ID,
            sa.DM AS DM,
            u.DISTRICT_C AS DISTRICT,
            sa.REP_NAME AS AE_NAME,
            lead_se.NAME AS SE_NAME,
            uc.ID AS USE_CASE_ID,
            uc.NAME_C AS USE_CASE_NAME,
            uc.STAGE_C AS STAGE,
            uc.USE_CASE_STATUS_C AS USE_CASE_STATUS,
            CAST(uc.ESTIMATED_ANNUAL_CREDIT_CONSUMPTION_C AS FLOAT) AS EACV,
            uc.TECHNICAL_USE_CASE_C AS TECHNICAL_UC,
            uc.COMPETITORS_C AS COMPETITORS,
            uc.IMPLEMENTER_C AS IMPLEMENTER,
            uc.USE_CASE_COMMENTS_C AS USE_CASE_COMMENTS,
            uc.NEXT_STEPS_C AS NEXT_STEPS,
            uc.NAME AS USE_CASE_NUMBER,
            uc.SPECIALIST_COMMENTS_C AS SE_COMMENTS_FULL
        FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY sa
        JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON sa.ACCOUNT_ID = a.ID
        JOIN FIVETRAN.SALESFORCE.USER u ON a.OWNER_ID = u.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER lead_se ON a.LEAD_SALES_ENGINEER_C = lead_se.ID
        JOIN FIVETRAN.SALESFORCE.USE_CASE_C uc ON uc.ACCOUNT_C = a.ID AND uc._FIVETRAN_DELETED = FALSE
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON sa.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE sa.DS = CURRENT_DATE()
        AND COALESCE(_dm.NAME, sa.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND sa.ACCOUNT_STATUS = 'Active'
        AND uc.STAGE_C IS NOT NULL
        AND uc.STAGE_C != '8 - Use Case Lost'
        ORDER BY sa.ACCOUNT_NAME, uc.ESTIMATED_ANNUAL_CREDIT_CONSUMPTION_C DESC NULLS LAST
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_product_usage():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            c.SALESFORCE_ACCOUNT_ID,
            c.ACCOUNT_NAME AS ACCOUNT_NAME,
            c.PRODUCT_CATEGORY,
            NULL AS USE_CASE,
            NULL AS PRIMARY_FEATURE,
            CAST(SUM(c.CREDITS) AS FLOAT) AS TOTAL_CREDITS,
            NULL::FLOAT AS TOTAL_JOBS
        FROM SNOWHOUSE.PS_TAM.CSP_ACCOUNT_CONSUMPTION c
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON c.SALESFORCE_ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS = 'Active'
        GROUP BY c.SALESFORCE_ACCOUNT_ID, c.ACCOUNT_NAME, c.PRODUCT_CATEGORY
        HAVING SUM(c.CREDITS) > 0
        ORDER BY c.ACCOUNT_NAME, SUM(c.CREDITS) DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_software_renewals():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            o.NAME AS OPPORTUNITY_NAME,
            o.ID AS OPPORTUNITY_ID,
            a.ACCOUNT_NAME,
            a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
            o.STAGE_NAME,
            o.FORECAST_CATEGORY_NAME AS FORECAST_STATUS,
            CAST(COALESCE(o.PRODUCT_ACV_LOOKER_C, o.ACV_C, o.AMOUNT) AS FLOAT) AS TOTAL_ACV,
            CAST(COALESCE(o.RENEWAL_ACV_LOOKER_C, o.ACV_C, 0) AS FLOAT) AS RENEWAL_ACV,
            CAST(o.PRODUCT_FORECAST_TCV_C AS FLOAT) AS PRODUCT_FORECAST_TCV,
            o.CLOSE_DATE,
            o.NEXT_STEPS_C AS NEXT_STEPS,
            a.REP_NAME AS OWNER,
            a.DM
        FROM FIVETRAN.SALESFORCE.OPPORTUNITY o
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON o.ACCOUNT_ID = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND o.IS_CLOSED = FALSE
        AND o.IS_DELETED = FALSE
        AND o.TYPE = 'Renewal'
        AND o.AMOUNT > 0
        AND o.CLOSE_DATE BETWEEN CURRENT_DATE() AND DATEADD(MONTH, 6, CURRENT_DATE())
        ORDER BY o.CLOSE_DATE ASC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_services_renewals():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            p.NAME AS PROJECT_NAME,
            p.ID AS PROJECT_ID,
            a.NAME AS ACCOUNT_NAME,
            a.SALESFORCE_ACCOUNT_ID,
            a.ACCOUNT_OWNER_MANAGER_C AS DM,
            a.ACCOUNT_OWNER_NAME AS AE,
            p.SUB_AGREEMENT_TYPE_C AS AGREEMENT_TYPE,
            p.SERVICE_TYPE_C AS SERVICE_TYPE,
            p.PSE_STAGE_C AS PROJECT_STAGE,
            p.PSE_START_DATE_C AS START_DATE,
            p.PSE_END_DATE_C AS END_DATE,
            CAST(p.PROJECT_REVENUE_AMOUNT_C AS FLOAT) AS REVENUE_AMOUNT,
            p.DELIVERY_MANAGER_ENGAGEMENT_C AS DELIVERY_MANAGER,
            c.NAME AS PROJECT_MANAGER,
            DATEDIFF('day', CURRENT_DATE(), p.PSE_END_DATE_C) AS DAYS_TO_END
        FROM FIVETRAN.SALESFORCE.PSE_PROJ_C p
        JOIN SALES.RAVEN.ACCOUNT a ON p.PSE_ACCOUNT_C = a.SALESFORCE_ACCOUNT_ID
        LEFT JOIN FIVETRAN.SALESFORCE.CONTACT c ON p.PSE_PROJECT_MANAGER_C = c.ID
        WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS_C = 'Active'
        AND p.IS_DELETED = FALSE
        AND p.PSE_IS_ACTIVE_C = TRUE
        AND p.PSE_STAGE_C IN ('In Progress', 'Stalled', 'Stalled - Expiring', 'Pipeline', 'Out Year')
        AND p.PSE_END_DATE_C BETWEEN CURRENT_DATE() AND DATEADD(MONTH, 6, CURRENT_DATE())
        ORDER BY p.PSE_END_DATE_C ASC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_new_opps():
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
            LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON o.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
            LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
            WHERE COALESCE(_dm.NAME, o.DM) IN ('Erik Schneider', 'Raymond Navarro')
            AND o.DS = CURRENT_DATE()
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
            WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
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
def load_exec_new_use_cases():
    session = _get_session()
    df = session.sql(_sql("""
        SELECT
            a.ACCOUNT_NAME,
            a.ACCOUNT_ID AS SALESFORCE_ACCOUNT_ID,
            uc.NAME_C AS USE_CASE_NAME,
            uc.USE_CASE_STATUS_C AS USE_CASE_STATUS,
            CAST(uc.ESTIMATED_ANNUAL_CREDIT_CONSUMPTION_C AS FLOAT) AS ACV,
            uc.STAGE_C AS STAGE,
            uc.CREATED_DATE,
            u.NAME AS OWNER,
            uc.NEXT_STEPS_C AS NEXT_STEPS,
            a.DM,
            uc.ID AS USE_CASE_ID,
            uc.NAME AS USE_CASE_NUMBER
        FROM FIVETRAN.SALESFORCE.USE_CASE_C uc
        JOIN SNOWHOUSE.SALES.ACCOUNTS_DAILY a ON uc.ACCOUNT_C = a.ACCOUNT_ID AND a.DS = CURRENT_DATE()
        LEFT JOIN FIVETRAN.SALESFORCE.USER _ae ON a.REP_NAME = _ae.NAME AND _ae.IS_ACTIVE = true
        LEFT JOIN FIVETRAN.SALESFORCE.USER _dm ON _ae.MANAGER_ID = _dm.ID
        LEFT JOIN FIVETRAN.SALESFORCE.USER u ON uc.OWNER_ID = u.ID
        WHERE COALESCE(_dm.NAME, a.DM) IN ('Erik Schneider', 'Raymond Navarro')
        AND uc.STAGE_C IS NOT NULL
        AND uc.STAGE_C != '8 - Use Case Lost'
        AND uc._FIVETRAN_DELETED = FALSE
        AND uc.CREATED_DATE >= DATEADD('day', -90, CURRENT_DATE())
        ORDER BY uc.CREATED_DATE DESC
    """)).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_org_hierarchy():
    session = _get_session()
    df = session.sql("""
        WITH derived_dm AS (
            SELECT a.ACCOUNT_ID, a.DISTRICT_NAME, a.REGION_NAME, a.GEO_NAME,
                COALESCE(dm_user.NAME, a.DM) AS DM
            FROM SNOWHOUSE.SALES.ACCOUNTS_DAILY a
            LEFT JOIN FIVETRAN.SALESFORCE.USER ae_user ON a.REP_NAME = ae_user.NAME AND ae_user.IS_ACTIVE = true
            LEFT JOIN FIVETRAN.SALESFORCE.USER dm_user ON ae_user.MANAGER_ID = dm_user.ID
            WHERE a.DS = CURRENT_DATE() AND a.ACCOUNT_STATUS = 'Active'
            AND a.REGION_NAME IN (
                'LATAM','MajorsAcq',
                'CommAcqEast','CommAcqWest',
                'EntAcqCentral','EntAcqEast','EntAcqWest',
                'NortheastExp','SoutheastExp','CentralExp','Commercial',
                'SouthwestExp','CanadaExp','NorthwestExp','USGrowthExp'
            )
        ),
        district_top_dm AS (
            SELECT DISTRICT_NAME, REGION_NAME, GEO_NAME, DM,
                RANK() OVER (PARTITION BY DISTRICT_NAME ORDER BY COUNT(DISTINCT ACCOUNT_ID) DESC) AS rk
            FROM derived_dm WHERE DM IS NOT NULL
            GROUP BY DISTRICT_NAME, REGION_NAME, GEO_NAME, DM
        )
        SELECT DISTINCT
            t.GEO_NAME      AS THEATRE,
            t.REGION_NAME   AS REGION,
            t.DISTRICT_NAME AS DISTRICT,
            t.DM            AS DISTRICT_MANAGER,
            COALESCE(u.IS_ACTIVE, false) AS DM_IS_ACTIVE
        FROM district_top_dm t
        LEFT JOIN (SELECT DISTINCT NAME, IS_ACTIVE FROM FIVETRAN.SALESFORCE.USER) u
            ON t.DM = u.NAME
        WHERE t.rk = 1
        AND t.GEO_NAME IS NOT NULL AND t.DISTRICT_NAME IS NOT NULL
        ORDER BY THEATRE, REGION, DISTRICT
    """).to_pandas()
    return df