import streamlit as st
import pandas as pd
from datetime import datetime
from data import load_capacity_renewals, load_capacity_pipeline, render_html_table
from constants import SFDC_BASE
from components import section_banner, empty_state

df          = load_capacity_renewals()
cap_pipe_df = load_capacity_pipeline()
today       = pd.Timestamp.now().normalize()

section_banner("Capacity & Renewals", "Active contracts, conversion candidates, pipeline, and investment opportunities")

st.warning("⚠️ Data access permissions to account capacity data causing issues and limitations — working through resolution.", icon=None)

tab_active, tab_candidates, tab_pipeline, tab_invest = st.tabs([
    "Active Contracts",
    "Conversion Candidates",
    "Capacity & Renewal Pipeline",
    "Investment Opportunities",
])

# ── Active Contracts ──────────────────────────────────────────────────────────
with tab_active:
    if not df.empty:
        fc1, fc2 = st.columns(2)
        with fc1:
            ae_filter = st.multiselect("AE", options=sorted(df["ACCOUNT_OWNER"].dropna().unique()), default=[], key="cap_ae")
        with fc2:
            search = st.text_input("Search account", "", key="cap_search", placeholder="Account name…")

        filtered = df.copy()
        if ae_filter:
            filtered = filtered[filtered["ACCOUNT_OWNER"].isin(ae_filter)]
        if search:
            filtered = filtered[filtered["ACCOUNT_NAME"].str.contains(search, case=False, na=False)]

        k1, k2 = st.columns(2)
        k1.metric("Accounts",       len(filtered))
        k2.metric("Total Capacity", f"${filtered['TOTAL_CAP'].sum():,.0f}")

        display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                             "LEAD_SE", "CONTRACT_START_DATE", "CONTRACT_END_DATE",
                             "TOTAL_CAP", "OVERAGE_DATE"]].copy()
        display["ACCOUNT_LINK"] = display["SALESFORCE_ACCOUNT_ID"].apply(
            lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
        )
        with st.expander(f"{len(filtered)} contracts", expanded=True):
            render_html_table(display, columns=[
                {"col": "ACCOUNT_NAME",      "label": "Account"},
                {"col": "ACCOUNT_LINK",      "label": "SFDC",       "fmt": "link"},
                {"col": "ACCOUNT_OWNER",     "label": "AE"},
                {"col": "DM",                "label": "DM"},
                {"col": "LEAD_SE",           "label": "Lead SE"},
                {"col": "CONTRACT_START_DATE","label": "Start",     "fmt": "date"},
                {"col": "CONTRACT_END_DATE", "label": "End",        "fmt": "date"},
                {"col": "TOTAL_CAP",         "label": "Total Cap",  "fmt": "dollar"},
                {"col": "OVERAGE_DATE",      "label": "Overage Date","fmt": "date"},
            ], height=600)
            st.download_button(":material/download: Export CSV", filtered.to_csv(index=False), "capacity_contracts.csv", "text/csv", key="cap_csv")

        st.markdown('<p class="sf-section-label">Jump to Account Details</p>', unsafe_allow_html=True)
        _cr_nav_acct = st.selectbox("Account", options=[""] + sorted(filtered["ACCOUNT_NAME"].dropna().unique()), key="cap_nav_acct", label_visibility="collapsed", placeholder="Select an account to open…")
        if _cr_nav_acct and st.button("Open in Account Details →", key="cap_nav_go", type="primary"):
            from data import load_hierarchy as _lh
            _hier = _lh()
            _cr_row = filtered[filtered["ACCOUNT_NAME"] == _cr_nav_acct]
            if not _cr_row.empty:
                _dm_val = _cr_row.iloc[0].get("DM", "")
                _d_rows = _hier[_hier["DM"] == _dm_val]
                if not _d_rows.empty:
                    _d = _d_rows.iloc[0]
                    st.session_state["acct_theater"]   = _d.get("THEATER", "")
                    st.session_state["acct_region"]    = _d.get("REGION", "")
                    st.session_state["acct_district"]  = _d.get("DISTRICT", "")
            st.session_state["acct_ae"]            = "All AEs"
            st.session_state["acct_detail_select"] = _cr_nav_acct
            st.session_state["current_page"]       = ":material/manage_accounts: Account Details"
            st.rerun()
    else:
        empty_state("No capacity contract data found.")

