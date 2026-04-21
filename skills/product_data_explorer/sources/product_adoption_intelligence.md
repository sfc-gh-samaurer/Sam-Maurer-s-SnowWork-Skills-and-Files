## Source 6: Product Adoption Intelligence

**Purpose**: Detect meaningful changes in a customer's Snowflake product usage — new feature adoption, revenue surges, and attrition signals — and surface them as business insights with a recommended sales action.

**When to use this source**:
- User asks about "product trends", "what changed", "adoption signals", "product spike/drop", "new features", "product attrition", "what's growing/declining"
- User asks "show me all my accounts" or "any product signals across my book" (use **Book/Triage format**)
- After presenting WLC or Product Category data, offer this as a follow-up: "Want to see what's changed recently?"
- When embedding a product signal summary into another skill (use **Short format**)

---

### Output Format

This source supports three output formats. Choose based on context:

| Format | When to use | Length |
|--------|-------------|--------|
| **Book/Triage** | User asks about all their accounts, book scan, territory, manager rollup | Ranked triage table, 1 row per account |
| **Short** | Default for general product adoption questions ("product insights for X", "how is adoption going?", "product feature summary") OR embedding into another skill | 4–5 lines per account |
| **Long** | Explicit signal/change request ("what changed?", "any signals?", "product deep-dive") | 4 sections + optional table |

**Default trigger rule**: If the user asks a general product adoption question without specifying a feature or requesting a deep-dive, use **Short format** directly — do not ask clarifying questions, just run the SQL and return Short format output. This replaces the Product Insights Autopilot.

---

### Book / Triage Format Template

Use when the user asks about their full book, a territory, or a manager's team. Goal: show every account that has a meaningful signal in one scannable view — ranked so the AE knows exactly where to spend their time.

**Step 0**: Resolve the user's name to their accounts via `resources/account_lookup.sql` (same as WCA). Then run the Book Scan SQL below with `{person_or_geo_filter}` replaced.

**Materiality filter before surfacing**: suppress signals where `feature_pct_of_acct < 2%` AND `prior_2w_rev < 100`, UNLESS the feature is on the Monitored AI Feature List.

**Triage table structure** — three sections in order:

```
## Product Adoption — Book Signal Triage
*[Person Name] · [N] accounts with signals · [Date]*

### Needs Attention
| Account | Signal | Feature | What's Happening |
|---------|--------|---------|------------------|
| [account] | Collapsing / Declining | [feature] | [1-line: direction, % of spend, implication] |

### Moving Fast
| Account | Signal | Feature | What's Happening |
|---------|--------|---------|------------------|
| [account] | Surging / Ramping | [feature] | [1-line: WoW growth, % of spend, implication] |

### New Adoption
| Account | Feature | What's Happening |
|---------|---------|------------------|
| [account] | [feature] | [1-line: first seen, any context] |
```

**Sorting rules**:
- **Needs Attention**: sort by `acct_90d_rev DESC` (largest accounts first — protect the biggest revenue)
- **Moving Fast**: sort by `feature_pct_of_acct DESC` (most material signals first)
- **New Adoption**: sort by `acct_90d_rev DESC`

**After table**: Always end with — *"Want me to pull the full intelligence report for any of these accounts?"*

**Accounts with no signals**: Do not list them. Mention count only: *"[N] accounts showed no significant product changes."*

---

### Short Format Template

Use when embedding into another skill or giving a quick signal summary. Max 5 lines per account.

```
**[Account Name]** · [dominant product category, ~X% of spend]
- [Signal 1 — most important growth or new adoption signal, 1 sentence]
- [Signal 2 — most important risk or attrition signal, 1 sentence]
- Recommended: [1 concrete action for the AE/SE]
```

**Rules for short format**:
- Lead with the single most actionable signal — do NOT list everything
- Use plain language. No tag codes (no "FEATURE_ATTRITION"), no z-scores, no percentages unless they add impact
- If there is no meaningful signal (account stable, no changes), write: `[Account] · No significant product adoption changes in the last 90 days.`
- Signal 1 = best growth/opportunity. Signal 2 = biggest risk. If only one type exists, omit the other line

---

### Long Format Template

Use for standalone product adoption deep-dives. Always use this structure — 4 sections in order.

