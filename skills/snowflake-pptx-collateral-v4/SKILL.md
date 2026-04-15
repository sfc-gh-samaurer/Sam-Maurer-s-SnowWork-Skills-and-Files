---
name: snowflake-pptx-collateral-v4
description: "Create professional Snowflake-branded PowerPoint (PPTX) decks. Designs slides in HTML/CSS first (world-class visual quality), then converts to PPTX in one of two modes: (1) Image Mode — pixel-perfect PNG slides, not editable; (2) Editable Mode — native python-pptx shapes and text boxes, fully editable in PowerPoint. Use for: presentations, business reviews, district reviews, customer decks, summary slides, status updates, executive presentations. Triggers: PPTX, PowerPoint, deck, slides, presentation, create deck, build slides, business review deck, summary slide."
allowed-tools: Bash, Read, Write
log_marker: SKILL_USED_RENDER_PPTX
skill_version: "2026-04-15"
---

<!--
  ┌─────────────────────────────────────────────────┐
  │  QUICK INSTALL                                  │
  │                                                 │
  │  1. Place this folder anywhere on your machine  │
  │  2. Run:                                        │
  │     cortex skill add /path/to/snowflake-pptx-collateral │
  │  3. Start a Cortex Code session and ask it to   │
  │     create a PPTX deck                          │
  │                                                 │
  │  Requires: pip install python-pptx playwright   │
  │            playwright install chromium           │
  └─────────────────────────────────────────────────┘
-->

# Snowflake PPTX Collateral Generator

Generate polished, Snowflake-branded PowerPoint decks using an **HTML-first design workflow**. Slides are designed in HTML/CSS for maximum visual quality, then converted to PPTX in one of two modes:

| Mode | Description | Editable in PowerPoint? |
|------|-------------|------------------------|
| **Image** | Playwright screenshots each HTML slide and inserts as a full-bleed PNG | No — design-only |
| **Editable** | python-pptx recreates each slide as native shapes, text boxes, and tables | Yes — fully editable |

Both modes use the same HTML/CSS design system as the visual source of truth. Image mode preserves 100% design fidelity. Editable mode preserves all layout, color, typography, and content — with minor approximations for CSS features python-pptx cannot replicate (gradients, border-radius, clip-paths).

---

## ⚠ Quality Guardrails (Read Before Writing Any Slide)

### Top Failure Modes — Catch These Before They Happen

0. **PLAN CONTENT BEFORE DESIGN** — Content Blueprint (Phase 4 in `interaction-model.md`) is mandatory. Specify a visual pattern for EVERY content slide before writing HTML.
1. **Cover title ≤ 50 characters** — punchy 4–6 words. Details go in subtitle.
2. **At least 50% of content slides MUST use a visual pattern** (card grid, KPI row, table, timeline, two-column, hub-spoke) — NEVER produce 3+ consecutive bullet-only slides.
3. **TEAL and ORANGE fills ALWAYS use dark text, NEVER WHITE** — These are light accent colours. White text on them is unreadable. See Fill→Text table in `core-branding.md`.
4. **Dark-background slides need white text on all custom shapes** — Chapter dividers, covers, and quote slides have dark fills. Enforce explicitly in python-pptx Editable mode.
5. **ALL CAPS for titles** — slide titles and cover titles, always.
6. **Content must not extend below `top:490px`** in HTML — respect the safe zone.
7. **No generic placeholder text** — never use "Item 1", "TBD", "placeholder", or filler content.
8. **Editable mode: every custom shape via `add_shape_text()`** — copy from `core-helpers.md` Section 12.7. NEVER set text on python-pptx shapes directly. It enforces Arial font, auto_size, no-outline, contrast correction.
9. **Editable mode: Cover slide PH mapping** — Layout 13 → PH[3]=44pt title, PH[0]=subtitle, PH[2]=author. See `core-helpers.md` Section 10.1.
10. **Multi-line text uses `\n` in a single string** in python-pptx — NEVER separate runs.
11. **Google Drive default save** — save to `~/Google Drive/My Drive/` so files sync automatically. See `core-helpers.md` Section 18.

