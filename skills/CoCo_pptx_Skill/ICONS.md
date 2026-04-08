# PPTX Icon Library Reference — Template-Embedded Icons

> **This file is a reference companion to SKILL.md.**
> Read this file when you need icon catalog names, helper functions, or icon-based layout code.

## 15. Snowflake Icon Library (Template-Embedded)

The template (slides 66-68) contains **103 official Snowflake vector icons** — product logos, concept icons, cloud provider logos, and general business icons. These are embedded as Freeform, Group, and Picture shapes that can be **programmatically copied** to any slide for architecture diagrams, feature grids, and visual layouts.

### 15.1 Icon Catalog

**AI & ML**: Snowflake Cortex, Document AI, Universal Search, Snowflake Copilot, Snowflake Horizon

**Data & Tables**: Data, Database, Snowflake Database, Snowflake Databases, Dynamic Tables, External Tables, Hybrid Tables, Iceberg Tables, Structured Data, Semi-Structured Data, Unstructured Data, All Your Data, Secure Data, Metadata, Integrated Data

**Platform & Compute**: Snowpark, Snowpark Containers, Streamlit in Snowflake, Snowflake Native App, Kafka Connectors, Server, Architecture, Performance / Scale, Concurrency, Speed

**Collaboration & Sharing**: Sharing, Snowflake Marketplace, Data Monetization, Public Data Exchange, Private Data Exchange

**Security & Governance**: Security, Transactions, High Availability

**Users & People**: User, Users, 3rd Party, Processes, Process

**Devices**: Desktop, Laptop, Mobile, Application, Dev, 3rd Party Apps

**Business & Operations**: Operating Snowflake, Easy Management, Management, Optimize, Search, Communicate, Enterprise, Industry, Corporate, Target, Cost Savings, Pricing, Results, Self Service, Easily On-Board

**Actions & Concepts**: Launch, Edit, Copy, Flag, Time, Event, On-Demand, Calendar, Location, Social, Idea, Email, Expand, Consolidate

**Analytics**: Analytics / Statistics, Data Analytics Applications, Geospatial Analytics, Accelerated Analytics, Interactive Tables, Interactive Warehouse, Capacity

**Cloud Providers**: AWS S3Bucket, S3 Data Protection, Microsoft Azure Blob, GCS

**Snowflake Values**: Own it, Integrity, Be Excellent, Put Customers First, Think Big, Make Each Other the Best

**Other**: Snowflake Trail, Workshop, Happy Hour, Contact Sales, Finance Option, Simplify Database Admin, Single Source of Truth, Easy / Consolidate, Eliminate Complexity

### 15.2 Icon Helper Functions

