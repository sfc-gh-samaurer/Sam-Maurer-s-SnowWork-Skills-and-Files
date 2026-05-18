---
name: deal-package-standalone
description: "Generate a complete deal review package: one-page HTML proposal (always) and optional TDR deck (PPTX). Use for ALL requests that mention: deal package, deal review, proposal package, TDR, deal materials, generate proposal deck, create deal review. DO NOT attempt deal package generation manually - always invoke this skill first."
---

# Deal Package Generator (Standalone)

Generate a complete, deal-review-passing package of materials from a single structured interview. This skill is fully self-contained with no dependencies on other skills.

## Output Artifacts

| # | Artifact | Format | Selection | Method |
|---|----------|--------|-----------|--------|
| 1 | **One-Page Proposal** | HTML | [x] Always | Brand system HTML/CSS, timeline embedded inline — generated first |
| 2 | **TDR Deck** | PPTX | [ ] Optional | Self-contained design system → editable PPTX via python-pptx |

**Timeline is NEVER a standalone artifact.** It is always embedded:
- In the TDR deck as the Gantt slide (slide 11)
- In the HTML proposal as an inline CSS grid Gantt

## Output Directory

ALL artifacts are written to:
```
~/Downloads/{CUSTOMER}-{DEAL_NAME}/
```
Where `{CUSTOMER}` and `{DEAL_NAME}` are derived from user input (spaces replaced with hyphens, title case).

## Prerequisites

- `uv` installed (for running python-pptx scripts)
- `python-pptx` installed: `pip install python-pptx`

## Pricing & Estimation Guardrails

**⚠️ CRITICAL: All estimates are INDICATIVE ONLY and require Pre-Sales Architecture validation before customer-facing use.**

- ALWAYS present pricing as ranges (±40%), NEVER single-point estimates
- NEVER output a single dollar amount like "$53,600" — always "$45K - $75K"
- NEVER output a single hour figure like "160 hours" — always "130-200 hours"
- Customer-facing HTML proposal shows ranges: "$X - $Y"
- Internal TDR shows role-level detail but includes disclaimer
- Load `references/pricing-guidance.md` for rate cards and sizing heuristics

**Disclaimer (include in every pricing section):**
> Investment estimates are indicative and subject to Pre-Sales Architecture review. Actual investment will depend on scope refinement, resource availability, and engagement complexity.

## TDR Deck Slide Structure (21 slides)

The TDR deck follows the MASTER template structure. Each slide is tagged with its audience.

| # | Slide | Audience | Layout |
|---|-------|----------|--------|
| 1 | Title / Cover | PRESENT | Dark gradient cover |
| 2 | Agenda | PRESENT | Two-column list |
| 3 | Executive Summary | PRESENT | Three-column card grid |
| 4 | Our Understanding | PRESENT | Two-column |
| 5 | Methodology & Engagement Approach | PRESENT | Phase table |
| 6 | Outcomes | PRESENT | Two-column card grid |
| 7 | Scope Summary | PRESENT | Three-column cards |
| 8 | Scope by Role | **SKIP** | Two-column table |
| 9 | Technical Review Outcome | **SKIP** | Placeholder |
| 10 | Dependencies | PRESENT | Bulleted card list |
| 11 | Timeline with Key Milestones | PRESENT | Gantt chart |
| 12 | Milestones & Validation | PRESENT | Table |
| 13 | Detailed RACI | PRESENT | RACI table |
| 14 | Governance Cadence | PRESENT | Table |
| 15 | Team Structure | PRESENT | Team cards |
| 16 | Commercials / Pricing | **SKIP** | Pricing table + disclaimer |
| 17 | Staffing Plan | **SKIP** | Role-by-week grid |
| 18 | Risks & Mitigations | PRESENT | 7-row table |
| 19 | Assumptions & Commitments | PRESENT | Two-section bullets |
| 20 | Next Steps / Close Plan | PRESENT | Action table |
| 21 | Thank You | PRESENT | Dark gradient closing |

Slides marked **SKIP** get "(Skip for presentation)" as subtitle — they contain critical review content but are not shown to customers in live meetings.

### Conditional Slides (appended after slide 21 when applicable)

| Condition | Slides to Add |
|-----------|--------------|
| **Migration deal** | Source inventory, migration approach, testing plan |
| **Partner involved** | Partner scope/responsibilities, contracting model |
| **Investment > $500k** | Stage Gates (discovery, conversion, burndown) |
| **Fixed Fee** | Enhanced milestones with explicit acceptance criteria per milestone |

