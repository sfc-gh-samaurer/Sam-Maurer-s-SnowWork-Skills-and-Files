---
name: pptx-html-slide-design
description: HTML/CSS design system and full slide templates for Snowflake-branded presentations at 960×540px. Reference for generating world-class slide designs in HTML before converting to PPTX.
---

# HTML Slide Design System

## Design Philosophy

Each slide is a **self-contained 960×540px HTML document** rendered by Playwright at 2× DPI. Because design happens in HTML/CSS rather than python-pptx shapes, you have access to gradients, modern layouts, shadows, and precise typography — producing slides that are indistinguishable from professionally designed decks.

**Snowflake brand principles (from official 2026 template):**
- **Clean and airy** — embrace white space, avoid clutter. Less text, more visual.
- **ALL CAPS only on cover and chapter titles** (44pt Arial Bold). Content slide titles and body copy are NOT all caps — title case only.
- **Arial is the required font** — Snowflake's official fallback for PowerPoint/HTML. Do not use Montserrat, Roboto, or any other font.
- **Use only theme colors** — never introduce off-brand colors. See color palette below.
- **One idea per slide** — if you need three bullet points, ask whether those could be three cards or a visual layout instead.
- Every element must fit within 960×540px with `overflow: hidden` — nothing can scroll or extend beyond the slide boundary
- Use the CSS design tokens below for all colors, spacing, and typography — never invent colors
- At least 50% of content slides must use a visual pattern beyond a simple bullet list

---

## 1. CSS Design Tokens

Paste this `<style>` block verbatim into every slide. Then add slide-specific CSS below it.

```css
/* ═══ SNOWFLAKE SLIDE DESIGN SYSTEM v4 ═══ */
:root {
  /* Primary brand */
  --sf-blue:        #29B5E8;
  --sf-mid-blue:    #11567F;
  --sf-white:       #FFFFFF;
  --sf-dark-text:   #262626;
  --sf-body-grey:   #5B5B5B;
  --sf-light-bg:    #F5F5F5;

  /* Accent palette — official 2026 brand names */
  --sf-teal:        #75CDD7;   /* "Star Blue" */
  --sf-orange:      #FF9F36;   /* "Valencia Orange" */
  --sf-violet:      #7254A3;   /* "Purple Moon" */
  --sf-pink:        #D45B90;   /* "First Light" */
  --sf-midnight:    #000000;   /* "Midnight" — use very sparingly */
  /* Note: Secondary colors (teal/orange/violet/pink) are for accents only.
     Most slides should use only sf-blue, sf-mid-blue, sf-white, sf-dark-text, sf-body-grey. */

  /* Utility */
  --sf-border:      #C8C8C8;
  --sf-grid:        #DDDDDD;
  --sf-table-grey:  #717171;
  --sf-light-row:   #F8FAFB;

  /* Semantic */
  --sf-green:       #2ECC71;
  --sf-amber:       #F5A623;
  --sf-red:         #E74C3C;
  --sf-light-green: #E8F8EF;
  --sf-light-amber: #FFF3E0;
  --sf-light-red:   #FDEDEC;
  --sf-light-blue:  #E8F4FD;

  /* Slide geometry (96dpi — 1px = 1/96 inch) */
  --slide-w:       960px;
  --slide-h:       540px;
  --pad-left:       38px;   /* 0.40" */
  --pad-right:      48px;   /* 0.50" right clearance */
  --title-top:      29px;   /* 0.30" */
  --subtitle-top:   69px;   /* 0.72" */
  --content-top:   144px;   /* 1.50" */
  --footer-top:    511px;   /* 5.32" */
  --safe-bottom:   490px;   /* 5.10" — max content bottom */
  --content-w:     876px;   /* 9.13" */

  /* Typography — Arial is the REQUIRED font (Snowflake official standard) */
  --font:  Arial, 'Helvetica Neue', Helvetica, sans-serif;
  /* Font size scale:
     Cover/Chapter title: 44px bold ALL CAPS
     Content slide title: 18px bold (title case — NOT all caps)
     Subtitle:            12px regular
     Section head:        12px bold
     Body copy:           10px regular
     Small body:          9px regular
     Caption/footnote:    6-7px regular
     Big numbers (KPI):   28-44px bold
  */

  /* Rounded corners */
  --radius-sm:   4px;
  --radius-md:   6px;
  --radius-lg:  10px;
}

/* Base reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 960px; height: 540px;
  overflow: hidden;
  font-family: var(--font);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  background: #fff;
}
.slide {
  width: 960px; height: 540px;
  position: relative; overflow: hidden;
}
```

---

## 2. Common Components

Add these classes to any slide's `<style>` block as needed.

### Slide Header (title + subtitle)
```css
.slide-header {
  position: absolute;
  left: var(--pad-left); top: var(--title-top);
  width: var(--content-w);
}
.slide-title {
  font-size: 18px; font-weight: 700; color: var(--sf-dark-text);
  /* Title case — do NOT use text-transform: uppercase here.
     ALL CAPS is reserved for cover and chapter titles only (44pt). */
  letter-spacing: 0.01em;
  line-height: 1.15;
}
.slide-subtitle {
  font-size: 12px; color: var(--sf-body-grey);
  margin-top: 6px; line-height: 1.35;
}
```

### Left Edge Bar (present on all content slides)
```css
.edge-bar {
  position: absolute;
  left: 0; top: 36px;
  width: 4px; height: 38px;
  background: var(--sf-blue);
}
```

### Footer & Page Number

All content slides must include the official Snowflake copyright footer and a page number.

```css
.slide-footer {
  position: absolute;
  left: var(--pad-left); top: var(--footer-top);
  width: 500px;
  font-size: 6px; color: #929292;
  letter-spacing: 0.01em;
  font-family: Arial, sans-serif;
}
.slide-page-num {
  position: absolute;
  right: 20px; top: var(--footer-top);
  width: 50px;
  font-size: 6px; color: #919191;
  text-align: right;
  font-family: Arial, sans-serif;
}
```

**Footer text (use verbatim):**
```
© 2026 Snowflake Inc. All Rights Reserved
```

**Page number** — right side at `right: 20px`, same `top: var(--footer-top)` baseline. Use the actual slide number (passed as a parameter or hardcoded per slide).

### Card
```css
.card {
  background: var(--sf-light-bg);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  overflow: hidden;
}
.card--blue  { background: var(--sf-mid-blue); color: var(--sf-white); }
.card--accent { background: var(--sf-blue);    color: var(--sf-white); }
.card-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin-bottom: 6px;
}
.card-body { font-size: 9.5px; line-height: 1.5; }
```

