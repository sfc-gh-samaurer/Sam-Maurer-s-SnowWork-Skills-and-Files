---
name: prospect_research
description: >
  Generate a prospect or self-service brief for a target account. Resolves
  accounts via account_finder, then orchestrates company research, value
  propositions, and contacts into a 6-7 section brief. For capacity customers,
  hands off to account_summarization which produces the full 10-section
  capacity brief. Trigger when users ask to "prep me for [account]", "brief
  me on [company]", or "research [company]".
created_date: 2026-02-26
last_updated: 2026-03-13
owner_name: Tess Tao
version: 1.1.0
---

## When to Use
- "Brief me on [company]"
- "Prep me for my meeting with [account]"
- "Give me a sales overview for [company]"
- "What do I need to know about [account] before my call?"
- "Full account prep for [company]"
- "Research [company] and give me talking points"


### Known Orchestratable Skills

| Skill Directory | Provides | Conditional |
|-----------------|----------|-------------|
| `account_finder` | Account resolution (ID, type, team, capacity status) | No -- always runs first |
| `account_summarization` | Full 10-section capacity customer brief | **Yes** -- capacity customers only (hand off entirely) |
| `contact_intelligence` | Prioritized GTM-ready contacts | No |

### Data Sources (SQL Functions)

| Function | Provides |
|----------|----------|
| `GET_3P_DATA(account_id)` | Firmographics: employee count, annual revenue, tech stack |
| `RECO_FOR_PROSPECTING_SP_SALES(account_id, company_profile, recent_news)` | Use case recommendations with real customer stories |

### Built-in Tools

| Tool | Provides |
|------|----------|
| `web_search` | Company research: profile, financials, news, industry, competitors |

### Dependency Graph (Prospect / Self-Service)

```
account_finder ─────────────────┬──→ 3x web_search ──→ RECO_FOR_PROSPECTING_SP_SALES
  (resolve account first)       │    (company research)   (use case recommendations)
                                ├──→ GET_3P_DATA (firmographics + tech stack)
                                │
                                └──→ contact_intelligence (if available)
```

### Capacity Customer Handoff

```
account_finder ──→ IS_CAPACITY_CUSTOMER = true ──→ hand off to account_summarization
                   (this skill exits; account_summarization handles everything)
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| account_id or account_name | Yes | Target account |
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

Invoke the `account_finder` skill:

```
skill account_finder
```

The skill will search `sales.raven.d_salesforce_account_customers`, handle disambiguation, and return full account metadata.

### Step 2: Route by Account Type

After account_finder returns, check `IS_CAPACITY_CUSTOMER`:

#### If IS_CAPACITY_CUSTOMER = true → Hand Off to account_summarization

**Do NOT continue with this skill's workflow.** Instead:

1. Tell the user: "[Account Name] is a capacity customer. Handing off to the capacity brief workflow."
2. Invoke the `account_summarization` skill, passing the already-resolved account data (account_id, account name, team info, etc.) so it skips its own account_finder step:

```
skill account_summarization
```

Provide the resolved `SALESFORCE_ACCOUNT_ID` and note the account is pre-resolved. Also pass through any `persona`, `focus`, or `personal_twist` inputs from the user.

**This skill's workflow ends here for capacity customers.** `account_summarization` will handle the full 10-section capacity brief (account summary queries + company research + value prop + contacts + synthesis).

#### If IS_CAPACITY_CUSTOMER = false → Continue with Prospect/Self-Service Brief

Proceed to Step 3.

### Step 3: Present Plan and Confirm (Prospects & Self-Service Only)

Use `ask_user_question` to present the brief plan with clearly labeled speed tiers.

**For PROSPECT accounts** (TYPE = Prospect, Partner, or unknown):

```
questions:
  - header: "Brief Type"
    question: "[Account Name] is a PROSPECT (owned by [SALESFORCE_OWNER_NAME], SE: [LEAD_SALES_ENGINEER_NAME]).\n\nChoose a brief type:"
    multiSelect: false
    options:
      - label: "Full Brief (~5 min)"
        description: "Complete 6-section prospect brief: company research, news, contacts, firmographics, and AI use case recommendations. Most comprehensive but slowest."
      - label: "Quick Brief (~1-2 min)"
        description: "Company research, news, and firmographics. Uses cached use case recommendations instead of regenerating. No contacts."
