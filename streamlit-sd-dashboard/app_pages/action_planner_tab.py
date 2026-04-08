from data import load_action_planner_pipeline, generate_cortex_response, load_account_consumption_summary, load_accounts_base, load_capacity_renewals
import pandas as pd
import re

SFDC_BASE = "https://snowforce.lightning.force.com/lightning/r"


def _latest_se_comment(full_text):
    if pd.isna(full_text) or not str(full_text).strip():
        return ""
    text = str(full_text).strip()
    parts = re.split(r'(?=\[\d{1,2}/\d{1,2}/\d{2,4})', text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts[0] if parts else text[:500]


def _recent_se_comments(full_text, n=3):
    if pd.isna(full_text) or not str(full_text).strip():
        return ""
    text = str(full_text).strip()
    parts = re.split(r'(?=\[\d{1,2}/\d{1,2}/\d{2,4})', text)
    parts = [p.strip() for p in parts if p.strip()]
    return "\n".join(parts[:n]) if parts else text[:1000]

SD_OFFERINGS = {
    "Snowflake Intelligence (SI)": {
        "price": "Custom fixed-fee",
        "timeline": "8-12 weeks",
        "description": "Fixed-fee custom offering to deploy Snowflake Intelligence. Phases: Discovery & Planning, Build (Cortex Search/Analyst, SI app, up to 3 data sources), Iteration & UAT. Sr. SA at 25 hrs/week.",
    },
    "OpenFlow Bronze Activation": {
        "price": "Custom fixed-fee",
        "timeline": "6-10 weeks",
        "description": "Implement OpenFlow-based data ingestion pipelines. Source assessment, connector config, pipeline build, monitoring, documentation & handoff.",
    },
    "Cortex Search Implementation": {
        "price": "Custom fixed-fee",
        "timeline": "6-10 weeks",
        "description": "Enterprise search over unstructured/semi-structured data. Document processing, chunking/embedding, search service, relevance tuning.",
    },
    "Cortex Analyst Implementation": {
        "price": "Custom fixed-fee",
        "timeline": "6-10 weeks",
        "description": "Natural language querying over structured data. Semantic model design, verified queries, evaluation framework, production hardening.",
    },
    "Architecture Advisory Services": {
        "price": "$9K-63K per topic",
        "timeline": "1-12 weeks",
        "description": "Advisory, design guidance, enablement — NO hands-on. Topics: Core Platform, Data Engineering, AI/ML, Security & Governance, Iceberg/Open Catalog, Terraform. Sr SA $415/hr, SA $335/hr.",
    },
    "Security Assessment": {
        "price": "Custom scoped",
        "timeline": "4-8 weeks",
        "description": "Security posture evaluation against best practices. Scorecard, findings, remediation recommendations, Trust Center enablement.",
    },
    "Resident Solution Architect (RSA)": {
        "price": "$21K (8 wk) or $75K (6 mo)",
        "timeline": "8 weeks or 6 months",
        "description": "Embedded SA providing advisory, enablement, acceleration. 10 hrs/week. Upskills teams, uncovers use cases, accelerates go-lives.",
    },
    "Migration Readiness Assessment (MRA)": {
        "price": "Custom scoped",
        "timeline": "2-4 weeks",
        "description": "Structured migration readiness assessment. Current state analysis, wave planning, resource allocation, risk identification, delivery readout.",
    },
    "Migration Excellence": {
        "price": "Custom scoped",
        "timeline": "12-20+ weeks",
        "description": "End-to-end migration delivery. Code conversion (SnowConvert), ETL migration, data validation, performance testing, cutover, go-live support.",
    },
    "QuickStart Accelerator": {
        "price": "Territory-based",
        "timeline": "1-3 weeks",
        "description": "Rapid onboarding aligned to primary use case. Requires Fundamentals training. Accelerates initial time-to-value.",
    },
    "Customer Journey Workshop (CJW)": {
        "price": "Investment (free)",
        "timeline": "1-2 days",
        "description": "Collaborative workshop to map data journey, identify quick wins, prioritize use cases, build implementation roadmap. Key SD entry point.",
    },
    "Launchpad / Platform Setup": {
        "price": "Custom scoped",
        "timeline": "8-12 weeks",
        "description": "Platform foundation build-out. Warehouse sizing, monitoring, CI/CD, DR/BCP, security, cost governance, data quality foundations.",
    },
}


def _build_offerings_context():
    lines = []
    for name, o in SD_OFFERINGS.items():
        lines.append(f"- {name} ({o['timeline']}): {o['description']}")
    return "\n".join(lines)


def _build_consumption_context(account_name):
    try:
        cdf = load_account_consumption_summary(account_name)
    except Exception:
        return ""
    if cdf.empty:
        return "No consumption data available for this account."
    cat_totals = cdf.groupby("PRODUCT_CATEGORY")["CREDITS"].sum().sort_values(ascending=False)
    months = sorted(cdf["MONTH"].unique())
    complete_months = months[:-1] if len(months) > 1 else months
    lines = [f"CONSUMPTION OVERVIEW (last 6 months, {len(complete_months)} complete months):"]
    lines.append(f"Total credits: {cat_totals.sum():,.0f}")
    lines.append("")
    for cat, total in cat_totals.items():
        cat_data = cdf[cdf["PRODUCT_CATEGORY"] == cat]
        monthly = cat_data.groupby("MONTH")["CREDITS"].sum().sort_index()
        complete = monthly.iloc[:-1] if len(monthly) > 1 else monthly
        if len(complete) >= 3:
            recent_avg = complete.iloc[-2:].mean()
            earlier_avg = complete.iloc[:2].mean()
            if earlier_avg > 0:
                change = ((recent_avg - earlier_avg) / earlier_avg) * 100
                trend = f"trending {'up' if change > 10 else 'down' if change < -10 else 'flat'} ({change:+.0f}%)"
            else:
                trend = "new usage"
        elif len(complete) >= 2:
            if complete.iloc[0] > 0:
                change = ((complete.iloc[-1] - complete.iloc[0]) / complete.iloc[0]) * 100
                trend = f"{change:+.0f}% change"
            else:
                trend = "new usage"
        else:
            trend = "limited data"
        lines.append(f"- {cat}: {total:,.0f} credits ({trend})")
        top_features = cat_data.groupby("PRIMARY_FEATURE")["CREDITS"].sum().sort_values(ascending=False).head(3)
        for feat, creds in top_features.items():
            lines.append(f"  - {feat}: {creds:,.0f} credits")
    return "\n".join(lines)


def _build_account_context(account_name):
    try:
        base_df = load_accounts_base()
        cap_df = load_capacity_renewals()
    except Exception:
        return ""
    acct = base_df[base_df["ACCOUNT_NAME"] == account_name]
    if acct.empty:
        return ""
    row = acct.iloc[0]
    lines = ["ACCOUNT CONTEXT:"]
    arr = row.get("ARR")
    if pd.notna(arr) and arr > 0:
        lines.append(f"- ARR: ${arr:,.0f}")
    tier = row.get("TIER")
    if pd.notna(tier):
        lines.append(f"- Tier: {tier}")
    industry = row.get("INDUSTRY")
    if pd.notna(industry):
        sub = row.get("SUBINDUSTRY")
        lines.append(f"- Industry: {industry}" + (f" / {sub}" if pd.notna(sub) else ""))
    cap = cap_df[cap_df["ACCOUNT_NAME"] == account_name]
    if not cap.empty:
        cr = cap.iloc[0]
        end_date = cr.get("CONTRACT_END_DATE")
        if pd.notna(end_date):
            lines.append(f"- Contract end: {str(end_date)[:10]}")
        total_cap = cr.get("TOTAL_CAPACITY")
        remaining = cr.get("CAPACITY_REMAINING")
        if pd.notna(total_cap) and pd.notna(remaining) and total_cap > 0:
            pct_used = ((total_cap - remaining) / total_cap) * 100
            lines.append(f"- Capacity: ${total_cap:,.0f} total, ${remaining:,.0f} remaining ({pct_used:.0f}% consumed)")
        overage = cr.get("OVERAGE_UNDERAGE_PREDICTION")
        if pd.notna(overage):
            lines.append(f"- Overage/underage prediction: ${overage:,.0f}")
    return "\n".join(lines) if len(lines) > 1 else ""


def _build_prompt(account_name, ae_name, se_name, district, use_cases_df, se_notes=""):
    uc_details = []
    for _, row in use_cases_df.iterrows():
        parts = [f"- **{row['USE_CASE_NAME']}** | Stage: {row['STAGE']} | EACV: ${row['EACV']:,.0f}"]
        for field, label in [
            ("WORKLOADS", "Workloads"), ("USE_CASE_DESCRIPTION", "Description"),
            ("TECHNICAL_UC", "Technical UC"), ("COMPETITORS", "Competitors"),
            ("INCUMBENT_VENDOR", "Incumbent"), ("IMPLEMENTER", "Implementer"),
            ("NEXT_STEPS", "Next Steps"), ("USE_CASE_RISK", "Risk"),
        ]:
            val = row.get(field)
            if pd.notna(val) and str(val).strip():
                text = str(val)[:300] if field == "USE_CASE_DESCRIPTION" else str(val)[:200]
                parts.append(f"  {label}: {text}")
        se_cmts = _recent_se_comments(row.get("SE_COMMENTS_FULL"), n=3)
        if se_cmts:
            parts.append(f"  SE Comments (latest 3):\n{se_cmts}")
        uc_details.append("\n".join(parts))

    total_eacv = use_cases_df["EACV"].sum()
    offerings_ctx = _build_offerings_context()
    consumption_ctx = _build_consumption_context(account_name)
    account_ctx = _build_account_context(account_name)

    se_notes_section = ""
    if se_notes and se_notes.strip():
        se_notes_section = f"""
ADDITIONAL CONTEXT FROM SE:
{se_notes.strip()}
"""

    return f"""You are a Snowflake Services Delivery (SD) strategist writing an action plan for a Sales Engineer to share with their Account Executive (AE). The AE should be able to read this in 2 minutes and walk away knowing exactly how to bring SD into the conversation to move these deals forward.

This is NOT a rigid offering-matching exercise. Think strategically about what this customer actually needs to get these use cases from pipeline to production. Use your knowledge of Snowflake services capabilities to craft a thoughtful, specific plan.

ACCOUNT: {account_name}
DISTRICT: {district}
AE: {ae_name} | SE: {se_name}
TOTAL PIPELINE EACV: ${total_eacv:,.0f}

{account_ctx}

{consumption_ctx}
{se_notes_section}
USE CASES IN PIPELINE (not yet deployed):
{chr(10).join(uc_details)}

FOR REFERENCE — SD has these types of engagement capabilities (use as inspiration, not as a checklist):
{offerings_ctx}

Write the plan in this format:

## SD Action Plan: {account_name}

### The Story
In 3-4 sentences, tell {ae_name} the narrative: what is this customer trying to accomplish across these use cases, where are they stuck or at risk, and how does bringing SD into the picture change the outcome? Be specific to THEIR use cases — not generic. Factor in their ARR, capacity position, contract timeline, consumption patterns, competitors, and SE commentary to paint a grounded picture.

### What SD Can Do Here
For each meaningful area of engagement (NOT one per offering — group by what makes strategic sense), write a short paragraph that covers:
- Which use case(s) this helps get live
- What SD would actually do (be specific — not just an offering name)
- Why this matters for the deal (speed, risk, competitive, complexity)
- Rough timeline where possible

Keep it to 2-4 areas max. Not every use case needs its own section. Some may not need SD at all — that is fine, skip them.

### How {ae_name} Should Talk About This
3-4 conversational sentences or bullet points the AE can use with the customer. These should sound natural, not salesy. Frame around the customer''s goals, not Snowflake offerings. Reference their actual use cases by name.

### Recommended Play
A short paragraph on the recommended sequence: what to lead with, what to follow up with, and what the entry point should be (e.g., a workshop, a scoping call, attaching to an existing deal, etc.). Factor in the contract timeline and capacity position when recommending urgency.

### Next Steps
3-4 concrete actions with owners (AE, SE, SD).

IMPORTANT GUIDELINES:
- Be strategic, not mechanical. This is a sales tool, not a procurement document.
- Reference use case names and specifics throughout. No generic filler.
- Use the consumption data to ground your recommendations — if they''re heavy on Data Engineering but have no AI/ML usage, that tells a story. If a category is trending up or down, factor that in.
- Use the account context (ARR, capacity, contract end date) to calibrate the size and urgency of your recommendations.
- If SE Comments provide recent context about what''s happening on the ground, use that — it''s the freshest signal.
- If a use case has competitors listed, use that to inform urgency.
- If a use case is early stage, the play might be different than late stage — adjust accordingly.
- If data is sparse for a use case (no description, no workloads), acknowledge the gap and recommend a discovery step rather than guessing.
- Keep the total plan under 600 words. Brevity is power.
- Do NOT just list offerings. Think about what the customer needs to succeed."""


ap_df = load_action_planner_pipeline()

if ap_df.empty:
    st.error("No pipeline data found for EntBayAreaTech1 / EntPacNorthwest districts.")
    st.stop()

ap_col_filters, ap_col_main = st.columns([1, 3])

with ap_col_filters:
    st.markdown("#### Filters")

    ap_districts = sorted(ap_df["DISTRICT"].dropna().unique())
    ap_selected_districts = st.multiselect(
        "District",
        ap_districts,
        default=ap_districts,
        key="ap_district",
    )
    ap_filtered = ap_df[ap_df["DISTRICT"].isin(ap_selected_districts)]

    ap_stage_options = sorted(ap_filtered["STAGE"].dropna().unique())
    ap_pipeline_stages = [s for s in ap_stage_options if s not in ("7 - Deployed", "8 - Use Case Lost", "0 - Not In Pursuit")]
    ap_stage_default = ap_pipeline_stages if ap_pipeline_stages else ap_stage_options
    ap_selected_stages = st.multiselect(
        "Stage",
        ap_stage_options,
        default=ap_stage_default,
        key="ap_stage",
    )
    ap_filtered = ap_filtered[ap_filtered["STAGE"].isin(ap_selected_stages) | ap_filtered["STAGE"].isna()]

    ap_account_names = sorted(ap_filtered["ACCOUNT_NAME"].dropna().unique())
    ap_search = st.text_input("Search accounts", placeholder="Type to filter...", key="ap_search")
    if ap_search:
        ap_account_names = [a for a in ap_account_names if ap_search.lower() in a.lower()]

    st.caption(f"{len(ap_account_names)} accounts | {len(ap_filtered)} use cases")

with ap_col_main:
    if not ap_account_names:
        st.info("No accounts match your filters.")
        st.stop()

    ap_selected_account = st.selectbox(
        "Select account",
        ap_account_names,
        index=None,
        placeholder="Choose an account...",
        key="ap_account",
    )

    if not ap_selected_account:
        ap_summary = (
            ap_filtered.groupby(["ACCOUNT_NAME", "DISTRICT", "AE_NAME"])
            .agg(Pipeline_UCs=("USE_CASE_NAME", lambda x: x.notna().sum()), Total_EACV=("EACV", "sum"))
            .reset_index()
            .sort_values("Pipeline_UCs", ascending=False)
        )
        ap_summary["Total_EACV"] = ap_summary["Total_EACV"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "$0")
        ap_summary.columns = ["Account", "District", "AE", "Pipeline UCs", "Total EACV"]
        st.dataframe(ap_summary, use_container_width=True, hide_index=True, height=min(len(ap_summary) * 35 + 40, 600))
        st.stop()

    ap_account_df = ap_filtered[ap_filtered["ACCOUNT_NAME"] == ap_selected_account].reset_index(drop=True)
    ap_account_df_ucs = ap_account_df[ap_account_df["USE_CASE_NAME"].notna()].reset_index(drop=True)
    ap_ae = ap_account_df["AE_NAME"].iloc[0] if not ap_account_df.empty else "Unknown"
    ap_se = ap_account_df["SE_NAME"].iloc[0] if not ap_account_df.empty else "Unknown"
    ap_district = ap_account_df["DISTRICT"].iloc[0] if not ap_account_df.empty else "Unknown"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AE", ap_ae)
    m2.metric("SE", ap_se)
    m3.metric("Pipeline UCs", len(ap_account_df_ucs))
    m4.metric("Pipeline EACV", f"${ap_account_df_ucs['EACV'].sum():,.0f}")

    if ap_account_df_ucs.empty:
        st.info("No pipeline use cases found for this account. Use cases may be deployed, lost, or not yet created.")
        st.stop()

    st.markdown("##### Select use cases for action plan")

    ap_display = ap_account_df_ucs[["USE_CASE_NAME", "USE_CASE_ID", "USE_CASE_NUMBER", "STAGE", "EACV", "WORKLOADS", "TECHNICAL_UC", "USE_CASE_DESCRIPTION", "NEXT_STEPS", "SE_COMMENTS_FULL"]].copy()
    ap_display["SE_COMMENTS"] = ap_display["SE_COMMENTS_FULL"].apply(_latest_se_comment)
    ap_display["SFDC"] = ap_display.apply(
        lambda r: f"{SFDC_BASE}/{r['USE_CASE_ID']}/view" if pd.notna(r.get("USE_CASE_ID")) else None, axis=1
    )
    ap_display = ap_display[["USE_CASE_NAME", "SFDC", "USE_CASE_ID", "USE_CASE_NUMBER", "STAGE", "EACV", "WORKLOADS", "TECHNICAL_UC", "USE_CASE_DESCRIPTION", "NEXT_STEPS", "SE_COMMENTS", "SE_COMMENTS_FULL"]]
    ap_display["EACV"] = ap_display["EACV"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "$0")

    ap_edited = st.data_editor(
        ap_display.assign(Select=True),
        column_config={
            "USE_CASE_NAME": st.column_config.TextColumn("Use Case", width="large"),
            "SFDC": st.column_config.LinkColumn("SFDC", display_text="Open", width="small"),
            "Select": st.column_config.CheckboxColumn("Select", default=True, width="small"),
            "USE_CASE_ID": None,
            "USE_CASE_NUMBER": None,
            "STAGE": st.column_config.TextColumn("Stage", width="medium"),
            "EACV": st.column_config.TextColumn("EACV", width="small"),
            "WORKLOADS": st.column_config.TextColumn("Workloads", width="medium"),
            "TECHNICAL_UC": st.column_config.TextColumn("Technical UC", width="medium"),
            "USE_CASE_DESCRIPTION": st.column_config.TextColumn("Description", width="large"),
            "NEXT_STEPS": st.column_config.TextColumn("Next Steps", width="medium"),
            "SE_COMMENTS": st.column_config.TextColumn("SE Comments", width="large"),
            "SE_COMMENTS_FULL": None,
        },
        column_order=["USE_CASE_NAME", "SFDC", "Select", "STAGE", "EACV", "WORKLOADS", "TECHNICAL_UC", "USE_CASE_DESCRIPTION", "NEXT_STEPS", "SE_COMMENTS"],
        use_container_width=True,
        hide_index=True,
        disabled=["USE_CASE_NAME", "SFDC", "STAGE", "EACV", "WORKLOADS", "TECHNICAL_UC", "USE_CASE_DESCRIPTION", "NEXT_STEPS", "SE_COMMENTS"],
        key=f"ap_editor_{ap_selected_account}",
    )

    ap_mask = ap_edited["Select"]
    ap_selected_ucs = ap_account_df_ucs.iloc[ap_mask[ap_mask].index]

    se_notes = st.text_area(
        "Additional context (optional — anything not in the data that should inform the plan)",
        placeholder="e.g., 'Just had a call — they're evaluating Databricks for this use case and need a POC by end of Q1'",
        key=f"ap_se_notes_{ap_selected_account}",
        height=80,
    )

    btn_col, model_col, _ = st.columns([1, 1, 2])
    with model_col:
        ap_model = st.selectbox(
            "Model",
            ["claude-3-5-sonnet", "llama3.1-405b", "mistral-large2", "llama3.1-70b", "mixtral-8x7b"],
            index=0,
            key="ap_model",
        )
    with btn_col:
        ap_generate = st.button(
            f"Generate action plan ({len(ap_selected_ucs)} UCs)",
            type="primary",
            disabled=len(ap_selected_ucs) == 0,
            icon=":material/auto_awesome:",
            key="ap_generate",
        )

    plan_key = f"ap_plan_{ap_selected_account}"

    if ap_generate and len(ap_selected_ucs) > 0:
        prompt = _build_prompt(ap_selected_account, ap_ae, ap_se, ap_district, ap_selected_ucs, se_notes=se_notes)
        with st.spinner(f"Generating action plan via Cortex ({ap_model})..."):
            try:
                plan = generate_cortex_response(prompt, model=ap_model)
            except Exception as e:
                plan = f"**Error generating plan:** {str(e)}"
        st.session_state[plan_key] = plan
        st.session_state[f"{plan_key}_model"] = ap_model

    if plan_key in st.session_state:
        stored_plan = st.session_state[plan_key]
        stored_model = st.session_state.get(f"{plan_key}_model", "unknown")
        st.caption(f"Generated with {stored_model}")
        with st.container(border=True):
            st.markdown(stored_plan)

        dl_col, clear_col, _ = st.columns([1, 1, 2])
        with dl_col:
            st.download_button(
                "Download action plan (.md)",
                data=stored_plan,
                file_name=f"SD_Action_Plan_{ap_selected_account.replace(' ', '_').replace(',', '')}.md",
                mime="text/markdown",
                icon=":material/download:",
                key="ap_download",
            )
        with clear_col:
            if st.button("Clear plan", key="ap_clear"):
                del st.session_state[plan_key]
                if f"{plan_key}_model" in st.session_state:
                    del st.session_state[f"{plan_key}_model"]
                st.rerun()
