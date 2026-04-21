---
name: account-background-refresh-prep
description: "Prepare comprehensive Account meeting readout documents for Snowflake Services Delivery. Aggregates data from Salesforce, Glean (presentations/slides/docs), Google Calendar, Slack, and email to produce a Google Doc briefing covering: open action items (at top), recent interactions, account team, customer stakeholders, Services Delivery play (partner dynamics, platform enablement, bronze/silver/gold layers, migration vs greenfield, AI/ML), timelines, POC status, deal metrics, risks, and questions for meeting. Use for: 2x2 prep, account prep, account background, account refresh, account readout, meeting prep, deal review, account briefing, QBR prep, update me on an account, prep me on an account."
---

# Account Background, Refresh and Prep

Generate comprehensive Account meeting readout documents as Google Docs for Snowflake Services Delivery Practice Managers. Triggered by: "prep me on [account]", "update me on [account]", "account prep", "account background", "2x2 prep".

## Prerequisites

- Google Workspace MCP configured (for Google Docs and Drive)
- Glean access for searching Salesforce, Slack, GDrive, GCal, Gmail

## Workflow

### Step 1: Gather Account Information

**Goal:** Collect the account name, raw notes, and existing memory context.

**Actions (run in parallel):**

1. **Ask** user for account name and any raw notes (if not already provided in the prompt):
   - Account name
   - Raw notes from recent meetings/calls
   - Any attached images (deal summary slides, org charts, etc.)

2. **Check memory** at `/memories/` for any existing briefing on this account (e.g., `<account>_account_briefing.md`) — do this immediately alongside asking

3. **Read** any attached images using the Read tool (it supports visual analysis) — extract ACV, TACV, close date, use cases, champions, risks, next steps, org chart details

### Step 2: Search All Data Sources (Fully Parallel)

**Goal:** Aggregate data from all available internal sources simultaneously.

**CRITICAL: Launch ALL of the following searches in a SINGLE parallel tool call batch:**

1. **Google Calendar** (`gcal` app filter): `"[AccountName]"` + key stakeholder names — find past and upcoming meetings
2. **Google Drive** (`gdrive` app filter): `"[AccountName] Snowflake"` — presentations, account plans, slide decks
3. **Salesforce** (`salescloud` app filter): `"[AccountName]"` — opportunity data, deal stage, ACV
4. **Slack** (`slack` app filter): `"[AccountName]"` + key stakeholder names — recent discussion threads, action items
5. **Email** (`gmailnative` app filter): `"[AccountName]"` + AE name + SE name — correspondence, calendar invites

**Also in the same parallel batch:**
6. **Glean general search**: `"[AccountName] action items follow up"` — surface any outstanding tasks
7. **Glean general search**: `"[AccountName] meeting notes recap"` — find meeting summaries and recaps

**Query variation strategy (apply to each source):**
- Full company name (e.g., "PPM America")
- Common abbreviation (e.g., "PPM")
- Account name + key stakeholder names
- Account name + technical terms (e.g., "migration", "Snowflake", "POC")

**Note:** Salesforce Glean searches often return limited opportunity-level data. If empty, rely on user notes and memory. This is a known limitation.

### Step 3: Compile Readout Content

**Goal:** Produce comprehensive readout content with action items and recent interactions FIRST.

**Required Sections** (strictly in this order — action items and interactions go at the TOP):

```
# [Account Name] — Account Readout
**Prepared:** [date] | **Deal Close Target:** [date if known]

---

## ⚡ Your Open Action Items
> Items you (the SD PM) need to follow up on before or after this meeting.
1. [Action item with due date if known]
2. [Action item]
...

## 📅 Recent Interactions & Meeting History
> Most recent interactions first.

### [Most Recent Date]: [Event Name/Type]
- Key discussion points
- Decisions made
- Who attended

### [Earlier Date]: [Event Name/Type]
- Key discussion points
...

---

## Account Overview
Table: Company, HQ, Size/Revenue, Industry, Current Tech Stack, Key Products/Services

## Account Team (Snowflake)
Table: AE, SE, RSD/RVP, SD Practice Director, SD Practice Manager

## Key Customer Stakeholders
Table: Name, Title, Role in Deal (Decision Maker/Champion/Influencer/Evaluator)

## Deal Summary
Table: ACV, TACV, Close Date, Stage, Budget Status, Technical Win Details, Implementation Target

## Services Delivery Play
### Migration/Implementation Overview
- Current State vs Target State
- Primary use cases

### Partner Dynamics
Table: Partner, Status, Notes

### Services Delivery Model
- Platform Enablement scope
- Bronze Layer (Ingestion) scope
- Transformations (Silver/Gold) scope
- Migration Readiness scope
- AI/ML scope (if applicable)
- Architecture Advisory scope

### Recommended SD Offerings
Table: Offering (QuickStart/Fast Track/RSA/AI-ML Expert/Migration Readiness), Fit, Notes

### Business Value Drivers
- Cost reduction, productivity, accessibility, etc.

## Key Use Cases
Table: Use Case, Description, Priority

## POC / Timeline Status
Table: POC Status, Budget, Deal Stage, Close Date, SI Selection, Implementation Kickoff, Meeting Cadence

## Key Risks & Watch Items
- Bulleted list of deal risks and things to monitor

## Questions for Next Meeting
1. Numbered list of specific questions to raise

## Data Sources & Gaps
- List of sources consulted and any data gaps
```

### Step 4: Create Google Doc and Save to Drive

