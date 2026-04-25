import streamlit as st
from data import clear_all_caches, _init_session, load_org_hierarchy, load_user_prefs, save_user_prefs
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

if "_prefs_loaded" not in st.session_state:
    _saved = load_user_prefs()
    for _k, _v in _saved.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v
    st.session_state["_prefs_loaded"] = True
    st.session_state["_prefs_hash"] = ""

st.markdown("""
<style>
    /* ── Base & Typography ── */
    [data-testid="stAppViewContainer"] { background-color: #F2F4F7; }
    [data-testid="stHeader"] { background-color: #11567F; height: 2px; }
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
        color: #8A999E;
        margin: 18px 0 8px 2px;
    }

    /* ── nav scroll bar (legacy render_nav_bar) ── */
    .tab-nav {
        display: flex; align-items: center; gap: 8px;
        background: white; border: 1px solid #E4E7EB;
        border-radius: 8px; padding: 8px 14px;
        margin-bottom: 14px; flex-wrap: wrap;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04);
    }
    .tab-nav-label {
        color: #11567F; font-weight: 700; font-size: 0.78rem;
        text-transform: uppercase; letter-spacing: 0.08em;
        white-space: nowrap; margin-right: 4px;
    }
    .tab-nav-link {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 100%);
        color: white !important; text-decoration: none !important;
        padding: 4px 12px; border-radius: 20px; font-size: 0.76rem;
        font-weight: 600; cursor: pointer; white-space: nowrap; display: inline-block;
    }
    .tab-nav-link:hover { background: linear-gradient(135deg, #164E63 0%, #0369A1 100%); }
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
            st.rerun()

    st.divider()
    st.markdown("### :material/filter_alt: Scope")

    org_df = load_org_hierarchy()

    if "sf_theater" not in st.session_state:
        st.session_state["sf_theater"] = ["Expansions"]
    if "sf_region" not in st.session_state:
        st.session_state["sf_region"] = ["NorthwestExp"]
    if "sf_pm" not in st.session_state:
        st.session_state["sf_pm"] = ["Sam Maurer"]
    if "sf_district" not in st.session_state:
        st.session_state["sf_district"] = []
    if "selected_dms" not in st.session_state:
        st.session_state["selected_dms"] = ["Erik Schneider", "Raymond Navarro"]

    all_theaters = sorted(org_df["THEATRE"].dropna().unique())
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
    valid_pms = sorted(h3["PRACTICE_MANAGERS"].dropna().unique())
    cur_pms = st.session_state.get("sf_pm", [])
    clean_pms = [p for p in cur_pms if p in valid_pms]
    if clean_pms != cur_pms:
        st.session_state["sf_pm"] = clean_pms
    st.multiselect("Practice Manager", valid_pms, key="sf_pm")
    sel_pm = st.session_state.get("sf_pm", [])

    h4 = h3[h3["PRACTICE_MANAGERS"].isin(sel_pm)] if sel_pm else h3
    valid_districts = sorted(h4["DISTRICT"].dropna().unique())
    cur_districts = st.session_state.get("sf_district", [])
    clean_districts = [d for d in cur_districts if d in valid_districts]
    if clean_districts != cur_districts:
        st.session_state["sf_district"] = clean_districts
    st.multiselect("District", valid_districts, key="sf_district")
    sel_district = st.session_state.get("sf_district", [])

    h5 = h4[h4["DISTRICT"].isin(sel_district)] if sel_district else h4
    new_dms = sorted(h5["DISTRICT_MANAGER"].dropna().unique().tolist())
    if not new_dms:
        new_dms = ["Erik Schneider", "Raymond Navarro"]

    prev_dms = st.session_state.get("selected_dms", None)
    if prev_dms is not None and set(new_dms) != set(prev_dms):
        st.session_state["selected_dms"] = new_dms
        clear_all_caches()
        st.rerun()
    st.session_state["selected_dms"] = new_dms

    st.divider()
    n_dms = len(new_dms)
    dms_preview = ", ".join(new_dms[:2]) + ("…" if n_dms > 2 else "")
    st.caption(f"**{n_dms}** DM(s): {dms_preview}")

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    st.caption(f"Data as of: **{datetime.now().strftime('%b %d, %Y')}**")

    if st.button(":material/refresh: Refresh Data", type="primary", use_container_width=True):
        clear_all_caches()
        st.session_state.last_refresh = datetime.now()
        st.rerun()

    _cur_prefs = {
        "sf_theater": st.session_state.get("sf_theater", []),
        "sf_region":  st.session_state.get("sf_region", []),
        "sf_pm":      st.session_state.get("sf_pm", []),
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
_pms_str      = ", ".join(st.session_state.get("sf_pm", []))      or "All PMs"
_n_dms        = len(st.session_state.get("selected_dms", []))
_page_label   = st.session_state.get("current_page", "").split(": ")[-1]

st.markdown(
    f'<div class="sf-app-header">'
    f'<div>'
    f'<p class="sf-app-title">❄️ SD Presales · Run the Business</p>'
    f'<p class="sf-app-scope">'
    f'Theater: <strong>{_theaters_str}</strong> &nbsp;·&nbsp; '
    f'PM: <strong>{_pms_str}</strong> &nbsp;·&nbsp; '
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

_selected = st.session_state.get("current_page", ":material/bar_chart: Executive Summary")
with open(os.path.join(_APP_DIR, f"app_pages/{_PAGE_FILES[_selected]}")) as f:
    exec(f.read())
