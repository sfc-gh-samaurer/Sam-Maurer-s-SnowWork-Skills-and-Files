import streamlit as st
import pandas as pd
import re
from data import load_use_cases, load_action_planner_pipeline, render_html_table, render_nav_bar

from constants import SFDC_BASE

df = load_use_cases()
ap_df = load_action_planner_pipeline()

render_nav_bar([
    ("All Use Cases", "nav-uc-all"),
    ("Account-Level Use Case Summary", "nav-uc-summary"),
])

st.markdown('<div id="nav-uc-all" class="tab-banner"><p class="tab-banner-title">All Use Cases</p></div>', unsafe_allow_html=True)

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
    if impl_filter:
        _IMPL_PS = {"Snowflake SD Prime", "Customer Prime + Snowflake SD"}
        _IMPL_PARTNER = {"Partner Only"}
        _IMPL_BOTH = {"Partner Prime + Snowflake SD", "Snowflake SD Prime + Partner"}
        _IMPL_NONE = {None, "", "Customer Only", "Unknown"}
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
            combined_impl = impl_masks[0]
            for m in impl_masks[1:]:
                combined_impl = combined_impl | m
            filtered = filtered[combined_impl]
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
        stuck_count = len(filtered[filtered["DAYS_IN_STAGE"] > 90])
        st.metric("Stuck >90d", stuck_count)

    display = filtered[["ACCOUNT_NAME", "SALESFORCE_ACCOUNT_ID", "USE_CASE_NAME", "USE_CASE_ID", "USE_CASE_NUMBER", "USE_CASE_STATUS",
                        "ACV", "STAGE", "DECISION_DATE", "CREATED_DATE", "LAST_MODIFIED_DATE",
                        "DAYS_IN_STAGE", "OWNER", "NEXT_STEPS", "IS_PS_ENGAGED"]].copy()

    display["UC_LINK"] = display.apply(
        lambda r: f'{SFDC_BASE}/{r["USE_CASE_ID"]}/view' if pd.notna(r.get("USE_CASE_ID")) else None,
        axis=1
    )
    display["UC_DISPLAY"] = display["USE_CASE_NUMBER"].fillna("")
    display["PS_ENGAGED"] = display["IS_PS_ENGAGED"].map({True: "Yes", False: "No"})

    with st.expander(f":material/table: **Use Cases** — {len(filtered)} records", expanded=True):
        render_html_table(display, columns=[
            {"col": "ACCOUNT_NAME", "label": "Account"},
            {"col": "USE_CASE_NAME", "label": "Use Case"},
            {"col": "UC_LINK", "label": "UC #", "fmt": "link", "display_col": "UC_DISPLAY"},
            {"col": "USE_CASE_STATUS", "label": "Status"},
            {"col": "ACV", "label": "eACV", "fmt": "dollar"},
            {"col": "STAGE", "label": "Stage"},
            {"col": "DECISION_DATE", "label": "Decision Date", "fmt": "date"},
            {"col": "CREATED_DATE", "label": "Created", "fmt": "date"},
            {"col": "LAST_MODIFIED_DATE", "label": "Modified", "fmt": "date"},
            {"col": "DAYS_IN_STAGE", "label": "Days Since Modified", "fmt": "number"},
            {"col": "OWNER", "label": "AE"},
            {"col": "NEXT_STEPS", "label": "Next Steps"},
            {"col": "PS_ENGAGED", "label": "PS Engaged"},
        ], height=600)

        csv = filtered.to_csv(index=False)
        st.download_button(":material/download: Export CSV", csv, "use_cases.csv", "text/csv", key="uc_csv")
else:
    st.info("No use case data found.")