### KPI Box
```css
.kpi-box {
  background: var(--sf-mid-blue);
  border-radius: var(--radius-md);
  padding: 14px 10px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
}
.kpi-value {
  font-size: 28px; font-weight: 700; color: var(--sf-white);
  letter-spacing: -0.02em; line-height: 1;
}
.kpi-label {
  font-size: 8.5px; color: var(--sf-teal);
  margin-top: 5px; line-height: 1.35; text-align: center;
}
```

### Callout Box (left-border accent)
```css
.callout {
  border-left: 4px solid var(--sf-blue);
  background: var(--sf-light-blue);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: 10px 12px;
}
.callout--warn  { border-color: var(--sf-orange); background: var(--sf-light-amber); }
.callout--alert { border-color: var(--sf-red);    background: var(--sf-light-red); }
.callout--green { border-color: var(--sf-green);  background: var(--sf-light-green); }
.callout-title { font-size: 10px; font-weight: 700; color: var(--sf-mid-blue); margin-bottom: 4px; }
.callout-body  { font-size: 9px;  color: var(--sf-dark-text); line-height: 1.5; }
```

### Bullet List
```css
.bullet-list { list-style: none; padding: 0; }
.bullet-list li {
  font-size: 10px; color: var(--sf-dark-text); line-height: 1.55;
  padding-left: 14px; position: relative; margin-bottom: 5px;
}
.bullet-list li::before {
  content: ''; position: absolute; left: 0; top: 6px;
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--sf-blue);
}
.bullet-list--check li::before { content: '✓'; color: var(--sf-green); background: none; top: 1px; font-size: 10px; font-weight: 700; }
.bullet-list--white li        { color: var(--sf-white); }
.bullet-list--white li::before { background: var(--sf-teal); }
```

### Divider Line
```css
.divider {
  height: 1px; background: var(--sf-grid); margin: 10px 0;
}
.divider--blue { background: var(--sf-blue); }
.divider--mid  { background: var(--sf-mid-blue); }
```

### Phase / Chevron Bar
```css
.phase-bar {
  background: var(--sf-mid-blue);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-size: 10px; font-weight: 700; color: var(--sf-white);
  text-transform: uppercase; letter-spacing: 0.04em;
  text-align: center;
}
.phase-bar--blue { background: var(--sf-blue); }
```

### Data Table
```css
.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { background: var(--sf-mid-blue); }
.data-table thead th {
  font-size: 9px; font-weight: 700; color: var(--sf-white);
  padding: 7px 10px; text-align: left;
  text-transform: uppercase; letter-spacing: 0.04em;
}
.data-table tbody tr:nth-child(odd)  { background: var(--sf-light-row); }
.data-table tbody tr:nth-child(even) { background: var(--sf-white); }
.data-table tbody td {
  font-size: 9px; color: var(--sf-table-grey);
  padding: 6px 10px; border-bottom: 1px solid var(--sf-grid);
}
.data-table tbody td.bold { font-weight: 700; color: var(--sf-dark-text); }
.data-table tbody td.center { text-align: center; }
```

---

## 3. Slide Type Library

Each example below is a **complete, self-contained HTML file** at 960×540px. Copy the template, replace content, and save as `slides/slide_NN_name.html`.

---

### S1 — Cover Slide

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
/* === DESIGN TOKENS === */
:root { --sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-orange:#FF9F36;--sf-border:#C8C8C8;--sf-light-blue:#E8F4FD;--font:Arial,'Helvetica Neue',Helvetica,sans-serif; }
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:var(--sf-blue);}

/* Diagonal overlay — darker bottom-right */
.slide::before {
  content:''; position:absolute; inset:0;
  background: linear-gradient(145deg, transparent 40%, rgba(0,0,0,0.22) 100%);
  pointer-events:none;
}
/* Geometric accent — bottom white wave */
.wave {
  position:absolute; bottom:0; left:0; width:100%; height:90px;
  background: var(--sf-mid-blue);
  clip-path: ellipse(110% 80px at 30% 100%);
}
/* Top-right large faded circle for visual interest */
.bg-circle {
  position:absolute; top:-120px; right:-100px;
  width:380px; height:380px; border-radius:50%;
  background: rgba(255,255,255,0.06);
}
/* Snowflake wordmark area */
.logo-area {
  position:absolute; top:32px; left:38px;
  display:flex; align-items:center; gap:10px;
}
.logo-snowflake {
  font-size:22px; color:var(--sf-white); opacity:0.9;
}
.logo-text {
  font-size:13px; font-weight:700; color:var(--sf-white);
  letter-spacing:0.12em; text-transform:uppercase; opacity:0.9;
}
/* Main title area */
.cover-title {
  position:absolute; left:38px; top:155px; width:640px;
  font-size:40px; font-weight:700; color:var(--sf-white);
  text-transform:uppercase; letter-spacing:-0.01em;
  line-height:1.1;
}
.cover-subtitle {
  position:absolute; left:38px; top:315px; width:560px;
  font-size:16px; font-weight:600; color:rgba(255,255,255,0.85);
  letter-spacing:0.02em;
}
.cover-meta {
  position:absolute; left:38px; bottom:20px; width:500px;
  font-size:11px; color:rgba(255,255,255,0.70); letter-spacing:0.03em;
}
/* Right-side accent — vertical bar with teal top */
.right-accent {
  position:absolute; right:80px; top:120px;
  width:3px; height:240px;
  background: linear-gradient(to bottom, var(--sf-teal), rgba(255,255,255,0.15));
  border-radius:2px;
}
</style></head><body>
<div class="slide">
  <div class="bg-circle"></div>
  <div class="wave"></div>
  <div class="right-accent"></div>
  <div class="logo-area">
    <span class="logo-snowflake">❄</span>
    <span class="logo-text">Snowflake Professional Services</span>
  </div>
  <div class="cover-title">Okta D&amp;I: Architecture<br>Modernization &amp;<br>Access Controls</div>
  <div class="cover-subtitle">Project Kickoff — April 2026</div>
  <div class="cover-meta">Keith Hoyle · Solutions Architect &nbsp;|&nbsp; Sam Maurer · Program Manager</div>
