import streamlit as st
import pandas as pd
from datetime import datetime
from data import load_capacity_renewals, load_capacity_pipeline, render_html_table, render_nav_bar

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

df = load_capacity_renewals()
cap_pipe_df = load_capacity_pipeline()

today = pd.Timestamp.now().normalize()

render_nav_bar([
    ("Active Capacity Contracts", "nav-cr-active"),
    ("Capacity Conversion Candidates", "nav-cr-candidates"),
    ("Capacity &amp; Renewal Pipeline", "nav-cr-pipeline"),
    ("Investment Opportunities", "nav-cr-invest"),
])

# --- FILTERS ---
st.markdown('<div id="nav-cr-active" class="tab-banner"><p class="tab-banner-title">Active Capacity Contracts</p></div>', unsafe_allow_html=True)

if not df.empty:
    fc1, fc2 = st.columns(2)
    with fc1:
        ae_filter = st.multiselect("AE", options=sorted(df["ACCOUNT_OWNER"].dropna().unique()), default=[], key="cap_ae")
    with fc2:
        search = st.text_input("Search account", "", key="cap_search")

    filtered = df.copy()
    if ae_filter:
        filtered = filtered[filtered["ACCOUNT_OWNER"].isin(ae_filter)]
    if search:
        filtered = filtered[filtered["ACCOUNT_NAME"].str.contains(search, case=False, na=False)]

    def sfdc_account_link(name, sfdc_id):
        if pd.notna(sfdc_id) and sfdc_id:
            return f"{SFDC_BASE}/Account/{sfdc_id}/view"
        return None

    display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                        "LEAD_SE",
                        "CONTRACT_START_DATE", "CONTRACT_END_DATE",
                        "TOTAL_CAP",
                        "CAPACITY_USED",
                        "OVERAGE_UNDERAGE_PREDICTION", "OVERAGE_DATE"]].copy()

    display["ACCOUNT_LINK"] = display.apply(lambda r: sfdc_account_link(r["ACCOUNT_NAME"], r["SALESFORCE_ACCOUNT_ID"]), axis=1)

    kpi1, kpi2 = st.columns(2)
    with kpi1:
        st.metric("Accounts", len(filtered))
    with kpi2:
        used_ytd = filtered["CAPACITY_USED"].sum()
        st.metric("Total Used YTD", f"${used_ytd:,.0f}")
    with st.expander(f"{len(filtered)} contracts", expanded=True):
        render_html_table(display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "ACCOUNT_LINK", "label": "SFDC", "fmt": "link"},
            {"col": "ACCOUNT_OWNER", "label": "AE"},
            {"col": "DM", "label": "DM"},
            {"col": "LEAD_SE", "label": "Lead SE"},
            {"col": "CONTRACT_START_DATE", "label": "Start", "fmt": "date"},
            {"col": "CONTRACT_END_DATE", "label": "End", "fmt": "date"},
            {"col": "TOTAL_CAP", "label": "Total Cap", "fmt": "dollar"},
            {"col": "CAPACITY_USED", "label": "Cap Used", "fmt": "dollar"},
            {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Over/Under", "fmt": "dollar"},
            {"col": "OVERAGE_DATE", "label": "Overage Date", "fmt": "date"},
        ], height=600)

        csv = filtered.to_csv(index=False)
        st.download_button(":material/download: Export CSV", csv, "capacity_contracts.csv", "text/csv", key="cap_csv")

    candidates = filtered[
        (filtered["CONTRACT_END_DATE"].notna())
    ].copy()
    candidates["DAYS_LEFT"] = (pd.to_datetime(candidates["CONTRACT_END_DATE"]) - today).dt.days
    candidates = candidates[
        (candidates["DAYS_LEFT"] <= 730)
        & (candidates["DAYS_LEFT"] > 0)
        & (candidates["OVERAGE_UNDERAGE_PREDICTION"] < 0)
    ].sort_values("OVERAGE_UNDERAGE_PREDICTION", ascending=True)

    st.divider()
    st.markdown('<div id="nav-cr-candidates" class="tab-banner"><p class="tab-banner-title">Capacity Conversion Candidates</p></div>', unsafe_allow_html=True)

    if not candidates.empty:
        with st.expander(f"{len(candidates)} accounts ending within 24 months with predicted underburn", expanded=True):
            st.caption("These accounts are predicted to have significant unused capacity at contract end — consider converting remaining capacity into services contracts.")
            conv_display = candidates[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                                       "CONTRACT_END_DATE", "DAYS_LEFT",
                                       "CAPACITY_USED",
                                       "OVERAGE_UNDERAGE_PREDICTION"]].copy()
            conv_display["ACCOUNT_LINK"] = conv_display.apply(
                lambda r: f'{SFDC_BASE}/Account/{r["SALESFORCE_ACCOUNT_ID"]}/view' if pd.notna(r.get("SALESFORCE_ACCOUNT_ID")) else None, axis=1)
            render_html_table(conv_display, columns=[
                {"col": "ACCOUNT_NAME", "label": "Account"},
                {"col": "ACCOUNT_LINK", "label": "SFDC", "fmt": "link"},
                {"col": "ACCOUNT_OWNER", "label": "AE"},
                {"col": "DM", "label": "DM"},
                {"col": "CONTRACT_END_DATE", "label": "End Date", "fmt": "date"},
                {"col": "DAYS_LEFT", "label": "Days Left", "fmt": "number"},
                {"col": "CAPACITY_USED", "label": "Used (YTD)", "fmt": "dollar"},
                {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Pred Under", "fmt": "dollar"},
            ])

else:
    st.info("No capacity data found.")

st.divider()

# --- CAPACITY & RENEWAL PIPELINE ---
st.markdown('<div id="nav-cr-pipeline" class="tab-banner"><p class="tab-banner-title">Capacity &amp; Renewal Pipeline</p></div>', unsafe_allow_html=True)

if not cap_pipe_df.empty:
    cap_pipe_df["CLOSE_DATE"] = pd.to_datetime(cap_pipe_df["CLOSE_DATE"])
    fp1, fp2, fp3, fp4, fp5, fp6, fp7 = st.columns(7)
    with fp1:
        dm_filter_p = st.multiselect("DM", options=sorted(cap_pipe_df["DM"].dropna().unique()), default=[], key="cpipe_dm")
    with fp2:
        type_filter = st.multiselect("Opp Type", options=sorted(cap_pipe_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="cpipe_type")
    with fp3:
        ae_filter_p = st.multiselect("AE", options=sorted(cap_pipe_df["OWNER"].dropna().unique()), default=[], key="cpipe_ae")
    with fp4:
        stage_filter_p = st.multiselect("Stage", options=sorted(cap_pipe_df["STAGE_NAME"].dropna().unique()), default=[], key="cpipe_stage")
    with fp5:
        fc_filter_p = st.multiselect("Forecast", options=sorted(cap_pipe_df["FORECAST_STATUS"].dropna().unique()), default=[], key="cpipe_fc")
    with fp6:
        valid_close = cap_pipe_df["CLOSE_DATE"].dropna()
        min_close = valid_close.min().date() if not valid_close.empty else None
        max_close = valid_close.max().date() if not valid_close.empty else None
        close_date_filter = st.date_input("Close Date Range", value=[], min_value=min_close, max_value=max_close, key="cpipe_close_date")
    with fp7:
        search_p = st.text_input("Search opportunity", "", key="cpipe_search")

    filtered_p = cap_pipe_df.copy()
    if dm_filter_p:
        filtered_p = filtered_p[filtered_p["DM"].isin(dm_filter_p)]
    if type_filter:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_TYPE"].isin(type_filter)]
    if ae_filter_p:
        filtered_p = filtered_p[filtered_p["OWNER"].isin(ae_filter_p)]
    if stage_filter_p:
        filtered_p = filtered_p[filtered_p["STAGE_NAME"].isin(stage_filter_p)]
    if fc_filter_p:
        filtered_p = filtered_p[filtered_p["FORECAST_STATUS"].isin(fc_filter_p)]
    if close_date_filter:
        if len(close_date_filter) == 1:
            filtered_p = filtered_p[filtered_p["CLOSE_DATE"].dt.date >= close_date_filter[0]]
        elif len(close_date_filter) == 2:
            filtered_p = filtered_p[(filtered_p["CLOSE_DATE"].dt.date >= close_date_filter[0]) & (filtered_p["CLOSE_DATE"].dt.date <= close_date_filter[1])]
    if search_p:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_NAME"].str.contains(search_p, case=False, na=False) | filtered_p["ACCOUNT_NAME"].str.contains(search_p, case=False, na=False)]

    pk1, pk2, pk3, pk4 = st.columns(4)
    with pk1:
        st.metric("Open Opps", len(filtered_p))
    with pk2:
        total_acv = filtered_p["PRODUCT_FORECAST_ACV"].sum()
        st.metric("Total Product Forecast ACV", f"${total_acv:,.0f}")
    with pk3:
        total_tcv = filtered_p["CALCULATED_TCV"].sum()
        st.metric("Total Calculated TCV", f"${total_tcv:,.0f}")
    with pk4:
        renewals_ct = len(filtered_p[filtered_p["OPPORTUNITY_TYPE"] == "Renewal"])
        st.metric("Renewals", renewals_ct)

    display_p = filtered_p.copy()
    display_p["OPP_LINK"] = display_p.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    with st.expander(f"{len(filtered_p)} opportunities", expanded=True):
        render_html_table(display_p, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE", "label": "Type"},
            {"col": "STAGE_NAME", "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "PRODUCT_FORECAST_ACV", "label": "Product Forecast ACV", "fmt": "dollar"},
            {"col": "PRODUCT_FORECAST_TCV", "label": "Product Forecast TCV", "fmt": "dollar"},
            {"col": "CALCULATED_TCV", "label": "Calculated TCV", "fmt": "dollar"},
            {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
            {"col": "OWNER", "label": "Owner"},
            {"col": "DM", "label": "DM"},
        ], height=500)

        csv_p = filtered_p.to_csv(index=False)
        st.download_button(":material/download: Export Pipeline CSV", csv_p, "capacity_pipeline.csv", "text/csv", key="cpipe_csv")
else:
    st.info("No capacity pipeline opportunities found.")

st.divider()

st.markdown('<div id="nav-cr-invest" class="tab-banner"><p class="tab-banner-title">Investment Opportunities</p></div>', unsafe_allow_html=True)

if not cap_pipe_df.empty:
    invest_df = cap_pipe_df.copy()
    invest_df["CLOSE_DATE"] = pd.to_datetime(invest_df["CLOSE_DATE"], errors="coerce")
    invest_df = invest_df[invest_df["CLOSE_DATE"] > today]
    invest_df = invest_df[invest_df["FORECAST_STATUS"].fillna("") != "Omitted"]

    def _current_fq():
        m = today.month
        fy = today.year + 1 if m >= 2 else today.year
        q = 1 if m in (2, 3, 4) else 2 if m in (5, 6, 7) else 3 if m in (8, 9, 10) else 4
        return f"Q{q}-{fy}"

    if1, if2, if3 = st.columns(3)
    with if1:
        fq_opts = sorted(invest_df["FISCAL_QUARTER"].dropna().unique())
        _cfq = _current_fq()
        fq_default = [_cfq] if _cfq in fq_opts else []
        fq_filter = st.multiselect("Fiscal Quarter", options=fq_opts, default=fq_default, key="invest_fq")
    with if2:
        type_opts = sorted(invest_df["OPPORTUNITY_TYPE"].dropna().unique())
        type_filter_inv = st.multiselect("Type", options=type_opts, default=type_opts, key="invest_type")
    with if3:
        _TCV_MAP = {"All": 0, "$250,000+": 250_000, "$500,000+": 500_000, "$1,000,000+": 1_000_000}
        tcv_label = st.radio("Calculated TCV Threshold", list(_TCV_MAP.keys()), index=2, horizontal=True, key="invest_tcv_radio")
        tcv_threshold = _TCV_MAP[tcv_label]
    excl_segments = st.checkbox("Exclude Segments", value=True, key="invest_excl_segs")
    if fq_filter:
        invest_df = invest_df[invest_df["FISCAL_QUARTER"].isin(fq_filter)]
    if type_filter_inv:
        invest_df = invest_df[invest_df["OPPORTUNITY_TYPE"].isin(type_filter_inv)]
    if excl_segments:
        invest_df = invest_df[~invest_df["OPPORTUNITY_NAME"].str.contains(r"segment\s*\d+", case=False, na=False, regex=True)]
    invest_df = invest_df[invest_df["CALCULATED_TCV"].fillna(0) >= tcv_threshold].copy()
    invest_df["EST_INVESTMENT"] = invest_df["CALCULATED_TCV"].fillna(0) * 0.10
    invest_df["OPP_LINK"] = invest_df.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    ik1, ik2, ik3 = st.columns(3)
    with ik1:
        st.metric("Opportunities", len(invest_df))
    with ik2:
        st.metric("Total Calculated TCV", f"${invest_df['CALCULATED_TCV'].fillna(0).sum():,.0f}")
    with ik3:
        st.metric("Est. Total Investment", f"${invest_df['EST_INVESTMENT'].sum():,.0f}")

    with st.expander(f"{len(invest_df)} opportunities", expanded=True):
        render_html_table(invest_df, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK", "label": "Link", "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE", "label": "Type"},
            {"col": "STAGE_NAME", "label": "Stage"},
            {"col": "FORECAST_STATUS", "label": "Forecast"},
            {"col": "PRODUCT_FORECAST_ACV", "label": "Product Forecast ACV", "fmt": "dollar"},
            {"col": "PRODUCT_FORECAST_TCV", "label": "Product Forecast TCV", "fmt": "dollar"},
            {"col": "CALCULATED_TCV", "label": "Calculated TCV", "fmt": "dollar"},
            {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
            {"col": "OWNER", "label": "Opp Owner"},
            {"col": "EST_INVESTMENT", "label": "Est. Investment", "fmt": "dollar"},
        ], height=500)

        csv_inv = invest_df.to_csv(index=False)
        st.download_button(":material/download: Export Investment CSV", csv_inv, "investment_opps.csv", "text/csv", key="invest_csv")
else:
    st.info("No investment opportunity data found.")
