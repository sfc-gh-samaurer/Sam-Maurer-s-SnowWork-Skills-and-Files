---
name: pptx-core-branding
description: Snowflake colour palette, fill-text contrast rules, and typography specifications.
---

## 4. Colour Palette (MANDATORY)

Extracted from `theme1.xml` colour scheme. **Use ONLY these colours. Never invent or use any colour not in this list.**

```python
# ── Theme Colours (from theme1.xml "Snowflake 2018") ──
DK1       = RGBColor(0x26, 0x26, 0x26)  # dk1  — primary dark text
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)  # lt1  — white
DK2       = RGBColor(0x11, 0x56, 0x7F)  # dk2  — Snowflake dark navy blue
SF_BLUE   = RGBColor(0x29, 0xB5, 0xE8)  # accent1 — Snowflake Blue (primary brand)
TEAL      = RGBColor(0x71, 0xD3, 0xDC)  # accent3
ORANGE    = RGBColor(0xFF, 0x9F, 0x36)  # accent4
VIOLET    = RGBColor(0x7D, 0x44, 0xCF)  # accent5
PINK      = RGBColor(0xD4, 0x5B, 0x90)  # accent6

# ── Extended Utility Colours (from sample slides) ──
BODY_GREY = RGBColor(0x5B, 0x5B, 0x5B)  # subtitle / body text colour
TBL_GREY  = RGBColor(0x71, 0x71, 0x71)  # table data cell text
SLD_NUM   = RGBColor(0x92, 0x92, 0x92)  # slide number text (light layouts)
MUTED     = RGBColor(0xBF, 0xBF, 0xBF)  # disabled / followed-link grey
LIGHT_BG  = RGBColor(0xF5, 0xF5, 0xF5)  # alternating table row fill
BORDER    = RGBColor(0xC8, 0xC8, 0xC8)  # table cell border strokes
GRID_LINE = RGBColor(0xDD, 0xDD, 0xDD)  # light grid/cell border strokes
CONN_LINE = RGBColor(0xCC, 0xCC, 0xCC)  # connector lines between shapes
ERROR_RED = RGBColor(0xA2, 0x00, 0x00)  # "Do not" callout (use sparingly)
```

### Colour-Usage Matrix

| Context | Colour | Notes |
|---------|--------|-------|
| Dark text on white/light backgrounds | DK1 `#262626` | Default for all light-bg slides |
| White text on dark backgrounds | WHITE `#FFFFFF` | DK2, SF_BLUE, accent1 backgrounds |
| Slide titles | Inherited | DK1 on light bg, auto white on dark bg |
| Subtitles | BODY_GREY `#5B5B5B` | All subtitle placeholders |
| Section paragraph headings | DK2 `#11567F` | Bold, 15pt |
| Table header row fill | DK2 `#11567F` | White bold text |
| Table emphasis row fill | SF_BLUE `#29B5E8` | White text |
| Table data cell text | TBL_GREY `#717171` | On white or LIGHT_BG fill |
| Table borders | BORDER `#C8C8C8` | 1pt (12700 EMU) |
| Accent boxes in diagrams | SF_BLUE, DK2, TEAL, ORANGE, VIOLET, PINK | Use Fill→Text table below |
| Snowflake Blue as text | Only at **28pt or larger** | Accessibility rule from template guidelines |
| TEAL, ORANGE, VIOLET, PINK as text | **Never** | Only for shape fills, never small text |

### Fill → Text Colour Contrast (MANDATORY)

When using accent colours as **shape fills**, use this lookup for text colour. Never guess — wrong combinations are unreadable.

| Fill Colour | Text Colour | Reason |
|------------|-------------|--------|
| **DK2** `#11567F` | WHITE | Dark fill — 7.9:1 contrast |
| **SF_BLUE** `#29B5E8` | WHITE | Brand standard (emphasis rows, headers) |
| **TEAL** `#71D3DC` | **DK1** | Light fill — white is only 1.7:1 |
| **ORANGE** `#FF9F36` | **DK1** | Light fill — white is only 2.0:1 |
| **VIOLET** `#7D44CF` | WHITE | Dark fill — 6.0:1 contrast |
| **PINK** `#D45B90` | WHITE | Medium fill — 3.8:1 (bold only) |
| **BODY_GREY** `#5B5B5B` | WHITE | Dark enough for white text |
| **LIGHT_BG** `#F5F5F5` | DK1 | Very light — dark text required |
| **GRID_LINE** `#DDDDDD` | DK1 | Grid/cell borders only — do not use as text colour |
| **CONN_LINE** `#CCCCCC` | DK1 | Connector lines only — do not use as text colour |
| **WHITE** | DK1 | Light — dark text required |
| **ERROR_RED** `#A20000` | WHITE | Dark fill — high contrast |

