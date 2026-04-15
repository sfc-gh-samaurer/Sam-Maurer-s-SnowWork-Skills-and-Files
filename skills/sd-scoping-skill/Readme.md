# Snowflake Service Delivery Scoping Skill

A Cortex Code skill for scoping Snowflake professional services engagements.

## Overview

This skill helps Solution Architects and Service Delivery Managers generate comprehensive engagement scope documents with effort estimates, deliverables, risks, and assumptions based on customer requirements.

## Features

- **Guided Scoping Workflow** - Interactive questions to gather engagement context
- **Snowhouse Integration** - Automatic customer consumption baseline queries
- **Modular Estimation** - Pre-built modules for common engagement types (RBAC, Data Engineering, BC/DR, etc.)
- **Role-Based Hours** - Estimates split by SA, SC, SDM with allocation patterns
- **Complexity Multipliers** - Adjustments based on scale, novelty, and maturity
- **Consumption Impact** - Projects incremental credit/storage increase
- **Self-Evaluation** - Quality checklist before completion
- **Standardized Output** - Consistent markdown scope statements

## Installation

### Step 1: Clone the repository

```bash
git clone git@github.com:snowflake-solutions/cortex-code-skills.git
cd cortex-code-skills
```

### Step 2: Install the skill

**Option A: Symlink (recommended for development)**

```bash
ln -s "$(pwd)/skills/sd-scoping-skill" ~/.snowflake/cortex/skills/sd-scoping-skill
```

**Option B: Copy to local skills**

```bash
cp -r skills/sd-scoping-skill ~/.snowflake/cortex/skills/
```

## Quick Start

```
Help me scope a Data Engineering engagement for Acme Corp
```

Or provide a requirements file:
```
@Requirements.md - Help me scope this engagement
```

## File Structure

```
sd-scoping-skill/
├── SKILL.md                      # Main skill definition & workflow
├── Readme.md                     # This file
├── skill_evidence.yaml           # Team validation tracking
│
├── scoping_modules/              # Module-specific scoping guidance
│   ├── scoping_modules.md        # Module index and overview
│   ├── account-setup.md          # Account setup & configuration
│   ├── aiml.md                   # AI/ML implementations
│   ├── bcdr.md                   # Business continuity & disaster recovery
│   ├── data-engineering.md       # Data pipelines & transformations
│   ├── migration.md              # Platform migrations
│   ├── native-apps.md            # Native app development
│   └── optimization.md           # Performance optimization
│
└── references/                   # Supporting reference documents
    ├── snowhouse-queries.md      # Customer consumption queries (MANDATORY)
    ├── baseline-hours.md         # Hour estimates per deliverable type
    ├── complexity-factors.md     # Scale, novelty, maturity multipliers
    ├── consumption-estimates.md  # Credit/storage projection templates
    ├── scope-template.md         # Output format template
    ├── self-evaluation.md        # Quality checklist
    ├── migration.md              # Migration-specific guidance
    ├── discovery-questions.md    # Discovery questions by module
    ├── architectural-decisions.md # Technical decision documentation
    └── Resource_Profiles.md      # Resource SKUs & allocation patterns
```

## Workflow

```
Step 0: Load References (MANDATORY)
    ↓
Step 1: Gather Engagement Context
    → 1.2.1: Run Snowhouse Queries (MANDATORY)
    ↓
Step 2: Analyze Requirements
    ↓
Step 3: Estimate Deliverables
    ↓
Step 4: Calculate Effort
    ↓
Step 5: Document Outcomes
    ↓
Step 6: Generate Scope Document
    ↓
Step 7: Self-Evaluate Before Completion
```

**Key checkpoints (STOP points):**
- After Step 0: Confirm references loaded
- After Step 1.2.1: Confirm Snowhouse data captured
- After Step 1.10: Confirm engagement summary
- After Step 4: Approve effort breakdown
- After Step 7: Final review

## Supported Modules

| Module | Description |
|--------|-------------|
| Account Setup & RBAC | Org strategy, SSO, role design, security policies |
| Data Engineering | Ingestion, transformation, data modeling, pipelines |
| BC/DR | Business continuity, disaster recovery, replication |
| Cortex AI | Search, Analyst, Agents, Snowflake Intelligence |
| Dashboard/Analytics | Streamlit, BI connectivity |
| Machine Learning | Feature engineering, model deployment |
| Native Apps | App architecture, marketplace, multi-tenant |
| Migration | Schema conversion, data migration, validation |