```
## [Account Name] — Product Adoption Intelligence
*[Date] · Last 90 days*

### At a Glance
- [1-sentence dominant category characterization with % of spend]
- [1-sentence AI/ML status: absent / early / growing / mature]
- [1-sentence overall trajectory: stable / expanding / declining]

### Act Now — Emerging Signals
[Only include if signals exist. 2–5 bullets, most important first.]
- **[Feature name] [direction]**: [what the data shows] — [why it matters to this customer] — [suggested action]

### Core Business
[Only stable/growing features above 5% of total spend. Keep brief.]
- **[Category] (~X% of spend)**: [1-sentence description of what's happening]

### Risk / Dormant Signals
[Only include if signals exist. 2–4 bullets.]
- **[Feature] went dark / declining**: [what happened] — [business implication]

### Opportunity Map  ← optional, include when ≥3 opportunities exist
| Signal | Sales Play |
|--------|------------|
| [signal] | [action] |
```

**Rules for long format**:
- "Act Now" section is the most important — lead with it after At a Glance
- Never show raw percentages in the narrative unless they are striking (>200% WoW, -90%+). Use directional language instead: "surging", "declining sharply", "collapsed", "steady"
- Omit any section that has no meaningful content — do not show empty sections
- Do not show individual revenue figures unless the user has asked for financials

---

### Detection Logic (run silently — not shown to user)

**Step 1: Pull weekly revenue by feature (90-day window)**

```sql
WITH weekly AS (
    SELECT salesforce_account_id, salesforce_account_name,
        product_category, use_case, feature,
        DATE_TRUNC('week', general_date) AS week_start,
        SUM(revenue) AS weekly_rev
    FROM SALES.RAVEN.A360_DAILY_ACCOUNT_PRODUCT_CATEGORY_REVENUE_VIEW
    WHERE salesforce_account_id = '{account_id}'
      AND general_date >= CURRENT_DATE - 90
      AND general_date < CURRENT_DATE
    GROUP BY 1,2,3,4,5,6
),
totals AS (
    SELECT salesforce_account_id, salesforce_account_name,
        product_category, use_case, feature,
        SUM(weekly_rev)                                                       AS total_90d,
        COUNT(DISTINCT week_start)                                            AS active_weeks,
        MIN(week_start)                                                       AS first_week,
        MAX(week_start)                                                       AS last_week,
        MAX(CASE WHEN week_start >= CURRENT_DATE - 14
                 THEN weekly_rev END)                                         AS last_2w_rev,
        MAX(CASE WHEN week_start >= CURRENT_DATE - 28
                 AND week_start < CURRENT_DATE - 14
                 THEN weekly_rev END)                                         AS prior_2w_rev
    FROM weekly
    GROUP BY 1,2,3,4,5
)
SELECT *,
    COALESCE(last_2w_rev, 0)                                                  AS last_2w_rev_clean,
    COALESCE(prior_2w_rev, 0)                                                 AS prior_2w_rev_clean,
    CASE WHEN COALESCE(prior_2w_rev, 0) > 0
         THEN ROUND(DIV0(COALESCE(last_2w_rev,0) - prior_2w_rev, prior_2w_rev) * 100, 1)
         ELSE NULL END                                                        AS recent_wow_pct
FROM totals
WHERE total_90d > 5
ORDER BY total_90d DESC;
```

**Step 1b: YoY category comparison** *(run for Short format; skip for Long and Book/Triage)*

```sql
SELECT product_category,
    SUM(CASE WHEN general_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
             AND general_date <  DATE_TRUNC('month', CURRENT_DATE)
             THEN revenue END)                                           AS last_month_rev,
    SUM(CASE WHEN general_date >= DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month')
             AND general_date <  DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE))
             THEN revenue END)                                           AS lyoy_rev,
    ROUND(DIV0(
        SUM(CASE WHEN general_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
                 AND general_date < DATE_TRUNC('month', CURRENT_DATE) THEN revenue END) -
        SUM(CASE WHEN general_date >= DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month')
                 AND general_date < DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE)) THEN revenue END),
        NULLIF(SUM(CASE WHEN general_date >= DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month')
                        AND general_date < DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE)) THEN revenue END), 0)
    ) * 100, 1)                                                         AS yoy_pct
FROM SALES.RAVEN.A360_DAILY_ACCOUNT_PRODUCT_CATEGORY_REVENUE_VIEW
WHERE salesforce_account_id = '{account_id}'
  AND general_date >= DATEADD('year', -1, DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month')
  AND general_date < CURRENT_DATE
GROUP BY 1
ORDER BY last_month_rev DESC NULLS LAST;
```

