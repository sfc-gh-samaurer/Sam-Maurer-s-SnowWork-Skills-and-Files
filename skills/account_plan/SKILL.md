---
name: account_plan
description: >
  Generate comprehensive 8-tab HTML account plans combining use case data
  with company intelligence and AI-powered recommendations.
  Supports HTML report and Markdown output without Google Doc export.
  Trigger when users ask for "generate account plan for [account]",
  "create account plan for [account]", or "account plan for [account]".
created_date: 2026-03-13
last_updated: 2026-03-13
owner_name: Tess Tao
version: 1.0.0
---

# Account Plan

Generate comprehensive 8-tab HTML account plans combining use case data with company intelligence and AI-powered recommendations.

## When to Use
- "generate account plan for [account]"
- "create account plan for [account]"
- "account plan for [account]"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| account_id or account_name | Yes | Salesforce Account ID or company name |
| output_format | No | `html` (default), `md` (fastest), or `both` |

## Output
- **HTML report** (default): `~/Desktop/account-plans/{Account_Name}_Account_Plan.html` — opened in browser via local HTTP server
- **Markdown file**: `~/Desktop/account-plans/{Account_Name}_Account_Plan.md` — plain text version, also displayed in the response
- **Both**: HTML report + Markdown file

---

## Execution

### STEP 1: Find Account (account-finder)

Use the `account-finder` (`skills/account-finder/SKILL.md`) skill to resolve the company name to a Salesforce account.

This returns:
- `account_id`, `account_name`
- `IS_CAPACITY_CUSTOMER` (true/false)
- Account team: AE (owner), SE, DM, RVP
- Segment, industry, sub-industry
- Contract status metadata

If multiple matches, `account-finder` will ask the user to confirm.

Store `account_id` and `account_name` for all subsequent steps. Store the account team info for Tab 7 (Account Team Assignments).

**If `IS_CAPACITY_CUSTOMER` is false**, stop and tell the user: "Account plans require use case data that is only available for capacity (customer) accounts. For prospect accounts, try the `prospect_research` skill instead." Do not proceed to Step 1B or beyond.

### STEP 1B: Choose Output Format & Location

Ask the user which output format they want:

| Option | Description |
|--------|-------------|
| **HTML report** (default) | Generate the 8-tab HTML report and open in browser (~3–5 min) |
| **Markdown file** (fastest) | Generate a markdown file and display the full text in the response |
| **Both** | Generate both HTML report and Markdown file |

Also confirm the output directory. Default is `~/Desktop/account-plans/` — ask the user if this works or if they'd prefer a different location.

**Default behavior:** If the user doesn't respond, skips the question, or doesn't express a preference, **generate the HTML report to the default directory**. Do not wait indefinitely — proceed with defaults after a reasonable pause.

Store the choice as `OUTPUT_FORMAT` (`html`, `md`, or `both`) and `OUTPUT_DIR` for use in later steps.

**Important:** Do not use subagents to generate outputs. Subagents start with a fresh context and do not carry over the account data, use case results, and company research collected in earlier steps — leading to incomplete reports or redundant data re-fetching.

**If `OUTPUT_FORMAT` is `both`:** Generate the HTML report and the Markdown file in parallel using parallel tool calls in a single response, since both outputs use the same collected data and have no dependency on each other.

### STEP 2: Collect Use Case Data

