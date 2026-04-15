# Self-Evaluation Checklist

After creating or modifying any artifact (scope doc, SQL queries, code), evaluate against these criteria:

## Checklist

| Criterion | Question | Pass? |
|-----------|----------|-------|
| **Correctness** | Does the output do what was asked? | |
| **Instruction Adherence** | Did I follow all skill rules and guidelines? | |
| **Completeness** | All parts of the request addressed? | |
| **Consistency** | Matches existing patterns and conventions? | |
| **No Conflicts** | No contradictory or ambiguous content? | |
| **Data Accuracy** | Are metrics/numbers verified and correctly calculated? | |

## Report Format

After self-evaluation, report:

1. **Checklist results** - Pass/fail for each criterion
2. **Gaps identified** - What's missing or incomplete
3. **Assumptions made** - What did I assume without confirmation
4. **Confidence score** - 1-5 scale (1=low, 5=high)

## Common Mistakes to Check

### SQL Queries
- [ ] Used DISTINCT when counting unique items
- [ ] Verified column names exist before using
- [ ] Checked if session context needed (PST.SVCS views)
- [ ] Confirmed which account context is active
- [ ] Validated joins don't inflate row counts

### Scope Documents
- [ ] Customer metrics are from correct account(s)
- [ ] **Tenure uses ALL historical subscriptions** (query 1.3.1), not just active ones
- [ ] Account counts are distinct, not row counts
- [ ] Internal URLs/IDs only included if doc is internal-only
- [ ] Warehouse/credit data specifies which account and time period
- [ ] **Consumption shows CURRENT BASELINE** (query 1.3.3)
- [ ] **Consumption shows INCREMENTAL INCREASE** (new credits, % increase)
- [ ] **Consumption shows BOTH together** (baseline vs new)

### General
- [ ] Re-read the original request before declaring done
- [ ] Verified numbers make sense (sanity check)
- [ ] Noted any data limitations or caveats
