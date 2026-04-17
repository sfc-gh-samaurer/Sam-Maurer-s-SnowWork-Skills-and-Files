---
name: engagement-status-report
description: "Generate automated weekly engagement status reports for Snowflake PS accounts. Creates a 2-slide PowerPoint deck (Program Status Overview + Hour Tracking), uploads to Google Slides in Drive, and creates a Gmail draft. Use for: status report, weekly update, engagement status, account status, project status, weekly deck, status slides."
---

# Engagement Status Report Generator

## Overview
Generates weekly status reports for Snowflake Professional Services engagements. For each account:
1. Gathers recent activity from Slack, Email, Salesforce timecards, and other connected sources
2. Creates a 2-slide Snowflake-branded PowerPoint deck
3. Uploads it as native Google Slides to the user's Google Drive (`SnowWork → Accounts → {AccountName} → Weekly Status`)
4. Creates a Gmail draft with the Google Slides link, ready to send to the customer

## Prerequisites
- **Glean MCP** — for searching Slack, email, Salesforce, and Gong for account activity
- **Google Workspace MCP** — for Google Drive upload and Gmail draft creation
- **Python 3** with `python-pptx` installed (`pip install python-pptx`)
- **Streamlit Resource Planning app** running at `localhost:8503` — for live hour tracking data
- **Google Drive folder structure** — `SnowWork → Accounts` must exist in user's Drive
- A `generate_status.py` script created for each account (see Step 3 below)
- Snowflake template at: `~/.snowflake/cortex/skills/slide-generator/assets/snowflake_template.pptx`

> **First time?** See the `README.md` in the skill package for full one-time setup instructions.

---

## Workflow

### Step 1: Identify Target Accounts
Ask the user which accounts to generate status reports for. For each account, confirm:
- Account name (used in file names and Drive folder paths)
- Customer primary contact name and email
- Snowflake SA name and email
- Snowflake AE name and email (for CC)
- PSE Project ID (format: `{AccountName}-{SFDCProjectID}`)
- Contracted hours per resource

### Step 2: Gather Account Data (per account)
Use Glean search tools to gather recent activity from the past 2 weeks:

```
1. mcp_glean_search — query: "{AccountName}" app="slack" updated="past_2_weeks"
2. mcp_glean_search — query: "{AccountName} {SA_Name}" updated="past_2_weeks"
3. mcp_glean_search — query: "{AccountName}" app="salescloud" updated="past_month"
4. mcp_glean_search — query: "{AccountName} status update" updated="past_month"
5. mcp_glean_chat — "What is the current status of the {AccountName} Snowflake engagement?"
```

Compile into structured sections:
- **Executive Summary** (2–3 sentences covering engagement purpose and current state)
- **Key Accomplishments/Updates** (5–6 bullets from the past 2 weeks)
- **Next Steps** (4–5 bullets for the coming week)
- **Key Program Milestones** (table: milestone name, RAG status)
- **Hours** (contracted, billed, remaining per resource — from Streamlit app)
- **Overall Status** (Green / Yellow / Red)

### Step 3: Build PowerPoint Deck

Each account needs a `generate_status.py` script in `~/.snowflake/cortex/playground/workspace/Accounts/{AccountName}/WeeklyStatus/`.
Use the `generate_status_template.py` from the skill package as the starting point.

**Key variables to customize at the top of the script:**
```python
ACCOUNT_NAME = "{AccountName}"                         # e.g. "TSI"
OUTPUT = "~/.snowflake/cortex/playground/workspace/Accounts/{AccountName}/WeeklyStatus/{AccountName}_Weekly_Status_{YYYY-MM-DD}.pptx"
STATUS_DATE = "{M/D/YY}"                               # e.g. "4/1/26"
OVERALL_STATUS = "On Track"                            # Green / Yellow / Red

# Hour tracking (from Streamlit Resource Planning app)
SA_NAME = "{SA Full Name}"
SA_ROLE = "Solution Architect"
SA_CONTRACTED = 120
SA_TOTAL_BILLED = 69.0
SA_WEEKLY_DATA = [                                     # list of [week, sched, billed]
    ["02/08/26", 5.0, 5.0],
    ...
]
SDM_NAME = "{SDM Full Name}"
SDM_CONTRACTED = 24
SDM_TOTAL_BILLED = 14.0
SDM_WEEKLY_DATA = [ ... ]

# Slide 1 content (from Glean data gathered in Step 2)
EXEC_SUMMARY = "..."
ACCOMPLISHMENTS = ["...", "..."]
NEXT_STEPS = ["...", "..."]
MILESTONES = [
    ("Phase Name", None, True),        # section header row
    ("Milestone Name", "blue", False), # complete=blue, yellow=in progress, gray=not started
]

# Email
EMAIL_TO = "{customer.email@company.com}"
EMAIL_CC = "{sa.name@snowflake.com}, {ae.name@snowflake.com}"
EMAIL_SUBJECT = "Snowflake <> {AccountName} - Weekly Status Update - {date}"
EMAIL_BODY = """..."""
```

Run the script:
```bash
python3 ~/.snowflake/cortex/playground/workspace/Accounts/{AccountName}/WeeklyStatus/generate_status.py
```

