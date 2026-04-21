---
name: account_summarization
description: >
  Generate a comprehensive capacity customer brief. Resolves accounts via
  account_finder, runs 11 parallel SQL queries against sales.raven.* views,
  invokes company research and value proposition SP, and synthesizes into
  a 10-section brief. Trigger when users ask for "account summary for [company]",
  "brief me on [customer]", "how is [account] doing?", or when prospect_research
  detects a capacity customer.
created_date: 2026-02-26
last_updated: 2026-03-13
owner_name: Tess Tao
version: 1.1.0
---

## When to Use
- "Account summary for [company]"
- "Brief me on [customer]"
- "How is [account] doing?"
- "Contract status for [company]"
- "Consumption trends for [account]"
- "Pipeline for [company]"
- Called by `prospect_research` when it detects a capacity customer

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| account_id or account_name | Yes | Salesforce Account ID or company name |
| pre_resolved_account | No | If called from another skill (e.g., prospect_research) that already ran account_finder, the full account info may be passed directly. Skip Step 1 if provided. |
| persona | No | AE \| SE \| DM -- adjusts tone and emphasis (default: AE) |
| focus | No | "value prop", "research", "contacts", "everything" (default) |
| personal_twist | No | Custom angle passed to value proposition |

## Workflow

### Step 0: Permission Preflight Check

Try the primary role first, then fall back to backup:

```sql
USE ROLE SALES_RAVEN_RO_RL;
```

- **If it succeeds**: Proceed.
- **If it fails**: Try the backup role:

```sql
USE ROLE SALES_BASIC_RO;
```

- **If backup succeeds**: Proceed (all queries work with this role too).
- **If both fail**: Stop and tell the user they need either the `SALES_RAVEN_RO_RL` or `SALES_BASIC_RO` role.

### Step 1: Resolve Account via account_finder

**Skip this step if the caller already provides a resolved `account_id` and `IS_CAPACITY_CUSTOMER` flag.**

If only a company name is provided, invoke the `account_finder` skill:

```
skill account_finder
```

The skill will search `sales.raven.d_salesforce_account_customers`, handle disambiguation, and return full account metadata including `SALESFORCE_ACCOUNT_ID` and `IS_CAPACITY_CUSTOMER`.

**IMPORTANT:** If `IS_CAPACITY_CUSTOMER = false`, inform the user that this account is not a capacity customer and offer to run `prospect_research` instead.

### Step 2: Present Plan and Confirm

Use `ask_user_question` to present the capacity customer brief plan with clearly labeled speed tiers:

```
questions:
  - header: "Brief Type"
    question: "[Account Name] is an EXISTING CAPACITY CUSTOMER (owned by [SALESFORCE_OWNER_NAME], SE: [LEAD_SALES_ENGINEER_NAME]).\n\nChoose a brief type:"
    multiSelect: false
    options:
      - label: "Full Brief (~5 min)"
        description: "Complete 10-section brief: Snowflake data + company research + news + contacts + AI use case recommendations. Most comprehensive but slowest."
      - label: "Quick Brief (~1-2 min)"
        description: "Snowflake data + company research + news + firmographics. Uses cached use case recommendations instead of regenerating. No contacts."
      - label: "Account Data Only (~30s)"
        description: "Raw account summary tables — contract, pipeline, support, consumption. No synthesis or formatting."
```

**Wait for user confirmation before proceeding.**

#### Route by Brief Type

- **"Full Brief"** → Proceed to Step 3 (full workflow).
- **"Quick Brief"** → Proceed to Step 3-Quick (quick workflow).
- **"Account Data Only"** → Proceed to Step 3-Raw (raw data workflow).

### Step 3: Fetch All Data (Full Brief)

**This step is for the "Full Brief" option only.** For "Quick Brief" see Step 3-Quick. For "Account Data Only" see Step 3-Raw.

Execute data gathering in dependency order. Run the following **in parallel**:

#### 3A: Account Summary Queries (11 queries)

Run ALL 11 queries in a single response using `snowflake_sql_execute`.

