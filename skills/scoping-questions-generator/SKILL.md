---
name: scoping-questions-generator
description: "Generate fixed-bid scoping questions, pre-call document requests, and scope boundary definitions for Snowflake data platform engagements. Produces a comprehensive Excel workbook to drive scoping calls and SOW alignment. Use when: scoping call preparation, fixed-bid estimation, SOW scoping, pre-call questionnaire, scope boundaries, discovery questions, engagement scoping. Triggers: scoping questions, scoping call, fixed bid scoping, pre-call prep, scope boundaries, SOW scoping, discovery questionnaire, engagement scoping, scoping document."
---

# Scoping Questions Generator

Generate a comprehensive Scoping Questions Excel workbook for a Snowflake data platform engagement. Covers executive/strategic questions, environment, source systems, transformation, consumption/AI, people, governance, timeline, and commercial topics. Includes pre-call document requests and scope boundary definitions for SOW alignment.

## Prerequisites

- `openpyxl` Python library available
- Customer context: source systems, phases, known constraints
- Ideally, prior artifacts exist: Bronze Layer plan, Ingestion-to-Consumption map, Implementation Roadmap

## Workflow

### Step 1: Gather Context

**Ask** the user for:
1. **Customer name** and engagement type (Fixed Fee, T&M, Fast Track)
2. **Source system list** and phase assignments (or reference prior artifacts)
3. **Known unknowns** — specific areas where information is lacking
4. **Key risks** — areas that need deeper probing during scoping
5. **Engagement model** — roles expected (SA, ASE, SDM, Partner)

If prior artifacts exist (Bronze plan, Roadmap), read them to auto-generate source-specific questions.

**⚠️ STOP**: Confirm context and focus areas.

### Step 2: Generate Questions by Category

Organize questions into these categories:

**1. Executive & Strategic**
- Business drivers, success criteria, executive sponsor
- ROI expectations, competitive pressures, timeline drivers
- Decision-making process, budget authority

**2. Environment & Platform**
- Current Snowflake account (edition, region, features)
- Cloud provider (AWS/Azure/GCP), existing infrastructure
- Network topology, security requirements (HIPAA/PCI/SOX)
- CI/CD, DevOps, environment strategy (dev/staging/prod)

**3. Source Systems** (generate per source or source category)
- API access and credentials readiness
- Data volume, frequency, historical depth
- Schema documentation availability
- Known data quality issues
- Owner/DBA/admin contact
- Sunset timelines or migration plans

**4. Transformation & Data Modeling**
- Existing business logic documentation
- Current transformation tools (ETL/ELT)
- Data model maturity (star schema, 3NF, ad-hoc)
- Business rule complexity and SME availability

**5. Consumption & AI**
- Current BI tools and reporting landscape
- AI/ML aspirations and existing capabilities
- Self-service requirements
- Semantic layer / natural language query interest

**6. People & Resources**
- Customer team availability (hours/week)
- SME identification per domain
- Partner involvement
- Training and enablement needs

**7. Governance & Compliance**
- Data governance maturity
- Regulatory requirements (HIPAA, PCI, GDPR, SOX)
- Data classification and masking requirements
- Audit and lineage requirements

**8. Timeline & Dependencies**
- Hard deadlines (system sunsets, contract expirations, fiscal year)
- External dependencies (vendor timelines, regulatory deadlines)
- Parallel initiatives that may compete for resources

**9. Commercial & SOW**
- Engagement structure preferences
- Payment terms and milestone expectations
- Change control tolerance
- Success metrics for engagement evaluation

**Question attributes:**
| Column | Description |
|--------|------------|
| Category | Question category |
| Sub-Category | Specific topic within category |
| Question | The actual question to ask |
| Why It Matters for Fixed-Bid | Why this answer impacts scoping/pricing |
| Phase | Which phase(s) this question relates to |
| Priority | Critical, High, Medium |
| Response | Blank column for capturing answers |

