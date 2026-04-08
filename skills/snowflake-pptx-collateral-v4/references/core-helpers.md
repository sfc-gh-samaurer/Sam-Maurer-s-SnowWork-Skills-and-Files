---
name: pptx-core-helpers
description: Placeholder helpers (set_ph, set_ph_lines, set_ph_sections, set_ph_bold_keywords, set_ph_rich), custom shape text rules, add_shape_text(), footnotes, images, and saving.
---

## 9. Placeholder Helper Functions

Always let placeholders **inherit styling from the template**. Do not override fonts or colours on placeholder text.

### Helper Function Selection Guide

| Content Pattern | Use This Function | Example |
|----------------|-------------------|---------|
| Title or subtitle (single string) | `set_ph()` | `set_ph(slide, 0, "Our Strategy")` |
| Heading + body bullet groups | **`set_ph_sections()`** ⭐ PREFERRED | 2-3 headings each with 2-4 bullets |
| Bold keyword: description pairs | `set_ph_bold_keywords()` | Feature name + explanation per line |
| Simple flat bullet list (all equal) | `set_ph_lines()` | 4-6 bullet points, no grouping needed |
| Mixed formatting in one paragraph | `set_ph_rich()` | Bold + normal in same line |

**⚠ CRITICAL**: Never use `set_ph_lines()` with empty strings to create spacing. If you need heading/body grouping, use `set_ph_sections()`. If you find yourself adding blank lines between items, you should be using `set_ph_sections()` instead.

