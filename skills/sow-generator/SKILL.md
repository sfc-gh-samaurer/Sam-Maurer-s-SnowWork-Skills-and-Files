---
name: sow-generator
description: Generate properly formatted Snowflake PS Fixed Fee Statement of Work (.docx) documents. Supports all fixed-fee engagement types (Platform, Migration, Analytics, Advisory, AI/ML, Governance, Training, SPCS). Uses guided conversational intake, auto-reads proposals/TDRs, validates before generating, and uploads to Google Drive.
---

# SOW Generator Skill — Fixed Fee Engagements

Generate Snowflake Professional Services Fixed Fee SOW documents (.docx) with exact Snowflake PS template formatting.

## ⚖️ Legal Authority — PRIMARY SOURCE

**ALWAYS read `references/legal_cx_sow_guidance.md` before generating any SOW.**

This file is the authoritative legal source provided by SD Legal (Katie Flanagan). It contains:
- Official approved attachment templates with Google Doc links
- Mandatory drafting rules for T&M and Fixed Fee engagements
- The standard SOW attachment skeleton (8 sections)
- Critical overrides to default skill behavior

**Where this guide conflicts with instructions elsewhere in this skill, the guide wins.**  
Where this guide is silent, the existing skill instructions remain valid.

### Critical Overrides from Legal Guidance

1. **NO acceptance criteria in Fixed Fee SOWs** — Do not auto-include acceptance criteria in milestone tables. Only add if customer has explicitly required it AND only after first sending without it. This overrides any default behavior that includes acceptance criteria.

2. **Project Plan / RACI are OPTIONAL** — Only include these attachment sections if the customer has requested them or there is a specific need. Do NOT auto-generate them.

3. **Timelines must say "target"** — Any project timeline in the attachment body must be framed as a "target timeline."

4. **T&M: never commit to deliverables** — Qualify all outcomes as "potential", "anticipated", or "targeted."

5. **AI/ML SOWs require Nick DiRienzo sign-off** — Consult Nick DiRienzo's team before drafting AI/ML Use Case Support SOWs.

## What This Skill Produces

A Word document (.docx) containing the complete SOW — Order Form Exhibit (Sections A–I) + Attachment 1 (Program Management with Milestones) + per-work-stream attachments + Signatures. Uses verbatim legal boilerplate from `static_content.py` (legal text version tracked).

**This skill is Fixed Fee only.** It does not support T&M engagements.

## Legal Text Version

All generated SOWs use legal text from `static_content.py`. Check `LEGAL_TEXT_VERSION` before sending to CLM to confirm you are using current approved language.

## Output — Drive First

SOW documents are saved locally AND uploaded to the account's Google Drive folder:
- **Local**: `~/CoCo/Accounts/{AccountName}/SOW/{CustomerName}_SOW_{YYYY-MM-DD}_vN.docx`
- **Drive**: Upload to the account's Google Drive folder using `upload_docx.mjs`
- **Version management**: Before generating, search Drive for existing `{CustomerName}_SOW` files to determine the next version number (v1, v2, v3...)
- Return the Drive link as the primary output

## Email Draft Bullet Formatting Rule

If this skill creates any Gmail drafts, all bullet lists in `mcp_google-worksp_create_draft` body content MUST use 4-space indented format:
```
    • item one
    • item two
```

## STOP — Always run validate_sow_data() before generating.

```bash
python3 SKILL_DIR/scripts/generate_sow.py <json_path> <output_path>
```
The CLI automatically runs validation and blocks generation if there are blocking issues.

## Core Workflow (5 Phases)

---

### Phase 0 — Proposal / TDR Auto-Read (ALWAYS DO THIS FIRST)

Before asking ANY other questions, ask:

> "Do you have a Google Slides proposal or TDR deck for this engagement? If so, share the link and I'll read it to pre-populate the SOW."

**If YES**: Read the Google Slides presentation using `mcp_google-worksp_read_presentation`. Extract:
- Work stream descriptions → `attachments[].brief_description`
- Milestone names and target weeks → `milestones.items[]`
- Snowflake responsibilities bullet points → `attachments[].snowflake_responsibilities`
- Team roles (SDM, SA, DE) → `roles.snowflake[]`
- Customer stakeholders → `roles.customer[]`
- Scope items, assumptions, exclusions → use as starting point for overrides
- Gantt/timeline slide → note the slide ID and offer to screenshot it for `gantt_image_path`

