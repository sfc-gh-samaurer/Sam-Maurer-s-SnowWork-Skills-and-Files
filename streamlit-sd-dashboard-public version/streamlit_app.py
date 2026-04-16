import streamlit as st
from data import clear_all_caches, _init_session, load_org_hierarchy
from datetime import datetime
import os

_APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="SD Presales Pipeline",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

_init_session()

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
        padding: 24px 32px;
        margin-bottom: 22px;
        box-shadow: 0 6px 24px rgba(41,181,232,0.30);
    }
    .tab-banner-title {
        color: white !important;
        font-size: 4.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .tab-banner-sub {
        color: rgba(255,255,255,0.78);
        font-size: 0.92rem;
        margin: 5px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
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

# ── HEADER ────────────────────────────────────────────────────────────────────
header_left, header_right = st.columns([3, 1])
with header_left:
    theaters_str = ", ".join(st.session_state.get("sf_theater", [])) or "All Theaters"
    regions_str = ", ".join(st.session_state.get("sf_region", [])) or "All Regions"
    pms_str = ", ".join(st.session_state.get("sf_pm", [])) or "All Practice Managers"
    n_dms = len(st.session_state.get("selected_dms", []))

    st.markdown("## ❄️ SD Presales Pipeline")
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

tab0, tab1, tab2, tab3, tab4 = st.tabs([
    ":material/bar_chart: Executive Summary",
    ":material/trending_up: Capacity & Renewals",
    ":material/rocket_launch: Use Cases",
    ":material/support_agent: SD Projects",
    ":material/work: Pipeline in SnowWork",
])

with tab0:
    with open(os.path.join(_APP_DIR, "app_pages/exec_summary_tab.py")) as f:
        exec(f.read())

with tab1:
    with open(os.path.join(_APP_DIR, "app_pages/capacity_renewals.py")) as f:
        exec(f.read())

with tab2:
    with open(os.path.join(_APP_DIR, "app_pages/use_cases_tab.py")) as f:
        exec(f.read())

with tab3:
    with open(os.path.join(_APP_DIR, "app_pages/pst_tab.py")) as f:
        exec(f.read())

with tab4:
    with open(os.path.join(_APP_DIR, "app_pages/pipeline_snowwork_tab.py")) as f:
        exec(f.read())
