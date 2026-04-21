---
name: opportunity_meddpicc_quality
description: Interactive MEDDPICC scoring coach for opportunities. Shows current scores, explains what's missing on weak elements, and lets the user simulate updated text to see how scores would change. Triggers - meddpicc score, meddpicc coach, improve meddpicc, meddpicc feedback, score my opp, meddpicc help, what's missing in meddpicc, how to improve meddpicc, meddpicc simulation, meddpicc what-if, MEDDPICC.
created_date: 2026-03-03
last_updated: 2026-03-13
owner_name: Alexis Charolais
version: 1.1.0
---

Before showing any output, follow these instructions exactly.

# opportunity_meddpicc_quality

Interactive coaching skill that helps AEs and managers understand and improve MEDDPICC scores on their opportunities. Three-step flow: review current scores, get coaching on weak elements, simulate improvements.

## Snowflake Connection

Always use connection `snowhouse` by default. If not available, ask the user for the name of their connection.

## Data Sources

| Table | Purpose |
|-------|---------|
| `SALES.RAVEN.SDA_OPPORTUNITY_VIEW` | Opportunity data with MEDDPICC text fields and LLM scores |
| `SALES.RAVEN.MEDDPICC_PROMPT_LIBRARY_VIEW` | LLM scoring prompts (managed in datascience-airflow, read-only) |

## MEDDPICC Elements

The 8 MEDDPICC elements and their column mappings in `SDA_OPPORTUNITY_VIEW`:

| Element | Text Column | Score Column |
|---------|-------------|--------------|
| Metrics (M) | `MEDDPICC_METRICS` | `MEDDPICC_METRICS_SCORE` |
| Economic Buyer (E) | `MEDDPICC_ECONOMIC_BUYER` | `MEDDPICC_ECONOMIC_BUYER_SCORE` |
| Decision Criteria (DC) | `MEDDPICC_DECISION_CRITERIA` | `MEDDPICC_DECISION_CRITERIA_SCORE` |
| Decision Process (DP) | `MEDDPICC_DECISION_PROCESS` | `MEDDPICC_DECISION_PROCESS_SCORE` |
| Paper Process (PP) | `MEDDPICC_PAPER_PROCESS` | `MEDDPICC_PAPER_PROCESS_SCORE` |
| Identified Pain (IP) | `MEDDPICC_IDENTIFY_PAIN` | `MEDDPICC_IDENTIFIED_PAIN_SCORE` |
| Champion (CH) | `MEDDPICC_CHAMPION` | `MEDDPICC_CHAMPION_SCORE` |
| Competition (CO) | `MEDDPICC_PRIMARY_COMPETITOR` | `MEDDPICC_COMPETITION_SCORE` |

## Workflow

### Step 0: Identify the Opportunity

If the user hasn't specified an opportunity, use the `ask_user_question` tool to prompt them:

```json
{
  "questions": [{
    "header": "Opportunity",
    "question": "Which opportunity would you like to review? Enter an opportunity name or Salesforce ID.",
    "type": "text",
    "defaultValue": ""
  }]
}
```

```sql
-- Search by name (fuzzy)
SELECT
    OPPORTUNITY_ID,
    OPPORTUNITY_NAME,
    STAGE_NAME,
    OPPORTUNITY_OWNER_NAME,
    TOTAL_ACV
FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
WHERE LOWER(OPPORTUNITY_NAME) LIKE LOWER('%{search_term}%')
   OR LOWER(OPPORTUNITY_ID) LIKE LOWER('%{search_term}%')
ORDER BY TOTAL_ACV DESC NULLS LAST
LIMIT 10
```

If multiple results, use `ask_user_question` with the results as options:

```json
{
  "questions": [{
    "header": "Select Opp",
    "question": "Multiple opportunities found. Which one?",
    "multiSelect": false,
    "options": [
      {"label": "Opp Name 1", "description": "Stage | Owner | $ACV"},
      {"label": "Opp Name 2", "description": "Stage | Owner | $ACV"}
    ]
  }]
}
```

### Step 1: Show Current MEDDPICC Scores

Pull the current state from RAVEN:

```sql
SELECT
    OPPORTUNITY_ID,
    OPPORTUNITY_NAME,
    STAGE_NAME,
    OPPORTUNITY_OWNER_NAME,
    TOTAL_ACV,
    MEDDPICC_OVERALL_SCORE,
    MEDDPICC_METRICS,
    MEDDPICC_METRICS_SCORE,
    MEDDPICC_ECONOMIC_BUYER,
    MEDDPICC_ECONOMIC_BUYER_SCORE,
    MEDDPICC_DECISION_CRITERIA,
    MEDDPICC_DECISION_CRITERIA_SCORE,
    MEDDPICC_DECISION_PROCESS,
    MEDDPICC_DECISION_PROCESS_SCORE,
    MEDDPICC_PAPER_PROCESS,
    MEDDPICC_PAPER_PROCESS_SCORE,
    MEDDPICC_IDENTIFY_PAIN,
    MEDDPICC_IDENTIFIED_PAIN_SCORE,
    MEDDPICC_CHAMPION,
    MEDDPICC_CHAMPION_SCORE,
    MEDDPICC_PRIMARY_COMPETITOR,
    MEDDPICC_COMPETITION_SCORE
FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW
WHERE OPPORTUNITY_ID = '{opportunity_id}'
```

