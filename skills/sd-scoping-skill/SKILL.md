---
name: snowflake-sd-scoping
description: "Scope Service Delivery Engagements - Produce deliverables list, SA/SDM hour estimates, project plan, assumptions, and risks for professional services proposals. Use when: scoping new PS engagements, estimating consulting effort, creating SOW documents, planning discovery sessions, or preparing project kickoff materials. Triggers: scope engagement, estimate hours, SOW, proposal, engagement planning, PS scoping."
author: Vikas Malik
version: 1.2.0
date: 2026-02-11
---

# Snowflake Service Delivery Scoping

## Overview
This skill helps scope Service Delivery Engagements based on customer requirements.

## Purpose
Generate comprehensive , scalable enagagement scope with:
- Effort estimate by phase & resource type 
- Milestone definations 
- Risk , dependency , assumptions , scope  & out of scope statements 
- Modular , resuable components for consistency & scale. 

## When to Use this Skill
- Scoping new Snowflake implementation engagements 
- Estimating efforts for Snowflake implementation engagements
- Creating Scope & SOW statements 

## Prerequisites
- Objective/Goal of the engagement
- Type of engagement (Advisory, Build, or Co-Build)
- Timeline expectations (8 weeks, 12 weeks, etc.)
- Any existing requirements documentation or SOW drafts

## Engagement Type Modifiers

| Type | Description 
|------|-------------
| Advisory T&M | Time & materials guidance 
| Advisory Outcome | Fixed outcome advisory 
| Build | Snowflake delivers solution 
| Co-Build | Joint development with customer 
| Migration | Data/workload migration 


## Phase Duration Guidelines

| Phase | 8 Weeks | 12 Weeks | 16 Weeks |
|-------|---------|----------|----------|
| Kickoff & Onboarding | 1 wk | 1 wk | 1 wk |
| Discovery & Planning | 1 wk | 2 wk | 2 wk |
| Design | 1 wk | 2 wk | 3 wk |
| Implementation | 3 wk | 4 wk | 6 wk |
| Testing | 1 wk | 2 wk | 2 wk |
| UAT & Deployment | 1 wk | 1 wk | 2 wk |

## Workflow

### Step 0: Load References (MANDATORY)

**STOP. Read reference files before proceeding.**

| File | Purpose |
|------|---------|
| `references/snowhouse-queries.md` | SQL for customer consumption data - MUST run |
| `references/baseline-hours.md` | Hour estimates per deliverable type |
| `references/complexity-factors.md` | Multipliers (scale, novelty, maturity) |
| `references/consumption-estimates.md` | Credit/storage projection templates |
| `references/scope-template.md` | Required output format |
| `references/self-evaluation.md` | Quality checklist before completion |

For module-specific patterns, also read from `scoping_modules/` based on selected module.

**STOP**: Confirm reference files loaded before proceeding to Step 1.

---

### Step 1: Gather Engagement Context

#### 1.1 Customer Identification (ALWAYS ASK FIRST)
👉 **CRITICAL: Start with customer identification before any other questions.**

Use `ask_user_question` tool to collect ONE of:

| # | Field | Format | Required |
|---|-------|--------|----------|
| 1 | **Salesforce Account ID** | Text (18-char ID, e.g., 001XXXXXXXXXXXX) | Yes (or Customer Name) |
| 2 | **Customer Name** | Text (company name) | Yes (or SF Account ID) |

#### 1.2 Customer Lookup & Confirmation
👉 **Search Glean/Raven MCP to retrieve customer details.**

Using the provided Account ID or Customer Name:
1. Search **Glean MCP** (`mcp_glean_search`) for customer information
2. Query **Raven MCP** for Salesforce account details if available

Present retrieved customer information to user:
```
Customer Information Found:
- Account Name: [Name]
- Salesforce Account ID: [ID]
- Industry: [Industry]
- Region: [Region]
- Account Owner: [AE Name]
- Sales Engineer: [SE Name]
- Contract Value: [Value]
- Contract End Date: [Date]
```

