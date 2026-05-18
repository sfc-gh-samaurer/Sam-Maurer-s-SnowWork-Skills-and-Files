# TDR Design System Reference

## Overview

This is a self-contained design system for generating Technical Deal Review (TDR) presentation decks using python-pptx. All brand tokens, geometry constants, utility functions, and slide patterns are inlined below. No external file dependencies are required.

The system produces 10×5.625" (960×540px) widescreen slides with Snowflake branding. Slides are designed HTML-first (for visual fidelity previews) then rendered to python-pptx native shapes for an editable PPTX output.

---

## CSS Design Tokens

Used for HTML-first slide design at 960×540px canvas size:

```css
:root {
  --sf-blue: #29B5E8;
  --sf-mid-blue: #11567F;
  --sf-white: #FFFFFF;
  --sf-dark-text: #262626;
  --sf-body-grey: #5B5B5B;
  --sf-light-bg: #F5F5F5;
  --sf-teal: #75CDD7;
  --sf-orange: #FF9F36;
  --sf-violet: #7254A3;
  --sf-pink: #D45B90;
  --sf-midnight: #000000;
  --sf-border: #C8C8C8;
  --sf-grid: #DDDDDD;
  --sf-table-grey: #717171;
  --sf-light-row: #F8FAFB;
  --sf-green: #2ECC71;
  --sf-amber: #F5A623;
  --sf-red: #E74C3C;
  --sf-light-green: #E8F8EF;
  --sf-light-amber: #FFF3E0;
  --sf-light-red: #FDEDEC;
  --sf-light-blue: #E8F4FD;
  --slide-w: 960px;
  --slide-h: 540px;
  --pad-left: 38px;
  --pad-right: 48px;
  --title-top: 29px;
  --subtitle-top: 69px;
  --content-top: 144px;
  --footer-top: 511px;
  --safe-bottom: 490px;
  --content-w: 876px;
  --font: Arial, 'Helvetica Neue', Helvetica, sans-serif;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 10px;
}
```

---

## Brand Color Constants (python-pptx)

```python
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SF_BLUE = RGBColor(0x29, 0xB5, 0xE8)
SF_MID_BLUE = RGBColor(0x11, 0x56, 0x7F)
SF_DARK_BG = RGBColor(0x0c, 0x33, 0x51)
SF_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SF_DARK_TEXT = RGBColor(0x26, 0x26, 0x26)
SF_BODY_GREY = RGBColor(0x5B, 0x5B, 0x5B)
SF_LIGHT_BG = RGBColor(0xF5, 0xF5, 0xF5)
SF_TEAL = RGBColor(0x75, 0xCD, 0xD7)
SF_ORANGE = RGBColor(0xFF, 0x9F, 0x36)
SF_BORDER = RGBColor(0xC8, 0xC8, 0xC8)
SF_GRID = RGBColor(0xDD, 0xDD, 0xDD)
SF_LIGHT_ROW = RGBColor(0xF8, 0xFA, 0xFB)
SF_TABLE_GREY = RGBColor(0x71, 0x71, 0x71)
SF_GREEN = RGBColor(0x2E, 0xCC, 0x71)
SF_AMBER = RGBColor(0xF5, 0xA6, 0x23)
SF_RED = RGBColor(0xE7, 0x4C, 0x3C)
SF_VIOLET = RGBColor(0x72, 0x54, 0xA3)
SF_PAGE_NUM = RGBColor(0x91, 0x91, 0x91)
SF_COPYRIGHT = RGBColor(0x92, 0x92, 0x92)
SF_LIGHT_BLUE = RGBColor(0xE8, 0xF4, 0xFD)
SF_LIGHT_GREEN = RGBColor(0xE8, 0xF8, 0xEF)
```

---

## Geometry Constants