```python
def set_ph(slide, idx, text):
    """Set placeholder text. Styling inherits from master layout.
    
    Key behaviours:
    - Prevents title/subtitle expansion (TEXT_TO_FIT_SHAPE)
    - Adjusts internal margins to create visual gap between title and subtitle
      (template gap is only 0.02" — effectively zero without this fix)
    - Resets paragraph indent so wrapped subtitle lines align to the left edge
    """
    from pptx.enum.text import MSO_AUTO_SIZE
    ph = slide.placeholders[idx]
    
    # Guard: warn if title exceeds 50 chars (Rule 26)
    t_pos = (ph.top or 0) / 914400
    if t_pos < 0.50:  # Title placeholder
        clean = text.replace('\n', ' ')
        if len(clean) > 50:
            print(f"⚠ TITLE TOO LONG: {len(clean)} chars (max 50): \"{clean[:50]}...\"")
    
    ph.text = text
    ph.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    
    # --- Internal margin fix for title-subtitle gap ---
    # The <a:bodyPr> element controls internal padding.
    # Title bottom at 0.70", subtitle top at 0.72" = only 0.02" gap.
    # We zero the title's bottom inset and add top inset to subtitle.
    from lxml import etree
    ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    bodyPr = ph.text_frame._txBody.find(f'{{{ns}}}bodyPr')
    if bodyPr is None:
        bodyPr = etree.SubElement(ph.text_frame._txBody, f'{{{ns}}}bodyPr')
    
    t_pos = (ph.top or 0) / 914400
    if t_pos < 0.50:
        # TITLE: zero bottom padding → text sits higher in the box
        bodyPr.set('bIns', '0')
    elif 0.60 < t_pos < 1.20:
        # SUBTITLE: add top padding (54864 EMU ≈ 0.06") → pushes text down
        bodyPr.set('tIns', '54864')
    
    # --- Wrapped line alignment fix (TITLE & SUBTITLE ONLY) ---
    # Reset indent so second line of wrapped text starts at same left as first.
    # CRITICAL: Only apply to title/subtitle (t_pos < 1.20). Do NOT apply to body
    # placeholders — resetting their marL/indent would kill bullet indentation.
    if t_pos < 1.20:
        for para in ph.text_frame.paragraphs:
            pPr = para._p.find(f'{{{ns}}}pPr')
            if pPr is None:
                pPr = etree.SubElement(para._p, f'{{{ns}}}pPr')
                para._p.insert(0, pPr)  # pPr must be first child of <a:p>
            pPr.set('indent', '0')
            pPr.set('marL', '0')

def _pad_body_ph(ph):
    """Add bottom padding to body placeholders to prevent text from crowding the footer.
    The template's body PHs end at 5.12" — 0.02" past the 5.10" safe zone.
    Adding 0.10" (91440 EMU) bottom padding ensures text stays visually clear of
    the copyright line (5.32") and accent dot (5.30").
    Only applies to placeholders below the subtitle area (top > 1.20").
    """
    from lxml import etree
    t_pos = (ph.top or 0) / 914400
    if t_pos > 1.20:  # Body placeholder
        ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
        bodyPr = ph.text_frame._txBody.find(f'{{{ns}}}bodyPr')
        if bodyPr is None:
            bodyPr = etree.SubElement(ph.text_frame._txBody, f'{{{ns}}}bodyPr')
        bodyPr.set('bIns', '91440')  # 0.10" bottom padding

def set_ph_lines(slide, idx, lines, font_size=None):
    """Fill placeholder with multiple flat paragraphs (same level, no headings).
    
    Use ONLY for simple bullet lists where every line is equal (no heading+body pairs).
    For heading+body groups, use set_ph_sections() instead.
    
    ⚠ NEVER pass empty strings in lines — empty paragraphs create inconsistent spacing.
    """
    ph = slide.placeholders[idx]
    tf = ph.text_frame
    tf.clear()
    _pad_body_ph(ph)
    # Filter out empty lines — they cause uneven spacing (Rule 35)
    lines = [l for l in lines if l.strip()]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        if font_size:
            p.font.size = Pt(font_size)

def set_ph_rich(slide, idx, runs_list):
    """Fill placeholder with rich text runs.
    Each item: (text, {font_opts}).
    Example: [("Bold part", {"bold": True}), (" normal part", {})]
    """
    ph = slide.placeholders[idx]
    tf = ph.text_frame
    tf.clear()
    _pad_body_ph(ph)
    p = tf.paragraphs[0]
    for i, (text, opts) in enumerate(runs_list):
        run = p.runs[0] if i == 0 and p.runs else p.add_run()
        run.text = text
        if opts.get("bold"): run.font.bold = True
        if opts.get("size"): run.font.size = Pt(opts["size"])
        if opts.get("color"): run.font.color.rgb = opts["color"]

def set_ph_sections(slide, idx, sections, heading_size=None, body_size=None):
    """Fill placeholder with heading + body pairs (the PREFERRED content pattern).
    
    USE THIS whenever body content has grouped information — it produces consistent
    spacing through proper Level 0/Level 1 hierarchy with explicit section gaps.
    
    sections: list of (heading_text, [body_line_1, body_line_2, ...])
    
    Headings render at Level 0 with BOLD + DK2 colour + 14pt gap before 2nd+ headings.
    Body lines render at Level 1 with template bullet style.
    
    Example:
        set_ph_sections(slide, 1, [
            ("Access Latest Models", [
                "New models launch in limited regions first",
                "Cross-region gives immediate access",
            ]),
            ("Multi-Region Deployments", [
                "GCP, Azure accounts can access full catalog",
            ]),
        ])
    """
    ph = slide.placeholders[idx]
    tf = ph.text_frame
    tf.clear()
    _pad_body_ph(ph)
    first = True
    for heading, body_lines in sections:
        # Heading paragraph: Level 0, Bold, DK2
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.level = 0
        
        # --- Section spacing: add space-before to non-first headings ---
        # Template default spcBef for L0 is 0pt, which makes sections run together.
        # Explicitly set 14pt (177800 EMU) gap before 2nd+ headings.
        if not first:
            from lxml import etree
            ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
            pPr = p._p.find(f'{{{ns}}}pPr')
            if pPr is None:
                pPr = etree.SubElement(p._p, f'{{{ns}}}pPr')
                p._p.insert(0, pPr)
            spcBef = etree.SubElement(pPr, f'{{{ns}}}spcBef')
            spcPts = etree.SubElement(spcBef, f'{{{ns}}}spcPts')
            spcPts.set('val', '1400')  # 14pt in hundredths = 1400
        first = False
        
        run = p.add_run()
        run.text = heading
        run.font.bold = True
        run.font.color.rgb = DK2
        if heading_size:
            run.font.size = Pt(heading_size)
        # Body paragraphs: Level 1 (gets template bullet automatically)
        for line in body_lines:
            bp = tf.add_paragraph()
            bp.level = 1
            bp.text = line
            if body_size:
                bp.font.size = Pt(body_size)

def set_ph_bold_keywords(slide, idx, items, kw_size=None, body_size=None):
    """Fill placeholder where each item has a bold keyword prefix.
    
    items: list of (keyword, description)
    
    Renders as: "**Keyword:** Description text" per paragraph.
    
    Example:
        set_ph_bold_keywords(slide, 1, [
            ("Latency", "Cross-region adds network latency between regions"),
            ("Account-Wide", "The parameter affects ALL users in the account"),
            ("SnowGov", "NOT supported in U.S. SnowGov regions"),
        ])
    """
    ph = slide.placeholders[idx]
    tf = ph.text_frame
    tf.clear()
    _pad_body_ph(ph)
    for i, (keyword, description) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        # Bold keyword run
        r1 = p.add_run()
        r1.text = f"{keyword}: "
        r1.font.bold = True
        if kw_size: r1.font.size = Pt(kw_size)
        # Normal description run
        r2 = p.add_run()
        r2.text = description
        if body_size: r2.font.size = Pt(body_size)
```

