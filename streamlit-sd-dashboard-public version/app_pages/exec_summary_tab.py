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

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.exec-banner {
    background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 6px 24px rgba(41,181,232,0.30);
}
.exec-banner-icon { font-size: 3.4rem; line-height: 1; flex-shrink: 0; }
.exec-banner-title {
    color: white !important;
    font-size: 4.4rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}
.exec-banner-sub {
    color: rgba(255,255,255,0.78);
    font-size: 0.92rem;
    margin: 5px 0 0;
}
.kpi-grid {
    display: flex;
    gap: 14px;
    margin: 4px 0 20px 0;
}
.kpi-card {
    flex: 1;
    border-radius: 14px;
    padding: 22px 14px 16px;
    text-align: center;
    box-shadow: 0 3px 14px rgba(0,0,0,0.09);
    border-top: 5px solid;
    transition: box-shadow 0.2s;
}
.kpi-icon { font-size: 2.4rem; margin-bottom: 10px; display: block; line-height: 1; }
.kpi-value {
    font-size: 2.2rem;
    font-weight: 900;
    line-height: 1.0;
    margin-bottom: 7px;
}
.kpi-label {
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.kpi-sub { font-size: 0.7rem; opacity: 0.58; }
.detail-header {
    background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin: 24px 0 14px 0;
    display: flex;
    align-items: center;
    box-shadow: 0 6px 24px rgba(41,181,232,0.30);
}
.detail-header-title { font-size: 4.4rem; font-weight: 800; color: white !important; margin: 0; letter-spacing: -0.02em; line-height: 1.15; }
.detail-header-sub { font-size: 0.92rem; color: rgba(255,255,255,0.78); margin: 5px 0 0; }
</style>
""", unsafe_allow_html=True)

# ── HEADER BANNER ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="exec-banner">
    <div>
        <p class="exec-banner-title">Executive Summary</p>
        <p class="exec-banner-sub">Real-time pipeline health &amp; renewal tracking across your district</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TIMEFRAME SELECTOR ────────────────────────────────────────────────────────
days_window = st.radio(
    "Select timeframe option to 30/60/90 days:",
    options=[30, 60, 90],
    format_func=lambda x: f"Last {x} days",
    horizontal=True,
    key="exec_days_window",
)

cutoff = today - pd.Timedelta(days=days_window)
new_opps = new_opps_all[new_opps_all["CREATED_DATE"] >= cutoff].copy()
new_uc = new_uc_all[new_uc_all["CREATED_DATE"] >= cutoff].copy()

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
sw_n  = len(sw_renewals)
svc_n = len(svc_renewals)
opp_n = len(new_opps)
uc_n  = len(new_uc)
cv_n  = len(conv_candidates)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card" style="background:linear-gradient(160deg,#EFF6FF,#DBEAFE);border-top-color:#3B82F6;">
        <span class="kpi-icon">🔄</span>
        <div class="kpi-value" style="color:#1D4ED8;">{sw_n}</div>
        <div class="kpi-label" style="color:#1E40AF;">Cap Renewals</div>
        <div class="kpi-sub">Closing in 6 months</div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(160deg,#F0F9FF,#E0F2FE);border-top-color:#0284C7;">
        <span class="kpi-icon">🤝</span>
        <div class="kpi-value" style="color:#0369A1;">{svc_n}</div>
        <div class="kpi-label" style="color:#075985;">SD Renewals</div>
        <div class="kpi-sub">Active projects ending</div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(160deg,#F0FDF4,#DCFCE7);border-top-color:#16A34A;">
        <span class="kpi-icon">💼</span>
        <div class="kpi-value" style="color:#15803D;">{opp_n}</div>
        <div class="kpi-label" style="color:#166534;">New Opps</div>
        <div class="kpi-sub">Last {days_window} days</div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(160deg,#FAF5FF,#F3E8FF);border-top-color:#9333EA;">
        <span class="kpi-icon">💡</span>
        <div class="kpi-value" style="color:#7E22CE;">{uc_n}</div>
        <div class="kpi-label" style="color:#6B21A8;">New Use Cases</div>
        <div class="kpi-sub">Last {days_window} days</div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(160deg,#FFFBEB,#FEF3C7);border-top-color:#D97706;">
        <span class="kpi-icon">⚡</span>
        <div class="kpi-value" style="color:#B45309;">{cv_n}</div>
        <div class="kpi-label" style="color:#92400E;">Conv. Candidates</div>
        <div class="kpi-sub">Underburn &lt;24 months</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── DETAILED RESULTS HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="detail-header">
    <div>
        <p class="detail-header-title">Detailed Results</p>
        <p class="detail-header-sub">Click each section below to expand</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SECTION 1: Software Renewals ──────────────────────────────────────────────
with st.expander(
    f"🔄  **Upcoming Software Renewals** — {len(sw_renewals)} open renewal opps closing in next 6 months",
    expanded=False,
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

# ── SECTION 2: Services Renewals ──────────────────────────────────────────────
with st.expander(
    f"🤝  **Upcoming Services Renewals** — {len(svc_renewals)} active PS projects ending in next 6 months",
    expanded=False,
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

# ── SECTION 3: New Opportunities ──────────────────────────────────────────────
with st.expander(
    f"💼  **New Opportunities** — {len(new_opps)} created in last {days_window} days",
    expanded=False,
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

# ── SECTION 4: New Use Cases ──────────────────────────────────────────────────
with st.expander(
    f"💡  **New Use Cases** — {len(new_uc)} created in last {days_window} days",
    expanded=False,
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

# ── SECTION 5: Capacity Conversion Candidates ─────────────────────────────────
with st.expander(
    f"⚡  **Top Capacity Conversion Candidates** — {len(conv_candidates)} accounts ending <24mo w/ predicted underburn",
    expanded=False,
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