## Engagement Types

| Type | Description | SA Allocation | SC Allocation |
|------|-------------|---------------|---------------|
| Advisory T&M | Time & materials guidance | 60-80% | 0% |
| Advisory Outcome | Fixed outcome advisory | 60-80% | 0% |
| Build | Snowflake delivers solution | 15-30% | 70-85% |
| Co-Build | Joint development with customer | 25-40% | 60-75% |
| Migration | Data/workload migration | Varies | Varies |

## Output Format

The skill generates a scope statement with:
- Executive Summary
- Customer Information & Context (with Snowhouse data)
- Outcomes & Success Criteria
- Deliverables Table with Complexity
- Phase Breakdown with Hours
- Total Effort Summary
- **Projected Consumption Impact** (baseline + incremental)
- Resource Skills Required
- Assumptions
- Risks & Dependencies
- Out of Scope
- RACI Matrix

## Required Inputs

| Input | Required |
|-------|----------|
| Customer Name or SF Account ID | Yes |
| Engagement Type | Yes |
| Timeline (8/12/16 weeks) | Yes |
| Primary Module | Yes |
| Customer Snowflake Maturity | Yes |
| Requirements (file or description) | Yes |

## Limitations

- Estimates based on standard patterns; actual effort varies
- Does not include pricing or commercial terms
- Assumes standard Snowflake architecture
- Highly customized deployments may require additional scoping

## Contributing

To add new modules:
1. Create new module file in `scoping_modules/` directory
2. Add module definition with: Focus Areas, Key Objects, Risk Areas, Complexity Drivers, Phases, Effort Baseline
3. Add discovery questions to `references/discovery-questions.md`
4. Update `scoping_modules/scoping_modules.md` index
5. Test with a sample project

## Authors

- **Vikas Malik** - Original skill
- **dbergey** - Snowhouse integration, consumption impact, self-evaluation

Version: 1.2.0  
Date: 2026-02-11

---

## Backlog / Future Enhancements

### Google Drive Export (Not Yet Implemented)

**Goal**: Optionally sync generated scope documents to a Google Drive folder.

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| 1. Manual CLI | Use `gdrive` CLI after generation | Simple, no code changes | Manual step |
| 2. Skill Step 8 | Add optional export step using Python Google Drive API | Integrated workflow | Requires OAuth setup, credentials management |
| 3. MCP Integration | Use Google Drive MCP (if available) | Consistent with Glean/Raven pattern | Depends on MCP availability |

**Recommended path**:
1. Start with Option 1 (manual `gdrive` CLI) to validate workflow
2. If frequently used, implement Option 2 as Step 8 in SKILL.md
3. Consider Option 3 if Google Drive MCP becomes available

**Prerequisites for implementation**:
- `gdrive` CLI: `brew install gdrive` + one-time OAuth
- Python API: `credentials.json` from Google Cloud Console
- MCP: MCP server with Drive access configured

### Estimate Refinement via Project Outcomes (Not Yet Implemented)

**Goal**: Use actual project outcomes to continuously improve estimation accuracy.

**Concept**: After an engagement completes, the SA on the ground writes a retrospective document capturing:
- Actual hours by role vs. estimated
- Scope changes and reasons
- Unexpected complexity factors
- Lessons learned

This feedback could be used to:

| Enhancement | Description |
|-------------|-------------|
| **Calibrate baseline hours** | Compare estimates to actuals, adjust `baseline-hours.md` |
| **Refine complexity multipliers** | Identify which factors consistently under/over-estimate |
| **Build pattern library** | Catalog successful patterns by engagement type |
| **Train estimation model** | Feed outcomes into ML model for better predictions |

**Implementation approach**:
1. Define standard retrospective template (markdown)
2. Create `references/outcomes/` folder to store anonymized project outcomes
3. Add Step 0.5: "Check similar past engagements" before estimating
4. Periodically review outcomes to update baseline hours and multipliers

**Data needed per project**:
- Engagement type, modules, timeline
- Estimated vs. actual hours (by role)
- Key variance drivers
- Customer maturity assessment accuracy
