---
name: weekly-district-forecast
description: "Generate weekly Services Delivery district forecast emails for EntBayAreaTech1 and EntPacNorthwest. Use when: weekly forecast, district forecast, weekly update, weekly email, SD forecast, weekly district email, forecast email, write my weekly updates, generate forecast, EntBayAreaTech1, EntPacNorthwest."
---

# Weekly District Forecast

Generate weekly Services Delivery (SD) district forecast emails for the user's two districts: **EntBayAreaTech1** (DM: Erik Schneider) and **EntPacNorthwest** (DM: Raymond Navarro). Emails focus on **pipeline deals, closing timelines, new business generation**, with delivery updates as secondary context.

## District Configuration

| Field | EntBayAreaTech1 | EntPacNorthwest |
|-------|-----------------|-----------------|
| DM (To:) | Erik Schneider | Raymond Navarro |
| CC | Yash Chechani, Paul Pachence, Linda Tasner, Zheng Li | Brian Whittington, Paul Pachence, Linda Tasner, Zheng Li |
| Greeting | "Hi Erik & team," | "Hi Raymond & team -" |
| Subject | `Services Delivery - Weekly District Forecast - EntBayAreaTech1 - {M/D/YYYY}` | `Services Delivery - Weekly District Forecast - EntPacNorthwest - {M/D/YYYY}` |

## Email Template

```
Subject: Services Delivery - Weekly District Forecast - {District} - {M/D/YYYY}
To: {DM}
CC: {CC list}

{Greeting}

Please see the district's weekly Services Delivery (SD) {update|forecast} for the week ending {M/D/YY}.

Key notes for the week:

1. **{Account}** ({$Amount}, {Stage}) – {1-3 sentences: SOW status, deal progress, next steps}
2. **{Account}** ({$Amount}, {Stage}) – {1-3 sentences}
3. ...
{Optional general note: Summit workshops, cap conversions, enablement sessions}

Let me know if you have any questions or notes.

Thanks!
--
```

## Content Priority Rules

1. **Pipeline deals with close dates this quarter** — always include, lead with $ and stage
2. **SOW/proposal status changes** — signature progress, customer feedback, legal review
3. **New biz generation activities** — Summit workshop nominations, selling sessions, cap conversion discussions, CJW planning
4. **Cap conversions** — highlight accounts with predicted underage approaching renewals
5. **Delivery updates** — brief, 1 sentence max, only when relevant to pipeline or renewal
6. **Stages to use:** Most Likely, Upside, Pipeline, Potential (mirror the Patch Review deck)

## Workflow

### Step 1: Determine Scope

Use today's date to calculate the week-ending date (Friday of the current week). If today is not Friday, use the most recent Friday or the upcoming Friday — whichever makes sense contextually.

Ask the user which district(s) to generate:
- EntBayAreaTech1 only
- EntPacNorthwest only
- Both districts

If the user's initial request already specifies, skip this question.

### Step 2: Retrieve Prior Week's Email

For each district, search Gmail for the most recent forecast email:

```
mcp_glean2_search
  app: gmailnative
  owner: me
  query: "Services Delivery Weekly District Forecast {DistrictName}"
  num_results: 3
  type: email
```

Read the full thread of the most recent result with `mcp_glean2_read_document`. This provides:
- The accounts covered last week (continuity tracking)
- Deal status as of last week (to identify changes)
- Tone and style reference

### Step 3: Gather Pipeline Data

**A. Patch Review Deck (primary pipeline source)**

Search for the most recent Patch Review or TAM Review deck:

```
mcp_glean2_search
  owner: me
  query: "Patch Review Q{quarter} FY{year} EntBayAreaTech1 EntPacNorthwest"
  num_results: 3
```

Read it with `mcp_glean2_read_document`. Extract for the target district:
- Each pipeline opportunity: Account, AE, Play Type, Status, Amount, Close Date, Description
- Suggested opportunities (Potential)
- Credit conversion candidates

**B. SNOW_CERTIFIED / SALES.RAVEN (supplementary)**

If the Patch Review deck is stale (>2 weeks old) or unavailable, query pipeline data:

```sql
-- Example: check for open PS opps in the district
-- Adapt based on available semantic views in SNOW_CERTIFIED
```

### Step 4: Gather Weekly Activity

For each key account identified in Step 2 and Step 3, search for this week's activity:

**A. Email threads** — search Gmail for account-specific activity:

```
mcp_glean2_search
  app: gmailnative
  query: "{Account Name} SOW OR proposal OR kickoff OR scope"
  updated: past_week
```

**B. Meeting summaries** — Zoom recaps are rich data sources:

```
mcp_glean2_search
  app: gmailnative
  query: "Meeting assets {Account Name}"
  updated: past_week
```

**C. Slack activity** — for deal-related discussions:

```
mcp_glean2_search
  app: slack
  query: "{Account Name} deal OR SOW OR proposal"
  updated: past_week
```

Read the most relevant results with `mcp_glean2_read_document` to extract specifics.

### Step 5: Identify New Biz Activities

Search for cross-district activities that should be called out:
- Summit workshop nominations/confirmations
- Selling sessions / enablement sessions planned
- Cap conversion discussions with AEs
- CJW (Customer Joint Workshop) planning

```
mcp_glean2_search
  owner: me
  query: "Summit workshop nomination {district}"
  updated: past_month
```

### Step 6: Draft the Email

For each district, compose the email following the template:

**Ordering rules:**
1. Most Likely deals first (closest to closing)
2. Upside deals second
3. Pipeline deals third (by close date ascending)
4. New biz generation activities (cap conversions, workshops, enablement)
5. Brief delivery notes last (if any)

**Writing style (match Sam's voice):**
- Direct, concise, action-oriented
- Account name bolded, followed by dollar amount and stage in parentheses
- 1-3 sentences per item — what happened, what's next
- End items with clear next steps or what's pending
- Casual professional tone: "Ping me" / "Let me know" / "Thanks!"
- Use "we" language for team activities
- Reference specific people by first name when relevant

**⚠️ MANDATORY STOPPING POINT**: Present the draft email(s) to the user for review before any further action.

### Step 7: Finalize

After user review and edits:
1. Present the final version formatted for easy copy-paste into Gmail
2. Optionally: create a Gmail draft via `mcp_google-worksp_create_draft` if the Google Workspace MCP is available

## Stopping Points

- ✋ After Step 6: Draft presented for user review — do NOT send or finalize without approval
- ✋ If no pipeline data found: inform user and ask for manual input on key deals
- ✋ If prior week's email not found: ask user for context on which accounts to cover

## Output

One formatted email per district, ready to copy-paste or save as Gmail draft. Each email contains:
- Proper subject line with date
- To/CC fields
- Numbered key notes focused on pipeline and new biz
- Consistent tone matching Sam's established style

## Notes

- The user typically sends both emails on the same day (Thursday or Friday), within minutes of each other
- Date format in subject: M/D/YYYY (e.g., 5/15/2026)
- Date format in body: M/D/YY (e.g., 5/15/26)
- The Patch Review deck is the system of record for pipeline amounts and stages — always prefer it over ad-hoc queries
- When an account appeared in last week's email, provide a status update showing progression (not a repeat of the same text)
- Cap conversions are a district-wide theme — OK to group as a single bullet rather than per-account
- Summit workshop nominations are a Q2 FY27 theme worth highlighting when there are confirmed attendees