```sql
SELECT 
    uc.ACCOUNT_NAME, uc.SALESFORCE_ACCOUNT_ID, uc.USE_CASE_ID, uc.USE_CASE_NUMBER, uc.USE_CASE_NAME,
    uc.USE_CASE_ACV, uc.USE_CASE_STAGE, uc.DECISION_DATE,
    uc.MEDDPICC_CHAMPION as uc_champion_id,
    uc.MEDDPICC_CHAMPION_NAME as uc_champion,
    uc.USE_CASE_LEAD_SE_ID as uc_se_owner,
    uc.USE_CASE_COMMENTS, uc.NEXT_STEPS, uc.USE_CASE_RISK_LEVEL, uc.RISK_DESCRIPTION,
    uc.LAST_MODIFIED_DATE, uc.CREATED_DATE,
    uc.WORKLOADS, uc.USE_CASE_STATUS,
    uc.TECHNICAL_WIN, uc.TECHNICAL_WIN_DATE,
    uc.MEDDPICC_ECONOMIC_BUYER as uc_economic_buyer_id, uc.MEDDPICC_ECONOMIC_BUYER_NAME as uc_economic_buyer,
    uc.MEDDPICC_IDENTIFY_PAIN, uc.MEDDPICC_METRICS,
    uc.MEDDPICC_DECISION_CRITERIA, uc.MEDDPICC_DECISION_PROCESS,
    uc.MEDDPICC_OVERALL_SCORE,
    uc.MEDDPICC_CHAMPION_SCORE, uc.MEDDPICC_METRICS_SCORE,
    uc.MEDDPICC_ECONOMIC_BUYER_SCORE, uc.MEDDPICC_DECISION_CRITERIA_SCORE,
    uc.MEDDPICC_DECISION_PROCESS_SCORE, uc.MEDDPICC_IDENTIFY_PAIN_SCORE,
    uc.MEDDPICC_COMPETITOR_SCORE,
    uc.COMPETITORS, uc.INCUMBENT_VENDOR,
    uc.POC_STAGE, uc.POC_DECISION, uc.POC_START_DATE, uc.POC_END_DATE,
    uc.DAYS_IN_STAGE, uc.USE_CASE_DESCRIPTION,
    uc.OWNER_NAME,
    chg.change_type, chg.uc_stage_change, chg.uc_acv_change, chg.uc_decision_date_change
FROM sales.raven.sda_use_case_view uc
LEFT JOIN (
    SELECT USE_CASE_NUMBER,
        MOVEMENT_DETAIL as change_type,
        CASE WHEN ENTERED_STAGE != EXIT_STAGE THEN ENTERED_STAGE || ' → ' || EXIT_STAGE END as uc_stage_change,
        CASE WHEN ENTERED_EACV != EXIT_EACV THEN EXIT_EACV - ENTERED_EACV END as uc_acv_change,
        CASE WHEN ENTERED_DECISION_DATE != EXIT_DECISION_DATE
            THEN TO_VARCHAR(ENTERED_DECISION_DATE) || ' → ' || TO_VARCHAR(EXIT_DECISION_DATE) END as uc_decision_date_change
    FROM sales.raven.sda_use_case_movement_view
    WHERE SALESFORCE_ACCOUNT_ID = '{ACCOUNT_ID}'
        AND SNAPSHOT_TYPE = 'WEEKLY'
    QUALIFY ROW_NUMBER() OVER (PARTITION BY USE_CASE_NUMBER ORDER BY EXIT_SNAPSHOT_DATE DESC) = 1
) chg ON uc.USE_CASE_NUMBER = chg.USE_CASE_NUMBER
WHERE uc.SALESFORCE_ACCOUNT_ID = '{ACCOUNT_ID}'
ORDER BY uc.LAST_MODIFIED_DATE DESC LIMIT 200
```

Note: Filter by `SALESFORCE_ACCOUNT_ID` (from account-finder), not `account_name` string match. The `uc_se_owner` returns an SE ID (not name) — resolve via account-finder's SE name if needed. **Important:** `uc_champion` and `uc_economic_buyer` are the display names. The `_id` columns are Salesforce Contact IDs — do not display those to users.

### STEP 2A: Pre-Computed Stats (run in parallel with Step 2)

```sql
SELECT 
    USE_CASE_STATUS,
    USE_CASE_STAGE,
    COUNT(*) as UC_COUNT,
    ROUND(SUM(USE_CASE_ACV), 0) as TOTAL_ACV
FROM sales.raven.sda_use_case_view
WHERE SALESFORCE_ACCOUNT_ID = '{ACCOUNT_ID}'
GROUP BY USE_CASE_STATUS, USE_CASE_STAGE
ORDER BY USE_CASE_STAGE
```

**CRITICAL: Use these exact query results for all stat cards and header numbers. Do NOT manually count or sum rows from Step 2.**

Map the results to template variables as follows:

| Template Variable | Source |
|---|---|
| `{{DEPLOYED_COUNT}}` | `SUM(UC_COUNT)` where `USE_CASE_STATUS = 'Production'` |
| `{{DEPLOYED_ACV}}` | `SUM(TOTAL_ACV)` where `USE_CASE_STATUS = 'Production'` |
| `{{IMPLEMENTATION_COUNT}}` | `SUM(UC_COUNT)` where `USE_CASE_STATUS = 'Implementation'` |
| `{{IMPLEMENTATION_ACV}}` | `SUM(TOTAL_ACV)` where `USE_CASE_STATUS = 'Implementation'` |
| `{{VALIDATION_COUNT}}` | `SUM(UC_COUNT)` where `USE_CASE_STAGE` IN ('2 - Scoping', '3 - Technical / Business Validation') |
| `{{VALIDATION_SCOPING_ACV}}` | `SUM(TOTAL_ACV)` for same stages |
| `{{DISCOVERY_COUNT}}` | `SUM(UC_COUNT)` where `USE_CASE_STAGE = '1 - Discovery'` |
| `{{DISCOVERY_ACV}}` | `SUM(TOTAL_ACV)` where `USE_CASE_STAGE = '1 - Discovery'` |
| `{{TOTAL_USE_CASES}}` | `SUM(UC_COUNT)` across all rows |
| `{{TOTAL_ACV}}` | `SUM(TOTAL_ACV)` across all rows |

### STEP 2B: Contact Intelligence (parallel with Step 2 — optional)

Run these two queries **in parallel with the use case query above**. These use the same `SALES_RAVEN_RO_RL` role. If either query fails, proceed without contact-intelligence data — Tab 2 will render from use case data alone.

#### 2B-i. High-Value Contacts
```sql
SELECT
    ci.contact_intelligence_type, ci.person_id, ci.name, ci.email, ci.title,
    ci.phone, ci.department, ci.role, ci.seniority, ci.status, ci.sub_status,
    ci.sla_status, ci.new_icp, ci.interesting_moment_date, ci.interesting_moment_desc,
    ci.account_name
FROM sales.raven.contact_intelligence_view ci
WHERE ci.salesforce_account_id = '{ACCOUNT_ID}'
ORDER BY CASE ci.contact_intelligence_type
    WHEN 'Quality Contact' THEN 1 WHEN 'Recent MQL' THEN 2
    WHEN 'Recently Engaged' THEN 3 WHEN 'Email Contact' THEN 4 ELSE 5 END
LIMIT 50
```

#### 2B-ii. Contact Engagement Velocity
```sql
SELECT
    ci.person_id, ci.name, ci.email, ci.title, ci.phone,
    ci.seniority, ci.department, ci.new_icp, ci.status,
    COUNT(CASE WHEN ci.interesting_moment_date >= CURRENT_DATE() - 30 THEN 1 END) AS touches_last_30d,
    COUNT(CASE WHEN ci.interesting_moment_date >= CURRENT_DATE() - 60 THEN 1 END) AS touches_last_60d,
    MAX(ci.interesting_moment_date) AS most_recent_touch,
    LISTAGG(DISTINCT ci.interesting_moment_type, ', ') WITHIN GROUP (ORDER BY ci.interesting_moment_type) AS touch_types
FROM sales.raven.contact_intelligence_view ci
WHERE ci.salesforce_account_id = '{ACCOUNT_ID}'
    AND ci.interesting_moment_date >= CURRENT_DATE() - 60
    AND ci.interesting_moment_source != 'Sumble'
GROUP BY ci.person_id, ci.name, ci.email, ci.title, ci.phone, ci.seniority, ci.department, ci.new_icp, ci.status
HAVING touches_last_30d >= 2
ORDER BY touches_last_30d DESC, most_recent_touch DESC
```

**Cross-referencing logic for Tab 2:**
- Match contact-intelligence records to use case champions by **name** (fuzzy match on `ci.name` vs `uc_champion`).
- When a match is found, enrich the stakeholder card with: `email`, `phone`, `title`, `seniority`, `department`, `new_icp`, and engagement velocity (`touches_last_30d`).
- High-velocity contacts (from 2B-ii) who do NOT match any use case champion are flagged as **emerging contacts** and included in the Technical Champions grid with a velocity badge.
- Engagement dots become more data-driven: combine use case activity recency with marketing engagement velocity when both are available.

### STEP 3: AI Use Case Analysis (inline LLM)

After collecting use case data from Step 2, analyze each use case by prompting the LLM with the raw data to produce structured AI analysis.

For each use case (or batch all use cases into a single prompt for efficiency), provide the following fields as context and request a structured analysis:

**Input per use case:**
- `USE_CASE_NAME`, `USE_CASE_STAGE`, `USE_CASE_ACV`, `DAYS_IN_STAGE`
- `USE_CASE_COMMENTS` (SE comments), `NEXT_STEPS`
- `USE_CASE_RISK_LEVEL`, `RISK_DESCRIPTION`
- `MEDDPICC_OVERALL_SCORE` + component scores (Champion, Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Competitor)
- `MEDDPICC_CHAMPION`, `MEDDPICC_ECONOMIC_BUYER`
- `COMPETITORS`, `INCUMBENT_VENDOR`
- `TECHNICAL_WIN`, `POC_STAGE`, `POC_DECISION`
- `USE_CASE_DESCRIPTION`

**Prompt instruction:**

> You are a Snowflake sales engineering analyst. For each use case below, produce a structured JSON analysis. Base your assessment on the data provided — do not fabricate information. Use the MEDDPICC scores, risk fields, SE comments, and stage progression to inform your analysis.
>
> For each use case, return:
> ```json
> {
>   "use_case_id": "<USE_CASE_ID>",
>   "overall_score": <0-100 integer>,
>   "summary": "<1-2 sentence health summary>",
>   "se_notes_summary": "<synthesized summary of SE comments and next steps>",
>   "use_case_health": { "score": <0-100>, "analysis": "<brief reasoning>" },
>   "meddpicc_analysis": { "score": <use MEDDPICC_OVERALL_SCORE from data>, "analysis": "<brief assessment of MEDDPICC gaps>" },
>   "blocking_questions": ["<question 1>", "<question 2>"],
>   "actionable_next_steps": ["<action 1>", "<action 2>"]
> }
> ```
>
> Scoring guidelines:
> - `overall_score`: Weight MEDDPICC (40%), stage progression health (20%), risk level (20%), SE engagement recency (20%). Score 80+ = excellent, 60-79 = good, 40-59 = moderate, <40 = poor.
> - `blocking_questions`: Identify 2-4 unresolved questions that could stall the deal. Derive from: missing MEDDPICC fields, high risk descriptions, stalled stage, competitive threats.
> - `actionable_next_steps`: Recommend 2-4 concrete actions for the SE/AE. Derive from: current stage needs, MEDDPICC gaps, next steps field, competitive positioning.
> - `se_notes_summary`: Synthesize the SE comments and next steps into a concise summary. If no comments exist, note "No SE comments recorded."
> - `meddpicc_analysis.score`: Use the actual `MEDDPICC_OVERALL_SCORE` from the data (do not recalculate).

The output feeds directly into Tabs 4 (Pipeline Coverage), 5 (Use Case Health), 6 (Risks & Gaps), and 7 (Next Actions). The data shape matches exactly what the HTML templates expect.

### STEP 4: Company Intelligence (parallel)

Run ALL of the following in parallel:

#### 4a. Firmographics — GET_3P_DATA
```sql
SELECT * FROM TABLE(SALES.RAVEN.GET_3P_DATA('{ACCOUNT_ID}'))
```
Extracts: industry, annual revenue, employee count, key products, tech stack, website domain, market cap, headquarters.

Use the `website_domain` from this result to disambiguate web searches below (e.g., append domain to search queries for accuracy).

#### 4b. Web Search — Company Profile
```
web_search("{ACCOUNT_NAME} company profile products services {INDUSTRY}")
```
Provides: company description, product portfolio, market positioning.

#### 4c. Web Search — Strategic Priorities
```
web_search("{ACCOUNT_NAME} strategic priorities CEO annual report investor day {YEAR}")
```
Provides: board-level priorities, executive quotes, strategic themes for the current fiscal year.

#### 4d. Web Search — Recent News & Competitive Landscape
```
web_search("{ACCOUNT_NAME} recent news AI data cloud competitors {CURRENT_QUARTER} {YEAR}")
```
Provides: recent developments, AI/data strategy signals, competitive moves, market news.

#### Web Fetch Guardrail

**CRITICAL — Try NOT use `web_fetch` in this skill.** Rely exclusively on `web_search` result snippets for all company intelligence. The snippets returned by `web_search` provide sufficient context for populating the report.

