# Scope Document Template

## T&M with Deliverables

```markdown
# [Customer Name] - Professional Services Scope of Work

## Executive summary
[2-3 sentences: what the engagement accomplishes]

## Customer information
- **Customer Name**: [Name]
- **Industry**: [Industry]
- **Duration**: [X weeks]
- **Engagement Type**: [Advisory/Build/Co-Build]
- **Commercial Model**: [T&M / Fixed Price]

## Customer context (Snowhouse)

**Organization:** [Org ID from query]
**Active accounts:** [Count] across [deployments]
**Primary edition:** [Business Critical/Enterprise/Standard]
**Tenure:** ~[X] years (customer since [YYYY-MM-DD from query 1.3.1])

### Top 5 accounts by credit usage (30-day)

| Account | Deployment | Edition | Credits (30d) |
|---------|------------|---------|---------------|
| [Locator] | [deployment] | [edition] | [credits] |

### Feature adoption

- **Snowpipe:** [Active (X pipes, Y bytes/90d) / Not used]
- **Tasks:** [X tasks, Y runs/90d / Not used]
- **Streams:** [Active / Not used]
- **Serverless features:** [List or "None detected"]

### Consumption notes

[Any spikes, trends, or anomalies observed. Or "Stable consumption pattern."]

---

## Outcomes and success criteria

**Engagement outcomes:**
- [What Snowflake will deliver - tangible output]
- [What Snowflake will deliver - tangible output]
- [What Snowflake will deliver - tangible output]

**Success criteria:**
- [How we measure success - specific, measurable]
- [How we measure success - specific, measurable]
- [How we measure success - specific, measurable]

## Scope

[Detailed description of what is in scope]

## Effort summary

| Phase | Activities | SA | SDM | Total |
|-------|------------|---:|----:|------:|
| Kickoff & Discovery | Setup communication channels and confirm access requirements<br>Review existing architecture and identify integration points<br>Conduct kickoff meeting to align on goals and success criteria | X | X | X |
| [Phase 2] | [Verb] [specific activity]<br>[Verb] [specific activity]<br>[Verb] [specific activity] | X | X | X |
| [Phase N] | [Verb] [specific activity]<br>[Verb] [specific activity] | X | X | X |
| **Total** | | **X** | **X** | **X** |

**Activity format rules:**
- Use `<br>` for line breaks within the Activities cell
- Each activity starts with an action verb (Setup, Review, Conduct, Evaluate, Configure, Build, Define, Implement, Create, Advise, Guide, Document)
- Be specific about what is being done (not "Design architecture" but "Design Snowpipe architecture for multi-database ingestion")
- Include scope indicators where relevant (e.g., "up to 15 objects", "3 sessions")

## Deliverables

| # | Deliverable | Description | Complexity |
|---|-------------|-------------|------------|
| 1 | [Name] | [Description] | L/M/H |

## Phase breakdown

### Phase 1: Kickoff & Onboarding ([X] hours)

| Activity | SA | SDM |
|----------|---:|----:|
| [Activity - verb first] | X | X |

**Deliverables:**
- [Deliverable 1]

### Phase 2: Discovery & Planning ([X] hours)
[Repeat structure]

### Phase 3: Design ([X] hours)
[Repeat structure]

### Phase 4: Implementation ([X] hours)
[Repeat structure]

### Phase 5: Testing ([X] hours)
[Repeat structure]

### Phase 6: UAT & Deployment ([X] hours)
[Repeat structure]

### Phase 7: Documentation & Knowledge Transfer ([X] hours)
[Repeat structure]

## Total effort summary

| Role | Hours |
|------|------:|
| Solution Architect (SA) | X |
| Solution Consultant (SC) | X |
| Service Delivery Manager (SDM) | X |
| **Total** | **X** |

## Projected consumption impact

### Current baseline

| Metric | Value |
|--------|-------|
| Current monthly credits | ~X,XXX |
| Active warehouses | XX |
| Top warehouse | [NAME] (XXX credits/30d) |

### Expected consumption increase

This engagement will add **X-Y credits/month** to [Customer]'s consumption (~X-Y% increase over current baseline).

| Impact Type | Low Estimate | High Estimate |
|-------------|--------------|---------------|
| New monthly credits | +X | +Y |
| Percentage increase | +X% | +Y% |
| New storage | +X TB | +Y TB |
| Storage cost increase | +$X/mo | +$Y/mo |

### Detailed breakdown

#### Initial [load/development/migration] (one-time)

| Component | Estimate | Calculation |
|-----------|----------|-------------|
| [Component 1] | X credits | [Formula] |
| [Component 2] | X credits | [Formula] |
| **Total Initial** | **X credits** | |

#### Ongoing monthly (NEW consumption)

| Component | Low | High | Notes |
|-----------|-----|------|-------|
| [Component 1] | X | Y | [Notes] |
| [Component 2] | X | Y | [Notes] |
| Storage | X TB | Y TB | [Compression assumption] |
| Storage Cost | $X/mo | $Y/mo | [$23-40/TB by edition] |
| **Monthly Credits** | **X** | **Y** | Excluding storage |

### Assumptions

- [Key assumption 1]
- [Key assumption 2]

*Estimates will be refined during the engagement based on actual data characteristics.*

## Resource skills required

| Skill Area | SA | SC | Required |
|------------|:--:|:--:|:--------:|
| Data Engineering | Y | Y | Yes |
| Snowpark Python | | Y | No |
| Cortex AI | Y | Y | No |

## Assumptions
1. [Assumption 1]
2. [Assumption 2]

## Risks and dependencies

| Phase | Risk | Impact | Probability | Mitigation |
|-------|------|--------|-------------|------------|
| [Phase name] | [Risk description] | H/M/L | H/M/L | [Strategy] |
| All | [Risk that spans phases] | H/M/L | H/M/L | [Strategy] |

## Out of scope
- [Item 1]
- [Item 2]

## RACI matrix

| Phase | Accountable | Responsible | Consulted | Informed |
|-------|-------------|-------------|-----------|----------|
| Discovery | Customer | Snowflake | Customer | Snowflake |
| Design | Snowflake | Snowflake | Customer | Customer |
| Implementation | Snowflake | Snowflake | Customer | Customer |
| UAT | Customer | Customer | Snowflake | Snowflake |
| Deployment | Customer | Customer | Snowflake | Snowflake |

**RACI rules:**
- Each cell must have exactly ONE party (Snowflake or Customer)
- Never use "Both", "Joint", or combined entries
- A = Accountable (owns the outcome), R = Responsible (does the work), C = Consulted (provides input), I = Informed (kept updated)

## Key contacts

| Role | Name | Organization |
|------|------|--------------|
| Account Lead | [Name] | Snowflake |
| Customer Contact | [Name] | [Customer] |

## Sign-off
- **Prepared By**: [Name]
- **Title**: [Title]
- **Date**: [Date]
```

---

## RSA Template

```markdown
# [Customer Name] - Resident Services Agreement

## Engagement overview
[Summary of flexible engagement model]

**Duration:** [X months]
**Hours:** [X hours per month / X total hours]
**Focus Areas:** [List primary areas]

## Work categories

### [Category 1]
- [Activity - verb first]
- [Activity - verb first]

### [Category 2]
- [Activity - verb first]

## Governance
- [Check-in cadence]
- [Hour tracking approach]
- [Scope adjustment process]

## Assumptions
1. [Assumption 1]
2. [Assumption 2]

## Out of scope
- [Item 1]
- [Item 2]
```
