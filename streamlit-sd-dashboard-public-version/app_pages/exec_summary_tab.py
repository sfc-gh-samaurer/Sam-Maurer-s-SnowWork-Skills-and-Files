import streamlit as st
import pandas as pd
from datetime import datetime
from data import (
    load_exec_software_renewals,
    load_exec_services_renewals,
    load_exec_new_opps,
    load_exec_new_use_cases,
    load_capacity_renewals,
    load_capacity_pipeline,
    render_html_table,
)
from constants import SFDC_BASE
from components import section_banner, empty_state

today = pd.Timestamp.now().normalize()

sw_renewals_raw = load_exec_software_renewals()
svc_renewals    = load_exec_services_renewals()
new_opps_all    = load_exec_new_opps()
new_uc_all      = load_exec_new_use_cases()
cap_df          = load_capacity_renewals()
cap_pipe_df     = load_capacity_pipeline()

sw_renewals = sw_renewals_raw[
    ~sw_renewals_raw["OPPORTUNITY_NAME"].str.contains("Segment", case=False, na=False)
].copy()


def _to_naive(series):
    s = pd.to_datetime(series, errors="coerce")
    if s.dt.tz is not None:
        s = s.dt.tz_localize(None)
    return s


sw_renewals["CLOSE_DATE"]       = _to_naive(sw_renewals["CLOSE_DATE"])
svc_renewals["END_DATE"]        = _to_naive(svc_renewals["END_DATE"])
new_opps_all["CREATED_DATE"]    = _to_naive(new_opps_all["CREATED_DATE"])
new_uc_all["CREATED_DATE"]      = _to_naive(new_uc_all["CREATED_DATE"])

conv_candidates = pd.DataFrame()
if not cap_df.empty:
    _cap = cap_df.copy()
    _cap["DAYS_LEFT"] = (pd.to_datetime(_cap["CONTRACT_END_DATE"]) - today).dt.days
    _cap["PCT_REMAINING"] = (_cap["CAPACITY_REMAINING"] / _cap["TOTAL_CAP"] * 100).round(1)
    conv_candidates = _cap[
        (_cap["CONTRACT_END_DATE"].notna())
        & (_cap["DAYS_LEFT"] <= 730)
        & (_cap["DAYS_LEFT"] > 0)
        & (_cap["OVERAGE_UNDERAGE_PREDICTION"] < 0)
    ].sort_values("OVERAGE_UNDERAGE_PREDICTION", ascending=True).head(15)


def _current_and_next_fq():
    m = today.month
    fy = today.year + 1 if m >= 2 else today.year
    q = 1 if m in (2, 3, 4) else 2 if m in (5, 6, 7) else 3 if m in (8, 9, 10) else 4
    next_q = q + 1 if q < 4 else 1
    next_fy = fy if q < 4 else fy + 1
    return [f"Q{q}-{fy}", f"Q{next_q}-{next_fy}"]


invest_fqs = _current_and_next_fq()
invest_df  = pd.DataFrame()
if not cap_pipe_df.empty:
    _ip = cap_pipe_df.copy()
    _ip["CLOSE_DATE"] = pd.to_datetime(_ip["CLOSE_DATE"], errors="coerce")
    _ip = _ip[_ip["CLOSE_DATE"] > today]
    _ip = _ip[_ip["FORECAST_STATUS"].fillna("") != "Omitted"]
    _ip = _ip[_ip["FISCAL_QUARTER"].isin(invest_fqs)]
    invest_df = _ip[_ip["CALCULATED_TCV"].fillna(0) >= 500_000]

# ── TIMEFRAME SELECTOR (above KPI row) ────────────────────────────────────────
if "exec_days_window" not in st.session_state:
    st.session_state["exec_days_window"] = 15

days_window = st.radio(
    "Timeframe for New Opps & Use Cases:",
    options=[15, 30, 60, 90],
    format_func=lambda x: f"Last {x} days",
    horizontal=True,
    key="exec_days_window",
    label_visibility="collapsed",
)

cutoff  = today - pd.Timedelta(days=days_window)
new_opps = new_opps_all[new_opps_all["CREATED_DATE"] >= cutoff].copy()
new_uc   = new_uc_all[new_uc_all["CREATED_DATE"] >= cutoff].copy()

sw_n     = len(sw_renewals)
svc_n    = len(svc_renewals)
opp_n    = len(new_opps)
uc_n     = len(new_uc)
cv_n     = len(conv_candidates)
invest_n = len(invest_df)

# ── KPI METRICS ───────────────────────────────────────────────────────────────
# ── KPI CARDS ─────────────────────────────────────────────────────────────────
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
  <div class="kpi-card" style="background:linear-gradient(160deg,#FDF2F8,#FCE7F3);border-top-color:#D45B90;">
    <span class="kpi-icon">💰</span>
    <div class="kpi-value" style="color:#BE185D;">{invest_n}</div>
    <div class="kpi-label" style="color:#9D174D;">Invest Candidates</div>
    <div class="kpi-sub">Cap deals &gt;$500K, 2 Qtrs</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="sf-section-label">Detailed Results — click to expand</p>', unsafe_allow_html=True)

# ── Section 1: Software Renewals ──────────────────────────────────────────────
with st.expander(f"Upcoming Software Renewals ({sw_n})", expanded=False):
    if sw_renewals.empty:
        empty_state("No software renewal opportunities closing in the next 6 months.")
    else:
        sw_display = sw_renewals.copy()
        sw_display["OPP_LINK"] = sw_display["OPPORTUNITY_ID"].apply(
            lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(sw_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",     "fmt": "link"},
            {"col": "STAGE_NAME",      "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_ACV",       "label": "ACV",      "fmt": "dollar"},
            {"col": "RENEWAL_ACV",     "label": "Rnwl ACV", "fmt": "dollar"},
            {"col": "CLOSE_DATE",      "label": "Close",    "fmt": "date"},
            {"col": "OWNER",           "label": "AE"},
        ], height=max(200, min(400, sw_n * 38 + 60)))

