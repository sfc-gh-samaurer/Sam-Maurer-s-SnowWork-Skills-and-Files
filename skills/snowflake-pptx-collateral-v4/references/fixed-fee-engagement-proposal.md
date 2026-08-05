---
name: fixed-fee-engagement-proposal
description: Structure, hours model, two-tier milestone pattern, and honest-TBD doctrine for Snowflake PS proposals where the fee is fixed up front (capacity conversion, investment attach, pre-agreed budget) and scope must be justified against a pinned number.
---

# Fixed-Fee PS Engagement Proposal — Committed-Hours Variant

A variant of `ps-engagement-proposal.md` for engagements where **the price is known before the
scope is**. Build it with the same `snowflake-pptx-collateral-v4` editable PPTX approach (official
template + python-pptx); everything in `core-helpers.md`, `core-branding.md` and the guardrails in
`SKILL.md` still applies.

---

## When to use this instead of `ps-engagement-proposal.md`

| Use this variant when | Use `ps-engagement-proposal.md` when |
|---|---|
| Fee is fixed and known up front — capacity conversion, investment attach, pre-agreed budget | Investment is derived bottom-up from resource loading |
| The job is to **justify credible scope against a pinned number** | The job is to price the scope the customer asked for |
| Customer expects milestone-based invoicing tied to accepted deliverables | A single resource/rate table is sufficient |
| Real unknowns remain but the proposal must ship anyway | Scope is well understood at proposal time |

The tell: someone internally says *"we have roughly $X of capacity to burn"* before anyone has
sized the work. That inverts the normal exercise and this variant exists for that inversion.

## Bundled builder — start here, do not write a deck from scratch

The skill ships a complete, runnable implementation of this variant. Do not hand-roll the geometry.

| File | What it is |
|---|---|
| `assets/build_fixed_fee_proposal.py` | The full 27-slide builder — 10 workstreams, 8 acceptance gates, 4 billing milestones, $220,000 fixed. Runs as-is with placeholder content. |
| `assets/proposal_helpers.py` | Engagement-agnostic helper library + the post-save rendered-height check. Contains no engagement content. |

**Workflow**

1. Copy `assets/build_fixed_fee_proposal.py` into the engagement folder as `build_proposal.py`.
2. Run it unchanged first. It should print `Slides: 27`, `Rendered heights OK`, and the price check.
   That confirms the template resolved and the environment works before you touch content.
3. Edit the **CONFIG** block (fee, duration, contingency, rates, customer, output path).
4. Replace every list in the **CONTENT** block. Structure is the deliverable; the text is example
   text and must not ship.
5. Leave the **BUILD** and **ASSERTS** blocks alone. Geometry is tuned to the 10 × 5.625" canvas and
   the asserts are what keep the fee consistent across six slides.

The builder imports the helper library rather than copying it:

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # or the assets/ path
from proposal_helpers import *
```

If you relocate the build script out of `assets/`, point `sys.path` at the skill's `assets/`
directory instead — do not paste a second copy of the helpers into the engagement folder.

> **What the helper library covers.** Colour constants, `set_bullet` / `clear_bullet`, `set_ph`,
> `add_shape_text`, `add_rect`, `add_textbox`, `content_chrome`, `set_table_borders`, `style_cell`,
> `cell_bullets`, `simple_table`, `add_kpi`, `add_card`, `narrative_panel`, `new_deck` / `save_deck`,
> and `est_table_bottom` / `verify_rendered_heights`. `resolve_template()` globs the skill install
> root, so the same script works from any machine.

### Asserts the bundled builder already enforces

Beyond the four documented in §1.3, the shipped script also checks that the fee does not land more
than $1,000 under the presented number, that BM1 stays at or below 25%, and that the `Base Hrs`
column on the scope slides agrees row-for-row with the effort table. That last one catches the most
common editing mistake: rebalancing hours in `EFFORT` and forgetting the scope slides.

---

## 1. The central invariant

> **Fee = committed hours × role rates.** Say this on the pricing slide, then enforce it in code.

Because the fee is pinned, every later scope change is a **redistribution**, never an addition.
That single idea drives the whole build.

### 1.1 Hours model

```
base hours per (workstream × role)
  → per-role column totals            ← THE LOAD-BEARING CONSTRAINT
  → + contingency %                   (25% is the working default)
  → committed hours per role
  → × role rate = fixed fee