</div>
</body></html>
```

---

### S2 — Chapter Divider

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-teal:#71D3DC;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;
  background: linear-gradient(135deg, var(--sf-mid-blue) 0%, #0d3d5e 100%);}
/* Ghost chapter number in background */
.ghost-num {
  position:absolute; right:-20px; top:-40px;
  font-size:340px; font-weight:700; color:rgba(255,255,255,0.04);
  line-height:1; letter-spacing:-0.04em; user-select:none;
}
/* Accent line */
.accent-line {
  position:absolute; left:38px; top:50%;
  transform: translateY(-50%);
  width:4px; height:130px;
  background: linear-gradient(to bottom, var(--sf-teal), var(--sf-blue));
  border-radius:2px;
}
.chapter-label {
  position:absolute; left:60px; top:192px;
  font-size:10px; font-weight:700; color:var(--sf-teal);
  text-transform:uppercase; letter-spacing:0.18em;
}
.chapter-title {
  position:absolute; left:60px; top:214px; width:700px;
  font-size:44px; font-weight:700; color:var(--sf-white);
  text-transform:uppercase; letter-spacing:-0.01em; line-height:1.08;
}
.chapter-subtitle {
  position:absolute; left:60px; top:324px; width:580px;
  font-size:14px; color:rgba(255,255,255,0.60); line-height:1.5;
}
/* Bottom accent strip */
.bottom-strip {
  position:absolute; bottom:0; left:0; width:100%; height:4px;
  background: linear-gradient(to right, var(--sf-teal), var(--sf-blue), transparent);
}
</style></head><body>
<div class="slide">
  <div class="ghost-num">02</div>
  <div class="accent-line"></div>
  <div class="chapter-label">Chapter 02</div>
  <div class="chapter-title">Engagement<br>Context &amp; Scope</div>
  <div class="chapter-subtitle">Understanding where Okta is today and where we are taking them</div>
  <div class="bottom-strip"></div>
</div>
</body></html>
```

---

### S3 — Agenda Slide

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-grid:#DDDDDD;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
/* Edge bar */
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
/* Header */
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
/* Footer */
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
/* Agenda items */
.agenda-grid {
  position:absolute; left:38px; top:100px;
  width:876px; height:390px;
  display:grid;
  grid-template-columns: repeat(5, 1fr);
  gap:12px;
}
.agenda-item {
  background: var(--sf-light-bg);
  border-radius:8px; overflow:hidden;
  display:flex; flex-direction:column;
}
.agenda-num {
  background: var(--sf-mid-blue);
  padding: 12px 16px;
  font-size: 28px; font-weight:700; color:var(--sf-white);
  letter-spacing:-0.02em; line-height:1;
}
.agenda-num span {
  display:block; font-size:9px; font-weight:400;
  color: rgba(255,255,255,0.6); letter-spacing:0.08em; margin-top:2px;
}
.agenda-label {
  padding: 10px 12px;
  font-size: 10.5px; font-weight:700; color:var(--sf-dark-text);
  text-transform:uppercase; letter-spacing:0.03em; line-height:1.3;
  flex: 1;
}
.agenda-desc {
  padding: 0 12px 10px;
  font-size: 8.5px; color:var(--sf-body-grey); line-height:1.45;
}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">AGENDA</div>
  <div class="slide-subtitle">What we'll cover today</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="agenda-grid">
    <div class="agenda-item">
      <div class="agenda-num">01<span>About Us</span></div>
      <div class="agenda-label">Our Team</div>
      <div class="agenda-desc">Who we are and how we partner</div>
    </div>
    <div class="agenda-item">
      <div class="agenda-num">02<span>Context</span></div>
      <div class="agenda-label">Scope &amp; Objectives</div>
      <div class="agenda-desc">What we're solving and why it matters</div>
    </div>
    <div class="agenda-item">
      <div class="agenda-num">03<span>Delivery</span></div>
      <div class="agenda-label">How We Deliver</div>
      <div class="agenda-desc">Approach, timeline, and milestones</div>
    </div>
    <div class="agenda-item">
      <div class="agenda-num">04<span>Working</span></div>
      <div class="agenda-label">Ways of Working</div>
      <div class="agenda-desc">Cadence, tools, and collaboration norms</div>
    </div>
    <div class="agenda-item">
      <div class="agenda-num">05<span>Q&A</span></div>
      <div class="agenda-label">Open Questions</div>
      <div class="agenda-desc">Discovery items &amp; next steps</div>
    </div>
  </div>
</div>
</body></html>
```

---

### S4 — Single Column Content (Bullets)

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-light-blue:#E8F4FD;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
.content{position:absolute;left:38px;top:96px;width:876px;}
.section-heading{font-size:13px;font-weight:700;color:var(--sf-mid-blue);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;margin-top:14px;}
.section-heading:first-child{margin-top:0;}
.bullet-list{list-style:none;padding:0;}
.bullet-list li{font-size:10.5px;color:var(--sf-dark-text);line-height:1.55;padding-left:16px;position:relative;margin-bottom:4px;}
.bullet-list li::before{content:'';position:absolute;left:0;top:7px;width:5px;height:5px;border-radius:50%;background:var(--sf-blue);}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">WHY WE'RE HERE</div>
  <div class="slide-subtitle">Okta's data platform challenges and what success looks like</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="content">
    <div class="section-heading">Current State Challenges</div>
    <ul class="bullet-list">
      <li>Snowflake architecture is functional but unoptimized — no consistent medallion Bronze/Silver/Gold pattern</li>
      <li>22 TB of redundant SCD Type-1 snapshots consuming storage and compute budget</li>
      <li>Access controls are manual and role-heavy — no tag-based masking, no row-level security</li>
      <li>dbt adoption is nascent — high-value transformation logic remains in ad-hoc SQL</li>
    </ul>
    <div class="section-heading">Target State</div>
    <ul class="bullet-list">
      <li>Medallion architecture: governed Bronze ingestion → curated Silver → analytics-ready Gold</li>
      <li>SCD Type-2 implementation eliminating snapshot debt — proven to save 22 TB on a single table</li>
      <li>Layered RBAC model with SCIM provisioning, tag-based masking, and row-level security</li>
      <li>Accelerated dbt adoption with embedded Snowflake PS support and pattern library</li>
    </ul>
  </div>
</div>
</body></html>
```

---

### S5 — Two-Column Content

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-light-blue:#E8F4FD;--sf-orange:#FF9F36;--sf-light-amber:#FFF3E0;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
.two-col{position:absolute;left:38px;top:96px;width:876px;height:396px;display:grid;grid-template-columns:1fr 1fr;gap:16px;}
.col-panel{border-radius:8px;padding:16px 18px;overflow:hidden;}
.col-panel--light{background:var(--sf-light-bg);}
.col-panel--blue{background:var(--sf-mid-blue);}
.col-panel--accent{background:var(--sf-light-blue);border-left:4px solid var(--sf-blue);}
.col-heading{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--sf-mid-blue);margin-bottom:10px;}
.col-panel--blue .col-heading{color:var(--sf-teal);}
.bullet-list{list-style:none;padding:0;}
.bullet-list li{font-size:10px;line-height:1.55;padding-left:15px;position:relative;margin-bottom:5px;color:var(--sf-dark-text);}
.bullet-list li::before{content:'';position:absolute;left:0;top:6px;width:5px;height:5px;border-radius:50%;background:var(--sf-blue);}
.col-panel--blue .bullet-list li{color:rgba(255,255,255,0.88);}
.col-panel--blue .bullet-list li::before{background:var(--sf-teal);}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">FIRST 90 DAYS VS SECOND 90 DAYS</div>
  <div class="slide-subtitle">Phased outcomes across the full 180-day engagement</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="two-col">
    <div class="col-panel col-panel--blue">
      <div class="col-heading">Days 1–90: Foundation</div>
      <ul class="bullet-list">
        <li>Medallion architecture design reviewed and approved</li>
        <li>Bronze ingestion layer live for P0 Product Usage domain</li>
        <li>Greenfield RBAC role model designed and documented</li>
        <li>SCIM provisioning configured with Okta Identity</li>
        <li>SCD Type-2 pattern implemented on top 3 snapshot tables</li>
        <li>dbt project structure established with core patterns</li>
        <li>All deliverables in shared Google Drive + Jira tracked</li>
      </ul>
    </div>
    <div class="col-panel col-panel--light">
      <div class="col-heading">Days 91–180: Acceleration</div>
      <ul class="bullet-list">
        <li>Silver and Gold layers live for Product Usage and 2nd domain</li>
        <li>Tag-based masking and row-level security deployed</li>
        <li>Flyway schema migration tooling integrated</li>
        <li>Snowflake-managed Iceberg tables configured for AWS/Databricks</li>
        <li>dbt adoption embedded across 2+ engineering squads</li>
        <li>Full platform runbook and knowledge transfer completed</li>
        <li>Architecture decision records (ADRs) signed off</li>
      </ul>
    </div>
  </div>
