---
name: pptx-content-standards
description: Content writing standards, title philosophy, narrative voice, and Snowflake content bank.
---

## 20. Content Writing Standards (Consulting-Grade Quality)

Every deck produced by this skill must read as if it were written by a senior
partner at a top-tier strategy firm (Bain, McKinsey, BCG). The difference
between a mediocre deck and a great deck is **never the layout — it's the words**.

### 20.1 Title Philosophy

Titles are the most important text on any slide. They must earn the audience's attention.

| Quality | Example | Verdict |
|---------|---------|---------|
| **Generic** | "OVERVIEW" | Useless — says nothing |
| **Descriptive** | "CORTEX AI OVERVIEW" | Adequate for internal docs |
| **Evocative** | "THE AI ENGINE INSIDE YOUR DATA" | Consulting-grade — tells a story |
| **Metaphorical** | "FROM RAW DATA TO REFINED INTELLIGENCE" | Executive-ready — creates intrigue |

**Rules for Titles**:
- **Every title must pass the "so what?" test** — if someone reads only the title, they should understand the slide's purpose
- **Use action-oriented or outcome-oriented language** — "ACCELERATING TIME TO INSIGHT" not "TIME TO INSIGHT"
- **Use metaphors and strong verbs when appropriate** — "UNLOCKING", "ARCHITECTING", "NAVIGATING", "FORGING"
- **ALL CAPS** is required by Snowflake brand — make the words worthy of the emphasis
- **Max 5-6 words** for punchy impact, or 8-10 words for descriptive titles
- **Never use single-word titles** — "OVERVIEW", "AGENDA", "SUMMARY" are banned. Use "YOUR SESSION ROADMAP", "WHAT WE COVERED AND WHAT COMES NEXT"

**Title Pairs — Good vs. Bad**:

| Bad | Good |
|-----|------|
| AGENDA | YOUR SESSION ROADMAP |
| BENEFITS | THE CASE FOR CHANGE |
| APPROACH | FORGING THE PATH FORWARD |
| ARCHITECTURE | THE ENGINE UNDER THE HOOD |
| NEXT STEPS | CHARTING THE COURSE AHEAD |
| KEY METRICS | THE NUMBERS THAT MATTER |
| TEAM | THE TEAM BEHIND THE MISSION |
| CHALLENGES | NAVIGATING THE TERRAIN |
| SUMMARY | THE VIEW FROM THE SUMMIT |
| COMPARISON | WEIGHING THE OPTIONS |
| ROADMAP | STAGING THE ASCENT |
| CASE STUDY | PROOF OF IMPACT |

### 20.2 Subtitle Philosophy

Subtitles are the **tagline** for the slide. They frame the context, set the tone,
and tell the reader WHY this slide matters.

**Rules for Subtitles**:
- **Always a complete sentence or phrase** — never a single word or fragment
- **15-25 words** — long enough to provide context, short enough to read at a glance
- **Set the "why" and the "who"** — connect the slide content to the audience's world
- **Use evocative, outcome-oriented language** — describe impact, not process

**Subtitle Examples**:

| Slide Topic | Bad Subtitle | Good Subtitle |
|------------|-------------|---------------|
| Cortex AI overview | "Overview of features" | "The AI-powered engine fueling your journey from complex code to conversational command" |
| Architecture options | "Three options" | "Evaluating three architectural paths to determine the fastest route to production value" |
| Benefits | "Key benefits" | "Why the data points, the economics, and the architecture all point in the same direction" |
| Team bios | "Project team" | "A specialised syndicate of experts engineered to navigate the technical terrain so you don't have to" |
| Roadmap | "Implementation plan" | "A phased approach to building autonomous enterprise intelligence — from first deploy to peak autonomy" |

### 20.3 Body Content Standards

Body content is where most decks fail. Common failures: too short (fragments),
too generic (could apply to anything), or flat (no hierarchy).

**Rules for Body Bullets**:
- **Every bullet must be a complete thought** — minimum 15 words, typically 20-35 words
- **Start each bullet with a bold keyword or phrase** — this is the "headline" of the bullet
  - Use `set_ph_sections()` for heading + body pairs
  - Use `set_ph_bold_keywords()` for keyword: description patterns
