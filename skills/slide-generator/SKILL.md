---
name: slide-generator
description: "Create professional PowerPoint presentations using the Snowflake template theme and native layouts. Use for: creating slides, building presentations, generating decks from notes, making sales decks, creating customer presentations, SOW decks, proposal decks, executive summaries. Triggers: create presentation, make slides, build deck, powerpoint, pptx, customer presentation, sales deck, proposal deck, SOW deck."
---

# Snowflake Slide Generator - Theme-Native Engine

Generate professional PowerPoint presentations using the official Snowflake template with native layouts and theme-extracted colors.

## How It Works

1. Loads the official Snowflake `.pptx` template (branding, logos, fonts, copyright footer)
2. Extracts theme colors and fonts dynamically from the template XML
3. Deletes all template slides - clean slate
4. Uses native template layouts where they match slide types (title, content, two_column, cards, agenda, quote, closing)
5. Falls back to Layout 12 (blank canvas) with clean text-only titles for complex visual slides
6. Result: Full Snowflake template theme compliance with native placeholders + bespoke layout for complex slides

## Automatic Validation (slide_validator.py)

The engine includes automatic pre-generation and post-generation validation, enabled by default.

### Pre-Generation: `validate_and_fix_slides()`
Runs before rendering. Auto-detects and corrects common JSON schema mismatches:

| Slide Type | Auto-Fix Applied |
|---|---|
| `executive_summary` | Converts `left_sections`/`right_sections` → `overview`/`engagement`/`workstreams`; converts `text`/`body` → `bullets` |
| `pricing_table` | Converts flat `rows` arrays → `roles` dicts with `{role, responsibilities[], hours, rate, price}` |
| `gantt_timeline` | Converts `name`→`label`, `programs`→`areas`, `end`→`duration`, `marker_week`→area milestones; fixes `spanning_bar` keys |
| `timeline` | Converts `total_weeks`→`total_units`; parses string durations like "Weeks 1-4" to numeric `start`/`duration` |
| `raci_table` / `risk_table` | Converts flat dict rows → `{"values": [...]}` format |

### Post-Generation: `detect_blank_slides()`
Opens the generated `.pptx` and checks each slide for meaningful content (text > 20 chars or tables). Skips title/section/closing slides. Reports any blank slides found.

### CLI Flag
- Default: validation ON
- `--no-validate`: skip both pre and post validation

## Key Features

- **Theme-native approach**: Colors, fonts, and layouts extracted from the Snowflake template
- **36 slide types**: Full range from basic content to charts, diagrams, infographics, and proposal layouts
- **Auto text fitting**: Font sizes scale based on content volume
- **Auto content splitting**: Long bullet lists split across slides with "(cont.)"
- **Section dividers**: Auto-inserted when `section` property changes
- **Phase color cycling**: 6 theme accent colors for cards, timeline bars, phase details
- **Template dimensions**: 10" x 5.625" (standard 16:9 Snowflake template)
- **Clean headers**: Text-only titles with small accent bar (no thick navy header bars)
- **Font**: Arial (from template theme)

## Workflow

### Step 1: Gather Requirements

Ask the user for:
1. **Presentation topic/title**
2. **Content source** - user-provided notes/outline, Snowflake docs, or Salesforce data
3. **Approximate number of slides**
4. **Specific sections** needed

### Step 2: Build the slides JSON

Create a JSON file with the slide content. The JSON has a `slides` array where each item is a slide with a `type` field.

### Step 3: Generate Presentation

```bash
python3 ~/.snowflake/cortex/skills/slide-generator/scripts/generate_slides.py \
  --slides-json /path/to/slides.json \
  --output /path/to/output.pptx
```

### Step 4: Verify and Deliver

1. Confirm the output file was created
2. Report the file path to the user

## Stopping Points

**STOP and ask the user** at these points:
1. After gathering requirements - confirm the slide outline before generating
2. After generation - ask if they want modifications

## All 36 Slide Types

### Basic Types
| Type | Description | Layout |
|------|-------------|--------|
| `title` | Cyan background, uppercase title, dotted wave decoration | Native Layout 0 |
| `section` | Dark blue bg, two-tone white+cyan title text, dotted wave | Native Layout 0 |
| `gradient_section` | Same as section (delegates to render_section) | Native Layout 0 |
| `agenda` | Numbered agenda items, white text on dark background | Native Layout 9 |
| `content` | Bullets or body text, auto-splits | Native Layout 5 |
| `two_column` | Side-by-side with native placeholders | Native Layout 6 |
| `framed_two_column` | Rounded-rect framed columns with colored borders | Blank canvas |
| `cards` | 2-4 cards (card/column/outcome styles) | Native 3/4-col or blank |
| `table` | Data table with navy header | Blank canvas |
| `timeline` | Gantt-style timeline bars | Blank canvas |
| `phase_detail` | Phase deep-dive with activities | Native Layout 5 |
| `quote` | Large centered quote | Native Layout 23 |
| `steps` | Numbered action items with circles | Blank canvas |
| `closing` | Cyan bg, two-tone "THANK YOU" text, dotted wave | Native Layout 0 |
| `venn` | Overlapping semi-transparent circles | Blank canvas |

