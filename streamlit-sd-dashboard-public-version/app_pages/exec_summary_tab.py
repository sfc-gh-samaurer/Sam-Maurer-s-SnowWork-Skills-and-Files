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
    load_wow_use_cases,
    load_wow_projects,
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
for _d in [sw_renewals_raw, svc_renewals, new_opps_all]:
    if "AGREEMENT_TYPE" not in _d.columns:
        _d["AGREEMENT_TYPE"] = _d.get("OPPORTUNITY_TYPE", "")
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
        & (_cap["OVERAGE_UNDERAGE_PREDICTION"] < -75000)
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

# ── PAGE-LEVEL TIMEFRAME ────────────────────────────────────────────────────────
_tw = st.radio("**Timeframe:**", ["7 days", "14 days"], horizontal=True, key="exec_days", label_visibility="visible")
days_window = int(_tw.split()[0])

st.warning("**⚠️ Data access permissions to ACCOUNT CAPACITY DATA causing issues and limitations — working through resolution. Validate all consumption data in A360 before decision making or actions.**", icon=None)

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

# ── MONEY AT STAKE ROW ────────────────────────────────────────────────────────
_renewal_acv  = sw_renewals["TOTAL_ACV"].fillna(0).sum()
_cap_acv      = cap_pipe_df["PRODUCT_FORECAST_ACV"].fillna(0).sum() if not cap_pipe_df.empty else 0
_conv_opp     = abs(conv_candidates["OVERAGE_UNDERAGE_PREDICTION"].fillna(0).sum()) if not conv_candidates.empty else 0
_invest_tcv   = invest_df["CALCULATED_TCV"].fillna(0).sum() if not invest_df.empty else 0

def _fmt_m(v):
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"

