import streamlit as st
import pandas as pd

from data import (
    load_accounts_base,
    load_capacity_renewals,
    load_use_cases,
    load_ps_pipeline,
    load_ps_projects_active,
    load_exec_software_renewals,
)

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

PURSUIT_STAGES = {
    "1 - Discovery",
    "2 - Scoping",
    "3 - Technical / Business Validation",
    "4 - Use Case Won / Migration Plan",
    "5 - Implementation In Progress",
    "6 - Implementation Complete",
}

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

/* ── Use Case Stages ── */
.uc-stage-pill {
    display: inline-block;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    white-space: nowrap;
}
.stage-1 { background: #eff6ff; color: #1d4ed8; }
.stage-2 { background: #f0fdf4; color: #15803d; }
.stage-3 { background: #fefce8; color: #854d0e; }
.stage-4 { background: #fef3c7; color: #92400e; }
.stage-5 { background: #fff7ed; color: #9a3412; }
.stage-6 { background: #dcfce7; color: #166534; }
.stage-default { background: #f1f5f9; color: #475569; }

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


def stage_class(stage):
    if not stage:
        return "stage-default"
    n = stage.split(" - ")[0].strip()
    return f"stage-{n}" if n in {"1","2","3","4","5","6"} else "stage-default"


STAGE_DOTS = {"1":"#3b82f6","2":"#22c55e","3":"#eab308","4":"#f97316","5":"#f97316","6":"#10b981"}

# ── Load all data ─────────────────────────────────────────────────────────────
accounts_df = load_accounts_base()
cap_df      = load_capacity_renewals()
uc_df       = load_use_cases()
pipe_df     = load_ps_pipeline()
proj_df     = load_ps_projects_active()
renewal_df  = load_exec_software_renewals()

# ── Account selector ──────────────────────────────────────────────────────────
account_names = sorted(accounts_df["ACCOUNT_NAME"].dropna().unique())

st.markdown('<div class="tab-banner"><p class="tab-banner-title">Account Details</p></div>', unsafe_allow_html=True)

selected = st.selectbox(
    "account_select",
    options=[""] + account_names,
    index=0,
    key="acct_detail_select",
    label_visibility="collapsed",
    placeholder="🔍  Search or select an account...",
)

if not selected:
    st.markdown('<p style="color:#94a3b8;font-size:0.95rem;margin-top:12px;">Select an account above to view its full snapshot.</p>', unsafe_allow_html=True)
    st.stop()

# ── Filter datasets ───────────────────────────────────────────────────────────
acct_row  = accounts_df[accounts_df["ACCOUNT_NAME"] == selected]
acct_cap  = cap_df[cap_df["ACCOUNT_NAME"] == selected]
acct_uc   = uc_df[(uc_df["ACCOUNT_NAME"] == selected) & (uc_df["STAGE"].isin(PURSUIT_STAGES))].sort_values("STAGE")
acct_pipe = pipe_df[pipe_df["ACCOUNT_NAME"] == selected]
acct_proj = proj_df[proj_df["ACCOUNT_NAME"] == selected]
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

# ── ROW 1: Contract & Capacity | Use Cases | Renewal ──────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])

# --- Contract & Capacity ---
with col1:
    if not acct_cap.empty:
        r = acct_cap.iloc[0]
        total_cap = fmt_currency(r.get("TOTAL_CAP"))
        c_start   = fmt_date(r.get("CONTRACT_START_DATE"))
        c_end     = fmt_date(r.get("CONTRACT_END_DATE"))
        ov_date   = fmt_date(r.get("OVERAGE_DATE"))
        cap_html  = f"""
        <div class="stat-row"><span class="stat-label">Total Capacity</span><span class="stat-value">{total_cap}</span></div>
        <div class="stat-row"><span class="stat-label">Contract Start</span><span class="stat-value">{c_start}</span></div>
        <div class="stat-row"><span class="stat-label">Contract End</span><span class="stat-value">{c_end}</span></div>
        <div class="stat-row"><span class="stat-label">Overage Date</span><span class="stat-value">{ov_date}</span></div>
        """
    else:
        cap_html = '<p class="none-msg">Not a capacity customer.</p>'

    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">Contract &amp; Capacity</div>
      <div class="card-body">{cap_html}</div>
    </div><div class="section-spacer"></div>""", unsafe_allow_html=True)

# --- Use Cases ---
with col2:
    uc_count = len(acct_uc)
    if uc_count > 0:
        stage_counts = acct_uc["STAGE"].value_counts()
        dist_html = '<div class="stage-dist">'
        for stg, cnt in stage_counts.items():
            n = str(stg).split(" - ")[0].strip()
            dot_color = STAGE_DOTS.get(n, "#94a3b8")
            dist_html += f'<span class="stage-dist-item"><span class="stage-dot" style="background:{dot_color}"></span>{esc(str(stg))} ({cnt})</span>'
        dist_html += '</div>'

        uc_rows = ""
        for _, uc in acct_uc.iterrows():
            name  = str(uc.get("USE_CASE_NAME") or uc.get("USE_CASE_NUMBER") or "—")
            stage = str(uc.get("STAGE") or "—")
            acv   = fmt_currency(uc.get("ACV"), "—")
            owner = str(uc.get("OWNER") or "—")
            dd    = fmt_date(uc.get("DECISION_DATE"), "—")
            ns    = str(uc.get("NEXT_STEPS") or "")[:90]
            ns_html = f'<br><span style="color:#94a3b8;font-size:0.72rem">{esc(ns)}{"…" if len(str(uc.get("NEXT_STEPS") or "")) > 90 else ""}</span>' if ns else ""
            sc    = stage_class(stage)
            uc_rows += f"""<tr>
              <td>{esc(name)}{ns_html}</td>
              <td><span class="uc-stage-pill {sc}">{esc(stage)}</span></td>
              <td>{acv}</td>
              <td>{esc(owner)}</td>
              <td>{dd}</td>
            </tr>"""

        total_eacv = fmt_currency(acct_uc["ACV"].sum())
        uc_body = f"""
        <div class="kpi-strip">
          <div class="kpi-strip-item"><div class="kpi-strip-label">In Pursuit</div><div class="kpi-strip-value">{uc_count}</div></div>
          <div class="kpi-strip-item"><div class="kpi-strip-label">Total eACV</div><div class="kpi-strip-value">{total_eacv}</div></div>
        </div>
        {dist_html}
        <table class="data-table">
          <thead><tr><th>Use Case</th><th>Stage</th><th>eACV</th><th>Owner</th><th>Decision Date</th></tr></thead>
          <tbody>{uc_rows}</tbody>
        </table>"""
    else:
        uc_body = '<p class="none-msg">No active use cases in pursuit.</p>'

    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">
        <span>Open Use Cases</span>
        {"<span class='card-count'>" + str(uc_count) + "</span>" if uc_count > 0 else ""}
      </div>
      <div class="card-body">{uc_body}</div>
    </div><div class="section-spacer"></div>""", unsafe_allow_html=True)

# --- Software Renewal ---
with col3:
    if not acct_ren.empty:
        r = acct_ren.iloc[0]
        opp_name  = str(r.get("OPPORTUNITY_NAME") or "—")[:45]
        ren_stage = str(r.get("STAGE_NAME") or "—")
        ren_fc    = str(r.get("FORECAST_STATUS") or "—")
        ren_acv   = fmt_currency(r.get("TOTAL_ACV"))
        ren_close = fmt_date(r.get("CLOSE_DATE"))
        ren_html  = f"""
        <div class="stat-row"><span class="stat-label">Opportunity</span><span class="stat-value" style="font-size:0.76rem">{esc(opp_name)}</span></div>
        <div class="stat-row"><span class="stat-label">Stage</span><span class="stat-value">{esc(ren_stage)}</span></div>
        <div class="stat-row"><span class="stat-label">Forecast</span><span class="stat-value">{esc(ren_fc)}</span></div>
        <div class="stat-row"><span class="stat-label">ACV</span><span class="stat-value">{ren_acv}</span></div>
        <div class="stat-row"><span class="stat-label">Close Date</span><span class="stat-value">{ren_close}</span></div>
        """
    else:
        ren_html = '<p class="none-msg">No upcoming software renewal found.</p>'

    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">Software Renewal</div>
      <div class="card-body">{ren_html}</div>
    </div><div class="section-spacer"></div>""", unsafe_allow_html=True)

# ── ROW 2: PS&T Pipeline | Active PS Projects ─────────────────────────────────
col4, col5 = st.columns([3, 2])

# --- PS&T Pipeline ---
with col4:
    if not acct_pipe.empty:
        total_tcv = acct_pipe["TOTAL_PST_TCV"].fillna(0).sum()
        pipe_rows = ""
        for _, p in acct_pipe.iterrows():
            opp_name = str(p.get("OPPORTUNITY_NAME") or "—")[:50]
            opp_id   = str(p.get("OPPORTUNITY_ID") or "")
            opp_link = f'<a class="td-link" href="{SFDC_BASE}/Opportunity/{opp_id}/view" target="_blank">{esc(opp_name)}</a>' if opp_id else esc(opp_name)
            tcv      = fmt_currency(p.get("TOTAL_PST_TCV"))
            fc       = str(p.get("PS_FORECAST_CATEGORY") or p.get("FORECAST_STATUS") or "—")
            seller   = str(p.get("PS_SELLER_NAME") or "—")
            comm_raw = str(p.get("PS_COMMENTS") or "")[:120]
            comm_html = f'<div class="comment-block">{esc(comm_raw)}{"…" if len(str(p.get("PS_COMMENTS") or "")) > 120 else ""}</div>' if comm_raw else ""
            pipe_rows += f"""<tr>
              <td>{opp_link}{comm_html}</td>
              <td>{tcv}</td>
              <td>{esc(fc)}</td>
              <td>{esc(seller)}</td>
            </tr>"""
        pipe_body = f"""
        <div class="kpi-strip">
          <div class="kpi-strip-item"><div class="kpi-strip-label">Open Opps</div><div class="kpi-strip-value">{len(acct_pipe)}</div></div>
          <div class="kpi-strip-item"><div class="kpi-strip-label">Total PST TCV</div><div class="kpi-strip-value">{fmt_currency(total_tcv)}</div></div>
        </div>
        <table class="data-table">
          <thead><tr><th>Opportunity</th><th>TCV</th><th>PS Forecast</th><th>PS Seller</th></tr></thead>
          <tbody>{pipe_rows}</tbody>
        </table>"""
    else:
        pipe_body = '<p class="none-msg">No open PS&amp;T pipeline opportunities.</p>'

    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">
        <span>PS&amp;T Pipeline</span>
        {"<span class='card-count'>" + str(len(acct_pipe)) + "</span>" if not acct_pipe.empty else ""}
      </div>
      <div class="card-body">{pipe_body}</div>
    </div><div class="section-spacer"></div>""", unsafe_allow_html=True)

# --- Active PS Projects ---
with col5:
    if not acct_proj.empty:
        proj_rows = ""
        for _, p in acct_proj.iterrows():
            pname  = str(p.get("PROJECT_NAME") or "—")[:42]
            pid    = str(p.get("PROJECT_ID") or "")
            plink  = f'<a class="td-link" href="{SFDC_BASE}/pse__Proj__c/{pid}/view" target="_blank">{esc(pname)}</a>' if pid else esc(pname)
            stage  = str(p.get("PROJECT_STAGE") or "—")
            pm     = str(p.get("PROJECT_MANAGER") or "—")
            end_dt = fmt_date(p.get("END_DATE"))
            rev    = fmt_currency(p.get("REVENUE_AMOUNT"))
            proj_rows += f"""<tr>
              <td>{plink}</td>
              <td>{esc(stage)}</td>
              <td>{esc(pm)}</td>
              <td>{end_dt}</td>
              <td>{rev}</td>
            </tr>"""
        proj_body = f"""
        <div class="kpi-strip">
          <div class="kpi-strip-item"><div class="kpi-strip-label">Active Projects</div><div class="kpi-strip-value">{len(acct_proj)}</div></div>
        </div>
        <table class="data-table">
          <thead><tr><th>Project</th><th>Stage</th><th>PM</th><th>End Date</th><th>Revenue</th></tr></thead>
          <tbody>{proj_rows}</tbody>
        </table>"""
    else:
        proj_body = '<p class="none-msg">No active PS projects.</p>'

    st.markdown(f"""<div class="snapshot-card">
      <div class="card-header">
        <span>Active PS Projects</span>
        {"<span class='card-count'>" + str(len(acct_proj)) + "</span>" if not acct_proj.empty else ""}
      </div>
      <div class="card-body">{proj_body}</div>
    </div><div class="section-spacer"></div>""", unsafe_allow_html=True)

# ── ROW 3: Account Intelligence | Snowflake Footprint ─────────────────────────
has_intel = any([strategy, risk_note, comments, risk_mit, cons_risk])
has_footprint = any([total_acc, aws_acc, az_acc, gcp_acc, pred_1yv != "—", maturity])

if has_intel or has_footprint:
    col6, col7 = st.columns([3, 2])

    # --- Account Intelligence ---
    with col6:
        intel_parts = []
        if strategy:
            intel_parts.append(f'<div style="margin-bottom:8px"><div class="kpi-strip-label" style="margin-bottom:3px">Account Strategy</div><div class="comment-block">{esc(strategy)}</div></div>')
        if risk_note:
            intel_parts.append(f'<div style="margin-bottom:8px"><div class="kpi-strip-label" style="margin-bottom:3px">Account Risk</div><div class="risk-block">{esc(risk_note)}</div></div>')
        if risk_mit:
            intel_parts.append(f'<div style="margin-bottom:8px"><div class="kpi-strip-label" style="margin-bottom:3px">Risk Mitigation</div><div class="notes-block">{esc(risk_mit)}</div></div>')
        if comments:
            intel_parts.append(f'<div style="margin-bottom:8px"><div class="kpi-strip-label" style="margin-bottom:3px">Account Comments</div><div class="comment-block">{esc(comments)}</div></div>')

        intel_body = "".join(intel_parts) if intel_parts else '<p class="none-msg">No account intelligence notes.</p>'
        st.markdown(f"""<div class="snapshot-card">
          <div class="card-header">Account Intelligence</div>
          <div class="card-body">{intel_body}</div>
        </div>""", unsafe_allow_html=True)

    # --- Snowflake Footprint ---
    with col7:
        footprint_rows = ""
        if total_acc:
            footprint_rows += f'<div class="stat-row"><span class="stat-label">Total Snowflake Accounts</span><span class="stat-value">{int(total_acc)}</span></div>'
        if aws_acc:
            footprint_rows += f'<div class="stat-row"><span class="stat-label">AWS Accounts</span><span class="stat-value">{int(aws_acc)}</span></div>'
        if az_acc:
            footprint_rows += f'<div class="stat-row"><span class="stat-label">Azure Accounts</span><span class="stat-value">{int(az_acc)}</span></div>'
        if gcp_acc:
            footprint_rows += f'<div class="stat-row"><span class="stat-label">GCP Accounts</span><span class="stat-value">{int(gcp_acc)}</span></div>'
        if pred_1yv != "—":
            footprint_rows += f'<div class="stat-row"><span class="stat-label">Predicted 1-Yr Value</span><span class="stat-value">{pred_1yv}</span></div>'
        if pred_3yv != "—":
            footprint_rows += f'<div class="stat-row"><span class="stat-label">Predicted 3-Yr Value</span><span class="stat-value">{pred_3yv}</span></div>'
        if maturity:
            footprint_rows += f'<div class="stat-row"><span class="stat-label">Maturity Score</span><span class="stat-value">{maturity}</span></div>'

        footprint_body = footprint_rows if footprint_rows else '<p class="none-msg">No footprint data available.</p>'
        st.markdown(f"""<div class="snapshot-card">
          <div class="card-header">Snowflake Footprint &amp; Signals</div>
          <div class="card-body">{footprint_body}</div>
        </div>""", unsafe_allow_html=True)
