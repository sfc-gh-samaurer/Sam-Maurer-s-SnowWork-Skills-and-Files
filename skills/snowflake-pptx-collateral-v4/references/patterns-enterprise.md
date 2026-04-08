---
name: pptx-patterns-enterprise
description: 37 advanced visual slide patterns — full Python code for enterprise consulting layouts.
---

# PPTX Visual Patterns Reference — Enterprise Playbook

> **This file is a reference companion to SKILL.md.**
> Read this file when you need the full Python code for a specific visual pattern.
> The Pattern Selection Guide at the bottom maps content types to pattern numbers.

## 14. Advanced Slide Patterns (Enterprise Playbook)

These patterns are inspired by enterprise consulting decks and cover every
common slide archetype. All patterns use the Snowflake template, Snowflake
colours, and safe content zones.

### 14.0 Positioning & Alignment Standards (Mandatory for ALL Patterns)

Every pattern in this section MUST follow these alignment rules:

| Rule | Specification | Reason |
|------|--------------|--------|
| **Min content top** | ≥ **1.30"** for all custom shapes | Subtitle PH ends at 1.12"; 0.18" gap prevents visual overlap |
| **Max content bottom** | ≤ **5.10"** (4.00" on Layout 2, 4.60" on Layout 3) | Above copyright/accent elements |
| **Left margin** | ≥ **0.40"** | Matches placeholder alignment |
| **Right margin** | ≤ **9.50"** | 0.50" clearance from slide edge |
| **Vertical text anchor** | `tf.vertical_anchor = MSO_ANCHOR.MIDDLE` on **every `add_shape()` with text** | Without this, text sits at top of shape — looks misaligned |
| **Exception to MIDDLE** | Only omit for shapes with height > 0.80" AND multi-paragraph flowing text | Tall containers with headings + bullets should let text flow from top |
| **Horizontal centering** | `p.alignment = PP_ALIGN.CENTER` on shape text | Text should be centred within shapes |
| **Description alignment** | Description textboxes below shapes must have **same width and X as parent** | Prevents jagged alignment across columns |
| **Consistent Y per row** | All shapes in the same conceptual row must share the **same Y position** | Prevents uneven visual lines |

**Before creating any pattern:** Verify the topmost custom shape starts at ≥ 1.30".
**After creating any pattern:** Run `verify_slide()` to catch violations.

### 14.1 Visual Agenda — Timeline Blocks

Horizontal blocks across the slide, each showing a time slot, topic, and description.
Best for workshop, training, or meeting decks.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "WORKSHOP AGENDA")
set_ph(slide, 1, "Today's session plan and expected outcomes")

agenda_items = [
    ("9:00 – 9:30", "Welcome &\nOverview", "Set context and\nreview objectives"),
    ("9:30 – 10:30", "Deep Dive:\nArchitecture", "Technical walkthrough\nof the solution"),
    ("10:45 – 11:30", "Hands-On\nLab", "Build and test\nin your environment"),
    ("11:30 – 12:00", "Q&A &\nNext Steps", "Open discussion\nand action items"),
]
n = len(agenda_items)
box_w = (9.10 - 0.20 * (n - 1)) / n
x = 0.40

for i, (time, topic, desc) in enumerate(agenda_items):
    # Time label (small, above box)
    t_box = slide.shapes.add_textbox(
        Inches(x), Inches(1.30), Inches(box_w), Inches(0.25))
    t_box.text_frame.word_wrap = True
    p = t_box.text_frame.paragraphs[0]; p.text = time
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Topic box (coloured)
    bg = SF_BLUE if i % 2 == 0 else DK2
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.60), Inches(box_w), Inches(0.70))
    box.fill.solid(); box.fill.fore_color.rgb = bg
    box.line.fill.background()
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = topic
    p.font.size = Pt(11); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Description box (white, below)
    d_box = slide.shapes.add_textbox(
        Inches(x), Inches(2.40), Inches(box_w), Inches(0.80))
    d_box.text_frame.word_wrap = True
    p = d_box.text_frame.paragraphs[0]; p.text = desc
    p.font.size = Pt(9); p.font.color.rgb = DK1
    p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER

    x += box_w + 0.20
```

### 14.2 Visual Agenda — Outcomes Row

Extends 14.1: add an "Expected Outcomes" row below the agenda boxes. Each
outcome card maps to its agenda block.

```python
# After agenda boxes from 14.1, add outcome cards:
outcomes = [
    "Aligned on program scope and timeline",
    "Shared understanding of architecture decisions",
    "Working prototype in your environment",
    "Clear action items with owners and dates",
]
x = 0.40
for i, outcome in enumerate(outcomes):
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(3.40), Inches(box_w), Inches(0.70))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT_BG  # #F5F5F5
    box.line.fill.background()
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = outcome
    p.font.size = Pt(9); p.font.color.rgb = DK1
    p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER
    x += box_w + 0.20

# "EXPECTED OUTCOMES" label on left
lbl = slide.shapes.add_textbox(Inches(0.40), Inches(3.20), Inches(2.00), Inches(0.20))
p = lbl.text_frame.paragraphs[0]; p.text = "EXPECTED OUTCOMES"
p.font.size = Pt(8); p.font.bold = True
p.font.color.rgb = DK2; p.font.name = "Arial"
```

### 14.3 Goals & Objectives — Split Panel

Left side shows goals with bold headings + body. Right side shows desired outcomes.
Use Layout 0 (free canvas) or Layout 6 (2-col placeholder).

```python
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_ph(slide, 0, "GOALS & OBJECTIVES")
set_ph(slide, 3, "What we aim to achieve and how we'll measure success")
set_ph_sections(slide, 1, [
    ("Modernise Data Platform", [
        "Migrate legacy warehouses to Snowflake",
        "Reduce query latency by 60%",
    ]),
    ("Enable Self-Service Analytics", [
        "Deploy Cortex AI for natural language queries",
        "Train 200+ business analysts on new tools",
    ]),
], heading_size=11, body_size=10)
set_ph_sections(slide, 2, [
    ("Desired Outcomes", [
        "Single source of truth across all BUs",
        "Real-time dashboards for executive team",
        "50% reduction in time-to-insight",
        "Full audit trail and governance compliance",
    ]),
], heading_size=11, body_size=10)
```

### 14.4 "What This IS / IS NOT" — Contrast Slide

Clean comparison to set expectations. Use Layout 6 (2-col) with contrasting fills.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "WHAT THIS ENGAGEMENT IS & IS NOT")
set_ph(slide, 1, "Setting clear expectations upfront")

# "IS" box (left, light background)
is_box = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.40), Inches(1.40), Inches(4.30), Inches(3.50))
is_box.fill.solid(); is_box.fill.fore_color.rgb = LIGHT_BG  # #F5F5F5
is_box.line.fill.background()
tf = is_box.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run(); r.text = "THIS IS"; r.font.size = Pt(14)
r.font.bold = True; r.font.color.rgb = DK2; r.font.name = "Arial"
items_is = [
    "A focused technical assessment of your current architecture",
    "A set of prioritised, actionable recommendations",
    "A roadmap with effort estimates and quick wins",
]
for item in items_is:
    p2 = tf.add_paragraph(); p2.level = 0
    r2 = p2.add_run(); r2.text = f"•  {item}"
    r2.font.size = Pt(10); r2.font.color.rgb = DK1; r2.font.name = "Arial"

# "IS NOT" box (right, light background)
not_box = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(4.90), Inches(1.40), Inches(4.60), Inches(3.50))
not_box.fill.solid(); not_box.fill.fore_color.rgb = LIGHT_BG  # #F5F5F5
not_box.line.fill.background()
tf = not_box.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run(); r.text = "THIS IS NOT"; r.font.size = Pt(14)
r.font.bold = True; r.font.color.rgb = DK1; r.font.name = "Arial"
items_not = [
    "A complete re-architecture of your entire data stack",
    "A replacement of your existing BI tool investment",
    "A reevaluation of your organisation's strategy",
]
for item in items_not:
    p2 = tf.add_paragraph(); p2.level = 0
    r2 = p2.add_run(); r2.text = f"•  {item}"
    r2.font.size = Pt(10); r2.font.color.rgb = BODY_GREY; r2.font.name = "Arial"
```

### 14.5 Before / After Comparison

Side-by-side comparison showing transformation. Use Layout 6 or custom shapes.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "TRANSFORMATION JOURNEY")
set_ph(slide, 1, "From current state to future state")

# "BEFORE" panel
for label, bg, fg, left_x in [("BEFORE", BODY_GREY, WHITE, 0.40), ("AFTER", SF_BLUE, WHITE, 5.00)]:
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left_x), Inches(1.30), Inches(4.50), Inches(0.40))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = bg
    hdr.line.fill.background()
    hdr.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = hdr.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = fg; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

before_items = ["Manual data pipelines", "Weekly batch reporting", "Siloed team access", "No governance framework"]
after_items = ["Automated Snowpipe ingestion", "Real-time streaming dashboards", "Self-service access for all BUs", "Full RBAC and data masking"]

for items, left_x in [(before_items, 0.40), (after_items, 5.00)]:
    for j, item in enumerate(items):
        row = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left_x), Inches(1.85 + j * 0.70), Inches(4.50), Inches(0.55))
        row.fill.solid()
        row.fill.fore_color.rgb = LIGHT_BG if left_x < 3 else WHITE
        row.line.fill.background()
        tf = row.text_frame; tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.text = item
        p.font.size = Pt(10); p.font.color.rgb = DK1; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER
```

### 14.6 Numbered Steps / Approach (3-Step Process)

Three numbered columns, each with a circled number, bold title, and bullet details.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "OUR APPROACH")
set_ph(slide, 1, "A structured three-phase methodology")

steps = [
    ("1", "ASSESS\nCURRENT STATE", [
        "Audit existing data architecture",
        "Interview key stakeholders",
        "Document pain points and gaps",
    ]),
    ("2", "DESIGN\nFUTURE STATE", [
        "Define target architecture on Snowflake",
        "Map data flows and integrations",
        "Create migration runbook",
    ]),
    ("3", "IMPLEMENT &\nVALIDATE", [
        "Execute phased migration",
        "Run parallel testing",
        "Deliver training and handover",
    ]),
]
n = len(steps); gap = 0.25
col_w = (9.10 - gap * (n - 1)) / n; x = 0.40

for i, (num, title, bullets) in enumerate(steps):
    # Number circle
    circ = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x + col_w/2 - 0.20), Inches(1.35), Inches(0.40), Inches(0.40))
    circ.fill.solid(); circ.fill.fore_color.rgb = SF_BLUE
    circ.line.fill.background()
    circ.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = circ.text_frame.paragraphs[0]; p.text = num
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Title box
    t_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.85), Inches(col_w), Inches(0.60))
    t_box.fill.solid(); t_box.fill.fore_color.rgb = DK2
    t_box.line.fill.background()
    tf = t_box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Bullet items below
    for j, bullet in enumerate(bullets):
        b_box = slide.shapes.add_textbox(
            Inches(x), Inches(2.60 + j * 0.40), Inches(col_w), Inches(0.35))
        b_box.text_frame.word_wrap = True
        p = b_box.text_frame.paragraphs[0]; p.text = f"• {bullet}"
        p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"

    x += col_w + gap
```