### Dark-Background Constant (Editable Mode — Copy Into Every Script)

```python
DARK_BG_LAYOUTS = {9, 10, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28}
COVER_LAYOUTS   = {13, 14, 15, 16, 17}
```

Custom shapes on these layouts MUST use `WHITE` text. `add_shape_text()` auto-corrects `DK1→WHITE` on dark layouts.

### Fill → Text Contrast (NEVER guess)

```python
FILL_TEXT = {
    "DK2":     WHITE,   # dark navy → white
    "SF_BLUE": WHITE,   # Snowflake blue → white
    "TEAL":    DK1,     # ⚠ LIGHT fill → DK1 dark text (NEVER WHITE)
    "ORANGE":  DK1,     # ⚠ LIGHT fill → DK1 dark text (NEVER WHITE)
    "VIOLET":  WHITE,   # dark purple → white
}
```

---

## Workflow

### Step 1: Gather Requirements

**Ask** the user:
1. **Deck purpose**: Business review, customer proposal, status update, summary slide, etc.
2. **Slide count & types**: What slides do they need? (See slide type catalog below)
3. **Content source**: Do they have data ready, or should we generate/query it?
4. **Output path**: Where to save the .pptx file (default: Google Drive if available, else `~/Downloads/`)
5. **Output mode** *(optional — default is Editable)*: Image-only (pixel-perfect, not editable) or Editable (native PowerPoint shapes and text)?

**Mode guidance to offer the user:**
- **Editable mode** *(DEFAULT)* — native python-pptx shapes and text boxes, fully editable in PowerPoint. Use this unless the user explicitly requests image-only.
- **Image mode** — Playwright screenshot of the HTML, pixel-perfect design fidelity. Use only when the user explicitly asks for image/screenshot mode or maximum design fidelity is the top priority.

### Step 2: Plan Slide Structure

Design the deck using the interaction model in `references/interaction-model.md`. The key deliverable at this step is the **Content Blueprint** — a slide-by-slide plan with title, subtitle, content, and visual pattern specified for each slide.

**Present** the proposed slide-by-slide outline to the user.

**STOP**: Get approval before writing any HTML or code.

### Step 3: Generate HTML Slide Files

> **PRIMARY WORKFLOW** — See `references/html-slide-design.md` for the full design system, CSS tokens, and 12 ready-to-use slide type templates.

For each slide in the approved Content Blueprint:

1. Create a `slides/` directory in the output location
2. Write one HTML file per slide: `slides/slide_01_cover.html`, `slides/slide_02_agenda.html`, etc.
3. Base each file on the appropriate template from `references/html-slide-design.md`
4. Paste the CSS design tokens block at the top of every slide's `<style>` section
5. Fill in the actual slide content (title, bullets, data, team names, etc.)
6. Ensure **every slide is exactly 960×540px with `overflow: hidden`** — no exceptions

**Design rules (enforced):**
- Titles in **ALL CAPS**, 18px bold, `--sf-dark-text` on light backgrounds, white on dark
- Use CSS variables from the design token block — never invent colors
- At least 50% of content slides must use a visual pattern (card grid, KPI row, table, timeline, two-column) — not just a bullet list
- Cover, Chapter, and Thank You slides use dark/blue backgrounds; all content slides use white
- Left edge bar (4px `--sf-blue`) on every content slide at `left:0; top:36px; height:38px`
- Footer text at `top:511px` on every content slide: "Confidential — Snowflake Professional Services"
- Content must not extend below `top:490px` (the safe-bottom zone)

### Step 3b: Verify HTML Dimensions

Before batch conversion, open 1–2 slides in a browser and confirm:
- Slide renders at exactly 960×540px
- No horizontal or vertical scrollbars appear
- All content is visible within the slide boundary

