---
name: scope-proposal-estimator
description: "Generate a Snowflake Professional Services scope & proposal HTML document. Use when: creating a PS engagement proposal, scoping a customer engagement, writing a scope estimate, generating a proposal doc, building a PS SOW overview. Triggers: scope estimate, engagement proposal, PS proposal, proposal doc, scope document, generate proposal, create proposal, proposal html."
---

# Scope & Proposal Estimator

Generates a polished, print-ready Snowflake PS engagement proposal HTML document using the established template format. Produces a customer-ready deliverable matching the visual style defined in `assets/proposal_template.html`.

## Setup

**Load** `assets/proposal_template.html` to understand the exact HTML structure, CSS classes, and layout patterns before generating output.

## Workflow

### Step 1: Gather Engagement Basics

**Ask** the user for the following (all required):

```
Engagement basics:
- Customer / Account name  (e.g., Acme Corp)
- Engagement title         (e.g., Data Governance & Classification)
- Status                   (DRAFT or FINAL)
- Date                     (e.g., April 2026)
- Duration                 (e.g., 10 wks)
- Fixed investment         (e.g., $85,980)
- Output file name         (e.g., acme-scope-estimate.html)
```

**⚠️ STOP**: Wait for user response before proceeding.

---

### Step 2: Executive Summary

**Ask** the user for a 2-4 sentence executive summary paragraph describing:
- What Snowflake PS will do for the customer
- The key technical scope (tables/objects targeted, native capabilities used)
- The primary business outcome (cost savings, risk reduction, speed, etc.)

**Tip**: Keep it specific — reference actual technology (e.g., `SYSTEM$CLASSIFY`, dynamic masking, Cortex AI) and quantifiable outcomes where possible.

**⚠️ STOP**: Wait for user response.

---

### Step 3: Workstreams (1–4)

For each workstream (repeat until user says done, max 4), collect:

```
Workstream [N]:
- Name           (e.g., Data Governance & Tagging Strategy)
- Color theme    (blue | purple | green | amber)
- Deliverables   (4–6 bullet points, each with bolded lead-in and brief description)
- Ad hoc callout (optional — one short paragraph of advisory/boundary note)
- Timeline phases:
    Phase name | Start week | End week | Milestone type (standard | handoff)
    (e.g.: Discovery & Framework | 1 | 2 | standard)
```

**Color theme mapping:**

| Theme  | Bar gradient         | Section dot | Card top border |
|--------|----------------------|-------------|-----------------|
| blue   | `#0ea5e9 → #0284c7`  | `#0ea5e9`   | `#29B5E8`       |
| purple | `#8b5cf6 → #7c3aed`  | `#8b5cf6`   | `#8b5cf6`       |
| green  | `#10b981 → #059669`  | `#10b981`   | `#10b981`       |
| amber  | `#f59e0b → #d97706`  | `#f59e0b`   | `#f59e0b`       |

**⚠️ STOP**: After the user finishes entering all workstreams, confirm count and names before continuing.

---

### Step 4: Metric Cards

**Ask**: How many top-level metric cards? (2–4, default is 2: Duration + Investment)

For each card:
```
Label   (e.g., Duration | Fixed Investment | Tables in Scope | Team Size)
Value   (e.g., 10 wks   | $85,980          | ~100             | 2)
Accent color (green | blue | purple | amber — one per card)
```

**⚠️ STOP**: Wait for user response.

---

### Step 5: Supporting Sections

**Ask** for:

```
Why Snowflake PS (2–6 value proposition cards):
  Each card: title | icon (font-awesome class) | description (2 sentences)

Delivery Team (1–6 roles — fully user-defined, no defaults assumed):
  Each role: title | icon | color theme | headline sentence | paragraph | 3–5 bullet points

Assumptions (any number of bullet points)

Out of Scope (any number of bullet points)

Next Steps (any number of table rows):
  Step # | Action title | Details | Target date
```

**⚠️ STOP**: Wait for user response.

---

### Step 6: Generate HTML

Using the structure from `assets/proposal_template.html` as an exact reference, write a complete new HTML file with the user's inputs. Follow these rules precisely:

#### General Structure
Preserve the full `<head>` block (Tailwind CDN, Google Fonts Lato, Font Awesome, all `<style>` rules) unchanged. Replace only content inside `<body>`.

