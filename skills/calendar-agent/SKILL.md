---
name: calendar-agent
description: "Fetch today's Google Calendar events, categorize by color, enrich each meeting with Glean context and account memory, and output a structured meeting brief. Use when: calendar prep, what's on my schedule today, meeting context, prep for meetings, what do I have today, summarize today's meetings."
---

# Calendar Agent

Fetch today's Google Calendar events, categorize them by color into priority tiers, enrich each with account memory and Glean context, and produce a structured meeting brief ready for daily prep.

## Color-to-Category Reference

| colorId | Color | Category | Priority | Prep Depth |
|---------|-------|----------|----------|------------|
| `2`, `10` | Green (Sage/Basil) | Client Meetings | 1 - Highest | Full brief: account memory, Glean, SF opp, talking points |
| `5` | Yellow (Banana) | BizDev | 2 - High | Opp context, MEDDPICC, proposal docs, competitive intel |
| `11` | Red (Tomato) | Delivery Execution | 3 - High | Project status, open risks, resource/timecard context |
| `8` | Gray (Graphite) | Deal Review | 4 - Medium | Pipeline summary, deal stage, MEDDPICC score |
| `4` | Salmon (Flamingo) | Pre-Delivery Ops | 5 - Medium | SOW status, kickoff readiness, resource requests |
| `1`, `3` | Purple (Lavender/Grape) | Working Time | 6 - Low | Acknowledge only — no prep needed |
| `7`, `9` | Blue (Peacock/Blueberry) | Default / Admin | 7 - Low | Basic attendee context only |
| none | No color | Uncategorized | 8 - Low | List only |

## Prerequisites

- Account memory files live in `/memories/` — check for `<account_slug>_account_briefing.md` or `<account_slug>_*.md`
- The Google Calendar API requires IT enablement on the Snowflake-managed GCP project (RITM0566995 / project: symbolic-wind-489721-n4). Until enabled, use the Gmail fallback below.

## Workflow

### Step 1: Fetch Today's Events

**Try Method A first, fall back to B or C if it fails.**

**Method A — Google Calendar MCP (preferred when available)**

Call `mcp_google-worksp_list_events` with:
- `time_min`: today at 00:00:00 local time (RFC3339 format)
- `time_max`: today at 23:59:59 local time (RFC3339 format)
- `max_results`: 50

If this returns a Calendar API error, proceed to Method B.

---

**Method B — Gmail Calendar Invite Fallback (use when Calendar API unavailable)**

Search Gmail for today's meeting invites and accepted events:

```
mcp_google-worksp_search_emails
  query: "subject:(invite OR invitation OR calendar) after:yesterday before:tomorrow"

mcp_google-worksp_search_emails  
  query: "has:attachment filename:ics after:2d"

mcp_google-worksp_search_emails
  query: "from:calendar-notification@google.com OR from:calendar@google.com after:2d"
```

For each result, `mcp_google-worksp_read_email` to extract:
- Meeting title (from subject, strip "Invitation:" / "Accepted:" prefix)
- Date/time (from email body or .ics attachment text)
- Attendees (from body)
- Google Meet / Zoom link (from body)
- Organizer

**Important:** Gmail fallback cannot read colorId — ask the user to categorize ambiguous meetings:
> "I found [N] meetings via Gmail. I can't read calendar colors this way. Can you tell me which of these are Client Meetings vs BizDev vs Delivery? Or just list the names and I'll make my best guess."

Alternatively, make a best-guess categorization based on:
- Meeting title keywords: "sync", "check-in", "status" → likely Delivery (Red) or Admin (Blue)
- Company name in title that matches account memory → likely Client Meeting (Green)
- "BD", "discovery", "intro", "demo" → likely BizDev (Yellow)
- "deal review", "pipeline" → Deal Review (Gray)
- "kickoff", "onboarding", "pre-delivery" → Pre-Delivery Ops (Salmon)
- Name-only (e.g., "1:1 with [Name]") → Admin/Internal (Blue)

---

**Method C — Manual Schedule Paste (ultimate fallback)**

If both A and B yield no results, ask:
> "I wasn't able to pull your calendar automatically. Please paste your schedule for today (you can copy it from Google Calendar's day view or just list your meetings with times) and I'll prep from that."

Parse the pasted text: extract time, title, attendees for each event.

---

### Step 2: Categorize and Sort Events

For each event:
1. Read the `colorId` field (may be absent if inheriting calendar color — treat absent as `7` / Default)
2. Map to category using the reference table above
3. Skip declined events (`attendees[].self.responseStatus == "declined"`)
4. Sort output: Green → Yellow → Red → Gray → Salmon → Purple → Blue → Uncategorized
5. Within each category, sort by start time ascending

### Step 3: Enrich — Client Meetings (Green, colorId 2/10)

For each Client Meeting, run in order:

**a. Account Memory Check**
- Extract company name from event title (remove meeting verbs: "call with", "sync with", "meeting:", etc.)
- Run `memory view /memories/` and look for `<company_slug>_account_briefing.md` or matching file
- If found: read and extract the **Open Items** section and last session summary
- Note last contact date from memory file