st.markdown(f"""
<style>
.money-grid{{display:flex;gap:10px;margin:8px 0 10px 0;flex-wrap:wrap;}}
.money-card{{
    flex:1;min-width:160px;
    background:linear-gradient(135deg,#1e293b,#334155);
    border-radius:10px;padding:12px 18px;
    box-shadow:0 2px 6px rgba(0,0,0,0.18);
    display:flex;flex-direction:column;gap:3px;
}}
.mc-label{{font-size:0.67rem;font-weight:700;text-transform:uppercase;
           letter-spacing:0.08em;color:rgba(255,255,255,0.5);}}
.mc-value{{font-size:1.35rem;font-weight:900;color:white;
           font-variant-numeric:tabular-nums;line-height:1.1;}}
.mc-sub{{font-size:0.67rem;color:rgba(255,255,255,0.4);margin-top:2px;}}
</style>
<div class="money-grid">
  <div class="money-card">
    <span class="mc-label">Renewal ACV</span>
    <span class="mc-value">{_fmt_m(_renewal_acv)}</span>
    <span class="mc-sub">Open renewals · next 6 mo</span>
  </div>
  <div class="money-card">
    <span class="mc-label">Cap Pipeline ACV</span>
    <span class="mc-value">{_fmt_m(_cap_acv)}</span>
    <span class="mc-sub">Forecast ACV · all open</span>
  </div>
  <div class="money-card">
    <span class="mc-label">Conversion Opportunity</span>
    <span class="mc-value">{_fmt_m(_conv_opp)}</span>
    <span class="mc-sub">Predicted unused capacity</span>
  </div>
  <div class="money-card">
    <span class="mc-label">Investment Pipeline TCV</span>
    <span class="mc-value">{_fmt_m(_invest_tcv)}</span>
    <span class="mc-sub">Cap deals &gt;$500K · 2 qtrs</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── WoW SUMMARY ───────────────────────────────────────────────────────────────
_wow_uc   = load_wow_use_cases(days=days_window)
_wow_proj = load_wow_projects(days=days_window)


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

_ex_adv    = _ex_stages[_ex_stages["DIRECTION"] == "Advance"].drop_duplicates(subset=["USE_CASE_ID"], keep="first") if not _ex_stages.empty else pd.DataFrame()
_ex_reg    = _ex_stages[_ex_stages["DIRECTION"] == "Regression"].drop_duplicates(subset=["USE_CASE_ID"], keep="first") if not _ex_stages.empty else pd.DataFrame()
_ex_wins   = _wow_uc[(_wow_uc["FIELD"] == "Technical_Win__c") & (_wow_uc["NEW_VALUE"] == "Yes") & (_wow_uc["CURRENT_STAGE"].str.startswith("8") == False)].drop_duplicates(subset=["USE_CASE_ID"], keep="first")
_ex_gl     = _wow_uc[_wow_uc["FIELD"] == "Actual_Go_Live_Date__c"].drop_duplicates(subset=["USE_CASE_ID"], keep="first")
_ex_pstage = _wow_proj[_wow_proj["FIELD"] == "pse__Stage__c"]
_ex_comp   = _ex_pstage[_ex_pstage["NEW_VALUE"] == "Completed"]
_ex_stall  = _ex_pstage[_ex_pstage["NEW_VALUE"].isin(["Stalled", "Stalled - Expiring"])]

# ── 8-WEEK PIPELINE TREND ─────────────────────────────────────────────────────
_ot = new_opps_all.copy()
_ot["CREATED_DATE"] = pd.to_datetime(_ot["CREATED_DATE"], errors="coerce")
_ot["WEEK"] = _ot["CREATED_DATE"].dt.to_period("W").apply(lambda p: p.start_time)

_ut = new_uc_all.copy()
_ut["CREATED_DATE"] = pd.to_datetime(_ut["CREATED_DATE"], errors="coerce")
_ut["WEEK"] = _ut["CREATED_DATE"].dt.to_period("W").apply(lambda p: p.start_time)

_ow = _ot.groupby("WEEK").size().reset_index(name="New Opps")
_uw = _ut.groupby("WEEK").size().reset_index(name="New Use Cases")
_trend_df = _ow.merge(_uw, on="WEEK", how="outer").sort_values("WEEK").fillna(0).tail(8)
_trend_df["Week"] = _trend_df["WEEK"].apply(lambda x: x.strftime("%b %d") if pd.notna(x) else "")
_trend_df = _trend_df.set_index("Week")[["New Opps", "New Use Cases"]].astype(int)

with st.expander("📈 Pipeline Momentum — 8-Week Trend", expanded=False):
    st.caption("New opportunities and new use cases created per week. Based on last 90 days of data.")
    if not _trend_df.empty:
        st.bar_chart(_trend_df, color=["#3B82F6", "#9333EA"], height=220)
    else:
        st.caption("No trend data available.")

# ── THIS WEEK SECTION ────────────────────────────────────────────────────────
_ew_uc_n = len(_ex_adv) + len(_ex_reg) + len(_ex_wins)

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #92400e 0%, #b45309 55%, #d97706 100%);
    border-radius: 10px;
    padding: 12px 22px;
    margin: 8px 0 6px 0;
    box-shadow: 0 2px 10px rgba(146,64,14,0.3);
    display:flex; align-items:center; justify-content:space-between;
">
  <span style="color:white;font-weight:800;font-size:1rem;letter-spacing:0.03em;">\U0001f4c5 THIS WEEK</span>
  <span style="color:rgba(255,255,255,0.75);font-size:0.82rem;font-weight:600;">Last {days_window} days</span>
</div>
""", unsafe_allow_html=True)

def _ex_uc_link(row):
    uid = row.get("USE_CASE_ID")
    return f"{SFDC_BASE}/{uid}/view" if uid and str(uid).strip() else None

def _ex_proj_link(row):
    pid = row.get("PROJECT_ID")
    return f"{SFDC_BASE}/pse__Proj__c/{pid}/view" if pid and str(pid).strip() else None

def _prep_ex_proj(df_in):
    d = df_in.copy()
    d["PROJ_LINK"] = d.apply(_ex_proj_link, axis=1)
    d["CHANGE_DESC"] = d.apply(
        lambda r: f"{r['OLD_VALUE']} → {r['NEW_VALUE']}"
        if pd.notna(r.get("OLD_VALUE")) and pd.notna(r.get("NEW_VALUE"))
        else str(r.get("NEW_VALUE", "")),
        axis=1,
    )
    return d

def _tag_ex(df, label):
    d = df.copy()
    d["CHANGE"] = label
    return d

_ex_proj_cols = [
    {"col": "ACCOUNT_NAME",  "label": "Account"},
    {"col": "AE",           "label": "AE"},
    {"col": "PROJECT_NAME",  "label": "Project"},
    {"col": "PROJ_LINK",     "label": "SFDC",       "fmt": "link"},
    {"col": "CHANGE_DESC",   "label": "Change"},
    {"col": "CHANGED_AT",    "label": "Changed",    "fmt": "date"},
    {"col": "REVENUE_AMOUNT","label": "Revenue",    "fmt": "dollar"},
]

