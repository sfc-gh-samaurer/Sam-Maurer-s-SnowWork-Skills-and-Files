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

### Step 3: Generate the Python Script

Write a Python script that uses the utility functions from the reference below to build the deck. The script follows this structure:

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
- Always use `prs.slide_layouts[6]` (blank layout)
- Slide dimensions: `Inches(10) x Inches(5.625)` (official template standard)
- Font: **Arial** throughout (Snowflake official fallback font family)
- Use **Arial Black** for big number KPIs (44pt stat blocks)
- Titles in **ALL CAPS** per brand guidelines
- Background: `#F3F3F3` for content slides when contrast is needed (white is fine by default), Snowflake Blue for cover/chapter/thank you slides
- Every content slide gets `add_footer(slide, context_label)`
- Every content slide gets `add_section_header(slide, title, subtitle)`
- Standard margins: left=0.40", title top=0.30", subtitle=0.72", content=1.50"

### Step 4: Execute and Save

1. **Run** the Python script
2. **Confirm** the .pptx was created and report the file path
3. **Offer** to adjust slides or regenerate

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

## Stopping Points

- STOP after Step 2 (slide structure approval)
- STOP after Step 4 (present file, offer changes)

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
from pptx.enum.shapes import MSO_SHAPE
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
SLIDE_WIDTH  = Inches(10)
SLIDE_HEIGHT = Inches(5.625)

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT
blank_layout = prs.slide_layouts[6]  # Always use blank layout

# Standard layout measurements (from official template)
LEFT_MARGIN   = Inches(0.40)
TITLE_TOP     = Inches(0.30)
SUBTITLE_TOP  = Inches(0.72)
CONTENT_TOP   = Inches(1.50)
CONTENT_WIDTH = Inches(9.13)  # matches template placeholder width
SLIDE_NUM_X   = Inches(9.00)
SLIDE_NUM_Y   = Inches(5.32)
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
def add_shape(slide, left, top, width, height, fill_color=None, line_color=None):
    """Add a rectangle shape. No line by default."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
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
    """KPI metric box. Large value + small label + optional delta.
    Use Arial Black for the value to match template big-number style."""
    add_textbox(slide, left, top, width, Inches(0.4), value,
                font_size=28, bold=True, color=SF_WHITE,
                alignment=PP_ALIGN.CENTER, font_name="Arial Black")
    add_textbox(slide, left, top + Inches(0.4), width, Inches(0.25), label,
                font_size=8, bold=False, color=SF_STAR_BLUE,
                alignment=PP_ALIGN.CENTER)
    if delta:
        add_textbox(slide, left, top + Inches(0.6), width, Inches(0.2), delta,
                    font_size=10, bold=True, color=delta_color,
                    alignment=PP_ALIGN.CENTER)
```

### add_big_number
```python
def add_big_number(slide, left, top, width, value, label):
    """Big number stat block (44pt Arial Black) matching template 'Four Column Layout w/ Big Numbers'."""
    add_textbox(slide, left, top, width, Inches(0.6), value,
                font_size=44, bold=True, color=SF_BLUE,
                alignment=PP_ALIGN.LEFT, font_name="Arial Black")
    add_textbox(slide, left, top + Inches(0.6), width, Inches(0.3), label,
                font_size=10, bold=False, color=SF_DARK_TEXT)
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

## Callout Box Pattern

Left-border accent callout used for warnings, info, and critical alerts:
```python
def add_callout(slide, left, top, width, height, title, body,
                accent_color=SF_BLUE, bg_color=SF_LIGHT_BLUE):
    """Callout box with colored left border accent."""
    add_shape(slide, left, top, width, height, fill_color=bg_color)
    add_shape(slide, left, top, Inches(0.06), height, fill_color=accent_color)
    add_textbox(slide, left + Inches(0.25), top + Inches(0.05), width - Inches(0.4),
                Inches(0.25), title, font_size=10, bold=True, color=accent_color)
    add_textbox(slide, left + Inches(0.25), top + Inches(0.30), width - Inches(0.4),
                height - Inches(0.35), body, font_size=9, color=SF_DARK_TEXT)
```

Preset callout types:
- **Info**: `accent_color=SF_BLUE, bg_color=SF_LIGHT_BLUE`
- **Warning**: `accent_color=SF_AMBER, bg_color=SF_LIGHT_AMBER`
- **Critical**: `accent_color=SF_RED, bg_color=SF_LIGHT_RED`
- **Neutral**: `accent_color=SF_MID_BLUE, bg_color=SF_GRAY_50`

## Text Contrast Rules (from Brand Guidelines)

**Black text** (`SF_DARK_TEXT`) on: `SF_LIGHT_BG`, `SF_WHITE`, `SF_BLUE`, `SF_STAR_BLUE`, `SF_VALENCIA`, `SF_FIRSTLIGHT`

**White text** on: `SF_MID_BLUE`, `SF_MIDNIGHT`, `SF_PURPLE`, `SF_MED_GRAY`

**Snowflake Blue text**: minimum 28pt (accessibility requirement)