**b. Glean Context**
- `mcp_glean2_search` query: `"<Company Name>"` — limit 5 results
- `mcp_glean2_search` query: `"<Company Name> proposal OR SOW OR opportunity"` — limit 3 results
- Note any recently modified docs, emails, or decks

**c. Account Finder**
- Invoke `account_finder` skill with the company name
- Extract: `account_id`, `account_owner`, `SE name`, `open opportunity name + stage`
- Construct Salesforce URL: `https://snowflake.lightning.force.com/lightning/r/Account/<account_id>/view`

**d. Talking Points**
- Generate 3-5 concise talking points based on:
  - Open Items from account memory
  - Recent Glean activity
  - Opportunity stage and next steps
  - Any risks or blockers noted in memory

**e. Output block:**
```
[HH:MM] CLIENT MEETING — <Title>
Attendees: <names>
Account: <Company> | Owner: <AE> | SE: <SE>
SF Opportunity: <Opp Name> — Stage: <Stage>
Last Contact: <date from memory>
Open Items:
  • <item 1>
  • <item 2>
Talking Points:
  • <point 1>
  • <point 2>
  • <point 3>
Glean: <top doc/email reference>
```

### Step 4: Enrich — BizDev (Yellow, colorId 5)

For each BizDev meeting:

**a.** Extract company or topic from event title
**b.** `mcp_glean2_search` for `"<company/topic> proposal OR deck OR opportunity"` — limit 5
**c.** Invoke `account_finder` to get Salesforce opportunity context
**d.** If opportunity found, note MEDDPICC completeness if visible in results
**e.** Search Drive: `mcp_google-worksp_search_drive` for `"<company> proposal"` or `"<company> SOW"`

**Output block:**
```
[HH:MM] BIZDEV — <Title>
Company/Topic: <name>
SF Opportunity: <name> — Stage: <stage>
Proposal/Deck: <Drive link if found>
Key Prep: <1-2 sentences from Glean context>
```

### Step 5: Enrich — Delivery Execution (Red, colorId 11)

For each Delivery meeting:

**a.** Extract account/project name from event title
**b.** Check account memory for open project risks or action items
**c.** `mcp_glean2_search` for `"<project/account> status OR risk OR milestone"` — limit 3
**d.** Note if timecard/resource requests are relevant (flag if end of week)

**Output block:**
```
[HH:MM] DELIVERY — <Title>
Project/Account: <name>
Open Risks: <from memory or Glean>
Action Items: <from memory Open Items>
Timecard Note: <if applicable>
```

### Step 6: Enrich — Deal Review (Gray, colorId 8)

For each Deal Review:

**a.** `mcp_glean2_search` for `"<topic/account> pipeline OR deal OR MEDDPICC"` — limit 3
**b.** Note deal stage and any recent activity

**Output block:**
```
[HH:MM] DEAL REVIEW — <Title>
Context: <1-2 lines from Glean>
```

### Step 7: Enrich — Pre-Delivery Ops (Salmon, colorId 4)

For each Pre-Delivery Ops meeting:

**a.** Check account memory for SOW status, kickoff readiness
**b.** `mcp_glean2_search` for `"<account> SOW OR kickoff OR resource"` — limit 3

**Output block:**
```
[HH:MM] PRE-DELIVERY OPS — <Title>
SOW/Kickoff Status: <from memory or Glean>
```

### Step 8: Working Time & Admin (Purple / Blue)

List these events with time and title only — no enrichment. Add a note: "(Focus block — no prep needed)" for purple. "(Admin/internal)" for blue.

### Step 9: Output

Return a structured object with:
- `meeting_count`: total number of events
- `priority_meetings`: list of Green + Yellow events with full enrichment
- `delivery_meetings`: Red events with enrichment
- `ops_meetings`: Gray + Salmon events with enrichment
- `focus_blocks`: Purple events
- `admin_meetings`: Blue + uncategorized events
- Full formatted text brief for display in chat

Pass this structured output to `browser-prep` and include it in the `daily-prep` final briefing.

## Stopping Points

- If all three methods fail to return any events: output a minimal briefing and proceed to comms-triage
- If more than 10 enriched meetings: ask user if they want full enrichment for all or top-priority only

## Notes

- **Calendar API status:** Requires IT RITM on project `symbolic-wind-489721-n4`. Until enabled, Method B (Gmail) is the primary path. To request enablement, submit a ticket referencing RITM0566995 and ask for `calendar-json.googleapis.com` to be enabled.
- Today's date/time for RFC3339 construction: use the `env` context which provides today's date
- colorId can be absent (event inherits calendar color) — treat absent as Blue/Default when using Method A
- When using Method B (Gmail), colorId is unavailable — use title-keyword heuristics for categorization
- All-day events: include in list but skip Glean enrichment unless it's a Client or BizDev event
- Multi-hour blocks (3+ hours) are likely Working Time regardless of color — flag but don't over-prep