```python
SLIDE_W = Inches(10)
SLIDE_H = Inches(5.625)
PAD_LEFT = Inches(0.396)
TITLE_TOP = Inches(0.302)
SUBTITLE_TOP = Inches(0.583)
CONTENT_TOP = Inches(1.0)
FOOTER_TOP = Inches(5.323)
SAFE_BOTTOM = Inches(5.104)
CONTENT_W = Inches(9.125)
EDGE_BAR_LEFT = Inches(0)
EDGE_BAR_TOP = Inches(0.375)
EDGE_BAR_WIDTH = Inches(0.042)
EDGE_BAR_HEIGHT = Inches(0.396)
COPYRIGHT_TEXT = "© 2026 Snowflake Inc. All Rights Reserved"
```

---

## Core Utility Functions

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import copy


def new_deck():
    """Create a new blank presentation with correct slide dimensions."""
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def add_blank_slide(prs):
    """Add a blank slide to the presentation."""
    layout = prs.slide_layouts[6]  # Blank layout
    return prs.slides.add_slide(layout)


def set_solid_bg(slide, color):
    """Set a solid background color on a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color=None, border_color=None, border_width=None, radius=None):
    """Add a rectangle shape to a slide with optional fill, border, and rounded corners."""
    if radius:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.adjustments[0] = radius
    else:
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)

    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()

    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width or Pt(1)
    else:
        shape.line.fill.background()

    return shape


def set_shape_text(shape, text, font_size=Pt(10), bold=False, color=SF_DARK_TEXT, alignment=PP_ALIGN.LEFT):
    """Set text on a shape's text frame (replaces existing content)."""
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return tf


def add_shape_para(tf, text, font_size=Pt(10), bold=False, color=SF_DARK_TEXT, alignment=PP_ALIGN.LEFT, space_before=None):
    """Add a new paragraph to an existing text frame."""
    p = tf.add_paragraph()
    p.alignment = alignment
    if space_before:
        p.space_before = space_before
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return p


