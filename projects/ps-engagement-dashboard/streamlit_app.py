"""
PS Engagement & Go-Live Dashboard  (v3 — Crystalline Lab)
Streamlit in Snowflake (SiS) app for district-level PS visibility.

Design system: "The Crystalline Lab"
  Primary #006686 · Accent #29B5E8 · Surface #F9F9FF · Cards #FFFFFF
  Manrope headlines · Inter body · no-line rule (tonal separation)

Layout (Stitch v3 mock):
  Row 0  – Header + subtitle
  Row 1  – 6 KPI metric cards (horizontal)
  Row 2  – Tabbed toggle: District Engagement | Regional POV
  Row 3  – Two-column: Go-Live Readiness + Engagement Opportunity
  Row 4  – Delivery Risk & Action
  Row 5  – Detail Tables (4 tabs)

Data sources:
  - Projects: Smartsheet SFDC Connector
  - Use Cases: PST.PS_APPS_DEV.SDA_USE_CASES_CACHE
  - Themes: PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
  - Snapshots: PST.PS_APPS_DEV.PS_DASHBOARD_SNAPSHOTS (WoW deltas)
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from collections import Counter

# ── Page Config ─────────────────────────────────────────
st.set_page_config(page_title="PS Engagement Dashboard", layout="wide")

# ── Crystalline Lab CSS ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

/* Surface background */
[data-testid="stAppViewContainer"] { background-color: #F9F9FF; }
[data-testid="stSidebar"] { background-color: #F1F3FF; }

/* Header typography */
h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: #141B2B !important; }
h1 { font-weight: 800 !important; }
h2 { font-weight: 700 !important; font-size: 1.3rem !important; }

/* Body text */
p, span, div, label, [data-testid="stText"] {
    font-family: 'Inter', sans-serif !important;
}

/* Metric cards — white on surface, no border lines */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    color: #5A6578 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    color: #006686 !important;
}

/* Tab styling */
[data-testid="stTabs"] button {
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #006686 !important;
    border-bottom-color: #29B5E8 !important;
}

/* Remove default Streamlit dividers — no-line rule */
hr { display: none !important; }

/* Plotly chart containers */
.stPlotlyChart { border-radius: 12px; }

/* Table styling — zebra, no lines */
[data-testid="stDataFrame"] th {
    background: #F1F3FF !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Constants ───────────────────────────────────────────
VALID_REGIONS = {
    "CanadaExp", "CentralExp", "Commercial", "USGrowthExp",
    "NortheastExp", "NorthwestExp", "SoutheastExp", "SouthwestExp",
    "CommAcqEast", "CommAcqWest",
    "EntAcqCentral", "EntAcqEast", "EntAcqWest",
    "LATAM",
}
PS_ROLES = ["Implementation", "Advisory", "Proposing", "Support"]

SMARTSHEET_TABLE = (
    "SMARTSHEET_DB.RAW_SMARTSHEET"
    ".SHEET_1030823650217860_SFDC_CONNECTOR_SHEET_PROJECTS"
)
SDA_CACHE = "PST.PS_APPS_DEV.SDA_USE_CASES_CACHE"

SF_PS_IMPL = {"Snowflake SD Prime", "Partner Prime + Snowflake SD",
              "Customer Prime + Snowflake SD"}

# Crystalline Lab color palette for charts
CLR_PRIMARY = "#006686"
CLR_ACCENT = "#29B5E8"
CLR_SURFACE = "#F9F9FF"
CLR_CARD = "#FFFFFF"
CLR_TEXT = "#141B2B"
CLR_MUTED = "#5A6578"
CLR_GREEN = "#0D9373"
CLR_AMBER = "#E8A317"
CLR_RED = "#D64045"

# Chart color sequence (for stacked bars, donut, etc.)
CHART_COLORS = ["#006686", "#29B5E8", "#0D9373", "#E8A317", "#8B5CF6", "#D64045"]


# ── Helpers ─────────────────────────────────────────────

def fy_quarter(d):
    """Return (q_num, fy_year) for the Snowflake FY quarter containing d."""
    m, y = d.month, d.year
    if m == 1:
        return 4, y
    elif m <= 4:
        return 1, y + 1
    elif m <= 7:
        return 2, y + 1
    elif m <= 10:
        return 3, y + 1
    else:
        return 4, y + 1


def quarter_label(q, fy):
    return f"Q{q} FY{fy % 100:02d}"


def quarter_dates(q, fy):
    cal = fy - 1
    if q == 1:
        return date(cal, 2, 1), date(cal, 4, 30)
    elif q == 2:
        return date(cal, 5, 1), date(cal, 7, 31)
    elif q == 3:
        return date(cal, 8, 1), date(cal, 10, 31)
    else:
        return date(cal, 11, 1), date(cal + 1, 1, 31)


def step_quarter(q, fy, steps):
    idx = (fy - 2000) * 4 + (q - 1) + steps
    return (idx % 4) + 1, 2000 + idx // 4


def nearby_quarter_labels(d, n_back=1, n_forward=2):
    cur_q, cur_fy = fy_quarter(d)
    labels = []
    for offset in range(-n_back, n_forward + 1):
        q, fy = step_quarter(cur_q, cur_fy, offset)
        labels.append(quarter_label(q, fy))
    return labels


def parse_quarter_label(label):
    parts = label.split()
    return int(parts[0][1]), 2000 + int(parts[1][2:])


def fmt_acv(v):
    if pd.isna(v) or v == 0:
        return "$0"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:.0f}"


def health_summary(row):
    m = {"Green": "G", "Yellow": "Y", "Red": "R"}
    return "/".join(
        m.get(row.get(c, ""), "-")
        for c in ["PROJECT_STATUS", "SCOPE_HEALTH",
                   "SCHEDULE_HEALTH", "CONSUMPTION_HEALTH"]
    )


def top_workloads(series, n=3):
    counts = Counter()
    for val in series.dropna():
        for w in str(val).split(";"):
            w = w.strip()
            if w:
                counts[w] += 1
    return ", ".join(w for w, _ in counts.most_common(n))


def issue_description(row):
    issues = []
    for label, col in [("Status", "PROJECT_STATUS"), ("Scope", "SCOPE_HEALTH"),
                        ("Schedule", "SCHEDULE_HEALTH")]:
        val = row.get(col, "")
        if val in ("Yellow", "Red"):
            issues.append(f"{label} {val.lower()}")
    hrs = row.get("HRS_REM")
    if pd.notna(hrs) and hrs < 0:
        issues.append(f"{abs(hrs):.0f} hrs overrun")
    return "; ".join(issues) if issues else "On track"


def suggested_action(row):
    actions = []
    if row.get("SCOPE_HEALTH") in ("Yellow", "Red"):
        actions.append("Scope review with PM + customer")
    if row.get("SCHEDULE_HEALTH") in ("Yellow", "Red"):
        actions.append("Timeline re-baseline needed")
    hrs = row.get("HRS_REM")
    if pd.notna(hrs) and hrs < 0:
        actions.append("SOW amendment or scope reduction")
    if row.get("PROJECT_STATUS") in ("Red",):
        actions.append("Escalate to leadership")
    return "; ".join(actions) if actions else "-"


def in_selected_quarters(dates, quarter_ranges):
    mask = pd.Series(False, index=dates.index)
    for qs, qe in quarter_ranges:
        mask = mask | ((dates >= qs) & (dates <= qe))
    return mask


def plotly_layout(title="", height=380):
    """Return a Crystalline Lab-styled Plotly layout dict."""
    return dict(
        title=dict(text=title, font=dict(family="Manrope", size=16, color=CLR_TEXT)),
        paper_bgcolor=CLR_CARD,
        plot_bgcolor=CLR_CARD,
        font=dict(family="Inter", size=12, color=CLR_MUTED),
        margin=dict(l=40, r=20, t=50, b=40),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )


# ── Cached Data Loaders ────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Loading project data...")
def load_projects():
    s = get_active_session()
    return s.sql(f"""
        SELECT
            PROJECT_ID, ACCOUNT_NAME, PROJECT_NAME, PROJECT_MANAGER,
            TRY_TO_DATE(END_DATE) AS END_DT,
            PROJECT_STATUS, SCOPE_HEALTH, SCHEDULE_HEALTH, CONSUMPTION_HEALTH,
            SERVICE_TYPE, INVESTMENT_TYPE, BILLING_TYPE,
            TRY_TO_DOUBLE(BILLABLE_HOURS)   AS HRS_USED,
            TRY_TO_DOUBLE(REMAINING_HOURS)  AS HRS_REM,
            PROJECT_STATUS_COMMENTS
        FROM {SMARTSHEET_TABLE}
        WHERE ACTIVE = 'true'
        ORDER BY ACCOUNT_NAME, PROJECT_NAME
    """).to_pandas()


@st.cache_data(ttl=3600, show_spinner="Loading use case data...")
def load_use_cases():
    s = get_active_session()
    return s.sql(f"""
        SELECT
            ACCOUNT_NAME, USE_CASE_NAME, USE_CASE_STAGE, USE_CASE_ACV,
            PS_ENGAGEMENT, IS_PS_ENGAGED, IMPLEMENTER,
            WORKLOADS, COMPETITORS,
            REGION, SUB_REGION, DISTRICT, TERRITORY,
            SEGMENT, ACCOUNT_TIER, INDUSTRY, ARR,
            GO_LIVE_DATE, DAYS_IN_STAGE, CACHE_REFRESHED_AT
        FROM {SDA_CACHE}
        ORDER BY ACCOUNT_NAME, USE_CASE_NAME
    """).to_pandas()


@st.cache_data(ttl=3600, show_spinner="Loading engagement themes...")
def load_themes():
    s = get_active_session()
    return s.sql("""
        SELECT DISTRICT, REGION, ENGAGEMENT_TYPE, ACCOUNT_COUNT,
               ACCOUNTS_WITH_STATUS, THEME_SUMMARY, REFRESHED_AT
        FROM PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE
    """).to_pandas()


@st.cache_data(ttl=3600, show_spinner="Loading snapshots...")
def load_snapshots():
    s = get_active_session()
    try:
        return s.sql("""
            SELECT * FROM PST.PS_APPS_DEV.PS_DASHBOARD_SNAPSHOTS
            ORDER BY SNAPSHOT_DATE DESC
        """).to_pandas()
    except Exception:
        return pd.DataFrame()


# ── Load & Normalize ───────────────────────────────────
projects_all = load_projects()
use_cases_all = load_use_cases()
themes_all = load_themes()
snapshots = load_snapshots()

projects_all["END_DT"] = pd.to_datetime(projects_all["END_DT"], errors="coerce")
use_cases_all["GO_LIVE_DATE"] = pd.to_datetime(
    use_cases_all["GO_LIVE_DATE"], errors="coerce"
)
use_cases_all = use_cases_all[use_cases_all["REGION"].isin(VALID_REGIONS)].copy()
use_cases_all["STAGE_CLEAN"] = (
    use_cases_all["USE_CASE_STAGE"]
    .str.replace(r"^\d+\s*-\s*", "", regex=True)
)


# ── Sidebar Filters ─────────────────────────────────────
today = date.today()
cur_q, cur_fy = fy_quarter(today)
cur_label = quarter_label(cur_q, cur_fy)

with st.sidebar:
    st.markdown(
        '<h2 style="color:#006686; margin-bottom:4px;">PS Dashboard</h2>',
        unsafe_allow_html=True,
    )
    st.caption(f"{cur_label}  ·  {today.strftime('%B %d, %Y')}")

    # Quarter selector
    q_options = nearby_quarter_labels(today, n_back=1, n_forward=3)
    sel_quarters = st.multiselect(
        "Quarter(s)", q_options, default=[cur_label],
    )
    if not sel_quarters:
        sel_quarters = [cur_label]

    # Region filter
    regions = sorted(use_cases_all["REGION"].dropna().unique().tolist())
    default_regions = [r for r in regions if r == "SouthwestExp"] or regions[:1]
    sel_regions = st.multiselect("Region", regions, default=default_regions)

    # District filter — cascaded
    avail_districts = sorted(
        use_cases_all[use_cases_all["REGION"].isin(sel_regions)]["DISTRICT"]
        .dropna().unique().tolist()
    ) if sel_regions else sorted(
        use_cases_all["DISTRICT"].dropna().unique().tolist()
    )
    sel_districts = st.multiselect(
        "District", avail_districts, default=avail_districts,
    )

    # Filter use cases by district
    uc = use_cases_all[use_cases_all["DISTRICT"].isin(sel_districts)].copy()

    # Cross-filter projects to accounts in selected districts
    district_accounts = set(uc["ACCOUNT_NAME"].dropna().unique())
    proj = projects_all[
        projects_all["ACCOUNT_NAME"].isin(district_accounts)
    ].copy()

    # Implementer filter
    impl_vals = sorted(uc["IMPLEMENTER"].dropna().unique().tolist())
    sel_impl = st.multiselect("Implementer", impl_vals)

    # PM filter
    pms = sorted(proj["PROJECT_MANAGER"].dropna().unique().tolist())
    sel_pm = st.multiselect("Project Manager", pms)

    # Cache info + refresh
    if "CACHE_REFRESHED_AT" in use_cases_all.columns:
        refreshed = pd.to_datetime(
            use_cases_all["CACHE_REFRESHED_AT"], errors="coerce"
        ).max()
        if pd.notna(refreshed):
            st.caption(f"UC data: {refreshed.strftime('%b %d, %Y %H:%M')} UTC")
    if st.button("Refresh cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# Apply secondary filters
if sel_impl:
    uc = uc[uc["IMPLEMENTER"].isin(sel_impl)].copy()

proj_view = (
    proj[proj["PROJECT_MANAGER"].isin(sel_pm)].copy()
    if sel_pm else proj.copy()
)


# ── Enrich Use Cases with Project Context ──────────────
_pctx = proj.copy()
_pctx["_HEALTH"] = _pctx.apply(health_summary, axis=1)
_pctx["_PROJ_LINE"] = _pctx["PROJECT_NAME"] + " (" + _pctx["_HEALTH"] + ")"

acct_proj_ctx = (
    _pctx.groupby("ACCOUNT_NAME")
    .agg(
        PS_PROJECT=("_PROJ_LINE", lambda x: " | ".join(x)),
        PS_PM=("PROJECT_MANAGER", lambda x: ", ".join(sorted(x.dropna().unique()))),
        PS_STATUS=("PROJECT_STATUS_COMMENTS", lambda x: " | ".join(x.dropna())),
    )
    .reset_index()
)
uc = uc.merge(acct_proj_ctx, on="ACCOUNT_NAME", how="left")


# ── Multi-Quarter Date Ranges ──────────────────────────
quarter_ranges = []
for ql in sel_quarters:
    q_num, fy = parse_quarter_label(ql)
    qs, qe = quarter_dates(q_num, fy)
    start = today if ql == cur_label else qs
    quarter_ranges.append((pd.Timestamp(start), pd.Timestamp(qe)))

today_ts = pd.Timestamp(today)
q_label_str = ", ".join(sel_quarters)


# ── Derived Metrics ────────────────────────────────────
ps_engaged = uc[
    uc["PS_ENGAGEMENT"].isin(PS_ROLES)
    | (uc["IS_PS_ENGAGED"] == True)  # noqa: E712
].copy()
role_n = {r: len(ps_engaged[ps_engaged["PS_ENGAGEMENT"] == r]) for r in PS_ROLES}

# Go-live forecast
golive_q = uc[
    uc["GO_LIVE_DATE"].notna()
    & in_selected_quarters(uc["GO_LIVE_DATE"], quarter_ranges)
]

# At-risk projects
proj_view["HEALTH"] = proj_view.apply(health_summary, axis=1)
at_risk = proj_view[
    proj_view["PROJECT_STATUS"].isin(["Yellow", "Red"])
    | proj_view["SCOPE_HEALTH"].isin(["Yellow", "Red"])
    | proj_view["SCHEDULE_HEALTH"].isin(["Yellow", "Red"])
    | (proj_view["HRS_REM"].fillna(0) < 0)
]

# Unengaged use cases (opportunity)
not_engaged = uc[
    ~uc["PS_ENGAGEMENT"].isin(PS_ROLES)
    & (uc["IS_PS_ENGAGED"] != True)  # noqa: E712
    & uc["STAGE_CLEAN"].isin([
        "Discovery", "Scoping", "Technical / Business Validation",
        "Use Case Won / Migration Plan", "Implementation In Progress",
    ])
].copy()

# PS-engaged ACV
total_acv = ps_engaged["USE_CASE_ACV"].fillna(0).sum()

# SF PS-Led percentage
sf_led = ps_engaged["IMPLEMENTER"].isin(SF_PS_IMPL).sum()
sf_pct = (sf_led * 100 // len(ps_engaged)) if len(ps_engaged) > 0 else 0

# Pre-compute ACV display column on ps_engaged (needed by detail tabs)
ps_engaged["ACV"] = ps_engaged["USE_CASE_ACV"].apply(fmt_acv)

# Flag-only (unspecified role) — must come after ACV column is added
flag_only = ps_engaged[~ps_engaged["PS_ENGAGEMENT"].isin(PS_ROLES)]
role_n["Unspecified"] = len(flag_only)

# WoW deltas (graceful — requires >= 2 snapshot dates)
wow_deltas = {}
if len(snapshots) > 0 and "SNAPSHOT_DATE" in snapshots.columns:
    snap_dates = sorted(snapshots["SNAPSHOT_DATE"].unique(), reverse=True)
    if len(snap_dates) >= 2:
        curr_snap = snapshots[snapshots["SNAPSHOT_DATE"] == snap_dates[0]].iloc[0]
        prev_snap = snapshots[snapshots["SNAPSHOT_DATE"] == snap_dates[1]].iloc[0]
        for col in ["ACTIVE_PROJECTS", "GO_LIVES", "PS_ENGAGED_UCS",
                     "PS_ENGAGED_EACV", "AT_RISK"]:
            if col in curr_snap.index and col in prev_snap.index:
                try:
                    wow_deltas[col] = int(curr_snap[col]) - int(prev_snap[col])
                except (ValueError, TypeError):
                    pass


# ══════════════════════════════════════════════════════════
# ROW 0: Header
# ══════════════════════════════════════════════════════════
st.markdown(
    f'<h1 style="margin-bottom:0;">PS Engagement & Go-Live Dashboard</h1>',
    unsafe_allow_html=True,
)
st.caption(
    f"{' · '.join(sel_districts)}  ·  {q_label_str}  ·  {today.strftime('%B %d, %Y')}"
)


# ══════════════════════════════════════════════════════════
# ROW 1: KPI Cards (two rows of 3 for readability)
# ══════════════════════════════════════════════════════════
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1.container(border=True):
    st.metric("Active Projects", len(proj_view),
              delta=wow_deltas.get("ACTIVE_PROJECTS"))
with r1c2.container(border=True):
    st.metric("Go-Lives This Quarter", len(golive_q),
              delta=wow_deltas.get("GO_LIVES"))
with r1c3.container(border=True):
    st.metric("PS-Engaged Use Cases", len(ps_engaged),
              delta=wow_deltas.get("PS_ENGAGED_UCS"))

r2c1, r2c2, r2c3 = st.columns(3)
with r2c1.container(border=True):
    st.metric("PS-Engaged EACV", fmt_acv(total_acv))
with r2c2.container(border=True):
    st.metric("SF PS-Led %", f"{sf_pct}%")
with r2c3.container(border=True):
    st.metric("At Risk Projects", len(at_risk),
              delta=wow_deltas.get("AT_RISK"),
              delta_color="inverse")


# ══════════════════════════════════════════════════════════
# ROW 2: District Engagement / Regional POV Toggle
# ══════════════════════════════════════════════════════════
view_tab1, view_tab2 = st.tabs(["District Engagement", "Regional POV"])

# ── Tab 1: District Engagement (stacked horizontal bar) ──
with view_tab1:
    # Build district-level EACV by engagement type
    dist_data = []
    for district in sorted(ps_engaged["DISTRICT"].dropna().unique()):
        d_engaged = ps_engaged[ps_engaged["DISTRICT"] == district]
        row = {"District": district}
        for role in PS_ROLES:
            subset = d_engaged[d_engaged["PS_ENGAGEMENT"] == role]
            row[role] = subset["USE_CASE_ACV"].fillna(0).sum()
        unspec = d_engaged[~d_engaged["PS_ENGAGEMENT"].isin(PS_ROLES)]
        row["Unspecified"] = unspec["USE_CASE_ACV"].fillna(0).sum()
        row["_total"] = sum(row[r] for r in PS_ROLES + ["Unspecified"])
        dist_data.append(row)

    if dist_data:
        dist_df = pd.DataFrame(dist_data).sort_values("_total", ascending=True)

        fig_dist = go.Figure()
        for i, role in enumerate(PS_ROLES + ["Unspecified"]):
            fig_dist.add_trace(go.Bar(
                y=dist_df["District"],
                x=dist_df[role],
                name=role,
                orientation="h",
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                hovertemplate="%{y}<br>" + role + ": $%{x:,.0f}<extra></extra>",
            ))
        fig_dist.update_layout(
            **plotly_layout("EACV by District & Engagement Type", height=max(300, len(dist_df) * 40 + 100)),
            barmode="stack",
            xaxis=dict(title="Estimated ACV ($)", tickformat="$,.0f"),
            yaxis=dict(title=""),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        # UC count by district — compact donut
        col_donut, col_table = st.columns([1, 2])
        with col_donut:
            uc_by_dist = ps_engaged.groupby("DISTRICT").size().reset_index(name="UCs")
            fig_donut = go.Figure(go.Pie(
                labels=uc_by_dist["DISTRICT"],
                values=uc_by_dist["UCs"],
                hole=0.55,
                marker=dict(colors=CHART_COLORS[:len(uc_by_dist)]),
                textinfo="label+value",
                textfont=dict(family="Inter", size=11),
            ))
            fig_donut.update_layout(**plotly_layout("PS-Engaged UCs by District", height=300))
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_table:
            # Summary table: district, total UCs, total EACV, top workloads
            summary_rows = []
            for d in sorted(ps_engaged["DISTRICT"].dropna().unique()):
                sub = ps_engaged[ps_engaged["DISTRICT"] == d]
                summary_rows.append({
                    "District": d,
                    "UCs": len(sub),
                    "EACV": fmt_acv(sub["USE_CASE_ACV"].fillna(0).sum()),
                    "Top Workloads": top_workloads(sub["WORKLOADS"]),
                    "SF PS-Led": f"{(sub['IMPLEMENTER'].isin(SF_PS_IMPL).sum() * 100 // max(len(sub), 1))}%",
                })
            if summary_rows:
                st.dataframe(
                    pd.DataFrame(summary_rows),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "District": st.column_config.TextColumn("District", width="small"),
                        "UCs": st.column_config.NumberColumn("UCs", format="%d", width="small"),
                        "EACV": st.column_config.TextColumn("EACV", width="small"),
                        "Top Workloads": st.column_config.TextColumn("Top Workloads", width="large"),
                        "SF PS-Led": st.column_config.TextColumn("SF PS-Led%", width="small"),
                    },
                )
    else:
        st.info("No PS-engaged use cases in selected districts.")

# ── Tab 2: Regional POV (thematic narrative) ──
with view_tab2:
    active_regions = sorted(ps_engaged["REGION"].dropna().unique())

    # National-level PS contribution table
    _nat_engaged = use_cases_all[
        use_cases_all["PS_ENGAGEMENT"].isin(PS_ROLES)
        | (use_cases_all["IS_PS_ENGAGED"] == True)  # noqa: E712
    ].copy()
    _nat_flag = _nat_engaged[~_nat_engaged["PS_ENGAGEMENT"].isin(PS_ROLES)]

    national_themes = {}
    for _, tr in themes_all[themes_all["REGION"] == "NATIONAL"].iterrows():
        national_themes[tr["ENGAGEMENT_TYPE"]] = (
            tr["THEME_SUMMARY"].strip().strip(",") if pd.notna(tr["THEME_SUMMARY"]) else "-"
        )

    nat_rows = []
    for role in PS_ROLES:
        subset = _nat_engaged[_nat_engaged["PS_ENGAGEMENT"] == role]
        if len(subset) == 0:
            continue
        nat_rows.append({
            "Engagement Type": role,
            "Use Cases": len(subset),
            "EACV": fmt_acv(subset["USE_CASE_ACV"].fillna(0).sum()),
            "Top Workloads": top_workloads(subset["WORKLOADS"]),
            "What We're Doing": national_themes.get(role, "-"),
        })
    if len(_nat_flag) > 0:
        nat_rows.append({
            "Engagement Type": "Unspecified*",
            "Use Cases": len(_nat_flag),
            "EACV": fmt_acv(_nat_flag["USE_CASE_ACV"].fillna(0).sum()),
            "Top Workloads": top_workloads(_nat_flag["WORKLOADS"]),
            "What We're Doing": national_themes.get("Unspecified", "-"),
        })

    if nat_rows:
        st.markdown("**PS Contribution by Engagement Type** (National)")
        st.dataframe(
            pd.DataFrame(nat_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Engagement Type": st.column_config.TextColumn("Engagement Type", width="small"),
                "Use Cases": st.column_config.NumberColumn("Use Cases", format="%d", width="small"),
                "EACV": st.column_config.TextColumn("EACV", width="small"),
                "Top Workloads": st.column_config.TextColumn("Top Workloads", width="medium"),
                "What We're Doing": st.column_config.TextColumn("What We're Doing", width="large"),
            },
        )

    # Regional theme table
    if len(active_regions) > 0:
        _eng_order = {"Advisory": 0, "Implementation": 1, "Proposing": 2,
                      "Support": 3, "Unspecified": 4}
        _pov_rows = []
        for _, tr in themes_all[
            themes_all["REGION"].isin(active_regions)
            & (themes_all["ENGAGEMENT_TYPE"] != "_POV")
            & (themes_all["REGION"] != "NATIONAL")
        ].iterrows():
            eng = tr["ENGAGEMENT_TYPE"]
            district = tr["DISTRICT"] if pd.notna(tr.get("DISTRICT")) else None
            summary = tr["THEME_SUMMARY"].strip().strip(",") if pd.notna(tr["THEME_SUMMARY"]) else "-"
            _pov_rows.append({
                "Engagement Type": eng if eng != "Unspecified" else "Unspecified*",
                "Region": tr["REGION"],
                "District": district if district else "",
                "Themes": summary,
                "_sort_eng": _eng_order.get(eng, 5),
                "_is_region": 0 if district else 1,
            })

        if _pov_rows:
            st.markdown("**Regional Thematic POV**")
            pov_df = pd.DataFrame(_pov_rows)
            pov_df = pov_df.sort_values(
                ["Region", "_sort_eng", "_is_region", "District"]
            ).drop(columns=["_sort_eng", "_is_region"])

            st.dataframe(
                pov_df,
                use_container_width=True,
                hide_index=True,
                height=min(len(pov_df) * 35 + 40, 600),
                column_config={
                    "Engagement Type": st.column_config.TextColumn("Engagement Type", width="small"),
                    "Region": st.column_config.TextColumn("Region", width="small"),
                    "District": st.column_config.TextColumn("District", width="small"),
                    "Themes": st.column_config.TextColumn("Themes", width="large"),
                },
            )

    # Status Highlights
    acct_statuses = (
        _pctx[_pctx["PROJECT_STATUS_COMMENTS"].notna()
              & (_pctx["PROJECT_STATUS_COMMENTS"] != "")]
        .groupby("ACCOUNT_NAME")
        .apply(
            lambda g: "\n".join(
                f"**{row['PROJECT_NAME']}** ({row['_HEALTH']}): {row['PROJECT_STATUS_COMMENTS']}"
                for _, row in g.iterrows()
                if pd.notna(row["PROJECT_STATUS_COMMENTS"]) and row["PROJECT_STATUS_COMMENTS"].strip()
            ),
            include_groups=False,
        )
        .reset_index()
        .rename(columns={0: "status_text"})
    )
    acct_statuses = acct_statuses[acct_statuses["status_text"].str.strip() != ""]

    if len(acct_statuses) > 0:
        with st.expander(f"Status Highlights ({len(acct_statuses)} accounts with updates)", expanded=False):
            for _, row in acct_statuses.iterrows():
                st.markdown(f"**{row['ACCOUNT_NAME']}**")
                st.markdown(row["status_text"])


# ══════════════════════════════════════════════════════════
# ROW 2.5: Cohort Analytics & Trends (from Stitch v3 mock)
# ══════════════════════════════════════════════════════════
st.markdown("## Cohort Analytics & Trends")

ca_left, ca_right = st.columns(2)

# ── Chart 1: Attach Rate by ACV Band ──
with ca_left:
    with st.container(border=True):
        # Bucket all UCs by ARR-based ACV bands
        _all_accts = uc.drop_duplicates("ACCOUNT_NAME").copy()
        _all_accts["ACV_BAND"] = pd.cut(
            _all_accts["ARR"].fillna(0),
            bins=[0, 50_000, 250_000, 1_000_000, float("inf")],
            labels=["<50K", "50K–250K", "250K–1M", "1M+"],
            right=True,
        )
        _engaged_accts = _all_accts[
            _all_accts["ACCOUNT_NAME"].isin(ps_engaged["ACCOUNT_NAME"].unique())
        ]

        _band_total = _all_accts.groupby("ACV_BAND", observed=True).size()
        _band_engaged = _engaged_accts.groupby("ACV_BAND", observed=True).size()
        _attach_rate = ((_band_engaged / _band_total) * 100).fillna(0).round(1)

        _bands = ["<50K", "50K–250K", "250K–1M", "1M+"]
        _rates_current = [_attach_rate.get(b, 0) for b in _bands]

        fig_acv_band = go.Figure()
        fig_acv_band.add_trace(go.Bar(
            x=_bands, y=_rates_current,
            name="Current",
            marker_color=CLR_PRIMARY,
            text=[f"{v:.0f}%" for v in _rates_current],
            textposition="outside",
            textfont=dict(family="Inter", size=11),
        ))
        fig_acv_band.update_layout(
            **plotly_layout("Attach Rate by ACV Band", height=320),
            yaxis=dict(title="Attach Rate %", range=[0, max(_rates_current + [10]) * 1.3]),
            xaxis=dict(title=""),
            showlegend=True,
        )
        st.plotly_chart(fig_acv_band, use_container_width=True)

# ── Chart 2: Attach Rate by Customer Segment ──
with ca_right:
    with st.container(border=True):
        _seg_accts = uc.drop_duplicates("ACCOUNT_NAME").copy()
        _seg_accts["_SEG"] = _seg_accts["SEGMENT"].fillna("Unknown")
        _seg_engaged = _seg_accts[
            _seg_accts["ACCOUNT_NAME"].isin(ps_engaged["ACCOUNT_NAME"].unique())
        ]

        _seg_total = _seg_accts.groupby("_SEG", observed=True).size()
        _seg_eng = _seg_engaged.groupby("_SEG", observed=True).size()
        _seg_rate = ((_seg_eng / _seg_total) * 100).fillna(0).round(1)

        # Show top segments by total account count
        _top_segs = _seg_total.sort_values(ascending=False).head(6).index.tolist()
        _seg_vals = [_seg_rate.get(s, 0) for s in _top_segs]

        fig_seg = go.Figure()
        fig_seg.add_trace(go.Bar(
            x=_top_segs, y=_seg_vals,
            name="Current",
            marker_color=CLR_ACCENT,
            text=[f"{v:.0f}%" for v in _seg_vals],
            textposition="outside",
            textfont=dict(family="Inter", size=11),
        ))
        fig_seg.update_layout(
            **plotly_layout("Attach Rate by Customer Segment", height=320),
            yaxis=dict(title="Attach Rate %", range=[0, max(_seg_vals + [10]) * 1.3]),
            xaxis=dict(title="", tickangle=-30),
            showlegend=True,
        )
        st.plotly_chart(fig_seg, use_container_width=True)

ca_left2, ca_right2 = st.columns(2)

# ── Chart 3: PS-Engaged EACV Trend (WoW) ──
with ca_left2:
    with st.container(border=True):
        if len(snapshots) > 0 and "SNAPSHOT_DATE" in snapshots.columns:
            snap_dates = sorted(snapshots["SNAPSHOT_DATE"].unique())
            if len(snap_dates) >= 2:
                trend_data = []
                for sd in snap_dates:
                    snap_row = snapshots[snapshots["SNAPSHOT_DATE"] == sd]
                    if "PS_ENGAGED_EACV" in snap_row.columns and len(snap_row) > 0:
                        trend_data.append({
                            "Date": pd.Timestamp(sd),
                            "EACV": snap_row["PS_ENGAGED_EACV"].iloc[0],
                        })
                if trend_data:
                    trend_df = pd.DataFrame(trend_data)
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(
                        x=trend_df["Date"], y=trend_df["EACV"],
                        mode="lines+markers",
                        line=dict(color=CLR_PRIMARY, width=2.5),
                        marker=dict(size=8, color=CLR_ACCENT),
                        hovertemplate="%{x|%b %d}: $%{y:,.0f}<extra></extra>",
                    ))
                    fig_trend.update_layout(
                        **plotly_layout("PS-Engaged EACV Trend (WoW)", height=320),
                        yaxis=dict(title="EACV ($)", tickformat="$,.0f"),
                        xaxis=dict(title=""),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("EACV trend data not available in snapshots.")
            else:
                st.caption("PS-Engaged EACV Trend (WoW)")
                st.info("Trend available after 2+ weekly snapshots accumulate.")
        else:
            st.caption("PS-Engaged EACV Trend (WoW)")
            st.info("Trend available after snapshot accumulation begins.")

# ── Chart 4: Go-Live Quarter Movement (waterfall) ──
with ca_right2:
    with st.container(border=True):
        # Compute go-live movement: how many UCs moved in/out of selected quarters
        _gl_all = uc[uc["GO_LIVE_DATE"].notna()].copy()
        _in_q = _gl_all[in_selected_quarters(_gl_all["GO_LIVE_DATE"], quarter_ranges)]
        _start_count = len(_in_q)

        # "Moved out" = UCs whose go-live was in selected quarters last snapshot
        # but no longer is. Since we may have only 1 snapshot, approximate from
        # stage progression: UCs past go-live date but not in Go-Live/Complete stage
        _past_due = _in_q[
            (_in_q["GO_LIVE_DATE"] < today_ts)
            & (~_in_q["STAGE_CLEAN"].isin(["Go-Live / Hypercare", "Complete"]))
        ]
        _moved_out = len(_past_due)

        # "Moved in" = UCs in early stages with go-live in selected quarters
        # that are newly scoped (proxy: days in stage < 30)
        _new_in = _in_q[
            _in_q["DAYS_IN_STAGE"].fillna(999) < 30
        ]
        _moved_in = len(_new_in)

        _net = _start_count - _moved_out + _moved_in

        fig_wf = go.Figure(go.Waterfall(
            x=["Start", "Moved Out", "Moved In", "Net Q/E"],
            y=[_start_count, -_moved_out, _moved_in, _net],
            measure=["absolute", "relative", "relative", "total"],
            connector=dict(line=dict(color=CLR_MUTED, width=1)),
            decreasing=dict(marker=dict(color=CLR_RED)),
            increasing=dict(marker=dict(color=CLR_GREEN)),
            totals=dict(marker=dict(color=CLR_PRIMARY)),
            text=[str(_start_count), str(-_moved_out) if _moved_out else "0",
                  f"+{_moved_in}" if _moved_in else "0", str(_net)],
            textposition="outside",
            textfont=dict(family="Manrope", size=13, color=CLR_TEXT),
        ))
        fig_wf.update_layout(
            **plotly_layout(f"Go-Live Quarter Movement ({q_label_str})", height=320),
            yaxis=dict(title="Use Cases"),
            xaxis=dict(title=""),
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)


# ══════════════════════════════════════════════════════════
# ROW 3: Go-Live Readiness + Engagement Opportunity (side by side)
# ══════════════════════════════════════════════════════════
col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.markdown(f"**Go-Live Readiness** ({len(golive_q)})")

        if len(golive_q) > 0:
            gl_show = golive_q.sort_values("GO_LIVE_DATE")[
                ["ACCOUNT_NAME", "USE_CASE_NAME", "GO_LIVE_DATE", "STAGE_CLEAN",
                 "PS_ENGAGEMENT", "IMPLEMENTER", "USE_CASE_ACV"]
            ].copy()
            gl_show["EACV"] = gl_show["USE_CASE_ACV"].apply(fmt_acv)
            gl_show["Risk"] = gl_show["ACCOUNT_NAME"].apply(
                lambda a: "No PS project" if a not in district_accounts or
                (a in acct_proj_ctx["ACCOUNT_NAME"].values and
                 acct_proj_ctx[acct_proj_ctx["ACCOUNT_NAME"] == a]["PS_PROJECT"].iloc[0] == "")
                else "On track"
            )

            st.dataframe(
                gl_show[["ACCOUNT_NAME", "USE_CASE_NAME", "GO_LIVE_DATE",
                         "STAGE_CLEAN", "EACV", "Risk"]],
                use_container_width=True,
                hide_index=True,
                height=min(len(gl_show) * 35 + 40, 400),
                column_config={
                    "ACCOUNT_NAME": "Account",
                    "USE_CASE_NAME": "Use Case",
                    "GO_LIVE_DATE": st.column_config.DateColumn("Go-Live", format="MM/DD/YY"),
                    "STAGE_CLEAN": "Stage",
                    "EACV": "EACV",
                    "Risk": "Risk Flag",
                },
            )
        else:
            st.info("No go-live dates in the selected quarter(s).")

with col_right:
    with st.container(border=True):
        st.markdown(f"**Engagement Opportunity** ({len(not_engaged)})")
        st.caption("Active pipeline UCs without PS engagement")

        if len(not_engaged) > 0:
            wl_counts = Counter()
            for val in ps_engaged["WORKLOADS"].dropna():
                for w in str(val).split(";"):
                    w = w.strip()
                    if w:
                        wl_counts[w] += 1

            ne_show = not_engaged.sort_values("USE_CASE_ACV", ascending=False)[
                ["ACCOUNT_NAME", "USE_CASE_NAME", "STAGE_CLEAN",
                 "USE_CASE_ACV", "WORKLOADS"]
            ].head(20).copy()
            ne_show["EACV"] = ne_show["USE_CASE_ACV"].apply(fmt_acv)

            st.dataframe(
                ne_show[["ACCOUNT_NAME", "USE_CASE_NAME", "STAGE_CLEAN",
                         "EACV", "WORKLOADS"]],
                use_container_width=True,
                hide_index=True,
                height=min(len(ne_show) * 35 + 40, 400),
                column_config={
                    "ACCOUNT_NAME": "Account",
                    "USE_CASE_NAME": "Use Case",
                    "STAGE_CLEAN": "Stage",
                    "EACV": "EACV",
                    "WORKLOADS": "Workloads",
                },
            )
        else:
            st.info("All active use cases have PS engagement.")


# ══════════════════════════════════════════════════════════
# ROW 4: Delivery Risk & Action
# ══════════════════════════════════════════════════════════
with st.container(border=True):
    st.markdown(f"**Delivery Risk & Action** ({len(at_risk)})")

    if len(at_risk) > 0:
        risk_show = at_risk.copy()
        risk_show["Issue"] = risk_show.apply(issue_description, axis=1)
        risk_show["Action"] = risk_show.apply(suggested_action, axis=1)

        # Waterfall-style risk visualization
        risk_by_type = []
        scope_r = len(at_risk[at_risk["SCOPE_HEALTH"].isin(["Yellow", "Red"])])
        sched_r = len(at_risk[at_risk["SCHEDULE_HEALTH"].isin(["Yellow", "Red"])])
        hrs_r = len(at_risk[at_risk["HRS_REM"].fillna(0) < 0])
        status_r = len(at_risk[at_risk["PROJECT_STATUS"].isin(["Red"])])

        if scope_r + sched_r + hrs_r + status_r > 0:
            fig_risk = go.Figure(go.Bar(
                x=["Scope", "Schedule", "Hours Overrun", "Status Red"],
                y=[scope_r, sched_r, hrs_r, status_r],
                marker_color=[CLR_AMBER, CLR_AMBER, CLR_RED, CLR_RED],
                text=[scope_r, sched_r, hrs_r, status_r],
                textposition="outside",
                textfont=dict(family="Manrope", size=13, color=CLR_TEXT),
            ))
            fig_risk.update_layout(
                **plotly_layout("Risk Breakdown", height=260),
                yaxis=dict(title="Projects"),
                xaxis=dict(title=""),
                showlegend=False,
            )
            st.plotly_chart(fig_risk, use_container_width=True)

        st.dataframe(
            risk_show[["ACCOUNT_NAME", "PROJECT_NAME", "PROJECT_MANAGER",
                        "HEALTH", "END_DT", "HRS_REM", "Issue", "Action",
                        "PROJECT_STATUS_COMMENTS"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "ACCOUNT_NAME": "Account",
                "PROJECT_NAME": "Project",
                "PROJECT_MANAGER": "PM",
                "HEALTH": st.column_config.TextColumn(
                    "Health", help="Status/Scope/Schedule/Consumption"
                ),
                "END_DT": st.column_config.DateColumn("End Date", format="MM/DD/YY"),
                "HRS_REM": st.column_config.NumberColumn("Hrs Rem", format="%.0f"),
                "Issue": st.column_config.TextColumn("Issue", width="medium"),
                "Action": st.column_config.TextColumn("Suggested Action", width="large"),
                "PROJECT_STATUS_COMMENTS": st.column_config.TextColumn(
                    "PM Status", width="large"
                ),
            },
        )
    else:
        st.info("No at-risk projects. All green.")


# ══════════════════════════════════════════════════════════
# ROW 5: Detail Tables (below fold)
# ══════════════════════════════════════════════════════════
detail_tab0, detail_tab1, detail_tab2, detail_tab3 = st.tabs([
    f"District Breakdown ({len(ps_engaged)})",
    f"Active PS Projects ({len(proj_view)})",
    f"PS-Engaged Use Cases ({len(ps_engaged)})",
    f"All Use Cases ({len(uc)})",
])

# ── Detail: District Breakdown ──────────────
_district_themes = {}
_region_themes = {}
for _, tr in themes_all[
    (themes_all["REGION"] != "NATIONAL") & (themes_all["ENGAGEMENT_TYPE"] != "_POV")
].iterrows():
    summary = tr["THEME_SUMMARY"].strip().strip(",") if pd.notna(tr["THEME_SUMMARY"]) else "-"
    if pd.notna(tr.get("DISTRICT")):
        _district_themes[(tr["DISTRICT"], tr["ENGAGEMENT_TYPE"])] = summary
    else:
        _region_themes[(tr["REGION"], tr["ENGAGEMENT_TYPE"])] = summary

with detail_tab0:
    dist_rows = []
    for district in sorted(ps_engaged["DISTRICT"].dropna().unique()):
        dist_engaged = ps_engaged[ps_engaged["DISTRICT"] == district]
        dist_region = dist_engaged["REGION"].mode().iloc[0] if len(dist_engaged) > 0 else ""
        dist_flag_df = flag_only[flag_only["DISTRICT"] == district] if "DISTRICT" in flag_only.columns else pd.DataFrame()
        for role in PS_ROLES:
            subset = dist_engaged[dist_engaged["PS_ENGAGEMENT"] == role]
            if len(subset) == 0:
                continue
            dist_rows.append({
                "District": district,
                "Region": dist_region,
                "Engagement Type": role,
                "Use Cases": len(subset),
                "EACV": subset["USE_CASE_ACV"].fillna(0).sum(),
                "Top Workloads": top_workloads(subset["WORKLOADS"]),
                "What We're Doing": _district_themes.get(
                    (district, role), _region_themes.get((dist_region, role), "-")
                ),
            })
        if len(dist_flag_df) > 0:
            dist_rows.append({
                "District": district,
                "Region": dist_region,
                "Engagement Type": "Unspecified*",
                "Use Cases": len(dist_flag_df),
                "EACV": dist_flag_df["USE_CASE_ACV"].fillna(0).sum(),
                "Top Workloads": top_workloads(dist_flag_df["WORKLOADS"]),
                "What We're Doing": _district_themes.get(
                    (district, "Unspecified"), _region_themes.get((dist_region, "Unspecified"), "-")
                ),
            })

    if dist_rows:
        dist_detail_df = pd.DataFrame(dist_rows)
        st.dataframe(
            dist_detail_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "District": st.column_config.TextColumn("District", width="small"),
                "Region": st.column_config.TextColumn("Region", width="small"),
                "Engagement Type": st.column_config.TextColumn("Engagement Type", width="small"),
                "Use Cases": st.column_config.NumberColumn("Use Cases", format="%d", width="small"),
                "EACV": st.column_config.NumberColumn("EACV", format="$%d", width="small"),
                "Top Workloads": st.column_config.TextColumn("Top Workloads", width="medium"),
                "What We're Doing": st.column_config.TextColumn("What We're Doing", width="large"),
            },
        )
    else:
        st.info("No PS-engaged use cases in selected districts.")

# ── Detail: Active PS Projects ──────────────
proj_cols = [
    "PROJECT_ID", "ACCOUNT_NAME", "PROJECT_NAME", "PROJECT_MANAGER",
    "END_DT", "HEALTH", "SERVICE_TYPE", "INVESTMENT_TYPE", "BILLING_TYPE",
    "HRS_USED", "HRS_REM", "PROJECT_STATUS_COMMENTS",
]
proj_cfg = {
    "PROJECT_ID": st.column_config.TextColumn("ID", width="small"),
    "ACCOUNT_NAME": "Account",
    "PROJECT_NAME": "Project",
    "PROJECT_MANAGER": "PM",
    "END_DT": st.column_config.DateColumn("End Date", format="MM/DD/YY"),
    "HEALTH": st.column_config.TextColumn(
        "Health", help="Status/Scope/Schedule/Consumption — G=Green Y=Yellow R=Red"
    ),
    "SERVICE_TYPE": "Service",
    "INVESTMENT_TYPE": "Investment",
    "BILLING_TYPE": "Billing",
    "HRS_USED": st.column_config.NumberColumn("Hrs Used", format="%.1f"),
    "HRS_REM": st.column_config.NumberColumn("Hrs Rem", format="%.1f"),
    "PROJECT_STATUS_COMMENTS": st.column_config.TextColumn(
        "Status Notes", width="large"
    ),
}

ending_q = proj_view[
    proj_view["END_DT"].notna()
    & in_selected_quarters(proj_view["END_DT"], quarter_ranges)
]

with detail_tab1:
    ptab_all, ptab_ending, ptab_risk = st.tabs([
        f"All ({len(proj_view)})",
        f"Ending in Quarter ({len(ending_q)})",
        f"At Risk ({len(at_risk)})",
    ])
    with ptab_all:
        st.dataframe(
            proj_view[proj_cols], use_container_width=True,
            hide_index=True, column_config=proj_cfg,
        )
    with ptab_ending:
        if len(ending_q):
            st.dataframe(
                ending_q[proj_cols], use_container_width=True,
                hide_index=True, column_config=proj_cfg,
            )
        else:
            st.info("No projects ending in selected quarter(s).")
    with ptab_risk:
        if len(at_risk):
            st.dataframe(
                at_risk[proj_cols], use_container_width=True,
                hide_index=True, column_config=proj_cfg,
            )
        else:
            st.info("No at-risk projects.")

# ── Detail: PS-Engaged Use Cases ──────────────

uc_cols = [
    "ACCOUNT_NAME", "USE_CASE_NAME", "STAGE_CLEAN", "PS_ENGAGEMENT",
    "IMPLEMENTER", "PS_PROJECT", "PS_PM", "ACV", "GO_LIVE_DATE",
    "DAYS_IN_STAGE", "PS_STATUS",
]
uc_cfg = {
    "ACCOUNT_NAME": "Account",
    "USE_CASE_NAME": "Use Case",
    "STAGE_CLEAN": "Stage",
    "PS_ENGAGEMENT": "PS Role",
    "IMPLEMENTER": "Implementer",
    "PS_PROJECT": st.column_config.TextColumn("Active Project(s)"),
    "PS_PM": "PM",
    "ACV": "ACV",
    "GO_LIVE_DATE": st.column_config.DateColumn("Go-Live", format="MM/DD/YY"),
    "DAYS_IN_STAGE": st.column_config.NumberColumn("Days in Stage", format="%d"),
    "PS_STATUS": st.column_config.TextColumn("Project Status", width="large"),
}

with detail_tab2:
    role_tab_labels = [f"All ({len(ps_engaged)})"]
    role_tab_filters = [None]
    for r in PS_ROLES:
        role_tab_labels.append(f"{r} ({role_n[r]})")
        role_tab_filters.append(r)
    role_tab_labels.append(f"Unspecified ({role_n['Unspecified']})")
    role_tab_filters.append("_flag_only")

    role_tabs = st.tabs(role_tab_labels)
    for tab, filt in zip(role_tabs, role_tab_filters):
        with tab:
            if filt is None:
                df = ps_engaged
            elif filt == "_flag_only":
                df = flag_only
            else:
                df = ps_engaged[ps_engaged["PS_ENGAGEMENT"] == filt]
            if len(df):
                st.dataframe(
                    df[uc_cols], use_container_width=True,
                    hide_index=True, column_config=uc_cfg,
                )
            else:
                st.info("No use cases in this category.")

# ── Detail: All Use Cases ──────────────
with detail_tab3:
    all_uc_cols = [
        "ACCOUNT_NAME", "USE_CASE_NAME", "STAGE_CLEAN", "PS_ENGAGEMENT",
        "IS_PS_ENGAGED", "IMPLEMENTER", "USE_CASE_ACV", "GO_LIVE_DATE",
        "WORKLOADS", "DAYS_IN_STAGE", "SEGMENT", "INDUSTRY",
    ]
    all_uc_cfg = {
        "ACCOUNT_NAME": "Account",
        "USE_CASE_NAME": "Use Case",
        "STAGE_CLEAN": "Stage",
        "PS_ENGAGEMENT": "PS Engagement",
        "IS_PS_ENGAGED": "PS Flag",
        "IMPLEMENTER": "Implementer",
        "USE_CASE_ACV": st.column_config.NumberColumn("EACV", format="$%.0f"),
        "GO_LIVE_DATE": st.column_config.DateColumn("Go-Live", format="MM/DD/YY"),
        "WORKLOADS": "Workloads",
        "DAYS_IN_STAGE": st.column_config.NumberColumn("Days in Stage", format="%d"),
        "SEGMENT": "Segment",
        "INDUSTRY": "Industry",
    }
    st.dataframe(
        uc[all_uc_cols], use_container_width=True,
        hide_index=True, column_config=all_uc_cfg,
    )