**Goal:** Create a Google Doc, place it in the correct account folder in Google Drive, and open it.

**Actions (steps 4a and 4b in parallel where possible):**

**4a. Find or create the Google Drive folder chain:**
1. Search Drive for the account folder: `mcp_google-worksp_search_drive` query=`"[AccountName]"` under Accounts folder `1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck`
2. If no account folder found: `mcp_google-worksp_create_drive_folder` name=`"[AccountName]"`, parent_id=`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck`
3. Search for `"Account Prep"` subfolder inside the account folder
4. If no Account Prep subfolder found: `mcp_google-worksp_create_drive_folder` name=`"Account Prep"`, parent_id=`{account_folder_id}`

**4b. Create the Google Doc:**
1. Use `mcp_google-worksp_create_document` with:
   - title: `"[AccountName] — Account Readout [YYYY-MM-DD]"`
   - content: full markdown readout from Step 3
2. Move the doc: `mcp_google-worksp_move_file` file_id=`{doc_id}`, new_folder_id=`{account_prep_folder_id}`

**4c. Open the doc in the user's default browser:**
- Use `bash` tool: `open "https://docs.google.com/document/d/{doc_id}/edit"`
- This opens in the user's real browser (Chrome/Safari), NOT the SnowWork panel
- Confirm the URL to the user so they can bookmark it

### Step 5: Save to Memory

**Goal:** Store key account details for future reference.

**Actions:**

1. **Save/update** briefing summary at `/memories/<account_lowercase>_account_briefing.md` with:
   - Account team
   - Customer stakeholders
   - Deal details (ACV, close date, stage)
   - SD play summary
   - Key risks
   - Most recent interaction date and summary
   - Open action items
   - Artifacts (Google Doc URL, deck links, etc.)

## Formatting Rules

### Bullet Lists
When passing content to `mcp_google-worksp_create_document`, use markdown `- item` syntax for all bullet lists. **Never** use `• item` (bullet character).

### Tables — CRITICAL
**The `mcp_google-worksp_create_document` tool does NOT render markdown table syntax.** Markdown pipes (`| col | col |`) appear as raw text in the output.

**Always use `mcp_google-worksp_batch_update_document` to insert real Google Docs tables.**

#### Workflow for tables:
1. Create the document first using `mcp_google-worksp_create_document` with **NO markdown tables** — use plain text placeholders like `[TABLE: Account Overview]` where each table goes.
2. Use `mcp_google-worksp_get_document_structure` to get the document structure and find the index of each placeholder.
3. For each table, call `mcp_google-worksp_batch_update_document` with `insertTable` requests to replace the placeholder with a real table, then populate cells with `insertText`.

#### Table API pattern:
```json
[
  {
    "insertTable": {
      "rows": 3,
      "columns": 2,
      "location": { "index": <index_of_placeholder_newline> }
    }
  }
]
```
Then delete the placeholder text and insert cell content using `insertText` at the cell start indices from `get_document_structure`.

#### Simpler alternative for small tables (2-column key/value):
Instead of API tables, use **bold key + plain value** format in the document body — this renders cleanly and requires no post-processing:
```
**Company:** PPM America
**HQ:** Chicago, IL
**Industry:** Asset Management
```
Use this format for all 2-column lookup tables (Account Overview, Deal Summary, POC Status, etc.).
Reserve the full `insertTable` API approach for multi-column tables (3+ columns) like migration estimation breakdowns.

## SD Offering Reference

| Offering | Price Range | Duration | Fit |
|---|---|---|---|
| QuickStart | ~$7K | 1-2 weeks | Quick entry, platform standup |
| Fast Track | $45-75K | 4-8 weeks | Platform setup, initial use cases, architecture design |
| RSA (Readiness Assessment) | Varies | 6-12 months | Complex environments needing ongoing guidance |
| AI/ML Expert Engagement | Varies | ~5 weeks | Synthetic data, ML use cases, Cortex AI |
| Migration Readiness Assessment | Varies | 2-4 weeks | De-risk migration before kickoff |

## SD Play Classification Guide

| Pattern | Indicators |
|---|---|
| **Platform Enablement** | New to Snowflake, needs Private Link/SSO/governance setup |
| **Bronze Layer (Ingestion)** | Needs data pipeline setup, OpenFlow/Snowpipe/CDC |
| **Transformations (Silver/Gold)** | Medallion architecture, dbt, Dynamic Tables |
| **Migration (E2E with SD)** | Snowflake SD owns full migration, no SI partner |
| **Migration (Piece of Pie with SI)** | SI partner leads, SD does architecture advisory/enablement |
| **Greenfield Implementation** | Net-new build, no legacy migration |
| **AI/ML** | Cortex AI, ML functions, data science workloads |

## Stopping Points

- After Step 1 if account name is ambiguous and cannot be inferred from context
- After Step 3 if user wants to review content before creating the Google Doc

## Output

- Google Doc at: SnowWork → Accounts → {AccountName} → Account Prep
- Doc auto-opened in browser
- Memory briefing updated at `/memories/<account>_account_briefing.md`
- Confirm Google Doc URL to user upon completion

## Troubleshooting

**Glean searches return no relevant results:**
- Try alternate query terms (abbreviations, people names, technical terms)
- Fall back to user-provided notes and memory file
- Note data gaps in "Data Sources & Gaps" section

**Google Workspace MCP not configured:**
- Run `skill: google_workspace_install` to set up