### When to Use Each Helper

| Content Pattern | Helper Function | Example |
|----------------|----------------|---------|
| Simple single-line text | `set_ph(slide, idx, "TEXT")` | Titles, subtitles |
| Flat list of items (same importance) | `set_ph_lines(slide, idx, [...])` | Agendas, reference links |
| **Heading + body pairs** (most common) | `set_ph_sections(slide, idx, [...])` | Feature lists, use cases, takeaways |
| **Bold keyword : description** items | `set_ph_bold_keywords(slide, idx, [...])` | Considerations, warnings, definitions |
| Mixed formatting in one paragraph | `set_ph_rich(slide, idx, [...])` | Custom inline formatting |

### Paragraph Levels — When to Use What

| Level | Purpose | Visual Result | When to Use |
|-------|---------|---------------|-------------|
| **L0** (default) | Top-level paragraph | No bullet on layout 5; bullet on 6-8 | Headings, flat list items |
| **L1** | Sub-item / body detail | Indented with `\u2022` bullet | Body text under a heading, supporting details |
| **L2** | Sub-sub-item | Further indented bullet | Rare — use only for deep nesting |

**CRITICAL**: When a placeholder contains **section headings followed by body text** (e.g. "Feature Name" then "description of the feature"), you **MUST** use `set_ph_sections()` or manually set heading paragraphs to L0 bold DK2 and body paragraphs to L1. **Never leave headings and body at the same level with the same formatting** — this creates an unreadable wall of text.

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

| Circle Diameter | Usable Width | Max Characters | Max Lines | Max Font Size | Example Use |
|----------------|-------------|---------------|-----------|---------------|-------------|
| ≤ 0.60"        | ~0.42"      | 2 chars        | 1 line    | **14pt**      | Number badge "01" |
| 0.61-0.80"     | ~0.53"      | 2-3 chars      | 1 line    | **14pt**      | Initials "DR" |
| 0.81-1.00"     | ~0.70"      | 6-8 chars      | 1-2 lines | **10pt**      | Short label |
| 1.01-1.50"     | ~0.98"      | 8-12 chars     | 2 lines   | **11pt**      | "CORTEX\nAI" |
| 1.51-2.00"     | ~1.26"      | 12-18 chars    | 2-3 lines | **14pt**      | Hub label |

⚠ **Circles are the #1 overflow problem.** Text inside a circle only has ~70% of the diameter as usable width. A 0.55" circle gives only 0.39" for text — 18pt font WILL overflow. Always use `MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` on circles as a safety net.

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