If any content overflows, reduce font sizes or trim content before proceeding.

### Step 4a: Convert HTML → PPTX (Image Mode)

> Use this path **only** when the user explicitly selected **Image mode**. The default is Editable Mode (Step 4b).
> **CONVERSION SCRIPT** — See `references/html-to-pptx-conversion.md` for the full Playwright conversion script.

**CRITICAL RULE — IMAGE-ONLY PPTX:**
The PPTX output is an image-only deck. Every slide is a single full-bleed PNG screenshot of its HTML source, inserted to fill the entire 10"×5.625" slide area. **No text boxes, shapes, titles, placeholders, speaker notes, or layout elements are added to PPTX slides by python-pptx.** The Playwright screenshot IS the complete slide. Never deviate from this.

- Design quality is 100% determined by the HTML/CSS source
- To change anything about a slide's appearance, edit its `.html` file and reconvert — do not attempt to patch the PPTX directly
- This is the intentional architecture: HTML is the source of truth; PPTX is the distribution format

1. Write `convert_to_pptx.py` using the template from `references/html-to-pptx-conversion.md`
2. Install dependencies if not already present:
   ```bash
   pip install python-pptx playwright
   playwright install chromium
   ```
3. Run the conversion:
   ```bash
   python convert_to_pptx.py "OutputDeck.pptx" "slides/slide_*.html"
   ```
4. **Confirm** the `.pptx` file was created and report the file path
5. **Offer** to adjust any slide's HTML and reconvert

---

### Step 4b: Convert HTML → Editable PPTX (Editable Mode) — DEFAULT

> **This is the default output mode.** Use this path unless the user explicitly requested Image mode.
> **IMPLEMENTATION GUIDE** — See `references/html-to-editable-pptx.md` for the full python-pptx builder patterns.

In editable mode, the HTML slides serve as the visual specification. Write a Python script that implements each slide as native python-pptx objects using the patterns from `references/html-to-editable-pptx.md`.

**What is preserved exactly:**
- All text content, font sizes, bold/italic, color values
- Tables with styled header rows and alternating data rows
- Layout geometry (positions and sizes derived from CSS px ÷ 96 = inches)
- Brand colors, edge bars, footers, section headers
- KPI boxes, card grids, two-column layouts, RACI tables

**What is approximated (CSS features python-pptx cannot replicate):**
- `linear-gradient` backgrounds → solid fill with the dominant color
- `border-radius` on cards → square rectangle corners
- `clip-path` waves/diagonals → omitted or replaced with a solid shape
- `box-shadow`, `opacity`, `::before/::after` decorations → omitted

1. Read `references/html-to-editable-pptx.md` for the full builder function library
2. Write a Python script that calls the appropriate builder for each slide, passing real content
3. Load `references/core-helpers.md` — defines `add_shape_text()`, `set_ph()`, saving, and all brand constants
4. Install dependency: `pip install python-pptx`
5. Run the script and confirm the `.pptx` was created
6. **Offer** to adjust any slide and regenerate

**Editable Mode Output — Default Save Location:**
```python
import os
GDRIVE_DIR = os.path.expanduser("~/Google Drive/My Drive")
deck_name = "My_Deck"
if os.path.isdir(GDRIVE_DIR):
    output_path = os.path.join(GDRIVE_DIR, f"{deck_name}.pptx")
else:
    output_path = os.path.expanduser(f"~/Downloads/{deck_name}.pptx")
    print(f"⚠ Google Drive not found — saving to {output_path}")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
prs.save(output_path)
print(f"Saved: {output_path}")
```

---

## Slide Type Catalog

> All slide types are implemented in HTML/CSS. Use the templates in `references/html-slide-design.md` as your starting point for each type.

