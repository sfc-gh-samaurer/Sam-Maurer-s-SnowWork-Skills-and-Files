---
name: implementation-roadmap-builder
description: "Create phased Implementation Roadmap Excel workbooks for Snowflake data platform engagements. Generates detailed task breakdowns by phase with subsections (Discovery, Ingestion, Transformation, UAT, Consumption/AI), plus a comprehensive Dependencies & Risks sheet. Use when: implementation planning, project roadmap, task breakdown, risk assessment, phase planning, delivery roadmap, project plan. Triggers: implementation roadmap, project plan, task breakdown, phased roadmap, delivery plan, risk register, implementation plan, phase tasks."
---

# Implementation Roadmap Builder

Generate a comprehensive phased Implementation Roadmap Excel workbook for a Snowflake data platform engagement. Breaks each phase into detailed tasks with subsections, dependencies, deliverables, and risk notes, plus a consolidated Dependencies & Risks register.

## Prerequisites

- `openpyxl` Python library available
- Source system inventory and domain mappings (ideally from `bronze-layer-planner` and `ingestion-to-consumption-mapper` outputs)
- Understanding of customer's implementation phases and business priorities

## Workflow

### Step 1: Gather Inputs

**Ask** the user for:
1. **Customer name**
2. **Phase structure** — number of phases, names, timelines, goals
3. **Source-to-phase assignments** — which sources are in which phase
4. **Domain-to-phase assignments** — which Silver/Gold domains per phase
5. **Special tracks** — any parallel workstreams (e.g., legacy migration, CRM migration)
6. **Key business context** — critical business outcomes per phase, executive stakeholders, sunset deadlines
7. **Existing artifacts** — Bronze Layer plan, Ingestion-to-Consumption map, architecture diagram

If prior artifacts exist, read them to auto-populate phase assignments and source/domain lists.

**⚠️ STOP**: Confirm phase structure, goals, and assignments before proceeding.

### Step 2: Design Task Breakdown per Phase

For each phase, generate tasks organized into these subsections:

**DISCOVERY / PLANNING / DESIGN**
- Source system discovery (one per source in that phase)
- Requirements workshops with business stakeholders
- Data model design and architecture decisions
- Integration design (API, CDC, file-based)

**DATA INGESTION (BRONZE LAYER)**
- One task per source system or source group
- Covers: connector setup, pipeline development, monitoring
- References specific ingestion pattern from Bronze plan

**TRANSFORMATION / MODELING / ORCHESTRATION (SILVER & GOLD)**
- One task per Silver domain being built in this phase
- One task per Gold domain being built in this phase
- Orchestration setup (Streams, Tasks, Dynamic Tables, dbt)

**UAT / TESTING**
- Bronze data quality validation (row counts, schema, freshness)
- Silver business rule validation with SMEs
- Gold output validation with business users
- End-to-end pipeline reliability testing
- AI/Cortex accuracy testing (if applicable)

**CONSUMPTION / BI CONNECTIONS / AI**
- Semantic View deployment
- Cortex Intelligence / AI use cases
- Dashboard / BI tool deployment
- Streamlit app deployment
- Self-service tool enablement

**Task attributes (columns):**
| Column | Description |
|--------|------------|
| # | Sequential task number within phase |
| Task | Short task name |
| Subsection | Discovery, Ingestion, Transform, Testing, Consumption |
| Description | 2-3 sentence detailed description of what this task entails |
| Source Systems / Components | Which systems or Snowflake components are involved |
| Dependencies | What must be complete before this task can start |
| Deliverable | Concrete output of this task |
| Risk / Notes | Known risks, assumptions, or important notes |

### Step 3: Build Dependencies & Risks Register

Consolidate all risks and dependencies into categories:

| Category | Examples |
|----------|---------|
| **Platform & Infrastructure** | Account provisioning, licensing, cloud infrastructure |
| **Source System Access** | API credentials, DBA access, network connectivity |
| **Data Quality & Business Logic** | Data quality issues, complex business logic, undocumented rules |
| **People & Knowledge** | SME availability, tacit knowledge loss, resource contention |
| **Third-Party & Contractual** | Vendor contracts, sunset deadlines, licensing |
| **Technical & Architecture** | NL query accuracy, migration complexity, scope creep |