- **Be specific, not generic** — include numbers, names, timeframes, or outcomes where possible
- **Maximum 4-5 bullets per placeholder** — quality over quantity
- **Each bullet must add NEW information** — no repetition or filler

**Content Density Guide**:

| Slide Type | Min Bullets | Words per Bullet | Helper Function |
|-----------|------------|-----------------|----------------|
| Content (1-col) | 3-4 sections | 20-35 words per body line | `set_ph_sections()` |
| Content (2-col) | 2-3 sections per col | 15-25 words per body line | `set_ph_sections()` |
| Content (3-col) | 1-2 sections per col | 10-20 words per body line | `set_ph_sections()` |
| Considerations | 3-5 items | 15-30 words each | `set_ph_bold_keywords()` |
| Flat list (agenda, links) | 4-8 items | 5-15 words each | `set_ph_lines()` |

**Body Content Examples**:

| Bad (fragment) | Good (complete thought) |
|---------------|----------------------|
| "Faster queries" | "Query execution times reduced from 4 hours to 23 seconds through multi-cluster auto-scaling and intelligent workload distribution" |
| "Cost savings" | "Annualised infrastructure savings of $2.3M achieved by consolidating seven legacy systems into a single Snowflake platform" |
| "Easy to use" | "Zero-friction productivity: teams build production-grade data pipelines through conversational commands without writing infrastructure code" |
| "Better governance" | "Row-level security and dynamic data masking enforced from day one, with full audit trails on every data access event" |

### 20.4 Narrative Voice & Tone

Write in the voice of a senior strategy consultant presenting to executives:

- **Authoritative**: State facts with confidence — "This approach delivers..." not "This approach might help..."
- **Outcome-oriented**: Lead with results — "10x faster insights" not "We improved query speed"
- **Specific**: Use numbers, timeframes, and names — "500+ self-service users in 90 days" not "many users quickly"
- **Forward-leaning**: Use active, future-tense language — "We will deploy..." not "It can be deployed..."
- **Concise but substantial**: Every word earns its place — no filler phrases like "it should be noted that" or "in order to"

**Banned Phrases** (never use these in any deck):

| Banned | Replacement |
|--------|------------|
| "Overview of..." | (just state the content directly) |
| "In this slide we will..." | (never narrate the slide itself) |
| "As mentioned earlier..." | (each slide must stand alone) |
| "Various features" | (name the specific features) |
| "Multiple benefits" | (list the specific benefits) |
| "It is important to note" | (just state the point) |
| "Leveraging synergies" | (be specific about what improves) |
| "Best-in-class" | (show the data instead) |

### 20.5 Feature Status Tagging (MANDATORY for Snowflake Features)

When a deck mentions any Snowflake feature or capability, **always include its availability status** using one of these tags. Audiences — especially customers and sales teams — need to know what they can use TODAY vs. what is coming.

| Tag | Meaning | How to Display |
|-----|---------|---------------|
| **GA** | Generally Available | Append "(GA)" after feature name, or use a green/DK2 badge |
| **Public Preview** | Available but not production-ready | Append "(Public Preview)" — warn about limitations |
| **Private Preview** | Invite-only access | Append "(Private Preview)" — note how to request access |
| **Coming Soon** | Announced but not yet available | Append "(Coming Soon)" with expected timeline if known |

