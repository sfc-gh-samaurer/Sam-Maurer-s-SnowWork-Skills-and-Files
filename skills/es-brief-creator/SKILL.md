---
name: es-brief-creator
description: "Create the one-slide ES Brief PPTX used to qualify a deal as an Engineering Solution. Builds from an existing proposal deck (.pptx/.pdf) or from a plain description when no deck exists, filling the standard ES Brief template: customer, engineering solution, solution description, the challenge, desired outcomes, and comments against the three fixed ES qualification criteria. Use when the user asks for an ES brief, ES qualification brief, engineering solution brief, ES review slide, ES submission, or asks to qualify a deal as an Engineering Solution."
---

# ES Brief Creator

Produces a single-slide ES Brief from the standard template. The template has no
autofit, so overlong text is silently clipped on render — the builder enforces
per-field character caps as hard failures rather than letting a clipped slide
ship.

## Prerequisites

Scripts declare their own dependencies; run them with `uv` so they resolve:

```bash
uv --version
```

## Workflow

### Step 1: Establish the source

Two paths:

- **From a proposal** (preferred when one exists) — confirm the file path, then:
  ```bash
  uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/extract_proposal.py \
    --input "/abs/path/proposal.pptx" --output "/abs/path/proposal_extract.json"
  ```
  Read the JSON. Executive summary, objectives, scope, milestone, and pricing
  slides carry nearly everything the brief needs.

- **From a description** — no deck yet. Gather the customer, what they do, the
  current-state gap, the intended outcomes, and the commercial shape (fee,
  duration, milestone count) from conversation context. Ask only for what is
  genuinely missing.

### Step 2: Draft the content spec

**Load `references/content-guide.md`** for how to write each field, then write a
JSON spec:

```json
{
  "customer": "Acme, Inc.",
  "short_name": "Acme",
  "engineering_solution": "Short name for what SD builds",
  "overview": "What they do + current-state fact. <=208 chars.",
  "challenge": "The concrete gap. What is manual, missing, ungoverned. <=208 chars.",
  "outcomes": ["End-state capability", "..."],
  "qualification": {
    "New Solution Ownership": "What SD builds from scratch. <=136 chars.",
    "Production-Ready Delivery": "How it lands live + validation. <=136 chars.",
    "Fixed Price Contract": "Fee, duration, milestone structure. <=136 chars."
  }
}
```

The three qualification keys are fixed by the ES program — the builder rejects
any others. Max five outcome bullets, 52 chars each. `short_name` is optional and
controls the slide title only; omit it to use `customer`.

**Assess fit honestly.** If the scope is largely configuration of native
Snowflake features or largely advisory, the New Solution Ownership criterion is
weak. Say so plainly instead of inflating the comment.

**⚠️ STOP**: Present the drafted content and your read on qualification fit —
including any criterion you consider weak — and confirm before building.

### Step 3: Build

```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/build_es_brief.py \
  --content "/abs/path/content.json" \
  --output "/abs/path/ES Brief - <Customer>.pptx"
```

The script validates every field against its cap before touching the template
and exits non-zero with the offending text and the exact overage if anything
would clip. Trim and re-run — do not raise the caps.

After writing, it re-opens the file and asserts no paragraph would render blank
(see the `endParaRPr` trap in `references/template-map.md`).

### Step 4: Verify and hand off

Open the deck for the user (`open <path>`) — layout cannot be verified
programmatically beyond the caps and paragraph-structure asserts, and there is
no reliable local PPTX renderer on a managed laptop.

**⚠️ STOP**: Present the path and ask the user to eyeball the slide.

## Tools

### scripts/build_es_brief.py
JSON content spec → one-slide ES Brief `.pptx`. Validates character caps, clones
template paragraph protos to preserve formatting, and post-verifies paragraph
structure. `--content` (required), `--output` (required), `--template` (optional;
defaults to the bundled `assets/es_brief_template.pptx`).

### scripts/extract_proposal.py
`.pptx` / `.pdf` → JSON (per-slide text + tables). `--input` (required),
`--output` (optional; stdout if omitted).

## References

- `references/template-map.md` — shape IDs, paragraph protos, character caps, and
  the two silent-failure traps. Read before changing the builder.
- `references/content-guide.md` — how to write each field and how to judge
  qualification fit. Read before drafting content.

## Stopping Points

- ✋ Step 2: Confirm content and qualification fit before building.
- ✋ Step 4: User reviews the rendered slide.

## Output

`ES Brief - <Customer>.pptx` (one slide) plus the reusable `content.json`.
