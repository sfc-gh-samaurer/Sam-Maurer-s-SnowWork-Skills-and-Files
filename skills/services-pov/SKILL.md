---
name: services-pov
description: "Create customer-ready Services Point of View documents for Snowflake accounts. Queries internal data (Raven, SFDC), analyzes use case pipeline, positions services opportunities, and generates a Snowflake-branded HTML deliverable with roadmap, key activities, and investment details. Use for: services POV, services point of view, services positioning, engagement plan, services proposal, customer services strategy, services roadmap. DO NOT attempt to build services POV documents manually — invoke this skill first."
---

# Services Point of View Generator

## Setup

- Load `references/sql-queries.md` for all Raven/SFDC query templates
- Load `references/pov-template.md` for the markdown document structure
- Load `references/pricing-guidance.md` for investment estimation guardrails

## Prerequisites

- Snowflake connection with `SALES_RAVEN_RO_RL` role (fallback: `SALES_BASIC_RO`)
- Warehouse: Use `SNOWHOUSE` (not AC_WH). Combine `USE WAREHOUSE SNOWHOUSE;` with queries.
- `build_pov_html.py` script for HTML generation (in `scripts/`)
- Output directory for deliverables

## Workflow

### Step 1: Gather Inputs

**Ask user for:**
- Company name (required)
- Output directory (required, default: current directory)
- Opportunity focus area (optional — e.g., "Snowflake Intelligence", "Cortex AI", "Data Engineering modernization")
- Any known context (optional): pain points, strategic priorities, key contacts

Store as working variables: `<COMPANY>`, `<OUTPUT_DIR>`, `<FOCUS_AREA>`.

**⚠️ STOP**: Confirm inputs before proceeding.

### Step 2: Resolve Account & Pull Internal Data

**Goal:** Build comprehensive account picture from Raven/SFDC data.

**2a. Resolve account using `account_finder` skill:**

Invoke the `account_finder` skill with the company name. This returns the full account record including `SALESFORCE_ACCOUNT_ID`, account team, segment, industry, and tier.

If `account_finder` is unavailable, fall back to running **Query 7 — Account Finder** from `references/sql-queries.md`:
```sql
USE ROLE SALES_RAVEN_RO_RL;
USE WAREHOUSE SNOWHOUSE;
```

Store `SALESFORCE_ACCOUNT_ID` for all subsequent queries. If multiple matches, disambiguate with user.

**2b. Run all Raven queries in parallel** (use the resolved account ID):

| Query | Data | Priority |
|-------|------|----------|
| Query 10 | Contract status | Required |
| Query 12 | Active use cases | Required |
| Query 13 | Open pipeline | Required |
| Query 14 | Product revenue (L7D/L30D) | Required |
| Query 15 | Monthly consumption (12mo) | Required |
| Query 19 | AI-generated goals & pain points | Required |
| Query 8 | Firmographics | Recommended |
| Query 11 | Over/under prediction | Recommended |
| Query 16 | Support cases (90d) | Optional |
| Query 17 | Warehouse anomaly detection | Optional |

**2c. Pull all use cases (including lost):**
Run a modified Query 12 that includes ALL statuses (remove the `NOT IN` filter) to capture deployed, in-pursuit, and lost use cases. This is critical for the "Lessons Learned" section.

```sql
SELECT u.use_case_name, u.use_case_acv, u.use_case_stage, u.use_case_status,
  u.decision_date, u.go_live_date
FROM sales.raven.sda_use_case_view AS u
WHERE u.salesforce_account_id = '<ACCOUNT_ID>'
ORDER BY u.use_case_acv DESC NULLS LAST;
```

**2d. Web research (run in parallel with SQL):**
- `"<COMPANY>" annual report revenue employees`
- `"<COMPANY>" data strategy AI cloud`
- `"<COMPANY>" executive team leadership CTO CIO CDO`
- `"<COMPANY>" Snowflake case study OR partnership`

**Web research fallbacks:**
- For private companies, search `"<COMPANY>" Crunchbase funding` or `"<COMPANY>" Pitchbook`
- If `<COMPANY>` is a subsidiary, also search the parent company name
- If minimal results, use industry description from SFDC firmographics (Query 8)

