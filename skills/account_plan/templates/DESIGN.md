# Generate Account Plan - Design Document

**Based on:** Block Account Success Plan report format

---

## CRITICAL: Match Block Report Format Exactly

This skill generates Account Plans that MUST match the Block report design. Each section below documents the exact HTML structure, CSS classes, and data elements required.

---

## Phase 1: Account Identification

### Step 1.1: Resolve Account via account-finder

Use the `account-finder` (`skills/account-finder/SKILL.md`) skill to resolve the company name to a Salesforce account. This returns:
- `account_id`, `account_name`
- Account team: AE (owner), SE, DM, RVP
- Segment, industry, sub-industry
- `IS_CAPACITY_CUSTOMER` flag

If multiple matches, `account-finder` handles disambiguation with the user.

### Step 1.2: Confirm Selection
If `account-finder` returns multiple candidates, it will ask the user to confirm before proceeding.

---

## Phase 2: Data Collection

### Step 2.1: Use Case Enriched Query

```sql
SELECT 
    uc.ACCOUNT_NAME, uc.SALESFORCE_ACCOUNT_ID, uc.USE_CASE_ID, uc.USE_CASE_NUMBER, uc.USE_CASE_NAME,
    uc.USE_CASE_ACV, uc.USE_CASE_STAGE, uc.DECISION_DATE,
    uc.MEDDPICC_CHAMPION as uc_champion_id,
    uc.MEDDPICC_CHAMPION_NAME as uc_champion,
    uc.USE_CASE_LEAD_SE_ID as uc_se_owner,
    uc.USE_CASE_COMMENTS, uc.NEXT_STEPS, uc.USE_CASE_RISK_LEVEL, uc.RISK_DESCRIPTION,
    'https://app.vivun.com/use-cases/' || uc.USE_CASE_ID as uc_url,
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
    WHERE SALESFORCE_ACCOUNT_ID = '{{ACCOUNT_ID}}'
        AND SNAPSHOT_TYPE = 'WEEKLY'
    QUALIFY ROW_NUMBER() OVER (PARTITION BY USE_CASE_NUMBER ORDER BY EXIT_SNAPSHOT_DATE DESC) = 1
) chg ON uc.USE_CASE_NUMBER = chg.USE_CASE_NUMBER
WHERE uc.SALESFORCE_ACCOUNT_ID = '{{ACCOUNT_ID}}'
ORDER BY uc.LAST_MODIFIED_DATE DESC
LIMIT 200
```

Note: Filter by `SALESFORCE_ACCOUNT_ID` (from account-finder), not `account_name` string match. The `uc_se_owner` returns an SE ID (not name) — resolve via account-finder's SE name if needed. **Important:** `uc_champion` and `uc_economic_buyer` are the display names. The `_id` columns are Salesforce Contact IDs — do not display those to users.

### Step 2.1A: Pre-Computed Stats (run in parallel with Step 2.1)

```sql
SELECT 
    USE_CASE_STATUS,
    USE_CASE_STAGE,
    COUNT(*) as UC_COUNT,
    ROUND(SUM(USE_CASE_ACV), 0) as TOTAL_ACV
FROM sales.raven.sda_use_case_view
WHERE SALESFORCE_ACCOUNT_ID = '{{ACCOUNT_ID}}'
GROUP BY USE_CASE_STATUS, USE_CASE_STAGE
ORDER BY USE_CASE_STAGE
```

**CRITICAL: Use these exact query results for all stat cards and header numbers. Do NOT manually count or sum rows from Step 2.1.**

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

### Step 2.2: AI Use Case Analysis (inline LLM)

After collecting use case data, analyze each use case by prompting the LLM with the raw data to produce structured AI analysis.

For each use case (or batch all into a single prompt), provide these fields as context:
- `USE_CASE_NAME`, `USE_CASE_STAGE`, `USE_CASE_ACV`, `DAYS_IN_STAGE`
- `USE_CASE_COMMENTS` (SE comments), `NEXT_STEPS`
- `USE_CASE_RISK_LEVEL`, `RISK_DESCRIPTION`
- `MEDDPICC_OVERALL_SCORE` + 7 component scores
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
> - `blocking_questions`: 2-4 unresolved questions derived from missing MEDDPICC fields, high risk, stalled stage, competitive threats.
> - `actionable_next_steps`: 2-4 concrete actions derived from current stage needs, MEDDPICC gaps, next steps field, competitive positioning.
> - `se_notes_summary`: Synthesize SE comments and next steps. If no comments exist, note "No SE comments recorded."
> - `meddpicc_analysis.score`: Use actual `MEDDPICC_OVERALL_SCORE` from data (do not recalculate).

The output feeds into Tabs 4, 5, 6, and 7. The data shape matches exactly what the HTML templates expect (same structure as the former `ai_analysis` JSON column).

### Step 2.3: Company Intelligence (replaces Snow Owl)

Run ALL of the following in parallel:

**Firmographics:**
```sql
SELECT * FROM TABLE(SALES.RAVEN.GET_3P_DATA('{{ACCOUNT_ID}}'))
```
Extracts: industry, annual revenue, employee count, key products, tech stack, website domain, market cap.

**Web Search (3 parallel calls):**
1. `web_search("{{ACCOUNT_NAME}} company profile products services {{INDUSTRY}}")` — company overview
2. `web_search("{{ACCOUNT_NAME}} strategic priorities CEO annual report investor day {{YEAR}}")` — board priorities, executive quotes
3. `web_search("{{ACCOUNT_NAME}} recent news AI data cloud competitors {{CURRENT_QUARTER}} {{YEAR}}")` — recent news, competitive landscape

Use `website_domain` from GET_3P_DATA to disambiguate web searches.

### Step 2.4: Contact Intelligence (parallel with Steps 2.1–2.3 — optional)

Run in parallel with the above. If queries fail, proceed without — Tab 2 renders from Use Case alone.

**High-Value Contacts:**
```sql
SELECT
    ci.contact_intelligence_type, ci.person_id, ci.name, ci.email, ci.title,
    ci.phone, ci.department, ci.role, ci.seniority, ci.status, ci.sub_status,
    ci.sla_status, ci.new_icp, ci.interesting_moment_date, ci.interesting_moment_desc,
    ci.account_name
FROM sales.raven.contact_intelligence_view ci
WHERE ci.salesforce_account_id = '{{ACCOUNT_ID}}'
ORDER BY CASE ci.contact_intelligence_type
    WHEN 'Quality Contact' THEN 1 WHEN 'Recent MQL' THEN 2
    WHEN 'Recently Engaged' THEN 3 WHEN 'Email Contact' THEN 4 ELSE 5 END
LIMIT 50
```

**Contact Engagement Velocity:**
```sql
SELECT
    ci.person_id, ci.name, ci.email, ci.title, ci.phone,
    ci.seniority, ci.department, ci.new_icp, ci.status,
    COUNT(CASE WHEN ci.interesting_moment_date >= CURRENT_DATE() - 30 THEN 1 END) AS touches_last_30d,
    COUNT(CASE WHEN ci.interesting_moment_date >= CURRENT_DATE() - 60 THEN 1 END) AS touches_last_60d,
    MAX(ci.interesting_moment_date) AS most_recent_touch,
    LISTAGG(DISTINCT ci.interesting_moment_type, ', ') WITHIN GROUP (ORDER BY ci.interesting_moment_type) AS touch_types
FROM sales.raven.contact_intelligence_view ci
WHERE ci.salesforce_account_id = '{{ACCOUNT_ID}}'
    AND ci.interesting_moment_date >= CURRENT_DATE() - 60
    AND ci.interesting_moment_source != 'Sumble'
GROUP BY ci.person_id, ci.name, ci.email, ci.title, ci.phone, ci.seniority, ci.department, ci.new_icp, ci.status
HAVING touches_last_30d >= 2
ORDER BY touches_last_30d DESC, most_recent_touch DESC
```

**Cross-referencing for Tab 2:**
- Fuzzy-match `ci.name` to use case `uc_champion` / `uc_economic_buyer`.
- Matched: enrich stakeholder card with `email`, `phone`, `title`, `seniority`, `department`, `new_icp`, velocity.
- Unmatched high-velocity contacts: add to Technical Champions grid as emerging contacts with velocity badge.
- Engagement dots: combine use case activity recency + contact-intelligence `touches_last_30d` when both available.
- Velocity badge class: `high` (5+ touches/30d), `medium` (3–4), `low` (2).

### Step 2.5: Cached Brief Recommendations (fast — try before SP)

Check if a recent workflow brief already contains use case recommendations for this account. This avoids the slow `RECO_FOR_PROSPECTING_SP_SALES()` call (~30s).

```sql
SELECT 
    f.value:header::STRING AS recommendation_header,
    f.value:summary::STRING AS recommendation_summary,
    f.value:details[0]:content::STRING AS recommendation_content
FROM SALES.RAVEN.WORKFLOW_EXECUTIONS,
    LATERAL FLATTEN(input => RESPONSE_PAYLOAD:payload) f
WHERE WORKFLOW_ID LIKE '%BRIEF'
  AND INPUTS:account_id::STRING = '{{ACCOUNT_ID}}'
  AND STATUS = 'COMPLETED'
  AND f.value:header::STRING IN ('Use Case Recommendations', 'Potential Snowflake Value Proposition')
  AND DATEDIFF('day', TRY_TO_TIMESTAMP(REPLACE(COMPLETED_AT::STRING, '"', '')), CURRENT_TIMESTAMP()) <= 30
ORDER BY COMPLETED_AT DESC
LIMIT 1;
```

