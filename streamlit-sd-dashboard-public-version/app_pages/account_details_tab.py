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
.acct-header-left { flex: 1; }
.acct-name {
    color: white !important;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.acct-pills { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.pill {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.pill-blue  { background: rgba(255,255,255,0.22); color: white; }
.pill-gray  { background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.88); }
.pill-green { background: #10b981; color: white; }
.pill-amber { background: #f59e0b; color: white; }
.acct-team {
    color: rgba(255,255,255,0.82);
    font-size: 0.9rem;
    display: flex;
    gap: 18px;
    flex-wrap: wrap;
}
.acct-team-item { display: flex; flex-direction: column; gap: 1px; }
.acct-team-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.65; }
.acct-team-value { font-weight: 600; font-size: 0.88rem; color: white; }
.acct-arr-badge {
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 12px 20px;
    text-align: center;
    min-width: 120px;
    flex-shrink: 0;
    margin-left: 20px;
}
.arr-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.65); }
.arr-value { font-size: 1.6rem; font-weight: 900; color: white; line-height: 1.1; margin-top: 2px; }
.sfdc-link {
    display: inline-block;
    margin-top: 10px;
    color: rgba(255,255,255,0.7);
    font-size: 0.78rem;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.3);
}
.sfdc-link:hover { color: white; }