**Risk attributes (columns):**
| Column | Description |
|--------|------------|
| # | Sequential number |
| Category | Risk/dependency category |
| Phase(s) | Which phases are affected |
| Dependency / Risk | Description |
| Type | Dependency or Risk |
| Severity | High, Medium, Low |
| Mitigation Strategy | How to address |
| Owner | Who is responsible |

### Step 4: Generate the Excel Workbook

Create a Python script using `openpyxl` that generates these sheets:

**Sheet 1: Summary Roadmap**
- One row per phase: Phase, Timeline, Goal, Key Deliverables, Source Systems, Silver Domains, Gold Domains, Key Dependencies, Key Risks
- High-level overview for executives

**Sheets 2-N: Phase Detail Sheets** (one per phase + parallel tracks)
- Named: "Phase 1 — [Short Name]", "Phase 2 — [Short Name]", etc.
- Header row with phase title, timeline, and goal
- Subsection headers as merged row dividers
- All tasks with full 8-column detail
- Auto-numbered within each phase

**Sheet N+1: Dependencies & Risks**
- Category section headers
- All risks and dependencies with full detail
- Severity color-coding: High=red fill, Medium=orange fill, Low=green fill

**Formatting:**
- Header row: dark blue fill (#11567F), white bold text
- Subsection dividers: medium gray fill, bold text
- Phase headers: phase-specific color (Phase 1=blue, Phase 2=purple, Phase 3=pink, Parallel=orange)
- Column auto-width, text wrapping on Description column
- Freeze panes

**⚠️ STOP**: Present task counts per phase and risk summary before generating Excel.

### Step 5: Generate and Deliver

1. Write the Python generation script
2. Execute to produce the Excel file
3. Report: total phases, tasks per phase, total risks, severity distribution

**Output location**: `<customer_directory>/<Customer>_Implementation_Roadmap.xlsx`

## Stopping Points

- ✋ Step 1: Phase structure confirmed
- ✋ Step 4: Task counts and risk summary reviewed

## Output

Multi-sheet Excel workbook with:
- Summary Roadmap (executive overview)
- Detailed phase sheets with subsection-organized tasks
- Consolidated Dependencies & Risks register with severity ratings

## Reference: Boxout Health Example

- 4 phases + 1 parallel track across 12 months
- Phase 1: 34 tasks (Foundation & POC, 5 sources)
- Phase 2: 45 tasks (Profitability & Automation, 14 sources)
- Phase 3: 53 tasks (Pricing & Advanced Intel, 26 sources)
- Parallel: 19 tasks (Siebel Migration)
- 32 risk/dependency items across 6 categories
- Total: 151 tasks + 32 risks

## Google Drive Output

After generating the XLSX locally, upload it to Google Drive as a Google Sheet.

**Folder path:** SnowWork → Accounts → {AccountName} → Implementation

**Step 1: Ensure folder chain exists**

Use `mcp_google-worksp_search_drive` to check if each folder exists before creating:
- Check for `{AccountName}` under Accounts folder (`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck`)
- Check for `Implementation` under `{AccountName}`
- Create any missing folders with `mcp_google-worksp_create_drive_folder`

**Step 2: Upload the XLSX**

```bash
cd /Users/michaelkelly/.snowflake/cortex/.mcp-servers/google-workspace && \
./node /Users/michaelkelly/CoCo/Scripts/upload_to_gsheets.mjs \
  "/path/to/<Customer>_Implementation_Roadmap.xlsx" "<Customer> Implementation Roadmap" "IMPLEMENTATION_FOLDER_ID"
```

Returns JSON with the Google Sheets URL:
```json
{"id":"...","name":"...","url":"https://docs.google.com/spreadsheets/d/.../edit"}
```

**Step 3: Report the link**

Present the Google Sheets URL to the user so they can open it directly.

**Bullet formatting rule:** In all email drafts and Google Docs content, bullet lists must use 4-space indented format:
```
    • item one
    • item two
```
For Google Docs markdown passed to `mcp_google-worksp_create_document`, use `- item` (markdown list) which auto-converts to properly indented bullets.