**Priority guidelines:**
- **Critical**: Answer required before SOW — blocks estimation
- **High**: Answer needed early in engagement — significant effort impact
- **Medium**: Important but can be discovered during engagement

### Step 3: Generate Pre-Call Document Requests

List artifacts to request from the customer before the scoping call:

| # | Document | Description | Priority | Notes |
|---|----------|-------------|----------|-------|
| 1 | System architecture diagram | Current state data flow | Critical | |
| 2 | Source system inventory | List of all data sources | Critical | |
| 3 | API documentation | Per source system | High | |
| 4 | Data dictionaries | Schema definitions | High | |
| 5 | Sample reports / dashboards | Current BI outputs | Medium | |
| ... | (generate based on customer context) | | | |

### Step 4: Generate Scope Boundaries

Define In-Scope, Out-of-Scope, and Assumptions for SOW alignment:

| Category | In-Scope | Out-of-Scope | Assumptions |
|----------|----------|-------------|-------------|
| Platform | Snowflake architecture, RBAC, governance | Production operations, 24/7 support | Customer provides BC account |
| Ingestion | N sources via specified patterns | Custom connector development | API credentials provided |
| Transformation | Silver/Gold models via dbt/DT | Full data warehouse redesign | Business rules documented |
| AI/Cortex | Semantic Views, Cortex Agent | Custom ML model training | Gold models validated first |
| Testing | Integration testing, validation | Performance/load testing | Customer owns UAT sign-off |
| ... | (generate based on engagement scope) | | |

### Step 5: Generate the Excel Workbook

Create a Python script using `openpyxl` with these sheets:

**Sheet 1: Scoping Questions**
- All questions organized by category with sub-category grouping
- Category headers as merged row dividers
- Priority color-coding: Critical=red, High=orange, Medium=yellow
- Response column for capturing answers during/after call

**Sheet 2: Pre-Call Document Requests**
- Numbered list with description, priority, and status columns
- Organized by urgency

**Sheet 3: Scope Boundaries**
- Category rows with In-Scope, Out-of-Scope, Assumptions columns
- Clear delineation for SOW alignment

**Formatting:**
- Header row: dark blue fill (#11567F), white bold text
- Category dividers: colored section headers
- Priority cells: conditional formatting (red/orange/yellow)
- Wide columns for Question and Response (text wrapping)
- Freeze panes

**⚠️ STOP**: Present question count by category and priority distribution before generating.

### Step 6: Generate and Deliver

1. Write the Python generation script
2. Execute to produce the Excel file
3. Report: total questions, priority distribution, document requests count

**Output location**: `<customer_directory>/<Customer>_Scoping_Questions.xlsx`

## Stopping Points

- ✋ Step 1: Context confirmed
- ✋ Step 5: Question summary reviewed

## Output

Multi-sheet Excel workbook with:
- Categorized scoping questions with priority ratings
- Pre-call document request list
- Scope boundary definitions for SOW alignment

## Reference: Boxout Health Example

- 86 questions across 9 categories
- 23 pre-call document requests
- 11 scope boundary categories
- Priority distribution: Critical (most source access questions), High (business logic), Medium (consumption/AI)

## Google Drive Output

After generating the XLSX locally, upload it to Google Drive as a Google Sheet.

**Folder path:** SnowWork → Accounts → {AccountName} → Scoping

**Step 1: Ensure folder chain exists**

Use `mcp_google-worksp_search_drive` to check if each folder exists before creating:
- Check for `{AccountName}` under Accounts folder (`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck`)
- Check for `Scoping` under `{AccountName}`
- Create any missing folders with `mcp_google-worksp_create_drive_folder`

**Step 2: Upload the XLSX**

```bash
cd /Users/michaelkelly/.snowflake/cortex/.mcp-servers/google-workspace && \
./node /Users/michaelkelly/CoCo/Scripts/upload_to_gsheets.mjs \
  "/path/to/<Customer>_Scoping_Questions.xlsx" "<Customer> Scoping Questions" "SCOPING_FOLDER_ID"
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