**Slide 1: Program Status Overview**
- Header bar with status date and account name
- Top-right summary box: Architect hours, hours remaining, overall status dot
- Phase timeline chevron bar with current phase marker
- Left column: Executive Summary, Key Accomplishments, Next Steps (Snowflake dk2 header bars)
- Right column: Key Milestones table (Complete=blue, In Progress=yellow/orange, Not Started=gray)
- Bottom: legend bar

**Slide 2: Hour Tracking**
- Title: "Hour Tracking"
- Side-by-side tables per team member (SA on right, SDM/PM on left)
- Columns: Week | Scheduled | Billed | Variance
- TOTAL row (bold, teal bg), future weeks (light blue bg)
- Data from `localhost:8503/Resource_Planning`

Template path: `~/.snowflake/cortex/skills/slide-generator/assets/snowflake_template.pptx`
Layout: 12 (blank) for all custom shapes

**STOPPING POINT** — After generating the PPTX, ask the user to review it before continuing.

### Step 4: Capture Live Hours Data
1. Navigate to `http://localhost:8503/Resource_Planning`
2. Click **Refresh Data**
3. Set Engagement Status = **Active**, find the account
4. Expand the project expander
5. Read current week numbers: Scheduled, Billed, Variance per resource
6. Update the TOTAL row in the `generate_status.py` and re-run if numbers differ

### Step 5: Upload PPTX → Google Slides in Drive

**CRITICAL:** Always use the upload-then-convert approach. Do NOT use `mcp_google-worksp_create_presentation` (markdown rendering does not preserve Snowflake branding).

#### 5a: Resolve or create target Drive folder

Search for existing folder:
```
mcp_google-worksp_search_drive — query: "{AccountName} Weekly Status"
```

If the folder doesn't exist, create it:
```
# 1. Create account folder under SnowWork/Accounts
mcp_google-worksp_create_drive_folder
  name: "{AccountName}"
  parent_id: "1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck"   ← SnowWork/Accounts root

# 2. Create Weekly Status subfolder
mcp_google-worksp_create_drive_folder
  name: "Weekly Status"
  parent_id: {account_folder_id from step above}
```

#### 5b: Upload and convert to Google Slides

```bash
MCP=~/.snowflake/cortex/.mcp-servers/google-workspace
cd $MCP && ./node ~/CoCo/Scripts/upload_to_gslides.mjs \
  "~/.snowflake/cortex/playground/workspace/Accounts/{AccountName}/WeeklyStatus/{filename}.pptx" \
  "{AccountName} - Weekly Status - {YYYY-MM-DD}" \
  {weekly_status_folder_id}
```

Script returns JSON: `{"id":"...","name":"...","url":"https://docs.google.com/presentation/d/.../edit"}`
Save the `url` for Step 6.

**Naming convention:** `{AccountName} - Weekly Status - {YYYY-MM-DD}`

### Step 6: Create Gmail Draft

Use `mcp_google-worksp_create_draft`:

```
to:      {customer primary contact email}
cc:      {SA email}, {AE email}
subject: Snowflake <> {AccountName} - Weekly Status Update - {M/D/YY}
body:    (template below)
```

**Email body template:**
```
Hi {CustomerFirstName},

Hope your week is going well. Please find this week's status update linked below.

View Status Deck: {Google Slides URL}

Highlights this week:
    • {key accomplishment 1}
    • {key accomplishment 2}
    • {key accomplishment 3}

Focused next steps:
    • {next step 1}
    • {next step 2}
    • {next step 3}

Hours Summary: {billed} of {contracted} Architect hours consumed | {remaining} remaining

Please let us know if you have any questions or if there is anything you would like to discuss before our next session.

Best regards,
{Your Name}
{Your Title}, Snowflake Professional Services
```

**Bullet formatting rule:** All bullet lists in the email body MUST use 4-space indented format (`    • item`). Never flush-left (`• item`).

---

## Google Drive Output

All outputs go to: **SnowWork → Accounts → {AccountName} → Weekly Status**

**Known Drive folder IDs (pre-created):**
| Folder | ID |
|---|---|
| SnowWork (root) | `1ph8vYMtrfCSB6ECIFZN0S5StHakjuNmu` |
| SnowWork/Accounts | `1Yk76x9n8uyghuBrwt_gPehVG7TH6RNck` |
| SnowWork/Internal | `1x6uOOcSTerODqM_tTdoyD9T8SV3vR4kf` |

New accounts: create `{AccountName}` under `SnowWork/Accounts`, then `Weekly Status` under that.

---

## Output Summary

For each account, the following are created:
- **Local PPTX:** `~/.snowflake/cortex/playground/workspace/Accounts/{AccountName}/WeeklyStatus/{AccountName}_Weekly_Status_{YYYY-MM-DD}.pptx`
- **Google Slides:** Native presentation in `SnowWork/Accounts/{AccountName}/Weekly Status/`
- **Gmail Draft:** Ready-to-send draft in Gmail Drafts (includes Google Slides link)

---

## Theme Colors Reference (Snowflake Template)
| Name | Hex | Use |
|---|---|---|
| dk2 | `#11567F` | Headers, titles |
| accent1 | `#29B5E8` | Highlights, complete |
| accent4 | `#FF9F36` | In Progress, at risk |
| Green | `#4CAF50` | On Track status |
| Yellow | `#FFC107` | At Risk status |
| Red | `#F44336` | Off Track status |
| Gray | `#BDBDBD` | Not Started |