**Rules:**
1. **NEVER use `web_fetch` on competitor domains under any circumstances.** Competitors include but are not limited to: Databricks, Amazon Redshift, ClickHouse, Firebolt, Google BigQuery, Google (Platform), Microsoft Fabric / Azure Synapse, Oracle, Teradata, IBM, Cloudera, Vertica, Dremio, Starburst, Palantir, Greenplum, Yellowbrick, Exasol, Actian, Microfocus (OpenText), SAP, Fivetran, dbt Labs, or any other data/cloud/AI vendor that competes with Snowflake. This is a strict compliance requirement.
2. If a `web_search` snippet is too brief, run a more targeted `web_search` query instead of fetching the page.

### STEP 4B: Moonshot Recommendations

#### 4B-i. Cached Brief Lookup (fast — try first)

Check if a recent workflow brief already contains use case recommendations for this account. This avoids the slow SP call (~30s) when a pre-generated brief exists.

```sql
SELECT 
    f.value:header::STRING AS recommendation_header,
    f.value:summary::STRING AS recommendation_summary,
    f.value:details[0]:content::STRING AS recommendation_content
FROM SALES.RAVEN.WORKFLOW_EXECUTIONS,
    LATERAL FLATTEN(input => RESPONSE_PAYLOAD:payload) f
WHERE WORKFLOW_ID LIKE '%BRIEF'
  AND INPUTS:account_id::STRING = '{ACCOUNT_ID}'
  AND STATUS = 'COMPLETED'
  AND f.value:header::STRING IN ('Use Case Recommendations', 'Potential Snowflake Value Proposition')
  AND DATEDIFF('day', TRY_TO_TIMESTAMP(REPLACE(COMPLETED_AT::STRING, '"', '')), CURRENT_TIMESTAMP()) <= 30
ORDER BY COMPLETED_AT DESC
LIMIT 1;
```

- `recommendation_summary` = one-paragraph value proposition
- `recommendation_content` = full markdown with use case descriptions, reference customers, relevance, partners

**If a row is returned:** Use `recommendation_summary` and `recommendation_content` directly to populate Tab 8 Moonshot Idea cards. **Skip the SP call below.**

**If no rows returned** (no brief in last 30 days): Fall back to 4B-ii below.

#### 4B-ii. Use Case Recommender SP (fallback — slow)

**Only call this if Step 4B-i returned no results.**

**CRITICAL — Read carefully before executing:**

This is a **stored procedure** (CALL), NOT a table function. Do NOT use `SELECT ... FROM TABLE(...)` syntax — that will fail with "Unknown user-defined table function."

**Execution — single compound statement (do NOT split into separate queries):**
```sql
CALL SALES.RAVEN.RECO_FOR_PROSPECTING_SP_SALES(
    '{ACCOUNT_ID}',
    '{COMPANY_PROFILE}',
    '{NEWS_CONTEXT}'
);
SELECT $1 AS full_output FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
```

Run both statements in a **single** `snowflake_sql_execute` call (semicolon-separated). This is critical because:
- The SP returns large JSON (8-15KB) that gets truncated at ~4KB on a bare CALL display.
- `RESULT_SCAN(LAST_QUERY_ID())` expires quickly — splitting into separate calls will fail with "Statement not found."
- **Never call the SP twice.** If output still looks truncated, use whatever you have. Re-calling wastes ~30s and output may differ.

**Inputs:**
- `{COMPANY_PROFILE}` = summary synthesized from GET_3P_DATA + web search results (4b) — **keep under 500 chars** (trim to key facts: industry, revenue, products, tech stack)
- `{NEWS_CONTEXT}` = recent news from web search (4d) — **keep under 500 chars** (2-3 headline facts)

This returns industry-matched use case recommendations with:
- Curated Industry Team use cases (description, benefits, reference customers, partners)
- Similarity-matched customer stories (real metrics, challenges, goals, Snowflake usage, results)

Use these to generate the Moonshot Idea cards (categories: Risk Reduction, New Revenue, Operational Efficiency).

