import streamlit as st
from data import clear_all_caches, _init_session, load_org_hierarchy, load_user_prefs, save_user_prefs
from datetime import datetime
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
    [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
    [data-testid="stHeader"] { background-color: #29B5E8; height: 2rem; }
    .block-container { padding-top: 2.5rem; padding-bottom: 0rem; }
    h1, h2, h3 { color: #11567F; }
    div[data-testid="stTabs"] button { font-size: 16px; font-weight: 600; }
    div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom: 3px solid #29B5E8; color: #11567F; }
    .stDataFrame { border-radius: 8px; }
    div[data-testid="stMetric"] { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; }
    .tab-banner {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 55%, #29B5E8 100%);
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(41,181,232,0.20);
    }
    .tab-banner-title {
        color: white !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    .tab-banner-sub {
        color: rgba(255,255,255,0.78);
        font-size: 0.92rem;
        margin: 5px 0 0;
    }
    .tab-nav {
        display: flex;
        align-items: center;
        gap: 10px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 20px;
        flex-wrap: wrap;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .tab-nav-label {
        color: #11567F;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        white-space: nowrap;
        margin-right: 4px;
    }
    .tab-nav-link {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 100%);
        color: white !important;
        text-decoration: none !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        cursor: pointer;
        white-space: nowrap;
        display: inline-block;
    }
    .tab-nav-link:hover {
        background: linear-gradient(135deg, #164E63 0%, #0369A1 100%);
        color: white !important;
        text-decoration: none !important;
    }
    section[data-testid="stSidebar"] [data-testid^="baseButton-"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-align: left !important;
        padding: 8px 14px !important;
        margin-bottom: 2px !important;
        transition: all 0.15s ease !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0C4A6E 0%, #0284C7 100%) !important;
        border-color: #0284C7 !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
        background: white !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
        background: #f0f9ff !important;
        color: #0C4A6E !important;
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
    import json as _json
    _cur_prefs = {
        "sf_theater": st.session_state.get("sf_theater", []),
        "sf_region":  st.session_state.get("sf_region", []),
        "sf_pm":      st.session_state.get("sf_pm", []),
        "sf_district": st.session_state.get("sf_district", []),
    }
    _cur_hash = _json.dumps(
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