- **Capacity accounts** → header = `Use Case Recommendations`
- **Prospect/self-serve accounts** → header = `Potential Snowflake Value Proposition`
- `recommendation_content` = full markdown with use case descriptions, reference customers, relevance, partners

**If a row is returned:** Use directly for Tab 8 Moonshot cards. Skip `RECO_FOR_PROSPECTING_SP_SALES()`.
**If no rows returned:** Fall back to the SP call (see ../SKILL.md Step 4B-ii).

---

## Phase 3: Complete CSS (COPY EXACTLY)

```css
:root {
    --primary: #29B5E8;
    --secondary: #1A1A2E;
    --accent: #00D4AA;
    --warning: #FF6B6B;
    --success: #4ECDC4;
    --gold: #FFD93D;
    --purple: #A855F7;
    --bg-dark: #0F0F1A;
    --bg-card: #1A1A2E;
    --text-primary: #FFFFFF;
    --text-secondary: #B0B0C0;
    --border: #2D2D44;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg-dark);
    color: var(--text-primary);
    line-height: 1.6;
}

.container { max-width: 1600px; margin: 0 auto; padding: 20px; }

header {
    background: linear-gradient(135deg, var(--secondary) 0%, #252542 100%);
    padding: 30px 40px;
    border-radius: 16px;
    margin-bottom: 30px;
    border: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-content h1 {
    font-size: 2.5rem;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.header-content p { color: var(--text-secondary); font-size: 1.1rem; }
.header-stats { display: flex; gap: 30px; }

.header-stat {
    text-align: center;
    padding: 15px 25px;
    background: rgba(41, 181, 232, 0.1);
    border-radius: 12px;
    border: 1px solid var(--primary);
}

.header-stat-value { font-size: 1.8rem; font-weight: 700; color: var(--primary); }
.header-stat-label { font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }

nav {
    display: flex;
    gap: 8px;
    margin-bottom: 30px;
    flex-wrap: wrap;
    background: var(--bg-card);
    padding: 12px;
    border-radius: 12px;
    border: 1px solid var(--border);
}

.nav-btn {
    padding: 12px 24px;
    background: transparent;
    color: var(--text-secondary);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.nav-btn:hover, .nav-btn.active { background: var(--primary); color: white; }

.section { display: none; }
.section.active { display: block; }

.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 24px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }

.card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid var(--border);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(41, 181, 232, 0.15);
}

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.card h3 { font-size: 1.2rem; color: var(--text-primary); margin-bottom: 8px; }
.card p { color: var(--text-secondary); font-size: 0.95rem; }

.badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-deployed { background: rgba(78, 205, 196, 0.2); color: var(--success); }
.badge-implementation { background: rgba(41, 181, 232, 0.2); color: var(--primary); }
.badge-validation { background: rgba(168, 85, 247, 0.2); color: var(--purple); }
.badge-scoping { background: rgba(255, 217, 61, 0.2); color: var(--gold); }
.badge-discovery { background: rgba(255, 107, 107, 0.2); color: var(--warning); }
.badge-lost { background: rgba(100, 100, 100, 0.2); color: #888; }

.section-title {
    font-size: 1.8rem;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border);
    display: flex;
    align-items: center;
    gap: 12px;
}

.section-title::before {
    content: '';
    width: 6px;
    height: 30px;
    background: linear-gradient(180deg, var(--primary), var(--accent));
    border-radius: 3px;
}

/* STAKEHOLDER CARDS - EXACT BLOCK STRUCTURE */
.stakeholder-card { position: relative; overflow: hidden; }
.stakeholder-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; }
.stakeholder-executive::before { background: var(--gold); }
.stakeholder-champion::before { background: var(--success); }
.stakeholder-technical::before { background: var(--primary); }
.stakeholder-influencer::before { background: var(--purple); }

.stakeholder-role { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px; }
.stakeholder-name { font-size: 1.3rem; font-weight: 600; margin-bottom: 4px; }
.stakeholder-title { font-size: 0.9rem; color: var(--primary); margin-bottom: 12px; }

/* ENGAGEMENT LEVEL DOTS (5-DOT SCALE) */
.engagement-level { display: flex; gap: 4px; margin-top: 12px; }
.engagement-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--border); }
.engagement-dot.active { background: var(--accent); }
.engagement-label { font-size: 0.75rem; color: var(--text-secondary); margin-left: 8px; }

/* STRATEGY CARDS WITH ALIGNMENT SCORES */
.strategy-card { background: linear-gradient(135deg, var(--bg-card) 0%, rgba(41, 181, 232, 0.05) 100%); }
.strategy-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.strategy-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }

/* ALIGNMENT SCORE BAR */
.alignment-score { display: flex; align-items: center; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.alignment-bar { flex: 1; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.alignment-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }

/* PIPELINE CARDS */
.pipeline-card { position: relative; }
.pipeline-value { font-size: 1.6rem; font-weight: 700; color: var(--primary); margin-bottom: 4px; }
.pipeline-stage { font-size: 0.85rem; padding: 4px 10px; background: rgba(41, 181, 232, 0.1); border-radius: 4px; display: inline-block; margin-bottom: 12px; }
.pipeline-champion { font-size: 0.9rem; color: var(--accent); margin-bottom: 8px; }
.pipeline-pitch { font-size: 0.85rem; color: var(--text-secondary); padding: 12px; background: rgba(0,0,0,0.2); border-radius: 8px; margin-top: 12px; }

/* BUSINESS UNIT CARDS (ORG UNIT) */
.bu-card { border-left: 4px solid; }
.bu-square { border-color: #00D4AA; }
.bu-cashapp { border-color: #00C244; }
.bu-afterpay { border-color: #B2FCE4; }
.bu-risk { border-color: #FF6B6B; }
.bu-platform { border-color: #A855F7; }

/* ORG UNIT STRUCTURE */
.org-unit { padding: 20px; border-radius: 12px; background: rgba(41, 181, 232, 0.05); border: 1px solid var(--border); margin-bottom: 16px; }
.org-unit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.org-unit-name { font-size: 1.1rem; font-weight: 600; }
.org-unit-stakeholders { display: flex; flex-wrap: wrap; gap: 8px; }

/* STAKEHOLDER CHIPS (ENGAGED/PARTIAL/GAP) */
.stakeholder-chip { padding: 6px 12px; background: var(--bg-card); border-radius: 20px; font-size: 0.85rem; border: 1px solid var(--border); }
.stakeholder-chip.engaged { border-color: var(--success); color: var(--success); }
.stakeholder-chip.partial { border-color: var(--gold); color: var(--gold); }
.stakeholder-chip.gap { border-color: var(--warning); color: var(--warning); }

/* METRICS TABLE */
.metrics-table { width: 100%; border-collapse: collapse; }
.metrics-table th, .metrics-table td { padding: 14px 16px; text-align: left; border-bottom: 1px solid var(--border); }
.metrics-table th { background: rgba(41, 181, 232, 0.1); font-weight: 600; color: var(--primary); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
.metrics-table tr:hover { background: rgba(41, 181, 232, 0.05); }

/* RISK CARDS */
.risk-card { border-left: 4px solid; }
.risk-high { border-color: var(--warning); }
.risk-medium { border-color: var(--gold); }
.risk-low { border-color: var(--success); }

.risk-indicator { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
.risk-indicator.high { background: rgba(255, 107, 107, 0.2); color: var(--warning); }
.risk-indicator.medium { background: rgba(255, 217, 61, 0.2); color: var(--gold); }
.risk-indicator.low { background: rgba(78, 205, 196, 0.2); color: var(--success); }

/* ACTION ITEMS */
.action-item { display: flex; gap: 16px; padding: 16px; background: rgba(0,0,0,0.2); border-radius: 12px; margin-bottom: 12px; align-items: flex-start; }
.action-priority { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; flex-shrink: 0; }
.action-priority.p1 { background: var(--warning); color: white; }
.action-priority.p2 { background: var(--gold); color: #1A1A2E; }
.action-priority.p3 { background: var(--primary); color: white; }

.action-content h4 { font-size: 1rem; margin-bottom: 4px; }
.action-content p { font-size: 0.9rem; color: var(--text-secondary); }
.action-meta { display: flex; gap: 16px; margin-top: 8px; font-size: 0.8rem; }
.action-meta span { color: var(--text-secondary); }

/* STAT CARDS */
.stat-card { text-align: center; padding: 30px 20px; }
.stat-value { font-size: 2.5rem; font-weight: 700; margin-bottom: 8px; }
.stat-value.green { color: var(--success); }
.stat-value.blue { color: var(--primary); }
.stat-value.gold { color: var(--gold); }
.stat-value.purple { color: var(--purple); }
.stat-label { font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }

/* AI SCORE INDICATORS */
.ai-score { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
.ai-score.excellent { background: rgba(78, 205, 196, 0.2); color: var(--success); }
.ai-score.good { background: rgba(41, 181, 232, 0.2); color: var(--primary); }
.ai-score.moderate { background: rgba(255, 217, 61, 0.2); color: var(--gold); }
.ai-score.poor { background: rgba(255, 107, 107, 0.2); color: var(--warning); }

/* SE NOTES BOX */
.se-notes-box {
    background: rgba(168, 85, 247, 0.1);
    border-left: 3px solid var(--purple);
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
}

/* BLOCKING QUESTIONS */
.blocking-questions {
    background: rgba(255, 107, 107, 0.1);
    border-left: 3px solid var(--warning);
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
}
.blocking-questions ul { margin: 8px 0 0 20px; font-size: 0.85rem; color: var(--text-secondary); }

/* DATA SOURCE TRANSPARENCY */
.data-source-indicator { position: relative; cursor: help; }
.data-source-indicator::after {
    content: attr(data-source);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: var(--secondary);
    color: var(--text-primary);
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.75rem;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    z-index: 1000;
    border: 1px solid var(--border);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.data-source-indicator:hover::after { opacity: 1; visibility: visible; bottom: calc(100% + 8px); }

.source-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 4px;
    font-size: 0.6rem;
    font-weight: 700;
    margin-left: 6px;
    vertical-align: middle;
}
.source-icon.uc-data { background: rgba(41, 181, 232, 0.3); color: var(--primary); }
.source-icon.ai { background: rgba(168, 85, 247, 0.3); color: var(--purple); }
.source-icon.web { background: rgba(0, 212, 170, 0.3); color: var(--accent); }
.source-icon.thirdparty { background: rgba(255, 217, 61, 0.3); color: var(--gold); }
.source-icon.reco { background: rgba(78, 205, 196, 0.3); color: var(--success); }
.source-icon.contacts { background: rgba(255, 152, 0, 0.3); color: #FF9800; }

/* CONTACT INTELLIGENCE ENRICHMENT */
.contact-detail {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
    font-size: 0.8rem;
    color: var(--text-secondary);
}
.contact-detail a { color: var(--primary); text-decoration: none; }
.contact-detail a:hover { text-decoration: underline; }
.contact-detail span { display: inline-flex; align-items: center; gap: 4px; }

.velocity-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 600;
}
.velocity-badge.high { background: rgba(255, 107, 107, 0.2); color: var(--warning); }
.velocity-badge.medium { background: rgba(255, 217, 61, 0.2); color: var(--gold); }
.velocity-badge.low { background: rgba(78, 205, 196, 0.2); color: var(--success); }

.stakeholder-emerging::before { background: #FF9800; }

.icp-badge {
    display: inline-flex;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: rgba(41, 181, 232, 0.2);
    color: var(--primary);
}

/* METADATA PANEL */
.metadata-panel {
    background: linear-gradient(135deg, rgba(41, 181, 232, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 24px;
    overflow: hidden;
}
.metadata-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: rgba(0,0,0,0.2);
    cursor: pointer;
    transition: background 0.2s ease;
}
.metadata-header:hover { background: rgba(0,0,0,0.3); }
.metadata-header h4 { display: flex; align-items: center; gap: 8px; font-size: 0.95rem; color: var(--text-secondary); }
.metadata-toggle { font-size: 1.2rem; color: var(--text-secondary); transition: transform 0.3s ease; }
.metadata-panel.expanded .metadata-toggle { transform: rotate(180deg); }
.metadata-content { max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }
.metadata-panel.expanded .metadata-content { max-height: 500px; }

.metadata-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; padding: 20px; }
.metadata-item { background: rgba(0,0,0,0.2); padding: 14px 16px; border-radius: 8px; border-left: 3px solid; }
.metadata-item.uc-data { border-color: var(--primary); }
.metadata-item.ai { border-color: var(--purple); }
.metadata-item.web { border-color: var(--accent); }
.metadata-item.thirdparty { border-color: var(--gold); }
.metadata-item.reco { border-color: var(--success); }
.metadata-item.contacts { border-color: #FF9800; }
.metadata-item.manual { border-color: var(--gold); }
.metadata-item h5 { font-size: 0.85rem; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.metadata-item p { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5; }
.metadata-item code { font-size: 0.7rem; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: var(--primary); }
.freshness-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; background: rgba(78, 205, 196, 0.2); color: var(--success); }
.freshness-badge.stale { background: rgba(255, 217, 61, 0.2); color: var(--gold); }

/* MOONSHOT CATEGORY BADGES */
.moonshot-category {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.moonshot-category.risk { background: rgba(41, 181, 232, 0.2); color: var(--primary); }
.moonshot-category.revenue { background: rgba(0, 212, 170, 0.2); color: var(--accent); }
.moonshot-category.efficiency { background: rgba(168, 85, 247, 0.2); color: var(--purple); }

/* MOONSHOT CARD */
.moonshot-card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.moonshot-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(41, 181, 232, 0.15);
}
.moonshot-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
}
.moonshot-card.risk-category::before { background: var(--primary); }
.moonshot-card.revenue-category::before { background: var(--accent); }
.moonshot-card.efficiency-category::before { background: var(--purple); }

.moonshot-title { font-size: 1.2rem; font-weight: 600; color: var(--text-primary); margin: 12px 0 8px; }
.moonshot-description { color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 16px; line-height: 1.6; }

/* CUSTOMER SUCCESS BOX */
.customer-success-box {
    background: rgba(0, 212, 170, 0.1);
    border-left: 3px solid var(--accent);
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
}
.customer-success-box strong { color: var(--accent); font-size: 0.8rem; }

/* CUSTOMER VALUE BOX */
.customer-value-box {
    background: rgba(76, 175, 80, 0.1);
    border-left: 3px solid var(--success);
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
}
.customer-value-box h5 {
    color: var(--success);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 6px 0;
}
.customer-value-box p {
    margin: 0;
    font-size: 0.85rem;
    color: var(--text-primary);
}

/* IMPACT ESTIMATE */
.impact-estimate {
    display: flex;
    gap: 16px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    flex-wrap: wrap;
}
.impact-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.impact-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.impact-value { font-size: 1rem; font-weight: 600; color: var(--primary); }
.impact-value.high { color: var(--success); }
.impact-value.medium { color: var(--gold); }

/* RELEVANCE SCORE */
.relevance-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.relevance-badge.high { background: rgba(78, 205, 196, 0.2); color: var(--success); }
.relevance-badge.medium { background: rgba(255, 217, 61, 0.2); color: var(--gold); }

/* STRATEGIC ALIGNMENT BOX */
.strategic-alignment-box {
    background: rgba(41, 181, 232, 0.08);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
}
.strategic-alignment-box h5 { font-size: 0.8rem; color: var(--primary); margin-bottom: 6px; }
.strategic-alignment-box p { font-size: 0.85rem; color: var(--text-secondary); }

/* STAKEHOLDER TAGS */
.stakeholder-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.stakeholder-tag {
    padding: 4px 12px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border);
    border-radius: 16px;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* SUMMARY BANNER */
.summary-banner {
    background: linear-gradient(135deg, rgba(41, 181, 232, 0.15) 0%, rgba(0, 212, 170, 0.15) 100%);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    border: 1px solid var(--primary);
}
.summary-banner h2 { font-size: 1.3rem; margin-bottom: 12px; color: var(--primary); }
.summary-banner p { color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7; }

/* QUOTE BLOCK */
.quote-block {
    padding: 20px;
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(41, 181, 232, 0.1) 100%);
    border-left: 4px solid var(--purple);
    border-radius: 0 12px 12px 0;
    margin: 16px 0;
}
.quote-block p { font-style: italic; color: var(--text-primary); margin-bottom: 8px; }
.quote-attribution { font-size: 0.85rem; color: var(--text-secondary); }

footer {
    margin-top: 40px;
    padding: 24px;
    background: var(--bg-card);
    border-radius: 16px;
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.9rem;
    border: 1px solid var(--border);
}

@media (max-width: 1200px) {
    .grid-4 { grid-template-columns: repeat(2, 1fr); }
    .grid-3 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
    header { flex-direction: column; gap: 20px; }
    .header-stats { flex-wrap: wrap; justify-content: center; }
}
```

