# Example Inputs

Reference examples of user inputs that the proposal generator should handle. These are sanitized meeting notes and project descriptions.

## Example 1: GenAI Solution (Complete Input)

> Project Description: they are looking for a GenAI solution that can help provide deeper insights in less time about their products while opening access to non-technical users.
> They have many product tables and also tables with product reviews.
> In the engagement, we would leverage Cortex AISQL for unstructured data processing, Cortex Analyst with several personas, Cortex Search for unstructured data interactions, and Snowflake Intelligence as an orchestrating and interface layer. I expect this to complete in 12 weeks.
>
> Can you write a Proposal?

**Analysis**: All 3 elements present. Generate immediately.

## Example 2: ML Migration (Meeting Notes)

> - Wants help migrating some trees to snowflake
> - Very manual process running ML models (4 ML models: 1 regression, 3 classification)
> - LightGBM models for electricity consumption prediction and customer classification
> - Running notebooks on bi-monthly cadence, want to increase
> - No MLOps currently
> - Team of 5, mostly one person managing models
> - Everything based in Redshift, migrating to Snowflake
> - Wants native Snowflake: Feature store, registry, observability
> - Ideally everything moved over by mid-January

**Analysis**: Has description and timeline. Missing explicit Snowflake tools (can infer from "native Snowflake" mention). May need to confirm specific SF features.

## Example 3: Augmented BI (Mixed Notes + Summary)

> Client is looking to leverage Snowflake Cortex to build an "Augmented BI" solution, empowering business users and executives to get quick insights from their data using natural language.
> They are exploring Cortex Analyst for structured data and Cortex Search for unstructured data.
> Data includes 30 CRM tables, 400k CRM notes, 15M transaction rows.
> End vision: robust internal front-end system. Wants governance in scope for phase one.
> Timeline - now!

**Analysis**: Has description and SF tools. Timeline is vague ("now!") - may need to ask for specific duration in weeks.

## Example 4: Propensity Modeling (Detailed Meeting Notes)

> - Want a model that scans data every 15 minutes to pull cohorts most likely to buy
> - 1.4M customers, focusing on 260k latent segment
> - Data: purchase history, customer value, some demographics
> - Using basic third-party model currently, doing some clustering
> - Wants us to build and develop it
> - Phase 1 focuses on historic data, Phase 2 adds behavioral data
> - Wants it ASAP

**Analysis**: Has description. Missing explicit Snowflake tools and specific timeline. Need to ask for both.