### Visual & Diagram Types (NEW)
| Type | Description | Layout |
|------|-------------|--------|
| `process_flow` | Chevron arrow shapes for step workflows | Blank canvas |
| `kpi_dashboard` | Large metric numbers with labels and trends | Blank canvas |
| `quadrant` | 2x2 colored grid (SWOT, priority mapping) | Blank canvas |
| `hub_spoke` | Center hub circle with spokes to outer nodes | Blank canvas |
| `pyramid` | Stacked trapezoids for hierarchy/funnel | Blank canvas |
| `icon_grid` | Shape icons (hexagon, pentagon, etc.) with labels | Blank canvas |
| `horizontal_bars` | RACI-style colored segment bars | Blank canvas |
| `image` | Insert PNG/JPG image with optional caption | Blank canvas |
| `donut_chart` | Native donut/pie chart | Blank canvas |
| `bar_chart` | Native bar/column chart (stacked, grouped) | Blank canvas |
| `org_chart` | Connected boxes with hierarchy lines | Blank canvas |
| `watermark` | Background image with overlay text | Blank canvas |
| `connector_diagram` | Shapes connected with arrows/lines | Blank canvas |
| `grouped_shapes` | Shape groupings for infographics | Blank canvas |
| `service_options` | Multi-column pricing/service comparison layout | Blank canvas |
| `category_list` | Colored category badges with name/description items | Blank canvas |

### Proposal & Engagement Types (NEW)
| Type | Description | Layout |
|------|-------------|--------|
| `executive_summary` | Two-panel split: white left (overview + workstream cards) + dark blue right (checkmark outcomes) | Blank canvas |
| `engagement_approach` | Three-column phased layout with colored headers, arrow bullets, and outcome footer bars | Blank canvas |
| `gantt_timeline` | Detailed Gantt with milestone groups, colored arrow bars, triangle markers, and week columns | Blank canvas |
| `pricing_table` | Role/responsibility pricing table with arrow bullets, optional span notes, and total footer bar | Blank canvas |
| `proposal_timeline` | Multi-owner engagement timeline with colored bars per owner (SF/SI/Customer), phase sections, checkpoints, and footer scope notes | Blank canvas |

### Value Assessment Types (NEW)
| Type | Description | Layout |
|------|-------------|--------|
| `pillar_cards` | 2-4 executive summary pillar cards with accent bar, stat metric, and bullets | Blank canvas |
| `workstream_lanes` | Horizontal tinted lanes for parallel workstreams with status badges | Blank canvas |
| `phase_circles` | Row of circular phase indicators with supporting tables below | Blank canvas |
| `comparison_tables` | Two tables side by side with conclusion callout | Blank canvas |
| `team_photo` | Two-group team photo grid — circular profile photos with white border, name + role, dark blue bg, vertical divider; Slack photos auto-fetched by email | Blank canvas |

## JSON Schema Reference

```json
{
  "slides": [
    { "type": "slide_type", ...fields }
  ]
}
```

### Slide Type: `title`
Cyan background with Snowflake logo (white, top-left), large white bold title (mixed case), smaller black bold subtitle below, and black bold date positioned lower on the slide. Wave decoration and copyright footer from template.
```json
{
  "type": "title",
  "title": "Snowflake Professional Services Proposal",
  "subtitle": "Realizing BI, AI & ML business outcomes on the Snowflake Platform",
  "date": "CONFIDENTIAL  |  March 2026"
}
```

### Slide Type: `section`
Dark blue background with two-tone text (white + cyan last word), dotted wave decoration. Supports optional `number` field for numbered section dividers (large accent-colored number displayed above title — common in executive migration proposals).
```json
{
  "type": "section",
  "title": "Section Name",
  "subtitle": "Optional subtitle (shown in light teal)",
  "number": "01"
}
```

### Slide Type: `gradient_section`
```json
{
  "type": "gradient_section",
  "title": "Section Title",
  "subtitle": "Optional subtitle",
  "color1": "#11567F",
  "color2": "#29B5E8",
  "angle": 135
}
```

### Slide Type: `agenda`
```json
{
  "type": "agenda",
  "title": "Agenda",
  "items": ["Topic 1", "Topic 2", "Topic 3"]
}
```

### Slide Type: `content`
```json
{
  "type": "content",
  "title": "Slide Title",
  "bullets": ["Point 1", "Point 2"]
}
```

### Slide Type: `two_column`
Also used for **workstream detail slides** in executive migration proposals — left column is "WHAT'S INCLUDED", right column is "KEY ASSUMPTIONS & PRICING", `callout` holds the bottom emphasis note.
```json
{
  "type": "two_column",
  "title": "Slide Title",
  "left_title": "LEFT HEADER",
  "left_bullets": ["Item 1", "Item 2"],
  "right_title": "RIGHT HEADER",
  "right_bullets": ["Item A", "Item B"],
  "callout": "Optional callout text"
}
```

**Workstream detail pattern** (title format: "Workstream Name  |  $Price  |  Owner"):
```json
{
  "type": "two_column",
  "title": "Discovery & Analysis  |  $160K  |  Snowflake SD + Partner",
  "left_title": "WHAT'S INCLUDED",
  "left_bullets": ["Bullet 1", "Bullet 2"],
  "right_title": "KEY ASSUMPTIONS & PRICING",
  "right_bullets": ["Assumption 1", "Pricing line"],
  "callout": "One-sentence emphasis note."
}
```

### Slide Type: `framed_two_column`
```json
{
  "type": "framed_two_column",
  "title": "Slide Title",
  "left_title": "LEFT HEADER",
  "left_color": "#29B5E8",
  "left_bullets": ["Item 1", "Item 2"],
  "right_title": "RIGHT HEADER",
  "right_color": "#7D44CF",
  "right_bullets": ["Item A", "Item B"],
  "callout": "Optional callout text"
}
```

### Slide Type: `cards`
Three styles: `card` (numbered circles), `column` (colored header + bullets), `outcome` (header + description).
```json
{
  "type": "cards",
  "title": "Title",
  "cards": [
    {
      "style": "column",
      "title": "Card Title",
      "bullets": ["Bullet 1", "Bullet 2"],
      "color": "#29B5E8"
    }
  ]
}
```