After reading: "I found the following in your proposal. Here's what I've pre-populated — please review and correct anything before I proceed:" Then show a structured summary.

**If NO**: Proceed to Phase 1.

---

### Phase 1 — Engagement Template OR Start Fresh

Ask: "Do you want to start from an engagement template, or build from scratch?"

**Available templates** (in `SKILL_DIR/templates/`):
| Template | Use Case |
|----------|----------|
| `template_simple_platform.json` | Platform setup only, 2 milestones |
| `template_data_migration.json` | Platform + DMVA migration, 3 milestones |
| `template_full_migration.json` | Platform + Ingestion + DMVA + Code Conversion, 5 milestones |
| `template_analytics.json` | Platform + Analytics Enablement (Cortex, dashboards), 2 milestones |
| `template_advisory.json` | Advisory/Assessment only, 2 milestones |

**If user selects a template**: Load the JSON, show a summary, ask the user to fill in all `[PLACEHOLDER]` fields.
**If starting fresh**: Proceed to Phase 2.

---

### Phase 2 — Work Streams & Attachment Types

Ask which work types are in scope (can select multiple):

**Core work streams** (these become the numbered attachments):
- `platform_implementation` — Platform provisioning, RBAC, CI/CD, security (Attachment 2+)
- `data_ingestion` — Snowpipe, Openflow CDC, External Stage, API integrations
- `historical_data_migration` — DMVA-based one-time bulk migration
- `code_conversion` — SnowConvert, Snowpark Connect, SQL/PySpark rewrite
- `spcs_container_migration` — Docker/R/Python lift-and-shift to SPCS
- `analytics_enablement` — Cortex AI/ML, Streamlit apps, semantic layers, dashboards
- `advisory_assessment` — Architecture assessment, FinOps, WAF, migration scoping
- `data_governance` — Masking policies, row access policies, data products, tagging
- `training_enablement` — Workshop delivery, knowledge transfer programs
- `ai_ml_factory` — Feature stores, model registry, Cortex ML pipelines
- `generic` — Custom/other work type (requires full user-provided content)

> **Program Management (Attachment 1) is ALWAYS included automatically.** The generator auto-creates it. Cross-Workstream Governance is auto-added when 2+ core work streams.
> **Milestones** live inside Attachment 1 (NOT a separate final attachment).
> **Gantt chart**: Provide `gantt_image_path` (local image file) to embed a project timeline.

---

### Phase 3 — Order Form Exhibit Questions

For the Order Form Exhibit (Sections A–I), ask:

1. **Customer name** — Substituted into preamble and signature block.

2. **Source environments** *(Section F.1)*  
   "What source data environments will Snowflake SD need access to?"  
   Examples: "Amazon Redshift", "Google BigQuery AIC V3", "Cerner HealtheEDW Data Share"  
   → `source_environments` array

3. **Target Snowflake environment** *(Section F.1)*  
   "What is the target Snowflake account type?"  
   Examples: "Snowflake Business Critical account(s)", "Snowflake Business Critical with Private Link"  
   → `target_environments` array

4. **Engagement duration** *(Section E)*  
   "What is the estimated engagement duration?"  
   Format: "ten (10) weeks", "six (6) months"  
   Default if not provided: `"twelve (12) months"`  
   → `engagement_duration` string

5. **Training Funds amount** *(Section C)*  
   "What is the training credit amount included in this engagement?"  
   Default: `$[TBD]`  
   → `training_funds.amount`

6. **Production access** *(Section F.3)*  
   "Will Snowflake SD need access to any Customer production environments?"  
   → `production_access.needed`

7. **Assumption Validation Checkpoint — ALWAYS ASK** *(Section H — OPTIONAL)*  
   "Is there an Assumption Validation Checkpoint in this engagement?"  
   If yes: "After which milestone? How long? (e.g., 'one (1) week')"  
   → `assumption_validation_checkpoint`

