---
name: deal-package
description: "Generate a complete deal review package: one-page HTML proposal (always), TDR deck (PPTX, optional), and optional Deal Pricing Sheet (Google Sheet). Optionally generates SOW and Capacity to PS&T. Use for ALL requests that mention: deal package, deal review, proposal package, TDR, deal materials, generate proposal deck, create deal review, deal pricing sheet, DPS. DO NOT attempt deal package generation manually - always invoke this skill first."
---

# Deal Package Generator

Generate a complete, deal-review-passing package of materials from a single structured interview. Produces multiple coordinated artifacts from one system-of-record JSON.

## Output Artifacts

| # | Artifact | Format | Selection | Method |
|---|----------|--------|-----------|--------|
| 1 | **One-Page Proposal** | HTML | [x] Always | Brand system HTML/CSS, timeline embedded inline — generated first |
| 2 | **TDR Deck** | PPTX | [ ] Optional | HTML-first design → editable PPTX via `snowflake-pptx-collateral-v4` approach |
| 3 | **SOW** | .docx | [ ] Optional | Delegates to `sow-generator` skill |
| 4 | **Capacity to PS&T** | Google Sheet | [ ] Optional | Delegates to `capacity-to-pst` skill (capacity conversion deals only) |
| 5 | **Deal Pricing Sheet** | Google Sheet | [ ] Optional | Copy DPS template + populate from master JSON via Google Workspace MCP |

**Timeline is NEVER a standalone artifact.** It is always embedded:
- In the TDR deck as the Gantt slide (slide 11)
- In the HTML proposal as an inline CSS grid Gantt

## Output Directory

ALL artifacts are written to:
```
~/Downloads/{CUSTOMER}-{DEAL_NAME}/
```
Where `{CUSTOMER}` and `{DEAL_NAME}` are derived from user input (spaces replaced with hyphens, title case).

Example: `~/Downloads/Sharp-Healthcare-Ontology-Engagement/`

## Prerequisites

- `uv` installed (for running python-pptx scripts)
- `python-pptx` installed: `pip install python-pptx`
- For TDR deck image mode only: `playwright` + `playwright install chromium`
- Snowflake PPTX template at `~/.snowflake/cortex/github-skills/skills/snowflake-pptx-collateral-v4/` (required for TDR deck generation)

## TDR Deck Slide Structure (21 slides)

The TDR deck follows the MASTER template structure. Each slide is tagged with its audience.

| # | Slide | Audience | Layout |
|---|-------|----------|--------|
| 1 | Title / Cover | PRESENT | Data Cloud_1_1_1 |
| 2 | Agenda | PRESENT | Agenda |
| 3 | Executive Summary | PRESENT | One Column Layout |
| 4 | Our Understanding | PRESENT | One Column Layout |
| 5 | Methodology & Engagement Approach | PRESENT | One Column Layout |
| 6 | Outcomes | PRESENT | One Column Layout |
| 7 | Scope Summary | PRESENT | One Column Layout_1_1 |
| 8 | Scope by Role | **SKIP** | One Column Layout |
| 9 | Technical Review Outcome | **SKIP** | One Column Layout |
| 10 | Dependencies | PRESENT | One Column Layout_1_1 |
| 11 | Timeline with Key Milestones | PRESENT | One Column Layout |
| 12 | Milestones & Validation | PRESENT | Multi-use layout_1_1 |
| 13 | Detailed RACI | PRESENT | One Column Layout |
| 14 | Governance Cadence | PRESENT | Multi-use layout_1 |
| 15 | Team Structure | PRESENT | Multi-use layout_1 |
| 16 | Commercials / Pricing | **SKIP** | One Column Layout |
| 17 | Staffing Plan | **SKIP** | One Column Layout |
| 18 | Risks & Mitigations | PRESENT | One Column Layout |
| 19 | Assumptions & Commitments | PRESENT | One Column Layout |
| 20 | Next Steps / Close Plan | PRESENT | One Column Layout |
| 21 | Thank You | PRESENT | Thank You_1 |

Slides marked **SKIP** get "(Skip for presentation)" as subtitle — they contain critical review content but are not shown to customers in live meetings.

### Conditional Slides (appended after slide 21 when applicable)

| Condition | Slides to Add |
|-----------|--------------|
| **Migration deal** | Source inventory, migration approach, testing plan, MRA/pilot findings |
| **Partner involved** | Partner scope/responsibilities, contracting model |
| **Investment > $500k** | Stage Gates (discovery, conversion, burndown) |
| **Fixed Fee** | Enhanced milestones with explicit acceptance criteria per milestone |

## Workflow

### Phase 0: Auto-Populate Known Facts

Before asking the user for information, attempt to pre-populate known facts from available sources. Try each source in order; skip unavailable ones:

**Source 1 — Chief Memory KG** (if MCP available):
```
memory_context({ entity: "<customer_name>" })
memory_query({ query: "<customer> AE SE sales engineer" })
memory_query({ query: "<customer> contacts stakeholders TPM" })
memory_query({ query: "<customer> Deal Pricing Sheet" })
```

Extract and pre-fill:
- AE name, SE name (from entity relationships)
- Customer contacts (TPM, technical leads)
- Deal context (engagement type, pricing, SFDC opp ID)
- Deal Pricing Sheet location (Google Sheet ID if exists)
- Prior decisions (scope, strategy, risk items from prior sessions)

**Source 2 — Snowhouse Query** (if KG unavailable or incomplete):
```sql
SELECT OPPORTUNITY_NAME, ACCOUNT_NAME, AE_NAME, SE_NAME, STAGE, AMOUNT
FROM <relevant_SFDC_view>
WHERE ACCOUNT_NAME ILIKE '%<customer>%'
ORDER BY CLOSE_DATE DESC LIMIT 5;
```

**Source 3 — User Interview** (for any remaining gaps):
Only ask the user for facts not found in Sources 1-2. Present what was auto-populated and ask for confirmation/corrections.

**Output**: A fact sheet with known values and `[TBD — need from user]` markers for unknowns.

### Phase 1: Context Collection (Interview)

Collect ALL information needed across ALL artifacts in a single structured interview. Use `ask_user_question` for each group. Accept file paths, pasted text, or Memory Palace entity references as input sources.

**Group A — Identity & Framing**
1. Customer name
2. Engagement title (short descriptive name)
3. Date (default: current month/year)
4. AE name, SE name (for next steps / close plan)
5. Engagement type: T&M or Fixed Fee
6. Funding model: Customer-funded / Capacity conversion / Snowflake investment
7. SI partner involvement? If yes, partner name