#### 4B-iii. Industry Comparison (supplementary — for the Industry Comparison Table only)
```sql
SELECT 
    uc.ACCOUNT_NAME,
    uc.USE_CASE_NAME,
    uc.WORKLOADS,
    uc.USE_CASE_ACV,
    uc.USE_CASE_STAGE
FROM sales.raven.sda_use_case_view uc
WHERE uc.USE_CASE_STAGE = '7 - Deployed'
  AND uc.USE_CASE_ACV > 100000
  AND uc.SALESFORCE_ACCOUNT_ID != '{ACCOUNT_ID}'
  AND (
    LOWER(uc.WORKLOADS) LIKE '%ai%' OR
    LOWER(uc.WORKLOADS) LIKE '%cortex%' OR
    LOWER(uc.WORKLOADS) LIKE '%ml%' OR
    LOWER(uc.WORKLOADS) LIKE '%data engineering%'
  )
ORDER BY uc.USE_CASE_ACV DESC
LIMIT 30
```
This feeds ONLY the Industry Comparison Table at the bottom of Tab 8 (account name, UC name, workloads, ACV columns). Note: `uc_technical_campaign` is not available in `sda_use_case_view` — filter on `WORKLOADS` only.

### STEP 5: Generate HTML Report

*Skip this step if `OUTPUT_FORMAT` is `md`.*

Write the HTML to `{OUTPUT_DIR}/{Account_Name}_Account_Plan.html`. Create the directory if it doesn't exist:

```bash
mkdir -p {OUTPUT_DIR}
```

See **templates/DESIGN.md** for complete CSS and HTML templates. Must match Block report structure exactly.

### STEP 6: Open Report in Browser

*Skip this step if `OUTPUT_FORMAT` is `md`.*

Start a local HTTP server and open the report in the application's browser:

```bash
# Start HTTP server in the directory containing the HTML file (run in background)
cd {OUTPUT_DIR} && python3 -m http.server 8765
```

```
# Open in application browser
open_browser: http://localhost:8765/{Account_Name}_Account_Plan.html
```

Note: The application's browser does not support file:// URLs directly, so a local HTTP server is required.

### STEP 7: Generate Markdown File

*Skip this step if `OUTPUT_FORMAT` is `html`.*

Generate a **clean, readable markdown document** with the account plan content. This is a plain-text version structured for easy reading and sharing.

#### Create output directory

```bash
mkdir -p {OUTPUT_DIR}
```

#### Required structure — 8 sections as H2 headings:

```markdown
## Executive Overview
[Company overview paragraph, health summary, stat highlights]
[Key metrics table: Deployed | Implementation | Validation | Discovery counts]
[Relationship Summary: Strengths, Opportunities, Risks]

## Stakeholder Map
[Executive Leadership table: Name | Title | Engagement Level | Notes]
[Technical Champions table: Name | Title | Department | Engagement Level]
[Business Unit coverage summary]
[Engagement gaps and priorities]

## Strategic Execution
[Strategic Alignment table: Priority | Status | Coverage | Verdict]
[Strategy cards with alignment details]
[Competitive Intelligence summary]

## Pipeline Coverage
[ACV summary by stage table]
[Pipeline details: UC name, stage, ACV, champion, AI next steps]
[Pipeline Gap Analysis]

## Use Case Health
[AI-Surfaced Blocking Questions by UC]
[Critical Risks with analysis]
[Competitive Threat Assessment]

## Risks & Gaps
[Risk summary with severity]
[Product gaps: Blocking | Impacting | Resolved]
[Mitigation strategies]

## Next Actions
[Priority 1 actions (30 days) with owners]
[Priority 2 actions (30-60 days)]
[Priority 3 actions (60-90 days)]
[Account Team Assignments table: Role | Name]

## Moonshot Ideas
[Category sections: Risk Reduction, New Revenue, Operational Efficiency]
[Each idea: title, description, strategic alignment, customer example, estimated impact]
[Industry Comparison table]
```

Use the **same data** already gathered in Steps 1–4. Format tables as markdown tables, use bold for emphasis, use bullet lists for items. The content should be professional and readable — not raw data dumps.

**Important:** Do not include internal data source names, function names, or technical references in the markdown content (e.g., do not write "GET_3P_DATA", "web_search", "account-finder", "sales.raven.*", "RECO_FOR_PROSPECTING_SP_SALES", etc.). The document is meant for sharing — present the data as plain business content without attribution to internal tools.

#### Write file and display content

Write the markdown to `{OUTPUT_DIR}/{Account_Name}_Account_Plan.md`.

**After writing the file, display the full markdown content in the response** so the user can read the account plan directly without opening the file. This applies to both `md` and `both` output formats — always show the markdown in the chat. Present it as:

> Your account plan has been saved to `{OUTPUT_DIR}/{Account_Name}_Account_Plan.md`
>
> [full markdown content displayed here]

---

## Role & Permissions

Before running queries, set the role:
1. Try `USE ROLE SALES_RAVEN_RO_RL` — required for `GET_3P_DATA()`, `RECO_FOR_PROSPECTING_SP_SALES()`, and all `sales.raven.*` views
2. If unavailable, fall back to `USE ROLE SALES_BASIC_RO`

---

## 8 Tabs (Required Structure)

### Tab 1: Executive Overview
- Summary banner with health assessment (from use case stage counts + AI scores)
- 4-column stat grid: Deployed / Implementation / Validation / Discovery use case counts — **use exact numbers from Step 2A**
- 2-column layout:
  - **Company Overview table** — populated from `GET_3P_DATA()`: Industry, Annual Revenue, Employees, Key Products, Market Cap
  - **Strategic Priorities** — populated from web search (Step 4c), with executive quote block if found
- Relationship Summary: Strengths / Opportunities / Risks (3-column, LLM-synthesized from all data)

### Tab 2: Stakeholder Map
- Summary banner with engagement strategy
- Executive Leadership grid (3-column) with **5-dot engagement scale** — from use case MEDDPICC economic_buyer fields + web search executive research. When contact-intelligence match exists, enrich with email, phone, title, seniority.
- Technical Champions grid (4-column) with engagement dots — from use case MEDDPICC champion fields, enriched with contact-intelligence data (email, department, ICP status) when name match found. High-velocity contacts from Step 2B-ii not in use case data are added as emerging contacts with a velocity badge.
- **Business Unit Engagement Map** with **stakeholder chips** (engaged/partial/gap) — synthesized from use case org coverage. Contact-intelligence department data used to validate/fill coverage gaps.
- Engagement Gaps with priority indicators — engagement dots incorporate marketing engagement velocity from contact-intelligence (Step 2B-ii `touches_last_30d`) when available, combined with use case activity recency

### Tab 3: Strategic Execution
- Summary banner with strategic vision
- **Strategic Alignment Table** (Priority | Status | Coverage | Verdict) — priorities from web search (Step 4c), coverage from use case workloads/campaigns
- 4-column summary stats
- **Strategy Cards** with **alignment score bars** (percentage fill) — alignment of UC coverage to each priority
- AT RISK deep dive cards with target stakeholders and positioning
- Competitive Intelligence grid (3-column) — from web search (Step 4d) + `GET_3P_DATA()` tech stack

### Tab 4: Pipeline Coverage
- 4-column ACV stats by stage — **use exact numbers from Step 2A**
- **Metadata Panel** (collapsible, data sources)
- **Pipeline Cards** with:
  - Stage badge + AI score badge (use case data + ai_analysis)
  - UC name
  - ACV value + Champion (use case)
  - **SE notes box** (purple border) — from ai_analysis.se_notes_summary
  - **Blocking questions box** (red border) — from ai_analysis.blocking_questions
  - AI Next Steps pitch box — from ai_analysis.actionable_next_steps
- Emerging Opportunities grid
- Pipeline Gap Analysis table

### Tab 5: Use Case Health
- Metadata Panel
- Summary banner with AI risk factors
- **AI-Surfaced Blocking Questions** (2-column grid by UC) — from ai_analysis.blocking_questions
- Critical Risks with AI Analysis boxes — from uc_risk_level + ai_analysis
- Engagement Gaps
- Competitive Threat Assessment table
- Product Gap Impact (Blocking/Impacting/Resolved 3-column)

### Tab 6: Risks & Gaps
Same structure as Tab 5.

### Tab 7: Next Actions
- Metadata Panel (AI/use case/account-finder sources)
- Summary banner with focus areas
- **Priority 1** actions (P1 badge, 30 days) with AI-Generated Action boxes — from ai_analysis.actionable_next_steps
- **Priority 2** actions (P2 badge, 30-60 days)
- **Priority 3** actions (P3 badge, 60-90 days)
- **Account Team Assignments table** — populated from `account-finder` metadata:
  - Account Executive: AE name from account-finder
  - Solution Engineer: SE name from account-finder
  - District Manager: DM from account-finder
  - Regional VP: RVP from account-finder