### Cover Slide
- Dark gradient background (`var(--sf-mid-blue)` to `#0c3351`)
- Decorative wave, background circles, diagonal overlay for depth
- Large title: ALL CAPS, 36–44px bold, white, **≤ 50 characters**
- Rule/divider line in `var(--sf-teal)` below subtitle
- Subtitle, date, and team meta line in white with reduced opacity
- Right accent bar + customer badge (top-right corner)

### Chapter / Section Divider
- Dark gradient background, same family as Cover
- Ghost oversized chapter number (3–5% opacity) as background texture
- Vertical teal accent bar on the left edge
- Chapter label (e.g. "Chapter 01") in `var(--sf-teal)`, small caps
- Title: ALL CAPS, 44–52px bold, white, 2-line max
- Subtitle below in white at 55% opacity
- Bottom strip gradient in teal→blue

### Content Slide (default)
- White background
- Left edge bar: 4px `var(--sf-blue)` at `left:0; top:36px; height:38px`
- Title: ALL CAPS, 18px bold, `var(--sf-dark-text)`, `top:29px; left:38px`
- Subtitle: 12px, `var(--sf-body-grey)`, `top:56px`
- Content area starts at `top:96px`
- Footer: 7px, `var(--sf-body-grey)`, `top:511px`
- Content must not extend below `top:490px`

### KPI / Big Numbers Slide
- Content slide base
- KPI row: 3–4 equal-width boxes in `var(--sf-mid-blue)` or `var(--sf-blue)`
- Each box: large number (28–36px bold white), label below in teal/muted white
- Optional table or detail content below the KPI row

### Card Grid Slide (3-up, 4-up, 2×N)
- Content slide base
- Cards: rounded corners (8px), header strip in `var(--sf-mid-blue)` or `var(--sf-blue)`, light grey body
- Card header: icon + title in ALL CAPS white
- Card body: 8.5–9px body text in `var(--sf-dark-text)`

### Two-Column Slide
- Content slide base
- Left and right columns with distinct header colors (dark vs accent)
- Column headers include a label (e.g. "Today") and bold title in white
- Column bodies in `var(--sf-light-bg)` with bullet sections

### Table Slide
- Content slide base
- Table header row: `var(--sf-mid-blue)` background, white bold text, 9px
- Alternating rows: `var(--sf-light-row)` and white
- Cell text: 8.5–9px, `#717171` for data, bold `var(--sf-dark-text)` for first column
- Optional badges/tags in cells using small inline `<span>` elements

### Timeline Slide
- Content slide base
- Phase header bars: phase 1 in `var(--sf-mid-blue)`, phase 2 in `var(--sf-blue)`
- Track columns below with workstream rows, dividers, and milestone callouts
- Milestone bars pinned to the bottom of each phase column

### Team Cards Slide
- Content slide base
- Two groups: Snowflake team (dark gradient card backgrounds) + client team (light backgrounds)
- Each card: avatar icon + name, role (teal for SF team, grey for client), bio text
- Section labels with top border dividers

### RACI Table Slide
- Content slide base
- Standard table layout with role columns
- R/A/C/I badges as small colored circles inline
- Legend row at the bottom of the slide (inside safe zone)

### Ways of Working Slide
- Content slide base — typically 4-column card grid
- Each column: icon + title header, bullet list of norms in body
- Header colors vary across columns for visual separation

### Thank You / Closing Slide
- Dark gradient background, similar to Cover
- Left accent bar, decorative wave + ring shapes
- Snowflake icon, large "Thank You" in ALL CAPS white
- Subtitle + numbered next steps list
- Contact card (right side): frosted glass panel with team names, roles, emails

---

## Font Size Hierarchy