### Step 3: Analyze & Synthesize

**Goal:** Turn raw data into services positioning insights.

**3a. Categorize use cases:**
- **Deployed**: Use cases in Production — these are the foundation
- **Active Pipeline**: Use cases in Discovery, Tech Validation, or Evaluation — these are the services opportunity
- **Lost**: Use cases that were Closed Lost — analyze for patterns (scoping, timing, feature maturity, competitive)

**3b. Identify the opportunity focus area:**
If user didn't specify `<FOCUS_AREA>`, recommend one based on:
- Highest concentration of pipeline EACV
- Customer's stated goals (from Query 19)
- Product revenue trends showing emerging adoption (e.g., Cortex AI functions appearing)
- Lost use case patterns suggesting need for expert guidance

**3c. Calculate key metrics:**
- Total deployed EACV
- Total active pipeline EACV
- Monthly consumption range (from 12-month trend)
- Contract utilization %
- Renewal status and days in stage

**3d. Map services workstreams:**
For each active use case, identify:
- What services activities are needed (design, build, test, enable)
- Dependencies between use cases
- Which can be quick wins vs. multi-week efforts
- How they ladder up to the focus area

### Step 4: Write the Services POV Document

**Goal:** Generate the markdown document using `references/pov-template.md` as the structure.

Write the document to `<OUTPUT_DIR>/<COMPANY>_Services_POV.md` using the template sections. Key guidelines:

- **Executive Summary**: Lead with the business context, state the services opportunity clearly, quantify pipeline at stake, connect to renewal
- **Account Snapshot**: Use exact data from Raven (contract, consumption, account team)
  - Signal column guidance:
    - ✅ = healthy (>50% utilization, consumption growing, renewal active)
    - ⚠️ = attention (30-50% utilization, flat consumption, renewal in early stage)
    - 🔴 = risk (<30% utilization, declining consumption, no active renewal)
- **What Customer is Trying to Do**: Tell the story in phases (foundation → current → aspirational)
- **Tech Stack**: Use SFDC TECH_STACK field + product revenue breakdown
- **Use Case Pipeline**: Three tables — Deployed, Active, Lost with lessons learned
- **Opportunity Focus Section**: Deep dive on the recommended focus area with why-now, what-failed-before, proposed scope
- **Services Roadmap**: 3-phase approach (Foundation/Quick Wins → Expand/Deepen → Production/Enablement) with weekly Gantt-style tables
- **Key Activities**: Workstream tables with Activity, Description, Outcome columns
- **Investment & ROI**: See pricing guidance below
- **Success Criteria**: What success looks like for the customer AND for Snowflake
- **Next Steps**: Action table with Owner and Timeline
- **Appendix**: Leadership context, recent events

**Tone:** Customer-ready but internally grounded. An AE should be able to hand this to a customer executive.

#### Investment Section — Pricing Guardrails

**⚠️ CRITICAL: All estimates are INDICATIVE ONLY and require Pre-Sales Architecture validation before customer-facing use.**

Use ±40% bands when estimating investment. NEVER provide a single-point estimate. Follow guidance in `references/pricing-guidance.md`.

Example format for the Investment table:
```
| Engagement | Duration | Estimated Range* |
|------------|----------|-----------------|
| Phase 1: Foundation | 3-5 weeks | $25K - $50K |
| Phase 2: Expand | 4-6 weeks | $40K - $75K |
| Phase 3: Enablement | 3-5 weeks | $25K - $50K |
| **Total** | **10-16 weeks** | **$90K - $175K** |

*Estimates are indicative and subject to Pre-Sales Architecture review.
Actual investment will depend on scope refinement, resource availability, and engagement complexity.
```

**Sizing heuristics (for range generation only):**
- Advisory engagement: 12-24 hrs/wk SA, plus ~20% SDM overhead
- Quick Win phase: typically 3-5 weeks
- Multi-phase engagement: typically 10-16 weeks total
- Use T-shirt sizing for early positioning:
  - Small: $30K - $75K (4-6 weeks, single workstream)
  - Medium: $75K - $150K (8-12 weeks, 2-3 workstreams)
  - Large: $150K - $300K (12-20 weeks, full platform engagement)

### Step 5: Generate HTML Report

