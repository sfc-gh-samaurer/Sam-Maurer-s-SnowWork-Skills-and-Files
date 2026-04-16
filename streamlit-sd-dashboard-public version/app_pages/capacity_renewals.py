import streamlit as st
import pandas as pd
from datetime import datetime
from data import load_capacity_renewals, load_capacity_pipeline, render_html_table

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"

df = load_capacity_renewals()
cap_pipe_df = load_capacity_pipeline()

today = pd.Timestamp.now().normalize()

# --- FILTERS ---
st.markdown('<div class="tab-banner"><p class="tab-banner-title">Active Capacity Contracts</p></div>', unsafe_allow_html=True)

if not df.empty:
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        dm_filter = st.multiselect("DM", options=sorted(df["DM"].dropna().unique()), default=[], key="cap_dm")
    with fc2:
        ae_filter = st.multiselect("AE", options=sorted(df["ACCOUNT_OWNER"].dropna().unique()), default=[], key="cap_ae")
    with fc3:
        cap_filter = st.multiselect("Remaining Capacity", options=["$0 (No Data)", "< $1M", "$1M - $5M", "$5M - $10M", "> $10M"], default=[], key="cap_band")
    with fc4:
        search = st.text_input("Search account", "", key="cap_search")

    filtered = df.copy()
    if dm_filter:
        filtered = filtered[filtered["DM"].isin(dm_filter)]
    if ae_filter:
        filtered = filtered[filtered["ACCOUNT_OWNER"].isin(ae_filter)]
    if cap_filter:
        cap_masks = []
        if "$0 (No Data)" in cap_filter:
            cap_masks.append(filtered["CAPACITY_REMAINING"].fillna(0) == 0)
        if "< $1M" in cap_filter:
            cap_masks.append((filtered["CAPACITY_REMAINING"].fillna(0) > 0) & (filtered["CAPACITY_REMAINING"].fillna(0) < 1_000_000))
        if "$1M - $5M" in cap_filter:
            cap_masks.append((filtered["CAPACITY_REMAINING"].fillna(0) >= 1_000_000) & (filtered["CAPACITY_REMAINING"].fillna(0) < 5_000_000))
        if "$5M - $10M" in cap_filter:
            cap_masks.append((filtered["CAPACITY_REMAINING"].fillna(0) >= 5_000_000) & (filtered["CAPACITY_REMAINING"].fillna(0) < 10_000_000))
        if "> $10M" in cap_filter:
            cap_masks.append(filtered["CAPACITY_REMAINING"].fillna(0) >= 10_000_000)
        if cap_masks:
            combined_cap = cap_masks[0]
            for m in cap_masks[1:]:
                combined_cap = combined_cap | m
            filtered = filtered[combined_cap]
    if search:
        filtered = filtered[filtered["ACCOUNT_NAME"].str.contains(search, case=False, na=False)]

    def sfdc_account_link(name, sfdc_id):
        if pd.notna(sfdc_id) and sfdc_id:
            return f"{SFDC_BASE}/Account/{sfdc_id}/view"
        return None

    display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                        "LEAD_SE",
                        "CONTRACT_START_DATE", "CONTRACT_END_DATE",
                        "CAPACITY_USED", "CAPACITY_REMAINING",
                        "OVERAGE_UNDERAGE_PREDICTION", "OVERAGE_DATE"]].copy()

    display["ACCOUNT_LINK"] = display.apply(lambda r: sfdc_account_link(r["ACCOUNT_NAME"], r["SALESFORCE_ACCOUNT_ID"]), axis=1)

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Accounts", len(filtered))
    with kpi2:
        used_ytd = filtered["CAPACITY_USED"].sum()
        st.metric("Total Used YTD", f"${used_ytd:,.0f}")
    with kpi3:
        remaining = filtered["CAPACITY_REMAINING"].sum()
        st.metric("Total Remaining", f"${remaining:,.0f}")

    render_html_table(display, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "ACCOUNT_LINK", "label": "SFDC", "fmt": "link"},
        {"col": "ACCOUNT_OWNER", "label": "AE"},
        {"col": "DM", "label": "DM"},
        {"col": "LEAD_SE", "label": "Lead SE"},
        {"col": "CONTRACT_START_DATE", "label": "Start", "fmt": "date"},
        {"col": "CONTRACT_END_DATE", "label": "End", "fmt": "date"},
        {"col": "CAPACITY_USED", "label": "Cap Used YTD", "fmt": "dollar"},
        {"col": "CAPACITY_REMAINING", "label": "Cap Remain", "fmt": "dollar"},
        {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Over/Under", "fmt": "dollar"},
        {"col": "OVERAGE_DATE", "label": "Overage Date", "fmt": "date"},
    ], height=600)

    csv = filtered.to_csv(index=False)
    st.download_button(":material/download: Export CSV", csv, "capacity_contracts.csv", "text/csv", key="cap_csv")

    candidates = filtered[
        (filtered["CONTRACT_END_DATE"].notna())
    ].copy()
    candidates["DAYS_LEFT"] = (pd.to_datetime(candidates["CONTRACT_END_DATE"]) - today).dt.days
    candidates["PCT_REMAINING"] = candidates.apply(
        lambda r: round(r["CAPACITY_REMAINING"] / (r["CAPACITY_REMAINING"] + r["CAPACITY_USED"]) * 100, 1)
        if pd.notna(r["CAPACITY_REMAINING"]) and pd.notna(r["CAPACITY_USED"]) and (r["CAPACITY_REMAINING"] + r["CAPACITY_USED"]) > 0
        else None, axis=1
    )
    candidates = candidates[
        (candidates["DAYS_LEFT"] <= 730)
        & (candidates["DAYS_LEFT"] > 0)
        & (candidates["OVERAGE_UNDERAGE_PREDICTION"] < 0)
    ].sort_values("OVERAGE_UNDERAGE_PREDICTION", ascending=True)

    st.divider()
    st.markdown('<div class="tab-banner"><p class="tab-banner-title">Capacity Conversion Candidates</p></div>', unsafe_allow_html=True)

    if not candidates.empty:
        with st.expander(f"{len(candidates)} accounts ending within 24 months with predicted underburn", expanded=True):
            st.caption("These accounts are predicted to have significant unused capacity at contract end — consider converting remaining capacity into services contracts.")
            conv_display = candidates[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                                       "CONTRACT_END_DATE", "DAYS_LEFT",
                                       "CAPACITY_USED", "CAPACITY_REMAINING", "PCT_REMAINING",
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
                {"col": "CAPACITY_USED", "label": "Used YTD", "fmt": "dollar"},
                {"col": "CAPACITY_REMAINING", "label": "Cap Remain", "fmt": "dollar"},
                {"col": "PCT_REMAINING", "label": "% Remain", "fmt": "pct"},
                {"col": "OVERAGE_UNDERAGE_PREDICTION", "label": "Pred Under", "fmt": "dollar"},
            ])

