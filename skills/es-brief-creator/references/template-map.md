# ES Brief Template Map

Single slide, 10 x 5.63 in, Google-Slides origin. Shape IDs are stable across
copies of `assets/es_brief_template.pptx`. The two content cards are nested
inside groups (200, 203, 206), so lookup must recurse.

| Shape | Role |
|-------|------|
| 199 | Title placeholder — `ES Brief: {Customer}` |
| 202 | Dark header bar — 2 paragraphs, each a bold accent label run + plain white value run |
| 205 | Left card — Solution Description |
| 208 | Right card — ES Qualification Criteria Comments |
| 209 | Confidentiality strip (leave alone) |

## Paragraph protos

Rebuilding a card means deep-copying one of its ORIGINAL paragraphs and swapping
the run text. Each proto carries the formatting for its role:

**Shape 205 (left card)**

| Proto | Formatting | Used for |
|-------|-----------|----------|
| 0 | 14pt bold, navy #11567F | section head |
| 1 | 10pt body | overview paragraph |
| 2 | 10pt bold | `The Challenge:` label |
| 3 | 10pt body | challenge paragraph |
| 4 | 12pt bold | `Desired Outcomes` subhead |
| 5 | 10pt bullet | each outcome bullet (clone N times) |

**Shape 208 (right card)**

| Proto | Formatting | Used for |
|-------|-----------|----------|
| 0 | 14pt bold, 2 runs | section head (split across two runs) |
| 1, 3, 5 | 12pt bold | criterion label |
| 2, 4, 6 | 12pt body | criterion comment |

## Render limits — the reason this skill exists

The template has **no autofit**. Overflowing text is clipped at render time and
every programmatic check still passes, so the defect is invisible until someone
opens the deck. `build_es_brief.py` asserts these:

| Field | Cap |
|-------|-----|
| Overview paragraph | 208 chars |
| Challenge paragraph | 208 chars |
| Outcome bullet | 52 chars each, max 5 bullets |
| Qualification comment | 136 chars each |

## Two silent-failure traps

**1. `a:endParaRPr` ordering.** Per the DrawingML schema `endParaRPr` must be the
LAST child of `a:p`. Cloned paragraphs carry one. If runs are appended after it,
python-pptx reads the text back correctly but **PowerPoint renders the entire
paragraph blank**. `strip_endpara()` removes it before appending; `verify()`
re-opens the saved file and asserts the invariant holds.

**2. `text_frame.text = ...` destroys formatting.** It collapses the paragraph to
a single unformatted run, wiping the bold labels, navy heads, and bullet glyphs.
Always clone protos instead.
