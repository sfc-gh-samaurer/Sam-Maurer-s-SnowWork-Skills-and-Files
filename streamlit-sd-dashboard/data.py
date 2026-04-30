import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from decimal import Decimal
import html as html_mod

_ROLE = "SALES_ENGINEER"
_WAREHOUSE = "SNOWADHOC"


def _get_session():
    session = st.connection("snowflake").session()
    session.sql(f"USE ROLE {_ROLE}").collect()
    session.sql(f"USE WAREHOUSE {_WAREHOUSE}").collect()
    session.sql("USE SECONDARY ROLES ALL").collect()
    return session


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
    load_account_consumption_summary.clear()
    load_exec_software_renewals.clear()
    load_exec_services_renewals.clear()
    load_exec_new_opps.clear()
    load_exec_new_use_cases.clear()


@st.cache_data(ttl=86400)
def load_accounts_base():
    session = _get_session()
    df = session.sql("""
        SELECT
            fa.NAME AS ACCOUNT_NAME,
            fa.ID AS SALESFORCE_ACCOUNT_ID,
            fa.ACCOUNT_OWNER_NAME_C AS ACCOUNT_OWNER,
            fa.ACCOUNT_OWNER_MANAGER_C AS DM,
            CAST(fa.ARR_C AS FLOAT) AS ARR,
            fa.INDUSTRY,
            raven.SUB_INDUSTRY AS SUBINDUSTRY,
            fa.TIER_C AS TIER,
            raven.LEAD_SALES_ENGINEER_NAME AS LEAD_SE
        FROM FIVETRAN.SALESFORCE.ACCOUNT fa
        LEFT JOIN SALES.RAVEN.D_SALESFORCE_ACCOUNT_CUSTOMERS raven ON fa.ID = raven.SALESFORCE_ACCOUNT_ID
        WHERE fa.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND fa.ACCOUNT_STATUS_C = 'Active'
        ORDER BY fa.ARR_C DESC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_capacity_renewals():
    session = _get_session()
    df = session.sql("""
        WITH base AS (
            SELECT
                a.NAME AS ACCOUNT_NAME,
                a.ID AS SALESFORCE_ACCOUNT_ID,
                a.ACCOUNT_OWNER_NAME_C AS ACCOUNT_OWNER,
                a.ACCOUNT_OWNER_MANAGER_C AS DM,
                CAST(a.ARR_C AS FLOAT) AS ARR,
                a.TIER_C AS TIER,
                raven.LEAD_SALES_ENGINEER_NAME AS LEAD_SE
            FROM FIVETRAN.SALESFORCE.ACCOUNT a
            LEFT JOIN SALES.RAVEN.D_SALESFORCE_ACCOUNT_CUSTOMERS raven ON a.ID = raven.SALESFORCE_ACCOUNT_ID
            WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
            AND a.ACCOUNT_STATUS_C = 'Active'
        ),
        capacity AS (
            SELECT
                dc.SALESFORCE_ACCOUNT_ID,
                dc.CONTRACT_START_DATE,
                dc.CONTRACT_END_DATE,
                CAST(dc.CAPACITY_PURCHASED AS FLOAT) AS CAPACITY_PURCHASED,
                CAST(dc.TOTAL_CAPACITY AS FLOAT) AS TOTAL_CAPACITY,
                CAST(dc.TOTAL_CAPACITY - dc.CAPACITY_USAGE_REMAINING AS FLOAT) AS CAPACITY_USED,
                CAST(dc.CAPACITY_USAGE_REMAINING AS FLOAT) AS CAPACITY_REMAINING
            FROM SALES.RAVEN.DIM_CONTRACT_VIEW dc
            WHERE dc.AGREEMENT_TYPE = 'Capacity'
            AND dc.CAPACITY_PURCHASED > 0
            QUALIFY ROW_NUMBER() OVER (PARTITION BY dc.SALESFORCE_ACCOUNT_ID ORDER BY dc.CONTRACT_END_DATE DESC) = 1
        ),
        overage AS (
            SELECT
                ov.SALESFORCE_ACCOUNT_ID,
                CAST(ov.OVERAGE_UNDERAGE_PREDICTION AS FLOAT) AS OVERAGE_UNDERAGE_PREDICTION,
                ov.DAY_OF_OVERAGE AS OVERAGE_DATE
            FROM SALES.RAVEN.A360_OVERAGE_UNDERAGE_PREDICTION_VIEW ov
            QUALIFY ROW_NUMBER() OVER (PARTITION BY ov.SALESFORCE_ACCOUNT_ID ORDER BY ov.CONTRACT_END_DATE DESC) = 1
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
            c.CONTRACT_START_DATE,
            c.CONTRACT_END_DATE,
            c.CAPACITY_PURCHASED,
            c.TOTAL_CAPACITY,
            c.CAPACITY_USED,
            c.CAPACITY_REMAINING,
            ov.OVERAGE_UNDERAGE_PREDICTION,
            ov.OVERAGE_DATE,
            r.RENEWAL_OPP_NAME,
            r.RENEWAL_OPP_ID,
            r.RENEWAL_OPP_STAGE,
            r.RENEWAL_FORECAST_STATUS,
            r.RENEWAL_OPP_ACV,
            r.RENEWAL_CLOSE_DATE,
            r.RENEWAL_NEXT_STEPS
        FROM base b
        LEFT JOIN capacity c ON b.SALESFORCE_ACCOUNT_ID = c.SALESFORCE_ACCOUNT_ID
        LEFT JOIN overage ov ON b.SALESFORCE_ACCOUNT_ID = ov.SALESFORCE_ACCOUNT_ID
        LEFT JOIN renewals r ON b.SALESFORCE_ACCOUNT_ID = r.SALESFORCE_ACCOUNT_ID AND r.rn = 1
        WHERE c.CAPACITY_PURCHASED > 0
        ORDER BY ov.OVERAGE_UNDERAGE_PREDICTION ASC NULLS LAST
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
            uc.USE_CASE_NUMBER,
            uc.DECISION_DATE
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
            a.NAME AS ACCOUNT_NAME,
            a.ID AS SALESFORCE_ACCOUNT_ID,
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
            a.ACCOUNT_OWNER_NAME_C AS AE
        FROM FIVETRAN.SALESFORCE.PSE_PROJ_C p
        JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON p.PSE_ACCOUNT_C = a.ID
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
        WITH sda_opps AS (
            SELECT
                o.ACCOUNT_NAME,
                o.SALESFORCE_ACCOUNT_ID,
                o.OPPORTUNITY_NAME,
                o.OPPORTUNITY_ID,
                o.OPPORTUNITY_TYPE,
                o.STAGE_NAME,
                o.FORECAST_STATUS,
                CAST(o.TOTAL_ACV AS FLOAT) AS TOTAL_ACV,
                o.CLOSE_DATE,
                o.FISCAL_QUARTER,
                o.DAYS_IN_STAGE,
                o.OPPORTUNITY_OWNER_NAME AS OWNER,
                o.DM,
                o.CREATED_DATE,
                CAST(o.OPP_PROBABILITY AS FLOAT) AS OPP_PROBABILITY,
                CAST(o.MEDDPICC_OVERALL_SCORE AS FLOAT) AS MEDDPICC_SCORE,
                o.SALES_QUALIFIED_DATE,
                o.SE_COMMENTS,
                o.NEXT_STEPS
            FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
            WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
            AND o.DS = CURRENT_DATE()
            AND o.IS_OPEN = 1
            AND o.IS_CLOSED = FALSE
        ),
        fivetran_opps AS (
            SELECT
                a.NAME AS ACCOUNT_NAME,
                a.ID AS SALESFORCE_ACCOUNT_ID,
                opp.NAME AS OPPORTUNITY_NAME,
                opp.ID AS OPPORTUNITY_ID,
                opp.TYPE AS OPPORTUNITY_TYPE,
                opp.STAGE_NAME,
                opp.FORECAST_CATEGORY_NAME AS FORECAST_STATUS,
                CAST(opp.AMOUNT AS FLOAT) AS TOTAL_ACV,
                opp.CLOSE_DATE,
                CAST(opp.FISCAL_QUARTER AS VARCHAR) AS FISCAL_QUARTER,
                opp.LEAN_DATA_DAYS_IN_STAGE_C AS DAYS_IN_STAGE,
                u.NAME AS OWNER,
                a.ACCOUNT_OWNER_MANAGER_C AS DM,
                opp.CREATED_DATE,
                CAST(opp.PROBABILITY AS FLOAT) AS OPP_PROBABILITY,
                NULL AS MEDDPICC_SCORE,
                NULL AS SALES_QUALIFIED_DATE,
                NULL AS SE_COMMENTS,
                opp.NEXT_STEP AS NEXT_STEPS
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
            JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON opp.ACCOUNT_ID = a.ID
            LEFT JOIN FIVETRAN.SALESFORCE.USER u ON opp.OWNER_ID = u.ID
            WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
            AND a.ACCOUNT_STATUS_C = 'Active'
            AND opp.IS_CLOSED = FALSE
            AND opp.IS_DELETED = FALSE
            AND opp.ID NOT IN (SELECT OPPORTUNITY_ID FROM sda_opps)
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
            tf.MEDDPICC_SCORE,
            tf.SALES_QUALIFIED_DATE,
            tf.SE_COMMENTS,
            tf.NEXT_STEPS,
            ps.PS_SERVICE_TYPE,
            ps.PS_SELLER_NAME,
            ps.PS_INVESTMENT_TYPE,
            CAST(ps.PS_SERVICES_TCV AS FLOAT) AS PS_SERVICES_TCV,
            CAST(ps.EDUCATION_SERVICES_TCV AS FLOAT) AS EDUCATION_SERVICES_TCV,
            CAST(COALESCE(ps.PS_SERVICES_TCV, 0) AS FLOAT) + CAST(COALESCE(ps.EDUCATION_SERVICES_TCV, 0) AS FLOAT) AS TOTAL_PST_TCV,
            CAST(ps.PS_SERVICES_FORECAST AS FLOAT) AS PS_SERVICES_FORECAST,
            CAST(ps.EDUCATION_SERVICES_FORECAST AS FLOAT) AS EDUCATION_SERVICES_FORECAST,
            ps.PS_FORECAST_CATEGORY,
            ps.QUOTE_SUB_AGREEMENT_TYPE,
            pr.PRODUCT_NAMES
        FROM ts_filtered tf
        LEFT JOIN SALES.RAVEN.SDA_OPPORTUNITY_PS_VIEW ps ON tf.OPPORTUNITY_ID = ps.OPPORTUNITY_ID
        LEFT JOIN products pr ON tf.OPPORTUNITY_ID = pr.OPPORTUNITY_ID
        ORDER BY tf.CLOSE_DATE ASC
    """).to_pandas()
    return _fix_decimals(df)



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
            a.ACCOUNT_OWNER_NAME_C AS AE,
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
        JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON opp.ACCOUNT_ID = a.ID
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
def load_action_planner_pipeline():
    session = _get_session()
    df = session.sql("""
        SELECT
            a.NAME AS ACCOUNT_NAME,
            a.ID AS ACCOUNT_ID,
            u.DISTRICT_C AS DISTRICT,
            a.ACCOUNT_OWNER_NAME_C AS AE_NAME,
            raven.LEAD_SALES_ENGINEER_NAME AS SE_NAME,
            v.DELIVERABLE_ID AS USE_CASE_ID,
            v.DELIVERABLE_NAME AS USE_CASE_NAME,
            COALESCE(d.USE_CASE_STAGE, v.NEW_STAGE) AS STAGE,
            COALESCE(d.USE_CASE_STATUS, v.USE_CASE_STATUS_C) AS USE_CASE_STATUS,
            CAST(COALESCE(d.USE_CASE_EACV, v.ACV_C) AS FLOAT) AS EACV,
            v.TECHNICAL_USE_CASE_C AS TECHNICAL_UC,
            v.USE_CASE_DESCRIPTION,
            v.WORKLOADS,
            v.COMPETITORS,
            v.INCUMBENT_VENDOR_C AS INCUMBENT_VENDOR,
            v.IMPLEMENTER_C AS IMPLEMENTER,
            v.USE_CASE_COMMENTS,
            v.NEXT_STEPS_C AS NEXT_STEPS,
            v.USE_CASE_RISK,
            v.USE_CASE_NUMBER,
            v.PARTNERS_C AS PARTNERS,
            v.INDUSTRY_USE_CASE_C AS INDUSTRY_UC,
            d.SE_COMMENTS AS SE_COMMENTS_FULL
        FROM FIVETRAN.SALESFORCE.ACCOUNT a
        JOIN FIVETRAN.SALESFORCE.USER u ON a.OWNER_ID = u.ID
        LEFT JOIN SALES.RAVEN.D_SALESFORCE_ACCOUNT_CUSTOMERS raven ON a.ID = raven.SALESFORCE_ACCOUNT_ID
        LEFT JOIN SALES.SE_REPORTING.VIVUN_DELIVERABLE_USE_CASE v ON v.ACCOUNT_ID = a.ID
        LEFT JOIN MDM.MDM_INTERFACES.DIM_USE_CASE d ON v.USE_CASE_NUMBER = d.USE_CASE_NUMBER
        WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS_C = 'Active'
        ORDER BY a.NAME, v.ACV_C DESC NULLS LAST
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_account_consumption_summary(account_name):
    session = _get_session()
    df = session.sql(f"""
        WITH monthly AS (
            SELECT
                p.MONTH,
                p.PRODUCT_CATEGORY,
                p.USE_CASE,
                p.PRIMARY_FEATURE,
                CAST(SUM(p.TOTAL_CREDITS) AS FLOAT) AS CREDITS
            FROM SALES.RAVEN.A360_PRODUCT_CATEGORY_VIEW p
            WHERE p.SALESFORCE_ACCOUNT_ID IN (
                SELECT ID FROM FIVETRAN.SALESFORCE.ACCOUNT
                WHERE NAME = '{account_name.replace("'", "''")}'
                AND ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
            )
            AND p.MONTH >= DATEADD(MONTH, -6, CURRENT_DATE())
            GROUP BY p.MONTH, p.PRODUCT_CATEGORY, p.USE_CASE, p.PRIMARY_FEATURE
        )
        SELECT * FROM monthly WHERE CREDITS > 0
        ORDER BY PRODUCT_CATEGORY, MONTH
    """).to_pandas()
    return _fix_decimals(df)


def generate_cortex_response(prompt_text, model="claude-3-5-sonnet"):
    session = _get_session()
    escaped = prompt_text.replace("'", "''")
    result = session.sql(
        f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped}') AS response"
    ).to_pandas()
    return result.iloc[0]["RESPONSE"]


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
            SELECT ID
            FROM FIVETRAN.SALESFORCE.ACCOUNT
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


@st.cache_data(ttl=86400)
def load_exec_software_renewals():
    session = _get_session()
    df = session.sql("""
        SELECT
            o.ACCOUNT_NAME,
            o.SALESFORCE_ACCOUNT_ID,
            o.OPPORTUNITY_NAME,
            o.OPPORTUNITY_ID,
            o.STAGE_NAME,
            o.FORECAST_STATUS,
            CAST(o.TOTAL_ACV AS FLOAT) AS TOTAL_ACV,
            CAST(o.RENEWAL_ACV AS FLOAT) AS RENEWAL_ACV,
            o.CLOSE_DATE,
            o.FISCAL_QUARTER,
            o.OPPORTUNITY_OWNER_NAME AS OWNER,
            o.NEXT_STEPS,
            o.DM
        FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
        WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
        AND o.DS = CURRENT_DATE()
        AND o.IS_OPEN = 1
        AND o.IS_CLOSED = FALSE
        AND o.OPPORTUNITY_TYPE = 'Renewal'
        AND o.CLOSE_DATE BETWEEN CURRENT_DATE() AND DATEADD(MONTH, 6, CURRENT_DATE())
        ORDER BY o.CLOSE_DATE ASC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_services_renewals():
    session = _get_session()
    df = session.sql("""
        SELECT
            p.NAME AS PROJECT_NAME,
            p.ID AS PROJECT_ID,
            a.NAME AS ACCOUNT_NAME,
            a.ID AS SALESFORCE_ACCOUNT_ID,
            a.ACCOUNT_OWNER_MANAGER_C AS DM,
            a.ACCOUNT_OWNER_NAME_C AS AE,
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
        JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON p.PSE_ACCOUNT_C = a.ID
        LEFT JOIN FIVETRAN.SALESFORCE.CONTACT c ON p.PSE_PROJECT_MANAGER_C = c.ID
        WHERE a.ACCOUNT_OWNER_MANAGER_C IN ('Erik Schneider', 'Raymond Navarro')
        AND a.ACCOUNT_STATUS_C = 'Active'
        AND p.IS_DELETED = FALSE
        AND p.PSE_IS_ACTIVE_C = TRUE
        AND p.PSE_STAGE_C IN ('In Progress', 'Stalled', 'Stalled - Expiring', 'Pipeline', 'Out Year')
        AND p.PSE_END_DATE_C BETWEEN CURRENT_DATE() AND DATEADD(MONTH, 6, CURRENT_DATE())
        ORDER BY p.PSE_END_DATE_C ASC
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_new_opps():
    session = _get_session()
    df = session.sql("""
        WITH sda_new AS (
            SELECT
                o.ACCOUNT_NAME,
                o.SALESFORCE_ACCOUNT_ID,
                o.OPPORTUNITY_NAME,
                o.OPPORTUNITY_ID,
                o.OPPORTUNITY_TYPE,
                o.STAGE_NAME,
                o.FORECAST_STATUS,
                CAST(o.TOTAL_ACV AS FLOAT) AS TOTAL_ACV,
                o.CLOSE_DATE,
                o.CREATED_DATE,
                o.OPPORTUNITY_OWNER_NAME AS OWNER,
                o.DM,
                ft.AGREEMENT_TYPE_C AS AGREEMENT_TYPE
            FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
            LEFT JOIN FIVETRAN.SALESFORCE.OPPORTUNITY ft ON o.OPPORTUNITY_ID = ft.ID
            WHERE o.DM IN ('Erik Schneider', 'Raymond Navarro')
            AND o.DS = CURRENT_DATE()
            AND o.CREATED_DATE >= DATEADD('day', -90, CURRENT_DATE())
        ),
        fivetran_new AS (
            SELECT
                a.NAME AS ACCOUNT_NAME,
                a.ID AS SALESFORCE_ACCOUNT_ID,
                opp.NAME AS OPPORTUNITY_NAME,
                opp.ID AS OPPORTUNITY_ID,
                opp.TYPE AS OPPORTUNITY_TYPE,
                opp.STAGE_NAME,
                opp.FORECAST_CATEGORY_NAME AS FORECAST_STATUS,
                CAST(opp.AMOUNT AS FLOAT) AS TOTAL_ACV,
                opp.CLOSE_DATE,
                opp.CREATED_DATE,
                u.NAME AS OWNER,
                a.ACCOUNT_OWNER_MANAGER_C AS DM,
                opp.AGREEMENT_TYPE_C AS AGREEMENT_TYPE
            FROM FIVETRAN.SALESFORCE.OPPORTUNITY opp
            JOIN FIVETRAN.SALESFORCE.ACCOUNT a ON opp.ACCOUNT_ID = a.ID
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
    """).to_pandas()
    return _fix_decimals(df)


@st.cache_data(ttl=86400)
def load_exec_new_use_cases():
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
            uc.OWNER_NAME AS OWNER,
            uc.NEXT_STEPS,
            uc.ACCOUNT_DM AS DM,
            uc.USE_CASE_ID,
            uc.USE_CASE_NUMBER
        FROM MDM.MDM_INTERFACES.DIM_USE_CASE uc
        WHERE uc.ACCOUNT_DM IN ('Erik Schneider', 'Raymond Navarro')
        AND uc.USE_CASE_STAGE IS NOT NULL
        AND uc.IS_LOST = FALSE
        AND uc.CREATED_DATE >= DATEADD('day', -90, CURRENT_DATE())
        ORDER BY uc.CREATED_DATE DESC
    """).to_pandas()
    return _fix_decimals(df)
