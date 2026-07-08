import streamlit as st
import pandas as pd
import altair as alt
from data import (
    load_milestone_acv,
    load_accounts_base,
    load_ps_projects_active,
    load_use_cases,
    render_html_table,
    _scope_key,
)
from constants import SFDC_BASE, SF_STAR_BLUE, SF_MID_BLUE
from components import section_banner, empty_state

_sk = _scope_key()
try:
    milestone_df = load_milestone_acv(_scope=_sk)
except Exception:
    milestone_df = pd.DataFrame()
accounts_df = load_accounts_base(_scope=_sk)
projects_df = load_ps_projects_active(_scope=_sk)
if not projects_df.empty and "PRACTICE" in projects_df.columns:
    projects_df = projects_df[projects_df["PRACTICE"] != "Education Services"]
uc_df = load_use_cases(_scope=_sk)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: SERVICES ACV IMPACT
# ═══════════════════════════════════════════════════════════════════════════════
section_banner("Services ACV Impact", "ACV of use cases delivered through Professional Services milestones")

if not milestone_df.empty:
    milestone_df["GO_LIVE_DATE"] = pd.to_datetime(milestone_df["GO_LIVE_DATE"], errors="coerce")
    milestone_df = milestone_df[milestone_df["GO_LIVE_DATE"] >= "2024-01-01"]
    _total_acv = milestone_df["ESTIMATED_ACV"].fillna(0).sum()
    _milestone_count = len(milestone_df)
    _unique_uc = milestone_df["MILESTONE_ID"].nunique()

    _summary = milestone_df.groupby("FISCAL_QUARTER_LABEL", as_index=False).agg(
        USE_CASE_COUNT=("MILESTONE_NAME", "count"),
        TOTAL_ESTIMATED_ACV=("ESTIMATED_ACV", "sum"),
    ).sort_values("FISCAL_QUARTER_LABEL")

    _avg_acv_per_q = _summary["TOTAL_ESTIMATED_ACV"].mean() if len(_summary) > 0 else 0

    _current_fq_label = None
    _today = pd.Timestamp.now().normalize()
    _m = _today.month
    _fy = _today.year + 1 if _m >= 2 else _today.year
    _q = 1 if _m in (2, 3, 4) else 2 if _m in (5, 6, 7) else 3 if _m in (8, 9, 10) else 4
    _current_fq_label = f"FY{_fy}-Q{_q}"
    _current_fq_acv = _summary[_summary["FISCAL_QUARTER_LABEL"] == _current_fq_label]["TOTAL_ESTIMATED_ACV"].sum() if _current_fq_label else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total ACV Attached", f"${_total_acv:,.0f}")
    k2.metric("Milestones", f"{_milestone_count}")
    k3.metric("Avg ACV / Quarter", f"${_avg_acv_per_q:,.0f}")
    k4.metric(f"Current FQ ({_current_fq_label})", f"${_current_fq_acv:,.0f}")

    _bar = alt.Chart(_summary).mark_bar(
        cornerRadiusTopLeft=4, cornerRadiusTopRight=4
    ).encode(
        x=alt.X("FISCAL_QUARTER_LABEL:N", title="Fiscal Quarter", sort=None),
        y=alt.Y("TOTAL_ESTIMATED_ACV:Q", title="Total Estimated ACV ($)", axis=alt.Axis(format="$,.0f")),
        color=alt.condition(
            alt.datum.FISCAL_QUARTER_LABEL == _current_fq_label,
            alt.value("#0284C7"),
            alt.value("#29B5E8"),
        ),
        tooltip=[
            alt.Tooltip("FISCAL_QUARTER_LABEL:N", title="Quarter"),
            alt.Tooltip("TOTAL_ESTIMATED_ACV:Q", title="ACV", format="$,.0f"),
            alt.Tooltip("USE_CASE_COUNT:Q", title="Milestones"),
        ],
    ).properties(height=340)
    st.altair_chart(_bar, use_container_width=True)

    with st.expander(f"Milestone Details ({_milestone_count})", expanded=False):
        _fc1, _fc2 = st.columns(2)
        with _fc1:
            _fq_opts = sorted(milestone_df["FISCAL_QUARTER_LABEL"].dropna().unique().tolist())
            _sel_fq = st.selectbox("Fiscal Quarter", ["All"] + _fq_opts, key="acv_fq")
        with _fc2:
            _stage_opts = sorted(milestone_df["USE_CASE_STAGE"].dropna().unique().tolist())
            _sel_stage = st.selectbox("Use Case Stage", ["All"] + _stage_opts, key="acv_stage")

        _filtered = milestone_df.copy()
        if _sel_fq != "All":
            _filtered = _filtered[_filtered["FISCAL_QUARTER_LABEL"] == _sel_fq]
        if _sel_stage != "All":
            _filtered = _filtered[_filtered["USE_CASE_STAGE"] == _sel_stage]

        st.markdown(f"**{len(_filtered)} milestones** &nbsp;·&nbsp; Estimated ACV: **${_filtered['ESTIMATED_ACV'].fillna(0).sum():,.0f}**")

        _filtered["MILESTONE_URL"] = _filtered["MILESTONE_ID"].apply(
            lambda x: f"{SFDC_BASE}/pse__Milestone__c/{x}/view" if pd.notna(x) else None
        )
        render_html_table(_filtered, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "AE", "label": "AE"},
            {"col": "PROJECT_NAME", "label": "Project"},
            {"col": "MILESTONE_NAME", "label": "Milestone"},
            {"col": "MILESTONE_URL", "label": "SFDC", "fmt": "link"},
            {"col": "USE_CASE_STAGE", "label": "UC Stage"},
            {"col": "MILESTONE_STATUS", "label": "Status"},
            {"col": "GO_LIVE_DATE", "label": "Go-Live", "fmt": "date"},
            {"col": "ESTIMATED_ACV", "label": "Est. ACV", "fmt": "dollar"},
            {"col": "FISCAL_QUARTER_LABEL", "label": "FQ"},
        ], height=420)