All sizes are CSS pixels in the HTML source. At 96dpi (960px = 10"), these map 1:1 to print points.

| Element | CSS Size | Weight | Color CSS var |
|---------|----------|--------|---------------|
| Cover title | 36–44px | 700 | `#fff` |
| Chapter title | 44–52px | 700 | `#fff` |
| Slide title (content) | 18px | 700 | `--sf-dark-text` |
| Slide subtitle | 12px | 400 | `--sf-body-grey` |
| Card / section title | 10–12px | 700 | `#fff` (on dark) / `--sf-mid-blue` (on light) |
| Body text | 9–10px | 400 | `--sf-dark-text` |
| Bullet text | 8.5–9.5px | 400 | `--sf-dark-text` |
| Table header | 9px | 700 | `#fff` |
| Table data | 8.5–9px | 400 | `#717171` |
| KPI value | 28–36px | 700 | `#fff` |
| Footer | 7px | 400 | `--sf-body-grey` |

---

## Color Usage Rules (from Brand Guidelines)

- **Titles**: SF_DARK_TEXT (#262626) on light backgrounds
- **Accent/Sections**: SF_BLUE or SF_MID_BLUE
- **Secondary colors** (Star Blue, Valencia, Purple Moon, First Light): use very sparingly
- **Snowflake Blue as text color**: minimum 28pt for accessibility
- **TEAL/ORANGE fills**: ALWAYS use dark text — NEVER white (light accent colours)
- **Dark backgrounds** (chapter dividers, covers, quote slides): ALWAYS white text
- **Do not** use non-brand colors
- See `core-branding.md` for full palette and Fill→Text contrast rules

---

## Stopping Points

- STOP after Step 2 (slide structure / Content Blueprint approval)
- STOP after Step 3b (verify HTML dimensions in browser before converting)
- STOP after Step 4a or 4b (present PPTX file path, offer per-slide adjustments)

**Resume rule:** On approval, proceed directly to next step.

---

## Output

**Image mode:** A `.pptx` file where every slide is a full-bleed PNG image — a Playwright screenshot of its HTML source inserted to fill the entire 10"×5.625" slide area. No editable shapes or text boxes. 1920×1080 retina quality.

**Editable mode:** A `.pptx` file with native shapes, text boxes, and tables — fully editable in PowerPoint, Keynote, and Google Slides. Layout, colors, and typography match the HTML design system. Some CSS decorative effects (gradients, rounded corners, clip-paths) are approximated with flat shapes.

In both modes:
- Slides match Snowflake January 2026 brand guidelines
- Arial font, official Snowflake color palette, ALL CAPS titles
- Confidential footer on every content slide
- HTML/CSS source files are kept as the design source of truth
- **Default save: `~/Google Drive/My Drive/` (syncs to Google Drive)**

---

# Reference Files

| File | Purpose |
|------|---------|
| `references/html-slide-design.md` | **PRIMARY** — CSS design tokens, official brand rules (typography, colors, logo, footer), 12 full HTML slide templates |
| `references/html-to-pptx-conversion.md` | **Image mode** — Playwright conversion script, image-only PPTX rules, file naming |
| `references/html-to-editable-pptx.md` | **Editable mode** — python-pptx builder patterns for all 12 slide types, CSS→pptx mapping |
| `references/core-helpers.md` | **Editable mode** — `add_shape_text()`, `set_ph()`, `DARK_BG_LAYOUTS`, brand colour constants, Google Drive saving |
| `references/core-branding.md` | Snowflake color palette, Fill→Text contrast rules, typography specifications |
| `references/core-template.md` | Official template loading, layout indices 0–28, placeholder IDs, safe zones |
| `references/interaction-model.md` | Phases 0–5: requirements gathering, section menu, visual options, Content Blueprint |
| `references/patterns-enterprise.md` | 37 advanced visual patterns (useful as CSS design inspiration for HTML slides) |
| `references/slide-patterns.md` | Additional slide pattern catalog |
| `references/content-standards.md` | Writing quality rules, narrative structure, slide content standards |
| `references/verification.md` | Post-generation checklist |
| `references/icons.md` | Snowflake icon catalog for architecture slides |
| `references/google-slides-upload.md` | Upload .pptx to Google Slides via Drive API |