##### Query 1: Contract Status
```sql
SELECT
    c.salesforce_account_name,
    c.contract_start_date,
    c.contract_end_date,
    round(c.capacity_purchased, 2) AS capacity_purchased,
    round(c.total_capacity, 2) AS total_capacity_available,
    greatest(0, round(c.total_capacity - c.total_revenue, 4)) AS capacity_usage_remaining,
    greatest(0, round(c.perc_capacity_available, 4)) AS total_capacity_util_pct
FROM sales.raven.dim_contract_view AS c
WHERE c.salesforce_account_id = '<account_id>'
  AND current_date() BETWEEN c.contract_start_date AND c.contract_end_date
  AND c.agreement_type = 'Capacity';
```

##### Query 2: Contract Over/Under Prediction
```sql
SELECT
    CASE WHEN day_of_overage IS NOT NULL THEN 'overage' ELSE 'underage' END AS predicted_status,
    u.overage_underage_prediction,
    u.day_of_overage,
    u.days_till_overage
FROM sales.raven.a360_overage_underage_prediction_view AS u
WHERE u.salesforce_account_id = '<account_id>';
```

##### Query 3: Contract Renewals (ending in 90 days, no bookings/committed opps)
```sql
WITH contract AS (
    SELECT
        c.salesforce_account_name,
        min(c.contract_start_date) AS contract_start_date,
        max(c.contract_end_date) AS contract_end_date,
        round(sum(c.capacity_purchased), 2) AS capacity_purchased,
        round(greatest(0, sum(c.total_capacity) - sum(c.total_revenue)), 2) AS capacity_usage_remaining,
        round(sum(c.total_capacity), 2) AS total_capacity_available,
        round(div0(sum(total_revenue), sum(c.total_capacity)), 4) AS total_capacity_util_pct,
        count(distinct c.salesforce_contract_id) AS contract_count
    FROM sales.raven.dim_contract_view AS c
    WHERE c.salesforce_account_id = '<account_id>'
      AND c.agreement_type = 'Capacity'
    GROUP BY 1
    HAVING max(c.contract_end_date) BETWEEN CURRENT_DATE + 1 AND CURRENT_DATE + 90
)
SELECT
    c.salesforce_account_name,
    c.contract_start_date,
    c.contract_end_date,
    c.capacity_purchased,
    c.capacity_usage_remaining,
    c.total_capacity_available,
    c.total_capacity_util_pct,
    c.contract_count
FROM contract AS c
LEFT JOIN sales.raven.a360_bookings_acv_view AS b
    ON '<account_id>' = b.salesforce_account_id
    AND b.contract_end_date > c.contract_end_date
LEFT JOIN sales.raven.sda_opportunity_view AS o
    ON '<account_id>' = o.salesforce_account_id
    AND o.is_open = 1 AND o.is_won = false AND o.is_lost = false
    AND o.opportunity_type = 'Renewal' AND o.is_commit = 1
WHERE b.salesforce_account_id IS NULL AND o.salesforce_account_id IS NULL
GROUP BY ALL;
```

##### Query 4: Active Use Cases
```sql
SELECT
    u.use_case_name,
    u.use_case_acv,
    u.use_case_stage,
    u.use_case_status,
    u.decision_date,
    u.go_live_date
FROM sales.raven.sda_use_case_view AS u
WHERE u.salesforce_account_id = '<account_id>'
  AND u.use_case_status NOT IN ('Not In Pursuit', 'Production')
ORDER BY u.use_case_acv DESC NULLS LAST;
```

##### Query 5: Open Pipeline
```sql
SELECT
    p.opportunity_name,
    p.opportunity_type AS type,
    p.close_date,
    sum(p.total_acv) AS total_acv,
    p.stage_name,
    p.days_in_stage,
    p.forecast_status,
    p.created_date,
    p.renewal_type
FROM sales.raven.sda_opportunity_view AS p
WHERE p.salesforce_account_id = '<account_id>'
  AND p.is_open = 1 AND p.is_lost = false AND p.is_won = false
GROUP BY ALL
ORDER BY sum(p.total_acv) DESC NULLS LAST;
```