else:
    empty_state("No milestone ACV data found for the current scope.")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: DISTRICT COVERAGE & WHITESPACE
# ═══════════════════════════════════════════════════════════════════════════════
section_banner("District Coverage & Whitespace", "Accounts with active SD projects vs total book of business")

if not accounts_df.empty:
    _accts_with_proj = set(projects_df["SALESFORCE_ACCOUNT_ID"].dropna().unique()) if not projects_df.empty else set()
    _ps_engaged_ucs = set()
    if not uc_df.empty and "IS_PS_ENGAGED" in uc_df.columns:
        _ps_engaged_ucs = set(uc_df[uc_df["IS_PS_ENGAGED"] == True]["SALESFORCE_ACCOUNT_ID"].dropna().unique())

    accounts_df["HAS_PROJECT"] = accounts_df["SALESFORCE_ACCOUNT_ID"].isin(_accts_with_proj)
    accounts_df["HAS_PS_UC"] = accounts_df["SALESFORCE_ACCOUNT_ID"].isin(_ps_engaged_ucs)
    accounts_df["IS_WHITESPACE"] = ~accounts_df["HAS_PROJECT"] & ~accounts_df["HAS_PS_UC"]

    _total_accts = len(accounts_df)
    _covered = accounts_df["HAS_PROJECT"].sum()
    _ps_uc_ct = accounts_df["HAS_PS_UC"].sum()
    _whitespace_ct = accounts_df["IS_WHITESPACE"].sum()
    _coverage_pct = _covered / _total_accts * 100 if _total_accts > 0 else 0

    _whitespace_pct = f"{_whitespace_ct / _total_accts * 100:.0f}%" if _total_accts > 0 else "—"
    _ps_no_proj = len(accounts_df[accounts_df['HAS_PS_UC'] & ~accounts_df['HAS_PROJECT']])

    ck1, ck2, ck3, ck4 = st.columns(4)
    ck1.metric("Total Accounts", f"{_total_accts}")
    ck2.metric("With Active Project", f"{_covered} / {_total_accts}  ({_coverage_pct:.0f}%)")
    ck3.metric("PS-Engaged UC (no proj)", f"{_ps_no_proj}")
    ck4.metric("Whitespace", f"{_whitespace_ct}  ({_whitespace_pct})")

    if "DM" in accounts_df.columns:
        _dm_coverage = accounts_df.groupby("DM", as_index=False).agg(
            ACCOUNTS=("SALESFORCE_ACCOUNT_ID", "count"),
            WITH_PROJECT=("HAS_PROJECT", "sum"),
            WITH_PS_UC=("HAS_PS_UC", "sum"),
            WHITESPACE=("IS_WHITESPACE", "sum"),
            TOTAL_ARR=("ARR", "sum"),
        )
        _dm_coverage["COVERAGE_PCT"] = (_dm_coverage["WITH_PROJECT"] / _dm_coverage["ACCOUNTS"] * 100).round(0)
        _dm_coverage["WITH_PROJECT"] = _dm_coverage["WITH_PROJECT"].fillna(0).astype(int)
        _dm_coverage["WITH_PS_UC"] = _dm_coverage["WITH_PS_UC"].fillna(0).astype(int)
        _dm_coverage["WHITESPACE"] = _dm_coverage["WHITESPACE"].fillna(0).astype(int)
        _dm_coverage = _dm_coverage.sort_values("COVERAGE_PCT", ascending=False)

        render_html_table(_dm_coverage, columns=[
            {"col": "DM", "label": "DM"},
            {"col": "ACCOUNTS", "label": "Accounts", "fmt": "number"},
            {"col": "WITH_PROJECT", "label": "w/ Project", "fmt": "number"},
            {"col": "COVERAGE_PCT", "label": "Coverage %", "fmt": "pct"},
            {"col": "WITH_PS_UC", "label": "w/ PS UC", "fmt": "number"},
            {"col": "WHITESPACE", "label": "Whitespace", "fmt": "number"},
            {"col": "TOTAL_ARR", "label": "Total ARR", "fmt": "dollar"},
        ], height=min(300, len(_dm_coverage) * 40 + 60))