def add_text(slide, left, top, width, height, text, font_size=Pt(10), bold=False, color=SF_DARK_TEXT, alignment=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    """Add a text box to a slide."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return tf


def add_para(tf, text, font_size=Pt(10), bold=False, color=SF_DARK_TEXT, alignment=PP_ALIGN.LEFT, space_before=None, bullet=False):
    """Add a paragraph to a text frame with optional bullet."""
    p = tf.add_paragraph()
    p.alignment = alignment
    if space_before:
        p.space_before = space_before
    if bullet:
        p.level = 0
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return p


def add_content_slide_frame(slide, title_text, subtitle_text=None):
    """Add standard content slide framing: white bg, edge bar, title, subtitle, footer."""
    set_solid_bg(slide, SF_WHITE)

    # Left edge bar
    add_rect(slide, EDGE_BAR_LEFT, EDGE_BAR_TOP, EDGE_BAR_WIDTH, EDGE_BAR_HEIGHT, fill_color=SF_BLUE)

    # Title
    add_text(slide, PAD_LEFT, TITLE_TOP, CONTENT_W, Inches(0.35),
             title_text, font_size=Pt(18), bold=True, color=SF_DARK_TEXT)

    # Subtitle
    if subtitle_text:
        add_text(slide, PAD_LEFT, SUBTITLE_TOP, CONTENT_W, Inches(0.3),
                 subtitle_text, font_size=Pt(12), color=SF_BODY_GREY)

    # Footer copyright
    add_text(slide, PAD_LEFT, FOOTER_TOP, CONTENT_W, Inches(0.2),
             COPYRIGHT_TEXT, font_size=Pt(6), color=SF_COPYRIGHT)

    return slide


def add_dark_slide_frame(slide, title_text, subtitle_text=None):
    """Add dark-themed slide framing (for cover/chapter slides)."""
    set_solid_bg(slide, SF_DARK_BG)

    # Title
    add_text(slide, PAD_LEFT, Inches(2.0), CONTENT_W, Inches(0.7),
             title_text.upper(), font_size=Pt(44), bold=True, color=SF_WHITE,
             alignment=PP_ALIGN.LEFT)

    # Subtitle
    if subtitle_text:
        add_text(slide, PAD_LEFT, Inches(2.7), CONTENT_W, Inches(0.4),
                 subtitle_text, font_size=Pt(14), color=SF_TEAL)

    # Footer copyright
    add_text(slide, PAD_LEFT, FOOTER_TOP, CONTENT_W, Inches(0.2),
             COPYRIGHT_TEXT, font_size=Pt(6), color=SF_COPYRIGHT)

    return slide


def add_skip_badge(slide):
    """Add a red 'SKIP FOR PRESENTATION' badge in the top-right corner."""
    badge = add_rect(slide, Inches(7.0), Inches(0.1), Inches(2.8), Inches(0.3),
                     fill_color=SF_RED)
    set_shape_text(badge, "SKIP FOR PRESENTATION", font_size=Pt(9), bold=True,
                   color=SF_WHITE, alignment=PP_ALIGN.CENTER)
    return badge
```

---

## Fill → Text Contrast Rules

| Fill Color | Text Color | Use Case |
|---|---|---|
| SF_DARK_BG (`#0C3351`) | SF_WHITE | Cover slides, chapter dividers |
| SF_WHITE (`#FFFFFF`) | SF_DARK_TEXT | Standard content slides |
| SF_LIGHT_BG (`#F5F5F5`) | SF_DARK_TEXT | Card backgrounds |
| SF_BLUE (`#29B5E8`) | SF_WHITE | Accent headers, badges |
| SF_MID_BLUE (`#11567F`) | SF_WHITE | Table headers |
| SF_GREEN (`#2ECC71`) | SF_WHITE | Status badges (good) |
| SF_AMBER (`#F5A623`) | SF_DARK_TEXT | Status badges (warning) |
| SF_RED (`#E74C3C`) | SF_WHITE | Status badges (critical), skip badge |
| SF_LIGHT_BLUE (`#E8F4FD`) | SF_DARK_TEXT | Info highlight rows |
| SF_LIGHT_GREEN (`#E8F8EF`) | SF_DARK_TEXT | Success highlight rows |
| SF_LIGHT_ROW (`#F8FAFB`) | SF_DARK_TEXT | Alternating table rows |
| SF_VIOLET (`#7254A3`) | SF_WHITE | Accent elements |
| SF_TEAL (`#75CDD7`) | SF_DARK_TEXT | Subtitle text on dark bg |

---

## Slide Type Patterns

### Cover Slide

```python
def make_cover_slide(prs, title, subtitle, date_str=None):
    slide = add_blank_slide(prs)
    add_dark_slide_frame(slide, title, subtitle)
    if date_str:
        add_text(slide, PAD_LEFT, Inches(3.2), CONTENT_W, Inches(0.3),
                 date_str, font_size=Pt(10), color=SF_BODY_GREY)
    return slide
```

### Agenda Slide

```python
def make_agenda_slide(prs, items):
    """items: list of strings"""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, "Agenda")
    y = CONTENT_TOP
    for i, item in enumerate(items, 1):
        # Number circle
        circle = add_rect(slide, PAD_LEFT, y, Inches(0.3), Inches(0.3), fill_color=SF_BLUE)
        set_shape_text(circle, str(i), font_size=Pt(10), bold=True,
                       color=SF_WHITE, alignment=PP_ALIGN.CENTER)
        # Item text
        add_text(slide, Inches(0.85), y, Inches(8.0), Inches(0.3),
                 item, font_size=Pt(12), color=SF_DARK_TEXT)
        y += Inches(0.45)
    return slide
```

### Two-Column Slide

```python
def make_two_col_slide(prs, title, left_title, left_items, right_title, right_items):
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)
    col_w = Inches(4.3)
    col_gap = Inches(0.5)
    left_x = PAD_LEFT
    right_x = Inches(5.0)
    y = CONTENT_TOP

    # Left column
    add_text(slide, left_x, y, col_w, Inches(0.25),
             left_title, font_size=Pt(11), bold=True, color=SF_MID_BLUE)
    tf_l = add_text(slide, left_x, y + Inches(0.3), col_w, Inches(3.5),
                    left_items[0], font_size=Pt(10), color=SF_BODY_GREY)
    for item in left_items[1:]:
        add_para(tf_l, item, font_size=Pt(10), color=SF_BODY_GREY, space_before=Pt(4))

    # Right column
    add_text(slide, right_x, y, col_w, Inches(0.25),
             right_title, font_size=Pt(11), bold=True, color=SF_MID_BLUE)
    tf_r = add_text(slide, right_x, y + Inches(0.3), col_w, Inches(3.5),
                    right_items[0], font_size=Pt(10), color=SF_BODY_GREY)
    for item in right_items[1:]:
        add_para(tf_r, item, font_size=Pt(10), color=SF_BODY_GREY, space_before=Pt(4))

    return slide
```

### Card Grid Slide

```python
def make_card_grid_slide(prs, title, cards, cols=3):
    """cards: list of dicts with 'title', 'value', 'subtitle' keys"""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)

    card_w = Inches(2.8) if cols == 3 else Inches(4.2)
    card_h = Inches(1.2)
    gap = Inches(0.2)
    start_x = PAD_LEFT
    y = CONTENT_TOP

    for i, card in enumerate(cards):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap)
        cy = y + row * (card_h + gap)

        rect = add_rect(slide, x, cy, card_w, card_h,
                        fill_color=SF_LIGHT_BG, border_color=SF_BORDER, border_width=Pt(0.5))
        tf = set_shape_text(rect, card.get('value', ''), font_size=Pt(22),
                            bold=True, color=SF_MID_BLUE, alignment=PP_ALIGN.CENTER)
        add_shape_para(tf, card.get('title', ''), font_size=Pt(9),
                       bold=True, color=SF_DARK_TEXT, alignment=PP_ALIGN.CENTER)
        if card.get('subtitle'):
            add_shape_para(tf, card['subtitle'], font_size=Pt(8),
                           color=SF_BODY_GREY, alignment=PP_ALIGN.CENTER)

    return slide
```

### KPI + Table Slide

```python
def make_kpi_table_slide(prs, title, kpis, table_headers, table_rows):
    """kpis: list of dicts with 'label', 'value'; table_headers/rows: lists"""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)

    # KPI row at top
    kpi_w = Inches(2.0)
    for i, kpi in enumerate(kpis):
        x = PAD_LEFT + i * (kpi_w + Inches(0.2))
        rect = add_rect(slide, x, CONTENT_TOP, kpi_w, Inches(0.7),
                        fill_color=SF_LIGHT_BLUE)
        tf = set_shape_text(rect, kpi['value'], font_size=Pt(16),
                            bold=True, color=SF_MID_BLUE, alignment=PP_ALIGN.CENTER)
        add_shape_para(tf, kpi['label'], font_size=Pt(8),
                       color=SF_BODY_GREY, alignment=PP_ALIGN.CENTER)

    # Table below KPIs
    table_top = CONTENT_TOP + Inches(0.9)
    n_cols = len(table_headers)
    n_rows = len(table_rows) + 1
    col_w = CONTENT_W / n_cols
    tbl = slide.shapes.add_table(n_rows, n_cols,
                                  PAD_LEFT, table_top, CONTENT_W, Inches(0.3 * n_rows)).table

    # Header row
    for ci, h in enumerate(table_headers):
        cell = tbl.cell(0, ci)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = SF_MID_BLUE
        for para in cell.text_frame.paragraphs:
            for run in para.runs:
                run.font.size = Pt(9)
                run.font.bold = True
                run.font.color.rgb = SF_WHITE
                run.font.name = "Arial"

    # Data rows
    for ri, row in enumerate(table_rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.text = str(val)
            if ri % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = SF_LIGHT_ROW
            for para in cell.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = SF_DARK_TEXT
                    run.font.name = "Arial"

    return slide
```

### Timeline (Gantt) Slide

```python
def make_timeline_slide(prs, title, phases):
    """phases: list of dicts with 'name', 'start_col', 'span', 'color'
       Renders a simplified Gantt on a 12-column grid (months or weeks)."""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)

    grid_left = PAD_LEFT
    grid_top = CONTENT_TOP + Inches(0.3)
    grid_w = CONTENT_W
    col_w = grid_w / 12
    bar_h = Inches(0.35)
    gap = Inches(0.1)

    for i, phase in enumerate(phases):
        y = grid_top + i * (bar_h + gap)
        x = grid_left + phase['start_col'] * col_w
        w = phase['span'] * col_w
        color = phase.get('color', SF_BLUE)

        bar = add_rect(slide, x, y, w, bar_h, fill_color=color)
        set_shape_text(bar, phase['name'], font_size=Pt(9), bold=True,
                       color=SF_WHITE, alignment=PP_ALIGN.CENTER)

    return slide
```

### Table Slide

```python
def make_table_slide(prs, title, headers, rows, col_widths=None):
    """Full-width table slide with branded header row."""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)

    n_cols = len(headers)
    n_rows = len(rows) + 1
    row_h = min(Inches(0.3), (SAFE_BOTTOM - CONTENT_TOP) / n_rows)
    tbl_h = row_h * n_rows

    tbl_shape = slide.shapes.add_table(n_rows, n_cols,
                                        PAD_LEFT, CONTENT_TOP, CONTENT_W, tbl_h)
    tbl = tbl_shape.table

    if col_widths:
        for ci, w in enumerate(col_widths):
            tbl.columns[ci].width = w

    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = SF_MID_BLUE
        for para in cell.text_frame.paragraphs:
            for run in para.runs:
                run.font.size = Pt(9)
                run.font.bold = True
                run.font.color.rgb = SF_WHITE
                run.font.name = "Arial"

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.text = str(val) if val else ""
            if ri % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = SF_LIGHT_ROW
            for para in cell.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = SF_DARK_TEXT
                    run.font.name = "Arial"

    return slide
```

### Team Cards Slide

```python
def make_team_cards_slide(prs, title, members):
    """members: list of dicts with 'name', 'role', 'detail'"""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)

    cols = min(4, len(members))
    card_w = Inches(2.1)
    card_h = Inches(1.5)
    gap = Inches(0.15)
    start_x = PAD_LEFT

    for i, m in enumerate(members):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap)
        y = CONTENT_TOP + row * (card_h + gap)

        rect = add_rect(slide, x, y, card_w, card_h,
                        fill_color=SF_LIGHT_BG, border_color=SF_BORDER, border_width=Pt(0.5))
        tf = set_shape_text(rect, m['name'], font_size=Pt(10),
                            bold=True, color=SF_DARK_TEXT, alignment=PP_ALIGN.CENTER)
        add_shape_para(tf, m['role'], font_size=Pt(9),
                       color=SF_MID_BLUE, alignment=PP_ALIGN.CENTER)
        if m.get('detail'):
            add_shape_para(tf, m['detail'], font_size=Pt(8),
                           color=SF_BODY_GREY, alignment=PP_ALIGN.CENTER)

    return slide
```

### RACI Matrix Slide

```python
def make_raci_slide(prs, title, activities, roles, matrix):
    """matrix: 2D list of 'R','A','C','I' or '' values"""
    slide = add_blank_slide(prs)
    add_content_slide_frame(slide, title)

    headers = ["Activity"] + roles
    rows = []
    for i, act in enumerate(activities):
        rows.append([act] + matrix[i])

    col_widths = [Inches(3.0)] + [Inches((9.125 - 3.0) / len(roles))] * len(roles)
    make_table_slide.__wrapped__ if hasattr(make_table_slide, '__wrapped__') else None

    n_cols = len(headers)
    n_rows = len(rows) + 1
    row_h = min(Inches(0.3), (SAFE_BOTTOM - CONTENT_TOP) / n_rows)
    tbl_h = row_h * n_rows

    tbl_shape = slide.shapes.add_table(n_rows, n_cols,
                                        PAD_LEFT, CONTENT_TOP, CONTENT_W, tbl_h)
    tbl = tbl_shape.table

    for ci, w in enumerate(col_widths):
        tbl.columns[ci].width = w

    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = SF_MID_BLUE
        for para in cell.text_frame.paragraphs:
            for run in para.runs:
                run.font.size = Pt(9)
                run.font.bold = True
                run.font.color.rgb = SF_WHITE
                run.font.name = "Arial"

    raci_colors = {'R': SF_BLUE, 'A': SF_GREEN, 'C': SF_AMBER, 'I': SF_LIGHT_BG}

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.text = str(val)
            if ci > 0 and val in raci_colors:
                cell.fill.solid()
                cell.fill.fore_color.rgb = raci_colors[val]
            elif ri % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = SF_LIGHT_ROW
            for para in cell.text_frame.paragraphs:
                para.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.bold = ci > 0
                    run.font.color.rgb = SF_WHITE if val in ('R', 'A') else SF_DARK_TEXT
                    run.font.name = "Arial"

    return slide
```

### Thank You Slide

```python
def make_thank_you_slide(prs, contact_name=None, contact_email=None):
    slide = add_blank_slide(prs)
    add_dark_slide_frame(slide, "Thank You")
    if contact_name:
        add_text(slide, PAD_LEFT, Inches(3.0), CONTENT_W, Inches(0.3),
                 contact_name, font_size=Pt(12), color=SF_WHITE)
    if contact_email:
        add_text(slide, PAD_LEFT, Inches(3.35), CONTENT_W, Inches(0.3),
                 contact_email, font_size=Pt(10), color=SF_TEAL)
    return slide
```

---

## Typography Rules

| Element | Size | Weight | Case |
|---|---|---|---|
| Cover / Chapter title | 44px (Pt 33) | Bold | ALL CAPS |
| Content slide title | 18px (Pt 13.5) | Bold | Title Case |
| Subtitle | 12px (Pt 9) | Regular | Sentence case |
| Body text | 10px (Pt 7.5) | Regular | Sentence case |
| Small text | 9px (Pt 6.75) | Regular | Sentence case |
| Caption / Footer | 6-7px (Pt 4.5-5.25) | Regular | Sentence case |

Font: **Arial** everywhere. Never use Montserrat, Roboto, or Lato.

Note: CSS `px` at 96dpi maps to approximately `Pt × 0.75` in python-pptx. The Pt values in the utility functions above use the direct point equivalents for the slide's 10" width.

---

## Design Rules Summary

1. Every slide is 960×540px (10×5.625") with `overflow: hidden` — no content bleeds off-canvas.
2. Left edge bar: 4px wide SF_BLUE bar on every content slide (not cover/chapter slides).
3. Footer: "© 2026 Snowflake Inc. All Rights Reserved" positioned at `footer-top` (511px / 5.323") on every slide.
4. Content must NOT extend below `safe-bottom` (490px / 5.104") to avoid footer collision.
5. At least 50% of content slides must use a visual pattern (cards, tables, timelines, KPIs) — not just bullet lists.
6. SKIP slides receive a red "SKIP FOR PRESENTATION" badge in the top-right corner via `add_skip_badge()`.
7. Dark slides (cover, chapter, thank-you) use SF_DARK_BG background with white/teal text.
8. Content slides use white background with the standard frame (edge bar + title + footer).
9. Tables always use SF_MID_BLUE header row with white text, alternating SF_LIGHT_ROW for data rows.
10. Status indicators: Green = on track/good, Amber = at risk/warning, Red = critical/blocked.