**Goal:** Convert markdown to Snowflake-branded HTML.

```bash
python3 <SKILL_DIR>/scripts/build_pov_html.py \
  --input <OUTPUT_DIR>/<COMPANY>_Services_POV.md \
  --output <OUTPUT_DIR>/<COMPANY>_Services_POV.html
```

**Post-generation customizations (apply via edit tool):**
1. Verify all section headings rendered correctly in navigation
2. Confirm pipeline opportunity badge displays correctly

### Step 6: Preview & Deliver

Start local HTTP server to preview:
```bash
python3 -m http.server 8504 --directory <OUTPUT_DIR>
```

Browse `http://localhost:8504/<COMPANY>_Services_POV.html` to verify rendering.

Present summary to user with:
- File locations (markdown + HTML)
- Key metrics highlighted
- Offer to adjust sections or convert to PowerPoint
- **Reminder:** Investment estimates are indicative — validate with Pre-Sales Architecture before external use

## Handoff to Deal Package

After the Services POV is approved by the AE/SE, invoke the `deal-package` skill to generate commercial artifacts:
- HTML proposal with pricing
- TDR deck for deal review
- DPS for pricing approval

Pass the following from the POV into deal-package:
- Focus area → `meta.engagement_title`
- Investment range → `pricing` estimate (still requires validation)
- Roadmap phases → `gantt.phases`
- Account team (AE/SE) → `meta.ae_name` / `meta.se_name`
- Use case context → `tdr.our_understanding`

To hand off: "Invoke the `deal-package` skill and reference `<OUTPUT_DIR>/<COMPANY>_Services_POV.md` as the source document."

## Stopping Points

- ✋ Step 1: Confirm company name, output directory, and focus area
- ✋ Step 6: Present final document for review

## Troubleshooting

**Error: "Object does not exist" on USE WAREHOUSE**
- `AC_WH` may not be accessible. Use `SNOWHOUSE` warehouse instead.
- Run `SHOW WAREHOUSES` to discover available warehouses.

**Error: Schema not authorized (SNOWSCIENCE, MDM)**
- `SNOWSCIENCE.OPERATIONAL_ANALYTICS` and `MDM.MDM_INTERFACES` may not be accessible with `SALES_RAVEN_RO_RL`.
- Use `sales.raven.sda_use_case_view` as fallback for use case data.
- Skip SNOWSCIENCE queries if not authorized — the POV can be built entirely from Raven views.

**Error: Dollar-sign quoting in GET_E360_SEARCH_RESULTS**
- Engagement search (Query 18) uses `$$` delimiters that can conflict with SQL parsers.
- If it fails, skip it — Query 19 (RECO_FOR_PROSPECTING) provides rich engagement context.

**Error: Query 19 (RECO_FOR_PROSPECTING) fails or times out**
- If web research yields minimal results, pass a short industry description for `<COMPANY_PROFILE_SUMMARY>`.
- Keep `<RECENT_NEWS_SUMMARY>` brief (1-2 sentences is sufficient).
- If the SP times out (>60s), skip it — use case data from Query 12b combined with firmographics provides sufficient context for the POV.

**Error: HTML renders with wrong title/subtitle**
- The `build_pov_html.py` script is purpose-built for Services POV documents. If the title doesn't render correctly, verify the markdown H1 follows the pattern `# <COMPANY> - Services Point of View`.

## Success Criteria

- ✅ SFDC account resolved with verified metadata
- ✅ All use cases captured (deployed + active + lost)
- ✅ Lost use case patterns analyzed and incorporated
- ✅ Opportunity focus area identified and deeply positioned
- ✅ 3-phase services roadmap with weekly activities
- ✅ Investment estimate provided as ±40% range with disclaimer
- ✅ Renewal impact explicitly connected
- ✅ Document is customer-ready (professional tone, no internal jargon)
- ✅ HTML report delivered with Snowflake branding
- ✅ Pricing disclaimer included: estimates require Pre-Sales Architecture validation

## Output

- **Markdown**: `<COMPANY>_Services_POV.md`
- **HTML**: `<COMPANY>_Services_POV.html` (Snowflake-branded, browser-viewable)
- Saved to user-specified output directory
