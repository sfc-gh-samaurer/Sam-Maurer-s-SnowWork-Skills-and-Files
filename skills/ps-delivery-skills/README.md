# Snowflake PS Services Delivery Skills Suite

A collection of Cortex Code (CoCo) skills that automate the creation of Snowflake Professional Services delivery artifacts — from initial account research through proposal delivery and SOW generation.

## Quick Install

```bash
# 1. Unzip to a permanent location
unzip ps-delivery-skills.zip -d ~/CoCo/Skills

# 2. Symlink each skill into your Cortex Code skills directory
cd ~/.snowflake/cortex/skills
for skill in ~/CoCo/Skills/*/; do
  ln -sf "$skill" "$(basename $skill)"
done

# 3. Restart Cortex Code (or start a new session)
```

After installation, skills are automatically available in any CoCo session. Just use the trigger phrases listed below.

## Prerequisites

- **Cortex Code (CoCo)** installed and configured
- **Python 3.11+** with `openpyxl` and `matplotlib` (for Excel and diagram generation)
- **python-pptx** (used by slide-generator and slide-generator-proposal)
- **python-docx** (used by sow-generator)

Install Python dependencies:
```bash
pip3 install openpyxl matplotlib python-pptx python-docx
```

The `slide-generator` and `sow-generator` skills include `pyproject.toml` files and can alternatively be run via `uv`:
```bash
uv run --project ~/.snowflake/cortex/skills/slide-generator python ...
```

## Skills Reference

| # | Skill | What It Does | Output | How to Trigger |
|---|-------|-------------|--------|----------------|
| 1 | **account-background-refresh-prep** | Prepares 2x2 account meeting readout documents. Aggregates data from Salesforce, Glean, Google Calendar, Slack, and email to produce a briefing covering: account team, stakeholders, recent interactions, SD play, deal metrics, risks, and meeting questions. | Word (.docx) | *"prep a 2x2 for [Customer]"*, *"account background"*, *"meeting prep"*, *"deal review"* |
| 2 | **bronze-layer-planner** | Inventories source systems, assigns Snowflake ingestion patterns (Openflow CDC, Snowpipe, API-to-S3, Marketplace, Cortex AI, etc.), estimates effort per activity type. Generates a 5-sheet Excel workbook. | Excel (.xlsx) | *"create a bronze layer plan"*, *"source inventory"*, *"ingestion patterns"*, *"data onboarding plan"* |
| 3 | **ingestion-to-consumption-mapper** | Maps source systems through Bronze, Silver, and Gold layers of the Snowflake Medallion Architecture. Generates dot matrices showing which sources feed which domains, with phase assignments and reverse mappings. | Excel (.xlsx) — 7 sheets | *"map ingestion to consumption"*, *"medallion architecture"*, *"data lineage"*, *"bronze silver gold"* |
| 4 | **implementation-roadmap-builder** | Breaks each implementation phase into detailed tasks organized by subsection (Discovery, Ingestion, Transformation, UAT, Consumption/AI). Includes a consolidated Dependencies & Risks register with severity ratings. | Excel (.xlsx) | *"build an implementation roadmap"*, *"project plan"*, *"task breakdown"*, *"phased roadmap"* |
| 5 | **scoping-questions-generator** | Generates categorized scoping questions (executive, environment, source systems, transformation, AI, people, governance, timeline, commercial), pre-call document requests, and scope boundary definitions for SOW alignment. | Excel (.xlsx) — 3 sheets | *"generate scoping questions"*, *"prep for scoping call"*, *"fixed bid scoping"* |
| 6 | **architecture-diagram-generator** | Creates future state architecture diagrams showing data flow from source systems through Bronze/Silver/Gold layers to AI & Consumption. Phase-colored, with governance overlay. | SVG (editable) + PNG (high-fidelity) | *"create an architecture diagram"*, *"future state diagram"*, *"platform diagram"* |
| 7 | **slide-generator** | General-purpose PowerPoint engine with 34 slide types (tables, Gantt timelines, KPI dashboards, process flows, org charts, Venn diagrams, hub-spoke, pyramids, charts, etc.) using Snowflake template branding. | PowerPoint (.pptx) | *"create a presentation"*, *"make slides"*, *"build a deck"* |
| 8 | **slide-generator-proposal** | Generates 16-slide Services Delivery Proposal decks following the ACQ Proposal Template structure: Title, Exec Summary, Outcomes, Approach, Timeline, Milestone Details, Assumptions, Customer Responsibilities, Governance, RACI, Pricing, Risks, Next Steps. | PowerPoint (.pptx) | *"create a proposal for [Customer]"*, *"build a proposal deck"*, *"services proposal"* |
| 9 | **sow-generator** | Generates Statement of Work documents matching the official Snowflake PS template specification. Supports Fixed Fee and T&M engagements with structured JSON, markdown, or conversational input. | Word (.docx) | *"generate a SOW"*, *"create a statement of work"* |

## Recommended Workflow

For a new customer engagement, use the skills in this order:

```
Step 1:  account-background-refresh-prep    Understand the account
            │
Step 2:  bronze-layer-planner               Inventory sources & estimate effort
            │
Step 3:  ingestion-to-consumption-mapper    Map the full data flow (B → S → G)
            │
Step 4:  implementation-roadmap-builder     Break into phased tasks & risks
            │
Step 5:  scoping-questions-generator        Prepare for scoping call
            │
Step 6:  architecture-diagram-generator     Visualize the future state
            │
Step 7:  slide-generator-proposal           Build the proposal deck
            │
Step 8:  sow-generator                      Generate the Statement of Work
```

