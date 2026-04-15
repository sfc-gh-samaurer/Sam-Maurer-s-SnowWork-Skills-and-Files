# Complexity Factors and Multipliers

## Deliverable Complexity Levels (L/M/H)

Use these criteria when assigning complexity in the deliverables table.

### Low (L)
- Well-understood pattern with existing examples
- Single data source or integration point
- Standard Snowflake features (GA, documented)
- Minimal business logic or transformation
- Customer has done similar work before

**Examples:** Single-source staging table, basic Streamlit page, standard RBAC setup

### Medium (M)
- Some custom design required
- 2-3 data sources or integration points
- Moderate business logic or transformations
- Customer needs guidance but understands concepts
- Some iteration expected during design

**Examples:** Multi-source pipeline, Cortex Search service, error handling framework

### High (H)
- Novel architecture or first-of-kind pattern
- 4+ data sources or complex integration
- Heavy business logic, edge cases, exceptions
- Preview features or undocumented approaches
- Significant iteration and validation needed

**Examples:** Multi-region replication, custom ML pipeline, self-healing automation

---

## Scale Factor

Apply based on object counts or data volume.

| Scale | Multiplier | Criteria |
|-------|------------|----------|
| Small | 1.0x | < 50 objects, < 100 GB |
| Medium | 1.15x | 50-500 objects, 100 GB - 1 TB |
| Large | 1.3x | 500-5,000 objects, 1-10 TB |
| Massive | 1.5x | 5,000+ objects, 10+ TB |

**Object types to count:** tables, views, streams, tasks, procedures, stages, pipes

**Scale affects:**
- Discovery and assessment time
- Pattern validation effort
- Testing and edge case coverage
- Documentation thoroughness

---

## Novelty Factor

How much original design work vs. applying known patterns.

| Novelty | Multiplier | Indicators |
|---------|------------|------------|
| Template | 0.85x | Repeating proven pattern with minor customization |
| Standard | 1.0x | Known approach, some adaptation required |
| Custom | 1.25x | New combination of features, design decisions needed |
| Novel | 1.5x | First-of-kind, no existing reference, experimentation required |

**Questions to assess novelty:**
- Has Snowflake PS done this exact thing before?
- Can you point to documentation or a reference architecture?
- Are there known gotchas and best practices?
- Will this require trial-and-error or spike work?

---

## Advisory vs Build Distinction

Advisory engagements require different effort than implementation.

### Advisory Multipliers (apply to baseline hours)

| Activity Type | Advisory | Build | Notes |
|---------------|----------|-------|-------|
| Discovery | 1.0x | 1.0x | Same effort either way |
| Design | 1.0x | 0.7x | Advisory needs thorough documentation |
| Implementation | 0x | 1.0x | Advisory = no implementation |
| Testing | 0.3x | 1.0x | Advisory validates approach, not code |
| Documentation | 1.5x | 1.0x | Advisory deliverable IS the document |
| Knowledge Transfer | 1.2x | 1.0x | Advisory emphasizes enablement |

**Advisory engagement characteristics:**
- Deliverables are documents, not deployed objects
- Success = customer can implement independently
- More time on "why" and trade-offs
- Heavier documentation burden

**Build engagement characteristics:**
- Deliverables are working Snowflake objects
- Success = solution deployed and operational
- More time on coding and debugging
- Documentation supports handoff

---

## Base Complexity Multipliers

| Factor | Multiplier | When to Apply |
|--------|------------|---------------|
| Preview features | 1.25x | Any Snowflake feature in preview/beta |
| Cross-source joins | 1.25x | Data from 3+ distinct sources |
| Complex transformations | 1.5x | Heavy business logic, multiple CTEs |
| Regulatory/compliance | 1.25x | HIPAA, PCI, SOX requirements |
| Limited customer availability | 1.2x | Customer team < 50% available |

---

## Customer Maturity Adjustments

| Maturity Level | Modifier | Indicators |
|----------------|----------|------------|
| None | +30% | No Snowflake experience, needs basics |
| Beginner | +20% | < 6 months on Snowflake, limited use |
| Intermediate | baseline | 6-18 months, active usage |
| Advanced | -10% | > 18 months, strong internal team |

---

## Technical Risk Factors

| Risk | Multiplier | Mitigation |
|------|------------|------------|
| Unproven integration | 1.3x | Add spike/POC phase |
| Data quality unknown | 1.2x | Add discovery buffer |
| Third-party dependency | 1.2x | Document SLAs, escalation paths |
| Tight timeline | 1.15x | Reduce scope or add resources |

---

## Module-Specific Factors

### Data Engineering
- Multi-region: +15%
- Real-time requirements: +25%
- Complex CDC patterns: +20%
- Massive scale (5K+ objects): +50%

### Apps (Streamlit)
- External authentication: +20%
- High concurrency (50+ users): +15%
- Custom components: +30%

### GenAI / Cortex
- Custom model fine-tuning: +40%
- Multi-agent orchestration: +30%
- RAG with complex sources: +25%

### ML/AI
- Feature engineering heavy: +25%
- Model explainability required: +20%
- MLOps/monitoring: +30%

### Iceberg / Open Table Formats
- Multi-catalog (3+ catalog types): +25%
- Cross-cloud or cross-region storage: +30%
- Bidirectional cross-engine writes: +35%
- Full Polaris Catalog deployment: +25%
- Table conversion from managed tables (100+ tables): +20%
- Preview catalog types or features: +25%
- Strict auto-refresh SLAs (sub-minute): +20%
- Complex IAM / cross-account trust policies: +15%

---

## Stacking Multipliers

When multiple factors apply, multiply them together.

**Example (Paychex):**
- Scale: Massive (65K databases) = 1.5x
- Novelty: Custom (new pattern combination) = 1.25x
- Advisory: Documentation-heavy = 1.0x (already advisory baseline)
- Maturity: Intermediate = 1.0x

Total multiplier: 1.5 × 1.25 = **1.875x**

If base advisory estimate was 80 hours, adjusted = 150 hours.

---

## Contingency Guidelines

| Confidence Level | Contingency |
|------------------|-------------|
| High (clear requirements, known tech) | 10% |
| Medium (some unknowns) | 15% |
| Low (significant unknowns) | 20-25% |

Always add contingency after applying multipliers.

---

## Quick Reference: Complexity Assessment

When scoping a new engagement, answer these questions:

1. **What's the L/M/H for each deliverable?** (Use criteria above)
2. **What's the scale?** (Count objects, estimate data volume)
3. **What's the novelty?** (Template → Novel spectrum)
4. **Is this Advisory or Build?** (Adjust activity mix)
5. **What multipliers stack?** (Preview, compliance, availability, etc.)
6. **What's the confidence level?** (Set contingency %)
