---
name: slide-generator-proposal
description: "Create professional Snowflake Services Delivery Proposal PowerPoint decks using the official ACQ Proposal Template. Use for: creating proposals, building delivery proposals, generating customer proposal decks, services proposals, fast track proposals, engagement proposals. Triggers: proposal, delivery proposal, services proposal, create proposal, build proposal deck, customer proposal, fast track proposal, engagement proposal, ACQ proposal."
---

# Snowflake Services Delivery Proposal Generator

Generate professional Services Delivery Proposal PowerPoint presentations using the official Snowflake ACQ Proposal Template with native layouts, Snowflake branding, and prescriptive proposal structure.

## Relationship to Slide Generator

This skill is a **proposal-specific wrapper** around the `slide-generator` skill. It uses the same `generate_slides.py` engine, all 44 slide types, theme-native architecture, and visual capabilities documented in the slide-generator SKILL.md. **Refer to the slide-generator skill for the full JSON schema reference, slide type documentation, and visual design notes.**

The key differences are:
1. **Prescriptive proposal structure** — follows the ACQ Proposal Template slide order and content patterns
2. **Proposal template as reference** — the template at `/Users/michaelkelly/CoCo/Proposal/ACQ - PROPOSAL TEMPLATE.pptx` defines the expected output format
3. **Proposal-specific content guidance** — each slide has specific content expectations for Services Delivery proposals

## How It Works

1. Uses the same `generate_slides.py` engine from the `slide-generator` skill
2. Follows the ACQ Proposal Template structure as prescriptive output guidance
3. All slides render using the Snowflake `.pptx` template (branding, logos, fonts, copyright footer)
4. Generates a complete proposal deck with the correct slide order, content types, and formatting

## Proposal Template Reference

The official ACQ Proposal Template (`ACQ - PROPOSAL TEMPLATE.pptx`) defines a **16-slide Services Delivery Proposal** with the following prescriptive structure. This is the target output format — all generated proposals should follow this structure.

### Template Slide Structure (Prescriptive Order)

| # | Slide Purpose | Slide Generator Type | Template Layout Reference |
|---|--------------|---------------------|--------------------------|
| 1 | **Title / Cover** | `title` | Cyan background, large title, customer name as subtitle, date |
| 2 | **Executive Summary** | `executive_summary` | Two-panel: left (Customer Overview + Engagement Goals) + right (engagement scope areas with icons) |
| 3 | **Engagement Outcomes & Success Criteria** | `outcomes_criteria` | Paired roundRect shapes (gray outcome → cyan criteria) with arrow connectors between them |
| 4 | **Engagement Approach** | `engagement_approach` | Three-column phased layout with colored headers, activity areas, and outcome footer bars |
| 5 | **High Level Timeline (Visual)** | `proposal_timeline` or custom | Visual swim-lane timeline showing roles (ASE, SA), phases, and duration blocks |
| 6 | **High Level Timeline (Gantt)** | `gantt_timeline` | Detailed Gantt with milestone groups, program areas, week columns, colored bars, and milestone markers |
| 7-9 | **Milestone Detail Slides** (one per milestone) | `milestone_detail` | Colored accent bar + duration badge top-right + outcome subtitle + Area/Activities/Deliverables/Hours table |
| 10 | **Delivery Assumptions** | `assumptions_split` | Four-quadrant split layout: dark/light alternating backgrounds with assumption categories |
| 11 | **Customer Responsibilities** | `customer_responsibilities` | Table with advisory footer banner bar at bottom |
| 12 | **Governance Cadence** | `governance_table` | Governance cadence table with alternating row backgrounds |
| 13 | **RACI** | `raci_table` | RACI matrix with colored R/A/C/I markers, section headers, and circle legend |
| 14 | **Pricing / Resource Estimates** | `pricing_table` | Role / Responsibilities / Hours / Rate / Price table with total footer bar |
| 15 | **Risks & Mitigations** | `risk_table` | Risk table with severity-colored impact column (High=red, Medium=orange, Low=green) |
| 16 | **Next Steps** | `next_steps_proposal` | Numbered step cards with colored accent bars, description text, and "Our Goal" sections |