**If scores exist (non-NULL):** Display as a table.

**If scores are NULL:** Ask the user how they want to generate scores:

```json
{
  "questions": [{
    "header": "Scoring",
    "question": "Scores are not yet available for this opportunity. How would you like to generate them?",
    "multiSelect": false,
    "options": [
      {"label": "Let CoCo score", "description": "Have the assistant score it directly using the MEDDPICC criteria — faster, no Snowflake compute"},
      {"label": "Run the pipeline in Snowflake (requires permissions)", "description": "Run CORTEX.COMPLETE() in Snowflake using the production prompt — most accurate, matches the pipeline, but requires permissions"}
    ]
  }]
}
```

- **If "Let CoCo score":** Proceed to Step 1c.
- **If "Run the pipeline in Snowflake (requires permissions)":** Proceed to Step 1b.

#### Step 1b: Generate Scores via Snowflake LLM (when scores are NULL)

Use this SQL to score the opportunity on-the-fly. This replicates the production scoring pipeline without writing to any table.

```sql
WITH prompt AS (
    SELECT PROMPT_TEXT
    FROM SALES.RAVEN.MEDDPICC_PROMPT_LIBRARY_VIEW
    WHERE TYPE = 'Standard' AND PROMPT_TYPE = 'Opportunity'
),
user_msg AS (
    SELECT OBJECT_CONSTRUCT(
        'object_type', 'Opportunity',
        'current_stage', o.STAGE_NAME,
        'previous_stage', '',
        'metrics_value', COALESCE(o.MEDDPICC_METRICS, ''),
        'economic_buyer_value', COALESCE(o.MEDDPICC_ECONOMIC_BUYER, ''),
        'decision_criteria_value', COALESCE(o.MEDDPICC_DECISION_CRITERIA, ''),
        'decision_process_value', COALESCE(o.MEDDPICC_DECISION_PROCESS, ''),
        'paper_process_value', COALESCE(o.MEDDPICC_PAPER_PROCESS, ''),
        'identified_pain_value', COALESCE(o.MEDDPICC_IDENTIFY_PAIN, ''),
        'champion_value', COALESCE(o.MEDDPICC_CHAMPION, ''),
        'competition_value', COALESCE(o.MEDDPICC_PRIMARY_COMPETITOR, ''),
        'record_name', o.OPPORTUNITY_NAME,
        'owner_name', COALESCE(o.OPPORTUNITY_OWNER_NAME, ''),
        'manager_name', ''
    )::STRING as payload
    FROM SALES.RAVEN.SDA_OPPORTUNITY_VIEW o
    WHERE o.OPPORTUNITY_ID = '{opportunity_id}'
),
llm_call AS (
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'claude-3-5-sonnet',
        ARRAY_CONSTRUCT(
            OBJECT_CONSTRUCT('role', 'system', 'content', p.PROMPT_TEXT),
            OBJECT_CONSTRUCT('role', 'user', 'content', u.payload)
        ),
        OBJECT_CONSTRUCT()
    ) as raw_response
    FROM prompt p, user_msg u
)
SELECT raw_response:choices[0]:messages::STRING as scores_text
FROM llm_call
```

Parse the JSON response to extract element scores. The structure is:
```json
{
  "element_scores": {
    "metrics": {"score": 9, "required": true, "current_value": "..."},
    "economic_buyer": {"score": 0, "required": true, "current_value": "..."},
    "decision_criteria": {"score": 8, ...},
    "decision_process": {"score": 7, ...},
    "paper_process": {"score": 0, ...},
    "identified_pain": {"score": 10, ...},
    "champion": {"score": 5, ...},
    "competition": {"score": 10, ...}
  },
  "overall_score": 52
}
```

#### Step 1c: Score It Yourself (when scores are NULL and user chooses self-scoring)

Score each element directly using the MEDDPICC criteria from Step 2, based on the text fields already fetched in Step 1. Apply the Evaluation Dimensions (Completeness, Specificity, Quantification, Actionability, Progression) and Scoring Scale. For Competition, use the rule: non-null = 10, null = 0. Calculate overall as `round((sum_of_all_8_scores / 80) * 100)`.

Present the results in the same display format as Step 1b.

#### Display Format

Show a summary table with the full text for each element and a status column:

```
| Element             | Score  | Status           | Text                                |
|---------------------|--------|------------------|-------------------------------------|
| Metrics             | X/10   | Strong / Needs Improvement | <full text from MEDDPICC field>     |
| Economic Buyer      | X/10   | Strong / Needs Improvement | <full text or "(empty)" if NULL>    |
| Decision Criteria   | X/10   | ...              | ...                                 |
| Decision Process    | X/10   | ...              | ...                                 |
| Paper Process       | X/10   | ...              | ...                                 |
| Identified Pain     | X/10   | ...              | ...                                 |
| Champion            | X/10   | ...              | ...                                 |
| Competition         | X/10   | ...              | ...                                 |
|---------------------|--------|------------------|-------------------------------------|
| Overall             | XX/100 |                  |                                     |
```