```

Worked example ($220K — the values shipped in `assets/build_fixed_fee_proposal.py`):

| Role | Base | +Contingency | Committed | Rate | Extended |
|---|---|---|---|---|---|
| Sr. Solution Architect | 160 | +40 | 200 | $335 | $67,000 |
| Consultant / Data Engineer | 352 | +88 | 440 | $305 | $134,200 |
| Project Manager (SDM) | 58 | +14 | 72 | $260 | $18,720 |
| **Total** | **570** | **+142** | **712** | — | **$219,920** |

Presented as **$220,000**. Landing a few hundred dollars under a round number is normal and
desirable — never inflate hours to hit the round number exactly.

### 1.2 The rule that keeps the price stable

**When you rebalance scope, redistribute base hours *across* workstreams while holding the
per-role column totals constant.** Add a workstream, delete one, split one — as long as the Sr. SA
/ Consultant / PM columns still total 160 / 352 / 58, the fee is untouched and no other slide needs
repricing.

Put this as a comment directly above the effort table in the build script:

```python
# INVARIANT: column totals must stay SA=160, C=352, PM=58 → committed 200/440/72 → $219,920.
# Redistribute across workstreams freely; never change the column totals.
effort = [
    # (num, name, phase, sr_sa, consultant, pm)
    ("1", "Project Setup & Kickoff", "0", 8, 16, 4),
    ...
]
```

### 1.3 Build-time asserts — non-negotiable

A fixed-fee deck has four numbers repeated across six slides. Asserts are the only thing that keeps
them consistent through edits. Every fixed-fee build script ends with:

```python
assert tot_sa == 160 and tot_c == 352 and tot_pm == 58, \
    f"role column totals drifted: {tot_sa}/{tot_c}/{tot_pm} — fixed fee is now wrong"
assert COMMIT_SA * RATE_SA + COMMIT_C * RATE_C + COMMIT_PM * RATE_PM == 219_920, \
    "committed hours no longer price to the stated fee"
assert sum(b.fee for b in bm) == 220_000, f"billing milestones sum to {sum(...)}, expected 220000"
assert sum(b.hrs for b in bm) == COMMIT_TOT, "billing hours != committed hours"
```

The last two caught real drift during a mid-flight scope expansion. Keep them when editing.

---

## 2. Two-tier milestone model

Fixed-fee engagements need **two separate milestone tracks**. Do not collapse them — they answer
different questions and different people read them.

| | Acceptance gates | Billing milestones |
|---|---|---|
| Label | `M1 … Mn` | `BM1 … BMn` |
| Count | One per phase-end — 7–8 typical | **4** is the right number |
| Question answered | "Is this deliverable done and correct?" | "When do we invoice?" |
| Audience | Delivery leads, technical SMEs | Procurement, finance |
| Slide | Milestones and Acceptance Gates | Milestone Payment Schedule |

**Mapping rules**
- Each BM covers a **contiguous** gate range *and* a contiguous workstream range. Never interleave.
- Allocate the fee **pro-rata to committed hours**, not evenly:
  `bm_hours = round(ws_base_hours × COMMIT_TOT / BASE_TOT)`
- Then hand-tune the fees to round thousands that sum **exactly** to the fee. Show the percentage.
- State on the slide that allocation is pro-rata and does not change the fixed fee.

Worked example (712 committed hrs → $220,000):

| BM | Name | Gates | Hrs | Fee | % |
|---|---|---|---|---|---|
| BM1 | Design Accepted | M1–M2 | 130 | $40K | 18.2% |
| BM2 | Ingestion & CDC Validation Accepted | M3–M4 | 185 | $57K | 25.9% |
| BM3 | History Model & Freshness Accepted | M5–M6 | 187 | $58K | 26.4% |
| BM4 | Consumption, Second Domain & Closure | M7–M8 | 210 | $65K | 29.5% |

Front-loading is a red flag to procurement; a gentle back-weighting (largest BM last) reads as
confidence. Avoid a BM1 above ~25%.

---

## 3. Slide inventory

27 slides. Most are shared with `ps-engagement-proposal.md`; six are specific to this variant.

| # | Slide | Status |
|---|---|---|
| 1 | Cover (Layout 13) | shared |
| 2 | Proposal Content / Agenda | shared |
| 3 | Executive Summary + Objectives | shared |
| 4 | **Current State and Target State** | **NEW** |
| 5–7 | Workstream Scope Summary (1/3 … 3/3) | shared, `Base Hrs` column added |
| 8 | Engagement Deliverables | shared |
| 9 | **Project Timeline — Gantt with acceptance-gate diamonds** | **NEW** |
| 10 | Milestones and Acceptance Gates | shared |
| 11 | **Open Scope Items and Pending Inputs** | **NEW** |
| 12 | **Customer Dependencies and Commitments** | **NEW** |
| 13–14 | Snowflake / Customer Roles and Responsibilities | shared |
| 15 | Engagement RACI | shared |
| 16 | Assumptions and Exclusions | shared |
| 17 | **Resource Effort and Contingency** | **NEW** |
| 18 | Risks and Mitigations | shared |
| 19 | Pricing | shared, reframed on committed hours |
| 20 | **Milestone Payment Schedule** | **NEW** |
| 21 | Next Steps | shared |
| 22 | Appendix divider (Layout 18) | shared |
| 23–26 | Appendix: architecture, mechanics, data model, option comparison | engagement-specific |
| 27 | Thank You (Layout 28) | shared |

### 3.1 Current State and Target State (slide 4)

Two-column `Today → Target` native table, 7–8 rows. Today column in `TBL_GREY` regular, Target
column in `DK1` **bold** — the asymmetry does the persuading. One row per dimension the engagement
actually changes (cadence, history, deletes, schema drift, interface, consumption, repeatability).

Place it **before** any scope slide. It earns the scope rather than asserting it.

### 3.2 Open Scope Items and Pending Inputs (slide 11)

The single most useful slide in this variant, and the reason you never have to invent scope.

- 2×2 `add_card` grid. One card per genuine unknown.
- Each card: 3–4 lines, each ending `: TBD`, plus one line naming **where it closes** ("Selected at
  the M2 gate", "Effort shown is a placeholder").
- Bottom `LIGHT_BLUE` rounded bar: **PENDING INPUTS FROM \<CUSTOMER\>** — the concrete artefacts you
  are waiting on (DDL, ERD, samples, written acceptance criteria).

This slide is what makes a fixed fee credible in the presence of unknowns: it shows the unknowns are
*catalogued and owned*, not glossed over.

### 3.3 Customer Dependencies and Commitments (slide 12)

Columns: `#` · Commitment · Customer Owner · Required By · **Impact if Delayed**.

