import streamlit as st
import pandas as pd
import re
from data import load_use_cases, load_action_planner_pipeline, render_html_table, load_wow_use_cases
from constants import SFDC_BASE
from components import section_banner, empty_state

df    = load_use_cases()
ap_df = load_action_planner_pipeline()
wow   = load_wow_use_cases()

section_banner("Use Cases", "Pipeline use cases across all accounts")


def _stage_num(s):
    try:
        return int(str(s).split(" - ")[0].strip())
    except Exception:
        return -1


wow_stages = wow[wow["FIELD"] == "Stage__c"].copy()
if not wow_stages.empty:
    wow_stages["DIRECTION"] = wow_stages.apply(
        lambda r: "Advance" if _stage_num(r["NEW_VALUE"]) > _stage_num(r["OLD_VALUE"]) else "Regression", axis=1
    )
else:
    wow_stages["DIRECTION"] = pd.Series(dtype=str)

wow_advances     = wow_stages[wow_stages["DIRECTION"] == "Advance"] if not wow_stages.empty else pd.DataFrame()
wow_regressions  = wow_stages[wow_stages["DIRECTION"] == "Regression"] if not wow_stages.empty else pd.DataFrame()
wow_lost         = wow_stages[wow_stages["NEW_VALUE"].str.contains("8 - Use Case Lost", na=False)] if not wow_stages.empty else pd.DataFrame()
wow_tech_wins    = wow[wow["FIELD"] == "Technical_Win__c"]
wow_golive       = wow[wow["FIELD"] == "Actual_Go_Live_Date__c"]

_adv_n = len(wow_advances)
_reg_n = len(wow_regressions)
_win_n = len(wow_tech_wins)
_gl_n  = len(wow_golive)

_wow_label = f"This Week's Use Case Changes  \u2014  {_adv_n} advances\u00a0\u00b7\u00a0{_reg_n} regressions\u00a0\u00b7\u00a0{_win_n} tech wins\u00a0\u00b7\u00a0{_gl_n} go-live shifts"

with st.expander(_wow_label, expanded=False):
    _wt1, _wt2, _wt3, _wt4 = st.tabs([
        f"Stage Advances ({_adv_n})",
        f"Regressions ({_reg_n})",
        f"Tech Wins ({_win_n})",
        f"Go-Live Shifts ({_gl_n})",
    ])

    def _uc_link(row):
        uid = row.get("USE_CASE_ID")
        return f"{SFDC_BASE}/{uid}/view" if uid and str(uid).strip() else None

    def _add_uc_links(df_in):
        d = df_in.copy()
        d["UC_LINK"] = d.apply(_uc_link, axis=1)
        return d

    _wow_stage_cols = [
        {"col": "ACCOUNT_NAME",  "label": "Account"},
        {"col": "USE_CASE_NAME", "label": "Use Case"},
        {"col": "UC_LINK",       "label": "SFDC",           "fmt": "link"},
        {"col": "OLD_VALUE",     "label": "From Stage"},
        {"col": "NEW_VALUE",     "label": "To Stage"},
        {"col": "ACV",           "label": "eACV",           "fmt": "dollar"},
        {"col": "UC_STATUS",     "label": "Status"},
        {"col": "DECISION_DATE", "label": "Decision Date",  "fmt": "date"},
        {"col": "TARGET_GO_LIVE","label": "Target Go-Live", "fmt": "date"},
        {"col": "CHANGED_AT",   "label": "Changed",        "fmt": "date"},
    ]

    with _wt1:
        if wow_advances.empty:
            empty_state("No stage advances this week.")
        else:
            render_html_table(_add_uc_links(wow_advances), columns=_wow_stage_cols, height=max(180, min(500, _adv_n * 40 + 60)))

    with _wt2:
        if wow_regressions.empty:
            empty_state("No stage regressions this week.")
        else:
            render_html_table(_add_uc_links(wow_regressions), columns=_wow_stage_cols, height=max(180, min(500, _reg_n * 40 + 60)))

    with _wt3:
        if wow_tech_wins.empty:
            empty_state("No technical wins recorded this week.")
        else:
            render_html_table(_add_uc_links(wow_tech_wins), columns=[
                {"col": "ACCOUNT_NAME",  "label": "Account"},
                {"col": "USE_CASE_NAME", "label": "Use Case"},
                {"col": "UC_LINK",       "label": "SFDC",          "fmt": "link"},
                {"col": "CURRENT_STAGE", "label": "Current Stage"},
                {"col": "ACV",           "label": "eACV",          "fmt": "dollar"},
                {"col": "UC_STATUS",     "label": "Status"},
                {"col": "TARGET_GO_LIVE","label": "Target Go-Live","fmt": "date"},
                {"col": "CHANGED_AT",   "label": "When",           "fmt": "date"},
            ], height=max(180, min(500, _win_n * 40 + 60)))

    with _wt4:
        if wow_golive.empty:
            empty_state("No go-live date changes this week.")
        else:
            render_html_table(_add_uc_links(wow_golive), columns=[
                {"col": "ACCOUNT_NAME",  "label": "Account"},
                {"col": "USE_CASE_NAME", "label": "Use Case"},
                {"col": "UC_LINK",       "label": "SFDC",          "fmt": "link"},
                {"col": "CURRENT_STAGE", "label": "Current Stage"},
                {"col": "OLD_VALUE",     "label": "Previous Date"},
                {"col": "NEW_VALUE",     "label": "New Date"},
                {"col": "ACV",           "label": "eACV",          "fmt": "dollar"},
                {"col": "CHANGED_AT",   "label": "Changed",        "fmt": "date"},
            ], height=max(180, min(500, _gl_n * 40 + 60)))


