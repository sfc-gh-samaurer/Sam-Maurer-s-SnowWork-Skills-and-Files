---
name: snowflake-pptx-collateral
description: "Create professional Snowflake-branded PowerPoint (PPTX) decks using python-pptx. Use for: presentations, business reviews, district reviews, customer decks, summary slides, status updates, executive presentations. Triggers: PPTX, PowerPoint, deck, slides, presentation, create deck, build slides, business review deck, summary slide."
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
  │  Requires: pip install python-pptx              │
  └─────────────────────────────────────────────────┘
-->

# Snowflake PPTX Collateral Generator

Generate polished, Snowflake-branded PowerPoint decks programmatically using python-pptx, matching the official Snowflake January 2026 template.

## Workflow

### Step 1: Gather Requirements

**Ask** the user:
1. **Deck purpose**: Business review, customer proposal, status update, summary slide, etc.
2. **Slide count & types**: What slides do they need? (See slide type catalog below)
3. **Content source**: Do they have data ready, or should we generate/query it?
4. **Output path**: Where to save the .pptx file

### Step 2: Plan Slide Structure

Design the deck using slide types from the catalog below.

**Present** the proposed slide-by-slide outline to the user.

**STOP**: Get approval before writing code.

### Step 3: Generate HTML Preview

Before writing any python-pptx code, generate a **self-contained HTML file** that renders the full deck as slide-like pages. This serves as the visual blueprint that the PPTX script will faithfully replicate.

**HTML slide spec:**
- Each slide is a `<div class="slide">` with `width: 960px; height: 540px` (matches 10:5.625 ratio at 96dpi)
- Use inline CSS only; no external stylesheets or JS dependencies
- Honor all Snowflake brand colors (hex values from the color constants below)
- Cover / chapter / thank-you slides: `background: #29B5E8`
- Content slides: `background: #ffffff` (use `#F3F3F3` only when extra contrast is needed)
- Titles: ALL CAPS, Arial Bold, 18pt, color `#262626`
- Section dividers between slides: `<hr style="page-break-after:always">`
- Wrap all slides in a `<div class="deck">` with `display:flex; flex-direction:column; gap:24px; padding:24px; background:#e0e0e0`
- Include a `<style>` block at the top for `.slide`, `.slide-cover`, `.kpi-box`, `.callout`, `.card`, `.table` etc.

**Produce the HTML file** at the same base path as the intended PPTX (e.g. `deck_preview.html`).

**STOP**: Present the HTML path to the user and ask them to review it in a browser. Get explicit approval (or requested changes) before proceeding to Step 4.

### Step 4: Convert HTML Blueprint to PPTX

Using the approved HTML as the content source of truth, write a Python script that reproduces every slide in python-pptx. Map HTML elements to python-pptx utilities:

| HTML element | python-pptx call |
|---|---|
| `.slide-cover` background | `set_slide_bg(slide, SF_BLUE)` |
| `<h1>` / `.slide-title` | `add_section_header(slide, title, subtitle)` |
| `.kpi-box` | `make_kpi_box(...)` or `add_big_number(...)` |
| `<table>` | `add_table(...)` + `style_header_row(...)` + `style_data_rows(...)` |
| `.callout` | `add_callout(...)` |
| `.card` | `add_card(...)` |
| `.banner` | `add_banner(...)` |
| footer text | `add_footer(slide, context_label)` |

The script follows this structure:

```python
#!/usr/bin/env python3
"""[Deck Name] Generator"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Brand colors (from reference below)
# Utility functions (from reference below)
# Slide data
# build_deck() function
# Save
```

