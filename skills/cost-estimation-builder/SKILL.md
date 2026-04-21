---
name: cost-estimation-builder
description: "Create professional Cost Estimation Excel workbooks for Snowflake PS engagements. Reads from an existing Implementation Roadmap workbook to generate multi-sheet pricing with Summary, Detailed Pricing, Milestone×Role, and Role×Milestone breakdowns. Use when: cost estimation, pricing sheet, engagement pricing, hours estimation, role-based pricing, fixed fee estimation, deal review pricing. Triggers: cost estimation, pricing sheet, estimate cost, pricing breakdown, hours and cost, engagement pricing, deal pricing, fixed fee pricing, cost sheet, PS pricing."
---

# Cost Estimation Builder

Generate a professional multi-sheet Cost Estimation Excel workbook for a Snowflake Professional Services engagement. Reads tasks from an existing Implementation Roadmap workbook (from `implementation-roadmap-builder`) and produces detailed pricing breakdowns by milestone, role, and work area.

## Prerequisites

- `openpyxl` Python library available
- An existing Implementation Roadmap Excel workbook (from `implementation-roadmap-builder` or similar)
  - Must have per-milestone sheets (e.g., "M1", "M2", "M3", "M4") with columns: #, Work Area, Task, Deliverable, Role, Hours, Risk, Timeline
- Role definitions with hourly rates

## Workflow

### Step 1: Gather Inputs

**Ask** the user for:
1. **Customer name**
2. **Path to the Implementation Roadmap Excel** — the roadmap file to read tasks from
3. **Role definitions and rates** — which roles and their hourly rates. Common defaults:

| Role | Default Rate | Description |
|------|-------------|-------------|
| Lead SA | $335/hr | Lead Solution Architect — architecture, design, AI/ML |
| Impl SA | $335/hr | Implementation Solution Architect — hands-on build |
| AI SA | $415/hr | AI Solution Architect — Cortex AI, ML, Semantic Views |
| ASE | $0 (complimentary) | Activation Solutions Engineer — security, SCIM, SSO |
| SDM | $265/hr | Services Delivery Manager — program management |
| Partner | $335/hr | Subcontracted partner — requirements, data modeling |

4. **Engagement duration** — total weeks, overlapping milestone structure
5. **Special pricing notes** — complimentary roles, capped hours, discounts

If the user provides specific rates, use those. Otherwise, use defaults above.

**⚠️ STOP**: Confirm role definitions and rates before proceeding.

### Step 2: Read Roadmap Data

