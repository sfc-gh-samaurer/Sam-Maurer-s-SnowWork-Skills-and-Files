---
name: pptx-core-template
description: Template loading, slide dimensions, layout map, decorative zones, and safe content zones.
---

## 2. Template Loading

The template file is `snowflake_template.pptx`. Search for it in this order:

1. `templates/snowflake_template.pptx` (project root)
2. `~/.cortex/skills/900-999_utilities/945-render-pptx/snowflake_template.pptx`

After loading, **remove ALL 71 sample slides** before adding your own:

```python
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE

# --- Locate template ---
TEMPLATE_SEARCH = [
    os.path.join(os.getcwd(), "templates", "snowflake_template.pptx"),
    os.path.expanduser("~/.cortex/skills/900-999_utilities/945-render-pptx/snowflake_template.pptx"),
]
TEMPLATE = next((p for p in TEMPLATE_SEARCH if os.path.isfile(p)), None)
assert TEMPLATE, "snowflake_template.pptx not found"

prs = Presentation(TEMPLATE)

# --- Build icon index BEFORE removing slides (icons live on slides 66-68) ---
# Only needed if deck will include architecture/feature slides with icons.
# Safe to call always — returns empty dict if icon slides not found.
ICON_INDEX = build_icon_index(prs)

# --- Remove all sample slides (robust — handles both rId formats) ---
while len(prs.slides) > 0:
    sldId = prs.slides._sldIdLst[0]
    rId = (sldId.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
           or sldId.get('r:id'))
    if rId:
        prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(sldId)
```

---

## 3. Slide Dimensions

| Property | Value | EMU |
|----------|-------|-----|
| Width | 10.00" | 9,144,000 |
| Height | 5.63" | 5,143,500 |

- **Font**: Arial everywhere (headings and body, inherited from theme)
- **Theme name**: "Snowflake 2018" (theme1.xml)
- **Slide master**: 1 master, 29 layouts

---

## 4. Colour Palette & Typography

> **See `core-branding.md` for the full colour palette, colour-usage matrix, fill→text contrast table, typography rules, paragraph spacing, and bullet style.** All colour constants and font specifications are defined there as the single source of truth. Do NOT define colour or font rules in this file.

---

## 6. Layout Map — Complete Reference

### 6.1 Cover Slides

