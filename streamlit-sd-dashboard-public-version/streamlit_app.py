import streamlit as st
from data import clear_all_caches, _init_session, load_org_hierarchy, load_user_prefs, save_user_prefs, load_data_freshness, load_hierarchy, load_account_search_list
from datetime import datetime
import json
import os

_APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="SD Presales Run the Business",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

_init_session()

_HIERARCHY_VERSION = "v8"
if st.session_state.get("_hierarchy_version") != _HIERARCHY_VERSION:
    load_hierarchy.clear()
    load_org_hierarchy.clear()
    load_account_search_list.clear()
    st.session_state["_hierarchy_version"] = _HIERARCHY_VERSION

if "_prefs_loaded" not in st.session_state:
    _saved = load_user_prefs()
    for _k, _v in _saved.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v
    st.session_state["_prefs_loaded"] = True
    st.session_state["_prefs_hash"] = ""
    st.session_state["_last_seen_at"] = _saved.get("last_seen_at", None)
    st.session_state["_whats_new_shown"] = False
    st.session_state["_filter_presets"]  = _saved.get("filter_presets", [])
    st.session_state["_pinned_accounts"] = _saved.get("pinned_accounts", [])

st.markdown("""
<style>
    /* ── Base & Typography ── */
    [data-testid="stAppViewContainer"] { background-color: #F2F4F7; }
    [data-testid="stHeader"] { display: none; }
    .block-container { margin-top: 0 !important; }
    .block-container { padding-top: 0.75rem; padding-bottom: 0.5rem; padding-left: 1.5rem; padding-right: 1.5rem; max-width: 100%; }
    h1, h2, h3 { color: #11567F; }

    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E4E7EB;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(16,24,40,0.06);
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #8A999E !important;
    }
    div[data-testid="stMetricValue"] {
        color: #11567F !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
        font-variant-numeric: tabular-nums;
    }
    div[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

    /* ── Section Banner ── */
    .sf-banner, .tab-banner, .exec-banner, .detail-header {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
        border-radius: 10px;
        padding: 12px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(41,181,232,0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .sf-banner-title, .tab-banner-title, .exec-banner-title, .detail-header-title {
        color: white !important;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    .sf-banner-sub, .tab-banner-sub, .exec-banner-sub, .detail-header-sub {
        color: rgba(255,255,255,0.75);
        font-size: 0.82rem;
        margin: 3px 0 0;
    }
    .sf-banner-count {
        background: rgba(255,255,255,0.2);
        color: white;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        white-space: nowrap;
        flex-shrink: 0;
    }

    /* ── App Header Card ── */
    .sf-app-header {
        background: #FFFFFF;
        border: 1px solid #E4E7EB;
        border-radius: 10px;
        padding: 12px 20px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(16,24,40,0.05);
    }
    .sf-app-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #11567F;
        margin: 0 0 2px 0;
        letter-spacing: -0.02em;
    }
    .sf-app-scope {
        font-size: 0.75rem;
        color: #8A999E;
        margin: 0;
    }
    .sf-app-scope strong { color: #334155; }
    .sf-refresh-ts { font-size: 0.72rem; color: #8A999E; text-align: right; margin-bottom: 4px; }

    /* ── Filter Bar ── */
    .sf-filter-bar {
        background: #FFFFFF;
        border: 1px solid #E4E7EB;
        border-radius: 8px;
        padding: 10px 14px 4px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
    }

    /* ── Expanders ── */
    div[data-testid="stExpander"] {
        border: 1px solid #E4E7EB !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        background: #FFFFFF;
        overflow: hidden;
    }
    div[data-testid="stExpander"] > details > summary {
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #0f172a !important;
        padding: 10px 14px !important;
        background: #FFFFFF;
    }
    div[data-testid="stExpander"] > details > summary:hover {
        background: #F8FAFC !important;
    }
    div[data-testid="stExpander"] > details[open] > summary {
        border-bottom: 1px solid #E4E7EB;
    }

    /* ── st.tabs inside tab pages ── */
    div[data-testid="stTabs"] > div[role="tablist"] {
        border-bottom: 2px solid #E4E7EB;
        gap: 0;
        margin-bottom: 16px;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #8A999E !important;
        padding: 8px 20px !important;
        border-bottom: 2px solid transparent !important;
        margin-bottom: -2px;
        border-radius: 0 !important;
        background: transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #11567F !important;
        border-bottom-color: #29B5E8 !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        color: #11567F !important;
        background: #F8FAFC !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E4E7EB;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8A999E;
        margin-bottom: 6px;
    }
    section[data-testid="stSidebar"] [data-testid^="baseButton-"] {
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-align: left !important;
        padding: 7px 12px !important;
        margin-bottom: 2px !important;
        transition: all 0.15s ease-out !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 100%) !important;
        border-color: transparent !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
        background: transparent !important;
        color: #334155 !important;
        border: 1px solid #E4E7EB !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
        background: #F0F9FF !important;
        color: #0C4A6E !important;
        border-color: #93C5FD !important;
    }

    /* ── DataFrames ── */
    .stDataFrame { border-radius: 8px; }

    /* ── Empty + Error States ── */
    .sf-empty-state {
        color: #8A999E;
        font-size: 0.85rem;
        font-style: italic;
        padding: 24px 16px;
        text-align: center;
        border: 1px dashed #E4E7EB;
        border-radius: 8px;
        margin: 8px 0;
        background: #FAFAFA;
    }
    .sf-error-state {
        color: #D93025;
        font-size: 0.85rem;
        padding: 12px 16px;
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        margin: 8px 0;
    }

    /* ── KPI Cards (exec summary legacy, kept for compatibility) ── */
    .kpi-grid { display: flex; gap: 12px; margin: 4px 0 18px 0; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 130px;
        border-radius: 10px;
        padding: 16px 10px 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(16,24,40,0.07);
        border-top: 3px solid;
    }
    .kpi-icon { font-size: 1.6rem; margin-bottom: 6px; display: block; line-height: 1; }
    .kpi-value {
        font-size: 1.8rem; font-weight: 900; line-height: 1.0;
        margin-bottom: 4px; font-variant-numeric: tabular-nums;
    }
    .kpi-label {
        font-size: 0.66rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 2px;
    }
    .kpi-sub { font-size: 0.64rem; opacity: 0.55; }

    /* ── Section divider label ── */
    .sf-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #11567F;
        margin: 18px 0 8px 0;
        padding-left: 8px;
        border-left: 3px solid #29B5E8;
    }

    /* ── Snapshot cards (Account Details) ── */
    .snapshot-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EB;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
        height: 100%;
    }
    .card-header {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #11567F;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 2px solid #E0F2FE;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 3px 0;
        border-bottom: 1px solid #F8FAFC;
    }
    .stat-label { font-size: 0.75rem; color: #8A999E; }
    .stat-value { font-size: 0.82rem; font-weight: 600; color: #0f172a; font-variant-numeric: tabular-nums; }
    .none-msg { color: #94a3b8; font-size: 0.80rem; font-style: italic; }

    /* ── WoW expander accent ── */
    div[data-testid="stExpander"]:has(summary:first-line) {
        border-left: 3px solid transparent !important;
    }

    /* ── Pill styles ── */
    .pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.66rem;
        font-weight: 600;
        margin-right: 4px;
        letter-spacing: 0.02em;
    }
    .pill-blue  { background: #E0F2FE; color: #0284C7; }
    .pill-green { background: #DCFCE7; color: #16A34A; }
    .pill-red   { background: #FEE2E2; color: #DC2626; }
    .pill-gray  { background: #F1F5F9; color: #475569; }
    .pill-amber { background: #FEF3C7; color: #D97706; }

    /* ── ARR/ACV badge on account header ── */
    .acct-arr-badge {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 8px;
        padding: 8px 14px;
        text-align: right;
        backdrop-filter: blur(4px);
    }
    .arr-label { font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(255,255,255,0.65); font-weight: 600; }
    .arr-value { font-size: 1.5rem; font-weight: 900; color: white; line-height: 1.1; margin-top: 2px; font-variant-numeric: tabular-nums; }

    /* ── Sidebar scope section highlight ── */
    section[data-testid="stSidebar"] .stMultiSelect > label,
    section[data-testid="stSidebar"] .stTextInput > label {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: #11567F !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ── WoW summary banner color coding ── */
    .wow-positive { color: #16A34A; font-weight: 700; }
    .wow-negative { color: #DC2626; font-weight: 700; }
    .wow-neutral  { color: #8A999E; font-weight: 600; }

</style>
""", unsafe_allow_html=True)