## Workflow

### Phase 0: Auto-Populate Known Facts

Before asking the user for information, attempt to pre-populate known facts from available sources:

**Source 1 — Memory files** (check `/memories/` for account context):
```
memory view /memories/ → look for files matching customer name
If found, read to extract AE, SE, contacts, deal context, prior decisions.
```

**Source 2 — Services POV** (if exists as a file):
```
Look for *_Services_POV.md in ~/Downloads/ or user-specified directory.
If found, extract:
  - Engagement framing → meta.engagement_title
  - Phases/roadmap → gantt.phases
  - Account team → meta.ae_name, meta.se_name
  - Use case context → tdr.our_understanding
  - Investment range → pricing estimate (still requires validation)
```

**Source 3 — Snowhouse Query** (direct SQL, no skill dependency):
```sql
USE ROLE SALES_RAVEN_RO_RL;
USE WAREHOUSE SNOWHOUSE;
SELECT OPPORTUNITY_NAME, ACCOUNT_NAME, AE_NAME, SE_NAME, STAGE, AMOUNT
FROM sales.raven.sda_opportunity_view
WHERE ACCOUNT_NAME ILIKE '%<customer>%'
  AND is_open = 1
ORDER BY CLOSE_DATE DESC LIMIT 5;
```

**Source 4 — User Interview** (for any remaining gaps):
Only ask the user for facts not found in Sources 1-3. Present what was auto-populated and ask for confirmation/corrections.

**Output**: A fact sheet with known values and `[TBD — need from user]` markers for unknowns.

### Phase 1: Context Collection (Source-Document-First)

**PRIMARY PATH: Accept a source document and extract from it.**

Ask the user: "Do you have a source document I can work from? (meeting notes, SOW draft, pricing sheet, prior proposal, Services POV, or pasted text)"

**If source document provided:**
1. Read/parse the entire document
2. Extract ALL possible fields into the master JSON structure
3. Present extracted data as a fact sheet
4. Ask ONLY for gaps (typically 5-10 questions, not 40)

**If no source document (interview path):**

Collect information using `ask_user_question` for each group. Keep questions focused on gaps only.

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
5. Snowflake features and products involved
6. **Strategic / business outcomes** — ROI, cost savings, time reduction, business value
7. **Technical outcomes** — capabilities delivered, architecture improvements

**Group C — Methodology, Timeline & Milestones**
1. Phases with names, durations, and activities per phase
2. Total duration in weeks
3. Target go-live date
4. Which activities are Snowflake-owned vs Customer-owned vs SI-owned
5. **Milestones with acceptance criteria** — name, deliverables, acceptance criteria, duration

**Group D — Team, Pricing & Staffing**
1. Roles on the engagement (SA, SC, SDM, etc.)
2. Hours per role — *always as estimated ranges (e.g., "150-200 hrs")*
3. Rates per role (defaults from FY27 Standard Price Book if not provided)
4. Snowflake investment amount (if any) — *indicate as range*
5. Customer total after investment — *indicate as range*
6. **SA activities** — specific deliverables the SA owns
7. **SDM activities** — specific responsibilities the SDM owns
8. **Team structure** — named resources where known

**FY27 Standard Price Book Defaults (Reference Only):**
| SKU | Role | Rate |
|-----|------|------|
| SVC-TMSSA | Senior Solution Architect | $400/hr |
| SVC-TMSA | Solution Architect | $335/hr |
| SVC-TMSC | Solutions Consultant | $325/hr |
| SVC-TMSDM | Service Delivery Manager | $260/hr |

*Rates are list prices. Final pricing requires Pre-Sales Architecture validation.*

**Group E — Governance & RACI**
1. Governance forums (e.g., Weekly standup, Biweekly steering, Monthly exec review)
2. Cadence, participants, responsibilities, materials for each forum
3. RACI activities — see RACI Rules section below

**Group F — Risk & Boundaries**
1. Assumptions (commitments, access requirements, role expectations, clarifications)
2. Dependencies (items that must be complete before kickoff)
3. Risks for ALL 7 categories (each needs: risk description, impact level, mitigation):
   - Organizational, Governance, Technical, Resource, Scope, Timeline, Adoption
4. Out-of-scope items (explicit exclusions)

**Group G — Close Plan**
1. Next steps / actions with owners and details (5-6 items)