##### Query 6: Support Cases (last 7 days, Sev-1/2/3)
```sql
SELECT
    csc.sfdc_case_number,
    csc.subject,
    csc.severity,
    csc.status,
    csc.created_date,
    csc.case_creator_name,
    csc.case_owner_name
FROM sales.raven.a360_cust_support_cases_view AS csc
WHERE csc.salesforce_account_id = '<account_id>'
  AND csc.severity IN ('Sev-3: Medium', 'Sev-2: High', 'Sev-1: Critical')
  AND csc.created_date BETWEEN CURRENT_DATE() - 7 AND CURRENT_DATE()
ORDER BY csc.severity ASC, csc.created_date DESC NULLS LAST;
```

##### Query 7: Product Category Revenue (30-day windows with YoY)
```sql
SELECT
    p.product_category,
    p.use_case,
    p.feature,
    SUM(CASE WHEN p.general_date >= DATEADD(DAY, -30, CURRENT_DATE()) AND p.general_date < CURRENT_DATE() THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_l30d,
    SUM(CASE WHEN p.general_date >= DATEADD(DAY, -7, CURRENT_DATE()) AND p.general_date < CURRENT_DATE() THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_l7d,
    SUM(CASE WHEN p.general_date >= DATEADD(DAY, -14, CURRENT_DATE()) AND p.general_date < DATEADD(DAY, -7, CURRENT_DATE()) THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_l8_14d,
    SUM(CASE WHEN p.general_date >= DATE_TRUNC('MONTH', DATEADD(MONTH, -1, CURRENT_DATE())) AND p.general_date < DATE_TRUNC('MONTH', CURRENT_DATE()) THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_last_month,
    SUM(CASE WHEN p.general_date >= DATE_TRUNC('MONTH', DATEADD(MONTH, -13, CURRENT_DATE())) AND p.general_date < DATE_TRUNC('MONTH', DATEADD(MONTH, -12, CURRENT_DATE())) THEN COALESCE(p.revenue, 0) ELSE 0 END) AS revenue_lym
FROM sales.raven.a360_daily_account_product_category_revenue_view AS p
WHERE p.salesforce_account_id = '<account_id>'
  AND ((p.general_date >= DATE_TRUNC('MONTH', DATEADD(MONTH, -13, CURRENT_DATE())) AND p.general_date < DATE_TRUNC('MONTH', DATEADD(MONTH, -12, CURRENT_DATE())))
    OR (p.general_date >= DATEADD(DAY, -30, CURRENT_DATE()) AND p.general_date < CURRENT_DATE())
    OR (p.general_date >= DATE_TRUNC('MONTH', DATEADD(MONTH, -1, CURRENT_DATE())) AND p.general_date < DATE_TRUNC('MONTH', CURRENT_DATE())))
  AND COALESCE(p.revenue, 0) > 0
GROUP BY p.product_category, p.use_case, p.feature
ORDER BY revenue_l7d DESC;
```

##### Query 8: Monthly/Daily Consumption Trend
```sql
SELECT 'MONTHLY' AS agg_level, DATE_TRUNC(month, c.general_date)::date AS trend_date, SUM(c.revenue) AS revenue
FROM sales.raven.a360_revenue_consumption_view AS c
WHERE c.salesforce_account_id = '<account_id>'
  AND c.general_date < CURRENT_DATE()
  AND c.general_date >= DATEADD('month', -13, DATE_TRUNC(month, CURRENT_DATE()))
  AND c.general_date < DATE_TRUNC(month, CURRENT_DATE())
GROUP BY ALL
UNION ALL
SELECT 'DAILY' AS agg_level, c.general_date::date AS trend_date, SUM(c.revenue) AS revenue
FROM sales.raven.a360_revenue_consumption_view AS c
WHERE c.salesforce_account_id = '<account_id>'
  AND c.general_date < CURRENT_DATE()
  AND c.general_date >= DATEADD('day', -14, CURRENT_DATE())
GROUP BY ALL
ORDER BY agg_level, trend_date;
```

##### Query 9: Daily Consumption (last 30 days)
```sql
SELECT c.general_date::date AS day_ts, ROUND(SUM(c.revenue), 2) AS revenue_daily
FROM sales.raven.a360_revenue_consumption_view AS c
WHERE c.salesforce_account_id = '<account_id>'
  AND c.general_date < CURRENT_DATE()
  AND c.general_date >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY 1 ORDER BY 1;
```