### 14.7 Stat Callout / Big Number Grid

Large bold numbers with supporting text underneath, in a 2x2 or 1x4 grid.
Grabs attention with key metrics.

> **CRITICAL**: Numbers using SF_BLUE colour MUST be **≥ 28pt**. If you need numbers
> smaller than 28pt (e.g. in a compact 2×2 grid), use **DK2** instead of SF_BLUE.
> This is Rule 10 — SF_BLUE is only allowed at 28pt or above. No exceptions.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "THE CASE FOR CHANGE")
set_ph(slide, 1, "Key data points driving the transformation")

stats = [
    ("53%", "of enterprises\nlag in data readiness", SF_BLUE),
    ("$12.9M", "average annual cost\nof poor data quality", DK2),
    ("3.5x", "faster insights with\nmodern data platforms", SF_BLUE),
    ("89%", "of leaders cite data as\ntop strategic priority", DK2),
]
n = len(stats); gap = 0.20
box_w = (9.10 - gap * (n - 1)) / n; x = 0.40

for i, (number, description, accent) in enumerate(stats):
    # Number (big, bold — only SF_BLUE at 28pt+ or DK2 allowed as text)
    n_box = slide.shapes.add_textbox(
        Inches(x), Inches(1.50), Inches(box_w), Inches(0.60))
    n_box.text_frame.word_wrap = True
    p = n_box.text_frame.paragraphs[0]; p.text = number
    p.font.size = Pt(28); p.font.bold = True
    p.font.color.rgb = accent; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Divider line (accent colour as fill is fine)
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x + 0.30), Inches(2.15), Inches(box_w - 0.60), Inches(0.03))
    line.fill.solid(); line.fill.fore_color.rgb = accent
    line.line.fill.background()

    # Description
    d_box = slide.shapes.add_textbox(
        Inches(x), Inches(2.30), Inches(box_w), Inches(0.80))
    d_box.text_frame.word_wrap = True
    p = d_box.text_frame.paragraphs[0]; p.text = description
    p.font.size = Pt(10); p.font.color.rgb = DK1
    p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER

    x += box_w + gap

# Optional bottom insight bar
insight = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.40), Inches(3.60), Inches(9.10), Inches(0.60))
insight.fill.solid(); insight.fill.fore_color.rgb = DK2
insight.line.fill.background()
insight.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
p = insight.text_frame.paragraphs[0]
p.text = "Snowflake's unified platform addresses all four challenges in a single solution"
p.font.size = Pt(11); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER
```

### 14.8 Roadmap / Phased Timeline

Horizontal swim-lane style roadmap with phases across the top and
activities in rows below. Use Layout 0 (free canvas).

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "IMPLEMENTATION ROADMAP")
set_ph(slide, 1, "Phased approach over 12 weeks")

phases = [
    ("PHASE 1:\nDESIGN & TEST", "Weeks 1-4", SF_BLUE, WHITE),
    ("PHASE 2:\nBUILD & PILOT", "Weeks 5-8", DK2, WHITE),
    ("PHASE 3:\nSCALE & DEPLOY", "Weeks 9-12", TEAL, DK1),
]
activities = [
    # (text, phase_start_idx, phase_span)
    ("Discovery & requirements gathering", 0, 1),
    ("Architecture design & review", 0, 1),
    ("Pilot environment setup", 1, 1),
    ("Data migration & ETL development", 1, 1),
    ("UAT & performance testing", 1, 2),
    ("Production deployment & cutover", 2, 1),
    ("Training & knowledge transfer", 2, 1),
]
n_phases = len(phases); gap = 0.15
phase_w = (9.10 - gap * (n_phases - 1)) / n_phases
x = 0.40

# Phase headers
for i, (label, timing, color, txt_color) in enumerate(phases):
    px = 0.40 + i * (phase_w + gap)
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(px), Inches(1.30), Inches(phase_w), Inches(0.65))
    box.fill.solid(); box.fill.fore_color.rgb = color
    box.line.fill.background()
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = txt_color; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
    # Timing label
    t_lbl = slide.shapes.add_textbox(
        Inches(px), Inches(1.95), Inches(phase_w), Inches(0.20))
    p = t_lbl.text_frame.paragraphs[0]; p.text = timing
    p.font.size = Pt(8); p.font.color.rgb = BODY_GREY
    p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER

# Activity bars
row_h = 0.32; y_start = 2.25
for j, (text, start, span) in enumerate(activities):
    ax = 0.40 + start * (phase_w + gap)
    aw = phase_w * span + gap * (span - 1)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(ax), Inches(y_start + j * (row_h + 0.08)),
        Inches(aw), Inches(row_h))
    bar.fill.solid()
    bar.fill.fore_color.rgb = LIGHT_BG
    bar.line.color.rgb = BORDER
    bar.line.width = Pt(0.5)
    tf = bar.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### 14.9 Guiding Principles / Numbered Pillars

Bold numbered principle headings with body descriptions. Use Layout 5 or custom shapes.

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
set_ph(slide, 0, "GUIDING PRINCIPLES")
set_ph(slide, 2, "Our approach is grounded in these core principles")
set_ph_sections(slide, 1, [
    ("1.  Data Gravity", [
        "Keep processing close to where data lives",
        "Minimise data movement across clouds",
    ]),
    ("2.  Zero-Copy Sharing", [
        "Share data without duplicating it",
        "Maintain a single source of truth",
    ]),
    ("3.  Governance by Default", [
        "Row-level security and dynamic masking from day one",
        "Full audit trail on all data access",
    ]),
    ("4.  Cost Transparency", [
        "Per-query cost attribution to business units",
        "Auto-suspend and right-size warehouses",
    ]),
], heading_size=11, body_size=10)
```

### 14.10 Decision Matrix / Option Comparison

Three options side by side with criteria and recommendations. Use Layout 0.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "ARCHITECTURE OPTIONS")
set_ph(slide, 1, "Evaluating three approaches for the data platform")

options = [
    ("OPTION A:\nLIFT & SHIFT", BODY_GREY, [
        "Migrate existing ETL as-is",
        "Lowest effort, fastest timeline",
        "Does not address tech debt",
    ]),
    ("OPTION B:\nRE-ARCHITECT", SF_BLUE, [
        "Redesign pipelines for Snowflake",
        "Medium effort, strong ROI",
        "Addresses performance gaps",
    ]),
    ("OPTION C:\nGREENFIELD", DK2, [
        "Build from scratch on Snowflake",
        "Highest effort, highest long-term value",
        "Clean architecture, no legacy",
    ]),
]
n = len(options); gap = 0.20
col_w = (9.10 - gap * (n - 1)) / n; x = 0.40

for i, (title, color, items) in enumerate(options):
    # Header
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.30), Inches(col_w), Inches(0.55))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = color
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Content items
    for j, item in enumerate(items):
        b = slide.shapes.add_textbox(
            Inches(x + 0.10), Inches(2.00 + j * 0.40),
            Inches(col_w - 0.20), Inches(0.35))
        b.text_frame.word_wrap = True
        p = b.text_frame.paragraphs[0]; p.text = f"• {item}"
        p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"

    x += col_w + gap

# Recommendation bar
rec = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.40), Inches(3.80), Inches(9.10), Inches(0.50))
rec.fill.solid(); rec.fill.fore_color.rgb = SF_BLUE
rec.line.fill.background()
rec.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
p = rec.text_frame.paragraphs[0]
p.text = "RECOMMENDED: Option B — best balance of effort, ROI, and future-readiness"
p.font.size = Pt(11); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER
```

### 14.11 Pros / Cons (Benefits & Challenges)

Two-column comparison with green (benefits) and red (challenges) colour coding.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "BENEFITS & CHALLENGES")
set_ph(slide, 1, "Key considerations for cross-region inference")

for label, fill, txt_clr, items, lx in [
    ("BENEFITS", DK2, WHITE, [
        "Access to latest models regardless of region",
        "No code changes required",
        "No data stored or cached in transit",
        "Same credit rates — no egress charges",
    ], 0.40),
    ("CHALLENGES", SF_BLUE, WHITE, [
        "Added network latency for cross-region calls",
        "Account-wide setting — affects all users",
        "Not supported in SnowGov regions",
        "Automatic routing — no manual region selection",
    ], 5.00),
]:
    # Header
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(lx), Inches(1.30), Inches(4.50), Inches(0.40))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = fill
    hdr.line.fill.background()
    hdr.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = hdr.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = txt_clr; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    for j, item in enumerate(items):
        row = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(lx), Inches(1.85 + j * 0.65), Inches(4.50), Inches(0.50))
        row.fill.solid(); row.fill.fore_color.rgb = LIGHT_BG
        row.line.color.rgb = BORDER
        row.line.width = Pt(0.5)
        tf = row.text_frame; tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.text = item
        p.font.size = Pt(10); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### 14.12 Case Study Card

Structured case study with Challenge → Approach → Result sections.
Use Layout 11 (Split) for image+text, or Layout 0 for all-text.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CASE STUDY: GLOBAL RETAILER")
set_ph(slide, 1, "How we delivered 10x query performance improvement")

sections = [
    ("THE CHALLENGE", SF_BLUE, WHITE, "Legacy data warehouse couldn't handle Black Friday traffic spikes. Reports took 4+ hours and analysts resorted to spreadsheets."),
    ("OUR APPROACH", DK2, WHITE, "Migrated to Snowflake with multi-cluster auto-scaling. Implemented Cortex AI for natural language queries and Snowpipe for real-time ingestion."),
    ("THE RESULT", TEAL, DK1, "Query times reduced from 4 hours to 23 seconds. Self-service analytics adopted by 500+ users. $2.3M annual savings in infrastructure costs."),
]
y = 1.35
for label, color, txt_clr, text in sections:
    # Label bar
    lbl = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.40), Inches(y), Inches(2.20), Inches(0.35))
    lbl.fill.solid(); lbl.fill.fore_color.rgb = color
    lbl.line.fill.background()
    lbl.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = lbl.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = txt_clr; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Content
    txt = slide.shapes.add_textbox(
        Inches(2.80), Inches(y), Inches(6.70), Inches(0.55))
    txt.text_frame.word_wrap = True
    p = txt.text_frame.paragraphs[0]; p.text = text
    p.font.size = Pt(10); p.font.color.rgb = DK1; p.font.name = "Arial"

    y += 0.80

# Result metrics row
metrics = [("10x", "Faster Queries"), ("500+", "Self-Service Users"), ("$2.3M", "Annual Savings")]
x = 0.40
for num, label in metrics:
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y + 0.20), Inches(2.90), Inches(0.70))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT_BG
    box.line.fill.background()
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = num; r.font.size = Pt(20)
    r.font.bold = True; r.font.color.rgb = DK2; r.font.name = "Arial"
    p2 = tf.add_paragraph()
    r2 = p2.add_run(); r2.text = label; r2.font.size = Pt(9)
    r2.font.color.rgb = BODY_GREY; r2.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER; p2.alignment = PP_ALIGN.CENTER
    x += 3.10
```

### 14.13 Team Bios / Profile Cards

Team member cards with name, title, and brief bio. Use Layout 8 (4-col) for up to 4,
or Layout 0 for custom layouts.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "YOUR PROJECT TEAM")
set_ph(slide, 1, "Key personnel dedicated to your engagement")