8. **Subcontractor — ALWAYS ASK** *(Sections G.5 and I — OPTIONAL)*  
   "Is there a named subcontractor on Snowflake paper?"  
   If yes: "Partner name, their role, and which Attachment covers their work?"  
   → `subcontractor`

---

### Phase 4 — Per-Attachment Details

For each work stream selected in Phase 2, ask:

1. **Title** — Default from library (e.g., "Attachment 2: Platform Implementation"). Confirm or override.
2. **Brief description** — 1–2 sentences for Section B listing. → `brief_description`
3. **Scope table rows** — Source/target platform, hours (omit Snowflake hours by default), fixed fee or `$[TBD]`.
4. **Snowflake Responsibilities** — Action-oriented bullets. Must be provided; this is the most engagement-specific section. Pre-populated from proposal if available.
5. **Customer Responsibilities extras** — Show library defaults, ask what to add. → `customer_responsibilities_extra`
6. **Scope Exclusions extras** — Library defaults shown, ask for additions. → `exclusions_extra`
7. **Scope Assumptions extras** — Library defaults shown, ask for additions. → `assumptions_extra`
8. **RACI parties** — 2-party (Snowflake + Customer) or 3-party (add partner)? → `raci_parties`

---

### Phase 5 — Milestones & Fees

1. **Milestone names** — 2+ milestones required. For each: name, key deliverables, percentage (%), amount, and target week/date.
2. **Total fee** — Overall fixed fee. Can be `$[TBD]`.
3. **Gantt image** — "Is there a project timeline image you want embedded? Provide a local file path." → `gantt_image_path`

---

### Phase 6 — Validation, Confirm & Generate

1. Run `validate_sow_data()` by executing `generate_sow.py` with the JSON (CLI auto-validates).
2. Show the validation checklist to the user.
3. Surface any warnings (e.g., `$[TBD]` amounts, missing scope tables).
4. **Block generation** if there are blocking issues. Ask the user to fix them.
5. Once clean: "Ready to generate. The SOW will be saved locally and uploaded to Drive. Confirm?"
6. Generate, upload to Drive, return the Drive link.

---

## Order Form Exhibit — Section Map (A–I)

| Section | Title | Type | Notes |
|---------|-------|------|-------|
| Header | Order Form Exhibit - TECHNICAL SERVICES SOW | Verbatim | Always |
| Preamble | Parties and definitions | Verbatim + `{customer_name}` | Always |
| **A** | Description of Technical Services | Verbatim | Always |
| **B** | Custom Fixed Fee | Dynamic | Per-attachment `brief_description` list |
| **C** | Training Funds | Verbatim + `{training_amount}` | Always; defaults `$[TBD]` |
| **D** | Payments and Expenses | Verbatim | Always |
| **E** | Scheduling and Term | Verbatim + `{engagement_duration}` | Always |
| **F** | Snowflake Access (F.1–F.4) | Mostly verbatim; F.1 dynamic | F.1 uses `source_environments` |
| **G** | Additional Terms (G.1–G.5) | Mostly verbatim; G.5 dynamic | G.5 dynamic if subcontractor |
| **H** | Fixed Fee Engagement Terms (AVC) | Verbatim + `{trigger_milestone}` | **OPTIONAL — ALWAYS ASK** |
| **I** | Subcontractor Technical Services | Verbatim + `{partner_name}` | **OPTIONAL — ALWAYS ASK** |

---

## Attachment Library Summary

Pre-built transferable content (customer responsibilities, exclusions, assumptions, RACI) for each work type:

| Type | Category Headers (Customer Responsibilities) | Default Exclusions |
|------|---------------------------------------------|-------------------|
| `platform_implementation` | Before Kickoff, Week 1, Within First 4 Weeks, Throughout, Post-Migration | 2 |
| `data_ingestion` | Week 1, 5 Days After Kickoff, By Week 4, Throughout, Per Wave, Post-Migration | 7 |
| `historical_data_migration` | Before Kickoff, 5 Days After Kickoff, Week 1, Week 1-2, Weeks 1-6, Before Pilot, During Migration, Per Phase, Production, Post | 11 |
| `code_conversion` | Before Pilot, 5 Days After Kickoff, Throughout, Per Wave | 9 |
| `spcs_container_migration` | Before Kickoff, Week 1, Throughout, Post-Migration | 7 |
| `analytics_enablement` | Before Kickoff, Throughout, Post-Delivery | 5 |
| `advisory_assessment` | Before Kickoff, Throughout Assessment, Post-Delivery | 5 |
| `data_governance` | Before Kickoff, Throughout, Post-Delivery | 5 |
| `training_enablement` | Before Kickoff, Throughout, Post-Delivery | 4 |
| `ai_ml_factory` | Before Kickoff, Throughout, Post-Delivery | 6 |
| `program_management` | Before Kickoff, Throughout | 2 |
| `generic` | Before Kickoff, Throughout | 1 |