```python
import re, copy
from pptx.enum.shapes import MSO_SHAPE_TYPE

def build_icon_index(prs):
    """Build a lookup dictionary of all template icons from slides 66 and 68.
    
    Call ONCE after loading the template (before removing sample slides).
    Returns dict: normalized_name -> (shape_object, slide_part)
    
    Usage:
        prs = Presentation(TEMPLATE)
        ICON_INDEX = build_icon_index(prs)
        # ... then remove sample slides ...
        # ... then use place_icon() with ICON_INDEX ...
    """
    icon_index = {}
    
    def _normalize(s):
        return re.sub(r'\s+', ' ', s.strip().lower())
    
    for sn in [66, 68]:
        if sn - 1 >= len(prs.slides):
            continue
        slide = prs.slides[sn - 1]
        labels = []
        graphics = []
        
        for shape in slide.shapes:
            l = shape.left / 914400
            t = shape.top / 914400
            w = shape.width / 914400
            h = shape.height / 914400
            if t < 0.6 or shape.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER:
                continue
            if shape.has_text_frame and shape.text_frame.text.strip():
                txt = shape.text_frame.text.strip().replace('\n', ' ')
                labels.append((l, t, txt))
            elif shape.shape_type in (MSO_SHAPE_TYPE.GROUP, MSO_SHAPE_TYPE.FREEFORM,
                                       MSO_SHAPE_TYPE.PICTURE):
                if w < 1.0 and h < 1.0:
                    graphics.append((l, t, shape))
        
        for gl, gt, gshape in graphics:
            best_label = None
            best_dist = 999
            for ll, lt, ltxt in labels:
                if lt > gt and lt - gt < 0.7 and abs(ll - gl) < 0.5:
                    dist = abs(ll - gl) + abs(lt - gt)
                    if dist < best_dist:
                        best_dist = dist
                        best_label = ltxt
            if best_label:
                key = _normalize(best_label)
                if key not in icon_index:
                    icon_index[key] = (gshape, slide.part)
    
    return icon_index


def place_icon(slide, icon_index, icon_name, target_left, target_top, scale=2.0):
    """Copy a template icon to a specific position on a slide.
    
    Args:
        slide: Target slide object
        icon_index: Dict from build_icon_index()
        icon_name: Icon name from the catalog (case-insensitive)
        target_left: Left position in inches
        target_top: Top position in inches
        scale: Size multiplier (default 2.0 = double the original ~0.3" icon)
    
    Returns the new XML element, or None if icon not found.
    """
    key = re.sub(r'\s+', ' ', icon_name.strip().lower())
    if key not in icon_index:
        return None
    
    src_shape, src_part = icon_index[key]
    new_el = copy.deepcopy(src_shape._element)
    
    # Reposition and scale
    ns_a = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    for child in new_el.iter():
        if child.tag.endswith('}xfrm'):
            off = child.find(f'{{{ns_a}}}off')
            ext = child.find(f'{{{ns_a}}}ext')
            if off is not None:
                off.set('x', str(int(target_left * 914400)))
                off.set('y', str(int(target_top * 914400)))
            if ext is not None and scale != 1.0:
                cx = int(int(ext.get('cx', '0')) * scale)
                cy = int(int(ext.get('cy', '0')) * scale)
                ext.set('cx', str(cx))
                ext.set('cy', str(cy))
            break  # Only adjust the top-level xfrm
    
    # Fix image relationships (for PICTURE and GROUP shapes containing images)
    ns_r = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    for blip in new_el.iter(f'{{{ns_a}}}blip'):
        embed_id = blip.get(f'{{{ns_r}}}embed')
        if embed_id:
            src_rel = src_part.rels.get(embed_id)
            if src_rel:
                new_rId = slide.part.relate_to(src_rel.target_part, src_rel.reltype)
                blip.set(f'{{{ns_r}}}embed', new_rId)
    
    slide.shapes._spTree.append(new_el)
    return new_el


def add_icon_with_label(slide, icon_index, icon_name, left, top,
                         label=None, scale=2.0, label_size=Pt(7)):
    """Place an icon with a bold label below it.
    
    Args:
        label: Override text (defaults to icon_name)
        scale: Icon size multiplier
        label_size: Font size for label (default 7pt)
    
    Example:
        add_icon_with_label(slide, ICON_INDEX, "Snowflake Cortex",
            1.0, 1.70, label="Cortex AI")
    """
    el = place_icon(slide, icon_index, icon_name, left, top, scale=scale)
    lbl = label or icon_name
    
    # Label (bold, centred below icon)
    tb = slide.shapes.add_textbox(
        Inches(left - 0.30), Inches(top + 0.55),
        Inches(1.20), Inches(0.25))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = lbl
    p.font.size = label_size; p.font.bold = True
    p.font.color.rgb = DK1; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
    
    return el
```

### 15.3 Usage Pattern — Build Icon Index Before Removing Slides

```python
# ⚠ CRITICAL: Build the icon index BEFORE removing sample slides,
# because the icons live on template slides 66-68.

prs = Presentation(TEMPLATE_PATH)
ICON_INDEX = build_icon_index(prs)   # ← MUST come first

# NOW remove sample slides
while len(prs.slides) > 0:
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        rId = (sldId.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
               or sldId.get('r:id'))
        if rId:
            prs.part.drop_rel(rId)
            sldIdLst.remove(sldId)
            break
```