else:
    st.info("No capacity data found.")

st.divider()

# --- CAPACITY & RENEWAL PIPELINE ---
st.markdown('<div class="tab-banner"><p class="tab-banner-title">Capacity &amp; Renewal Pipeline</p></div>', unsafe_allow_html=True)

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
        total_acv = filtered_p["TOTAL_ACV"].sum()
        st.metric("Total ACV", f"${total_acv:,.0f}")
    with pk3:
        total_tcv = filtered_p["TCV"].sum()
        st.metric("Total TCV", f"${total_tcv:,.0f}")
    with pk4:
        renewals_ct = len(filtered_p[filtered_p["OPPORTUNITY_TYPE"] == "Renewal"])
        st.metric("Renewals", renewals_ct)

    display_p = filtered_p.copy()
    display_p["OPP_LINK"] = display_p.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1)

    render_html_table(display_p, columns=[
        {"col": "ACCOUNT_NAME", "label": "Account"},
        {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
        {"col": "OPP_LINK", "label": "Opp SFDC", "fmt": "link"},
        {"col": "OPPORTUNITY_TYPE", "label": "Type"},
        {"col": "STAGE_NAME", "label": "Stage"},
        {"col": "FORECAST_STATUS", "label": "Forecast"},
        {"col": "TOTAL_ACV", "label": "Total ACV", "fmt": "dollar"},
        {"col": "RENEWAL_ACV", "label": "Rnwl ACV", "fmt": "dollar"},
        {"col": "GROWTH_ACV", "label": "Growth ACV", "fmt": "dollar"},
        {"col": "TCV", "label": "TCV", "fmt": "dollar"},
        {"col": "CLOSE_DATE", "label": "Close Date", "fmt": "date"},
        {"col": "OWNER", "label": "Owner"},
        {"col": "DM", "label": "DM"},

    ], height=500)

    csv_p = filtered_p.to_csv(index=False)
    st.download_button(":material/download: Export Pipeline CSV", csv_p, "capacity_pipeline.csv", "text/csv", key="cpipe_csv")
else:
    st.info("No capacity pipeline opportunities found.")