Use `ask_user_question` to confirm:

| # | Field | Options | Required |
|---|-------|---------|----------|
| 3 | **Confirm Customer Info** | "Yes, this is correct" / "No, let me provide correct details" | Yes |

**If user selects "No"**, ask for override:

| # | Field | Format | Required |
|---|-------|--------|----------|
| 4 | **Customer Name** | Text | Yes |
| 5 | **Industry** | Text | No |
| 6 | **Region** | Text | No |

#### 1.2.1 Run Snowhouse Consumption Queries (MANDATORY)

👉 **After customer confirmed, run Snowhouse queries for consumption baseline.**

Execute queries from `references/snowhouse-queries.md`:
1. Find customer accounts
2. Get top 5 accounts by credits (30-day)
3. Get total baseline consumption

**If no data returned** (new customer): Note "No baseline consumption - new customer" for scope doc.

**STOP**: Confirm Snowhouse data captured before proceeding.

#### 1.3 Use Case Selection (ASK AFTER CUSTOMER CONFIRMED)
**Pull existing use cases from Glean/Raven MCP for user selection.**

1. Search **Glean MCP** for use cases associated with the customer account
2. Query **Raven MCP** for Salesforce use cases if available
3. Present use cases as selectable options

Use `ask_user_question` with retrieved use cases:

| # | Field | Options | Required |
|---|-------|---------|----------|
| 7 | **Select Use Case** | [List of existing use cases from search] + option to enter new | Yes |
| 8 | **New Use Case Name** | Text (if "Enter new use case" selected) | Conditional |

Example use case options format:
- "Apollo Decomm Phase 1 - $950K ACV"
- "MySQL Migration - PoC"
- "Redshift Migration"
- "AI/ML Pilots"

#### 1.4 Opportunity ID (ASK AFTER USE CASE)
Use `ask_user_question` to collect:

| # | Field | Format | Required |
|---|-------|--------|----------|
| 9 | **Salesforce Opportunity ID** | Text (18-char ID, e.g., 006XXXXXXXXXXXX) or Type NA | No |

If Opportunity ID provided, use **Raven MCP** to pull:
- Opportunity name, stage, value
- Close date, forecast status
- Associated products/services

#### 1.5 Requirements & Meeting Notes (ASK FIFTH)
👉 **Ask after customer and use case are confirmed. Skip to next step if user provides no input.**
⚠️ **If user does not provide Doc URL or File Path then its Mandatory to ask for Describe Requirement**

Use `ask_user_question` tool to collect:

| # | Field | Format | Required |
|---|-------|--------|----------|
| 10 | **GDrive Folder/Doc URL** | URL (e.g., https://drive.google.com/...) | Yes |
| 11 | **Local File Path** | Absolute path to requirements/notes file or name of file in current folder. If none then type none or NA| Yes |
| 12 | **Describe Requirement** | Text | Yes if URL or folder or file not provided |

If URL/path provided:
- Use **Glean MCP** to search and retrieve relevant documents
- Read local files directly if path provided
- Extract key requirements, goals, and meeting notes

**Fallback**: If no documents available, ask user to describe requirements verbally in next section.

#### 1.6 Engagement Details (ASK SIXTH - if not captured from Salesforce/docs)
Use `ask_user_question` tool to collect these inputs:

| # | Field | Options/Format | Required |
|---|-------|----------------|----------|
| 13 | **Customer Name** | Text input | Yes (if not from SF) |
| 14 | **Engagement Type** | Advisory T&M / Advisory Outcome / Build / Co-Build | Yes |
| 15 | **Timeline** | 8 weeks / 12 weeks / 16 weeks / Custom | Yes |
| 16 | **Primary Module** | Pull module list from scoping_modules/* file | Yes |

#### 1.7 Additional Context (Should Have)
| # | Field | Options/Format | Required |
|---|-------|----------------|----------|
| 17 | **Customer Snowflake Maturity** | None (new) / Beginner / Intermediate / Advanced | Yes | 
| 18 | **Industry** | Text input (for risk/assumption context) | No | 
| 19 | **Commercial Model** | Fixed Price / T&M |  Yes | 
| 20 | **Success Criteria** | Customer-defined metrics | Yes | 

#### 1.8 Module Selection
Select one or more applicable modules:Pull module list from scoping_modules/* file 

Below is list of example

| Module | Description | Key Deliverables |
|--------|-------------|------------------|
| Account Setup & RBAC | Org strategy, SSO, role design, policies | Roles, policies, IdP integration |
| Data Engineering | Ingestion, transformation, pipelines | Tables, views, procs, tasks |
| BC/DR | Business continuity, disaster recovery | Replication, failover config |
| Cortex AI | Search, Analyst, Agents, Intelligence | Search services, semantic models |
| Dashboard/Analytics | Streamlit, BI connectivity | Streamlit pages, dashboards |
| Machine Learning | Feature engineering, model deployment | Models, notebooks, UDFs |
| Native Apps | Marketplace app development | App versions, procedures |
| Migration | Platform/workload migration | Conversion scripts, validation |

#### 1.9 Conditional Questions

**Always confirm below for Co-Build:**
- Which phases will customer or Partner own?
- What % of development work will customer or Partner  do?

**If Migration:**
- Source platform (Oracle/Teradata/SQL Server/Other)?
- Estimated data volume?
- Number of objects to migrate?

**If Cortex AI:**
- Are preview features acceptable?
- Number of personas/use cases?

#### 1.10 Confirm Understanding
👉 Before proceeding to Step 2, summarize gathered context and confirm with user:

```
Engagement Summary:
- Customer: [Name]
- Type: [Engagement Type]
- Duration: [X weeks]
- Modules: [List]
- Maturity: [Level]
- Key Requirements: [Summary]

Please confirm this is accurate before I proceed with scoping.
```

**STOP**: Do not proceed until user confirms engagement summary.

### Step 2: Analyze Requirements & Engagement Context

#### 2.1 Scope Dimensions (Complexity Drivers)
- Use scoping_modules.md  to understand complexity driver based on module choosen 

#### 2.2 Delivery & Support Model
- Testing Involvement : None/ UAT Support / Full QA Ownership
- Performance optimization : Not Required / Basic tuning / Advance Optimization
- Customer enablement : None / Basic training / Enablement Program 
- Warranty Support : None / 1-2 weeks hand holding / Dedicated support 

After gathering inputs, identify:
- Types of deliverables needed
- Complexity level (Low/Medium/High)
- Dependencies and prerequisites
- Technical challenges
- Applicable Snowflake features (standard vs preview)

### Step 3: Estimate Deliverables
- Use scoping_modules.md  to understand key deliverables for each module 


### Step 4: Calculate Effort in Hours

⚠️ **Don't estimate hours for SI Partners & Customer. Just provide list of activities where SI Partners & Customer are responsible**

- Use scoping_modules.md  to under key components , complexity factor and associated effort 
- Use Resource_Profiles.md for resource type allocation

1. Sum baseline hours for all objects
2. Apply complexity multiplier
3. Apply engagement type allocation (SA vs SC split)
4. Calculate SDM hours (minimum 20% of total)
5. Add phase-specific overhead (kickoff, design reviews, KT)

Use `references/complexity-factors.md` for multipliers (scale, novelty, maturity).

**STOP**: Present effort breakdown for user approval before generating scope doc.

### Step 5: Document Outcomes

Create bulleted list of engagement outcomes:

**Examples:**
```
1. Enable data engineering team with SQL Best Practices
2. Machine Learning Model for Churn Prediction
3. Data Pipeline for Gold Layer
4. Cortex Analyst service for 2 personas
```

### Step 6: Verify Author Information

👉 **Before generating the scope document, confirm the author's name and title.**

⚠️ **Do NOT infer name from the Snowflake username or title from the Snowflake role.** These are often inaccurate (e.g., username `JBRODY` does not reliably map to a full name, and role `TECHNICAL_ACCOUNT_MANAGER` is not a job title).

Use `ask_user_question` to collect:

| # | Field | Format | Required |
|---|-------|--------|----------|
| 21 | **Prepared By (Name)** | Text | Yes |
| 22 | **Title** | Text | Yes |

These values will populate the **Sign-off** section of the scope document.

**STOP**: Confirm name and title before generating scope document.

### Step 7: Generate Scope Document

Create markdown document using template from `references/scope-template.md`.

**Key sections required:**
- Executive Summary
- Customer Information & Context (with Snowhouse data)
- Outcomes & Success Criteria
- Deliverables table with complexity
- Phase Breakdown with hours
- Total Effort Summary
- **Projected Consumption Impact** (baseline + incremental)
- Assumptions, Risks, Out of Scope
- RACI Matrix

### Step 8: Self-Evaluate Before Completion

**Run `humanizer` skill** on scope document to remove AI writing patterns.

Review scope document against `references/self-evaluation.md` checklist:

| Check | Pass? |
|-------|-------|
| All reference files read? | |
| Snowhouse queries executed? | |
| Customer context populated with real data? | |
| Effort multipliers applied correctly? | |
| Consumption impact section included? | |
| Activities start with verbs? | |

**Report confidence score (1-5) before declaring complete.**

**STOP**: Final review with user before delivering scope document.

---

## Output

- Markdown scope document containing: executive summary, customer context (with Snowhouse consumption data), outcomes & success criteria, deliverables table with complexity ratings, phase breakdown with SA/SDM hours, projected consumption impact, assumptions, risks, out-of-scope items, and RACI matrix
- Effort estimates broken down by phase, resource type (SA vs SDM), and complexity multiplier
- Confidence score (1-5) from self-evaluation checklist

---

## Migration Engagements

For migration-specific phases, baseline hours, complexity factors, and risks, see `references/migration.md`.

---

## Ground Rules

1. ⚠️ **Don't assume** - Ask clarifying questions before proceeding
2. 👉 **Include buffer** - Add 10-15% contingency for unknowns
3. ⚠️ **SDM minimum 20%** - Never go below 20% SDM allocation
4. 👉 **Preview features** - Add 25% buffer for new/preview Snowflake features
5. 👉 **Phase order** - Always present estimates by project phase
6. 👉 **Object counts** - Bound scope with explicit object counts

## Limitations

⚠️ Keep these limitations in mind:
- Estimates based on standard engagement patterns; actual effort varies
- Does not include pricing or commercial terms
- Assumes standard Snowflake architecture
- Highly customized deployments may require additional scoping

## Troubleshooting

- **Unclear requirements**: Request discovery call summary or documentation
- **Aggressive timeline**: Highlight phases needing more time; provide alternatives
- **Scope creep detected**: Document out-of-scope items explicitly
- **Resource mismatch**: Recommend appropriate SKU (SA vs SC vs MSA/MSC)


## ⚠️ Do NOT

- ⚠️ Don't calculate amount. Only present estimate in hours 
- ⚠️ Don't estimate hours for Partners or customer unless asked to do so
- ⚠️ Make assumptions about Snowflake concepts - always verify with docs
- ⚠️ Make assumptions about Project Phases 

## 👉 Always DO

- 👉 Check memory at start of every conversation
- 👉 Update memory with progress and findings
- 👉 Use `system_instructions` for Snowflake products (RBAC, dbt, Streamlit, Cortex)
- 👉 Use `snowflake_product_docs` to understand Snowflake feature and ask relevant questions
- 👉 Provide file paths and links to created artifacts
- 👉 Always follow instructions and steps outlined in this doc 