_stage_parts = []
if not _ex_adv.empty:
    _stage_parts.append(_tag_ex(_ex_adv, "\u2191 Stage Advance"))
if not _ex_reg.empty:
    _stage_parts.append(_tag_ex(_ex_reg, "\u2193 Stage Regression"))

_wins_parts = []
if not _ex_wins.empty:
    _tw_wins = _ex_wins.copy()
    _tw_wins["NEW_VALUE"] = "Tech Win \u2713"
    _wins_parts.append(_tag_ex(_tw_wins, "\u2713 Tech Win"))

_n_stage_changes = len(_ex_adv) + len(_ex_reg)
_n_wins = len(_ex_wins)

with st.expander(f"UC Changes ({_ew_uc_n})", expanded=False):
    st.caption("Use case stage advances, regressions, and technical wins in the selected timeframe.")
    _uc_tab_stage, _uc_tab_wins = st.tabs([
        f"Stage Changes ({_n_stage_changes})",
        f"Tech Wins ({_n_wins})",
    ])

    with _uc_tab_stage:
        if _stage_parts:
            _stage_merged = pd.concat(_stage_parts, ignore_index=True)
            _stage_merged["UC_LINK"] = _stage_merged.apply(_ex_uc_link, axis=1)
            _fc1, _fc2, _fc3 = st.columns([1.4, 1.4, 5])
            _dir_filter = _fc1.radio(
                "Direction", ["All", "Advances", "Regressions"],
                index=1, horizontal=True, key="exec_uc_dir",
                label_visibility="collapsed",
            )
            _min_stage = _fc2.selectbox(
                "From Stage \u2265", ["Any", "2", "3", "4", "5"],
                index=1, key="exec_uc_minstage",
                label_visibility="collapsed",
            )
            _fc1.caption("Direction")
            _fc2.caption("From Stage \u2265")
            _stage_filtered = _stage_merged.copy()
            if _dir_filter == "Advances":
                _stage_filtered = _stage_filtered[_stage_filtered["CHANGE"] == "\u2191 Stage Advance"]
            elif _dir_filter == "Regressions":
                _stage_filtered = _stage_filtered[_stage_filtered["CHANGE"] == "\u2193 Stage Regression"]
            if _min_stage != "Any":
                _stage_filtered = _stage_filtered[
                    _stage_filtered["OLD_VALUE"].apply(_stage_num_ex) >= int(_min_stage)
                ]
            if _stage_filtered.empty:
                empty_state("No stage changes match the current filters.")
            else:
                render_html_table(_stage_filtered, columns=[
                    {"col": "ACCOUNT_NAME",  "label": "Account"},
                    {"col": "AE",           "label": "AE"},
                    {"col": "USE_CASE_NAME", "label": "Use Case"},
                    {"col": "UC_LINK",       "label": "SFDC",          "fmt": "link"},
                    {"col": "CHANGE",        "label": "Change"},
                    {"col": "OLD_VALUE",     "label": "From"},
                    {"col": "NEW_VALUE",     "label": "To"},
                    {"col": "ACV",           "label": "UC eACV",       "fmt": "dollar"},
                    {"col": "CURRENT_STAGE", "label": "Current Stage"},
                    {"col": "DECISION_DATE", "label": "Decision Date", "fmt": "date"},
                    {"col": "CHANGED_AT",    "label": "Changed",       "fmt": "date"},
                ], height=max(120, min(450, len(_stage_filtered) * 38 + 60)))
        else:
            empty_state("No stage changes this week.")

    with _uc_tab_wins:
        if _wins_parts:
            _wins_merged = pd.concat(_wins_parts, ignore_index=True)
            _wins_merged["UC_LINK"] = _wins_merged.apply(_ex_uc_link, axis=1)
            render_html_table(_wins_merged, columns=[
                {"col": "ACCOUNT_NAME",  "label": "Account"},
                {"col": "AE",           "label": "AE"},
                {"col": "USE_CASE_NAME", "label": "Use Case"},
                {"col": "UC_LINK",       "label": "SFDC",          "fmt": "link"},
                {"col": "ACV",           "label": "UC eACV",       "fmt": "dollar"},
                {"col": "CURRENT_STAGE", "label": "Stage"},
                {"col": "DECISION_DATE", "label": "Decision Date", "fmt": "date"},
                {"col": "CHANGED_AT",    "label": "Changed",       "fmt": "date"},
            ], height=max(120, min(400, len(_wins_merged) * 38 + 60)))
        else:
            empty_state("No technical wins this week.")