**Background**: `scheme:accent1` = SF_BLUE `#29B5E8` on ALL cover layouts.
Decorative GroupShapes (waves) and the Snowflake logo shape are baked in.
Title text inherits DK1 (#262626) which is readable on the blue background.

| Idx | Name | Placeholders | Decorative Elements |
|-----|------|-------------|---------------------|
| **13** | Data Cloud_1_1 | PH3=title (L=0.40" T=1.30" W=8.10" H=2.10" sz=44pt), PH0=subtitle (L=0.40" T=3.46" W=5.90" H=0.48" sz=18pt), PH2=author (L=0.40" T=4.77" W=4.60" H=0.30" sz=14pt) | 2x GroupShape wave at bottom (T=4.12"), Snowflake logo at (0.50",0.60" 2.00"x0.46"), copyright at (0.50",5.36") |
| **14** | Data Cloud_1_1_3_2 | PH0=title (same pos), PH2=subtitle, PH3=author | GroupShape wave lower (T=3.19"), Snowflake logo |
| **15** | Data Cloud_1_1_3_1 | PH0=title, PH2=subtitle, PH3=author | GroupShape right graphic (5.71",1.31" 5.65"x3.01"), Snowflake logo |
| **16** | Data Cloud_1_1_2 | PH0=title, PH2=subtitle, PH3=author | Clean — Snowflake logo only |
| **17** | Data Cloud_1_1_1 | PH0=title (W=6.27"), PH2=subtitle, PH3=author | Right white panel (6.67",0.00" 3.33"x5.62"), 2x GroupShape, Snowflake logo |

**Cover no-go zones**: Do NOT place custom shapes overlapping:
- Snowflake logo: 0.50"-2.50" horizontal, 0.60"-1.06" vertical
- Copyright text: 0.50"-2.29", T=5.36"
- Wave graphics: varies by layout (see above)

### 6.2 Chapter / Section Dividers

**Background**: `scheme:dk2` = `#11567F` (dark navy blue) on ALL chapter layouts.
Text automatically renders WHITE (inherited from placeholder lstStyle).

| Idx | Name | Placeholders | Decorative Elements |
|-----|------|-------------|---------------------|
| **18** | Quote - Violet_1_1 | PH1=body (L=0.40" T=1.33" W=8.19" H=2.97" sz=40pt bold, white, lnSpc=74%) | Clean — copyright (0.72",5.32"), white accent dot (0.50",5.30") |
| **19** | Quote - Violet_1_1_2_1 | PH1=body (same) | Right image (7.71",1.95" 2.29"x3.18"), top-left image (0.00",0.00" 1.44"x1.77") |
| **20** | Quote - Violet_1_1_2_1_1 | PH1=body (same) | Bottom wave GroupShape (T=4.12") |
| **21** | Quote - Violet_1_1_2_1_1_1 | PH1=body (same) | Center wave GroupShape (0.00",1.97" 10.00"x3.65") |
| **22** | Quote - Violet_1_1_2_1_1_1_1 | PH1=body (same) | Right graphic GroupShape (5.71",1.31" 5.65"x3.01") |

**Chapter text rules**: ALL CAPS, max 2-3 lines, use `\n` for line breaks.

### 6.3 Quote Slides

| Idx | Name | Background | Placeholders | Decorative |
|-----|------|-----------|-------------|------------|
| **23** | Quote - Violet_1_1_1 | dk2 (dark navy) | PH1=quote (L=0.40" T=1.46" W=8.19" H=2.84" sz=42pt bold white lnSpc=100%), PH2=attribution (L=0.40" T=4.40" W=4.60" H=0.30" sz=16pt bold white) | Open-quote icon GroupShape (0.50",0.52" 1.29"x0.94") |
| **24** | Quote - Violet_1_1_1_3 | lt1 (**white**) | PH1=quote (same, but text=DK1), PH2=attribution (text=BODY_GREY) | Open-quote icon |
| **25** | Quote - Violet_1_1_1_2 | dk2 (dark navy) | PH1=quote (W=6.65" — narrower), PH2=attribution (L=3.30" T=4.37" W=4.60" H=0.75" right-aligned) | Open-quote icon |

### 6.4 Content Slides — Multi-use (white background)

**Background**: Inherited from master = `scheme:lt1` (white).
All have: slide number PH12 (9.00",5.32"), accent dot (0.50",5.30" blue), left edge bar (0.00",0.38" blue), copyright text (0.72",5.32").

| Idx | Name | Title PH0 | Subtitle PH1 | Special Feature |
|-----|------|-----------|-------------|-----------------|
| **0** | Multi-use layout | L=0.40" T=0.30" W=9.13" H=0.40" (lnSpc=85%) | L=0.40" T=0.72" W=9.13" H=0.40" | Standard — free canvas below 1.14" |
| **1** | Multi-use layout_2 | Same | L=0.40" **T=1.23"** W=9.13" H=0.40" | Long title variant — subtitle pushed down, taller left edge bar (0.80") |
| **2** | Multi-use layout_1 | Same | T=0.72" | Bottom dotted-line wave GroupShape (T=4.11" H=1.50") — safe zone above 4.00" |
| **3** | Multi-use layout_1_1 | Same | T=0.72" | Bottom wave GroupShape (T=4.78" H=0.85") — safe zone above 4.70" |
| **4** | Multi-use layout_1_1_1 | Same | T=0.72" | Bottom-right arrow PIC (8.51",3.21" 1.50"x2.11") — avoid lower-right |

### 6.5 Content Slides — Column Layouts (white background)

All share: PH0=title (L=0.40" T=0.30" W=~9.1" H=0.40"), slide number, accent dot, edge bar, copyright.

| Idx | Name | Cols | Subtitle PH | Body Placeholders | Default Font | Bullets |
|-----|------|------|------------|-------------------|-------------|---------|
| **5** | One Column Layout | 1 | PH2 (T=0.72") | PH1 (L=0.40" T=1.50" **W=6.85"** H=3.62") | 14pt, lnSpc=115% | L1=none, L2+=bullet |
| **6** | One Column Layout_1 | 2 | PH3 (T=0.72") | PH1 (L=0.40" W=4.55"), PH2 (L=5.05" W=4.55") both T=1.50" H=3.62" | 14pt inherited | All levels=bullet |
| **7** | One Column Layout_1_1 | 3 | PH4 (T=0.72") | PH1 (L=0.40" W=2.95"), PH2 (L=3.47" W=2.95"), PH3 (L=6.70" W=2.95") all T=1.50" H=3.62" | **14pt L1-L2, 12pt L3-L4** | All levels=bullet |
| **8** | One Column Layout_1_1_1 | 4 | PH5 (T=0.72") | PH1 (L=0.40" W=2.10"), PH2 (L=2.69"), PH3 (L=5.11"), PH4 (L=7.53") all T=1.50" H=3.62" | 14pt all levels | All levels=bullet |

### 6.6 Agenda Slides

| Idx | Name | Description | PH1 (Title Area) | PH2 (Body Area) | Dark Panel |
|-----|------|------------|-------------------|------------------|------------|
| **9** | Agenda | Side title + right body | L=0.40" T=0.30" W=2.11" H=0.75" — sz=26pt bold DK1 | L=3.24" T=1.00" W=6.26" H=4.12" — white text, bullets, centered | **Right panel**: DK2 rectangle (2.51",0 → 10",5.62"), plus SF_BLUE decorative circles and corner image |
| **10** | Agenda_1 | Sidebar + content | L=0.40" T=0.30" W=2.60" H=0.75" — sz=26pt bold **WHITE** | L=0.40" T=1.41" W=2.42" H=2.80" — 12pt **WHITE**, bullets, centered | **Left panel**: DK2 rectangle (0,0 → 3.00",5.62") |

### 6.7 Split Layout

| Idx | Name | Left Side | Right Side |
|-----|------|-----------|------------|
| **11** | Split Layout | PH0=title (L=0.40" T=0.30" W=4.35" H=0.69") + PH1=subtitle (L=0.40" T=0.69" W=4.19" H=0.32" sz=16pt BODY_GREY lnSpc=105%) | PH2=body (L=5.40" T=1.40" W=3.90" H=3.73" sz=18pt **WHITE** lnSpc=115% bullets) on **DK2 panel** |

Right side: DK2 rectangle (5.00",0 → 10",5.62") overlaid with SF_BLUE accent shapes and bottom image. PH2 text is white on dark background.

### 6.8 Blank Canvas

| Idx | Name | Description |
|-----|------|------------|
| **12** | Data Cloud_1 | Nearly blank — only PH12 slide number + accent dot + copyright. Use for full-bleed image slides. |

### 6.9 Custom Layout

| Idx | Name | Description |
|-----|------|------------|
| **26** | CUSTOM | **White title bar at top** (PH0 at T=0.30") + **DK2 dark navy rectangle** from T=1.23" to bottom (0.00",1.23" 10.00"x4.40"). Content below title is on DARK background — use WHITE text for custom shapes placed in this area. |

### 6.10 Thank You / Closing Slides

**Background**: `scheme:accent1` = SF_BLUE `#29B5E8`.

| Idx | Name | PH1 Body | Decorative |
|-----|------|---------|------------|
| **27** | Thank You | L=0.40" T=2.06" W=8.19" H=1.48" — 52pt bold WHITE lnSpc=75% | Snowflake logo (0.50",4.86" white), copyright (0.50",5.32") |
| **28** | Thank You_1 | Same | Same + bottom wave GroupShape (T=4.12") |

---

## 7. Decorative Elements — Do-Not-Overlap Zones

Every layout has fixed decorative elements baked into the master. **Never place custom shapes on top of them.**

### Common Elements (present on most content layouts)

| Element | Position | Size | Fill |
|---------|----------|------|------|
| Left edge bar | (0.00", 0.38") | 0.15" x 0.40" | accent1 (SF_BLUE) |
| Bottom-left accent dot | (0.50", 5.30") | 0.15" x 0.14" | accent1 (blue on light bg) or WHITE (on dark bg) |
| Copyright text | (0.72", 5.32") | ~1.84" x 0.10" | Grey text: "© 2026 Snowflake Inc. All Rights Reserved" |
| Slide number (PH12) | (9.00", 5.32") | 0.52" x 0.10" | #929292 on light bg, #FFFFFF on dark bg, #EFEFEF on agenda |

### Cover-Specific Elements

| Element | Position | Size | Notes |
|---------|----------|------|-------|
| Snowflake logo | (0.50", 0.60") | 2.00" x 0.46" | White fill shape (baked-in, every cover layout) |
| Copyright text | (0.50", 5.36") | 1.79" x 0.10" | Slightly lower than content slides |

---

## 8. Safe Content Zones

### Content Slides (layouts 0-8, white background)

| Edge | Position | Notes |
|------|----------|-------|
| Top (absolute min) | **1.14"** | Below title (0.30"+0.40") + subtitle (0.72"+0.40"). For layouts without subtitle text, 0.72" is safe. |
| Top (recommended) | **1.30"** | **MANDATORY for custom shapes / diagrams.** Provides 0.18" visual breathing room below subtitle. All patterns in Section 14 MUST start at ≥ 1.30". |
| Left | **0.40"** | Matches placeholder left margin |
| Right | **9.50"** | Gives 0.50" clearance from slide edge (content width = 9.10") |
| Bottom | **5.10"** | Above accent dot (5.30"), copyright (5.32"), slide number (5.32") |

For Layout 2 (bottom wave): bottom safe = **4.00"**
For Layout 3 (bottom wave): bottom safe = **4.60"**
For Layout 4 (bottom-right arrow): avoid below 3.10" and right of 8.40"

**⚠ CRITICAL: Body placeholder overflow**. Layouts 5-8 define body PHs ending at **5.12"** (T=1.50" + H=3.62"), which is 0.02" past the 5.10" safe zone. When content fills the full placeholder height, text crowds the footer. All body placeholder helpers (`set_ph_lines`, `set_ph_sections`, `set_ph_bold_keywords`, `set_ph_rich`) now call `_pad_body_ph()` to add 0.10" bottom internal padding, keeping text clear of the footer zone.

**⚠ CRITICAL: Title → Subtitle gap is only 0.017"** (title PH bottom=0.70", subtitle PH top=0.72"). The title placeholder has `spAutoFit` in the template, which means it EXPANDS downward if text overflows — directly overlapping the subtitle. To prevent this:
1. `set_ph()` now sets `auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` (shrinks text instead of expanding shape)
2. `set_ph()` zeroes the title's bottom internal margin and adds 0.06" top padding to subtitle — creating a visible ~0.08" visual gap
3. `set_ph()` resets paragraph `indent=0` and `marL=0` — so wrapped subtitle text starts at the same left position as the first line (no hanging indent)
4. Title text MUST be ≤ 50 characters — see Rule 26
5. Subtitle text MUST be ≤ 65 characters — see Rule 27 (fits on one line at 14pt in 9.1")

### Cover Slides (layouts 13-17)

Content zone for covers is managed by placeholders — do not add custom shapes to cover slides.

### Layout 26 (CUSTOM)

| Zone | Area | Text Colour |
|------|------|-------------|
| Title bar (white) | 0.00"-1.23" vertical | DK1 (dark) |
| Dark canvas (DK2) | 1.23"-5.62" vertical, full width | **WHITE** (use white text/shapes) |

---
