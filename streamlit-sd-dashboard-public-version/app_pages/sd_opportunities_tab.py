import streamlit as st
import pandas as pd
from datetime import date, timedelta
from data import load_ps_pipeline, load_ps_history, render_html_table, _scope_key
from constants import SFDC_BASE
from components import section_banner, empty_state


def _fiscal_quarters(n_back=3, n_forward=5):
    today = date.today()
    fy_year = today.year + 1 if today.month >= 2 else today.year
    fy_month = today.month - 1 if today.month >= 2 else today.month + 11
    current_fq = (fy_month - 1) // 3 + 1
    quarters = []
    for offset in range(-n_back, n_forward + 1):
        q = current_fq + offset
        y = fy_year
        while q > 4:
            q -= 4
            y += 1
        while q < 1:
            q += 4
            y -= 1
        cal_year = y - 1
        q_starts = {1: (2, 1), 2: (5, 1), 3: (8, 1), 4: (11, 1)}
        q_ends = {1: (4, 30), 2: (7, 31), 3: (10, 31), 4: (1, 31)}
        sm, sd = q_starts[q]
        em, ed = q_ends[q]
        start_d = date(cal_year, sm, sd)
        end_year = cal_year + 1 if q == 4 else cal_year
        end_d = date(end_year, em, ed)
        label = f"FQ{q} FY{y % 100:02d}"
        quarters.append((label, start_d, end_d))
    current_label = f"FQ{current_fq} FY{fy_year % 100:02d}"
    return quarters, current_label


def _apply_timeframe_filter(df, fq_selection, custom_start, custom_end, fq_map):
    if "CLOSE_DATE" not in df.columns or df.empty:
        return df
    close_dates = pd.to_datetime(df["CLOSE_DATE"], errors="coerce").dt.date
    if fq_selection == "Custom Range":
        if custom_start and custom_end:
            mask = (close_dates >= custom_start) & (close_dates <= custom_end)
            return df[mask]
    elif fq_selection != "All":
        start_d, end_d = fq_map[fq_selection]
        mask = (close_dates >= start_d) & (close_dates <= end_d)
        return df[mask]
    return df


_FQ_LIST, _CURRENT_FQ = _fiscal_quarters()
_FQ_MAP = {label: (s, e) for label, s, e in _FQ_LIST}
_FQ_OPTIONS = ["All"] + [label for label, _, _ in _FQ_LIST] + ["Custom Range"]

_sk = _scope_key()
pipeline_df = load_ps_pipeline(_scope=_sk)
history_df  = load_ps_history(_scope=_sk)
for _df in [pipeline_df, history_df]:
    if "AGREEMENT_TYPE" not in _df.columns:
        _df["AGREEMENT_TYPE"] = _df.get("OPPORTUNITY_TYPE", "")

section_banner("SD Opportunities", "Open pipeline and historical sold services & training")

st.markdown('<p class="sf-section-label">SD Pipeline (Open Opportunities)</p>', unsafe_allow_html=True)

