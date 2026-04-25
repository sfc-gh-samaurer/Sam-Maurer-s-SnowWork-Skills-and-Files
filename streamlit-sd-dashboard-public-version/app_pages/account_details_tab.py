import streamlit as st
import pandas as pd

from data import (
    load_hierarchy,
    load_accounts_for_scope,
    load_capacity_renewals,
    load_exec_software_renewals,
)

from constants import SFDC_BASE
from components import section_banner, empty_state


st.markdown("""
<style>
/* ── Account Header ── */
.acct-header {
    background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    box-shadow: 0 4px 16px rgba(41,181,232,0.22);
}
.acct-header-left { flex: 1; min-width: 0; }
.acct-name {
    color: white !important;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.acct-meta-line {
    color: rgba(255,255,255,0.72);
    font-size: 0.82rem;
    margin-bottom: 10px;
}
.acct-pills { display: flex; gap: 7px; flex-wrap: wrap; margin-bottom: 12px; }
.pill {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    white-space: nowrap;
}
.pill-blue   { background: rgba(255,255,255,0.22); color: white; }
.pill-gray   { background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.85); }
.pill-green  { background: #10b981; color: white; }
.pill-red    { background: #ef4444; color: white; }
.pill-amber  { background: #f59e0b; color: white; }
.acct-team {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}
.acct-team-item { display: flex; flex-direction: column; gap: 1px; }
.acct-team-label { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(255,255,255,0.55); }
.acct-team-value { font-weight: 600; font-size: 0.86rem; color: white; }
.acct-header-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 10px;
    margin-left: 24px;
    flex-shrink: 0;
}
.acct-arr-badge {
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 10px 18px;
    text-align: center;
    min-width: 110px;
}
.arr-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.6); }
.arr-value { font-size: 1.5rem; font-weight: 900; color: white; line-height: 1.1; margin-top: 2px; }
.arr-sub { font-size: 0.68rem; color: rgba(255,255,255,0.55); margin-top: 2px; }
.sfdc-link {
    display: inline-block;
    color: rgba(255,255,255,0.65);
    font-size: 0.75rem;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.3);
    padding-bottom: 1px;
}
.sfdc-link:hover { color: white; border-color: white; }

/* ── Snapshot Cards ── */
.snapshot-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    border-top: 3px solid #29B5E8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    overflow: hidden;
    margin-bottom: 0;
}
.card-header {
    background: #f8fafc;
    padding: 9px 16px;
    font-size: 0.66rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.card-count {
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 10px;
    padding: 1px 8px;
    font-size: 0.7rem;
    font-weight: 800;
}
.card-body { padding: 14px 16px; }
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
    gap: 8px;
}
.stat-row:last-child { border-bottom: none; }
.stat-label { font-size: 0.79rem; color: #64748b; flex-shrink: 0; }
.stat-value { font-size: 0.86rem; font-weight: 700; color: #0f172a; text-align: right; }
.none-msg { color: #94a3b8; font-size: 0.82rem; font-style: italic; padding: 4px 0; }


/* ── Stage distribution bar ── */
.stage-dist { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.stage-dist-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    color: #475569;
}
.stage-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}

/* ── Data tables ── */
.data-table { width: 100%; border-collapse: collapse; font-size: 0.79rem; }
.data-table th {
    font-size: 0.64rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #94a3b8;
    font-weight: 700;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px 8px 6px 0;
    text-align: left;
}
.data-table td {
    padding: 6px 8px 6px 0;
    border-bottom: 1px solid #f8fafc;
    color: #1e293b;
    vertical-align: top;
    line-height: 1.4;
}
.data-table tr:last-child td { border-bottom: none; }
.td-muted { color: #94a3b8 !important; font-style: italic; }
.td-link { color: #0284c7; text-decoration: none; font-weight: 600; }
.td-link:hover { text-decoration: underline; }

/* ── KPI strip ── */
.kpi-strip { display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
.kpi-strip-item {
    background: #f8fafc;
    border-radius: 8px;
    padding: 7px 13px;
    border: 1px solid #e2e8f0;
}
.kpi-strip-label { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700; }
.kpi-strip-value { font-size: 1.05rem; font-weight: 800; color: #0f172a; line-height: 1.2; }

/* ── Comments / notes block ── */
.comment-block {
    background: #f8fafc;
    border-left: 3px solid #29B5E8;
    border-radius: 0 6px 6px 0;
    padding: 7px 11px;
    font-size: 0.78rem;
    color: #334155;
    line-height: 1.5;
    margin-top: 5px;
}
.notes-block {
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    border-radius: 0 6px 6px 0;
    padding: 7px 11px;
    font-size: 0.78rem;
    color: #451a03;
    line-height: 1.5;
    margin-top: 5px;
}
.risk-block {
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    border-radius: 0 6px 6px 0;
    padding: 7px 11px;
    font-size: 0.78rem;
    color: #450a0a;
    line-height: 1.5;
    margin-top: 5px;
}
.section-spacer { margin-bottom: 16px; }

/* ── Footprint grid ── */
.footprint-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.footprint-item {
    background: #f8fafc;
    border-radius: 8px;
    padding: 8px 10px;
    text-align: center;
    border: 1px solid #e2e8f0;
}
.footprint-label { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700; }
.footprint-value { font-size: 1.1rem; font-weight: 800; color: #0f172a; }
</style>
""", unsafe_allow_html=True)