### Slide Type: `table`
```json
{
  "type": "table",
  "title": "Table Title",
  "headers": ["Col 1", "Col 2"],
  "rows": [["A", "B"], ["C", "D"]],
  "col_widths": [5.0, 4.0],
  "callout": "Optional note"
}
```

### Slide Type: `timeline`
```json
{
  "type": "timeline",
  "title": "16-Week Roadmap",
  "total_units": 16,
  "phases": [
    {"name": "Phase 1", "start": 1, "duration": 4, "color": "#29B5E8"}
  ],
  "note": "Optional note"
}
```

### Slide Type: `phase_detail`
```json
{
  "type": "phase_detail",
  "title": "Phase 1: Kickoff",
  "weeks": "Week 1",
  "phase_index": 0,
  "activities": ["Activity 1", "Activity 2"],
  "deliverable": "Project Plan"
}
```

### Slide Type: `venn`
```json
{
  "type": "venn",
  "title": "Venn Diagram",
  "circles": [
    {"label": "Circle 1\nDetail", "color": "#7D44CF"},
    {"label": "Circle 2\nDetail", "color": "#29B5E8"}
  ],
  "center_text": "Overlap Label",
  "items": ["Footer item 1", "Footer item 2"]
}
```

### Slide Type: `process_flow`
Chevron arrow shapes for step-by-step workflows.
```json
{
  "type": "process_flow",
  "title": "Delivery Lifecycle",
  "steps": [
    {"label": "Discovery", "description": "Requirements\nAnalysis", "color": "#11567F"},
    {"label": "Build", "description": "Implementation", "color": "#29B5E8"}
  ],
  "callout": "Optional note"
}
```

### Slide Type: `kpi_dashboard`
Large metric numbers with labels and trend indicators.
```json
{
  "type": "kpi_dashboard",
  "title": "Key Metrics",
  "kpis": [
    {"value": "98%", "label": "Uptime", "trend": "+2%", "color": "#29B5E8", "subtitle": "vs. last quarter"},
    {"value": "4.2M", "label": "Records", "trend": "+500K", "color": "#7D44CF"}
  ]
}
```

### Slide Type: `quadrant`
2x2 colored grid for SWOT analysis, priority mapping, etc.
```json
{
  "type": "quadrant",
  "title": "Priority Matrix",
  "x_label": "Impact",
  "y_label": "Effort",
  "quadrants": [
    {"label": "Quick Wins", "items": ["Item 1", "Item 2"], "color": "#29B5E8"},
    {"label": "Strategic", "items": ["Item 3"], "color": "#7D44CF"},
    {"label": "Fill-Ins", "items": ["Item 4"], "color": "#71D3DC"},
    {"label": "Deprioritize", "items": ["Item 5"], "color": "#FF9F36"}
  ]
}
```

### Slide Type: `hub_spoke`
Center hub circle with radiating spokes to outer nodes.
```json
{
  "type": "hub_spoke",
  "title": "Engagement Model",
  "hub": "Core\nConcept",
  "spokes": [
    {"label": "Spoke 1", "color": "#29B5E8"},
    {"label": "Spoke 2", "color": "#7D44CF"}
  ]
}
```

### Slide Type: `pyramid`
Stacked trapezoids for hierarchy or funnel visualization.
```json
{
  "type": "pyramid",
  "title": "Maturity Model",
  "levels": [
    {"label": "Top Level", "color": "#11567F"},
    {"label": "Middle", "description": "More detail", "color": "#29B5E8"},
    {"label": "Foundation", "color": "#71D3DC"}
  ]
}
```

### Slide Type: `icon_grid`
Shape icons (hexagons, pentagons, etc.) with labels and descriptions.
```json
{
  "type": "icon_grid",
  "title": "Capabilities",
  "shape": "hexagon",
  "columns": 4,
  "icons": [
    {"label": "Security", "description": "RBAC & DDM", "number": "01", "color": "#29B5E8"}
  ]
}
```

### Slide Type: `horizontal_bars`
RACI-style colored segment bars with legend.
```json
{
  "type": "horizontal_bars",
  "title": "Responsibility View",
  "bars": [
    {
      "label": "Platform",
      "segments": [
        {"value": 8, "label": "Snowflake", "color": "#29B5E8"},
        {"value": 2, "label": "Partner", "color": "#7D44CF"}
      ]
    }
  ],
  "legend": [
    {"label": "Snowflake", "color": "#29B5E8"},
    {"label": "Partner", "color": "#7D44CF"}
  ]
}
```

### Slide Type: `image`
Insert a PNG/JPG image with optional title and caption.
```json
{
  "type": "image",
  "title": "Architecture Diagram",
  "image_path": "/path/to/image.png",
  "caption": "Figure 1: System Architecture"
}
```

### Slide Type: `donut_chart`
Native donut/pie chart.
```json
{
  "type": "donut_chart",
  "title": "Distribution",
  "categories": ["Cat A", "Cat B", "Cat C"],
  "values": [45, 30, 25],
  "series_name": "Share",
  "colors": ["#29B5E8", "#7D44CF", "#FF9F36"]
}
```

### Slide Type: `bar_chart`
Native bar or column chart (supports stacked, horizontal).
```json
{
  "type": "bar_chart",
  "title": "Quarterly Results",
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [
    {"name": "Revenue", "values": [100, 120, 140, 160]},
    {"name": "Cost", "values": [80, 85, 90, 95]}
  ],
  "colors": ["#29B5E8", "#FF9F36"],
  "stacked": false,
  "horizontal": false
}
```