#### Section Spacing & Dividers
- Section headers use `padding-bottom: 6px; border-bottom: 2px solid #cbd5e1` (thicker, slightly darker line)
- Metrics wrapper: `class="px-6 pt-5 pb-2"` — tighter bottom before the executive summary
- Executive summary paragraph: `class="text-sm text-slate-600 leading-relaxed mt-2"` (not `mt-4`)
- All content section wrappers use `pb-6` (not `pb-4`) for breathing room between sections
- Why Snowflake PS wrapper: `class="px-6 py-6"` (not `py-4`)
- Metric card CSS: `padding: 24px 16px` (not `28px 20px`)

#### Header — No Date Stamp
Do **not** render a separate date line in the header. Only show the DRAFT/FINAL status tag:
```html
<div class="text-right text-sm">
  <div class="tag white mb-2">DRAFT</div>
</div>
```

#### Footer — Snowflake Confidential (Both Pages)
Add a page-1 footer div immediately **before** the `<!-- PAGE BREAK -->` div:
```html
<!-- PAGE 1 FOOTER -->
<div style="margin: 12px 24px 0; padding-top: 8px; border-top: 1px solid #e2e8f0;">
  <div style="font-size: 9px; color: #94a3b8; letter-spacing: 0.03em;">
    &copy; 2026 Snowflake Inc. All Rights Reserved &nbsp;|&nbsp; Snowflake Confidential
  </div>
</div>
```

Replace the closing `<footer>` with:
```html
<!-- FOOTER -->
<footer class="px-6 py-3" style="border-top: 1px solid #e2e8f0;">
  <div style="font-size: 9px; color: #94a3b8; letter-spacing: 0.03em;">
    &copy; 2026 Snowflake Inc. All Rights Reserved &nbsp;|&nbsp; Snowflake Confidential
  </div>
</footer>
```

#### Universal Grid Layout Rule

Apply to **every** multi-card section (Metric Cards, What You Get, Why Snowflake PS, Delivery Team) based on item count:

| Count | Tailwind class                   | Layout      |
|-------|----------------------------------|-------------|
| 1     | *(no grid wrapper, full width)*  | Single card |
| 2     | `grid grid-cols-2 gap-6`         | Side by side|
| 3     | `grid grid-cols-3 gap-3`         | Three cols  |
| 4     | `grid grid-cols-2 gap-3`         | 2 × 2       |
| 5     | `grid grid-cols-3 gap-3`         | 3 + 2       |
| 6     | `grid grid-cols-3 gap-3`         | 2 rows of 3 |

#### Metric Cards
Each: `class="card metric-card"` with `style="border-top: 3px solid {accent_color};"`.
- `<div class="num" style="color:{accent_color};">{value}</div>`
- `<div class="lbl">{label}</div>`
- Accent colors: green=`#10b981`, blue=`#29B5E8`, purple=`#8b5cf6`, amber=`#f59e0b`

#### Gantt Chart — Column Span Formula

Total grid columns = total_weeks + 1 (col 1 = 160px label, cols 2..N+1 = weeks).
Set `grid-template-columns: 160px repeat({total_weeks}, 1fr)` on the grid container.

For a phase spanning `week_start` to `week_end`:
- Bar: `grid-column: {week_start + 1} / {week_end + 2}`
- Spacer before bar (if week_start > 1): `grid-column: 2 / {week_start + 1}`
- Spacer after bar (if week_end < total_weeks): `grid-column: {week_end + 2} / {total_weeks + 2}`

Milestone diamond: `standard` → workstream bar color; `handoff` → always `#10b981`.

**Example** — 10-week engagement, phase W1–W2:
```html
<div style="padding:3px 0;">Phase Name</div>
<div style="grid-column: 2 / 4; padding:3px 2px;">
  <div style="background:linear-gradient(135deg, #0ea5e9, #0284c7); border-radius:3px; height:22px; position:relative;">
    <span style="position:absolute; right:-7px; top:50%; transform:translateY(-50%) rotate(45deg); width:11px; height:11px; background:#0284c7; border:2px solid white; box-shadow:0 1px 3px rgba(0,0,0,0.2);"></span>
  </div>
</div>
<div style="grid-column: 4 / 12;"></div>
```