Each skill can also be used independently. Skills reference each other's outputs when available (e.g., the roadmap builder can read from the bronze layer plan).

## Skill Details

### 1. account-background-refresh-prep
Searches Salesforce, Glean (presentations/slides/docs), Google Calendar, Slack, and email to compile a comprehensive account readout. Output sections: account team, customer stakeholders, recent interactions, follow-up actions, Services Delivery play analysis, timelines, POC status, deal metrics, risks, and questions for your meeting.

### 2. bronze-layer-planner
**Excel sheets produced:**
- Bronze Implementation Plan (per-source detail with effort by activity)
- Summary by Source (sortable overview)
- Effort by Activity Type (pivot view)
- Ingestion Pattern Reference (customer-facing education)
- Discovery Questions (per-source validation questions)

**Ingestion patterns covered:** Openflow CDC, Openflow JDBC, Snowpipe, API-to-S3-to-Snowpipe, Marketplace/Data Share, Cortex AI (AI_PARSE_DOCUMENT), Snowpark Python, EDI X12 Parser, BCP/Legacy Export, Reverse-Engineer SQL + dbt Migration, Native SF Migration.

### 3. ingestion-to-consumption-mapper
**Excel sheets produced:**
- Information (summary, phase legend)
- Source Data Ingestion (Bronze layer inventory)
- Curated Data (Silver domains with source mappings)
- Consume (Gold domains with Silver sources)
- Source-to-Domain Mapping (dot matrix)
- Gold-to-Source Mapping (reverse traceability)
- Curated-to-Source Mapping (reverse traceability)

### 4. implementation-roadmap-builder
**Excel sheets produced:**
- Summary Roadmap (executive one-pager)
- Per-phase detail sheets with tasks organized into: Discovery/Planning/Design, Data Ingestion, Transformation/Modeling/Orchestration, UAT/Testing, Consumption/BI/AI
- Dependencies & Risks register (severity-coded: High/Medium/Low)

### 5. scoping-questions-generator
**Excel sheets produced:**
- Scoping Questions (86+ categorized, priority-coded)
- Pre-Call Document Requests (artifacts to request from customer)
- Scope Boundaries (In-Scope / Out-of-Scope / Assumptions for SOW)

### 6. architecture-diagram-generator
**Outputs:**
- SVG: Editable in Figma, Illustrator, Inkscape (1920x1080, dark theme)
- PNG: High-fidelity raster (3600x2025 pixels, 150 DPI)
- Python script: Rerunnable matplotlib generator

**Layout:** Source Systems (by phase) → Bronze → Silver (by category) → Gold (by category) → AI & Consumption, with Governance and Timeline bars.

### 7. slide-generator
**34 slide types:** title, section, agenda, content, two_column, cards, table, timeline, phase_detail, quote, steps, closing, venn, framed_two_column, gradient_section, process_flow, kpi_dashboard, quadrant, hub_spoke, pyramid, icon_grid, horizontal_bars, image, donut_chart, bar_chart, org_chart, watermark, connector_diagram, grouped_shapes, service_options, category_list, executive_summary, engagement_approach, gantt_timeline.

Uses the official Snowflake PowerPoint template with native layouts, logos, and theme colors.

### 8. slide-generator-proposal
**16-slide structure:** Title, Executive Summary, Outcomes & Success Criteria, Engagement Approach, High Level Timeline (Gantt), Milestone Detail slides (one per milestone), Delivery Assumptions, Customer Responsibilities, Governance Cadence, RACI Matrix, Pricing/Resource Estimates, Risks & Mitigations, Next Steps.

References the ACQ Proposal Template. Requires the `slide-generator` skill (uses the same engine).

### 9. sow-generator
Generates `.docx` Statement of Work documents. Supports Fixed Fee and T&M engagement types. Accepts input as structured JSON, markdown, or conversational.

## File Structure

```
ps-delivery-skills/
├── README.md
├── account-background-refresh-prep/
│   └── SKILL.md
├── architecture-diagram-generator/
│   └── SKILL.md
├── bronze-layer-planner/
│   └── SKILL.md
├── implementation-roadmap-builder/
│   └── SKILL.md
├── ingestion-to-consumption-mapper/
│   └── SKILL.md
├── scoping-questions-generator/
│   └── SKILL.md
├── slide-generator/
│   ├── SKILL.md
│   ├── pyproject.toml
│   ├── scripts/
│   │   ├── generate_slides.py
│   │   ├── generate_slides_v2.py
│   │   └── generate_slides_v3.py
│   └── assets/
│       ├── snowflake_template.pptx
│       ├── logos/
│       └── icons/
├── slide-generator-proposal/
│   └── SKILL.md
└── sow-generator/
    ├── SKILL.md
    ├── pyproject.toml
    └── scripts/
        └── generate_sow.py
```

## Tips

- Skills work best when you provide context from prior artifacts (e.g., "use the bronze layer plan I already created")
- The slide-generator-proposal skill depends on slide-generator — both must be installed
- You can chain skills in a single session: "create a bronze layer plan, then map ingestion to consumption, then build a roadmap"
- Each skill has built-in stopping points where it will ask for your review before proceeding
- All Excel outputs use consistent formatting: dark blue headers (#11567F), alternating rows, freeze panes, auto-width columns
