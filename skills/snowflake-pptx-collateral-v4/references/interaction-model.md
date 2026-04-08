---
name: pptx-interaction-model
description: Consultative interaction workflow for deck creation. Phases 0-5 from requirements gathering to delivery.
---

---
## 0. Interaction Model — Before You Build

**THIS IS A HARD GATE — NOT A SUGGESTION.** You MUST complete the interaction phases before writing any Python. Your first message in response to a deck request is ALWAYS Phase 0 — no exceptions. Do not reason that "the user wants speed" or "the request is clear enough" to justify skipping. The interaction model exists because even clear requests produce mediocre decks without design input. The 5 phases below are sequential gates — never skip Phase 2 (Section Builder) or Phase 4 (Content Blueprint). Present them as a menu the user can select from, not as an interrogation.

### Phase 0: Offer Two Paths

Present both options up front. Let the user decide how they want to work:

```
I'll build a consulting-grade Snowflake deck for you. Two ways to start:

**OPTION A — Guided Build (recommended for best results)**
I'll ask you a few targeted questions, then present a Section Menu
so you can pick exactly what goes in the deck and how it looks.
Takes ~3 minutes of your input, produces the strongest output.

**OPTION B — Self-Directed**
Paste your own outline or brief. I'll interpret it, propose a
Content Blueprint for your review, then build.

Which do you prefer? (or just paste your outline to go with B)
```

If the user picks Option B (pastes an outline), skip to Phase 4 — convert their outline into a Content Blueprint, present it for approval, then build.

