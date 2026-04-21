---
name: comms-triage
description: "Review Gmail and Slack for messages requiring attention. Create email drafts (never send), create Slack drafts or response notes, and log follow-up tasks to a Google Sheet. Use when: triage my messages, what needs my attention, review my inbox, check my email, slack messages, follow-up tasks, communications triage, what do I need to respond to."
---

# Comms Triage

Review Gmail and Slack for items requiring attention across the last 5 business days. Create draft responses (never send). Log all follow-up items to a Google Sheet.

## Core Rules

- **NEVER send any email or Slack message** — drafts only, always
- **NEVER mark emails as read** unless the user explicitly asks
- **Triage, don't resolve** — surface and queue, not act
- **Customer emails always P1** — any email from a non-@snowflake.com domain matching a known account

## Google Sheet Task Log

**Sheet ID:** `1Hd4CUpd_mrl1Rp0glT0U1BMewknwac12XW2C_t_zXgM`
**Range:** `Task Log!A1`
**Columns:** `Date | Priority | Source | From/Channel | Subject/Context | Suggested Action | Deep Link | Status`

---

## Workflow

### Step 1: Gmail Triage — Last 5 Business Days

**A. Run three searches** (deduplicate by message ID):

```
1. Recent customer/external emails needing response:
   mcp_google-worksp_search_emails
   query: "from:(-snowflake.com) after:5d -category:promotions -category:social -category:updates"
   max_results: 30

2. Starred or important (any age within 5 business days):
   mcp_google-worksp_search_emails
   query: "is:starred OR is:important after:5d -category:promotions"
   max_results: 20

3. Internal emails needing a response:
   mcp_google-worksp_search_emails
   query: "from:snowflake.com is:unread after:5d -category:promotions"
   max_results: 20
```

**B. Prioritize each email:**

| Priority | Criteria |
|----------|----------|
| P1 — Customer | Sender domain is NOT @snowflake.com AND matches a known account name (from `/memories/` files), OR subject contains a known customer/account name |
| P1 — Urgent | Subject contains: urgent, action required, ASAP, deadline, decision needed, by EOD, by EOM, "time sensitive" |
| P1 — Customer Awaiting Response | External email where Michael Kelly sent the last message MORE than 48 hours ago with no reply — escalate |
| P2 — Internal Action | From @snowflake.com, contains a question, request, approval ask, or "can you" / "could you" / "please" |
| P3 — FYI | Newsletters, notifications, no direct ask, CC-only threads |

**C. For P1 customer emails — assess urgency:**

After prioritizing, add an **urgency flag** to each P1 customer email:
- 🔴 **High** — unanswered for 3+ business days, or has explicit deadline
- 🟡 **Medium** — unanswered for 1-2 business days, or has open question
- 🟢 **Low** — just received today, no deadline, FYI-adjacent

Read full thread with `mcp_google-worksp_get_email_thread` for each P1 before drafting.

**D. Draft Responses for P1 and P2:**

For each P1/P2 that needs a response:
1. Read the full thread
2. Draft a reply: acknowledge the ask, give a thoughtful response using account memory context, end with clear next steps
3. `mcp_google-worksp_create_draft` — never send
4. Note draft in the log row

**E. Log all P1 and P2 to Task Sheet:**
```
Date | Priority | Gmail | Sender name + email | Subject | "Review draft" or action | mailto deep link | Pending
```

**F. P3:** Count only — "N FYI emails skipped."

---

### Step 2: Slack Triage

**A. Fetch:**
1. Unread DMs — priority if from customers, execs, cross-functional partners
2. @mentions in any channel
3. Key channels: `#ps-delivery`, `#ps-americas`, project channels from account memory

**B. Prioritize:**

| Priority | Criteria |
|----------|----------|
| P1 | DM asking a question or needing a decision |
| P1 | @mention needing your response |
| P2 | Channel thread where you're the right person to respond |
| P3 | General updates, emoji reactions, FYI |

**C. Draft and log P1/P2** — same pattern as Gmail.

---

### Step 3: Follow-Up Tasks from Account Memory

Check memory files for active accounts with Open Items marked "this week" or "today". Log each as P2.

---

### Step 4: End-of-Week Reminders (Thursday/Friday only)

- Add row: "Submit timecard" → https://snowflake.lightning.force.com/lightning/n/pse__Timecard_Entry
- Add row: "Update account memory for active engagements"
- Add row: "Send weekly status reports" (if applicable)

---

### Step 5: Output Summary

```
COMMS TRIAGE SUMMARY
────────────────────
Gmail (last 5 business days)
  Customer emails reviewed:  [N]
  P1 🔴 High urgency:        [N] — [N] drafts created
  P1 🟡 Medium urgency:      [N] — [N] drafts created
  P2 Internal action:        [N] — [N] drafts created
  P3 FYI/skipped:            [N]

Slack
  DMs: [N] | Mentions: [N] | P1/P2 items: [N]

Tasks logged to Daily Task Log: [N] rows
Sheet: https://docs.google.com/spreadsheets/d/1Hd4CUpd_mrl1Rp0glT0U1BMewknwac12XW2C_t_zXgM/edit

Top Actions Required:
  1. 🔴 [Customer] [Sender] — [Subject] — [urgency reason] → [draft link]
  2. 🔴 [Customer] ...
  3. 🟡 [Customer] ...
  4. [P2 internal item]
  ... (up to 5)
```

---

## Stopping Points

- If Task Log sheet unreachable: warn and output task list in chat
- If Slack MCP unavailable: skip, note in summary
- If 20+ P1/P2 emails: surface top 10 by recency + urgency, ask if user wants the rest

## Notes

- Customer domain detection: match sender `@domain.com` against known account names in `/memories/`
- Always read the full thread before drafting — context matters
- Subject prefix for drafts: always `Re: <original subject>`
- Slack deep links: `https://snowflake.slack.com/archives/<channel_id>/p<timestamp_no_dot>`
- Task sheet accumulates across days — always include today's date on each row