Parse the Implementation Roadmap workbook:
1. Open the workbook with `openpyxl` (data_only=True)
2. For each milestone sheet (M1, M2, etc.):
   - Skip header rows and section divider rows (rows where # is None and task text is a section name)
   - Skip total rows (containing "TOTAL")
   - Extract: task number, work area/section, task description, deliverable, role, hours
   - Track the current section name for section-based grouping
3. Build a data structure:

```python
phases_data = [
    {
        "label": "M1: Foundation & Platform Setup",
        "color": "29B5E8",  # Snowflake cyan
        "weeks": 8,
        "timeline": "Weeks 1-8",
        "tasks": [
            {"num": 1, "task": "...", "section": "Discovery", "deliverable": "...", "hours": 24, "role": "Lead SA"},
            ...
        ]
    },
    ...
]
```

**Section name normalization**: Clean up long section names for the cost sheet:
- "Discovery & Architecture" → "Discovery"
- "Security & Governance" → "Security"
- "Bronze Ingestion — Eagle Pace Sources" → "Bronze Ingestion"
- "Silver Layer — Investments & Distributions" → "Silver Layer"
- "Powerbi Model Pushdown & Semantic Views" → "Semantic Views"
- "Cortex Analyst & Ai Deployment" → "AI / Cortex"
- "Program Management (MX)" → "Program Mgmt"

### Step 3: Calculate Totals

Compute:
- **role_totals**: total hours per role across all milestones
- **grand_total**: sum of (hours × rate) for all billable roles (exclude complimentary roles like ASE)
- **grand_hours**: total hours including complimentary
- **Per-milestone**: hours and cost per milestone
- **Per-work-area**: hours and cost per section/work area

### Step 4: Generate the Excel Workbook

Create a Python script using `openpyxl` with these sheets:

---

**Sheet 1: Summary** (tab color: Snowflake cyan #29B5E8)

5 sections on one sheet:

**Section 1 — TOTAL HOURS BY ROLE**
| Role | Hours | Rate ($/hr) | Total Cost | % of Hours | % of Cost |
For complimentary roles, show "$0" or "Complimentary" in cost column.

**Section 2 — COST BY MILESTONE**
| Milestone | Timeline | Weeks | Total Hours | Total Cost | % of Total | Focus Area |

**Section 3 — COST BY ROLE × MILESTONE**
| Role | M1 | M2 | M3 | M4 | Total |
(values in $ amounts)

**Section 4 — HOURS BY ROLE × MILESTONE**
| Role | M1 | M2 | M3 | M4 | Total |
(values in hours)

**Section 5 — COST BY WORK AREA × MILESTONE**
| Work Area | M1 | M2 | M3 | M4 | Total |
(values in $ amounts)

---

**Sheet 2: Detailed Pricing** (tab color: dark blue #11567F)

Per-milestone sections with every task priced:

For each milestone:
- Color-coded milestone header bar (full-width merge)
- Column headers: #, Work Area, Task/Deliverable, Deliverable, Role, Hours, Rate, Cost
- Every task from the roadmap with: rate looked up by role, cost = hours × rate
- Role labels color-coded (Lead SA=cyan, Impl SA=dark blue, SDM=pink, Partner=purple, ASE=gray)
- Milestone subtotal row
- For complimentary roles: show $0 in Rate and Cost columns

Grand total row at the bottom (dark fill, white text).

---

**Sheet 3: Milestone × Role** (tab color: purple #7D44CF)

For each milestone:
- Milestone color header bar
- Table: Role, Hours, Rate, Cost, % of Milestone, % of Total
- Milestone total row

---

**Sheet 4: Role × Milestone** (tab color: pink #D45B90)

For each role:
- Role color header bar (each role gets its own color)
- Table: Milestone, Hours, Rate, Cost, % of Role, % of Total
- Role total row

---

### Formatting Spec

**Colors** (Snowflake brand palette):
```python
CYAN = "29B5E8"       # Primary Snowflake blue
DARK_BLUE = "11567F"  # Secondary dark blue
PURPLE = "7D44CF"     # Accent purple
PINK = "D45B90"       # Accent pink
GREEN = "2EA77A"      # Success green
DARK = "1E293B"       # Headers/dark backgrounds
LIGHT_BG = "F5F8FA"   # Alternating row light
```

**Fonts:**
- Title: Arial 16pt bold, color DARK
- Subtitle: Arial 10pt, color "666666"
- Section headers: Arial 12pt bold, color DARK_BLUE
- Table headers: Arial 11pt bold, white on DARK fill
- Body: Arial 10pt, color "333333"
- Totals: Arial 11pt bold, white on milestone/cyan fill

**Number formats:**
- Money: `'"$"#,##0'`
- Percentage: `'0.0%'`

**Layout:**
- Alternating row fills (LIGHT_BG / WHITE)
- Thin borders (#DDDDDD) on all data cells
- Column widths: auto-sized per sheet (see reference below)
- Wrap text on task description columns
- Center alignment on numeric columns

### Step 5: Generate and Deliver

1. Write the Python generation script to the customer directory
2. Execute to produce the Excel file
3. Report summary:
   - Grand total: hours and cost
   - Role breakdown: hours, rate, cost per role
   - Milestone breakdown: hours, cost, % per milestone
   - Work area breakdown: top areas by cost

**Output files**:
- Script: `<customer_directory>/gen_cost_estimation.py`
- Excel: `<customer_directory>/<Customer>_Cost_Estimation.xlsx`

**⚠️ STOP**: Present grand total, role breakdown, and milestone breakdown before generating.

## Stopping Points

- ✋ Step 1: Roles and rates confirmed
- ✋ Step 5: Grand total and breakdown reviewed

## Output

Multi-sheet Excel workbook with:
- **Summary**: 5 pivot-table-style sections (Role totals, Milestone costs, Role×Milestone cost, Role×Milestone hours, WorkArea×Milestone cost)
- **Detailed Pricing**: Every task priced with role, rate, and cost; milestone subtotals; grand total
- **Milestone × Role**: Per-milestone role cost breakdown with percentages
- **Role × Milestone**: Per-role milestone cost breakdown with percentages

## Reference: Column Widths

**Summary sheet:**
| Column | Width | Content |
|--------|-------|---------|
| A | 32 | Role / Milestone / Work Area names |
| B-E | 16-18 | Numeric values (hours, $, %) |
| F | 16 | Percentages or totals |
| G | 44 | Focus area descriptions |

**Detailed Pricing sheet:**
| Column | Width | Content |
|--------|-------|---------|
| A | 5 | Task # |
| B | 18 | Work area |
| C | 65 | Task description |
| D | 30 | Deliverable name |
| E | 12 | Role label |
| F | 10 | Hours |
| G | 10 | Rate |
| H | 14 | Cost |

**Milestone × Role / Role × Milestone sheets:**
| Column | Width | Content |
|--------|-------|---------|
| A | 30-42 | Role/Milestone name |
| B | 12 | Hours |
| C | 14 | Rate |
| D | 16 | Cost |
| E-F | 14 | Percentages |

## Reference: Victory Capital Example

- **Grand Total**: $741,550 | 2,320 hours | 139 tasks | 32 weeks
- **Roles**: Lead SA (1,016 hrs, $340K), Impl SA (520 hrs, $174K), SDM (404 hrs, $107K), Partner (358 hrs, $120K), ASE (22 hrs, complimentary)
- **Milestones**: M1 Foundation ($132K), M2 Eagle PACE Bronze+Silver/Gold ($275K), M3 Redshift+Corp Services ($157K), M4 AI/Semantic/Victor ($178K)
- **4 sheets**: Summary, Detailed Pricing, Milestone×Role, Role×Milestone

## Reference: Populous Example

- **Grand Total**: $983,450 | 3,002 hours | 30 weeks
- **Roles**: SA ($335/hr, 2,116 hrs), AI SA ($415/hr, 336 hrs), SDM ($265/hr, 510 hrs), ASE (40 hrs complimentary)
- **Phases**: P1 CRM/ERP/HR ($652K), P2 BIM/Cost ($198K), P3 Process/CA Health ($134K)
- **4 sheets**: Summary, Detailed Pricing, Phase×Role, Role×Phase
- Read tasks from `Populous_Implementation_Roadmap.xlsx` (3 phase sheets)

## Google Drive Output

After generating the XLSX locally, upload it to Google Drive as a Google Sheet.

**Folder path:** SnowWork → Accounts → {AccountName} → Cost Estimation

**Step 1: Ensure folder chain exists**

Use `mcp_google-worksp_search_drive` to check if each folder exists before creating:
- Check for `{AccountName}` under Accounts folder (`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck`)
- Check for `Cost Estimation` under `{AccountName}`
- Create any missing folders with `mcp_google-worksp_create_drive_folder`

**Step 2: Upload the XLSX**

```bash
cd /Users/michaelkelly/.snowflake/cortex/.mcp-servers/google-workspace && \
./node /Users/michaelkelly/CoCo/Scripts/upload_to_gsheets.mjs \
  "/path/to/<Customer>_Cost_Estimation.xlsx" "<Customer> Cost Estimation" "COST_ESTIMATION_FOLDER_ID"
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