## Workflow

### Step 1: Gather Proposal Requirements

Ask the user for:
1. **Customer name**
2. **Engagement type** — e.g., Fast Track, Standard Delivery, Custom
3. **Engagement duration** — total weeks/months
4. **Milestones** — names and durations (e.g., "Foundational Setup & Initial Data Ingestion — 5 weeks")
5. **Workstreams / Scope areas** — what Snowflake will help with (e.g., Data Onboarding, Consumption Activation, Architecture Foundations)
6. **Roles & pricing** — SA hours/rate, SDM hours/rate, ASE (complimentary), total fees
7. **Any existing notes, scoping documents, or SOW content** to pull from

### Step 2: Build Proposal Content

Using the gathered requirements, construct the JSON for all 16 slides following the prescriptive structure above. Apply these content guidelines for each slide:

#### Slide 1: Title
```json
{
  "type": "title",
  "title": "Services Delivery Proposal",
  "subtitle": "[CUSTOMER NAME]",
  "date": "CONFIDENTIAL  |  [Month Year]"
}
```

#### Slide 2: Executive Summary
Use `executive_summary` type. Two-panel layout:
- **Left panel — Customer Overview**: 1-2 paragraphs of customer background and business context
- **Left panel — Engagement Goals**: Overarching goals of the program (NOT outcomes — goals describe what we aim to address)
- **Right panel — Engagement Scope Areas**: 2-4 workstream cards with icons describing what Snowflake Services Delivery will focus on

Content guidance from template:
- "Customer Overview" = customer background and high-level business overview
- "Engagement Goals" = overarching goals of the program we are about to address — this should NOT include outcomes
- Right side = "Overview of engagement areas of scope and what Snowflake Services Delivery will be focused on"

Workstream examples from template:
- **Architecture Foundations & Security**: Account Set Up, RBAC / Security, Table Structure & Virtual Warehouse, Horizon Governance Guidance
- **Data Onboarding**: Sources: X,Y,Z / # Objects / Ingestion Patterns
- **Consumption Activation**: Data Transformation Advisory, Semantic Layer to support X,Y,Z

#### Slide 3: Engagement Outcomes & Success Criteria
Use `outcomes_criteria` type with paired roundRect shapes:
```json
{
  "type": "outcomes_criteria",
  "title": "Engagement Outcomes & Success Criteria",
  "left_label": "Outcomes",
  "right_label": "Success Criteria",
  "pairs": [
    {"outcome": "Snowflake is configured securely and consistently", "criteria": "Core environment, access controls, and governance are in place"},
    {"outcome": "High-value data is accessible in Snowflake", "criteria": "Initial data sources are onboarded, validated, and queryable"},
    {"outcome": "Teams can begin generating insights", "criteria": "At least one analytics/DS/AI pathway is connected"},
    {"outcome": "Internal teams gain knowledge and confidence", "criteria": "Reusable patterns and examples are delivered"},
    {"outcome": "Organization has clarity on next steps", "criteria": "Prioritized roadmap and readiness assessment reviewed"}
  ]
}
```

#### Slide 4: Engagement Approach
Use `engagement_approach` type. Three phases (columns):
- **Phase 1: Foundational Discovery & Roadmap** — "Align on what matters most, confirm readiness, establish a clear execution path"
- **Phase 2: Guided Implementation & Hands-On Enablement** — "Enable priority data and insights while building team confidence and capability"
- **Phase 3: Tracking, Alignment & Future Roadmapping** — "Maintain momentum, reduce risk, ensure consistent alignment to outcomes"

Each phase has:
- Colored header bar with phase name
- Description paragraph
- "Activity Areas:" label followed by arrow-bulleted activities
- Footer bar with outcome statement