**Group B — Problem, Solution & Outcomes**
1. Problem statement / pain points (3-5 specific pain points with evidence)
2. Current state description (what exists today, what's broken)
3. Engagement objectives (what success looks like)
4. Proposed solution / deliverables (what Snowflake PS will build/deliver)
5. Snowflake features and products involved (Cortex, Semantic Views, Dynamic Tables, etc.)
6. **Strategic / business outcomes** — ROI, cost savings, time reduction, business value (for Outcomes slide)
7. **Technical outcomes** — capabilities delivered, architecture improvements (for Outcomes slide)

**Group C — Methodology, Timeline & Milestones**
1. Phases with names, durations, and activities per phase
2. Total duration in weeks
3. Target go-live date
4. Which activities are Snowflake-owned vs Customer-owned vs SI-owned
5. **Milestones with acceptance criteria** — for each milestone: name, deliverables, acceptance criteria, duration (for Milestones slide)

**Group D — Team, Pricing & Staffing**
1. Roles on the engagement (SA, SC, SDM, etc.)
2. Hours per role (total or hours/week x weeks)
3. Rates per role (defaults from FY27 Standard Price Book below if not provided)
4. Snowflake investment amount (if any discount/investment)
5. Customer total after investment
6. **SA activities** — specific deliverables the SA owns (for Scope by Role slide)
7. **SDM activities** — specific responsibilities the SDM owns (for Scope by Role slide)
8. **Team structure** — named resources where known, reporting lines (for Team Structure slide)

**FY27 Standard Price Book Defaults:**
| SKU | Role | Rate |
|-----|------|------|
| SVC-TMSSA | Senior Solution Architect | $400/hr |
| SVC-TMSA | Solution Architect | $335/hr |
| SVC-TMSC | Solutions Consultant | $325/hr |
| SVC-TMSDM | Service Delivery Manager | $260/hr |

Validate rates against FY27 pricebook. If custom rates are used, note the variance.

**Group E — Governance & RACI**
1. Governance forums (e.g., Weekly standup, Biweekly steering, Monthly exec review)
2. Cadence, participants, responsibilities, materials for each forum
3. RACI activities — 3-column format: Activity / Snowflake role / Customer role
   - Default: Customer = A (Accountable) for ~99% of rows
   - Snowflake = R (Responsible) or C (Consulted) for most rows
   - Add Partner column only if SI partner is involved
   - Snowflake is NEVER Accountable for customer-owned decisions

**Group F — Risk & Boundaries**
1. Assumptions (commitments, access requirements, role expectations, clarifications)
2. Dependencies (items that must be complete before kickoff)
3. Risks for ALL 7 categories (each needs: risk description, impact level, mitigation):
   - Organizational, Governance, Technical, Resource, Scope, Timeline, Adoption
4. Out-of-scope items (explicit exclusions)

**Group G — Close Plan**
1. Next steps / actions with owners and details (5-6 items)

### Phase 1.5: Deal Pricing Sheet

Check whether a Deal Pricing Sheet (DPS) already exists for this deal:

1. **Ask the user**: "Has a Deal Pricing Sheet been completed for this deal? If so, provide the Google Sheet name or link."
2. **Check memory**: `memory_query({ query: "<customer> Deal Pricing Sheet" })` — look for a stored Sheet ID.
3. **If DPS exists**: Read it to extract hours, rates, totals, and staffing plan. Pre-populate Commercials (slide 16) and Staffing (slide 17) from this data. Store the DPS link in `pricing.pricing_sheet_link`. Set `dps.generate = false`.
4. **If DPS does not exist**: Set `dps.generate = true` and collect the following DPS-specific fields (use `ask_user_question`):
   - **SFDC Opportunity URL** (mandatory) — `dps.sfdc_opportunity_url`
   - **Deal structure** — "Direct" or partner paper → `dps.deal_structure`
   - **Partner name** (if partner paper) → `dps.partner_name`
   - **Is this an investment deal?** (Yes/No) → `dps.is_investment`. If yes, ask for investment discount % → `dps.investment_discount_pct` (e.g., "100.000%" for full investment)
   - **Billing frequency** — "Upfront" or "Monthly" → `dps.billing_frequency`
   - **Expected start date** → `dps.expected_start_date`
   - **Currency** (default "USD") → `dps.currency`
   - **VPA discount %** (default "0%") → `dps.vpa_discount_pct`
   - Auto-derive: `dps.economic_review_answers` from deal context (investment_planned = "Yes" if `dps.is_investment`, partner_is_prime from `dps.deal_structure`, etc.)
5. **If no hours/rates available yet**: Run a lightweight estimation — ask for duration (weeks) and intensity. Default: SA at 20 hrs/wk, SDM at 20% of SA hours. Validate rates against FY27 pricebook.
6. **Ensure SKU assignment**: Each role in `pricing.roles[]` must have a `sku` field. Map from role title using the SKU Reference Table (see below).
7. **DPS Template**: `1jXFPXMTQFc_qMV48E42iRs7mUiP9vqgaagQntGJ6KdU` (FY27 v0.10).

**Input Sources:** The user may provide any of:
- Pasted meeting notes or description text
- File paths to documents (SOW, proposal drafts, meeting recordings)
- Memory Palace entity references
- Semantic extraction reports (for data-heavy engagements)
- Previous proposal artifacts to reference

If the user provides a rich source document, extract as much as possible from it and only ask for gaps.

### Phase 2: Deal Review Validation Gate

Before generating any artifacts, validate completeness against the TDR checklist. ALL items must be present:

- [ ] Executive summary (problem + solution + outcomes in 2-3 sentences)
- [ ] Current state + engagement objectives documented
- [ ] Methodology with named phases, durations, and activities
- [ ] Outcomes — strategic/business AND technical (for Outcomes slide)
- [ ] Scope boundaries defined (assessment, architecture, implementation, out-of-scope)
- [ ] Scope by role — SA and SDM activities with hours
- [ ] Program schedule / timeline with phases mapped to weeks
- [ ] Milestones with SMART acceptance criteria
- [ ] Dependencies listed (pre-kickoff requirements)
- [ ] RACI populated (3-column: Activity / Snowflake / Customer, at least 8-10 rows)
- [ ] Governance cadence defined (at least 2-3 forums)
- [ ] Team structure with named roles
- [ ] Pricing with roles, hours, rates, subtotal, investment, customer total
- [ ] Assumptions documented (commitments, access, roles, clarifications)
- [ ] ALL 7 risk categories covered (org, gov, tech, resource, scope, timeline, adoption)
- [ ] Next steps / close plan with owners

**If any items are missing:** Tell the user exactly which items are missing, suggest reasonable defaults where possible, and loop back to Phase 1 for the specific groups needed.

**If all items present:** Proceed to Phase 3.

### Phase 3: Generate Master JSON

Build the master `deal-package.json` containing ALL fields needed for ALL artifacts. This is the system of record.

The JSON structure is defined in `<SKILL_DIR>/schemas/deal-package-schema.json`. It contains:
- `meta` — customer, engagement title, date, AE/SE, engagement type, funding model
- `tdr` — executive summary, understanding, methodology, scope, dependencies, governance, assumptions, risks, next steps
- `cover` — customer name for Cover slide
- `gantt` — phases with week ranges for Timeline slide and HTML Gantt
- `outcomes` — strategic and technical outcomes for Outcomes slide
- `scope_by_role` — SA/SDM activities for Scope by Role slide
- `milestones` — milestone table for Milestones slide
- `raci` — 3-column RACI activities for RACI slide
- `team_structure` — named roles for Team Structure slide
- `staffing_plan` — role-by-week hours for Staffing Plan slide
- `pricing` — roles/hours/rates for Commercials slide and HTML proposal
- `html_proposal` — metrics, pain points, deliverables, team cards, why PS, etc.
- `timeline_embed` — display options for embedded timeline (time unit, target go-live)

**CRITICAL: Follow the formatting rules:**
- ALL array items that describe issues/challenges/objectives use: `"**Title**: description"`
- Text paragraphs: MAX 350 characters
- Array items: MAX 125 characters each
- Arrays: MAX 4-5 bullet points
- Phase activities: MAX 3 items per phase, each MAX 90 chars

### Phase 4: User Review & Approval

Present the master JSON as readable markdown, organized by slide/artifact:

```markdown
## Cover (Slide 1)
**Customer:** [name]
**Title:** [engagement title]
**Author:** [SE name] | [date]

## Executive Summary (Slide 3)
**Summary:** [exec_summary text]
**Challenges:** [bullet items]
**Solution:** [bullet items]
**Outcomes:** [bullet items]

## Outcomes (Slide 6)
**Strategic:** [items]
**Technical:** [items]

## Milestones (Slide 12)
| Milestone | Deliverables | Acceptance Criteria | Duration |
|...|...|...|...|

## RACI (Slide 13)
| Activity | Snowflake | Customer |
|...|...|...|

## Pricing (Slide 16)
| Role | Hours | Rate | Total |
|...|...|...|...|
**Subtotal:** $X | **Investment:** ($Y) | **Customer Total:** $Z
```

**MANDATORY STOPPING POINT.** Wait for user approval or change requests. Iterate until approved.

### Phase 5: Generate One-Page HTML Proposal (Always)

Generate the HTML proposal immediately after JSON approval — no artifact selection gate needed.

Generate using the brand system HTML/CSS. Load the HTML template from `<SKILL_DIR>/templates/html-one-page.html` and populate with data from the master JSON. The template sections:

1. **Header** — Blue gradient, engagement title, customer name, date, DRAFT tag
2. **Metrics** — 3 metric cards (duration, total cost, key stat)
3. **Summary paragraph** — engagement overview
4. **The Problem** — 2x2 grid of pain cards with icons
5. **What You Get** — 3-column deliverable cards with bullet lists
6. **Timeline** — CSS grid Gantt chart (embedded inline, NOT standalone)
7. **T&M/FF Qualifier** — engagement type terms callout
8. **Why Snowflake PS** — 3-column value cards
9. **Delivery Team** — role cards with hours@rate
10. **Assumptions & Dependencies** — bullet lists
11. **Out of Scope** — bullet list
12. **Next Steps** — action table
13. **Footer** — Copyright + Confidential

Write to: `~/Downloads/{CUSTOMER}-{DEAL_NAME}/{CUSTOMER}-Proposal.html`

**⚠️ STOPPING POINT after HTML delivery.** Present the file path, then ask:

> The one-page HTML proposal is ready. Would you like to continue and generate additional artifacts?

Use `ask_user_question` with multi-select options:
- [ ] **TDR Deck (PPTX)** — full 21-slide deal review deck
- [ ] **SOW (.docx)** — delegates to `sow-generator` skill
- [ ] **Capacity to PS&T (Google Sheet)** — delegates to `capacity-to-pst` skill
- [ ] **Deal Pricing Sheet (Google Sheet)** — auto-generated if `dps.generate = true`
- [ ] **None — proposal only**

If user selects none / proposal only, proceed to Phase 7 (Deliver). Otherwise proceed to Phase 6.

### Phase 6: Generate Optional Artifacts

Generate only the artifacts the user selected in Phase 5.

#### 6A: TDR Deck (PPTX) — HTML-First Design → Editable PPTX

The TDR deck uses the `snowflake-pptx-collateral-v4` HTML-first workflow for professional visual quality.

**Step 1: Load design system references**

Load these references from the `snowflake-pptx-collateral-v4` skill before writing any HTML:
- `~/.snowflake/cortex/github-skills/skills/snowflake-pptx-collateral-v4/references/html-slide-design.md` — CSS design tokens, brand rules, 12 HTML slide templates
- `~/.snowflake/cortex/github-skills/skills/snowflake-pptx-collateral-v4/references/html-to-editable-pptx.md` — python-pptx builder patterns
- `~/.snowflake/cortex/github-skills/skills/snowflake-pptx-collateral-v4/references/core-helpers.md` — `add_shape_text()`, brand constants, saving

**Step 2: Create slides directory**
```bash
mkdir -p ~/Downloads/{CUSTOMER}-{DEAL_NAME}/slides/
```

**Step 3: Write one HTML file per slide**

Create `slides/slide_01_cover.html` through `slides/slide_21_thankyou.html` using the design system templates. Every slide must be exactly **960×540px** with `overflow: hidden`.

Design rules (enforced — same as `snowflake-pptx-collateral-v4`):
- Titles in **ALL CAPS**, 18px bold, `var(--sf-dark-text)` on light backgrounds, white on dark
- Use CSS variables from the design token block — never invent colors
- Left edge bar: 4px `var(--sf-blue)` on every content slide
- Footer: `"Confidential — Snowflake Professional Services"` at `top:511px`
- Content must not extend below `top:490px`
- At least 50% of content slides use a visual pattern (card grid, table, timeline, two-column) — not just bullets
- Cover, Thank You use dark/blue gradient backgrounds with white text
- SKIP slides: add `"(SKIP FOR PRESENTATION)"` as a red badge in the top-right corner

**TDR Slide → Visual Pattern mapping:**

| Slide | Title | Visual Pattern |
|-------|-------|----------------|
| 1 | Cover | Dark gradient cover slide |
| 2 | Agenda | Two-column list |
| 3 | Executive Summary | Three-column card grid (Challenges / Solution / Outcomes) |
| 4 | Our Understanding | Two-column (Current State / Engagement Objectives) |
| 5 | Methodology & Engagement Approach | Phase table with columns: Phase / Workstreams / Duration / Activities |
| 6 | Outcomes | Two-column card grid (Strategic/Business / Technical) |
| 7 | Scope Summary | Three-column cards + out-of-scope section below |
| 8 | Scope by Role *(SKIP)* | Two-column table: SA activities / SDM activities with hours |
| 9 | Technical Review Outcome *(SKIP)* | Placeholder sections for reviewer |
| 10 | Dependencies | Bulleted card list |
| 11 | Timeline with Key Milestones | Gantt chart — CSS grid with phase bars and week labels |
| 12 | Milestones & Validation | Table: Milestone / Deliverables / Acceptance Criteria / Duration |
| 13 | Detailed RACI | RACI table with R/A/C/I badges (3-col: Activity / Snowflake / Customer) |
| 14 | Governance Cadence | Table: Forum / Cadence / Participants / Responsibilities |
| 15 | Team Structure | Team cards (Snowflake roles with names, hours) |
| 16 | Commercials / Pricing *(SKIP)* | Pricing table + total callout box + DPS link |
| 17 | Staffing Plan *(SKIP)* | Role-by-week allocation grid |
| 18 | Risks & Mitigations | Table: Category / Risk / Impact / Mitigation (7 categories) |
| 19 | Assumptions & Commitments | Two-section bullet list (Assumptions / Dependencies) |
| 20 | Next Steps / Close Plan | Action table: Step / Owner / Details |
| 21 | Thank You | Dark gradient closing slide with contact info |

**Step 4: Convert HTML → Editable PPTX**

After all HTML slides are written, use the patterns from `html-to-editable-pptx.md` and `core-helpers.md` to write a Python script that builds the deck as native python-pptx shapes, text boxes, and tables.

```bash
python ~/Downloads/{CUSTOMER}-{DEAL_NAME}/build_tdr.py
```

Output: `~/Downloads/{CUSTOMER}-{DEAL_NAME}/{CUSTOMER}-TDR.pptx`

**What is preserved exactly:** All text, tables, layout geometry, brand colors, edge bars, footers.
**What is approximated:** CSS gradients → solid fill; border-radius → square corners; box-shadows → omitted.

#### 6C: SOW (Optional)

If selected, transform the master JSON into the sow-generator schema format and delegate to the `sow-generator` skill.

#### 6D: Capacity to PS&T (Optional)

Delegate to the `capacity-to-pst` skill.

#### 6E: Deal Pricing Sheet (Optional)

If selected (i.e., `dps.generate = true` — user has no pre-existing DPS), generate a populated Google Sheet from the DPS template using Google Workspace MCP tools.

**CRITICAL RULES:**
- **GREEN-shaded cells only** — NEVER write to non-green/non-yellow cells. That breaks formulas.
- **Use `copy_file`** to copy the template (preserves all 17 tabs, formulas, conditional formatting, data validation). Do NOT use `create_spreadsheet`.
- **Tab completion order**: Deal Summary first → Resource/Staffing Plan → Economic Review Summary last (it auto-populates financial sections from Deal Summary).
- Items 1-6 in the fee table (rows 14-19) auto-populate from child tabs 2-7. For pure T&M deals, leave them alone (they show blank/zero, which is fine). T&M SKU lines go in items 7+ (rows 20+).
- Child tabs 2-7 (Code Conversion, Snowpark, Data Migration, Partner FF x2, Other FF) only need population if the engagement includes those workstream types. For standard T&M advisory deals, skip them entirely.

**Step 1: Copy Template**

```
copy_file(
  file_id: '1jXFPXMTQFc_qMV48E42iRs7mUiP9vqgaagQntGJ6KdU',
  new_name: 'Deal Pricing Sheet - {meta.customer} - {meta.engagement_title} - {meta.date}'
)
```

Store the returned file ID in `pricing.pricing_sheet_id`.

**Step 2: Populate Deal Summary Tab** (`'1. Deal Summary'`)

Use `batch_values_update` to write all green cells in one call:

| Cell | Value | Source |
|------|-------|--------|
| `A2` | `"{meta.customer} - {meta.engagement_title}"` | `meta` |
| `D5` | SFDC opportunity URL | `dps.sfdc_opportunity_url` |
| `D6` | Currency | `dps.currency` (default "USD") |
| `D7` | Pricebook | `dps.pricebook` (default "Snowflake Pricing") |
| `D8` | Deal structure | `dps.deal_structure` (default "Direct") |
| `D9` | Partner name | `dps.partner_name` (blank if Direct) |
| `D10` | VPA discount % | `dps.vpa_discount_pct` (default "0%") |
| `D11` | Investment flag | "Yes" if `dps.is_investment`, else "No" |

**Fee Table** — For T&M deals, populate items 7+ (starting at row 20). For each role in `pricing.roles[]`, write one fee table row:

| Column | Field | Source |
|--------|-------|--------|
| B | Workstream description | `meta.engagement_title` |
| C | Product name | Lookup from SKU Reference Table below |
| D | Product code (SKU) | `pricing.roles[].sku` |
| E | Description | Role description or engagement title |
| F | Billing frequency | `dps.billing_frequency` |
| G | Year | "Year 1" |
| H | Service type | "T&M" or "Fixed Fee" based on `meta.engagement_type` |
| I | Sub | "N" |
| K | Qty (hours) | `pricing.roles[].hours` |
| L | List unit price (rate) | `pricing.roles[].rate` |
| N | Investment discount % | `dps.investment_discount_pct` if `dps.is_investment`, else "0%" |

For **Fixed Fee** deals (SVC-CUSTOMFF / SVC-CUSTFF-PC): Use tab 7 ("Other Fixed Fee") for the fixed-fee workstream details if applicable. The fee table item row auto-populates from the child tab. Alternatively, for simple custom fixed fee, populate the fee table row directly with service type "Fixed Fee".

**Step 3: Populate Resource/Staffing Plan Tab** (`'8. Resource/Staffing Plan'`)

Use `batch_values_update`:

| Cell | Value | Source |
|------|-------|--------|
| `D1` | Project start date | `dps.expected_start_date` |

**INPUT STAFFING DETAILS section** (row 19+): For each entry in `staffing_plan.role_weeks[]`:

| Column | Field | Source |
|--------|-------|--------|
| A | Project area | `meta.engagement_title` |
| B | Work product | Phase/workstream name |
| C | Role | Role name (must match template role names) |
| E | Total hours | Sum of `weekly_hours` array |
| F, G, H, ... | Weekly hours | `staffing_plan.role_weeks[].weekly_hours[0], [1], [2], ...` |

**Step 4: Populate Economic Review Summary Tab** (`'Economic Review Summary'`)

Use `batch_values_update` — GREEN cells only:

| Cell | Value | Source |
|------|-------|--------|
| `C4` | Account name | `meta.customer` |
| `C5` | Engagement name | `"{meta.customer} - {meta.engagement_title}"` |
| `C6` | SFDC opportunity link | `dps.sfdc_opportunity_url` |
| `C7` | Review date | Today's date (MM/DD/YYYY) |
| `C8` | PS Sales Team | `dps.ps_sales_team` |
| `I4` | Tech review completed? | `dps.economic_review_answers.tech_review_completed` |
| `I5` | Net new project? | `dps.economic_review_answers.net_new_project` |
| `I6` | Partner is prime? | `dps.economic_review_answers.partner_is_prime` |
| `I7` | Subcontractor involved? | `dps.economic_review_answers.subcontractor_involved` |
| `I8` | Investment planned? | `dps.economic_review_answers.investment_planned` |
| `I9` | Seeking additional discount? | `dps.economic_review_answers.seeking_additional_discount` |

The financial sections (rows 13+) auto-populate from the Deal Summary fee table. Do NOT write to them.

**Step 5: Store Result**

- Save the generated Sheet ID in `pricing.pricing_sheet_id` in deal-package.json.
- Construct the Sheet URL: `https://docs.google.com/spreadsheets/d/{sheet_id}/edit`
- Store the URL in `pricing.pricing_sheet_link`.
- Include the DPS link in the TDR Commercials slide (slide 16) notes.
- Report the Sheet URL to the user.

**Reference: MasterControl Completed DPS** — `1jM6SqCWL3vBZ__3RbetpsqI2GetjUnDLPU_8jZ9M9pw`
Use this as a pattern reference for correct cell population. Key values: A2="MasterControl - Get Well Investment", D5=SFDC URL, D8="Direct", D11="Yes", fee table rows with 100% investment discount, Resource/Staffing Plan with 20hrs/wk SA + 5hrs/wk SDM over 8 weeks.

### Phase 6.5: Self-Validation (TDR only — skip if TDR not generated)

Before delivering, validate the TDR deck against the TDR checklist:

```
SELF-VALIDATION CHECKLIST
═══════════════════════════

MANDATORY COMPLETENESS CHECKS (9/9 required):
[✓/✗] HAS_SCOPE — Detailed scope with in/out of scope
[✓/✗] HAS_OUT_OF_SCOPE — Explicit exclusions and assumptions
[✓/✗] HAS_CUSTOMER_OUTCOME — Business outcomes tied to objectives
[✓/✗] HAS_TIMELINE — Time-phased timeline with milestones
[✓/✗] HAS_RESOURCE_HOURS — Hours by role mapped to activities
[✓/✗] HAS_RACI — RACI with single Accountable per task
[✓/✗] HAS_RISKS_MITIGATIONS — Risk table with mitigations and owners
[✓/✗] HAS_VOLUMETRICS — Technical inventory (if applicable)
[✓/✗] HAS_MILESTONES — SMART milestones with acceptance criteria

YES/NO EVALUATION QUESTIONS (8/8 required):
[✓/✗] Business outcome discussed
[✓/✗] Engagement type clear
[✓/✗] Partner model mentioned (if applicable)
[✓/✗] Partner responsibilities defined (if applicable)
[✓/✗] Risks associated with scope items
[✓/✗] Risks include actionable mitigations
[✓/✗] Schedule exhausts proposed hours
[✓/✗] Activities consistent across all sections

RACI INTEGRITY CHECKS:
[✓/✗] Every row has exactly one A (Accountable)
[✓/✗] Customer is A for ~99% of rows
[✓/✗] Snowflake is not A for customer-owned decisions
[✓/✗] Table has 3 columns (or 4 if partner involved)

DPS CONSISTENCY CHECKS (if Deal Pricing Sheet generated or provided):
[✓/✗] Hours match DPS fee table
[✓/✗] Rates match DPS and FY27 pricebook
[✓/✗] Total deal value matches DPS
[✓/✗] DPS link included in Commercials slide notes
[✓/✗] SKU codes in DPS match pricing.roles[].sku in JSON
[✓/✗] Resource/Staffing Plan weekly hours match staffing_plan.role_weeks
[✓/✗] Economic Review Summary fields populated (account, engagement, SFDC link, date)

SLIDE AUDIENCE CHECKS:
[✓/✗] All SKIP slides have "(Skip for presentation)" subtitle
[✓/✗] No PRESENT slides have skip annotations
```

If any mandatory check fails, auto-fix or flag to the user.

**Target: 9/9 mandatory TRUE, 8/8 yes/no YES, all integrity checks TRUE.**

**Optional: TDR AI Assistant submission** — offer to submit the deck to `PST.AI_COUNCIL.SD_TDR_AI_ASSISTANT` for official scoring (requires `AI_COUNCIL_USER_RO_RL` role). Target score: 85+.

### Phase 7: Deliver

1. Write the master JSON to `~/Downloads/{CUSTOMER}-{DEAL_NAME}/deal-package.json`
2. List all generated files with paths
3. Present self-validation results (TDR only, if generated)
4. Remind the user:
   - HTML proposal: open in browser → Cmd+P to save as PDF
   - TDR deck: open in PowerPoint — all shapes are editable
   - HTML slide source files kept in `slides/` as the design source of truth

## Key Rules

### TDR Deck Generation
The TDR deck is built HTML-first: design each of the 21 slides as a 960×540px HTML file using the `snowflake-pptx-collateral-v4` brand system, then convert to a fully editable PPTX using python-pptx native shapes. The HTML files are kept as the design source of truth. Do not use `generate_tdr.py` — it is superseded by this approach.

### Character Limits
- Text paragraphs: MAX 350 characters
- Array items: MAX 125 characters each
- Arrays: MAX 4-5 bullet points
- Phase activities: MAX 3 items per phase, each MAX 90 chars
- Bold format: `"**Title**: description"` for all titled items

### RACI Rules (3-Column)
- Format: Activity / Snowflake / Customer (+ Partner if applicable)
- Customer = A (Accountable) by default for ~99% of rows
- Snowflake = R or C for most rows
- Every row must have exactly one A
- Snowflake is NEVER A for customer-owned decisions (signoff, approval, UAT, go-live)

### Pricing Defaults
If no pricing is provided, use FY27 Standard Price Book rates (SVC-TMSA $335/hr, SVC-TMSDM $260/hr). If a Deal Pricing Sheet is provided, extract pricing from it and include the link in the Commercials slide notes.

### SKU Reference Table

Map role titles in `pricing.roles[].title` to product codes for the DPS fee table:

| Role Title (in JSON) | Product Code (SKU) | Product Name (in DPS) | FY27 Rate |
|---|---|---|---|
| T&M Solutions Architect | SVC-TMSA | T&M Solutions Architect | $335/hr |
| T&M Senior Solutions Architect | SVC-TMSSA | T&M Senior Solutions Architect | $400/hr |
| T&M Principal Solutions Architect | SVC-TMPSA | T&M Principal Solutions Architect | — |
| T&M Solutions Consultant | SVC-TMSC | T&M Solutions Consultant | $325/hr |
| T&M Service Delivery Manager | SVC-TMSDM | T&M Service Delivery Manager | $260/hr |
| Custom Fixed Fee | SVC-CUSTOMFF | Custom Fixed Fee | per-deal |
| Custom Fixed Fee (PC) | SVC-CUSTFF-PC | Custom Fixed Fee (Partner Channel) | per-deal |

**Matching rules** (when user provides a role title without exact SKU):
- Contains "Senior" or "Sr" + "Architect" → SVC-TMSSA
- Contains "Principal" + "Architect" → SVC-TMPSA
- Contains "Solutions Architect" or "SA" (not Senior/Principal) → SVC-TMSA
- Contains "Solutions Consultant" or "SC" → SVC-TMSC
- Contains "Service Delivery Manager" or "SDM" → SVC-TMSDM
- Contains "Custom Fixed Fee" or "Fixed Fee" → SVC-CUSTOMFF (or SVC-CUSTFF-PC for partner channel)

### Timeline Always Embedded
Timeline appears in two places — the TDR deck Gantt slide AND the HTML proposal inline Gantt. It is NEVER a standalone artifact.

### Advisory Language (Timeline)
Snowflake activities must use advisory language:
- "architecture review" not "architecture build"
- "performance advisory" not "performance tuning"
- "enablement" not "implementation"
- Snowflake does NOT own: pipeline dev, data modeling, production ops, KT, handoff, deployment

### SKIP Slides
Slides marked SKIP in the audience map get `"(Skip for presentation)"` as subtitle. They are NOT shown to customers but contain critical review content. No deck-wide "internal only" footer — only SKIP slides are annotated.

## Stopping Points

- Phase 0: After auto-population, present fact sheet for confirmation
- Phase 1: After each interview group if information is incomplete
- Phase 1.5: After DPS check, confirm pricing approach
- Phase 2: If validation fails, present missing items before looping back
- Phase 4: **MANDATORY** — Wait for user approval of the master JSON
- Phase 5: **MANDATORY** — After HTML proposal delivery, ask which additional artifacts to generate
- Phase 6.5: After TDR self-validation, present results (TDR only)
- Phase 7: After delivery, wait for user review feedback

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `tech-review-generator` | TDR generation authority. Provides the MASTER template, approved examples, and 39-item checklist. `generate_tdr.py` follows its patterns. |
| `proposal-generator` | Legacy PPTX orchestrator. Superseded by deal-package for TDR generation. Still provides uv project environment. |
| `sd-technical-deal-review` | Legacy template sub-skill. Superseded by MASTER template. Retained for reference. |
| `snowflake-pptx-collateral-v4` | **Primary TDR deck generator.** Provides HTML design system + editable PPTX builder patterns used in Phase 6A. Load its references before writing TDR slide HTML. |
| `snowflake-html-collateral` | Brand system for one-page HTML proposal generation. |
| `sow-generator` | Optional delegation target for .docx SOW output. |
| `capacity-to-pst` | Optional delegation target for capacity conversion deals. |
| `kickoff-deck-generator` | Post-deal skill. Not used by deal-package. |
| DPS Template `1jXFPXMTQFc_qMV48E42iRs7mUiP9vqgaagQntGJ6KdU` | FY27 v0.10 Deal Pricing Sheet template (17 tabs). Copy via `copy_file`, populate green cells only. |
| MasterControl DPS `1jM6SqCWL3vBZ__3RbetpsqI2GetjUnDLPU_8jZ9M9pw` | Completed DPS reference for cell population patterns. |

## Scoring Model Reference (from tech-review-generator)

The TDR AI Assistant scores decks on a 0-100 completeness scale:
- **PASS**: score >= 76 (avg 84, range 76-93)
- **NEEDS_REVISIONS**: score < 76 (avg 67, range 47-74)

Key differentiators between PASS and NEEDS_REVISIONS:
1. HAS_OUT_OF_SCOPE — explicit exclusions
2. HAS_TIMELINE — time-phased with milestones
3. HAS_RISKS_MITIGATIONS — risks with mitigations and owners
4. HAS_MILESTONES — SMART milestones with acceptance criteria
