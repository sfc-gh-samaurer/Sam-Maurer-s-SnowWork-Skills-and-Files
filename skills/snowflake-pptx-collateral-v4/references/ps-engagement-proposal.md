---
name: ps-engagement-proposal
description: Standard structure, slide-by-slide guidance, and content rules for Snowflake Professional Services engagement proposal decks built with the snowflake-pptx-collateral-v4 system.
---

# PS Engagement Proposal — Canonical Deck Structure

Use this reference whenever the user asks for a **PS engagement proposal deck**. This defines the
standard slide order, content expectations, and conditional slots. Always build using the
`snowflake-pptx-collateral-v4` editable PPTX approach (official Snowflake template + python-pptx).

**Reference implementation:** `/tmp/build_workday_finops_proposal.py`
**Reference output:** `~/Google Drive/My Drive/Accounts/Workday/Workday_FinOps_Transformation_Proposal_May2026.pptx`

---

## Engagement Types

Adjust the deck based on what type of PS engagement is being proposed:

| Engagement Type | Notes |
|----------------|-------|
| **FinOps / Cost Optimization** | Include Value Summary slide (slide 4) with savings table and ROI |
| **Architecture / Platform Build** | Replace Value Summary with "Why Now / Platform Maturity" slide |
| **Governance / Security** | Replace Value Summary with "Risk Reduction & Compliance" slide |
| **AI / ML Implementation** | Replace Value Summary with "Use Case Pipeline & Business Impact" slide |
| **Migration** | Replace Value Summary with "Migration Complexity & Risk Assessment" |
| **General PS Engagement** | Skip slide 4 entirely or use a generic "Business Case" slide |

The rest of the deck (slides 1–3, 5–18) is **engagement-agnostic** and applies to all proposals.

---

## Standard Deck Structure (28 slides)

### MAIN DECK (18 slides)

#### Slide 1 — Cover
- **Layout:** `prs.slide_layouts[13]` (Data Cloud_1_1 — official Snowflake cover)
- **PH mapping:** PH[3]=title (44pt, ALL CAPS, ≤50 chars), PH[0]=subtitle, PH[2]=author/date
- **Title format:** `"[CUSTOMER] [SHORT DESCRIPTION]"` — e.g., `"WORKDAY FINOPS\nTRANSFORMATION"`
- **Subtitle:** Full engagement description — e.g., `"FinOps Framework, Standards & Optimization Execution"`
- **Author:** `"[SA Name] · [Role]  |  [SDM Name] · [Role]  |  [Month Year]"`

#### Slide 2 — Agenda
- **Pattern:** 6–7 column card grid with numbered sections
- **Each card:** Large number (22pt bold), sublabel (7pt teal), section title (9pt bold), 1-line description (8pt)
- **Standard agenda items:** Executive Summary · [Value/Business Case] · Eng. Objectives · Scope & Model · Deliverables · Timeline · Team & Governance
- **Visual:** SF_MID_BLUE header per card, SF_LIGHT_BG body, SF_BLUE footer badge

#### Slide 3 — Executive Summary
- **Pattern:** KPI row (4 boxes) + two context panels + 4-column workstream grid
- **KPI row:** 4 key numbers (e.g., current state metric, problem indicator, engagement focus %, opportunity size)
- **Context panels (left/right):** "Situation" (light blue) + "New Engagement Model" (light grey)
- **Workstream grid:** 4 mini-cards, alternating SF_MID_BLUE/SF_BLUE headers, SF_LIGHT_BG body
- **Content:** Briefly explain the customer's situation, the engagement pivot/rationale, and the 4 major workstream areas

#### Slide 4 — [CONDITIONAL: Value / Business Case]
> **Include for:** FinOps/cost optimization engagements — use savings table format below
> **Replace with:** Appropriate business case slide for other engagement types (see Engagement Types table)
> **Skip for:** Simple implementation engagements where the value is self-evident