**IMPORTANT**: Always show the user what's included in the defaults and ask for additions — never silently apply defaults without showing them.

---


---

## JSON Schema (Quick Reference)

The input JSON uses this top-level structure. All fields are described in the Phase 3–5 workflow above.

```json
{
  "customer_name": "Acme Corp",
  "sow_title": "Statement of Work — Acme Corp",
  "engagement_type": "fixed_fee",
  "total_fee": "$[TBD]",
  "engagement_duration": "ten (10) weeks",
  "source_environments": ["AWS Redshift"],
  "target_environments": ["Snowflake Business Critical account(s)"],
  "production_access": {"needed": false},
  "training_funds": {"amount": "$[TBD]", "expiry": "twelve (12) months"},
  "assumption_validation_checkpoint": {"enabled": false},
  "subcontractor": {"enabled": false},
  "gantt_image_path": null,
  "roles": {
    "snowflake": [{"role": "SDM", "responsibilities": "..."}],
    "customer": [{"role": "Project Sponsor", "responsibilities": "..."}]
  },
  "attachments": [
    {
      "type": "platform_implementation",
      "title": "Attachment 2: Platform Implementation",
      "brief_description": "One or two sentence description for Section B.",
      "scope_table": [["Source Platform", "..."], ["Target Platform", "..."], ["Fixed Fee", "$[TBD]"]],
      "snowflake_responsibilities": ["Action-oriented bullet 1", "Bullet 2"],
      "customer_responsibilities_extra": [{"category": "Before Kickoff", "items": ["Extra item..."]}],
      "exclusions_extra": ["Engagement-specific exclusion"],
      "assumptions_extra": ["Engagement-specific assumption"],
      "customer_responsibilities_override": null,
      "exclusions_override": null,
      "assumptions_override": null,
      "raci_parties": ["Snowflake SD", "Customer"],
      "raci": [{"activity": "RBAC design", "sf": "A/R", "customer": "C"}]
    }
  ],
  "milestones": {
    "items": [
      {"num": "1", "name": "Milestone 1 Name", "deliverables": "...", "pct": "50%", "amount": "$[TBD]", "target": "Week X"},
      {"num": "2", "name": "Milestone 2 Name", "deliverables": "...", "pct": "50%", "amount": "$[TBD]", "target": "Week Y"}
    ]
  }
}
```

**Override behavior:**
- `*_extra` arrays: APPEND to library defaults
- `*_override` arrays: REPLACE library defaults entirely
- `raci`: if provided, replaces library defaults; if omitted, library defaults are used

---




---

## Project Attachments (DMVA & Code Conversion)

In addition to the main SOW Attachment 1, the skill can generate two standard
Snowflake PS project-specific attachments that the CLM process requires:

1. **Data Migration & Validation Project** (`dmva_attachment`)
2. **Code Conversion Project** (`code_conversion_attachment`)

### How to Generate Attachments

Add one or both keys to the top-level SOW JSON and run:

```bash
python3 SKILL_DIR/scripts/generate_project_attachments.py <json_path> <output_dir>
```

### Track Changes Behavior

All values supplied by the PS writer (platform names, object counts, resource/staffing
plan rows, unit test selections, etc.) are written as **OOXML tracked insertions**
(`<w:ins w:author="Snowflake PS Generator" ...>`). When the document is opened in
Word, these changes appear in the standard Track Changes view so the reviewer can
Accept All before sending to the customer. Boilerplate legal language is written
as plain (un-tracked) text.

### `dmva_attachment` Schema