team = [
    ("Jane Smith", "Project Lead", "15 years in data platform modernisation. Led 50+ Snowflake migrations for Fortune 500 clients."),
    ("Tom Chen", "Solutions Architect", "Snowflake SnowPro Advanced certified. Expert in multi-cloud architecture and Cortex AI."),
    ("Lisa Park", "Data Engineer", "Specialist in real-time streaming, Snowpipe, and dynamic tables."),
    ("Mark Davis", "Change Management", "Certified Prosci practitioner. Drives adoption and training for enterprise data platforms."),
]
n = len(team); gap = 0.15
card_w = (9.10 - gap * (n - 1)) / n; x = 0.40

for i, (name, title, bio) in enumerate(team):
    # Name header
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.35), Inches(card_w), Inches(0.35))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = DK2
    hdr.line.fill.background()
    hdr.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = hdr.text_frame.paragraphs[0]; p.text = name
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Title
    t_box = slide.shapes.add_textbox(
        Inches(x), Inches(1.75), Inches(card_w), Inches(0.25))
    p = t_box.text_frame.paragraphs[0]; p.text = title
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Bio
    b_box = slide.shapes.add_textbox(
        Inches(x), Inches(2.05), Inches(card_w), Inches(1.50))
    b_box.text_frame.word_wrap = True
    p = b_box.text_frame.paragraphs[0]; p.text = bio
    p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"

    x += card_w + gap
```

### 14.14 Scenario Analysis / Market Sizing

Multiple scenarios side by side with key figures and a comparison table.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "SCENARIO ANALYSIS")
set_ph(slide, 1, "Three growth scenarios for the data platform investment")

scenarios = [
    ("CONSERVATIVE", BODY_GREY, "$1.2M", "12-month ROI", [
        "Migrate top 5 workloads only",
        "Single-region deployment",
    ]),
    ("MODERATE", SF_BLUE, "$3.5M", "8-month ROI", [
        "Migrate all production workloads",
        "Multi-region with cross-region inference",
    ]),
    ("AGGRESSIVE", DK2, "$7.8M", "5-month ROI", [
        "Full platform modernisation",
        "Cortex AI across all business units",
    ]),
]
n = len(scenarios); gap = 0.20
col_w = (9.10 - gap * (n - 1)) / n; x = 0.40

for i, (label, color, value, roi, items) in enumerate(scenarios):
    # Header
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.30), Inches(col_w), Inches(0.40))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = color
    hdr.line.fill.background()
    hdr.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = hdr.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Big number (use DK2 for all scenario values — safe as text at any size)
    v_box = slide.shapes.add_textbox(
        Inches(x), Inches(1.80), Inches(col_w), Inches(0.50))
    p = v_box.text_frame.paragraphs[0]; p.text = value
    p.font.size = Pt(28); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # ROI
    r_box = slide.shapes.add_textbox(
        Inches(x), Inches(2.30), Inches(col_w), Inches(0.25))
    p = r_box.text_frame.paragraphs[0]; p.text = roi
    p.font.size = Pt(9); p.font.color.rgb = BODY_GREY
    p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER

    # Detail items
    for j, item in enumerate(items):
        b = slide.shapes.add_textbox(
            Inches(x + 0.10), Inches(2.70 + j * 0.35),
            Inches(col_w - 0.20), Inches(0.30))
        b.text_frame.word_wrap = True
        p = b.text_frame.paragraphs[0]; p.text = f"• {item}"
        p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"

    x += col_w + gap
```

### 14.15 Competitive Landscape / Market Map

Positioned boxes showing market players or capabilities in a grid layout.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "COMPETITIVE LANDSCAPE")
set_ph(slide, 1, "How Snowflake compares to alternatives")

# Category headers (left labels)
categories = ["Cloud-Native DW", "Legacy On-Prem", "Open Source"]
for j, cat in enumerate(categories):
    lbl = slide.shapes.add_textbox(
        Inches(0.40), Inches(1.60 + j * 1.10), Inches(1.80), Inches(0.30))
    p = lbl.text_frame.paragraphs[0]; p.text = cat
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"

# Player boxes in a grid
players = [
    [("Snowflake", SF_BLUE), ("BigQuery", BODY_GREY), ("Redshift", BODY_GREY), ("Synapse", BODY_GREY)],
    [("Teradata", BODY_GREY), ("Oracle", BODY_GREY), ("Netezza", BODY_GREY)],
    [("Spark/Databricks", BODY_GREY), ("Trino/Presto", BODY_GREY), ("DuckDB", BODY_GREY)],
]
for row_i, row in enumerate(players):
    for col_i, (name, color) in enumerate(row):
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(2.40 + col_i * 1.80), Inches(1.55 + row_i * 1.10),
            Inches(1.60), Inches(0.45))
        box.fill.solid(); box.fill.fore_color.rgb = color
        box.line.fill.background()
        box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = box.text_frame.paragraphs[0]; p.text = name
        p.font.size = Pt(9); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER
```

### 14.16 Multi-Row Grid / Tracking Matrix

Grid layout with row headers on the left and content cells. Good for status
tracking, RACI matrices, or capability assessments.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CAPABILITY ASSESSMENT")
set_ph(slide, 1, "Current maturity across key data platform capabilities")

headers = ["Capability", "Current", "Target", "Gap"]
rows = [
    ["Data Ingestion", "Batch ETL", "Real-time Snowpipe", "HIGH"],
    ["Analytics", "SQL + Excel", "Cortex AI + Streamlit", "HIGH"],
    ["Governance", "Manual RBAC", "Dynamic Masking + Tags", "MEDIUM"],
    ["Sharing", "File exports", "Snowflake Marketplace", "HIGH"],
    ["Cost Mgmt", "Monthly review", "Per-query attribution", "LOW"],
]
n_cols = len(headers); n_rows = len(rows) + 1
tbl_shape = slide.shapes.add_table(
    n_rows, n_cols,
    Inches(0.40), Inches(1.30), Inches(9.10), Inches(0.40 * n_rows))
tbl = tbl_shape.table

# Header row
for ci, h in enumerate(headers):
    cell = tbl.cell(0, ci)
    cell.text = h
    cell.fill.solid(); cell.fill.fore_color.rgb = DK2
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(10); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER

# Data rows
# Fill + text colour pairs (TEAL/ORANGE are light → use DK1; DK2/SF_BLUE are dark → WHITE)
gap_fills = {"HIGH": (DK2, WHITE), "MEDIUM": (SF_BLUE, WHITE), "LOW": (DK2, WHITE)}
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri + 1, ci)
        cell.text = val
        cell.fill.solid()
        if ci == 0:  # Row header
            cell.fill.fore_color.rgb = LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.bold = True; p.font.size = Pt(10)
                p.font.color.rgb = DK1; p.font.name = "Arial"
        elif ci == 3:  # Gap column — colour coded
            fill_c, txt_c = gap_fills.get(val, (LIGHT_BG, DK1))
            cell.fill.fore_color.rgb = fill_c
            for p in cell.text_frame.paragraphs:
                p.font.bold = True; p.font.size = Pt(10)
                p.font.color.rgb = txt_c; p.font.name = "Arial"
                p.alignment = PP_ALIGN.CENTER
        else:
            cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10); p.font.color.rgb = DK1
                p.font.name = "Arial"

set_table_borders(tbl, n_rows, n_cols)
```

### 14.17 Responsibilities / RACI Matrix

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "ROLES & RESPONSIBILITIES")
set_ph(slide, 1, "RACI matrix for the implementation")

headers = ["Activity", "Project Lead", "Architect", "Data Eng", "Client PM"]
rows = [
    ["Architecture Design", "A", "R", "C", "I"],
    ["Data Migration", "A", "C", "R", "I"],
    ["Testing & QA", "I", "C", "R", "A"],
    ["Go-Live Decision", "R", "C", "I", "A"],
    ["Training", "A", "R", "C", "I"],
]
# RACI fill + text pairs (light fills → DK1, dark fills → WHITE)
raci_styles = {
    "R": (SF_BLUE, WHITE), "A": (DK2, WHITE),
    "C": (DK2, WHITE), "I": (BODY_GREY, WHITE),
}
n_cols = len(headers); n_rows = len(rows) + 1
tbl_shape = slide.shapes.add_table(
    n_rows, n_cols,
    Inches(0.40), Inches(1.30), Inches(9.10), Inches(0.38 * n_rows))
tbl = tbl_shape.table

for ci, h in enumerate(headers):
    cell = tbl.cell(0, ci)
    cell.text = h
    cell.fill.solid(); cell.fill.fore_color.rgb = DK2
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(10); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER

for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri + 1, ci)
        cell.text = val
        if ci == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.bold = True; p.font.size = Pt(10)
                p.font.color.rgb = DK1; p.font.name = "Arial"
        else:
            fill_c, txt_c = raci_styles.get(val, (LIGHT_BG, DK1))
            cell.fill.solid(); cell.fill.fore_color.rgb = fill_c
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11); p.font.bold = True
                p.font.color.rgb = txt_c; p.font.name = "Arial"
                p.alignment = PP_ALIGN.CENTER