_NAV_PAGES = [
    ":material/bar_chart: Executive Summary",
    ":material/business_center: SD Opportunities",
    ":material/trending_up: Capacity & Renewals",
    ":material/rocket_launch: Use Cases",
    ":material/support_agent: SD Projects",
    ":material/manage_accounts: Account Details",
]
if "current_page" not in st.session_state:
    st.session_state["current_page"] = _NAV_PAGES[0]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### :material/navigation: Pages")
    for _i, _pg in enumerate(_NAV_PAGES):
        _active = st.session_state.get("current_page") == _pg
        if st.button(
            _pg,
            key=f"_nav_btn_{_i}",
            use_container_width=True,
            type="primary" if _active else "secondary",
        ):
            st.session_state["current_page"] = _pg

    st.divider()
    st.markdown("### :material/filter_alt: Scope")

    org_df = load_org_hierarchy()

    if "sf_theater" not in st.session_state:
        st.session_state["sf_theater"] = []
    if "sf_region" not in st.session_state:
        st.session_state["sf_region"] = []
    if "sf_district" not in st.session_state:
        st.session_state["sf_district"] = []
    if "selected_dms" not in st.session_state:
        st.session_state["selected_dms"] = ["Erik Schneider", "Raymond Navarro"]

    all_theaters = sorted(org_df["THEATRE"].dropna().unique())
    cur_theaters = st.session_state.get("sf_theater", [])
    clean_theaters = [t for t in cur_theaters if t in all_theaters]
    if clean_theaters != cur_theaters:
        st.session_state["sf_theater"] = clean_theaters
    st.multiselect("Theater", all_theaters, key="sf_theater")
    sel_theater = st.session_state.get("sf_theater", [])

    h2 = org_df[org_df["THEATRE"].isin(sel_theater)] if sel_theater else org_df
    valid_regions = sorted(h2["REGION"].dropna().unique())
    cur_regions = st.session_state.get("sf_region", [])
    clean_regions = [r for r in cur_regions if r in valid_regions]
    if clean_regions != cur_regions:
        st.session_state["sf_region"] = clean_regions
    st.multiselect("Region", valid_regions, key="sf_region")
    sel_region = st.session_state.get("sf_region", [])

    h3 = h2[h2["REGION"].isin(sel_region)] if sel_region else h2
    valid_districts = sorted(h3["DISTRICT"].dropna().unique())
    cur_districts = st.session_state.get("sf_district", [])
    clean_districts = [d for d in cur_districts if d in valid_districts]
    if clean_districts != cur_districts:
        st.session_state["sf_district"] = clean_districts
    st.multiselect("District", valid_districts, key="sf_district")
    sel_district = st.session_state.get("sf_district", [])

    h4 = h3[h3["DISTRICT"].isin(sel_district)] if sel_district else h3
    new_dms = sorted(h4["DISTRICT_MANAGER"].dropna().unique().tolist())
    new_districts = sorted(h4["DISTRICT"].dropna().unique().tolist())
    # Build display labels: mark inactive DMs
    _dm_active_map = h4.drop_duplicates("DISTRICT_MANAGER").set_index("DISTRICT_MANAGER")["DM_IS_ACTIVE"].to_dict() if "DM_IS_ACTIVE" in h4.columns else {}
    def _dm_label(dm):
        return dm if _dm_active_map.get(dm, True) else f"{dm} (inactive)"
    if not sel_theater and not sel_region and not sel_district:
        new_dms = []
        new_districts = []

    prev_dms = st.session_state.get("selected_dms", None)
    if prev_dms is not None and set(new_dms) != set(prev_dms):
        st.session_state["selected_dms"] = new_dms
        st.session_state["selected_districts"] = new_districts
        clear_all_caches()
        st.rerun()
    st.session_state["selected_dms"] = new_dms
    st.session_state["selected_districts"] = new_districts

    # ── Feedback Button ────────────────────────────────────────────────────────
    @st.dialog("Bugs & Enhancement Requests", width="large")
    def _feedback_dialog():
        st.caption("Report a bug or suggest an improvement. Submissions go directly to Sam Maurer.")
        _fb_name    = st.text_input("Your Name", key="_fb_name")
        _fb_type    = st.radio("Type", ["Bug Report", "Enhancement Request"], horizontal=True, key="_fb_type")
        _fb_subject = st.text_input("Subject", key="_fb_subject")
        _fb_desc    = st.text_area("Description", height=160, key="_fb_desc")
        st.markdown("")
        if st.button("Send", type="primary", use_container_width=True, key="_fb_send"):
            if not _fb_name.strip() or not _fb_subject.strip() or not _fb_desc.strip():
                st.warning("Please fill in all fields before sending.")
            else:
                try:
                    from snowflake.snowpark.context import get_active_session
                    _fb_session = get_active_session()
                    _subj = f"[SD Dashboard] {_fb_type}: {_fb_subject.strip()}"
                    _body = (
                        f"SD Dashboard Feedback\n"
                        f"{'─'*40}\n"
                        f"From:    {_fb_name.strip()}\n"
                        f"Type:    {_fb_type}\n"
                        f"Subject: {_fb_subject.strip()}\n\n"
                        f"Description:\n{_fb_desc.strip()}"
                    )
                    _subj_esc = _subj.replace("'", "''")
                    _body_esc = _body.replace("'", "''")
                    _fb_session.sql(
                        f"SELECT SYSTEM$SEND_EMAIL('SD_CENTER_EMAIL_INT', 'sam.maurer@snowflake.com', '{_subj_esc}', '{_body_esc}')"
                    ).collect()
                    st.success("✅ Sent! Thank you for your feedback.")
                except Exception as _fb_err:
                    st.error(f"Could not send email: {_fb_err}")

    if st.button("🐛 Bugs & Enhancement Requests", use_container_width=True, type="secondary", key="_feedback_btn"):
        _feedback_dialog()

    st.divider()
    n_dms = len(new_dms)
    if n_dms:
        with st.expander(f"**{n_dms}** DM(s) in scope", expanded=False):
            st.markdown("\n".join(f"- {_dm_label(d)}" for d in new_dms))
    else:
        st.caption("No DMs selected")

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    try:
        _fdata = load_data_freshness()
        _fdate = _fdata.get("accounts_date", "Unknown")
        _fok   = _fdata.get("today_loaded", False)
        _fdot  = "🟢" if _fok else "🟡"
        st.caption(f"{_fdot} Data as of: **{_fdate}**")
    except Exception:
        st.caption(f"Data as of: **{datetime.now().strftime('%b %d, %Y')}**")

    if st.button(":material/refresh: Refresh Data", type="primary", use_container_width=True):
        clear_all_caches()
        st.session_state.last_refresh = datetime.now()
        st.rerun()

    # ── Saved Views ───────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### :material/bookmark: Saved Views")
    _saved_presets = st.session_state.get("_filter_presets", [])

    def _load_preset(p):
        st.session_state["sf_theater"] = p.get("sf_theater", [])
        st.session_state["sf_region"]  = p.get("sf_region", [])
        st.session_state["sf_district"]= p.get("sf_district", [])
        clear_all_caches()

    if _saved_presets:
        for _pi, _pr in enumerate(_saved_presets):
            _pc1, _pc2 = st.columns([3, 1])
            with _pc1:
                if st.button(_pr["name"], key=f"_preset_load_{_pi}", use_container_width=True, type="secondary"):
                    _load_preset(_pr)
                    st.rerun()
            with _pc2:
                if st.button("✕", key=f"_preset_del_{_pi}", help="Delete this view"):
                    _saved_presets.pop(_pi)
                    st.session_state["_filter_presets"] = _saved_presets
                    save_user_prefs({
                        "sf_theater": st.session_state.get("sf_theater", []),
                        "sf_region":  st.session_state.get("sf_region", []),
                        "sf_district":st.session_state.get("sf_district", []),
                        "filter_presets": _saved_presets,
                        "last_seen_at": st.session_state.get("_last_seen_at", ""),
                    })
                    st.rerun()
    else:
        st.caption("No saved views yet.")

    _new_preset_name = st.text_input("Save current scope as…", key="_new_preset_name", placeholder="e.g. My District")
    if st.button(":material/save: Save View", key="_preset_save", use_container_width=True, type="secondary"):
        if _new_preset_name.strip():
            _new_preset = {
                "name":        _new_preset_name.strip(),
                "sf_theater":  st.session_state.get("sf_theater", []),
                "sf_region":   st.session_state.get("sf_region", []),
                "sf_district": st.session_state.get("sf_district", []),
            }
            _saved_presets.append(_new_preset)
            st.session_state["_filter_presets"] = _saved_presets
            save_user_prefs({
                "sf_theater": st.session_state.get("sf_theater", []),
                "sf_region":  st.session_state.get("sf_region", []),
                "sf_district":st.session_state.get("sf_district", []),
                "filter_presets": _saved_presets,
                "last_seen_at": st.session_state.get("_last_seen_at", ""),
            })
            st.rerun()

    # ── Global Account Search ─────────────────────────────────────────────────
    _cur_prefs = {
        "sf_theater": st.session_state.get("sf_theater", []),
        "sf_region":  st.session_state.get("sf_region", []),
        "sf_district": st.session_state.get("sf_district", []),
    }
    _cur_hash = json.dumps(
        {k: sorted(v) for k, v in _cur_prefs.items()}, sort_keys=True
    )
    if _cur_hash != st.session_state.get("_prefs_hash", ""):
        save_user_prefs(_cur_prefs)
        st.session_state["_prefs_hash"] = _cur_hash

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
_theaters_str = ", ".join(st.session_state.get("sf_theater", [])) or "All Theaters"
_n_dms        = len(st.session_state.get("selected_dms", []))
_page_label   = st.session_state.get("current_page", "").split(": ")[-1]

