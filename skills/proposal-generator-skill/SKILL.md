---
name: proposal-generator
description: "Generate Snowflake Professional Services proposal presentations from meeting notes or project descriptions. Use for **ALL** requests that mention: proposal, deal review, engagement proposal, PS proposal, generate presentation, create proposal. DO NOT attempt proposal generation manually - always invoke this skill first."
---

# Proposal Generator

Generate structured proposal presentations from freeform meeting notes or project descriptions. Supports multiple presentation templates.

## Prerequisites

- `uv` installed (for running the PPTX renderer script)

## Setup

1. **List** available templates by scanning `<SKILL_DIR>/templates/` for subdirectories
2. Each template directory contains: `SKILL.md` (generation instructions), `template.pptx`, `schema.json`

## Workflow

### Step 1: Select Template

**If only one template exists**, auto-select it and inform the user.

**If multiple templates exist**, present a menu:

```
Available proposal templates:
1. SD Technical Deal Review
2. [Future Template]
...

Which template would you like to use?
```

**Load** the selected template's `SKILL.md` for generation instructions.
**Load** the selected template's `schema.json` to understand the expected JSON structure.

### Step 2: Gather Input

**Ask** the user for:
1. A **project name** (used to create the output folder). Suggest a short kebab-case name based on the client or project (e.g., `customer14-c360`).
2. Their **project description**, meeting notes, or freeform writeup. The user may provide this as pasted text, a file path, or multiple messages.

**Create** the project folder at `proposals/<project-name>/` in the current working directory. All intermediate and final outputs will be written here.

### Step 3: Validate Required Elements

Check the input against the required elements defined in the template sub-skill. For the SD Technical Deal Review, these are:
1. Project description
2. Snowflake tools and features
3. Timeline in weeks

**If elements are missing:**
- Tell the user exactly which elements are missing
- Ask them to provide the missing information
- Loop back to validation once they respond

**If all elements are present:** Proceed to Step 4.

### Step 4: Generate Proposal JSON

Using the generation instructions from the loaded template sub-skill:

1. Generate a complete, valid JSON object following the schema
2. Infer reasonable values for fields not explicitly stated (challenges from problem context, outcomes from goals, etc.)
3. Strictly adhere to character limits and formatting rules from the sub-skill

**Ask** the user how they want to review the proposal:
- **Display in chat**: Present formatted markdown with raw JSON in a collapsed block
- **Write to markdown file**: Write to `proposals/<project-name>/presentation_content.md` (confirm path with user)

If writing to file, include both the readable markdown and the raw JSON at the end of the file.

**⚠️ MANDATORY STOPPING POINT**: Wait for user feedback before proceeding.

### Step 5: Review and Refine

The user may request changes such as:
- Modify specific sections
- Adjust tone or detail level
- Add or remove items
- Fix inaccuracies

For each change request:
1. Apply the requested changes to the JSON
2. Present the updated proposal
3. Wait for further feedback or approval

**Resume rule:** Continue refining until the user indicates they are satisfied (e.g., "looks good", "finalize", "done", "export").

### Step 6: Export to PowerPoint

Once the user approves:

1. **Ask** the user for the output PPTX filename (suggest `<project-name>.pptx` as default)
2. **Write** the finalized JSON to `proposals/<project-name>/proposal.json`
3. **Run** the renderer:
   ```bash
   uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/render_pptx.py \
       --template <SKILL_DIR>/templates/<selected-template>/template.pptx \
       --data proposals/<project-name>/proposal.json \
       --output proposals/<project-name>/<filename>.pptx
   ```
4. **Inform** the user of the output file location and project folder contents

## Tools

### Script: render_pptx.py

**Description**: Renders a proposal JSON into a PowerPoint presentation by replacing `{{placeholder}}` markers in a template.

**Usage:**
```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/render_pptx.py \
    --template <template.pptx> --data <proposal.json> --output <output.pptx>
```

**Arguments:**
- `--template`: Path to the PPTX template file (required)
- `--data`: Path to the proposal JSON file (required)
- `--output`: Path for the output PPTX file (required)

**When to use:** After the user has approved the final proposal JSON.
**When NOT to use:** During the drafting/refinement phase.

## Stopping Points

- ✋ Step 1: If multiple templates, wait for selection
- ✋ Step 3: If required elements missing, wait for user input
- ✋ Step 4: After presenting generated proposal, wait for feedback
- ✋ Step 5: After each refinement, wait for feedback or approval

## Output

All outputs are written to `proposals/<project-name>/`:

```
proposals/<project-name>/
├── proposal.json              # Finalized JSON (system of record)
├── presentation_content.md    # Markdown review copy (if chosen)
└── <project-name>.pptx        # Final PowerPoint presentation
```

The JSON is preserved so the proposal can be re-rendered against updated templates without re-generating content.

## Adding New Templates

To add a new template, create a new directory under `<SKILL_DIR>/templates/<template-name>/` with:
1. `SKILL.md` - Generation instructions (required elements, JSON field specs, formatting rules)
2. `template.pptx` - PowerPoint template with `{{placeholder}}` markers
3. `schema.json` - Example JSON structure showing all expected fields