# ── Section 2: Services Renewals ──────────────────────────────────────────────
with st.expander(f"Upcoming Services Renewals ({svc_n})", expanded=False):
    if svc_renewals.empty:
        empty_state("No active PS projects ending in the next 6 months.")
    else:
        svc_display = svc_renewals.copy()
        svc_display["ACCT_LINK"] = svc_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(svc_display, columns=[
            {"col": "ACCOUNT_NAME",  "label": "Account"},
            {"col": "ACCT_LINK",     "label": "SFDC",     "fmt": "link"},
            {"col": "PROJECT_NAME",  "label": "Project"},
            {"col": "PROJECT_STAGE", "label": "Stage"},
            {"col": "START_DATE",    "label": "Start",    "fmt": "date"},
            {"col": "END_DATE",      "label": "End",      "fmt": "date"},
            {"col": "DAYS_TO_END",   "label": "Days Left","fmt": "number"},
            {"col": "PROJECT_MANAGER","label": "PM"},
            {"col": "AE",            "label": "AE"},
        ], height=max(200, min(400, svc_n * 38 + 60)))

# ── Section 3: New Opportunities ──────────────────────────────────────────────
with st.expander(f"New Opportunities — last {days_window} days ({opp_n})", expanded=False):
    if new_opps.empty:
        empty_state(f"No opportunities created in the last {days_window} days.")
    else:
        new_opps_display = new_opps.copy()
        new_opps_display["OPP_LINK"] = new_opps_display["OPPORTUNITY_ID"].apply(
            lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(new_opps_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",      "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE","label": "Type"},
            {"col": "AGREEMENT_TYPE",  "label": "Agreement"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_ACV",       "label": "ACV",       "fmt": "dollar"},
            {"col": "CLOSE_DATE",      "label": "Close",     "fmt": "date"},
            {"col": "CREATED_DATE",    "label": "Created",   "fmt": "date"},
            {"col": "OWNER",           "label": "AE"},
        ], height=max(200, min(500, opp_n * 38 + 60)))

# ── Section 4: New Use Cases ──────────────────────────────────────────────────
with st.expander(f"New Use Cases — last {days_window} days ({uc_n})", expanded=False):
    if new_uc.empty:
        empty_state(f"No use cases created in the last {days_window} days.")
    else:
        uc_display = new_uc.copy()
        uc_display["ACCT_LINK"] = uc_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(uc_display, columns=[
            {"col": "ACCOUNT_NAME",  "label": "Account"},
            {"col": "ACCT_LINK",     "label": "SFDC",    "fmt": "link"},
            {"col": "USE_CASE_NAME", "label": "Use Case"},
            {"col": "STAGE",         "label": "Stage"},
            {"col": "ACV",           "label": "eACV",    "fmt": "dollar"},
            {"col": "CREATED_DATE",  "label": "Created", "fmt": "date"},
            {"col": "OWNER",         "label": "AE"},
        ], height=max(200, min(500, uc_n * 38 + 60)))

# ── Section 5: Capacity Conversion Candidates ─────────────────────────────────
with st.expander(f"Capacity Conversion Candidates ({cv_n})", expanded=False):
    if conv_candidates.empty:
        empty_state("No capacity conversion candidates found.")
    else:
        st.caption("Accounts predicted to have significant unused capacity at contract end. Consider converting remaining capacity into services.")
        conv_display = conv_candidates[[
            "ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
            "CONTRACT_END_DATE", "DAYS_LEFT", "TOTAL_CAP", "CAPACITY_REMAINING", "PCT_REMAINING"
        ]].copy()
        conv_display["ACCT_LINK"] = conv_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(conv_display, columns=[
            {"col": "ACCOUNT_NAME",       "label": "Account"},
            {"col": "ACCT_LINK",          "label": "SFDC",       "fmt": "link"},
            {"col": "ACCOUNT_OWNER",      "label": "AE"},
            {"col": "DM",                 "label": "DM"},
            {"col": "CONTRACT_END_DATE",  "label": "End Date",   "fmt": "date"},
            {"col": "DAYS_LEFT",          "label": "Days Left",  "fmt": "number"},
            {"col": "TOTAL_CAP",          "label": "Total Cap",  "fmt": "dollar"},
            {"col": "CAPACITY_REMAINING", "label": "Remaining",  "fmt": "dollar"},
            {"col": "PCT_REMAINING",      "label": "% Remain",   "fmt": "pct"},
        ], height=max(200, min(500, cv_n * 38 + 60)))

# ── Section 6: Investment Candidates ──────────────────────────────────────────
with st.expander(f"Investment Candidates — {' & '.join(invest_fqs)} ({invest_n})", expanded=False):
    if invest_df.empty:
        empty_state("No investment candidates found.")
    else:
        st.caption(f"Future capacity opportunities with Calculated TCV ≥$500K closing in {' or '.join(invest_fqs)}.")
        inv_display = invest_df.copy()
        inv_display["OPP_LINK"] = inv_display.apply(
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )
        inv_display["EST_INVESTMENT"] = inv_display["CALCULATED_TCV"].fillna(0) * 0.10
        render_html_table(inv_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",       "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE","label": "Type"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "CALCULATED_TCV",  "label": "Calc TCV",   "fmt": "dollar"},
            {"col": "CLOSE_DATE",      "label": "Close Date", "fmt": "date"},
            {"col": "EST_INVESTMENT",  "label": "Est. Invest","fmt": "dollar"},
        ], height=max(200, min(500, invest_n * 38 + 60)))