# ── Conversion Candidates ─────────────────────────────────────────────────────
with tab_candidates:
    if not df.empty:
        candidates = df.copy()
        candidates["DAYS_LEFT"] = (pd.to_datetime(candidates["CONTRACT_END_DATE"]) - today).dt.days
        candidates = candidates[
            (candidates["CONTRACT_END_DATE"].notna())
            & (candidates["DAYS_LEFT"] <= 730)
            & (candidates["DAYS_LEFT"] > 0)
            & (candidates["OVERAGE_UNDERAGE_PREDICTION"] < 0)
        ].sort_values("OVERAGE_UNDERAGE_PREDICTION", ascending=True)

        if candidates.empty:
            empty_state("No conversion candidates found matching the criteria.")
        else:
            st.caption("Accounts predicted to have significant unused capacity at contract end — consider converting remaining capacity into services contracts.")
            k1, k2 = st.columns(2)
            k1.metric("Candidates", len(candidates))
            k2.metric("Avg Days Left", f"{candidates['DAYS_LEFT'].mean():,.0f}")

            conv_display = candidates[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "ACCOUNT_OWNER", "DM",
                                       "CONTRACT_END_DATE", "DAYS_LEFT",
                                       "TOTAL_CAP", "CAPACITY_REMAINING",
                                       "OVERAGE_UNDERAGE_PREDICTION"]].copy()
            conv_display["ACCOUNT_LINK"] = conv_display["SALESFORCE_ACCOUNT_ID"].apply(
                lambda x: f"{SFDC_BASE}/Account/{x}/view" if pd.notna(x) and x else None
            )
            with st.expander(f"{len(candidates)} conversion candidates", expanded=True):
                render_html_table(conv_display, columns=[
                    {"col": "ACCOUNT_NAME",             "label": "Account"},
                    {"col": "ACCOUNT_LINK",             "label": "SFDC",         "fmt": "link"},
                    {"col": "ACCOUNT_OWNER",            "label": "AE"},
                    {"col": "DM",                       "label": "DM"},
                    {"col": "CONTRACT_END_DATE",        "label": "End Date",     "fmt": "date"},
                    {"col": "DAYS_LEFT",                "label": "Days Left",    "fmt": "number"},
                    {"col": "TOTAL_CAP",                "label": "Total Cap",    "fmt": "dollar"},
                    {"col": "CAPACITY_REMAINING",       "label": "Remaining",    "fmt": "dollar"},
                    {"col": "OVERAGE_UNDERAGE_PREDICTION","label": "Overage Pred","fmt": "dollar"},
                ])
    else:
        empty_state("No capacity data available.")

# ── Capacity & Renewal Pipeline ───────────────────────────────────────────────
with tab_pipeline:
    if not cap_pipe_df.empty:
        cap_pipe_df["CLOSE_DATE"] = pd.to_datetime(cap_pipe_df["CLOSE_DATE"])

        fp1, fp2, fp3, fp4, fp5 = st.columns(5)
        with fp1:
            dm_filter_p = st.multiselect("DM", options=sorted(cap_pipe_df["DM"].dropna().unique()), default=[], key="cpipe_dm")
        with fp2:
            type_filter = st.multiselect("Type", options=sorted(cap_pipe_df["OPPORTUNITY_TYPE"].dropna().unique()), default=[], key="cpipe_type")
        with fp3:
            ae_filter_p = st.multiselect("AE", options=sorted(cap_pipe_df["OWNER"].dropna().unique()), default=[], key="cpipe_ae")
        with fp4:
            stage_filter_p = st.multiselect("Stage", options=sorted(cap_pipe_df["STAGE_NAME"].dropna().unique()), default=[], key="cpipe_stage")
        with fp5:
            fc_filter_p = st.multiselect("Forecast", options=sorted(cap_pipe_df["FORECAST_STATUS"].dropna().unique()), default=[], key="cpipe_fc")

        cd1, cd2 = st.columns([2, 3])
        with cd1:
            valid_close = cap_pipe_df["CLOSE_DATE"].dropna()
            min_close = valid_close.min().date() if not valid_close.empty else None
            max_close = valid_close.max().date() if not valid_close.empty else None
            close_date_filter = st.date_input("Close Date Range", value=[], min_value=min_close, max_value=max_close, key="cpipe_close_date")
        with cd2:
            search_p = st.text_input("Search opportunity", "", key="cpipe_search", placeholder="Account or opportunity…")

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
                filtered_p = filtered_p[
                    (filtered_p["CLOSE_DATE"].dt.date >= close_date_filter[0])
                    & (filtered_p["CLOSE_DATE"].dt.date <= close_date_filter[1])
                ]
        if search_p:
            filtered_p = filtered_p[
                filtered_p["OPPORTUNITY_NAME"].str.contains(search_p, case=False, na=False)
                | filtered_p["ACCOUNT_NAME"].str.contains(search_p, case=False, na=False)
            ]

        pk1, pk2, pk3, pk4 = st.columns(4)
        pk1.metric("Open Opps",   len(filtered_p))
        pk2.metric("Forecast ACV",f"${filtered_p['PRODUCT_FORECAST_ACV'].sum():,.0f}")
        pk3.metric("Calc TCV",    f"${filtered_p['CALCULATED_TCV'].sum():,.0f}")
        pk4.metric("Renewals",    len(filtered_p[filtered_p["OPPORTUNITY_TYPE"] == "Renewal"]))

        display_p = filtered_p.copy()
        display_p["OPP_LINK"] = display_p.apply(
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )
        with st.expander(f"{len(filtered_p)} opportunities", expanded=True):
            render_html_table(display_p, columns=[
                {"col": "ACCOUNT_NAME",        "label": "Account"},
                {"col": "OPPORTUNITY_NAME",    "label": "Opportunity"},
                {"col": "OPP_LINK",            "label": "SFDC",       "fmt": "link"},
                {"col": "OPPORTUNITY_TYPE",    "label": "Type"},
                {"col": "STAGE_NAME",          "label": "Stage"},
                {"col": "FORECAST_STATUS",     "label": "Forecast"},
                {"col": "PRODUCT_FORECAST_ACV","label": "Fcst ACV",   "fmt": "dollar"},
                {"col": "PRODUCT_FORECAST_TCV","label": "Fcst TCV",   "fmt": "dollar"},
                {"col": "CALCULATED_TCV",      "label": "Calc TCV",   "fmt": "dollar"},
                {"col": "CLOSE_DATE",          "label": "Close Date", "fmt": "date"},
                {"col": "OWNER",               "label": "AE"},
                {"col": "DM",                  "label": "DM"},
            ], height=500)
            st.download_button(":material/download: Export CSV", filtered_p.to_csv(index=False), "capacity_pipeline.csv", "text/csv", key="cpipe_csv")
    else:
        empty_state("No capacity pipeline opportunities found.")