set_table_borders(tbl, n_rows, n_cols)
```

### 14.18 Chevron Process Flow

Connected chevron shapes instead of boxes — instantly reads as a "process".
More visually dynamic than rectangles.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "THE JOURNEY TO PRODUCTION AI")
set_ph(slide, 1, "A four-stage methodology that transforms raw ambition into measurable outcomes")

stages = [
    ("DISCOVER", "Identify high-value\nuse cases & data\nreadiness", SF_BLUE),
    ("DESIGN", "Architect the target\nstate & define\nsuccess metrics", DK2),
    ("BUILD", "Develop, test, and\nvalidate in a\ncontrolled pilot", SF_BLUE),
    ("SCALE", "Roll out enterprise-\nwide with monitoring\n& feedback loops", DK2),
]
n = len(stages)
chev_w = 2.30; overlap = 0.20  # chevrons overlap slightly for connected look
total_w = chev_w * n - overlap * (n - 1)
x_start = (10.0 - total_w) / 2  # centre on slide

for i, (label, desc, color) in enumerate(stages):
    x = x_start + i * (chev_w - overlap)
    # Step number circle (below subtitle safe zone at 1.12")
    circ = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x + chev_w/2 - 0.15), Inches(1.22), Inches(0.30), Inches(0.30))
    circ.fill.solid(); circ.fill.fore_color.rgb = color
    circ.line.fill.background()
    tf = circ.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = str(i + 1)
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Chevron shape (starts after circle with 0.05" gap)
    chev = slide.shapes.add_shape(
        MSO_SHAPE.CHEVRON,
        Inches(x), Inches(1.57), Inches(chev_w), Inches(0.70))
    chev.fill.solid(); chev.fill.fore_color.rgb = color
    chev.line.fill.background()
    tf = chev.text_frame; tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY safety net
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(11); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Description below chevron
    d_box = slide.shapes.add_textbox(
        Inches(x + 0.15), Inches(2.40), Inches(chev_w - 0.30), Inches(0.90))
    d_box.text_frame.word_wrap = True
    p = d_box.text_frame.paragraphs[0]; p.text = desc
    p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 14.19 Milestone Timeline

Horizontal line with circle milestones — elegant for project timelines, release
cadences, or historical progression. Completely different visual from box grids.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CHARTING THE COURSE AHEAD")
set_ph(slide, 1, "Key milestones from kickoff to full production deployment")

milestones = [
    ("WEEK 1-2", "Discovery &\nRequirements", "Stakeholder interviews,\ndata audit, success\ncriteria defined"),
    ("WEEK 3-4", "Architecture\n& Design", "Target state blueprint,\nsecurity review,\ncost model"),
    ("WEEK 5-8", "Build &\nPilot", "Core pipelines live,\nCortex AI functions\nvalidated in staging"),
    ("WEEK 9-10", "UAT &\nOptimise", "Performance tuning,\nuser acceptance,\nrunbook finalised"),
    ("WEEK 11-12", "Go-Live &\nHandover", "Production cutover,\ntraining delivered,\nsupport transition"),
]
n = len(milestones)
line_left = 0.70; line_right = 9.30
line_y = 2.60; dot_r = 0.14
spacing = (line_right - line_left) / (n - 1)

# Horizontal timeline line
line = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(line_left), Inches(line_y), Inches(line_right - line_left), Inches(0.04))
line.fill.solid(); line.fill.fore_color.rgb = BORDER
line.line.fill.background()

for i, (time, title, desc) in enumerate(milestones):
    cx = line_left + i * spacing  # centre x of this milestone
    color = SF_BLUE if i % 2 == 0 else DK2

    # Milestone dot
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(cx - dot_r), Inches(line_y - dot_r + 0.02),
        Inches(dot_r * 2), Inches(dot_r * 2))
    dot.fill.solid(); dot.fill.fore_color.rgb = color
    dot.line.fill.background()

    # Time label (ABOVE the line) — use DK2 for all text (SF_BLUE not allowed below 28pt)
    t_box = slide.shapes.add_textbox(
        Inches(cx - 0.60), Inches(1.40), Inches(1.20), Inches(0.25))
    p = t_box.text_frame.paragraphs[0]; p.text = time
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Title (ABOVE the line, below time)
    ti_box = slide.shapes.add_textbox(
        Inches(cx - 0.70), Inches(1.65), Inches(1.40), Inches(0.80))
    ti_box.text_frame.word_wrap = True
    p = ti_box.text_frame.paragraphs[0]; p.text = title
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = DK1; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Description (BELOW the line)
    d_box = slide.shapes.add_textbox(
        Inches(cx - 0.70), Inches(2.90), Inches(1.40), Inches(1.00))
    d_box.text_frame.word_wrap = True
    p = d_box.text_frame.paragraphs[0]; p.text = desc
    p.font.size = Pt(8); p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 14.20 Hub & Spoke Diagram

Central concept surrounded by related elements — perfect for capability
overviews, ecosystem maps, or "what makes up X" slides.

```python
import math

slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "THE CORTEX AI ECOSYSTEM")
set_ph(slide, 1, "Six interconnected capabilities powering intelligent automation across the platform")

hub_label = "CORTEX\nAI"
spokes = [
    ("LLM\nFunctions", SF_BLUE),
    ("Cortex\nSearch", DK2),
    ("Cortex\nAnalyst", SF_BLUE),
    ("Fine-\nTuning", DK2),
    ("Cortex\nAgents", SF_BLUE),
    ("Document\nAI", DK2),
]

# Centre hub — positioned to keep ALL spokes within safe zone (1.30"–4.70" vertically)
# Hub centre at 3.10" with orbit_r=1.40 means spokes range from 1.70" to 4.50" ✓
hub_cx, hub_cy = 4.90, 3.10; hub_r = 0.50
# ✅ Use add_shape_text() — auto-inserts \n for narrow shapes, enforces all brand rules
add_shape_text(slide, MSO_SHAPE.OVAL,
               hub_cx - hub_r, hub_cy - hub_r, hub_r * 2, hub_r * 2,
               hub_label, DK2, WHITE, font_size=11, bold=True)

# Spoke elements arranged in a circle
# ⚠ SAFE ZONE: spoke tops must be ≥ 1.30", spoke bottoms must be ≤ 4.70"
# With hub_cy=3.10, orbit_r=1.40, spoke_r=0.40:
#   Top spoke:    sy = 3.10 - 1.40 = 1.70  → top = 1.70 - 0.40 = 1.30" ✓
#   Bottom spoke: sy = 3.10 + 1.40 = 4.50  → bot = 4.50 + 0.40 = 4.90" ✓
n = len(spokes); spoke_r = 0.40; orbit_r = 1.40
for i, (label, color) in enumerate(spokes):
    angle = (2 * math.pi * i / n) - math.pi / 2  # start from top
    sx = hub_cx + orbit_r * math.cos(angle)
    sy = hub_cy + orbit_r * math.sin(angle)
    
    # Clamp to safe zone (prevent header/footer overlap)
    sy = max(1.30 + spoke_r, min(4.70 - spoke_r, sy))

    # Connector line: small dot between hub and spoke for visual link
    mid_x = hub_cx + (orbit_r * 0.55) * math.cos(angle)
    mid_y = hub_cy + (orbit_r * 0.55) * math.sin(angle)
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(mid_x - 0.04), Inches(mid_y - 0.04),
        Inches(0.08), Inches(0.08))
    dot.fill.solid(); dot.fill.fore_color.rgb = BORDER
    dot.line.fill.background()

    # ✅ Spoke circle via add_shape_text() — auto-inserts \n if label has spaces
    # Even "Cortex Search" becomes "Cortex\nSearch" automatically for ≤2" shapes
    add_shape_text(slide, MSO_SHAPE.OVAL,
                   sx - spoke_r, sy - spoke_r, spoke_r * 2, spoke_r * 2,
                   label, color, WHITE, font_size=9, bold=True)
```

### 14.21 Pyramid / Layered Hierarchy

Stacked trapezoids that narrow toward the top — perfect for priority layers,
maturity models, or strategic hierarchy (e.g. vision → strategy → execution).

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "THE STRATEGIC HIERARCHY")
set_ph(slide, 1, "Building from operational foundation to transformational vision")

layers = [
    ("VISION", "Autonomous, AI-first enterprise intelligence", SF_BLUE),
    ("STRATEGY", "Platform modernisation roadmap with measurable milestones", DK2),
    ("CAPABILITIES", "Cortex AI, Snowpipe, Dynamic Tables, Marketplace sharing", SF_BLUE),
    ("FOUNDATION", "Governed data platform with RBAC, masking, and audit trails", DK2),
]
n = len(layers)
max_w = 8.50; min_w = 3.00; layer_h = 0.70; gap = 0.08
centre_x = 5.00  # slide centre

for i, (label, desc, color) in enumerate(layers):
    # i=0 (VISION) is narrowest at top, i=n-1 (FOUNDATION) is widest at bottom
    w = min_w + (max_w - min_w) * (i / (n - 1)) if n > 1 else max_w
    x = centre_x - w / 2
    y = 1.40 + i * (layer_h + gap)  # VISION at top, FOUNDATION at bottom

    # Layer shape (use PENTAGON for slight arrow-up feel, or RECTANGLE)
    lyr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(layer_h))
    lyr.fill.solid(); lyr.fill.fore_color.rgb = color
    lyr.line.fill.background()
    tf = lyr.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Bold label + lighter description on same line
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = f"{label}:  "
    r1.font.size = Pt(10); r1.font.bold = True
    r1.font.color.rgb = WHITE; r1.font.name = "Arial"
    r2 = p.add_run(); r2.text = desc
    r2.font.size = Pt(9); r2.font.color.rgb = WHITE; r2.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 14.22 Funnel Diagram

Progressively narrower stages — classic for conversion pipelines, qualification
processes, or progressive filtering. Each stage is a centred trapezoid.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "FROM AMBITION TO IMPACT")
set_ph(slide, 1, "Progressive qualification narrows 100 ideas to the 5 that transform the business")

stages = [
    ("IDEATION", "100+ AI use cases identified across all business units", 8.00, SF_BLUE),
    ("ASSESSMENT", "Top 30 scored on feasibility, data readiness, and ROI", 6.40, DK2),
    ("PILOT", "8 high-confidence candidates validated in sandbox", 4.80, SF_BLUE),
    ("PRODUCTION", "5 proven solutions deployed enterprise-wide", 3.20, DK2),
]
n = len(stages)
stage_h = 0.68; gap = 0.06
centre_x = 5.00

for i, (label, desc, w, color) in enumerate(stages):
    x = centre_x - w / 2
    y = 1.35 + i * (stage_h + gap)

    stg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(stage_h))
    stg.fill.solid(); stg.fill.fore_color.rgb = color
    stg.line.fill.background()
    tf = stg.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = f"{label}   "
    r1.font.size = Pt(11); r1.font.bold = True
    r1.font.color.rgb = WHITE; r1.font.name = "Arial"
    r2 = p.add_run(); r2.text = desc
    r2.font.size = Pt(9); r2.font.color.rgb = WHITE; r2.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Count badge on left edge
    badge = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x - 0.20), Inches(y + stage_h/2 - 0.18), Inches(0.36), Inches(0.36))
    badge.fill.solid(); badge.fill.fore_color.rgb = WHITE
    badge.line.color.rgb = color; badge.line.width = Pt(1.5)
    tf = badge.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    count = ["100+", "30", "8", "5"][i]
    p = tf.paragraphs[0]; p.text = count
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 14.23 Hexagon Feature Grid

Hexagons arranged in a honeycomb-style grid — instantly differentiates from box
layouts. Ideal for capability maps, feature overviews, or technology stacks.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "THE BUILDING BLOCKS OF INTELLIGENCE")
set_ph(slide, 1, "Six core platform capabilities that interlock to deliver autonomous data operations")

features = [
    ("Cortex\nAI", "LLM inference\nat scale", SF_BLUE),
    ("Cortex\nSearch", "Hybrid semantic\nretrieval", DK2),
    ("Cortex\nAnalyst", "Conversational\nBI on your data", SF_BLUE),
    ("Dynamic\nTables", "Declarative\ndata pipelines", DK2),
    ("Snowpipe\nStreaming", "Sub-second\ningestion", SF_BLUE),
    ("Data\nSharing", "Zero-copy\ncross-org access", DK2),
]

hex_w = 1.60; hex_h = 1.40
positions = [
    # Row 1 (3 hexagons)
    (1.10, 1.30), (3.25, 1.30), (5.40, 1.30),
    # Row 2 (3 hexagons, offset right by half-width)
    (2.18, 2.60), (4.33, 2.60), (6.48, 2.60),
]

for i, ((x, y), (label, desc, color)) in enumerate(zip(positions, features)):
    # Hexagon shape
    hx = slide.shapes.add_shape(
        MSO_SHAPE.HEXAGON,
        Inches(x), Inches(y), Inches(hex_w), Inches(hex_h))
    hx.fill.solid(); hx.fill.fore_color.rgb = color
    hx.line.fill.background()
    tf = hx.text_frame; tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY safety net
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Label
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = label
    r.font.size = Pt(10); r.font.bold = True
    r.font.color.rgb = WHITE; r.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
    # Description below label
    p2 = tf.add_paragraph()
    r2 = p2.add_run(); r2.text = desc
    r2.font.size = Pt(8); r2.font.color.rgb = WHITE; r2.font.name = "Arial"
    p2.alignment = PP_ALIGN.CENTER
```