If the user picks Option A (or doesn't specify), proceed through Phases 1-4 below.

---

### Phase 1: Quick Context (ask in ONE message, max 4 questions)

Only ask what's genuinely missing from the user's request. If the user already provided audience + topic + purpose + slide count, skip to Phase 2.

```
Before I show you the Section Menu, a few quick questions:

1. **Who is the audience?**
   a) C-Suite / VP — strategic, outcome-focused
   b) Director / Manager — strategic + tactical
   c) Architect / Engineer — technical deep-dive
   d) Mixed / Workshop — exec headlines with technical backup
   e) Customer / External — polished narrative, benefit-oriented

2. **How many slides?**
   a) Short & punchy — 6-10 slides (exec summary, board update)
   b) Standard — 10-15 slides (strategy pitch, customer proposal)
   c) Comprehensive — 15-25 slides (workshop, deep-dive, detailed plan)
   d) You decide — I'll recommend based on audience + sections

3. **What is the ONE thing the audience should remember?**
   (One sentence — the core takeaway or call to action)

4. **Any must-include topics?**
   (e.g., specific products, case studies, competitive points, compliance)
```

**Mapping answers to defaults:**

| Audience | Default slide count | Narrative style | Default sections |
|----------|-------------------|-----------------|-----------------|
| C-Suite / VP | 6-10 | Lead with answer (Pyramid Principle) | Statement + Content + Data Viz + CTA |
| Director / Manager | 10-15 | Problem → Solution → Proof | Agenda + Content + Frameworks + Roadmap + CTA |
| Architect / Engineer | 12-20 | Technical depth, decision trees | Agenda + Approach + Architecture + Tables + Roadmap |
| Mixed / Workshop | 15-25 | Chapter dividers, progressive depth | Agenda + Statement + Content + Process + Frameworks + Roadmap |
| Customer / External | 8-15 | Polished story, proof points | Statement + Content + Case Studies + CTA |

**Slide count drives section depth:**

| Slide Budget | Section Strategy |
|-------------|-----------------|
| 6-10 | 1 slide per section max. Cut Agenda, merge Context into Statement. Every slide must earn its place. |
| 10-15 | Standard depth. 1-2 slides per section. Include Agenda if 4+ sections. |
| 15-25 | Full depth. Core Content gets 3-8 slides. Add Process, Frameworks, and deeper Case Studies. |

If the user picks a slide count that conflicts with the number of sections they select, flag it:
```
You've selected 9 sections but a budget of 6-10 slides. That's tight — 
I'd suggest either trimming to 5-6 sections or expanding to 12-15 slides.
Which do you prefer?
```

---

### Phase 2: Section Menu (MANDATORY — present EVERY time)

This is the core of the interaction. Present the Section Catalogue as a numbered menu. The user picks which sections they want and in what order. Each section type has visual options they can choose from.

**Present this menu to the user:**

```
SECTION MENU — Pick the sections you want (in order)
====================================================
Each section becomes a chapter in your deck.
I'll add a divider slide between chapters automatically.

#   SECTION                        WHAT IT DOES                                      SLIDES
--  ----------------------------   ------------------------------------------------  ------
1   TITLE & COVER                  Opening slide with deck title, subtitle, date      1
2   AGENDA & TABLE OF CONTENTS     Session roadmap, numbered topics, time alloc.      1-2
3   EXECUTIVE STATEMENT            Big bold assertion, vision quote, or "imagine if"  1-2
4   SITUATION & CONTEXT            Current state, market landscape, the challenge     1-3
5   APPROACH, SCOPE & OBJECTIVES   Methodology, project scope, goals, principles      1-3
6   CORE CONTENT                   Key arguments, value propositions, capabilities    2-8
7   PROCESS & JOURNEY              Workflows, customer journeys, swimlanes            1-3
8   DATA & METRICS                 Charts, KPIs, benchmarks, survey findings          1-4
9   COMPARISON TABLES              Feature matrices, options, pricing, scorecards     1-3
10  FRAMEWORKS & ARCHITECTURE      Concept models, tech stacks, ecosystem diagrams    1-4
11  ROADMAP & TIMELINE             Phased plans, sprints, milestones, calendars       1-2
12  CASE STUDIES & PROOF POINTS    Customer stories, logos, testimonials, results      1-3
13  TEAM & ORGANIZATION            Org charts, bios, responsibilities, RACI           1-2
14  CALL TO ACTION & NEXT STEPS    Summary, asks, next steps, contact info            1

EXAMPLE: "I'll take 1, 2, 4, 6, 8, 10, 11, 14" or "All of them" or "1, 3, 6, 12, 14"
```

**Default section selections by audience** (use if user says "you pick"):

| Audience | Recommended Sections |
|----------|---------------------|
| C-Suite / VP | 1, 3, 6, 8, 14 (tight, punchy, 6-10 slides) |
| Director / Manager | 1, 2, 4, 6, 8, 10, 11, 14 (balanced, 10-15 slides) |
| Architect / Engineer | 1, 2, 5, 6, 7, 9, 10, 11, 14 (detailed, 12-20 slides) |
| Mixed / Workshop | 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 14 (comprehensive, 15-25 slides) |
| Customer / External | 1, 3, 6, 8, 12, 14 (story-driven, 8-15 slides) |

---

### Phase 3: Visual Options Per Section (present after user picks sections)

For EACH section the user selected, offer 3-5 visual pattern choices. Present them all in ONE message so the user can respond once.

**Visual Options Catalogue:**

```
Great choices! Now let's pick the visual style for each section.
Pick a letter for each, or say "your pick" and I'll choose the best mix.

SECTION 1 — TITLE & COVER
   a) Clean title + subtitle on branded background (default)
   b) Title with full-bleed background image
   c) Bold statement title with accent bar

SECTION 2 — AGENDA & TABLE OF CONTENTS
   a) Numbered list with descriptions (clean, simple)
   b) Clickable tile grid — 2 columns with section names + page numbers
   c) Visual timeline — horizontal flow with numbered milestones
   d) Icon-based agenda — each topic gets an icon + description

SECTION 3 — EXECUTIVE STATEMENT
   a) Centred bold quote on dark/light background (think "Imagine if...")
   b) Big number + insight ("$4.2B opportunity in 3 years")
   c) Vision statement with supporting pillars (3 columns below)
   d) Full-bleed image with text overlay

SECTION 4 — SITUATION & CONTEXT
   a) Left text + right visual (split layout)
   b) Before/After comparison (two columns) → 14.5
   c) Landscape overview with callout boxes
   d) Challenge cards — 3-4 pain points as coloured cards
   e) Market data with trend narrative
   f) Stat scatter with key market numbers → 14.35

SECTION 5 — APPROACH, SCOPE & OBJECTIVES
   a) Numbered phases with descriptions (chevron flow)
   b) Scope matrix — in/out table
   c) Objectives with icon bullets
   d) Guiding principles — 4-6 principle cards

SECTION 6 — CORE CONTENT (per sub-topic slide)
   a) Title + structured bullets (heading/body pairs)
   b) 3-column or 4-column card layout
   c) Icon grid — 6-9 capabilities with icons
   d) Left/right split — visual + text
   e) Hub & spoke — central concept with radiating points → 14.20
   f) Pillar layout — 3-5 vertical columns with headers
   g) Icon column cards — feature catalogue or service menu → 14.37
   h) Grouped category menu with tier columns → 14.31

SECTION 7 — PROCESS & JOURNEY
   a) Horizontal process flow (chevrons or arrows) → 14.18
   b) Customer journey map with horizon columns + touchpoints → 14.32
   c) Swimlane diagram (rows = teams, cols = phases) → 14.29
   d) Circular lifecycle diagram
   e) Step-by-step vertical flow

SECTION 8 — DATA & METRICS
   a) KPI dashboard — 4-6 big numbers with labels
   b) Chart placeholder + narrative callouts
   c) Survey results — bar/donut style with insights
   d) Benchmark comparison — us vs. industry
   e) Trend narrative — before/after with data
   f) Stat scatter — large numbers with category context → 14.35

SECTION 9 — COMPARISON TABLES
   a) Feature matrix with check/cross indicators
   b) Option comparison — side by side columns
   c) Pricing/tier table → 14.31
   d) Scorecard with RAG (Red/Amber/Green) status
   e) RACI or responsibility matrix
   f) Maturity / capability assessment grid → 14.28
   g) Dual-context comparison (current vs. future) → 14.33

SECTION 10 — FRAMEWORKS & ARCHITECTURE
   a) Layered stack (data sources → platform → apps) → 15.4
   b) Hub & spoke ecosystem diagram → 14.20 / 15.5
   c) 2x2 matrix / quadrant
   d) Concentric circles (core → edge)
   e) Snowflake icon architecture (uses template icons) → 15.6
   f) Competitive landscape map
   g) Two-horizon split (today vs. tomorrow) → 14.34

SECTION 11 — ROADMAP & TIMELINE
   a) Horizontal phased roadmap (3-5 phases) → 14.24
   b) Swimlane roadmap — multi-workstream with lanes → 14.29
   c) Gantt table — table-based project timeline → 14.36
   d) Milestone scatter — 30/60/90-day transition plan → 14.30
   e) Sprint/release cycle diagram
   f) Vertical milestone ladder → 14.19

SECTION 12 — CASE STUDIES & PROOF POINTS
   a) Logo + headline + 3 results (single company)
   b) Multi-logo grid with one-liner per customer
   c) Before/after transformation story
   d) Quote card — customer testimonial with photo placeholder
   e) Results dashboard — 3-4 metrics from a real engagement

SECTION 13 — TEAM & ORGANIZATION
   a) Org chart — hierarchy with names and roles
   b) Team grid — photo placeholders + bios
   c) RACI table
   d) Responsibilities matrix (us vs. client)

SECTION 14 — CALL TO ACTION & NEXT STEPS
   a) 3-5 numbered next steps with owners and dates
   b) Summary + single bold ask
   c) Two-path decision slide ("Option A vs Option B")
   d) Contact card with key people
```

**Rules for visual selection:**
- If user says "your pick" or "you choose", select the most visually diverse mix — never repeat the same pattern in consecutive sections
- Ensure at least 1 in 3 content slides uses a visual pattern (not just text)
- Never use the same visual pattern more than twice in one deck
- Architecture sections (10) MUST use Snowflake template icons when discussing Snowflake products

---

### Phase 4: Content Blueprint (MANDATORY — before writing ANY code)

**Do NOT generate Python code until the content blueprint is complete and reviewed.**

After sections and visuals are selected, write the full content plan. This is the single biggest quality lever — a bad outline produces a bad deck regardless of formatting. Content is 80% of deck quality; layout is 20%.

**Blueprint format** — produce this as plain text, present it to the user for approval:

```
CONTENT BLUEPRINT
=================
Deck:      [Title]
Audience:  [who]
Sections:  [list]
Narrative: [HOOK → CONTEXT → TENSION → RESOLUTION → CTA]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHAPTER: [Section Name]
  Divider subtitle: [one line setting up this chapter]

  SLIDE [n] — [Layout ID] | Visual: [Pattern name + ref]
    Title:    [ALL CAPS, ≤50 chars — must pass "So what?" test]
    Subtitle: [1 sentence, ≤65 chars]
    Content:  [specific points with numbers, names, outcomes]
    Visual:   [MANDATORY — exact pattern + ref from patterns-enterprise.md or slide-patterns.md]
              Options: chevron-flow | hub-spoke | stat-callouts | timeline | layered-stack |
                       comparison-table | icon-grid | pillar-columns | before-after | metric-cards |
                       swimlane | maturity-grid | bullet-only (max 2 consecutive)

  SLIDE [n+1] — ...
    ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHAPTER: [Next Section Name]
  ...

[...continue for ALL slides...]
```

**Content quality review** — before proceeding to code, check EVERY slide in the blueprint:

| # | Check | Test | Fix if it fails |
|---|-------|------|-----------------|
| 1 | **"So what?"** | If someone reads ONLY the title, do they know why this slide matters? | Rewrite title to convey the conclusion, not the topic |
| 2 | **Specificity** | Does every bullet include at least ONE of: a number, a timeframe, a named technology, or a concrete outcome? | Add a specific data point or example |
| 3 | **Differentiation** | Could a competitor say the exact same thing? | Add Snowflake-specific detail or a unique insight |
| 4 | **No filler** | Is every bullet a complete thought (15+ words) that adds new information? | Remove or merge weak bullets |
| 5 | **Narrative flow** | Does each slide logically follow the previous one? Is there a clear arc across chapters? | Reorder or add a bridging slide |
| 6 | **Visual density** | Do ≥40% of content slides have a visual pattern (not "bullet-only")? Are there 3+ consecutive "bullet-only" slides? | Replace some bullet slides with chevron-flow, stat-callouts, hub-spoke, comparison-table, icon-grid, or timeline patterns from `patterns-enterprise.md` |
| 7 | **No bullet monotony** | Count slides marked "bullet-only" — if more than 60% of content slides, the deck will look flat | Swap at least half the bullet slides for visual patterns |

**Example — weak vs. strong blueprint entries:**

```
WEAK:
  SLIDE 6 — Architecture
    Title:    "ARCHITECTURE OVERVIEW"
    Content:  Applications, AI/ML, Data Platform, Data Sources

STRONG:
  SLIDE 6 — Layout 0 | Visual: Layered Stack + Icons (15.4)
    Title:    "THE ENGINE UNDER THE HOOD"
    Subtitle: "Four integrated layers turning 11 data silos into one intelligent platform"
    Content:  Apps (clinical dashboards, patient 360) → AI/ML (Cortex AI, Document AI)
              → Platform (Snowflake, Iceberg, Dynamic Tables) → Sources (EHR, claims, labs)
    Visual:   Layered stack with Snowflake icons, 4 colour-coded bars
```

The weak version produces a generic slide. The strong version produces a consulting-grade slide because the content was designed before the code was written.

**BEFORE presenting the blueprint, self-validate visual density:**
1. Count content slides (exclude cover, dividers, thank-you)
2. Count slides with a visual pattern specified (anything other than "bullet-only")
3. If visual slides < 40% of content slides → go back and swap bullet-only slides for visual patterns
4. If 3+ consecutive slides are "bullet-only" → insert a visual pattern between them
5. Only present the blueprint after it passes these checks

**Present the blueprint to the user and ask:**
```
Here's the Content Blueprint. Please review:
- Any slides to add, remove, or reorder?
- Any content points missing or incorrect?
- Visual density: [X]/[Y] content slides use visual patterns ([Z]%)
- Happy to proceed to build?
```

**Only after the user approves (or says "looks good") → proceed to Phase 5.**

---

### Phase 5: Build & Deliver

Generate the Python code and produce the deck. After delivery, always offer:

```
Deck is ready! A few options:
- Adjust content depth, visual style, or slide count?
- Add/remove sections?
- Swap visual patterns on any slide?
- Regenerate with a different narrative angle?
```

---

### Rules for the Interaction Model

- **Phase 0 is ALWAYS your first response** — no Python code, no Content Blueprint, no slide descriptions. Just the two-path choice. This is non-negotiable regardless of how detailed the user's request is
- **Phase 1 triggers when details are missing** — if the user didn't specify ALL of: audience, slide count, core takeaway, and specific sections, ask the missing questions (max 4). A request like "build me a deck on data sharing" is missing most of these — you MUST ask
- **Phase 2 (Section Menu) is MANDATORY** — always present the full menu, even for experienced users. It takes 10 seconds to pick numbers and produces dramatically better results
- **Phase 3 (Visual Options) is MANDATORY** — always show visual choices per section. Default to "your pick" if user wants speed
- **Phase 4 (Content Blueprint) is MANDATORY** — never skip the blueprint. Never go straight from questions to code. Present the blueprint and WAIT for user approval before writing any Python
- **Never ask more than 4 questions in Phase 1** — audience, slide count, core takeaway, must-includes. Skip any the user already answered
- **If the user says "just do it" or "skip questions"** — default to: Audience = Director, auto-select sections per mapping table, choose diverse visuals, and still produce the Content Blueprint for approval before building. Even "just do it" does NOT skip the blueprint
- **Never produce generic content** — every deck must read like it was written by a senior strategy consultant (see Section 20)
- **Always shape a narrative** — a deck is a story (HOOK → CONTEXT → TENSION → RESOLUTION → CTA), not a list of facts
- **After producing the deck**, always offer refinement options (Phase 5)
- **If running in headless/non-interactive mode** (`-p` flag or similar), proceed with Self-Directed path: make reasonable defaults for missing details, produce the Content Blueprint in output, then build. This is the ONLY case where waiting for user reply is not possible. **Even in headless mode, you MUST self-validate the Content Blueprint for visual density before generating code**: ≥40% of content slides must have a visual pattern assigned (not "bullet-only"), and no more than 2 consecutive slides can be "bullet-only". If the blueprint fails this check, revise it before proceeding to code generation