with st.expander(f"Project Changes ({len(_ex_pstage)})", expanded=False):
    st.caption("PS project stage changes (advances, completions, and stalls) in the selected timeframe.")
    if _ex_pstage.empty:
        empty_state("No project stage changes this week.")
    else:
        render_html_table(_prep_ex_proj(_ex_pstage), columns=_ex_proj_cols, height=max(120, min(350, len(_ex_pstage) * 38 + 60)))

with st.expander(f"New Opportunities — last {days_window} days ({opp_n})", expanded=False):
    st.caption("New opportunities created in the selected timeframe across your scope.")
    if new_opps.empty:
        empty_state(f"No opportunities created in the last {days_window} days.")
    else:
        new_opps_display = new_opps.copy()
        new_opps_display["OPP_LINK"] = new_opps_display["OPPORTUNITY_ID"].apply(
            lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(new_opps_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OWNER",           "label": "AE"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",      "fmt": "link"},
            {"col": "AGREEMENT_TYPE",  "label": "Agreement Type"},
            {"col": "CLOSE_DATE",      "label": "Close",     "fmt": "date"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_ACV",       "label": "ACV",       "fmt": "dollar"},
            {"col": "CREATED_DATE",    "label": "Created",   "fmt": "date"},
        ], height=max(200, min(500, opp_n * 38 + 60)))

with st.expander(f"New Use Cases — last {days_window} days ({uc_n})", expanded=False):
    st.caption("New use cases created in the selected timeframe across your scope.")
    if new_uc.empty:
        empty_state(f"No use cases created in the last {days_window} days.")
    else:
        uc_display = new_uc.copy()
        uc_display["ACCT_LINK"] = uc_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(uc_display, columns=[
            {"col": "ACCOUNT_NAME",  "label": "Account"},
            {"col": "OWNER",         "label": "AE"},
            {"col": "ACCT_LINK",     "label": "SFDC",    "fmt": "link"},
            {"col": "USE_CASE_NAME", "label": "Use Case"},
            {"col": "STAGE",         "label": "Stage"},
            {"col": "CREATED_DATE",  "label": "Created", "fmt": "date"},
            {"col": "ACV",           "label": "eACV",    "fmt": "dollar"},
        ], height=max(200, min(500, uc_n * 38 + 60)))

# ── PIPELINE & CAPACITY SECTION ───────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 10px;
    padding: 12px 22px;
    margin: 16px 0 6px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    display:flex; align-items:center; justify-content:space-between;
">
  <span style="color:white;font-weight:800;font-size:1rem;letter-spacing:0.03em;">\U0001f4ca PIPELINE &amp; CAPACITY</span>
  <span style="color:rgba(255,255,255,0.55);font-size:0.78rem;">Fixed date windows \u2014 not affected by timeframe toggle</span>
