---
name: snowflake-pptx-collateral
description: "Create professional Snowflake-branded PowerPoint (PPTX) decks using python-pptx. Use for: presentations, business reviews, district reviews, customer decks, summary slides, status updates, executive presentations. Triggers: PPTX, PowerPoint, deck, slides, presentation, create deck, build slides, business review deck, summary slide."
allowed-tools: Bash, Read, Write
log_marker: SKILL_USED_RENDER_PPTX
skill_version: "2026-04-15"
---

# PPTX Creation — Official Snowflake Template (January 2026)

This skill creates PowerPoint decks using the official Snowflake corporate
template and `python-pptx`. All decks inherit Snowflake brand colours, Arial
typography, and slide-master layouts automatically.

**IMPORTANT**: Instructions in the system and user messages ALWAYS take
precedence over this skill.

---

## Session Prerequisites (Always First)

Before any operation, load the required references:

1. Load `references/core-branding.md` and `references/core-template.md`
2. Load `references/core-helpers.md`
3. Follow the Interaction Model in `references/interaction-model.md`
4. Only proceed to code generation after the Content Blueprint is approved

---

## ⚠ CRITICAL — READ BEFORE GENERATING ANY CODE

**HARD STOP: DO NOT WRITE ANY PYTHON CODE ON YOUR FIRST RESPONSE.**

Your first response to the user MUST be Phase 0 (Offer Two Paths) from
`references/interaction-model.md`. You MUST wait for the user to reply before
proceeding. If the user's request is vague or missing details, you MUST ask
Phase 1 questions. You may NEVER skip directly to code generation.

The only exception: headless/non-interactive mode (`-p` flag) — make reasonable
defaults, produce the Content Blueprint, then build.

### Top 19 Failure Modes (memorise these — violations are caught by verify_slide/verify_deck)