### 14.24 Arrow Ribbon Roadmap

Large horizontal arrow shapes as phases — each arrow points into the next,
creating a strong visual flow. More dynamic than the box-based roadmap (14.8).

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "STAGING THE ASCENT")
set_ph(slide, 1, "A phased deployment strategy from first signal to full operational autonomy")

phases = [
    ("PHASE 1", "Foundation", "Weeks 1-4", [
        "Data platform assessment",
        "Security & governance design",
        "Stakeholder alignment",
    ], SF_BLUE, WHITE),
    ("PHASE 2", "Build", "Weeks 5-10", [
        "Pipeline development",
        "Cortex AI integration",
        "UAT & performance testing",
    ], DK2, WHITE),
    ("PHASE 3", "Scale", "Weeks 11-16", [
        "Enterprise rollout",
        "Training & enablement",
        "Operational monitoring",
    ], SF_BLUE, WHITE),
]
n = len(phases)
arrow_w = 3.10; arrow_h = 0.65; overlap = 0.15
total_w = arrow_w * n - overlap * (n - 1)
x_start = (10.0 - total_w) / 2

for i, (phase, title, timing, items, bg, fg) in enumerate(phases):
    x = x_start + i * (arrow_w - overlap)

    # Arrow-like chevron shape (points right, overlaps create connected flow)
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.CHEVRON,
        Inches(x), Inches(1.35), Inches(arrow_w), Inches(arrow_h))
    arrow.fill.solid(); arrow.fill.fore_color.rgb = bg
    arrow.line.fill.background()
    tf = arrow.text_frame; tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY safety net
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = f"{phase}: {title}"
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = fg; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Timing label below arrow
    t_box = slide.shapes.add_textbox(
        Inches(x + 0.20), Inches(2.05), Inches(arrow_w - 0.40), Inches(0.20))
    p = t_box.text_frame.paragraphs[0]; p.text = timing
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Activity items below
    for j, item in enumerate(items):
        b = slide.shapes.add_textbox(
            Inches(x + 0.20), Inches(2.35 + j * 0.35),
            Inches(arrow_w - 0.40), Inches(0.30))
        b.text_frame.word_wrap = True
        p = b.text_frame.paragraphs[0]; p.text = f"• {item}"
        p.font.size = Pt(9); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### 14.25 Icon Circle Grid (Large Numbers in Circles)

Large coloured circles with big numbers/icons inside and labels below — much
more visually striking than plain textboxes for key metrics.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "THE NUMBERS THAT MATTER")
set_ph(slide, 1, "Four proof points that quantify the transformation impact")

metrics = [
    ("10x", "Faster\nQuery Speed", "From 4 hours to\n23 seconds on\ncomplex analytics", SF_BLUE),
    ("500+", "Self-Service\nUsers", "Analysts empowered\nto query without\nengineering support", DK2),
    ("$2.3M", "Annual\nSavings", "Infrastructure costs\neliminated through\nplatform consolidation", SF_BLUE),
    ("99.9%", "Platform\nUptime", "Enterprise-grade\nreliability with\nauto-scaling", DK2),
]
n = len(metrics); circ_r = 0.55
gap = (9.10 - n * circ_r * 2) / (n + 1)

for i, (number, label, desc, color) in enumerate(metrics):
    cx = 0.40 + gap * (i + 1) + circ_r * (2 * i + 1)

    # Large circle with number
    circ = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(cx - circ_r), Inches(1.40),
        Inches(circ_r * 2), Inches(circ_r * 2))
    circ.fill.solid(); circ.fill.fore_color.rgb = color
    circ.line.fill.background()
    tf = circ.text_frame; tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY safety net
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = number
    p.font.size = Pt(20); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Label below circle
    l_box = slide.shapes.add_textbox(
        Inches(cx - 0.85), Inches(2.60), Inches(1.70), Inches(0.45))
    l_box.text_frame.word_wrap = True
    p = l_box.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = DK1; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Description
    d_box = slide.shapes.add_textbox(
        Inches(cx - 0.85), Inches(3.05), Inches(1.70), Inches(0.90))
    d_box.text_frame.word_wrap = True
    p = d_box.text_frame.paragraphs[0]; p.text = desc
    p.font.size = Pt(8); p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 14.26 Maturity Progression Bar

Horizontal graduated bars showing progression from current to target state.
Each bar fills proportionally with accent colour. Great for readiness assessments.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "PLATFORM MATURITY ASSESSMENT")
set_ph(slide, 1, "Current capability scores and target state across five critical dimensions")

dimensions = [
    ("Data Ingestion", 0.35, 0.90, "Batch ETL → Real-time Snowpipe"),
    ("Analytics & AI", 0.20, 0.85, "SQL reports → Cortex AI conversational"),
    ("Governance", 0.50, 0.95, "Manual RBAC → Dynamic masking & tags"),
    ("Data Sharing", 0.15, 0.80, "File exports → Snowflake Marketplace"),
    ("Cost Management", 0.40, 0.75, "Monthly review → Per-query attribution"),
]
bar_left = 2.80; bar_w = 5.80; bar_h = 0.35; y_start = 1.40; row_gap = 0.55

for i, (label, current, target, desc) in enumerate(dimensions):
    y = y_start + i * row_gap

    # Dimension label (left side)
    lbl = slide.shapes.add_textbox(
        Inches(0.40), Inches(y), Inches(2.30), Inches(bar_h))
    p = lbl.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = DK1; p.font.name = "Arial"

    # Background bar (full width, light grey)
    bg_bar = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(bar_left), Inches(y), Inches(bar_w), Inches(bar_h))
    bg_bar.fill.solid(); bg_bar.fill.fore_color.rgb = LIGHT_BG
    bg_bar.line.color.rgb = BORDER; bg_bar.line.width = Pt(0.5)

    # Current state fill (solid colour)
    if current > 0:
        cur_bar = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(bar_left), Inches(y),
            Inches(bar_w * current), Inches(bar_h))
        cur_bar.fill.solid(); cur_bar.fill.fore_color.rgb = SF_BLUE
        cur_bar.line.fill.background()
        tf = cur_bar.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.text = f"{int(current*100)}%"
        p.font.size = Pt(8); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER

    # Target marker (thin vertical line)
    t_x = bar_left + bar_w * target
    marker = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(t_x), Inches(y - 0.05), Inches(0.03), Inches(bar_h + 0.10))
    marker.fill.solid(); marker.fill.fore_color.rgb = DK2
    marker.line.fill.background()

    # Target label
    t_lbl = slide.shapes.add_textbox(
        Inches(t_x - 0.25), Inches(y - 0.22), Inches(0.50), Inches(0.18))
    p = t_lbl.text_frame.paragraphs[0]; p.text = f"{int(target*100)}%"
    p.font.size = Pt(7); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Legend
for j, (text, color) in enumerate([("Current", SF_BLUE), ("Target", DK2)]):
    lx = 7.50 + j * 1.20
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(lx), Inches(4.45), Inches(0.12), Inches(0.12))
    dot.fill.solid(); dot.fill.fore_color.rgb = color; dot.line.fill.background()
    ll = slide.shapes.add_textbox(Inches(lx + 0.18), Inches(4.40), Inches(0.80), Inches(0.20))
    p = ll.text_frame.paragraphs[0]; p.text = text
    p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### 14.27 Diamond Decision Tree

Diamond shapes for decision points with branching paths — ideal for
governance flows, approval processes, or "if/then" logic.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "WHEN TO USE CROSS-REGION INFERENCE")
set_ph(slide, 1, "A decision framework for determining the right inference strategy")

# Central decision diamond
diamond = slide.shapes.add_shape(
    MSO_SHAPE.DIAMOND,
    Inches(3.80), Inches(1.40), Inches(2.40), Inches(1.20))
diamond.fill.solid(); diamond.fill.fore_color.rgb = DK2
diamond.line.fill.background()
tf = diamond.text_frame; tf.word_wrap = True
tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY safety net
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.text = "Model available\nin your region?"
p.font.size = Pt(10); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

# YES path (left)
yes_arrow = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(2.20), Inches(1.97), Inches(1.60), Inches(0.04))
yes_arrow.fill.solid(); yes_arrow.fill.fore_color.rgb = SF_BLUE
yes_arrow.line.fill.background()
yes_lbl = slide.shapes.add_textbox(Inches(2.50), Inches(1.75), Inches(1.00), Inches(0.20))
p = yes_lbl.text_frame.paragraphs[0]; p.text = "YES"
p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = DK2; p.font.name = "Arial"

yes_box = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.40), Inches(1.60), Inches(1.80), Inches(0.80))
yes_box.fill.solid(); yes_box.fill.fore_color.rgb = SF_BLUE
yes_box.line.fill.background()
tf = yes_box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.text = "Use local\ninference"
p.font.size = Pt(10); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

# NO path (right)
no_arrow = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(6.20), Inches(1.97), Inches(1.60), Inches(0.04))
no_arrow.fill.solid(); no_arrow.fill.fore_color.rgb = DK2
no_arrow.line.fill.background()
no_lbl = slide.shapes.add_textbox(Inches(6.40), Inches(1.75), Inches(1.00), Inches(0.20))
p = no_lbl.text_frame.paragraphs[0]; p.text = "NO"
p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = DK2; p.font.name = "Arial"

# Second decision diamond
diamond2 = slide.shapes.add_shape(
    MSO_SHAPE.DIAMOND,
    Inches(7.40), Inches(1.40), Inches(2.20), Inches(1.20))
diamond2.fill.solid(); diamond2.fill.fore_color.rgb = SF_BLUE
diamond2.line.fill.background()
tf = diamond2.text_frame; tf.word_wrap = True
tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # ← MANDATORY safety net
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.text = "Latency\ntolerant?"
p.font.size = Pt(10); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

# Outcome boxes below
outcomes = [
    (0.40, "Optimal Path:\nLocal inference\nfor minimum latency", SF_BLUE),
    (3.60, "Enable Cross-Region:\nALTER ACCOUNT SET\nCORTEX_ENABLED_\nCROSS_REGION = 'ANY'", DK2),
    (7.00, "Wait for Model:\nMonitor region\navailability for\nfuture deployment", BODY_GREY),
]
for ox, text, color in outcomes:
    ob = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(ox), Inches(3.20), Inches(2.80), Inches(1.30))
    ob.fill.solid(); ob.fill.fore_color.rgb = color
    ob.line.fill.background()
    tf = ob.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(9); p.font.bold = True
    fg = WHITE if color != BODY_GREY else WHITE
    p.font.color.rgb = fg; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 14.28 Maturity / Capability Assessment Grid

Full matrix with row labels (capability areas) on the left and maturity stages across
the top (e.g., Basic → Emerging → Leading). Each cell contains descriptive text.
Best for digital maturity assessments, capability audits, or readiness evaluations.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "PRICING CAPABILITY MATURITY")
set_ph(slide, 1, "Assessing current state across six dimensions")

stages = ["Basic", "Emerging", "Leading"]
stage_colors = [BODY_GREY, SF_BLUE, DK2]