</div>
</body></html>
```

---

### S6 — KPI Dashboard

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-orange:#FF9F36;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
/* KPI row */
.kpi-row{position:absolute;left:38px;top:96px;width:876px;height:100px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
.kpi-box{background:var(--sf-mid-blue);border-radius:8px;padding:14px 12px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.kpi-box--accent{background:var(--sf-blue);}
.kpi-value{font-size:30px;font-weight:700;color:var(--sf-white);letter-spacing:-0.03em;line-height:1;}
.kpi-label{font-size:8.5px;color:var(--sf-teal);margin-top:5px;line-height:1.35;}
.kpi-box--accent .kpi-label{color:rgba(255,255,255,0.75);}
/* Workstream table */
.table-area{position:absolute;left:38px;top:212px;width:876px;}
.ws-table{width:100%;border-collapse:collapse;}
.ws-table thead tr{background:var(--sf-mid-blue);}
.ws-table thead th{font-size:9px;font-weight:700;color:#fff;padding:7px 10px;text-align:left;text-transform:uppercase;letter-spacing:0.04em;}
.ws-table tbody tr:nth-child(odd){background:#F8FAFB;}
.ws-table tbody tr:nth-child(even){background:#fff;}
.ws-table tbody td{font-size:9px;color:#717171;padding:6px 10px;border-bottom:1px solid #DDDDDD;}
.ws-table tbody td:first-child{font-weight:700;color:var(--sf-dark-text);}
.tag{display:inline-block;background:var(--sf-light-bg);border:1px solid var(--sf-border);border-radius:3px;padding:1px 6px;font-size:7.5px;color:var(--sf-body-grey);}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">SCOPE SUMMARY</div>
  <div class="slide-subtitle">Five workstreams · 180 days · $245K investment</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="kpi-row">
    <div class="kpi-box"><div class="kpi-value">180</div><div class="kpi-label">Day Engagement<br>(April–October 2026)</div></div>
    <div class="kpi-box kpi-box--accent"><div class="kpi-value">5</div><div class="kpi-label">Workstreams<br>In Scope</div></div>
    <div class="kpi-box"><div class="kpi-value">650</div><div class="kpi-label">SA Hours<br>Keith Hoyle</div></div>
    <div class="kpi-box"><div class="kpi-value">156</div><div class="kpi-label">SDM Hours<br>Delivery Management</div></div>
  </div>
  <div class="table-area">
    <table class="ws-table">
      <thead><tr><th>Workstream</th><th>Phase 1 (Days 1–90)</th><th>Phase 2 (Days 91–180)</th><th>Key Tech</th></tr></thead>
      <tbody>
        <tr><td>1. Medallion Architecture</td><td>Bronze layer for Product Usage (P0)</td><td>Silver &amp; Gold + 2nd domain</td><td><span class="tag">Iceberg</span> <span class="tag">SCD2</span></td></tr>
        <tr><td>2. Access Controls &amp; RBAC</td><td>Greenfield role model design</td><td>Tag masking + RLS deploy</td><td><span class="tag">SCIM</span> <span class="tag">Flyway</span></td></tr>
        <tr><td>3. dbt Acceleration</td><td>Project structure + patterns</td><td>Embedded squad adoption</td><td><span class="tag">dbt</span> <span class="tag">Airflow</span></td></tr>
        <tr><td>4. Data Quality &amp; Observability</td><td>DMF coverage design</td><td>Automated alerting live</td><td><span class="tag">DMFs</span></td></tr>
        <tr><td>5. Governance &amp; Docs</td><td>ADR framework + runbook start</td><td>Full KT + handover</td><td><span class="tag">Confluence</span></td></tr>
      </tbody>
    </table>
  </div>
</div>
</body></html>
```

---