### Slide Type: `org_chart`
Connected boxes with hierarchy lines.
```json
{
  "type": "org_chart",
  "title": "Team Structure",
  "nodes": [
    {"id": "ceo", "label": "CEO", "role": "Executive", "color": "#11567F"},
    {"id": "vp1", "label": "VP Eng", "parent": "ceo", "color": "#29B5E8"},
    {"id": "vp2", "label": "VP Sales", "parent": "ceo", "color": "#7D44CF"}
  ]
}
```

### Slide Type: `watermark`
Background image with semi-transparent overlay and text.
```json
{
  "type": "watermark",
  "title": "Overlay Title",
  "subtitle": "Subtitle text",
  "image_path": "/path/to/background.png"
}
```

### Slide Type: `connector_diagram`
Shapes connected with arrows/lines.
```json
{
  "type": "connector_diagram",
  "title": "Data Flow",
  "boxes": [
    {"id": "src", "label": "Source", "x": 1, "y": 2, "width": 1.8, "height": 0.6, "color": "#29B5E8"},
    {"id": "dst", "label": "Target", "x": 7, "y": 2, "width": 1.8, "height": 0.6, "color": "#7D44CF"}
  ],
  "connections": [
    {"from": "src", "to": "dst", "label": "ETL", "arrow": true}
  ]
}
```

### Slide Type: `grouped_shapes`
Shape groupings for infographics.
```json
{
  "type": "grouped_shapes",
  "title": "Categories",
  "groups": [
    {
      "label": "Group A",
      "shapes": [
        {"shape": "hexagon", "label": "Item 1", "color": "#29B5E8"},
        {"shape": "hexagon", "label": "Item 2", "color": "#7D44CF"}
      ]
    }
  ]
}
```

### Slide Type: `executive_summary`
Two-panel split layout: white left panel with overview text and workstream cards, dark blue right panel with checkmark outcome items.
```json
{
  "type": "executive_summary",
  "title": "Executive Summary",
  "left_width": 0.6,
  "overview": {
    "heading": "OVERVIEW",
    "text": "Customer background and context description."
  },
  "engagement": {
    "heading": "PS ENGAGEMENT OVERVIEW",
    "subtitle": "Brief engagement description",
    "workstreams": [
      {
        "title": "Workstream 1",
        "icon": "\u2601",
        "color": "#29B5E8",
        "bullets": ["Activity 1", "Activity 2"]
      }
    ]
  },
  "outcomes": {
    "heading": "ENGAGEMENT OUTCOMES",
    "items": [
      "Outcome description 1",
      "Outcome description 2"
    ]
  }
}
```

### Slide Type: `engagement_approach`
Three-column phased layout with colored header bars, description text, arrow-bulleted activity areas, and colored footer bars with outcome text.
```json
{
  "type": "engagement_approach",
  "title": "Engagement Approach",
  "subtitle": "Optional description of the approach",
  "phases": [
    {
      "label": "Phase 1: Discover",
      "header_color": "#29B5E8",
      "description": "Phase description text",
      "activities_label": "Activity Areas:",
      "activities": ["Activity 1", "Activity 2"],
      "bullet_char": "\u2192",
      "footer_color": "#D45B90",
      "outcome": "Key Outcome"
    }
  ]
}
```

### Slide Type: `gantt_timeline`
Detailed Gantt chart with milestone groups (colored left bars), program area rows, numbered week columns, colored duration bars, and orange triangle milestone markers.
```json
{
  "type": "gantt_timeline",
  "title": "High Level Timeline",
  "subtitle": "Optional subtitle",
  "legend": "Milestone Achieved",
  "total_weeks": 17,
  "milestones": [
    {
      "label": "Milestone Group 1",
      "color": "#29B5E8",
      "areas": [
        {
          "name": "Program Area",
          "start": 1,
          "duration": 4,
          "color": "#29B5E8",
          "bar_label": "Optional bar text",
          "milestones": [4]
        }
      ]
    }
  ],
  "spanning_bar": {
    "label": "Program Management / Tracking",
    "color": "#29B5E8",
    "start": 1,
    "duration": 17,
    "milestones": [17]
  },
  "footnote": "Optional footnote text"
}
```

### Slide Type: `pricing_table`
Role/responsibility pricing table with arrow-bulleted responsibilities, optional span notes across numeric columns, and a dark teal total footer bar.
```json
{
  "type": "pricing_table",
  "title": "Resource Estimates and Proposed Fees",
  "subtitle": "The team below represents a blend of strategic and technical resources...",
  "columns": ["Role", "Responsibilities", "Hours*", "Rate", "Price (USD)"],
  "col_widths": [0.15, 0.50, 0.10, 0.10, 0.15],
  "roles": [
    {
      "role": "Activation Solutions Engineer",
      "responsibilities": [
        "Onboarding enablement and best practices",
        "Initial platform configuration support"
      ],
      "span_text": "(offered as a complimentary onboarding benefit)"
    },
    {
      "role": "Solutions Architect (SA)",
      "responsibilities": [
        "Technical design and architecture",
        "Data pipeline development",
        "Performance optimization"
      ],
      "hours": "180",
      "rate": "$325/hr.",
      "price": "$58,500"
    }
  ],
  "total_label": "Total Engagement Fees",
  "total_value": "$73,500 USD",
  "footnote": "*Hours are estimated and may vary based on scope"
}
```

### Slide Type: `proposal_timeline`
Multi-owner engagement timeline with colored bars per owner (Snowflake, SI Partner, Customer), phase sections, checkpoint diamonds, and footer scope notes. Owner colors map to Snowflake theme: SF=accent1 (cyan), SI=accent4 (orange), Customer=accent5 (purple), Checkpoints=accent3 (teal).

**Language guardrail for Snowflake (SF) activities**: Use ADVISORY language only — "architecture review" not "architecture build", "performance advisory" not "performance tuning", "enablement" not "implementation", "quality gate checkpoints" not "quality assurance". Snowflake does NOT own: pipeline dev, data modeling, production ops, KT, handoff, deployment.

