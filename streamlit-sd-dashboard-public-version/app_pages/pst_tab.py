import streamlit as st
import pandas as pd
import re
from data import load_ps_projects_active, render_html_table
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
