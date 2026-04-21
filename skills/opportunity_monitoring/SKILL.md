---
name: opportunity_monitoring
description: Monitors opportunity hygiene compliance against approved metrics. Works for both sales managers (team view) and individual AEs (own opportunities). Triggers - opportunity tracking, out of compliance, stuck opportunities, stale opportunities, my opportunities, how are my opportunities doing, pipeline health, pipeline hygiene, pipeline compliance, deal hygiene, stale next steps, who hasn't updated next steps, at risk deals, deals at risk.
created_date: 2026-02-27
last_updated: 2026-03-13
owner_name: Ecaterina Vidrascu
version: 1.3.0
---

# Opportunity Monitoring

Monitors opportunity pipeline compliance and progress for sales managers (team-wide) and individual AEs (own book). Covers stuck opportunities, missing fields, and stage progression metrics.

## Table of Contents

1. [When to Activate](#when-to-activate)
2. [Core Concepts](#core-concepts)
3. [Compliance Rules](#compliance-rules)
4. [Workflow](#workflow)
5. [Insight Patterns](#insight-patterns)
6. [Data Sources](#data-sources)
7. [References](#references)

## Input Parameters

| Parameter | Source | Description |
|-----------|--------|-------------|
| user_email | Auto-detected via Query 0 (CURRENT_USER) | User's email for opportunity scoping |
| is_manager | Auto-detected via Query 0 (IS_MANAGER flag) | TRUE = team view, FALSE = own opportunities |

## Output

Returns opportunity tracking metrics:
- Pipeline progress with week-over-week comparison
- Out of compliance opportunities with specific violations
- Compliance summary counts by violation type
- Stuck opportunities by stage

## When to Activate

Activate this skill when:
- User asks about opportunity compliance, "out of compliance", or hygiene
- Checking for stuck or stale opportunities
- Reviewing pipeline progress
- AE asks "how are my opportunities?" or "check my compliance"
- Manager asks about team opportunity health
- User mentions "stuck", "stale", "pipeline", "deal hygiene"

### Handoff to MEDDPICC Quality Skill

**IMPORTANT:** If the user's input matches any of these trigger phrases, do NOT run opportunity monitoring. Instead, hand off to the `opportunity_meddpicc_quality` skill (located at `shared_skills/sales/book_management/opportunity_meddpicc_quality/SKILL.md`):

- "meddpicc score"
- "meddpicc coach"
- "improve meddpicc"
- "meddpicc feedback"
- "meddpicc help"
- "what's missing in meddpicc"
- "how to improve meddpicc"
- "meddpicc simulation"

If any of these phrases appear in the user's request, load and follow the `opportunity_meddpicc_quality` skill instead of this one.

## Core Concepts

This skill tracks opportunity compliance against operational standards. Opportunities that violate these rules need attention -- whether from the AE who owns them or the manager overseeing the team.

**Key Insight:** Compliance issues compound - an opportunity past its close date with stale activity is likely blocked and needs intervention.

**Dual Mode:** Query 0 auto-detects whether the user is a manager or individual AE. Managers see their entire team's opportunities; individual AEs see only their own opportunities.

## Compliance Rules

### Priority Definitions

| Priority | Meaning | Action |
|----------|---------|--------|
| **P0** | Forecast-breaking or data integrity issue | Fix this week — blocks accurate forecasting or booking |
| **P1** | Deal at risk of slipping or stalling | Address this quarter — requires a conversation or plan update |
| **P2** | Hygiene gap or early warning signal | Address soon — clean up before it escalates |

### Rule Assignments

| # | Priority | Flag | Conditions | Rule | Why It Matters |
|---|----------|------|------------|------|----------------|
| 6 | **P0** | Committed Not in Negotiation+ (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, FORECAST_STATUS = 'Commit', STAGE before Negotiation (SDR Qualified: SQL / Sales Qualified Opportunity / Discovery / Scope / Use Case / Technical / Business Impact Validation), IS_CLOSED = FALSE | Committed opportunities should be at Negotiation stage or later to justify the forecast call | Commit on early-stage deals inflates forecast confidence without sufficient deal maturity |
| 10 | **P0** | TCV < ACV (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, TCV < TOTAL_ACV, TOTAL_ACV > 0, FORECAST_STATUS != 'Omitted', IS_CLOSED = FALSE | TCV should be greater than or equal to ACV — a lower TCV indicates a data entry or deal structuring error | TCV < ACV is almost always a mistake that distorts deal economics and booking accuracy |
| 3 | **P0** | $0 Total ACV (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, STAGE >= Discovery, TOTAL_ACV = 0, IS_CLOSED = FALSE | Capacity opportunities closing this quarter at Discovery or later should have ACV populated | $0 ACV on active deals hides pipeline value and blocks accurate forecasting |
| 1 | **P0** | Close Date in Past | IS_CAPACITY = TRUE, CLOSE_DATE < today, CLOSE_DATE >= 2021-01-01, TOTAL_ACV > 0, STAGE_NAME != 'Sales Ops Review', FORECAST_STATUS != 'Omitted', IS_CLOSED = FALSE | Capacity opportunities with a close date that has already passed need their close date updated or the deal closed out | Stale close dates pollute forecasts and hide deals that may be stuck or abandoned |
| 2 | **P1** | No Next Step Update L7D (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, STAGE >= Technical / Business Impact Validation, NEXT_STEPS unchanged in last 7 days (compared via snapshot), FORECAST_STATUS != 'Omitted', IS_CLOSED = FALSE | Opportunities closing this quarter at advanced stages must have fresh Next Steps to show active deal progression | Stale next steps on late-stage deals signal lost momentum and risk quarter-end surprises |
| 7 | **P1** | Stale Opportunities (Benchmarked) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, DAYS_IN_STAGE > DAYS_IN_STAGE_BENCHMARK_P75 (historical closed-won), TOTAL_ACV > $100K, FORECAST_STATUS != 'Omitted', IS_CLOSED = FALSE | Opportunities that have stayed in their current stage longer than 75th percentile of historical closed-won deals are likely stuck | Stale high-value deals closing this quarter need intervention — they are statistically unlikely to progress without action |
| 9 | **P1** | No Tech Win at Negotiation+ (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, STAGE in Negotiation / Deal Review / Deal Imminent, TECHNICAL_WIN = FALSE or NULL, TOTAL_ACV > 0, FORECAST_STATUS != 'Omitted', IS_CLOSED = FALSE | Late-stage opportunities should have achieved Technical Win before entering Negotiation | Deals in Negotiation+ without Tech Win risk stalling on technical objections and are less likely to close |
| 4 | **P1** | Still in Early Stages (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, STAGE in SDR Qualified: SQL / Sales Qualified Opportunity / Discovery / Scope / Use Case, TOTAL_ACV > 0, FORECAST_STATUS != 'Omitted', THEATER != 'Corporate', IS_CLOSED = FALSE | Capacity opportunities closing this quarter should not still be in early stages | Early-stage deals closing soon are unlikely to close on time and inflate the forecast |
| 11 | **P1** | MEDDPICC Incomplete (ACV > $100K) | IS_CAPACITY = TRUE, TOTAL_ACV > $100K, any of 8 MEDDPICC fields (Metrics, Economic Buyer, Decision Process, Decision Criteria, Identify Pain, Paper Process, Champion, Competition) is empty/NULL, IS_CLOSED = FALSE | High-value opportunities must have all MEDDPICC fields completed for proper deal qualification | Incomplete MEDDPICC on large deals signals gaps in qualification that increase risk of loss or slip |
| 12 | **P1** | Manager Deal Change Alerts (Combined) | Manager-only. Compares current vs 7-day-ago snapshot. Flags: A) Close date pushed >= 1 month or 1 quarter, B) Close date within first 2 weeks of next Q start, C) Close date on a weekend, D) TCV < ACV (TOTAL_ACV > 0, not Omitted), E) ACV changed > 10%. IS_CAPACITY = TRUE, IS_CLOSED = FALSE | Surfaces suspicious deal changes that warrant manager review — date pushes, weekend dates, large ACV swings, and TCV errors | Catches reps pushing dates blindly, placeholder weekend dates, and significant deal value changes that need a conversation |
| 5 | **P2** | Pipeline Forecast Status (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE within current FQ, FORECAST_STATUS = 'Pipeline', TOTAL_ACV > 0, THEATER != 'Corporate', IS_CLOSED = FALSE. Only flagged during 2nd and 3rd month of the quarter. | Opportunities closing this quarter should have been moved out of Pipeline status by mid-quarter | Deals still in Pipeline late in the quarter signal missing forecast calls and risk inaccurate commit numbers |
| 8 | **P2** | Close Date on Last Day of Quarter (Closing This Q) | IS_CAPACITY = TRUE, CLOSE_DATE = FQ_END, TOTAL_ACV > 0, FORECAST_STATUS != 'Omitted', IS_CLOSED = FALSE | Opportunities with close date set to the last day of the quarter likely have a placeholder date rather than a real close plan | Last-day close dates are often default placeholders and signal the rep hasn't confirmed actual timing |
| 13 | **P2** | MEDDPICC Score < 7 | IS_CAPACITY = TRUE, IS_CLOSED = FALSE, any of 8 MEDDPICC score fields (Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identify Pain, Champion, Competition) has a score < 7 (NULL treated as 0) | Opportunities with low MEDDPICC scores have weak qualification in one or more areas | Low scores indicate gaps in deal qualification that may lead to stalled or lost deals |

### Priority Escalation

An opportunity's effective priority escalates when multiple rules fire on the same deal:

| Combination | Escalates To | Rationale |
|-------------|--------------|-----------|
| Any violation + CLOSE_DATE within 40 days of today | **P0** | Deals closing soon need immediate attention regardless of violation severity |
| Any violation + TOTAL_ACV >= $200K | **P0** | Large deals with any compliance issue are high-impact and need immediate attention |
| Any P1 + TOTAL_ACV > $100K | **P0** | High-value deals with deal-risk signals need immediate attention |
| Any P2 + another P1 or P0 on the same opp | **P1** | Compounding issues on one deal signal deeper problems |
| Rule 2 (stale next steps) + Rule 7 (stale stage) on same opp | **P0** | No activity AND stuck in stage — deal is likely dead or blocked |
| Any violation + CLOSE_DATE > 300 days away | Cap at **P2** | Deals far from closing should not clutter P0/P1 — flag for awareness only |
| Any violation + TOTAL_ACV < $50K + CLOSE_DATE > 100 days away | Keep **P2** | Low-value deals far from closing can remain P2 even if other escalation rules would apply |

## Workflow

### Step 1: Identify User

Auto-detect user from Snowflake login:

```sql
-- See references/queries.sql for Query 0
```

**If no match:** Ask user for their email address.

Greet by first name. Store `user_email` (from EMPLOYEE_EMAIL) and `is_manager` (from IS_MANAGER) for subsequent queries.

- **If manager:** Confirm team size and proceed to Step 1.1 for team roster.
- **If individual AE:** Confirm their opportunities and skip to Step 2.

### Step 1.1: Get Team Roster (Managers Only)

```sql
-- See references/queries.sql for Query 0.1
```

### Step 2: Run Compliance Rules

Queries are consolidated to minimize round-trips. Run these in order:

| Query | Purpose | Scope |
|-------|---------|-------|
| **Query 1** | Consolidated detail — Rules 1, 3-11, 13 with boolean flag columns per opportunity | All users |
| **Query 2** | Rule 2 detail — Next Steps staleness (requires snapshot join) | All users |
| **Query 3** | Consolidated summary — violation counts and ACV at risk for Rules 1-11, 13 | All users |
| **Query 4** | Rule 12 detail — Manager deal change alerts (snapshot comparison) | Managers only |
| **Query 4.1** | Rule 12 summary — aggregate counts for deal change flags | Managers only |

All queries use a unified `team_members` CTE that automatically scopes based on `:is_manager`:
- Manager → shows team's opportunities (direct reports)
- Individual AE → shows only their own opportunities

Skip Query 4 and 4.1 if `:is_manager = FALSE`.

```sql
-- See references/queries.sql for all queries
```

### Step 3: Rank and Present Findings

After running all rule queries, rank findings by priority and present them grouped by P0 → P1 → P2.

**Ranking algorithm:**
1. Collect all flagged opportunities across all rules
2. For each opportunity, determine the highest-priority rule it violates
3. Apply escalation rules (see Priority Escalation table above) — e.g., a P1 on a $100K+ deal becomes P0
4. If an opportunity violates multiple rules, list all violations but rank it by the highest one
5. Within each priority group, sort by CLOSE_DATE ascending (earliest closing first), then by TOTAL_ACV descending (biggest deals first)

**Presentation structure:**

**IMPORTANT:** Do not show any thinking steps, intermediate analysis, query results, or priority calculation reasoning to the user. Only show the final formatted output starting with the greeting. Run all queries and apply all escalation logic silently.

### Display Mode Selection

Before presenting results, determine the display mode based on the user's request:

| User Says | Display Mode | What to Show |
|-----------|-------------|--------------|
| "summary", "key takeaways", "quick view", "highlights" | **Summary** | Key Takeaways only (no detail tables) |
| "table", "full details", "all opportunities", "detail", "show me the table" | **Table** | Priority detail tables only (no Key Takeaways) |
| "both", "summary and table", "everything", "full view", "all" | **Both** | Key Takeaways + Priority detail tables |
| Neither specified | **Ask** | Ask the user using `ask_user_question` |

**When asking the user:**
```json
{
  "questions": [{
    "header": "View",
    "question": "How would you like to see your compliance findings? Tip: next time you can say 'summary', 'table', or 'both' directly in your request.",
    "multiSelect": false,
    "options": [
      {"label": "Key Takeaways", "description": "Short summary of opportunities that need urgent attention. Next time say 'summary of my opps'."},
      {"label": "Full Table", "description": "Detailed table of all flagged opportunities with violations and recommended actions. Next time say 'table of my opps'."},
      {"label": "Both", "description": "Key Takeaways summary followed by the full detail tables. Next time say 'both' or 'all info'."}
    ]
  }]
}
```

- **Summary mode:** Show greeting + Key Takeaways section only. Include the MEDDPICC Score Footer and MEDDPICC Bridge prompt at the end. Do NOT show the P0/P1/P2 detail tables.
- **Table mode:** Show greeting + P0/P1/P2 detail tables only. Include the MEDDPICC Score Footer and MEDDPICC Bridge prompt at the end. Do NOT show the Key Takeaways section.
- **Both mode:** Show greeting + Key Takeaways section + P0/P1/P2 detail tables. Include the MEDDPICC Score Footer and MEDDPICC Bridge prompt at the end.



After identifying the user, present findings in this order:

**If zero violations are found across all rules:**

For an individual AE:
> Hey [First Name], you have zero compliance findings across all 13 rules. Your book is clean — no opportunities flagged for any P0, P1, or P2 violations.
>
> All capacity opportunities are current on close dates, ACV is populated, forecast statuses are appropriate, next steps are fresh, MEDDPICC is complete where required, and TCV/ACV alignment checks out.
>
> Well done, keep the good work going!

For a manager:
> Hey [First Name], your team has zero compliance findings across all 13 rules. Your team's book is clean — no opportunities flagged for any P0, P1, or P2 violations.
>
> All capacity opportunities across your team are current on close dates, ACV is populated, forecast statuses are appropriate, next steps are fresh, MEDDPICC is complete where required, and TCV/ACV alignment checks out.
>
> Well done, keep the good work going!

**If violations are found, present in this order:**

**For individual AEs:**

1. **Greeting + intro:** Greet with "Hey [First Name]", then: "here are the key focus areas for your opportunities."
2. **Key Takeaways:** A concise summary of the most important findings, structured as:
   - **Urgent Attention Needed** (if any P0 findings exist): One bullet per P0 opp with the opp name hyperlinked to Salesforce, the core issue and action needed.
   - **Other Focus Areas:** Bullets summarizing P1/P2 themes. Whenever a specific opportunity is mentioned by name, always hyperlink it to Salesforce: `[Opp Name](https://snowforce.my.salesforce.com/{OPPORTUNITY_ID})`. Group by pattern rather than listing every opp, but any opp called out individually must be hyperlinked.
3. **Detailed Views:** Full priority tables, only for levels that have findings. Omit any P0/P1/P2 section entirely if there are zero violations at that level.
4. **Truncation rule:** If an AE has more than 10 flagged opportunities, show only P0 and P1 opps (up to 10 total). Omit P2 from the detail section and add a note: *"You have X additional P2 findings ($YK ACV) not shown."* Key Takeaways should still reference P2 themes.

```
### Key Takeaways

**Urgent Attention Needed**
- [Opp Name](https://snowforce.my.salesforce.com/{OPPORTUNITY_ID}) ($XK, closes DD-MM-YYYY) — [core issue]. [One-line action].

**Other Focus Areas**
- X deals still in early stages closing this quarter ($YK total ACV)
- [other pattern summaries...]

---

## P0 — Fix This Week (X opps, $YM ACV at risk)

| # | Opportunity | Violations | Recommended Action |
| ... |

## P1 — Address This Quarter (X opps, $YM ACV at risk)

| # | Opportunity | Violations | Recommended Action |
| ... |

## P2 — Address Soon (X opps, $YM ACV at risk)

| # | Opportunity | Violations | Recommended Action |
| ... |

---

You have X opportunities with a MEDDPICC field score less than 7.
```

5. **MEDDPICC Score Footer:** After the last priority table (or truncation note), always append: *"You have X opportunities with a MEDDPICC field score less than 7."* Use the R13_MEDDPICC_SCORE_LOW_COUNT from Query 3. If the count is 0, omit this line AND the coaching bridge below.

**For managers:**

1. **Greeting + intro:** Greet with "Hey [First Name]", then: "here are the key focus areas for your team's opportunities."
2. **Key Takeaways:** Same structure as AE view but covering the full team. Mention rep names alongside opportunities.
3. **Per-Employee Detail:** Group findings by employee. For each employee with violations, show their name as a heading followed by their priority tables. Within each employee section, group by P0 → P1 → P2 and sort by Close Date ASC then ACV DESC. Omit employees with zero violations.
4. **Truncation rule:** If a rep has more than 10 flagged opportunities, show only P0 and P1 opps (up to 10 total). Omit P2 from their detail section and add a note: *"[Rep] has X additional P2 findings ($YK ACV) not shown — see Rep Summary for totals."* The Rep Summary table always includes full counts across all priorities.

```
### Key Takeaways

**Urgent Attention Needed**
- [Opp Name](https://snowforce.my.salesforce.com/{OPPORTUNITY_ID}) ($XK, closes DD-MM-YYYY) — [core issue]. Discuss with [Rep Name].

**Other Focus Areas**
- [pattern summaries mentioning rep names where relevant...]

---

### [Employee Name 1]

**P0 — Fix This Week (X opps, $YK ACV at risk)**

| # | Opportunity | Violations | Recommended Action |
| ... |

**P1 — Address This Quarter (X opps, $YK ACV at risk)**

| # | Opportunity | Violations | Recommended Action |
| ... |

---

### [Employee Name 2]

**P0 — Fix This Week (X opps, $YK ACV at risk)**

| # | Opportunity | Violations | Recommended Action |
| ... |

---

### Rep Summary
| Rep | P0 | P1 | P2 | Total ACV at Risk |
| ... |

---

Your team has X opportunities with a MEDDPICC field score less than 7.
```

5. **MEDDPICC Score Footer:** After the Rep Summary table, always append: *"Your team has X opportunities with a MEDDPICC field score less than 7."* Use the R13_MEDDPICC_SCORE_LOW_COUNT from Query 3. If the count is 0, omit this line AND the coaching bridge below.

If there are no P0 findings, omit the "Urgent Attention Needed" section and start Key Takeaways directly with the focus area bullets.

**Column layout:** Use 4 columns: `# | Opportunity | Violations | Recommended Action`.

**Opportunity column:** Show the opportunity name as a clickable Salesforce link, followed by ACV and Close Date on the same line separated by middot:
`[Opp Name](https://snowforce.my.salesforce.com/{OPPORTUNITY_ID}) · ACV: $XK · Close Date: DD-MM-YYYY`

**ACV format:** Use abbreviated format with NO spaces between number and suffix — `$10K`, `$250K`, `$1.2M`. Use K for thousands, M for millions. No decimals for round K values (`$10K` not `$10.0K` or `$10 K`). Use one decimal for M values (`$1.2M` not `$1.2 M`).

**Close Date format:** DD-MM-YYYY (e.g., 30-04-2026)

**Rules for the Violation column:**
- Bold the rule name, then add deal-specific context drawn from the opportunity's NEXT_STEPS, STAGE_NAME, CLOSE_DATE, and other fields
- Include relevant data: days overdue, dollar gaps, days stale, closing timeline, stage name, benchmark delta
- **R13 (MEDDPICC Score Low):** When listing this violation, just write "**MEDDPICC Score Low**" with no further detail — do NOT show the overall score or individual element scores. The per-element breakdown is only shown when the user explicitly asks for MEDDPICC violations (see MEDDPICC Violations Drill-Down below).
- Examples:
  - "**Early Stage** — still in Scope/Use Case, closing in 18 days (Mar 23)"
  - "**Stale Next Steps** — unchanged 7+ days, last activity was 2/25 regroup call"
  - "**TCV < ACV** — TCV is $0 vs $10K ACV; No Tech Win — in Negotiation without Technical Win; Stale Next Steps (unchanged 7+ days)"
  - "**No Tech Win** — in Negotiation without Technical Win; Last Day of Q (close date Apr 30)"
  - "**MEDDPICC Score Low**"
- If multiple violations, list them separated by semicolons

**Rules for the Recommended Action column:**
- Provide a specific, contextualized action based on what's actually happening in the deal (read the NEXT_STEPS field for context)
- Reference specific people, meetings, dates, or deal events from the opp's next steps
- Examples:
  - "Assess if deal can realistically close — primary contact Daniel is leaving, transition call with replacement Augustine needed"
  - "Follow up with Robert on ERP valuation status — last outreach was 2/17 with no response noted"
  - "Update next steps — follow up with Karen on sizing questionnaire completion"
  - "Fix TCV to match deal terms, then decide: push close date or close out — customer has been unresponsive since Cap1 signing"
- For managers, include the rep name: "Discuss with [Rep] — [specific context]"

**For individual AEs:** Skip the rep summary.

### MEDDPICC Score Footer and Coaching Bridge

**MEDDPICC Score Footer:** After presenting compliance findings (after the last priority table for AEs, or after the Rep Summary table for managers), always append:
- For individual AEs: *"You have X opportunities with a MEDDPICC field score less than 7."*
- For managers: *"Your team has X opportunities with a MEDDPICC field score less than 7."*
- Use `R13_MEDDPICC_SCORE_LOW_COUNT` from Query 3. If the count is 0, omit this line AND the coaching bridge below.

**MEDDPICC Coaching Bridge:** When `R13_MEDDPICC_SCORE_LOW_COUNT > 0`, immediately after the footer line, present this prompt:

```json
{
  "questions": [{
    "header": "MEDDPICC",
    "question": "Would you like to work on improving MEDDPICC scores?",
    "multiSelect": false,
    "options": [
      {"label": "View score breakdown", "description": "Show the MEDDPICC Violations Drill-Down table with per-element scores for all flagged opportunities"},
      {"label": "Coach me on an opportunity", "description": "Pick an opportunity and get interactive coaching — see what's missing, simulate improvements, and get the score up"},
      {"label": "Skip", "description": "No thanks, I'm done for now"}
    ]
  }]
}
```

- **"View score breakdown":** Show the MEDDPICC Violations Drill-Down table (see below).
- **"Coach me on an opportunity":** Hand off to the `opportunity_meddpicc_quality` skill (`shared_skills/sales/book_management/opportunity_meddpicc_quality/SKILL.md`). This will walk the user through reviewing current scores, coaching on weak elements, simulating improvements, and pointing them to Salesforce to update.
- **"Skip":** End the skill output.

### MEDDPICC Violations Drill-Down

This section is shown when the user selects "View score breakdown" from the coaching bridge above, OR when the user explicitly asks for MEDDPICC violations (e.g., "show me MEDDPICC violations", "which opps have low MEDDPICC scores", "MEDDPICC details"). It is NOT included in the standard opportunity monitoring output.

When triggered, display all opportunities flagged by R13 (MEDDPICC Score < 7) in a table with the opportunity ID and the low scores for each MEDDPICC element:

```
| # | Opportunity | Overall | Metrics | Econ Buyer | Decision Criteria | Decision Process | Paper Process | Identify Pain | Champion | Competition |
|---|-------------|---------|---------|------------|-------------------|------------------|---------------|---------------|----------|-------------|
| 1 | [Opp Name](https://snowforce.my.salesforce.com/{OPPORTUNITY_ID}) | XX/80 | X/10 | X/10 | X/10 | X/10 | X/10 | X/10 | X/10 | X/10 |
```

- Only show score values for elements that scored < 7. For elements scoring >= 7, display the actual score value.
- Bold low scores (< 7) to make them stand out.
- Sort by TOTAL_ACV descending.
- Include all R13-flagged opps (no truncation).


## Insight Patterns

**Good Example (manager, table format — grouped by employee):**

> Hey Sarah, here are the key focus areas for your team's opportunities.
>
> ### Key Takeaways
>
> **Urgent Attention Needed**
> - [Acme Corp-Cap-New Business](https://snowforce.my.salesforce.com/006...) ($500K, closes 15-03-2026) — marked Commit but still in Discovery with stale next steps. Discuss with John to either downgrade forecast or accelerate stage.
> - [Beta Inc-Cap-Renewal](https://snowforce.my.salesforce.com/006...) ($400K, closes 28-03-2026) — TCV is $200K vs $400K ACV. Discuss with Jane to fix TCV.
>
> **Other Focus Areas**
> - 4 deals have stale next steps across John and Jane ($800K total ACV)
> - 2 deals are still in early stages closing this quarter ($350K total ACV)
>
> ---
>
> ### John Smith
>
> **P0 — Fix This Week (2 opps, $800K ACV at risk)**
>
> | # | Opportunity | Violations | Recommended Action |
> |---|-------------|------------|--------------------|
> | 1 | [Acme Corp-Cap-New Business](https://snowforce.my.salesforce.com/006...) · ACV: $500K · Close Date: 15-03-2026 | **Commit/Stage Mismatch** — marked Commit but still in Discovery; Stale Next Steps — unchanged 14 days | Discuss with John — either downgrade forecast or get champion call scheduled this week |
> | 2 | [Gamma LLC-Cap-New Business](https://snowforce.my.salesforce.com/006...) · ACV: $300K · Close Date: 10-04-2026 | **$0 ACV** — in Negotiation with no ACV populated | Discuss with John — populate ACV, pricing proposal was sent 3/1 |
>
> ---
>
> ### Jane Doe
>
> **P0 — Fix This Week (1 opp, $400K ACV at risk)**
>
> | # | Opportunity | Violations | Recommended Action |
> |---|-------------|------------|--------------------|
> | 1 | [Beta Inc-Cap-Renewal](https://snowforce.my.salesforce.com/006...) · ACV: $400K · Close Date: 28-03-2026 | **TCV < ACV** — TCV is $200K vs $400K ACV, likely a data entry error | Discuss with Jane — fix TCV, confirm with finance if multi-year |
>
> ---
>
> ### Rep Summary
> | Rep | P0 | P1 | P2 | Total ACV at Risk |
> |-----|----|----|----|----|
> | John Smith | 2 | 0 | 0 | $800K |
> | Jane Doe | 1 | 0 | 0 | $400K |

**Good Example (individual AE, table format):**

> Hey Devan, here are the key focus areas for your opportunities.
>
> ### Key Takeaways
>
> **Urgent Attention Needed**
> - [Acme Corp-Cap-New Business](https://snowforce.my.salesforce.com/006...) ($500K, closes 10-03-2026) — 12 days past close date. Update close date or close out.
>
> **Other Focus Areas**
> - 2 deals have stale next steps — update with current status
> - 1 deal in Deal Review without Technical Win documented
>
> ---
>
> **P0 — Fix This Week (1 opp)**
>
> | # | Opportunity | Violations | Recommended Action |
> |---|-------------|------------|--------------------|
> | 1 | [Acme Corp-Cap-New Business](https://snowforce.my.salesforce.com/006...) · ACV: $500K · Close Date: 10-03-2026 | **Close Date Past** — 12 days overdue, last next steps update was a 2/26 follow-up email with no response | Update close date or close out — no engagement in 2 weeks |
>
> **P1 — Address This Quarter (2 opps)**
>
> | # | Opportunity | Violations | Recommended Action |
> |---|-------------|------------|--------------------|
> | 1 | [Beta Inc-Cap-Renewal](https://snowforce.my.salesforce.com/006...) · ACV: $200K · Close Date: 15-04-2026 | **Stale Next Steps** — unchanged 10 days, last activity was 3/1 pricing discussion | Update next steps — follow up with procurement on pricing approval |
> | 2 | [Gamma LLC-Cap-New Business](https://snowforce.my.salesforce.com/006...) · ACV: $150K · Close Date: 30-03-2026 | **No Tech Win** — in Deal Review without Technical Win documented | Get tech win documented — SE confirmed POC passed, needs to be logged |

**Bad Example (avoid):**
> "I found some issues with your opportunities. Here are the details..."
> (No priority grouping, no ACV ranking, no clear action items, no clickable links)

## Data Sources

| Table | Purpose |
|-------|---------|
| `SALES.RAVEN.RAVEN_EMPLOYEE_WITH_REPORTING_CHAIN` | User identity detection, manager/IC role, team member lookup |
| `SALES.RAVEN.SDA_OPPORTUNITY_VIEW` | Opportunity data, compliance fields, stage progress |
| `SALES.RAVEN.SDA_OPPORTUNITY_SNAPSHOT_VIEW` | Historical daily snapshots for detecting field changes (e.g., Next Steps staleness) |

## References

### Internal

- [queries.sql](references/queries.sql) - SQL queries for compliance and progress

### Skills

- [opportunity_meddpicc_quality](skills/opportunity_meddpicc_quality/SKILL.md) - Interactive MEDDPICC scoring coach for opportunities (handoff target from coaching bridge)