st.markdown(
    f'<div class="sf-app-header">'
    f'<div>'
    f'<p class="sf-app-title">❄️ SD Presales · Run the Business</p>'
    f'<p class="sf-app-scope">'
    f'Theater: <strong>{_theaters_str}</strong> &nbsp;·&nbsp; '
    f'<strong>{_n_dms}</strong> DM(s) in scope'
    f'</p>'
    f'</div>'
    f'<div style="text-align:right">'
    f'<p class="sf-app-title" style="font-size:0.95rem;color:#29B5E8;">{_page_label}</p>'
    f'<p class="sf-app-scope">Refreshed {st.session_state.last_refresh.strftime("%b %d · %I:%M %p")}</p>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

_PAGE_FILES = {
    ":material/bar_chart: Executive Summary": "exec_summary_tab.py",
    ":material/business_center: SD Opportunities": "sd_opportunities_tab.py",
    ":material/trending_up: Capacity & Renewals": "capacity_renewals.py",
    ":material/rocket_launch: Use Cases": "use_cases_tab.py",
    ":material/support_agent: SD Projects": "pst_tab.py",
    ":material/manage_accounts: Account Details": "account_details_tab.py",
}

# ── WHAT'S NEW BANNER ─────────────────────────────────────────────────────────
_last_seen = st.session_state.get("_last_seen_at")
if _last_seen and not st.session_state.get("_whats_new_shown"):
    try:
        from data import load_exec_new_opps, load_exec_new_use_cases
        import pandas as _pd_wn
        _ls_dt  = _pd_wn.to_datetime(_last_seen)
        _wn_opps = load_exec_new_opps()
        _wn_ucs  = load_exec_new_use_cases()
        _wn_opps["CREATED_DATE"] = _pd_wn.to_datetime(_wn_opps["CREATED_DATE"], errors="coerce")
        _wn_ucs["CREATED_DATE"]  = _pd_wn.to_datetime(_wn_ucs["CREATED_DATE"],  errors="coerce")
        _new_opp_ct = len(_wn_opps[_wn_opps["CREATED_DATE"] > _ls_dt])
        _new_uc_ct  = len(_wn_ucs[_wn_ucs["CREATED_DATE"]   > _ls_dt])
        if _new_opp_ct > 0 or _new_uc_ct > 0:
            _parts = []
            if _new_opp_ct > 0:
                _parts.append(f"**{_new_opp_ct}** new opportunit{'y' if _new_opp_ct == 1 else 'ies'}")
            if _new_uc_ct > 0:
                _parts.append(f"**{_new_uc_ct}** new use case{'s' if _new_uc_ct != 1 else ''}")
            _since = _ls_dt.strftime("%b %d")
            st.info(f"✨ Since your last visit ({_since}): {' and '.join(_parts)} were created.", icon=None)
        st.session_state["_whats_new_shown"] = True
    except Exception:
        st.session_state["_whats_new_shown"] = True

_today_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
if st.session_state.get("_last_seen_at") != _today_str[:10]:
    _wn_prefs = {
        "sf_theater":   st.session_state.get("sf_theater", []),
        "sf_region":    st.session_state.get("sf_region", []),
        "sf_district":  st.session_state.get("sf_district", []),
        "last_seen_at": _today_str[:10],
    }
    save_user_prefs(_wn_prefs)
    st.session_state["_last_seen_at"] = _today_str[:10]

_selected = st.session_state.get("current_page", ":material/bar_chart: Executive Summary")
_no_scope = not st.session_state.get("selected_dms")

if _no_scope:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#EFF8FF,#F0FAFF);border:2px solid #29B5E8;
                border-radius:12px;padding:28px 32px;margin:40px auto;max-width:520px;text-align:center">
      <div style="font-size:1.4rem;margin-bottom:8px">🗺️</div>
      <div style="font-weight:700;font-size:1.05rem;color:#11567F;margin-bottom:6px">Select a Scope to Get Started</div>
      <div style="color:#475569;font-size:0.88rem;line-height:1.6">
        Use the <strong>Theater</strong>, <strong>Region</strong>, or <strong>District</strong> filters
        in the sidebar to narrow your view.<br><br>
        Tip: selecting a Region loads data for all districts within it.
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    with open(os.path.join(_APP_DIR, f"app_pages/{_PAGE_FILES[_selected]}")) as f:
        exec(f.read())

# ── DATA FRESHNESS FOOTER ─────────────────────────────────────────────────────
try:
    _fresh = load_data_freshness()
    _date  = _fresh.get("accounts_date", "Unknown")
    _ok    = _fresh.get("today_loaded", False)
    _dot   = "🟢" if _ok else "🟡"
    st.markdown(
        f'<div style="margin-top:24px;padding:6px 4px;border-top:1px solid #E4E7EB;'
        f'font-size:0.70rem;color:#8A999E;display:flex;gap:16px;flex-wrap:wrap;">'
        f'<span>{_dot} SNOWHOUSE.SALES.ACCOUNTS_DAILY — latest partition: <strong style="color:#334155">{_date}</strong></span>'
        f'<span style="margin-left:auto">Data refreshes daily &nbsp;·&nbsp; '
        f'<a href="https://app.snowflake.com" target="_blank" style="color:#29B5E8;text-decoration:none">Snowflake</a></span>'
        f'</div>',
        unsafe_allow_html=True,
    )
except Exception:
    pass