```json
{
  "type": "proposal_timeline",
  "title": "Engagement Timeline",
  "subtitle": "16-Week Rollout | Snowflake Service Delivery + SI Partner | Target: Q4 Go-Live",
  "time_unit": "Weeks",
  "total_periods": 16,
  "owners": [
    {"key": "sf", "label": "Snowflake (SF)"},
    {"key": "si", "label": "SI Partner"},
    {"key": "wd", "label": "Customer"},
    {"key": "checkpoint", "label": "Checkpoint"}
  ],
  "phases": [
    {
      "label": "Phase 1 — Discovery & Alignment",
      "activities": [
        {"owner": "sf", "owner_prefix": "SF", "label": "Kickoff workshops & stakeholder alignment", "start": 1, "end": 2, "bar_text": "Kickoff & Deep Dive"},
        {"owner": "sf", "owner_prefix": "SF", "label": "Current-state architecture assessment", "start": 1, "end": 2, "bar_text": "Arch Assessment"},
        {"owner": "si", "owner_prefix": "SI", "label": "Team mobilization & project plan baseline", "start": 1, "end": 2, "bar_text": "Team Mobilization"},
        {"owner": "wd", "owner_prefix": "WD", "label": "Access provisioning & stakeholder scheduling", "start": 1, "end": 3, "bar_text": "Access & Scheduling"}
      ]
    },
    {
      "label": "Phase 2 — Build & Integration",
      "activities": [
        {"owner": "sf", "owner_prefix": "SF", "label": "RBAC role hierarchy & governance advisory", "start": 3, "end": 6, "bar_text": "RBAC & Governance"},
        {"owner": "si", "owner_prefix": "SI", "label": "Pipeline development & data modeling", "start": 3, "end": 12, "bar_text": "Pipeline Dev → Data Models → Testing"},
        {"owner": "wd", "owner_prefix": "WD", "label": "Data validation & business logic review", "start": 8, "end": 14, "bar_text": "Validation → Review → UAT Sign-off"}
      ]
    }
  ],
  "checkpoints": [
    {"period": 2, "label": "Scope &\nRoadmap\nConfirmed"},
    {"period": 8, "label": "Platform\nBaselined"},
    {"period": 14, "label": "UAT\nComplete"},
    {"period": 16, "label": "Go-Live\nReady"}
  ],
  "footer_notes": [
    "SF scope: Architecture advisory, enablement, reviews & quality gates",
    "SI scope: End-to-end pipeline development, data models, testing & deployment",
    "Customer: Program management, access provisioning, validation & operational ownership"
  ]
}
```

### Value Assessment Layout Types

These 4 types produce the custom layouts used in value assessment / business case decks. They use full-width header bars, tinted fills, and metric-heavy designs optimized for executive audiences.

### Slide Type: `pillar_cards`
Executive summary with 2-4 pillar cards. Each card has a colored accent top bar, tag, title, large stat metric, stat label, and bullet list.
```json
{
  "type": "pillar_cards",
  "title": "Executive Summary",
  "subtitle": "Optional italic subtitle below the header bar",
  "pillars": [
    {
      "tag": "PILLAR 1",
      "title": "Operational Efficiency",
      "stat": "400+",
      "stat_label": "hours reclaimed for engineering teams",
      "color": "#29B5E8",
      "bullets": ["Engineers stay on roadmap items", "Migration offloaded to PS"]
    },
    {
      "tag": "PILLAR 2",
      "title": "Accelerated Time-to-Value",
      "stat": "12+",
      "stat_label": "weeks faster than internal execution",
      "color": "#71D3DC",
      "bullets": ["Gold layer live in weeks", "Full conversion in parallel"]
    },
    {
      "tag": "PILLAR 3",
      "title": "Risk Mitigation",
      "stat": "Fixed Fee",
      "stat_label": "budget predictability",
      "color": "#FF9F36",
      "bullets": ["Best-practice architecture Day 1", "DMVA automated validation"]
    }
  ],
  "conclusion": "Optional bold conclusion text at the bottom"
}
```

### Slide Type: `workstream_lanes`
Horizontal tinted workstream lanes with status badges. Used for parallel workstream visualizations (e.g., gold layer replication + code conversion running in parallel).
```json
{
  "type": "workstream_lanes",
  "title": "The Gold Layer Advantage",
  "subtitle": "Optional italic description",
  "lanes": [
    {
      "tag": "WORKSTREAM 1",
      "title": "Gold Layer Replication (DMVA)",
      "description": "300 gold tables validated & available for data sharing",
      "color": "#71D3DC",
      "badge": "DATA SHARING LIVE",
      "badge_x": 6.5,
      "badge_width": 1.8,
      "badge_subtitle": "Weeks 4-6",
      "outcome": "Business users access\nnew data immediately",
      "outcome_x": 8.5,
      "outcome_width": 2.5
    },
    {
      "tag": "WORKSTREAM 2",
      "title": "Full Code Conversion (SnowConvert + CoCo)",
      "description": "SPs, views, DDL converted to Snowflake-native code",
      "color": "#11567F",
      "badge": "FULL MIGRATION COMPLETE",
      "badge_x": 7.0,
      "badge_width": 2.5,
      "badge_subtitle": "Weeks 14-32"
    }
  ],
  "key_title": "KEY BUSINESS VALUE",
  "key_bullets": [
    "Business users get data sharing access within weeks",
    "No disruption to existing workflows during conversion"
  ]
}
```