---

## Phase 4: HTML Tab Templates (Match Block Report Exactly)

### Tab 1: Executive Overview

```html
<section id="overview" class="section active">
    <h2 class="section-title">Executive Overview</h2>
    
    <!-- Account Health Banner -->
    <div class="summary-banner">
        <h2>Account Health: {{HEALTH_ASSESSMENT}}</h2>
        <p>{{EXECUTIVE_SUMMARY}} <!-- 2-3 sentences about account state, key opportunity, risks --></p>
    </div>
    
    <!-- Stage Breakdown Stats (4-column) -->
    <div class="grid-4">
        <div class="card stat-card">
            <div class="stat-value green">{{DEPLOYED_COUNT}}</div>
            <div class="stat-label">Deployed Use Cases</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value blue">{{IMPLEMENTATION_COUNT}}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value gold">{{VALIDATION_COUNT}}</div>
            <div class="stat-label">In Validation</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value purple">{{DISCOVERY_COUNT}}</div>
            <div class="stat-label">In Discovery</div>
        </div>
    </div>
    
    <!-- Company Overview + Strategic Priorities (2-column) -->
    <!-- Company Overview: populated from GET_3P_DATA() -->
    <!-- Strategic Priorities: populated from web_search (strategic priorities query) -->
    <div class="grid-2">
        <div class="card">
            <h3>Company Overview</h3>
            <p style="margin-bottom: 16px;">{{COMPANY_DESCRIPTION}}</p>
            <table class="metrics-table">
                <tr><td>Industry</td><td>{{INDUSTRY}}</td></tr>
                <tr><td>Annual Revenue</td><td>{{REVENUE}}</td></tr>
                <tr><td>Employees</td><td>{{EMPLOYEES}}</td></tr>
                <tr><td>Key Products</td><td>{{KEY_PRODUCTS}}</td></tr>
                <tr><td>Market Cap</td><td>{{MARKET_CAP}}</td></tr>
            </table>
        </div>
        
        <div class="card">
            <h3>Strategic Priorities ({{YEAR}})</h3>
            <!-- Include quote block if available from web search -->
            <div class="quote-block">
                <p>"{{EXECUTIVE_QUOTE}}"</p>
                <div class="quote-attribution">- {{EXECUTIVE_NAME}}, {{EXECUTIVE_TITLE}}</div>
            </div>
            <ul style="padding-left: 20px; color: var(--text-secondary); font-size: 0.95rem;">
                <li style="margin-bottom: 8px;"><strong style="color: var(--primary);">{{PRIORITY_1_NAME}}:</strong> {{PRIORITY_1_DESC}}</li>
                <li style="margin-bottom: 8px;"><strong style="color: var(--primary);">{{PRIORITY_2_NAME}}:</strong> {{PRIORITY_2_DESC}}</li>
                <li style="margin-bottom: 8px;"><strong style="color: var(--primary);">{{PRIORITY_3_NAME}}:</strong> {{PRIORITY_3_DESC}}</li>
                <li style="margin-bottom: 8px;"><strong style="color: var(--primary);">{{PRIORITY_4_NAME}}:</strong> {{PRIORITY_4_DESC}}</li>
            </ul>
        </div>
    </div>
    
    <!-- Snowflake Relationship Summary (Strengths/Opportunities/Risks) -->
    <div class="card" style="margin-bottom: 24px;">
        <h3>Snowflake Relationship Summary</h3>
        <div class="grid-3" style="margin-top: 16px; margin-bottom: 0;">
            <div>
                <h4 style="color: var(--success); margin-bottom: 12px;">Strengths</h4>
                <ul style="padding-left: 20px; color: var(--text-secondary); font-size: 0.9rem;">
                    <li>{{STRENGTH_1}}</li>
                    <li>{{STRENGTH_2}}</li>
                    <li>{{STRENGTH_3}}</li>
                    <li>{{STRENGTH_4}}</li>
                    <li>{{STRENGTH_5}}</li>
                </ul>
            </div>
            <div>
                <h4 style="color: var(--gold); margin-bottom: 12px;">Opportunities</h4>
                <ul style="padding-left: 20px; color: var(--text-secondary); font-size: 0.9rem;">
                    <li>{{OPPORTUNITY_1}}</li>
                    <li>{{OPPORTUNITY_2}}</li>
                    <li>{{OPPORTUNITY_3}}</li>
                    <li>{{OPPORTUNITY_4}}</li>
                    <li>{{OPPORTUNITY_5}}</li>
                </ul>
            </div>
            <div>
                <h4 style="color: var(--warning); margin-bottom: 12px;">Risks</h4>
                <ul style="padding-left: 20px; color: var(--text-secondary); font-size: 0.9rem;">
                    <li>{{RISK_1}}</li>
                    <li>{{RISK_2}}</li>
                    <li>{{RISK_3}}</li>
                    <li>{{RISK_4}}</li>
                    <li>{{RISK_5}}</li>
                </ul>
            </div>
        </div>
    </div>
</section>
```