**Rules:**
- Every feature mentioned on a content slide MUST have its status tag
- Tables listing features MUST include a "Status" column
- Titles can include the status: e.g. "CORTEX AGENTS — GA" or "ML OBSERVABILITY — PUBLIC PREVIEW"
- For slides listing multiple features, use colour-coded badges: DK2 fill for GA, SF_BLUE fill for Preview
- If unsure about current status, refer to [Snowflake documentation](https://docs.snowflake.com/) — do NOT guess
- Feature status changes frequently — always verify against the latest docs at time of deck creation

**Example — Feature Table with Status Column:**

| Feature | Status | Description |
|---------|--------|-------------|
| Cortex AI Functions | GA | LLM functions via SQL |
| Cortex Agents | GA | Multi-tool AI orchestration |
| ML Observability | Public Preview | Model monitoring & drift detection |

### 20.6 Chapter Divider Text

Chapter dividers use 40pt bold ALL CAPS white text on a dark navy background.
They must be punchy, evocative, and set the tone for the section that follows.

**Rules**:
- **Max 2-3 lines, max 5-6 words per line**
- **Use metaphors, action words, or provocative questions**
- **The divider text IS the section brand** — make it memorable

**Examples**:

| Section | Bad | Good |
|---------|-----|------|
| Current state analysis | "CURRENT STATE" | "WHERE WE\nSTAND TODAY" |
| Proposed solution | "PROPOSED SOLUTION" | "FORGING THE\nPATH FORWARD" |
| Implementation plan | "IMPLEMENTATION" | "STAGING THE\nASCENT" |
| Closing/Summary | "SUMMARY" | "THE VIEW FROM\nTHE SUMMIT" |
| AI/Innovation | "AI CAPABILITIES" | "THE ENGINE OF\nINTELLIGENCE" |

### 20.7 Content Depth by Audience

The same topic requires dramatically different content depending on who is in the room.

| Audience | Depth | Slide Count | Content Focus | Tone |
|----------|-------|-------------|---------------|------|
| **C-Suite / VP** (CTO, CDO, CFO) | High-level strategic | 6-10 | Business outcomes, ROI, competitive advantage, risk mitigation. Numbers > words. Lead with "so what" not "how." | Authoritative, outcome-first, decisive |
| **Director / Manager** | Strategic + tactical | 10-15 | Capabilities, timelines, resource needs, trade-offs. Balance vision with execution detail. | Confident, structured, option-oriented |
| **Architect / Engineer** | Technical deep-dive | 12-20 | Architecture diagrams, code patterns, configuration, performance benchmarks, integration points. | Precise, evidence-based, actionable |
| **Mixed / Workshop** | Progressive disclosure | 15-25 | Start executive, then drill down. Use chapter dividers to signal depth changes. | Adaptive — headline for execs, detail for practitioners |
| **Customer / External** | Polished narrative | 8-15 | Value proposition, proof points, customer stories, differentiation. NO internal jargon. | Persuasive, benefit-oriented, credibility-building |

**Rules**:
- **Always ask or infer the audience** before writing content (see Section 0)
- **Executive slides**: max 4 bullets, each 20-30 words, lead with the outcome
- **Technical slides**: up to 6 bullets, include specific config/code/commands, reference documentation
- **Mixed audience**: use the "headline + detail" pattern — bold headline for the exec, supporting detail for the practitioner

### 20.8 Deck Archetypes & Content Blueprints

Below are **slide-by-slide content blueprints** for the 6 most common deck types. When the user's request matches an archetype, follow the blueprint — it ensures nothing important is missing.

#### Archetype 1: Executive Briefing (6-10 slides)

*Use when*: Presenting a technology, capability, or initiative to leadership for awareness or approval.

| # | Slide | Layout/Pattern | Content to Include |
|---|-------|---------------|-------------------|
| 1 | Cover | Layout 13 | Evocative title, audience-specific subtitle, presenter name + date |
| 2 | Context & Opportunity | Layout 5 (1-col) | 3-4 sections: market trend driving urgency, internal trigger or pain point, size of the opportunity (quantified), why now (timing catalyst) |
| 3 | The Vision | 14.21 (Pyramid) or Layout 5 | The end-state articulated in 2-3 layers — from strategic vision down to operational foundation |
| 4 | Key Proof Points | 14.25 (Icon Circles) or 14.7 (Stats) | 4 quantified metrics that make the case — cost savings, speed improvement, adoption numbers, risk reduction |
| 5 | How We Get There | 14.18 (Chevrons) or 14.6 (Steps) | 3-4 phase process with clear deliverables per phase — not just phase names but what each phase *produces* |
| 6 | Investment & Returns | Layout 6 (2-col) | Left: investment required (time, cost, resources). Right: expected returns (ROI, timeline to value, risk offset) |
| 7 | Recommended Next Steps | Layout 7 (3-col) | 3 specific actions with owners and dates — "Approve budget by March 15", "Kick off discovery week of March 20", "First pilot live by May 1" |
| 8 | Thank You | Layout 28 | |

#### Archetype 2: Technical Architecture Review (12-18 slides)

*Use when*: An architect presents a solution design to a technical audience for review, feedback, or sign-off.

| # | Slide | Layout/Pattern | Content to Include |
|---|-------|---------------|-------------------|
| 1 | Cover | Layout 13 | Solution name, "Architecture Review", architect name + date |
| 2 | Agenda | 14.1 (Visual Agenda) | 4-5 session blocks: Context, Current State, Proposed Architecture, Key Decisions, Next Steps |
| 3 | Business Context | Layout 5 (1-col) | The business problem this architecture solves — 3-4 sections with heading + 1-2 body lines each. Include the success criteria. |
| 4 | Current State | 14.5 (Before/After) or Layout 6 | Left: current architecture components, data flows, pain points. Right: target state highlights. |
| 5 | Chapter: Architecture | Layout 18 | "THE ENGINE\nUNDER THE HOOD" or similar |
| 6 | Architecture Overview | 14.20 (Hub & Spoke) or Layout 0 (diagram) | Central platform (Snowflake) with connected components — ingestion, processing, serving, governance, monitoring |
| 7 | Data Flow | 14.18 (Chevron Flow) | End-to-end data flow: Source → Ingest → Transform → Serve → Consume. Include technology at each stage (Snowpipe, Dynamic Tables, Cortex AI, Streamlit) |
| 8 | Technology Stack | 14.23 (Hexagons) | Platform capabilities used — each hexagon is a technology with 1-line description |
| 9 | Security & Governance | Layout 6 (2-col) | Left: authentication, network policy, encryption. Right: RBAC, masking, row-level security, audit trails |
| 10 | Key Design Decisions | 14.10 (Decision Matrix) | 2-3 architectural choices with options evaluated — e.g. "ETL vs ELT", "Single vs multi-cluster warehouse", "Cortex AI vs external ML" |
| 11 | Performance & Sizing | Layout 0 + Table | Warehouse sizing table, expected query volumes, latency targets, concurrency model |
| 12 | Chapter: Execution | Layout 20 | "STAGING THE\nASCENT" |
| 13 | Implementation Roadmap | 14.19 (Milestone Timeline) | 5-6 milestones with dates, deliverables, and dependencies |
| 14 | Risks & Mitigations | Layout 6 (2-col) | Left: technical risks (data volume, latency, complexity). Right: mitigation strategy for each |
| 15 | Open Questions | Layout 5 (1-col) | 3-5 items requiring decision or input from the review audience — specific, actionable |
| 16 | Thank You | Layout 27 | |

#### Archetype 3: Workshop / Training Deck (15-25 slides)

*Use when*: Facilitating a hands-on session, training, or collaborative working session.

| # | Slide | Layout/Pattern | Content to Include |
|---|-------|---------------|-------------------|
| 1 | Cover | Layout 13 | Workshop title, "Hands-On Workshop", facilitator + date |
| 2 | Agenda + Outcomes | 14.1 + 14.2 (Timeline + Outcomes) | Time blocks with topics AND expected outcomes per block |
| 3 | Learning Objectives | Layout 7 (3-col) | 3 objectives: "By the end of this session you will be able to..." — specific, measurable |
| 4 | What This IS / IS NOT | 14.4 (Contrast) | Set expectations — "This IS a hands-on lab" vs "This IS NOT a product demo" |
| 5+ | Chapter + Content | Mix of patterns | Each major topic gets a chapter divider → concept slide → hands-on exercise slide. Concept slides use `set_ph_sections` for theory. Exercise slides use bold instructions. |
| - | Demo / Exercise | Layout 0 + code blocks | Step-by-step instructions with numbered steps, SQL/Python snippets, expected output |
| - | Key Concept | 14.21 (Pyramid) or 14.20 (Hub & Spoke) | Visual explanation of the architecture or concept being taught |
| - | Practice Exercise | Layout 5 (1-col) | Bold exercise title, numbered instructions, expected outcome, time allocation |
| N-2 | Key Takeaways | Layout 7 (3-col) | 3 things to remember — practical, actionable, tied back to learning objectives |
| N-1 | Resources & Next Steps | Layout 5 (1-col) | Documentation links, Snowflake Community, support channels, follow-up session dates |
| N | Thank You | Layout 28 | |

#### Archetype 4: Project Proposal / Statement of Work (12-20 slides)

*Use when*: Proposing a project, engagement, or initiative for funding/approval.

| # | Slide | Layout/Pattern | Content to Include |
|---|-------|---------------|-------------------|
| 1 | Cover | Layout 15 (right graphic) | Project name, "Proposal", client/team name + date |
| 2 | Executive Summary | Layout 5 (1-col) | 3-4 sections: the opportunity, proposed approach, expected outcomes, investment required. Each section heading + 1-2 body lines. |
| 3 | The Case for Change | 14.7 (Stat Callout) or 14.25 (Icon Circles) | 4 quantified pain points — cost of inaction, competitive gap, operational inefficiency, risk exposure |
| 4 | Goals & Objectives | 14.3 (Split Panel) | Left: what we aim to achieve (goals with measurable targets). Right: desired business outcomes |
| 5 | Scope: IS / IS NOT | 14.4 (Contrast) | Explicit scope boundaries — critical for proposals to prevent scope creep |
| 6 | Our Approach | 14.18 (Chevron Flow) | 3-4 phase methodology with deliverables per phase |
| 7 | Detailed Roadmap | 14.19 (Milestone Timeline) or 14.24 (Arrow Ribbon) | Specific milestones with dates, owners, and dependencies |
| 8 | Architecture (if technical) | 14.20 (Hub & Spoke) or 14.23 (Hexagons) | Solution architecture overview — what technologies, how they connect |
| 9 | Team | 14.13 (Team Bios) | Key personnel with name, role, and 1-2 line credentials |
| 10 | Investment & Timeline | Layout 0 + Table | Detailed cost breakdown by phase, resource type, and timeline |
| 11 | Expected ROI | 14.25 (Icon Circles) | Quantified return metrics — savings, speed improvement, revenue impact |
| 12 | Risks & Mitigations | Layout 6 (2-col) | Top 3-4 risks with specific mitigation strategies |
| 13 | Governance & RACI | 14.17 (RACI Matrix) | Who is responsible, accountable, consulted, informed for each workstream |
| 14 | Recommended Decision | Layout 5 (1-col) | Clear recommendation with supporting rationale — "We recommend Option B because..." |
| 15 | Immediate Next Steps | Layout 7 (3-col) | 3 actions with owners and dates — make it easy to say "yes" |
| 16 | Thank You | Layout 28 | |

#### Archetype 5: Quarterly Business Review / QBR (10-15 slides)

*Use when*: Reporting progress, metrics, and plans to stakeholders on a recurring cadence.

| # | Slide | Layout/Pattern | Content to Include |
|---|-------|---------------|-------------------|
| 1 | Cover | Layout 16 (clean) | "Q1 2026 Business Review", team name, date |
| 2 | Executive Summary | Layout 5 (1-col) | 3-4 bold-keyword items: headline achievement, key challenge, strategic pivot, upcoming priority |
| 3 | Key Metrics | 14.25 (Icon Circles) or 14.7 (Stats) | 4 headline numbers — adoption rate, cost performance, SLA compliance, user satisfaction |
| 4 | Achievements This Quarter | Layout 6 (2-col) | Left: completed deliverables. Right: impact/outcomes achieved. Use `set_ph_sections` for structure |
| 5 | Maturity Progress | 14.26 (Maturity Bars) | Current vs. target state across 4-5 capability dimensions — visual progress since last QBR |
| 6 | Platform Usage Trends | Layout 0 + Table | Credit consumption, query volume, user growth, storage growth — with quarter-over-quarter comparison |
| 7 | Challenges & Lessons | 14.11 (Pros/Cons adaptation) | Left: what went well. Right: what we learned / what to improve |
| 8 | Next Quarter Priorities | 14.18 (Chevron Flow) or Layout 7 (3-col) | 3-4 key initiatives with expected outcomes and success metrics |
| 9 | Roadmap Ahead | 14.19 (Milestone Timeline) | Next 2-3 quarters with major milestones |
| 10 | Resource & Budget | Layout 0 + Table | Budget actuals vs. plan, resource allocation, forecast |
| 11 | Ask / Decision Needed | Layout 5 (1-col) | Specific requests: additional budget, headcount, timeline extension, scope change |
| 12 | Thank You | Layout 27 | |

#### Archetype 6: Product / Feature Deep Dive (10-15 slides)

*Use when*: Educating an audience about a specific Snowflake feature, capability, or product.

| # | Slide | Layout/Pattern | Content to Include |
|---|-------|---------------|-------------------|
| 1 | Cover | Layout 13 | Feature name, evocative tagline subtitle, presenter + date |
| 2 | Why This Matters | Layout 5 (1-col) | 3 sections: the problem it solves, who benefits, the scale of impact. Lead with the pain point, not the feature. |
| 3 | What It Is | 14.20 (Hub & Spoke) or 14.23 (Hexagons) | Core capability surrounded by sub-features / components. Visual ecosystem map. |
| 4 | How It Works | 14.18 (Chevron Flow) | End-to-end flow: input → processing → output. Include which Snowflake services are involved at each step. |
| 5 | Key Capabilities | Layout 7 (3-col) or 14.23 (Hexagons) | 3-6 capabilities with heading + 1-2 body lines each. Be specific — "processes 50M tokens/day" not "fast processing" |
| 6 | When to Use / When NOT to Use | 14.4 (IS / IS NOT) | Clear guidance on use cases vs. anti-patterns — architects need to know boundaries |
| 7 | Configuration & Setup | Layout 5 (1-col) | SQL commands, parameters, prerequisites. Use bold keywords for each config item. |
| 8 | Real-World Example | 14.12 (Case Study) | Challenge → Approach → Result with quantified metrics |
| 9 | Key Considerations | Layout 5 (1-col) | 4-5 bold-keyword items: performance implications, cost model, security considerations, limitations, regional availability |
| 10 | Decision Framework | 14.27 (Diamond Decision Tree) | When to use this feature vs alternatives — visual decision logic |
| 11 | Key Takeaways | Layout 7 (3-col) | 3 things to remember — practical, tied to "when would I use this" |
| 12 | Resources | Layout 5 (1-col) | Documentation links, community posts, training resources, support channels |
| 13 | Thank You | Layout 28 | |

### 20.9 Content Frameworks

Use these proven consulting frameworks to structure slide content. Pick the
framework that fits the slide's purpose.

| Framework | Structure | Best For | Example |
|-----------|----------|---------|---------|
| **SCR** (Situation-Complication-Resolution) | State the situation → Introduce the complication → Present the resolution | Executive summaries, opening slides, case for change | "Our data platform handles 10TB/day (situation). Legacy ETL pipelines break every Friday at peak load (complication). Snowflake's elastic compute and Snowpipe streaming eliminate batch failures entirely (resolution)." |
| **CAR** (Challenge-Approach-Result) | Describe the challenge → Explain the approach → Quantify the result | Case studies, proof points, QBR achievements | "Challenge: 4-hour report generation. Approach: Migrated to Snowflake with multi-cluster warehouses. Result: Reports in 23 seconds, $2.3M annual savings." |
| **MECE** (Mutually Exclusive, Collectively Exhaustive) | Break a topic into non-overlapping categories that cover everything | Architecture slides, capability maps, option comparisons | Cortex AI capabilities → LLM Functions / Search / Analyst / Fine-Tuning / Agents / Document AI (no overlap, nothing missing) |
| **Pyramid Principle** | Lead with the answer, then support with evidence | Every executive slide — state the conclusion first, then the supporting data | Title: "CROSS-REGION INFERENCE DELIVERS 3X MODEL ACCESS". Body: supporting evidence for why. |
| **5W1H** (What, Why, Who, When, Where, How) | Answer all six questions about a topic | Feature deep-dives, project proposals, initiative overviews | What is Cortex AI? Why does it matter? Who benefits? When to use it? Where does it run? How to enable it? |
| **Before/After** | Contrast current state with future state | Transformation slides, value propositions, case for change | "Before: 7 siloed data warehouses, 4-hour reports. After: Single Snowflake platform, 23-second reports." |

**Rule**: Every content slide should follow one of these frameworks. If you can't identify which framework a slide uses, the content is probably unfocused.

### 20.10 Snowflake Content Bank

Common themes and talking points that recur across Snowflake decks. Use these
as building blocks when generating content — adapt to the specific context.

#### Platform Value Propositions

| Theme | Key Points | Quantifiable Claims |
|-------|-----------|-------------------|
| **Elastic Performance** | Auto-scaling compute separates storage from compute; multi-cluster warehouses handle concurrency spikes without manual intervention | "Scale from 1 to 128 clusters in seconds", "Zero contention between workloads" |
| **Near-Zero Administration** | No indexing, no tuning, no vacuuming, no partitioning; automatic micro-partitioning and query optimisation | "80% reduction in DBA overhead", "Zero maintenance windows" |
| **Unified Data Platform** | Structured, semi-structured, and unstructured data in one platform; SQL, Python, Java, Scala all supported | "Single platform for all data workloads", "Native JSON, Parquet, Avro, ORC support" |
| **Secure by Design** | End-to-end encryption (AES-256), dynamic data masking, row-level security, RBAC, network policies, Tri-Secret Secure | "99.9% SLA", "SOC 2 Type II, HIPAA, PCI DSS, FedRAMP compliant" |
| **Cost Efficiency** | Per-second billing, auto-suspend, resource monitors, per-query cost attribution | "Pay only for compute you use", "Auto-suspend after 5 minutes of inactivity" |
| **Data Sharing & Marketplace** | Zero-copy data sharing, Snowflake Marketplace, data clean rooms | "Share live data without moving it", "2,000+ datasets in Marketplace" |

#### Cortex AI Talking Points

| Capability | What It Does | When to Recommend | Key Metric |
|-----------|-------------|------------------|------------|
| **Cortex AI Functions** | LLM inference (COMPLETE, SUMMARIZE, TRANSLATE, SENTIMENT, CLASSIFY, EXTRACT_ANSWER) directly in SQL | When users need AI on structured/semi-structured data without ML infrastructure | "50+ LLM models available", "No data leaves Snowflake perimeter" |
| **Cortex Search** | Hybrid semantic + keyword search with real-time index refresh | When users need RAG, document search, or knowledge base retrieval | "Sub-second search over millions of documents" |
| **Cortex Analyst** | Natural language to SQL for business intelligence — conversational analytics | When analysts need self-service BI without writing SQL | "Natural language queries on your semantic model" |
| **Cortex Fine-Tuning** | Custom model training on your data within Snowflake's security perimeter | When off-the-shelf models don't meet domain-specific accuracy needs | "Fine-tune in hours, not weeks" |
| **Cortex Agents** | Orchestrated multi-tool AI agents that combine Analyst + Search + custom tools | When complex questions require multiple data sources and reasoning steps | "Multi-step reasoning across structured and unstructured data" |
| **Document AI** | Extract structured data from PDFs, invoices, contracts using pre-trained models | When processing unstructured documents at scale | "Process thousands of documents per hour" |
| **Cross-Region Inference** | Route AI requests to any region where the model is available | When latest models aren't available in the user's home region | "Access any model from any region, no egress charges" |

#### Architecture Talking Points

| Topic | Key Points |
|-------|-----------|
| **Data Ingestion** | Snowpipe (continuous), Snowpipe Streaming (sub-second), COPY INTO (batch), Kafka connector, external stages (S3, Azure Blob, GCS) |
| **Transformation** | Dynamic Tables (declarative pipelines), Tasks + Streams (CDC), Stored Procedures (Python/SQL), dbt integration |
| **Serving & Consumption** | Snowflake SQL, Snowpark (Python/Java/Scala), Streamlit in Snowflake, REST API, JDBC/ODBC, Partner connectors (Tableau, Power BI, Looker) |
| **Governance** | Object tagging, access history, data lineage, dynamic masking, row access policies, network policies, Horizon (data governance suite) |
| **Cost Management** | Resource monitors, warehouse auto-suspend, query acceleration, search optimisation, serverless tasks, per-query attribution |
| **Multi-Cloud** | Available on AWS, Azure, GCP across 30+ regions; cross-cloud replication; Snowgrid for global data mesh |

#### Common Metrics for Proof Points

Use these when you need to quantify impact in stat callouts, case studies, or ROI slides:

| Category | Typical Metrics |
|----------|----------------|
| **Performance** | Query speed improvement (Nx faster), report generation time (hours → seconds), concurrency (simultaneous users) |
| **Cost** | Annual savings ($XM), infrastructure cost reduction (X%), licence consolidation, DBA time freed |
| **Adoption** | Self-service users (#), departments onboarded (#), queries per day (#), active dashboards (#) |
| **Efficiency** | Time-to-insight reduction (X%), pipeline development time (weeks → days), manual tasks automated (#) |
| **Governance** | Compliance certifications, audit coverage (%), data classified (%), masking policies applied (#) |
| **Scale** | Data volume (TB/PB), daily ingestion rate, concurrent workloads, global regions served |

---

