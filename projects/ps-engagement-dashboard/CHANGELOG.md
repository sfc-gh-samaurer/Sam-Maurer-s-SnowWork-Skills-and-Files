# Changelog

All notable changes to the PS Engagement & Go-Live Dashboard.

## [2.0.0] — In Development

### Migration: Streamlit in Snowflake → SPCS React Application

**Why**: The SiS runtime constrains what we can build. Missing `st.metric(border=True)`, full server reruns on every interaction, CSS injection hacks for basic styling, and Plotly-only charting limit the fidelity of the Stitch v3 mock. SPCS with React gives us pixel-perfect control, instant client-side interactivity, and access to purpose-built charting libraries.

**What's changing**:
- **Framework**: Python/Streamlit → Next.js 16 (TypeScript, App Router)
- **Charting**: Plotly → Nivo (D3-based: grouped bars, waterfall, line, donut)
- **Layout/Cards**: CSS injection → Tremor v3 (KPI cards, tabs, grids)
- **Styling**: st.markdown CSS hacks → Tailwind CSS with Crystalline Lab design tokens
- **Data access**: Snowpark → Snowflake Node.js SDK (OAuth from SPCS context)
- **Deployment**: `snow streamlit deploy` → Docker build + `CREATE SERVICE` on SPCS
- **Hosting**: SiS managed compute → `SD_WH_APPS_COMPUTE_POOL` (SPCS)

**What stays the same**:
- All SQL queries and business logic (ported from Python to TypeScript)
- Data sources (cache tables, Smartsheet, snapshots)
- FY quarter logic, role definitions, risk classification
- Dashboard sections and layout structure (matching Stitch v3 mock)

**What's net-new**:
- Client-side interactivity (instant tab switches, filter changes — no server rerun)
- Proper responsive layout with CSS Grid / Tailwind
- Docker container with security hardening
- SPCS service with OAuth-gated public endpoint
- Dependency security audit and maintenance policy (see SECURITY.md)

**v1 Streamlit app**: Remains deployed at `PST.PS_APPS_DEV.PS_ENGAGEMENT_DASHBOARD` as fallback.

## [1.1.0] — 2026-04-08

### Crystalline Lab Design System & Cohort Analytics

#### Added
- Crystalline Lab design system implementation via CSS injection (Stitch v3 mock)
  - Primary `#006686`, Accent `#29B5E8`, Surface `#F9F9FF`, Card `#FFFFFF`
  - Manrope headlines, Inter body, frosted-glass card effects
- Row 2.5: Cohort Analytics & Trends section (2x2 grid)
  - Attach Rate by ACV Band — `pd.cut()` on ARR into 4 bands, Plotly bar chart
  - Attach Rate by Customer Segment — top 6 segments, Plotly bar
  - PS-Engaged EACV Trend WoW — Plotly scatter+lines from snapshots
  - Go-Live Quarter Movement — Plotly waterfall (Start → Moved Out → Moved In → Net)
- Plotly dependency added to `environment.yml`
- SEGMENT, INDUSTRY, ARR columns added to `refresh_cache.sql`

#### Fixed
- **ACV KeyError** (`KeyError: "['ACV'] not in index"` at line 1048): Moved `ps_engaged["ACV"]` column creation to before `flag_only` DataFrame derivation
- **st.metric border**: Removed `border=True` parameter incompatible with SiS runtime
- **District column casing**: Fixed `KeyError: 'District'` — Snowflake returns UPPERCASE columns

## [1.0.0] — 2026-03-19

### Initial Release

- PS Engagement & Go-Live Dashboard deployed to Streamlit in Snowflake
- KPI cards: PS-Engaged EACV, Use Cases, UC Attach Rate, Account Penetration, Go-Lives, At Risk
- District engagement breakdown with bar charts
- Go-Live readiness tracking with quarterly filtering
- Engagement opportunity pipeline
- Delivery risk and action table
- Regional thematic POV (expandable)
- Data refresh via scheduled Snowflake tasks