### 12.7 MANDATORY Helper Function — `add_shape_text()` (MUST COPY INTO EVERY SCRIPT)

**You MUST define this function at the top of every script and use it for ALL custom shapes.** Never set text on shapes manually — always call `add_shape_text()`. This function enforces font, auto_size, alignment, and multi-line handling in one place so nothing is forgotten.

```python
def add_shape_text(slide, shape_type, left, top, width, height,
                   text, fill_colour, font_colour,
                   font_size=10, bold=False, alignment=PP_ALIGN.CENTER):
    """Add a shape with text — enforces ALL brand rules automatically.
    
    Args:
        text: Use \\n for multi-line: "LINE ONE\\nLINE TWO". 
              NEVER pass multiple strings or create separate runs.
    """
    shape = slide.shapes.add_shape(
        shape_type,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_colour
    shape.line.fill.background()                 # no outline

    # AUTO LINE-BREAK: narrow shapes (≤2") can't word-wrap legibly.
    # If caller forgot \n, insert it between words automatically.
    if width <= 2.0 and '\n' not in text and ' ' in text:
        text = text.replace(' ', '\n')

    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # CRITICAL: shrink to fit
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Set margins tight for small shapes
    from pptx.util import Pt as PtUtil
    tf.margin_left = PtUtil(4)
    tf.margin_right = PtUtil(4)
    tf.margin_top = PtUtil(2)
    tf.margin_bottom = PtUtil(2)

    p = tf.paragraphs[0]
    p.text = text                                 # ← single string, use \n for lines
    p.font.name = "Arial"                         # CRITICAL: explicit font
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = font_colour
    p.alignment = alignment

    return shape
```

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

# ⚠ CALLOUT with title + body — ALWAYS use \n between title and body
add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.40, 4.30, 2.95, 0.75,
               "Chargeback\nBill teams for actual usage", SF_BLUE, WHITE, font_size=10, bold=True)
#              ^^^^^^^^^ \n separates bold title from description

# ⚠ TIP box — ALWAYS use \n between sentences
add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 5.55, 4.00, 3.95, 1.05,
               "TIP: Use GET_QUERY_OPERATOR_STATS()\nto analyze query plan operators\nand identify bottlenecks",
               TEAL, DK1, font_size=9)
```

⚠ **COMMON MISTAKE — Callout shapes with title + body:**

```python
# ❌ WRONG — title and body concatenated on one line
add_shape_text(..., "ChargebackBill teams for actual usage", ...)  # Unreadable!

# ✅ CORRECT — \n between title and body text
add_shape_text(..., "Chargeback\nBill teams for actual usage", ...)

# ❌ WRONG — multi-sentence TIP without line breaks
add_shape_text(..., "TIP: Use X()to analyze Y and find Z", ...)

# ✅ CORRECT — \n between each sentence/clause
add_shape_text(..., "TIP: Use X()\nto analyze Y\nand find Z", ...)
```

**Rule: If a shape text contains more than 5 words, check if it needs `\n` to split across lines.** Callout boxes, TIP boxes, and label+description shapes almost always need `\n`.

**Rules:**
- NEVER set `p.text`, `run.text`, or `shape.text_frame.text` directly on custom shapes. Always use `add_shape_text()`.
- NEVER create separate runs within one paragraph. One string, one `p.text` assignment.
- For description text below shapes, still use `add_shape_text()` with `LIGHT_BG` or `WHITE` fill and smaller font.
- The function enforces: Arial font, auto_size, vertical centering, tight margins, and no-outline — all in one call.

### 12.8 MANDATORY Helper Function — `add_code_block()` (For SQL / Code / Multi-Line Text Blocks)

**Use this for ANY shape that displays code, SQL, command examples, or dense multi-line text (e.g. best practices lists).** This helper enforces `\n` line breaks, left-alignment, auto-sizing, and monospace-style formatting.

⚠ **CRITICAL**: SQL statements, code snippets, and multi-line best-practices lists are the #1 source of concatenated text. The LLM tends to build these as a single long string without `\n`. This helper FORCES you to pass lines as a list, which guarantees proper line breaks.

```python
def add_code_block(slide, left, top, width, height, lines,
                   bg_colour=None, font_colour=None, font_size=9):
    """Add a code/SQL/multi-line text block with proper line breaks.
    
    Args:
        lines: LIST of strings — each becomes one line. 
               NEVER pass a single concatenated string.
               Example: ["-- Create monitor", "CREATE RESOURCE MONITOR budget", "  WITH CREDIT_QUOTA = 5000;"]
        bg_colour: Background fill (default LIGHT_BG)
        font_colour: Text colour (default DK1)
    """
    from pptx.util import Inches, Pt
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN, MSO_ANCHOR

    if bg_colour is None: bg_colour = LIGHT_BG
    if font_colour is None: font_colour = DK1

    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_colour
    shape.line.fill.background()

    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # CRITICAL: shrink to fit
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Pt(6)
    tf.margin_right = Pt(6)
    tf.margin_top = Pt(4)
    tf.margin_bottom = Pt(4)

    # Join lines with \n — guarantees line breaks
    text = "\n".join(lines)
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_colour
    p.alignment = PP_ALIGN.LEFT

    return shape
