---
name: pptx-html-to-editable-pptx
description: python-pptx implementation guide for producing native, editable PPTX slides that match the HTML/CSS design system. Use when the user wants editable shapes and text boxes rather than image-only slides.
---

# HTML → Editable PPTX Implementation Guide

## Overview

This guide translates the HTML/CSS design system (`html-slide-design.md`) into native python-pptx objects — real text boxes, shapes, and tables that are fully editable in PowerPoint.

**Fidelity tradeoffs vs image-only mode:**
- CSS `border-radius` → square rectangle corners (python-pptx does not support rounded rects natively)
- `linear-gradient` backgrounds → solid fill using the dominant color
- `clip-path` waves and diagonal overlays → omitted or replaced with a solid shape
- `box-shadow`, `::before/::after` decorations → omitted
- All text, tables, KPI boxes, edge bars, footers, color fills → pixel-accurate

The design intent and Snowflake branding are fully preserved. Slides are fully editable in PowerPoint.

---

## Core Rule: Text Lives Inside Shapes

**ALWAYS place text directly in a shape's `.text_frame` — never add a floating `add_textbox()` on top of a shape.**

```
❌ WRONG — floating text box layered over a shape:
    add_rect(slide, x, y, w, h, fill=SF_MID_BLUE)
    add_text(slide, x+pad, y+pad, w, h, "Label")   ← separate shape, z-order issues

✅ CORRECT — text set directly in the shape's text frame:
    shape = add_rect(slide, x, y, w, h, fill=SF_MID_BLUE)
    set_shape_text(shape, "Label")
```

**Rule:** `add_text()` (standalone textbox) is only for elements that have **no background shape** — slide titles, subtitles, footers, body paragraphs, and bullet lists. For any element that has a colored fill (card header, KPI box, badge, phase bar, milestone bar, button, etc.), always use `set_shape_text()` on the shape returned by `add_rect()`.

This ensures:
- Moving a shape in PowerPoint moves its label with it
- No invisible floating text boxes cluttering the slide layer panel
- Clean, editable object hierarchy

---

## Core Rule: Kill the Default Drop Shadow on EVERY Shape

**Every `add_shape()` shape inherits a soft theme drop shadow by default.** Across a slide full
of rectangles, badges, and pills these stacked shadows are the single biggest reason an editable
deck looks like generic clip-art instead of a designed slide. The HTML source has flat shapes —
match it.

```python
shape.shadow.inherit = False   # ← set on EVERY rect/oval/triangle you create
```

This is already baked into `add_rect()` above. If you create a shape any other way
(`add_shape(MSO_SHAPE.OVAL, …)`, `add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, …)` for a roof, etc.),
set `shape.shadow.inherit = False` manually right after creating it. Tables and `add_textbox()`
do not need it.

---

## Core Rule: Tables Use Native Table Objects (NEVER a Grid of Rectangles)

**Any tabular, matrix, or grid content MUST be a native python-pptx table created with
`slide.shapes.add_table(...)`.** This covers data tables, RACI matrices, deliverables lists,
pricing tables, scope summaries, dashboard catalogs — anything with rows and columns.

```
❌ WRONG — a grid of individual rectangles faking a table:
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = add_rect(slide, x, y, w, h, fill)   ← NOT a table
            set_shape_text(cell, val)

✅ CORRECT — one native table object, per-cell fills set on the cell:
    tbl = slide.shapes.add_table(n_rows, n_cols, left, top, width, height).table
    cell = tbl.cell(r, c)
    cell.fill.solid(); cell.fill.fore_color.rgb = fill   ← editable table cell
    cell.text = val
```

**Why this matters:**
- A grid of rectangles cannot be edited as a table in PowerPoint — no row/column insert, no
  tab-to-next-cell, no table styling. It only *looks* like a table until someone tries to edit it.
- Native tables keep content aligned automatically and are far smaller in the file.
- Per-cell color coding (e.g. RACI R/A/C/I, status cells, alternating row stripes) is fully
  supported on native cells via `cell.fill.solid()` — you lose nothing by using a real table.

**Rules:**
- Use the `build_table_slide`, `build_kpi_table`, and `build_raci` builders below — they already
  use `add_table`. Do not reimplement tables with `add_rect`.
- Set per-cell fills with `cell.fill.solid(); cell.fill.fore_color.rgb = COLOR`. For RACI, map each
  code to a `(fill, text_color)` pair and apply it to the cell.
- Disable built-in banded styling when you set fills explicitly: `tbl.first_row = False;
  tbl.horz_banding = False` (otherwise the theme banding fights your colors).
- **Column widths must be integer EMU.** `Inches(...)` is already an int, but division produces a
  float and raises `TypeError: value must be an integral type`. Wrap any computed width in `int(...)`:
  `role_w = int((CONTENT_W - act_w) / 4)`.
- The ONLY things that may remain `add_rect()` shapes near a table are non-tabular accents:
  legend badges, callout bars, section labels. The table grid itself is never rectangles.

---

## Core Rule: Bullets Are Native, Never Typed Glyphs

**Every bulleted list MUST use real PowerPoint bullets, never a glyph typed into the run text.**

```
❌ WRONG — a typed glyph faking a bullet:
    run.text = "•  One source of truth per domain"   ← not a list item
    run.text = "✓  Every cost traceable to a BU"     ← wraps under the dot

✅ CORRECT — clean text + native bullet on the paragraph:
    run.text = "One source of truth per domain"
    set_bullet(para, char="•", color=SF_BLUE)        ← real, indented bullet
```