else:
    empty_state("No accounts found for the current scope.")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: PROJECT HEALTH SCORECARD
# ═══════════════════════════════════════════════════════════════════════════════
section_banner("Project Health Scorecard", "Status distribution, stalled projects, and expiration risk")

if not projects_df.empty:
    _green = len(projects_df[projects_df["PROJECT_STATUS"] == "Green"])
    _yellow = len(projects_df[projects_df["PROJECT_STATUS"] == "Yellow"])
    _red = len(projects_df[projects_df["PROJECT_STATUS"] == "Red"])
    _stalled = len(projects_df[projects_df["PROJECT_STAGE"].isin(["Stalled", "Stalled - Expiring"])])
    _total_proj = len(projects_df)
    _green_pct = f"{_green / _total_proj * 100:.0f}%" if _total_proj > 0 else "—"
    _avg_pct_complete = projects_df[projects_df["PROJECT_STAGE"] == "In Progress"]["PCT_HOURS_COMPLETE"].mean()
    _avg_pct_str = f"{_avg_pct_complete:.0f}%" if pd.notna(_avg_pct_complete) else "—"

    hk1, hk2, hk3, hk4, hk5 = st.columns(5)
    hk1.metric("Green", f"{_green}", delta=_green_pct)
    hk2.metric("Yellow", f"{_yellow}")
    hk3.metric("Red", f"{_red}")
    hk4.metric("Stalled", f"{_stalled}")
    hk5.metric("Avg % Complete", _avg_pct_str)

    if "DM" in projects_df.columns:
        _status_by_dm = projects_df.groupby(["DM", "PROJECT_STATUS"], as_index=False).size()
        _status_by_dm.columns = ["DM", "Status", "Count"]
        _status_order = ["Green", "Yellow", "Red", ""]
        _color_scale = alt.Scale(
            domain=["Green", "Yellow", "Red", ""],
            range=["#16A34A", "#EAB308", "#DC2626", "#94A3B8"],
        )
        _stacked = alt.Chart(_status_by_dm).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("DM:N", title="District Manager", sort="-y"),
            y=alt.Y("Count:Q", title="Projects"),
            color=alt.Color("Status:N", scale=_color_scale, legend=alt.Legend(title="Status")),
            tooltip=[
                alt.Tooltip("DM:N", title="DM"),
                alt.Tooltip("Status:N", title="Status"),
                alt.Tooltip("Count:Q", title="Projects"),
            ],
        ).properties(height=280)
        st.altair_chart(_stacked, use_container_width=True)

    _today = pd.Timestamp.now().normalize()
    _end_col = pd.to_datetime(projects_df["END_DATE"], errors="coerce")
    _expiring_60 = projects_df[
        _end_col.notna()
        & (_end_col <= (_today + pd.Timedelta(days=60)))
        & (_end_col >= _today)
    ].copy()

    if not _expiring_60.empty:
        _exp_acct_ids = set(_expiring_60["SALESFORCE_ACCOUNT_ID"].dropna())
        _svc_opp_accts = set()
        _expiring_60["HAS_RENEWAL"] = _expiring_60["SALESFORCE_ACCOUNT_ID"].isin(_svc_opp_accts)
        _no_renewal = _expiring_60[~_expiring_60["HAS_RENEWAL"]]

        if not _no_renewal.empty:
            with st.expander(f"Expiring in 60 Days — No Renewal Opp ({len(_no_renewal)})", expanded=False):
                st.caption("Projects ending within 60 days. Review for potential follow-on engagement.")
                render_html_table(_no_renewal, columns=[
                    {"col": "ACCOUNT_NAME", "label": "Account"},
                    {"col": "AE", "label": "AE"},
                    {"col": "DM", "label": "DM"},
                    {"col": "PROJECT_NAME", "label": "Project"},
                    {"col": "PROJECT_STAGE", "label": "Stage"},
                    {"col": "END_DATE", "label": "End Date", "fmt": "date"},
                    {"col": "REVENUE_AMOUNT", "label": "Revenue", "fmt": "dollar"},
                    {"col": "PROJECT_MANAGER", "label": "PM"},
                ], height=min(350, len(_no_renewal) * 40 + 60))