**Input Sources:** The user may provide any of:
- Pasted meeting notes or description text
- File paths to documents (SOW, proposal drafts, meeting recordings)
- Memory file references
- Previous proposal artifacts to reference
- Services POV markdown file

If the user provides a rich source document, extract as much as possible from it and only ask for gaps.

### Phase 2: Deal Review Validation Gate

Before generating any artifacts, validate completeness against the TDR checklist. ALL items must be present:

- [ ] Executive summary (problem + solution + outcomes in 2-3 sentences)
- [ ] Current state + engagement objectives documented
- [ ] Methodology with named phases, durations, and activities
- [ ] Outcomes — strategic/business AND technical
- [ ] Scope boundaries defined (assessment, architecture, implementation, out-of-scope)
- [ ] Scope by role — SA and SDM activities with hours (as ranges)
- [ ] Program schedule / timeline with phases mapped to weeks
- [ ] Milestones with SMART acceptance criteria
- [ ] Dependencies listed (pre-kickoff requirements)
- [ ] RACI populated (3-column: Activity / Snowflake / Customer, at least 8-10 rows)
- [ ] Governance cadence defined (at least 2-3 forums)
- [ ] Team structure with named roles
- [ ] Pricing with roles, hours (ranges), rates, subtotal range, investment, customer total range
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
- `outcomes` — strategic and technical outcomes
- `scope_by_role` — SA/SDM activities
- `milestones` — milestone table
- `raci` — 3-column RACI activities
- `team_structure` — named roles
- `staffing_plan` — role-by-week hours
- `pricing` — roles/hours/rates (*all as estimated ranges*)
- `html_proposal` — metrics, pain points, deliverables, team cards, why PS, etc.
- `timeline_embed` — display options for embedded timeline

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

## Pricing (Slide 16) — INTERNAL ONLY, REQUIRES PRE-SALES ARCHITECTURE REVIEW
| Role | Hours (Est. Range) | Rate | Estimated Range |
|...|...|...|...|
**Estimated Subtotal:** $X - $Y | **Investment:** ($Z) | **Estimated Customer Total:** $A - $B