Use YoY to add one line of context to the Short format "At a Glance" — e.g. *"Data Engineering up 22% YoY"* or *"AI/ML flat YoY but accelerating in the last 2 weeks."*

**Step 2: Classify each feature into a signal type**

Apply these rules in order. A feature can have at most one primary signal.

| Signal Tag | Condition | Notes |
|------------|-----------|-------|
| `NEW_FEATURE_ADOPTION` | first_week within last 21 days AND total_90d > 5 | Brand new adoption |
| `EMERGING_AI_ADOPTION` | Feature is on the Monitored AI List (below) AND first_week within last 30 days | Flag even if revenue is tiny |
| `RAPID_SURGE` | recent_wow_pct > 150% AND prior_2w_rev > 10 | Confirmed surge (not zero-to-nonzero) |
| `STEADY_GROWTH` | recent_wow_pct between 30% and 150% AND active_weeks >= 8 | Sustained multi-week growth |
| `FEATURE_ATTRITION` | last_2w_rev = 0 AND prior_2w_rev > 50 AND last_week < CURRENT_DATE - 14 | Feature stopped |
| `SHARP_DECLINE` | recent_wow_pct < -60% AND prior_2w_rev > 20 | Major recent drop |
| `STABLE` | ABS(recent_wow_pct) < 20% OR active_weeks < 4 | No significant change |

**Monitored AI Feature List** (any first adoption = signal regardless of revenue):
- Cortex Code
- Agents API
- SI Agent Orchestration
- AI Compute
- Document AI
- SPCS GPU
- Cortex Analyst (via Agents)
- Cortex Analyst (via SI)

**Step 3: Compute account-level totals for "At a Glance"**

```sql
SELECT product_category,
    SUM(revenue) AS cat_90d_rev,
    ROUND(DIV0(SUM(revenue), SUM(SUM(revenue)) OVER ()) * 100, 1) AS cat_pct
FROM SALES.RAVEN.A360_DAILY_ACCOUNT_PRODUCT_CATEGORY_REVENUE_VIEW
WHERE salesforce_account_id = '{account_id}'
  AND general_date >= CURRENT_DATE - 90
  AND general_date < CURRENT_DATE
GROUP BY 1
ORDER BY cat_90d_rev DESC;
```

**Step 4: Materiality filter**

Before surfacing signals, apply:
- Suppress `FEATURE_ATTRITION` and `SHARP_DECLINE` if the feature was <1% of total account spend in the prior period
- For `RAPID_SURGE` and `STEADY_GROWTH`, only surface if feature is >0.5% of account total spend OR is on the Monitored AI List

---

### Multi-Account Book Scan (for AE book, territory, or manager rollup)

Use this when the user asks for signals across their book or a territory. Returns one row per account with the most important signal. Feed results into the short format, one account per entry.

