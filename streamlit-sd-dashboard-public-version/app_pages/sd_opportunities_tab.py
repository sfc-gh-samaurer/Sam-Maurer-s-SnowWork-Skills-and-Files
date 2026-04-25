import streamlit as st
import pandas as pd
from data import load_ps_pipeline, load_ps_history, render_html_table
from constants import SFDC_BASE
from components import section_banner, empty_state

pipeline_df = load_ps_pipeline()
history_df  = load_ps_history()

section_banner("SD Opportunities", "Open pipeline and historical sold services & training")

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1, k2 = st.columns(2)
pipe_tcv = pipeline_df["TOTAL_PST_TCV"].fillna(0).sum() if not pipeline_df.empty else 0
k1.metric("Pipeline Opps", len(pipeline_df))
k2.metric("Pipeline TCV",  f"${pipe_tcv:,.0f}")

st.markdown('<p class="sf-section-label">SD Pipeline (Open Opportunities)</p>', unsafe_allow_html=True)

# ── Pipeline ──────────────────────────────────────────────────────────────────
if not pipeline_df.empty:
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
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
    search_p = st.text_input("Search opportunity name", "", key="psp_search", placeholder="Type to filter…")

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
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
    )

    with st.expander(f"{len(filtered_p)} opportunities", expanded=True):
        render_html_table(display_p, columns=[
            {"col": "ACCOUNT_NAME",              "label": "Account"},
            {"col": "OPPORTUNITY_NAME",           "label": "Opportunity"},
            {"col": "OPP_LINK",                   "label": "SFDC",         "fmt": "link"},
            {"col": "OPPORTUNITY_TYPE",           "label": "Type"},
            {"col": "PRODUCT_NAMES",              "label": "Products"},
            {"col": "STAGE_NAME",                 "label": "Stage"},
            {"col": "FORECAST_STATUS",            "label": "Forecast"},
            {"col": "PS_FORECAST_CATEGORY",       "label": "PS Fcast Cat"},
            {"col": "PS_INVESTMENT_TYPE",         "label": "Invest"},
            {"col": "QUOTE_SUB_AGREEMENT_TYPE",   "label": "Agreement"},
            {"col": "CLOSE_DATE",                 "label": "Close",        "fmt": "date"},
            {"col": "CREATED_DATE",               "label": "Created",      "fmt": "date"},
            {"col": "SALES_QUALIFIED_DATE",       "label": "SQ Date",      "fmt": "date"},
            {"col": "FISCAL_QUARTER",             "label": "FQ"},
            {"col": "TOTAL_PST_TCV",              "label": "PS&T TCV",     "fmt": "dollar"},
            {"col": "PS_SERVICES_FORECAST",       "label": "PS Fcast $",   "fmt": "dollar"},
            {"col": "DM",                         "label": "DM"},
            {"col": "OWNER",                      "label": "AE"},
            {"col": "PS_SELLER_NAME",             "label": "PS Seller"},

            {"col": "OPP_PROBABILITY",            "label": "Prob %",       "fmt": "pct"},
        ], height=450)
        st.download_button(":material/download: Export CSV", filtered_p.to_csv(index=False), "pst_pipeline.csv", "text/csv", key="psp_csv")
else:
    empty_state("No PS&T pipeline opportunities found.")

st.divider()

st.markdown('<p class="sf-section-label">Historical Sold Services & Training</p>', unsafe_allow_html=True)

# ── History ───────────────────────────────────────────────────────────────────
if not history_df.empty:
    hc1, hc2, hc3, hc4, hc5 = st.columns(5)
    with hc1:
        acct_filter_h = st.multiselect("Account", options=sorted(history_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psh_acct")
    with hc2:
        ae_filter_h = st.multiselect("AE", options=sorted(history_df["AE"].dropna().unique()), default=[], key="psh_ae")
    with hc3:
        pf_filter_h = st.multiselect("Product Family", options=sorted(history_df["PRODUCT_FAMILIES"].dropna().unique()), default=[], key="psh_pf")
    with hc4:
        type_filter_h = st.multiselect("Opp Type", options=sorted(history_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="psh_type")
    with hc5:
        search_h = st.text_input("Search", "", key="psh_search", placeholder="Account or opportunity…")

    filtered_h = history_df.copy()
    if acct_filter_h:
        filtered_h = filtered_h[filtered_h["ACCOUNT_NAME"].isin(acct_filter_h)]
    if ae_filter_h:
        filtered_h = filtered_h[filtered_h["AE"].isin(ae_filter_h)]
    if pf_filter_h:
        filtered_h = filtered_h[filtered_h["PRODUCT_FAMILIES"].isin(pf_filter_h)]
    if type_filter_h:
        filtered_h = filtered_h[filtered_h["OPPORTUNITY_TYPE"].isin(type_filter_h)]
    if search_h:
        filtered_h = filtered_h[
            filtered_h["OPPORTUNITY_NAME"].str.contains(search_h, case=False, na=False)
            | filtered_h["ACCOUNT_NAME"].str.contains(search_h, case=False, na=False)
        ]

    hk1, hk2, hk3, hk4 = st.columns(4)
    hk1.metric("Closed Won",   len(filtered_h))
    hk2.metric("PS Services",  f"${filtered_h['PS_SERVICES_ACV'].sum():,.0f}")
    hk3.metric("Edu Services", f"${filtered_h['EDU_SERVICES_ACV'].sum():,.0f}")
    hk4.metric("Total PST",    f"${filtered_h['TOTAL_PST_AMOUNT'].sum():,.0f}")

    display_h = filtered_h.copy()
    display_h["OPP_LINK"] = display_h.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
    )
    with st.expander(f"{len(filtered_h)} closed won opportunities", expanded=True):
        render_html_table(display_h, columns=[
            {"col": "ACCOUNT_NAME",     "label": "Account"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK",         "label": "SFDC",         "fmt": "link"},
            {"col": "DM",               "label": "DM"},
            {"col": "AE",               "label": "AE"},
            {"col": "OPP_OWNER",        "label": "Opp Owner"},
            {"col": "OPPORTUNITY_TYPE", "label": "Type"},
            {"col": "CLOSE_DATE",       "label": "Close Date",   "fmt": "date"},
            {"col": "PRODUCT_FAMILIES", "label": "Product Family"},
            {"col": "PS_SERVICES_ACV",  "label": "PS Svc $",     "fmt": "dollar"},
            {"col": "EDU_SERVICES_ACV", "label": "Edu Svc $",    "fmt": "dollar"},
            {"col": "TOTAL_PST_AMOUNT", "label": "Total PST $",  "fmt": "dollar"},
            {"col": "PS_INVESTMENT_TYPE","label": "Invest Type"},
            {"col": "PS_INVESTMENT_AMOUNT","label": "Invest $",  "fmt": "dollar"},
            {"col": "PS_SELLER_NAME",   "label": "PS Seller"},
            {"col": "STAGE_NAME",       "label": "Stage"},
        ], height=600)
        st.download_button(":material/download: Export CSV", filtered_h.to_csv(index=False), "pst_history.csv", "text/csv", key="psh_csv")
else:
    empty_state("No historical PS&T opportunities found.")
