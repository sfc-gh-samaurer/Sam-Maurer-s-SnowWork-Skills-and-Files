---
name: sd-technical-deal-review
description: "Generate SD Technical Deal Review proposal content. Loaded by proposal-generator when this template is selected."
parent_skill: proposal-generator
---

# SD Technical Deal Review - Generation Instructions

## When to Load

Loaded by the root proposal-generator skill when the user selects the SD Technical Deal Review template.

## Template Info

- **Template file**: `template.pptx` (in this directory)
- **Schema file**: `schema.json` (in this directory)
- **Slides covered**: Executive Summary (3), Our Understanding (4), Methodology (5), Engagement Model (6), Scope (7), Dependencies (9), Assumptions (13), Risks (14), Next Steps (15)

## Required Input Elements

A well-structured proposal requires these 3 elements:
1. **Project description** - What the project is about
2. **Snowflake tools and features** - Which Snowflake products/features will be used
3. **Timeline** - Duration in weeks

If any element is missing, ask the user for it specifically. If outcomes, challenges, or client name are not stated, infer them from context. Use "[CLIENT]" as a placeholder if no client is specified.

## Formatting Rules

### Bold Formatting (Critical)
For ALL array items that describe an issue, challenge, objective, action, or titled item, use:
`"**Title**: description"`

Examples:
- `"**Organizational Complexity**: Multiple business units across vertical markets create persistent data silos"`
- `"**Data Silos**: Unstructured review data not integrated with product insights"`
- `"**Access Barriers**: Non-technical users cannot analyze data independently"`

### Length Constraints (to fit Arial 12pt on a single slide)
- Text paragraphs: MAX 350 characters
- Array items: MAX 125 characters each
- Arrays: MAX 4-5 bullet points
- Be concise: every word must earn its place

## JSON Field Specifications

Generate a complete JSON with these sections IN THIS ORDER:

### Executive Summary (Slide 3)
- `exec_summary`: Text (MAX 300 chars, 2-3 sentences)
- `exec_challenges`: Array of challenges (MAX 4-5 items, each MAX 80 chars). Format: `"**Challenge Title**: description"`
- `exec_solution`: Array of solution elements (MAX 4-5 items, each MAX 80 chars). Format: `"**Solution Title**: description"`
- `exec_outcomes`: Array of benefits (MAX 4-5 items, each MAX 80 chars). Format: `"**Outcome Title**: description"`

### Our Understanding (Slide 4)
- `our_understanding`: Text paragraph (MAX 350 chars, 2-4 sentences)
- `our_understanding_current_state`: Array of challenges (MAX 5-6 items, each MAX 100 chars). Format: `"**Issue Title**: Brief description"`
- `our_understanding_engagement_objectives`: Array of objectives (MAX 5-6 items, each MAX 100 chars). Format: `"**Objective Title**: description"`

### Methodology (Slide 5)
- `meth_summary`: Text (MAX 300 chars)
- `meth_phases`: Array of phase objects:
  ```json
  [
    {"phase": "**Phase 1: Name**", "duration": "X hours", "activities": ["activity 1", "activity 2", "activity 3"]},
    ...
  ]
  ```
  Activities: MAX 3 items per phase, each MAX 90 chars.

### Engagement Model (Slide 6)
- `engage_summary`: Text (MAX 200 chars)
- `low_engage_high_own`: Array (MAX 3-4 items, MAX 80 chars each)
- `high_engage_high_own`: Array (MAX 3-4 items, MAX 80 chars each)
- `low_engage_low_own`: Array (MAX 3-4 items, MAX 80 chars each)
- `high_engage_low_own`: Array (MAX 3-4 items, MAX 80 chars each)

### Scope (Slide 7)
- `scope_assessment`: Array (MAX 4 items, MAX 100 chars each)
- `scope_architecture`: Array (MAX 4 items, MAX 100 chars each)
- `scope_implementation`: Array (MAX 4 items, MAX 100 chars each)
- `scope_out`: Array (MAX 4-5 items, MAX 100 chars each)

### Dependencies (Slide 9)
- `dependencies`: Array (MAX 6-8 items, MAX 100 chars each). Format: `"**Dependency Title**: description"`

### Assumptions (Slide 13)
- `assum_commitments`: Array (MAX 4-5 items, MAX 100 chars each). Format: `"**Commitment**: description"`
- `assum_access`: Array (MAX 4-5 items, MAX 100 chars each). Format: `"**Access Item**: description"`
- `assum_roles`: Array (MAX 4-5 items, MAX 100 chars each). Format: `"**Role**: description"`
- `assum_clarification`: Array (MAX 3-4 items, MAX 100 chars each). Format: `"**Clarification Item**: description"`

### Risks (Slide 14)
For each risk category (org, gov, tech, resource, scope, timeline, adopt):
- `risks_<category>`: Description (MAX 100 chars)
- `impact_<category>`: Level ("High", "Medium", "Low")
- `mitigation_<category>`: Strategy (MAX 100 chars)

Note: governance impact key is `impact__gov` (double underscore), adoption mitigation key is `mitigation_adoption`.

- `additional_risk_considerations`: Array (MAX 3-4 items, MAX 100 chars each). Format: `"**Risk**: description"`

### Next Steps (Slide 15)
- `next_actions`: Array (MAX 5-6 items, MAX 80 chars each). Format: `"**Action**: description"`

## Output

A single valid JSON object containing all fields above. Do NOT add commentary before or after the JSON. Present the JSON directly.
