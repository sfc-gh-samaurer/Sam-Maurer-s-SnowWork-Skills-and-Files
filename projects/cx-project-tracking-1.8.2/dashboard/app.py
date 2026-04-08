import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(
    page_title="CX Project Tracking",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("CX Project Tracking")


@st.fragment(run_every=timedelta(minutes=30))
def dashboard():
    conn = st.connection("snowflake")

    @st.cache_data(ttl=timedelta(minutes=10))
    def load_summary():
        return conn.query("""
            SELECT
                (SELECT COUNT(DISTINCT EMAIL) FROM FIVETRAN.SALESFORCE.USER
                 WHERE DEPARTMENT = 'Professional Services' AND IS_ACTIVE = TRUE) AS TOTAL_SD_EMPLOYEES,
                (SELECT COUNT(DISTINCT EMAIL)
                 FROM SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS) AS EMPLOYEES_WITH_TAGS,
                TOTAL_SD_EMPLOYEES - EMPLOYEES_WITH_TAGS AS EMPLOYEES_WITHOUT_TAGS,
                (SELECT COUNT(DISTINCT t.PROJECT)
                 FROM SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS t
                 JOIN (SELECT DISTINCT SESSION_ID, SNOWFLAKE_ACCOUNT_TYPE
                       FROM SNOWSCIENCE.LLM.CORTEX_CODE_REQUEST_FACT) f
                     ON t.SESSION_ID = f.SESSION_ID
                 WHERE f.SNOWFLAKE_ACCOUNT_TYPE = 'Internal'
                   AND UPPER(t.CUSTOMER) NOT IN ('INTERNAL','DEBUG_FIX_TEST','TEST')
                   AND UPPER(t.PROJECT) NOT IN ('TEST')
                   AND t.PROJECT IS NOT NULL AND TRIM(t.PROJECT) != ''
                ) AS UNIQUE_PROJECTS_INTERNAL,
                (SELECT COUNT(DISTINCT t.PROJECT)
                 FROM SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS t
                 JOIN (SELECT DISTINCT SESSION_ID, SNOWFLAKE_ACCOUNT_TYPE
                       FROM SNOWSCIENCE.LLM.CORTEX_CODE_REQUEST_FACT) f
                     ON t.SESSION_ID = f.SESSION_ID
                 WHERE f.SNOWFLAKE_ACCOUNT_TYPE != 'Internal'
                   AND UPPER(t.CUSTOMER) NOT IN ('INTERNAL','DEBUG_FIX_TEST','TEST')
                   AND UPPER(t.PROJECT) NOT IN ('TEST')
                   AND t.PROJECT IS NOT NULL AND TRIM(t.PROJECT) != ''
                ) AS UNIQUE_PROJECTS_CUSTOMER,
                (SELECT COUNT(DISTINCT SESSION_ID)
                 FROM SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS) AS TOTAL_SESSIONS,
                (SELECT MAX(START_TIME)
                 FROM SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS) AS LAST_DATA_REFRESH
        """)

    @st.cache_data(ttl=timedelta(minutes=10))
    def load_projects():
        return conn.query("SELECT * FROM SD_APPS_DB.COCO_USAGE.V_SESSION_TAG_PROJECTS")

    @st.cache_data(ttl=timedelta(minutes=10))
    def load_missing_employees():
        return conn.query("SELECT * FROM SD_APPS_DB.COCO_USAGE.V_SESSION_TAG_MISSING_EMPLOYEES")

    summary = load_summary()
    projects_df = load_projects()
    missing_df = load_missing_employees()

    last_refresh = summary["LAST_DATA_REFRESH"].iloc[0]
    if pd.notna(last_refresh):
        refresh_str = pd.Timestamp(last_refresh).strftime("%Y-%m-%d %H:%M UTC")
    else:
        refresh_str = "No data yet"

    st.caption(f"Data last refreshed: **{refresh_str}**  \u2022  Loaded every 30 min from query history  \u2022  Auto-refreshes")

    with st.container(horizontal=True):
        st.metric("Projects (Internal)", int(summary["UNIQUE_PROJECTS_INTERNAL"].iloc[0]), border=True)
        st.metric("Projects (Customer)", int(summary["UNIQUE_PROJECTS_CUSTOMER"].iloc[0]), border=True)
        st.metric("Employees with Tags", int(summary["EMPLOYEES_WITH_TAGS"].iloc[0]), border=True)
        st.metric("Employees Missing Tags", int(summary["EMPLOYEES_WITHOUT_TAGS"].iloc[0]), border=True)
        st.metric("Total SD Employees", int(summary["TOTAL_SD_EMPLOYEES"].iloc[0]), border=True)
        st.metric("Total Sessions", int(summary["TOTAL_SESSIONS"].iloc[0]), border=True)

    st.divider()

    st.header("Projects")
    st.caption(f"{len(projects_df)} unique customer projects tracked")

    if not projects_df.empty:
        display_projects = projects_df.rename(columns={
            "CUSTOMER": "Customer",
            "PROJECT": "Project",
            "SESSION_COUNT": "Sessions",
            "CONSULTANT_COUNT": "Consultants",
            "FIRST_TAGGED": "First Tagged",
            "LAST_TAGGED": "Last Tagged",
        })
        st.dataframe(
            display_projects[["Customer", "Project", "Sessions", "Consultants", "First Tagged", "Last Tagged"]],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No project tags recorded yet.")

    st.divider()

    st.header("Employees Without Tags")

    col1, col2 = st.columns(2)

    managers = sorted(missing_df["MANAGER_NAME"].dropna().unique().tolist())

    with col1:
        selected_manager = st.selectbox(
            "Filter by Manager",
            options=["All"] + managers,
            index=0,
        )

    with col2:
        search_term = st.text_input("Search Employee", placeholder="Name or email...")

    filtered_df = missing_df.copy()

    if selected_manager != "All":
        filtered_df = filtered_df[filtered_df["MANAGER_NAME"] == selected_manager]

    if search_term:
        mask = (
            filtered_df["CONSULTANT_NAME"].str.contains(search_term, case=False, na=False)
            | filtered_df["CONSULTANT_EMAIL"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    st.caption(f"{len(filtered_df)} employees without a recorded session tag")

    if not filtered_df.empty:
        display_missing = filtered_df.rename(columns={
            "CONSULTANT_NAME": "Name",
            "CONSULTANT_EMAIL": "Email",
            "TITLE": "Title",
            "MANAGER_NAME": "Manager",
        })
        st.dataframe(
            display_missing[["Name", "Email", "Title", "Manager"]],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.success("All employees in this group have recorded tags!")


dashboard()