### Tab 2: Stakeholder Map

```html
<section id="stakeholders" class="section">
    <h2 class="section-title">Stakeholder Map</h2>
    
    <div class="summary-banner">
        <h2>Engagement Strategy</h2>
        <p>{{STAKEHOLDER_STRATEGY_SUMMARY}}</p>
    </div>

    <!-- Executive Leadership (3-column grid) -->
    <h3 style="margin: 24px 0 16px; color: var(--text-primary);">Executive Leadership</h3>
    <div class="grid-3">
        <!-- Repeat for each executive -->
        <div class="card stakeholder-card stakeholder-executive">
            <div class="stakeholder-role">{{ROLE_UPPERCASE}}</div>
            <div class="stakeholder-name">{{NAME}}</div>
            <div class="stakeholder-title">{{TITLE}}</div>
            <p style="font-size: 0.9rem;">{{DESCRIPTION}}</p>
            <!-- 5-DOT ENGAGEMENT SCALE — dots informed by contact-intelligence velocity when available -->
            <div class="engagement-level">
                <span class="engagement-dot {{ACTIVE_IF_1}}"></span>
                <span class="engagement-dot {{ACTIVE_IF_2}}"></span>
                <span class="engagement-dot {{ACTIVE_IF_3}}"></span>
                <span class="engagement-dot {{ACTIVE_IF_4}}"></span>
                <span class="engagement-dot {{ACTIVE_IF_5}}"></span>
                <span class="engagement-label">{{ENGAGEMENT_LABEL}}</span>
            </div>
            <!-- Contact Intelligence enrichment: render only when name matched from Step 2B -->
            <div class="contact-detail">
                <span>📧 <a href="mailto:{{EMAIL}}">{{EMAIL}}</a></span>
                <span>📱 {{PHONE}}</span>
                <span>{{SENIORITY}}</span>
                <!-- Omit any field that is NULL/empty from Step 2B -->
            </div>
        </div>
    </div>
    
    <!-- Technical Champions & Key Contacts (4-column grid) -->
    <!-- Includes use case champions enriched with contact-intelligence + emerging high-velocity contacts from Step 2B -->
    <h3 style="margin: 24px 0 16px; color: var(--text-primary);">Technical Champions & Key Contacts</h3>
    <div class="grid-4">
        <!-- Repeat for each use case champion (enriched with contact-intelligence when name matched) -->
        <div class="card stakeholder-card stakeholder-champion">
            <div class="stakeholder-role">{{DEPARTMENT}}</div>
            <div class="stakeholder-name">{{NAME}}</div>
            <div class="stakeholder-title">{{TITLE}}</div>
            <p style="font-size: 0.85rem;">{{INFLUENCE_DESC}} ${{ACV_INFLUENCE}}+ influence.</p>
            <div class="engagement-level">
                <!-- 5 dots — combine use case recency with contact-intelligence velocity when available -->
                <span class="engagement-label">{{ENGAGEMENT_LABEL}}</span>
            </div>
            <!-- Contact Intelligence enrichment: render only when name matched from Step 2B -->
            <div class="contact-detail">
                <span>📧 <a href="mailto:{{EMAIL}}">{{EMAIL}}</a></span>
                <span>📱 {{PHONE}}</span>
                <span>{{SENIORITY}}</span>
                <span class="icp-badge" title="ICP Status">{{NEW_ICP}}</span>
                <!-- Omit any field that is NULL/empty from Step 2B -->
            </div>
        </div>
        <!-- Emerging contacts: high-velocity contacts from Step 2B-ii NOT matching any use case champion -->
        <div class="card stakeholder-card stakeholder-emerging">
            <div class="stakeholder-role">{{DEPARTMENT}} <span class="velocity-badge {{VELOCITY_CLASS}}">{{TOUCHES_LAST_30D}} touches/30d</span></div>
            <div class="stakeholder-name">{{NAME}} <span class="source-icon contacts" title="Contact Intelligence">CI</span></div>
            <div class="stakeholder-title">{{TITLE}}</div>
            <p style="font-size: 0.85rem;">Emerging contact — {{TOUCH_TYPES}}</p>
            <div class="contact-detail">
                <span>📧 <a href="mailto:{{EMAIL}}">{{EMAIL}}</a></span>
                <span>📱 {{PHONE}}</span>
                <span>{{SENIORITY}}</span>
                <span class="icp-badge" title="ICP Status">{{NEW_ICP}}</span>
            </div>
        </div>
    </div>
    
    <!-- Business Unit Engagement Map (2-column grid with org-unit cards) -->
    <h3 style="margin: 24px 0 16px; color: var(--text-primary);">Business Unit Engagement Map</h3>
    <div class="grid-2">
        <!-- Repeat for each business unit -->
        <div class="card org-unit">
            <div class="org-unit-header">
                <div class="org-unit-name" style="color: {{BU_COLOR}};">{{BU_NAME}}</div>
                <span class="badge badge-{{ENGAGEMENT_BADGE}}">{{ENGAGEMENT_STATUS}}</span>
            </div>
            <p style="font-size: 0.9rem; margin-bottom: 12px;">{{BU_DESCRIPTION}}</p>
            <!-- Stakeholder chips with engagement status -->
            <div class="org-unit-stakeholders">
                <span class="stakeholder-chip engaged">{{ENGAGED_STAKEHOLDER_1}}</span>
                <span class="stakeholder-chip engaged">{{ENGAGED_STAKEHOLDER_2}}</span>
                <span class="stakeholder-chip partial">{{PARTIAL_STAKEHOLDER}}</span>
                <span class="stakeholder-chip gap">{{GAP_STAKEHOLDER}}</span>
            </div>
        </div>
    </div>
    
    <!-- Engagement Gaps & Action Required -->
    <div class="card" style="margin-top: 24px;">
        <h3>Engagement Gaps & Action Required</h3>
        <div class="grid-3" style="margin-top: 16px; margin-bottom: 0;">
            <div class="risk-card risk-high" style="padding: 16px; border-radius: 8px; background: rgba(255,107,107,0.05);">
                <span class="risk-indicator high">HIGH PRIORITY</span>
                <h4 style="margin: 12px 0 8px;">{{GAP_TITLE}}</h4>
                <p style="font-size: 0.9rem; color: var(--text-secondary);">{{GAP_DESCRIPTION}}</p>
            </div>
            <div class="risk-card risk-medium" style="padding: 16px; border-radius: 8px; background: rgba(255,217,61,0.05);">
                <span class="risk-indicator medium">MEDIUM PRIORITY</span>
                <h4 style="margin: 12px 0 8px;">{{GAP_TITLE}}</h4>
                <p style="font-size: 0.9rem; color: var(--text-secondary);">{{GAP_DESCRIPTION}}</p>
            </div>
        </div>
    </div>
</section>
```

