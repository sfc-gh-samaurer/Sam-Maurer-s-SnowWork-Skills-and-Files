---
name: snowflake-pptx-collateral
description: "Create professional Snowflake-branded PowerPoint (PPTX) decks. Designs slides in HTML/CSS first (world-class visual quality), then converts to PPTX in one of two modes: (1) Image Mode — pixel-perfect PNG slides, not editable; (2) Editable Mode — native python-pptx shapes and text boxes, fully editable in PowerPoint. Use for: presentations, business reviews, district reviews, customer decks, summary slides, status updates, executive presentations. Triggers: PPTX, PowerPoint, deck, slides, presentation, create deck, build slides, business review deck, summary slide."
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

## Workflow

### Step 1: Gather Requirements

**Ask** the user:
1. **Deck purpose**: Business review, customer proposal, status update, summary slide, etc.
2. **Slide count & types**: What slides do they need? (See slide type catalog below)
3. **Content source**: Do they have data ready, or should we generate/query it?
4. **Output path**: Where to save the .pptx file
5. **Output mode**: Image-only (pixel-perfect, not editable) or Editable (native PowerPoint shapes and text)?

**Mode guidance to offer the user:**
- **Image mode** — best for final client deliverables, investor decks, anything where design perfection matters more than editability
- **Editable mode** — best for internal decks, templates the user will customize, or any deck that needs post-delivery edits in PowerPoint

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

> Use this path when the user selected **Image mode** or did not specify.
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

### Step 4b: Convert HTML → Editable PPTX (Editable Mode)

> Use this path when the user selected **Editable mode**.
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
3. Install dependency: `pip install python-pptx`
4. Run the script and confirm the `.pptx` was created
5. **Offer** to adjust any slide and regenerate

## Slide Type Catalog

> All slide types are implemented in HTML/CSS. Use the templates in `references/html-slide-design.md` as your starting point for each type. The descriptions below define the visual rules each type must follow.

### Cover Slide
- Dark gradient background (`var(--sf-mid-blue)` to `#0c3351`)
- Decorative wave, background circles, diagonal overlay for depth
- Large title: ALL CAPS, 36–44px bold, white
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

## Color Usage Rules (from Brand Guidelines)

- **Titles**: SF_DARK_TEXT (#262626) on light backgrounds
- **Accent/Sections**: SF_BLUE or SF_MID_BLUE
- **Secondary colors** (Star Blue, Valencia, Purple Moon, First Light): use very sparingly
- **Snowflake Blue as text color**: minimum 28pt for accessibility
- **Do not** use non-brand colors
- **Do not** use low-contrast text/background combinations
- See "Text Contrast Rules" section below for allowed combinations

## Stopping Points

- STOP after Step 2 (slide structure / Content Blueprint approval)
- STOP after Step 3b (verify HTML dimensions in browser before converting)
- STOP after Step 4a or 4b (present PPTX file path, offer per-slide adjustments)

**Resume rule:** On approval, proceed directly to next step.

## Output

**Image mode:** A `.pptx` file where every slide is a full-bleed PNG image — a Playwright screenshot of its HTML source inserted to fill the entire 10"×5.625" slide area. No editable shapes or text boxes. 1920×1080 retina quality.

**Editable mode:** A `.pptx` file with native shapes, text boxes, and tables — fully editable in PowerPoint, Keynote, and Google Slides. Layout, colors, and typography match the HTML design system. Some CSS decorative effects (gradients, rounded corners, clip-paths) are approximated with flat shapes.

In both modes:
- Slides match Snowflake January 2026 brand guidelines
- Arial font, official Snowflake color palette, ALL CAPS titles
- Confidential footer on every content slide
- HTML/CSS source files are kept as the design source of truth

---

# Reference Files

| File | Purpose |
|------|---------|
| `references/html-slide-design.md` | **PRIMARY** — CSS design tokens, 12 full HTML slide templates, design tips |
| `references/html-to-pptx-conversion.md` | **Image mode** — Playwright conversion script, image-only PPTX rules, file naming |
| `references/html-to-editable-pptx.md` | **Editable mode** — python-pptx builder patterns for all 12 slide types, CSS→pptx mapping |
| `references/interaction-model.md` | Phases 0–5: requirements gathering, section menu, visual options, Content Blueprint |
| `references/core-branding.md` | Snowflake color palette, fill→text contrast rules, typography specifications |
| `references/patterns-enterprise.md` | 37 advanced visual patterns (useful as CSS design inspiration for HTML slides) |
| `references/slide-patterns.md` | Additional slide pattern catalog |
| `references/content-standards.md` | Writing quality rules, narrative structure, slide content standards |
| `references/verification.md` | Post-generation checklist |