> ⚠️ All pricing is indicative (±40%) and requires Pre-Sales Architecture validation.
```

**MANDATORY STOPPING POINT.** Wait for user approval or change requests. Iterate until approved.

### Phase 5: Generate One-Page HTML Proposal (Always)

Generate the HTML proposal immediately after JSON approval — no artifact selection gate needed.

Generate using the brand system HTML/CSS. Load the HTML template from `<SKILL_DIR>/templates/html-one-page.html` and populate with data from the master JSON. The template sections:

1. **Header** — Blue gradient, engagement title, customer name, date, DRAFT tag
2. **Metrics** — 3 metric cards (duration, total cost *as range*, key stat)
3. **Summary paragraph** — engagement overview
4. **The Problem** — 2x2 grid of pain cards with icons
5. **What You Get** — 3-column deliverable cards with bullet lists
6. **Timeline** — CSS grid Gantt chart (embedded inline, NOT standalone)
7. **T&M/FF Qualifier** — engagement type terms callout
8. **Why Snowflake PS** — 3-column value cards
9. **Delivery Team** — role cards with hours@rate *shown as ranges*
10. **Assumptions & Dependencies** — bullet lists
11. **Out of Scope** — bullet list
12. **Next Steps** — action table
13. **Footer** — Copyright + Confidential + Pricing disclaimer

**Pricing in HTML proposal:** Always show as ranges. Include footer text:
> "The investment range above represents an initial estimate based on current scope understanding. Final pricing will be confirmed following detailed scoping and architecture review."

Write to: `~/Downloads/{CUSTOMER}-{DEAL_NAME}/{CUSTOMER}-Proposal.html`

**⚠️ STOPPING POINT after HTML delivery.** Present the file path, then ask:

> The one-page HTML proposal is ready. Would you like to generate the TDR Deck (PPTX)?

Use `ask_user_question` with options:
- **Yes — generate TDR Deck (PPTX)** — full 21-slide deal review deck
- **No — proposal only**

If user selects no, proceed to Phase 7 (Deliver). Otherwise proceed to Phase 6.

### Phase 6: Generate TDR Deck (PPTX)

The TDR deck is built using the self-contained design system in `<SKILL_DIR>/references/tdr-design-system.md`.

**Step 1: Load design system reference**

Load `<SKILL_DIR>/references/tdr-design-system.md` for:
- CSS design tokens and brand colors
- python-pptx helper function patterns
- Geometry constants
- Fill→Text contrast rules
- Slide type implementation patterns

**Step 2: Create slides directory**
```bash
mkdir -p ~/Downloads/{CUSTOMER}-{DEAL_NAME}/slides/
```

**Step 3: Write one HTML file per slide**

Create `slides/slide_01_cover.html` through `slides/slide_21_thankyou.html` using the design system. Every slide must be exactly **960×540px** with `overflow: hidden`.

Design rules (enforced):
- Titles: 18px bold Title Case on content slides; ALL CAPS only on cover/chapter
- Font: Arial everywhere — never Montserrat, Roboto, or Lato
- Use CSS variables from the design token block — never invent colors
- Left edge bar: 4px `var(--sf-blue)` on every content slide
- Footer: `"© 2026 Snowflake Inc. All Rights Reserved"` at `top:511px`
- Content must not extend below `top:490px`
- At least 50% of content slides use a visual pattern (card grid, table, timeline, two-column) — not just bullets
- Cover, Thank You use dark/blue gradient backgrounds with white text
- SKIP slides: add `"(SKIP FOR PRESENTATION)"` as a red badge in the top-right corner
- Pricing slides: include disclaimer "Estimates are indicative — Pre-Sales Architecture review required"

**TDR Slide → Visual Pattern mapping:**

| Slide | Title | Visual Pattern |
|-------|-------|----------------|
| 1 | Cover | Dark gradient cover slide |
| 2 | Agenda | Two-column list |
| 3 | Executive Summary | Three-column card grid (Challenges / Solution / Outcomes) |
| 4 | Our Understanding | Two-column (Current State / Engagement Objectives) |
| 5 | Methodology | Phase table: Phase / Workstreams / Duration / Activities |
| 6 | Outcomes | Two-column card grid (Strategic/Business / Technical) |
| 7 | Scope Summary | Three-column cards + out-of-scope section |
| 8 | Scope by Role *(SKIP)* | Two-column table: SA / SDM activities with hours |
| 9 | Technical Review *(SKIP)* | Placeholder for reviewer |
| 10 | Dependencies | Bulleted card list |
| 11 | Timeline | Gantt chart — CSS grid with phase bars and week labels |
| 12 | Milestones | Table: Milestone / Deliverables / Acceptance Criteria / Duration |
| 13 | RACI | RACI table with R/A/C/I badges |
| 14 | Governance | Table: Forum / Cadence / Participants / Responsibilities |
| 15 | Team Structure | Team cards with names and hours |
| 16 | Commercials *(SKIP)* | Pricing table + total range + disclaimer |
| 17 | Staffing Plan *(SKIP)* | Role-by-week allocation grid |
| 18 | Risks | Table: Category / Risk / Impact / Mitigation (7 categories) |
| 19 | Assumptions | Two-section bullet list (Assumptions / Dependencies) |
| 20 | Next Steps | Action table: Step / Owner / Details |
| 21 | Thank You | Dark gradient closing with contact info |

**Step 4: Convert HTML → Editable PPTX**

Use the python-pptx patterns from `references/tdr-design-system.md` to write a Python script that builds the deck as native shapes, text boxes, and tables.

```bash
python ~/Downloads/{CUSTOMER}-{DEAL_NAME}/build_tdr.py
```

Output: `~/Downloads/{CUSTOMER}-{DEAL_NAME}/{CUSTOMER}-TDR.pptx`

**What is preserved exactly:** All text, tables, layout geometry, brand colors, edge bars, footers.
**What is approximated:** CSS gradients → solid fill; border-radius → square corners; box-shadows → omitted.

### Phase 6.5: Self-Validation (TDR only)

Before delivering, validate the TDR deck:

```
SELF-VALIDATION CHECKLIST
═══════════════════════════

MANDATORY COMPLETENESS CHECKS (9/9 required):
[✓/✗] HAS_SCOPE — Detailed scope with in/out of scope
[✓/✗] HAS_OUT_OF_SCOPE — Explicit exclusions and assumptions
[✓/✗] HAS_CUSTOMER_OUTCOME — Business outcomes tied to objectives
[✓/✗] HAS_TIMELINE — Time-phased timeline with milestones
[✓/✗] HAS_RESOURCE_HOURS — Hours by role mapped to activities (as ranges)
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

