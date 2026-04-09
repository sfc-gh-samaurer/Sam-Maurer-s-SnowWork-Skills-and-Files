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

## Dependencies

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
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
SF_TEAL        = RGBColor(0x71, 0xD3, 0xDC)   # --sf-teal
SF_ORANGE      = RGBColor(0xFF, 0x9F, 0x36)   # --sf-orange
SF_BORDER      = RGBColor(0xC8, 0xC8, 0xC8)   # --sf-border
SF_GRID        = RGBColor(0xDD, 0xDD, 0xDD)   # --sf-grid
SF_LIGHT_ROW   = RGBColor(0xF8, 0xFA, 0xFB)   # --sf-light-row
SF_TABLE_GREY  = RGBColor(0x71, 0x71, 0x71)   # --sf-table-grey
SF_GREEN       = RGBColor(0x2E, 0xCC, 0x71)
SF_AMBER       = RGBColor(0xF5, 0xA6, 0x23)
SF_RED         = RGBColor(0xE7, 0x4C, 0x3C)
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
    """Add a filled rectangle. fill=None → transparent. line=None → no border."""
    from pptx.util import Emu
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
    return shape

def add_text(slide, left, top, width, height, text, size=10, bold=False,
             color=SF_DARK_TEXT, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
             wrap=True, italic=False):
    """Add a text box. Returns the shape."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Arial"
    p.alignment = align
    tf.vertical_anchor = valign
    return tb

def add_para(tf, text, size=9, bold=False, color=SF_DARK_TEXT,
             align=PP_ALIGN.LEFT, space_before=Pt(0), space_after=Pt(3)):
    """Append a paragraph to an existing text frame."""
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

## Slide Structure Helpers

```python
def add_content_slide_frame(prs, title, subtitle=""):
    """
    Build a standard content slide scaffold:
    - White background
    - Left edge bar (4px blue)
    - Title (ALL CAPS, 18pt bold)
    - Subtitle (12pt grey)
    - Footer
    Returns the slide object ready for content.
    """
    slide = add_blank_slide(prs)
    # Edge bar
    add_rect(slide, EDGE_BAR_LEFT, EDGE_BAR_TOP, EDGE_BAR_WIDTH, EDGE_BAR_HEIGHT, SF_BLUE)
    # Title
    add_text(slide, PAD_LEFT, TITLE_TOP, CONTENT_W, Inches(0.4),
             title.upper(), size=18, bold=True, color=SF_DARK_TEXT)
    # Subtitle
    if subtitle:
        add_text(slide, PAD_LEFT, SUBTITLE_TOP, CONTENT_W, Inches(0.35),
                 subtitle, size=12, color=SF_BODY_GREY)
    # Footer
    add_text(slide, PAD_LEFT, FOOTER_TOP, Inches(6), Inches(0.2),
             "Confidential — Snowflake Professional Services",
             size=7, color=SF_BODY_GREY)
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
    # Header bar (logo area)
    add_rect(slide, 0, 0, SLIDE_W, Inches(0.42), RGBColor(0x0a, 0x2c, 0x45))
    add_text(slide, PAD_LEFT, Inches(0.09), Inches(4), Inches(0.25),
             "✦  SNOWFLAKE PROFESSIONAL SERVICES",
             size=8, bold=True, color=SF_WHITE)
    # Customer badge (top right)
    if customer_name:
        add_rect(slide, Inches(8.6), Inches(0.52), Inches(1.3), Inches(0.7),
                 RGBColor(0x15, 0x45, 0x68))
        add_text(slide, Inches(8.6), Inches(0.55), Inches(1.3), Inches(0.22),
                 "PREPARED FOR", size=6, color=RGBColor(0x88, 0xbb, 0xcc),
                 align=PP_ALIGN.CENTER)
        add_text(slide, Inches(8.6), Inches(0.76), Inches(1.3), Inches(0.38),
                 customer_name, size=14, bold=True, color=SF_WHITE,
                 align=PP_ALIGN.CENTER)
    # Right accent bar
    add_rect(slide, Inches(9.7), Inches(1.1), Inches(0.03), Inches(2.6), SF_TEAL)
    # Title
    add_text(slide, PAD_LEFT, Inches(1.48), Inches(6.8), Inches(2.1),
             title.upper(), size=36, bold=True, color=SF_WHITE, wrap=True)
    # Teal rule
    add_rect(slide, PAD_LEFT, Inches(3.15), Inches(1.25), Inches(0.03), SF_TEAL)
    # Subtitle
    add_text(slide, PAD_LEFT, Inches(3.27), Inches(6.5), Inches(0.4),
             subtitle, size=14, bold=True, color=SF_WHITE)
    # Date line
    add_text(slide, PAD_LEFT, Inches(3.72), Inches(6.5), Inches(0.3),
             date_line, size=11, color=RGBColor(0xaa, 0xaa, 0xaa))
    # Team meta (footer area)
    add_text(slide, PAD_LEFT, Inches(5.35), CONTENT_W, Inches(0.2),
             team_meta, size=9, color=RGBColor(0x88, 0x88, 0x88))
    return slide
```

### 2. Chapter / Section Divider

```python
def build_chapter(prs, chapter_num, title, subtitle=""):
    slide = add_dark_slide_frame(prs)
    # Ghost chapter number (very light, large)
    add_text(slide, Inches(5.5), Inches(-0.5), Inches(5), Inches(4.5),
             str(chapter_num).zfill(2),
             size=200, bold=True, color=RGBColor(0x0f, 0x3a, 0x56))
    # Left accent bar
    add_rect(slide, PAD_LEFT, Inches(1.7), Inches(0.042), Inches(1.45), SF_TEAL)
    # Chapter label
    add_text(slide, Inches(0.55), Inches(1.75), Inches(5), Inches(0.25),
             f"CHAPTER {str(chapter_num).zfill(2)}",
             size=10, bold=True, color=SF_TEAL)
    # Title (2 lines)
    add_text(slide, Inches(0.55), Inches(2.07), Inches(7.5), Inches(1.8),
             title.upper(), size=48, bold=True, color=SF_WHITE, wrap=True)
    # Subtitle
    if subtitle:
        add_text(slide, Inches(0.55), Inches(3.42), Inches(6.5), Inches(0.5),
                 subtitle, size=14, color=RGBColor(0x88, 0xaa, 0xbb))
    return slide
```

### 3. Agenda Slide

```python
def build_agenda(prs, items):
    """
    items: list of dicts with keys: num, sublabel, label, desc, time
    Example: {"num":"01","sublabel":"Welcome","label":"About Our Team",
              "desc":"Who we are...", "time":"9:00 – 9:20"}
    Max 5 items (one per column).
    """
    slide = add_content_slide_frame(prs, "Agenda",
                                    "Today's kickoff — what we'll cover and when")
    n = len(items)
    col_w = CONTENT_W / n
    gap = Inches(0.1)
    for i, item in enumerate(items):
        x = PAD_LEFT + i * (col_w)
        item_w = col_w - gap
        # Header (dark blue)
        add_rect(slide, x, CONTENT_TOP, item_w, Inches(0.78), SF_MID_BLUE)
        add_text(slide, x + Inches(0.14), CONTENT_TOP + Inches(0.1), item_w, Inches(0.5),
                 item["num"], size=26, bold=True, color=SF_WHITE)
        add_text(slide, x + Inches(0.14), CONTENT_TOP + Inches(0.54), item_w, Inches(0.2),
                 item.get("sublabel","").upper(), size=7, color=RGBColor(0xaa,0xcc,0xdd))
        # Body (light bg)
        body_top = CONTENT_TOP + Inches(0.78)
        body_h = SAFE_BOTTOM - body_top - Inches(0.35)
        add_rect(slide, x, body_top, item_w, body_h, SF_LIGHT_BG)
        add_text(slide, x + Inches(0.12), body_top + Inches(0.1), item_w - Inches(0.2),
                 Inches(0.3), item["label"].upper(),
                 size=9, bold=True, color=SF_DARK_TEXT)
        add_text(slide, x + Inches(0.12), body_top + Inches(0.42), item_w - Inches(0.2),
                 body_h - Inches(0.6), item["desc"], size=8, color=SF_BODY_GREY, wrap=True)
        # Time badge
        badge_top = SAFE_BOTTOM - Inches(0.28)
        add_rect(slide, x + Inches(0.12), badge_top, item_w - Inches(0.24), Inches(0.22), SF_BLUE)
        add_text(slide, x + Inches(0.12), badge_top, item_w - Inches(0.24), Inches(0.22),
                 item["time"], size=7, bold=True, color=SF_WHITE, align=PP_ALIGN.CENTER,
                 valign=MSO_ANCHOR.MIDDLE)
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
        add_rect(slide, x, CONTENT_TOP, col_w, Inches(0.55), header_bg)
        add_text(slide, x + Inches(0.16), CONTENT_TOP + Inches(0.06), col_w, Inches(0.2),
                 header_label.upper(), size=8, color=RGBColor(0xaa,0xcc,0xdd))
        add_text(slide, x + Inches(0.16), CONTENT_TOP + Inches(0.24), col_w, Inches(0.28),
                 header_title, size=12, bold=True, color=SF_WHITE)
        body_top = CONTENT_TOP + Inches(0.55)
        body_h = SAFE_BOTTOM - body_top
        add_rect(slide, x, body_top, col_w, body_h, SF_LIGHT_BG)
        y = body_top + Inches(0.13)
        for sec in sections:
            add_text(slide, x + Inches(0.14), y, col_w - Inches(0.2), Inches(0.22),
                     sec["head"].upper(), size=8, bold=True, color=SF_MID_BLUE)
            y += Inches(0.24)
            for bullet in sec["bullets"]:
                tb = slide.shapes.add_textbox(x + Inches(0.26), y, col_w - Inches(0.35), Inches(0.18))
                tf = tb.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = "•  " + bullet
                run.font.size = Pt(8.5)
                run.font.color.rgb = SF_DARK_TEXT
                run.font.name = "Arial"
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
    table_headers: list of str
    table_rows: list of lists of str
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    # KPI row
    kpi_w = CONTENT_W / len(kpis)
    kpi_h = Inches(1.04)
    for i, kpi in enumerate(kpis):
        x = PAD_LEFT + i * kpi_w
        bg = SF_BLUE if i % 2 == 0 else SF_MID_BLUE
        add_rect(slide, x, CONTENT_TOP, kpi_w - Inches(0.1), kpi_h, bg)
        add_text(slide, x, CONTENT_TOP + Inches(0.17), kpi_w - Inches(0.1), Inches(0.5),
                 kpi["value"], size=32, bold=True, color=SF_WHITE,
                 align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        add_text(slide, x, CONTENT_TOP + Inches(0.67), kpi_w - Inches(0.1), Inches(0.3),
                 kpi["label"], size=8, color=SF_TEAL,
                 align=PP_ALIGN.CENTER)
    # Table
    tbl_top = CONTENT_TOP + kpi_h + Inches(0.12)
    tbl_h = SAFE_BOTTOM - tbl_top
    n_rows = len(table_rows) + 1
    n_cols = len(table_headers)
    tbl = slide.shapes.add_table(n_rows, n_cols, PAD_LEFT, tbl_top, CONTENT_W, tbl_h).table
    # Header
    for c, hdr in enumerate(table_headers):
        cell = tbl.cell(0, c)
        cell.text = hdr
        cell.fill.solid(); cell.fill.fore_color.rgb = SF_MID_BLUE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9); p.font.bold = True
        p.font.color.rgb = SF_WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Data rows
    for r, row in enumerate(table_rows):
        bg = SF_LIGHT_ROW if r % 2 == 0 else SF_WHITE
        for c, val in enumerate(row):
            cell = tbl.cell(r + 1, c)
            cell.text = val
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
    cols: 3 or 4
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
        # Header
        add_rect(slide, x, y, card_w, head_h, hc)
        add_text(slide, x + Inches(0.14), y + Inches(0.07), card_w - Inches(0.18),
                 Inches(0.2), card.get("icon",""), size=13, color=SF_WHITE)
        add_text(slide, x + Inches(0.14), y + Inches(0.27), card_w - Inches(0.18),
                 Inches(0.24), card["title"].upper(), size=9, bold=True, color=SF_WHITE)
        # Body
        add_rect(slide, x, y + head_h, card_w, card_h - head_h, SF_LIGHT_BG)
        add_text(slide, x + Inches(0.13), y + head_h + Inches(0.1),
                 card_w - Inches(0.2), card_h - head_h - Inches(0.15),
                 card["body"], size=8.5, color=SF_DARK_TEXT, wrap=True)
    return slide
```

### 7. Timeline Slide (Two-Phase)

```python
def build_timeline(prs, title, subtitle, phase1, phase2):
    """
    phase1/phase2: {
      "label": str, "title": str, "date": str,
      "tracks": [{"num":str, "label":str, "text":str}, ...],
      "milestone": str
    }
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    phase_h = Inches(0.58)
    phase_y = CONTENT_TOP
    col_w = CONTENT_W / 2

    for i, (phase, bg) in enumerate([(phase1, SF_MID_BLUE), (phase2, SF_BLUE)]):
        x = PAD_LEFT + i * col_w
        # Phase header
        add_rect(slide, x, phase_y, col_w - Inches(0.05), phase_h, bg)
        add_text(slide, x + Inches(0.18), phase_y + Inches(0.06), col_w, Inches(0.18),
                 phase["label"].upper(), size=8, color=RGBColor(0xaa,0xcc,0xdd))
        add_text(slide, x + Inches(0.18), phase_y + Inches(0.22), col_w, Inches(0.25),
                 phase["title"], size=13, bold=True, color=SF_WHITE)
        add_text(slide, x + Inches(0.18), phase_y + Inches(0.44), col_w, Inches(0.18),
                 phase["date"], size=8, color=RGBColor(0x99,0xbb,0xcc))
        # Track body
        track_top = phase_y + phase_h
        track_h = SAFE_BOTTOM - track_top
        track_bg = RGBColor(0xee, 0xf4, 0xf8) if i == 0 else RGBColor(0xe8, 0xf4, 0xfc)
        add_rect(slide, x, track_top, col_w - Inches(0.05), track_h, track_bg)
        y = track_top + Inches(0.12)
        for t in phase["tracks"]:
            # Number badge
            add_rect(slide, x + Inches(0.14), y, Inches(0.2), Inches(0.2), bg)
            add_text(slide, x + Inches(0.14), y, Inches(0.2), Inches(0.2),
                     t["num"], size=8, bold=True, color=SF_WHITE,
                     align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
            add_text(slide, x + Inches(0.4), y, col_w - Inches(0.55), Inches(0.18),
                     t["label"].upper(), size=8, bold=True, color=SF_DARK_TEXT)
            add_text(slide, x + Inches(0.4), y + Inches(0.19), col_w - Inches(0.55),
                     Inches(0.28), t["text"], size=8, color=SF_BODY_GREY, wrap=True)
            # Divider
            add_rect(slide, x + Inches(0.14), y + Inches(0.5), col_w - Inches(0.28),
                     Inches(0.01), SF_GRID)
            y += Inches(0.55)
        # Milestone bar (pinned to bottom)
        ms_top = SAFE_BOTTOM - Inches(0.32)
        add_rect(slide, x + Inches(0.1), ms_top, col_w - Inches(0.2), Inches(0.28), bg)
        add_text(slide, x + Inches(0.2), ms_top, col_w - Inches(0.25), Inches(0.28),
                 phase.get("milestone",""), size=8, bold=True, color=SF_WHITE,
                 valign=MSO_ANCHOR.MIDDLE)
    return slide
```

### 8. Table Slide (Deliverables / Data)

```python
def build_table_slide(prs, title, subtitle, headers, rows,
                      first_col_bold=True, col_widths=None):
    """
    col_widths: optional list of Inches values that sum to CONTENT_W
    """
    slide = add_content_slide_frame(prs, title, subtitle)
    tbl_top = CONTENT_TOP
    tbl_h = SAFE_BOTTOM - tbl_top
    n_rows = len(rows) + 1
    n_cols = len(headers)
    shape = slide.shapes.add_table(n_rows, n_cols, PAD_LEFT, tbl_top, CONTENT_W, tbl_h)
    tbl = shape.table
    if col_widths:
        for c, w in enumerate(col_widths):
            tbl.columns[c].width = w
    # Header row
    for c, hdr in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = hdr
        cell.fill.solid(); cell.fill.fore_color.rgb = SF_MID_BLUE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9); p.font.bold = True
        p.font.color.rgb = SF_WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Data rows
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
                add_rect(slide, x, y, Inches(0.52), card_h, SF_MID_BLUE)
                add_text(slide, x, y + Inches(0.55), Inches(0.52), Inches(0.3),
                         "✦", size=16, color=SF_TEAL, align=PP_ALIGN.CENTER)
                add_rect(slide, x + Inches(0.52), y, card_w - Inches(0.52), card_h,
                         RGBColor(0x0d, 0x3f, 0x5e))
                name_color = SF_WHITE
                role_color = SF_TEAL
                bio_color = RGBColor(0xaa, 0xcc, 0xdd)
            else:
                add_rect(slide, x, y, Inches(0.52), card_h, SF_LIGHT_BG)
                add_rect(slide, x + Inches(0.52), y, card_w - Inches(0.52), card_h,
                         SF_LIGHT_BG)
                add_text(slide, x, y + Inches(0.55), Inches(0.52), Inches(0.3),
                         "●", size=14, color=SF_BODY_GREY, align=PP_ALIGN.CENTER)
                name_color = SF_DARK_TEXT
                role_color = SF_BODY_GREY
                bio_color = SF_BODY_GREY
            tx = x + Inches(0.65)
            tw = card_w - Inches(0.75)
            add_text(slide, tx, y + Inches(0.1), tw, Inches(0.28),
                     m["name"], size=11, bold=True, color=name_color)
            add_text(slide, tx, y + Inches(0.36), tw, Inches(0.22),
                     m["role"], size=8, color=role_color)
            add_text(slide, tx, y + Inches(0.6), tw, Inches(0.65),
                     m["bio"], size=8, color=bio_color, wrap=True)

    # Section labels
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
    """
    headers: ["Activity", "Name1\nRole1", ...]
    rows: [["Activity name", "R", "A", "I", "C", "I", "R"], ...]
    RACI values: R / A / C / I
    """
    RACI_COLORS = {
        "R": (SF_MID_BLUE,    SF_WHITE),
        "A": (RGBColor(0xdd,0xee,0xf8), SF_BLUE),
        "C": (RGBColor(0xdd,0xee,0xf8), SF_BLUE),
        "I": (SF_LIGHT_BG,   SF_BODY_GREY),
    }
    slide = add_content_slide_frame(prs, title, subtitle)
    tbl_top = CONTENT_TOP
    legend_h = Inches(0.28) if legend else Inches(0)
    tbl_h = SAFE_BOTTOM - tbl_top - legend_h - Inches(0.06)
    n_rows = len(rows) + 1
    n_cols = len(headers)
    shape = slide.shapes.add_table(n_rows, n_cols, PAD_LEFT, tbl_top, CONTENT_W, tbl_h)
    tbl = shape.table
    # Header
    for c, hdr in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = hdr
        cell.fill.solid(); cell.fill.fore_color.rgb = SF_MID_BLUE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(8); p.font.bold = True
        p.font.color.rgb = SF_WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Data rows
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
    # Legend
    if legend:
        legend_y = SAFE_BOTTOM - legend_h + Inches(0.04)
        items = [("R", "Responsible"), ("A", "Accountable"), ("C", "Consulted"), ("I", "Informed")]
        lx = PAD_LEFT
        for code, label in items:
            bg, fg = RACI_COLORS[code]
            add_rect(slide, lx, legend_y, Inches(0.22), Inches(0.2), bg)
            add_text(slide, lx, legend_y, Inches(0.22), Inches(0.2),
                     code, size=8, bold=True, color=fg,
                     align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
            add_text(slide, lx + Inches(0.25), legend_y, Inches(1.0), Inches(0.2),
                     f"— {label}", size=7, color=SF_BODY_GREY)
            lx += Inches(1.4)
    return slide
```

### 11. Ways of Working (4-column)

```python
def build_wow(prs, title, subtitle, columns):
    """
    columns: list of {"header_color": RGBColor, "icon": str, "title": str,
                       "items": [str, ...]}  — 4 items
    """
    return build_card_grid(prs, title, subtitle,
        [{"header_color": c["header_color"], "icon": c["icon"],
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
    # Left accent bar
    add_rect(slide, PAD_LEFT, Inches(1.7), Inches(0.042), Inches(1.8), SF_TEAL)
    # SF Icon + heading
    add_text(slide, Inches(0.55), Inches(1.7), Inches(5), Inches(0.42),
             "✦", size=30, color=SF_TEAL)
    add_text(slide, Inches(0.55), Inches(2.12), Inches(6.5), Inches(0.9),
             "THANK YOU", size=48, bold=True, color=SF_WHITE)
    add_text(slide, Inches(0.55), Inches(3.05), Inches(6.5), Inches(0.35),
             "We're excited to get started. Here's what happens next.",
             size=14, color=RGBColor(0xaa,0xaa,0xaa))
    # Next steps
    y = Inches(3.55)
    for step in next_steps:
        add_rect(slide, Inches(0.55), y, Inches(0.22), Inches(0.22), SF_TEAL)
        add_text(slide, Inches(0.55), y, Inches(0.22), Inches(0.22),
                 step["num"], size=8, bold=True, color=SF_MID_BLUE,
                 align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        add_text(slide, Inches(0.85), y, Inches(6), Inches(0.22),
                 step["text"], size=10, color=SF_WHITE)
        y += Inches(0.3)
    # Contact card (right panel)
    card_x = Inches(7.8)
    add_rect(slide, card_x, Inches(0.9), Inches(2.1), Inches(3.7),
             RGBColor(0x15, 0x45, 0x68))
    add_text(slide, card_x + Inches(0.18), Inches(1.0), Inches(1.8), Inches(0.22),
             "YOUR SNOWFLAKE TEAM", size=7, color=RGBColor(0x88,0xaa,0xcc))
    cy = Inches(1.28)
    for contact in team_contacts:
        add_text(slide, card_x + Inches(0.18), cy, Inches(1.8), Inches(0.22),
                 contact["name"], size=10, bold=True, color=SF_WHITE)
        add_text(slide, card_x + Inches(0.18), cy + Inches(0.22), Inches(1.8), Inches(0.18),
                 contact["role"], size=8, color=SF_TEAL)
        add_text(slide, card_x + Inches(0.18), cy + Inches(0.4), Inches(1.8), Inches(0.18),
                 contact["email"], size=7.5, color=RGBColor(0x88,0xaa,0xcc))
        # Divider
        add_rect(slide, card_x + Inches(0.18), cy + Inches(0.62), Inches(1.7),
                 Inches(0.01), RGBColor(0x22,0x55,0x77))
        cy += Inches(0.75)
    return slide
```

---

## Putting It Together

```python
def build_deck(output_path):
    prs = new_deck()

    build_cover(prs,
        title="Data Platform Architecture Modernization",
        subtitle="Project Kickoff — April 2026",
        date_line="180-Day Engagement  ·  April 2026 – October 2026",
        team_meta="Keith Hoyle · SA   |   Sam Maurer · PrM   |   TBD · SDM",
        customer_name="Okta D&I")

    build_agenda(prs, [
        {"num":"01","sublabel":"Welcome","label":"About Our Team","desc":"Who we are...","time":"9:00–9:20"},
        # ...
    ])

    # ... add all other slides ...

    prs.save(output_path)
    print(f"Saved: {output_path}")
```

---

## Approximation Reference

| HTML/CSS feature | python-pptx approximation |
|---|---|
| `border-radius: 8px` | Square corners (no native support) |
| `linear-gradient(...)` bg | Solid fill with dominant/start color |
| `clip-path` wave | Omitted — replaced with solid rect or nothing |
| `overflow: hidden` clipping | Not needed (content is manually positioned) |
| `box-shadow` | Omitted |
| `::before/::after` decoration | Omitted or replaced with a simple `add_rect` |
| Ghost number (opacity ~3%) | Very light text color approximation |
| CSS `opacity` on elements | Not supported natively; use lighter color values |
| Flexbox/grid auto-layout | Manual position calculation with Inches() math |
| `text-transform: uppercase` | Apply `.upper()` in Python before setting text |
