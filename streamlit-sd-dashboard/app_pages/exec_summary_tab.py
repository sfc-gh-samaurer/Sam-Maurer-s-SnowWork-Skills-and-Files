import streamlit as st
import pandas as pd
from datetime import datetime
from data import (
    load_exec_software_renewals,
    load_exec_services_renewals,
    load_exec_new_opps,
    load_exec_new_use_cases,
    load_capacity_renewals,
    render_html_table,
)

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

today = pd.Timestamp.now().normalize()

sw_renewals = load_exec_software_renewals()
svc_renewals = load_exec_services_renewals()
new_opps_all = load_exec_new_opps()
new_uc_all = load_exec_new_use_cases()
cap_df = load_capacity_renewals()

def _to_naive(series):
    s = pd.to_datetime(series, errors="coerce")
    if s.dt.tz is not None:
        s = s.dt.tz_localize(None)
    return s

sw_renewals["CLOSE_DATE"] = _to_naive(sw_renewals["CLOSE_DATE"])
svc_renewals["END_DATE"] = _to_naive(svc_renewals["END_DATE"])
new_opps_all["CREATED_DATE"] = _to_naive(new_opps_all["CREATED_DATE"])
new_uc_all["CREATED_DATE"] = _to_naive(new_uc_all["CREATED_DATE"])

# --- Conversion candidates logic (same as capacity_renewals tab) ---
conv_candidates = pd.DataFrame()
if not cap_df.empty:
    cap_df_copy = cap_df.copy()
    cap_df_copy["DAYS_LEFT"] = (pd.to_datetime(cap_df_copy["CONTRACT_END_DATE"]) - today).dt.days
    cap_df_copy["PCT_REMAINING"] = (cap_df_copy["CAPACITY_REMAINING"] / cap_df_copy["TOTAL_CAPACITY"] * 100).round(1)
    conv_candidates = cap_df_copy[
        (cap_df_copy["CONTRACT_END_DATE"].notna())
        & (cap_df_copy["DAYS_LEFT"] <= 730)
        & (cap_df_copy["DAYS_LEFT"] > 0)
        & (cap_df_copy["OVERAGE_UNDERAGE_PREDICTION"] < 0)
    ].sort_values("OVERAGE_UNDERAGE_PREDICTION", ascending=True).head(15)

st.markdown("### :material/bar_chart: Executive Summary")
st.caption(f"Territory: Erik Schneider & Raymond Navarro — as of {today.strftime('%B %d, %Y')}")

days_window = st.radio(
    "New items window",
    options=[30, 60, 90],
    format_func=lambda x: f"Last {x} days",
    horizontal=True,
    key="exec_days_window",
)

cutoff = today - pd.Timedelta(days=days_window)
new_opps = new_opps_all[new_opps_all["CREATED_DATE"] >= cutoff].copy()
new_uc = new_uc_all[new_uc_all["CREATED_DATE"] >= cutoff].copy()

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric(":material/autorenew: SW Renewals", len(sw_renewals), help="Open renewal opps closing in next 6 months")
with k2:
    st.metric(":material/handshake: Svc Renewals", len(svc_renewals), help="Active PS projects ending in next 6 months")
with k3:
    st.metric(":material/add_circle: New Opps", len(new_opps), help=f"Opportunities created in last {days_window} days")
with k4:
    st.metric(":material/lightbulb: New Use Cases", len(new_uc), help=f"Use cases created in last {days_window} days")
with k5:
    st.metric(":material/swap_horiz: Conv Candidates", len(conv_candidates), help="Capacity accounts w/ predicted underburn ending <24mo")

st.divider()

# ── SECTION 1: Software Renewals ──────────────────────────────────────────
with st.expander(
    f":material/autorenew: **Upcoming Software Renewals** — {len(sw_renewals)} open renewal opps closing in next 6 months",
    expanded=True,
):
    if sw_renewals.empty:
        st.info("No software renewal opportunities closing in the next 6 months.")
    else:
        sw_display = sw_renewals.copy()
        sw_display["OPP_LINK"] = sw_display["OPPORTUNITY_ID"].apply(
            lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
        )
        sw_display["ACCT_LINK"] = sw_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(sw_display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCT_LINK", "label": "Acct", "fmt": "link"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK", "label": "Opp", "fmt": "link"},
            {"col": "STAGE_NAME", "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_ACV", "label": "Total ACV", "fmt": "dollar"},
            {"col": "RENEWAL_ACV", "label": "Rnwl ACV", "fmt": "dollar"},
            {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
            {"col": "FISCAL_QUARTER", "label": "FQ"},
            {"col": "OWNER", "label": "Owner"},
            {"col": "DM", "label": "DM"},
            {"col": "NEXT_STEPS", "label": "Next Steps"},
        ], height=max(200, min(400, len(sw_display) * 35 + 60)))

