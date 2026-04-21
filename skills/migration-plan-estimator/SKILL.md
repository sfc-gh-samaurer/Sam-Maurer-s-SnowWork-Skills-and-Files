---
name: migration-plan-estimator
description: "Generate migration plan and estimation Excel workbooks for Snowflake migration engagements. Creates 6-tab workbooks with: task lists, cost summaries, scoping questions, risk registers, RACI matrices, and assumptions. Use when: migration estimation, migration plan, scoping estimation, migration hours, migration cost, create estimation workbook, migration pricing, indicative estimate, fixed fee estimate, migration tasks and hours."
---

# Migration Plan & Estimator

Generate a professional 6-tab Excel workbook for Snowflake migration engagements using openpyxl with Snowflake branding.

## Prerequisites

- Account/customer memory file exists (check `/memories/` for account briefing)
- Source platform and scope are known (database count, data volume, source technology)
- Role rates are defined (or use SD defaults)

## Workflow

### Step 1: Gather Parameters

**Ask user for or extract from context:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CUSTOMER_NAME` | Customer/account name | Required |
| `SOURCE_PLATFORM` | Source database (SQL Server, Oracle, Teradata, etc.) | Required |
| `TARGET_PLATFORM` | Snowflake cloud (Azure, AWS, GCP) | Azure |
| `DB_COUNT` | Number of databases in scope | Required |
| `DATA_VOLUME` | Total data size (e.g., "3.3 TB") | Required |
| `CONVERSION_TOOL` | SnowConvert AI, DMVA, Manual | SnowConvert AI |
| `MA_RATE` | Migration Architect hourly rate | $335 |
| `MDC_RATE` | Migration Delivery Consultant hourly rate | $180 |
| `SDM_RATE` | Services Delivery Manager hourly rate | $260 |
| `AE_FREE_HOURS` | Free Activation Engineer hours | 40 |
| `OUTPUT_DIR` | Output directory path | Required |

**Check memory** for account details:
```
memory view /memories/<account>_account_briefing.md
```

**STOP**: Confirm parameters with user before generating.

### Step 2: Scale Task Hours

Use this baseline scaling model. Adjust hours based on scope:

**Scaling factors by DB count:**
- < 20 DBs: 0.5x baseline
- 20-50 DBs: 0.75x baseline
- 50-100 DBs: 1.0x baseline (reference: 86 DBs)
- 100-200 DBs: 1.3x baseline
- 200+ DBs: 1.6x baseline

**Baseline hours (at 1.0x for ~86 DBs, ~3.3 TB):**

| Phase | MA | MDC | SDM | Customer |
|-------|-----|-----|-----|----------|
| 1. Platform Setup & Foundation | 80 | 0 | 0 | 22 |
| 2. Migration Planning | 112 | 20 | 16 | 60 |
| 3. Data Migration | 24 | 112 | 0 | 52 |
| 4. Code Conversion | 80 | 192 | 0 | 88 |
| 5. UAT & Validation | 28 | 40 | 4 | 108 |
| 6. Deployment & Cutover | 32 | 36 | 16 | 88 |
| 7. Project Management | 0 | 0 | 64 | 0 |
| **TOTAL** | **356** | **400** | **100** | **418** |

Adjust Phase 4 (Code Conversion) most aggressively - it's the most variable.

### Step 3: Generate Python Script

Write a Python script using openpyxl that generates a 6-tab workbook. Use this exact structure:

**Tab 1: "Migration Tasks"** - Detailed task list
- Title row: `"{CUSTOMER_NAME} - {SOURCE_PLATFORM} to Snowflake Migration | Indicative Task Estimation"`
- Subtitle: `"Source: {SOURCE_PLATFORM} ({DB_COUNT} databases, ~{DATA_VOLUME}) | Target: Snowflake on {TARGET_PLATFORM} | Tool: {CONVERSION_TOOL}"`
- Headers: #, Phase, Task, Migration Architect (${MA_RATE}/hr), Migration Delivery Consultant (${MDC_RATE}/hr), SDM (${SDM_RATE}/hr), Customer ({CUSTOMER_NAME}), Notes
- 7 phase categories (bold category rows) with tasks underneath
- SUM formulas in total row for each role column
- Freeze panes at row 5

**Tab 2: "Cost Summary"** - Aggregate costs
- Section 1: Role Rate Card with cross-sheet references to Tasks tab totals
  - Activation Engineer row: "{AE_FREE_HOURS} hrs FREE" in green italic
  - MA/MDC/SDM rows: hours from `='Migration Tasks'!{col}{total_row}`, cost = `=B{r}*C{r}`
  - Total row with SUM formulas
- Section 2: Cost Breakdown by Phase with per-phase hours and formula `=(B{r}*{MA_RATE})+(C{r}*{MDC_RATE})+(D{r}*{SDM_RATE})`
- Red italic note: "Code Conversion phase is the most variable component"
- Gray italic disclaimer: "Indicative estimate. Final pricing subject to assessment results."

**Tab 3: "Scoping Questions"** - Key questions by category
- Headers: #, Category, Question, Why It Matters
- Categories: Database Inventory, ETL & Orchestration, Data & Integration, Data Science, Performance & SLAs, Security & Compliance, Testing & Deployment, Timeline, Staffing
- 20-25 questions tailored to source platform

**Tab 4: "Key Risks"** - Risk register
- Headers: #, Risk, Category, Likelihood, Impact, Mitigation
- Color-coded: High=red bold, Medium=orange bold, Low=green
- 10-15 risks covering: Code Conversion, Data Migration, Staffing, Performance, Integration, Scope, Commercial, Timeline, Security, Communication

**Tab 5: "RACI"** - Responsibility matrix
- Headers: Activity, Migration Architect, Migration Delivery Consultant, SDM, Activation Engineer, {CUSTOMER_NAME} (Customer), Snowflake Leadership (AE/RSD)
- Legend: R = Responsible | A = Accountable | C = Consulted | I = Informed
- Category section rows (bold, blue fill) for each phase
- R/A cells: bold dark blue; R cells: bold black; A cells: bold red

**Tab 6: "Assumptions"** - Key assumptions
- Headers: #, Category, Assumption
- Categories: Scope, Platform, Code Conversion, Data Migration, UAT, Deployment, Staffing, Timeline, Commercial
- 25-30 assumptions covering all engagement aspects

**Formatting constants:**
```python
SF_DARK = "11567F"
SF_BLUE = "29B5E8"
WHITE = "FFFFFF"
LIGHT_GRAY = "F2F2F2"
LIGHT_BLUE = "E8F7FC"
```

### Step 4: Execute and Deliver

1. Write the Python script to `{OUTPUT_DIR}/{CUSTOMER_NAME}_Migration_Estimation.py`
2. Run: `python3 {OUTPUT_DIR}/{CUSTOMER_NAME}_Migration_Estimation.py`
3. Verify output: `ls -la {OUTPUT_DIR}/{CUSTOMER_NAME}_Migration_Estimation.xlsx`
4. Update account memory with estimation summary

**STOP**: Present summary to user:
```
Migration Estimation: {CUSTOMER_NAME}
- MA: {ma_hrs} hrs @ ${MA_RATE} = ${ma_cost}
- MDC: {mdc_hrs} hrs @ ${MDC_RATE} = ${mdc_cost}
- SDM: {sdm_hrs} hrs @ ${SDM_RATE} = ${sdm_cost}
- Total Billable: ${total} ({total_hrs} Snowflake hrs)
- Customer: {cust_hrs} hrs (not billed)
- File: {output_path}
```

## Stopping Points

- After Step 1: Confirm parameters
- After Step 4: Present estimation summary

## Output

6-tab Excel workbook at `{OUTPUT_DIR}/{CUSTOMER_NAME}_Migration_Estimation.xlsx` with:
- All formulas linked (Tasks tab drives Cost Summary)
- Snowflake branding (dark blue headers, light blue subheaders)
- Freeze panes on all tabs
- Print-ready column widths

## Notes

- Phase 4 (Code Conversion) is always the most variable - flag this prominently
- Always note that SnowConvert assessment results will refine the estimate
- Customer hours are shown but not billed - make this clear
- Activation Engineer hours are free - highlight in green
- For non-SQL-Server sources, adjust platform-specific tasks (e.g., no SQL Agent Jobs for Oracle, add BTEQ conversion for Teradata)

## Google Drive Output

After generating the XLSX locally, upload it to Google Drive under:
**SnowWork → Accounts → {AccountName} → Migration**

### Folder Setup

1. Check if `{AccountName}` folder exists under Accounts (`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck`):
   ```
   mcp_google-worksp_search_drive: "{AccountName}"
   ```
2. If not found, create it:
   ```
   mcp_google-worksp_create_drive_folder: name="{AccountName}", parent_id="1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck"
   ```
3. Check if `Migration` subfolder exists under `{AccountName}` folder; create if missing:
   ```
   mcp_google-worksp_create_drive_folder: name="Migration", parent_id="{AccountName_folder_id}"
   ```

### Upload

```bash
cd /Users/michaelkelly/.snowflake/cortex/.mcp-servers/google-workspace && \
./node /Users/michaelkelly/CoCo/Scripts/upload_to_gsheets.mjs \
  "{OUTPUT_DIR}/{CUSTOMER_NAME}_Migration_Estimation.xlsx" \
  "{CUSTOMER_NAME} Migration Estimation" \
  "{Migration_folder_id}"
```

Returns JSON: `{"id":"...","name":"...","url":"https://docs.google.com/spreadsheets/d/.../edit"}`

Present the Google Sheets URL to the user after upload.

### Bullet Formatting Rule

In all email drafts (`mcp_google-worksp_create_draft` body) and Google Docs content, bullet lists MUST use indented format with 4 spaces before the bullet:

```
    • item one
    • item two
```

For Google Docs markdown passed to `mcp_google-worksp_create_document`, use `- item` (markdown list) which auto-converts to properly indented bullets.