```

**Usage examples:**
```python
# SQL code block
add_code_block(slide, 0.40, 1.35, 9.10, 1.35, [
    "-- Create resource monitor with alerts",
    "CREATE RESOURCE MONITOR monthly_budget",
    "  WITH CREDIT_QUOTA = 5000",
    "  FREQUENCY = MONTHLY",
    "  START_TIMESTAMP = IMMEDIATELY;",
], font_size=9)

# Best practices list
add_code_block(slide, 0.40, 3.95, 9.10, 1.00, [
    "BEST PRACTICES:",
    "• Separate warehouses for ETL vs BI",
    "• Set auto-suspend to 5 minutes minimum",
    "• Use resource monitors per department",
    "• Tag all queries for cost attribution",
], bg_colour=DK2, font_colour=WHITE, font_size=9)

# Cache monitoring SQL
add_code_block(slide, 0.40, 2.85, 9.10, 1.20, [
    "-- Monitor warehouse cache effectiveness",
    "SELECT",
    "  WAREHOUSE_NAME,",
    "  AVG(BYTES_SCANNED) AS avg_bytes_scanned,",
    "  AVG(BYTES_SPILLED_TO_LOCAL_STORAGE) AS avg_spill",
    "FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY",
    "GROUP BY 1 ORDER BY 2 DESC;",
], font_size=9)
```

**Rules:**
- ALWAYS pass `lines` as a **Python list** — one string per visual line. NEVER pass a pre-concatenated string.
- Use for: SQL examples, code snippets, CLI commands, best-practices lists, any dense multi-line block.
- For simple shape labels (1-3 short lines), continue using `add_shape_text()`.
- `add_code_block()` uses LEFT alignment and TOP anchor (code reads top-to-bottom).
- `add_shape_text()` uses CENTER alignment and MIDDLE anchor (labels are centred).

---

## 16. Footnote

```python
txBox = slide.shapes.add_textbox(
    Inches(0.40), Inches(4.70), Inches(9.10), Inches(0.35))
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Source: Snowflake Inc., 2026"
p.font.size = Pt(9); p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
```

Position at 4.70" top — above safe zone bottom (5.10") and clear of copyright.

---

## 17. Adding Images

```python
slide.shapes.add_picture(
    "path/to/image.png",
    Inches(0.40), Inches(1.50),   # within safe zone
    width=Inches(4.00))            # height auto-calculated
```

- Stay within safe content zone (Section 8)
- Max width 9.10" for full-width images on content slides
- PNG for icons/diagrams, JPEG for photos
- For split layout right side: left=5.40", width=4.10"
- For full-bleed: use layout 12 (blank canvas)

---

## 18. Saving

```python
import os
output_path = "outputs/My_Deck.pptx"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
prs.save(output_path)
print(f"Saved: {output_path}")
```

---