# ── SECTION 2: Services Renewals ──────────────────────────────────────────
with st.expander(
    f":material/handshake: **Upcoming Services Renewals** — {len(svc_renewals)} active PS projects ending in next 6 months",
    expanded=True,
):
    if svc_renewals.empty:
        st.info("No active PS projects ending in the next 6 months.")
    else:
        svc_display = svc_renewals.copy()
        svc_display["ACCT_LINK"] = svc_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(svc_display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCT_LINK", "label": "SFDC", "fmt": "link"},
            {"col": "PROJECT_NAME", "label": "Project"},
            {"col": "AGREEMENT_TYPE", "label": "Agreement"},
            {"col": "SERVICE_TYPE", "label": "Service Type"},
            {"col": "PROJECT_STAGE", "label": "Stage"},
            {"col": "START_DATE", "label": "Start", "fmt": "date"},
            {"col": "END_DATE", "label": "End", "fmt": "date"},
            {"col": "DAYS_TO_END", "label": "Days Left", "fmt": "number"},
            {"col": "REVENUE_AMOUNT", "label": "Revenue", "fmt": "dollar"},
            {"col": "PROJECT_MANAGER", "label": "PM"},
            {"col": "DELIVERY_MANAGER", "label": "DM Eng"},
            {"col": "AE", "label": "AE"},
            {"col": "DM", "label": "DM"},
        ], height=max(200, min(400, len(svc_display) * 35 + 60)))

# ── SECTION 3: New Opportunities ──────────────────────────────────────────
with st.expander(
    f":material/add_circle: **New Opportunities** — {len(new_opps)} created in last {days_window} days",
    expanded=True,
):
    if new_opps.empty:
        st.info(f"No opportunities created in the last {days_window} days.")
    else:
        new_opps_display = new_opps.copy()
        new_opps_display["OPP_LINK"] = new_opps_display["OPPORTUNITY_ID"].apply(
            lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
        )
        new_opps_display["ACCT_LINK"] = new_opps_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(new_opps_display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCT_LINK", "label": "Acct", "fmt": "link"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK", "label": "Opp", "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE", "label": "Type"},
            {"col": "AGREEMENT_TYPE", "label": "Agreement"},
            {"col": "STAGE_NAME", "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_ACV", "label": "ACV", "fmt": "dollar"},
            {"col": "CLOSE_DATE", "label": "Close", "fmt": "date"},
            {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
            {"col": "OWNER", "label": "Owner"},
            {"col": "DM", "label": "DM"},
        ], height=max(200, min(500, len(new_opps_display) * 35 + 60)))

# ── SECTION 4: New Use Cases ──────────────────────────────────────────────
with st.expander(
    f":material/lightbulb: **New Use Cases** — {len(new_uc)} created in last {days_window} days",
    expanded=True,
):
    if new_uc.empty:
        st.info(f"No use cases created in the last {days_window} days.")
    else:
        uc_display = new_uc.copy()
        uc_display["ACCT_LINK"] = uc_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(uc_display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCT_LINK", "label": "SFDC", "fmt": "link"},
            {"col": "USE_CASE_NAME", "label": "Use Case"},
            {"col": "USE_CASE_STATUS", "label": "Status"},
            {"col": "STAGE", "label": "Stage"},
            {"col": "ACV", "label": "eACV", "fmt": "dollar"},
            {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
            {"col": "OWNER", "label": "Owner"},
            {"col": "DM", "label": "DM"},
            {"col": "NEXT_STEPS", "label": "Next Steps"},
        ], height=max(200, min(500, len(uc_display) * 35 + 60)))

# ── SECTION 5: Capacity Conversion Candidates ────────────────────────────
with st.expander(
    f":material/swap_horiz: **Top Capacity Conversion Candidates** — {len(conv_candidates)} accounts ending <24mo w/ predicted underburn",
    expanded=True,
):
    if conv_candidates.empty:
        st.info("No capacity conversion candidates found.")
    else:
        st.caption("Accounts predicted to have significant unused capacity at contract end — consider converting remaining capacity into services contracts.")
        conv_display = conv_candidates[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                                        "CONTRACT_END_DATE", "DAYS_LEFT", "TOTAL_CAPACITY",
                                        "CAPACITY_REMAINING", "PCT_REMAINING",
                                        "OVERAGE_UNDERAGE_PREDICTION"]].copy()
        conv_display["ACCT_LINK"] = conv_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(conv_display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCT_LINK", "label": "SFDC", "fmt": "link"},
            {"col": "ACCOUNT_OWNER", "label": "AE"},
            {"col": "DM", "label": "DM"},
            {"col": "CONTRACT_END_DATE", "label": "End Date", "fmt": "date"},
            {"col": "DAYS_LEFT", "label": "Days Left", "fmt": "number"},
            {"col": "TOTAL_CAPACITY", "label": "Total Cap", "fmt": "dollar"},
            {"col": "CAPACITY_REMAINING", "label": "Cap Remain", "fmt": "dollar"},
            {"col": "PCT_REMAINING", "label": "% Remain", "fmt": "pct"},
            {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Pred Under", "fmt": "dollar"},
        ], height=max(200, min(500, len(conv_display) * 35 + 60)))