0. **PLAN CONTENT BEFORE CODE** — Content Blueprint (Phase 4) is mandatory. Content is 80% of deck quality. Blueprint MUST specify a visual pattern for every content slide (not just bullets).
1. **EVERY custom shape via `add_shape_text()`** — copy this helper from `references/core-helpers.md` Section 12.7. NEVER use `slide.shapes.add_shape()` directly — not for hub-spoke, not for chevrons, not for anything. `add_shape_text()` enforces Arial font, auto_size, no-outline, tight margins, correct contrast, AND auto-inserts `\n` for narrow shapes — all in ONE call.
2. **Cover title ≤ 50 characters** — punchy 4-6 words. Details go in subtitle.
3. **Multi-line text uses `\n` in a single string** — NEVER separate runs. `"LINE1\nLINE2"` not `run1 + run2`.
4. **Architecture slides use template icons** — `place_icon()` from `references/icons.md`.
5. **Always use `set_ph()` for placeholder text** — never `ph.text = "..."` directly.
6. **ONLY named palette constants** — DK1, SF_BLUE, TEAL, etc. from `references/core-branding.md`. No inline `RGBColor(...)`.
7. **Arial font on EVERY custom shape paragraph** — `add_shape_text()` handles this automatically.
8. **Content quality enforced by `verify_slide()`** — generic text flagged. See `references/verification.md`.
9. **EVERY content slide has title AND subtitle** — empty subtitles look unfinished.
10. **SQL / code / multi-line blocks via `add_code_block()`** — pass lines as a LIST, not a concatenated string. See `references/core-helpers.md` Section 12.8. NEVER set `Auto size: None` on code shapes.
11. **Comparison tables use native `add_table()`** — NEVER build grids from individual rectangle shapes. See `references/slide-patterns.md` Section 11.
12. **3+ categorised sections → separate shapes or columns** — NEVER dump 3+ bold-header groups into one placeholder. Use 3-col layout (Layout 7), `add_shape_text()` callout boxes, or `set_ph_sections()` across columns. See `references/slide-patterns.md` Section 12.8.
13. **≥40% of content slides MUST have visual elements** (diagrams, shapes, tables, icons) — NEVER produce 3+ consecutive bullet-only slides. Load `references/patterns-enterprise.md` and use chevrons, hub-spoke, stat callouts, timelines, etc. Bullet-only decks are rejected by `verify_deck()`.
14. **TEAL and ORANGE fills ALWAYS use DK1 text, NEVER WHITE** — These are light accent colours. WHITE text on them is unreadable (contrast ratio <2:1). `verify_slide()` catches this. See the Fill→Text contrast table in `core-branding.md`.
15. **EVERY custom shape MUST have NO outline** — `add_shape_text()` sets `shape.line.fill.background()` automatically. If you create shapes manually (DON'T), you must remove outlines. `verify_slide()` flags visible strokes.
16. **Cover slide PH mapping: Layout 13 → PH3=title(44pt), PH0=subtitle(18pt), PH2=author(14pt)** — The BIG title on cover slides goes in PH[3], NOT PH[0]. PH[0] is the subtitle. See `slide-patterns.md` Section 10.1. Getting this wrong makes the cover unreadable.
17. **ALL diagram shapes via `add_shape_text()` — it auto-inserts `\n`** — NEVER build shapes manually with `slide.shapes.add_shape()`. `add_shape_text()` automatically replaces spaces with `\n` for shapes ≤2" wide. If you build shapes manually, labels like "CORTEX AI" won't wrap and become unreadable. This is the #1 cause of ugly diagram slides.
18. **3+ section bullet slides MUST use columns or shapes, NEVER a single placeholder** — If a slide has 3+ bold-header groups (e.g. "Feature A" + bullets, "Feature B" + bullets, "Feature C" + bullets), it MUST use Layout 7 (3-column), Layout 6 (2-column), or separate `add_shape_text()` boxes. NEVER dump all sections into PH[1] as a wall of text. `verify_deck()` catches 3+ consecutive bullet-only slides.
19. **Custom shapes on DARK-BACKGROUND layouts MUST use WHITE text** — Layouts 9-PH2, 10, 11-PH2, 18-22, 23, 25, 26-canvas, 27-28 have DK2/SF_BLUE/accent1 dark fills. Any `add_shape_text()` call placed on the dark region of these layouts MUST pass `WHITE` as `font_colour`. DK1 text on a dark background is invisible. `verify_slide()` catches this. See the `DARK_BG_LAYOUTS` set in `references/core-helpers.md`.

---

## ⚠ MANDATORY — Copy These Into EVERY Script

### Dark-Background Layout Set (MUST CHECK before choosing text colour)

```python
# Layouts where the canvas (or a major panel) is dark — custom shapes MUST use WHITE text.
# For split layouts (9, 11), only the dark panel region requires WHITE.
DARK_BG_LAYOUTS = {9, 10, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28}
# Cover layouts (13-17) have accent1 (SF_BLUE) background — placeholder text inherits WHITE.
# But custom shapes on covers must also use WHITE.
COVER_LAYOUTS = {13, 14, 15, 16, 17}
```

### Fill → Text Contrast Lookup (NEVER guess — wrong combos are unreadable)

```python
# ALWAYS use this lookup when choosing text colour on accent fills:
FILL_TEXT = {
    "DK2":     WHITE,    # dark navy → white
    "SF_BLUE": WHITE,    # Snowflake blue → white
    "TEAL":    DK1,      # ⚠ LIGHT fill → DK1 dark text (NEVER WHITE)
    "ORANGE":  DK1,      # ⚠ LIGHT fill → DK1 dark text (NEVER WHITE)
    "VIOLET":  WHITE,    # dark purple → white
    "PINK":    WHITE,    # medium pink → white (bold only)
}
```

### Cover Slide PH Mapping (Layout 13 — Primary Cover)

```python
slide = prs.slides.add_slide(prs.slide_layouts[13])
set_ph(slide, 3, "BIG TITLE HERE")     # ← PH[3] = 44pt big title (NOT PH[0]!)
set_ph(slide, 0, "Subtitle line")      # ← PH[0] = 18pt subtitle
set_ph(slide, 2, "Author  |  Date")    # ← PH[2] = 14pt author
```

### Shape Labels — `add_shape_text()` Auto-Inserts `\n` for Narrow Shapes

```python
# add_shape_text() automatically replaces spaces with \n when width ≤ 2".
# You can pass EITHER format — the function handles it:
add_shape_text(slide, MSO_SHAPE.OVAL, x, y, 1.0, 1.0,
               "CORTEX AI", DK2, WHITE)     # → becomes "CORTEX\nAI" automatically
add_shape_text(slide, MSO_SHAPE.OVAL, x, y, 1.0, 1.0,
               "CORTEX\nAI", DK2, WHITE)    # → also works (already has \n)

# ⚠ But NEVER build shapes manually — always use add_shape_text():
# ❌ shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, ...); p.text = "CORTEX AI"
# ✅ add_shape_text(slide, MSO_SHAPE.OVAL, ..., "CORTEX AI", ...)
```

### Multi-Section Content — Use Columns or Shapes, NEVER Bullet Dump

```python
# ✅ CORRECT — 3 sections → 3-column layout:
slide = prs.slides.add_slide(prs.slide_layouts[7])  # Layout 7 = 3-column
set_ph(slide, 0, "FEATURE OVERVIEW")
set_ph(slide, 1, "Section A\n• Bullet 1\n• Bullet 2")
set_ph(slide, 2, "Section B\n• Bullet 1\n• Bullet 2")
set_ph(slide, 3, "Section C\n• Bullet 1\n• Bullet 2")

# ✅ ALSO CORRECT — 3 separate shape boxes on a blank layout:
slide = prs.slides.add_slide(prs.slide_layouts[0])
set_ph(slide, 0, "FEATURE OVERVIEW")
set_ph(slide, 1, "Key capabilities at a glance")
add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.5, 1.5, 2.8, 2.5, "Section A\n• Bullet 1\n• Bullet 2", LIGHT_BG, DK1)
add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 3.5, 1.5, 2.8, 2.5, "Section B\n• Bullet 1\n• Bullet 2", LIGHT_BG, DK1)
add_shape_text(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 6.5, 1.5, 2.8, 2.5, "Section C\n• Bullet 1\n• Bullet 2", LIGHT_BG, DK1)

# ❌ WRONG — wall of text in one placeholder:
set_ph(slide, 1, "Section A\n• Bullet\nSection B\n• Bullet\nSection C\n• Bullet")
```

---

## Dependencies

```bash
uv pip install python-pptx
```

## Output Destination

By default, decks save to `~/Google Drive/My Drive/` so they sync automatically
to Google Drive and can be opened in Google Slides. If Google Drive Desktop is
not installed, falls back to `~/Downloads/`.

See `references/core-helpers.md` Section 18 for save code.

| User Says | Save To |
|-----------|--------|
| "save to Google Drive", "open in Slides" | `~/Google Drive/My Drive/{deck_name}.pptx` |
| "save to Drive folder X" | `~/Google Drive/My Drive/X/{deck_name}.pptx` |
| "save locally", "save to Downloads" | `~/Downloads/{deck_name}.pptx` |
| (no preference stated) | Google Drive if available, else `~/Downloads/` |

---

## Primary Routing Table

| User Intent | Reference to Load | What It Contains |
|-------------|-------------------|------------------|
| Build a deck, create slides, make a presentation | `references/interaction-model.md` | Phase 0-5 consultative workflow |
| Template loading, layout indices, placeholder IDs | `references/core-template.md` | Layouts 0-28, PH indices, safe zones |
| Colours, fonts, typography specs | `references/core-branding.md` | Colour palette, fill→text contrast, font rules |
| Placeholder helpers, shape helpers, code blocks, saving (Google Drive default) | `references/core-helpers.md` | set_ph, set_ph_sections, add_shape_text, add_code_block, footnotes, images, saving to Google Drive or local |
| Basic slide code (cover, chapter, columns, table) | `references/slide-patterns.md` | Sections 10-13: cover, chapter, 1-4 col, agenda, split, quote, tables, diagrams |
| Advanced visual patterns (hub-spoke, roadmap, etc.) | `references/patterns-enterprise.md` | 37 patterns: numbered steps, chevrons, pyramids, swimlanes, etc. |
| Snowflake icons for architecture slides | `references/icons.md` | Icon catalog, build_icon_index, place_icon, add_icon_with_label |
| Content writing standards | `references/content-standards.md` | Title philosophy, narrative voice, content bank, deck archetypes |
| Slide verification functions | `references/verification.md` | verify_slide(), verify_deck() — copy into every script |

### When to Load Which References

**Every deck build** requires these (always load):
- `references/core-branding.md` — colour constants
- `references/core-template.md` — layout map and safe zones
- `references/core-helpers.md` — all helper functions
- `references/slide-patterns.md` — basic slide code + tables + diagrams
- `references/patterns-enterprise.md` — 37 visual patterns (chevrons, hub-spoke, pyramids, timelines, stat callouts, etc.) — **MANDATORY for visual variety**
- `references/verification.md` — verification functions

**Load on demand** based on deck content:
- `references/icons.md` — when deck discusses Snowflake products/features
- `references/content-standards.md` — when writing content for consulting-grade quality review

---

## Visual Pattern Selection Guide (Quick Reference)

When choosing patterns for each slide, match content type to pattern:

| Content Type | Use Pattern | Reference |
|-------------|------------|-----------|
| Process / methodology (3-5 steps) | Chevron Process or Numbered Steps | `patterns-enterprise.md` 14.18, 14.6 |
| Key metrics / proof points | Icon Circle Grid or Stat Callout | `patterns-enterprise.md` 14.25, 14.7 |
| Project timeline / milestones | Milestone Timeline or Arrow Ribbon | `patterns-enterprise.md` 14.19, 14.24 |
| Ecosystem / capabilities map | Hub & Spoke or Hexagon Grid | `patterns-enterprise.md` 14.20, 14.23 |
| Strategic hierarchy / layers | Pyramid | `patterns-enterprise.md` 14.21 |
| Before/after transformation | Before/After or Two-Horizon | `patterns-enterprise.md` 14.5, 14.34 |
| Phased roadmap | Roadmap or Swimlane | `patterns-enterprise.md` 14.8, 14.29 |
| Maturity assessment | Maturity Grid or Bars | `patterns-enterprise.md` 14.28, 14.26 |
| Customer journey | Journey Map | `patterns-enterprise.md` 14.32 |
| Feature catalogue | Icon Column Cards or Grouped Menu | `patterns-enterprise.md` 14.37, 14.31 |
| Decision logic | Diamond Decision Tree | `patterns-enterprise.md` 14.27 |
| Comparison / options | Dual-Context or Before/After | `patterns-enterprise.md` 14.33, 14.5 |
| 30-60-90 plan | Milestone Scatter Grid | `patterns-enterprise.md` 14.30 |

**Visual variety rule (ENFORCED by `verify_deck()`)**: At least 40% of content slides MUST have visual elements (custom shapes, diagrams, tables, or icons). NEVER produce 3+ consecutive bullet-only slides. `verify_deck()` will REJECT the deck if this fails. Bullet-only decks are unacceptable — consulting firms alternate: bullets → diagram → table → callout → diagram.

---

## Rules Summary (Non-Negotiable)

### Layout & Template
1. Always use the Snowflake template — never `Presentation()` from scratch
2. Remove all sample slides before adding content (see `core-template.md`)
3. Slide dimensions: 10.00" × 5.63" — do not change
4. Never overlap decorative elements — waves, logos, accent shapes

### Colour & Font
5. Only theme colours (constants in `core-branding.md`) — no exceptions
6. Never override placeholder fonts/colours — let them inherit
7. Arial font ONLY on all custom shapes — `add_shape_text()` enforces this
8. Fill→Text contrast table is mandatory — **TEAL/ORANGE fills ALWAYS use DK1 text, NEVER WHITE**
8b. Every custom shape MUST have no visible outline — `add_shape_text()` does this automatically

### Typography & Text
9. ALL CAPS for slide titles and cover titles
10. Cover titles: ≤ 50 characters, max 3 lines, 44pt
11. Subtitles: ≤ 65 characters, one sentence
12. Font size 9-14pt for body text

### Content Structure
13. Heading + body pairs → `set_ph_sections()` (L0 bold DK2 + L1 bulleted)
14. Bold keyword items → `set_ph_bold_keywords()`
15. Flat lists → `set_ph_lines()` (only when all items equal importance)
16. Max 6-8 body lines per slide — split if more

### Safe Zones & Sizing
17. Content in safe zones per layout (see `core-template.md`)
18. Custom shapes start at ≥ 1.30" from top
19. Minimum 0.15" gap between shapes — no touching/overlapping
20. Tables: max 8 data rows per slide, width ≤ 9.10"
21. Content right edge ≤ 9.50", bottom ≤ 5.10"

### Shape Rules
22. EVERY custom shape via `add_shape_text()` — no manual creation
23. EVERY shape has `MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE`
24. Multi-line text: single string with `\n` — NEVER separate runs
25. Respect text density limits (see `core-helpers.md` Section 12.1)

### Content Quality
26. Content Blueprint mandatory before code (Phase 4)
27. Every title passes "So what?" test
28. No generic text ("Item 1", "TBD", "placeholder")
29. Feature status tagging mandatory (GA / Preview / Coming Soon)
30. At least 40% of content slides use visual patterns (≥40%, max 2 consecutive bullet-only)

### Verification
31. Run `verify_slide()` after every slide creation
32. Run `verify_deck()` before saving
33. Fix all violations before proceeding

---

## Code Organisation (Every Script)

```
imports → colour constants → helper functions (set_ph, add_shape_text, etc.)
→ build_icon_index(prs) → remove sample slides → content data structures
→ slide generation (with verify_slide after each) → verify_deck() → save
```

**Key points:**
- Build icon index BEFORE removing slides (icons live on template slides 66-68)
- Define all content as data structures first, then loop to create slides
- Content quality IS code quality — every string literal must be consulting-grade

---

## Deck Structure Best Practices

### Narrative Arc
```
HOOK → CONTEXT → TENSION → RESOLUTION → CALL TO ACTION
```

### Standard Flow
| # | Slide Type | Layout |
|---|-----------|--------|
| 1 | Cover | Layout 13 (primary) |
| 2 | Agenda | Layout 9 or visual pattern |
| 3 | Chapter Divider | Layout 18 |
| 4-N | Content | Mix of layouts + visual patterns |
| N+1 | Summary | Layout 7 (3-col) |
| N+2 | Thank You | Layout 28 |

**Rules:**
- Never open with a solution — establish the problem first
- Each chapter divider marks a narrative stage transition
- Alternate layout types for visual variety
- Last content slide before Thank You must have clear call to action

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Google Drive folder not found | Install Google Drive Desktop, or use `~/Downloads/` fallback |
| File not appearing in Google Drive | Wait 10-30s for sync; check Drive Desktop is running |
| Placeholder not found | Check layout map in `core-template.md` for correct PH indices |
| Text invisible on dark slide | Use WHITE for text on dark-bg layouts (DARK_BG_LAYOUTS: 9,10,18-22,23,25-28 + COVER_LAYOUTS: 13-17). `add_shape_text()` auto-corrects DK1→WHITE on these layouts. `verify_slide()` catches remaining violations. |
| Text overflows placeholder | Reduce font size or split across slides |
| Font not Arial | Use `add_shape_text()` — it sets font automatically |
| Shapes overlap decorative waves | Check safe zones in `core-template.md` |
| Wrong subtitle PH index | Layout 5→PH2, 6→PH3, 7→PH4, 8→PH5, 0/1/2/3/4→PH1 |
| Wall of text | Switch to `set_ph_sections()` for heading+body hierarchy |
| Table clips below footer | Max 8 data rows. Verify bottom ≤ 5.10". Paginate if needed. |
| Text overflows circles | Use density limits in `core-helpers.md`. Always set auto_size. |
| Off-brand colour | Use only named constants from `core-branding.md` |
| Merged/concatenated text in shapes | Use `\n` in single string via `add_shape_text()`. Never separate runs. |
| SQL/code text concatenated on one line | Use `add_code_block()` with lines as a list. See `core-helpers.md` Section 12.8. |
| Comparison table built from rectangles | Use native `add_table()`. NEVER individual rectangle shapes for grids. |
| Code block has Auto size: None | Always use `TEXT_TO_FIT_SHAPE`. `add_code_block()` enforces this. |
| 3+ categories in one placeholder | Use Layout 7 (3-col), callout boxes via `add_shape_text()`, or multi-column `set_ph_sections()`. See `slide-patterns.md` Section 12.8. |
| Deck is mostly bullet slides | Add visual patterns from `patterns-enterprise.md`. ≥40% of content slides need visuals. Use chevrons, stat callouts, hub-spoke, timelines. |
| Generic placeholder content | Write specific content with numbers, names, outcomes |
| White text on TEAL/ORANGE fill | Use DK1 (`#262626`) — these are light fills. See FILL_TEXT lookup in "MANDATORY" section above |
| Shapes have visible outlines/strokes | Use `add_shape_text()` which sets `shape.line.fill.background()`. NEVER build shapes manually |
| Cover title in wrong placeholder | Layout 13: PH[3]=title(44pt), PH[0]=subtitle(18pt), PH[2]=author(14pt). Title goes in PH[3], NOT PH[0] |
| Duplicate/repeated text on quote slides | Use `p.text = "LINE1\nLINE2"` — NEVER use multiple runs or `\x0b` vertical tabs |
| Shape labels run together ("CORTEXAI") | ALWAYS use `\n` between words in diagram shapes: `"CORTEX\nAI"`. Small shapes can't word-wrap |
| 10+ bullet lines in one placeholder | NEVER dump sections into PH[1]. Use Layout 7 (3-col), Layout 6 (2-col), or `add_shape_text()` boxes |