##### Query 10: Weekly Consumption (last ~13 weeks)
```sql
SELECT DATE_TRUNC('week', c.general_date)::date AS week_ts, ROUND(SUM(c.revenue), 2) AS revenue_weekly
FROM sales.raven.a360_revenue_consumption_view AS c
WHERE c.salesforce_account_id = '<account_id>'
  AND c.general_date < CURRENT_DATE()
  AND c.general_date >= DATEADD('day', -91, CURRENT_DATE())
GROUP BY 1 ORDER BY 1;
```

##### Query 11: Monthly Consumption (last 12 months)
```sql
SELECT DATE_TRUNC('month', c.general_date)::date AS month_ts, ROUND(SUM(c.revenue), 2) AS revenue_monthly
FROM sales.raven.a360_revenue_consumption_view AS c
WHERE c.salesforce_account_id = '<account_id>'
  AND c.general_date < CURRENT_DATE()
  AND c.general_date >= DATEADD('month', -11, DATE_TRUNC('month', CURRENT_DATE()))
GROUP BY 1 ORDER BY 1;
```

#### 3B: Fetch Authoritative Firmographics (in parallel with 3A)

```sql
SELECT * FROM TABLE(SALES.RAVEN.GET_3P_DATA('<account_id>'));
```

**Extract `website_domain` for disambiguation:** From the GET_3P_DATA result, capture the company's website domain (e.g., `coinbase.com`). This is used in Step 3C to disambiguate web searches for companies with common names. If GET_3P_DATA does not return a website domain, proceed without it — do NOT query `d_salesforce_account_customers` or any other table for a website column.

#### 3C: Company Research via Web Search (after 3B returns, or in parallel if 3B is slow)

Use the built-in `web_search` tool for company research. Do NOT use the `GEMINI_DEEP_SEARCH()` SQL function or invoke the `gemini-web-search` skill.

**Dependency on 3B:** Step 3C needs `website_domain` from GET_3P_DATA (3B) for disambiguation. Wait for 3B to return before starting web searches. If 3B fails or returns no domain, proceed with web searches immediately without disambiguation.

**Disambiguation (IMPORTANT):** If a `website_domain` was obtained from GET_3P_DATA, append it to EVERY web search query to ensure results are about the correct company. Format: `"<ACCOUNT_NAME> (website: <website_domain>) ..."`. This prevents researching the wrong entity for companies with common names (e.g., Mercury, Bolt, Plaid). If no website domain is available, proceed without it.

Run the following **3 web searches in parallel**:

**Show your work to the user as you go:**
- Before searching: briefly state what you're about to search for and why (e.g., "Searching for Acme Corp's company profile, financial status, and recent news...")
- After each search: summarize in 1-2 sentences what you found and what was useful (e.g., "Found that Acme Corp is a public SaaS company (NYSE: ACME) with $2.1B market cap. Key recent news: Q3 earnings beat expectations.")
- If a search returns poor results: mention it and note any gaps (e.g., "Limited financial data found — company appears to be private with no recent funding announcements.")

**Search 1: Company Profile + Industry + Competitors**
```
web_search: "<ACCOUNT_NAME> <website_domain if available> company profile products services industry competitors"
```
From results, extract:
- One-liner description (25-50 words)
- Main products and services (top 5 with brief descriptions)
- Headquarters location, founding year, public/private status
- Market position and specific, factual differentiators (2-4 points — e.g., "largest cloud payments platform in Europe", "only provider of real-time X". Do NOT use generic terms like "leadership", "scale", "innovation")
- Current strategic focus areas (specific initiatives, not buzzwords)
- Geographic presence
- Industry sector, description (50-100 words), growth outlook (expanding/stable/contracting)
- Major industry trends (4-5 key trends), data and AI use cases (3-4 examples)
- Top 3-4 direct competitors with: name, brief description, positioning vs. the account, HQ location
- Do NOT extract employee count, annual revenue, or tech stack from web search results, Salesforce data, or any other source — tech stack MUST come exclusively from GET_3P_DATA

