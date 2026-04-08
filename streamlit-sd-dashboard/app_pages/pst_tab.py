import streamlit as st
import pandas as pd
from data import load_ps_projects_active, load_ps_pipeline, load_ps_history, load_product_usage, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

active_df = load_ps_projects_active()
pipeline_df = load_ps_pipeline()
history_df = load_ps_history()
product_df = load_product_usage()

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
with kpi1:
    st.metric("Active Projects", len(active_df))
with kpi2:
    active_rev = active_df["REVENUE_AMOUNT"].sum() if not active_df.empty else 0
    st.metric("Active Revenue", f"${active_rev:,.0f}")
with kpi3:
    total_hours = active_df["BILLABLE_HOURS"].sum() if not active_df.empty else 0
    st.metric("Billable Hours", f"{total_hours:,.0f}")
with kpi4:
    st.metric("Pipeline Opps", len(pipeline_df))
with kpi5:
    pipe_tcv = pipeline_df["TOTAL_PST_TCV"].fillna(0).sum() if not pipeline_df.empty else 0
    st.metric("Pipeline TCV", f"${pipe_tcv:,.0f}")
with kpi6:
    stalled = len(active_df[active_df["PROJECT_STAGE"].isin(["Stalled", "Stalled - Expiring"])]) if not active_df.empty else 0
    st.metric("Stalled Projects", stalled)


def render_product_expanders(sfdc_acct_ids, product_data, section_key):
    if product_data.empty or len(sfdc_acct_ids) == 0:
        return
    acct_products = product_data[product_data["SALESFORCE_ACCOUNT_ID"].isin(sfdc_acct_ids)]
    if acct_products.empty:
        return
    summary = acct_products.groupby(["ACCOUNT_NAME", "PRODUCT_CATEGORY"]).agg(
        TOTAL_CREDITS=("TOTAL_CREDITS", "sum"),
        TOTAL_JOBS=("TOTAL_JOBS", "sum"),
        FEATURES=("PRIMARY_FEATURE", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index().sort_values(["ACCOUNT_NAME", "TOTAL_CREDITS"], ascending=[True, False])

    with st.expander(f":material/category: Product Usage (Last 3 Months) — {len(acct_products)} products across {acct_products['SALESFORCE_ACCOUNT_ID'].nunique()} accounts", expanded=False):
        render_html_table(summary, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "PRODUCT_CATEGORY", "label": "Category"},
            {"col": "TOTAL_CREDITS", "label": "Credits", "fmt": "number"},
            {"col": "TOTAL_JOBS", "label": "Jobs", "fmt": "number"},
            {"col": "FEATURES", "label": "Features"},
        ])


st.markdown("### :material/check_circle: Active SD Projects")