```json
{
  "legacy_platform": "Amazon Redshift (3 clusters, 19 databases)",
  "target_platform": "Snowflake Service (non-production databases)",
  "engagement_type": "t_and_m",
  "scope": {
    "tables_full_load":       "1,847",
    "tables_incremental":     "0",
    "total_data_volume":      "4.2 TB",
    "oversized_columns":      "12",
    "modification_columns":   "3",
    "notes":                  "Optional free-text notes row"
  },
  "resource_plan": [
    {"week": "1-2",   "activity": "Data profiling and migration planning", "sf_hours": 40,  "customer_hours": 16},
    {"week": "3-10",  "activity": "Full data migration and validation",     "sf_hours": 200, "customer_hours": 104}
  ],
  "extra_exclusions":  ["Any exclusion beyond the standard list"],
  "extra_assumptions": ["Rocket Mortgage will provide a dedicated VDI for DMVA execution."]
}
```

**Tracked fields**: all `scope` values, all resource plan rows, `extra_assumptions`, `extra_exclusions`.

### `code_conversion_attachment` Schema

```json
{
  "legacy_platform":    "Amazon Redshift",
  "assessment_date":    "March 2026",
  "target_platform":    "Snowflake Service (non-production databases)",
  "engagement_type":    "t_and_m",
  "objects": [
    {"type": "Tables",      "count": "1,847"},
    {"type": "Views",       "count": "412"},
    {"type": "Procedures",  "count": "412"},
    {"type": "Functions",   "count": "89"},
    {"type": "SQL Scripts – Wrapped/Unwrapped", "count": "156"}
  ],
  "refactoring": [
    {"type": "Case Insensitive Collation",    "estimated": "45",      "max_refactor": "45"},
    {"type": "Global Temporary Tables",       "estimated": "12",      "max_refactor": "12"},
    {"type": "Nested Functions",              "estimated": "28",      "max_refactor": "28"},
    {"type": "Object Generating Dynamic SQL", "estimated": "Unknown", "max_refactor": "0"},
    {"type": "Custom Refactor Request",       "estimated": "0",       "max_refactor": "0"}
  ],
  "prerequisites": {
    "snowconvert_required": true
  },
  "unit_test": {
    "outside_env_dummy":     false,
    "without_data_customer": false,
    "dummy_data_customer":   false,
    "customer_static_data":  true
  },
  "code_correction_support_weeks": 0,
  "staffing_plan": [
    {"week": "1-2",   "activity": "Code assessment, SnowConvert setup, conversion plan", "sf_hours": 68},
    {"week": "3-8",   "activity": "Automated conversion and MDC review cycles",           "sf_hours": 400},
    {"week": "9-12",  "activity": "Refactoring, unit testing, defect remediation",        "sf_hours": 480},
    {"week": "13-16", "activity": "Final delivery, knowledge transfer",                   "sf_hours": 367}
  ],
  "extra_exclusions": []
}
```

**Tracked fields**: `legacy_platform`, `assessment_date`, all object counts, all refactoring numbers, unit test yes/no selections, all staffing plan rows, `code_correction_support_weeks` (when Fixed Fee), `extra_exclusions`.

**Standard object types** (any not listed default to 0):
`Tables`, `Views`, `Materialized Views`, `Macros`, `Functions`, `Procedures`, `Packages`, `Triggers`, `SQL Scripts – Wrapped/Unwrapped`, `Teradata Utility Scripts – Wrapped/Unwrapped`, `Oracle PL/SQL Scripts – Wrapped/Unwrapped`

**Standard refactoring types** (any not listed default to 0/0):
`Case Insensitive Collation`, `Cursor Loops`, `Global Temporary Tables`, `Materialized Views`, `Nested Functions`, `Nested Procedures and Transactions`, `Non-Logic View Layers`, `Object Generating Dynamic SQL`, `Triggers`, `Renaming of Objects`, `Custom Refactor Request`

---

## Document Formatting Specification

The Snowflake PS SOW format is derived from the reference Google Doc:
- **Reference**: https://docs.google.com/document/d/1n-BAcsVTN0YuK6Ky_uDQvIHKRGjYjRb5zSmcRbli4t4/edit
- **Local template**: exported to `/tmp/rocket_sow_template.docx` (see Template Approach section below)

