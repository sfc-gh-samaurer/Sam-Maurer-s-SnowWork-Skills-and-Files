---
name: architecture-diagram-generator
description: "Generate Future State Architecture diagrams for Snowflake data platform engagements. Creates both editable SVG and high-fidelity PNG showing the full data flow from source systems through Bronze, Silver, Gold layers to AI & Consumption. Use when: architecture diagram, future state diagram, data flow diagram, platform architecture, medallion architecture visual, system diagram, data platform diagram. Triggers: architecture diagram, future state, data flow diagram, system architecture, platform diagram, medallion diagram, SVG diagram, architecture visual."
---

# Architecture Diagram Generator

Generate professional Future State Architecture diagrams (SVG + PNG) for Snowflake Medallion Architecture engagements. Shows the full data flow from source systems through Bronze, Silver, Gold layers to AI & Consumption, with phase assignments and governance overlay.

## Prerequisites

- `matplotlib` Python library available (for PNG generation)
- Source system inventory with phase assignments
- Silver and Gold domain lists with category groupings

## Workflow

### Step 1: Gather Inputs

**Ask** the user for:
1. **Customer name**
2. **Source systems** with phase assignments and categories (or reference Bronze Layer plan)
3. **Silver domains** with category groupings
4. **Gold domains** with category groupings
5. **AI & Consumption components** — which Cortex AI features, BI tools, Streamlit apps
6. **Governance requirements** — HIPAA, Horizon, RBAC, Data Masking
7. **Phase structure** — names, timelines, colors

If prior artifacts exist (Bronze plan, Ingestion-to-Consumption map), read them to auto-populate.

**⚠️ STOP**: Confirm source/domain lists and layout expectations.

### Step 2: Design the Diagram Layout

**Standard layout (left-to-right flow):**

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   SOURCE     │   │   BRONZE    │   │   SILVER    │   │    GOLD     │   │ AI & CONSUME│
│   SYSTEMS    │ → │   (Raw)     │ → │  (Curated)  │ → │(Consumption)│ → │             │
│  by Phase    │   │  by Schema  │   │  by Domain  │   │  by Domain  │   │ Cortex, BI  │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
                        ┌───────── GOVERNANCE BAR (Horizon, RBAC, Masking) ─────────┐
                        └───────── TIMELINE BAR (Phase 1 → Phase 2 → Phase 3) ──────┘
```

**Column proportions** (of total width):
- Sources: ~18%
- Bronze: ~16%
- Silver: ~22%
- Gold: ~22%
- AI/Consumption: ~18%

**Visual design principles:**
- Dark theme background (#0F1B2D or similar)
- Phase-colored source groupings
- Category groupings within Silver and Gold columns
- Flow arrows between columns
- Governance bar spanning Bronze through Gold
- Timeline bar at bottom showing phase progression
- Snowflake-branded accent colors

### Step 3: Generate SVG (Editable)

Create an SVG file with:
- 1920×1080 viewport (16:9 presentation-ready)
- All text as SVG `<text>` elements (editable in Figma, Illustrator, Inkscape)
- Rounded rectangles for system/domain boxes
- Phase-colored grouping backgrounds
- Flow arrows between columns
- Gradient fills for visual hierarchy
- Legend showing phase colors and ingestion pattern icons

**SVG structure:**
```xml
<svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <!-- Column headers -->
  <!-- Source Systems (grouped by phase) -->
  <!-- Bronze schemas -->
  <!-- Silver domains (grouped by category) -->
  <!-- Gold domains (grouped by category) -->
  <!-- AI & Consumption components -->
  <!-- Flow arrows -->
  <!-- Governance bar -->
  <!-- Timeline bar -->
  <!-- Legend -->
</svg>
```

**Color scheme (configurable):**
- Background: #0F1B2D (dark navy)
- Phase 1: #29B5E8 (Snowflake cyan)
- Phase 2: #7D44CF (purple)
- Phase 3: #D45B90 (pink)
- Parallel: #ED561B (orange)
- Bronze: #CD7F32 or #B87333
- Silver: #C0C0C0
- Gold: #FFD700
- Text: #FFFFFF (primary), #A0A0A0 (secondary)
- Governance: #11567F (dark blue)

### Step 4: Generate PNG (High-Fidelity)

Create a Python script using `matplotlib` that generates a high-resolution PNG:
- Size: 24×13.5 inches at 150 DPI (3600×2025 pixels)
- Matches SVG layout and content exactly
- Uses matplotlib patches (FancyBboxPatch, FancyArrowPatch)
- Anti-aliased text and shapes
- Suitable for embedding in PowerPoint or printing

**Key matplotlib techniques:**
- `fig.patch.set_facecolor()` for background
- `FancyBboxPatch(boxstyle='round,pad=0.01')` for rounded boxes
- `FancyArrowPatch(arrowstyle='->', connectionstyle='arc3')` for flow arrows
- `ax.text()` with fontsize scaling for readable text at all zoom levels
- Category grouping via background rectangles with alpha

### Step 5: Generate and Deliver

1. Write and save the SVG file directly
2. Write the Python matplotlib script
3. Execute to generate the PNG
4. Verify both files (read SVG, check PNG file size/dimensions)

**Output files:**
- `<Customer>_Future_State_Architecture.svg` — Editable in design tools
- `<Customer>_Future_State_Architecture.png` — High-fidelity raster
- `generate_architecture_diagram.py` — Rerunnable script

**⚠️ STOP**: Present both outputs for review.

## Stopping Points

- ✋ Step 1: Source/domain lists confirmed
- ✋ Step 5: Outputs reviewed

## Output

- **SVG**: Editable vector diagram (1920×1080, dark theme)
- **PNG**: High-fidelity raster image (3600×2025 pixels)
- **Python script**: Rerunnable matplotlib generator

## Diagram Scaling Guidelines

| Sources | Layout Adjustment |
|---------|------------------|
| <15 | Single column per phase group, larger boxes |
| 15-30 | Two sub-columns for sources, medium boxes |
| 30-50 | Dense layout, smaller text, category grouping essential |
| 50+ | Consider splitting into multiple diagrams by phase |

| Silver/Gold Domains | Layout Adjustment |
|-------|------------------|
| <10 | Full-width boxes with descriptions |
| 10-20 | Category-grouped, compact boxes |
| 20-35 | Dense grid within categories, abbreviated names |
| 35+ | Consider separate Silver and Gold diagrams |

## Reference: Boxout Health Example

- 47 source systems across 4 phases
- 12 Bronze schemas, 33 Silver domains (10 categories), 25 Gold domains (10 categories)
- AI & Consumption: Cortex Agent, Semantic Views, Streamlit, Tableau/PowerBI/Sigma, Marketplace
- Governance: Horizon, RBAC, Data Masking (HIPAA), DMFs, Resource Monitors
- Dark theme, 1920×1080 SVG, 24×13.5in PNG at 150 DPI