### Slide Type: `phase_circles`
Row of circular phase indicators with optional supporting tables below. Used for delivery approach overviews.
```json
{
  "type": "phase_circles",
  "title": "PS Delivery Approach — Main Cluster (~18 weeks)",
  "phases": [
    {"label": "Phase 1", "name": "Discovery &\nAssessment", "weeks": "Wk 1-2", "color": "#11567F"},
    {"label": "Phase 2", "name": "Platform &\nDMVA Setup", "weeks": "Wk 3-4"},
    {"label": "Phase 3", "name": "CoCo-Powered\nConversion", "weeks": "Wk 3-8"},
    {"label": "Phase 4", "name": "Data Migration\n& Validation", "weeks": "Wk 7-10"},
    {"label": "Phase 5", "name": "UAT\nSupport", "weeks": "Wk 10-12"},
    {"label": "Phase 6", "name": "Cutover &\nKT", "weeks": "Wk 12-14"}
  ],
  "tables": [
    {
      "title": "Two Parallel Workstreams",
      "headers": ["Workstream", "Focus", "Key Tools", "Owner"],
      "rows": [
        ["WS1: Gold Layer", "Data validation", "DMVA", "Architect"],
        ["WS2: Code Conversion", "SPs, views, DDL", "SnowConvert + CoCo", "Consultant"]
      ],
      "col_widths": [2.5, 2.8, 2.2, 1.5]
    },
    {
      "title": "",
      "headers": ["Role", "Rate", "Hours", "Cost"],
      "rows": [
        ["Migration Architect", "$335/hr", "339 hrs", "$113,565"],
        ["Delivery Consultant", "$180/hr", "330 hrs", "$59,400"],
        ["SDM", "$260/hr", "133 hrs", "$34,580"],
        ["TOTAL", "", "802 hrs", "$207,545"]
      ],
      "col_widths": [3.5, 1.8, 1.8, 2.0]
    }
  ]
}
```

### Slide Type: `comparison_tables`
Two tables placed side by side with optional conclusion callout. Supports both full-width header bar and standard title styles. Used for side-by-side scope comparisons.
```json
{
  "type": "comparison_tables",
  "title": "The Stored Procedures Challenge",
  "header_style": "bar",
  "subtitle": "Optional subtitle text",
  "left_table": {
    "headers": ["Main Cluster (101 SPs)", "DIY + CoCo", "PS + CoCo"],
    "rows": [
      ["Conversion speed per SP", "2-4 hours", "15-90 min"],
      ["Total SP effort", "200-400 hrs", "123 hrs"],
      ["First-pass success rate", "60-75%", "90-95%"]
    ],
    "col_widths": [1.8, 1.3, 1.3]
  },
  "right_table": {
    "headers": ["All 3 Clusters (469 SPs)", "DIY + CoCo", "PS + CoCo"],
    "rows": [
      ["Conversion speed per SP", "2-4 hours", "15-90 min"],
      ["Total SP effort", "900-1,800 hrs", "562 hrs"],
      ["First-pass success rate", "60-75%", "90-95%"]
    ],
    "col_widths": [1.8, 1.3, 1.3]
  },
  "table_width": 4.3,
  "table_gap": 0.4,
  "conclusion": "Optional bold conclusion text below both tables"
}
```

### Slide Type: `quote`
```json
{
  "type": "quote",
  "quote": "Important quote text",
  "attribution": "Source, Year"
}
```

### Slide Type: `steps`
```json
{
  "type": "steps",
  "title": "Next Steps",
  "steps": [
    {"title": "Step 1", "description": "Description"},
    {"title": "Step 2", "description": "Description"}
  ]
}
```

### Slide Type: `closing`
Cyan background with two-tone "THANK YOU" text (dark blue + white), dotted wave decoration.
```json
{
  "type": "closing",
  "title": "Thank You",
  "subtitle": "Snowflake Services Delivery",
  "message": "We look forward to partnering with you."
}
```

### Slide Type: `service_options`
Multi-column pricing/service comparison with sections, bullet items, and optional scope clarifications bar.
```json
{
  "type": "service_options",
  "title": "Service Options",
  "subtitle": "Choose the right engagement model",
  "options": [
    {
      "name": "Option A",
      "price": "$150K",
      "duration": "8 weeks",
      "tagline": "Quick start",
      "sections": [
        {
          "header": "Includes",
          "color": "29B5E8",
          "items": ["Item 1", "Item 2"]
        }
      ],
      "footnote": "* Subject to scoping"
    }
  ],
  "clarifications": "Optional scope clarifications text"
}
```

### Slide Type: `category_list`
Colored category badges with name/description items in a structured list.
```json
{
  "type": "category_list",
  "title": "Service Categories",
  "categories": [
    {
      "label": "Category A",
      "color": "29B5E8",
      "items": [
        {"name": "Item Name", "description": "Item description"}
      ]
    }
  ]
}
```

### Slide Type: `team_photo`
Two-group team photo grid with circular profile photos, dark blue background, vertical divider, name and role text. Photos are auto-fetched from Slack using the `SLACK_BOT_TOKEN` environment variable when `slack_email` is provided. Falls back to a filled circle with initials if no photo is found.

```json
{
  "type": "team_photo",
  "title": "Your Engagement Team",
  "groups": [
    {
      "label": "Account Team",
      "members": [
        { "name": "Rachel Regan", "role": "Account Executive", "slack_email": "rachel.regan@snowflake.com" },
        { "name": "CV Briggler", "role": "Solutions Architect", "slack_email": "cv.briggler@snowflake.com" },
        { "name": "Kelsey Gonzalez", "role": "AI/ML Specialist Architect", "slack_email": "kelsey.gonzalez@snowflake.com" },
        { "name": "Jim Lebonitte", "role": "Enterprise Architect", "slack_email": "jim.lebonitte@snowflake.com" }
      ]
    },
    {
      "label": "Service Delivery Team",
      "members": [
        { "name": "Michael Kelly", "role": "Practice Manager", "slack_email": "michael.kelly@snowflake.com" },
        { "name": "Stephanie Vrona", "role": "Service Delivery Manager", "slack_email": "stephanie.vrona@snowflake.com" },
        { "name": "Wole Babalola", "role": "Solutions Architect", "slack_email": "wole.babalola@snowflake.com" },
        { "name": "Jiri Prochazka", "role": "Solutions Architect", "slack_email": "jiri.prochazka@snowflake.com" }
      ]
    }
  ]
}
```