### Tab 3: Strategic Execution

```html
<section id="strategy" class="section">
    <h2 class="section-title">Strategic Execution Analysis</h2>
    
    <div class="summary-banner">
        <h2>{{ACCOUNT_NAME}}'s Strategic Vision</h2>
        <p>{{STRATEGIC_VISION_SUMMARY}}</p>
    </div>

    <!-- Strategic Priority Alignment Table -->
    <!-- Priorities sourced from web_search; UC coverage from use case data -->
    <div class="card">
        <h3>How Snowflake is Operating Against {{ACCOUNT_NAME}}'s Strategic Priorities</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">Analysis of current pipeline execution against strategic alignment areas.</p>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Strategic Priority</th>
                    <th>Execution Status</th>
                    <th>Pipeline Coverage</th>
                    <th>Verdict</th>
                </tr>
            </thead>
            <tbody>
                <!-- Repeat for each priority -->
                <tr>
                    <td><strong>{{PRIORITY_NAME}}</strong><br><span style="color: var(--text-secondary); font-size: 0.85rem;">{{PRIORITY_DESC}}</span></td>
                    <td>{{EXECUTION_STATUS}}</td>
                    <td>${{DEPLOYED}} deployed<br>${{PIPELINE}} in pursuit</td>
                    <td><span class="badge badge-{{VERDICT_CLASS}}">{{VERDICT}}</span></td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Summary stats (4-column) -->
    <div class="grid-4" style="margin-top: 24px;">
        <div class="card stat-card">
            <div class="stat-value gold">{{COVERED_COUNT}} of {{TOTAL_PRIORITIES}}</div>
            <div class="stat-label">Priorities Well-Covered</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value" style="color: var(--warning);">{{GAP_COUNT}}</div>
            <div class="stat-label">Major Gaps</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value" style="color: var(--warning);">${{AT_RISK_ACV}}</div>
            <div class="stat-label">At Risk</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value green">${{ADDRESSABLE_GAP}}</div>
            <div class="stat-label">Addressable Gap EACV</div>
        </div>
    </div>

    <!-- Strategy Priority Deep Dives (2-column with alignment bars) -->
    <h3 style="margin: 32px 0 16px; color: var(--text-primary);">Strategic Priority Deep Dives</h3>
    <div class="grid-2">
        <!-- Repeat for each priority card -->
        <div class="card strategy-card">
            <div class="strategy-header">
                <div class="strategy-icon" style="background: {{ICON_BG}};">{{ICON}}</div>
                <div>
                    <h3>{{PRIORITY_TITLE}}</h3>
                    <span class="badge badge-{{STATUS_CLASS}}">{{STATUS}}</span>
                </div>
            </div>
            <p style="margin-bottom: 16px;">{{MARKET_CONTEXT}}</p>
            <h4 style="margin-bottom: 8px; color: var(--primary);">Current Snowflake Engagement</h4>
            <ul style="padding-left: 20px; font-size: 0.9rem; color: var(--text-secondary);">
                <li>{{ENGAGEMENT_POINT_1}}</li>
                <li>{{ENGAGEMENT_POINT_2}}</li>
                <li>{{ENGAGEMENT_POINT_3}}</li>
            </ul>
            <!-- ALIGNMENT SCORE BAR -->
            <div class="alignment-score">
                <span style="font-size: 0.85rem; color: var(--text-secondary);">Alignment:</span>
                <div class="alignment-bar">
                    <div class="alignment-fill" style="width: {{ALIGNMENT_PCT}}%; background: {{ALIGNMENT_COLOR}};"></div>
                </div>
                <span style="font-size: 0.85rem; color: {{ALIGNMENT_TEXT_COLOR}};">{{ALIGNMENT_PCT}}%</span>
            </div>
        </div>
    </div>

    <!-- AT RISK / GAP Deep Dives (full-width risk cards) -->
    <div class="card risk-card risk-high" style="margin-top: 24px; border-left-width: 4px;">
        <h3 style="color: var(--warning);">AT RISK: {{RISK_TITLE}}</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">{{RISK_SUMMARY}}</p>
        
        <div class="grid-2">
            <div>
                <h4 style="color: var(--primary); margin-bottom: 10px;">Target Stakeholders</h4>
                <div class="card stakeholder-card stakeholder-technical" style="margin-bottom: 10px;">
                    <div class="stakeholder-name">{{STAKEHOLDER_NAME}}</div>
                    <div class="stakeholder-title">{{STAKEHOLDER_TITLE}}</div>
                    <p style="font-size: 0.85rem;">{{STAKEHOLDER_CONTEXT}}</p>
                </div>
                <h4 style="color: var(--primary); margin-bottom: 10px; margin-top: 20px;">Target Teams</h4>
                <ul style="color: var(--text-secondary); padding-left: 20px; font-size: 0.9rem;">
                    <li>{{TARGET_TEAM_1}}</li>
                    <li>{{TARGET_TEAM_2}}</li>
                </ul>
            </div>
            <div>
                <h4 style="color: var(--primary); margin-bottom: 10px;">Positioning & Messaging</h4>
                <div style="padding: 16px; background: rgba(0,212,170,0.1); border-radius: 8px; margin-bottom: 12px;">
                    <h4 style="color: var(--accent); margin-bottom: 8px;">{{POSITIONING_TITLE}}</h4>
                    <p style="font-size: 0.85rem; color: var(--text-secondary);">"{{POSITIONING_MESSAGE}}"</p>
                </div>
                <h4 style="color: var(--primary); margin-bottom: 10px; margin-top: 20px;">EACV Opportunity</h4>
                <p style="font-size: 1.5rem; color: var(--success); font-weight: bold;">${{EACV_RANGE}}</p>
                <p style="color: var(--text-secondary); font-size: 0.85rem;">{{EACV_BREAKDOWN}}</p>
            </div>
        </div>
    </div>

    <!-- Competitive Intelligence -->
    <!-- Sourced from web_search (news/competitors query) + GET_3P_DATA tech stack -->
    <div class="card" style="margin-top: 24px;">
        <h3>Competitive Intelligence: {{COMPETITOR_NAME}} Positioning</h3>
        <p style="margin: 16px 0; color: var(--text-secondary);">{{COMPETITIVE_CONTEXT}}</p>
        <div class="grid-3" style="margin-top: 16px; margin-bottom: 0;">
            <div style="padding: 16px; background: rgba(255,107,107,0.1); border-radius: 8px;">
                <h4 style="color: var(--warning); margin-bottom: 8px;">{{COMPETITOR}} Strengths</h4>
                <ul style="padding-left: 16px; font-size: 0.85rem; color: var(--text-secondary);">
                    <li>{{COMPETITOR_STRENGTH_1}}</li>
                    <li>{{COMPETITOR_STRENGTH_2}}</li>
                </ul>
            </div>
            <div style="padding: 16px; background: rgba(41,181,232,0.1); border-radius: 8px;">
                <h4 style="color: var(--primary); margin-bottom: 8px;">Snowflake Differentiators</h4>
                <ul style="padding-left: 16px; font-size: 0.85rem; color: var(--text-secondary);">
                    <li>{{SF_DIFFERENTIATOR_1}}</li>
                    <li>{{SF_DIFFERENTIATOR_2}}</li>
                </ul>
            </div>
            <div style="padding: 16px; background: rgba(0,212,170,0.1); border-radius: 8px;">
                <h4 style="color: var(--accent); margin-bottom: 8px;">Win Strategy</h4>
                <ul style="padding-left: 16px; font-size: 0.85rem; color: var(--text-secondary);">
                    <li>{{WIN_STRATEGY_1}}</li>
                    <li>{{WIN_STRATEGY_2}}</li>
                </ul>
            </div>
        </div>
    </div>
</section>
```

### Tab 4: Pipeline Coverage

