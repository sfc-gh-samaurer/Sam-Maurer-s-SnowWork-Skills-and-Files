import streamlit as st
import pandas as pd
from data import load_use_cases, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

df = load_use_cases()

st.markdown("### :material/rocket_launch: All Use Cases")

if not df.empty:
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
    with fc1:
        acct_filter = st.multiselect("Account", options=sorted(df["ACCOUNT_NAME"].dropna().unique()), default=[], key="uc_acct")
    with fc2:
        ae_filter = st.multiselect("AE", options=sorted(df["OWNER"].dropna().unique()), default=[], key="uc_ae")
    with fc3:
        status_filter = st.multiselect("Status", options=sorted(df["USE_CASE_STATUS"].dropna().unique()), default=[], key="uc_status")
    with fc4:
        stage_filter = st.multiselect("Stage", options=sorted(df["STAGE"].dropna().unique()), default=[], key="uc_stage")
    with fc5:
        ps_filter = st.multiselect("PS Engaged", options=["Yes", "No"], default=[], key="uc_ps")
    with fc6:
        search = st.text_input("Search use case", "", key="uc_search")

    filtered = df.copy()
    if acct_filter:
        filtered = filtered[filtered["ACCOUNT_NAME"].isin(acct_filter)]
    if ae_filter:
        filtered = filtered[filtered["OWNER"].isin(ae_filter)]
    if status_filter:
        filtered = filtered[filtered["USE_CASE_STATUS"].isin(status_filter)]
    if stage_filter:
        filtered = filtered[filtered["STAGE"].isin(stage_filter)]
    if ps_filter:
        ps_vals = []
        if "Yes" in ps_filter:
            ps_vals.append(True)
        if "No" in ps_filter:
            ps_vals.append(False)
        filtered = filtered[filtered["IS_PS_ENGAGED"].isin(ps_vals)]
    if search:
        filtered = filtered[filtered["USE_CASE_NAME"].str.contains(search, case=False, na=False)]

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Total Use Cases", len(filtered))
    with kpi2:
        in_pursuit = len(filtered[filtered["USE_CASE_STATUS"] == "In Pursuit"])
        st.metric("In Pursuit", in_pursuit)
    with kpi3:
        in_impl = len(filtered[filtered["USE_CASE_STATUS"] == "Implementation"])
        st.metric("Implementation", in_impl)
    with kpi4:
        total_eacv = filtered["ACV"].sum()
        st.metric("Total EACV", f"${total_eacv:,.0f}")
    with kpi5:
        today = pd.Timestamp.now().normalize()
        filtered["DAYS_SINCE_MODIFIED"] = (today - pd.to_datetime(filtered["LAST_MODIFIED_DATE"], errors="coerce").dt.tz_localize(None)).dt.days
        stuck_count = len(filtered[filtered["DAYS_SINCE_MODIFIED"] > 90])
        st.metric("Stuck >90d", stuck_count)

    display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "USE_CASE_NAME", "USE_CASE_ID", "USE_CASE_NUMBER", "USE_CASE_STATUS",
                        "ACV", "STAGE", "DECISION_DATE", "CREATED_DATE", "LAST_MODIFIED_DATE",
                        "DAYS_SINCE_MODIFIED", "OWNER", "NEXT_STEPS", "IS_PS_ENGAGED"]].copy()

    display["UC_LINK"] = display.apply(
        lambda r: f'{SFDC_BASE}/{r["USE_CASE_ID"]}/view' if pd.notna(r.get("USE_CASE_ID")) else None,
        axis=1
    )
    display["UC_DISPLAY"] = display["USE_CASE_NUMBER"].fillna("")
    display["PS_ENGAGED"] = display["IS_PS_ENGAGED"].map({True: "Yes", False: "No"})

    render_html_table(display, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "USE_CASE_NAME", "label": "Use Case"},
        {"col": "UC_LINK", "label": "UC #", "fmt": "link", "display_col": "UC_DISPLAY"},
        {"col": "USE_CASE_STATUS", "label": "Status"},
        {"col": "ACV", "label": "EACV", "fmt": "dollar"},
        {"col": "STAGE", "label": "Stage"},
        {"col": "DECISION_DATE", "label": "Decision Date", "fmt": "date"},
        {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
        {"col": "LAST_MODIFIED_DATE", "label": "Modified", "fmt": "date"},
        {"col": "DAYS_SINCE_MODIFIED", "label": "Days Since Modified", "fmt": "number"},
        {"col": "OWNER", "label": "AE"},
        {"col": "NEXT_STEPS", "label": "Next Steps"},
        {"col": "PS_ENGAGED", "label": "PS Engaged"},
    ], height=600)

    csv = filtered.to_csv(index=False)
    st.download_button(":material/download: Export CSV", csv, "use_cases.csv", "text/csv", key="uc_csv")
else:
    st.info("No use case data found.")