**Why this matters:**
- A typed glyph has no hanging indent — when the line wraps, the second line sits under the dot instead of under the text. A native bullet indents correctly.
- A typed glyph can't be toggled with PowerPoint's bullet button, re-indented, or restyled — it's just characters.
- Native bullets still support ANY glyph (`•`, `✓`, `–`, `▸`) and any brand color, so you keep the designed look and gain real list behavior.

**Rules:**
- **Placeholder body text** (content-slide bullets) gets native template bullets automatically via `set_ph_lines()` / `set_ph_sections()` — use those; don't type glyphs.
- **Bullets inside custom shapes** (card bodies, navy panels, callouts) have no placeholder bullet, so apply `set_bullet(para, ...)` from `core-helpers.md` Section 12.7b to each list paragraph. The run text holds the words only.
- An intro/heading line inside a bulleted shape gets `clear_bullet(para)` so it stays unbulleted.
- A leftover `"•  "`, `"✓  "`, or `"-  "` prefix in any run is the #1 sign this rule was missed — strip it and call `set_bullet()`.

---

## Dependencies

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE_TYPE
from io import BytesIO
```

```bash
pip install python-pptx
```

---

## Brand Color Constants

```python
SF_BLUE        = RGBColor(0x29, 0xB5, 0xE8)   # --sf-blue
SF_MID_BLUE    = RGBColor(0x11, 0x56, 0x7F)   # --sf-mid-blue
SF_DARK_BG     = RGBColor(0x0c, 0x33, 0x51)   # gradient end / dark backgrounds
SF_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
SF_DARK_TEXT   = RGBColor(0x26, 0x26, 0x26)   # --sf-dark-text
SF_BODY_GREY   = RGBColor(0x5B, 0x5B, 0x5B)   # --sf-body-grey
SF_LIGHT_BG    = RGBColor(0xF5, 0xF5, 0xF5)   # --sf-light-bg
SF_TEAL        = RGBColor(0x75, 0xCD, 0xD7)   # --sf-teal  "Star Blue" (2026 brand)
SF_ORANGE      = RGBColor(0xFF, 0x9F, 0x36)   # --sf-orange  "Valencia Orange"
SF_BORDER      = RGBColor(0xC8, 0xC8, 0xC8)   # --sf-border
SF_GRID        = RGBColor(0xDD, 0xDD, 0xDD)   # --sf-grid
SF_LIGHT_ROW   = RGBColor(0xF8, 0xFA, 0xFB)   # --sf-light-row
SF_TABLE_GREY  = RGBColor(0x71, 0x71, 0x71)   # --sf-table-grey
SF_GREEN       = RGBColor(0x2E, 0xCC, 0x71)
SF_AMBER       = RGBColor(0xF5, 0xA6, 0x23)
SF_RED         = RGBColor(0xE7, 0x4C, 0x3C)
SF_VIOLET      = RGBColor(0x72, 0x54, 0xA3)   # "Purple Moon"  — use sparingly
SF_FIRST_LIGHT = RGBColor(0xD4, 0x5B, 0x90)   # "First Light"  — use sparingly
SF_MIDNIGHT    = RGBColor(0x00, 0x00, 0x00)   # "Midnight"     — near-black
SF_PAGE_NUM    = RGBColor(0x91, 0x91, 0x91)   # page number color
SF_COPYRIGHT   = RGBColor(0x92, 0x92, 0x92)   # copyright footer color
SF_LIGHT_BLUE  = RGBColor(0xE8, 0xF4, 0xFD)
SF_LIGHT_AMBER = RGBColor(0xFF, 0xF3, 0xE0)
SF_LIGHT_GREEN = RGBColor(0xE8, 0xF8, 0xEF)
```

---

## Geometry Constants

Derived from CSS pixel values at 96dpi (CSS px ÷ 96 = inches):

```python
# Slide canvas
SLIDE_W = Inches(10)       # 960px ÷ 96
SLIDE_H = Inches(5.625)    # 540px ÷ 96

# Standard positions (from CSS design tokens)
PAD_LEFT     = Inches(0.396)   # 38px  — left margin for all text
TITLE_TOP    = Inches(0.302)   # 29px  — slide title top
SUBTITLE_TOP = Inches(0.583)   # 56px  — slide subtitle top
CONTENT_TOP  = Inches(1.0)     # 96px  — content area start
FOOTER_TOP   = Inches(5.323)   # 511px — footer text top
SAFE_BOTTOM  = Inches(5.104)   # 490px — content must not go below this
CONTENT_W    = Inches(9.125)   # 876px — usable content width

# Edge bar (the 4px blue vertical accent on content slides)
EDGE_BAR_LEFT   = Inches(0)
EDGE_BAR_TOP    = Inches(0.375)   # 36px
EDGE_BAR_WIDTH  = Inches(0.042)   # 4px
EDGE_BAR_HEIGHT = Inches(0.396)   # 38px
```

---

## Core Utility Functions

```python
def new_deck():
    """Create a blank 16:9 Snowflake-standard deck."""
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs

def add_blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def set_solid_bg(slide, color):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color

def add_rect(slide, left, top, width, height, fill=None, line=None, line_width=Pt(0)):
    """Add a rectangle and return the shape. Text belongs in shape.text_frame — use set_shape_text()."""
    from pptx.enum.shapes import MSO_SHAPE
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line:
        shape.line.color.rgb = line
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False   # ← CRITICAL: kill the default theme drop shadow
    return shape

