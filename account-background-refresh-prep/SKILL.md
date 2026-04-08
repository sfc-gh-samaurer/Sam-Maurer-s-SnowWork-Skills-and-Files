---
name: account-background-refresh-prep
description: "Prepare comprehensive 2x2 Account meeting readout documents for Snowflake Services Delivery. Aggregates data from Salesforce, Glean (presentations/slides/docs), Google Calendar, Slack, and email to produce a Word (.docx) briefing covering: account team, customer stakeholders, recent interactions, follow-up action items, Services Delivery play (partner dynamics, platform enablement, bronze/silver/gold layers, migration vs greenfield, AI/ML), timelines, POC status, deal metrics, risks, and questions for meeting. Use for: 2x2 prep, account prep, account background, account refresh, account readout, meeting prep, deal review, account briefing, QBR prep."
---

# Account Background, Refresh and Prep

Generate comprehensive 2x2 Account meeting readout documents as formatted Word (.docx) files for Snowflake Services Delivery Practice Managers.

## Prerequisites

- `python-docx` installed (`pip install python-docx`)
- Glean access for searching Salesforce, Slack, GDrive, GCal, Gmail
- User-provided raw notes and/or attached images (deal summaries, org charts)

## Workflow

### Step 1: Gather Account Information

**Goal:** Collect the account name and user's raw notes.

**Actions:**

1. **Ask** user for account name and any raw notes they have:
   - Account name
   - Raw notes from recent meetings/calls
   - Any attached images (deal summary slides, org charts, etc.)

2. **Check memory** at `/memories/` for any existing briefing on this account (e.g., `<account>_account_briefing.md`)

3. **Check** if an account folder already exists at `/Users/michaelkelly/CoCo/Accounts/<Account_Name>/`

### Step 2: Search All Data Sources (Parallel)

**Goal:** Aggregate data from all available internal sources.

**Actions:** Execute ALL of the following Glean searches in parallel:

1. **Google Calendar** (`gcal` app filter): Search for account name + key people names
2. **Google Drive** (`gdrive` app filter): Search for account name + "Snowflake" for presentations, account plans, slide decks
3. **Salesforce** (`salescloud` app filter): Search for account name for opportunity data, deal stages, ACV
4. **Slack** (`slack` app filter): Search for account name + key people names for discussion threads
5. **Email** (`gmailnative` app filter): Search for account name + AE name + SE name for calendar invites and correspondence

**Try multiple query variations:**
- Full company name (e.g., "Advanced Drainage Systems")
- Common abbreviation (e.g., "ADS")
- Account name + key stakeholder names
- Account name + technical terms (e.g., "medallion", "migration", "Databricks")

**Note:** Salesforce searches via Glean often return no results for opportunity-level data. If Salesforce returns empty, rely on user notes and other sources. This is a known limitation.

### Step 3: Read Attached Images

**Goal:** Extract deal details from any user-attached images.

**Actions:**

1. **Read** any attached images using the Read tool (it supports visual analysis)
2. Extract: ACV, TACV, close date, use cases, champions, risks, next steps, org chart details
3. Cross-reference image data with user notes for consistency

### Step 4: Compile Readout Document

**Goal:** Produce a comprehensive readout in markdown format.

**Required Sections** (in this order):

```
# <Account Name> - 2x2 Account Readout
**Prepared:** <date> | **Deal Close Target:** <date>

## Account Overview
Table: Company, HQ, Size/Revenue, Industry, Current Tech Stack, Key Products/Services

## Account Team (Snowflake)
Table: AE, SE, RSD/RVP, SD Practice Director, SD Practice Manager

## Key Customer Stakeholders
Table: Name, Title, Role in Deal (Decision Maker/Champion/Influencer/Evaluator)

## Recent Interactions Timeline
### <Date>: <Event Name>
- Bullet points of what was discussed/decided

## Deal Summary
Table: ACV, TACV, Close Date, Stage, Budget status, Technical Win details, Implementation Target

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
Table: POC status, Budget, Deal Stage, Close Date, SI Selection, Implementation Kickoff, Meeting Cadence

## Your Open Action Items / Follow-Ups
Numbered list of specific action items for the SD Practice Manager

## Key Risks & Watch Items
Bulleted list of deal risks and things to monitor

## Questions for Next 2x2
Numbered list of specific questions to raise in the next meeting

## Data Sources
List of sources used and any gaps/limitations
```

### Step 5: Convert to Word Document

**Goal:** Generate a formatted .docx file with Snowflake branding colors.

**Actions:**

1. Save the markdown readout temporarily
2. **Execute** the conversion script:
   ```bash
   python3 /Users/michaelkelly/CoCo/md_to_docx.py "<temp_markdown_path>" "<output_docx_path>"
   ```
3. Output path convention: `/Users/michaelkelly/CoCo/Accounts/<Account_Name>/<Account_Abbreviation>_2x2_Readout.docx`
4. Create the account folder if it does not exist: `mkdir -p /Users/michaelkelly/CoCo/Accounts/<Account_Name>/`

### Step 6: Save to Memory

**Goal:** Store key account details for future reference.

**Actions:**

1. **Save** a briefing summary to `/memories/<account_lowercase>_account_briefing.md` with:
   - Account team
   - Customer stakeholders
   - Deal details (ACV, close date, stage)
   - SD play summary
   - Key risks
   - Sources used
   - Meeting cadence

## SD Offering Reference

| Offering | Price Range | Duration | Fit |
|---|---|---|---|
| QuickStart | ~$7K | 1-2 weeks | Quick entry, platform standup |
| Fast Track | $45-75K | 4-8 weeks | Platform setup, initial use cases, architecture design |
| RSA (Readiness Assessment) | Varies | 6-12 months | Complex environments needing ongoing guidance |
| AI/ML Expert Engagement | Varies | ~5 weeks | Synthetic data, ML use cases, Cortex AI |
| Migration Readiness Assessment | Varies | 2-4 weeks | De-risk migration before kickoff |

## SD Play Classification Guide

Classify the account's SD play based on these patterns:

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

- After Step 1 if account name or notes are ambiguous
- After Step 4 if user wants to review content before Word conversion

## Output

- Formatted Word document (.docx) at `/Users/michaelkelly/CoCo/Accounts/<Account_Name>/`
- Memory briefing at `/memories/<account>_account_briefing.md`
- Confirm file paths to user upon completion

## Troubleshooting

**Glean searches return no relevant results:**
- Try alternate query terms (abbreviations, people names, technical terms)
- Fall back to user-provided notes and images
- Note data gaps in the "Data Sources" section of the readout

**python-docx not installed:**
- Run: `pip3 install python-docx`

**md_to_docx.py not found:**
- The conversion script should exist at `/Users/michaelkelly/CoCo/md_to_docx.py`
- If missing, generate a new one that converts markdown tables/headings/lists to formatted Word with Snowflake blue (#29B5E8) heading colors and table header shading