rows = [
    ("Strategy",     ["Cost-plus pricing with\nincremental adjustments",
                      "Discrete price strategies\nper product line",
                      "Connected price strategy\nacross all channels"]),
    ("Analytics",    ["Ad-hoc tracking via\nspreadsheets only",
                      "Syndicated data with\nbasic dashboards",
                      "Predictive models with\nreal-time POS data"]),
    ("Technology",   ["Manual processes with\nlegacy ERP only",
                      "Cloud analytics with\nbasic integrations",
                      "AI-driven platform with\nautomated workflows"]),
    ("Organization", ["Siloed teams with\nno shared goals",
                      "Dotted-line reporting\nwith shared KPIs",
                      "Unified revenue team\nwith joint P&L"]),
    ("Governance",   ["Informal approvals\nwith no audit trail",
                      "Quarterly reviews with\nbasic compliance",
                      "Real-time policy engine\nwith full audit trail"]),
    ("Compliance",   ["Reactive risk response\nafter incidents",
                      "Proactive monitoring\nwith periodic audits",
                      "Continuous compliance\nwith automated alerts"]),
]

n_rows = len(rows)
n_cols = len(stages)
row_h = 0.55
col_w = 2.60
label_w = 1.70
x0 = 0.50                     # left edge of row labels
cx0 = x0 + label_w + 0.10     # left edge of first data column
y0 = 1.40                     # top of first row

# Stage column headers
for j, (stage, sc) in enumerate(zip(stages, stage_colors)):
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx0 + j * (col_w + 0.10)), Inches(y0 - 0.35),
        Inches(col_w), Inches(0.28))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = sc
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = stage
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Data rows
for i, (label, cells) in enumerate(rows):
    y = y0 + i * (row_h + 0.08)
    # Row label (coloured bar)
    lbl = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x0), Inches(y), Inches(label_w), Inches(row_h))
    lbl.fill.solid(); lbl.fill.fore_color.rgb = DK2
    lbl.line.fill.background()
    tf = lbl.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Data cells
    for j, cell_text in enumerate(cells):
        bg = LIGHT_BG if i % 2 == 0 else WHITE
        cell = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cx0 + j * (col_w + 0.10)), Inches(y),
            Inches(col_w), Inches(row_h))
        cell.fill.solid(); cell.fill.fore_color.rgb = bg
        cell.line.color.rgb = GRID_LINE
        cell.line.width = Pt(0.5)
        tf = cell.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.text = cell_text
        p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT
```

### 14.29 Swimlane Roadmap

Horizontal timeline with multiple swimlane rows (workstreams). Each row has a label
bar on the left and phase bars stretching across the timeline. Milestones appear as
small circles on phase boundaries. Best for multi-workstream implementation plans.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "IMPLEMENTATION ROADMAP")
set_ph(slide, 1, "Three workstreams across four quarters")

quarters = ["Q1 FY26", "Q2 FY26", "Q3 FY26", "Q4 FY26"]
n_q = len(quarters)
lane_x0 = 2.00           # left edge of timeline area
lane_w = 7.20             # total width of timeline area
q_w = lane_w / n_q        # width per quarter
lane_y0 = 1.40            # top of first header
lane_h = 0.90             # height per swimlane row
label_w = 1.50            # width of row labels

# Quarter headers
for qi, q_name in enumerate(quarters):
    hdr = slide.shapes.add_textbox(
        Inches(lane_x0 + qi * q_w), Inches(lane_y0),
        Inches(q_w), Inches(0.25))
    hdr.text_frame.word_wrap = True
    p = hdr.text_frame.paragraphs[0]; p.text = q_name
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Horizontal grid lines under headers
for qi in range(n_q + 1):
    vline = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(lane_x0 + qi * q_w), Inches(lane_y0 + 0.28),
        Inches(0.01), Inches(3 * (lane_h + 0.10)))
    vline.fill.solid(); vline.fill.fore_color.rgb = GRID_LINE
    vline.line.fill.background()

# Swimlanes: (label, [(start_q, span_q, text, color), ...], milestones)
swimlanes = [
    ("Data Platform", [
        (0, 2, "Foundation: Ingest &\nmodel core data", SF_BLUE),
        (2, 2, "Scale: Add streaming\n& real-time pipelines", TEAL),
    ], [2]),  # milestone at Q2/Q3 boundary
    ("AI / ML", [
        (1, 2, "Build: Train models\n& deploy Cortex AI", DK2),
        (3, 1, "Optimize: A/B test\n& refine models", BODY_GREY),
    ], [3]),
    ("Adoption", [
        (0, 1, "Plan: Stakeholder\nalignment", TEAL),
        (1, 3, "Execute: Training, rollout,\nchange management", SF_BLUE),
    ], [1, 3]),
]

for li, (label, phases, milestones) in enumerate(swimlanes):
    y = lane_y0 + 0.35 + li * (lane_h + 0.10)

    # Row label
    lbl = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.40), Inches(y), Inches(label_w), Inches(lane_h))
    lbl.fill.solid(); lbl.fill.fore_color.rgb = DK2
    lbl.line.fill.background()
    tf = lbl.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Phase bars
    for (sq, span, txt, clr) in phases:
        bar = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(lane_x0 + sq * q_w + 0.05), Inches(y + 0.08),
            Inches(span * q_w - 0.10), Inches(lane_h - 0.16))
        bar.fill.solid(); bar.fill.fore_color.rgb = clr
        bar.line.fill.background()
        tf = bar.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.text = txt
        p.font.size = Pt(8); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER

    # Milestone dots
    for mq in milestones:
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(lane_x0 + mq * q_w - 0.06), Inches(y + lane_h / 2 - 0.06),
            Inches(0.12), Inches(0.12))
        dot.fill.solid(); dot.fill.fore_color.rgb = WHITE
        dot.line.color.rgb = DK2; dot.line.width = Pt(1.5)
```

### 14.30 Milestone Scatter Planning Grid

Milestone events positioned across a timeline canvas at varying Y positions, creating
an organic "map" of activities. Good for 30/60/90-day plans, event-based planning,
or transition roadmaps where activities are not strictly sequential.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "90-DAY TRANSITION PLAN")
set_ph(slide, 1, "Key milestones from contract signing to full operation")

# Timeline baseline
baseline_y = 3.00
line = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0.60), Inches(baseline_y), Inches(8.80), Inches(0.02))
line.fill.solid(); line.fill.fore_color.rgb = BODY_GREY
line.line.fill.background()

# Day markers on the baseline
day_markers = [("Day 1", 0.60), ("Day 30", 3.30), ("Day 60", 5.90), ("Day 90", 8.60)]
for label, x in day_markers:
    # Vertical tick
    tick = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x + 0.20), Inches(baseline_y - 0.10), Inches(0.02), Inches(0.22))
    tick.fill.solid(); tick.fill.fore_color.rgb = DK2
    tick.line.fill.background()
    # Label
    lbl = slide.shapes.add_textbox(Inches(x), Inches(baseline_y + 0.15), Inches(0.80), Inches(0.22))
    p = lbl.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(8); p.font.bold = True; p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Milestone events: (x, y, text, color) — scattered above and below baseline
events = [
    (0.50,  1.50, "Contract\nSigned", SF_BLUE),
    (1.50,  2.00, "Governance\nKickoff", DK2),
    (2.50,  1.50, "Joint Transition\nPlanning Session", SF_BLUE),
    (3.50,  2.10, "Initial Joint\nPlan Complete", DK2),
    (4.50,  1.40, "Blueprint\nReview", SF_BLUE),
    (5.40,  2.10, "Capability\nAssessment Done", BODY_GREY),
    (6.50,  1.50, "Draft Plan\nv2 Review", DK2),
    (7.80,  1.80, "Final Plan\nApproved", SF_BLUE),
    (1.00,  3.60, "Public\nAnnouncement", TEAL),
    (3.00,  3.80, "Status Report\nto Stakeholders", BODY_GREY),
    (5.50,  3.60, "In-Flight\nProject Review", TEAL),
    (7.50,  3.60, "Go / No-Go\nDecision", DK2),
]

for ex, ey, txt, clr in events:
    # Event card
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(ex), Inches(ey), Inches(1.30), Inches(0.65))
    card.fill.solid(); card.fill.fore_color.rgb = clr
    card.line.fill.background()
    tf = card.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = txt
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Connector line to baseline
    cx = ex + 0.65  # center of card
    cy_card = ey + 0.65 if ey < baseline_y else ey
    cy_base = baseline_y if ey < baseline_y else baseline_y + 0.02
    conn = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(cx - 0.005), Inches(min(cy_card, cy_base)),
        Inches(0.01), Inches(abs(cy_card - cy_base)))
    conn.fill.solid(); conn.fill.fore_color.rgb = CONN_LINE
    conn.line.fill.background()
```

### 14.31 Grouped Category Menu

Rows of labelled items with left-side curly braces grouping related rows, and column
headers across the top. Ideal for pricing tiers, service menus, discount structures,
or any "menu of options" with logical groupings.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "SERVICE TIER MENU")
set_ph(slide, 1, "Select the capabilities that match your maturity stage")

tiers = ["Essentials", "Professional", "Enterprise"]
tier_colors = [BODY_GREY, SF_BLUE, DK2]

# Groups: (group_label, [(item_name, [tier_values...]), ...])
groups = [
    ("Data\nFoundation", [
        ("Ingestion & ETL",    ["Batch only", "Batch + micro-batch", "Real-time streaming"]),
        ("Storage Format",     ["Managed tables", "Managed + External", "Iceberg + hybrid"]),
        ("Data Sharing",       ["Internal only", "Cross-account", "Marketplace listing"]),
    ]),
    ("AI &\nAnalytics", [
        ("Cortex AI Access",   ["—", "Standard models", "Fine-tuned + custom"]),
        ("Dashboards",         ["SQL worksheets", "Streamlit apps", "Embedded analytics"]),
    ]),
    ("Governance", [
        ("Access Control",     ["RBAC basics", "Row-level security", "Dynamic masking"]),
        ("Audit & Compliance", ["Query history", "Access history", "Full lineage"]),
    ]),
]

row_h = 0.35
col_w = 2.30
label_col_w = 1.50
x0 = 1.80                # left edge of item names
cx0 = x0 + label_col_w + 0.10  # left edge of tier columns
y0 = 1.40

# Tier headers
for j, (tier, tc) in enumerate(zip(tiers, tier_colors)):
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx0 + j * (col_w + 0.05)), Inches(y0),
        Inches(col_w), Inches(0.30))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = tc
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = tier
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

row_y = y0 + 0.40
for grp_label, items in groups:
    grp_start_y = row_y
    for item_name, tier_vals in items:
        # Item name
        nm = slide.shapes.add_textbox(
            Inches(x0), Inches(row_y), Inches(label_col_w), Inches(row_h))
        nm.text_frame.word_wrap = True
        p = nm.text_frame.paragraphs[0]; p.text = item_name
        p.font.size = Pt(8); p.font.bold = True
        p.font.color.rgb = DK1; p.font.name = "Arial"

        # Tier values
        for j, val in enumerate(tier_vals):
            cell = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cx0 + j * (col_w + 0.05)), Inches(row_y),
                Inches(col_w), Inches(row_h))
            bg = LIGHT_BG if items.index((item_name, tier_vals)) % 2 == 0 else WHITE
            cell.fill.solid(); cell.fill.fore_color.rgb = bg
            cell.line.color.rgb = GRID_LINE
            cell.line.width = Pt(0.5)
            tf = cell.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]; p.text = val
            p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"
            p.alignment = PP_ALIGN.CENTER

        row_y += row_h + 0.05
    grp_end_y = row_y - 0.05

    # Left brace (curly bracket shape)
    brace = slide.shapes.add_shape(
        MSO_SHAPE.LEFT_BRACE,
        Inches(x0 - 0.30), Inches(grp_start_y),
        Inches(0.25), Inches(grp_end_y - grp_start_y))
    brace.fill.background()
    brace.line.color.rgb = DK2; brace.line.width = Pt(1)

    # Group label
    gl = slide.shapes.add_textbox(
        Inches(0.40), Inches(grp_start_y + (grp_end_y - grp_start_y) / 2 - 0.20),
        Inches(1.20), Inches(0.40))
    gl.text_frame.word_wrap = True
    p = gl.text_frame.paragraphs[0]; p.text = grp_label
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.RIGHT

    row_y += 0.15  # gap between groups
```

