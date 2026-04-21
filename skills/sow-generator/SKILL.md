---
name: sow-generator
description: Generate properly formatted Snowflake PS Statement of Work (.docx) documents matching the official template specification. Supports Fixed Fee and T&M engagements with structured JSON, markdown, or conversational input modes.
---

# SOW Generator Skill

Generate Snowflake Professional Services SOW Attachment 1 documents as .docx files with exact template formatting.

## What This Skill Produces

A Word document (.docx) containing **SOW Attachment 1** — the project-specific scope document (Sections 1-16). This does NOT include the legal wrapper (pages 1-2 of a full SOW), which is added separately during the signing process.

## Output Location

Default: `./deals/` relative to the user's working directory. On first run, check if this directory exists and create it if the user confirms. Use the naming convention: `Customer_SOW_YYYY-MM-DD_vN.docx`

**SOW documents remain as .docx files and are NOT converted to Google Docs.** Save locally to `~/CoCo/Accounts/{AccountName}/SOW/` or share the .docx directly.

## Email Draft Bullet Formatting Rule

If this skill creates any Gmail drafts (e.g., to share the SOW), all bullet lists in `mcp_google-worksp_create_draft` body content MUST use 4-space indented format:
```
    • item one
    • item two
```
Never use flush-left bullets (`• item` or `- item`) in email body content.

## Engagement Types

- **Fixed Fee** (`fixed_fee`): Milestone-based with payment percentages. The milestone table has 4 columns (Milestone, Payment, Description, Deliverable). Do NOT include Acceptance Criteria — Snowflake Legal has directed that acceptance criteria be removed from SOWs. The fee section has a payment schedule table.
- **Time & Materials** (`t_and_m`): Either milestones without payments (3-column table: Milestone, Description, Deliverable) OR phases with a rate card. Do NOT include Acceptance Criteria.

## Workflow

### Step 1: Determine Input Mode

Ask the user how they want to provide SOW content:

1. **Structured JSON** — User already has (or will provide) a JSON file matching the schema below
2. **Markdown** — User has a markdown SOW draft to convert
3. **Conversational** — Walk through each section interactively

### Step 2: Collect Content

#### Mode 1: Structured JSON
- User provides the path to a JSON file
- Read and validate it against the schema
- Confirm any missing optional sections

