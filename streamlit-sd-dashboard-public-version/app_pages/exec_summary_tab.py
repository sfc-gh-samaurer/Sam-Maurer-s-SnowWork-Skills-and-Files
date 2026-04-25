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
    load_ps_pipeline,
    load_wow_use_cases,
    load_wow_projects,
    load_fq_closed_sd,
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

st.warning("⚠️ Data access permissions to account capacity data causing issues and limitations — working through resolution.", icon=None)

cutoff       = today - pd.Timedelta(days=days_window)
prior_cutoff = cutoff - pd.Timedelta(days=days_window)
new_opps     = new_opps_all[new_opps_all["CREATED_DATE"] >= cutoff].copy()
new_uc       = new_uc_all[new_uc_all["CREATED_DATE"] >= cutoff].copy()
prior_opps   = new_opps_all[(new_opps_all["CREATED_DATE"] >= prior_cutoff) & (new_opps_all["CREATED_DATE"] < cutoff)]
prior_uc     = new_uc_all[(new_uc_all["CREATED_DATE"] >= prior_cutoff) & (new_uc_all["CREATED_DATE"] < cutoff)]

sw_n     = len(sw_renewals)
svc_n    = len(svc_renewals)
opp_n    = len(new_opps)
uc_n     = len(new_uc)
cv_n     = len(conv_candidates)
invest_n = len(invest_df)

opp_delta = opp_n - len(prior_opps)
uc_delta  = uc_n  - len(prior_uc)


def _delta_html(d):
    if d > 0:
        return f'<div class="kpi-delta" style="color:#16a34a;">▲ {d} vs prior period</div>'
    if d < 0:
        return f'<div class="kpi-delta" style="color:#dc2626;">▼ {abs(d)} vs prior period</div>'
    return f'<div class="kpi-delta" style="color:#8A999E;">— same as prior period</div>'

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>.kpi-delta{{font-size:0.62rem;margin-top:4px;font-weight:600;}}</style>
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
    {_delta_html(opp_delta)}
  </div>
  <div class="kpi-card" style="background:linear-gradient(160deg,#FAF5FF,#F3E8FF);border-top-color:#9333EA;">
    <span class="kpi-icon">💡</span>
    <div class="kpi-value" style="color:#7E22CE;">{uc_n}</div>
    <div class="kpi-label" style="color:#6B21A8;">New Use Cases</div>
    <div class="kpi-sub">Last {days_window} days</div>
    {_delta_html(uc_delta)}
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

# ── WoW SUMMARY ───────────────────────────────────────────────────────────────
_wow_uc   = load_wow_use_cases()
_wow_proj = load_wow_projects()


def _stage_num_ex(s):
    try:
        return int(str(s).split(" - ")[0].strip())
    except Exception:
        return -1


_ex_stages   = _wow_uc[_wow_uc["FIELD"] == "Stage__c"].copy()
if not _ex_stages.empty:
    _ex_stages["DIRECTION"] = _ex_stages.apply(
        lambda r: "Advance" if _stage_num_ex(r["NEW_VALUE"]) > _stage_num_ex(r["OLD_VALUE"]) else "Regression", axis=1
    )
else:
    _ex_stages["DIRECTION"] = pd.Series(dtype=str)

_ex_adv    = _ex_stages[_ex_stages["DIRECTION"] == "Advance"] if not _ex_stages.empty else pd.DataFrame()
_ex_reg    = _ex_stages[_ex_stages["DIRECTION"] == "Regression"] if not _ex_stages.empty else pd.DataFrame()
_ex_wins   = _wow_uc[_wow_uc["FIELD"] == "Technical_Win__c"]
_ex_gl     = _wow_uc[_wow_uc["FIELD"] == "Actual_Go_Live_Date__c"]
_ex_pstage = _wow_proj[_wow_proj["FIELD"] == "pse__Stage__c"]
_ex_comp   = _ex_pstage[_ex_pstage["NEW_VALUE"] == "Completed"]
_ex_stall  = _ex_pstage[_ex_pstage["NEW_VALUE"].isin(["Stalled", "Stalled - Expiring"])]