### 14.32 Customer Journey Map

Columns for time horizons (Short / Medium / Long-Term) with a left sidebar for
journey phases. Touchpoint dots and scenario cards positioned at different Y levels
within each column. Best for customer experience design, onboarding flows, or
lifecycle mapping.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CUSTOMER JOURNEY MAP")
set_ph(slide, 1, "From first contact to long-term advocacy")

horizons = ["Short-Term\n(0-30 days)", "Medium-Term\n(30-90 days)", "Long-Term\n(90+ days)"]
phases = ["Awareness", "Activation", "Retention", "Advocacy"]

sidebar_w = 1.50
col_w = 2.50
x0 = sidebar_w + 0.20
y0 = 1.40
total_h = 3.60

# Sidebar (journey phases)
phase_h = total_h / len(phases)
for pi, phase in enumerate(phases):
    py = y0 + pi * phase_h
    pb = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.40), Inches(py + 0.05), Inches(sidebar_w), Inches(phase_h - 0.10))
    pb.fill.solid(); pb.fill.fore_color.rgb = DK2 if pi % 2 == 0 else SF_BLUE
    pb.line.fill.background()
    tf = pb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = phase
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Column headers
for ci, horizon in enumerate(horizons):
    hx = x0 + ci * (col_w + 0.15)
    hdr = slide.shapes.add_textbox(Inches(hx), Inches(y0 - 0.35), Inches(col_w), Inches(0.30))
    hdr.text_frame.word_wrap = True
    p = hdr.text_frame.paragraphs[0]; p.text = horizon
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Column background bands
for ci in range(len(horizons)):
    hx = x0 + ci * (col_w + 0.15)
    band = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(hx), Inches(y0), Inches(col_w), Inches(total_h))
    band.fill.solid(); band.fill.fore_color.rgb = LIGHT_BG if ci % 2 == 0 else WHITE
    band.line.fill.background()

# Touchpoint cards: (col_idx, phase_idx, title, description)
touchpoints = [
    (0, 0, "Discover", "Prospect finds Snowflake\nvia event or referral"),
    (0, 1, "First POC", "Hands-on trial with\nsample datasets"),
    (1, 1, "Onboarding", "Production migration\nwith success team"),
    (1, 2, "Expand Use Cases", "Add AI/ML workloads\nand new teams"),
    (2, 2, "Platform Standard", "Enterprise-wide\ndata platform"),
    (2, 3, "Champion", "Customer presents at\nSnowflake Summit"),
]

card_w = 2.20
card_h = 0.60
for ci, pi, title, desc in touchpoints:
    cx = x0 + ci * (col_w + 0.15) + (col_w - card_w) / 2
    cy = y0 + pi * phase_h + (phase_h - card_h) / 2

    # Touchpoint dot
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(cx - 0.12), Inches(cy + card_h / 2 - 0.05),
        Inches(0.10), Inches(0.10))
    dot.fill.solid(); dot.fill.fore_color.rgb = SF_BLUE
    dot.line.fill.background()

    # Card
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx), Inches(cy), Inches(card_w), Inches(card_h))
    card.fill.solid(); card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = SF_BLUE; card.line.width = Pt(1)
    tf = card.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Title run
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = SF_BLUE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
    # Description
    p2 = tf.add_paragraph(); p2.text = desc
    p2.font.size = Pt(7); p2.font.color.rgb = DK1; p2.font.name = "Arial"
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(2)
```

### 14.33 Dual-Context Comparison

Centre column of category labels, flanked by two rounded-rectangle panels (e.g.,
Current State vs. Future State). Each row compares the same dimension across both
contexts. Ideal for transformation narratives, operating model shifts, or
before-and-after organisational changes.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "COMMERCIAL OPERATING MODEL SHIFT")
set_ph(slide, 1, "Moving from contract-driven to relationship-based engagement")

left_label = "Current State"
right_label = "Future State"

categories = [
    ("Governance",     "Hierarchical structure,\ndecentralized decisions",
                       "Fluid, value-based org\nwith flexible teams"),
    ("Selling",        "Pursuit of large contracts\nwith fixed scoping",
                       "Proactive market sales\nwith tailored solutions"),
    ("Relationships",  "Contract-driven with\nquarterly reviews",
                       "Partnership model with\nfrequent engagement"),
    ("Portfolio",      "Government-shaped portfolio\nmanufactured to spec",
                       "Industry-based requirements\ncustomer-defined needs"),
    ("Customization",  "Custom dev based on\ngovernment specifications",
                       "Standard product catalog\nwith configurability"),
    ("Profitability",  "Emphasis on contract\nprofitability per deal",
                       "Emphasis on portfolio\nand business unit P&L"),
]

panel_w = 2.80
center_w = 1.70
gap = 0.15
total_w = panel_w * 2 + center_w + gap * 2
x_left = (10.0 - total_w) / 2
x_center = x_left + panel_w + gap
x_right = x_center + center_w + gap
y0 = 1.40
row_h = 0.50

# Panel headers
for (x, label, clr) in [(x_left, left_label, BODY_GREY), (x_right, right_label, SF_BLUE)]:
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y0), Inches(panel_w), Inches(0.35))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = clr
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(10); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Panel background rectangles
for x in [x_left, x_right]:
    bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y0 + 0.40), Inches(panel_w), Inches(len(categories) * (row_h + 0.06)))
    bg.fill.solid(); bg.fill.fore_color.rgb = LIGHT_BG
    bg.line.fill.background()

# Rows
for i, (cat, left_text, right_text) in enumerate(categories):
    y = y0 + 0.48 + i * (row_h + 0.06)

    # Centre category label
    cl = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x_center), Inches(y), Inches(center_w), Inches(row_h))
    cl.fill.solid(); cl.fill.fore_color.rgb = DK2
    cl.line.fill.background()
    tf = cl.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = cat
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Left cell
    lc = slide.shapes.add_textbox(
        Inches(x_left + 0.10), Inches(y), Inches(panel_w - 0.20), Inches(row_h))
    lc.text_frame.word_wrap = True
    p = lc.text_frame.paragraphs[0]; p.text = left_text
    p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"

    # Right cell
    rc = slide.shapes.add_textbox(
        Inches(x_right + 0.10), Inches(y), Inches(panel_w - 0.20), Inches(row_h))
    rc.text_frame.word_wrap = True
    p = rc.text_frame.paragraphs[0]; p.text = right_text
    p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### 14.34 Two-Horizon Split (Today vs. Tomorrow)

Slide divided into left ("Today") and right ("Tomorrow") halves, each containing
bullet-point cards with icon-style bullets. A central divider or arrow connects
the two horizons. Best for transformation narratives, capability evolution, or
strategic positioning.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "FROM COST-PLUS TO PREDICTIVE PRICING")
set_ph(slide, 1, "Why tomorrow demands a fundamentally different approach")

half_w = 4.00
gap = 0.60
x_left = 0.50
x_right = x_left + half_w + gap
y0 = 1.40

# Column headers
for (x, label, clr) in [(x_left, "2024: Why Today?", BODY_GREY),
                          (x_right, "2027: Why Tomorrow?", SF_BLUE)]:
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y0), Inches(half_w), Inches(0.35))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = clr
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(11); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

# Central arrow (triangle pointing right)
arrow = slide.shapes.add_shape(
    MSO_SHAPE.ISOSCELES_TRIANGLE,
    Inches(x_left + half_w + 0.10), Inches(2.80),
    Inches(0.40), Inches(0.30))
arrow.rotation = 90.0
arrow.fill.solid(); arrow.fill.fore_color.rgb = DK2
arrow.line.fill.background()

# Bullet cards: list of (icon_char, title, description)
left_items = [
    ("Cost-Plus Mindset", "Prices based on cost + margin\nwith incremental adjustments"),
    ("Market Leadership", "Large installed base provides\npricing power by default"),
    ("Product Portfolio", "Broad portfolio enables\nbundling strategies"),
]
right_items = [
    ("Customer Intimacy", "Digitally integrated with\ncustomer decision workflows"),
    ("Simulation Expertise", "Predictive models optimize\npricing in real-time"),
    ("Centre of Excellence", "Dedicated pricing CoE drives\nconsistent global execution"),
]

card_h = 0.70
for items, x in [(left_items, x_left), (right_items, x_right)]:
    for i, (title, desc) in enumerate(items):
        cy = y0 + 0.50 + i * (card_h + 0.15)
        # Bullet dot
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x + 0.10), Inches(cy + 0.10),
            Inches(0.20), Inches(0.20))
        dot.fill.solid()
        dot.fill.fore_color.rgb = SF_BLUE if x == x_right else DK2
        dot.line.fill.background()
        # Card text
        tb = slide.shapes.add_textbox(
            Inches(x + 0.40), Inches(cy), Inches(half_w - 0.50), Inches(card_h))
        tb.text_frame.word_wrap = True
        p = tb.text_frame.paragraphs[0]; p.text = title
        p.font.size = Pt(10); p.font.bold = True
        p.font.color.rgb = DK1; p.font.name = "Arial"
        p2 = tb.text_frame.add_paragraph(); p2.text = desc
        p2.font.size = Pt(8); p2.font.color.rgb = BODY_GREY; p2.font.name = "Arial"
        p2.space_before = Pt(2)
```

### 14.35 Stat Scatter with Categories

Four category zones across the slide, each with a header bar, a large stat number,
and supporting context text. Creates a visually rich data landscape rather than a
simple grid. Best for market data, survey highlights, or impact summaries.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CONSUMER INSIGHTS THAT MATTER")
set_ph(slide, 1, "Four forces reshaping the purchasing experience")

# Categories: (header, stat, context, x, y, header_color)
categories = [
    ("CREATE EXPERIENCES", "38%", "Increase in spend on\nexperiences by 2030 — consumers\nprefer moments over things",
     0.50, 1.40, DK2),
    ("DRIVE IMPULSE", "80%", "Of consumers shop on impulse —\nbrands discoverable at the\nmoment of need win",
     5.00, 1.40, SF_BLUE),
    ("TAILOR COMMS", ">85%", "Of mobile marketers report\nsuccess with personalised\nmessaging strategies",
     0.50, 3.20, SF_BLUE),
    ("BUILD TRUST", ">50%", "Of consumers value health,\nwellness, and sustainability\nwhen choosing brands",
     5.00, 3.20, DK2),
]