### Font & Page
- **Font**: Arial, 7.5pt (`w:sz val="15"`, `w:szCs val="15"`) for ALL text — body, headings, table cells
- **Page**: Letter (8.5" × 11"), margins: 0.5" left/right, ~0.37" top, 0.7" bottom

### Line Spacing (EXACT values from reference doc)
| Paragraph type | `w:line` | `w:lineRule` | `w:before` | `w:after` |
|----------------|----------|--------------|------------|----------|
| Body text (normal) | `170` | `auto` | (none) | (none) |
| Main bullets | `170` | `auto` | `0` | `0` |
| Category headers (Cust. Resp.) | `240` | `auto` | `0` | `0` |
| Sub-bullets under categories | `240` | `auto` | (none) | (none) |
| Heading 1 | `170` | `auto` | `0` | (none) |

**Do NOT** use `w:lineRule="exact"` — the reference doc uses `"auto"` throughout.

### Bullet System (3 types, all using Word numPr)
Bullets in the reference doc use Word's native list numbering system (`numPr`), NOT Unicode `•` characters. The `numId` values reference numbering definitions inside the template file.

| Bullet type | `numId` | `ilvl` | `w:line` | `ind:left` | `ind:hanging` | Use |
|-------------|---------|--------|----------|------------|---------------|-----|
| Main bullets (role items, SF responsibilities) | `18` | `0` | `170` | `720` | `360` | Snowflake Responsibilities, main body lists |
| Category headers (Customer Responsibilities) | `12` | `0` | `240` | `720` | `360` | "Access — Week 1 of Term" headers |
| Sub-bullets under categories | `13` | `0` | `240` | `1440` | `360` | Items under each category header |

These `numId` values are only valid when using the exported template file as the document base (they reference `abstractNum` definitions inside that file).

### Heading / Style Types
- **Main body section headers** ("Description of Technical Services"): Use `Heading1` style
- **Attachment top-level headers** ("Attachment 1: Platform Implementation"): `style='normal'` + bold run
- **Attachment sub-sections** ("i. Scope.", "ii. Snowflake Responsibilities:"): `style='normal'` + bold run
- **Role labels** ("T&M Senior Solutions Architect"): `style='normal'` + bold run, `before=0 after=0`
- **All body text**: `style='normal'` (lowercase), `w:line="170" w:lineRule="auto"`

