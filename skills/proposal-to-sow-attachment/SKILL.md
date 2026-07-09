---
name: proposal-to-sow-attachment
description: "Convert an existing Snowflake Professional Services proposal (a .pptx deck or .pdf) into a legal Statement of Work (SOW) attachment as a formatted Google Doc — numbered sections, bulleted lists, and tables that mirror the proposal. Use whenever the user wants to turn a proposal, deck, or engagement pitch into an SOW, SOW attachment, scope-of-work document, or 'contract-ready' version. Triggers: proposal to SOW, convert proposal to SOW, SOW attachment, make an SOW from this deck, turn this proposal into a statement of work, scope of work google doc, contractify this proposal. This produces the project-specific scope attachment (not the MSA legal wrapper). Default output is a Google Doc; a .docx builder is available as a fallback. If the user wants to author an SOW from scratch without a source proposal, use sow-generator instead."
---

# Proposal → SOW Attachment Conversion

Turn an existing proposal deck/doc into a legal SOW attachment. The proposal
is the source of truth for scope, deliverables, timeline, milestones, pricing, RACI,
assumptions, and risks; this skill restructures that content into contract-style
prose with numbered sections and tables.

## What it produces

A **Google Doc** — the **project-specific SOW attachment** (scope sections + signature
block). It intentionally does **not** generate the MSA/Order-Form legal wrapper, which
is attached during signing. An incorporation clause on the cover references that wrapper.
A `.docx` builder (`build_sow.py`) remains available as a fallback when the user wants a
Word file instead of a Google Doc.

## Prerequisites

- **Google Workspace MCP** must be connected (the `create_document` tool) — this is how
  the Google Doc is created. If it is not available, install/enable it (see the
  `google_workspace_install` skill) or fall back to the `.docx` builder.
- Scripts depend on `python-docx`, `python-pptx`, and `pypdf` (see `pyproject.toml`).
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

Build a JSON spec (the single source used by both the Google Doc and `.docx` paths).
**Load `references/spec_schema.md`** for the full
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

### Step 3: Build the Google Doc (native tables)

**Do NOT put tables in the markdown you pass to `create_document`.** Its markdown table
parser is unreliable for multi-table docs — it merges later sections into the first
table's cells. Instead, narrative is created via markdown and every table is built
natively via the Docs API. Generate the ordered build plan:

```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/gdoc_plan.py \
  --spec "/abs/path/spec.json" --output "/abs/path/plan.json"
```

`plan.json` is an ordered list of items, each `{"kind":"md",...}` (narrative) or
`{"kind":"table","headers":[...],"rows":[[...]]}`. Build the document in order:

1. **Create the doc** with the first item (always `md`) via `create_document`
   (`title`: e.g. `"<Client> — <Engagement> | SOW Attachment A"`, `content`: item[0] text).
2. **Walk the remaining items in order**, always appending at the end of the body:
   - `md`  → `append_to_document` with the item text (headings/bold/bullets render fine).
   - `table` → `batch_update_document` with a single
     `{"insertTable":{"rows":R,"columns":C,"endOfSegmentLocation":{}}}` (an EMPTY table;
     do not fill yet). R = len(rows)+1 (header), C = len(headers).
3. **Fill all tables once, after all are placed.** Call `get_document_structure` — it
   returns every table with each cell's `startIndex`. Structure `tables[k]` maps to the
   k-th `table` item in `plan.json` (document order). For each table, generate its fill
   requests:
   ```bash
   uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/gdoc_fill_requests.py \
     --table-json /abs/path/tableK_struct.json --content-json /abs/path/tableK_content.json
   ```
   (`tableK_struct.json` = the single `tables[k]` object; `tableK_content.json` =
   `{"headers":[...],"rows":[[...]]}` from the plan item.) Apply each table's requests with
   `batch_update_document`.
   - **Process tables in DESCENDING document order (last table first).** Filling a table
     inserts text that shifts indices *after* it; going high→low keeps every table's
     snapshot `startIndex` valid. The helper already orders each table's own cell inserts
     back-to-front and bolds the header row.

Optionally `share_with` an email on `create_document`. Capture the returned document `url`.

**Fallback (.docx instead of Google Doc):**
```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/build_sow.py \
  --spec "/abs/path/spec.json" --output "/abs/path/<Client>_SOW_Attachment.docx"
```

### Step 4: Verify

Call `get_document_structure` once more and confirm: the expected number of tables exist,
each header row is populated and bold, no cell contains text bleed from another section
(the classic markdown-table failure), milestone payments total the fixed fee, and the
effort totals row matches. Then open the `url` in the browser.

**⚠️ STOP**: Present the document URL for review.

## Tools

### scripts/extract_proposal.py
`.pptx` / `.pdf` → structured JSON (per-slide/page text + tables).
`--input <file>` (required), `--output <json>` (optional; stdout if omitted).

### scripts/gdoc_plan.py
JSON spec → ordered Google Docs build plan: `md` items (narrative markdown, no tables) and
`table` items (`headers` + `rows`). In-cell bullets are inlined to `• a • b`.
`--spec <json>` (required), `--output <json>` (optional; stdout if omitted).

### scripts/gdoc_fill_requests.py
One empty-table structure (a `tables[k]` object from `get_document_structure`) + its
content (`{headers, rows}`) → a JSON array of Docs API requests (cell inserts back-to-front,
header row bolded) to pass to `batch_update_document`.
`--table-json <json>` (required), `--content-json <json>` (required); prints requests to stdout.

### scripts/spec_to_markdown.py (helper / docx-md)
JSON spec → full markdown (used internally by `gdoc_plan.py`; also handy for a quick
markdown export). Not used to render Google Doc tables.

### scripts/build_sow.py (fallback)
JSON spec → styled SOW `.docx` with auto-numbered sections, bullets, and branded tables.
Use only when a Word file is explicitly wanted instead of a Google Doc.
`--spec <json>` (required), `--output <docx>` (optional; uses `spec["output"]`).

## Stopping Points

- ✋ Step 2: Confirm section mapping + pricing/parity findings before building.
- ✋ Step 4: Final review of the generated document.

## Output

A contract-ready SOW attachment as a **Google Doc** (URL returned by `create_document`),
plus the intermediate `spec.json` and `.md` (reusable/editable for regeneration). A
`.docx` is available via the fallback builder when requested.