def _latest_se_comment_uc(full_text):
    if pd.isna(full_text) or not str(full_text).strip():
        return ""
    text = str(full_text).strip()
    parts = re.split(r'(?=\[\d{1,2}/\d{1,2}/\d{2,4})', text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts[0] if parts else text[:500]


st.divider()
st.markdown('<div id="nav-uc-summary" class="tab-banner"><p class="tab-banner-title">Account-Level Use Case Summary</p></div>', unsafe_allow_html=True)

if not ap_df.empty:
    uc_detail_left, uc_detail_right = st.columns([1, 3])

    with uc_detail_left:
        ap_stage_opts = sorted(ap_df["STAGE"].dropna().unique())
        ap_pipeline_stages = [s for s in ap_stage_opts if s not in ("7 - Deployed", "8 - Use Case Lost", "0 - Not In Pursuit")]
        ap_sel_stages = st.multiselect(
            "Stage",
            ap_stage_opts,
            default=ap_pipeline_stages if ap_pipeline_stages else ap_stage_opts,
            key="uc_detail_stage",
        )

    ap_stage_filtered = ap_df[ap_df["STAGE"].isin(ap_sel_stages) | ap_df["STAGE"].isna()]
    ap_account_names = sorted(ap_stage_filtered["ACCOUNT_NAME"].dropna().unique())

    with uc_detail_right:
        ap_sel_account = st.selectbox(
            "Select account",
            ap_account_names,
            index=None,
            placeholder="Choose an account...",
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
            ap_summary.columns = ["Account", "District", "AE", "Pipeline UCs", "Total EACV"]
            st.dataframe(ap_summary, use_container_width=True, hide_index=True, height=min(len(ap_summary) * 35 + 40, 400))
        else:
            ap_acct_df = ap_stage_filtered[ap_stage_filtered["ACCOUNT_NAME"] == ap_sel_account].reset_index(drop=True)
            ap_acct_ucs = ap_acct_df[ap_acct_df["USE_CASE_NAME"].notna()].reset_index(drop=True)
            ap_ae = ap_acct_df["AE_NAME"].iloc[0] if not ap_acct_df.empty else "Unknown"
            ap_se = ap_acct_df["SE_NAME"].iloc[0] if not ap_acct_df.empty else "Unknown"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("AE", ap_ae)
            m2.metric("SE", ap_se)
            m3.metric("Pipeline UCs", len(ap_acct_ucs))
            m4.metric("Pipeline EACV", f"${ap_acct_ucs['EACV'].sum():,.0f}")

            if not ap_acct_ucs.empty:
                ap_disp = ap_acct_ucs[["USE_CASE_NAME", "USE_CASE_ID", "USE_CASE_NUMBER", "STAGE", "EACV",
                                       "TECHNICAL_UC", "IMPLEMENTER", "USE_CASE_COMMENTS",
                                       "NEXT_STEPS", "SE_COMMENTS_FULL"]].copy()
                ap_disp["SE_COMMENTS"] = ap_disp["SE_COMMENTS_FULL"].apply(_latest_se_comment_uc)
                ap_disp["SFDC"] = ap_disp.apply(
                    lambda r: f"{SFDC_BASE}/{r['USE_CASE_ID']}/view" if pd.notna(r.get("USE_CASE_ID")) else None, axis=1
                )
                ap_disp = ap_disp[["USE_CASE_NAME", "SFDC", "USE_CASE_ID", "USE_CASE_NUMBER", "STAGE", "EACV",
                                   "TECHNICAL_UC", "IMPLEMENTER", "USE_CASE_COMMENTS",
                                   "NEXT_STEPS", "SE_COMMENTS", "SE_COMMENTS_FULL"]]
                ap_disp["EACV"] = ap_disp["EACV"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "$0")
                st.data_editor(
                    ap_disp,
                    column_config={
                        "USE_CASE_NAME": st.column_config.TextColumn("Use Case", width="large"),
                        "SFDC": st.column_config.LinkColumn("SFDC", display_text="Open", width="small"),
                        "USE_CASE_ID": None,
                        "USE_CASE_NUMBER": None,
                        "STAGE": st.column_config.TextColumn("Stage", width="medium"),
                        "EACV": st.column_config.TextColumn("EACV", width="small"),
                        "TECHNICAL_UC": st.column_config.TextColumn("Technical UC", width="medium"),
                        "IMPLEMENTER": st.column_config.TextColumn("Implementer", width="medium"),
                        "USE_CASE_COMMENTS": st.column_config.TextColumn("Comments", width="large"),
                        "NEXT_STEPS": st.column_config.TextColumn("Next Steps", width="medium"),
                        "SE_COMMENTS": st.column_config.TextColumn("SE Comments", width="large"),
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
                st.info("No pipeline use cases found for this account.")