```html
<section id="pipeline" class="section">
    <h2 class="section-title">Pipeline Coverage Map</h2>
    
    <!-- Pipeline Stage Stats (4-column) -->
    <div class="grid-4" style="margin-bottom: 32px;">
        <div class="card stat-card">
            <div class="stat-value green">${{DEPLOYED_ACV}}</div>
            <div class="stat-label">Deployed</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value blue">${{IMPLEMENTATION_ACV}}</div>
            <div class="stat-label">Implementation</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value gold">${{VALIDATION_SCOPING_ACV}}</div>
            <div class="stat-label">Validation/Scoping</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value purple">${{DISCOVERY_ACV}}</div>
            <div class="stat-label">Discovery</div>
        </div>
    </div>
    
    <!-- Metadata Panel -->
    <div class="metadata-panel" id="pipeline-metadata">
        <div class="metadata-header" onclick="toggleMetadata('pipeline-metadata')">
            <h4><span>📊</span> Data Sources & Transparency</h4>
            <span class="metadata-toggle">▼</span>
        </div>
        <div class="metadata-content">
            <div class="metadata-grid">
                <div class="metadata-item uc-data">
                    <h5 style="color: var(--primary);"><span class="source-icon uc-data">UC</span> Use Case Pipeline Data</h5>
                    <p>ACV, stage, decision dates, champion details, MEDDPICC scores</p>
                    <p style="margin-top: 8px;"><code>sales.raven.sda_use_case_view</code></p>
                    <span class="freshness-badge">Updated: {{UC_DATA_DATE}}</span>
                </div>
                <div class="metadata-item ai">
                    <h5 style="color: var(--purple);"><span class="source-icon ai">AI</span> AI Health Scores & Summaries</h5>
                    <p>Overall scores (0-100), SE notes summaries, blocking questions</p>
                    <p style="margin-top: 8px;"><code>Inline LLM analysis (Step 2.2)</code></p>
                    <span class="freshness-badge">Generated: Live</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Active Pipeline Cards with AI Enrichment (3-column) -->
    <h3 style="margin: 24px 0 16px;">Active Pipeline - AI-Enriched Analysis <span class="source-icon uc-data data-source-indicator" data-source="Source: Use Case + AI Analysis">UC</span></h3>
    <div class="grid-3">
        <!-- Repeat for each pipeline use case -->
        <div class="card pipeline-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <span class="badge badge-{{STAGE_CLASS}}">{{STAGE}}</span>
                <span class="ai-score {{AI_SCORE_CLASS}}">AI: {{AI_SCORE}}</span>
            </div>
            <h3 style="margin-top: 12px;">{{UC_NAME}} <a href="{{UC_URL}}" target="_blank" title="View in Salesforce" style="color: var(--primary); font-size: 0.8rem; text-decoration: none;">🔗</a></h3>
            <div class="pipeline-value">${{ACV}}</div>
            <div class="pipeline-champion">Champion: {{CHAMPION}}</div>
            <p style="font-size: 0.9rem; margin-bottom: 8px;">{{UC_DESCRIPTION}}</p>
            
            <!-- SE NOTES BOX (purple) -->
            <div class="se-notes-box" style="margin-top: 8px;">
                <strong style="color: var(--purple); font-size: 0.8rem;">AI Summary:</strong> <span style="font-size: 0.85rem;">{{SE_NOTES_SUMMARY}}</span>
            </div>
            
            <!-- BLOCKING QUESTIONS (red) - only if present -->
            <div class="blocking-questions" style="margin-top: 8px;">
                <strong style="color: var(--warning); font-size: 0.8rem;">Blocking:</strong>
                <ul style="margin-top: 4px;">
                    <li>{{BLOCKING_Q_1}}</li>
                    <li>{{BLOCKING_Q_2}}</li>
                </ul>
            </div>
            
            <!-- AI Next Steps -->
            <div class="pipeline-pitch">
                <strong>AI Next Steps:</strong> {{AI_NEXT_STEPS}}
            </div>
        </div>
    </div>
    
    <!-- Emerging Opportunities (4-column, simpler cards) -->
    <h3 style="margin: 32px 0 16px;">Emerging Opportunities</h3>
    <div class="grid-4">
        <div class="card pipeline-card">
            <span class="badge badge-{{STAGE_CLASS}}">{{STAGE}}</span>
            <h3 style="margin-top: 12px;">{{UC_NAME}}</h3>
            <div class="pipeline-value">${{ACV}}</div>
            <div class="pipeline-champion">Champion: {{CHAMPION}}</div>
            <p style="font-size: 0.85rem;">{{BRIEF_DESC}}</p>
        </div>
    </div>
    
    <!-- Pipeline Gap Analysis -->
    <div class="card" style="margin-top: 24px;">
        <h3>Pipeline Gap Analysis</h3>
        <div class="grid-2" style="margin-top: 16px; margin-bottom: 0;">
            <div>
                <h4 style="color: var(--warning); margin-bottom: 12px;">Whitespace Opportunities</h4>
                <table class="metrics-table">
                    <tr><td>{{WHITESPACE_1}}</td><td>{{STATUS_1}}</td><td>{{CONTEXT_1}}</td></tr>
                    <tr><td>{{WHITESPACE_2}}</td><td>{{STATUS_2}}</td><td>{{CONTEXT_2}}</td></tr>
                </table>
            </div>
            <div>
                <h4 style="color: var(--success); margin-bottom: 12px;">Competitive Positioning Needed</h4>
                <table class="metrics-table">
                    <tr><td>{{POSITIONING_1}}</td><td>{{PRIORITY_1}}</td><td>{{ACTION_1}}</td></tr>
                    <tr><td>{{POSITIONING_2}}</td><td>{{PRIORITY_2}}</td><td>{{ACTION_2}}</td></tr>
                </table>
            </div>
        </div>
    </div>
</section>
```

### Tab 5: Use Case Health

```html
<section id="usecases" class="section">
    <h2 class="section-title">Use Case Health Dashboard</h2>
    
    <!-- Metadata Panel -->
    <div class="metadata-panel" id="usecases-metadata">
        <div class="metadata-header" onclick="toggleMetadata('usecases-metadata')">
            <h4><span>📊</span> Data Sources & Transparency</h4>
            <span class="metadata-toggle">▼</span>
        </div>
        <div class="metadata-content">
            <div class="metadata-grid">
                <div class="metadata-item uc-data">
                    <h5 style="color: var(--primary);"><span class="source-icon uc-data">UC</span> Use Case Core Data</h5>
                    <p>Use case details, ACV, stage, champions, MEDDPICC fields</p>
                    <p style="margin-top: 8px;"><code>sales.raven.sda_use_case_view</code></p>
                    <span class="freshness-badge">Updated: {{UC_DATA_DATE}}</span>
                </div>
                <div class="metadata-item ai">
                    <h5 style="color: var(--purple);"><span class="source-icon ai">AI</span> AI Analysis</h5>
                    <p>Health scores, SE notes summaries, blocking questions, next steps</p>
                    <p style="margin-top: 8px;"><code>Inline LLM analysis (Step 2.2)</code></p>
                    <span class="freshness-badge">Generated: Live</span>
                </div>
                <div class="metadata-item uc-data">
                    <h5 style="color: var(--primary);"><span class="source-icon uc-data">UC</span> Use Case Risk Fields</h5>
                    <p>Risk level, risk description, champion changes from comparison view</p>
                    <span class="freshness-badge">Updated: {{UC_DATA_DATE}}</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="summary-banner">
        <h2>AI-Identified Risk Factors & Blocking Questions <span class="source-icon ai data-source-indicator" data-source="Source: Use Case AI Analysis">AI</span></h2>
        <p>{{RISK_FACTORS_SUMMARY}}</p>
    </div>
    
    <!-- AI-Surfaced Blocking Questions by Use Case (2-column) -->
    <h3 style="margin: 24px 0 16px;">AI-Surfaced Blocking Questions by Use Case</h3>
    <div class="grid-2" style="margin-bottom: 24px;">
        <!-- Repeat for each UC with blocking questions -->
        <div class="card blocking-questions" style="border-left-width: 4px; border-radius: 12px;">
            <h4 style="color: var(--warning); margin-bottom: 12px;">{{UC_NAME}} (${{ACV}}) <a href="{{UC_URL}}" target="_blank" style="color: var(--primary); font-size: 0.8rem;">🔗</a></h4>
            <ul>
                <li>{{BLOCKING_Q_1}}</li>
                <li>{{BLOCKING_Q_2}}</li>
                <li>{{BLOCKING_Q_3}}</li>
            </ul>
        </div>
    </div>
    
    <!-- Critical Risks vs Engagement Gaps (2-column) -->
    <div class="grid-2" style="margin-bottom: 24px;">
        <div class="card">
            <h3 style="color: var(--warning);">Critical Risks</h3>
            <div class="action-item" style="margin-top: 16px;">
                <div class="action-priority p1">1</div>
                <div class="action-content">
                    <h4>{{RISK_TITLE}}</h4>
                    <p>{{RISK_DESCRIPTION}}</p>
                    <div class="se-notes-box" style="margin-top: 8px;">
                        <strong style="color: var(--purple);">AI Analysis:</strong> {{AI_RISK_ANALYSIS}}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 style="color: var(--gold);">Engagement Gaps</h3>
            <div class="action-item" style="margin-top: 16px;">
                <div class="action-priority p2">A</div>
                <div class="action-content">
                    <h4>{{GAP_TITLE}}</h4>
                    <p>{{GAP_DESCRIPTION}}</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Competitive Threat Assessment Table -->
    <div class="card">
        <h3>Competitive Threat Assessment</h3>
        <table class="metrics-table" style="margin-top: 16px;">
            <thead>
                <tr>
                    <th>Competitor</th>
                    <th>Threat Level</th>
                    <th>Account Usage</th>
                    <th>Counter-Strategy</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>{{COMPETITOR_1}}</strong></td>
                    <td><span class="risk-indicator {{THREAT_CLASS_1}}">{{THREAT_LEVEL_1}}</span></td>
                    <td>{{USAGE_1}}</td>
                    <td>{{COUNTER_1}}</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <!-- Product Gap Impact (3-column) -->
    <div class="card" style="margin-top: 24px;">
        <h3>Product Gap Impact</h3>
        <div class="grid-3" style="margin-top: 16px; margin-bottom: 0;">
            <div style="padding: 16px; background: rgba(255,107,107,0.1); border-radius: 8px;">
                <h4 style="color: var(--warning); margin-bottom: 8px;">Blocking</h4>
                <ul style="padding-left: 16px; font-size: 0.85rem; color: var(--text-secondary);">
                    <li>{{BLOCKING_GAP_1}}</li>
                    <li>{{BLOCKING_GAP_2}}</li>
                </ul>
            </div>
            <div style="padding: 16px; background: rgba(255,217,61,0.1); border-radius: 8px;">
                <h4 style="color: var(--gold); margin-bottom: 8px;">Impacting</h4>
                <ul style="padding-left: 16px; font-size: 0.85rem; color: var(--text-secondary);">
                    <li>{{IMPACTING_GAP_1}}</li>
                    <li>{{IMPACTING_GAP_2}}</li>
                </ul>
            </div>
            <div style="padding: 16px; background: rgba(78,205,196,0.1); border-radius: 8px;">
                <h4 style="color: var(--success); margin-bottom: 8px;">Resolved</h4>
                <ul style="padding-left: 16px; font-size: 0.85rem; color: var(--text-secondary);">
                    <li>{{RESOLVED_GAP_1}}</li>
                    <li>{{RESOLVED_GAP_2}}</li>
                </ul>
            </div>
        </div>
    </div>
</section>
```