#### Mode 2: Markdown
- Read the user's markdown file
- Parse sections based on heading structure (# and ## headings map to the 16 SOW sections)
- Convert to the JSON schema format
- Show the user a summary of what was parsed and confirm before generating

#### Mode 3: Conversational
Walk through each section with the user. For each section:
1. Explain what it needs
2. Ask for the content
3. Confirm before moving on

**Required sections** (must have content):
- customer_name, engagement_type
- scope_of_services (executive_summary at minimum)
- milestones (at least 2)
- fees (total amount and payment structure)

**Standard sections** (suggest defaults if user skips):
- acceptance_process, change_management, general_provisions, signatures, term

**Project-specific sections** (ask for but allow empty):
- key_scope_items, raci, roles, governance, assumptions, dependencies, risks, access_security

### Step 3: Build JSON and Generate

Once content is collected and confirmed:

1. Write the JSON to a temp file (or the deals directory)
2. Run the generator script:

```bash
python3 SKILL_DIR/scripts/generate_sow.py <json_path> <output_path>
```

Where `SKILL_DIR` is the directory containing this SKILL.md file (use the `__skill_dir__` path or resolve from the skill location at `~/.snowflake/cortex/skills/sow-generator/`).

3. Confirm the output file was created and report its path

### Step 4: Review

After generation, offer to:
- Open or describe the document structure
- Make changes to specific sections (re-run with modified JSON)
- Generate a different version (v2, v3, etc.)

## STOP — Always confirm with the user before running the generation script.

## JSON Schema

The input JSON must have this top-level structure:

```json
{
  "customer_name": "Acme Corp",
  "sow_title": "Statement of Work — Acme Corp Data Platform",
  "engagement_type": "fixed_fee",
  "scope_of_services": { ... },
  "milestones": { ... },
  "acceptance_process": { ... },
  "key_scope_items": { ... },
  "raci": { ... },
  "roles": { ... },
  "governance": { ... },
  "assumptions": [ ... ],
  "dependencies": [ ... ],
  "risks": [ ... ],
  "access_security": { ... },
  "change_management": { ... },
  "fees": { ... },
  "term": { ... },
  "general_provisions": { ... },
  "signatures": { ... }
}
```

### Section Schemas

**scope_of_services**:
```json
{
  "executive_summary": ["Paragraph 1...", "Paragraph 2..."],
  "business_outcomes": [
    {"outcome": "Name", "description": "Details"}
  ],
  "our_understanding": {
    "paragraphs": ["..."],
    "challenges": [{"challenge": "Name", "description": "Details"}],
    "solution_paragraphs": ["..."],
    "solution_components": [{"component": "Name", "description": "Details"}]
  },
  "methodology": {
    "paragraphs": ["Overview paragraph..."],
    "phases": [
      {
        "title": "Phase 1: Foundation (Weeks 1-10)",
        "paragraphs": ["Phase description..."],
        "activities": ["Activity 1", "Activity 2"]
      }
    ]
  }
}
```

**milestones**:
```json
{
  "intro": "The following table sets forth...",
  "items": [
    {
      "name": "Milestone 0: Project Kickoff",
      "payment": "10%",
      "description": "Initial setup and alignment...",
      "deliverable": "Kickoff deck, project plan"
    }
  ]
}
```
Note: `payment` field is only used for `fixed_fee` engagements. Do NOT include `acceptance_criteria` — removed per Snowflake Legal directive.

**acceptance_process**:
```json
{
  "subsections": [
    {
      "number": "3.1",
      "title": "Deliverable Submission",
      "paragraphs": ["Upon completion of each milestone..."]
    }
  ]
}
```

**key_scope_items**:
```json
{
  "in_scope": [
    {"phase": "Phase 1", "scope_item": "DCDF gap assessment"}
  ],
  "out_of_scope": [
    "Production data migration",
    "Custom UI development"
  ]
}
```

Out-of-scope also supports structured format (numbered subsections):
```json
{
  "out_of_scope": [
    {"number": "4.2.1", "title": "Production Data Migration", "description": "Migration of production datasets is excluded from this engagement."},
    {"number": "4.2.2", "title": "Custom UI Development", "description": "Any custom front-end development beyond standard Snowflake interfaces."}
  ]
}
```

**raci**:
```json
{
  "intro": "The following RACI matrix...",
  "accountability_note": "Customer is Accountable (A) for every activity listed below.",
  "items": [
    {"is_phase_header": true, "activity": "Phase 1: Foundations"},
    {
      "activity": "DCDF Assessment",
      "responsible": "Snowflake",
      "accountable": "Snowflake",
      "consulted": "Customer",
      "informed": "Customer"
    }
  ],
  "work_products": [
    {"phase": "Phase 1", "work_product": "Assessment Report", "owner": "Snowflake"}
  ]
}
```

**roles**:
```json
{
  "snowflake": [
    {"role": "Engagement Manager", "responsibilities": "Overall delivery..."}
  ],
  "customer": [
    {"role": "Executive Sponsor", "responsibilities": "Strategic alignment..."}
  ]
}
```

**governance**:
```json
{
  "intro": "The following governance structure...",
  "alignment": {
    "paragraphs": ["The project alignment process ensures both parties maintain shared understanding of objectives, progress, and any changes throughout the engagement lifecycle."]
  },
  "forums": [
    {
      "forum": "Weekly Status",
      "cadence": "Weekly",
      "participants": "PM, Tech Lead",
      "responsibility": "Track progress",
      "materials": "Status report"
    }
  ]
}
```

**assumptions**: Array of strings OR array of objects. Both formats supported:

Simple (backward compatible):
```json
["Customer will provide access by Week 1", "VPN connectivity available"]
```

Structured (numbered with descriptions, preferred for complex engagements):
```json
[
  {"number": "8.1", "assumption": "Customer will designate a project lead with decision-making authority for the duration of the engagement."},
  {"number": "8.2", "assumption": "All required Snowflake accounts will be provisioned prior to the engagement start date."}
]
```

**dependencies**:
```json
[
  {"dependency": "Snowflake account provisioned", "required_by": "Week 1"}
]
```

**risks**:
```json
[
  {
    "risk": "Data quality issues",
    "impact": "High",
    "likelihood": "Medium",
    "mitigation": "Early data profiling in Phase 1"
  }
]
```

**access_security**:
```json
{
  "paragraphs": ["All work will be performed..."],
  "items": ["VPN access required", "MFA enabled"]
}
```

**change_management**:
```json
{
  "paragraphs": ["Any changes to the scope..."]
}
```

**fees** (Fixed Fee):
```json
{
  "paragraphs": ["The total fixed fee for this engagement..."],
  "total": "$250,000",
  "payment_schedule": [
    {"milestone": "Milestone 0: Kickoff", "percentage": "10%"}
  ]
}
```

**fees** (T&M):
```json
{
  "paragraphs": ["Services will be billed..."],
  "total": "$300,000 (estimated)",
  "not_to_exceed": "$350,000",
  "rate_card": [
    {"role": "Senior Consultant", "rate": "$350/hr"}
  ],
  "phases": [
    {"phase": "Phase 1", "hours": "400", "cost": "$140,000"}
  ]
}
```

**term**:
```json
{
  "paragraphs": ["This SOW shall commence on the Effective Date..."]
}
```

**general_provisions**:
```json
{
  "paragraphs": ["This SOW is governed by the terms of the Master Agreement..."]
}
```

**signatures**:
```json
{
  "intro": "IN WITNESS WHEREOF, the parties have executed this SOW..."
}
```

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

The generated .docx matches these exact specifications (derived from the Snowflake PS template):

- **Font**: Arial, 7.5pt (95250 EMU) for ALL text — body, headings, and table cells
- **H1 headings**: Bold Arial 7.5pt (section titles like "SCOPE OF SERVICES")
- **H2 headings**: Non-bold Arial 7.5pt (subsections like "1.1 Executive Summary")
- **Page**: Letter size (8.5" x 11")
- **Margins**: 0.5" left/right, ~0.37" top, 0.7" bottom
- **Line spacing**: 170 twips (~0.85 spacing), 0pt before/after
- **Tables**: Full-width (10800 dxa), black single borders (sz=4), bold header row text (where applicable), no cell shading
- **Bullets**: Unicode bullet character (•) in normal paragraphs
- **Section numbering**: In the text itself (e.g., "2. OUTCOMES AND ACCEPTANCE CRITERIA"), not Word auto-numbering