card_w = 4.30
card_h = 1.50
for header, stat, context, cx, cy, hdr_clr in categories:
    # Header bar
    hb = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx), Inches(cy), Inches(card_w), Inches(0.30))
    hb.fill.solid(); hb.fill.fore_color.rgb = hdr_clr
    hb.line.fill.background()
    tf = hb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = header
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.LEFT

    # Big stat number
    sn = slide.shapes.add_textbox(
        Inches(cx + 0.10), Inches(cy + 0.35), Inches(1.20), Inches(0.60))
    sn.text_frame.word_wrap = True
    p = sn.text_frame.paragraphs[0]; p.text = stat
    p.font.size = Pt(28); p.font.bold = True
    p.font.color.rgb = hdr_clr; p.font.name = "Arial"

    # Context text
    ct = slide.shapes.add_textbox(
        Inches(cx + 1.30), Inches(cy + 0.38), Inches(card_w - 1.50), Inches(card_h - 0.50))
    ct.text_frame.word_wrap = True
    p = ct.text_frame.paragraphs[0]; p.text = context
    p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### 14.36 Gantt Table

A PowerPoint table used as a Gantt chart — rows for workstreams, columns for weeks
or sprints. Cells are shaded to show duration. Milestone dots can be added as shapes
on top. Best for detailed project plans with specific timing.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "12-WEEK DELIVERY PLAN")
set_ph(slide, 1, "Workstream-level timeline with key milestones")

workstreams = [
    "Discovery & Assessment",
    "Data Architecture",
    "Pipeline Development",
    "AI / ML Integration",
    "Testing & Validation",
    "Rollout & Adoption",
]
n_weeks = 12
n_rows = len(workstreams) + 1  # +1 for header
n_cols = n_weeks + 1            # +1 for labels

table_left = Inches(0.40)
table_top = Inches(1.50)
table_width = Inches(9.20)
table_height = Inches(3.20)

table_shape = slide.shapes.add_table(n_rows, n_cols, table_left, table_top,
                                      table_width, table_height)
tbl = table_shape.table

# Set column widths
tbl.columns[0].width = Inches(1.60)
for c in range(1, n_cols):
    tbl.columns[c].width = Inches((9.20 - 1.60) / n_weeks)

# Header row
tbl.cell(0, 0).text = "Workstream"
for c in range(1, n_cols):
    tbl.cell(0, c).text = f"W{c}"

# Format header row
for c in range(n_cols):
    cell = tbl.cell(0, c)
    cell.fill.solid()
    cell.fill.fore_color.rgb = DK2
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.size = Pt(8)
        paragraph.font.bold = True
        paragraph.font.color.rgb = WHITE
        paragraph.font.name = "Arial"
        paragraph.alignment = PP_ALIGN.CENTER

# Gantt data: (start_week, end_week) — 1-indexed
gantt_data = [
    (1, 3),    # Discovery
    (2, 6),    # Data Architecture
    (4, 9),    # Pipeline Development
    (6, 10),   # AI/ML
    (8, 11),   # Testing
    (10, 12),  # Rollout
]
bar_colors = [SF_BLUE, DK2, SF_BLUE, TEAL, DK2, SF_BLUE]

for r, (ws_name, (start, end), clr) in enumerate(
        zip(workstreams, gantt_data, bar_colors)):
    row_idx = r + 1
    # Label cell
    label_cell = tbl.cell(row_idx, 0)
    label_cell.text = ws_name
    label_cell.fill.solid()
    label_cell.fill.fore_color.rgb = LIGHT_BG
    for paragraph in label_cell.text_frame.paragraphs:
        paragraph.font.size = Pt(8)
        paragraph.font.bold = True
        paragraph.font.color.rgb = DK1
        paragraph.font.name = "Arial"

    # Data cells — shade active weeks
    for c in range(1, n_cols):
        cell = tbl.cell(row_idx, c)
        if start <= c <= end:
            cell.fill.solid()
            cell.fill.fore_color.rgb = clr
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE
        # Clear default text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(6)

# Milestone dots (overlay shapes on the table)
milestones = [
    (3, 1, "Architecture\nSign-off"),   # week 3, row 1 (Discovery)
    (9, 3, "Model\nValidated"),          # week 9, row 3 (Pipeline)
    (12, 5, "Go-Live"),                  # week 12, row 5 (Rollout)
]
col_w_in = (9.20 - 1.60) / n_weeks
row_h_in = 3.20 / n_rows
for week, row, label in milestones:
    mx = 0.40 + 1.60 + (week - 0.5) * col_w_in - 0.06
    my = 1.50 + (row + 1.5) * row_h_in - 0.06
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(mx), Inches(my), Inches(0.12), Inches(0.12))
    dot.fill.solid(); dot.fill.fore_color.rgb = WHITE
    dot.line.color.rgb = DK2; dot.line.width = Pt(2)
```

### 14.37 Icon Column Cards

Vertical card columns (6-8), each with a coloured header and 3-4 items with small
bullet dots. Good for feature catalogues, service menus, capability breakdowns, or
any taxonomy that needs compact visual presentation.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CROWDSOURCING CAPABILITIES")
set_ph(slide, 1, "Six categories of insight collection methods")

columns = [
    ("Field Intel", ["Mystery shoppers", "Real-time data\ncollection", "Geospatial\nanalysis"]),
    ("Research", ["Collaborative\nsimulations", "Physician\nsurveys", "Panel\nstudies"]),
    ("Ideation", ["Virtual focus\ngroups", "Short-form\nideation", "Prediction\nmarketplace"]),
    ("Creative", ["Creative\nvisualizations", "Millennial\nideation", "Video creation"]),
    ("Analytics", ["Sentiment\nanalysis", "Social\nlistening", "Trend\nforecasting"]),
    ("Testing", ["A/B testing\nat scale", "Concept\nvalidation", "Usability\nresearch"]),
]

n = len(columns)
card_w = (9.10 - 0.15 * (n - 1)) / n
x0 = 0.45
y0 = 1.40
header_h = 0.35
item_h = 0.55
card_total_h = header_h + len(columns[0][1]) * item_h + 0.10

col_colors = [SF_BLUE, DK2, SF_BLUE, DK2, SF_BLUE, DK2]

for ci, ((title, items), clr) in enumerate(zip(columns, col_colors)):
    cx = x0 + ci * (card_w + 0.15)

    # Column header
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx), Inches(y0), Inches(card_w), Inches(header_h))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = clr
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(9); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # Card body background
    body = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx), Inches(y0 + header_h), Inches(card_w),
        Inches(len(items) * item_h + 0.10))
    body.fill.solid(); body.fill.fore_color.rgb = LIGHT_BG
    body.line.color.rgb = GRID_LINE
    body.line.width = Pt(0.5)

    # Items with bullet dots
    for ii, item_text in enumerate(items):
        iy = y0 + header_h + 0.10 + ii * item_h
        # Bullet dot
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(cx + 0.10), Inches(iy + 0.10),
            Inches(0.12), Inches(0.12))
        dot.fill.solid(); dot.fill.fore_color.rgb = clr
        dot.line.fill.background()
        # Text
        tb = slide.shapes.add_textbox(
            Inches(cx + 0.30), Inches(iy), Inches(card_w - 0.40), Inches(item_h))
        tb.text_frame.word_wrap = True
        p = tb.text_frame.paragraphs[0]; p.text = item_text
        p.font.size = Pt(8); p.font.color.rgb = DK1; p.font.name = "Arial"
```

### Pattern Selection Guide

| Slide Purpose | Recommended Pattern | Section | Visual Style |
|--------------|-------------------|---------|-------------|
| Workshop / meeting plan | Visual Agenda + Outcomes | 14.1, 14.2 | Boxes |
| What we aim to achieve | Goals & Objectives | 14.3 | Placeholder cols |
| Set expectations | IS / IS NOT | 14.4 | Contrast panels |
| Show transformation | Before / After | 14.5 | Side-by-side rows |
| Methodology / process flow | **Chevron Process Flow** | **14.18** | **Chevrons** |
| Key data points / attention | **Icon Circle Grid** | **14.25** | **Circles** |
| Project plan / milestones | **Milestone Timeline** | **14.19** | **Dots + line** |
| Phased deployment roadmap | **Arrow Ribbon Roadmap** | **14.24** | **Arrow shapes** |
| Core beliefs / design tenets | Guiding Principles | 14.9 | Placeholder list |
| Architecture / vendor choices | Decision Matrix | 14.10 | Column boxes |
| Weigh trade-offs | Pros / Cons | 14.11 | Two-column rows |
| Past success stories | Case Study Card | 14.12 | Label bars |
| Introduce the team | Team Bios | 14.13 | Name cards |
| Financial projections | Scenario Analysis | 14.14 | Column boxes |
| Capability / ecosystem map | **Hub & Spoke** | **14.20** | **Circles + lines** |
| Feature / technology stack | **Hexagon Grid** | **14.23** | **Hexagons** |
| Priority hierarchy / vision | **Pyramid** | **14.21** | **Stacked layers** |
| Conversion / qualification | **Funnel** | **14.22** | **Narrowing stages** |
| Readiness / maturity scoring | **Maturity Bars** | **14.26** | **Progress bars** |
| Decision logic / governance | **Diamond Decision Tree** | **14.27** | **Diamonds + flow** |
| Capability / readiness assessment | **Maturity Assessment Grid** | **14.28** | **Row labels + matrix cells** |
| Multi-workstream plan | **Swimlane Roadmap** | **14.29** | **Lanes + phase bars** |
| 30/60/90-day transition | **Milestone Scatter Grid** | **14.30** | **Cards on timeline canvas** |
| Pricing / service tiers | **Grouped Category Menu** | **14.31** | **Braces + tier columns** |
| Customer lifecycle / experience | **Customer Journey Map** | **14.32** | **Horizon columns + touchpoints** |
| Operating model shift | **Dual-Context Comparison** | **14.33** | **Centre labels + flanking panels** |
| Transformation narrative | **Two-Horizon Split** | **14.34** | **Today vs. Tomorrow halves** |
| Market data / impact stats | **Stat Scatter with Categories** | **14.35** | **Big numbers + context** |
| Detailed project schedule | **Gantt Table** | **14.36** | **Table-based Gantt** |
| Feature catalogue / taxonomy | **Icon Column Cards** | **14.37** | **Vertical card columns** |
| Status / maturity tracking | Multi-Row Grid | 14.16 | Table |
| Accountability assignment | RACI Matrix | 14.17 | Table |
| Architecture / platform overview | **Layered Stack + Icons** | **15.4** | **Layer bars + Snowflake icons** ⚠ MANDATORY — never use plain text bars |
| Ecosystem / connected services | **Hub & Spoke + Icons** | **15.5** | **Central hub + icon spokes** ⚠ MANDATORY — never use plain circles |
| Feature / capability grid | **Feature Grid + Icons** | **15.6** | **Icons + labels + descriptions** ⚠ MANDATORY — never use text-only grid |

---

