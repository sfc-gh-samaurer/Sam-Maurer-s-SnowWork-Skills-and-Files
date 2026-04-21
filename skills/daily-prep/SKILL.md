---
name: daily-prep
description: "Full daily preparation routine. Fetches today's calendar, enriches each meeting with context, opens browser tabs, triages email and Slack, creates draft responses, and logs follow-up tasks. The master orchestrator for starting your workday. Use when: prep me for today, morning prep, daily prep, set me up for the day, what's on my plate today, prepare for today, start my day, daily briefing, day prep."
---

# Daily Prep

Full daily prep orchestrator. Runs `calendar-agent` → `browser-prep` → `comms-triage` in sequence and delivers a complete daily briefing in chat.

**Trigger phrases:** "prep me for today" · "morning prep" · "daily prep" · "set me up for the day" · "what's on my plate today" · "prepare for today" · "start my day"

## Prerequisites

- Google Workspace MCP connected (Gmail, Drive, Docs, Sheets)
- Slack MCP connected
- Streamlit apps running on localhost:8501, 8502, 8504, 8505 (LaunchAgents handle auto-start)
- **Note:** Google Calendar API requires IT enablement (RITM0566995, project: symbolic-wind-489721-n4). Until enabled, calendar-agent uses Gmail invite fallback automatically — no action needed to use daily-prep.

## Orchestration Sequence

```
Step 1 → calendar-agent     Fetch + enrich today's meetings
Step 2 → browser-prep       Build Quick Links per meeting (no tab opening)
Step 3 → comms-triage       Triage Gmail + Slack (last 5 days) + log tasks
Step 4 → Final briefing     Synthesize everything into daily summary
```

Run each step sequentially. Pass calendar-agent output directly into browser-prep.

---

## Step 1: Run calendar-agent

Invoke the `calendar-agent` skill. It will:
- Fetch today's Google Calendar events
- Categorize by colorId (see color map below)
- Enrich Client Meetings, BizDev, and Delivery meetings with account memory + Glean context
- Return structured meeting list

**Color reference (quick):**

| Color | Category | colorId |
|-------|----------|---------|
| 🟢 Green | Client Meetings | `2`, `10` |
| 🟡 Yellow | BizDev | `5` |
| 🔴 Red | Delivery Execution | `11` |
| ⚫ Gray | Deal Review | `8` |
| 🟠 Salmon | Pre-Delivery Ops | `4` |
| 🟣 Purple | Working Time | `1`, `3` |
| 🔵 Blue | Default / Admin | `7`, `9` |

While calendar-agent runs, announce to the user:
> "Fetching today's calendar and enriching meetings with context..."

---

## Step 2: Run browser-prep

Invoke the `browser-prep` skill with the calendar-agent output. It will:
- Open 5 daily utility tabs (Gmail, Slack, Certinia, PM App, Resource Requests) via `open_browser`
- Build a **Quick Links** section for each meeting — relevant Drive docs, Salesforce links, Zoom links
- Search Drive and account memory for recently-worked files per account
- Return a formatted link list (does NOT open meeting-specific tabs)

Announce:
> "Building Quick Links for today's meetings..."

---

## Step 3: Run comms-triage

Invoke the `comms-triage` skill. It will:
- Search Gmail for emails needing response from the **last 5 business days** (unread, starred, important, external)
- Flag customer emails (non-@snowflake.com) with urgency scoring: 🔴 High / 🟡 Medium / 🟢 Low
- Review Slack DMs and mentions
- Create draft email replies for P1/P2 items (never send)
- Log all action items to the Daily Task Log Google Sheet

Announce:
> "Triaging email and Slack (last 5 business days)..."

---

## Step 4: Final Daily Briefing + Google Doc

After all three sub-skills complete:

### 4a. Create/Update the Google Doc

1. Determine today's doc title: `Daily Prep YYYY-MM-DD`
2. Check if a doc with this title already exists in the Daily Prep folder (ID: `1CVeyE8ZQqwZaISyL49lRfw2FRjOEu-_d`). If yes, update it; if no, create it.
3. Write the full briefing content using the **Google Doc format** below.
4. **Always open the doc in the browser** using `open_browser`:
   ```
   open_browser("https://docs.google.com/document/d/{doc_id}/edit")
   ```