def _latest_se_comment_uc(full_text):
    if pd.isna(full_text) or not str(full_text).strip():
        return ""
    text = str(full_text).strip()
    parts = re.split(r'(?=\[\d{1,2}/\d{1,2}/\d{2,4})', text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts[0] if parts else text[:500]


tab_all, tab_summary = st.tabs(["All Use Cases", "Account Summary"])

# ── All Use Cases ─────────────────────────────────────────────────────────────
with tab_all:
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
            impl_filter = st.multiselect("Implementer", options=["PS", "Partner", "Both", "None"], default=[], key="uc_impl")
        with fc6:
            search = st.text_input("Search", "", key="uc_search", placeholder="Use case name…")

        filtered = df.copy()
        if acct_filter:
            filtered = filtered[filtered["ACCOUNT_NAME"].isin(acct_filter)]
        if ae_filter:
            filtered = filtered[filtered["OWNER"].isin(ae_filter)]
        if status_filter:
            filtered = filtered[filtered["USE_CASE_STATUS"].isin(status_filter)]
        if stage_filter:
            filtered = filtered[filtered["STAGE"].isin(stage_filter)]
        if impl_filter:
            _IMPL_PS     = {"Snowflake SD Prime", "Customer Prime + Snowflake SD"}
            _IMPL_PARTNER = {"Partner Only"}
            _IMPL_BOTH   = {"Partner Prime + Snowflake SD", "Snowflake SD Prime + Partner"}
            impl_masks = []
            if "PS" in impl_filter:
                impl_masks.append(filtered["IMPLEMENTER"].isin(_IMPL_PS))
            if "Partner" in impl_filter:
                impl_masks.append(filtered["IMPLEMENTER"].isin(_IMPL_PARTNER))
            if "Both" in impl_filter:
                impl_masks.append(filtered["IMPLEMENTER"].isin(_IMPL_BOTH))
            if "None" in impl_filter:
                impl_masks.append(filtered["IMPLEMENTER"].isnull() | filtered["IMPLEMENTER"].isin({"Customer Only", "Unknown", ""}))
            if impl_masks:
                combined = impl_masks[0]
                for m in impl_masks[1:]:
                    combined = combined | m
                filtered = filtered[combined]
        if search:
            filtered = filtered[filtered["USE_CASE_NAME"].str.contains(search, case=False, na=False)]

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Use Cases", len(filtered))
        k2.metric("In Pursuit",      len(filtered[filtered["USE_CASE_STATUS"] == "In Pursuit"]))
        k3.metric("Implementation",  len(filtered[filtered["USE_CASE_STATUS"] == "Implementation"]))
        k4.metric("Total eACV",      f"${filtered['ACV'].sum():,.0f}")
        k5.metric("Stuck >90d",      len(filtered[filtered["DAYS_IN_STAGE"] > 90]))

        display = filtered[[
            "ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "USE_CASE_NAME", "USE_CASE_ID",
            "USE_CASE_NUMBER", "USE_CASE_STATUS", "ACV", "STAGE", "DECISION_DATE",
            "CREATED_DATE", "LAST_MODIFIED_DATE", "DAYS_IN_STAGE", "OWNER",
            "NEXT_STEPS", "IS_PS_ENGAGED"
        ]].copy()
        display["UC_LINK"] = display.apply(
            lambda r: f'{SFDC_BASE}/{r["USE_CASE_ID"]}/view' if pd.notna(r.get("USE_CASE_ID")) else None, axis=1
        )
        display["UC_DISPLAY"] = display["USE_CASE_NUMBER"].fillna("")
        display["PS_ENGAGED"] = display["IS_PS_ENGAGED"].map({True: "Yes", False: "No"})

        with st.expander(f"{len(filtered)} use cases", expanded=True):
            render_html_table(display, columns=[
                {"col": "ACCOUNT_NAME",     "label": "Account"},
                {"col": "USE_CASE_NAME",    "label": "Use Case"},
                {"col": "UC_LINK",          "label": "UC #",           "fmt": "link", "display_col": "UC_DISPLAY"},
                {"col": "USE_CASE_STATUS",  "label": "Status"},
                {"col": "ACV",              "label": "eACV",           "fmt": "dollar"},
                {"col": "STAGE",            "label": "Stage"},
                {"col": "DECISION_DATE",    "label": "Decision Date",  "fmt": "date"},
                {"col": "CREATED_DATE",     "label": "Created",        "fmt": "date"},
                {"col": "LAST_MODIFIED_DATE","label": "Modified",      "fmt": "date"},
                {"col": "DAYS_IN_STAGE",    "label": "Days Since Mod", "fmt": "number"},
                {"col": "OWNER",            "label": "AE"},
                {"col": "NEXT_STEPS",       "label": "Next Steps"},
                {"col": "PS_ENGAGED",       "label": "PS Engaged"},
            ], height=600)
            st.download_button(":material/download: Export CSV", filtered.to_csv(index=False), "use_cases.csv", "text/csv", key="uc_csv")
    else:
        empty_state("No use case data found.")

# ── Account Summary ───────────────────────────────────────────────────────────
with tab_summary:
    if not ap_df.empty:
        uc_left, uc_right = st.columns([1, 3])

        with uc_left:
            ap_stage_opts = sorted(ap_df["STAGE"].dropna().unique())
            ap_pipeline_stages = [s for s in ap_stage_opts if s not in ("7 - Deployed", "8 - Use Case Lost", "0 - Not In Pursuit")]
            ap_sel_stages = st.multiselect(
                "Stage",
                ap_stage_opts,
                default=ap_pipeline_stages if ap_pipeline_stages else ap_stage_opts,
                key="uc_detail_stage",
            )

        ap_stage_filtered = ap_df[ap_df["STAGE"].isin(ap_sel_stages) | ap_df["STAGE"].isna()]
        ap_account_names  = sorted(ap_stage_filtered["ACCOUNT_NAME"].dropna().unique())

        with uc_right:
            ap_sel_account = st.selectbox(
                "Select account",
                ap_account_names,
                index=None,
                placeholder="Choose an account…",
                key="uc_detail_account",
            )

            if not ap_sel_account:
                ap_summary = (
                    ap_stage_filtered.groupby(["ACCOUNT_NAME", "DISTRICT", "AE_NAME"])
                    .agg(Pipeline_UCs=("USE_CASE_NAME", lambda x: x.notna().sum()), Total_EACV=("EACV", "sum"))
                    .reset_index()
                    .sort_values("Pipeline_UCs", ascending=False)
                )
                ap_summary["Total_EACV"] = ap_summary["Total_EACV"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "$0")
                ap_summary.columns = ["Account", "District", "AE", "Pipeline UCs", "Total eACV"]
                st.dataframe(ap_summary, use_container_width=True, hide_index=True, height=min(len(ap_summary) * 35 + 40, 400))
            else:
                ap_acct_df  = ap_stage_filtered[ap_stage_filtered["ACCOUNT_NAME"] == ap_sel_account].reset_index(drop=True)
                ap_acct_ucs = ap_acct_df[ap_acct_df["USE_CASE_NAME"].notna()].reset_index(drop=True)
                ap_ae = ap_acct_df["AE_NAME"].iloc[0] if not ap_acct_df.empty else "—"
                ap_se = ap_acct_df["SE_NAME"].iloc[0] if not ap_acct_df.empty else "—"

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("AE", ap_ae)
                m2.metric("SE", ap_se)
                m3.metric("Pipeline UCs",  len(ap_acct_ucs))
                m4.metric("Pipeline eACV", f"${ap_acct_ucs['EACV'].sum():,.0f}")

                if st.button("Open in Account Details →", key=f"uc_nav_acct_{ap_sel_account}", type="primary"):
                    from data import load_hierarchy as _lh_uc
                    _hier_uc = _lh_uc()
                    _dm_uc   = ap_acct_df["DM"].iloc[0] if not ap_acct_df.empty else ""
                    _d_uc    = _hier_uc[_hier_uc["DM"] == _dm_uc]
                    if not _d_uc.empty:
                        _dr = _d_uc.iloc[0]
                        st.session_state["acct_theater"]   = _dr.get("THEATER", "")
                        st.session_state["acct_region"]    = _dr.get("REGION", "")
                        st.session_state["acct_district"]  = _dr.get("DISTRICT", "")
                    st.session_state["acct_ae"]            = "All AEs"
                    st.session_state["acct_detail_select"] = ap_sel_account
                    st.session_state["current_page"]       = ":material/manage_accounts: Account Details"
                    st.rerun()

                if not ap_acct_ucs.empty:
                    ap_disp = ap_acct_ucs[[
                        "USE_CASE_NAME", "USE_CASE_ID", "USE_CASE_NUMBER", "STAGE", "EACV",
                        "TECHNICAL_UC", "IMPLEMENTER", "USE_CASE_COMMENTS", "NEXT_STEPS", "SE_COMMENTS_FULL"
                    ]].copy()
                    ap_disp["SE_COMMENTS"] = ap_disp["SE_COMMENTS_FULL"].apply(_latest_se_comment_uc)
                    ap_disp["SFDC"] = ap_disp.apply(
                        lambda r: f"{SFDC_BASE}/{r['USE_CASE_ID']}/view" if pd.notna(r.get("USE_CASE_ID")) else None, axis=1
                    )
                    ap_disp = ap_disp[[
                        "USE_CASE_NAME", "SFDC", "USE_CASE_ID", "USE_CASE_NUMBER", "STAGE", "EACV",
                        "TECHNICAL_UC", "IMPLEMENTER", "USE_CASE_COMMENTS", "NEXT_STEPS", "SE_COMMENTS", "SE_COMMENTS_FULL"
                    ]]
                    ap_disp["EACV"] = ap_disp["EACV"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "$0")
                    st.data_editor(
                        ap_disp,
                        column_config={
                            "USE_CASE_NAME":    st.column_config.TextColumn("Use Case",    width="large"),
                            "SFDC":             st.column_config.LinkColumn("SFDC",        display_text="Open", width="small"),
                            "USE_CASE_ID":      None,
                            "USE_CASE_NUMBER":  None,
                            "STAGE":            st.column_config.TextColumn("Stage",       width="medium"),
                            "EACV":             st.column_config.TextColumn("eACV",        width="small"),
                            "TECHNICAL_UC":     st.column_config.TextColumn("Technical UC",width="medium"),
                            "IMPLEMENTER":      st.column_config.TextColumn("Implementer", width="medium"),
                            "USE_CASE_COMMENTS":st.column_config.TextColumn("Comments",    width="large"),
                            "NEXT_STEPS":       st.column_config.TextColumn("Next Steps",  width="medium"),
                            "SE_COMMENTS":      st.column_config.TextColumn("SE Comments", width="large"),
                            "SE_COMMENTS_FULL": None,
                        },
                        column_order=["USE_CASE_NAME", "SFDC", "STAGE", "EACV",
                                      "TECHNICAL_UC", "IMPLEMENTER", "USE_CASE_COMMENTS", "NEXT_STEPS", "SE_COMMENTS"],
                        use_container_width=True,
                        hide_index=True,
                        disabled=True,
                        key=f"uc_detail_editor_{ap_sel_account}",
                    )
                else:
                    empty_state("No pipeline use cases found for this account.")
    else:
        empty_state("No account use case data found.")