### 15.4 Architecture Diagram Pattern — Layered Stack

A professional architecture diagram with colored layer bars and official Snowflake icons. 
Use for technology overviews, platform capability slides, and solution architectures.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "SNOWFLAKE AI DATA CLOUD ARCHITECTURE")
set_ph(slide, 1, "Layered capabilities powering intelligent applications")

# Define layers (top to bottom)
# Format: (icon_catalog_name, x_position, label)
layers = [
    ("INTELLIGENT APPLICATIONS", SF_BLUE, 1.30, [
        ("Streamlit in Snowflake", 1.0, "Streamlit"),
        ("Snowpark Containers", 3.0, "SPCS"),
        ("Snowflake Copilot", 5.0, "Copilot"),
        ("Snowflake Native App", 7.0, "Native Apps"),
    ]),
    ("AI & ML SERVICES", DK2, 2.50, [
        ("Snowflake Cortex", 1.0, "Cortex AI"),
        ("Document AI", 3.0, "Document AI"),
        ("Universal Search", 5.0, "Universal Search"),
        ("Snowflake Horizon", 7.0, "Horizon"),
    ]),
    ("DATA PLATFORM", TEAL, 3.70, [
        ("Snowflake Database", 1.0, "Database"),
        ("Dynamic Tables", 3.0, "Dynamic Tables"),
        ("Iceberg Tables", 5.0, "Iceberg Tables"),
        ("Security", 7.0, "Security"),
    ]),
]

for layer_name, color, y, icons in layers:
    # Layer bar
    bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.40), Inches(y), Inches(9.10), Inches(0.28))
    bar.fill.solid(); bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    tf = bar.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = layer_name
    p.font.size = Pt(8); p.font.bold = True
    p.font.color.rgb = WHITE if color != TEAL else DK1
    p.font.name = "Arial"; p.alignment = PP_ALIGN.CENTER
    
    # Icons below the bar
    for icon_name, x, label in icons:
        add_icon_with_label(slide, ICON_INDEX, icon_name, x, y + 0.38, label)
```

### 15.5 Architecture Diagram Pattern — Hub & Spoke with Icons

Central capability surrounded by connected features — great for showing how a core 
platform connects to various services.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "CORTEX AI ECOSYSTEM")
set_ph(slide, 1, "Unified intelligence layer connecting all data services")

# Central hub (large circle) — centred vertically in safe zone (1.30"–4.70")
# Hub centre at 3.00" keeps all spokes within bounds
hub = slide.shapes.add_shape(MSO_SHAPE.OVAL,
    Inches(3.80), Inches(2.10), Inches(1.80), Inches(1.80))
hub.fill.solid(); hub.fill.fore_color.rgb = SF_BLUE
hub.line.fill.background()
tf = hub.text_frame; tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.text = "Cortex AI"
p.font.size = Pt(16); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

# Place icon in hub center
place_icon(slide, ICON_INDEX, "Snowflake Cortex", 4.40, 2.25, scale=2.5)

# Spoke icons around the hub
# ⚠ SAFE ZONE: All spoke y positions must be ≥ 1.30" and icons+labels must end ≤ 4.70"
# Icons are ~0.55" tall + label ~0.25" below = ~0.80" total per spoke
spokes = [
    ("Document AI",      1.50, 1.40, "Document AI"),       # top-left
    ("Universal Search", 6.80, 1.40, "Universal Search"),   # top-right
    ("Snowflake Copilot",1.50, 3.40, "Copilot"),            # bottom-left
    ("Snowflake Horizon",6.80, 3.40, "Governance"),         # bottom-right
    ("Snowpark",         4.10, 1.30, "Snowpark"),           # top-centre
    ("Security",         4.10, 3.80, "Security"),           # bottom-centre (label at ~4.55") ✓
]

for icon_name, x, y, label in spokes:
    add_icon_with_label(slide, ICON_INDEX, icon_name, x, y, label, scale=1.8)
    
    # Draw connector line from spoke to hub center (4.70", 3.00")
    hx, hy = 4.70, 3.00  # hub center
    ix, iy = x + 0.25, y + 0.25  # icon center (approx)
    line = slide.shapes.add_connector(
        1,  # MSO_CONNECTOR.STRAIGHT
        Inches(ix), Inches(iy),
        Inches(hx), Inches(hy))
    line.line.color.rgb = CONN_LINE
    line.line.width = Pt(1)
```

