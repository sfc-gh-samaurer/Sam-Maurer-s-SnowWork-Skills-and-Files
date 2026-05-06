# PS Engagement & Go-Live Dashboard

Regional dashboard for tracking Professional Services engagement coverage, go-live readiness, and delivery risk across district and regional views.

## Architecture

The dashboard exists in two versions:

### v1 — Streamlit in Snowflake (SiS)

- **File**: `streamlit_app.py` (1,255 lines)
- **Deployed to**: `PST.PS_APPS_DEV.PS_ENGAGEMENT_DASHBOARD`
- **Warehouse**: `PST_STEAMLIT_APPS`
- **Stack**: Python, Streamlit, Plotly, Snowpark
- **Status**: Production (fallback)

### v2 — SPCS React Application

- **Directory**: `v2/`
- **Deployed to**: `PST.PS_ACCOUNT_REVIEW.PS_ENGAGEMENT_DASHBOARD_V2` (SPCS service)
- **Compute Pool**: `SD_WH_APPS_COMPUTE_POOL`
- **Image Repo**: `PST.PS_ACCOUNT_REVIEW.MY_IMAGE_REPO`
- **Stack**: Next.js 16, React 19, Tremor, Nivo, Tailwind CSS, Snowflake Node.js SDK
- **Status**: In development

```
┌──────────────────────────────────────────────┐
│           SPCS Container (Next.js 16)         │
│  ┌──────────────────────────────────────────┐ │
│  │  React Frontend (Client-side)             │ │
│  │  ├─ Tremor v3  (KPI cards, tabs, layout) │ │
│  │  ├─ Nivo v0.88 (charts: bar, line, pie)  │ │
│  │  └─ Tailwind CSS (Crystalline Lab tokens) │ │
│  ├──────────────────────────────────────────┤ │
│  │  Next.js API Routes (Server-side)         │ │
│  │  └─ snowflake-sdk (OAuth from SPCS)       │ │
│  └──────────────────────────────────────────┘ │
│  Base: node:22-alpine (LTS, patched)          │
│  React: 19.2.4+ (post-RCE patch)             │
│  Next.js: 16.1.x (post-CVE-2025-66478 patch) │
└──────────────────────────────────────────────┘
         │  SQL queries (OAuth token)
         ▼
┌──────────────────────────────────────────────┐
│  Snowflake Data Sources                       │
│  ├─ PST.PS_APPS_DEV.SDA_USE_CASES_CACHE      │
│  ├─ PST.PS_APPS_DEV.PS_DASHBOARD_SNAPSHOTS   │
│  ├─ PST.PS_APPS_DEV.ENGAGEMENT_THEMES_CACHE  │
│  ├─ PST.PS_APPS_DEV.PROJECT_HEALTH_SNAPSHOTS │
│  ├─ SMARTSHEET_DB.RAW_SMARTSHEET.SHEET_*      │
│  └─ SALES.SE_REPORTING.DIM_ACCOUNTS_SLIM_SLIM│
└──────────────────────────────────────────────┘
```

## Design System: Crystalline Lab

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#006686` | Headers, active states |
| Accent | `#29B5E8` | Links, highlights, chart emphasis |
| Surface | `#F9F9FF` | Page background |
| Card | `#FFFFFF` | Card backgrounds |
| Text | `#141B2B` | Body text |
| Muted | `#5A6578` | Secondary text, labels |
| Headlines | Manrope 800 | Dashboard title, section headers |
| Body | Inter 400/500 | All body text, metrics |

## Dashboard Sections

1. **KPI Row** — 6 cards: PS-Engaged EACV, Use Cases, Attach Rate, Account Penetration, Go-Lives, At Risk
2. **District/Regional View** — Tabbed: engagement breakdown by district, regional thematic POV
3. **Cohort Analytics** — 2x2 grid: ACV Band attach, Segment attach, EACV trend WoW, Go-Live quarter movement
4. **PS Impact by Engagement Type** — Summary table with workload context
5. **Go-Live Readiness + Engagement Opportunity** — Side-by-side detail tables
6. **Delivery Risk & Action** — Red accounts with issue/action tracking
7. **District Breakdown** — Per-district metrics and UC counts

## Data Sources

| Table | Purpose | Refresh |
|-------|---------|---------|
| `SDA_USE_CASES_CACHE` | Use cases, engagement flags, ACV, segments | Daily (scheduled task) |
| `PS_DASHBOARD_SNAPSHOTS` | Point-in-time snapshots for WoW trending | Weekly (scheduled task) |
| `ENGAGEMENT_THEMES_CACHE` | Regional thematic narratives | On-demand |
| `PROJECT_HEALTH_SNAPSHOTS` | Smartsheet project health data | Daily |
| `DIM_ACCOUNTS_SLIM_SLIM` | Account metadata (tier, industry, ARR) | Upstream managed |

## Deployment

### v1 (Streamlit)

```bash
cd ~/.drewos/apps/ps-engagement-dashboard
snow streamlit deploy --replace -c SnowhouseHeadless
```

### v2 (SPCS)

```bash
cd ~/.drewos/apps/ps-engagement-dashboard/v2

# Build and push Docker image
docker build -t ps-engagement-dashboard:latest .
docker tag ps-engagement-dashboard:latest \
  sfcogsops-snowhouse-aws-us-west-2.registry.snowflakecomputing.com/pst/ps_account_review/my_image_repo/ps-engagement-dashboard:latest
docker push \
  sfcogsops-snowhouse-aws-us-west-2.registry.snowflakecomputing.com/pst/ps_account_review/my_image_repo/ps-engagement-dashboard:latest

# Create/update SPCS service (via Snowflake SQL)
# See spec.yaml for service specification
```

## FY Quarter Logic

Snowflake fiscal year offset: Feb = Q1, May = Q2, Aug = Q3, Nov = Q4.

```
Q1: Feb 1 – Apr 30
Q2: May 1 – Jul 31
Q3: Aug 1 – Oct 31
Q4: Nov 1 – Jan 31
```

## Security

See [SECURITY.md](SECURITY.md) for dependency audit, CVE analysis, and maintenance policy.
