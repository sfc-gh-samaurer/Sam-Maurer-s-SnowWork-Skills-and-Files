---
name: pptx-slide-patterns
description: Basic slide patterns (cover, chapter, content columns, agenda, split, quote, thank you), table patterns, and diagram patterns.
---

## 10. Slide Patterns

### 10.1 Cover Slide (Layout 13 — Primary Cover)

```python
slide = prs.slides.add_slide(prs.slide_layouts[13])

# ⚠ TITLE MUST be ≤ 50 characters (Rule 26). Count BEFORE calling set_ph.
title = "FROM DATA SILOS TO\nPATIENT INTELLIGENCE"       # 39 chars ✓
assert len(title.replace('\n', ' ')) <= 50, f"Title too long: {len(title.replace(chr(10), ' '))} chars"

set_ph(slide, 3, title)                                   # 44pt big title
set_ph(slide, 0, "Meridian Health Systems")               # 18pt subtitle
set_ph(slide, 2, "Sarah Chen  |  February 2026")          # 14pt author line
```

- **Background is accent1 (SF_BLUE)** with baked-in Snowflake logo and wave graphics
- PH3 title: ALL CAPS, **≤ 50 characters**, max 3 lines, use `\n` for breaks
- PH0 subtitle: Title Case, 1 line — client name or topic framing
- PH2 author: format as `First Last  |  Title  |  Date`
- Layouts 14 (bottom wave), 15 (right graphic), 16 (clean), 17 (customer logo area) use **same PH indices**

**Cover title examples — Good vs. Bad:**

| Bad (too long, generic) | Good (punchy, ≤50 chars) |
|------------------------|-------------------------|
| "TRANSFORMING PATIENT OUTCOMES WITH SNOWFLAKE'S AI DATA PLATFORM" (63 chars) | "FROM DATA SILOS TO\nPATIENT INTELLIGENCE" (39 chars) |
| "ACCELERATING DIGITAL TRANSFORMATION THROUGH DATA AND AI" (55 chars) | "THE AI ENGINE INSIDE\nYOUR DATA" (30 chars) |
| "SNOWFLAKE DATA CLOUD PLATFORM OVERVIEW AND CAPABILITIES" (55 chars) | "YOUR DATA,\nUNLEASHED" (20 chars) |

### 10.2 Chapter Divider (Layout 18 — Recommended)

```python
slide = prs.slides.add_slide(prs.slide_layouts[18])
set_ph(slide, 1, "CHAPTER\nTITLE")
```

- Background: DK2 dark navy. Text automatically renders bold WHITE at 40pt.
- ALL CAPS, max 2-3 lines
- Variants: 20 (bottom wave), 21 (center wave), 22 (right graphic)

### 10.3 Content — One Column (Layout 5)

**Flat list (all items same importance):**

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
set_ph(slide, 0, "SLIDE TITLE")
set_ph(slide, 2, "Subtitle if needed")
set_ph_lines(slide, 1, [
    "First paragraph (no bullet at L0)",
    "Second paragraph",
    "Third paragraph",
], font_size=11)
```

**Sections with headings + body (PREFERRED for structured content):**

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
set_ph(slide, 0, "WHEN TO USE CROSS-REGION INFERENCE")
set_ph(slide, 2, "Common scenarios and use cases")
set_ph_sections(slide, 1, [
    ("Ultra-Low Latency Requirements", [
        "Cross-region adds network latency between regions",
        "Always test your use case before production deployment",
    ]),
    ("U.S. SnowGov Regions", [
        "NOT supported — cannot route into or out of SnowGov",
    ]),
    ("Strict Data Residency", [
        "Cross-region may route data to a different region",
        "Verify compliance requirements before enabling",
    ]),
], heading_size=12, body_size=10)
```