**Search 2: Financial Status**
```
web_search: "<ACCOUNT_NAME> <website_domain if available> financial status market cap earnings funding 2026"
```
From results, extract:
- If public: market cap (with date), stock performance (30-day trend), latest earnings call date and key takeaways
- If private: latest funding round (date, amount, lead investors, valuation), total raised, latest known valuation
- Recent financial announcements
- Do NOT include annual revenue or employee count (provided by GET_3P_DATA)

**Search 3: Recent News (last 90 days only)**
```
web_search: "<ACCOUNT_NAME> <website_domain if available> news announcements after:<90_DAYS_AGO_DATE>"
```
Where `<90_DAYS_AGO_DATE>` is calculated as today's date minus 90 days in YYYY-MM-DD format (e.g., if today is 2026-02-26, use `after:2025-11-28`).

From results, **strictly filter by date** — only keep articles published within the last 90 days:
- **POST-FILTER STEP (mandatory):** For every article returned by web search, check its publication date. Calculate the 90-day cutoff date (today minus 90 days). **Discard** any article with a publication date before the cutoff. **Discard** any article with no identifiable date. Do this BEFORE summarizing or including anything.
- After filtering, if **zero articles remain**: set the news section to: "No significant news found in the last 90 days." Do NOT fall back to older articles.
- If articles remain after filtering:
  - Combined summary (60-80 words) of key themes and developments
  - Top 3 most important articles with: title, date (YYYY-MM-DD), source, summary (20-30 words), URL
- Focus on: earnings, product launches, partnerships, acquisitions, leadership changes, strategic initiatives
- Ignore: job postings, minor blog posts, marketing content

**After all searches complete:** Synthesize results into structured research notes for use in the brief sections. Include source URLs as citations.

#### 3D: Invoke `contact_intelligence` skill (in parallel with 3A, if available)

Pass: account_id

**If `contact_intelligence` skill is NOT available or fails: skip the Contacts section (Section 7) entirely.** Do NOT attempt to infer or research contacts from web search, LinkedIn, or any other source.

#### 3E: Cached Brief Lookup (in parallel with 3A)

Check if a recent workflow brief already contains use case recommendations for this account. This avoids the slow SP call when a pre-generated brief exists (the SP can take 30s+).

```sql
SELECT 
    f.value:header::STRING AS recommendation_header,
    f.value:summary::STRING AS recommendation_summary,
    f.value:details[0]:content::STRING AS recommendation_content
FROM SALES.RAVEN.WORKFLOW_EXECUTIONS,
    LATERAL FLATTEN(input => RESPONSE_PAYLOAD:payload) f
WHERE WORKFLOW_ID LIKE '%BRIEF'
  AND INPUTS:account_id::STRING = '<account_id>'
  AND STATUS = 'COMPLETED'
  AND f.value:header::STRING IN ('Use Case Recommendations', 'Potential Snowflake Value Proposition')
  AND DATEDIFF('day', COMPLETED_AT, CURRENT_TIMESTAMP()) <= 30
ORDER BY COMPLETED_AT DESC
LIMIT 1;
```

- **If a row is returned:** Store `recommendation_summary` and `recommendation_content` for use in Section 5. The SP call in Step 4 can be **skipped**.
- **If no rows returned:** The SP call in Step 4 is required as a fallback.

### Step 3-Quick: Quick Brief Workflow (~1-2 min)

**This path runs when the user selects "Quick Brief".** It skips the slow SP call but keeps web research.

Run the following **in parallel**:

1. **3A: Account Summary Queries** — All 11 queries (same as Step 3, 3A above)
2. **3B: GET_3P_DATA** — Firmographics (same as Step 3, 3B above)
3. **3C: Web Search** — All 3 web searches (same as Step 3, 3C above — wait for 3B's `website_domain` if available)
4. **3E: Cached Brief Lookup** — Check for pre-generated use case recommendations (same query as Step 3, 3E above)

**No SP call (RECO_FOR_PROSPECTING_SP_SALES). No contact_intelligence call.** Use cached recommendations from 3E if available.

After all queries return, synthesize into a **Quick Capacity Brief** with these sections:

1. **Time Sensitive Insights** — From queries 2, 3, 6 (overage/underage, renewals, support cases)
2. **Snowflake Usage** — From queries 1, 7, 8, 9, 10, 11 (contract, product revenue, consumption)
3. **Opportunities and Use Cases** — From queries 4, 5 (active use cases, pipeline)
4. **Recent Company News** — From web search (Search 3)
5. **Use Case Recommendations** — **Only if cached brief lookup (3E) returned results.** Otherwise omit this section.
6. **Recent Support Activity** — From query 6
7. **Company Insights** — From GET_3P_DATA + web search (Search 1, Search 2)
8. **Industry Insights** — From web search (Search 1)
9. **Competitors** — From web search (Search 1)

**Include account team info** from account_finder at the top (same format as Full Brief).

Apply the same synthesis rules as Step 5 (no fabrication, omit empty sections, scannable formatting).

**Footer:** *"Quick brief (cached recommendations) — re-run with 'Full Brief' for fresh AI use case recommendations."* Omit this footer if Use Case Recommendations were not available from cache.

### Step 3-Raw: Account Data Only Workflow (~30s)

**This path runs when the user selects "Account Data Only".** It returns raw query results with no synthesis.

Run **only** the 11 account summary queries (3A) — same queries as Step 3, 3A.

Present results as structured tables (one per query that returned data):

```markdown
# Account Data: [Account Name]
*Generated on [Date]*

## Contract Status
[Table from Query 1]

## Contract Health
[From Query 2]

## Upcoming Renewals
[From Query 3]

## Active Use Cases
[Table from Query 4]

## Open Pipeline
[Table from Query 5]

## Recent Support Cases
[Table from Query 6]

## Product Revenue Breakdown
[From Query 7]

## Consumption Trends
[From Queries 8-11]
```

Skip any query that returns no rows. No synthesis, no analysis, no recommendations.

**Footer:** *"Raw data only — re-run with 'Quick Brief' or 'Full Brief' for synthesis and analysis."*

### Step 4: Generate Use Case Recommendations (Full Brief only, after web search completes)

**Skip this step if the cached brief lookup (3E) returned results.**

Call the stored procedure directly with the account_id and company context from web search (Step 3C):

```sql
CALL SALES.RAVEN.RECO_FOR_PROSPECTING_SP_SALES(
  '<account_id>',
  '<company_profile_summary from Search 1>',
  '<recent_news_summary from Search 3>'
);
```

- If web search returned no usable company profile or news, pass empty strings (`''`)
- The SP returns 2 prioritized use cases with real customer stories, metrics, and relevance mapping
- **Never invent customer stories or metrics** — use the SP output as-is
- Frame as **expansion** opportunities (this is a capacity customer, not initial adoption)

**CRITICAL — If the SP call fails or returns an error:**
- **SKIP "Section 5: Use Case Recommendations" entirely.** Do NOT include it in the brief.
- **Do NOT generate, summarize, or infer your own use case recommendations.** You do not have access to validated customer stories, metrics, or relevance data — any recommendations you generate would be fabricated.
- Do NOT fall back to web search results, general Snowflake knowledge, or any other source to create substitute recommendations.
- Briefly note to the user: "Use case recommendations could not be generated (data source unavailable). Omitting this section."

### Step 5: Synthesize into 10-Section Capacity Brief

Combine all data sources into a unified brief matching the CAPACITY_BRIEF format.

**Include account team info** from account_finder at the top:
```markdown
**Account Team:** AE: [owner] | SE: [lead_se] | DM: [dm] | RVP: [rvp]
```

**Synthesis Rules:**
- **Don't repeat information** -- avoid restating facts across sections
- **Connect the dots** -- link contacts to relevant use cases, tie consumption to pipeline
- **Omit empty sections** rather than showing "No data available"
- **Keep it scannable** -- bullets, bold key terms, short paragraphs
- **Time Sensitive Insights come first** -- renewals, critical tickets, contract health flags
- **Only output the 10 defined sections below** -- do NOT add extra sections (e.g., "Opening Angle", "Next Steps", "Summary") unless the user explicitly asks for them
- **NEVER fabricate information** -- only include facts directly sourced from search results or SQL data. If a data source (SQL query, stored procedure, skill, or web search) fails or returns no data, **omit that section entirely**. Do NOT substitute your own knowledge, generate plausible-sounding content, or fill in gaps with general information. Every fact in the brief must trace back to a specific tool result from this session.
- **Sources footer (web only)** -- if you include a "Sources" section at the end of the brief, it must ONLY contain URLs from web search results. Do NOT list internal data sources such as "Salesforce Account Data", "GET_3P_DATA firmographics", "RECO_FOR_PROSPECTING_SP_SALES", "dim_contract_view", or any SQL function/table/view name. The Sources section is for external web citations only.

## Output Format: 10-Section Capacity Customer Brief

### Section 1: Time Sensitive Insights
**Sources:** Account summary (renewals, support cases, contract health) + contacts
- Renewals ending within 90 days without committed opps
- Sev-1/Sev-2 support cases in last 7 days
- Contract overage/underage prediction alerts
- Any other actionable items requiring immediate attention

### Section 2: Snowflake Usage
**Sources:** Account summary (contract status, consumption trends, product revenue)
- **Contract Details**: Capacity purchased, utilization %, remaining balance, contract dates
- **Consumption Trends**: Daily/weekly/monthly consumption with trend direction
- **Product Breakdown**: Revenue by product category (L7D, L30D, MoM, YoY changes)

### Section 3: Opportunities and Use Cases
**Sources:** Account summary (active use cases, open pipeline)
- **Active Use Cases**: Name, ACV, stage, status, decision/go-live dates
- **Open Pipeline**: Opportunity name, type, ACV, stage, forecast status, days in stage

### Section 4: Recent Company News
**Sources:** Web search (Search 3: Recent News)
- **Section header:** Use "Recent Company News" only. Do NOT append "(Last 90 Days)" or any date range to the header.
- If the post-filter step from Search 3 yielded zero articles, render: "No significant news found in the last 90 days." and move on.
- If articles passed the filter, render them as a mechanical passthrough with dates and sources.
- **Every cited article MUST be rendered as a hyperlink:** `[Article Title](URL)` with date and source. Example: `[Acme Launches AI Platform](https://example.com/article) — 2026-02-15, TechCrunch`. Never output a news item without a clickable link if a URL was captured during web search.
- **Double-check dates:** Before rendering each article, verify its date is within the last 90 days. If not, drop it silently.

### Section 5: Use Case Recommendations
**Sources:** Value proposition (RECO_FOR_PROSPECTING_SP_SALES)
- Mechanical passthrough of AI-recommended use cases with customer stories
- Framed as **expansion** opportunities (not initial adoption)

### Section 6: Recent Support Activity
**Sources:** Account summary (support cases)
- Sev-1/2/3 cases from last 7 days: case number, subject, severity, status, owner

### Section 7: Contacts
**Sources:** Contact intelligence (contact_intelligence skill)
- Mechanical passthrough of GTM-ready contacts with engagement data
- **If contact_intelligence is not available: omit this section entirely**

### Section 8: Company Insights
**Sources:** Web search (Search 1: Company Profile) + firmographics (GET_3P_DATA)
- **Summary**: 4-6 sentences covering: company name, industry, what they do, market position, geographic presence, specific factual differentiators, strategic focus, founding year, public/private status. NO financial metrics in summary.
- **Products & Services**: Max 4 products as bullets with 20-40 word descriptions
- **Financial Insights**: Market cap/funding + earnings call date/summary (from Search 2)
- **Tech Stack**: Verified technologies from GET_3P_DATA only — if none, say "No verified technology stack data available"

### Section 9: Industry Insights
**Sources:** Web search (Search 1: Industry Overview)
- **Summary**: 3-4 sentences on industry definition, market size, growth outlook, key drivers
- **Trends & Challenges**: 4 markdown bullets combining industry trends and challenges (20-40 words each)
- **Data & AI Use Cases**: 4 markdown bullets describing data/AI use cases in this industry (15-30 words each)
- If industry data is missing from web search, state: "Information currently unavailable."

### Section 10: Competitors
**Sources:** Web search (Search 1: Competitors)
- Competitive landscape analysis, key differentiators

## Refinement Commands

| Command | Effect |
|---------|--------|
| "Shorter" | Condense to 1-page executive summary |
| "Just time sensitive" | Show only Section 1 |
| "Just usage" | Show only Snowflake Usage + Product Revenue |
| "Just pipeline" | Show only Opportunities and Use Cases |
| "Just consumption" | Show only consumption trends and charts |
| "Focus on risks" | Highlight overage/underage, support cases, renewals |
| "More detail on [topic]" | Expand specific section |
| "Skip [section]" | Remove a section |

## Retry Policy

Before omitting a section due to failure, retry transient errors **once**:

- **SQL queries (11 account summary queries, GET_3P_DATA, cached brief lookup)**: If a query fails with a transient error (timeout, warehouse suspended, throttling), retry ONCE.
- **SP call (RECO_FOR_PROSPECTING_SP_SALES)**: If the SP fails, retry ONCE.
- **Web search**: If a web search returns zero results, retry ONCE with a simplified query (just company name + topic keyword).
- **Non-retryable (skip immediately)**: Role failures (`USE ROLE` denied), "object does not exist" errors, permission errors. Do NOT retry these.

## Error Handling

- **Query fails (after retry)**: **Omit the section(s) that depend on that query's data.** Do NOT generate substitute content from your own knowledge. Note the failure silently and continue with remaining data sources.
- **RECO_FOR_PROSPECTING_SP_SALES fails (after retry)**: **Skip Section 5 (Use Case Recommendations) entirely.** Do NOT generate your own recommendations.
- **GET_3P_DATA fails (after retry)**: Omit tech stack, employee count, and revenue data. Do NOT substitute with web search or general knowledge.
- **No data returned from a query**: Omit the section rather than showing empty content. Do NOT fill it with general information.
- **Skill fails**: **Omit the section.** Do NOT attempt to fill in the section with your own content.
- **Web search returns no results (after retry)**: Omit the affected sub-sections. Do NOT fabricate company profiles, news, or financial data.
- **Not a capacity customer**: Inform user, suggest `prospect_research` instead.
- **Account not found**: Ask user to verify company name or provide account_id.
- **All data sources fail**: Do NOT produce a brief from general knowledge. Inform the user that the brief could not be generated and suggest checking their connection/role.
- **Partial results**: Deliver what succeeded, clearly omit what failed. Never pad missing sections with generated content.

### Consolidated Error Reporting

During execution, **do not interrupt the user with individual error messages** for each failure. Instead:

1. Note failures silently as they occur and continue fetching remaining data sources.
2. After synthesis, append a **"Data Gaps"** footer at the end of the brief listing any sections that were omitted and why.
3. Format:
   ```
   ---
   **Data Gaps:** [Section name] ([reason]) | [Section name] ([reason]) | ...
   ```
   Example: `**Data Gaps:** Tech Stack (GET_3P_DATA timeout) | News (no results after retry) | Use Case Recs (SP unavailable)`
4. If no sections were omitted, do not include the Data Gaps footer.

## Examples

### Example 1: Full Brief (default)
**User**: Account summary for Coinbase

**What you do**:
1. Set role, invoke `account_finder` with "Coinbase" (or skip if pre-resolved)
2. Confirm `IS_CAPACITY_CUSTOMER = true`
3. Present brief type options: "Full Brief (~5 min)" / "Quick Brief (~1-2 min)" / "Account Data Only (~30s)"
4. User selects "Full Brief" → run in parallel:
   - 11 account summary queries + `GET_3P_DATA` + `contact_intelligence` + cached brief lookup
   - After GET_3P_DATA returns: 3 web searches with domain disambiguation
5. If cached brief lookup returned results, use those for Section 5. Otherwise call `RECO_FOR_PROSPECTING_SP_SALES` (after web research completes)
6. Synthesize into 10-section capacity brief with account team header
7. Append "Data Gaps" footer if any sections were omitted

### Example 2: Quick Brief
**User**: Brief me on Coinbase — quick

**What you do**:
1. Set role, resolve account
2. Present options → user selects "Quick Brief (~1-2 min)"
3. Run in parallel: 11 queries + GET_3P_DATA + web searches + cached brief lookup
4. No SP call. No contact_intelligence. Use cached recommendations if available.
5. Synthesize into quick capacity brief (up to 9 sections, minus Use Case Recs if no cache)
6. Footer: *"Quick brief (cached recommendations) — re-run with 'Full Brief' for fresh AI use case recommendations."*