_wow_summary = (
    f"This Week  \u2014  "
    f"{len(_ex_adv)} UC advances\u00a0\u00b7\u00a0{len(_ex_reg)} regressions\u00a0\u00b7\u00a0"
    f"{len(_ex_wins)} tech wins\u00a0\u00b7\u00a0"
    f"{len(_ex_comp)} projects completed\u00a0\u00b7\u00a0{len(_ex_stall)} stalled"
)

with st.expander(_wow_summary, expanded=False):
    _ew1, _ew2, _ew3 = st.tabs([
        f"UC Stage Changes ({len(_ex_adv) + len(_ex_reg)})",
        f"Tech Wins ({len(_ex_wins)})",
        f"SD Projects ({len(_ex_pstage)})",
    ])

    def _ex_uc_link(row):
        uid = row.get("USE_CASE_ID")
        return f"{SFDC_BASE}/{uid}/view" if uid and str(uid).strip() else None

    def _ex_proj_link(row):
        pid = row.get("PROJECT_ID")
        return f"{SFDC_BASE}/pse__Proj__c/{pid}/view" if pid and str(pid).strip() else None

    _ex_wow_cols = [
        {"col": "ACCOUNT_NAME",  "label": "Account"},
        {"col": "USE_CASE_NAME", "label": "Use Case"},
        {"col": "UC_LINK",       "label": "SFDC",           "fmt": "link"},
        {"col": "OLD_VALUE",     "label": "From Stage"},
        {"col": "NEW_VALUE",     "label": "To Stage"},
        {"col": "ACV",           "label": "UC eACV",           "fmt": "dollar"},
        {"col": "UC_STATUS",     "label": "Status"},
        {"col": "DECISION_DATE", "label": "Decision Date",  "fmt": "date"},
        {"col": "CHANGED_AT",   "label": "When",            "fmt": "date"},
    ]
    _ex_proj_cols = [
        {"col": "ACCOUNT_NAME",  "label": "Account"},
        {"col": "PROJECT_NAME",  "label": "Project"},
        {"col": "PROJ_LINK",     "label": "SFDC",           "fmt": "link"},
        {"col": "OLD_VALUE",     "label": "From Stage"},
        {"col": "NEW_VALUE",     "label": "To Stage"},
        {"col": "REVENUE_AMOUNT","label": "Revenue",        "fmt": "dollar"},
        {"col": "CHANGED_AT",   "label": "When",            "fmt": "date"},
    ]

    def _prep_ex_uc(df_in):
        d = df_in.copy()
        d["UC_LINK"] = d.apply(_ex_uc_link, axis=1)
        return d

    def _prep_ex_proj(df_in):
        d = df_in.copy()
        d["PROJ_LINK"] = d.apply(_ex_proj_link, axis=1)
        return d

    with _ew1:
        if _ex_adv.empty and _ex_reg.empty:
            empty_state("No stage changes this week.")
        else:
            if not _ex_adv.empty:
                st.markdown('<p class="sf-section-label">Advances</p>', unsafe_allow_html=True)
                render_html_table(_prep_ex_uc(_ex_adv), columns=_ex_wow_cols, height=max(120, min(350, len(_ex_adv) * 38 + 60)))
            if not _ex_reg.empty:
                st.markdown('<p class="sf-section-label">Regressions</p>', unsafe_allow_html=True)
                render_html_table(_prep_ex_uc(_ex_reg), columns=_ex_wow_cols, height=max(120, min(350, len(_ex_reg) * 38 + 60)))

    with _ew2:
        if _ex_wins.empty:
            empty_state("No technical wins recorded this week.")
        else:
            render_html_table(_prep_ex_uc(_ex_wins), columns=[
                {"col": "ACCOUNT_NAME",  "label": "Account"},
                {"col": "USE_CASE_NAME", "label": "Use Case"},
                {"col": "UC_LINK",       "label": "SFDC",          "fmt": "link"},
                {"col": "CURRENT_STAGE", "label": "Current Stage"},
                {"col": "ACV",           "label": "UC eACV",          "fmt": "dollar"},
                {"col": "CHANGED_AT",   "label": "When",           "fmt": "date"},
            ], height=max(120, min(350, len(_ex_wins) * 38 + 60)))

    with _ew3:
        if _ex_pstage.empty:
            empty_state("No project stage changes this week.")
        else:
            render_html_table(_prep_ex_proj(_ex_pstage), columns=_ex_proj_cols, height=max(120, min(350, len(_ex_pstage) * 38 + 60)))

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
            "CONTRACT_END_DATE", "DAYS_LEFT", "TOTAL_CAP", "OVERAGE_UNDERAGE_PREDICTION"
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
            {"col": "TOTAL_CAP",                    "label": "Total Cap",        "fmt": "dollar"},
            {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Predicted Underage", "fmt": "dollar"},
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

# ── FISCAL QUARTER SUMMARY ────────────────────────────────────────────────────
def _fq_label():
    m = today.month
    fy = today.year + 1 if m >= 2 else today.year
    q = 1 if m in (2, 3, 4) else 2 if m in (5, 6, 7) else 3 if m in (8, 9, 10) else 4
    return f"Q{q}-FY{str(fy)[2:]}"

_cfq_current = _fq_label()

st.divider()
st.markdown('<p class="sf-section-label">Quarter Summary</p>', unsafe_allow_html=True)

_sd_pipe = load_ps_pipeline()

def _valid_fq(q):
    try:
        parts = str(q).split("-FY")
        return len(parts) == 2 and len(parts[1]) in (2, 4) and parts[1].isdigit()
    except Exception:
        return False

_fq_raw = (
    list(cap_pipe_df["FISCAL_QUARTER"].dropna().unique()) +
    list(_sd_pipe["FISCAL_QUARTER"].dropna().unique() if not _sd_pipe.empty else [])
)
_fq_all = sorted(set(q for q in _fq_raw if _valid_fq(q)))
if _cfq_current not in _fq_all:
    _fq_all = [_cfq_current] + _fq_all
_fq_all = sorted(set(_fq_all))

def _fq_fy(q):
    suffix = q.split("-FY")[1]
    return int(suffix) if len(suffix) == 4 else int("20" + suffix)

_cur_fy  = _fq_fy(_cfq_current)
_fq_3yr  = [q for q in _fq_all if _fq_fy(q) <= _cur_fy + 3] or [_cfq_current]
_cfq_idx = _fq_3yr.index(_cfq_current) if _cfq_current in _fq_3yr else 0

selected_fq = st.selectbox(
    "Fiscal Quarter",
    options=_fq_3yr,
    index=_cfq_idx,
    key="exec_fq_select",
    label_visibility="collapsed",
)

_cap_fq = cap_pipe_df[cap_pipe_df["FISCAL_QUARTER"] == selected_fq] if not cap_pipe_df.empty else pd.DataFrame()
_cap_fq = _cap_fq[_cap_fq["FORECAST_STATUS"].fillna("") != "Omitted"] if not _cap_fq.empty else _cap_fq

_sd_fq = _sd_pipe[_sd_pipe["FISCAL_QUARTER"] == selected_fq] if not _sd_pipe.empty else pd.DataFrame()
_sd_fq = _sd_fq[_sd_fq["FORECAST_STATUS"].fillna("") != "Omitted"] if not _sd_fq.empty else _sd_fq

_closed_sd = load_fq_closed_sd(selected_fq)

fq1, fq2, fq3, fq4, fq5, fq6 = st.columns(6)
fq1.metric("Cap Opps",    len(_cap_fq),                                                           help=f"Open capacity opps closing in {selected_fq}")
fq2.metric("Cap TCV",     f"${_cap_fq['CALCULATED_TCV'].fillna(0).sum():,.0f}" if not _cap_fq.empty else "$0", help="Sum of Calculated TCV")
fq3.metric("SD Won Opps", len(_closed_sd),                                                        help=f"Closed won PS&T opps in {selected_fq}")
fq4.metric("SD ACV Won",  f"${_closed_sd['PS_SERVICES_ACV'].fillna(0).sum():,.0f}" if not _closed_sd.empty else "$0", help="Technical Services ACV on closed won deals")
fq5.metric("Open SD Opps",len(_sd_fq),                                                            help=f"Open PS&T opps closing in {selected_fq}")
fq6.metric("Open SD TCV", f"${_sd_fq['TOTAL_PST_TCV'].fillna(0).sum():,.0f}" if not _sd_fq.empty else "$0", help="Sum of Total PST TCV for open opps")

_fq_dd1, _fq_dd2, _fq_dd3 = st.tabs([
    f"Cap Opps & TCV ({len(_cap_fq)})",
    f"SD Won ({len(_closed_sd)})",
    f"Open SD ({len(_sd_fq)})",
])

with _fq_dd1:
    if _cap_fq.empty:
        empty_state(f"No open capacity opps found for {selected_fq}.")
    else:
        _cdisplay = _cap_fq.copy()
        _cdisplay["OPP_LINK"] = _cdisplay.apply(
            lambda r: f"{SFDC_BASE}/Opportunity/{r['OPPORTUNITY_ID']}/view" if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )
        render_html_table(_cdisplay, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",     "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE","label": "Type"},
            {"col": "STAGE_NAME",      "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "PRODUCT_FORECAST_ACV","label": "Fcst ACV","fmt": "dollar"},
            {"col": "CALCULATED_TCV",  "label": "Calc TCV",  "fmt": "dollar"},
            {"col": "CLOSE_DATE",      "label": "Close Date","fmt": "date"},
            {"col": "OWNER",           "label": "AE"},
        ], height=max(160, min(500, len(_cap_fq) * 40 + 60)))

with _fq_dd2:
    if _closed_sd.empty:
        empty_state(f"No closed SD won opps found for {selected_fq}.")
    else:
        _sd_closed_display = _closed_sd.copy()
        _sd_closed_display["OPP_LINK"] = _sd_closed_display.apply(
            lambda r: f"{SFDC_BASE}/Opportunity/{r['OPPORTUNITY_ID']}/view" if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )
        render_html_table(_sd_closed_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",       "fmt": "link"},
            {"col": "AE",              "label": "AE"},
            {"col": "CLOSE_DATE",      "label": "Close Date", "fmt": "date"},
            {"col": "PS_SERVICES_ACV", "label": "PS Svc ACV", "fmt": "dollar"},
            {"col": "TOTAL_PST",       "label": "Total PST",  "fmt": "dollar"},
        ], height=max(160, min(400, len(_closed_sd) * 40 + 60)))

with _fq_dd3:
    if _sd_fq.empty:
        empty_state(f"No open SD opps found for {selected_fq}.")
    else:
        _sd_open_display = _sd_fq.copy()
        _sd_open_display["OPP_LINK"] = _sd_open_display.apply(
            lambda r: f"{SFDC_BASE}/Opportunity/{r['OPPORTUNITY_ID']}/view" if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )
        render_html_table(_sd_open_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",       "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE","label": "Type"},
            {"col": "STAGE_NAME",      "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_PST_TCV",   "label": "PST TCV",    "fmt": "dollar"},
            {"col": "CLOSE_DATE",      "label": "Close Date", "fmt": "date"},
            {"col": "OWNER",           "label": "AE"},
        ], height=max(160, min(500, len(_sd_fq) * 40 + 60)))