> **⚠️ CRITICAL — Google Doc formatting rule:**
> `mcp_google-worksp_create_document` converts markdown to Google Docs format, but
> **pipe/markdown tables (`| col | col |`) are NOT converted — they render as raw text.**
> Use the heading + bullet format below for ALL tabular data in the doc.
> Markdown tables are fine in chat (Step 4b) but MUST NOT appear in the doc content.

#### Google Doc content format

Use this exact structure for `mcp_google-worksp_create_document` `content` parameter:

```markdown
# Daily Prep — [Day, Month Date, Year]
*Auto-generated at [HH:MM AM/PM CDT]*

---

## ⚠️ Schedule Conflicts — Resolve Now

**[N]-way conflict from [START]–[END] CDT:**

- **[HH:MM AM/PM]** — [Meeting Title] → **[Action: Keep / Reschedule / Delegate]**
- **[HH:MM AM/PM]** — [Meeting Title] → **[Action]**
- **[HH:MM AM/PM]** — [Meeting Title] → **[Action]**

**Recommendation:** [1–2 sentence decision guidance]

---

## Today's Schedule

### 🔴 Client Meetings

**[HH:MM AM/PM] — [Meeting Title]**
- Attendees: [names]
- Context: [account memory snippet]
- Notes: [description first line]

**[HH:MM AM/PM] — [Meeting Title]**
- Attendees: [names]
- Context: [account memory snippet]

### 🟡 BizDev

**[HH:MM AM/PM] — [Meeting Title]**
- Context: [1-line prep note]

### 🔴 Delivery Execution

**[HH:MM AM/PM] — [Meeting Title]**
- Open items: [from account memory]

### ⚫ Deal Reviews & Pre-Delivery Ops

**[HH:MM AM/PM] — [Meeting Title]** — [one-line context]

### 🔵 Admin / Internal

- [HH:MM AM/PM] — [Meeting Title]
- [HH:MM AM/PM] — [Meeting Title]

### 🟣 Focus Blocks & Working Time

- [HH:MM AM/PM] — [Meeting Title]

---

## 📬 Communications Requiring Action

**Gmail — [N] items:**
- **[P1]** [Sender] — *[Subject]* → [action]
- **[P2]** [Sender] — *[Subject]* → [action]

**Slack — [N] items:**
- [channel/person]: [message summary] → [action]

---

## ✅ Today's Action Items

1. **[P1]** [Source] — [Action description]
2. **[P1]** [Source] — [Action description]
3. **[P2]** [Source] — [Action description]

*[N] total items logged → [Google Sheet URL]*

---

*Generated by daily-prep skill | [Date]*
*Say "prep me for today" in SnowWork for AI-enriched briefing*
```

### 4b. Output the briefing in chat

---

```
╔══════════════════════════════════════════════════════╗
  DAILY PREP — [Day, Month Date, Year]
  Prepared at [HH:MM AM/PM]
╚══════════════════════════════════════════════════════╝

TODAY AT A GLANCE
  [N] total events  |  [N] client meetings  |  [N] BizDev  |  [N] delivery
  [N] emails need attention  |  [N] Slack items flagged
  [N] browser tabs opened  |  [N] tasks logged

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 CLIENT MEETINGS (Priority 1)
[For each green meeting:]
  [HH:MM] [Meeting Title]
  Account: [Company] | AE: [name] | SE: [name]
  SF Opp: [name] — Stage: [stage]
  Talking Points:
    • [point 1]
    • [point 2]
    • [point 3]
  Open Items: [from memory]
  Links: [SF Account URL] | [SF Opp URL] | [Drive folder URL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟡 BIZDEV MEETINGS (Priority 2)
[For each yellow meeting:]
  [HH:MM] [Meeting Title]
  Opportunity: [name] — Stage: [stage]
  Prep: [1-2 sentence context]
  Links: [SF Opp URL] | [Proposal Doc URL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 DELIVERY MEETINGS (Priority 3)
[For each red meeting:]
  [HH:MM] [Meeting Title]
  Project: [name] | Open Risks: [from memory]
  Action Items: [from account memory Open Items]
  Links: [PM App URL] | [SOW Drive URL] | [SF Account URL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚫ DEAL REVIEWS & PRE-DELIVERY OPS
[For each gray/salmon meeting:]
  [HH:MM] [Meeting Title] — [context line]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟣 FOCUS BLOCKS & ADMIN
[List with time and title only]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📬 COMMUNICATIONS REQUIRING ACTION
  Gmail — Top items:
    P1: [N] customer emails | [N] drafts created
      → [Sender]: [Subject] — [Gmail link]
      → [Sender]: [Subject] — [Gmail link]
    P2: [N] internal items | [N] drafts created

  Slack — Top items:
    [N] DMs | [N] mentions | [N] channel items
      → [channel/person]: [message summary]
      → [channel/person]: [message summary]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ TODAY'S ACTION ITEMS (logged to Daily Task Log)
  1. [P1] [Source] — [Action description]
  2. [P1] [Source] — [Action description]
  3. [P2] [Source] — [Action description]
  4. [P2] [Source] — [Action description]
  5. [P2] [Source] — [Action description]
  ... + [N] more in the Daily Task Log sheet

  Task Log: [Google Sheet URL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗  QUICK LINKS
  Utilities: Gmail | Slack | Certinia | PM App | Resource Requests
  [HH:MM] [Meeting Title]
    • [Link label]: [URL]
    • [Link label]: [URL]
  [HH:MM] [Meeting Title]
    • [Link label]: [URL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Have a great day. 
```