```sql
WITH weekly AS (
    SELECT salesforce_account_id, salesforce_account_name,
        feature, product_category,
        DATE_TRUNC('week', general_date) AS week_start,
        SUM(revenue) AS weekly_rev
    FROM SALES.RAVEN.A360_DAILY_ACCOUNT_PRODUCT_CATEGORY_REVENUE_VIEW
    WHERE salesforce_account_id IN (
        SELECT DISTINCT salesforce_account_id
        FROM SALES.RAVEN.D_SALESFORCE_ACCOUNT_CUSTOMERS
        WHERE {person_or_geo_filter}
          AND IS_CAPACITY_CUSTOMER = TRUE
    )
      AND general_date >= CURRENT_DATE - 90
      AND general_date < CURRENT_DATE
    GROUP BY 1,2,3,4,5
),
signals AS (
    SELECT salesforce_account_id, salesforce_account_name,
        product_category, feature,
        SUM(weekly_rev)                                                         AS total_90d,
        MIN(week_start)                                                         AS first_week,
        MAX(week_start)                                                         AS last_week,
        MAX(CASE WHEN week_start >= CURRENT_DATE - 14 THEN weekly_rev END)      AS last_2w_rev,
        MAX(CASE WHEN week_start >= CURRENT_DATE - 28
                 AND week_start < CURRENT_DATE - 14 THEN weekly_rev END)        AS prior_2w_rev
    FROM weekly
    GROUP BY 1,2,3,4
),
classified AS (
    SELECT *,
        COALESCE(last_2w_rev, 0)                                                AS l2w,
        COALESCE(prior_2w_rev, 0)                                               AS p2w,
        CASE
            WHEN DATEDIFF('day', first_week, CURRENT_DATE) <= 30
             AND total_90d > 5                                                   THEN 'NEW_ADOPTION'
            WHEN COALESCE(prior_2w_rev, 0) > 10
             AND DIV0(COALESCE(last_2w_rev,0) - prior_2w_rev, prior_2w_rev) > 1.5  THEN 'RAPID_SURGE'
            WHEN COALESCE(last_2w_rev, 0) = 0
             AND COALESCE(prior_2w_rev, 0) > 50                                 THEN 'ATTRITION'
            WHEN COALESCE(prior_2w_rev, 0) > 20
             AND DIV0(COALESCE(last_2w_rev,0) - prior_2w_rev, prior_2w_rev) < -0.6  THEN 'SHARP_DECLINE'
            ELSE NULL
        END                                                                     AS signal
    FROM signals
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY salesforce_account_id
            ORDER BY
                CASE signal
                    WHEN 'ATTRITION'    THEN 1
                    WHEN 'SHARP_DECLINE' THEN 2
                    WHEN 'RAPID_SURGE'  THEN 3
                    WHEN 'NEW_ADOPTION' THEN 4
                    ELSE 5
                END,
                total_90d DESC
        ) AS rn
    FROM classified
    WHERE signal IS NOT NULL
)
SELECT salesforce_account_name, product_category, feature, signal,
    ROUND(total_90d, 0) AS total_90d_rev
FROM ranked
WHERE rn = 1
ORDER BY
    CASE signal WHEN 'ATTRITION' THEN 1 WHEN 'SHARP_DECLINE' THEN 2
                WHEN 'RAPID_SURGE' THEN 3 WHEN 'NEW_ADOPTION' THEN 4 END,
    total_90d DESC;
```

**Ranking note**: ATTRITION and SHARP_DECLINE are shown first (risk = act sooner). RAPID_SURGE and NEW_ADOPTION follow (opportunity = also time-sensitive). Accounts with no signal are omitted.

---

### Sample Outputs — Short Format

> **Coinbase** · Data Engineering-first (~49% of spend)
> - Cortex Code just started ramping (6 weeks in) and Cortex AI Functions are accelerating sharply — early signals of an AI developer presence worth engaging now.
> - Agents API was tried for 3 weeks in February then stopped — find out what blocked them.
> - Recommended: Identify the Cortex Code champion; propose an SE-led architecture review on the agentic stack.

---

> **S&P Global Corporate DTS** · AI/ML-heavy (~65% of spend)
> - Cortex AI Functions surged dramatically in the last 2 weeks — their primary AI workload is scaling fast and likely needs architectural support.
> - Agents API and SPCS have both dropped sharply — the agentic stack experiments appear to have stalled.
> - Recommended: Engage now while the Cortex AI Functions momentum is high; bring a Cortex reference architecture for financial document analysis.

---

> **KPMG LLP** · AI/ML almost exclusively (~91% of spend)
> - Cortex Search is the one stable, consistent workload (running steady every week) — their core AI product.
> - Cortex AI Functions, their largest feature by spend ($183K over 90 days), has completely stopped — no revenue in the last 3 weeks.
> - Recommended: Urgent rescue conversation — what happened to the Cortex AI Functions workload? Has the project ended or hit a technical blocker?

---

> **Sumitomo Mitsui Trust Asset Management** · AI/ML dominant (~82% of spend)
> - Cortex Code is the one bright spot — growing steadily (+27% WoW, 6 weeks in) — someone is actively building.
> - Cortex AI Functions has collapsed from ~$12.8K/week to under $200/week in the last 2 weeks — their main AI workload has nearly stopped.
> - Recommended: Critical intervention — understand what drove the AI Functions collapse; Cortex Code growth suggests the team hasn't left, they may have pivoted.

---

### Naming Convention (align with SKILL.md)

| Internal Tag | User-Facing Language |
|---|---|
| `NEW_FEATURE_ADOPTION` | "just started using", "newly adopted", "first appeared" |
| `EMERGING_AI_ADOPTION` | "early AI signal", "started building with" |
| `RAPID_SURGE` | "surged", "growing fast", "accelerating sharply" |
| `STEADY_GROWTH` | "consistently growing", "steady ramp" |
| `FEATURE_ATTRITION` | "went dark", "has stopped", "no revenue since" |
| `SHARP_DECLINE` | "dropped sharply", "declining fast", "collapsed" |

Never use tag codes in user-facing output.
