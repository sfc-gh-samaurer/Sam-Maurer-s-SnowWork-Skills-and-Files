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

# ── USER PREFS: load once per browser session ─────────────────────────────────
if "_prefs_loaded" not in st.session_state:
    _saved = load_user_prefs()
    for _k, _v in _saved.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v
    st.session_state["_prefs_loaded"] = True
    st.session_state["_prefs_hash"] = ""

st.markdown("""
<style>
    /* ── Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    * { font-family: Inter, -apple-system, "Segoe UI", Roboto, sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #F2F4F7; }
    [data-testid="stHeader"] { background-color: #29B5E8; height: 2rem; }
    .block-container { padding-top: 2.5rem; padding-bottom: 0rem; max-width: 1440px; }
    h1, h2, h3 { color: #11567F; }

    /* ── Tabs ── */
    div[data-testid="stTabs"] button { font-size: 16px; font-weight: 600; }
    div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom: 3px solid #29B5E8; color: #11567F; }

    /* ── DataFrames + Metrics ── */
    .stDataFrame { border-radius: 8px; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E4E7EB;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 2px rgba(16,24,40,0.06);
        font-variant-numeric: tabular-nums;
    }
    div[data-testid="stMetricValue"] { color: #11567F; font-weight: 700; }

    /* ── Section Banner (unified — replaces tab-banner, exec-banner, detail-header) ── */
    .sf-banner,
    .tab-banner,
    .exec-banner,
    .detail-header {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
        border-radius: 12px;
        padding: 14px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(41,181,232,0.18);
    }
    .sf-banner-title,
    .tab-banner-title,
    .exec-banner-title,
    .detail-header-title {
        color: white !important;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    .sf-banner-sub,
    .tab-banner-sub,
    .exec-banner-sub,
    .detail-header-sub {
        color: rgba(255,255,255,0.78);
        font-size: 0.88rem;
        margin: 4px 0 0;
    }

    /* ── KPI Cards (exec summary) ── */
    .kpi-grid { display: flex; gap: 12px; margin: 4px 0 20px 0; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px;
        border-radius: 10px;
        padding: 18px 12px 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(16,24,40,0.08);
        border-top: 4px solid;
    }
    .kpi-icon { font-size: 2rem; margin-bottom: 8px; display: block; line-height: 1; }
    .kpi-value {
        font-size: 2rem; font-weight: 900; line-height: 1.0;
        margin-bottom: 6px; font-variant-numeric: tabular-nums;
    }
    .kpi-label {
        font-size: 0.72rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px;
    }
    .kpi-sub { font-size: 0.68rem; opacity: 0.55; }

    /* ── Empty + Error States ── */
    .sf-empty-state {
        color: #8A999E; font-size: 0.88rem; font-style: italic;
        padding: 20px; text-align: center;
        border: 1px dashed #E4E7EB; border-radius: 8px; margin: 8px 0;
    }
    .sf-error-state {
        color: #D93025; font-size: 0.88rem;
        padding: 12px 16px; background: #FEF2F2;
        border: 1px solid #FECACA; border-radius: 8px; margin: 8px 0;
    }

    /* ── Sidebar Nav ── */
    .tab-nav {
        display: flex; align-items: center; gap: 10px;
        background: white; border: 1px solid #E4E7EB;
        border-radius: 10px; padding: 10px 18px;
        margin-bottom: 18px; flex-wrap: wrap;
        box-shadow: 0 1px 2px rgba(16,24,40,0.06);
    }
    .tab-nav-label {
        color: #11567F; font-weight: 700; font-size: 0.82rem;
        text-transform: uppercase; letter-spacing: 0.08em; white-space: nowrap; margin-right: 4px;
    }
    .tab-nav-link {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 100%);
        color: white !important; text-decoration: none !important;
        padding: 5px 14px; border-radius: 20px; font-size: 0.80rem;
        font-weight: 600; cursor: pointer; white-space: nowrap; display: inline-block;
    }
    .tab-nav-link:hover {
        background: linear-gradient(135deg, #164E63 0%, #0369A1 100%);
        color: white !important;
    }

    /* ── Sidebar Buttons ── */
    section[data-testid="stSidebar"] [data-testid^="baseButton-"] {
        border-radius: 8px !important; font-weight: 600 !important;
        font-size: 0.85rem !important; text-align: left !important;
        padding: 8px 14px !important; margin-bottom: 2px !important;
        transition: all 0.15s ease-out !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 100%) !important;
        border-color: #0284C7 !important; color: white !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
        background: white !important; color: #334155 !important;
        border: 1px solid #E4E7EB !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
        background: #f0f9ff !important; color: #0C4A6E !important;
        border-color: #93C5FD !important;
    }
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
    st.markdown("### :material/navigation: Navigation")
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
    st.markdown("### :material/filter_alt: Filters")

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
    st.caption(f"**{len(new_dms)}** District Manager(s) in scope")

    # ── Save prefs when they change ───────────────────────────────────────────
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

# ── HEADER ────────────────────────────────────────────────────────────────────
header_left, header_right = st.columns([3, 1])
with header_left:
    theaters_str = ", ".join(st.session_state.get("sf_theater", [])) or "All Theaters"
    regions_str = ", ".join(st.session_state.get("sf_region", [])) or "All Regions"
    pms_str = ", ".join(st.session_state.get("sf_pm", [])) or "All Practice Managers"
    n_dms = len(st.session_state.get("selected_dms", []))

    st.markdown("## ❄️ SD Presales Run the Business")
    st.caption(
        f"Theater: **{theaters_str}** | Region: **{regions_str}** | "
        f"PM: **{pms_str}** | {n_dms} DM(s) in scope"
    )
with header_right:
    col_ts, col_btn = st.columns([2, 1])
    with col_ts:
        if "last_refresh" not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%b %d, %Y %I:%M %p')}")
    with col_btn:
        if st.button(":material/refresh: Refresh", type="primary", use_container_width=True):
            clear_all_caches()
            st.session_state.last_refresh = datetime.now()
            st.rerun()

st.divider()

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