```

**For SELF-SERVICE accounts** (TYPE = Self Service):

```
questions:
  - header: "Brief Type"
    question: "[Account Name] is a SELF-SERVICE CUSTOMER (owned by [SALESFORCE_OWNER_NAME]).\n\nChoose a brief type:"
    multiSelect: false
    options:
      - label: "Full Brief (~5 min)"
        description: "Complete 7-section self-service brief: company research, news, usage, contacts, firmographics, and AI use case recommendations. Most comprehensive but slowest."
      - label: "Quick Brief (~1-2 min)"
        description: "Company research, news, usage, and firmographics. Uses cached use case recommendations instead of regenerating. No contacts."
```

**Wait for user confirmation before proceeding.**

#### Route by Brief Type

- **"Full Brief"** → Proceed to Step 4 (full workflow).
- **"Quick Brief"** → Proceed to Step 4-Quick (quick workflow).

### Step 4: Fetch Data (Prospects & Self-Service — Full Brief)

**This step is for the "Full Brief" option only.** For "Quick Brief" see Step 4-Quick.

Run the following **in parallel**:

#### 4.1: Fetch Authoritative Firmographics

```sql
SELECT * FROM TABLE(SALES.RAVEN.GET_3P_DATA('<account_id>'));
```

**Extract `website_domain` for disambiguation:** From the GET_3P_DATA result, capture the company's website domain (e.g., `stripe.com`). This is used in Step 4.2 to disambiguate web searches for companies with common names. If GET_3P_DATA does not return a website domain, proceed without it — do NOT query `d_salesforce_account_customers` or any other table for a website column.

#### 4.2: Company Research via Web Search (after 4.1 returns, or in parallel if 4.1 is slow)

Use the built-in `web_search` tool for company research. Do NOT use the `GEMINI_DEEP_SEARCH()` SQL function or invoke the `gemini-web-search` skill.

**Dependency on 4.1:** Step 4.2 needs `website_domain` from GET_3P_DATA (4.1) for disambiguation. Wait for 4.1 to return before starting web searches. If 4.1 fails or returns no domain, proceed with web searches immediately without disambiguation.

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

#### 4.3: Invoke `contact_intelligence` skill (if available)

Pass: account_id

**If `contact_intelligence` skill is NOT available or fails: skip the Contacts section entirely.** Do NOT attempt to infer or research contacts from web search, LinkedIn, or any other source.

#### 4.4: Cached Brief Lookup (in parallel with 4.1)

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

- **If a row is returned:** Store `recommendation_summary` and `recommendation_content` for use in the Value Proposition section. The SP call in Step 5 can be **skipped**.
- **If no rows returned:** The SP call in Step 5 is required as a fallback.

### Step 4-Quick: Quick Brief Workflow (~1-2 min)

**This path runs when the user selects "Quick Brief".** It skips the slow SP call but keeps web research.

Run the following **in parallel**:

1. **4.1: GET_3P_DATA** — Firmographics (same as Step 4, 4.1 above)
2. **4.2: Web Search** — All 3 web searches (same as Step 4, 4.2 above — wait for 4.1's `website_domain` if available)
3. **4.4: Cached Brief Lookup** — Check for pre-generated use case recommendations (same query as Step 4, 4.4 above)

**No SP call (RECO_FOR_PROSPECTING_SP_SALES). No contact_intelligence call.** Use cached recommendations from 4.4 if available.

After all queries return, synthesize using the same output format as Step 6 (PROSPECT or SELF-SERVICE brief depending on account type), with these differences:

- **Contacts** — Omit this section (contact_intelligence is not called in Quick Brief).
- **Potential Snowflake Value Proposition** — **Only if cached brief lookup (4.4) returned results.** Otherwise omit this section.

Apply the same synthesis rules as Step 6 (no fabrication, omit empty sections, scannable formatting).

**Footer:** *"Quick brief (cached recommendations) — re-run with 'Full Brief' for fresh AI use case recommendations."* Omit this footer if Value Proposition was not available from cache.

### Step 5: Generate Use Case Recommendations (Full Brief only, after web search completes)

**Skip this step if the cached brief lookup (4.4) returned results.**

Call the stored procedure directly with the account_id and company context from web search (Step 4.2):

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
- Frame as **net-new adoption** (this is a prospect, not expansion)

**CRITICAL — If the SP call fails or returns an error:**
- **SKIP the "Potential Snowflake Value Proposition" section entirely.** Do NOT include it in the brief.
- **Do NOT generate, summarize, or infer your own use case recommendations.** You do not have access to validated customer stories, metrics, or relevance data — any recommendations you generate would be fabricated.
- Do NOT fall back to web search results, general Snowflake knowledge, or any other source to create substitute recommendations.
- Briefly note to the user: "Use case recommendations could not be generated (data source unavailable). Omitting this section."

### Step 6: Synthesize into Brief

Combine outputs into a unified brief.

**Include account team info** from account_finder at the top:
```markdown
**Account Team:** AE: [owner] | SE: [lead_se] | DM: [dm] | RVP: [rvp]
```

**Synthesis Rules:**
- **Don't repeat information** -- avoid restating facts across sections
- **Connect the dots** -- link contacts to relevant use cases
- **Omit empty sections** rather than showing "No data available"
- **Keep it scannable** -- bullets, bold key terms, short paragraphs
- **Only output the defined sections below** -- do NOT add extra sections (e.g., "Opening Angle", "Next Steps", "Summary") unless the user explicitly asks for them
- **NEVER fabricate information** -- only include facts directly sourced from search results or SQL data. If a data source (SQL query, stored procedure, skill, or web search) fails or returns no data, **omit that section entirely**. Do NOT substitute your own knowledge, generate plausible-sounding content, or fill in gaps with general information. Every fact in the brief must trace back to a specific tool result from this session.
- **Sources footer (web only)** -- if you include a "Sources" section at the end of the brief, it must ONLY contain URLs from web search results. Do NOT list internal data sources such as "Salesforce Account Data", "GET_3P_DATA firmographics", "RECO_FOR_PROSPECTING_SP_SALES", or any SQL function/table name. The Sources section is for external web citations only.

## Output Format

### PROSPECT Brief (6 sections):
1. **Company Insights** - Summary (4-6 sentences: name, industry, what they do, market position, geographic presence, differentiators, strategic focus, founding year, public/private. NO financial metrics in summary), then 3 sub-sections: Products & Services (max 4, bulleted), Financial Insights (market cap/funding + earnings), Tech Stack (from GET_3P_DATA only — if none, say "No verified technology stack data available")
2. **Industry Insights** - Summary (3-4 sentences on industry definition, market size, growth outlook, key drivers), then 2 sub-sections: Trends & Challenges (4 markdown bullets, 20-40 words each), Data & AI Use Cases (4 markdown bullets, 15-30 words each). If industry data is missing, state: "Information currently unavailable."
3. **Recent News** - Do NOT append "(Last 90 Days)" or any date range to this header. If no articles passed the 90-day post-filter, render: "No significant news found in the last 90 days." Otherwise, list articles with hyperlinks: `[Article Title](URL)` with date and source. Example: `[Acme Launches AI Platform](https://example.com/article) — 2026-02-15, TechCrunch`. Double-check each article's date is within 90 days before including it.
4. **Contacts** - Key stakeholders and decision makers *(omit if contact_intelligence unavailable)*
5. **Competitors** - Competitive landscape analysis
6. **Potential Snowflake Value Proposition** - Tailored use cases with customer stories

### SELF-SERVICE Brief (7 sections):
1. **Company Insights** - Summary (4-6 sentences: name, industry, what they do, market position, geographic presence, differentiators, strategic focus, founding year, public/private. NO financial metrics in summary), then 3 sub-sections: Products & Services (max 4, bulleted), Financial Insights (market cap/funding + earnings), Tech Stack (from GET_3P_DATA only — if none, say "No verified technology stack data available")
2. **Snowflake Usage** - Current self-service usage patterns (from firmographics/research)
3. **Industry Insights** - Summary (3-4 sentences on industry definition, market size, growth outlook, key drivers), then 2 sub-sections: Trends & Challenges (4 markdown bullets, 20-40 words each), Data & AI Use Cases (4 markdown bullets, 15-30 words each). If industry data is missing, state: "Information currently unavailable."
4. **Recent News** - Do NOT append "(Last 90 Days)" or any date range to this header. If no articles passed the 90-day post-filter, render: "No significant news found in the last 90 days." Otherwise, list articles with hyperlinks: `[Article Title](URL)` with date and source. Example: `[Acme Launches AI Platform](https://example.com/article) — 2026-02-15, TechCrunch`. Double-check each article's date is within 90 days before including it.
5. **Contacts** - Key stakeholders and decision makers *(omit if contact_intelligence unavailable)*
6. **Competitors** - Competitive landscape
7. **Potential Snowflake Value Proposition** - Enterprise upgrade opportunities with customer stories

## Refinement Commands

| Command | Effect |
|---------|--------|
| "Shorter" | Condense to 1-page executive summary |
| "Just the value prop" | Show only value proposition section |
| "More detail on [topic]" | Expand specific section |
| "Focus on [angle]" | Re-synthesize emphasizing specific angle |
| "Skip [section]" | Remove a section |
| "Treat as customer" | Re-run as capacity customer via account_summarization |

## Examples

### Example 1: Full Prospect Brief (default)
**User**: Prep me for my meeting with Stripe

**What you do**:
1. Set role
2. Invoke `account_finder` with "Stripe" -> IS_CAPACITY_CUSTOMER = false, TYPE = Prospect
3. Present brief type options: "Full Brief (~5 min)" / "Quick Brief (~1-2 min)"
4. User selects "Full Brief" → run in parallel:
   - `GET_3P_DATA` for firmographics + cached brief lookup
   - After GET_3P_DATA returns: 3 web searches with domain disambiguation
   - `skill contact_intelligence` for contacts
5. If cached brief lookup returned results, use those for Use Case Recommendations. Otherwise call `RECO_FOR_PROSPECTING_SP_SALES` with adoption framing.
6. Synthesize into 6-section prospect brief with account team header
7. Append "Data Gaps" footer if any sections were omitted

### Example 2: Quick Prospect Brief
**User**: Quick brief on Stripe

**What you do**:
1. Set role
2. Invoke `account_finder` with "Stripe" -> IS_CAPACITY_CUSTOMER = false, TYPE = Prospect
3. Present options → user selects "Quick Brief (~1-2 min)"
4. Run in parallel: GET_3P_DATA + web searches + cached brief lookup
5. No SP call. No contact_intelligence. Use cached recommendations if available.
6. Synthesize into prospect brief (up to 5 sections, minus Use Case Recs and Contacts)
7. Footer: *"Quick brief (cached recommendations) — re-run with 'Full Brief' for fresh AI use case recommendations."*

### Example 3: Capacity customer detected -> handoff
**User**: Brief me on Coinbase

**What you do**:
1. Set role
2. Invoke `account_finder` with "Coinbase" -> IS_CAPACITY_CUSTOMER = true
3. Tell user: "Coinbase is a capacity customer. Handing off to the capacity brief workflow."
4. Invoke `skill account_summarization` with pre-resolved account data
5. **This skill exits.** account_summarization produces the 10-section capacity brief.

## Retry Policy

Before omitting a section due to failure, retry transient errors **once**:

- **SQL queries (GET_3P_DATA, cached brief lookup)**: If a query fails with a transient error (timeout, warehouse suspended, throttling), retry ONCE.
- **SP call (RECO_FOR_PROSPECTING_SP_SALES)**: If the SP fails, retry ONCE.
- **Web search**: If a web search returns zero results, retry ONCE with a simplified query (just company name + topic keyword).
- **Non-retryable (skip immediately)**: Role failures (`USE ROLE` denied), "object does not exist" errors, permission errors. Do NOT retry these.

## Error Handling

- **account_finder fails**: Fall back to asking user for account_id directly.
- **Query fails (after retry)**: **Omit the section(s) that depend on that query's data.** Do NOT generate substitute content from your own knowledge. Note the failure silently and continue with remaining data sources.
- **RECO_FOR_PROSPECTING_SP_SALES fails (after retry)**: **Skip Use Case Recommendations section entirely.** Do NOT generate your own recommendations.
- **GET_3P_DATA fails (after retry)**: Omit tech stack, employee count, and revenue data. Do NOT substitute with web search or general knowledge.
- **No data returned from a query**: Omit the section rather than showing empty content. Do NOT fill it with general information.
- **Skill not available**: Skip it, note: "[Section] not available -- [skill] is not installed."
- **Skill fails (after retry)**: **Omit the section.** Do NOT attempt to fill in the section with your own content.
- **Web search returns no results (after retry)**: Omit the affected sub-sections. Do NOT fabricate company profiles, news, or financial data.
- **Not a prospect/self-service**: If capacity customer, hand off to `account_summarization`.
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