The Impact column is the point. Without it this is a wish list; with it, it is the contractual basis
for a schedule-relief conversation. Every row must name a real consequence ("Blocks design; extends
Discovery and risks M2"), never "may cause delays."

### 3.4 Resource Effort and Contingency (slide 17)

Native table: `#` · Workstream · Phase · Sr. SA · Consultant · PM/SDM · Base Hrs, then three
summary rows — **Base Total** (`LIGHT_BLUE`), **+ N% Contingency** (`LIGHT_BLUE`), **Total Committed
Capacity** (`DK2` / white).

Footnote must state what the contingency is *for* (name the two or three specific risks it absorbs)
and that **unused contingency is not billed**. A contingency with no stated purpose reads as padding.

### 3.5 Milestone Payment Schedule (slide 20)

KPI row of 4 boxes (`BM label` / `$fee` / `% of fixed fee`, alternating `DK2`/`SF_BLUE`), then the
allocation table: `#` · Billing Milestone · Phases/WS · Deliverables Accepted · Gates · Hrs · Fee,
with a `DK2` total row. Close with a `LIGHT_BLUE` note on invoicing trigger and pro-rata basis.

### 3.6 Gantt with acceptance-gate diamonds (slide 9)

Standard Gantt plus numbered `MSO_SHAPE.DIAMOND` markers in `ORANGE` with dark text, placed on the
**workstream row that owns the gate**, at the gate week. Then a 3-column legend below the grid
(`W{n} — {label}`) so the diamonds are readable without cross-referencing slide 10.

Also: put the phase tag (`P0`–`P4`) in a narrow column left of the workstream label, and give
Program Management its own `TEAL` full-width row at the bottom.

**Geometry that fits** (slide is 5.625" tall, footer at 5.32"):

| Workstream rows + PM | `rowh` | `step` |
|---|---|---|
| ≤ 10 | 0.215 | 0.26 |
| 11–12 | 0.20 | 0.24 |

`grid_bottom = rows_y0 + n_rows × step`; legend pitch 0.215 in 3 columns; note textbox below that.
Verify the note's bottom edge lands under 5.30".

---

## 4. Honest-TBD doctrine

A fixed fee creates pressure to invent scope. Don't. The discipline:

1. **Never fabricate a workstream to absorb budget.** Reviewers and the customer's technical staff
   detect it, and it poisons the credible parts of the deck.
2. **Name the unknown, its owner, and its closing gate.** An unknown with a resolution path is a
   managed risk; an unnamed one is a surprise.
3. **Tag placeholder workstreams `[SCOPE TBD]`** in the WS title and mirror the tag in the
   deliverables row. **Remove the tag the moment it closes** — a stale TBD on resolved scope makes
   the whole deck look unmaintained. (This happened: OpenFlow connectivity was validated between
   revisions and the `[SCOPE TBD]` tag plus the matching HIGH risk both had to come out.)
4. **Prefer a visible allowance over silent padding.** "WS7 carries a placeholder allowance" is
   honest; quietly inflating WS5 by 40 hours is not.

---

## 5. Internal candor never reaches customer collateral

Internal scoping calls produce blunt assessments. They shape the deck; they never appear in it.
Translate rather than delete — the underlying concern is usually real and belongs in scope or risk.

| Said internally | Customer-facing translation |
|---|---|
| "This connector isn't mature, we'll probably hit bugs" | A dedicated validation workstream + a named escalation path into the product engineering team |
| "For these tables SCD2 is maybe a week of work" | (never surfaced) — but keep scope generous and the contingency visible |
| "Cross-region CDC will be expensive and I've seen nobody do it" | A MEDIUM risk with cost/latency measured early and a named alternative topology |
| "Hardest part is getting them to sign a contract" | (never surfaced) — reflected as pre-kickoff dependencies with owners |

> **Hard rule.** If a specialist says *"don't soften this externally"* about a product's maturity,
> that is a direct instruction. Represent the concern as **scope and rigour on our side**, never as
> a caveat about the product. "GA connector + dedicated validation workstream" — not "you are an
> early adopter."

---

## 6. Expanding scope when the fee exceeds the obvious work

When honest sizing lands well under the fixed fee, add scope in this order. Each rung is real,
defensible work rather than padding, and each strengthens the deck's story.

1. **Testing / validation workstream** — structured test suite, edge cases, load and latency
   measurement, failure/recovery paths, defect triage with an escalation path. Almost always
   under-scoped in a first draft, and it earns its own gate.
2. **Semantic view / consumption layer** — turns raw ingestion into something a business user
   touches. Converts a plumbing project into a data-product project.
3. **Reusable pattern + one additional domain** — templatize the build and prove it once more.
   Frame as *pattern repeatability*, not "a second dataset," so the specific dataset stays a
   Discovery decision instead of a commitment you can't size yet.
4. **Value-case framing as a risk** — if the customer hasn't articulated business value, say so as
   a MEDIUM risk mitigated by items 2 and 3. This converts an internal criticism into visible rigour.

Never reach for: padding existing workstream hours, inflating contingency above ~25%, or adding
knowledge-transfer sessions as filler.

---

## 7. Checklist (fixed-fee specific — run alongside `verification.md`)

- [ ] Built from `assets/build_fixed_fee_proposal.py`, not hand-rolled; helpers imported not copied
- [ ] No placeholder text from the shipped example survives anywhere in the deck
- [ ] Role column totals match the documented invariant; all asserts pass
- [ ] Committed hours × rates equals the stated fee (within rounding *down* to the presented number)
- [ ] Billing milestones sum exactly to the fee **and** to committed hours
- [ ] No billing milestone exceeds ~25% at BM1; largest BM is at or near the end
- [ ] Every `[SCOPE TBD]` tag corresponds to a live card on the Open Scope slide — and none survives
      on scope that has since closed
- [ ] Every Customer Dependency row has a named owner and a concrete Impact-if-Delayed consequence
- [ ] Contingency footnote names the specific risks absorbed and states unused contingency is unbilled
- [ ] Pricing slide states the fee is based on committed hours, not elapsed weeks
- [ ] Each acceptance gate M1…Mn appears on both the Gantt (diamond) and the milestone table
- [ ] Gantt row geometry matches the table in §3.6 and the note clears 5.30"
- [ ] No internal candor survives anywhere in the deck, including speaker notes
- [ ] Content-aware table-height check run (see `verification.md` → Rendered Table Height)
