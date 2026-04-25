import streamlit as st
import pandas as pd
import json

from data import (
    load_accounts_for_scope,
    load_account_search_list,
    load_capacity_renewals,
    load_exec_software_renewals,
    load_use_cases,
    load_ps_projects_active,
    load_ps_pipeline,
    load_capacity_pipeline,
    save_user_prefs,
    render_html_table,
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


def uc_health_score(row):
    score = 0
    stage_str = str(row.get("STAGE", "") or "")
    try:
        sn = int(stage_str.split(" - ")[0].strip())
        score += {1: 5, 2: 10, 3: 18, 4: 25, 5: 30}.get(sn, 35 if sn >= 6 else 0)
    except Exception:
        pass
    tw = row.get("TECHNICAL_WIN")
    if tw is True or str(tw).lower() in ("true", "1", "yes"):
        score += 25
    dd = row.get("DECISION_DATE")
    if pd.notna(dd) and dd:
        try:
            score += 15 if pd.to_datetime(dd) > pd.Timestamp.now() else 7
        except Exception:
            pass
    try:
        if float(row.get("ACV", 0) or 0) > 0:
            score += 10
    except Exception:
        pass
    try:
        if float(row.get("DAYS_IN_STAGE", 999) or 999) < 60:
            score += 5
    except Exception:
        pass
    if "stall" in str(row.get("USE_CASE_STATUS", "") or "").lower():
        score -= 15
    return max(0, min(100, score))


def health_badge(score):
    if score >= 71:
        return f'<span style="background:#dcfce7;color:#16a34a;padding:2px 9px;border-radius:10px;font-size:0.69rem;font-weight:700;">● {score}</span>'
    if score >= 41:
        return f'<span style="background:#fef3c7;color:#d97706;padding:2px 9px;border-radius:10px;font-size:0.69rem;font-weight:700;">● {score}</span>'
    return f'<span style="background:#fee2e2;color:#dc2626;padding:2px 9px;border-radius:10px;font-size:0.69rem;font-weight:700;">● {score}</span>'

# ── Load account list scoped to sidebar DMs ───────────────────────────────────
_search_list = load_account_search_list()
_selected_dms = st.session_state.get("selected_dms") or []

section_banner("Account Details", "Account snapshot — search for an account in your scope")

if not _selected_dms:
    empty_state("Select a Scope in the sidebar to load accounts.", icon="🗺️")
    st.stop()

_scoped_df = _search_list[_search_list["DM"].isin(_selected_dms)]
account_names = sorted(_scoped_df["ACCOUNT_NAME"].dropna().unique().tolist())

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
        f'<p style="color:#94a3b8;font-size:0.88rem;margin-top:6px;">{len(account_names)} accounts in scope. Select one to view its snapshot.</p>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Load per-account datasets ─────────────────────────────────────────────────
_acct_district = _scoped_df.loc[_scoped_df["ACCOUNT_NAME"] == selected, "DISTRICT_NAME"]
_acct_district = _acct_district.iloc[0] if not _acct_district.empty else ""
accounts_df = load_accounts_for_scope(_acct_district) if _acct_district else pd.DataFrame()

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
      <div class="arr-label">ACV</div>
      <div class="arr-value">{arr}</div>
    </div>
    <a class="sfdc-link" href="{sfdc_url}" target="_blank">Open in Salesforce →</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Pin / Unpin ───────────────────────────────────────────────────────────────
_pinned_names = [p["name"] for p in st.session_state.get("_pinned_accounts", [])]
_is_pinned    = selected in _pinned_names
_pin_label    = "⭐ Unpin Account" if _is_pinned else "☆ Pin Account"
if st.button(_pin_label, key="acct_pin_btn", type="secondary"):
    _cur_pins = st.session_state.get("_pinned_accounts", [])
    if _is_pinned:
        _cur_pins = [p for p in _cur_pins if p["name"] != selected]
    else:
        _cur_pins.append({
            "name":     selected,
            "theater":  st.session_state.get("acct_theater", ""),
            "region":   st.session_state.get("acct_region", ""),
            "district": district,
        })
    st.session_state["_pinned_accounts"] = _cur_pins
    _pin_prefs = {
        "sf_theater": st.session_state.get("sf_theater", []),
        "sf_region":  st.session_state.get("sf_region", []),
        "sf_pm":      st.session_state.get("sf_pm", []),
        "sf_district":st.session_state.get("sf_district", []),
        "filter_presets": st.session_state.get("_filter_presets", []),
        "pinned_accounts": _cur_pins,
        "last_seen_at": st.session_state.get("_last_seen_at", ""),
    }
    save_user_prefs(_pin_prefs)
    st.rerun()
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

# ─────────────────────────────────────────────────────────────────────────────
# ── SECTION: Use Cases ───────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
uc_all = load_use_cases()
acct_ucs = uc_all[uc_all["ACCOUNT_NAME"] == selected].copy()

st.markdown('<p class="sf-section-label">Use Cases</p>', unsafe_allow_html=True)

if acct_ucs.empty:
    empty_state("No active use cases found for this account.")
else:
    acct_ucs["HEALTH"] = acct_ucs.apply(uc_health_score, axis=1)
    acct_ucs["HEALTH_BADGE"] = acct_ucs["HEALTH"].apply(health_badge)
    acct_ucs = acct_ucs.sort_values("HEALTH", ascending=True)

    _tw_count = int((acct_ucs["TECHNICAL_WIN"].isin([True, "true", "True", "1", 1])).sum())
    _avg_health = int(acct_ucs["HEALTH"].mean()) if not acct_ucs.empty else 0
    _total_eacv = acct_ucs["ACV"].fillna(0).sum()
    _adv_count = 0
    for _s in acct_ucs["STAGE"].dropna():
        try:
            if int(str(_s).split(" - ")[0].strip()) >= 4:
                _adv_count += 1
        except Exception:
            pass

    _uc_kpis = [
        ("Total UCs", str(len(acct_ucs))),
        ("Tech Wins", str(_tw_count)),
        ("Avg Health", str(_avg_health)),
        ("Total eACV", fmt_currency(_total_eacv, "$0")),
        ("Stage 4+", str(int(_adv_count))),
    ]
    _kpi_items = "".join(
        f'<div class="kpi-strip-item"><div class="kpi-strip-label">{lbl}</div><div class="kpi-strip-value">{val}</div></div>'
        for lbl, val in _uc_kpis
    )
    st.markdown(f'<div class="kpi-strip">{_kpi_items}</div>', unsafe_allow_html=True)

    acct_ucs["UC_SFDC_LINK"] = acct_ucs["USE_CASE_ID"].apply(
        lambda x: f"{SFDC_BASE}/{x}/view" if pd.notna(x) and x else None
    )
    render_html_table(acct_ucs, columns=[
        {"col": "HEALTH_BADGE",    "label": "Health",         "fmt": "html"},
        {"col": "USE_CASE_NAME",   "label": "Use Case"},
        {"col": "UC_SFDC_LINK",    "label": "SFDC",           "fmt": "link"},
        {"col": "STAGE",           "label": "Stage"},
        {"col": "ACV",             "label": "eACV",           "fmt": "dollar"},
        {"col": "DECISION_DATE",   "label": "Decision Date",  "fmt": "date"},
        {"col": "DAYS_IN_STAGE",   "label": "Days in Stage",  "fmt": "number"},
        {"col": "USE_CASE_STATUS", "label": "Status"},
    ], height=max(160, min(500, len(acct_ucs) * 38 + 60)))

# ─────────────────────────────────────────────────────────────────────────────
# ── SECTION: Open Opportunities ──────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="sf-section-label">Open Opportunities</p>', unsafe_allow_html=True)

_sd_pipe = load_ps_pipeline()
_cap_pipe = load_capacity_pipeline()

_sd_acct = _sd_pipe[_sd_pipe["ACCOUNT_NAME"] == selected].copy() if not _sd_pipe.empty else pd.DataFrame()
_cap_acct = _cap_pipe[_cap_pipe["ACCOUNT_NAME"] == selected].copy() if not _cap_pipe.empty else pd.DataFrame()

if not _sd_acct.empty:
    _sd_acct["OPP_TYPE"] = "PS & Services"
    if "TOTAL_ACV" not in _sd_acct.columns:
        _sd_acct["TOTAL_ACV"] = None
if not _cap_acct.empty:
    _cap_acct["OPP_TYPE"] = "Capacity Renewal"
    if "TOTAL_ACV" not in _cap_acct.columns and "CALCULATED_TCV" in _cap_acct.columns:
        _cap_acct["TOTAL_ACV"] = _cap_acct["CALCULATED_TCV"]

_opp_cols = ["OPPORTUNITY_NAME", "OPPORTUNITY_ID", "OPP_TYPE", "STAGE_NAME", "FORECAST_STATUS", "CLOSE_DATE", "TOTAL_ACV"]
_opps_combined = pd.concat(
    [df[[c for c in _opp_cols if c in df.columns]] for df in [_sd_acct, _cap_acct] if not df.empty],
    ignore_index=True
) if not (_sd_acct.empty and _cap_acct.empty) else pd.DataFrame()

if _opps_combined.empty:
    empty_state("No open opportunities found for this account.")
else:
    _opps_combined["OPP_LINK"] = _opps_combined["OPPORTUNITY_ID"].apply(
        lambda x: f"{SFDC_BASE}/Opportunity/{x}/view" if pd.notna(x) and x else None
    )
    render_html_table(_opps_combined, columns=[
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK",         "label": "SFDC",        "fmt": "link"},
        {"col": "OPP_TYPE",         "label": "Type"},
        {"col": "STAGE_NAME",       "label": "Stage"},
        {"col": "FORECAST_STATUS",  "label": "Forecast"},
        {"col": "CLOSE_DATE",       "label": "Close Date",  "fmt": "date"},
        {"col": "TOTAL_ACV",        "label": "ACV",         "fmt": "dollar"},
    ], height=max(120, min(400, len(_opps_combined) * 38 + 60)))

# ─────────────────────────────────────────────────────────────────────────────
# ── SECTION: Active PS Engagements ───────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="sf-section-label">Active PS Engagements</p>', unsafe_allow_html=True)

_ps_all = load_ps_projects_active()
_ps_acct = _ps_all[_ps_all["ACCOUNT_NAME"] == selected].copy() if not _ps_all.empty else pd.DataFrame()

if _ps_acct.empty:
    empty_state("No active PS engagements found for this account.")
else:
    def _ps_card(r):
        def _sv(key, default="—"):
            v = r.get(key)
            return default if v is None or (not isinstance(v, str) and pd.isna(v)) else str(v)
        stage = esc(_sv("PROJECT_STAGE"))
        pct = r.get("PCT_HOURS_COMPLETE")
        pct_str = f"{float(pct):.0f}%" if pct is not None and not (isinstance(pct, float) and pd.isna(pct)) else "—"
        svc = esc(_sv("SERVICE_TYPE"))
        billing = esc(_sv("BILLING_TYPE"))
        end_d = fmt_date(r.get("END_DATE"), "—")
        pm = esc(_sv("PROJECT_MANAGER"))
        notes = _sv("STATUS_NOTES", "")
        notes_html = f'<div class="comment-block" style="margin-top:7px">{esc(notes)}</div>' if notes.strip() else ""
        stage_color = {"In Progress": "#22c55e", "Stalled": "#ef4444", "Stalled - Expiring": "#dc2626",
                       "Pipeline": "#3b82f6", "Out Year": "#94a3b8"}.get(stage, "#94a3b8")
        return f"""
        <div class="snapshot-card" style="margin-bottom:10px">
          <div class="card-header">
            {esc(_sv("PROJECT_NAME"))}
            <span style="background:{stage_color}22;color:{stage_color};padding:2px 9px;border-radius:10px;font-size:0.68rem;font-weight:700;">{stage}</span>
          </div>
          <div class="card-body" style="font-size:0.8rem;color:#475569">
            Service: <strong>{svc}</strong> &nbsp;·&nbsp; Billing: <strong>{billing}</strong>
            &nbsp;·&nbsp; % Complete: <strong>{pct_str}</strong>
            &nbsp;·&nbsp; End: <strong>{end_d}</strong>
            &nbsp;·&nbsp; PM: <strong>{pm}</strong>
            {notes_html}
          </div>
        </div>"""

    _ps_show = _ps_acct.head(5)
    _ps_extra = _ps_acct.iloc[5:] if len(_ps_acct) > 5 else pd.DataFrame()
    for _, _row in _ps_show.iterrows():
        st.markdown(_ps_card(_row), unsafe_allow_html=True)
    if not _ps_extra.empty:
        with st.expander(f"Show {len(_ps_extra)} more project(s)"):
            for _, _row in _ps_extra.iterrows():
                st.markdown(_ps_card(_row), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ── SECTION: Strategic Insights (claude-4-opus) ───────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p class="sf-section-label">Strategic Insights</p>', unsafe_allow_html=True)
st.caption("AI-generated Practice Manager briefing — use cases in pursuit, at-risk signals, services opportunities, and recommended next steps for the AE conversation.")


def _build_pm_insights_prompt(acct_name, acct_data, ucs, opps, ps_proj, cap_data):
    a_d = acct_data

    cap_text = "No capacity contract on file."
    if not cap_data.empty:
        cr = cap_data.iloc[0]
        cap_text = (
            f"Total Capacity: {fmt_currency(cr.get('TOTAL_CAP'))}"
            f" | Contract End: {fmt_date(cr.get('CONTRACT_END_DATE'))}"
            f" | Predicted Underage: {fmt_currency(cr.get('OVERAGE_UNDERAGE_PREDICTION'))}"
        )

    uc_lines, at_risk_lines = [], []
    if not ucs.empty:
        for _, u in ucs.sort_values("STAGE", ascending=False).iterrows():
            tw = "yes" if u.get("TECHNICAL_WIN") in [True, "true", "True", "1", 1] else "no"
            dd = fmt_date(u.get("DECISION_DATE"))
            line = f"  - {esc(str(u.get('USE_CASE_NAME','')))} | Stage: {esc(str(u.get('STAGE','')))} | Health: {u.get('HEALTH',0)} | eACV: {fmt_currency(u.get('ACV'))} | TechWin: {tw} | Decision: {dd}"
            uc_lines.append(line)
            if u.get("HEALTH", 100) < 41:
                at_risk_lines.append(line)

    opp_lines = []
    if not opps.empty:
        for _, o in opps.iterrows():
            opp_lines.append(f"  - {esc(str(o.get('OPPORTUNITY_NAME','')))} | Type: {o.get('OPP_TYPE','')} | Stage: {o.get('STAGE_NAME','')} | ACV: {fmt_currency(o.get('TOTAL_ACV'))} | Close: {fmt_date(o.get('CLOSE_DATE'))}")

    ps_lines = []
    if not ps_proj.empty:
        for _, p in ps_proj.iterrows():
            pct = p.get("PCT_HOURS_COMPLETE")
            ps_lines.append(f"  - {esc(str(p.get('PROJECT_NAME','')))} | Stage: {p.get('PROJECT_STAGE','')} | {f'{pct:.0f}% complete' if pd.notna(pct) else ''} | Type: {p.get('SERVICE_TYPE','')}")

    def _sv(key, default=""):
        v = a_d.get(key)
        if v is None:
            return default
        try:
            if pd.isna(v):
                return default
        except Exception:
            pass
        return str(v)

    strategy = _sv("ACCOUNT_STRATEGY_C")
    risk_note = _sv("ACCOUNT_RISK_C")

    prompt = f"""You are a Snowflake Professional Services Practice Manager advisor preparing a briefing.

Analyze this Snowflake customer account and return 5-7 numbered, specific action items that help a Practice Manager understand how to generate services business and what to bring to the Account Executive.

ACCOUNT: {acct_name}
Tier: {_sv('TIER')} | Segment: {_sv('SEGMENT')} | Industry: {_sv('INDUSTRY')}
ACV: {fmt_currency(a_d.get('ARR'))} | Employees: {_sv('NUMBER_OF_EMPLOYEES', '—')}
AE: {_sv('ACCOUNT_OWNER')} | Lead SE: {_sv('LEAD_SE')} | DM: {_sv('DM')}
Consumption Risk: {_sv('CONSUMPTION_RISK_C')} | Maturity Score: {_sv('MATURITY_SCORE_C')}
{'Account Strategy: ' + strategy if strategy else ''}
{'Account Risk Notes: ' + risk_note if risk_note else ''}

CAPACITY CONTRACT:
{cap_text}

USE CASES IN PURSUIT ({len(ucs)} active, avg health score {int(ucs['HEALTH'].mean()) if not ucs.empty else 'n/a'}):
{chr(10).join(uc_lines) if uc_lines else '  None'}

AT-RISK USE CASES (health score < 41):
{chr(10).join(at_risk_lines) if at_risk_lines else '  None identified'}

OPEN OPPORTUNITIES:
{chr(10).join(opp_lines) if opp_lines else '  None'}

ACTIVE PS PROJECTS:
{chr(10).join(ps_lines) if ps_lines else '  None'}

FORMAT RULES — return ONLY a numbered list 1 through 7 (or fewer if fewer are relevant). Each item must:
1. Start with a bold action phrase in **markdown bold**
2. Reference specific data from above (use case names, amounts, dates, stage names)
3. End with "Suggested next step: [concrete action for the PM or SE to take]"

Focus on: PS engagement gaps, at-risk use case acceleration, converting unused capacity to services, renewal expansion, and new services opportunities tied to the account's active use cases."""
    return prompt


def _parse_cortex_response(raw):
    try:
        parsed = json.loads(raw)
        return parsed["choices"][0]["messages"]
    except Exception:
        return str(raw)


def _render_insights(text):
    import re
    items = re.split(r'\n(?=\d+\.)', text.strip())
    for item in items:
        item = item.strip()
        if not item:
            continue
        bold_match = re.search(r'\*\*(.+?)\*\*', item)
        title = bold_match.group(1) if bold_match else item.split("\n")[0][:80]
        next_step = ""
        ns_match = re.search(r'Suggested next step:\s*(.+)', item, re.IGNORECASE)
        if ns_match:
            next_step = ns_match.group(1).strip()
        body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
        body = re.sub(r'Suggested next step:.+', '', body, flags=re.IGNORECASE | re.DOTALL).strip()
        body = re.sub(r'^\d+\.\s*', '', body).strip()
        ns_html = f'<div style="border-top:1px solid #fde68a;margin-top:8px;padding-top:6px;font-size:0.77rem;color:#92400e"><strong>Next Step:</strong> {esc(next_step)}</div>' if next_step else ""
        st.markdown(f"""
<div style="border-left:4px solid #29B5E8;background:#f0f9ff;border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:10px">
  <div style="font-size:0.83rem;color:#1e293b;line-height:1.6">{body}</div>
  {ns_html}
</div>""", unsafe_allow_html=True)


_ins_key = f"_insights_{selected}"

if _ins_key not in st.session_state:
    if st.button("Generate Strategic Insights", type="primary", key="gen_insights_btn"):
        with st.spinner("Analyzing account with claude-4-opus..."):
            try:
                _prompt = _build_pm_insights_prompt(
                    selected, a,
                    acct_ucs if not acct_ucs.empty else pd.DataFrame(),
                    _opps_combined if not _opps_combined.empty else pd.DataFrame(),
                    _ps_acct if not _ps_acct.empty else pd.DataFrame(),
                    acct_cap,
                )
                from data import _get_session
                _sess = _get_session()
                _safe_prompt = _prompt.replace("'", "''")
                _raw = _sess.sql(
                    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-4-opus', [{{'role':'user','content':'{_safe_prompt}'}}], {{'temperature': 0}})"
                ).collect()[0][0]
                st.session_state[_ins_key] = _parse_cortex_response(_raw)
            except Exception as _e:
                st.error(f"Could not generate insights: {_e}")
        st.rerun()
else:
    _render_insights(st.session_state[_ins_key])
    if st.button("Regenerate", key="regen_insights_btn", type="secondary"):
        del st.session_state[_ins_key]
        st.rerun()