**FinOps / Cost Optimization format:**
- **Pattern:** 3 KPI boxes (large) + detailed savings breakdown table
- **KPI boxes:** Total savings potential · % of annualized spend · Number of workstreams
- **Table headers:** Workstream · Annual Savings Estimate · Difficulty · Timeline · Executor
- **Last row:** TOTAL row highlighted in SF_MID_BLUE with white text
- **Footnote:** `"** All savings figures are estimates and not binding or guaranteed"`

#### Slide 5 — Engagement Objectives & Success Criteria
- **Pattern:** 2×2 grid of objective cards
- **Each card:** Number badge (SF_BLUE) + title bar (SF_MID_BLUE) + body text (SF_LIGHT_BG) + metric footer (SF_TEAL)
- **Standard 4 objectives:** (1) Primary technical/platform outcome, (2) Execution/delivery outcome, (3) Standards/governance outcome, (4) Long-term sustainability outcome
- **Metric footer:** Always include a concrete success metric (e.g., "Success: X within Y weeks")
- **Content tip:** Objectives should be measurable. Avoid vague outcomes like "improve the platform."

#### Slide 6 — Engagement Model
> If engagement has a **partner or co-delivery model** (phData, SI partner, customer self-service), use a two-column split showing % split and what each party owns.
> For **Snowflake-only** engagements, replace with a single-column workstream overview or a "Delivery Philosophy" card grid.

**Two-party model format (e.g., 20/80 or 30/70):**
- **Left column (partner %):** Blue header bar, 5–6 row table showing partner scope items
- **Vertical divider**
- **Right column (Snowflake %):** Navy header bar, 5–6 card rows showing SA-led workstreams
- **Each row:** Title bar + description text with 1–2 lines

#### Slide 7 — Workstream Scope Summary (1/2)
- **Pattern:** 3 stacked workstream cards (one per WS)
- **Each card:** Header bar with WS number, title, hours badge (SF_TEAL), timeline badge (SF_BLUE or SF_MID_BLUE)
- **Card body:** 6 bullet points (SF_LIGHT_BG), uses `•` prefix in set_shape_text
- **Card footer:** Deliverables list in SF_LIGHT_BLUE bar
- **Slide covers:** WS1, WS2, WS3

#### Slide 8 — Workstream Scope Summary (2/2)
- **Same pattern** as slide 7
- **Slide covers:** WS4, WS5, WS6 (or phData support workstream)
- If fewer than 6 workstreams, combine into a single scope slide

#### Slide 9 — Engagement Deliverables
- **Pattern:** Full-width table
- **Table headers:** Deliverable · Description · Format · Workstream
- **Column widths:** [2.5", 3.5", 1.5", 1.2"]
- **Aim for 10–14 rows** — one per tangible deliverable
- **First column bold** — deliverable name is the anchor

#### Slide 10 — [CONDITIONAL: Deliverables Detail / Assessment Assets]
> **Include for:** Engagements where deliverable quality needs selling (FinOps dashboards, AI agents, assessment reports, architecture blueprints)
> **Skip for:** Implementation engagements where the deliverables table alone is sufficient

**Assessment Assets format (6-card grid):**
- 3×2 card grid, alternating SF_MID_BLUE/SF_BLUE headers
- Each card: emoji icon + asset title (header), 4–5 bullet points (body)
- Cards represent the major deliverable categories: dashboards, models, standards docs, pipelines, reports, playbooks

#### Slide 11 — Project Timeline
- **Pattern:** KPI row (3 boxes) + week-column header row + phase band row + Gantt rows
- **KPI boxes:** Total hours · Delivery weeks · Workstream count
- **Phase bands:** SETUP | CORE DELIVERY | OPERATIONALIZE | SUSTAIN (or similar 3–4 phases)
- **Gantt rows:** One row per workstream. Alternating SF_LIGHT_ROW/SF_WHITE label column, SF_MID_BLUE/SF_BLUE/SF_TEAL bars
- **Include:** Cross-engagement row for Program Management (all weeks, SF_TEAL bar)
- **Tip:** Keep total weeks to 12–24 max for readability. For multi-phase engagements, consider a simplified 2-phase timeline instead.