if not active_df.empty:
    active_df["END_DATE"] = pd.to_datetime(active_df["END_DATE"])
    fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns(7)
    with fc1:
        acct_filter_a = st.multiselect("Account", options=sorted(active_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psa_acct")
    with fc2:
        stage_filter_a = st.multiselect("Project Stage", options=sorted(active_df["PROJECT_STAGE"].dropna().unique()), default=[], key="psa_stage")
    with fc3:
        practice_filter_a = st.multiselect("Practice", options=sorted(active_df["PRACTICE"].dropna().unique()), default=[], key="psa_practice")
    with fc4:
        dm_filter_a = st.multiselect("DM", options=sorted(active_df["DM"].dropna().unique()), default=[], key="psa_dm")
    with fc5:
        ae_filter_a = st.multiselect("AE", options=sorted(active_df["AE"].dropna().unique()), default=[], key="psa_ae")
    with fc6:
        hide_past_end = st.checkbox("Hide past end dates", value=False, key="psa_hide_past")
    with fc7:
        search_a = st.text_input("Search project", "", key="psa_search")

    filtered_a = active_df.copy()
    if acct_filter_a:
        filtered_a = filtered_a[filtered_a["ACCOUNT_NAME"].isin(acct_filter_a)]
    if stage_filter_a:
        filtered_a = filtered_a[filtered_a["PROJECT_STAGE"].isin(stage_filter_a)]
    if practice_filter_a:
        filtered_a = filtered_a[filtered_a["PRACTICE"].isin(practice_filter_a)]
    if dm_filter_a:
        filtered_a = filtered_a[filtered_a["DM"].isin(dm_filter_a)]
    if ae_filter_a:
        filtered_a = filtered_a[filtered_a["AE"].isin(ae_filter_a)]
    if hide_past_end:
        today = pd.Timestamp.now().normalize()
        filtered_a = filtered_a[filtered_a["END_DATE"].isna() | (filtered_a["END_DATE"] >= today)]
    if search_a:
        filtered_a = filtered_a[filtered_a["PROJECT_NAME"].str.contains(search_a, case=False, na=False)]

    display_a = filtered_a.copy()
    display_a["OPP_LINK"] = display_a.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    render_html_table(display_a, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
        {"col": "PROJECT_NAME", "label": "Project"},
        {"col": "PRACTICE", "label": "Practice"},
        {"col": "DM", "label": "DM"},
        {"col": "AE", "label": "AE"},
        {"col": "PROJECT_STAGE", "label": "Stage"},
        {"col": "BILLING_TYPE", "label": "Billing"},
        {"col": "SKU_TYPE", "label": "SKU"},
        {"col": "INVESTMENT_TYPE", "label": "Invest"},
        {"col": "START_DATE", "label": "Start", "fmt": "date"},
        {"col": "END_DATE", "label": "Proj End", "fmt": "date"},
        {"col": "LAST_RESOURCE_END_DATE", "label": "Last Resource End", "fmt": "date", "highlight": True},
        {"col": "BILLABLE_HOURS", "label": "Bill Hrs", "fmt": "number"},
        {"col": "REVENUE_AMOUNT", "label": "Revenue", "fmt": "dollar"},
        {"col": "PROJECT_MANAGER", "label": "PM"},
        {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        {"col": "ASSIGNMENT_COUNT", "label": "Assignments", "fmt": "number"},
        {"col": "ASSIGNED_RESOURCES", "label": "Resources"},
        {"col": "ASSIGNED_ROLES", "label": "Roles"},
        {"col": "PS_FORECAST_CATEGORY", "label": "Fcast Cat"},
        {"col": "STATUS_NOTES", "label": "Status Notes"},
    ], height=500)

    render_product_expanders(filtered_a["SALESFORCE_ACCOUNT_ID"].unique(), product_df, "active")

    csv_a = filtered_a.to_csv(index=False)
    st.download_button(":material/download: Export Active CSV", csv_a, "pst_active_projects.csv", "text/csv", key="psa_csv")
else:
    st.info("No active PS&T projects found.")

st.divider()

import re

def _extract_base_name(project_name):
    if pd.isna(project_name):
        return ""
    cleaned = re.sub(r'\s*Year\s*\d+', '', str(project_name), flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Yr\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Y\d+\b', '', cleaned)
    cleaned = re.sub(r'\s*Phase\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Ph\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().rstrip('-').rstrip('_').strip()
    return cleaned

st.markdown("### :material/warning: Expiring SD Projects — No Extension")

if not active_df.empty:
    today = pd.Timestamp.now().normalize()

    exp_months = st.slider("Expiring within (months)", min_value=1, max_value=24, value=12, step=1, key="pse_months")
    cutoff_date = today + pd.DateOffset(months=exp_months)

    exp_df = active_df.copy()
    exp_df["END_DATE"] = pd.to_datetime(exp_df["END_DATE"])
    exp_df["LAST_RESOURCE_END_DATE"] = pd.to_datetime(exp_df["LAST_RESOURCE_END_DATE"])
    exp_df["EFFECTIVE_END_DATE"] = exp_df["LAST_RESOURCE_END_DATE"].fillna(exp_df["END_DATE"])
    exp_df["BASE_NAME"] = exp_df["PROJECT_NAME"].apply(_extract_base_name)

    expiring = exp_df[
        (exp_df["EFFECTIVE_END_DATE"].notna())
        & (exp_df["EFFECTIVE_END_DATE"] > today)
        & (exp_df["EFFECTIVE_END_DATE"] <= cutoff_date)
    ].copy()

    no_extension = []
    for idx, row in expiring.iterrows():
        same_acct = exp_df[
            (exp_df["SALESFORCE_ACCOUNT_ID"] == row["SALESFORCE_ACCOUNT_ID"])
            & (exp_df["BASE_NAME"] == row["BASE_NAME"])
            & (exp_df.index != idx)
        ]
        has_later = same_acct["EFFECTIVE_END_DATE"].notna() & (same_acct["EFFECTIVE_END_DATE"] > row["EFFECTIVE_END_DATE"])
        if not has_later.any():
            no_extension.append(idx)

    expiring_no_ext = expiring.loc[no_extension].sort_values("EFFECTIVE_END_DATE", ascending=True)

    if not expiring_no_ext.empty:
        ec1, ec2, ec3, ec4, ec5, ec6, ec7 = st.columns(7)
        with ec1:
            acct_filter_e = st.multiselect("Account", options=sorted(expiring_no_ext["ACCOUNT_NAME"].dropna().unique()), default=[], key="pse_acct")
        with ec2:
            stage_filter_e = st.multiselect("Project Stage", options=sorted(expiring_no_ext["PROJECT_STAGE"].dropna().unique()), default=[], key="pse_stage")
        with ec3:
            practice_filter_e = st.multiselect("Practice", options=sorted(expiring_no_ext["PRACTICE"].dropna().unique()), default=[], key="pse_practice")
        with ec4:
            dm_filter_e = st.multiselect("DM", options=sorted(expiring_no_ext["DM"].dropna().unique()), default=[], key="pse_dm")
        with ec5:
            ae_filter_e = st.multiselect("AE", options=sorted(expiring_no_ext["AE"].dropna().unique()), default=[], key="pse_ae")
        with ec6:
            hide_past_end_e = st.checkbox("Hide past end dates", value=False, key="pse_hide_past")
        with ec7:
            search_e = st.text_input("Search project", "", key="pse_search")

        filtered_e = expiring_no_ext.copy()
        if acct_filter_e:
            filtered_e = filtered_e[filtered_e["ACCOUNT_NAME"].isin(acct_filter_e)]
        if stage_filter_e:
            filtered_e = filtered_e[filtered_e["PROJECT_STAGE"].isin(stage_filter_e)]
        if practice_filter_e:
            filtered_e = filtered_e[filtered_e["PRACTICE"].isin(practice_filter_e)]
        if dm_filter_e:
            filtered_e = filtered_e[filtered_e["DM"].isin(dm_filter_e)]
        if ae_filter_e:
            filtered_e = filtered_e[filtered_e["AE"].isin(ae_filter_e)]
        if hide_past_end_e:
            filtered_e = filtered_e[filtered_e["END_DATE"].isna() | (filtered_e["END_DATE"] >= pd.Timestamp.now().normalize())]
        if search_e:
            filtered_e = filtered_e[filtered_e["PROJECT_NAME"].str.contains(search_e, case=False, na=False)]

        st.caption(f"{len(filtered_e)} projects ending within {exp_months} months with no similar project extending beyond their end date.")
        exp_display = filtered_e.copy()
        exp_display["OPP_LINK"] = exp_display.apply(
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)
        render_html_table(exp_display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
            {"col": "PROJECT_NAME", "label": "Project"},
            {"col": "PRACTICE", "label": "Practice"},
            {"col": "DM", "label": "DM"},
            {"col": "AE", "label": "AE"},
            {"col": "PROJECT_STAGE", "label": "Stage"},
            {"col": "BILLING_TYPE", "label": "Billing"},
            {"col": "SKU_TYPE", "label": "SKU"},
            {"col": "INVESTMENT_TYPE", "label": "Invest"},
            {"col": "START_DATE", "label": "Start", "fmt": "date"},
            {"col": "END_DATE", "label": "Proj End", "fmt": "date"},
            {"col": "LAST_RESOURCE_END_DATE", "label": "Last Resource End", "fmt": "date", "highlight": True},
            {"col": "BILLABLE_HOURS", "label": "Bill Hrs", "fmt": "number"},
            {"col": "REVENUE_AMOUNT", "label": "Revenue", "fmt": "dollar"},
            {"col": "PROJECT_MANAGER", "label": "PM"},
            {"col": "PS_SELLER_NAME", "label": "PS Seller"},
            {"col": "ASSIGNMENT_COUNT", "label": "Assignments", "fmt": "number"},
            {"col": "ASSIGNED_RESOURCES", "label": "Resources"},
            {"col": "ASSIGNED_ROLES", "label": "Roles"},
            {"col": "PS_FORECAST_CATEGORY", "label": "Fcast Cat"},
            {"col": "STATUS_NOTES", "label": "Status Notes"},
        ], height=500)

        csv_exp = filtered_e.to_csv(index=False)
        st.download_button(":material/download: Export Expiring CSV", csv_exp, "pst_expiring_no_extension.csv", "text/csv", key="psa_exp_csv")
    else:
        st.info("No expiring projects without extensions found in the next 12 months.")
else:
    st.info("No active PS&T projects to check for expirations.")

st.divider()

st.markdown("### :material/timeline: SD Pipeline (Open Opportunities)")

if not pipeline_df.empty:
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
    with fc1:
        acct_filter_p = st.multiselect("Account", options=sorted(pipeline_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psp_acct")
    with fc2:
        ae_filter_p = st.multiselect("AE", options=sorted(pipeline_df["OWNER"].dropna().unique()), default=[], key="psp_ae")
    with fc3:
        stage_filter_p = st.multiselect("Stage", options=sorted(pipeline_df["STAGE_NAME"].dropna().unique()), default=[], key="psp_stage")
    with fc4:
        type_filter_p = st.multiselect("Type", options=sorted(pipeline_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="psp_type")
    with fc5:
        fc_filter_p = st.multiselect("Forecast", options=sorted(pipeline_df["FORECAST_STATUS"].dropna().unique()), default=[], key="psp_fc")
    with fc6:
        search_p = st.text_input("Search opportunity", "", key="psp_search")

    filtered_p = pipeline_df.copy()
    if acct_filter_p:
        filtered_p = filtered_p[filtered_p["ACCOUNT_NAME"].isin(acct_filter_p)]
    if ae_filter_p:
        filtered_p = filtered_p[filtered_p["OWNER"].isin(ae_filter_p)]
    if stage_filter_p:
        filtered_p = filtered_p[filtered_p["STAGE_NAME"].isin(stage_filter_p)]
    if type_filter_p:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_TYPE"].isin(type_filter_p)]
    if fc_filter_p:
        filtered_p = filtered_p[filtered_p["FORECAST_STATUS"].isin(fc_filter_p)]
    if search_p:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_NAME"].str.contains(search_p, case=False, na=False)]

    display_p = filtered_p.copy()
    display_p["OPP_LINK"] = display_p.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)
    render_html_table(display_p, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
        {"col": "OPPORTUNITY_TYPE", "label": "Type"},
        {"col": "PRODUCT_NAMES", "label": "Products"},
        {"col": "PS_SERVICE_TYPE", "label": "Svc Type"},
        {"col": "STAGE_NAME", "label": "Stage"},
        {"col": "FORECAST_STATUS", "label": "Forecast"},
        {"col": "PS_INVESTMENT_TYPE", "label": "Invest"},
        {"col": "QUOTE_SUB_AGREEMENT_TYPE", "label": "Agreement"},
        {"col": "CLOSE_DATE", "label": "Close", "fmt": "date"},
        {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
        {"col": "SALES_QUALIFIED_DATE", "label": "SQ Date", "fmt": "date"},
        {"col": "FISCAL_QUARTER", "label": "FQ"},
        {"col": "DAYS_IN_STAGE", "label": "Days", "fmt": "number"},
        {"col": "TOTAL_ACV", "label": "Total ACV", "fmt": "dollar"},
        {"col": "TOTAL_PST_TCV", "label": "PST TCV", "fmt": "dollar"},
        {"col": "PS_SERVICES_TCV", "label": "PS TCV", "fmt": "dollar"},
        {"col": "EDUCATION_SERVICES_TCV", "label": "Edu TCV", "fmt": "dollar"},
        {"col": "PS_SERVICES_FORECAST", "label": "PS Fcast $", "fmt": "dollar"},
        {"col": "EDUCATION_SERVICES_FORECAST", "label": "Edu Fcast $", "fmt": "dollar"},
        {"col": "DM", "label": "DM"},
        {"col": "OWNER", "label": "AE"},
        {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        {"col": "OPP_PROBABILITY", "label": "Prob %", "fmt": "pct"},
        {"col": "MEDDPICC_SCORE", "label": "MEDDPICC", "fmt": "decimal1"},
        {"col": "PS_FORECAST_CATEGORY", "label": "PS Fcast Cat"},
    ], height=450)

    render_product_expanders(filtered_p["SALESFORCE_ACCOUNT_ID"].unique(), product_df, "pipeline")

    csv_p = filtered_p.to_csv(index=False)
    st.download_button(":material/download: Export Pipeline CSV", csv_p, "pst_pipeline.csv", "text/csv", key="psp_csv")
else:
    st.info("No PS&T pipeline opportunities found.")

st.divider()

st.markdown("### :material/history: Historical Sold Services & Training")

if not history_df.empty:
    hc1, hc2, hc3, hc4, hc5, hc6 = st.columns(6)
    with hc1:
        acct_filter_h = st.multiselect("Account", options=sorted(history_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psh_acct")
    with hc2:
        dm_filter_h = st.multiselect("DM", options=sorted(history_df["DM"].dropna().unique()), default=[], key="psh_dm")
    with hc3:
        ae_filter_h = st.multiselect("AE", options=sorted(history_df["AE"].dropna().unique()), default=[], key="psh_ae")
    with hc4:
        pf_filter_h = st.multiselect("Product Family", options=sorted(history_df["PRODUCT_FAMILIES"].dropna().unique()), default=[], key="psh_pf")
    with hc5:
        type_filter_h = st.multiselect("Opp Type", options=sorted(history_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="psh_type")
    with hc6:
        search_h = st.text_input("Search opportunity", "", key="psh_search")

    filtered_h = history_df.copy()
    if acct_filter_h:
        filtered_h = filtered_h[filtered_h["ACCOUNT_NAME"].isin(acct_filter_h)]
    if dm_filter_h:
        filtered_h = filtered_h[filtered_h["DM"].isin(dm_filter_h)]
    if ae_filter_h:
        filtered_h = filtered_h[filtered_h["AE"].isin(ae_filter_h)]
    if pf_filter_h:
        filtered_h = filtered_h[filtered_h["PRODUCT_FAMILIES"].isin(pf_filter_h)]
    if type_filter_h:
        filtered_h = filtered_h[filtered_h["OPPORTUNITY_TYPE"].isin(type_filter_h)]
    if search_h:
        filtered_h = filtered_h[filtered_h["OPPORTUNITY_NAME"].str.contains(search_h, case=False, na=False) | filtered_h["ACCOUNT_NAME"].str.contains(search_h, case=False, na=False)]

    hk1, hk2, hk3, hk4 = st.columns(4)
    with hk1:
        st.metric("Closed Won Opps", len(filtered_h))
    with hk2:
        st.metric("PS Services $", f"${filtered_h['PS_SERVICES_ACV'].sum():,.0f}")
    with hk3:
        st.metric("Edu Services $", f"${filtered_h['EDU_SERVICES_ACV'].sum():,.0f}")
    with hk4:
        st.metric("Total PST $", f"${filtered_h['TOTAL_PST_AMOUNT'].sum():,.0f}")

    display_h = filtered_h.copy()
    display_h["OPP_LINK"] = display_h.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    render_html_table(display_h, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "SFDC", "fmt": "link"},
        {"col": "DM", "label": "DM"},
        {"col": "AE", "label": "AE"},
        {"col": "OPP_OWNER", "label": "Opp Owner"},
        {"col": "OPPORTUNITY_TYPE", "label": "Type"},
        {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
        {"col": "PRODUCT_FAMILIES", "label": "Product Family"},
        {"col": "PS_SERVICES_ACV", "label": "PS Svc $", "fmt": "dollar"},
        {"col": "EDU_SERVICES_ACV", "label": "Edu Svc $", "fmt": "dollar"},
        {"col": "TOTAL_PST_AMOUNT", "label": "Total PST $", "fmt": "dollar"},
        {"col": "PS_SERVICE_TYPE", "label": "Svc Type"},
        {"col": "PS_INVESTMENT_TYPE", "label": "Invest Type"},
        {"col": "PS_INVESTMENT_AMOUNT", "label": "Invest $", "fmt": "dollar"},
        {"col": "PS_SELLER_NAME", "label": "PS Seller"},
        {"col": "STAGE_NAME", "label": "Stage"},
    ], height=600)

    csv_h = filtered_h.to_csv(index=False)
    st.download_button(":material/download: Export History CSV", csv_h, "pst_history.csv", "text/csv", key="psh_csv")
else:
    st.info("No historical PS&T opportunities found.")