def fmt_currency(v, default="—"):
    try:
        v = float(v)
        if v == 0:
            return default
        if abs(v) >= 1_000_000:
            return f"${v/1_000_000:.2f}M"
        if abs(v) >= 1_000:
            return f"${v/1_000:.0f}K"
        return f"${v:,.0f}"
    except Exception:
        return default


def fmt_date(v, default="—"):
    if pd.isna(v) or v is None or v == "":
        return default
    try:
        return pd.to_datetime(v).strftime("%b %d, %Y")
    except Exception:
        return str(v)


def esc(s):
    return (str(s) or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


STAGE_DOTS = {"1":"#3b82f6","2":"#22c55e","3":"#eab308","4":"#f97316","5":"#f97316","6":"#10b981"}

# ── Load hierarchy metadata (lightweight, cached) ────────────────────────────
hierarchy_df = load_hierarchy()

section_banner("Account Details", "Account snapshot — select a Theater, District, and Account")

# ── Cascading filters ─────────────────────────────────────────────────────────
st.markdown('<div style="margin-bottom:4px"></div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns([1, 1, 1, 1])

theaters = sorted(hierarchy_df["THEATER"].dropna().unique())

with f1:
    theater = st.selectbox(
        "Theater",
        options=[""] + theaters,
        key="acct_theater",
        placeholder="All Theaters",
        index=0,
    )

regions_avail = sorted(
    hierarchy_df[hierarchy_df["THEATER"] == theater]["REGION"].dropna().unique()
) if theater else sorted(hierarchy_df["REGION"].dropna().unique())

with f2:
    region = st.selectbox(
        "Region",
        options=[""] + regions_avail,
        key="acct_region",
        placeholder="All Regions",
        index=0,
    )

_dis_mask = pd.Series([True] * len(hierarchy_df), index=hierarchy_df.index)
if theater:
    _dis_mask = _dis_mask & (hierarchy_df["THEATER"] == theater)
if region:
    _dis_mask = _dis_mask & (hierarchy_df["REGION"] == region)
districts_avail = sorted(hierarchy_df[_dis_mask]["DISTRICT"].dropna().unique())

with f3:
    district = st.selectbox(
        "District",
        options=[""] + districts_avail,
        key="acct_district",
        placeholder="Select a District",
        index=0,
    )

# ── Load accounts only once a district is selected ───────────────────────────
if not district:
    empty_state("Select a Theater and District above to load accounts.", icon="🗺️")
    st.stop()

accounts_df = load_accounts_for_scope(district)

aes_avail = ["All AEs"] + sorted(accounts_df["ACCOUNT_OWNER"].dropna().unique())

with f4:
    selected_ae = st.selectbox(
        "Account Executive",
        options=aes_avail,
        key="acct_ae",
        index=0,
    )

if selected_ae and selected_ae != "All AEs":
    filtered_accounts = accounts_df[accounts_df["ACCOUNT_OWNER"] == selected_ae]
else:
    filtered_accounts = accounts_df

account_names = sorted(filtered_accounts["ACCOUNT_NAME"].dropna().unique())

# ── Account selector ──────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:6px;margin-bottom:2px"></div>', unsafe_allow_html=True)
selected = st.selectbox(
    "account_select",
    options=[""] + account_names,
    index=0,
    key="acct_detail_select",
    label_visibility="collapsed",
    placeholder="🔍  Search or select an account...",
)

if not selected:
    st.markdown(
        f'<p style="color:#94a3b8;font-size:0.88rem;margin-top:6px;">{len(account_names)} accounts in {district}{" — " + selected_ae if selected_ae != "All AEs" else ""}. Select one to view its snapshot.</p>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Load per-account datasets ─────────────────────────────────────────────────
cap_df     = load_capacity_renewals()
renewal_df = load_exec_software_renewals()

acct_row  = accounts_df[accounts_df["ACCOUNT_NAME"] == selected]
acct_cap  = cap_df[cap_df["ACCOUNT_NAME"] == selected]
acct_ren  = renewal_df[renewal_df["ACCOUNT_NAME"] == selected]

if acct_row.empty:
    st.warning("Account not found in dataset.")
    st.stop()

a = acct_row.iloc[0]
sfdc_id   = str(a.get("SALESFORCE_ACCOUNT_ID") or "")
sfdc_url  = f"{SFDC_BASE}/Account/{sfdc_id}/view" if sfdc_id else "#"
arr       = fmt_currency(a.get("ARR", 0), "—")
aps       = fmt_currency(a.get("APS", 0), "—")
tier      = str(a.get("TIER") or "")
industry  = str(a.get("INDUSTRY") or "")
sub_ind   = str(a.get("SUBINDUSTRY") or "")
segment   = str(a.get("SEGMENT") or "")
ae        = str(a.get("ACCOUNT_OWNER") or "—")
se        = str(a.get("LEAD_SE") or "—")
dm        = str(a.get("DM") or "—")
rvp       = str(a.get("RVP") or "—")
city      = str(a.get("BILLING_CITY") or "")
state_    = str(a.get("BILLING_STATE") or "")
country   = str(a.get("BILLING_COUNTRY") or "")
employees = a.get("NUMBER_OF_EMPLOYEES")
last_act  = fmt_date(a.get("LAST_ACTIVITY_DATE"), "—")
maturity  = a.get("MATURITY_SCORE_C")
cons_risk = a.get("CONSUMPTION_RISK_C")
strategy  = str(a.get("ACCOUNT_STRATEGY_C") or "")
risk_note = str(a.get("ACCOUNT_RISK_C") or "")
comments  = str(a.get("ACCOUNT_COMMENTS_C") or "")
risk_mit  = str(a.get("CONSUMPTION_RISK_MITIGATION_STEPS_C") or "")
pred_1yv  = fmt_currency(a.get("PREDICTED_1YV", 0), "—")
pred_3yv  = fmt_currency(a.get("PREDICTED_3YV", 0), "—")
total_acc = a.get("TOTAL_ACCOUNTS")
aws_acc   = a.get("AWS_ACCOUNTS")
az_acc    = a.get("AZURE_ACCOUNTS")
gcp_acc   = a.get("GCP_ACCOUNTS")

location = ", ".join(filter(None, [city, state_, country]))

# ── Account Header ────────────────────────────────────────────────────────────
pills_html = ""
if tier:
    pills_html += f'<span class="pill pill-blue">{esc(tier)}</span>'
if segment:
    pills_html += f'<span class="pill pill-gray">{esc(segment)}</span>'
if industry:
    pills_html += f'<span class="pill pill-gray">{esc(industry)}</span>'
if sub_ind and sub_ind != industry:
    pills_html += f'<span class="pill pill-gray">{esc(sub_ind)}</span>'
if not acct_cap.empty:
    pills_html += '<span class="pill pill-green">Capacity</span>'
if cons_risk:
    pills_html += '<span class="pill pill-red">Consumption Risk</span>'

meta_parts = []
if location:
    meta_parts.append(f"📍 {location}")
if employees:
    try:
        meta_parts.append(f"👥 {int(employees):,} employees")
    except Exception:
        pass
if last_act != "—":
    meta_parts.append(f"🕐 Last Activity: {last_act}")
meta_line = "  ·  ".join(meta_parts) if meta_parts else ""

st.markdown(f"""
<div class="acct-header">
  <div class="acct-header-left">
    <p class="acct-name">{esc(selected)}</p>
    <div class="acct-pills">{pills_html}</div>
    {"<div class='acct-meta-line'>" + esc(meta_line) + "</div>" if meta_line else ""}
    <div class="acct-team">
      <div class="acct-team-item">
        <span class="acct-team-label">Account Exec</span>
        <span class="acct-team-value">{esc(ae)}</span>
      </div>
      <div class="acct-team-item">
        <span class="acct-team-label">Lead SE</span>
        <span class="acct-team-value">{esc(se)}</span>
      </div>
      <div class="acct-team-item">
        <span class="acct-team-label">District Manager</span>
        <span class="acct-team-value">{esc(dm)}</span>
      </div>
      <div class="acct-team-item">
        <span class="acct-team-label">RVP</span>
        <span class="acct-team-value">{esc(rvp)}</span>
      </div>
    </div>
  </div>
  <div class="acct-header-right">
    <div class="acct-arr-badge">
      <div class="arr-label">ARR</div>
      <div class="arr-value">{arr}</div>
      {"<div class='arr-sub'>APS: " + aps + "</div>" if aps != "—" else ""}
    </div>
    <a class="sfdc-link" href="{sfdc_url}" target="_blank">Open in Salesforce →</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ROW 1: Contract & Capacity | Software Renewal | Snowflake Footprint ────────
col1, col2, col3 = st.columns(3)

# --- Contract & Capacity ---
with col1:
    if not acct_cap.empty:
        r = acct_cap.iloc[0]
        cap_html = f"""
        <div class="stat-row"><span class="stat-label">Total Capacity</span><span class="stat-value">{fmt_currency(r.get("TOTAL_CAP"))}</span></div>
        <div class="stat-row"><span class="stat-label">Contract Start</span><span class="stat-value">{fmt_date(r.get("CONTRACT_START_DATE"))}</span></div>
        <div class="stat-row"><span class="stat-label">Contract End</span><span class="stat-value">{fmt_date(r.get("CONTRACT_END_DATE"))}</span></div>
        <div class="stat-row"><span class="stat-label">Overage Date</span><span class="stat-value">{fmt_date(r.get("OVERAGE_DATE"))}</span></div>
        """
    else:
        cap_html = '<p class="none-msg">Not a capacity customer.</p>'
    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">Contract &amp; Capacity</div>
      <div class="card-body">{cap_html}</div>
    </div>""", unsafe_allow_html=True)

# --- Software Renewal ---
with col2:
    if not acct_ren.empty:
        r = acct_ren.iloc[0]
        ren_html = f"""
        <div class="stat-row"><span class="stat-label">Opportunity</span><span class="stat-value" style="font-size:0.76rem">{esc(str(r.get("OPPORTUNITY_NAME") or "—")[:45])}</span></div>
        <div class="stat-row"><span class="stat-label">Stage</span><span class="stat-value">{esc(str(r.get("STAGE_NAME") or "—"))}</span></div>
        <div class="stat-row"><span class="stat-label">Forecast</span><span class="stat-value">{esc(str(r.get("FORECAST_STATUS") or "—"))}</span></div>
        <div class="stat-row"><span class="stat-label">ACV</span><span class="stat-value">{fmt_currency(r.get("TOTAL_ACV"))}</span></div>
        <div class="stat-row"><span class="stat-label">Close Date</span><span class="stat-value">{fmt_date(r.get("CLOSE_DATE"))}</span></div>
        """
    else:
        ren_html = '<p class="none-msg">No upcoming software renewal found.</p>'
    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">Software Renewal</div>
      <div class="card-body">{ren_html}</div>
    </div>""", unsafe_allow_html=True)

# --- Snowflake Footprint & Signals ---
with col3:
    footprint_rows = ""
    if total_acc:
        footprint_rows += f'<div class="stat-row"><span class="stat-label">Snowflake Accounts</span><span class="stat-value">{int(total_acc)}</span></div>'
    if aws_acc:
        footprint_rows += f'<div class="stat-row"><span class="stat-label">AWS</span><span class="stat-value">{int(aws_acc)}</span></div>'
    if az_acc:
        footprint_rows += f'<div class="stat-row"><span class="stat-label">Azure</span><span class="stat-value">{int(az_acc)}</span></div>'
    if gcp_acc:
        footprint_rows += f'<div class="stat-row"><span class="stat-label">GCP</span><span class="stat-value">{int(gcp_acc)}</span></div>'
    if pred_1yv != "—":
        footprint_rows += f'<div class="stat-row"><span class="stat-label">Predicted 1-Yr Value</span><span class="stat-value">{pred_1yv}</span></div>'
    if pred_3yv != "—":
        footprint_rows += f'<div class="stat-row"><span class="stat-label">Predicted 3-Yr Value</span><span class="stat-value">{pred_3yv}</span></div>'
    if maturity:
        footprint_rows += f'<div class="stat-row"><span class="stat-label">Maturity Score</span><span class="stat-value">{maturity}</span></div>'
    fp_body = footprint_rows if footprint_rows else '<p class="none-msg">No footprint data available.</p>'
    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">Snowflake Footprint &amp; Signals</div>
      <div class="card-body">{fp_body}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div style="margin-top:16px"></div>', unsafe_allow_html=True)

# ── ROW 2: Account Intelligence (full width, conditional) ─────────────────────
has_intel = any([strategy, risk_note, comments, risk_mit])
if has_intel:
    intel_parts = []
    if strategy:
        intel_parts.append(f'<div class="intel-block"><div class="intel-label">Account Strategy</div><div class="comment-block">{esc(strategy)}</div></div>')
    if risk_note:
        intel_parts.append(f'<div class="intel-block"><div class="intel-label">Account Risk</div><div class="risk-block">{esc(risk_note)}</div></div>')
    if risk_mit:
        intel_parts.append(f'<div class="intel-block"><div class="intel-label">Risk Mitigation</div><div class="notes-block">{esc(risk_mit)}</div></div>')
    if comments:
        intel_parts.append(f'<div class="intel-block"><div class="intel-label">Account Comments</div><div class="comment-block">{esc(comments)}</div></div>')

    n = len(intel_parts)
    cols_per_row = 2
    grid_html = '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px;">'
    for part in intel_parts:
        grid_html += part
    if n % 2 == 1:
        grid_html += '<div></div>'
    grid_html += '</div>'

    st.markdown(f"""
    <style>
    .intel-label { font-size: 0.63rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em; color: #94a3b8; margin-bottom: 4px; }
    </style>
    <div class="snapshot-card">
      <div class="card-header">Account Intelligence</div>
      <div class="card-body">{grid_html}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="snapshot-card">
      <div class="card-header">Account Intelligence</div>
      <div class="card-body"><p class="none-msg">No account intelligence data on file for this account.</p></div>
    </div>""", unsafe_allow_html=True)