### Tab 6: Risks & Gaps

This tab follows the same structure as Tab 5 (Use Case Health). Key elements:
- Metadata panel with data sources
- Summary banner with risk factors
- AI-surfaced blocking questions grid
- Critical risks with AI analysis boxes
- Engagement gaps
- Competitive threat assessment table
- Product gap impact (Blocking/Impacting/Resolved)

### Tab 7: Next Actions

```html
<section id="actions" class="section">
    <h2 class="section-title">Next Actions & Pursuit Strategy</h2>
    
    <!-- Metadata Panel -->
    <div class="metadata-panel" id="actions-metadata">
        <div class="metadata-header" onclick="toggleMetadata('actions-metadata')">
            <h4><span>📊</span> Data Sources & Transparency</h4>
            <span class="metadata-toggle">▼</span>
        </div>
        <div class="metadata-content">
            <div class="metadata-grid">
                <div class="metadata-item ai">
                    <h5 style="color: var(--purple);"><span class="source-icon ai">AI</span> AI-Generated Next Steps</h5>
                    <p>Automated actionable recommendations extracted from AI analysis</p>
                    <p style="margin-top: 8px;"><code>ai_analysis.actionable_next_steps</code></p>
                    <span class="freshness-badge">Updated: {{AI_DATE}}</span>
                </div>
                <div class="metadata-item uc-data">
                    <h5 style="color: var(--primary);"><span class="source-icon uc-data">UC</span> Use Case SE Comments</h5>
                    <p>Latest SE updates and next steps from use case records</p>
                    <p style="margin-top: 8px;"><code>uc_se_comments, uc_next_step</code></p>
                    <span class="freshness-badge">Updated: {{UC_DATA_DATE}}</span>
                </div>
                <div class="metadata-item manual">
                    <h5 style="color: var(--gold);"><span class="source-icon" style="background: rgba(255,217,61,0.3); color: var(--gold);">M</span> Account Team (from account-finder)</h5>
                    <p>AE, SE, DM, RVP assignments from Salesforce account team</p>
                    <p style="margin-top: 8px;"><code>d_salesforce_account_customers</code></p>
                    <span class="freshness-badge">Updated: {{ACCOUNT_DATE}}</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="summary-banner">
        <h2>{{QUARTER}} {{YEAR}} Focus Areas</h2>
        <p>{{FOCUS_AREAS_NUMBERED_LIST}}</p>
    </div>
    
    <!-- Priority 1: Immediate Actions (30 Days) -->
    <h3 style="margin: 24px 0 16px;">Priority 1: AI-Derived Immediate Actions (Next 30 Days)</h3>
    <div class="action-item">
        <div class="action-priority p1">1</div>
        <div class="action-content">
            <h4>{{ACTION_TITLE}}</h4>
            <p>{{ACTION_DESCRIPTION}}</p>
            <div class="se-notes-box" style="margin-top: 8px; margin-bottom: 8px;">
                <strong style="color: var(--purple);">AI-Generated Action:</strong> {{AI_ACTION_DETAIL}}
            </div>
            <div class="action-meta">
                <span>Owner: {{OWNER}}</span>
                <span>Due: {{DUE_DATE}}</span>
                <span>Stakeholder: {{STAKEHOLDER}}</span>
            </div>
        </div>
    </div>
    
    <!-- Priority 2: Near-Term Actions (30-60 Days) -->
    <h3 style="margin: 32px 0 16px;">Priority 2: Near-Term Actions (30-60 Days)</h3>
    <div class="action-item">
        <div class="action-priority p2">4</div>
        <div class="action-content">
            <h4>{{ACTION_TITLE}}</h4>
            <p>{{ACTION_DESCRIPTION}}</p>
            <div class="action-meta">
                <span>Owner: {{OWNER}}</span>
                <span>Due: {{DUE_DATE}}</span>
                <span>Stakeholder: {{STAKEHOLDER}}</span>
            </div>
        </div>
    </div>
    
    <!-- Priority 3: Strategic Actions (60-90 Days) -->
    <h3 style="margin: 32px 0 16px;">Priority 3: Strategic Actions (60-90 Days)</h3>
    <div class="action-item">
        <div class="action-priority p3">7</div>
        <div class="action-content">
            <h4>{{ACTION_TITLE}}</h4>
            <p>{{ACTION_DESCRIPTION}}</p>
            <div class="action-meta">
                <span>Owner: {{OWNER}}</span>
                <span>Due: {{DUE_DATE}}</span>
                <span>Stakeholder: {{STAKEHOLDER}}</span>
            </div>
        </div>
    </div>
    
    <!-- Account Team Assignments — populated from account-finder metadata -->
    <div class="card" style="margin-top: 24px;">
        <h3>Account Team Assignments</h3>
        <table class="metrics-table" style="margin-top: 16px;">
            <thead>
                <tr>
                    <th>Role</th>
                    <th>Name</th>
                    <th>Primary Responsibilities</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Account Executive</td>
                    <td>{{AE_NAME}}</td>
                    <td>{{AE_RESPONSIBILITIES}}</td>
                </tr>
                <tr>
                    <td>Solution Engineer (Primary)</td>
                    <td>{{SE_NAME}}</td>
                    <td>{{SE_RESPONSIBILITIES}}</td>
                </tr>
                <tr>
                    <td>District Manager</td>
                    <td>{{DM_NAME}}</td>
                    <td>{{DM_RESPONSIBILITIES}}</td>
                </tr>
                <tr>
                    <td>Regional VP</td>
                    <td>{{RVP_NAME}}</td>
                    <td>{{RVP_RESPONSIBILITIES}}</td>
                </tr>
            </tbody>
        </table>
    </div>
</section>
```

### Tab 8: Moonshot Ideas

