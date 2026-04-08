import streamlit as st
from data import clear_all_caches, _init_session
from datetime import datetime
import os

_APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Enterprise Expansion, Northwest - SD Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="collapsed",
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
</style>
""", unsafe_allow_html=True)

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown("## :material/dashboard: Enterprise Expansion, Northwest - SD Dashboard")
    st.caption("DMs: Erik Schneider, EntBayAreaTech1 & Raymond Navarro, EntPacNorthwest — PM: Sam Maurer")
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
    ":material/auto_awesome: Use Case Action Plan",
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
    with open(os.path.join(_APP_DIR, "app_pages/action_planner_tab.py")) as f:
        exec(f.read())