# ── Pipeline ──────────────────────────────────────────────────────────────────
if not pipeline_df.empty:
    _pt1, _pt2, _pt3 = st.columns([1, 1, 1])
    with _pt1:
        _p_fq_default = _FQ_OPTIONS.index(_CURRENT_FQ) if _CURRENT_FQ in _FQ_OPTIONS else 0
        _p_fq = st.selectbox("Timeframe", _FQ_OPTIONS, index=_p_fq_default, key="psp_fq")
    _p_custom_start = _p_custom_end = None
    if _p_fq == "Custom Range":
        with _pt2:
            _p_custom_start = st.date_input("Start date", value=date.today() - timedelta(days=90), key="psp_ds")
        with _pt3:
            _p_custom_end = st.date_input("End date", value=date.today(), key="psp_de")

    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    with fc1:
        acct_filter_p = st.multiselect("Account", options=sorted(pipeline_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psp_acct")
    with fc2:
        ae_filter_p = st.multiselect("AE", options=sorted(pipeline_df["OWNER"].dropna().unique()), default=[], key="psp_ae")
    with fc3:
        stage_filter_p = st.multiselect("Stage", options=sorted(pipeline_df["STAGE_NAME"].dropna().unique()), default=[], key="psp_stage")
    with fc4:
        type_filter_p = st.multiselect("Agreement Type", options=sorted(pipeline_df["AGREEMENT_TYPE"].dropna().unique()), default=[], key="psp_type")
    with fc5:
        fc_filter_p = st.multiselect("Forecast", options=sorted(pipeline_df["FORECAST_STATUS"].dropna().unique()), default=[], key="psp_fc")
    search_p = st.text_input("Search opportunity name", "", key="psp_search", placeholder="Type to filter…")

    filtered_p = _apply_timeframe_filter(pipeline_df, _p_fq, _p_custom_start, _p_custom_end, _FQ_MAP)
    if acct_filter_p:
        filtered_p = filtered_p[filtered_p["ACCOUNT_NAME"].isin(acct_filter_p)]
    if ae_filter_p:
        filtered_p = filtered_p[filtered_p["OWNER"].isin(ae_filter_p)]
    if stage_filter_p:
        filtered_p = filtered_p[filtered_p["STAGE_NAME"].isin(stage_filter_p)]
    if type_filter_p:
        filtered_p = filtered_p[filtered_p["AGREEMENT_TYPE"].isin(type_filter_p)]
    if fc_filter_p:
        filtered_p = filtered_p[filtered_p["FORECAST_STATUS"].isin(fc_filter_p)]
    if search_p:
        filtered_p = filtered_p[filtered_p["OPPORTUNITY_NAME"].str.contains(search_p, case=False, na=False)]

    k1, k2 = st.columns(2)
    pipe_tcv = filtered_p["TOTAL_PST_TCV"].fillna(0).sum()
    k1.metric("Pipeline Opps", len(filtered_p))
    k2.metric("Pipeline TCV",  f"${pipe_tcv:,.0f}")

    display_p = filtered_p.copy()
    display_p["OPP_LINK"] = display_p.apply(
        lambda r: f'{SFDC_BASE}/Opportunity/{r["OPPORTUNITY_ID"]}/view' if pd.notna(r.get("OPPORTUNITY_ID")) else None, axis=1
    )

    with st.expander(f"{len(filtered_p)} opportunities", expanded=True):
        render_html_table(display_p, columns=[
            {"col": "ACCOUNT_NAME",              "label": "Account"},
            {"col": "OWNER",                      "label": "AE"},
            {"col": "OPPORTUNITY_NAME",           "label": "Opportunity"},
            {"col": "OPP_LINK",                   "label": "SFDC",         "fmt": "link"},
            {"col": "AGREEMENT_TYPE",             "label": "Agreement Type"},
            {"col": "PRODUCT_NAMES",              "label": "Products"},
            {"col": "STAGE_NAME",                 "label": "Stage"},
            {"col": "CLOSE_DATE",                 "label": "Close",        "fmt": "date"},
            {"col": "FORECAST_STATUS",            "label": "Forecast"},
            {"col": "PS_INVESTMENT_TYPE",         "label": "Invest"},
            {"col": "CREATED_DATE",               "label": "Created",      "fmt": "date"},
            {"col": "SALES_QUALIFIED_DATE",       "label": "SQ Date",      "fmt": "date"},
            {"col": "FISCAL_QUARTER",             "label": "FQ"},
            {"col": "TOTAL_PST_TCV",              "label": "PS&T TCV",     "fmt": "dollar"},
            {"col": "PS_SERVICES_FORECAST",       "label": "PS Fcast $",   "fmt": "dollar"},
            {"col": "DM",                         "label": "DM"},
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
    _ht1, _ht2, _ht3 = st.columns([1, 1, 1])
    with _ht1:
        _h_fq = st.selectbox("Timeframe", _FQ_OPTIONS, index=0, key="psh_fq")
    _h_custom_start = _h_custom_end = None
    if _h_fq == "Custom Range":
        with _ht2:
            _h_custom_start = st.date_input("Start date", value=date.today() - timedelta(days=365), key="psh_ds")
        with _ht3:
            _h_custom_end = st.date_input("End date", value=date.today(), key="psh_de")

    hc1, hc2, hc3, hc4, hc5 = st.columns(5)
    with hc1:
        acct_filter_h = st.multiselect("Account", options=sorted(history_df["ACCOUNT_NAME"].dropna().unique()), default=[], key="psh_acct")
    with hc2:
        ae_filter_h = st.multiselect("AE", options=sorted(history_df["AE"].dropna().unique()), default=[], key="psh_ae")
    with hc3:
        pf_filter_h = st.multiselect("Product Family", options=sorted(history_df["PRODUCT_FAMILIES"].dropna().unique()), default=[], key="psh_pf")
    with hc4:
        type_filter_h = st.multiselect("Agreement Type", options=sorted(history_df["AGREEMENT_TYPE"].dropna().unique()), default=[], key="psh_type")
    with hc5:
        search_h = st.text_input("Search", "", key="psh_search", placeholder="Account or opportunity…")

    filtered_h = _apply_timeframe_filter(history_df, _h_fq, _h_custom_start, _h_custom_end, _FQ_MAP)
    if acct_filter_h:
        filtered_h = filtered_h[filtered_h["ACCOUNT_NAME"].isin(acct_filter_h)]
    if ae_filter_h:
        filtered_h = filtered_h[filtered_h["AE"].isin(ae_filter_h)]
    if pf_filter_h:
        filtered_h = filtered_h[filtered_h["PRODUCT_FAMILIES"].isin(pf_filter_h)]
    if type_filter_h:
        filtered_h = filtered_h[filtered_h["AGREEMENT_TYPE"].isin(type_filter_h)]
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
            {"col": "AE",               "label": "AE"},
            {"col": "OPPORTUNITY_NAME", "label": "Opportunity"},
            {"col": "OPP_LINK",         "label": "SFDC",         "fmt": "link"},
            {"col": "DM",               "label": "DM"},
            {"col": "OPP_OWNER",        "label": "Opp Owner"},
            {"col": "AGREEMENT_TYPE",   "label": "Agreement Type"},
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
