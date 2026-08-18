# Writing ES Brief Content

The brief is a one-slide internal artifact whose job is to let an ES reviewer
decide whether the deal qualifies as an Engineering Solution. It is not a sales
document. Write for a reviewer who has never heard of the deal.

## Left card — Solution Description

**Overview (<=208 chars).** What the customer does and where their Snowflake
estate stands today. Lead with the business context, not the technology. State
the current-state fact that makes the engagement necessary.

**The Challenge (<=208 chars).** The specific, concrete gap. Name what is manual,
missing, or ungoverned. Avoid abstractions like "lacks maturity" — say what
does not exist. This paragraph carries most of the qualification weight, because
it establishes that something has to be *built*.

**Desired Outcomes (<=5 bullets, <=52 chars each).** End-state capabilities, not
activities. "Credits attributable to an owner, org-wide" is an outcome;
"implement tagging" is an activity. At 52 chars, drop articles and use accepted
shorthand.

## Right card — ES Qualification Criteria Comments

Three fixed criteria. Do not rename, reorder, or add. Each comment is <=136 chars
and must answer the criterion with deal-specific evidence, not restate it.

**New Solution Ownership.** Does Services Delivery own building something that
does not exist today? Name the concrete artifacts SD builds. This is the
criterion that fails most often — configuring native Snowflake features is
weaker evidence than building custom pipelines, dashboards, models, or apps.
Lead with the strongest build evidence available.

**Production-Ready Delivery.** Does it land as a live system in the customer's
environment, not a recommendation deck? Cite the validation and handover
mechanics: UAT sign-off, data validated against a named source, audit trails,
multi-region, knowledge transfer.

**Fixed Price Contract.** State the fee, duration, and milestone structure.
Fixed-fee with acceptance gates tied to deliverables is the qualifying shape.

## Be honest about fit

If the scope is mostly configuration of native features, or mostly advisory, say
so to the user rather than inflating the ownership comment. A brief that
overstates the build content wastes the reviewer's time and damages credibility
on the next submission. Surface the weakness and let the user decide whether to
submit, rescope, or withdraw.