**CRITICAL**: TEAL and ORANGE are light accent colours. Never use WHITE text on these fills — always use DK1.

**CRITICAL**: GRID_LINE and CONN_LINE are structural colours for lines/borders only. Never use them as text colour or shape fills — they serve as visual separators.

---

## 5. Typography Rules

### Font Sizes by Element (from layout placeholders and sample slides)

| Element | Font | Weight | Size | Case | Colour | Line Spacing |
|---------|------|--------|------|------|--------|-------------|
| Cover big title (PH3) | Arial | Bold | 44pt | ALL CAPS | DK1 (inherited) | 85% |
| Cover subtitle (PH0) | Arial | Bold | 18pt | Title Case | DK1 | 80% |
| Cover author line (PH2) | Arial | Regular | 14pt | Mixed | DK1 | 90% |
| Slide title (PH0) | Arial | Bold | 14pt | ALL CAPS | Inherited | 85% |
| Slide subtitle | Arial | Regular | inherited | Mixed | BODY_GREY #5B5B5B | — |
| Chapter divider (PH1) | Arial | Bold | 40pt | ALL CAPS | WHITE (inherited on dk2 bg) | 74% |
| Quote body (PH1) | Arial | Bold | 42pt | Sentence | WHITE (inherited on dk2 bg) | 100% |
| Quote attribution (PH2) | Arial | Bold | 16pt | Mixed | WHITE #FFFFFF | — |
| 1-col body (layout 5 PH1) | Arial | Regular | 14pt (inherited) | Sentence | Inherited | 115% |
| 2-col body (layout 6 PH1/2) | Arial | Regular | 14pt (inherited) | Sentence | Inherited | — (inherits master) |
| 3-col body (layout 7) | Arial | Regular | 14pt | Sentence | Inherited | — |
| 4-col body (layout 8) | Arial | Regular | 14pt | Sentence | Inherited | — |
| Agenda title (PH1) | Arial | Bold | 26pt | Mixed | DK1 on layout 9, WHITE on layout 10 | 85-100% |
| Agenda body (PH2) | Arial | Regular | 12-14pt | Mixed | WHITE on dk2 panel | — |
| Split subtitle (PH1) | Arial | Regular | 16pt | Mixed | BODY_GREY #5B5B5B | 105% |
| Split right body (PH2) | Arial | Regular | 18pt | Sentence | WHITE (on dk2 panel) | 115% |
| Table header | Arial | Bold | 10-14pt | Title Case | WHITE on DK2 fill | — |
| Table data | Arial | Regular | 9-11pt | Mixed | TBL_GREY #717171 | — |
| Footnote | Arial | Regular | 9pt | Sentence | BODY_GREY #5B5B5B | — |
| Thank You body (PH1) | Arial | Bold | 52pt | ALL CAPS | WHITE (on accent1 bg) | 75% |

### Paragraph Spacing (from lstStyle)

| Element | Space Before L1 | Space Before L2+ | Space After | Line Spacing |
|---------|-----------------|-------------------|-------------|-------------|
| Subtitle (all layouts) | 0pt | 10pt | 0pt | inherited |
| Body 1-col (layout 5) | 0pt | 10pt | 0pt | 115% |
| Body 2-col (layout 6) | 0pt | 10pt | 0pt | inherited |
| Body 3/4-col (layout 7/8) | 0pt | 10pt | 0pt | inherited |
| Chapter divider (18-22) | 0pt | 8pt (L2), 10pt (L3+) | 0pt | 74% |
| Quote (23) | 0pt | 10pt | 0pt | 100% |
| Agenda title (layout 9 PH1) | 0pt | 10pt | 0pt | 85% |
| Split subtitle (layout 11 PH1) | 0pt | 10pt | 0pt | 105% |
| Split right body (layout 11 PH2) | 0pt | 10pt | 0pt | 115% |
| Thank You (27/28) | 0pt | 0pt (L2), 10pt (L3+) | 0pt | 75% |

### Bullet Style

| Level | Character | Indent (EMU) | Left Margin (EMU) |
|-------|-----------|-------------|-------------------|
| L1 | None (most layouts) or `\u2022` (multi-col) | -228600 or -342900 | 457200 |
| L2 | `\u2022` | -342900 | 914400 |
| L3 | `\u2022` | -317500 | 1371600 |
| L4 | `\u2022` | -317500 | 1828800 |

- **1-column body (layout 5)**: L1 has NO bullet, L2+ has bullets
- **2/3/4-column body (layouts 6-8)**: ALL levels have bullets
- **Subtitle placeholders**: NO bullets at any level
- **Chapter/quote placeholders**: L1 NO bullet, L2+ has bullets (rarely used)

---