#### Slide 12 — Snowflake Roles & Responsibilities
- **Pattern:** 2–3 stacked role cards (one per Snowflake team member)
- **Each card:** SF_MID_BLUE header bar with ❄ icon + role title + time commitment badge (SF_BLUE)
- **Body:** SF_LIGHT_BG with 6 responsibility bullets
- **Standard Snowflake roles:** Solution Architect (20 hrs/wk) + Services Delivery Manager (4 hrs/wk)
- **Add as needed:** FinOps SE, Platform Architect, Technical Account Manager

#### Slide 13 — Workday / Customer Roles & Responsibilities
- **Pattern:** Full-width table
- **Table headers:** Role · Involvement · Responsibilities
- **Column widths:** [2.4", 1.1", 5.6"]
- **Aim for 5–7 rows** — one per required customer counterpart
- **Involvement tiers:** Required / Strongly Rec. / As Needed
- **Always include:** Platform Lead, Executive Sponsor, technical leads per major workstream

#### Slide 14 — Engagement RACI
- **Pattern:** RACI matrix table with color-coded R/A/C/I cells + legend
- **Table headers:** Activity · Snowflake SA · Snowflake SDM · [Customer] · [Partner if applicable]
- **RACI colors:** R=SF_BLUE/white · A=light blue/SF_BLUE · C=very light blue/SF_MID_BLUE · I=SF_LIGHT_BG/grey
- **Aim for 10–14 activity rows**
- **Legend:** Small badges at bottom of slide (inside safe zone)
- **Standard activities to always include:** Design/Build, Code Review, Environment Access, Status Reviews, Deliverable Acceptance, Knowledge Transfer

#### Slide 15 — Assumptions & Exclusions
- **Pattern:** 2×2 grid of assumption category cards
- **Standard 4 categories:** Customer Responsibilities · Technical Assumptions · Scope Boundaries · Engagement Exclusions
- **Each card:** SF_MID_BLUE or SF_BLUE header + SF_LIGHT_BG body with 4 bullets
- **Bullets:** Written as concrete statements, not vague disclaimers
- **Exclusions are as important as assumptions** — be explicit about what's NOT in scope

#### Slide 16 — Risk & Assumption Mitigations
- **Pattern:** 2×3 grid of risk cards (6 risks total)
- **Each card:** Severity badge (SF_RED/AMBER/GREEN) + title bar (SF_MID_BLUE) + body text (SF_LIGHT_BG)
- **Severity:** HIGH (2–3), MEDIUM (2–3), LOW (1–2)
- **Body text format:** `"Risk: [what could go wrong].\nMitigation: [how we handle it]"`
- **Standard risks to always include:** Customer availability, environment access, scope creep, organizational change, data quality/access

#### Slide 17 — Pricing
- **Pattern:** 4 KPI boxes (investment metrics) + resource breakdown table + pricing note callout
- **KPI boxes:** Total Investment (TBD or value) · Expected ROI or Value · SA Hours · Engagement Duration
- **Table headers:** Resource · Role · Weekly Hours · Total Hours · Rate
- **Standard rows:** Solution Architect + Services Delivery Manager + TOTAL (highlighted in SF_MID_BLUE)
- **Pricing note:** SF_LIGHT_BLUE callout box with pricing structure clarification
- **Footnote:** Savings/value disclaimer if applicable
- **IMPORTANT:** If investment is not yet confirmed, use `"TBD"` — never fabricate numbers

#### Slide 18 — Next Steps
- **Pattern:** 2-column grid of numbered action steps (4 per column = 8 total)
- **Each step:** Number badge (SF_BLUE) + title bar (SF_MID_BLUE) + description body (SF_LIGHT_BG)
- **Standard 8 next steps:**
  1. Sign-off on scope and approach
  2. Budget approval
  3. Execute Order Form and SOW
  4. Confirm partner/co-delivery alignment (if applicable)
  5. Initiate staffing (Solution Architect)
  6. Assign named customer counterparts
  7. Complete environment readiness (access, provisioning)
  8. Project Kickoff

---

### APPENDIX (10 slides)

#### Slide 19 — Appendix Divider
- **Layout:** `prs.slide_layouts[20]` (chapter divider with wave)
- **PH[1] text:** `"APPENDIX"`

#### Slides 20–28 — Appendix Content

**Standard appendix slides to include (select 5–9 based on engagement type):**

| Slide | Title | When to Include |
|-------|-------|-----------------|
| Maturity Model | "Snowflake [Domain] Maturity Model" | Always — shows where customer is today vs. end state |
| Platform Capabilities | "Snowflake [Domain] Capabilities" | Always — shows native features powering the engagement |
| Framework Detail | "[WS1 Name] Framework Detail" | When WS1 is complex or needs expanded explanation |
| Deliverables Detail | "Deliverables Object Details — [Name]" | When specific deliverables need extra justification |
| Standards Overview | "[Standards/Charter] Overview" | For governance engagements — excerpt key policies |
| Partner Model | "[Partner] Partnership Model" | When a partner is executing a significant workstream |
| Use Case & Capacity | "Use Case & Capacity Support" | Always — ties engagement to renewal/capacity context |
| Technical Architecture | "Technical Architecture Overview" | For build/migration engagements |
| Slide 28 | Thank You | Always last slide |

#### Slide 28 (always last) — Thank You
- **Layout:** `prs.slide_layouts[28]` (Thank You with wave)
- **PH[1] text:** `"THANK\nYOU"`
- **Contact card:** SF_MID_BLUE panel (right side) with team names, roles, emails
- **Tagline:** Engagement-specific closing line

---

## Build Script Pattern

Use the following template to bootstrap any new PS engagement proposal:

```python
#!/usr/bin/env python3
"""
[Customer] [Engagement Name] Proposal
Snowflake Professional Services — [Month Year]
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE

# ── Color constants (copy verbatim from core-helpers.md) ──────────────────────
SF_BLUE     = RGBColor(0x29, 0xB5, 0xE8)
SF_MID_BLUE = RGBColor(0x11, 0x56, 0x7F)
SF_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
SF_DARK_TEXT= RGBColor(0x26, 0x26, 0x26)
SF_BODY_GREY= RGBColor(0x5B, 0x5B, 0x5B)
SF_LIGHT_BG = RGBColor(0xF5, 0xF5, 0xF5)
SF_TEAL     = RGBColor(0x75, 0xCD, 0xD7)
SF_LIGHT_BLUE = RGBColor(0xE8, 0xF4, 0xFD)
SF_LIGHT_ROW  = RGBColor(0xF8, 0xFA, 0xFB)
SF_TABLE_GREY = RGBColor(0x71, 0x71, 0x71)
SF_RED      = RGBColor(0xE7, 0x4C, 0x3C)
SF_AMBER    = RGBColor(0xF5, 0xA6, 0x23)
SF_GREEN    = RGBColor(0x2E, 0xCC, 0x71)
SF_COPYRIGHT= RGBColor(0x92, 0x92, 0x92)
SF_PAGE_NUM = RGBColor(0x91, 0x91, 0x91)
COPYRIGHT   = "\u00a9 2026 Snowflake Inc. All Rights Reserved"

# ── Geometry (from core-template.md) ─────────────────────────────────────────
SLIDE_W     = Inches(10)
SLIDE_H     = Inches(5.625)
PAD_LEFT    = Inches(0.396)
TITLE_TOP   = Inches(0.302)
SUB_TOP     = Inches(0.583)
CONTENT_TOP = Inches(1.0)
FOOTER_TOP  = Inches(5.323)
SAFE_BOTTOM = Inches(5.104)
CONTENT_W   = Inches(9.125)
EDGE_L, EDGE_T, EDGE_W, EDGE_H = Inches(0), Inches(0.375), Inches(0.042), Inches(0.396)

# ── Helpers (copy add_rect, set_shape_text, add_text, etc. from core-helpers) ─
# [paste helpers here]

# ── Template loading ──────────────────────────────────────────────────────────
TEMPLATE = os.path.expanduser("~/.cortex/skills/900-999_utilities/945-render-pptx/snowflake_template.pptx")
prs = Presentation(TEMPLATE)
prs.slide_width = SLIDE_W; prs.slide_height = SLIDE_H

while len(prs.slides) > 0:
    sldId = prs.slides._sldIdLst[0]
    rId = (sldId.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
           or sldId.get('r:id'))
    if rId: prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(sldId)

# ── Slides 1–18 (main deck) ───────────────────────────────────────────────────
# [build each slide here following the structure in this reference]

# ── Slide 19 (appendix divider) ───────────────────────────────────────────────
# [chapter divider]

# ── Slides 20–28 (appendix) ───────────────────────────────────────────────────
# [appendix content slides]

# ── Save ──────────────────────────────────────────────────────────────────────
GDRIVE_DIR = os.path.expanduser("~/Google Drive/My Drive")
SUBFOLDER = f"Accounts/{CUSTOMER_NAME}"
output_dir = os.path.join(GDRIVE_DIR, SUBFOLDER) if os.path.isdir(GDRIVE_DIR) else os.path.expanduser("~/Downloads")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{CUSTOMER_NAME}_PS_Proposal_{MONTH_YEAR}.pptx")
prs.save(output_path)
print(f"✅ SAVED: {output_path}")
```

---

## Content Writing Rules

### Always
- Use real, specific content — never "TBD", "Item 1", or placeholder filler
- Ground every claim in what you know about the customer from context, memory, or prior conversation
- Objectives must be measurable — include a concrete success metric
- RACI must have at least one **R** per activity row
- Pricing slide: use `"TBD"` if investment is not confirmed; never invent dollar amounts

### Slide Titles
- Content slides: Title Case (NOT all caps) — e.g., `"Engagement Objectives and Success Criteria"`
- This is the 2026 Snowflake brand standard for content slide titles

### Workstream Naming
- Use consistent WS numbering: WS1, WS2, WS3... or WS-A, WS-B... for partner workstreams
- Workstream names should be action-oriented: `"FinOps Command Center"` not `"Monitoring"`

### Team slide
- Always use real names when known (from memory/Glean context)
- If SA is not yet staffed: `"[TBD] · Solution Architect"` with role description from the job reqs

---

## Conditional Slide Swaps by Engagement Type

### Slide 4 variants:

**FinOps / Cost Optimization:**
```
Title: "FinOps Value Summary"
Subtitle: "Financial opportunity from [Customer]'s Value Engineering analysis"
Pattern: 3 large KPIs + detailed savings breakdown table
KPIs: Savings potential / % of spend / Workstream count
Table: WS name | Savings estimate | Difficulty | Timeline | Executor
```

**Architecture / Platform Build:**
```
Title: "Platform Maturity & Investment Case"
Subtitle: "Where [Customer] is today and what this engagement unlocks"
Pattern: Maturity spectrum (3-stage visual) + business value table
```

**Governance / Data Security:**
```
Title: "Risk Reduction & Compliance Value"
Subtitle: "What unmanaged governance risk costs vs. the investment to fix it"
Pattern: Risk matrix + 3 KPIs (exposed data/tables/users) + remediation table
```

**AI / ML / Cortex:**
```
Title: "AI Use Case Pipeline & Business Impact"
Subtitle: "Qualified use cases and their estimated business value"
Pattern: Use case table (use case | EACV | stage | timeline) + 3 KPIs
```

---

## Quality Checklist (run before finalizing)

- [ ] Cover title ≤ 50 characters total
- [ ] Agenda has 6–7 items matching the actual deck sections
- [ ] Executive Summary KPIs are grounded in real customer data
- [ ] At least 50% of content slides use a visual pattern (not bullets only)
- [ ] Timeline Gantt bars don't exceed stated engagement duration
- [ ] RACI has at least one R per activity, no row is entirely I/C
- [ ] Pricing slide uses TBD if numbers are not confirmed
- [ ] Next Steps are action-oriented verbs (not nouns)
- [ ] Thank You slide includes real team names and emails
- [ ] All 28 slides saved and file opens without errors in PowerPoint