**Bold keyword items (e.g. considerations, warnings):**

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
set_ph(slide, 0, "IMPORTANT CONSIDERATIONS")
set_ph(slide, 2, "Key items to keep in mind")
set_ph_bold_keywords(slide, 1, [
    ("Latency", "Cross-region adds network latency. Test before production."),
    ("Account-Wide", "The parameter affects ALL users and ALL Cortex AI calls."),
    ("SnowGov", "NOT supported in U.S. SnowGov regions."),
    ("Automatic Routing", "Snowflake decides which region processes the request."),
], kw_size=11, body_size=11)
```

- Body: L=0.40" T=1.50" W=6.85" H=3.62", lnSpc=115%
- Level 0 has NO bullet; level 1+ has bullets

### 10.4 Content — Two Columns (Layout 6)

**Flat list:**

```python
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_ph(slide, 0, "SLIDE TITLE")
set_ph(slide, 3, "Subtitle if needed")
set_ph_lines(slide, 1, ["Left col item 1", "Left col item 2"], font_size=11)
set_ph_lines(slide, 2, ["Right col item 1", "Right col item 2"], font_size=11)
```

**Sections with headings + body (PREFERRED):**

```python
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_ph(slide, 0, "CORTEX AI CAPABILITIES")
set_ph(slide, 3, "Functions vs Search comparison")
set_ph_sections(slide, 1, [
    ("Cortex AI Functions", [
        "LLM inference (COMPLETE, SUMMARIZE)",
        "Text analysis (SENTIMENT, TRANSLATE)",
        "Fine-tuning support for custom models",
    ]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 2, [
    ("Cortex Search", [
        "Hybrid semantic + keyword search",
        "Real-time index refresh",
        "RAG-optimized retrieval",
    ]),
], heading_size=11, body_size=10)
```

- Each column: W=4.55", T=1.50" H=3.62"
- Left at 0.40", right at 5.05"
- ALL levels have bullet `\u2022`

### 10.5 Content — Three Columns (Layout 7)

**Key takeaway / summary pattern (heading + bullets per column):**

```python
slide = prs.slides.add_slide(prs.slide_layouts[7])
set_ph(slide, 0, "KEY TAKEAWAYS")
set_ph(slide, 4, "Summary of what to remember")
set_ph_sections(slide, 1, [
    ("Simple Setup", [
        "Single ALTER ACCOUNT command",
        "Enabled by ACCOUNTADMIN",
        "Default is DISABLED",
    ]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 2, [
    ("Full Model Access", [
        "Access latest LLMs regardless of region",
        "No code changes needed",
    ]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 3, [
    ("Secure & Cost-Efficient", [
        "No data stored/cached in transit",
        "No egress charges; same credit rates",
    ]),
], heading_size=11, body_size=10)
```

**Simple flat list per column:**

```python
slide = prs.slides.add_slide(prs.slide_layouts[7])
set_ph(slide, 0, "SLIDE TITLE")
set_ph(slide, 4, "Subtitle if needed")
set_ph_lines(slide, 1, ["Col 1 content"], font_size=11)
set_ph_lines(slide, 2, ["Col 2 content"], font_size=11)
set_ph_lines(slide, 3, ["Col 3 content"], font_size=11)
```

- Each column: W=2.95", at L=0.40", 3.47", 6.70"
- Default 14pt (L1-L2), 12pt (L3-L4)
- All levels have bullet
- **NOTE**: Columns are narrow (2.95") — keep text concise (max ~25 chars/line at 10pt)

### 10.6 Content — Four Columns (Layout 8)

```python
slide = prs.slides.add_slide(prs.slide_layouts[8])
set_ph(slide, 0, "SLIDE TITLE")
set_ph(slide, 5, "Subtitle if needed")
for col_idx in [1, 2, 3, 4]:
    set_ph_lines(slide, col_idx, [f"Column {col_idx} content"], font_size=11)
```

- Each column: W=2.10", at L=0.40", 2.69", 5.11", 7.53"
- 14pt all levels, all levels have bullet
- **NOTE**: Columns are very narrow (2.10") — max ~18 chars/line at 10pt, max 3-4 lines

### 10.7 Multi-use / Free Canvas (Layout 0)

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "SLIDE TITLE")
set_ph(slide, 1, "Subtitle")
# Add custom shapes in safe zone: below 1.14", above 5.10"
```

- Title lnSpc=85% (tight). Subtitle at T=0.72" in BODY_GREY.
- Free canvas below placeholders for tables, diagrams, custom shapes.
- Use layout 1 for long (2-line) titles (subtitle drops to 1.23").

### 10.8 Agenda Slide — Side Panel (Layout 9)

```python
slide = prs.slides.add_slide(prs.slide_layouts[9])
set_ph(slide, 1, "Agenda")                       # 26pt bold DK1 on white left panel
set_ph_lines(slide, 2, [                          # white text on DK2 right panel
    "Topic One",
    "Topic Two",
    "Topic Three",
])
```

- Left panel (0.00"-2.51"): white background, DK1 text
- **Right panel (2.51"-10.00"): DK2 fill**, white text automatically
- Decorative: SF_BLUE circles, corner image — do not overlap

### 10.9 Agenda Slide — Sidebar (Layout 10)

```python
slide = prs.slides.add_slide(prs.slide_layouts[10])
set_ph(slide, 1, "Section Title")                 # 26pt bold WHITE on DK2 panel
set_ph_lines(slide, 2, [                          # 12pt WHITE on DK2 panel
    "Item 1",
    "Item 2",
])
```

- **Left panel (0.00"-3.00"): DK2 fill**, both PH1 and PH2 have WHITE text
- Right area (3.00"-10.00"): white, for custom content (charts, data)

### 10.10 Split Layout (Layout 11)

```python
slide = prs.slides.add_slide(prs.slide_layouts[11])
set_ph(slide, 0, "SPLIT SLIDE TITLE")             # left side, DK1
set_ph(slide, 1, "Subtitle description text")     # 16pt BODY_GREY
set_ph_lines(slide, 2, [                           # 18pt WHITE on DK2 right panel
    "Right side bullet 1",
    "Right side bullet 2",
], font_size=14)
```

- Left (0.00"-5.00"): white background, title + subtitle
- **Right (5.00"-10.00"): DK2 fill** with SF_BLUE accent overlays
- PH2 right body: WHITE text, 18pt, bullets, lnSpc=115%

### 10.11 Quote + Attribution (Layout 23)

```python
slide = prs.slides.add_slide(prs.slide_layouts[23])
set_ph(slide, 1, "Quote text, keep it concise and impactful.")
set_ph(slide, 2, "Name  |  Title\nCompany Name")
```

- Background: DK2. Quote: 42pt bold white. Attribution: 16pt bold white.
- Decorative open-quote icon at (0.50",0.52")
- Use layout 24 for **white background** version (text renders DK1/BODY_GREY)

### 10.12 Quote — White Background (Layout 24)

```python
slide = prs.slides.add_slide(prs.slide_layouts[24])
set_ph(slide, 1, "Quote on white background.")
set_ph(slide, 2, "Name  |  Title\nCompany Name")
```

- Background: **white (lt1)**. Quote text: DK1. Attribution: BODY_GREY.

### 10.13 Blank Canvas (Layout 12)

```python
slide = prs.slides.add_slide(prs.slide_layouts[12])
# Full-bleed — only slide number, accent dot, copyright present
# Use for full-width images:
slide.shapes.add_picture("image.png", Inches(0), Inches(0), prs.slide_width, prs.slide_height)
```

### 10.14 Custom Layout (Layout 26)

```python
slide = prs.slides.add_slide(prs.slide_layouts[26])
set_ph(slide, 0, "SLIDE TITLE")     # white title bar at top
# Canvas below title is DK2 dark navy — use WHITE text for any shapes here
box = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0.50), Inches(1.50), Inches(4.00), Inches(1.00))
box.fill.background()
box.line.fill.background()
tf = box.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Content on dark background"
p.font.size = Pt(14); p.font.color.rgb = WHITE; p.font.name = "Arial"
```

### 10.15 Thank You (Layout 27 clean, Layout 28 with wave)

```python
slide = prs.slides.add_slide(prs.slide_layouts[28])   # wave variant
set_ph(slide, 1, "THANK\nYOU")
```

- Background: accent1 (SF_BLUE). Text: 52pt bold WHITE, lnSpc=75%
- Keep to 1-3 lines

---

## 11. Table Patterns

### ⚠ CRITICAL: ALWAYS Use Native `add_table()` — NEVER Build Tables from Individual Rectangles

**NEVER create comparison grids, data tables, or matrix layouts by placing individual rectangle shapes in a grid pattern.** This produces 20-30+ separate shapes that are:
- Impossible to edit in PowerPoint
- Fragile (alignment shifts on resize)
- Unprofessional looking (inconsistent cell sizes)

✅ **ALWAYS use `slide.shapes.add_table(n_rows, n_cols, ...)`** for any content that has rows and columns — comparisons, feature matrices, competitive analysis, data grids.

```python
# ✅ CORRECT — native table
tbl_shape = slide.shapes.add_table(
    n_rows, n_cols,
    Inches(0.40), Inches(1.30), Inches(9.10), Inches(0.40 * n_rows))
tbl = tbl_shape.table

# ❌ WRONG — rectangle grid (NEVER do this)
# for row in data:
#     for col in row:
#         slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, ...)  # NO!
```

**When to use which:**
| Content Type | Use This | NOT This |
|-------------|----------|----------|
| Comparison matrix (Snowflake vs X vs Y) | `add_table()` | Individual rectangles |
| Feature checklist grid | `add_table()` | Individual rectangles |
| Data with headers + rows | `add_table()` | Individual rectangles |
| Key-value pairs (3+ pairs) | `add_table()` | Individual rectangles |
| Settings grid (value + description pairs) | `add_table()` | Individual rectangles |
| Metric name list (stacked labels) | `add_table()` or `set_ph_lines()` | Individual rectangles |
| Process flow (sequential steps) | `add_shape_text()` shapes | `add_table()` |
| Hub & spoke / diagram | `add_shape_text()` shapes | `add_table()` |

⚠ **COMMON VIOLATION**: Building a "settings grid" where each row has a value + description as two adjacent rectangles (e.g. "60 seconds" | "ETL/Batch warehouses"). This MUST be a native table instead — fewer shapes, editable, and consistent sizing.

### Table Sizing Rules (CRITICAL)

**Width rules:**

| Columns | Max Table Width | Column Width Formula |
|---------|----------------|---------------------|
| 2-3 cols | 9.10" (L=0.40" to R=9.50") | `col_w = 9.10 / n_cols` |
| 4-5 cols | 9.10" | `col_w = 9.10 / n_cols` (min 1.50" per col) |
| 6+ cols | 9.10" | Reduce font to 8pt, `col_w = 9.10 / n_cols` (min 1.20") |

⚠ **Table left MUST be ≥ 0.40" and right edge MUST be ≤ 9.50"** (total width ≤ 9.10"). A table starting at left=0.40" with width=9.10" ends at 9.50" — exactly at the safe zone. Never create a table wider than 9.10".

```python
# MANDATORY table width calculation:
table_left = Inches(0.40)
table_width = Inches(9.10)  # ← NEVER exceed this
# If you need more columns, reduce column width, not increase table width
```

**Height rules:**

| Available Height | Row Height | Max Data Rows (+ header) | Total Rows |
|-----------------|-----------|-------------------------|------------|
| 3.80" (standard T=1.30" to B=5.10") | 0.35" | 9 data rows | 10 |
| 3.80" (standard) | 0.40" | 8 data rows | 9 |
| 3.80" (standard) | 0.45" | 7 data rows | 8 |

**Formula**: `max_rows = floor((5.10 - table_top) / row_height)`

If content exceeds max rows, **split across slides**:
```python
# Paginate: max 8 data rows per slide
PAGE_SIZE = 8
for page_idx in range(0, len(all_data), PAGE_SIZE):
    page_data = all_data[page_idx : page_idx + PAGE_SIZE]
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    suffix = f" (Page {page_idx // PAGE_SIZE + 1})" if len(all_data) > PAGE_SIZE else ""
    set_ph(slide, 0, f"TABLE TITLE{suffix}")
    # ... create table with page_data only ...
```

**Verify after placing**: `table_top + (n_rows × row_height) ≤ 5.10"`
If the table bottom exceeds 5.10", reduce row count or font size.

### 11.1 Table Style 1 — Header Row + Side Labels

From template Slide 56. Top row: white bg, grey bold headers. Left column: DK2 fill, white bold labels.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "TABLE TITLE")
set_ph(slide, 1, "Subtitle")

headers = ["", "Col A", "Col B", "Col C", "Col D"]
data = [
    ["Row 1", "val", "val", "val", "val"],
    ["Row 2", "val", "val", "val", "val"],
]
n_rows = len(data) + 1
tbl_shape = slide.shapes.add_table(
    n_rows, len(headers),
    Inches(0.50), Inches(1.30), Inches(9.00), Inches(0.40 * n_rows))
tbl = tbl_shape.table

# Header row (white bg, BODY_GREY bold text)
for ci, h in enumerate(headers):
    cell = tbl.cell(0, ci)
    cell.text = h
    cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(12); p.font.bold = True
        p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER

# Data rows
for ri, row in enumerate(data):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri + 1, ci)
        cell.text = str(val)
        if ci == 0:  # Side label
            cell.fill.solid(); cell.fill.fore_color.rgb = DK2
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12); p.font.bold = True
                p.font.color.rgb = WHITE; p.font.name = "Arial"
        else:
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10); p.font.color.rgb = TBL_GREY
                p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER
```

### 11.2 Table Style 2 — Full Header + Emphasis Row

From template Slide 57. DK2 header row + SF_BLUE emphasis row + alternating data.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "TABLE TITLE")
set_ph(slide, 1, "Subtitle")

headers = ["Col 1", "Col 2", "Col 3", "Col 4"]
emphasis = ["Highlight A", "Highlight B", "Highlight C", "Highlight D"]
data = [["val"] * 4] * 4

n_rows = len(data) + 2
tbl_shape = slide.shapes.add_table(
    n_rows, len(headers),
    Inches(0.50), Inches(1.37), Inches(9.00), Inches(0.35 * n_rows))
tbl = tbl_shape.table

# Header (DK2, white bold 14pt)
for ci, h in enumerate(headers):
    cell = tbl.cell(0, ci); cell.text = h
    cell.fill.solid(); cell.fill.fore_color.rgb = DK2
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(14); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER

# Emphasis (SF_BLUE, white 11pt)
for ci, val in enumerate(emphasis):
    cell = tbl.cell(1, ci); cell.text = val
    cell.fill.solid(); cell.fill.fore_color.rgb = SF_BLUE
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(11); p.font.color.rgb = WHITE
        p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER

# Data (alternating white / LIGHT_BG, TBL_GREY 10pt)
for ri, row in enumerate(data):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri + 2, ci); cell.text = str(val)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if ri % 2 == 0 else LIGHT_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10); p.font.color.rgb = TBL_GREY
            p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER
```

### 11.3 Table Borders

Apply 1pt (#C8C8C8) borders to all cells:

```python
from pptx.oxml.ns import qn
from lxml import etree

def set_table_borders(tbl, n_rows, n_cols):
    for ri in range(n_rows):
        for ci in range(n_cols):
            tc = tbl.cell(ri, ci)._tc
            tcPr = tc.find(qn("a:tcPr"))
            if tcPr is None:
                tcPr = etree.SubElement(tc, qn("a:tcPr"))
            for edge in ["lnL", "lnR", "lnT", "lnB"]:
                ln = etree.SubElement(tcPr, qn(f"a:{edge}"), w="12700")
                sf = etree.SubElement(ln, qn("a:solidFill"))
                etree.SubElement(sf, qn("a:srgbClr"), val="C8C8C8")

# Call after populating table:
# set_table_borders(tbl, n_rows, n_cols)
```

---

## 12. Custom Shape Text Rules

When placing content in custom shapes (boxes, callouts, flow steps), follow these
rules to prevent text overflow, clipping, and overlap.

### 12.1 Text Density Limits

**Rectangular shapes:**

| Box Width | Max Characters per Line | Max Total Lines | Max Font Size |
|-----------|------------------------|-----------------|---------------|
| < 2.0"    | ~18 chars              | 3-4 lines       | 10pt          |
| 2.0-3.0"  | ~28 chars              | 4-5 lines       | 11pt          |
| 3.0-4.5"  | ~42 chars              | 5-6 lines       | 12pt          |
| 4.5-9.0"  | ~65 chars              | 6-8 lines       | 14pt          |

**Formula**: `max_chars_per_line ≈ box_width_inches × 9` (at 10pt Arial).
Scale down 15% for bold text.

**Circles / Ovals (CRITICAL — usable area ≈ 70% of diameter):**

⚠ **MINIMUM circle diameter is 0.55".** NEVER create circles smaller than 0.55" — text won't fit legibly.

| Circle Diameter | Usable Width | Max Characters | Max Lines | Max Font Size | Example Use |
|----------------|-------------|---------------|-----------|---------------|-------------|
| 0.55-0.60"     | ~0.39"      | 2 chars        | 1 line    | **14pt bold** | Number badge "01" |
| 0.61-0.80"     | ~0.53"      | 2-3 chars      | 1 line    | **14pt**      | Initials "DR" |
| 0.81-1.00"     | ~0.70"      | 6-8 chars      | 1-2 lines | **10pt**      | Short label |
| 1.01-1.50"     | ~0.98"      | 8-12 chars     | 2 lines   | **11pt**      | "CORTEX\nAI" |
| 1.51-2.00"     | ~1.26"      | 12-18 chars    | 2-3 lines | **14pt**      | Hub label |

⚠ **Circles are the #1 overflow problem.** Text inside a circle only has ~70% of the diameter as usable width. A 0.55" circle gives only 0.39" for text — 18pt font WILL overflow. Always use `MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` on circles as a safety net. For numbered step circles (01, 02, etc.), use **0.55" diameter, 14pt bold, centre-aligned**.

**Chevrons (usable width ≈ 60% due to pointed ends):**

| Chevron Width | Usable Width | Max Characters | Max Font Size |
|--------------|-------------|---------------|---------------|
| < 2.5"       | ~1.50"      | ~13 chars      | 11pt          |
| 2.5-3.5"     | ~2.10"      | ~19 chars      | 12pt          |
| > 3.5"       | ~2.70"      | ~24 chars      | 14pt          |

### 12.2 Box Sizing Guidelines

```python
# Calculate minimum box height for given content
def min_box_height(text, box_width, font_size_pt=10):
    """Estimate minimum box height for text to fit without overflow."""
    chars_per_line = int(box_width * 9 * (10 / font_size_pt))
    n_lines = sum(1 + len(line) // chars_per_line for line in text.split('\n'))
    line_height = font_size_pt * 1.3 / 72  # pt to inches with spacing
    return n_lines * line_height + 0.15  # 0.15" padding
```

### 12.3 Shape Title + Body Pattern

For boxes with a bold title and body text, use separate runs:

```python
box = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.50), Inches(2.00), Inches(2.50), Inches(1.20))
box.fill.solid(); box.fill.fore_color.rgb = SF_BLUE
box.line.fill.background()
tf = box.text_frame; tf.word_wrap = True
tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY (Rule 39)
# Title run
p = tf.paragraphs[0]
r1 = p.add_run(); r1.text = "BOX TITLE"
r1.font.size = Pt(10); r1.font.bold = True
r1.font.color.rgb = WHITE; r1.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER
# Body run (new paragraph)
p2 = tf.add_paragraph()
r2 = p2.add_run(); r2.text = "Short description"
r2.font.size = Pt(9); r2.font.color.rgb = WHITE; r2.font.name = "Arial"
p2.alignment = PP_ALIGN.CENTER
```

### 12.4 Shape Gap, Overlap Prevention & Vertical Centering

- **Minimum gap between shapes**: 0.15" horizontal, 0.10" vertical
- **Never let shapes touch or overlap** — always calculate `top + height + gap` for the next shape
- **When stacking shapes vertically**, ensure: `shape_n.top = shape_(n-1).top + shape_(n-1).height + 0.10`
- **When placing shapes next to tables**, ensure the shape's bounding box does NOT intersect the table's bounding box
- **All shapes must end above 5.10"** (safe zone bottom) unless using Layout 12 (blank)
- **Vertically centre text in single-line shapes** (headers, labels, circles, callout boxes):

```python
# For any shape with a single centred label, set vertical anchor to MIDDLE:
tf = shape.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE  # ← centres text vertically
p = tf.paragraphs[0]; p.text = "Label"
p.alignment = PP_ALIGN.CENTER            # ← centres text horizontally
```

Without `MSO_ANCHOR.MIDDLE`, text defaults to top-anchored and floats to the top edge of the shape — especially noticeable on small buttons, circles, and header bars.

### 12.5 Mandatory Auto-Fit for Custom Shapes (CRITICAL)

**Every custom shape that contains text MUST have `MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` set.** This is the safety net that prevents text from overflowing — PowerPoint will shrink the font if the text doesn't fit.

```python
from pptx.enum.text import MSO_AUTO_SIZE

# MANDATORY: Set auto_size on EVERY shape with text
shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, ...)
tf = shape.text_frame
tf.word_wrap = True
tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← SAFETY NET — shrinks text to fit
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.text = "Label"
p.alignment = PP_ALIGN.CENTER
```

This applies to ALL shape types: ovals, circles, rounded rectangles, chevrons, hexagons, diamonds, and plain rectangles. The only exception is textboxes used for descriptions below shapes (created via `add_textbox()`), which can use `MSO_AUTO_SIZE.NONE` because they rely on word wrap and controlled sizing.

**Why this matters**: Without auto_size, a 0.55" circle with 18pt text will render the text AT 18pt regardless of fit — producing visible overflow. With `TEXT_TO_FIT_SHAPE`, PowerPoint reduces the font to whatever fits inside the shape boundary.

⚠ **Still respect Section 12.1 font limits** — auto_size is a safety net, not a license to use huge fonts. Choose an appropriate starting font size, and let auto_size handle edge cases.

### 12.6 Multi-Line Text in Shapes (CRITICAL)

When a shape label needs to span multiple lines, **always use `\n`** inside the string. Never concatenate strings without a separator.

```python
# ✅ CORRECT — explicit newline
p.text = "THE\nCHALLENGE"          # renders as 2 lines: "THE" / "CHALLENGE"

# ✅ CORRECT — single line
p.text = "THE CHALLENGE"            # renders as 1 line: "THE CHALLENGE"

# ❌ WRONG — concatenation without separator
p.text = "THE" + "CHALLENGE"       # renders as "THECHALLENGE" — unreadable!

# ❌ WRONG — f-string without space
p.text = f"{word1}{word2}"          # same problem: merged text
```

**Common multi-line patterns for shapes:**
```python
# Numbered pillar headers
p.text = "DATA-FIRST\nCULTURE"     # ✓ clear 2-line label

# Hub & spoke labels
p.text = "Document\nAI"            # ✓ fits in small circle
p.text = "Universal\nSearch"       # ✓ word per line for narrow shapes

# Chevron steps
p.text = "STEP 1:\nDiscovery"      # ✓ step number + name on separate lines

# Stat callout
p.text = "$18M"                    # ✓ short numbers stay on 1 line
```

⚠ **Every time you split text across lines in a shape, verify there is a `\n` between the parts.** The `verify_slide()` function flags shapes containing 10+ character strings with no spaces — a telltale sign of missing separators.

### 12.7 MANDATORY Helper Function — `add_shape_text()`

> **Canonical definition is in `core-helpers.md`.** Copy the function from there into every script. Do NOT redefine it here or inline.

**Usage examples:**
```python
# Hub centre
add_shape_text(slide, MSO_SHAPE.OVAL, 4.0, 2.4, 1.8, 1.8,
               "SNOWFLAKE\nAI DATA\nCLOUD", SF_BLUE, WHITE, font_size=11, bold=True)

# Spoke label
add_shape_text(slide, MSO_SHAPE.OVAL, 1.2, 1.6, 1.0, 1.0,
               "EHR\nSYSTEMS", DK2, WHITE, font_size=9, bold=True)

# Chevron step
add_shape_text(slide, MSO_SHAPE.CHEVRON, 0.4, 2.0, 2.0, 0.8,
               "CONSOLIDATE", SF_BLUE, WHITE, font_size=12, bold=True)

# Description box below a shape
add_shape_text(slide, MSO_SHAPE.RECTANGLE, 0.5, 3.5, 2.0, 0.8,
               "Unify all data sources\ninto a single platform", LIGHT_BG, DK1, font_size=9)

# Stat callout
add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 1.0, 2.0, 1.6, 1.0,
               "87%", SF_BLUE, WHITE, font_size=28, bold=True)
```

**Rules:**
- NEVER set `p.text`, `run.text`, or `shape.text_frame.text` directly on custom shapes. Always use `add_shape_text()`.
- NEVER create separate runs within one paragraph. One string, one `p.text` assignment.
- For description text below shapes, still use `add_shape_text()` with `LIGHT_BG` or `WHITE` fill and smaller font.
- The function enforces: Arial font, auto_size, vertical centering, tight margins, and no-outline — all in one call.

---

## 12.8 Multi-Category Content Rule (CRITICAL)

### ⚠ NEVER Dump 3+ Categorised Sections into One Placeholder

When content has **3 or more distinct categories** (each with a bold header + supporting bullets), you MUST split them into **separate visual containers** — not flatten everything into a single text placeholder. A wall of text with inline bold headers is lazy, hard to scan, and looks unprofessional.

**How to detect**: If you're about to write content like:
```
Bold Header A
  bullet 1
  bullet 2
Bold Header B
  bullet 3
  bullet 4
Bold Header C
  bullet 5
  bullet 6
```
...into a single placeholder → **STOP**. Use one of these patterns instead.

### Option 1: Three-Column Layout (Layout 7) — Best for 3 equal categories

```python
slide = prs.slides.add_slide(prs.slide_layouts[7])
set_ph(slide, 0, "SECURITY & COMPLIANCE FRAMEWORK")
set_ph(slide, 4, "Enterprise-grade controls for protected health information")
set_ph_sections(slide, 1, [
    ("Data Governance", [
        "Row-level security filters PHI by consumer role",
        "Dynamic masking hides SSN/MRN from unauthorized users",
        "Object tagging tracks PHI lineage across datasets",
    ]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 2, [
    ("Compliance Certifications", [
        "HIPAA BAA — Snowflake signs as Business Associate",
        "HITRUST CSF certified for healthcare workloads",
        "SOC 2 Type II, FedRAMP, StateRAMP authorized",
    ]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 3, [
    ("Audit & Monitoring", [
        "Access history logs every query on shared data",
        "Alert policies on anomalous access patterns",
        "Data Clean Rooms for analysis without PHI exposure",
    ]),
], heading_size=11, body_size=10)
```

### Option 2: Callout Boxes via `add_shape_text()` — Best for visual impact

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "SECURITY & COMPLIANCE FRAMEWORK")
set_ph(slide, 1, "Enterprise-grade controls for protected health information")

categories = [
    ("DATA GOVERNANCE\nRow-level security, dynamic masking,\nobject tagging, time-travel recovery", SF_BLUE),
    ("COMPLIANCE\nHIPAA BAA, HITRUST CSF,\nSOC 2 Type II, FedRAMP, StateRAMP", DK2),
    ("AUDIT & MONITORING\nAccess history, alert policies,\nData Clean Rooms for PHI protection", TEAL),
]
box_w = 2.80; gap = 0.20; x = 0.40
for text, colour in categories:
    fg = WHITE if colour != TEAL else DK1
    add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, 1.40, box_w, 2.80,
                   text, colour, fg, font_size=10)
    x += box_w + gap
```

### Option 3: Two-Column Layout (Layout 6) — Best for 4 categories (2 per column)

```python
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_ph(slide, 0, "SECURITY & COMPLIANCE FRAMEWORK")
set_ph(slide, 3, "Enterprise-grade controls for protected health information")
set_ph_sections(slide, 1, [
    ("Data Governance", ["Row-level security, dynamic masking, object tagging"]),
    ("Compliance", ["HIPAA BAA, HITRUST CSF, SOC 2 Type II"]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 2, [
    ("Audit & Monitoring", ["Access history, alert policies, anomaly detection"]),
    ("Data Clean Rooms", ["Analyze shared data without exposing PHI"]),
], heading_size=11, body_size=10)
```

### Decision Guide

| # of Categories | Best Pattern | Why |
|-----------------|-------------|-----|
| 2 | Two-column layout (Layout 6) | Clean side-by-side comparison |
| 3 | Three-column layout (Layout 7) or 3 callout boxes | Each category gets equal visual weight |
| 4 | Two-column with 2 sections each (Layout 6) | Balanced grid feel |
| 5-6 | Four-column (Layout 8) or icon-circle grid pattern | Dense but scannable |
| 7+ | Split across 2 slides | Too much for one slide |

**Auto size on EVERY placeholder used**: Even when using multi-column layouts, ensure `auto_size = TEXT_TO_FIT_SHAPE` is set if you're writing into body placeholders with `set_ph_sections()`. The helper handles this, but verify if writing custom code.

---

## 13. Diagram Patterns

### 13.1 Horizontal Flow Diagram

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "FLOW TITLE")
set_ph(slide, 1, "Subtitle")

stages = [
    ("STEP 1", SF_BLUE, WHITE),
    ("STEP 2", DK2,     WHITE),
    ("STEP 3", TEAL,    DK1),
    ("STEP 4", ORANGE,  DK1),
]
n = len(stages); gap = 0.25
box_w = (9.10 - gap * (n - 1)) / n; x = 0.40

for i, (label, bg, fg) in enumerate(stages):
    add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE,
                   x, 1.50, box_w, 2.00,
                   label, bg, fg, font_size=10, bold=True)
    if i > 0:
        arrow = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            Inches(x - gap + 0.02), Inches(2.35),
            Inches(gap - 0.04), Inches(0.20))
        arrow.fill.solid(); arrow.fill.fore_color.rgb = BODY_GREY
        arrow.line.fill.background()
    x += box_w + gap
```

### 13.2 Metric Callout Cards (use Layout 8)

```python
slide = prs.slides.add_slide(prs.slide_layouts[8])
set_ph(slide, 0, "KEY METRICS")
set_ph(slide, 5, "Performance highlights")
metrics = [("99.9%", "Uptime SLA"), ("50+", "Regions"), ("10x", "Faster"), ("Zero", "Admin")]
for col_idx, (num, label) in enumerate(metrics):
    set_ph_lines(slide, col_idx + 1, [num, label])
```

---