def set_shape_text(shape, text, size=10, bold=False, color=SF_WHITE,
                   align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE, wrap=True):
    """
    Set text DIRECTLY in a shape's text frame.
    Use this for any element that has a colored fill: card headers, KPI boxes,
    badges, phase bars, milestone bars, buttons, RACI cells, etc.
    NEVER use add_text() on top of a filled shape.
    """
    tf = shape.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = valign
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE   # ← safety net: shrink text to fit
    # Tight internal margins — the python-pptx default (~0.1") makes labels float
    # awkwardly inside small bars, pills, and badges. Override explicitly.
    tf.margin_left = Pt(6)
    tf.margin_right = Pt(6)
    tf.margin_top = Pt(3)
    tf.margin_bottom = Pt(3)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return shape

def add_shape_para(shape, text, size=9, bold=False, color=SF_WHITE,
                   align=PP_ALIGN.CENTER, space_before=Pt(0), space_after=Pt(2)):
    """Append an additional paragraph to an existing shape's text frame."""
    tf = shape.text_frame
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = space_before
    p.space_after = space_after
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return p

def add_text(slide, left, top, width, height, text, size=10, bold=False,
             color=SF_DARK_TEXT, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
             wrap=True):
    """
    Add a STANDALONE text box — use ONLY for elements with no background fill:
    slide titles, subtitles, footers, body paragraphs, bullet lists.
    For any element with a colored shape behind it, use add_rect() + set_shape_text() instead.
    """
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return tb

def add_para(tf, text, size=9, bold=False, color=SF_DARK_TEXT,
             align=PP_ALIGN.LEFT, space_before=Pt(0), space_after=Pt(3)):
    """Append a paragraph to an existing standalone text frame (titles, body, bullets)."""
    p = tf.add_paragraph()
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    p.alignment = align
    p.space_before = space_before
    p.space_after = space_after
    return p
```

---

## Mixed-Run Text: Bold Lead + Body in One Paragraph (HIGH-VALUE PATTERN)

HTML constantly uses a **bold (often colored) lead phrase followed by normal body text** in a
single line — callout bars ("**Our Approach:** address the data foundation…"), required-action
strips ("**Required Action:** the team must…"), key-principle notes, and bullets with a bold
keyword ("**Pilot build** — Snowflake PS builds…"). A single-run helper cannot reproduce this.
Use these two helpers — they are the difference between flat, generic slides and ones that read
like the HTML source.

```python
def add_callout_bar(slide, left, top, width, height, lead, body,
                    fill=SF_LIGHT_BLUE, accent=SF_BLUE,
                    lead_color=SF_MID_BLUE, body_color=SF_DARK_TEXT, size=9):
    """A filled callout bar with a colored left accent stripe and a bold lead + normal body
    on one line. Used for 'Our Approach:', 'Required Action:', 'Key principle:' style strips."""
    bar = add_rect(slide, left, top, width, height, fill)
    add_rect(slide, left, top, Inches(0.04), height, accent)   # left accent stripe
    tf = bar.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    tf.margin_left = Pt(10); tf.margin_right = Pt(8)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r0 = p.add_run(); r0.text = lead + "  "
    r0.font.size = Pt(size); r0.font.bold = True
    r0.font.color.rgb = lead_color; r0.font.name = "Arial"
    r1 = p.add_run(); r1.text = body
    r1.font.size = Pt(size); r1.font.color.rgb = body_color; r1.font.name = "Arial"
    return bar