```html
<section id="moonshots" class="section">
    <h2 class="section-title">Moonshot Ideas</h2>
    
    <!-- Metadata Panel -->
    <div class="metadata-panel" id="moonshots-metadata">
        <div class="metadata-header" onclick="toggleMetadata('moonshots-metadata')">
            <h4><span>🚀</span> Data Sources & Intelligence</h4>
            <span class="metadata-toggle">▼</span>
        </div>
        <div class="metadata-content">
            <div class="metadata-grid">
                <div class="metadata-item web">
                    <h5 style="color: var(--accent);"><span class="source-icon web">W</span> Web Research + 3P Data</h5>
                    <p>Company profile, strategic priorities, recent news, firmographics, tech stack</p>
                    <p style="margin-top: 8px;"><code>web_search + GET_3P_DATA()</code></p>
                    <span class="freshness-badge">Updated: {{WEB_DATE}}</span>
                </div>
                <div class="metadata-item reco">
                    <h5 style="color: var(--success);"><span class="source-icon reco">R</span> Use Case Recommender</h5>
                    <p>Industry-matched recommendations from cached brief or SP fallback</p>
                    <p style="margin-top: 8px;"><code>WORKFLOW_EXECUTIONS → RECO_FOR_PROSPECTING_SP_SALES()</code></p>
                    <span class="freshness-badge">Updated: {{RECO_DATE}}</span>
                </div>
                <div class="metadata-item uc-data">
                    <h5 style="color: var(--primary);"><span class="source-icon uc-data">UC</span> Industry Comparison Data</h5>
                    <p>Successful use cases from similar accounts with comparable workloads</p>
                    <p style="margin-top: 8px;"><code>30+ deployed use cases analyzed</code></p>
                    <span class="freshness-badge">Updated: {{UC_DATA_DATE}}</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="summary-banner">
        <h2>Strategic Innovation Opportunities for {{ACCOUNT_NAME}}</h2>
        <p>{{MOONSHOT_SUMMARY}} The following moonshot ideas are designed to deepen strategic engagement and drive transformational value across three key areas: risk reduction, new revenue enablement, and operational efficiency.</p>
    </div>
    
    <!-- Category Section: Risk Reduction -->
    <h3 style="margin: 32px 0 16px; color: var(--primary); display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">🛡️</span> Risk Reduction
        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: normal;">Ideas that reduce operational, compliance, or technology risk</span>
    </h3>
    <div class="grid-2">
        <!-- Repeat for each Risk Reduction moonshot -->
        <div class="moonshot-card risk-category">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <span class="moonshot-category risk">🛡️ Risk Reduction</span>
                <span class="relevance-badge {{RELEVANCE_CLASS}}">{{RELEVANCE_SCORE}}</span>
            </div>
            <h3 class="moonshot-title">{{MOONSHOT_TITLE}}</h3>
            <p class="moonshot-description">{{MOONSHOT_DESCRIPTION}}</p>
            
            <!-- Strategic Alignment -->
            <div class="strategic-alignment-box">
                <h5>Strategic Alignment</h5>
                <p>{{STRATEGIC_ALIGNMENT}}</p>
            </div>
            
            <!-- Customer Success Example — from cached brief or RECO_FOR_PROSPECTING_SP_SALES reference customers -->
            <div class="customer-success-box">
                <strong>Customer Success Example:</strong>
                <span style="font-size: 0.85rem;">{{CUSTOMER_EXAMPLE}} - {{EXAMPLE_DESCRIPTION}}</span>
            </div>
            
            <!-- Customer Value -->
            <div class="customer-value-box">
                <h5>💎 Customer Value</h5>
                <p>{{CUSTOMER_VALUE_STATEMENT}}</p>
            </div>
            
            <!-- Impact Estimate -->
            <div class="impact-estimate">
                <div class="impact-item">
                    <span class="impact-label">Est. ACV Potential</span>
                    <span class="impact-value">{{ACV_POTENTIAL}}</span>
                </div>
                <div class="impact-item">
                    <span class="impact-label">Risk Mitigation</span>
                    <span class="impact-value {{IMPACT_CLASS}}">{{RISK_MITIGATION}}</span>
                </div>
            </div>
            
            <!-- Key Stakeholders -->
            <div class="stakeholder-tags">
                <span class="stakeholder-tag">{{STAKEHOLDER_1}}</span>
                <span class="stakeholder-tag">{{STAKEHOLDER_2}}</span>
            </div>
        </div>
    </div>
    
    <!-- Category Section: New Revenue Streams -->
    <h3 style="margin: 32px 0 16px; color: var(--accent); display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">💰</span> New Revenue Streams
        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: normal;">Ideas that enable data monetization or new business models</span>
    </h3>
    <div class="grid-2">
        <!-- Repeat for each Revenue moonshot -->
        <div class="moonshot-card revenue-category">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <span class="moonshot-category revenue">💰 New Revenue</span>
                <span class="relevance-badge {{RELEVANCE_CLASS}}">{{RELEVANCE_SCORE}}</span>
            </div>
            <h3 class="moonshot-title">{{MOONSHOT_TITLE}}</h3>
            <p class="moonshot-description">{{MOONSHOT_DESCRIPTION}}</p>
            
            <div class="strategic-alignment-box">
                <h5>Strategic Alignment</h5>
                <p>{{STRATEGIC_ALIGNMENT}}</p>
            </div>
            
            <div class="customer-success-box">
                <strong>Customer Success Example:</strong>
                <span style="font-size: 0.85rem;">{{CUSTOMER_EXAMPLE}} - {{EXAMPLE_DESCRIPTION}}</span>
            </div>
            
            <div class="customer-value-box">
                <h5>💎 Customer Value</h5>
                <p>{{CUSTOMER_VALUE_STATEMENT}}</p>
            </div>
            
            <div class="impact-estimate">
                <div class="impact-item">
                    <span class="impact-label">Est. ACV Potential</span>
                    <span class="impact-value">{{ACV_POTENTIAL}}</span>
                </div>
                <div class="impact-item">
                    <span class="impact-label">Revenue Enablement</span>
                    <span class="impact-value {{IMPACT_CLASS}}">{{REVENUE_IMPACT}}</span>
                </div>
            </div>
            
            <div class="stakeholder-tags">
                <span class="stakeholder-tag">{{STAKEHOLDER_1}}</span>
                <span class="stakeholder-tag">{{STAKEHOLDER_2}}</span>
            </div>
        </div>
    </div>
    
    <!-- Category Section: Operational Efficiency -->
    <h3 style="margin: 32px 0 16px; color: var(--purple); display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">⚡</span> Operational Efficiency
        <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: normal;">Ideas that save time, reduce costs, or improve productivity</span>
    </h3>
    <div class="grid-2">
        <!-- Repeat for each Efficiency moonshot -->
        <div class="moonshot-card efficiency-category">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <span class="moonshot-category efficiency">⚡ Efficiency</span>
                <span class="relevance-badge {{RELEVANCE_CLASS}}">{{RELEVANCE_SCORE}}</span>
            </div>
            <h3 class="moonshot-title">{{MOONSHOT_TITLE}}</h3>
            <p class="moonshot-description">{{MOONSHOT_DESCRIPTION}}</p>
            
            <div class="strategic-alignment-box">
                <h5>Strategic Alignment</h5>
                <p>{{STRATEGIC_ALIGNMENT}}</p>
            </div>
            
            <div class="customer-success-box">
                <strong>Customer Success Example:</strong>
                <span style="font-size: 0.85rem;">{{CUSTOMER_EXAMPLE}} - {{EXAMPLE_DESCRIPTION}}</span>
            </div>
            
            <div class="customer-value-box">
                <h5>💎 Customer Value</h5>
                <p>{{CUSTOMER_VALUE_STATEMENT}}</p>
            </div>
            
            <div class="impact-estimate">
                <div class="impact-item">
                    <span class="impact-label">Est. ACV Potential</span>
                    <span class="impact-value">{{ACV_POTENTIAL}}</span>
                </div>
                <div class="impact-item">
                    <span class="impact-label">Efficiency Gain</span>
                    <span class="impact-value {{IMPACT_CLASS}}">{{EFFICIENCY_GAIN}}</span>
                </div>
            </div>
            
            <div class="stakeholder-tags">
                <span class="stakeholder-tag">{{STAKEHOLDER_1}}</span>
                <span class="stakeholder-tag">{{STAKEHOLDER_2}}</span>
            </div>
        </div>
    </div>
    
    <!-- Industry Comparison Table — from Step 4B-ii use case query -->
    <div class="card" style="margin-top: 32px;">
        <h3>Industry Comparison: Successful Patterns from Similar Accounts</h3>
        <p style="color: var(--text-secondary); margin: 12px 0 20px;">Reference implementations from comparable accounts that inform these moonshot recommendations.</p>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Account</th>
                    <th>Use Case</th>
                    <th>Workloads</th>
                    <th>ACV</th>
                    <th>Relevance</th>
                </tr>
            </thead>
            <tbody>
                <!-- Repeat for top 5-10 comparison accounts -->
                <tr>
                    <td><strong>{{ACCOUNT_NAME}}</strong></td>
                    <td>{{UC_NAME}}</td>
                    <td>{{WORKLOADS}}</td>
                    <td style="color: var(--success); font-weight: 600;">${{ACV}}</td>
                    <td><span class="relevance-badge {{RELEVANCE_CLASS}}">{{RELEVANCE}}</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</section>
```

---

## Phase 5: Helper Functions

### AI Score Classification
| Score | Class | Color |
|-------|-------|-------|
| >= 80 | excellent | green (--success) |
| >= 60 | good | blue (--primary) |
| >= 40 | moderate | gold (--gold) |
| < 40 | poor | red (--warning) |

### Stage to Badge Class
| Stage | Class |
|-------|-------|
| Deployed | badge-deployed |
| Implementation | badge-implementation |
| Validation | badge-validation |
| Scoping | badge-scoping |
| Discovery | badge-discovery |
| Lost | badge-lost |

### Engagement Level (5-dot scale)
- 5 dots active = "Strong"
- 4 dots active = "Strong"
- 3 dots active = "Moderate"
- 1-2 dots active = "Limited (via team)"
- 0 dots active = "No Direct Engagement"

### Alignment Score Colors
- 70%+ = linear-gradient(90deg, var(--success), var(--accent))
- 40-69% = linear-gradient(90deg, var(--gold), var(--warning))
- <40% = linear-gradient(90deg, var(--warning), #FF8888)

### Currency Formatting
- Full: $1,500,000
- Abbreviated: $32.5M

---

## Phase 6: JavaScript Functions

```javascript
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');
}

function toggleMetadata(panelId) {
    const panel = document.getElementById(panelId);
    panel.classList.toggle('expanded');
}
```

---

## Phase 7: Quality Checklist

Before delivering:
- [ ] Header shows Deployed ACV, Pipeline ACV, Total Use Cases
- [ ] All 8 tabs have content
- [ ] Executive Overview has health banner, stats grid, company overview (from GET_3P_DATA), strategic priorities (from web_search), relationship summary
- [ ] Stakeholder Map has executives with engagement dots, champions, business unit engagement map with stakeholder chips
- [ ] Strategic Execution has alignment table, strategy cards with alignment score bars, competitive intelligence
- [ ] Pipeline Coverage has stage stats, metadata panel, pipeline cards with AI scores/SE notes/blocking questions
- [ ] Use Case Health has blocking questions by UC, critical risks with AI analysis, competitive threat table, product gaps
- [ ] Risks & Gaps mirrors Use Case Health structure
- [ ] Next Actions has P1/P2/P3 sections with AI-generated actions, account team table (from account-finder)
- [ ] Moonshot Ideas has 3 category sections (Risk/Revenue/Efficiency), moonshot cards with customer success examples (from cached brief or RECO_FOR_PROSPECTING_SP_SALES fallback), customer value boxes, industry comparison table
- [ ] All Salesforce links work (UC_URL column)
- [ ] Metadata panels in Pipeline, Use Case Health, Risks, Actions, Moonshots tabs
- [ ] Source icons (UC, AI, W, R, M) displayed appropriately
- [ ] Dark theme CSS applied correctly