### Tab 8: Moonshot Ideas
- Summary banner with strategic innovation context
- **Metadata Panel** showing data sources: Web Research + 3P Data, Use Case Recommender, Industry Comparisons
- **Category Sections** (up to 10 ideas across 3 categories):
  - Risk Reduction — ideas that reduce operational, compliance, or technology risk
  - New Revenue Streams — ideas that enable data monetization or new business models
  - Operational Efficiency — ideas that save time, reduce costs, or improve productivity
- **Moonshot Cards** (generated from cached brief recommendations OR `RECO_FOR_PROSPECTING_SP_SALES()` fallback):
  - Category badge (risk-reduction/revenue/efficiency)
  - Idea title and description
  - **Strategic Alignment** to company priorities (from web search) — cyan box
  - **Customer Success Example** box (teal border) — from SP's reference customers with real metrics
  - **Customer Value** box (green border) — business outcome/value statement
  - **Estimated Impact** (ACV potential, time savings, risk mitigation)
  - **Key Stakeholders** to engage (from use case MEDDPICC + web search executives)
  - **Relevance Score** (High/Medium based on SP match quality)
- **Industry Comparison Table** — from Step 4B-iii query (account_name, UC name, workloads, ACV, relevance)

---

## Data Source Summary

| Source | What It Provides | Steps |
|--------|-----------------|-------|
| `account-finder` skill | Account resolution, team (AE/SE/DM/RVP), segment, industry | 1 |
| `sales.raven.sda_use_case_view` | All use case detail (stage, ACV, MEDDPICC scores + fields, SE comments, risk, workloads, competitors, POC status) | 2, 4B-iii |
| Inline LLM analysis (Step 3) | AI health scores, blocking questions, next steps, SE notes summaries — generated at runtime from use case data | 3 |
| `sales.raven.sda_use_case_movement_view` | Weekly UC movement tracking (stage changes, ACV changes, decision date changes) | 2 |
| `SALES.RAVEN.GET_3P_DATA()` | Firmographics (industry, revenue, employees, tech stack, website) | 4a |
| `sales.raven.contact_intelligence_view` | Contact details (email, phone, title, seniority, department), ICP scoring, engagement velocity, marketing signals | 2B |
| `web_search` (3 parallel calls) | Company profile, strategic priorities, recent news/competitors | 4b, 4c, 4d |
| `SALES.RAVEN.WORKFLOW_EXECUTIONS` (cached brief) | Pre-generated use case recommendations / value propositions from workflow briefs | 4B-i |
| `SALES.RAVEN.RECO_FOR_PROSPECTING_SP_SALES()` | Industry-matched use case recommendations with customer stories (fallback if no cached brief) | 4B-ii |

---

## Key Components to Match Block Report

| Component | CSS Class | Usage |
|-----------|-----------|-------|
| Engagement dots | `.engagement-dot.active` | 5-dot scale for stakeholder engagement |
| Stakeholder chips | `.stakeholder-chip.engaged/.partial/.gap` | Business unit engagement map |
| Alignment bars | `.alignment-bar` + `.alignment-fill` | Strategy cards with % |
| SE notes box | `.se-notes-box` | Purple border, AI summaries |
| Blocking questions | `.blocking-questions` | Red border, blocker lists |
| Pipeline value | `.pipeline-value` | Large ACV display |
| AI score badge | `.ai-score.excellent/.good/.moderate/.poor` | Health indicators |
| Risk indicator | `.risk-indicator.high/.medium/.low` | Threat levels |
| Action priority | `.action-priority.p1/.p2/.p3` | Priority badges |
| Metadata panel | `.metadata-panel` | Collapsible data sources |
| Source icons | `.source-icon.uc-data/.ai/.web/.3p/.contacts` | Data transparency |
| Moonshot category | `.moonshot-category.risk/.revenue/.efficiency` | Category badges |
| Customer success box | `.customer-success-box` | Teal border, success examples |
| Customer value box | `.customer-value-box` | Green border, business outcome statements |
| Impact estimate | `.impact-estimate` | Potential value display |
| Contact detail | `.contact-detail` | Email/phone/seniority on enriched stakeholder cards |
| Velocity badge | `.velocity-badge` | Marketing engagement velocity indicator (e.g., "5 touches/30d") |

---
## Reference
See **templates/DESIGN.md** for complete CSS and HTML templates