### S7 — Three/Four-Column Card Grid

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-orange:#FF9F36;--sf-grid:#DDDDDD;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
.card-grid{position:absolute;left:38px;top:96px;width:876px;height:396px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}
.card{border-radius:8px;overflow:hidden;display:flex;flex-direction:column;}
.card-header{padding:10px 14px 8px;display:flex;align-items:center;gap:10px;}
.card-header--blue{background:var(--sf-mid-blue);}
.card-header--accent{background:var(--sf-blue);}
.card-header--teal{background:linear-gradient(90deg,var(--sf-mid-blue),#0f4d72);}
.card-icon{font-size:18px;color:var(--sf-teal);}
.card-header--accent .card-icon{color:rgba(255,255,255,0.80);}
.card-title-text{font-size:11px;font-weight:700;color:var(--sf-white);text-transform:uppercase;letter-spacing:0.04em;line-height:1.2;}
.card-body{background:var(--sf-light-bg);padding:12px 14px;flex:1;}
.bullet-list{list-style:none;padding:0;}
.bullet-list li{font-size:9.5px;color:var(--sf-dark-text);line-height:1.5;padding-left:14px;position:relative;margin-bottom:4px;}
.bullet-list li::before{content:'';position:absolute;left:0;top:6px;width:4px;height:4px;border-radius:50%;background:var(--sf-blue);}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">DELIVERY APPROACH</div>
  <div class="slide-subtitle">Six principles that guide how Snowflake Professional Services delivers</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="card-grid">
    <div class="card">
      <div class="card-header card-header--blue"><span class="card-icon">◎</span><span class="card-title-text">Outcome-First</span></div>
      <div class="card-body"><ul class="bullet-list"><li>Every sprint ties to a measurable business outcome</li><li>No effort without a defined acceptance criterion</li></ul></div>
    </div>
    <div class="card">
      <div class="card-header card-header--accent"><span class="card-icon">⟳</span><span class="card-title-text">Iterative &amp; Agile</span></div>
      <div class="card-body"><ul class="bullet-list"><li>2-week sprint cadence with demo at every cycle</li><li>Scope pivots documented and re-prioritized fast</li></ul></div>
    </div>
    <div class="card">
      <div class="card-header card-header--blue"><span class="card-icon">⬡</span><span class="card-title-text">Knowledge Transfer</span></div>
      <div class="card-body"><ul class="bullet-list"><li>Build-alongside model — your team owns it on day 1</li><li>ADRs and runbooks written as we go, not at the end</li></ul></div>
    </div>
    <div class="card">
      <div class="card-header card-header--teal"><span class="card-icon">⬤</span><span class="card-title-text">Transparency</span></div>
      <div class="card-body"><ul class="bullet-list"><li>Weekly status with RAG health across workstreams</li><li>Risks surfaced immediately, not at retrospectives</li></ul></div>
    </div>
    <div class="card">
      <div class="card-header card-header--blue"><span class="card-icon">⊞</span><span class="card-title-text">Standards-Driven</span></div>
      <div class="card-body"><ul class="bullet-list"><li>Snowflake best-practice patterns, not custom hacks</li><li>All code reviewed against Okta's architecture principles</li></ul></div>
    </div>
    <div class="card">
      <div class="card-header card-header--accent"><span class="card-icon">↗</span><span class="card-title-text">Speed to Value</span></div>
      <div class="card-body"><ul class="bullet-list"><li>P0 domain (Product Usage) live in first 90 days</li><li>Quick wins shipped within sprint 2 to build momentum</li></ul></div>
    </div>
  </div>
</div>
</body></html>
```

---

### S8 — Horizontal Timeline / Roadmap

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-grid:#DDDDDD;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
/* Two phase panels */
.phases{position:absolute;left:38px;top:96px;width:876px;display:grid;grid-template-columns:1fr 1fr;gap:16px;}
.phase{border-radius:8px;overflow:hidden;}
.phase-header{padding:10px 16px 8px;display:flex;align-items:baseline;gap:12px;}
.phase-header--1{background:var(--sf-blue);}
.phase-header--2{background:var(--sf-mid-blue);}
.phase-num{font-size:36px;font-weight:700;color:rgba(255,255,255,0.25);line-height:1;letter-spacing:-0.04em;}
.phase-info{flex:1;}
.phase-label{font-size:10px;font-weight:700;color:var(--sf-white);text-transform:uppercase;letter-spacing:0.06em;}
.phase-dates{font-size:9px;color:rgba(255,255,255,0.65);margin-top:2px;}
.phase-content{background:var(--sf-light-bg);padding:14px 16px;}
.workstream-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;}
.workstream-row:last-child{margin-bottom:0;}
.ws-dot{width:8px;height:8px;border-radius:50%;background:var(--sf-blue);margin-top:4px;flex-shrink:0;}
.phase-header--2 ~ .phase-content .ws-dot{background:var(--sf-mid-blue);}
.ws-text{font-size:9.5px;color:var(--sf-dark-text);line-height:1.45;}
.ws-text strong{display:block;font-weight:700;color:var(--sf-mid-blue);font-size:9px;text-transform:uppercase;letter-spacing:0.03em;}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">180-DAY DELIVERY TIMELINE</div>
  <div class="slide-subtitle">Two phases — foundation then acceleration</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="phases">
    <div class="phase">
      <div class="phase-header phase-header--1">
        <div class="phase-num">1</div>
        <div class="phase-info"><div class="phase-label">Phase 1: Foundation</div><div class="phase-dates">April 2026 – July 2026 &nbsp;·&nbsp; 390 SA hrs · 78 SDM hrs</div></div>
      </div>
      <div class="phase-content">
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Architecture Design</strong>Medallion blueprint, data model review, ADR framework</div></div>
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Bronze Ingestion</strong>P0 Product Usage domain live in Snowflake, SCD Type-2 on top tables</div></div>
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Access Controls Design</strong>Greenfield RBAC role model, SCIM config, Flyway integration</div></div>
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>dbt Foundation</strong>Project structure, transformation patterns, first models in prod</div></div>
      </div>
    </div>
    <div class="phase">
      <div class="phase-header phase-header--2">
        <div class="phase-num">2</div>
        <div class="phase-info"><div class="phase-label">Phase 2: Acceleration</div><div class="phase-dates">July 2026 – October 2026 &nbsp;·&nbsp; 260 SA hrs · 78 SDM hrs</div></div>
      </div>
      <div class="phase-content">
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Silver &amp; Gold Layers</strong>Curated and analytics-ready tiers for Product Usage + 2nd domain</div></div>
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Security Deploy</strong>Tag-based masking, row-level security, access auditing live</div></div>
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Iceberg Tables</strong>Snowflake-managed Iceberg for AWS/Databricks MLOps interop</div></div>
        <div class="workstream-row"><div class="ws-dot"></div><div class="ws-text"><strong>Knowledge Transfer</strong>Full platform runbook, squad enablement, handover complete</div></div>
      </div>
    </div>
  </div>
</div>
</body></html>
```

---

### S9 — Team Cards

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-grid:#DDDDDD;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
.section-label{position:absolute;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;color:var(--sf-body-grey);}
.teams-wrap{position:absolute;left:38px;top:98px;width:876px;}
.team-row{display:flex;gap:12px;margin-bottom:14px;}
.team-card{border-radius:8px;overflow:hidden;display:flex;gap:0;flex:1;}
.avatar{width:52px;min-width:52px;display:flex;align-items:center;justify-content:center;font-size:22px;}
.avatar--sf{background:var(--sf-mid-blue);}
.avatar--client{background:var(--sf-light-bg);border:1px solid var(--sf-grid);}
.person{flex:1;padding:10px 14px;}
.person--sf{background:linear-gradient(135deg,var(--sf-mid-blue) 0%,#0e3f5e 100%);}
.person--client{background:var(--sf-light-bg);}
.person-name{font-size:11px;font-weight:700;color:var(--sf-white);}
.person--client .person-name{color:var(--sf-dark-text);}
.person-role{font-size:9px;color:var(--sf-teal);margin-top:2px;}
.person--client .person-role{color:var(--sf-body-grey);}
.person-bio{font-size:8.5px;color:rgba(255,255,255,0.70);margin-top:5px;line-height:1.4;}
.person--client .person-bio{color:var(--sf-body-grey);}
.divider-label{font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;color:var(--sf-body-grey);border-top:1px solid var(--sf-grid);padding-top:8px;margin-bottom:10px;}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">OUR TEAM</div>
  <div class="slide-subtitle">Your dedicated Snowflake Professional Services team + key Okta stakeholders</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="teams-wrap">
    <div class="team-row">
      <div class="team-card">
        <div class="avatar avatar--sf">❄</div>
        <div class="person person--sf"><div class="person-name">Keith Hoyle</div><div class="person-role">Solutions Architect · Snowflake PS</div><div class="person-bio">Technical lead for the engagement. Deep expertise in Snowflake medallion architecture, RBAC design, and data platform modernization for SaaS companies.</div></div>
      </div>
      <div class="team-card">
        <div class="avatar avatar--sf">❄</div>
        <div class="person person--sf"><div class="person-name">TBD</div><div class="person-role">Delivery Manager · Snowflake PS</div><div class="person-bio">Program management, sprint coordination, stakeholder communications, and risk tracking across all workstreams.</div></div>
      </div>
      <div class="team-card">
        <div class="avatar avatar--sf">❄</div>
        <div class="person person--sf"><div class="person-name">Sam Maurer</div><div class="person-role">Program Manager · Snowflake PS</div><div class="person-bio">Executive oversight, commercial governance, and strategic alignment between Okta and Snowflake leadership throughout the engagement.</div></div>
      </div>
    </div>
    <div class="divider-label">Okta Counterparts</div>
    <div class="team-row">
      <div class="team-card">
        <div class="avatar avatar--client">👤</div>
        <div class="person person--client"><div class="person-name">Jane Smith</div><div class="person-role">Data Platform Lead · Okta</div><div class="person-bio">Primary technical sponsor. Owns the Snowflake platform and data engineering roadmap at Okta.</div></div>
      </div>
      <div class="team-card">
        <div class="avatar avatar--client">👤</div>
        <div class="person person--client"><div class="person-name">John Doe</div><div class="person-role">Program Lead · Okta</div><div class="person-bio">Engagement coordinator. Manages internal stakeholder alignment, Jira/Smartsheet tracking, and sprint reviews.</div></div>
      </div>
      <div class="team-card">
        <div class="avatar avatar--client">👤</div>
        <div class="person person--client"><div class="person-name">+ Okta SMEs</div><div class="person-role">dbt Eng · Security/Gov · Product Usage</div><div class="person-bio">Domain leads embedded in each workstream sprint. Participation defined in RACI.</div></div>
      </div>
    </div>
  </div>
</div>
</body></html>
```

---

### S10 — Data Table (RACI / Deliverables)

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--sf-grid:#DDDDDD;--sf-light-row:#F8FAFB;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
.table-wrap{position:absolute;left:38px;top:92px;width:876px;}
.raci-table{width:100%;border-collapse:collapse;}
.raci-table thead tr{background:var(--sf-mid-blue);}
.raci-table thead th{font-size:9px;font-weight:700;color:var(--sf-white);padding:7px 10px;text-align:left;text-transform:uppercase;letter-spacing:0.04em;}
.raci-table thead th.center{text-align:center;}
.raci-table tbody tr:nth-child(odd){background:var(--sf-light-row);}
.raci-table tbody tr:nth-child(even){background:var(--sf-white);}
.raci-table tbody td{font-size:9px;color:#717171;padding:5px 10px;border-bottom:1px solid var(--sf-grid);}
.raci-table tbody td.activity{font-weight:700;color:var(--sf-dark-text);}
.raci-table tbody td.center{text-align:center;}
.badge{display:inline-block;border-radius:3px;padding:2px 8px;font-size:8px;font-weight:700;text-align:center;min-width:22px;}
.badge-r{background:var(--sf-blue);color:var(--sf-white);}
.badge-a{background:var(--sf-mid-blue);color:var(--sf-white);}
.badge-c{background:var(--sf-light-bg);color:var(--sf-body-grey);border:1px solid var(--sf-grid);}
.badge-i{background:var(--sf-light-bg);color:var(--sf-body-grey);border:1px solid var(--sf-grid);}
.legend{display:flex;gap:16px;margin-bottom:8px;align-items:center;}
.legend-item{font-size:8px;color:var(--sf-body-grey);display:flex;align-items:center;gap:4px;}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">ROLES &amp; RESPONSIBILITIES (RACI)</div>
  <div class="slide-subtitle">Clear accountability across Snowflake SD and Okta for each engagement activity</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="table-wrap">
    <div class="legend">
      <span class="legend-item"><span class="badge badge-r">R</span> Responsible</span>
      <span class="legend-item"><span class="badge badge-a">A</span> Accountable</span>
      <span class="legend-item"><span class="badge badge-c">C</span> Consulted</span>
      <span class="legend-item"><span class="badge badge-i">I</span> Informed</span>
    </div>
    <table class="raci-table">
      <thead><tr><th>Activity</th><th class="center">Snowflake SD</th><th class="center">Okta</th></tr></thead>
      <tbody>
        <tr><td class="activity">Architecture design &amp; ADRs</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-a">A</span></td></tr>
        <tr><td class="activity">Bronze layer development</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-c">C</span></td></tr>
        <tr><td class="activity">RBAC role model design</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-a">A</span></td></tr>
        <tr><td class="activity">SCIM &amp; Flyway configuration</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-c">C</span></td></tr>
        <tr><td class="activity">dbt patterns &amp; project structure</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-a">A</span></td></tr>
        <tr><td class="activity">Sprint planning &amp; prioritization</td><td class="center"><span class="badge badge-a">A</span></td><td class="center"><span class="badge badge-r">R</span></td></tr>
        <tr><td class="activity">Stakeholder access &amp; approvals</td><td class="center"><span class="badge badge-c">C</span></td><td class="center"><span class="badge badge-r">R</span></td></tr>
        <tr><td class="activity">UAT &amp; acceptance testing</td><td class="center"><span class="badge badge-c">C</span></td><td class="center"><span class="badge badge-r">R</span></td></tr>
        <tr><td class="activity">Weekly status reporting</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-i">I</span></td></tr>
        <tr><td class="activity">Production deployment decisions</td><td class="center"><span class="badge badge-c">C</span></td><td class="center"><span class="badge badge-a">A</span></td></tr>
        <tr><td class="activity">Knowledge transfer &amp; runbook</td><td class="center"><span class="badge badge-r">R</span></td><td class="center"><span class="badge badge-a">A</span></td></tr>
      </tbody>
    </table>
  </div>
</div>
</body></html>
```

---

### S11 — Ways of Working (4-Column)

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-dark-text:#262626;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--sf-teal:#71D3DC;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:#fff;}
.edge-bar{position:absolute;left:0;top:36px;width:4px;height:38px;background:var(--sf-blue);}
.slide-title{position:absolute;left:38px;top:29px;font-size:18px;font-weight:700;color:var(--sf-dark-text);text-transform:uppercase;letter-spacing:0.04em;}
.slide-subtitle{position:absolute;left:38px;top:56px;font-size:12px;color:var(--sf-body-grey);}
.footer{position:absolute;left:38px;top:511px;font-size:7px;color:var(--sf-body-grey);}
.wow-grid{position:absolute;left:38px;top:98px;width:876px;height:396px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
.wow-col{display:flex;flex-direction:column;gap:0;border-radius:8px;overflow:hidden;}
.wow-header{background:var(--sf-mid-blue);padding:10px 14px;font-size:10.5px;font-weight:700;color:var(--sf-white);text-transform:uppercase;letter-spacing:0.05em;display:flex;align-items:center;gap:8px;}
.wow-header .icon{font-size:14px;opacity:0.80;}
.wow-items{background:var(--sf-light-bg);flex:1;padding:12px 14px;display:flex;flex-direction:column;gap:0;}
.wow-item{padding:7px 0;border-bottom:1px solid #E0E0E0;display:flex;flex-direction:column;}
.wow-item:last-child{border-bottom:none;}
.wow-item-label{font-size:9px;font-weight:700;color:var(--sf-mid-blue);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:2px;}
.wow-item-value{font-size:9px;color:var(--sf-dark-text);line-height:1.4;}
</style></head><body>
<div class="slide">
  <div class="edge-bar"></div>
  <div class="slide-title">WAYS OF WORKING</div>
  <div class="slide-subtitle">How we collaborate, communicate, and track progress together</div>
  <div class="footer">Confidential — Snowflake Professional Services</div>
  <div class="wow-grid">
    <div class="wow-col">
      <div class="wow-header"><span class="icon">📅</span>Cadence</div>
      <div class="wow-items">
        <div class="wow-item"><div class="wow-item-label">Weekly Sync</div><div class="wow-item-value">60-min status meeting, every Tuesday 10am PT</div></div>
        <div class="wow-item"><div class="wow-item-label">Sprint Review</div><div class="wow-item-value">Bi-weekly demo at end of each 2-week sprint</div></div>
        <div class="wow-item"><div class="wow-item-label">Monthly Exec</div><div class="wow-item-value">30-min executive update with leadership</div></div>
        <div class="wow-item"><div class="wow-item-label">Phase Gate</div><div class="wow-item-value">Formal sign-off at 90-day milestone</div></div>
      </div>
    </div>
    <div class="wow-col">
      <div class="wow-header"><span class="icon">💬</span>Communication</div>
      <div class="wow-items">
        <div class="wow-item"><div class="wow-item-label">Async Channel</div><div class="wow-item-value">Shared Slack workspace for day-to-day Q&amp;A</div></div>
        <div class="wow-item"><div class="wow-item-label">Escalation Path</div><div class="wow-item-value">SDM → Sam Maurer → Snowflake AE</div></div>
        <div class="wow-item"><div class="wow-item-label">Response SLA</div><div class="wow-item-value">4-hour reply on Slack, same-day on email</div></div>
        <div class="wow-item"><div class="wow-item-label">Decisions</div><div class="wow-item-value">All decisions logged in ADR register</div></div>
      </div>
    </div>
    <div class="wow-col">
      <div class="wow-header"><span class="icon">📊</span>Tracking &amp; Artifacts</div>
      <div class="wow-items">
        <div class="wow-item"><div class="wow-item-label">Project Board</div><div class="wow-item-value">Jira / Smartsheet for sprint backlog + milestones</div></div>
        <div class="wow-item"><div class="wow-item-label">Documents</div><div class="wow-item-value">Shared Google Drive — all artifacts here</div></div>
        <div class="wow-item"><div class="wow-item-label">Status Report</div><div class="wow-item-value">Weekly RAG report sent by SDM on Fridays</div></div>
        <div class="wow-item"><div class="wow-item-label">Code</div><div class="wow-item-value">Okta GitHub repo, PR-based review process</div></div>
      </div>
    </div>
    <div class="wow-col">
      <div class="wow-header"><span class="icon">🤝</span>Engagement Norms</div>
      <div class="wow-items">
        <div class="wow-item"><div class="wow-item-label">Access</div><div class="wow-item-value">Okta provides Snowflake env access within 5 days of kickoff</div></div>
        <div class="wow-item"><div class="wow-item-label">Attendance</div><div class="wow-item-value">Required: technical lead + PM on all sprint ceremonies</div></div>
        <div class="wow-item"><div class="wow-item-label">Scope Changes</div><div class="wow-item-value">Change requests submitted via SDM, approved before work starts</div></div>
        <div class="wow-item"><div class="wow-item-label">Sign-off</div><div class="wow-item-value">All deliverables reviewed by Okta DL within 5 business days</div></div>
      </div>
    </div>
  </div>
</div>
</body></html>
```

---

### S12 — Thank You / Closing

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
:root{--sf-blue:#29B5E8;--sf-mid-blue:#11567F;--sf-white:#FFFFFF;--sf-teal:#71D3DC;--sf-body-grey:#5B5B5B;--sf-light-bg:#F5F5F5;--font:Arial,'Helvetica Neue',Helvetica,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:960px;height:540px;overflow:hidden;font-family:var(--font);-webkit-font-smoothing:antialiased;}
.slide{width:960px;height:540px;position:relative;overflow:hidden;background:var(--sf-blue);}
.slide::before{content:'';position:absolute;inset:0;background:linear-gradient(145deg,transparent 45%,rgba(0,0,0,0.20) 100%);}
.bg-circle-1{position:absolute;top:-150px;right:-80px;width:420px;height:420px;border-radius:50%;background:rgba(255,255,255,0.05);}
.bg-circle-2{position:absolute;bottom:-100px;left:-60px;width:280px;height:280px;border-radius:50%;background:rgba(17,86,127,0.40);}
.wave{position:absolute;bottom:0;left:0;width:100%;height:90px;background:var(--sf-mid-blue);clip-path:ellipse(110% 80px at 30% 100%);}
.logo-area{position:absolute;top:32px;left:38px;display:flex;align-items:center;gap:10px;}
.logo-snowflake{font-size:22px;color:var(--sf-white);opacity:0.90;}
.logo-text{font-size:13px;font-weight:700;color:var(--sf-white);letter-spacing:0.12em;text-transform:uppercase;opacity:0.90;}
.thank-you{position:absolute;left:38px;top:140px;font-size:72px;font-weight:700;color:var(--sf-white);text-transform:uppercase;letter-spacing:-0.02em;line-height:1;}
.tagline{position:absolute;left:42px;top:290px;font-size:16px;color:rgba(255,255,255,0.75);letter-spacing:0.02em;}
.contact-row{position:absolute;left:38px;top:350px;display:flex;gap:40px;}
.contact-item{display:flex;flex-direction:column;}
.contact-name{font-size:11px;font-weight:700;color:var(--sf-white);}
.contact-role{font-size:9px;color:rgba(255,255,255,0.65);margin-top:2px;}
.contact-info{font-size:9px;color:var(--sf-teal);margin-top:3px;}
.divider-vert{width:1px;background:rgba(255,255,255,0.25);height:60px;margin-top:auto;}
.bottom-text{position:absolute;left:38px;bottom:16px;font-size:8px;color:rgba(255,255,255,0.45);}
</style></head><body>
<div class="slide">
  <div class="bg-circle-1"></div>
  <div class="bg-circle-2"></div>
  <div class="wave"></div>
  <div class="logo-area"><span class="logo-snowflake">❄</span><span class="logo-text">Snowflake Professional Services</span></div>
  <div class="thank-you">Thank You</div>
  <div class="tagline">Let's build something great together.</div>
  <div class="contact-row">
    <div class="contact-item">
      <div class="contact-name">Keith Hoyle</div>
      <div class="contact-role">Solutions Architect</div>
      <div class="contact-info">keith.hoyle@snowflake.com</div>
    </div>
    <div class="divider-vert"></div>
    <div class="contact-item">
      <div class="contact-name">Sam Maurer</div>
      <div class="contact-role">Program Manager</div>
      <div class="contact-info">sam.maurer@snowflake.com</div>
    </div>
  </div>
  <div class="bottom-text">Confidential — Snowflake Professional Services · © 2026 Snowflake Inc.</div>
</div>
</body></html>
```

---

## 4. Snowflake Brand Rules

### Logo Usage

The Snowflake logo appears on **cover slides** and optionally on chapter dividers. Rules from the official 2026 brand guide:

- **Blue logo** (`snowflake-logo-blue.svg`) on white or light/dotted backgrounds
- **White logo** (`snowflake-logo-white.svg`) on Snowflake Blue, dark backgrounds, or image overlays
- **Minimum clear space**: equal to the x-height of the logo on all four sides — never crowd the logo
- **Resize proportionally** only — never stretch or distort
- Never recolor the logo or use off-brand logo versions
- The "bug" (snowflake icon only, no wordmark) may be used in tight spaces or as a decorative accent

**HTML implementation** — include as an `<img>` tag referencing the CDN or a local asset path:
```html
<!-- Blue wordmark — use on white/light slides -->
<img src="snowflake-logo-blue.png" style="height:28px; display:block;">

<!-- White wordmark — use on dark/blue slides -->
<img src="snowflake-logo-white.png" style="height:28px; display:block;">
```

When a logo file is not available, represent with the styled text mark:
```html
<div class="sf-wordmark">SNOWFLAKE</div>
```
```css
.sf-wordmark {
  font-family: Arial, sans-serif; font-size: 13px; font-weight: 700;
  color: var(--sf-blue); letter-spacing: 0.15em;
}
```

---

### Typography Rules (Official 2026 Standard)

| Element | Size | Weight | Case | Color |
|---|---|---|---|---|
| Cover / Chapter title | 44px | Bold | **ALL CAPS** | White (on dark bg) |
| Cover subtitle | 18px | Bold | Title case | White |
| Content slide title | 18px | Bold | **Title case — NOT all caps** | `--sf-dark-text` |
| Slide subtitle | 12px | Regular | Sentence case | `--sf-body-grey` |
| Section/card header | 11–13px | Bold | Title case or caps | Varies |
| Body copy | 10px | Regular | Sentence case | `--sf-dark-text` |
| Small body | 9px | Regular | Sentence case | `--sf-body-grey` |
| Big numbers (KPI) | 28–44px | Bold | — | `--sf-white` or `--sf-blue` |
| Footer / copyright | 6px | Regular | — | `#929292` |
| Page number | 6px | Regular | — | `#919191` |

**Important:** `text-transform: uppercase` in CSS is for **cover and chapter titles only**. Do not apply it to `.slide-title`, body copy, card headers, or any other element.

---

### Color Usage Rules

Colors in priority order — use earlier entries first, reach for secondary only when needed:

| Color | Hex | Official Name | Use |
|---|---|---|---|
| `--sf-blue` | `#29B5E8` | Snowflake Blue | Primary brand, accent bars, badges, links |
| `--sf-mid-blue` | `#11567F` | Mid-Blue | Section headers, dark panels, card headers |
| `--sf-dark-text` | `#262626` | — | All body text on white backgrounds |
| `--sf-body-grey` | `#5B5B5B` | Medium Gray | Subtitles, captions, secondary text |
| `--sf-light-bg` | `#F5F5F5` | — | Card/panel backgrounds |
| `--sf-teal` | `#75CDD7` | Star Blue | Accents, KPI labels, dividers |
| `--sf-orange` | `#FF9F36` | Valencia Orange | Alerts, highlights — sparingly |
| `--sf-violet` | `#7254A3` | Purple Moon | Sparingly only |
| `--sf-pink` | `#D45B90` | First Light | Sparingly only |
| `--sf-midnight` | `#000000` | Midnight | Near-black elements when needed |

**Rule:** Most slides need only the first 5 colors. Secondary colors (teal through midnight) should appear on fewer than 20% of slides.

---

### Footer & Page Number (Required on All Content Slides)

Every non-cover, non-chapter slide **must** include:

1. **Copyright line** — bottom left:
```html
<div class="slide-footer">© 2026 Snowflake Inc. All Rights Reserved</div>
```

2. **Page number** — bottom right:
```html
<div class="slide-page-num">3</div>
```

```css
.slide-footer {
  position: absolute; left: var(--pad-left); top: var(--footer-top);
  font-size: 6px; color: #929292; font-family: Arial, sans-serif;
}
.slide-page-num {
  position: absolute; right: 20px; top: var(--footer-top);
  font-size: 6px; color: #919191; text-align: right; font-family: Arial, sans-serif;
}
```

---

## 5. Design Tips

**Visual variety**: Avoid 3+ consecutive single-column bullet slides. Alternate between card grids, KPI rows, tables, and two-column layouts.

**Overflow guard**: Every slide must have `overflow: hidden` on both `html/body` and `.slide`. If content might overflow, reduce font sizes or cut content before running conversion.

**Dark backgrounds**: Use `--sf-mid-blue` or `--sf-blue` backgrounds for Chapter, Cover, and Thank You slides. White for all content slides. Never use non-brand colors.

**Contrast rule**: White text on `--sf-mid-blue` and `--sf-blue` only. Dark text (`--sf-dark-text`) on white and light backgrounds. Never white text on `--sf-teal` or `--sf-orange` (too light).

**Typography scale**: Cover/chapter titles = 44px bold ALL CAPS. Content slide titles = 18px bold title case (NOT all caps). Section headings = 11–13px bold. Body = 9.5–10.5px. Labels/metadata = 8–9px. Footer = 6px.

**Spacing reference**: `var(--pad-left)` = 38px for all left-edge content. Content should not extend past `var(--safe-bottom)` = 490px from top. Footer sits at 511px.