**Rules:**
- **Text lives in shape text_frames** — never overlay a separate textbox on top of a colored shape. Cards, callouts, banners, KPI boxes, and big numbers all set their text via `shape.text_frame`, not via a stacked `add_textbox()` call. Only use `add_textbox()` for standalone slide-level text (titles, subtitles, footers) that sits directly on the slide background.
- **Accent bars must be line connectors** — never use a thin rectangle shape as a decorative accent bar. Always use `add_vline()` or `add_hline()` (which call `slide.shapes.add_connector(MSO_CONNECTOR_TYPE.STRAIGHT, ...)`) for any colored bar that contains no text. If a shape has width < Inches(0.15) or height < Inches(0.15) and holds no text, replace it with a connector.
- Always use `prs.slide_layouts[6]` (blank layout)
- Slide dimensions: `Inches(10) x Inches(5.625)` (official template standard)
- Font: **Arial** throughout (Snowflake official fallback font family)
- Use **Arial Black** for big number KPIs (44pt stat blocks)
- Titles in **ALL CAPS** per brand guidelines
- Background: `#F3F3F3` for content slides when contrast is needed (white is fine by default), Snowflake Blue for cover/chapter/thank you slides
- Every content slide gets `add_footer(slide, context_label)`
- Every content slide gets `add_section_header(slide, title, subtitle)`
- Standard margins: left=0.45", title top=0.30", subtitle=0.72", content starts at ~1.08"
- **CRITICAL — Full-Bleed Layout Rule**: Content MUST fill the slide from the header divider (~1.08") down to the footer area (~5.10"). Never leave more than 0.3" of empty space between the lowest content element and the footer. See "Full-Bleed Layout Discipline" section below.

### Step 5: Execute and Save

1. **Run** the Python script
2. **Run the QA audit** (see "QA Verification" section below) to check that all slides fill properly
3. **Fix** any slides that fail the audit — recalculate heights dynamically
4. **Confirm** the .pptx was created and report the file path
5. **Offer** to adjust slides or regenerate

## Slide Type Catalog

### Cover Slide (Title)
- Snowflake Blue background (`set_slide_bg(slide, SF_BLUE)`)
- Large title: ALL CAPS, 44pt Arial Bold, white
- Subtitle: 18pt Arial Bold, white
- Metadata line: "First Lastname | Date" (white, smaller)
- Matches template "Data Cloud" cover layout pattern

### Chapter Title / Section Divider
- Full-color background (Snowflake Blue, Mid Blue, or gradient)
- Chapter title: ALL CAPS, large white text, centered or left-aligned
- Optional subtitle below in lighter color
- Matches template "Quote - Violet" layout pattern (used for chapter breaks)