# ── Investment Opportunities ──────────────────────────────────────────────────
with tab_invest:
    if not cap_pipe_df.empty:
        def _current_fq():
            m = today.month
            fy = today.year + 1 if m >= 2 else today.year
            q = 1 if m in (2, 3, 4) else 2 if m in (5, 6, 7) else 3 if m in (8, 9, 10) else 4
            return f"Q{q}-{fy}"

        invest_df = cap_pipe_df.copy()
        invest_df["CLOSE_DATE"] = pd.to_datetime(invest_df["CLOSE_DATE"], errors="coerce")
        invest_df = invest_df[invest_df["CLOSE_DATE"] > today]
        invest_df = invest_df[invest_df["FORECAST_STATUS"].fillna("") != "Omitted"]

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
            _TCV_MAP = {"All": 0, "$250K+": 250_000, "$500K+": 500_000, "$1M+": 1_000_000}
            tcv_label = st.radio("Min TCV", list(_TCV_MAP.keys()), index=2, horizontal=True, key="invest_tcv_radio")
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
            lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
        )

        ik1, ik2, ik3 = st.columns(3)
        ik1.metric("Opportunities",    len(invest_df))
        ik2.metric("Total Calc TCV",   f"${invest_df['CALCULATED_TCV'].fillna(0).sum():,.0f}")
        ik3.metric("Est. Investment",  f"${invest_df['EST_INVESTMENT'].sum():,.0f}")

        with st.expander(f"{len(invest_df)} opportunities", expanded=True):
            render_html_table(invest_df, columns=[
                {"col": "ACCOUNT_NAME",    "label": "Account"},
                {"col": "OPPORTUNITY_NAME","label": "Opportunity"},
                {"col": "OPP_LINK",        "label": "SFDC",       "fmt": "link"},
                {"col": "OPPORTUNITY_TYPE","label": "Type"},
                {"col": "STAGE_NAME",      "label": "Stage"},
                {"col": "FORECAST_STATUS", "label": "Forecast"},
                {"col": "PRODUCT_FORECAST_ACV","label": "Fcst ACV","fmt": "dollar"},
                {"col": "CALCULATED_TCV",  "label": "Calc TCV",   "fmt": "dollar"},
                {"col": "CLOSE_DATE",      "label": "Close Date", "fmt": "date"},
                {"col": "OWNER",           "label": "AE"},
                {"col": "EST_INVESTMENT",  "label": "Est. Invest","fmt": "dollar"},
            ], height=500)
            st.download_button(":material/download: Export CSV", invest_df.to_csv(index=False), "investment_opps.csv", "text/csv", key="invest_csv")
    else:
        empty_state("No investment opportunity data found.")