Status column: "Strong" if score >= 8, "Needs Improvement" if score <= 7. Do not truncate the text.


For each weak element, one weak element at a time:
1. Provide coaching feedback (step 2), then
2. Simulate the score changes (step 3), then
3. Tell the user to update Salesforce (step 4)

### Step 2: Coach on Weak Elements

After showing the scores, identify elements scoring **7 or lower**. 

**Quality Evaluation Criteria** (from `MEDDPICC_PROMPT_LIBRARY`):

| Element | What good looks like | Common gaps |
|---------|---------------------|-------------|
| **Metrics** | Quantifiable business impact; connected to customer KPIs; specific and measurable; baseline + target values | Missing baseline numbers, no target values, generic "save money" |
| **Economic Buyer** | Budget holder identified by title; sufficient authority level; C-level/VP/Director appropriate for deal size | No contact linked, junior title, no title at all |
| **Decision Criteria** | Formal + informal decision factors; your position relative to criteria; weighting of factors; linked to value prop | Generic "cost and performance", no competitive positioning |
| **Decision Process** | Approval steps + timeline; all stakeholders identified; where deal currently sits; blockers/accelerators | Just a list of steps without timeline, missing stakeholders |
| **Paper Process** | Contract review/approval process; procurement involvement + timing; legal review requirements; procurement timeline | Empty or "standard process", no timeline |
| **Identified Pain** | Specific business challenges; quantified impact; connected to your solution; who experiences it + their influence | Vague "they need to modernize", no quantification |
| **Champion** | Internal advocate identified by title; appropriate seniority for influence | Contact linked but no title, junior role |
| **Competition** | ANY non-null value = score of 10 regardless of content | Not selected |

**Scoring System:**
- Empty/missing field → score: 0
- All elements scored 0-10 regardless of required/not required
- Economic Buyer & Champion: scored on title appropriateness (0-10)
- Competition: non-null = 10, null = 0

**Evaluation Dimensions (0-10 total):**
1. Completeness (0-2): Is all required info present?
2. Specificity (0-2): Customer-specific vs generic?
3. Quantification (0-2): Metrics/impacts quantified?
4. Actionability (0-2): Useful for deal strategy?
5. Progression (0-2): Detail appropriate for current stage?

**Scoring Scale:**
- 0: Empty/missing
- 1: Minimal (single generic phrase)
- 2-3: Very generic
- 4-6: Basic but lacks specifics or quantification
- 7-8: Good detail, missing 1-2 key aspects
- 9-10: Comprehensive, meets all criteria

**Format the coaching like this:**

> **Paper Process (0/10)** - Currently empty.
> To score well, document:
> 1. The contract/proposal review steps (who reviews, in what order)
> 2. Procurement involvement and timing
> 3. Legal review requirements
> 4. Expected timeline from proposal to signature

Do NOT provide example text or suggest specific updates. Only explain what the scoring criteria require. Let the user decide what text they want to write.

Then ask: **"What would you like to update this field to?"** using the `ask_user_question` tool with a text input (no default value).

### Step 3: Simulate Score Changes

When the user provides updated text for an element:

1. Score the updated text yourself (you are the LLM) using the scoring criteria and element guidance from Step 2. Do NOT call `CORTEX.COMPLETE` -- just evaluate it directly and return a score (0-10) with brief reasoning.
2. Keep all other element scores unchanged from the baseline (Step 1/1b).
3. Recalculate overall: `round((sum_of_all_8_scores / 80) * 100)`.

**Display the before/after comparison:**

```
| Element          | Before | After | Change |
|------------------|--------|-------|--------|
| <changed element>| X/10   | Y/10  | +/-N   |
```

**Important notes on simulation:**
- This approach scores ONLY the changed element, so unchanged elements stay exactly the same (no non-deterministic drift).
- The simulation does NOT update any table. It's read-only. Tell the user: "This is a simulation. To update the actual score, update the field in Salesforce and the scoring pipeline will re-score it within 10 minutes."
- The user can simulate multiple elements in sequence. Keep a running tally of the baseline scores, updating each element as the user provides new text. Each subsequent simulation uses the latest running tally.
- If the user wants to simulate changes to **multiple elements at once**, score each element individually in parallel (multiple LLM calls) and combine the results.

### Step 4: Tell the user to update Salesforce

After simulation, tell the user wants to push the updated text to Salesforce.
Provide the SFDC link: https://snowforce.lightning.force.com/lightning/r/Opportunity/{opportunity_id}/view

## Important Constraints

- **Read-only on Snowflake**: This skill NEVER writes to any Snowflake table. All scoring is done via inline `CORTEX.COMPLETE()` calls.
- **Prompt source of truth**: Always read the prompt from `SALES.RAVEN.MEDDPICC_PROMPT_LIBRARY_VIEW`. Never hardcode or modify the prompt.
- **LLM model**: Use `claude-3-5-sonnet` to match the production pipeline.
- **Warehouse**: Queries run on the user's current warehouse. The `CORTEX.COMPLETE()` call is serverless.
