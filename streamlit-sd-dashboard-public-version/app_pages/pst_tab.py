import streamlit as st
import pandas as pd
import re
from data import load_ps_projects_active, render_html_table, load_wow_projects
from constants import SFDC_BASE
from components import section_banner, empty_state

active_df = load_ps_projects_active()
if not active_df.empty and "PRACTICE" in active_df.columns:
    active_df = active_df[active_df["PRACTICE"] != "Education Services"]

section_banner("Active SD Projects", "In-progress and pipeline services delivery engagements")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Active Projects", len(active_df))
k2.metric("Active Revenue",  f"${active_df['REVENUE_AMOUNT'].sum():,.0f}"  if not active_df.empty else "$0")
k3.metric("Billable Hours",  f"{active_df['BILLABLE_HOURS'].sum():,.0f}"   if not active_df.empty else "0")
k4.metric("Stalled",         len(active_df[active_df["PROJECT_STAGE"].isin(["Stalled", "Stalled - Expiring"])]) if not active_df.empty else 0)

# ── WoW Project Changes ───────────────────────────────────────────────────────
wow_proj  = load_wow_projects()
_today    = pd.Timestamp.now().normalize()

wow_stages = wow_proj[wow_proj["FIELD"] == "pse__Stage__c"]
wow_status = wow_proj[wow_proj["FIELD"] == "pse__Project_Status__c"]

wow_completed  = wow_stages[wow_stages["NEW_VALUE"] == "Completed"]
wow_stalled    = wow_stages[wow_stages["NEW_VALUE"].isin(["Stalled", "Stalled - Expiring"])]
wow_kicked_off = wow_stages[wow_stages["NEW_VALUE"].isin(["In Progress", "Scheduled"])]
wow_red        = wow_status[wow_status["NEW_VALUE"] == "Red"]

if not active_df.empty and "END_DATE" in active_df.columns:
    _end_col = pd.to_datetime(active_df["END_DATE"], errors="coerce")
    _expiring = active_df[
        _end_col.notna() &
        (_end_col <= (_today + pd.Timedelta(days=14))) &
        (_end_col >= _today)
    ]
else:
    _expiring = pd.DataFrame()

_comp_n  = len(wow_completed)
_stall_n = len(wow_stalled)
_kick_n  = len(wow_kicked_off)
_exp_n   = len(_expiring)

_proj_wow_label = (
    f"This Week's Project Changes  —  "
    f"{_comp_n} completed · {_kick_n} kicked off · {_stall_n} stalled · {_exp_n} expiring <14d"
)

def _proj_link(row):
    pid = row.get("PROJECT_ID")
    return f"{SFDC_BASE}/pse__Proj__c/{pid}/view" if pid and str(pid).strip() else None

def _add_proj_links(df_in):
    d = df_in.copy()
    d["PROJ_LINK"] = d.apply(_proj_link, axis=1)
    return d

_stage_cols = [
    {"col": "ACCOUNT_NAME",  "label": "Account"},
    {"col": "PROJECT_NAME",  "label": "Project"},
    {"col": "PROJ_LINK",     "label": "SFDC",        "fmt": "link"},
    {"col": "OLD_VALUE",     "label": "From Stage"},
    {"col": "NEW_VALUE",     "label": "To Stage"},
    {"col": "BILLING_TYPE",  "label": "Billing"},
    {"col": "SERVICE_TYPE",  "label": "Service Type"},
    {"col": "START_DATE",    "label": "Start",       "fmt": "date"},
    {"col": "END_DATE",      "label": "End",         "fmt": "date"},
    {"col": "REVENUE_AMOUNT","label": "Revenue",     "fmt": "dollar"},
    {"col": "PCT_COMPLETE",  "label": "% Complete",  "fmt": "pct"},
    {"col": "CHANGED_AT",   "label": "When",        "fmt": "date"},
]

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #92400e 0%, #b45309 55%, #d97706 100%);
    border-radius: 10px 10px 0 0;
    padding: 11px 20px;
    margin-bottom: -8px;
    box-shadow: 0 2px 10px rgba(146,64,14,0.35);
    display:flex; align-items:center; gap:18px;