/* ── Snapshot Cards ── */
.snapshot-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    border-top: 3px solid #29B5E8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    overflow: hidden;
    height: 100%;
    margin-bottom: 0;
}
.card-header {
    background: #f8fafc;
    padding: 9px 16px;
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    border-bottom: 1px solid #e2e8f0;
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
.stat-label { font-size: 0.8rem; color: #64748b; flex-shrink: 0; }
.stat-value { font-size: 0.88rem; font-weight: 700; color: #0f172a; text-align: right; }
.stat-value-muted { font-size: 0.88rem; color: #94a3b8; text-align: right; font-style: italic; }
.none-msg { color: #94a3b8; font-size: 0.82rem; font-style: italic; padding: 6px 0; }

/* ── Use Case Stages ── */
.uc-stage-pill {
    display: inline-block;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap;
}
.stage-early   { background: #eff6ff; color: #1d4ed8; }
.stage-mid     { background: #fef3c7; color: #92400e; }
.stage-late    { background: #dcfce7; color: #166534; }
.stage-default { background: #f1f5f9; color: #475569; }

/* ── Inline data tables ── */
.data-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.data-table th {
    font-size: 0.66rem;
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
}
.data-table tr:last-child td { border-bottom: none; }
.td-muted { color: #94a3b8 !important; font-style: italic; }
.td-link { color: #0284c7; text-decoration: none; font-weight: 600; }
.td-link:hover { text-decoration: underline; }

/* ── Section KPI strip ── */
.kpi-strip {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}
.kpi-strip-item {
    background: #f8fafc;
    border-radius: 8px;
    padding: 8px 14px;
    border: 1px solid #e2e8f0;
}
.kpi-strip-label { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700; }
.kpi-strip-value { font-size: 1.1rem; font-weight: 800; color: #0f172a; }

/* ── Comments block ── */
.comment-block {
    background: #f8fafc;
    border-left: 3px solid #29B5E8;
    border-radius: 0 6px 6px 0;
    padding: 8px 12px;
    font-size: 0.8rem;
    color: #334155;
    line-height: 1.5;
    margin-top: 4px;
}
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


def uc_stage_class(stage):
    if not stage:
        return "stage-default"
    s = stage.lower()
    if any(x in s for x in ["1 -", "2 -", "3 -", "discovery", "sql", "identified"]):
        return "stage-early"
    if any(x in s for x in ["4 -", "5 -", "scope", "validation", "proof"]):
        return "stage-mid"
    if any(x in s for x in ["6 -", "7 -", "tech win", "won", "live"]):
        return "stage-late"
    return "stage-default"


# ── Load all data ─────────────────────────────────────────────────────────────
accounts_df  = load_accounts_base()
cap_df       = load_capacity_renewals()
uc_df        = load_use_cases()
pipe_df      = load_ps_pipeline()
proj_df      = load_ps_projects_active()
renewal_df   = load_exec_software_renewals()

# ── Account selector ──────────────────────────────────────────────────────────
account_names = sorted(accounts_df["ACCOUNT_NAME"].dropna().unique())

st.markdown('<div class="tab-banner"><p class="tab-banner-title">Account Details</p></div>', unsafe_allow_html=True)

selected = st.selectbox(
    "Search or select an account",
    options=[""] + account_names,
    index=0,
    key="acct_detail_select",
    label_visibility="collapsed",
    placeholder="🔍  Search or select an account...",
)

if not selected:
    st.markdown('<p style="color:#94a3b8; font-size:0.95rem; margin-top:12px;">Select an account above to view its full snapshot.</p>', unsafe_allow_html=True)
    st.stop()

# ── Filter datasets ───────────────────────────────────────────────────────────
acct_row    = accounts_df[accounts_df["ACCOUNT_NAME"] == selected]
acct_cap    = cap_df[cap_df["ACCOUNT_NAME"] == selected]
acct_uc     = uc_df[uc_df["ACCOUNT_NAME"] == selected]
acct_pipe   = pipe_df[pipe_df["ACCOUNT_NAME"] == selected]
acct_proj   = proj_df[proj_df["ACCOUNT_NAME"] == selected]
acct_ren    = renewal_df[renewal_df["ACCOUNT_NAME"] == selected]

if acct_row.empty:
    st.warning("Account not found in dataset.")
    st.stop()

a = acct_row.iloc[0]
sfdc_id  = a.get("SALESFORCE_ACCOUNT_ID", "")
sfdc_url = f"{SFDC_BASE}/Account/{sfdc_id}/view" if sfdc_id else "#"
arr      = fmt_currency(a.get("ARR", 0), "—")
tier     = a.get("TIER", "") or ""
industry = a.get("INDUSTRY", "") or ""
sub_ind  = a.get("SUBINDUSTRY", "") or ""
ae       = a.get("ACCOUNT_OWNER", "") or "—"
se       = a.get("LEAD_SE", "") or "—"
dm       = a.get("DM", "") or "—"

# ── Account Header ────────────────────────────────────────────────────────────
pills_html = ""
if tier:
    pills_html += f'<span class="pill pill-blue">{tier}</span>'
if industry:
    pills_html += f'<span class="pill pill-gray">{industry}</span>'
if sub_ind and sub_ind != industry:
    pills_html += f'<span class="pill pill-gray">{sub_ind}</span>'
is_cap = not acct_cap.empty
if is_cap:
    pills_html += '<span class="pill pill-green">Capacity</span>'

st.markdown(f"""
<div class="acct-header">
  <div class="acct-header-left">
    <p class="acct-name">{selected}</p>
    <div class="acct-pills">{pills_html}</div>
    <div class="acct-team">
      <div class="acct-team-item">
        <span class="acct-team-label">Account Exec</span>
        <span class="acct-team-value">{ae}</span>
      </div>
      <div class="acct-team-item">
        <span class="acct-team-label">Lead SE</span>
        <span class="acct-team-value">{se}</span>
      </div>
      <div class="acct-team-item">
        <span class="acct-team-label">District Manager</span>
        <span class="acct-team-value">{dm}</span>
      </div>
    </div>
    <a class="sfdc-link" href="{sfdc_url}" target="_blank">Open in Salesforce →</a>
  </div>
  <div class="acct-arr-badge">
    <div class="arr-label">ARR</div>
    <div class="arr-value">{arr}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ROW 1: Contract & Capacity | Use Cases | Renewal ─────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])

# --- Contract & Capacity ---
with col1:
    if is_cap:
        cap_row = acct_cap.iloc[0]
        total_cap    = fmt_currency(cap_row.get("TOTAL_CAP"))
        contract_start = fmt_date(cap_row.get("CONTRACT_START_DATE"))
        contract_end   = fmt_date(cap_row.get("CONTRACT_END_DATE"))
        overage_date   = fmt_date(cap_row.get("OVERAGE_DATE"))
        cap_html = f"""
        <div class="stat-row"><span class="stat-label">Total Capacity</span><span class="stat-value">{total_cap}</span></div>
        <div class="stat-row"><span class="stat-label">Contract Start</span><span class="stat-value">{contract_start}</span></div>
        <div class="stat-row"><span class="stat-label">Contract End</span><span class="stat-value">{contract_end}</span></div>
        <div class="stat-row"><span class="stat-label">Overage Date</span><span class="stat-value">{overage_date}</span></div>
        """
    else:
        cap_html = '<p class="none-msg">Not a capacity customer</p>'

    st.markdown(f"""
    <div class="snapshot-card">
      <div class="card-header">Contract & Capacity</div>
      <div class="card-body">{cap_html}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Use Cases ---
with col2:
    uc_count = len(acct_uc)
    if uc_count > 0:
        uc_rows = ""
        for _, uc in acct_uc.iterrows():
            name    = uc.get("USE_CASE_NAME") or uc.get("USE_CASE_NUMBER") or "—"
            stage   = uc.get("STAGE") or "—"
            acv     = fmt_currency(uc.get("ACV"), "—")
            owner   = uc.get("OWNER") or "—"
            dd      = fmt_date(uc.get("DECISION_DATE"), "—")
            ns      = (uc.get("NEXT_STEPS") or "")[:80]
            ns_html = f'<br/><span style="color:#94a3b8;font-size:0.75rem">{ns}{"..." if len(str(uc.get("NEXT_STEPS") or "")) > 80 else ""}</span>' if ns else ""
            sc      = uc_stage_class(stage)
            uc_rows += f"""
            <tr>
              <td>{name}{ns_html}</td>
              <td><span class="uc-stage-pill {sc}">{stage}</span></td>
              <td>{acv}</td>
              <td>{owner}</td>
              <td>{dd}</td>
            </tr>"""
        uc_body = f"""
        <div class="kpi-strip">
          <div class="kpi-strip-item">
            <div class="kpi-strip-label">Total Use Cases</div>
            <div class="kpi-strip-value">{uc_count}</div>
          </div>
          <div class="kpi-strip-item">
            <div class="kpi-strip-label">Total eACV</div>
            <div class="kpi-strip-value">{fmt_currency(acct_uc["ACV"].sum())}</div>
          </div>
        </div>
        <table class="data-table">
          <thead><tr><th>Use Case</th><th>Stage</th><th>eACV</th><th>Owner</th><th>Decision</th></tr></thead>
          <tbody>{uc_rows}</tbody>
        </table>"""
    else:
        uc_body = '<p class="none-msg">No active use cases found.</p>'

    st.markdown(f"""
    <div class="snapshot-card">
      <div class="card-header">Open Use Cases</div>
      <div class="card-body">{uc_body}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Renewal ---
with col3:
    if not acct_ren.empty:
        ren_row = acct_ren.iloc[0]
        ren_name  = (ren_row.get("OPPORTUNITY_NAME") or "—")[:40]
        ren_stage = ren_row.get("STAGE_NAME") or "—"
        ren_fc    = ren_row.get("FORECAST_STATUS") or "—"
        ren_acv   = fmt_currency(ren_row.get("TOTAL_ACV"))
        ren_close = fmt_date(ren_row.get("CLOSE_DATE"))
        ren_html = f"""
        <div class="stat-row"><span class="stat-label">Opportunity</span><span class="stat-value" style="font-size:0.78rem">{ren_name}</span></div>
        <div class="stat-row"><span class="stat-label">Stage</span><span class="stat-value">{ren_stage}</span></div>
        <div class="stat-row"><span class="stat-label">Forecast</span><span class="stat-value">{ren_fc}</span></div>
        <div class="stat-row"><span class="stat-label">ACV</span><span class="stat-value">{ren_acv}</span></div>
        <div class="stat-row"><span class="stat-label">Close Date</span><span class="stat-value">{ren_close}</span></div>
        """
    else:
        ren_html = '<p class="none-msg">No upcoming software renewal found.</p>'

    st.markdown(f"""
    <div class="snapshot-card">
      <div class="card-header">Software Renewal</div>
      <div class="card-body">{ren_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

# ── ROW 2: PS&T Pipeline | Active PS Projects ─────────────────────────────────
col4, col5 = st.columns([3, 2])

# --- PS&T Pipeline ---
with col4:
    if not acct_pipe.empty:
        total_tcv = acct_pipe["TOTAL_PST_TCV"].fillna(0).sum()
        pipe_rows = ""
        for _, p in acct_pipe.iterrows():
            opp_name  = (p.get("OPPORTUNITY_NAME") or "—")[:45]
            opp_id    = p.get("OPPORTUNITY_ID") or ""
            opp_link  = f'<a class="td-link" href="{SFDC_BASE}/Opportunity/{opp_id}/view" target="_blank">{opp_name}</a>' if opp_id else opp_name
            tcv       = fmt_currency(p.get("TOTAL_PST_TCV"))
            fc        = p.get("PS_FORECAST_CATEGORY") or p.get("FORECAST_STATUS") or "—"
            seller    = p.get("PS_SELLER_NAME") or "—"
            comments  = (p.get("PS_COMMENTS") or "")[:100]
            comment_html = f'<div class="comment-block">{comments}{"..." if len(str(p.get("PS_COMMENTS") or "")) > 100 else ""}</div>' if comments else ""
            pipe_rows += f"""
            <tr>
              <td>{opp_link}{comment_html}</td>
              <td>{tcv}</td>
              <td>{fc}</td>
              <td>{seller}</td>
            </tr>"""
        pipe_body = f"""
        <div class="kpi-strip">
          <div class="kpi-strip-item">
            <div class="kpi-strip-label">Open Opps</div>
            <div class="kpi-strip-value">{len(acct_pipe)}</div>
          </div>
          <div class="kpi-strip-item">
            <div class="kpi-strip-label">Total PST TCV</div>
            <div class="kpi-strip-value">{fmt_currency(total_tcv)}</div>
          </div>
        </div>
        <table class="data-table">
          <thead><tr><th>Opportunity</th><th>TCV</th><th>PS Forecast</th><th>PS Seller</th></tr></thead>
          <tbody>{pipe_rows}</tbody>
        </table>"""
    else:
        pipe_body = '<p class="none-msg">No open PS&T pipeline opportunities.</p>'

    st.markdown(f"""
    <div class="snapshot-card">
      <div class="card-header">PS&T Pipeline</div>
      <div class="card-body">{pipe_body}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Active PS Projects ---
with col5:
    if not acct_proj.empty:
        proj_rows = ""
        for _, p in acct_proj.iterrows():
            pname   = (p.get("PROJECT_NAME") or "—")[:40]
            pid     = p.get("PROJECT_ID") or ""
            plink   = f'<a class="td-link" href="{SFDC_BASE}/pse__Proj__c/{pid}/view" target="_blank">{pname}</a>' if pid else pname
            stage   = p.get("PROJECT_STAGE") or "—"
            pm      = p.get("PROJECT_MANAGER") or "—"
            end_dt  = fmt_date(p.get("END_DATE"))
            rev     = fmt_currency(p.get("REVENUE_AMOUNT"))
            proj_rows += f"""
            <tr>
              <td>{plink}</td>
              <td>{stage}</td>
              <td>{pm}</td>
              <td>{end_dt}</td>
              <td>{rev}</td>
            </tr>"""
        proj_body = f"""
        <div class="kpi-strip">
          <div class="kpi-strip-item">
            <div class="kpi-strip-label">Active Projects</div>
            <div class="kpi-strip-value">{len(acct_proj)}</div>
          </div>
        </div>
        <table class="data-table">
          <thead><tr><th>Project</th><th>Stage</th><th>PM</th><th>End</th><th>Revenue</th></tr></thead>
          <tbody>{proj_rows}</tbody>
        </table>"""
    else:
        proj_body = '<p class="none-msg">No active PS projects.</p>'

    st.markdown(f"""
    <div class="snapshot-card">
      <div class="card-header">Active PS Projects</div>
      <div class="card-body">{proj_body}</div>
    </div>
    """, unsafe_allow_html=True)