---

## Stopping Points

- **Calendar API unavailable:** calendar-agent will automatically fall back to Gmail invite search (Method B), then manual paste (Method C) — daily-prep does not need to stop
- **No meetings today:** Skip Step 2, proceed to Step 3, output a lighter briefing
- **More than 8 enriched meetings:** Ask user if they want full enrichment for all or top 5 by priority
- **Gmail/Slack unavailable:** Note in briefing and continue — do not fail the entire routine

## Scheduled Google Doc Output (6am Daily)

A **standalone Python script + macOS LaunchAgent** runs automatically at 6am every day:

- **Script:** `~/.snowflake/cortex/scripts/daily_prep_generator.py`
- **LaunchAgent:** `~/Library/LaunchAgents/com.snowflake.cortex.dailyprep.plist`
- **Log:** `~/.snowflake/cortex/logs/daily_prep.log`
- **Output folder:** Google Drive → Daily Prep folder (ID: `1CVeyE8ZQqwZaISyL49lRfw2FRjOEu-_d`)
- **Doc naming:** `Daily Prep YYYY-MM-DD`
- **Behavior:** Creates doc, opens it in browser automatically at 6am

The 6am script generates a structured schedule (no AI enrichment). For the full enriched briefing with account context, talking points, and Glean research, open SnowWork and say "prep me for today" — this runs the full skill pipeline and updates the same doc.

### End-of-run behavior (in both script and skill)
After the daily prep completes, **always open the Google Doc in the browser**:
```python
subprocess.run(["open", f"https://docs.google.com/document/d/{doc_id}/edit"])
```
Or via `open_browser` tool in SnowWork:
```
open_browser("https://docs.google.com/document/d/{doc_id}/edit")
```

### ⚠️  Required: Enable Calendar API (one-time, 30 seconds)
The 6am script requires Google Calendar API enabled in GCP project 25733770608:
https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=25733770608

Until enabled, the 6am script will exit with a clear error pointing to that URL.
The SnowWork skill uses **Glean** as the calendar source (no API enablement needed).

### Reload LaunchAgent after changes
```bash
launchctl unload ~/Library/LaunchAgents/com.snowflake.cortex.dailyprep.plist
launchctl load ~/Library/LaunchAgents/com.snowflake.cortex.dailyprep.plist
```

### Scheduling / Recurring Use via SnowWork
SnowWork skills are conversation-triggered. To run manually at any time, say "prep me for today".
- On Mondays: comms-triage looks back 72 hours (since Friday) instead of 48
- On Fridays: comms-triage adds end-of-week reminders (timecard, status reports, memory updates)

## Individual Sub-Skill Usage

Each sub-skill can also be run independently:

| What you say | Skill invoked |
|---|---|
| "what's on my calendar today" | `calendar-agent` only |
| "open tabs for today" | `browser-prep` only (will run calendar-agent if needed) |
| "triage my messages" | `comms-triage` only |
| "prep me for today" | `daily-prep` (all three) |

## Notes

- Run time estimate: 3-5 minutes for a typical day (5-8 meetings, 20-30 emails)
- Account memory enrichment adds ~30s per client meeting — most valuable investment in the routine
- The Daily Task Log sheet persists across days — review it at end of day to update statuses
- On Mondays: comms-triage looks back 72 hours (since Friday) instead of 48
- On Fridays: comms-triage adds end-of-week reminders (timecard, status reports, memory updates)