">
  <span style="color:white;font-weight:800;font-size:0.95rem;white-space:nowrap;letter-spacing:0.02em;">📅 THIS WEEK</span>
  <span style="color:rgba(255,255,255,0.75);font-size:0.78rem;">
    <span style="color:#86efac;font-weight:700">{_comp_n}</span> <span style="color:rgba(255,255,255,0.55)">completed</span>
    &nbsp;·&nbsp; <span style="color:#fde68a;font-weight:700">{_kick_n}</span> <span style="color:rgba(255,255,255,0.55)">kicked off</span>
    &nbsp;·&nbsp; <span style="color:#fca5a5;font-weight:700">{_stall_n}</span> <span style="color:rgba(255,255,255,0.55)">stalled</span>
    &nbsp;·&nbsp; <span style="color:#fca5a5;font-weight:700">{_exp_n}</span> <span style="color:rgba(255,255,255,0.55)">expiring &lt;14d</span>
  </span>
</div>
""", unsafe_allow_html=True)
with st.expander(_proj_wow_label, expanded=False):
    _pt1, _pt2, _pt3, _pt4 = st.tabs([
        f"Completed ({_comp_n})",
        f"Kicked Off ({_kick_n})",
        f"Went Stalled ({_stall_n})",
        f"Expiring <14d ({_exp_n})",
    ])

    with _pt1:
        if wow_completed.empty:
            empty_state("No projects completed this week.")
        else:
            render_html_table(_add_proj_links(wow_completed), columns=_stage_cols, height=max(140, min(500, _comp_n * 40 + 60)))

    with _pt2:
        if wow_kicked_off.empty:
            empty_state("No projects kicked off this week.")
        else:
            render_html_table(_add_proj_links(wow_kicked_off), columns=_stage_cols, height=max(140, min(500, _kick_n * 40 + 60)))

    with _pt3:
        if wow_stalled.empty:
            empty_state("No projects went stalled this week.")
        else:
            render_html_table(_add_proj_links(wow_stalled), columns=_stage_cols, height=max(140, min(500, _stall_n * 40 + 60)))

    with _pt4:
        if _expiring.empty:
            empty_state("No projects expiring in the next 14 days.")
        else:
            _expiring_linked = _add_proj_links(_expiring)
            render_html_table(_expiring_linked, columns=[
                {"col": "ACCOUNT_NAME", "label": "Account"},
                {"col": "PROJECT_NAME", "label": "Project"},
                {"col": "PROJ_LINK",    "label": "SFDC",        "fmt": "link"},
                {"col": "PROJECT_STAGE","label": "Stage"},
                {"col": "BILLING_TYPE", "label": "Billing"},
                {"col": "END_DATE",     "label": "End Date",    "fmt": "date"},
                {"col": "REVENUE_AMOUNT","label": "Revenue",    "fmt": "dollar"},
                {"col": "PCT_COMPLETE", "label": "% Complete",  "fmt": "pct"},
            ], height=max(140, min(500, _exp_n * 40 + 60)))


def _extract_base_name(project_name):
    if pd.isna(project_name):
        return ""
    cleaned = re.sub(r'\s*Year\s*\d+', '', str(project_name), flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Yr\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Y\d+\b', '', cleaned)
    cleaned = re.sub(r'\s*Phase\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Ph\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().rstrip('-').rstrip('_').strip()
    return cleaned


if not active_df.empty:
    active_df["END_DATE"]            = pd.to_datetime(active_df["END_DATE"])
    active_df["LAST_RESOURCE_END_DATE"] = pd.to_datetime(active_df["LAST_RESOURCE_END_DATE"])

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        acct_filter_a  = st.multiselect("Account",       options=sorted(active_df["ACCOUNT_NAME"].dropna().unique()),  default=[], key="psa_acct")
    with fc2:
        stage_filter_a = st.multiselect("Project Stage", options=sorted(active_df["PROJECT_STAGE"].dropna().unique()), default=[], key="psa_stage")
    with fc3:
        dm_filter_a    = st.multiselect("DM",            options=sorted(active_df["DM"].dropna().unique()),            default=[], key="psa_dm")
    with fc4:
        ae_filter_a    = st.multiselect("AE",            options=sorted(active_df["AE"].dropna().unique()),            default=[], key="psa_ae")

    fc5, fc6, fc7 = st.columns([2, 1, 2])
    with fc5:
        exp_months_a = st.slider(
            "Show only projects expiring within N months (0 = show all)",
            min_value=0, max_value=24, value=0, step=1, key="psa_exp_months",
        )
    with fc6:
        hide_past_end = st.checkbox("Hide past end dates", value=False, key="psa_hide_past")
    with fc7:
        search_a = st.text_input("Search project", "", key="psa_search", placeholder="Project name…")

    filtered_a = active_df.copy()
    if acct_filter_a:
        filtered_a = filtered_a[filtered_a["ACCOUNT_NAME"].isin(acct_filter_a)]
    if stage_filter_a:
        filtered_a = filtered_a[filtered_a["PROJECT_STAGE"].isin(stage_filter_a)]
    if dm_filter_a:
        filtered_a = filtered_a[filtered_a["DM"].isin(dm_filter_a)]
    if ae_filter_a:
        filtered_a = filtered_a[filtered_a["AE"].isin(ae_filter_a)]
    if hide_past_end:
        _today = pd.Timestamp.now().normalize()
        filtered_a = filtered_a[filtered_a["END_DATE"].isna() | (filtered_a["END_DATE"] >= _today)]
    if search_a:
        filtered_a = filtered_a[filtered_a["PROJECT_NAME"].str.contains(search_a, case=False, na=False)]

    if exp_months_a > 0:
        today_exp  = pd.Timestamp.now().normalize()
        cutoff_exp = today_exp + pd.DateOffset(months=exp_months_a)
        filtered_a["_EFF_END"]   = filtered_a["LAST_RESOURCE_END_DATE"].fillna(filtered_a["END_DATE"])
        filtered_a["_BASE_NAME"] = filtered_a["PROJECT_NAME"].apply(_extract_base_name)
        expiring_mask = (
            filtered_a["_EFF_END"].notna()
            & (filtered_a["_EFF_END"] > today_exp)
            & (filtered_a["_EFF_END"] <= cutoff_exp)
        )
        expiring_set  = filtered_a[expiring_mask]
        no_ext_indices = []
        for idx, row in expiring_set.iterrows():
            same_acct = filtered_a[
                (filtered_a["SALESFORCE_ACCOUNT_ID"] == row["SALESFORCE_ACCOUNT_ID"])
                & (filtered_a["_BASE_NAME"] == row["_BASE_NAME"])
                & (filtered_a.index != idx)
            ]
            has_later = same_acct["_EFF_END"].notna() & (same_acct["_EFF_END"] > row["_EFF_END"])
            if not has_later.any():
                no_ext_indices.append(idx)
        filtered_a = expiring_set.loc[no_ext_indices]

    display_a = filtered_a.copy()
    display_a["OPP_LINK"] = display_a.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
    )

    with st.expander(f"{len(filtered_a)} projects", expanded=True):
        render_html_table(display_a, columns=[
            {"col": "ACCOUNT_NAME",        "label": "Account"},
            {"col": "OPPORTUNITY_NAME",    "label": "Opportunity"},
            {"col": "OPP_LINK",            "label": "Opp SFDC",      "fmt": "link"},
            {"col": "PROJECT_NAME",        "label": "Project"},
            {"col": "PRACTICE",            "label": "Practice"},
            {"col": "DM",                  "label": "DM"},
            {"col": "AE",                  "label": "AE"},
            {"col": "PROJECT_STAGE",       "label": "Stage"},
            {"col": "BILLING_TYPE",        "label": "Billing"},
            {"col": "SKU_TYPE",            "label": "SKU"},
            {"col": "INVESTMENT_TYPE",     "label": "Invest"},
            {"col": "START_DATE",          "label": "Start",         "fmt": "date"},
            {"col": "END_DATE",            "label": "Proj End",      "fmt": "date"},
            {"col": "LAST_RESOURCE_END_DATE","label": "Last Rsrc End","fmt": "date", "highlight": True},
            {"col": "BILLABLE_HOURS",      "label": "Bill Hrs",      "fmt": "number"},
            {"col": "REVENUE_AMOUNT",      "label": "Revenue",       "fmt": "dollar"},
            {"col": "PROJECT_MANAGER",     "label": "PM"},
            {"col": "PS_SELLER_NAME",      "label": "PS Seller"},
            {"col": "ASSIGNMENT_COUNT",    "label": "Assignments",   "fmt": "number"},
            {"col": "ASSIGNED_RESOURCES",  "label": "Resources"},
            {"col": "ASSIGNED_ROLES",      "label": "Roles"},
            {"col": "PS_FORECAST_CATEGORY","label": "Fcast Cat"},
        ], height=500)
        st.download_button(":material/download: Export CSV", filtered_a.to_csv(index=False), "pst_active_projects.csv", "text/csv", key="psa_csv")
else:
    empty_state("No active PS&T projects found.")