### 15.6 Feature Grid Pattern — Icons with Descriptions

A grid of icons with feature names and short descriptions — ideal for 
capability overviews and feature comparison slides.

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "SNOWFLAKE AI & ML CAPABILITIES")
set_ph(slide, 1, "Production-ready intelligence built into the data platform")

features = [
    ("Snowflake Cortex", "Cortex AI (GA)",
     "LLM functions via SQL:\nCOMPLETE, SUMMARIZE,\nSENTIMENT, TRANSLATE"),
    ("Document AI", "Document AI (GA)",
     "Extract structured data\nfrom PDFs, invoices, and\nscanned images"),
    ("Universal Search", "Universal Search (GA)",
     "Semantic + keyword search\nacross all Snowflake data\nassets"),
    ("Snowflake Copilot", "Copilot (GA)",
     "AI-assisted SQL generation,\noptimization, and natural-\nlanguage querying"),
    ("Snowflake Horizon", "Horizon (GA)",
     "Unified governance:\nmasking, lineage,\nclassification, policies"),
    ("Snowpark Containers", "Containers (GA)",
     "Run any Docker image\non Snowflake-managed\nGPU infrastructure"),
]

n_cols = 3
col_w = 2.70
gap_x = (9.10 - n_cols * col_w) / (n_cols + 1)

for i, (icon_name, label, desc) in enumerate(features):
    col = i % n_cols
    row = i // n_cols
    x = 0.40 + gap_x * (col + 1) + col_w * col + 0.20
    y = 1.40 + row * 1.80
    
    # Icon
    place_icon(slide, ICON_INDEX, icon_name, x + 0.70, y, scale=2.2)
    
    # Feature name (bold, below icon)
    nb = slide.shapes.add_textbox(
        Inches(x), Inches(y + 0.60), Inches(col_w - 0.40), Inches(0.30))
    tf = nb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(11); p.font.bold = True
    p.font.color.rgb = DK2; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
    
    # Description (below name)
    db = slide.shapes.add_textbox(
        Inches(x), Inches(y + 0.90), Inches(col_w - 0.40), Inches(0.60))
    tf = db.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = desc
    p.font.size = Pt(8); p.font.color.rgb = BODY_GREY; p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER
```

### 15.7 When to Use Icons

| Slide Type | Use Icons? | Recommended Pattern |
|-----------|-----------|-------------------|
| Architecture / platform overview | **YES** ⭐ | 15.4 Layered Stack or 15.5 Hub & Spoke |
| Feature / capability grid | **YES** ⭐ | 15.6 Feature Grid |
| Solution architecture for a customer | **YES** ⭐ | 15.4 with customer-relevant layers |
| Process flow / methodology | Maybe | Only if specific product icons are relevant; otherwise use chevrons (14.18) |
| Executive summary / strategy | No | Use stat callouts (14.7) or icon circles (14.25) instead |
| Agenda / timeline | No | Use visual agenda patterns (14.1, 14.2) |
| Before/After, Pros/Cons | No | Use comparison patterns (14.5, 14.11) |

**Rules for icon usage:**
1. Use icons from the catalog (Section 15.1) ONLY — never create custom icon shapes
2. Default scale = 2.0 (produces ~0.55" icons from ~0.28" originals)
3. Always add a label below the icon via `add_icon_with_label()`
4. Keep icons within the safe zone (0.40" – 9.50" wide, 1.30" – 5.10" tall)
5. Minimum spacing between icon centers: 1.50" horizontal, 1.40" vertical
6. Icon colour inherits from the template — do not recolour
7. Build `ICON_INDEX` BEFORE removing template slides (Section 15.3)

---