### Multi-Use Content Slide
- Background: white by default; use `SF_LIGHT_BG` (#F3F3F3) only when extra contrast is needed (e.g., slides dense with white cards or tables)
- Title: ALL CAPS at TITLE_TOP (0.30")
- Subtitle at SUBTITLE_TOP (0.72")
- Content area begins at CONTENT_TOP (1.50")
- Most common slide type — used for text, diagrams, mixed content

### Executive Summary
- Section header: "EXECUTIVE SUMMARY" + subtitle
- KPI strip: Mid Blue bar with 3-4 `make_kpi_box()` metric boxes
- Stem sentence (12pt body) + bullet list (10pt with unicode bullet)
- Optional callout box (amber for "Things to Watch", red for "Critical")

### Data Table Slide
- Section header with context
- One or more styled tables using `add_table` + `style_header_row` + `style_data_rows`
- Header row: `SF_MID_BLUE` background, white bold text
- Specify `col_widths` array to control column proportions
- Optional bold total row with `SF_GRAY_50` background
- Health status cells get color-coded via `color_code_status()`

### Big Numbers / KPI Slide
- Matches template "Four Column Layout w/ Big Numbers"
- 2-4 columns, each with `add_big_number()` (44pt Arial Black)
- Paragraph title above each number block
- Optional body text below

### Multi-Column Layout (2, 3, or 4 columns)
- Section header
- Calculate `col_width`, `col_gap`, `start_x`
- Each column: optional icon/image above, paragraph title, body text
- Column counts match template layouts: 1-col, 2-col, 3-col, 4-col

### Split Layout
- Left side: title + text content
- Right side: graphic, image, or diagram
- Matches template "Split Layout" pattern

### Callout / Deep Dive Slide
- Section header
- Vertical stack of callout boxes using `add_callout()` pattern
- Each box: colored left border + title + body text
- Spacing: `box_height + Inches(0.12)` between boxes

### Agenda Slide
- Title area on left (narrow column)
- Agenda items on right with Snowflake Blue diamond bullets
- Matches template "Agenda" layout pattern

### Quote Slide
- Full-color background (gradient)
- Large quote text centered
- Attribution line below
- Matches template "Quote - Violet" layout family

### Thank You / Closing Slide
- Snowflake Blue background (`set_slide_bg(slide, SF_BLUE)`)
- "THANK YOU" in large caps, white
- Contact information or next steps below

### Health Distribution Bar
- Stacked horizontal bar showing proportional segments
- Colors: `SF_RED` (at risk), `SF_AMBER` (monitor), `SF_GREEN` (healthy)
- White bold text labels inside each segment
- Calculate widths proportionally from counts

## Font Size Hierarchy

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Cover title | Arial | 44pt | Bold | White |
| Section header title | Arial | 18pt | Bold | SF_DARK_TEXT |
| Section subtitle | Arial | 12pt | Normal | SF_MED_GRAY |
| Paragraph title | Arial | 18pt | Bold | SF_MID_BLUE |
| Body text | Arial | 10-12pt | Normal | SF_DARK_TEXT |
| Bullets | Arial | 9-10pt | Normal | SF_DARK_TEXT |
| Table header | Arial | 9pt | Bold | White |
| Table data | Arial | 9pt | Normal | SF_DARK_TEXT |
| Footer | Arial | 6pt | Normal | SF_MED_GRAY |
| Big number KPI | Arial Black | 44pt | Bold | SF_BLUE |
| KPI metric box value | Arial Black | 28pt | Bold | White |
| KPI metric box label | Arial | 8pt | Normal | SF_STAR_BLUE |

## Color Usage Rules (from Brand Guidelines)

- **Titles**: SF_DARK_TEXT (#262626) on light backgrounds
- **Accent/Sections**: SF_BLUE or SF_MID_BLUE
- **Secondary colors** (Star Blue, Valencia, Purple Moon, First Light): use very sparingly
- **Snowflake Blue as text color**: minimum 28pt for accessibility
- **Do not** use non-brand colors
- **Do not** use low-contrast text/background combinations
- See "Text Contrast Rules" section below for allowed combinations

## Full-Bleed Layout Discipline

The #1 formatting issue is **dead space** — content that clusters in the top half of the slide, leaving 1-2" of empty white space above the footer. This looks unprofessional and wastes slide real estate.

### Key Constants

```python
LM             = Inches(0.45)     # Left margin
CONTENT_W      = Inches(9.10)     # Full content width (0.45" margins both sides)
FOOTER_Y       = Inches(5.30)     # Footer text top
CONTENT_BOTTOM = Inches(5.10)     # Maximum bottom edge for content (above footer)
HEADER_BOTTOM  = Inches(1.08)     # Content starts here (below header divider line)
```

### Rules

1. **Compute available height dynamically**: `avail_h = CONTENT_BOTTOM - start_y`. Then divide among the elements on the slide rather than using fixed heights.
2. **Cards, tables, and callout boxes** must expand to fill available vertical space. Calculate: `card_h = (avail_h - gaps) / num_cards`.
3. **Banners and callout boxes at the bottom** should stretch to `CONTENT_BOTTOM`: `banner_h = CONTENT_BOTTOM - banner_y`.
4. **Multi-column layouts**: Column width = `(CONTENT_W - (n-1) * gap) / n`. Never hardcode column widths that leave unused horizontal space.
5. **Never use hardcoded heights** when the number of items varies. Always compute proportionally.
6. **Stat grids**: `stat_w = (CONTENT_W - (n-1) * gap) / n` — stats should span the full width.

### Common Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|---|---|
| Cards at 0.72" height on a slide with only 3 cards | Calculate: `card_h = avail_h / 3 - gap` |
| Banner at fixed 0.55" leaving 1" below | `banner_h = CONTENT_BOTTOM - banner_y` |
| 3 columns at Inches(2.85) leaving 0.5" unused | `col_w = (CONTENT_W - 2*gap) / 3` |
| Stat boxes at Inches(1.68) leaving right margin bare | `stat_w = (CONTENT_W - 4*gap) / 5` |
| Figure-8 / diagram shapes not centered on slide | Center: `left = (SLIDE_WIDTH - shape_w) / 2` |

### QA Verification

After generating ANY deck, run this audit script to verify every slide fills properly:

```python
for i, slide in enumerate(prs.slides):
    max_bottom = max((s.top + s.height) / 914400 for s in slide.shapes)
    rightmost = max((s.left + s.width) / 914400 for s in slide.shapes)
    gap = 5.30 - max_bottom
    r_margin = 10.0 - rightmost
    ok = '✓' if gap < 0.35 else '⚠ GAP'
    rk = '✓' if r_margin < 0.60 else '⚠ NARROW'
    print(f'Slide {i+1}: bottom={max_bottom:.2f}" gap={gap:.2f}" {ok} | right={rightmost:.2f}" margin={r_margin:.2f}" {rk}')
```

**Pass criteria**: Every content slide (not title/closing) should show `✓` for both gap and margin. If any slide shows `⚠ GAP` or `⚠ NARROW`, recalculate that slide's element heights/widths dynamically.

## Stopping Points

- STOP after Step 2 (slide structure approval)
- STOP after Step 3 (HTML preview — get explicit approval before writing PPTX code)
- STOP after Step 5 (present file, offer changes)

**Resume rule:** On approval, proceed directly to next step.

## Output

A `.pptx` file that:
- Opens cleanly in PowerPoint, Keynote, and Google Slides
- Matches the official Snowflake January 2026 template style
- Uses Arial typography with ALL CAPS titles per brand guidelines
- Uses the official Snowflake color scheme consistently
- Has professional slide layouts with proper spacing (0.40" margins, standard positions)
- Includes confidential footer on every content slide

---

# PPTX Utility Functions Reference

## Dependencies

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR_TYPE
```

Install: `pip install python-pptx`

## Snowflake Brand Color Constants

```python
# ── Snowflake Official Theme Colors (from "Snowflake 2018" theme scheme) ──
# Primary palette
SF_BLUE       = RGBColor(0x29, 0xB5, 0xE8)   # Snowflake Blue — accent1, primary brand
SF_MID_BLUE   = RGBColor(0x11, 0x56, 0x7F)   # Mid Blue — accent2 / dk2, dark accent
SF_MIDNIGHT   = RGBColor(0x00, 0x00, 0x00)   # Midnight black

# Secondary palette (use sparingly per brand guidelines)
SF_STAR_BLUE  = RGBColor(0x75, 0xCD, 0xD7)   # Star Blue — accent3
SF_VALENCIA   = RGBColor(0xFF, 0x9F, 0x36)   # Valencia Orange — accent4
SF_PURPLE     = RGBColor(0x72, 0x54, 0xA3)   # Purple Moon — accent5
SF_FIRSTLIGHT = RGBColor(0xD4, 0x5B, 0x90)   # First Light (rose) — accent6

# Neutral palette
SF_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
SF_DARK_TEXT  = RGBColor(0x26, 0x26, 0x26)   # dk1 — primary text on light bg
SF_MED_GRAY   = RGBColor(0x5B, 0x5B, 0x5B)   # Medium Gray — subtitles/captions
SF_LIGHT_BG   = RGBColor(0xF3, 0xF3, 0xF3)   # Standard slide background
SF_GRAY_200   = RGBColor(0xD1, 0xD9, 0xE0)   # Borders / dividers
SF_GRAY_50    = RGBColor(0xF8, 0xFA, 0xFB)   # Alternating row light

# Semantic status colors
SF_GREEN      = RGBColor(0x2E, 0xCC, 0x71)   # Positive / healthy
SF_AMBER      = RGBColor(0xF5, 0xA6, 0x23)   # Warning / monitor
SF_RED        = RGBColor(0xE7, 0x4C, 0x3C)   # Critical / at risk

# Status cell background tints
SF_LIGHT_GREEN = RGBColor(0xE8, 0xF8, 0xEF)
SF_LIGHT_AMBER = RGBColor(0xFF, 0xF3, 0xE0)
SF_LIGHT_RED   = RGBColor(0xFD, 0xED, 0xEC)
SF_LIGHT_BLUE  = RGBColor(0xE8, 0xF4, 0xFD)
```

## Typography Rules

The official Snowflake template uses **Arial** as the standard font family:

- **Titles & chapter headings**: Arial Bold, ALL CAPS
- **Subtitles**: Arial, sentence case, color `SF_MED_GRAY`
- **Body text**: Arial, `SF_DARK_TEXT` (#262626)
- **Big number KPIs**: Arial Black, 44pt bold (for impact stats)
- **Table headers**: Arial Bold, 9pt, white on `SF_MID_BLUE`
- **Table data**: Arial, 9pt, `SF_DARK_TEXT`
- **Footers**: Arial, 8pt, `SF_MED_GRAY`
- **Snowflake Blue text**: minimum 28pt for accessibility (per brand guidelines)
- **Text contrast**: Black text on light backgrounds, white text on `SF_MID_BLUE` / `SF_MIDNIGHT` / `SF_PURPLE`

## Slide Setup

```python
# Official Snowflake template dimensions (10:5.625 = 16:9)
SLIDE_WIDTH    = Inches(10)
SLIDE_HEIGHT   = Inches(5.625)

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT
blank_layout = prs.slide_layouts[6]  # Always use blank layout

# Standard layout measurements
LM             = Inches(0.45)     # Left margin (and right margin)
CONTENT_W      = Inches(9.10)     # = 10.0 - 2*0.45
FOOTER_Y       = Inches(5.30)     # Footer top position
CONTENT_BOTTOM = Inches(5.10)     # Content must not exceed this
HEADER_BOTTOM  = Inches(1.08)     # Content starts below this
```

## Utility Functions

### set_slide_bg
```python
def set_slide_bg(slide, color):
    """Set solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color
```

### add_shape
```python
def add_shape(slide, left, top, width, height, fill_color=None, line_color=None, radius=None,
             text="", font_size=12, bold=False, text_color=SF_DARK_TEXT,
             alignment=PP_ALIGN.LEFT, font_name="Arial", v_anchor=MSO_ANCHOR.MIDDLE,
             ml=Inches(0.10), mt=Inches(0.05), mr=Inches(0.10), mb=Inches(0.05)):
    """Add a rectangle (or rounded rectangle) with optional inline text.
    Text lives directly in the shape's text_frame — never overlay a separate textbox."""
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    if text:
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left, tf.margin_top = ml, mt
        tf.margin_right, tf.margin_bottom = mr, mb
        tf.vertical_anchor = v_anchor
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = text_color
        p.font.name = font_name
        p.alignment = alignment
    return shape
```

### add_textbox
```python
def add_textbox(slide, left, top, width, height, text="", font_size=12,
                bold=False, color=SF_DARK_TEXT, alignment=PP_ALIGN.LEFT,
                font_name="Arial"):
    """Add a text box with styled first paragraph."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox
```

### add_paragraph
```python
def add_paragraph(text_frame, text, font_size=12, bold=False,
                  color=SF_DARK_TEXT, alignment=PP_ALIGN.LEFT,
                  space_before=Pt(0), space_after=Pt(4), font_name="Arial"):
    """Append a paragraph to an existing text frame."""
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    return p
```

### add_table + styling
```python
def add_table(slide, left, top, width, height, rows, cols):
    """Add a table and return the table object."""
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    return table_shape.table

def style_header_row(table, col_widths=None):
    """Style first row as Mid Blue header with white bold text."""
    for cell in table.rows[0].cells:
        cell.fill.solid()
        cell.fill.fore_color.rgb = SF_MID_BLUE
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = SF_WHITE
            p.font.name = "Arial"
            p.alignment = PP_ALIGN.LEFT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w

def style_data_cell(cell, font_size=9, bold=False, color=SF_DARK_TEXT,
                    alignment=PP_ALIGN.LEFT):
    """Style a single data cell."""
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.font.name = "Arial"
        p.alignment = alignment
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE

def style_data_rows(table, start_row=1):
    """Apply alternating row shading (GRAY_50 / WHITE)."""
    for row_idx in range(start_row, len(table.rows)):
        for cell in table.rows[row_idx].cells:
            cell.fill.solid()
            cell.fill.fore_color.rgb = SF_GRAY_50 if row_idx % 2 == 0 else SF_WHITE
            style_data_cell(cell)
```

### make_kpi_box
```python
def make_kpi_box(slide, left, top, width, value, label, delta="",
                 delta_color=SF_GREEN):
    """KPI metric box. All text (value, label, delta) lives in the shape's text_frame."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.75))
    shape.fill.background()
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = value
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = SF_WHITE
    p.font.name = "Arial Black"
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(8)
    p2.font.color.rgb = SF_STAR_BLUE
    p2.font.name = "Arial"
    p2.alignment = PP_ALIGN.CENTER
    if delta:
        p3 = tf.add_paragraph()
        p3.text = delta
        p3.font.size = Pt(10)
        p3.font.bold = True
        p3.font.color.rgb = delta_color
        p3.font.name = "Arial"
        p3.alignment = PP_ALIGN.CENTER
    return shape
```

### add_big_number
```python
def add_big_number(slide, left, top, width, value, label):
    """Big number stat block. Value and label live in the shape's text_frame."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.9))
    shape.fill.background()
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = value
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = SF_BLUE
    p.font.name = "Arial Black"
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(10)
    p2.font.color.rgb = SF_DARK_TEXT
    p2.font.name = "Arial"
    return shape
```

### add_section_header
```python
def add_section_header(slide, title, subtitle="", bg_color=None):
    """Template-style title area at top of content slide.
    Title in ALL CAPS per brand guidelines.
    bg_color is optional — white is fine for most slides, use SF_LIGHT_BG when needed for contrast."""
    if bg_color:
        set_slide_bg(slide, bg_color)
    # Title — ALL CAPS, left-aligned at standard position
    add_textbox(slide, LEFT_MARGIN, TITLE_TOP, CONTENT_WIDTH, Inches(0.40),
                title.upper(), font_size=18, bold=True, color=SF_DARK_TEXT)
    if subtitle:
        add_textbox(slide, LEFT_MARGIN, SUBTITLE_TOP, CONTENT_WIDTH, Inches(0.40),
                    subtitle, font_size=12, bold=False, color=SF_MED_GRAY)
```

### add_footer
```python
def add_footer(slide, context_label=""):
    """Standard footer with slide number area and optional context."""
    add_textbox(slide, LEFT_MARGIN, Inches(5.32), Inches(5), Inches(0.20),
                "Confidential — Snowflake Professional Services",
                font_size=6, color=SF_MED_GRAY)
    if context_label:
        add_textbox(slide, Inches(5.5), Inches(5.32), Inches(3.5), Inches(0.20),
                    context_label,
                    font_size=6, color=SF_MED_GRAY, alignment=PP_ALIGN.RIGHT)
```

### add_paragraph_title
```python
def add_paragraph_title(slide, left, top, width, text):
    """Paragraph title within content area (18pt bold, theme color).
    Matches template 'Paragraph Title' pattern used in column layouts."""
    add_textbox(slide, left, top, width, Inches(0.30), text,
                font_size=18, bold=True, color=SF_MID_BLUE)
```

## Health Status Color-Coding Pattern

For cells containing health/status values:
```python
STATUS_STYLES = {
    "AT RISK":  (SF_LIGHT_RED,   SF_RED),
    "MONITOR":  (SF_LIGHT_AMBER, SF_AMBER),
    "HEALTHY":  (SF_LIGHT_GREEN, SF_GREEN),
}

def color_code_status(cell):
    text = cell.text_frame.paragraphs[0].text.strip()
    if text in STATUS_STYLES:
        bg, fg = STATUS_STYLES[text]
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
        for p in cell.text_frame.paragraphs:
            p.font.color.rgb = fg
            p.font.bold = True
```

## Line Connector Utilities

Use connectors — **not thin rectangles** — for all accent bars, dividers, and decorative lines:

```python
def add_vline(slide, x, y1, y2, color, width_pt=3.5):
    """Vertical accent line. Always use this instead of a thin rectangle shape."""
    conn = slide.shapes.add_connector(MSO_CONNECTOR_TYPE.STRAIGHT, x, y1, x, y2)
    conn.line.color.rgb = color
    conn.line.width = Pt(width_pt)
    return conn

def add_hline(slide, x1, x2, y, color, width_pt=3.5):
    """Horizontal accent line. Always use this instead of a thin rectangle shape."""
    conn = slide.shapes.add_connector(MSO_CONNECTOR_TYPE.STRAIGHT, x1, y, x2, y)
    conn.line.color.rgb = color
    conn.line.width = Pt(width_pt)
    return conn
```

**Rule**: Any time you would create a shape with width < Inches(0.15) or height < Inches(0.15) purely for color (no text), use `add_vline` or `add_hline` instead.

## Callout Box Pattern

Left-border accent callout used for warnings, info, and critical alerts:
```python
def add_callout(slide, left, top, width, height, title, body,
                accent_color=SF_BLUE, bg_color=SF_LIGHT_BLUE):
    """Callout box. Title and body live directly in the shape's text_frame.
    Left margin is indented to clear the accent line."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)   # indented past the accent line
    tf.margin_top = Inches(0.05)
    tf.margin_right = Inches(0.10)
    tf.margin_bottom = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = accent_color
    p.font.name = "Arial"
    p.space_after = Pt(3)
    p2 = tf.add_paragraph()
    p2.text = body
    p2.font.size = Pt(9)
    p2.font.color.rgb = SF_DARK_TEXT
    p2.font.name = "Arial"
    # Accent line — connector, NOT a rectangle shape
    add_vline(slide, left + Inches(0.07), top + Inches(0.04),
              top + height - Inches(0.04), accent_color, width_pt=4.0)
    return shape
```

Preset callout types:
- **Info**: `accent_color=SF_BLUE, bg_color=SF_LIGHT_BLUE`
- **Warning**: `accent_color=SF_AMBER, bg_color=SF_LIGHT_AMBER`
- **Critical**: `accent_color=SF_RED, bg_color=SF_LIGHT_RED`
- **Neutral**: `accent_color=SF_MID_BLUE, bg_color=SF_GRAY_50`

### add_card
```python
def add_card(slide, left, top, width, height, title, body, accent_color=SF_BLUE, bg_color=SF_LIGHT_BG,
            accent_side="left"):
    """Card with colored accent line. Title and body live directly in the card
    shape's text_frame — no overlaid textboxes. Accent is a connector line, not a rectangle.
    accent_side: 'left' for vertical accent, 'top' for horizontal accent."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    # Left margin clears the left accent line; use smaller margin for top-accent cards
    tf.margin_left = Inches(0.20) if accent_side == "left" else Inches(0.14)
    tf.margin_top = Inches(0.08) if accent_side == "left" else Inches(0.14)
    tf.margin_right = Inches(0.10)
    tf.margin_bottom = Inches(0.08)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = title.upper()
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = SF_DARK_TEXT
    p.font.name = "Arial"
    p.space_after = Pt(4)
    p2 = tf.add_paragraph()
    p2.text = body
    p2.font.size = Pt(10)
    p2.font.color.rgb = SF_MED_GRAY
    p2.font.name = "Arial"
    p2.line_spacing = Pt(15)
    # Accent line — connector, NOT a rectangle shape
    if accent_side == "left":
        add_vline(slide, left + Inches(0.06), top + Inches(0.08),
                  top + height - Inches(0.08), accent_color, width_pt=3.5)
    else:  # top
        add_hline(slide, left, left + width, top, accent_color, width_pt=4.0)
    return shape
```

Card accent color variants:
- **Default/Blue**: `accent_color=SF_BLUE`
- **Positive**: `accent_color=SF_GREEN`
- **Warning**: `accent_color=SF_AMBER` or `SF_VALENCIA`
- **Critical**: `accent_color=SF_RED`
- **Neutral/Navy**: `accent_color=SF_MID_BLUE`

### add_banner
```python
def add_banner(slide, left, top, width, height, text, bold_prefix=""):
    """Banner with text living directly in the shape's text_frame."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = SF_LIGHT_BLUE
    shape.line.color.rgb = RGBColor(0xBB, 0xDE, 0xF0)
    shape.line.width = Pt(1)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.15)
    tf.margin_top = tf.margin_bottom = Inches(0.06)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    if bold_prefix:
        run1 = p.add_run()
        run1.text = bold_prefix + " "
        run1.font.size = Pt(10)
        run1.font.bold = True
        run1.font.color.rgb = SF_MID_BLUE
        run1.font.name = "Arial"
    run2 = p.add_run()
    run2.text = text
    run2.font.size = Pt(10)
    run2.font.color.rgb = SF_DARK_TEXT
    run2.font.name = "Arial"
    return shape
```

### Dynamic Column Width Helpers
```python
def col_widths(n, gap=Inches(0.20)):
    """Calculate equal column width for n columns spanning CONTENT_W."""
    return (CONTENT_W - (n - 1) * gap) / n

def col_x(i, n, gap=Inches(0.20)):
    """Calculate left position for column i (0-indexed) of n columns."""
    w = col_widths(n, gap)
    return LM + i * (w + gap)
```

## Text Contrast Rules (from Brand Guidelines)

**Black text** (`SF_DARK_TEXT`) on: `SF_LIGHT_BG`, `SF_WHITE`, `SF_BLUE`, `SF_STAR_BLUE`, `SF_VALENCIA`, `SF_FIRSTLIGHT`

**White text** on: `SF_MID_BLUE`, `SF_MIDNIGHT`, `SF_PURPLE`, `SF_MED_GRAY`

**Snowflake Blue text**: minimum 28pt (accessibility requirement)