#### Workstream Cards (What You Get)
Apply Universal Grid Layout Rule. Each card:
```html
<div class="card" style="border-top: 3px solid {border_color};">
  <div class="flex items-center gap-2 mb-2">
    <div class="pain-icon {icon_bg} {icon_color}" style="width:28px; height:28px; font-size:13px;">
      <i class="fa-solid {icon_class}"></i>
    </div>
    <div class="text-sm font-bold text-slate-700">{Name}</div>
  </div>
  <ul class="text-xs text-slate-500 leading-relaxed space-y-1.5 pl-4" style="list-style-type: disc;">
    <li><strong>{lead-in}</strong> — {detail}</li>
  </ul>
</div>
```

#### Why Snowflake PS Cards
Apply Universal Grid Layout Rule. Each card:
```html
<div class="card flex gap-3">
  <div class="pain-icon {icon_bg} {icon_color}" style="width:28px; height:28px; font-size:13px;">
    <i class="fa-solid {icon_class}"></i>
  </div>
  <div>
    <div class="text-sm font-semibold text-slate-700 mb-1">{Title}</div>
    <div class="text-xs text-slate-500">{Description}</div>
  </div>
</div>
```

#### Delivery Team Cards
Apply Universal Grid Layout Rule. Each card:
```html
<div class="card" style="border-top: 3px solid {theme_color};">
  <div class="flex items-center gap-2 mb-3">
    <div class="pain-icon {icon_bg} {icon_color}" style="width:28px; height:28px; font-size:13px;">
      <i class="fa-solid {icon_class}"></i>
    </div>
    <div class="text-sm font-bold text-slate-700">{Role Title}</div>
  </div>
  <p class="text-xs text-slate-500 leading-relaxed mb-2">{Headline + paragraph}</p>
  <ul class="text-xs text-slate-500 leading-relaxed space-y-1 pl-4" style="list-style-type: disc;">
    <li>{bullet}</li>
  </ul>
</div>
```

#### Color theme reference

| Theme  | Border/dot    | Bar gradient           | Icon bg class   | Icon color class    |
|--------|---------------|------------------------|-----------------|---------------------|
| blue   | `#29B5E8`     | `#0ea5e9 → #0284c7`    | `bg-sky-50`     | `text-sky-500`      |
| purple | `#8b5cf6`     | `#8b5cf6 → #7c3aed`    | `bg-violet-50`  | `text-violet-500`   |
| green  | `#10b981`     | `#10b981 → #059669`    | `bg-emerald-50` | `text-emerald-500`  |
| amber  | `#f59e0b`     | `#f59e0b → #d97706`    | `bg-amber-50`   | `text-amber-500`    |

#### Duration parsing
Parse human input (e.g., "10 wks", "8 weeks", "12") → extract integer week count for the Gantt grid.

#### Output path
Save to `~/Downloads/{output_file_name}` unless the user specified a different path.

---

### Step 7: Confirm & Deliver

After writing the file:
1. Confirm the output path to the user
2. Remind them to open in Chrome/Safari and use `Cmd+P → Save as PDF` for the final deliverable
3. Offer to iterate on any section

---

## Stopping Points

- ✋ Step 1: Basics confirmed
- ✋ Step 2: Executive summary confirmed
- ✋ Step 3: All workstreams confirmed (count + names)
- ✋ Step 4: Metric cards confirmed
- ✋ Step 5: Supporting sections confirmed
- ✋ Step 7: User satisfied with output

## Success Criteria

- ✅ Valid HTML that opens cleanly in a browser
- ✅ Gantt column spans mathematically correct for the given duration
- ✅ Workstream count matches layout grid choice
- ✅ All user inputs reflected accurately

## Output

A standalone HTML file at the specified path, ready to open in a browser and print/save as PDF.

## Troubleshooting

**Gantt looks misaligned** — Recheck column span math. Total grid cols = weeks + 1. Verify `grid-template-columns` matches the week count.

**Missing CSS styles** — Ensure the full `<head>` block from the template is preserved verbatim, including all Tailwind, Font Awesome, and `<style>` rules.

**Phase extends past total weeks** — Validate that `week_end ≤ total_weeks` for all phases. Warn the user if any phase exceeds the engagement duration.
