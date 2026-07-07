---
name: proposal-to-sow-attachment
description: "Convert an existing Snowflake Professional Services proposal (a .pptx deck or .pdf) into a legal Statement of Work (SOW) attachment as a formatted .docx — numbered sections, bulleted lists, and tables that mirror the proposal. Use whenever the user wants to turn a proposal, deck, or engagement pitch into an SOW, SOW attachment, scope-of-work document, or 'contract-ready' version. Triggers: proposal to SOW, convert proposal to SOW, SOW attachment, make an SOW from this deck, turn this proposal into a statement of work, scope of work docx, contractify this proposal. This produces the project-specific scope attachment (not the MSA legal wrapper). If the user wants to author an SOW from scratch without a source proposal, use sow-generator instead."
---

# Proposal → SOW Attachment Conversion

Turn an existing proposal deck/doc into a legal SOW attachment `.docx`. The proposal
is the source of truth for scope, deliverables, timeline, milestones, pricing, RACI,
assumptions, and risks; this skill restructures that content into contract-style
prose with numbered sections and tables.

## What it produces

A single `.docx` — the **project-specific SOW attachment** (scope sections + signature
block). It intentionally does **not** generate the MSA/Order-Form legal wrapper, which
is attached during signing. An incorporation clause on the cover references that wrapper.

## Prerequisites

Scripts depend on `python-docx`, `python-pptx`, and `pypdf` (see `pyproject.toml`).
Run scripts with `uv` so dependencies resolve automatically. Verify uv:
```bash
uv --version
```

## Workflow

### Step 1: Locate & extract the source proposal

Confirm the proposal file path (`.pptx` or `.pdf`). Extract its content to JSON:

```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/extract_proposal.py \
  --input "/abs/path/proposal.pptx" --output "/abs/path/proposal_extract.json"
```

Read the JSON. `.pptx` extraction preserves per-slide **text** and **tables** (as row
arrays) — tables usually hold scope, deliverables, milestones, RACI, effort, and risks.

### Step 2: Map proposal content → SOW spec

Build a JSON spec for `build_sow.py`. **Load `references/spec_schema.md`** for the full
schema and block types. Map the proposal into these standard SOW sections (include only
those the proposal supports; keep order):

1. Background & Engagement Overview  — subheadings for problem statement + engagement summary
2. Engagement Objectives & Success Criteria — `numbered` (num + bold title + criteria)
3. Scope of Services — `table` (Phase / Workstream / Activities / Timeline); in-cell `•` bullets
4. Engagement Deliverables — `table`
5. Project Timeline — `table` + `bullets` for checkpoints
6. Milestones & Acceptance Gates — `table` (incl. payments)
7. Roles & Responsibilities — subheadings + `bullets` per role
8. Engagement RACI — `table` (R/A/C/I)
9. Customer Dependencies & Commitments — `table`
10. Resource Effort — `table` (hours by role; keep the totals row)
11. Assumptions & Exclusions — subheadings + `bullets`
12. Risks & Mitigations — `table`
13. Pricing — `table` + `bullets` for committed outcomes
14. Next Steps — `paragraph` blocks with `num`
15. Acceptance — `signature` block

**Legalization (apply while mapping):**
- Convert marketing phrasing to contract prose; formalize numerals — "sixteen (16) weeks".
- Add an MSA/Order-Form incorporation clause in `cover.note`.
- Frame effort hours as estimates supporting the fixed fee, not a T&M commitment.
- Reference the deliverable acceptance/review window (e.g., five business days).
- **Verify milestone payments sum exactly to the total fixed fee.** If they don't (e.g.,
  the deck rounded), flag it and propose an even split — do not silently alter the total.

`references/example_spec.json` is a complete worked example (CrowdStrike Matillion
migration) — use it as a structural template.

**⚠️ STOP**: Present the proposed section list + any pricing/parity issues you found
(e.g., payments not summing to the fee) and confirm before generating.

### Step 3: Generate the .docx

```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/build_sow.py \
  --spec "/abs/path/spec.json" --output "/abs/path/<Client>_SOW_Attachment.docx"
```

### Step 4: Verify

Re-open the output and confirm section count, table dimensions, and totals:
```bash
python3 - <<'PY'
from docx import Document
d = Document("/abs/path/<Client>_SOW_Attachment.docx")
print("tables:", len(d.tables))
PY
```
Check: every proposal table is represented; milestone payments total the fixed fee;
effort totals row matches; no marketing language remains.

**⚠️ STOP**: Present the file path for review. Offer to `open` it.

## Tools

### scripts/extract_proposal.py
`.pptx` / `.pdf` → structured JSON (per-slide/page text + tables).
`--input <file>` (required), `--output <json>` (optional; stdout if omitted).

### scripts/build_sow.py
JSON spec → styled SOW `.docx` with auto-numbered sections, bullets, and branded tables.
`--spec <json>` (required), `--output <docx>` (optional; uses `spec["output"]`).

## Stopping Points

- ✋ Step 2: Confirm section mapping + pricing/parity findings before building.
- ✋ Step 4: Final review of the generated document.

## Output

A contract-ready SOW attachment `.docx` at the requested path, plus the intermediate
`spec.json` (reusable/editable for regeneration).