**Notes:**
- Each group supports 1–4 members; 4 members renders as a 2×2 grid, fewer as a single row
- `slack_email` triggers Slack photo lookup via `SLACK_BOT_TOKEN` env var; omit or leave blank to use initials placeholder
- `photo_url` can be specified directly to skip Slack lookup
- Always use on kickoff decks, Snow Day decks, and introductory proposal slides

## Phase Color Cycling

Cards, timeline bars, and phase_detail slides auto-assign colors from the template theme accent palette. Override with `"color": "#hex"` on any item.

Theme colors: accent1 (#29B5E8 Cyan), accent2 (#11567F Teal), accent3 (#71D3DC Light Teal), accent4 (#FF9F36 Orange), accent5 (#7D44CF Purple), accent6 (#D45B90 Pink).

## Deck Template Patterns

### Engagement Kickoff Deck Pattern
Use for project kickoff presentations at the start of an SD engagement.
1. `title` (engagement name + customer | date) > 2. `agenda` > 3. `team_photo` (Account Team + SD Team with Slack photos) > 4. `section` (Scope, Assumptions & Dependencies) > 5. `content` (scope of work) > 6. `engagement_approach` (3 phases) > 7. `gantt_timeline` (program timeline) > 8. `section` (Engagement Logistics) > 9. `two_column` (touchpoints + resourcing) > 10. `next_steps_proposal` > 11. `closing`
**Reference:** `assets/reference_decks/empower_kickoff_deck.json` — Empower Financial kickoff. [Google Slides](https://docs.google.com/presentation/d/1wGbUap0JUtqDZ1EzU09xK_eDht-yTV4kse0OW_0a684)

### Snow Day / Technical Discovery Deck Pattern
Use for Snow Days, account discovery sessions, or "art of the possible" demos.
1. `title` > 2. `agenda` > 3. `team_photo` (Account Team + SD Team) > 4. `section` (Identified Use Cases) > 5. `pillar_cards` (top use cases with stats) > 6. One `content` slide per use case flow > 7. `section` (From Concept to Reality) > 8. `engagement_approach` (3-phase SD approach) > 9. `cards` (why SD) > 10. `closing`
**Reference:** `assets/reference_decks/ball_hort_snow_day.json` — Ball Hort Snow Day. [Google Slides](https://docs.google.com/presentation/d/1KxYmBmLllyhsorBhJw5IHnVsY2D1Vj45a_mR-TMpHrQ)

### SOW Deck Pattern
1. `title` > 2. `agenda` > 3-4. `section` + `two_column` > 5-6. `section` + `cards` > 7-8. `section` + `timeline` + `phase_detail` > 9-10. `section` + `table` (milestones) > 11. `steps` > 12. `closing`

### Partner Engagement Deck Pattern
1. `title` > 2. `agenda` > 3. `gradient_section` > 4. `venn` > 5. `framed_two_column` > 6. `hub_spoke` > 7-11. Per model: `section` + `process_flow` + `table` + `cards` > 12. `horizontal_bars` > 13. `table` (RACI) > 14. `framed_two_column` (takeaway) > 15. `closing`

### Scoping Deck Pattern
1. `title` > 2. `agenda` > 3. `section` + `cards` (context) > 4. `section` + `table` (inventory) + `process_flow` (as-is) > 5. `section` + `horizontal_bars` (RACI) > 6-9. `section` + `framed_two_column` per workstream > 10. `section` + `process_flow` (to-be) + `table` (RACI matrix) > 11. `section` + `icon_grid` (next steps) > 12. `closing`

### Proposal Deck Pattern
1. `title` > 2. `agenda` > 3. `executive_summary` (overview + outcomes) > 4. `engagement_approach` (phased activities) > 5. `gantt_timeline` (detailed timeline) > 6. `proposal_timeline` (multi-owner rollout timeline with SF/SI/Customer bars) > 7-9. `section` + `cards`/`two_column` per workstream > 10. `pricing_table` (resource estimates & fees) > 11. `steps` (next steps) > 12. `closing`

### Executive Migration Proposal Pattern
Use for board-level or executive migration proposals with numbered sections, workstream detail appendix, and fixed-fee/T&M hybrid pricing.
1. `title` > 2. `agenda` (numbered sections as items) > 3. `section` (number: "01") + `executive_summary` + `cards` (migration landscape) > 4. `section` (number: "02") + `cards` (strategic reasons, 4 columns) > 5. `section` (number: "03") + `engagement_approach` (3-phase) + `cards` (what's migrating) + `gantt_timeline` + `cards` (governance model) + `framed_two_column` (risks & mitigations) > 6. `section` (number: "04") + `kpi_dashboard` (ROI metrics) > 7. `section` (number: "05") + `content` (decisions required) > 8. `section` (number: "06") + `table` (RACI) + N×`two_column` (workstream details: title includes name|price|owner) + `content` (pricing assumptions) > 9. `closing`

**Reference deck:** `assets/jdpower_exec_presentation.json` — JD Power BigQuery + Redshift → Snowflake migration, 29 slides, $3.1M+ engagement. [Google Slides source](https://docs.google.com/presentation/d/1Kqy1E94LolxW6TAFGf1ud2cauekp1Ck8BpsNli6ZaDQ/edit)

### Value Assessment Deck Pattern
Use for DIY vs. Professional Services business case decks with dual-scope options.
1. `title` > 2. `pillar_cards` (exec summary: 3 pillars) > 3. `workstream_lanes` (gold layer advantage) > 4-5. `kpi_dashboard` (migration overview × 2 scopes) > 6. `table` (resource constraints) > 7-8. `table` (PS acceleration × 2 scopes) > 9. `comparison_tables` (SP challenge side-by-side) > 10. `cards` (what PS brings) > 11-12. `phase_circles` (delivery approach × 2 scopes) > 13-14. `framed_two_column` (DIY costs & risks × 2) > 15-16. `table` + `kpi_dashboard` (savings × 2) > 17. `table` (risk comparison)

## Output

- File: PowerPoint (.pptx) at user-specified location
- Default: `~/Downloads/presentation_YYYYMMDD_HHMMSS.pptx`
- Template: 10" x 5.625" (standard Snowflake 16:9)

## Engine Files

- `scripts/generate_slides.py` - **Default engine** (v3 enhanced, 36 types)
- `scripts/generate_slides_v3.py` - Original v3 source (14 types, backup)
- `scripts/generate_slides_v2.py` - Legacy v2 hybrid engine

## Reference Decks (assets/)

| File | Description | Slides | Google Slides |
|------|-------------|--------|---------------|
| `partner_services_deck.json` | Partners + Snowflake SD — Greenfield, Migration, AI/ML engagement models | 26 | — |
| `jdpower_exec_presentation.json` | JD Power executive migration proposal — BigQuery + Redshift → Snowflake, 8 workstreams, $3.1M+ hybrid T&M+fixed-fee | 29 | [Link](https://docs.google.com/presentation/d/1Kqy1E94LolxW6TAFGf1ud2cauekp1Ck8BpsNli6ZaDQ) |
| `reference_decks/empower_kickoff_deck.json` | Engagement kickoff deck — **team_photo** slide, scope, program timeline, engagement logistics, next steps | 11 | [Link](https://docs.google.com/presentation/d/1wGbUap0JUtqDZ1EzU09xK_eDht-yTV4kse0OW_0a684) |
| `reference_decks/philips_proposal.json` | Full PS proposal — executive summary, approach, timeline, 2 milestone details, assumptions, customer responsibilities, governance, RACI, pricing, risk, next steps | 14 | [Link](https://docs.google.com/presentation/d/1KtY1M1NFxp_QoKzDDNtY6IPo5kcHsGvpceX1x5Q0GO4) |
| `reference_decks/ball_hort_snow_day.json` | Snow Day / technical discovery deck — pillar cards, 3-phase SD approach, use cases, "Why SD" cards | 9 | [Link](https://docs.google.com/presentation/d/1KxYmBmLllyhsorBhJw5IHnVsY2D1Vj45a_mR-TMpHrQ) |
| `reference_decks/quickstart_accelerator.json` | QuickStart partner delivery model — QSA process, pricing, **team_photo** with partner roles | 6 | [Link](https://docs.google.com/presentation/d/1wMGwpsiZhmrJRbJs36Z1RTKl2BRM6XROVHJ2BEKtF0s) |

## Visual Design Notes

- **ALWAYS use Snowflake template layouts and color scheme** when rendering customer visuals with python-pptx. Never use arbitrary colors — all fills, fonts, and accents must come from the template theme palette (dk1, lt1, dk2, accent1–accent6). Use native layouts where possible and LAYOUT_BLANK only for complex custom visuals.

- **Title slide**: Cyan (#29B5E8) background, uppercase title, native Layout 0 provides dotted wave, Snowflake logo, copyright footer
- **Section dividers**: Dark blue (#11567F) background set explicitly via `set_bg()`. Two-tone text: white for all words except last word in cyan. Native Layout 0 placeholders cleared/hidden.
- **Closing slide**: Cyan background, two-tone "THANK YOU" (dark blue + white)
- **Agenda**: Native Layout 9 with white text (T.lt1) for contrast on dark background
- **Hyperlink fix**: All placeholder text functions strip inherited hyperlink formatting and disable underlines
- **Template footer**: All layouts have built-in copyright footer; never add programmatically

## Google Drive Output

After generating the PPTX locally, upload and convert it to Google Slides in Drive.

### Folder structure
All outputs go to: **SnowWork → Accounts → {AccountName} → Presentations**

For a new account, create the folder chain:
1. `mcp_google-worksp_create_drive_folder` name="{AccountName}", parent_id=`1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck` → `{account_folder_id}`
2. `mcp_google-worksp_create_drive_folder` name="Presentations", parent_id=`{account_folder_id}` → `{presentations_folder_id}`

For internal decks (TDR, proposals with no specific account), use SnowWork/Internal (`1x6uOOcSTerODqM_tTdoyD9T8SV3vR4kf`) and create a `Presentations` subfolder there.

### Upload command
```bash
cd /Users/michaelkelly/.snowflake/cortex/.mcp-servers/google-workspace && \
./node /Users/michaelkelly/CoCo/Scripts/upload_to_gslides.mjs \
  "/path/to/output.pptx" "{Title}" "{folder_id}"
```
Returns JSON: `{"id":"...","name":"...","url":"https://docs.google.com/presentation/d/.../edit"}`

### Bullet point formatting
When writing any email draft body (mcp_google-worksp_create_draft), always indent bullet points with 4 spaces:
    • Like this item
    • And this item
Never use flush-left `• item` format. For Google Docs content (mcp_google-worksp_create_document), use `- item` markdown lists which auto-convert to properly indented bullets.