def add_bold_lead_bullets(shape, items, size=9, marker="\u2022  ",
                          marker_color=SF_BLUE, lead_color=SF_MID_BLUE,
                          body_color=SF_DARK_TEXT, space_after=Pt(4)):
    """Fill a shape with bullets. Each item is either a plain string OR a (lead, rest) tuple
    that renders a bold colored lead phrase followed by normal body text on the same line.
    Sets tight margins so text doesn't float inside the panel."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    tf.margin_left = Pt(8); tf.margin_right = Pt(8)
    tf.margin_top = Pt(6); tf.margin_bottom = Pt(6)
    for j, item in enumerate(items):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(1); p.space_after = space_after
        r0 = p.add_run(); r0.text = marker
        r0.font.size = Pt(size); r0.font.color.rgb = marker_color; r0.font.name = "Arial"
        if isinstance(item, tuple):
            lead, rest = item
            r1 = p.add_run(); r1.text = lead
            r1.font.size = Pt(size); r1.font.bold = True
            r1.font.color.rgb = lead_color; r1.font.name = "Arial"
            r2 = p.add_run(); r2.text = rest
            r2.font.size = Pt(size); r2.font.color.rgb = body_color; r2.font.name = "Arial"
        else:
            r1 = p.add_run(); r1.text = item
            r1.font.size = Pt(size); r1.font.color.rgb = body_color; r1.font.name = "Arial"
```

**Usage:**
```python
# Callout strip at the bottom of a slide
add_callout_bar(slide, PAD_LEFT, Inches(4.46), CONTENT_W, Inches(0.46),
                "Our Approach:", "Address the data foundation and use cases in parallel.")

# Bullets with bold keyword leads (mix tuples and plain strings freely)
body = add_rect(slide, x, y, col_w, col_h, SF_MID_BLUE)
add_bold_lead_bullets(body, [
    ("Pilot build", " \u2014 Snowflake PS builds 1\u20132 data products end-to-end."),
    ("Full catalog migration", " \u2014 migrate all remaining products once the pattern is proven."),
    "Plain bullet with no bold lead also works.",
], lead_color=SF_TEAL, body_color=RGBColor(0xD2, 0xE2, 0xEE))   # use light text on dark fills
```

⚠ On **dark-fill** panels (SF_MID_BLUE, navy), pass `lead_color=SF_TEAL` and a light
`body_color` (e.g. `#D2E2EE`). On **light** panels keep the SF_MID_BLUE / SF_DARK_TEXT defaults.

---

## Slide Structure Helpers

```python
# Page number position (from official brand template)
PAGE_NUM_LEFT = Inches(9.0)
PAGE_NUM_TOP  = Inches(5.323)
PAGE_NUM_W    = Inches(0.518)
PAGE_NUM_H    = Inches(0.101)

COPYRIGHT_TEXT = "\u00a9 2026 Snowflake Inc. All Rights Reserved"


def add_content_slide_frame(prs, title, subtitle="", page_num=None):
    """
    Build a standard content slide scaffold:
    - White background
    - Left edge bar (4px blue)
    - Title (Title Case, 18pt bold — NOT all caps; only cover/chapter titles are all caps)
    - Subtitle (12pt grey)
    - Official copyright footer: \u00a9 2026 Snowflake Inc. All Rights Reserved
    - Page number (optional, right-aligned)
    Returns the slide object ready for content.
    """
    slide = add_blank_slide(prs)
    # Edge bar
    add_rect(slide, EDGE_BAR_LEFT, EDGE_BAR_TOP, EDGE_BAR_WIDTH, EDGE_BAR_HEIGHT, SF_BLUE)
    # Title — title case, NOT all caps (per Snowflake 2026 brand guide)
    add_text(slide, PAD_LEFT, TITLE_TOP, CONTENT_W, Inches(0.4),
             title, size=18, bold=True, color=SF_DARK_TEXT)
    # Subtitle
    if subtitle:
        add_text(slide, PAD_LEFT, SUBTITLE_TOP, CONTENT_W, Inches(0.35),
                 subtitle, size=12, color=SF_BODY_GREY)
    # Official copyright footer
    add_text(slide, PAD_LEFT, FOOTER_TOP, Inches(6), Inches(0.15),
             COPYRIGHT_TEXT, size=6, color=SF_COPYRIGHT)
    # Page number (right-aligned, official position)
    if page_num is not None:
        add_text(slide, PAGE_NUM_LEFT, PAGE_NUM_TOP, PAGE_NUM_W, PAGE_NUM_H,
                 str(page_num), size=6, color=SF_PAGE_NUM,
                 align=PP_ALIGN.RIGHT)
    return slide

def add_dark_slide_frame(prs):
    """Blank dark-background slide (cover, chapter, thank you)."""
    slide = add_blank_slide(prs)
    set_solid_bg(slide, SF_MID_BLUE)
    # Bottom accent strip
    add_rect(slide, 0, Inches(5.54), Inches(4), Inches(0.085), SF_TEAL)
    return slide
```

---

## Slide Type Implementation Patterns

### 1. Cover Slide

```python
def build_cover(prs, title, subtitle, date_line, team_meta, customer_name=""):
    slide = add_dark_slide_frame(prs)
    # Header bar — text lives INSIDE the shape
    hbar = add_rect(slide, 0, 0, SLIDE_W, Inches(0.42), RGBColor(0x0a, 0x2c, 0x45))
    set_shape_text(hbar, "    ✦  SNOWFLAKE PROFESSIONAL SERVICES",
                   size=8, bold=True, color=SF_WHITE, align=PP_ALIGN.LEFT,
                   valign=MSO_ANCHOR.MIDDLE)
    # Customer badge — multi-line, text lives INSIDE the shape
    if customer_name:
        badge = add_rect(slide, Inches(8.6), Inches(0.52), Inches(1.3), Inches(0.7),
                         RGBColor(0x15, 0x45, 0x68))
        set_shape_text(badge, "PREPARED FOR", size=6,
                       color=RGBColor(0x88, 0xbb, 0xcc), align=PP_ALIGN.CENTER,
                       valign=MSO_ANCHOR.TOP)
        add_shape_para(badge, customer_name, size=14, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.CENTER)
    # Right accent bar (no text)
    add_rect(slide, Inches(9.7), Inches(1.1), Inches(0.03), Inches(2.6), SF_TEAL)
    # Title, subtitle, date, meta — standalone text on dark bg (no fill shape behind them)
    add_text(slide, PAD_LEFT, Inches(1.48), Inches(6.8), Inches(2.1),
             title.upper(), size=36, bold=True, color=SF_WHITE, wrap=True)
    add_rect(slide, PAD_LEFT, Inches(3.15), Inches(1.25), Inches(0.03), SF_TEAL)
    add_text(slide, PAD_LEFT, Inches(3.27), Inches(6.5), Inches(0.4),
             subtitle, size=14, bold=True, color=SF_WHITE)
    add_text(slide, PAD_LEFT, Inches(3.72), Inches(6.5), Inches(0.3),
             date_line, size=11, color=RGBColor(0xaa, 0xaa, 0xaa))
    add_text(slide, PAD_LEFT, Inches(5.35), CONTENT_W, Inches(0.2),
             team_meta, size=9, color=RGBColor(0x88, 0x88, 0x88))
    return slide
```

### 2. Chapter / Section Divider

```python
def build_chapter(prs, chapter_num, title, subtitle=""):
    slide = add_dark_slide_frame(prs)
    # All elements are standalone text on dark bg — no fill shapes hold text here
    add_text(slide, Inches(5.5), Inches(-0.5), Inches(5), Inches(4.5),
             str(chapter_num).zfill(2),
             size=200, bold=True, color=RGBColor(0x0f, 0x3a, 0x56))
    add_rect(slide, PAD_LEFT, Inches(1.7), Inches(0.042), Inches(1.45), SF_TEAL)
    add_text(slide, Inches(0.55), Inches(1.75), Inches(5), Inches(0.25),
             f"CHAPTER {str(chapter_num).zfill(2)}", size=10, bold=True, color=SF_TEAL)
    add_text(slide, Inches(0.55), Inches(2.07), Inches(7.5), Inches(1.8),
             title.upper(), size=48, bold=True, color=SF_WHITE, wrap=True)
    if subtitle:
        add_text(slide, Inches(0.55), Inches(3.42), Inches(6.5), Inches(0.5),
                 subtitle, size=14, color=RGBColor(0x88, 0xaa, 0xbb))
    return slide
```

### 3. Agenda Slide

```python
def build_agenda(prs, items):
    """
    items: list of dicts — num, sublabel, label, desc, time. Max 5.
    """
    slide = add_content_slide_frame(prs, "Agenda",
                                    "Today's kickoff — what we'll cover and when")
    n = len(items)
    col_w = CONTENT_W / n
    gap = Inches(0.1)
    for i, item in enumerate(items):
        x = PAD_LEFT + i * col_w
        item_w = col_w - gap

        # Header shape — num + sublabel live INSIDE the shape
        hdr = add_rect(slide, x, CONTENT_TOP, item_w, Inches(0.78), SF_MID_BLUE)
        set_shape_text(hdr, item["num"], size=26, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)
        add_shape_para(hdr, item.get("sublabel", "").upper(), size=7,
                       color=RGBColor(0xaa, 0xcc, 0xdd), align=PP_ALIGN.LEFT)

        # Body panel — light bg; label + desc are flowing content (standalone text ok over panel)
        body_top = CONTENT_TOP + Inches(0.78)
        body_h = SAFE_BOTTOM - body_top - Inches(0.35)
        add_rect(slide, x, body_top, item_w, body_h, SF_LIGHT_BG)
        add_text(slide, x + Inches(0.12), body_top + Inches(0.1), item_w - Inches(0.2),
                 Inches(0.28), item["label"].upper(), size=9, bold=True, color=SF_DARK_TEXT)
        add_text(slide, x + Inches(0.12), body_top + Inches(0.42), item_w - Inches(0.2),
                 body_h - Inches(0.58), item["desc"], size=8, color=SF_BODY_GREY, wrap=True)

        # Time badge — label lives INSIDE the shape
        badge_top = SAFE_BOTTOM - Inches(0.28)
        badge = add_rect(slide, x + Inches(0.12), badge_top,
                         item_w - Inches(0.24), Inches(0.22), SF_BLUE)
        set_shape_text(badge, item["time"], size=7, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    return slide
```

### 4. Two-Column Slide

```python
def build_two_column(prs, title, subtitle, left_header, left_label,
                     left_sections, right_header, right_label, right_sections):
    """
    left/right_sections: list of {"head": str, "bullets": [str, ...]}
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    col_w = (CONTENT_W - Inches(0.14)) / 2
    right_x = PAD_LEFT + col_w + Inches(0.14)

    def draw_column(x, header_bg, header_label, header_title, sections):
        # Column header — label + title live INSIDE the shape
        hdr = add_rect(slide, x, CONTENT_TOP, col_w, Inches(0.55), header_bg)
        set_shape_text(hdr, header_label.upper(), size=8,
                       color=RGBColor(0xaa, 0xcc, 0xdd),
                       align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)
        add_shape_para(hdr, header_title, size=12, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.LEFT)
        # Body panel — background only; flowing content uses standalone text
        body_top = CONTENT_TOP + Inches(0.55)
        body_h = SAFE_BOTTOM - body_top
        add_rect(slide, x, body_top, col_w, body_h, SF_LIGHT_BG)
        y = body_top + Inches(0.13)
        for sec in sections:
            add_text(slide, x + Inches(0.14), y, col_w - Inches(0.2), Inches(0.22),
                     sec["head"].upper(), size=8, bold=True, color=SF_MID_BLUE)
            y += Inches(0.24)
            for bullet in sec["bullets"]:
                add_text(slide, x + Inches(0.26), y, col_w - Inches(0.35), Inches(0.18),
                         "•  " + bullet, size=8.5, color=SF_DARK_TEXT, wrap=True)
                y += Inches(0.19)
            y += Inches(0.08)

    draw_column(PAD_LEFT, SF_MID_BLUE, left_label, left_header, left_sections)
    draw_column(right_x, SF_BLUE, right_label, right_header, right_sections)
    return slide