else:
    empty_state("No active projects found for the current scope.")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: REVENUE & ENGAGEMENT INTENSITY
# ═══════════════════════════════════════════════════════════════════════════════
section_banner("Revenue & Engagement Intensity", "Services TCV by DM and PS engagement rates")

if not projects_df.empty:
    _rev_by_dm = projects_df.groupby("DM", as_index=False).agg(
        ACTIVE_REVENUE=("REVENUE_AMOUNT", "sum"),
        PROJECT_COUNT=("PROJECT_NAME", "count"),
        BILLABLE_HOURS=("BILLABLE_HOURS", "sum"),
    )

    _ps_rate_by_dm = pd.DataFrame()
    if not uc_df.empty and "DM" in uc_df.columns and "IS_PS_ENGAGED" in uc_df.columns:
        _uc_grouped = uc_df.groupby("DM", as_index=False).agg(
            TOTAL_UCS=("USE_CASE_ID", "count"),
            PS_ENGAGED_UCS=("IS_PS_ENGAGED", "sum"),
        )
        _uc_grouped["PS_ENGAGEMENT_PCT"] = (_uc_grouped["PS_ENGAGED_UCS"] / _uc_grouped["TOTAL_UCS"] * 100).round(0)
        _ps_rate_by_dm = _uc_grouped[["DM", "TOTAL_UCS", "PS_ENGAGED_UCS", "PS_ENGAGEMENT_PCT"]]

    _intensity = _rev_by_dm.copy()

    if not _ps_rate_by_dm.empty:
        _intensity = _intensity.merge(_ps_rate_by_dm, on="DM", how="left").fillna(0)
    else:
        _intensity["TOTAL_UCS"] = 0
        _intensity["PS_ENGAGED_UCS"] = 0
        _intensity["PS_ENGAGEMENT_PCT"] = 0

    _intensity = _intensity.sort_values("ACTIVE_REVENUE", ascending=False)

    _cols_list = [
        {"col": "DM", "label": "DM"},
        {"col": "ACTIVE_REVENUE", "label": "TCV", "fmt": "dollar"},
        {"col": "PROJECT_COUNT", "label": "Projects", "fmt": "number"},
        {"col": "BILLABLE_HOURS", "label": "Bill Hrs", "fmt": "number"},
        {"col": "PS_ENGAGEMENT_PCT", "label": "PS Engage %", "fmt": "pct"},
    ]
    render_html_table(_intensity, columns=_cols_list, height=min(300, len(_intensity) * 40 + 60))

else:
    empty_state("No data available for revenue intensity analysis.")