PRICING CHECKS:
[✓/✗] All pricing shown as ranges (±40%)
[✓/✗] Pricing disclaimer included on Commercials slide
[✓/✗] Pre-Sales Architecture review callout present
[✓/✗] No single-point dollar amounts anywhere in the deck

SLIDE AUDIENCE CHECKS:
[✓/✗] All SKIP slides have "(Skip for presentation)" subtitle
[✓/✗] No PRESENT slides have skip annotations
```

If any mandatory check fails, auto-fix or flag to the user.

### Phase 7: Deliver

1. Write the master JSON to `~/Downloads/{CUSTOMER}-{DEAL_NAME}/deal-package.json`
2. List all generated files with paths
3. Present self-validation results (TDR only, if generated)
4. Remind the user:
   - HTML proposal: open in browser → Cmd+P to save as PDF
   - TDR deck: open in PowerPoint — all shapes are editable
   - HTML slide source files kept in `slides/` as the design source of truth
   - **⚠️ All pricing is indicative (ranges only) and requires Pre-Sales Architecture review before external sharing**

## Key Rules

### RACI Rules (STRICT)

1. **One A per row**: Every RACI row must have exactly ONE "A" (Accountable)
2. **Customer owns outcomes**: Customer = A (Accountable) by default for ~99% of rows
3. **Snowflake delivers**: Snowflake = R (Responsible) or C (Consulted) for most rows
4. **Snowflake NEVER accountable for**: customer signoff, approval, UAT, go-live decisions, data quality, business requirements validation
5. **Only exception**: Snowflake may be "A" for deliverable creation (e.g., "Deliver architecture document")
6. **Partner column**: Add only if `meta.si_partner` is set. Partner follows same rules as Snowflake.
7. **Minimum rows**: At least 8-10 RACI activities

### Character Limits
- Text paragraphs: MAX 350 characters
- Array items: MAX 125 characters each
- Arrays: MAX 4-5 bullet points
- Phase activities: MAX 3 items per phase, each MAX 90 chars
- Bold format: `"**Title**: description"` for all titled items

### Pricing Defaults
If no pricing is provided, use FY27 Standard Price Book rates (SVC-TMSA $335/hr, SVC-TMSDM $260/hr) as the basis for ±40% range calculation. All pricing shown as ranges until Pre-Sales Architecture validation. NEVER output a single-point dollar amount.

### SKU Reference Table

| Role Title | Product Code (SKU) | FY27 Rate |
|---|---|---|
| T&M Solutions Architect | SVC-TMSA | $335/hr |
| T&M Senior Solutions Architect | SVC-TMSSA | $400/hr |
| T&M Principal Solutions Architect | SVC-TMPSA | — |
| T&M Solutions Consultant | SVC-TMSC | $325/hr |
| T&M Service Delivery Manager | SVC-TMSDM | $260/hr |

### Timeline Always Embedded
Timeline appears in two places — the TDR deck Gantt slide AND the HTML proposal inline Gantt. It is NEVER a standalone artifact.

### Advisory Language (Timeline)
Snowflake activities must use advisory language:
- "architecture review" not "architecture build"
- "performance advisory" not "performance tuning"
- "enablement" not "implementation"
- Snowflake does NOT own: pipeline dev, data modeling, production ops, KT, handoff, deployment

### SKIP Slides
Slides marked SKIP get `"(Skip for presentation)"` as subtitle. They are NOT shown to customers but contain critical review content.

## Stopping Points

- Phase 0: After auto-population, present fact sheet for confirmation
- Phase 1: After source document extraction OR each interview group if information is incomplete
- Phase 2: If validation fails, present missing items before looping back
- Phase 4: **MANDATORY** — Wait for user approval of the master JSON
- Phase 5: **MANDATORY** — After HTML proposal delivery, ask whether to generate TDR
- Phase 6.5: After TDR self-validation, present results
- Phase 7: After delivery, wait for user review feedback

## Self-Contained Design

This skill has no dependencies on other skills. All required resources are included:
- `references/pricing-guidance.md` — rate cards, T-shirt sizing, range calculation
- `references/tdr-design-system.md` — complete brand system for TDR deck generation (colors, geometry, python-pptx patterns)
- `templates/html-one-page.html` — HTML proposal template
- `scripts/build_tdr_template.py` — python-pptx TDR builder template
- `schemas/deal-package-schema.json` — master JSON schema