### Table Formatting
- **Table style**: `'TableNormal'` (NOT `'Table Grid'` — that style doesn't exist in the Google-exported template)
- **Borders**: Must be added manually via `<w:tblBorders>` XML since TableNormal has no default borders
- **Width**: Full-width via `<w:tblW w:w="10800" w:type="dxa"/>`
- `CT_Tbl` does NOT have `get_or_add_tblPr()` — use `tbl_el.find(qn('w:tblPr'))` instead

Borders XML to inject:
```python
borders_xml = (
    '<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
    '</w:tblBorders>'
)
tbl_pr.append(parse_xml(borders_xml))
```

---

## ⚠️ Critical Bug: Table Ordering (sect_pr.addprevious)

**This is the #1 python-docx gotcha for custom SOW scripts.**

When mixing `doc.element.body.append(p)` for paragraphs with `doc.add_table()` for tables, **all tables will appear at the TOP of the document** and all paragraphs at the bottom. This happens because:

- `doc.add_table()` inserts the table **before** `<w:sectPr>` (the section properties element that Word keeps as the last child of `<w:body>`)
- `doc.element.body.append(p)` appends paragraphs **after** `<w:sectPr>`

**Fix**: Always insert paragraphs before `<w:sectPr>`:

```python
def _append_p(doc, ppr_el, runs):
    p = OxmlElement('w:p')
    # ... build paragraph content ...
    body = doc.element.body
    sect_pr = body.find(qn('w:sectPr'))
    if sect_pr is not None:
        sect_pr.addprevious(p)  # ← CRITICAL: not body.append(p)
    else:
        body.append(p)
    return p
```

Apply the same fix to any `page_break()` function that appends to `body`. This ensures paragraphs and tables are in the same ordered space in the document XML.

---

## Template Approach (Exact Format Match)

For format-compatible SOWs, always start from the reference Google Doc exported as .docx. **Do not build from a blank Document() — you will lose all numbering definitions and styles.**

### Step 1: Export reference Google Doc

Use `export_gdoc.mjs` at `~/.snowflake/cortex/.mcp-servers/google-workspace/`:

```bash
cd ~/.snowflake/cortex/.mcp-servers/google-workspace
./node export_gdoc.mjs "1n-BAcsVTN0YuK6Ky_uDQvIHKRGjYjRb5zSmcRbli4t4" "/tmp/rocket_sow_template.docx"
```

### Step 2: Open template, clear body, rebuild

```python
from docx import Document
from docx.oxml.ns import qn
from copy import deepcopy

tmpl = Document("/tmp/rocket_sow_template.docx")

# Clone pPr from specific template paragraphs (see indexes below)
PPR_BODY       = deepcopy(tmpl.paragraphs[2]._p.find(qn('w:pPr')))   # body text
PPR_H1         = deepcopy(tmpl.paragraphs[6]._p.find(qn('w:pPr')))   # Heading 1
PPR_BOLD_ROLE  = deepcopy(tmpl.paragraphs[10]._p.find(qn('w:pPr')))  # bold label
PPR_BULLET     = deepcopy(tmpl.paragraphs[12]._p.find(qn('w:pPr')))  # main bullet (numId=18, line=170)
PPR_CAT_HDR    = deepcopy(tmpl.paragraphs[145]._p.find(qn('w:pPr'))) # cat header (numId=12, line=240)
PPR_SUB_BULLET = deepcopy(tmpl.paragraphs[156]._p.find(qn('w:pPr'))) # sub-bullet (numId=13, line=240)
PPR_ATTACH_HDR = deepcopy(tmpl.paragraphs[118]._p.find(qn('w:pPr'))) # attachment title
PPR_SUBSEC     = deepcopy(tmpl.paragraphs[122]._p.find(qn('w:pPr'))) # attach sub-section

# Clone rPr from specific template runs
RPR_NORMAL = deepcopy(tmpl.paragraphs[2].runs[0]._r.find(qn('w:rPr')))
RPR_BULLET_RUN = deepcopy(tmpl.paragraphs[12].runs[0]._r.find(qn('w:rPr')))

# Open fresh copy, clear all body content
doc = Document("/tmp/rocket_sow_template.docx")
for child in list(doc.element.body):
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag in ('p', 'tbl', 'sdt'):
        doc.element.body.remove(child)
```

### Step 3: Build paragraphs by cloning pPr

```python
def _append_p(doc, ppr_el, runs):
    p = OxmlElement('w:p')
    if ppr_el is not None:
        p.append(deepcopy(ppr_el))
    for text, rpr_el in runs:
        if text:
            r = OxmlElement('w:r')
            if rpr_el is not None:
                r.append(deepcopy(rpr_el))
            t = OxmlElement('w:t')
            t.text = text
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r.append(t)
            p.append(r)
    # CRITICAL: insert before sectPr (not append to body)
    sect_pr = doc.element.body.find(qn('w:sectPr'))
    if sect_pr is not None:
        sect_pr.addprevious(p)
    else:
        doc.element.body.append(p)
    return p
```

### Template Paragraph Index Reference

| Index | Paragraph type | Key XML |
|-------|---------------|--------|
| 0 | Document title | `pStyle=Title`, `line=170 auto` |
| 2 | Body text (normal) | `line=170 auto`, no before/after |
| 6 | Heading 1 | `pStyle=Heading1`, `numPr numId=21`, `before=0` |
| 10 | Bold role label ("T&M SA") | `normal`, `before=0 after=0`, bold run |
| 12 | Main bullet | `numPr numId=18`, `line=170`, `ind left=720 hanging=360` |
| 118 | Attachment top-level header | `normal`, no explicit spacing, bold run |
| 122 | Attachment sub-section (i., ii.) | `normal`, no explicit spacing, bold run |
| 145 | Category header (Cust. Resp.) | `numPr numId=12`, `line=240`, `ind left=720 hanging=360` |
| 156 | Sub-bullet | `numPr numId=13`, `line=240`, `ind left=1440 hanging=360` |

---