</div>
""", unsafe_allow_html=True)

# ── Section 1: Software Renewals ──────────────────────────────────────────────
with st.expander(f"Upcoming Software Renewals — Next 6 Months ({sw_n})", expanded=False):
    st.caption("Open software renewal opportunities closing in the next 6 months. Excludes segment payments (Amount > $0 only).")
    if sw_renewals.empty:
        empty_state("No software renewal opportunities closing in the next 6 months.")
    else:
        sw_display = sw_renewals.copy()
        sw_display["OPP_LINK"] = sw_display["OPPORTUNITY_ID"].apply(
            lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
        )
        def _sw_urgency(row):
            try:
                days = (pd.to_datetime(row.get("CLOSE_DATE")) - today).days
            except Exception:
                return None
            if days < 30:  return "#fff1f2"
            if days < 60:  return "#fffbeb"
            return None
        render_html_table(sw_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OWNER",           "label": "AE"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",     "fmt": "link"},
            {"col": "STAGE_NAME",      "label": "Stage"},
            {"col": "CLOSE_DATE",      "label": "Close",    "fmt": "date"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "TOTAL_ACV",            "label": "Target ACV",  "fmt": "dollar"},
            {"col": "RENEWAL_ACV",           "label": "Prev ACV",    "fmt": "dollar"},
            {"col": "PRODUCT_FORECAST_TCV",  "label": "Fcst TCV",    "fmt": "dollar"},
        ], height=max(200, min(400, sw_n * 38 + 60)), row_style_fn=_sw_urgency)

# ── Section 2: Services Renewals ──────────────────────────────────────────────
with st.expander(f"Upcoming Services Renewals ({svc_n})", expanded=False):
    st.caption("Active PS&T projects ending in the next 6 months — candidates for renewal or extension discussions.")
    if svc_renewals.empty:
        empty_state("No active PS projects ending in the next 6 months.")
    else:
        svc_display = svc_renewals.copy()
        svc_display["ACCT_LINK"] = svc_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(svc_display, columns=[
            {"col": "ACCOUNT_NAME",  "label": "Account"},
            {"col": "AE",            "label": "AE"},
            {"col": "ACCT_LINK",     "label": "SFDC",     "fmt": "link"},
            {"col": "PROJECT_NAME",  "label": "Project"},
            {"col": "PROJECT_STAGE", "label": "Stage"},
            {"col": "START_DATE",    "label": "Start",    "fmt": "date"},
            {"col": "END_DATE",      "label": "End",      "fmt": "date"},
            {"col": "DAYS_TO_END",   "label": "Days Left","fmt": "number"},
            {"col": "PROJECT_MANAGER","label": "PM"},
        ], height=max(200, min(400, svc_n * 38 + 60)))

# ── Section 5: Capacity Conversion Candidates ─────────────────────────────────
with st.expander(f"Capacity Conversion Candidates ({cv_n})", expanded=False):
    st.caption("Capacity accounts predicted to have ≥$75K unused at contract end — opportunity to convert remaining capacity to services.")
    if conv_candidates.empty:
        empty_state("No capacity conversion candidates found.")
    else:
        conv_display = conv_candidates[[
            "ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
            "CONTRACT_END_DATE", "DAYS_LEFT", "TOTAL_CAP", "ACTUAL_CONSUMPTION_YTD_C", "OVERAGE_UNDERAGE_PREDICTION"
        ]].copy()
        conv_display["ACCT_LINK"] = conv_display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        render_html_table(conv_display, columns=[
            {"col": "ACCOUNT_NAME",       "label": "Account"},
            {"col": "ACCOUNT_OWNER",      "label": "AE"},
            {"col": "ACCT_LINK",          "label": "SFDC",       "fmt": "link"},
            {"col": "DM",                 "label": "DM"},
            {"col": "CONTRACT_END_DATE",  "label": "End Date",   "fmt": "date"},
            {"col": "DAYS_LEFT",          "label": "Days Left",  "fmt": "number"},
            {"col": "TOTAL_CAP",                    "label": "Total Cap",        "fmt": "dollar"},
            {"col": "ACTUAL_CONSUMPTION_YTD_C",       "label": "YTD Consumption", "fmt": "dollar"},
            {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Predicted Underage", "fmt": "dollar"},
        ], height=max(200, min(500, cv_n * 38 + 60)))

# ── Section 6: Investment Candidates ──────────────────────────────────────────
with st.expander(f"Investment Candidates — {' & '.join(invest_fqs)} ({invest_n})", expanded=False):
    st.caption(f"Future capacity opportunities (Calc TCV ≥$500K) closing in {' or '.join(invest_fqs)} — accounts worth proactive investment discussions.")
    if invest_df.empty:
        empty_state("No investment candidates found.")
    else:
        inv_display = invest_df.copy()
        inv_display["OPP_LINK"] = inv_display.apply(
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )
        inv_display["EST_INVESTMENT"] = inv_display["CALCULATED_TCV"].fillna(0) * 0.10
        render_html_table(inv_display, columns=[
            {"col": "ACCOUNT_NAME",    "label": "Account"},
            {"col": "OWNER",           "label": "AE"},
            {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
            {"col": "OPP_LINK",        "label": "SFDC",       "fmt": "link"},
            {"col": "AGREEMENT_TYPE",  "label": "Agreement Type"},
            {"col": "CLOSE_DATE",      "label": "Close Date", "fmt": "date"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "CALCULATED_TCV",  "label": "Calc TCV",   "fmt": "dollar"},
            {"col": "EST_INVESTMENT",  "label": "Est. Invest","fmt": "dollar"},
        ], height=max(200, min(500, invest_n * 38 + 60)))