```

### 5. KPI Row + Table Slide

```python
def build_kpi_table(prs, title, subtitle, kpis, table_headers, table_rows):
    """
    kpis: list of {"value":str, "label":str} — 4 items
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    kpi_w = CONTENT_W / len(kpis)
    kpi_h = Inches(1.04)
    for i, kpi in enumerate(kpis):
        x = PAD_LEFT + i * kpi_w
        bg = SF_BLUE if i % 2 == 0 else SF_MID_BLUE
        # KPI box — value + label live INSIDE the shape
        box = add_rect(slide, x, CONTENT_TOP, kpi_w - Inches(0.1), kpi_h, bg)
        set_shape_text(box, kpi["value"], size=32, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        add_shape_para(box, kpi["label"], size=8, color=SF_TEAL, align=PP_ALIGN.CENTER)
    # Table (cells already own their text — no floating text boxes needed)
    tbl_top = CONTENT_TOP + kpi_h + Inches(0.12)
    tbl_h = SAFE_BOTTOM - tbl_top
    tbl = slide.shapes.add_table(
        len(table_rows) + 1, len(table_headers), PAD_LEFT, tbl_top, CONTENT_W, tbl_h
    ).table
    tbl.first_row = False; tbl.horz_banding = False   # explicit fills win over theme banding
    for c, hdr in enumerate(table_headers):
        cell = tbl.cell(0, c)
        cell.text = hdr
        cell.fill.solid(); cell.fill.fore_color.rgb = SF_MID_BLUE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9); p.font.bold = True
        p.font.color.rgb = SF_WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for r, row in enumerate(table_rows):
        bg = SF_LIGHT_ROW if r % 2 == 0 else SF_WHITE
        for c, val in enumerate(row):
            cell = tbl.cell(r + 1, c)
            cell.text = str(val)
            cell.fill.solid(); cell.fill.fore_color.rgb = bg
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9)
            p.font.bold = (c == 0)
            p.font.color.rgb = SF_DARK_TEXT if c == 0 else SF_TABLE_GREY
            p.font.name = "Arial"
            p.alignment = PP_ALIGN.LEFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return slide
```

### 6. Card Grid Slide (3×2 or 4×2)

```python
def build_card_grid(prs, title, subtitle, cards, cols=3):
    """
    cards: list of {"header_color": RGBColor, "icon": str, "title": str, "body": str}
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    rows = (len(cards) + cols - 1) // cols
    card_w = (CONTENT_W - Inches(0.1) * (cols - 1)) / cols
    card_h = (SAFE_BOTTOM - CONTENT_TOP - Inches(0.1) * (rows - 1)) / rows
    head_h = Inches(0.55)
    for i, card in enumerate(cards):
        row, col = divmod(i, cols)
        x = PAD_LEFT + col * (card_w + Inches(0.1))
        y = CONTENT_TOP + row * (card_h + Inches(0.1))
        hc = card.get("header_color", SF_MID_BLUE)
        # Card header — icon + title live INSIDE the shape
        hdr = add_rect(slide, x, y, card_w, head_h, hc)
        set_shape_text(hdr, card.get("icon", ""), size=13,
                       color=SF_WHITE, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)
        add_shape_para(hdr, card["title"].upper(), size=9, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.LEFT)
        # Card body — body text lives INSIDE the shape
        body = add_rect(slide, x, y + head_h, card_w, card_h - head_h, SF_LIGHT_BG)
        set_shape_text(body, card["body"], size=8.5, color=SF_DARK_TEXT,
                       align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, wrap=True)
    return slide