#### Slide 5: High Level Timeline (Visual Swim-Lane)
Use `proposal_timeline` type for a visual swim-lane showing:
- **Evaluation → Contracting → Onboarding & Enablement** flow across top
- Role swim lanes: Activation Solution Engineer, Solutions Architect
- Phase blocks with duration labels (e.g., "5 WEEKS", "4 WEEKS", "3 WEEKS")
- Workstream blocks: Data Onboarding, Consumption Activation, Operational Readiness

#### Slide 6: High Level Timeline (Gantt)
Use `gantt_timeline` type with:
- Week-numbered columns (1 through total weeks)
- Milestone groups matching the defined milestones
- Program area rows within each milestone
- Colored arrow bars showing duration
- Orange triangle milestone markers at key checkpoints
- Spanning "Program Management / Tracking" bar across full duration
- Footnote for ASE note (if applicable)

#### Slides 7-9: Milestone Detail Slides
Use `milestone_detail` type for each milestone:
```json
{
  "type": "milestone_detail",
  "title": "Milestone 1, Foundational Setup & Initial Data Ingestion",
  "milestone_color": "#29B5E8",
  "duration": "5 Weeks",
  "outcome": "Outcome: Snowflake environment is production-ready with initial data flows operational",
  "columns": ["Area", "Activities", "Deliverables", "Hours"],
  "col_widths": [0.18, 0.37, 0.30, 0.15],
  "rows": [
    ["Architecture Foundations", "Account review, RBAC guidance, VWH strategy", "Architecture blueprint doc", "40"],
    ["Data Onboarding", "Source analysis, ingestion patterns", "Validated data pipelines", "60"]
  ]
}
```
- Use different `milestone_color` per milestone: accent1 (#29B5E8), accent5 (#7D44CF), accent6 (#D45B90)

#### Slide 10: Delivery Assumptions
Use `assumptions_split` type with 4 quadrants (dark/light alternating):
```json
{
  "type": "assumptions_split",
  "title": "Delivery Assumptions",
  "quadrants": [
    {"heading": "Engagement Assumptions", "items": ["Fast Track is hands-on enablement", "..."]},
    {"heading": "Environment & Execution", "items": ["Work in dev/validation only", "..."]},
    {"heading": "Scope Assumptions", "items": ["Single business priority focus", "..."]},
    {"heading": "Timeline Assumptions", "items": ["N-week milestone-based cadence", "..."]}
  ]
}
```
Quadrants render as: top-left=dark, top-right=light, bottom-left=light, bottom-right=dark

#### Slide 11: Customer Responsibilities
Use `customer_responsibilities` type:
```json
{
  "type": "customer_responsibilities",
  "title": "Customer Responsibilities",
  "columns": ["Category", "Responsibilities", "Details", "Owner"],
  "rows": [
    ["Resource Commitments", "Dedicated personnel", "Named project sponsor + technical leads", "Customer"],
    ["Data & Access", "Source provisioning", "Timely data access and credentials", "Customer"]
  ],
  "footer": "Snowflake provides hands-on guidance and enablement, but does not replace customer ownership of production systems."
}
```

#### Slide 12: Governance Cadence
Use `governance_table` type:
```json
{
  "type": "governance_table",
  "title": "Governance Cadence",
  "columns": ["Cadence", "Meeting", "Attendees", "Purpose", "Owner"],
  "rows": [
    ["Bi-Weekly", "Steering Committee", "Exec sponsors, SDM", "Strategic alignment & escalations", "SDM"],
    ["Weekly", "Technical Review", "SA, ASE, Tech leads", "Technical progress & decisions", "SA"],
    ["Daily", "Standup", "Delivery team", "Daily coordination", "ASE"],
    ["Weekly", "Delivery Review", "Full team", "Progress, risks, actions", "SDM"]
  ]
}
```

#### Slide 13: RACI Matrix
Use `raci_table` type:
```json
{
  "type": "raci_table",
  "title": "RACI Matrix",
  "badge": "Engagement RACI",
  "columns": ["Scope Area / Activity", "Snowflake", "Customer", "SI Partner"],
  "rows": [
    {"values": ["Program Management", "", "", ""], "is_section": true},
    {"values": ["Project Planning & Coordination", "R", "A", "C"]},
    {"values": ["Discovery & Architecture", "", "", ""], "is_section": true},
    {"values": ["Architecture Review & Guidance", "R", "C", "I"]},
    {"values": ["RBAC & Security Design", "R", "A", "C"]}
  ]
}
```
Use `is_section: true` for group header rows. RACI values auto-colored: R=cyan, A=navy, C=teal, I=gray

#### Slide 14: Resource Estimates & Proposed Fees
Use `pricing_table` type with:
- **Subtitle**: Team description paragraph
- **Columns**: Role | Responsibilities | Hours* | Rate | Price (USD)
- Standard roles: Activation Solutions Engineer (complimentary), Solutions Architect, Services Delivery Manager
- **Total footer bar** with engagement total
- **Footnote**: "*Hours are estimated and may vary based on scope"

#### Slide 15: Risks & Mitigations
Use `risk_table` type:
```json
{
  "type": "risk_table",
  "title": "Risks & Mitigations",
  "badge": "Risk Management",
  "columns": ["Risk", "Impact", "Mitigation"],
  "rows": [
    {"values": ["Lack of Customer Resource Availability", "High", "Identify named resources early; schedule working sessions in advance"], "severity": "high"},
    {"values": ["Unclear or Changing Requirements", "Medium", "Formalize scope in SOW; use milestone reviews for alignment"], "severity": "medium"},
    {"values": ["Technical Roadblocks", "Medium", "Pre-engagement environment validation; escalation paths"], "severity": "medium"},
    {"values": ["Slow Adoption of Recommendations", "Medium", "Hands-on enablement; documentation; paired working sessions"], "severity": "medium"},
    {"values": ["Scope Changes / Increases", "High", "Change control process; SOW amendment for material changes"], "severity": "high"},
    {"values": ["Underestimation of Effort", "Medium", "Buffer hours; milestone-based reassessment"], "severity": "medium"}
  ]
}
```

#### Slide 16: Next Steps
Use `next_steps_proposal` type:
```json
{
  "type": "next_steps_proposal",
  "title": "Next Steps",
  "steps": [
    {"number": "1", "title": "Finalize SOW", "description": "Review and finalize the Statement of Work...", "goal": "Guarantee a single, clear agreement on what will be delivered"},
    {"number": "2", "title": "Scoping & Best Practices", "description": "Confirm scope aligns with best practices...", "goal": "Ensure the project is scoped using Snowflake's proven best practices"},
    {"number": "3", "title": "Access & Environment", "description": "Ensure environment access and credentials...", "goal": "Prevent delays by ensuring our team can start securely on day one"},
    {"number": "4", "title": "Team Assignment", "description": "Assign Snowflake and customer resources...", "goal": "Ensure best-prepared experts are aligned for effective execution"},
    {"number": "5", "title": "Kickoff", "description": "Conduct a kickoff to align on goals and plan...", "goal": "Align everyone on goals, roles, and the plan"}
  ]
}
```

### Step 3: Generate Presentation

```bash
python3 ~/.snowflake/cortex/skills/slide-generator/scripts/generate_slides.py \
  --slides-json /path/to/proposal_slides.json \
  --output /path/to/output.pptx
```

Uses the same engine as slide-generator — all slide types, theme colors, and rendering capabilities are shared.

### Step 4: Review & Iterate

After generation, offer to:
- Review and adjust specific slides
- Modify milestone content, pricing, or timeline
- Add/remove slides
- Regenerate with updated content

## Stopping Points

**STOP and ask the user** at these points:
1. After gathering requirements — confirm the proposal outline and content before generating
2. After generation — ask if they want modifications

## Content Tone & Language Guidelines

- **Advisory language for Snowflake activities**: Use "architecture review" not "architecture build", "enablement" not "implementation", "guidance" not "execution"
- **Customer ownership**: Snowflake provides hands-on guidance; the customer owns production systems, data quality, and operational decisions
- **Outcome-focused**: Each milestone should clearly state what the customer achieves
- **Measurable success criteria**: Pair every outcome with concrete, verifiable criteria
- **Collaborative framing**: "We partner with you..." not "We will do..."

## Output

- File: PowerPoint (.pptx) at user-specified location
- Default: `~/Downloads/[CustomerName]_Proposal_YYYYMMDD.pptx`
- Template: 10" x 5.625" (standard Snowflake 16:9)
- All slides use Snowflake template theme compliance

## Snowflake Branded Assets

### Logos (at `assets/logos/`)
- `snowflake-bug-white.png` — White snowflake icon (used on title slides with cyan bg)
- `snowflake-bug-blue.png` — Blue snowflake icon (for white bg slides)
- `snowflake-logo-white.png` — Full white logo + wordmark
- `snowflake-logo-blue.png` — Full blue logo + wordmark

### Icons (at `assets/icons/`)
Use these for executive_summary workstream `icon_file` field:
- `icon-data-stream.png` — Data streaming/ingestion
- `icon-data-share.png` — Data sharing/collaboration
- `icon-database-sync.png` — Database synchronization
- `icon-network-graph.png` — Network/architecture
- `icon-security-lock.png` — Security/RBAC
- `icon-snowflake-dev.png` — Snowflake development
- `icon-code-json.png` — Code/API
- `icon-containers-deploy.png` — Containers/deployment
- `icon-data-bucket.png` — Data storage
- `icon-data-layers-geo.png` — Data layers/geospatial
- `icon-grid-sync.png` — Grid synchronization
- `icon-monitor-screen.png` — Monitoring/dashboards
- `icon-search-hexagon.png` — Search/discovery
- `icon-arctic-crown.png` — Arctic/premium
- `icon-marketplace-logo.png` — Marketplace
- `icon-snowpark-container.png` — Snowpark/containers

## Proposal Template Reference File

`/Users/michaelkelly/CoCo/Proposal/ACQ - PROPOSAL TEMPLATE.pptx`

This 16-slide template contains sample content for a "Fast Track" engagement. Use it as the definitive reference for slide structure, content placement, and formatting expectations. The template slides carry "Sample Format - Please Update To Your Engagement Specifics" banners — all generated content should replace these placeholders with real engagement data.

## Value Assessment Deck Pattern (DIY vs. PS Business Case)

Use this pattern when building a **Services Delivery Value Assessment** deck — a business case comparing DIY migration vs. Snowflake Professional Services. This is NOT a proposal (no SOW, no milestones) — it's a value justification deck for executive stakeholders.

**IMPORTANT**: This deck uses a **custom python-pptx layout** (NOT the slide-generator JSON engine). The layout is defined in a standalone Python build script with helper functions for consistent shapes, tables, metrics, and phase circles. Generate the deck by creating a python-pptx script following the patterns below, then executing it.

### When to Use
- Customer is evaluating DIY vs. PS for a migration or platform build
- Need to demonstrate ROI of PS engagement vs. internal execution
- Executive-level business case with cost comparisons, risk analysis, and savings projections
- Dual-scope presentations (e.g., Main Cluster vs. All 3 Clusters)

### Build Approach

Generate a standalone Python script using `python-pptx` (NOT the slide-generator JSON engine). The script uses:
- Blank slide layout (`prs.slide_layouts[6]`)
- Slide dimensions: `12192000 x 6858000` EMU (standard 16:9)
- Helper functions for all reusable elements (see below)
- Snowflake brand colors defined as constants

### Snowflake Brand Color Constants

```python
DARK_BLUE = RGBColor(0x11, 0x56, 0x7F)   # Snowflake navy/dark teal (accent2)
SNOW_BLUE = RGBColor(0x29, 0xB5, 0xE8)   # Snowflake cyan (accent1, primary)
ORANGE    = RGBColor(0xFF, 0x9F, 0x36)    # Snowflake orange (accent4)
TEAL      = RGBColor(0x11, 0x56, 0x7F)    # Same as DARK_BLUE (accent2)
GREEN     = RGBColor(0x71, 0xD3, 0xDC)    # Snowflake light teal (accent3)
PURPLE    = RGBColor(0x7D, 0x44, 0xCF)    # Snowflake purple (accent5)
RED       = RGBColor(0xD4, 0x5B, 0x90)    # Snowflake pink (accent6)
GRAY      = RGBColor(0x5B, 0x5B, 0x5B)    # Body text
D_GRAY    = RGBColor(0x33, 0x33, 0x33)    # Dark text
BLACK     = RGBColor(0x00, 0x00, 0x00)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
L_GRAY    = RGBColor(0xF2, 0xF2, 0xF2)   # Card/metric backgrounds
VL_BLUE   = RGBColor(0xE8, 0xF4, 0xFD)   # Very light blue tint
```

Tinted fill colors for workstream backgrounds:
- Light teal tint (WS1/gold layer): `RGBColor(0xE0, 0xF5, 0xF7)`
- Light blue tint (WS2/code conversion): `RGBColor(0xD4, 0xEC, 0xF5)`
- Phase circle week text: `RGBColor(0xA8, 0xE6, 0xF0)`

### Helper Functions

The build script uses these reusable helpers (all measurements in EMU):

| Function | Purpose | Key Details |
|----------|---------|-------------|
| `hbar(slide, title)` | Full-width DARK_BLUE header bar with white title text | Top of slide, Pt(26) bold Arial |
| `ftr(slide)` | Footer with "© 2026 Snowflake Inc." | Bottom of slide, Pt(9) gray |
| `tx(slide, l, t, w, h, text, sz, bold, color, italic, align)` | Single text box | Word wrap enabled, returns textbox |
| `multi_tx(slide, l, t, w, h, lines, sz, color, bold, spacing, bullet)` | Multi-line bulleted text | "• " prefix per line by default |
| `metric(slide, l, t, w, h, val, label, vc)` | KPI metric card | Rounded rect, L_GRAY fill, large value + small label |
| `stbl(slide, l, t, w, data, col_ws, row_h)` | Styled table | DARK_BLUE header row, alternating gray rows |
| `pillar_box(slide, l, t, w, h, accent_color, tag, title, stat, stat_label, bullets)` | Executive summary pillar card | White card with accent top bar, tag, title, big stat, bullets |
| `phase_circle(slide, l, t, w, h, num, name, weeks, color)` | Delivery phase circle | Oval with phase number, name, and week range |

### Prescriptive Slide Structure (17 slides)

| # | Slide Purpose | Layout Pattern | Content Notes |
|---|--------------|----------------|---------------|
| 1 | **Title / Cover** | Full-width DARK_BLUE bar (y=800000, h=4800000). Title above bar in BLACK, subtitle in WHITE, tagline in SNOW_BLUE, sub-tagline in tinted blue | Customer name, "Redshift to Snowflake Migration", tagline, date |
| 2 | **Executive Summary** | `hbar` + 3x `pillar_box` (equal width, gap=280000) + conclusion text in TEAL | Pillar 1=SNOW_BLUE, Pillar 2=GREEN, Pillar 3=ORANGE. Each has tag, title, big stat, bullets |
| 3 | **Gold Layer Advantage** | `hbar` + 2 rounded-rect workstream lanes (WS1=teal tint, WS2=blue tint) + status badges + KEY BUSINESS VALUE bullet list | WS1 shows "DATA SHARING LIVE" badge in GREEN. WS2 shows "FULL MIGRATION COMPLETE" in DARK_BLUE |
| 4-5 | **Migration Overview** (×2) | `hbar` + 5x `metric` cards in a row + two-column bullets ("Current Stack" / "Migration Scope") | Duplicate for each scope option. Use GREEN for DMVA metric, ORANGE for SPs metric |
| 6 | **Resource Constraints** | `hbar` + `stbl` for active workstreams + 3x `metric` cards at bottom | RED=DIY hours, GREEN=PS hours, SNOW_BLUE=freed hours |
| 7-8 | **Why PS Accelerates** (×2) | Title at top (no hbar) + subtitle + `stbl` with phase comparison + bold TEAL conclusion | Duplicate for each scope. Table: Phase / DIY / PS / Delta columns |
| 9 | **SP Challenge** | `hbar` + two side-by-side `stbl` (one per scope) + bold TEAL conclusion | Conversion speed, effort, success rate, team size, calendar time, rework |
| 10 | **What PS Brings** | Title at top + 3x tall rounded-rect cards (L_GRAY fill) with tag, title, bullet list | Card 1=CoCo (SNOW_BLUE tag), Card 2=DMVA (ORANGE tag), Card 3=SnowConvert (SNOW_BLUE tag) |
| 11-12 | **PS Delivery Approach** (×2) | Title at top + 6x `phase_circle` in a row + "Two Parallel Workstreams" `stbl` + pricing `stbl` | Duplicate for each scope. Show role/rate/hours/cost breakdown |
| 13-14 | **DIY Costs & Risks** (×2) | Title at top + two-column: left=cost bullet list, right=risk `stbl` | Duplicate for each scope |
| 15-16 | **Hard & Soft Savings** (×2) | `hbar` + Hard savings `stbl` + Soft savings `stbl` + 3x `metric` cards (right side): total/hard/soft | Duplicate for each scope. Total=GREEN, Hard=SNOW_BLUE, Soft=PURPLE |
| 17 | **Risk Comparison** | Title at top + wide `stbl` | Columns: Risk Category / DIY / With PS |

### Key Design Patterns

**Dual-scope slides**: For any slide where numbers differ between scope options (pricing, acceleration, costs, savings), create two versions — one per scope. Keep shared content slides (exec summary, what PS brings, resource constraints, risk comparison) as single slides.

**Color conventions**:
- Headers/dark elements: `DARK_BLUE` (#11567F)
- Primary accent/metrics: `SNOW_BLUE` (#29B5E8)
- Positive/savings/gold layer: `GREEN` (#71D3DC, Snowflake light teal)
- Warnings/PS-exclusive: `ORANGE` (#FF9F36)
- Soft savings/secondary: `PURPLE` (#7D44CF)
- Negative/DIY cost: `RED` (#D45B90, Snowflake pink)
- Body text: `GRAY` (#5B5B5B)
- Conclusion/callout text: `TEAL` (#11567F) bold

**Table styling**: Header row = DARK_BLUE fill + WHITE text. Alternating rows = L_GRAY. All text = Arial.

**Metric cards**: Rounded rectangle, L_GRAY fill, no border. Large value (Pt 28 bold) + small label (Pt 12 gray).

### Reference Implementation

Build script: `/Users/michaelkelly/CoCo/Accounts/Rocket/build_value_deck.py`
Output: `/Users/michaelkelly/CoCo/Accounts/Rocket/Rocket Mortgage Snowflake Services Delivery Value Assessment.pptx`

## Google Drive Output

After generating the PPTX locally, upload and convert it to Google Slides in Drive.

### Folder structure
All outputs go to: **SnowWork → Accounts → {AccountName} → Proposals**

For a new account, create the folder chain:
1. `mcp_google-worksp_create_drive_folder` name="{AccountName}", parent_id=`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck` → `{account_folder_id}`
2. `mcp_google-worksp_create_drive_folder` name="Proposals", parent_id=`{account_folder_id}` → `{proposals_folder_id}`

### Upload command
```bash
cd /Users/michaelkelly/.snowflake/cortex/.mcp-servers/google-workspace && \
./node /Users/michaelkelly/CoCo/Scripts/upload_to_gslides.mjs \
  "/path/to/output.pptx" "{Title}" "{proposals_folder_id}"
```
Returns JSON: `{"id":"...","name":"...","url":"https://docs.google.com/presentation/d/.../edit"}`

### Bullet point formatting
When writing any email draft body (mcp_google-worksp_create_draft), always indent bullet points with 4 spaces:
    • Like this item
    • And this item
Never use flush-left `• item` format. For Google Docs content (mcp_google-worksp_create_document), use `- item` markdown lists which auto-convert to properly indented bullets.