```

### 7. Timeline Slide (Two-Phase)

```python
def build_timeline(prs, title, subtitle, phase1, phase2):
    """
    phase1/phase2: {"label":str, "title":str, "date":str,
                    "tracks":[{"num":str,"label":str,"text":str},...], "milestone":str}
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    phase_h = Inches(0.58)
    col_w = CONTENT_W / 2

    for i, (phase, bg) in enumerate([(phase1, SF_MID_BLUE), (phase2, SF_BLUE)]):
        x = PAD_LEFT + i * col_w
        # Phase header bar — label + title + date live INSIDE the shape
        ph = add_rect(slide, x, CONTENT_TOP, col_w - Inches(0.05), phase_h, bg)
        set_shape_text(ph, phase["label"].upper(), size=8,
                       color=RGBColor(0xaa, 0xcc, 0xdd),
                       align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)
        add_shape_para(ph, phase["title"], size=13, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.LEFT)
        add_shape_para(ph, phase["date"], size=8,
                       color=RGBColor(0x99, 0xbb, 0xcc), align=PP_ALIGN.LEFT)
        # Track panel — background only; track items use standalone text
        track_top = CONTENT_TOP + phase_h
        track_h = SAFE_BOTTOM - track_top
        track_bg = RGBColor(0xee, 0xf4, 0xf8) if i == 0 else RGBColor(0xe8, 0xf4, 0xfc)
        add_rect(slide, x, track_top, col_w - Inches(0.05), track_h, track_bg)
        y = track_top + Inches(0.12)
        for t in phase["tracks"]:
            # Number badge — label lives INSIDE the shape
            nbadge = add_rect(slide, x + Inches(0.14), y, Inches(0.2), Inches(0.2), bg)
            set_shape_text(nbadge, t["num"], size=8, bold=True, color=SF_WHITE,
                           align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
            add_text(slide, x + Inches(0.4), y, col_w - Inches(0.55), Inches(0.18),
                     t["label"].upper(), size=8, bold=True, color=SF_DARK_TEXT)
            add_text(slide, x + Inches(0.4), y + Inches(0.19), col_w - Inches(0.55),
                     Inches(0.28), t["text"], size=8, color=SF_BODY_GREY, wrap=True)
            add_rect(slide, x + Inches(0.14), y + Inches(0.5),
                     col_w - Inches(0.28), Inches(0.01), SF_GRID)
            y += Inches(0.55)
        # Milestone bar — text lives INSIDE the shape
        ms_top = SAFE_BOTTOM - Inches(0.32)
        ms = add_rect(slide, x + Inches(0.1), ms_top, col_w - Inches(0.2), Inches(0.28), bg)
        set_shape_text(ms, phase.get("milestone", ""), size=8, bold=True,
                       color=SF_WHITE, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.MIDDLE)
    return slide
```

### 8. Table Slide (Deliverables / Data)

```python
def build_table_slide(prs, title, subtitle, headers, rows,
                      first_col_bold=True, col_widths=None):
    slide = add_content_slide_frame(prs, title, subtitle)
    tbl_top = CONTENT_TOP
    tbl_h = SAFE_BOTTOM - tbl_top
    shape = slide.shapes.add_table(
        len(rows) + 1, len(headers), PAD_LEFT, tbl_top, CONTENT_W, tbl_h
    )
    tbl = shape.table
    tbl.first_row = False; tbl.horz_banding = False   # explicit fills win over theme banding
    if col_widths:
        for c, w in enumerate(col_widths):
            tbl.columns[c].width = int(w)   # column widths must be integer EMU
    for c, hdr in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = hdr
        cell.fill.solid(); cell.fill.fore_color.rgb = SF_MID_BLUE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9); p.font.bold = True
        p.font.color.rgb = SF_WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for r, row in enumerate(rows):
        bg = SF_LIGHT_ROW if r % 2 == 0 else SF_WHITE
        for c, val in enumerate(row):
            cell = tbl.cell(r + 1, c)
            cell.text = str(val)
            cell.fill.solid(); cell.fill.fore_color.rgb = bg
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.font.bold = (c == 0 and first_col_bold)
            p.font.color.rgb = SF_DARK_TEXT if (c == 0 and first_col_bold) else SF_TABLE_GREY
            p.font.name = "Arial"
            p.alignment = PP_ALIGN.LEFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return slide
```

### 9. Team Cards Slide

```python
def build_team_slide(prs, title, subtitle, sf_team, client_team, client_label="Client"):
    """
    sf_team / client_team: list of {"name":str, "role":str, "bio":str}
    """
    slide = add_content_slide_frame(prs, title, subtitle)

    def draw_team_row(members, y, is_snowflake):
        n = len(members)
        card_w = (CONTENT_W - Inches(0.1) * (n - 1)) / n
        card_h = Inches(1.35)
        for i, m in enumerate(members):
            x = PAD_LEFT + i * (card_w + Inches(0.1))
            if is_snowflake:
                # Avatar shape — icon lives INSIDE the shape
                av = add_rect(slide, x, y, Inches(0.52), card_h, SF_MID_BLUE)
                set_shape_text(av, "✦", size=16, color=SF_TEAL,
                               align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
                # Info panel — name + role + bio live INSIDE the shape
                info = add_rect(slide, x + Inches(0.52), y, card_w - Inches(0.52),
                                card_h, RGBColor(0x0d, 0x3f, 0x5e))
                set_shape_text(info, m["name"], size=11, bold=True,
                               color=SF_WHITE, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)
                add_shape_para(info, m["role"], size=8, color=SF_TEAL, align=PP_ALIGN.LEFT)
                add_shape_para(info, m["bio"], size=8,
                               color=RGBColor(0xaa, 0xcc, 0xdd), align=PP_ALIGN.LEFT)
            else:
                av = add_rect(slide, x, y, Inches(0.52), card_h, SF_LIGHT_BG)
                set_shape_text(av, "●", size=14, color=SF_BODY_GREY,
                               align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
                info = add_rect(slide, x + Inches(0.52), y, card_w - Inches(0.52),
                                card_h, SF_LIGHT_BG)
                set_shape_text(info, m["name"], size=11, bold=True,
                               color=SF_DARK_TEXT, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)
                add_shape_para(info, m["role"], size=8,
                               color=SF_BODY_GREY, align=PP_ALIGN.LEFT)
                add_shape_para(info, m["bio"], size=8,
                               color=SF_BODY_GREY, align=PP_ALIGN.LEFT)

    y = CONTENT_TOP
    add_rect(slide, PAD_LEFT, y, CONTENT_W, Inches(0.02), SF_BLUE)
    add_text(slide, PAD_LEFT, y + Inches(0.05), CONTENT_W, Inches(0.22),
             "✦  SNOWFLAKE PROFESSIONAL SERVICES", size=8, bold=True, color=SF_BODY_GREY)
    y += Inches(0.28)
    draw_team_row(sf_team, y, is_snowflake=True)
    y += Inches(1.45)
    add_rect(slide, PAD_LEFT, y, CONTENT_W, Inches(0.01), SF_GRID)
    add_text(slide, PAD_LEFT, y + Inches(0.06), CONTENT_W, Inches(0.22),
             f"●  {client_label.upper()} COUNTERPARTS", size=8, bold=True, color=SF_BODY_GREY)
    y += Inches(0.3)
    draw_team_row(client_team, y, is_snowflake=False)
    return slide
```

### 10. RACI Matrix Slide

```python
def build_raci(prs, title, subtitle, headers, rows, legend=True):
    RACI_COLORS = {
        "R": (SF_MID_BLUE,                       SF_WHITE),
        "A": (RGBColor(0xdd, 0xee, 0xf8),        SF_BLUE),
        "C": (RGBColor(0xdd, 0xee, 0xf8),        SF_BLUE),
        "I": (SF_LIGHT_BG,                        SF_BODY_GREY),
    }
    slide = add_content_slide_frame(prs, title, subtitle)
    legend_h = Inches(0.28) if legend else Inches(0)
    tbl_h = SAFE_BOTTOM - CONTENT_TOP - legend_h - Inches(0.06)
    tbl = slide.shapes.add_table(
        len(rows) + 1, len(headers), PAD_LEFT, CONTENT_TOP, CONTENT_W, tbl_h
    ).table
    tbl.first_row = False; tbl.horz_banding = False   # explicit RACI cell fills win over banding
    for c, hdr in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = hdr
        cell.fill.solid(); cell.fill.fore_color.rgb = SF_MID_BLUE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(8); p.font.bold = True
        p.font.color.rgb = SF_WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for r, row in enumerate(rows):
        bg_base = SF_LIGHT_ROW if r % 2 == 0 else SF_WHITE
        for c, val in enumerate(row):
            cell = tbl.cell(r + 1, c)
            cell.text = val
            if c == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = bg_base
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(8.5); p.font.bold = True
                p.font.color.rgb = SF_DARK_TEXT; p.font.name = "Arial"
                p.alignment = PP_ALIGN.LEFT
            elif val.upper() in RACI_COLORS:
                bg, fg = RACI_COLORS[val.upper()]
                cell.fill.solid(); cell.fill.fore_color.rgb = bg
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(9); p.font.bold = True
                p.font.color.rgb = fg; p.font.name = "Arial"
                p.alignment = PP_ALIGN.CENTER
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = bg_base
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(8.5); p.font.name = "Arial"
                p.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if legend:
        legend_y = SAFE_BOTTOM - legend_h + Inches(0.04)
        items = [("R","Responsible"),("A","Accountable"),("C","Consulted"),("I","Informed")]
        lx = PAD_LEFT
        for code, label in items:
            bg, fg = RACI_COLORS[code]
            # Legend badge — code lives INSIDE the shape
            b = add_rect(slide, lx, legend_y, Inches(0.22), Inches(0.2), bg)
            set_shape_text(b, code, size=8, bold=True, color=fg,
                           align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
            add_text(slide, lx + Inches(0.25), legend_y, Inches(1.0), Inches(0.2),
                     f"— {label}", size=7, color=SF_BODY_GREY)
            lx += Inches(1.4)
    return slide
```

### 11. Ways of Working (4-column)

```python
def build_wow(prs, title, subtitle, columns):
    """columns: list of {"header_color":RGBColor,"icon":str,"title":str,"items":[str,...]}"""
    return build_card_grid(prs, title, subtitle,
        [{"header_color": c["header_color"],
          "icon": c["icon"],
          "title": c["title"],
          "body": "\n".join(f"–  {it}" for it in c["items"])}
         for c in columns],
        cols=4)
```

### 12. Thank You / Closing Slide

```python
def build_thank_you(prs, next_steps, team_contacts):
    """
    next_steps: list of {"num":str, "text":str}
    team_contacts: list of {"name":str, "role":str, "email":str}
    """
    slide = add_dark_slide_frame(prs)
    add_rect(slide, PAD_LEFT, Inches(1.7), Inches(0.042), Inches(1.8), SF_TEAL)
    add_text(slide, Inches(0.55), Inches(1.7), Inches(5), Inches(0.42), "✦",
             size=30, color=SF_TEAL)
    add_text(slide, Inches(0.55), Inches(2.12), Inches(6.5), Inches(0.9),
             "THANK YOU", size=48, bold=True, color=SF_WHITE)
    add_text(slide, Inches(0.55), Inches(3.05), Inches(6.5), Inches(0.35),
             "We're excited to get started. Here's what happens next.",
             size=14, color=RGBColor(0xaa, 0xaa, 0xaa))

    y = Inches(3.55)
    for step in next_steps:
        # Step number badge — num lives INSIDE the shape
        nb = add_rect(slide, Inches(0.55), y, Inches(0.22), Inches(0.22), SF_TEAL)
        set_shape_text(nb, step["num"], size=8, bold=True, color=SF_MID_BLUE,
                       align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        add_text(slide, Inches(0.85), y, Inches(6), Inches(0.22),
                 step["text"], size=10, color=SF_WHITE)
        y += Inches(0.3)

    # Contact card — background panel
    card_x = Inches(7.8)
    add_rect(slide, card_x, Inches(0.9), Inches(2.1), Inches(3.7),
             RGBColor(0x15, 0x45, 0x68))
    add_text(slide, card_x + Inches(0.18), Inches(1.0), Inches(1.8), Inches(0.22),
             "YOUR SNOWFLAKE TEAM", size=7, color=RGBColor(0x88, 0xaa, 0xcc))
    cy = Inches(1.28)
    for contact in team_contacts:
        add_text(slide, card_x + Inches(0.18), cy, Inches(1.8), Inches(0.22),
                 contact["name"], size=10, bold=True, color=SF_WHITE)
        add_text(slide, card_x + Inches(0.18), cy + Inches(0.22), Inches(1.8), Inches(0.18),
                 contact["role"], size=8, color=SF_TEAL)
        add_text(slide, card_x + Inches(0.18), cy + Inches(0.4), Inches(1.8), Inches(0.18),
                 contact["email"], size=7.5, color=RGBColor(0x88, 0xaa, 0xcc))
        add_rect(slide, card_x + Inches(0.18), cy + Inches(0.62), Inches(1.7),
                 Inches(0.01), RGBColor(0x22, 0x55, 0x77))
        cy += Inches(0.75)
    return slide
```
