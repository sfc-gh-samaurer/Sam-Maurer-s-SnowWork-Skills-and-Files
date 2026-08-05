#!/usr/bin/env python3
"""
Fixed-fee PS engagement proposal — generalized 27-slide builder.

WORKING EXAMPLE WITH PLACEHOLDER CONTENT. It runs as-is and produces a
structurally complete, brand-correct deck. Every string in the CONTENT section is
a placeholder: replace it. Do not ship the example text.

Read `references/fixed-fee-engagement-proposal.md` before editing. It explains
why the deck is shaped this way — the committed-hours invariant, the two-tier
milestone model, and the honest-TBD doctrine.

Use this variant when the FEE IS PINNED BEFORE THE SCOPE IS KNOWN (capacity
conversion, investment attach, pre-agreed budget). For bottom-up pricing, use
`references/ps-engagement-proposal.md` instead.

    python3 build_fixed_fee_proposal.py

Editing rules — read these first
    1. The per-role column totals in EFFORT are load-bearing. Redistribute hours
       ACROSS workstreams freely; never change the column totals, or the fixed
       fee silently breaks. The asserts at the bottom enforce this.
    2. Acceptance gates (M1..Mn) and billing milestones (BM1..BMn) are separate
       tracks. Do not collapse them.
    3. Never invent a workstream to absorb budget. Put genuine unknowns on the
       Open Scope Items slide with a named closing gate.
    4. Tables are native table objects; bullets are native bullets. Both are
       handled for you by `proposal_helpers` — use the helpers.
    5. After saving, read the rendered-height output. A flagged slide means the
       table grew past the footer; trim content or shrink the font.

Slide map
     1 Cover                        15 Engagement RACI
     2 Proposal Content             16 Assumptions and Exclusions
     3 Executive Summary            17 Resource Effort and Contingency  *
     4 Current State / Target *     18 Risks and Mitigations
     5-7 Workstream Scope 1-3/3     19 Pricing
     8 Engagement Deliverables      20 Milestone Payment Schedule       *
     9 Project Timeline (Gantt) *   21 Next Steps
    10 Milestones & Gates           22 Appendix divider
    11 Open Scope Items         *   23-26 Appendix (engagement-specific)
    12 Customer Dependencies    *   27 Thank You
    13-14 Roles & Responsibilities        (* = specific to this variant)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proposal_helpers import *   # noqa: F401,F403

# ═════════════════════════════════════════════════════════════════════════════
# CONFIG — the pinned commercial frame. Set these first.
# ═════════════════════════════════════════════════════════════════════════════
CUSTOMER      = "Example Corp"            # customer short name, used in prose
CUSTOMER_CAPS = "EXAMPLE CORP"            # cover / callout bars
ENGAGEMENT    = "SOURCE SYSTEM REPLICATION"
SUBTITLE      = "Change Data Capture Ingestion and Historical Data Model"
DECK_DATE     = "Month Year"
PRESENTERS    = [("Presenter Name", "Principal Services Solution Manager"),
                 ("Presenter Name", "Sr. Manager, Solutions Architecture")]

FEE           = 220_000        # the pinned fixed fee
DURATION_WKS  = 12             # indicative; the fee is based on hours, not weeks
CONTINGENCY   = 0.25           # 25% is the working default
FUNDING       = "conversion of unused customer capacity"

# Role rates and the contingency split. Committed = base + contingency.
RATE_SA, RATE_C, RATE_PM = 335, 305, 260
CONT_SA, CONT_C, CONT_PM = 40, 88, 14

OUTPUT = ("~/Google Drive/My Drive/"
          f"{CUSTOMER.replace(' ', '_')}_Proposal.pptx")

# ═════════════════════════════════════════════════════════════════════════════
# CONTENT — replace all of this. Structure is the deliverable; text is example.
# ═════════════════════════════════════════════════════════════════════════════
TBD = "TBD"

AGENDA = [
    "Executive Summary and Engagement Objectives",
    "Current State and Target State",
    "Workstream Scope Summary",
    "Engagement Deliverables",
    "Project Timeline",
    "Milestones and Acceptance Gates",
    "Open Scope Items and Pending Inputs",
    "Customer Dependencies and Commitments",
    f"Snowflake / {CUSTOMER} Roles and Responsibilities",
    "Engagement RACI",
    "Assumptions and Exclusions",
    "Resource Effort and Contingency",
    "Risks, Pricing and Milestone Payment Schedule",
    "Next Steps",
]

# Two prose panels. Left = the problem in the customer's own terms. Right = what
# we will do about it. Two paragraphs each; do not exceed that.
PROBLEM = [
    "State the customer's current situation factually and in their language. "
    "Name the system, the cadence, and the specific limitation that creates the "
    "business pain. Do not editorialise and do not pitch here.",
    "Add the consequence: what the business cannot do today, who is blocked, and "
    "what leadership has asked for. This paragraph earns the scope that follows.",
]
SUMMARY = [
    "State what Snowflake Professional Services will deliver, in one sentence, "
    "with the concrete nouns: the source, the mechanism, the target model. Avoid "
    "adjectives; the specificity is what reads as credible.",
    "Then state the second-order outcome — how the result is consumed, and how "
    "the pattern is made repeatable so the customer can extend it unaided.",
]

# 6 objectives, each with a measurable success criterion. If a criterion cannot
# be measured, it is not an objective — cut it.
OBJECTIVES = [
    ("01", "Land the source data in Snowflake",
     "All in-scope source tables replicating continuously into Snowflake."),
    ("02", "Prove the pipeline under real change volume",
     "Structured test suite passed across change, edge-case, load and recovery."),
    ("03", "Preserve full attribute history",
     "Historical model built from the change journal; every change is retained."),
    ("04", "Meet the agreed freshness target",
     "End-to-end latency from source commit to Snowflake within the target."),
    ("05", "Deliver a governed consumption layer",
     "Semantic view published as a discoverable Snowflake data product."),
    ("06", "Make the pattern repeatable",
     "Template proven on a second domain; customer onboards the rest unaided."),
]

# (today, target) — one row per dimension the engagement actually changes.
# Today reads grey/regular, Target reads dark/bold. The asymmetry persuades.
CURRENT_TARGET = [
    ("Source system of record, on-premises",
     "Snowflake as the governed consumption layer"),
    ("Single batch job, once per day",
     "Continuous change data capture to the freshness target"),
    ("Current state only — no change history retained",
     "Historical model built from the journal of every captured change"),
    ("Hard overwrite on update; no delete tracking",
     "Logical deletion via end-dating, no physical row loss"),
    ("New source attributes require a manual pipeline change",
     "Schema-drift tolerant landing and history layers"),
    ("Source tables joined into a hand-built flattened view",
     "Equivalent flattened Snowflake view over the history model"),
    ("Single BI extract; no direct Snowflake access",
     "Governed semantic view for BI, ad-hoc SQL and natural-language query"),
    ("Every new domain is a bespoke build",
     "A templatized pattern, proven once more and reusable by the customer"),
]

# (num, name, activities, phase, base_hrs_as_string)
# Base hrs here MUST equal the row total in EFFORT below. Tag placeholder scope
# with [SCOPE TBD] in the name and remove the tag the moment it closes.
WS = [
    ("1", "Project Setup & Kickoff", [
        "Establish communication channels, delivery cadence, and project governance",
        "Conduct kickoff; confirm goals, success criteria, and acceptance criteria",
        "Take handover of validated source connectivity and security configuration",
        "Provision Snowflake databases, schemas, roles, and warehouses",
    ], "Phase 0", "28"),
    ("2", "Discovery & Target-State Design", [
        "Review DDL, ERD, relationships and data samples for all in-scope tables",
        "Confirm history granularity: which columns are versioned vs. overwritten",
        "Design the journal-sourced history model and presentation-layer contract",
        "Recommend and confirm the transformation toolset; assess topology and cost",
        "Define schema-drift handling, delete semantics, and reference-data refresh",
    ], "Phase 1", "76"),
    ("3", "Change Data Capture Ingestion & Landing Layer", [
        "Configure the source CDC connector against validated private connectivity",
        "Define the replication object list and primary keys for in-scope tables",
        "Establish the journal and merged destination tables maintained in Snowflake",
        "Implement schema-drift handling so new attributes propagate without rebuild",
        "Instrument reconciliation counts, data-quality checks, and freshness telemetry",
    ], "Phase 2", "68"),
    ("4", "CDC Testing, Validation & Connector Hardening", [
        "Execute a structured test suite across insert, update, delete and bulk change",
        "Validate wide-table, data-type, LOB and character-set edge cases",
        "Measure sustained throughput, end-to-end latency and credit consumption",
        "Exercise failure and recovery paths: restart, replication lag, catch-up",
        "Triage and escalate connector defects to the Snowflake engineering team",
    ], "Phase 2", "80"),
    ("5", "Historical Model from the Change Journal", [
        "Build the history model from the journal tables, which retain every change",
        "Implement effective-from / effective-to dating, current flags, surrogate keys",
        "Implement logical deletion via end-dating rather than physical delete",
        "Build reference-data handling and the flattened presentation view",
        "Add tests for versioning correctness, no-gap/no-overlap dating and integrity",
    ], "Phase 2", "102"),
    ("6", "Orchestration & Freshness Enablement", [
        "Implement the refresh pattern selected in Phase 1 across all layers",
        "Tune scheduling, warehouse sizing and incremental processing to the target",
        "Configure retry logic, failure alerting and pipeline observability",
    ], "Phase 2", "48"),
    ("7", "Semantic View & Consumption Enablement", [
        "Build a Snowflake semantic view over the history and presentation layers",
        "Define logical tables, relationships, dimensions, metrics and synonyms",
        "Publish the domain as a governed, discoverable Snowflake data product",
    ], "Phase 3", "64"),
    ("8", "Reusable Pattern & Second-Domain Onboarding", [
        "Templatize the ingestion, journal-to-history and semantic-view pattern",
        "Apply the template to a second domain selected by the customer in Discovery",
        "Document the runbook so the customer can onboard further domains unaided",
    ], "Phase 3", "68"),
    ("9", "Validation, UAT & Cutover", [
        "Reconcile Snowflake output against the current source-system view",
        "Support customer UAT against the agreed acceptance criteria; resolve findings",
        "Monitor the first production refresh cycles after cutover",
    ], "Phase 3", "18"),
    ("10", "Knowledge Transfer & Project Closure", [
        "Deliver architecture documentation, data dictionary and operational runbooks",
        "Up to 3 knowledge transfer sessions across ingestion, history and consumption",
        "Hand over the reusable pattern for the remaining domains",
    ], "Phase 4", "18"),
]

# One deliverable per workstream keeps the two slides reconcilable.
DELIVERABLES = [
    ("Kickoff Deck · Access Checklist · Snowflake Environment Scaffold",
     "Kickoff alignment, connectivity handover, and provisioned Snowflake objects."),
    ("Source Data Assessment · Change-Tracking Specification",
     "Reviewed DDL/ERD, with the agreed list of versioned vs. overwritten columns."),
    ("Target Architecture Design · Transformation Toolset Recommendation",
     "Journal-sourced history design, presentation layer, and recommended pattern."),
    ("CDC Ingestion & Landing Layer",
     "Configured replication, journal and destination tables, schema-drift handling."),
    ("Test Plan · Validation Evidence · Defect Log",
     "Executed suite across change, edge-case, load and recovery, with escalations."),
    ("Historical Model · Flattened Presentation View",
     "Versioned entity and attribute history with end-dating, plus the flat view."),
    ("Orchestration & Alerting Configuration",
     "Refresh orchestration tuned to the freshness target, with retries and alerts."),
    ("Semantic View · Data Product Publication",
     "Semantic view with dimensions, metrics and synonyms, published and governed."),
    ("Reusable Onboarding Template · Second Domain Delivered",
     "Templatized pattern applied to a second customer-selected domain."),
    ("Reconciliation & UAT Sign-off · Documentation · Runbooks · KT",
     "Reconciliation, UAT sign-off, data dictionary, runbooks and up to 3 sessions."),
]

# (row label, phase tag, start week, end week, bar fill) — last row is PM.
GANTT = [
    ("WS1 · Setup & Kickoff",             "P0",  1,  1, DK2),
    ("WS2 · Discovery & Design",          "P1",  2,  3, SF_BLUE),
    ("WS3 · CDC Ingestion & Landing",     "P2",  3,  5, DK2),
    ("WS4 · Testing & Hardening",         "P2",  5,  7, DK2),
    ("WS5 · History from Journal",        "P2",  6,  9, DK2),
    ("WS6 · Orchestration & Freshness",   "P2",  8, 10, DK2),
    ("WS7 · Semantic View & Consumption", "P3",  9, 11, SF_BLUE),
    ("WS8 · Pattern & Second Domain",     "P3",  9, 11, SF_BLUE),
    ("WS9 · Validation, UAT & Cutover",   "P3", 11, 12, SF_BLUE),
    ("WS10 · Knowledge Transfer & Close", "P4", 12, 12, DK2),
    ("Program Management",                "—",   1, 12, TEAL),
]

# (gate number, GANTT row index that owns it, week, short label)
GATE_MARKS = [
    (1, 0,  1, "Kickoff & environment ready"),
    (2, 1,  3, "Design & change-tracking sign-off"),
    (3, 2,  5, "CDC ingestion configured & flowing"),
    (4, 3,  7, "Validation & hardening accepted"),
    (5, 4,  9, "Historical model complete"),
    (6, 5, 10, "Freshness target demonstrated"),
    (7, 7, 11, "Semantic view & second domain accepted"),
    (8, 9, 12, "Validation, UAT sign-off & closure"),
]

# (id, name, target, key deliverables, acceptance gate)
# The gate column must be objectively testable — "customer approves X", never
# "work is complete". These roll up into the billing milestones.
GATES = [
    ("M1", "Kickoff & Environment Ready", "End W1",
     "Kickoff deck; access checklist; Snowflake environment scaffold",
     "Connectivity handover complete; named SMEs and cadence confirmed"),
    ("M2", "Design & Change-Tracking Sign-off", "End W3",
     "Source assessment; change-tracking spec; target architecture; toolset",
     "Customer approves versioning rules, layer design and transformation toolset"),
    ("M3", "CDC Ingestion Configured & Flowing", "End W5",
     "Connector configuration; journal and destination tables; landing layer",
     "Change data observed landing in Snowflake for all in-scope tables"),
    ("M4", "Validation & Hardening Accepted", "End W7",
     "Test plan; validation evidence across change, edge-case, load, recovery",
     "Test suite passes; any connector defects logged with an agreed disposition"),
    ("M5", "Historical Model Complete", "End W9",
     "Journal-sourced history model; flattened view; history test results",
     "History tests pass; flattened view reproduces the current source interface"),
    ("M6", "Freshness Target Demonstrated", "End W10",
     "Orchestration configuration; alerting; observability",
     "End-to-end latency demonstrated within the agreed freshness target"),
    ("M7", "Semantic View & Second Domain Accepted", "End W11",
     "Semantic view; data product publication; template; second domain delivered",
     "Semantic view returns validated results; second domain lands via template"),
    ("M8", "Validation, UAT Sign-off & Closure", "End W12",
     "Reconciliation report; UAT sign-off; documentation, runbooks, KT sessions",
     "Customer confirms reconciliation, signs off UAT, accepts final deliverables"),
]

# The slide that makes a fixed fee credible under uncertainty. One card per
# GENUINE unknown. Each card: lines ending ": TBD", plus a line naming where it
# closes. Never fabricate scope to fill the fee — catalogue the gap instead.
OPEN_ITEMS = [
    ("Second Domain Selection", DK2, [
        "Which remaining domain is onboarded in WS8: TBD",
        "Selected by the customer during Discovery and confirmed at the M2 gate",
        "WS8 is sized for a domain of comparable scale to the primary domain",
        "A materially larger domain is handled through change control",
    ]),
    ("Historical Backfill", SF_BLUE, [
        "Whether history exists in the source to migrate: TBD",
        "Depth of history to load (full vs. from a cut-over date): TBD",
        "Backfill volume and reload window: TBD",
        "Current baseline assumes go-forward change capture only",
    ]),
    ("Transformation Tooling", SF_BLUE, [
        "The customer has stated no preference and asked for our recommendation",
        "Candidates: Dynamic Tables, Streams + Tasks, dbt Projects on Snowflake",
        "All three read from the CDC journal tables",
        "Selection made and approved at the M2 gate; comparison is in the Appendix",
    ]),
    ("Consumption Surfaces", DK2, [
        "One semantic view over the primary domain is in scope (WS7)",
        "Named consuming personas and report inventory: TBD",
        "Repointing existing BI reports is not in the baseline",
        "A Streamlit or Snowflake Intelligence surface can be added via change control",
    ]),
]
PENDING_INPUTS = ("DDL, ERD and relationship diagrams, and data samples for all "
                  "in-scope tables  ·  written acceptance criteria")

# (num, commitment, owner, required by, impact if delayed)
# The Impact column is the point. Name a real consequence, never "may cause
# delays" — this is the basis for a schedule-relief conversation.
DEPENDENCIES = [
    ("1", "Provide DDL, ERD, relationships and data samples for all in-scope tables",
     "Data Platform Owner", "Before Phase 1", "Blocks design; extends Discovery and risks M2"),
    ("2", "Provide written acceptance criteria for the engagement",
     "Data Platform Owner", "Before kickoff", "Ambiguous acceptance; rework risk at UAT"),
    ("3", "Maintain validated private connectivity and Snowflake access",
     "Platform / Network Admin", "Before kickoff", "Blocks ingestion work; delays all phases"),
    ("4", "Confirm source CDC prerequisites and licensing remain in place",
     "Source System DBA", "Before Phase 2", "Halts CDC ingestion entirely"),
    ("5", "Provide DBA support for CDC test scenarios and defect triage",
     "Source System DBA", "Phase 2 (WS4)", "Extends validation; delays M4"),
    ("6", "Approve change-tracking rules and transformation toolset",
     "Data Platform Owner", "M2 gate", "Holds the start of build"),
    ("7", "Select the second domain for template onboarding",
     "Data Platform Owner", "M2 gate", "WS8 cannot start; scope reverts to one domain"),
    ("8", "Define semantic view metrics and validate reconciliation at UAT",
     "Business / BI SME", "Phase 3 (M7–M8)", "Blocks semantic view acceptance and UAT"),
]

# Committed hours per role are filled in automatically from EFFORT.
SF_ROLES = [
    ("Sr. Solution Architect", "sa", [
        "Owns the target-state architecture and the historical model design",
        "Makes and defends the transformation toolset recommendation",
        "Owns the test strategy and the escalation path into Snowflake engineering",
        "Designs the semantic view and reusable template; leads knowledge transfer",
    ]),
    ("Consultant / Data Engineer", "c", [
        "Primary hands-on build of the landing, history and presentation layers",
        "Configures CDC ingestion and schema drift; executes the test suite",
        "Builds orchestration, alerting, observability and the semantic view",
        "Applies the template to the second domain and supports UAT",
    ]),
    ("Project Manager (SDM)", "pm", [
        "Owns project planning, scheduling and delivery governance",
        "Coordinates both teams; tracks scope, risk, issues and status",
        "Manages change control and serves as the primary escalation path",
    ]),
]

CUST_ROLES = [
    ("Executive Sponsor",
     "Provide executive alignment and escalation support; remove organizational "
     "blockers and reinforce prioritization of the programme.", "1–2 hrs/week"),
    ("Data Platform Owner",
     "Primary engagement counterpart. Owns the source domain, approves "
     "change-tracking rules and toolset, and provides acceptance criteria.", "4–6 hrs/week"),
    ("Source System DBA / Owner",
     "Explain the source data model, confirm CDC prerequisites and licensing, "
     "and support source-side connectivity and change freeze.", "3–5 hrs/week"),
    ("Platform / Network Administrator",
     "Provision Snowflake and connectivity access and enable source-side network "
     "reachability.", "As needed"),
    ("Business / Reporting SME",
     "Validate that replicated attributes and history reconcile to current "
     "outputs, and confirm the flattened view meets reporting needs.", "2–4 hrs/week"),
    ("Analytics / BI Stakeholder",
     "Represent consuming teams, confirm consumption scope, participate in UAT, "
     "and confirm acceptance.", "As needed"),
]

# (activity, Snowflake letter, Customer letter, assumption)
RACI = [
    ("Environment access & connectivity handover", "C", "R",
     "Private connectivity already validated and maintained"),
    ("Source data model walkthrough", "C", "R",
     "DDL, ERD and samples supplied for all in-scope tables"),
    ("Target architecture & history model design", "R", "A",
     "Customer approves versioning rules at the M2 gate"),
    ("Transformation toolset selection", "R", "A",
     "Snowflake recommends; customer approves"),
    ("CDC ingestion configuration", "R", "C",
     "Off-the-shelf connector on validated connectivity"),
    ("Testing & connector defect triage", "R", "C",
     "Escalated to Snowflake product engineering as needed"),
    ("History model & pipeline build", "R", "I",
     "Built from the CDC journal tables"),
    ("Semantic view definition & validation", "R", "A",
     "Customer defines metrics and validates results"),
    ("Second domain selection & onboarding", "C", "A",
     "Customer selects the domain; Snowflake applies the template"),
    ("Reconciliation, UAT & closure", "C", "A",
     "Customer validates against current source outputs"),
]

ASSUMPTIONS = [
    ("Customer Responsibilities", DK2, [
        "Validated private connectivity and Snowflake access maintained through delivery",
        "DDL, ERD, relationships and data samples supplied for all in-scope tables",
        "Named SMEs, including a source-system DBA, committed to a weekly cadence",
        "Deliverables reviewed and signed off within 5 business days at each gate",
    ]),
    ("Technical Assumptions", SF_BLUE, [
        "Primary scope is the single named domain agreed at proposal",
        "Source CDC prerequisites and customer-provided licensing remain valid",
        "The source model remains stable through validation; changes go to change control",
        "The freshness figure is a design target, not a contractual SLA",
    ]),
    ("Scope Boundaries", SF_BLUE, [
        "Snowflake output delivers functional parity with the current source view",
        "Go-forward change capture only unless historical backfill is confirmed in scope",
        "One semantic view over the primary domain; one second domain via the template",
        "Up to 3 knowledge transfer sessions",
    ]),
    ("Engagement Exclusions", DK2, [
        "Master data management, entity resolution and a full conformed-dimension model",
        "Source domains beyond the primary domain and the one second domain in WS8",
        "Rebuild or repoint of existing BI, self-service or legacy reporting processes",
        "Discovery of shadow consumers; infrastructure and licence procurement",
    ]),
]

# (num, name, phase, sr_sa, consultant, pm)
# INVARIANT: the per-role COLUMN TOTALS are what price the deck. Redistribute
# across workstreams freely; never change the column totals. Asserts enforce it.
EFFORT = [
    ("1",  "Project Setup & Kickoff",              "0",  8, 16, 4),
    ("2",  "Discovery & Target-State Design",      "1", 28, 40, 8),
    ("3",  "CDC Ingestion & Landing Layer",        "2", 18, 44, 6),
    ("4",  "Testing, Validation & Hardening",      "2", 22, 52, 6),
    ("5",  "Historical Model from Journal",        "2", 26, 68, 8),
    ("6",  "Orchestration & Freshness",            "2", 14, 30, 4),
    ("7",  "Semantic View & Consumption",          "3", 18, 40, 6),
    ("8",  "Reusable Pattern & Second Domain",     "3", 18, 46, 4),
    ("9",  "Validation, UAT & Cutover",            "3",  4,  8, 6),
    ("10", "Knowledge Transfer & Closure",         "4",  4,  8, 6),
]
EXPECT_SA, EXPECT_C, EXPECT_PM = 160, 352, 58   # ← the load-bearing constraint

CONTINGENCY_COVERS = ("connector defect resolution, reconciliation rework and "
                      "second-domain variance")

# (title, severity, colour, risk, mitigation)
# Internal candor is TRANSLATED here, never reproduced. If a specialist says
# "don't soften this externally" about product maturity, represent the concern as
# scope and rigour on our side — never as a caveat about the product.
RISKS = [
    ("Source Connector Defects", "HIGH", SF_RED,
     "Risk: the CDC connector may encounter defects against this specific schema — "
     "wide tables, unusual data types or character sets are known sensitivities.",
     "Mitigation: dedicated validation workstream (WS4) with a structured test suite, "
     "plus a direct escalation path into Snowflake product engineering; covered by "
     "the delivery contingency."),
    ("Cross-Region Cost & Latency", "MEDIUM", SF_AMBER,
     "Risk: the Snowflake account and the source network sit in different regions. "
     "CDC is a chatty protocol, so egress cost and replication latency could exceed "
     "expectations.",
     "Mitigation: cost and latency measured early in WS4 against real change volume; "
     "an in-region account with data sharing is assessed as an alternative topology "
     "at the M2 gate."),
    ("Source Documentation Delay", "HIGH", SF_RED,
     "Risk: DDL, ERD and data samples arrive late, blocking design.",
     "Mitigation: named as a pre-kickoff dependency with a defined owner and impact "
     "statement."),
    ("CDC Licensing & Prerequisites", "MEDIUM", SF_AMBER,
     "Risk: customer-provided source licensing or source-side prerequisites lapse or "
     "prove insufficient.",
     "Mitigation: the customer confirms licensing and prerequisites remain in place "
     "before Phase 2 build."),
    ("Freshness Target Not Met", "MEDIUM", SF_AMBER,
     "Risk: end-to-end latency exceeds the target under production change volume.",
     "Mitigation: treated as a design target; incremental processing, warehouse "
     "tuning and observability built in and measured before cutover."),
    ("Undefined Downstream Value Case", "MEDIUM", SF_AMBER,
     "Risk: history in isolation is a point solution; without named consumers the "
     "business value is hard to demonstrate to leadership.",
     "Mitigation: semantic view and second-domain onboarding make the pattern visible "
     "and reusable; consuming personas confirmed during Discovery."),
]

FEE_COVERS = [
    "End-to-end delivery of the primary domain from the source system into Snowflake "
    "— CDC ingestion, landing layer, journal-sourced historical model, and "
    "orchestration to the agreed freshness target",
    "A dedicated testing and validation workstream covering change, edge-case, load "
    "and recovery scenarios, with escalation into Snowflake product engineering",
    "A governed semantic view over the primary domain, plus a reusable onboarding "
    "template proven on a second customer-selected domain",
    "{base} base hours plus a {pct}% delivery contingency ({commit} committed hours) "
    "across the Sr. Solution Architect, Consultant and Project Manager roles, with "
    "all documentation and runbooks",
]

# (label, name, phases/WS, deliverables accepted, gates, hrs, fee, pct)
# 4 is the right number. Contiguous gate AND workstream ranges — never interleave.
# Allocate pro-rata to committed hours, then hand-tune to round thousands that
# sum EXACTLY to the fee. Keep BM1 under ~25%; largest BM at the end.
BILLING = [
    ("BM1", "Design Accepted", "Phase 0–1  ·  WS1–2",
     "Kickoff and environment scaffold  ·  source data assessment  ·  "
     "change-tracking specification  ·  target architecture and toolset recommendation",
     "M1–M2", 130, 40_000, "18.2%"),
    ("BM2", "Ingestion & Validation Accepted", "Phase 2  ·  WS3–4",
     "CDC connector configured  ·  journal and landing layer with schema-drift "
     "handling  ·  executed test suite, validation evidence and defect log",
     "M3–M4", 185, 57_000, "25.9%"),
    ("BM3", "History Model & Freshness Accepted", "Phase 2  ·  WS5–6",
     "Journal-sourced historical model  ·  flattened presentation view  ·  "
     "orchestration, alerting and observability against the freshness target",
     "M5–M6", 187, 58_000, "26.4%"),
    ("BM4", "Consumption, Second Domain & Closure", "Phase 3–4  ·  WS7–10",
     "Semantic view and data product  ·  reusable template with a second domain "
     "onboarded  ·  reconciliation, UAT sign-off, documentation, runbooks and KT",
     "M7–M8", 210, 65_000, "29.5%"),
]

NEXT_STEPS = [
    "Customer provides DDL, ERD, samples and written acceptance criteria",
    "Confirm the second domain candidate for template onboarding",
    "Align on CDC topology: retain cross-region or assess an in-region account",
    "Sign-off on scope, approach and pricing",
    "Execute Order Form and SOW",
    "Initiate staffing of the Snowflake delivery team",
    "Confirm named customer counterparts, including DBA support",
    "Project kickoff",
]

# Appendix — architecture flow. 6 boxes fit the 9.10" content width at fw=1.408.
ARCH_FLOW = [
    ("SOURCE SYSTEM",   "On-prem source\nin-scope tables",        DK2),
    ("CDC CONNECTOR",   "Managed connector\nprivate connectivity", SF_BLUE),
    ("JOURNAL TABLE",   "Append-only\nevery change captured",      DK2),
    ("HISTORY MODEL",   "Versioned entity\n& attribute history",   SF_BLUE),
    ("PRESENTATION",    "Flattened view\ndata product",            DK2),
    ("SEMANTIC VIEW",   "Dimensions, metrics\n& synonyms",         SF_BLUE),
]
ARCH_BANDS = [
    ("ORCHESTRATION — transformation pattern selected at M2 (Dynamic Tables / "
     "Streams + Tasks / dbt Projects)  ·  freshness target  ·  retry logic  ·  "
     "failure alerting", DK2),
    ("HISTORY SEMANTICS — built from the journal, not the merged table  ·  update "
     "opens a new dated record  ·  delete end-dates logically  ·  new attributes "
     "absorbed without rebuild", SF_BLUE),
    ("CONSUMPTION — semantic view for BI and natural-language query  ·  ad-hoc SQL "
     "·  AI/ML models  ·  reusable for the next domain", BODY_GREY),
]

# Appendix — the mechanics slide. Explains WHY history is built where it is.
# This is the slide that proves you understand the product, not just the pattern.
MECHANICS = [
    ("Journal Table", DK2, [
        "The connector uses Snowflake Streaming to append every captured change",
        "Each insert, update and delete from the source stream lands as its own row",
        "The complete change chronology is retained — nothing is overwritten",
        "This is the correct source for the historical model",
    ]),
    ("Merged Destination Table", SF_BLUE, [
        "The connector then applies a primary-key merge over the journal",
        "The result mirrors current state in the source as closely as possible",
        "Intermediate states between refreshes are collapsed away",
        "Useful for current-state parity, but insufficient for history",
    ]),
]
MECHANICS_IMPL = [
    "The historical model reads the journal table, so no change is lost between "
    "refresh cycles — including multiple updates to the same record in one interval.",
    "Change history begins accumulating from the moment CDC is enabled. Any history "
    "predating cutover is a separate backfill question, listed as an open scope item.",
    "The merged destination table is retained and used to reconcile current-state "
    "parity against the existing source view during UAT.",
    "This journal-to-history transformation is the reusable component templatized in "
    "WS8 and applied to the second domain.",
]

# Appendix — data model summary. Keep the TBD column honest.
DATA_MODEL = [
    ("Entity / Grain", "2", "Define the grain of the domain — the primary entity",
     "Full historical versioning", TBD),
    ("Satellite / Attribute", "7", "Groups of business attributes joined to the entity",
     "Full historical versioning", TBD),
    ("Lookup / Reference", "13", "Relatively static reference and definition tables",
     "Refresh strategy to be confirmed — likely full refresh, not CDC", TBD),
]
MODEL_KNOWN = [
    "Table count and approximate volume confirmed on the scoping call",
    "Attributes only — no transactional data in scope",
    "Tables joined into a flattened view that is the current interface",
    "Attributes change infrequently, not daily",
]
MODEL_UNKNOWN = [
    "Column-level detail, keys and data types: TBD",
    "Which columns are versioned vs. overwritten: TBD",
    "Observed change rate per table: TBD",
    "Historical data available to backfill: TBD",
]

# Appendix — the decision framework for a deferred choice. Use this pattern
# whenever the customer has asked for a recommendation you cannot yet make.
OPTIONS = [
    ("Dynamic Tables",
     "Declarative incremental refresh over the journal table against a target lag. "
     "Snowflake manages the refresh graph.",
     "Lowest operational overhead; freshness expressed directly as target lag",
     "History patterns need careful modelling; some constructs are not "
     "incrementally refreshable"),
    ("Streams + Tasks",
     "Explicit change capture on the journal table with procedural merge logic into "
     "the history layer.",
     "Full control over merge semantics, end-dating and drift handling",
     "More code to own and operate; scheduling and dependencies are manual"),
    ("dbt Projects on Snowflake",
     "dbt snapshots and models over the journal table, executed natively inside "
     "Snowflake.",
     "Built-in snapshot pattern, testing and lineage; familiar engineering workflow",
     "Introduces a modelling framework and CI/CD practice the customer must adopt"),
]
OPTIONS_NOTE = (
    "RECOMMENDATION: TBD.  The selection depends on the column-level change-tracking "
    "rules and observed change rates, which require the DDL, ERD and data samples. We "
    "will present a recommendation with rationale during Discovery and confirm it at "
    "the M2 acceptance gate before any build begins. All three patterns are "
    "Snowflake-native, read from the CDC journal tables, and can meet the freshness "
    "target.")


# ═════════════════════════════════════════════════════════════════════════════
# BUILD — geometry is tuned to the 10 x 5.625" canvas. Change content, not this.
# ═════════════════════════════════════════════════════════════════════════════
prs, L = new_deck()
FEE_STR = f"${FEE:,}"

# ── 1 — Cover (Layout 13) ────────────────────────────────────────────────────
s = prs.slides.add_slide(L[13])
set_ph(s, 3, f"{CUSTOMER_CAPS}\n{ENGAGEMENT}")
set_ph(s, 0, SUBTITLE)
set_ph(s, 2, "\n".join(f"{n} · {r}" for n, r in PRESENTERS) + f"\n{DECK_DATE}")

# ── 2 — Proposal Content ─────────────────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Proposal Content")
col_x = [0.55, 5.15]; row_y0 = 1.42; rh = 0.55; badge = 0.34
split = 7
for i, item in enumerate(AGENDA):
    col = 0 if i < split else 1
    row = i if i < split else i - split
    x = col_x[col]; y = row_y0 + row * rh
    add_shape_text(s, MSO_SHAPE.RECTANGLE, x, y, badge, badge, f"{i+1:02d}",
                   SF_BLUE, WHITE, font_size=12, bold=True)
    add_textbox(s, x + badge + 0.12, y - 0.02, 3.85, badge + 0.05, [item],
                size=11, color=DK1, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# ── 3 — Executive Summary & Objectives ───────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Executive Summary")
ra_y = 1.16; ra_h = 1.66
narrative_panel(s, 0.40, 4.55, ra_y, ra_h,
                "OUR UNDERSTANDING OF THE PROBLEM", DK2, PROBLEM)
narrative_panel(s, 5.05, 4.55, ra_y, ra_h, "ENGAGEMENT SUMMARY", SF_BLUE, SUMMARY)
add_shape_text(s, MSO_SHAPE.RECTANGLE, 0.40, 3.04, 9.20, 0.30,
               "ENGAGEMENT OBJECTIVES & SUCCESS CRITERIA",
               DK2, WHITE, font_size=9.5, bold=True, alignment=PP_ALIGN.LEFT)
grid_y0 = 3.46; ocol_x = [0.46, 5.11]; col_w = 4.49; orowh = 0.535
for i, (num, ttl, succ) in enumerate(OBJECTIVES):
    cx = ocol_x[i % 2]; cy = grid_y0 + (i // 2) * orowh
    tb = s.shapes.add_textbox(Inches(cx), Inches(cy), Inches(col_w),
                              Inches(orowh - 0.03))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    for m in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{m}", Pt(0))
    p0 = tf.paragraphs[0]; p0.alignment = PP_ALIGN.LEFT
    rn = p0.add_run(); rn.text = num + "   "
    rn.font.name = "Arial"; rn.font.size = Pt(10.5); rn.font.bold = True
    rn.font.color.rgb = SF_BLUE
    rt = p0.add_run(); rt.text = ttl
    rt.font.name = "Arial"; rt.font.size = Pt(10.5); rt.font.bold = True
    rt.font.color.rgb = DK1
    line_spacing(p0, 104)
    p1 = tf.add_paragraph(); p1.alignment = PP_ALIGN.LEFT
    rs = p1.add_run(); rs.text = succ
    rs.font.name = "Arial"; rs.font.size = Pt(8.5); rs.font.color.rgb = BODY_GREY
    line_spacing(p1, 104)

# ── 4 — Current State and Target State ───────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Current State and Target State")
set_ph(s, 1, "From a once-daily current-state extract to continuous capture with "
             "full history in Snowflake")
simple_table(s, ["Today — Source System", "Target — Snowflake"], [4.55, 4.55],
             [[(t, dict(size=9, color=TBL_GREY)),
               (f, dict(size=9, color=DK1, bold=True))] for t, f in CURRENT_TARGET],
             top=1.28, hdr_size=10)
add_textbox(s, 0.40, 5.02, 9.10, 0.26,
            ["Target-state architecture and change-capture mechanics are detailed "
             "in the Appendix. Private connectivity to the source is already "
             "validated and in place."], size=7.5, color=BODY_GREY)

# ── 5-7 — Workstream Scope Summary ───────────────────────────────────────────
BASE_HRS_TOTAL = sum(sa + c + pm for _, _, _, sa, c, pm in EFFORT)


def scope_slide(rows, part, total=False):
    s = prs.slides.add_slide(L[0]); content_chrome(s)
    set_ph(s, 0, f"Workstream Scope Summary ({part})")
    headers = ["#", "Workstream", "Activities", "Phase", "Base Hrs"]
    widths = [0.40, 1.85, 4.85, 0.90, 0.85]
    n = len(rows) + 1 + (1 if total else 0)
    gtbl = s.shapes.add_table(n, 5, Inches(0.40), Inches(1.18),
                              Inches(sum(widths)), Inches(0.34)).table
    for ci, w in enumerate(widths):
        gtbl.columns[ci].width = Inches(w)
    for ci, h in enumerate(headers):
        gtbl.cell(0, ci).text = h
        style_cell(gtbl.cell(0, ci), fill=DK2, size=9, color=WHITE, bold=True,
                   align=(PP_ALIGN.LEFT if ci in (1, 2) else PP_ALIGN.CENTER))
    for ri, (num, name, acts, ph, hrs) in enumerate(rows):
        r = ri + 1
        rowfill = WHITE if ri % 2 == 0 else LIGHT_ROW
        gtbl.cell(r, 0).text = num
        style_cell(gtbl.cell(r, 0), fill=rowfill, size=9, color=DK2, bold=True,
                   align=PP_ALIGN.CENTER)
        gtbl.cell(r, 1).text = name
        style_cell(gtbl.cell(r, 1), fill=rowfill, size=8.5, color=DK1, bold=True,
                   align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP)
        cell_bullets(gtbl.cell(r, 2), acts, size=8, color=TBL_GREY)
        gtbl.cell(r, 2).fill.solid()
        gtbl.cell(r, 2).fill.fore_color.rgb = rowfill
        gtbl.cell(r, 3).text = ph
        style_cell(gtbl.cell(r, 3), fill=rowfill, size=8.5, color=TBL_GREY,
                   align=PP_ALIGN.CENTER)
        gtbl.cell(r, 4).text = hrs
        style_cell(gtbl.cell(r, 4), fill=rowfill, size=9, color=DK1, bold=True,
                   align=PP_ALIGN.CENTER)
    if total:
        r = len(rows) + 1
        vals = ["", "Total",
                "Base delivery hours across Sr. SA, Consultant and PM. A "
                f"{int(CONTINGENCY*100)}% contingency is detailed on the Resource "
                "Effort slide.",
                f"{DURATION_WKS} wks", str(BASE_HRS_TOTAL)]
        for ci, v in enumerate(vals):
            gtbl.cell(r, ci).text = v
            style_cell(gtbl.cell(r, ci), fill=DK2, size=9, color=WHITE, bold=True,
                       align=(PP_ALIGN.LEFT if ci in (1, 2) else PP_ALIGN.CENTER))
    set_table_borders(gtbl, n, 5)
    gtbl.rows[0].height = Inches(0.28)


# 3 + 3 + 4 keeps every scope table clear of the footer. Do not put 5 on a slide.
scope_slide(WS[0:3], "1/3")
scope_slide(WS[3:6], "2/3")
scope_slide(WS[6:10], "3/3", total=True)

# ── 8 — Engagement Deliverables ──────────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Engagement Deliverables")
simple_table(s, ["#", "Deliverable", "Description"], [0.40, 4.40, 4.30],
             [[(str(i + 1), dict(size=9, color=DK2, bold=True, align=PP_ALIGN.CENTER)),
               (name, dict(size=7.5, color=DK1, bold=True)),
               (desc, dict(size=7.5, color=TBL_GREY))]
              for i, (name, desc) in enumerate(DELIVERABLES)],
             top=1.10, hdr_size=9, center_cols=(0,))

# ── 9 — Project Timeline (Gantt with gate diamonds) ──────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Project Timeline")
set_ph(s, 1, f"Indicative {DURATION_WKS}-week schedule — private connectivity to "
             "the source is already validated and in place")
WK_N = DURATION_WKS
x0 = 3.02; xe = 9.56
wkw = (xe - x0) / WK_N
top_axis = 1.30; axis_h = 0.22
rows_y0 = 1.56
# Geometry table (see reference §3.6): <=10 rows -> 0.215/0.26; 11-12 -> 0.20/0.24
rowh, step = (0.215, 0.26) if len(GANTT) <= 10 else (0.20, 0.24)


def wx(week):
    return x0 + (week - 1) * wkw


grid_bottom = rows_y0 + len(GANTT) * step
for w in range(WK_N + 1):
    add_rect(s, x0 + w * wkw, top_axis + axis_h - 0.02, 0.0085,
             grid_bottom - top_axis - axis_h + 0.02, GRID)
for w in range(1, WK_N + 1):
    add_textbox(s, x0 + (w - 1) * wkw, top_axis, wkw, axis_h, [f"W{w}"],
                size=7, color=BODY_GREY, bold=True,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for i, (label, tag, a, b, fill) in enumerate(GANTT):
    ry = rows_y0 + i * step
    if i % 2 == 0:
        add_rect(s, 0.40, ry, xe - 0.40, rowh, LIGHT_ROW)
    add_textbox(s, 0.40, ry, 0.34, rowh, [tag], size=7, color=SF_BLUE, bold=True,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(s, 0.76, ry, x0 - 0.86, rowh, [label], size=7.5, color=DK1,
                bold=(i == len(GANTT) - 1), align=PP_ALIGN.LEFT,
                anchor=MSO_ANCHOR.MIDDLE)
    bx = wx(a); bw = (b - a + 1) * wkw
    add_shape_text(s, MSO_SHAPE.ROUNDED_RECTANGLE, bx + 0.025, ry + 0.035,
                   bw - 0.05, rowh - 0.07, "", fill, WHITE, font_size=6)
# gate diamonds sit on the row that OWNS the gate
for num, row, week, label in GATE_MARKS:
    ry = rows_y0 + row * step
    cx = wx(week) + wkw / 2
    d = 0.195
    add_shape_text(s, MSO_SHAPE.DIAMOND, cx - d / 2, ry + rowh / 2 - d / 2, d, d,
                   str(num), ORANGE, DK1, font_size=7, bold=True)
# 3-column legend so the diamonds are readable without the milestone slide
leg_y = grid_bottom + 0.10
lcol = [0.40, 3.48, 6.56]
leg_rows = (len(GATE_MARKS) + 2) // 3
for i, (num, row, week, label) in enumerate(GATE_MARKS):
    x = lcol[i // leg_rows]; y = leg_y + (i % leg_rows) * 0.215
    add_shape_text(s, MSO_SHAPE.DIAMOND, x, y, 0.19, 0.19, str(num),
                   ORANGE, DK1, font_size=7, bold=True)
    add_textbox(s, x + 0.25, y - 0.015, 2.78, 0.22, [f"W{week} — {label}"],
                size=7, color=DK1, anchor=MSO_ANCHOR.MIDDLE)
add_textbox(s, 0.40, leg_y + leg_rows * 0.215 + 0.04, 9.10, 0.26,
            ["Weeks are relative to a confirmed kickoff. Parallel workstreams "
             "start once the history model is stable; a dated Gantt is issued "
             "with the SOW."], size=7.5, color=BODY_GREY)

# ── 10 — Milestones and Acceptance Gates ─────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Milestones and Acceptance Gates")
set_ph(s, 1, "Each phase closes on a milestone with defined deliverables and a "
             "formal acceptance gate")
simple_table(s, ["#", "Milestone", "Target", "Key Deliverables", "Acceptance Gate"],
             [0.45, 2.20, 0.72, 3.00, 2.73],
             [[(num, dict(size=8, color=DK2, bold=True, align=PP_ALIGN.CENTER)),
               (name, dict(size=7.5, color=DK1, bold=True)),
               (tgt, dict(size=7, color=DK1, bold=True, align=PP_ALIGN.CENTER)),
               (dv, dict(size=7, color=TBL_GREY)),
               (gate, dict(size=7, color=TBL_GREY))]
              for num, name, tgt, dv, gate in GATES],
             top=1.18, hdr_size=8.5, center_cols=(0, 2))
add_textbox(s, 0.40, 4.90, 9.10, 0.26,
            [f"Target weeks are indicative and relative to a confirmed kickoff. "
             f"These {len(GATES)} gates roll up into the {len(BILLING)} billing "
             "milestones on the Milestone Payment Schedule."],
            size=7.5, color=BODY_GREY)

# ── 11 — Open Scope Items and Pending Inputs ─────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Open Scope Items and Pending Inputs")
set_ph(s, 1, "Items deliberately left open in this baseline; each is resolved "
             "before or shortly after SOW")
ax = [0.40, 5.05]; ay = [1.28, 3.06]; aw = 4.55; ah = 1.68
for i, (title, fill, items) in enumerate(OPEN_ITEMS):
    add_card(s, ax[i % 2], ay[i // 2], aw, ah, title.upper(), items,
             header_fill=fill, header_size=9.5, body_size=8.5)
add_shape_text(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.40, 4.78, 9.10, 0.40,
               f"PENDING INPUTS FROM {CUSTOMER_CAPS}:  {PENDING_INPUTS}",
               LIGHT_BLUE, DK1, font_size=8.5, bold=True, alignment=PP_ALIGN.LEFT)

# ── 12 — Customer Dependencies and Commitments ───────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Customer Dependencies and Commitments")
set_ph(s, 1, f"Commitments required from {CUSTOMER}; the fixed fee assumes these "
             "are met on schedule")
simple_table(s, ["#", "Customer Commitment", "Customer Owner", "Required By",
                 "Impact if Delayed"],
             [0.40, 3.30, 1.90, 1.45, 2.15],
             [[(num, dict(size=8.5, color=DK2, bold=True, align=PP_ALIGN.CENTER)),
               (commit, dict(size=8, color=DK1, bold=True)),
               (owner, dict(size=8, color=TBL_GREY)),
               (req, dict(size=8, color=DK1, bold=True, align=PP_ALIGN.CENTER)),
               (impact, dict(size=7.5, color=TBL_GREY))]
              for num, commit, owner, req, impact in DEPENDENCIES],
             top=1.26, center_cols=(0, 3))
add_textbox(s, 0.40, 5.02, 9.10, 0.26,
            ["Named customer owners are placeholders pending confirmation of the "
             "delivery team. Slippage on a commitment shifts the dependent "
             "acceptance gate."], size=7.5, color=BODY_GREY)

# ── Effort maths — computed here because slides 13, 17, 19, 20 all consume it ─
tot_sa = sum(r[3] for r in EFFORT)
tot_c = sum(r[4] for r in EFFORT)
tot_pm = sum(r[5] for r in EFFORT)
BASE_TOT = tot_sa + tot_c + tot_pm
COMMIT_SA, COMMIT_C, COMMIT_PM = tot_sa + CONT_SA, tot_c + CONT_C, tot_pm + CONT_PM
COMMIT_TOT = COMMIT_SA + COMMIT_C + COMMIT_PM
COMMIT_BY_KEY = {"sa": COMMIT_SA, "c": COMMIT_C, "pm": COMMIT_PM}
EXTENDED = COMMIT_SA * RATE_SA + COMMIT_C * RATE_C + COMMIT_PM * RATE_PM

# ── 13 — Snowflake Roles and Responsibilities ────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Snowflake Roles and Responsibilities")
set_ph(s, 1, f"{len(SF_ROLES)}-role delivery team; allocations are confirmed at "
             "staffing and do not change the fixed fee")
simple_table(s, ["Role", "Committed Hours", "Key Responsibilities"],
             [2.40, 1.60, 5.10],
             [[(role, dict(size=9.5, color=DK2, bold=True)),
               (f"{COMMIT_BY_KEY[key]} hrs",
                dict(size=9, color=DK1, bold=True, align=PP_ALIGN.CENTER)),
               (items, dict(size=8, color=TBL_GREY))]
              for role, key, items in SF_ROLES],
             top=1.40, hdr_size=9, center_cols=(1,))
add_textbox(s, 0.40, 4.62, 9.10, 0.40,
            ["Weekly allocations per role are set once total engagement duration "
             f"is confirmed. Committed hours include the {int(CONTINGENCY*100)}% "
             "contingency detailed on the Resource Effort slide."],
            size=8, color=BODY_GREY, line_pct=108)

# ── 14 — Customer Roles and Responsibilities ─────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, f"{CUSTOMER} Roles and Responsibilities")
simple_table(s, ["Role", "Responsibilities", "Est. Weekly Allocation"],
             [2.35, 5.65, 1.10],
             [[(role, dict(size=9, color=DK1, bold=True)),
               (resp, dict(size=8.5, color=TBL_GREY)),
               (alloc, dict(size=8.5, color=DK1, bold=True, align=PP_ALIGN.CENTER))]
              for role, resp, alloc in CUST_ROLES],
             top=1.24, hdr_size=9, center_cols=(2,))
add_textbox(s, 0.40, 5.02, 9.10, 0.26,
            [f"Named individuals per role to be confirmed with {CUSTOMER} before "
             "SOW execution."], size=7.5, color=BODY_GREY)

# ── 15 — Engagement RACI ─────────────────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Engagement RACI")
RACI_FILL = {"R": SF_BLUE, "A": DK2, "C": LIGHT_BLUE, "I": LIGHT_BG}
RACI_TEXT = {"R": WHITE, "A": WHITE, "C": DK2, "I": TBL_GREY}
simple_table(s, ["Activity", "Snowflake", CUSTOMER, "Assumption"],
             [2.95, 1.15, 1.15, 3.85],
             [[(act, dict(size=8.5, color=DK1, bold=True)),
               (sf, dict(fill=RACI_FILL[sf], size=10, color=RACI_TEXT[sf],
                         bold=True, align=PP_ALIGN.CENTER)),
               (cu, dict(fill=RACI_FILL[cu], size=10, color=RACI_TEXT[cu],
                         bold=True, align=PP_ALIGN.CENTER)),
               (assum, dict(size=8, color=TBL_GREY))]
              for act, sf, cu, assum in RACI],
             top=1.16, hdr_size=9, center_cols=(1, 2))
add_textbox(s, 0.40, 4.96, 9.10, 0.30,
            ["R = Responsible    A = Accountable    C = Consulted    I = Informed"],
            size=8, color=BODY_GREY, bold=True)

# ── 16 — Assumptions and Exclusions ──────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Assumptions and Exclusions")
ax = [0.40, 5.05]; ay = [1.28, 3.20]; aw = 4.55; ah = 1.80
for i, (title, fill, items) in enumerate(ASSUMPTIONS):
    add_card(s, ax[i % 2], ay[i // 2], aw, ah, title.upper(), items,
             header_fill=fill, header_size=9.5, body_size=8.5)

# ── 17 — Resource Effort and Contingency ─────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Resource Effort and Contingency")
set_ph(s, 1, f"Effort by role and workstream with a {int(CONTINGENCY*100)}% "
             "delivery contingency, supporting the fixed fee")
ewidths = [0.38, 3.32, 0.62, 1.00, 1.55, 0.90, 1.43]
n = len(EFFORT) + 4
etbl = s.shapes.add_table(n, 7, Inches(0.40), Inches(1.18),
                          Inches(sum(ewidths)), Inches(0.30)).table
for ci, w in enumerate(ewidths):
    etbl.columns[ci].width = Inches(w)
for ci, h in enumerate(["#", "Workstream", "Phase", "Sr. SA", "Consultant",
                        "PM/SDM", "Base Hrs"]):
    etbl.cell(0, ci).text = h
    style_cell(etbl.cell(0, ci), fill=DK2, size=8.5, color=WHITE, bold=True,
               align=(PP_ALIGN.LEFT if ci == 1 else PP_ALIGN.CENTER))
for ri, (num, name, ph, sa, c, pm) in enumerate(EFFORT):
    r = ri + 1
    rowfill = WHITE if ri % 2 == 0 else LIGHT_ROW
    for ci, v in enumerate([num, name, ph, str(sa), str(c), str(pm),
                            str(sa + c + pm)]):
        etbl.cell(r, ci).text = v
        if ci == 1:
            style_cell(etbl.cell(r, ci), fill=rowfill, size=8, color=DK1,
                       bold=True, align=PP_ALIGN.LEFT)
        elif ci == 6:
            style_cell(etbl.cell(r, ci), fill=rowfill, size=8.5, color=DK1,
                       bold=True, align=PP_ALIGN.CENTER)
        else:
            style_cell(etbl.cell(r, ci), fill=rowfill, size=8.5,
                       color=(DK2 if ci == 0 else TBL_GREY), bold=(ci == 0),
                       align=PP_ALIGN.CENTER)
CONT_TOT = CONT_SA + CONT_C + CONT_PM
summ = [
    ("Base Total", tot_sa, tot_c, tot_pm, BASE_TOT, LIGHT_BLUE, DK1),
    (f"+ {int(CONTINGENCY*100)}% Contingency", CONT_SA, CONT_C, CONT_PM,
     CONT_TOT, LIGHT_BLUE, DK2),
    ("Total Committed Capacity", COMMIT_SA, COMMIT_C, COMMIT_PM, COMMIT_TOT,
     DK2, WHITE),
]
for si, (lbl, sa, c, pm, tot, fill, txt) in enumerate(summ):
    r = len(EFFORT) + 1 + si
    for ci, v in enumerate(["", lbl, ""]):
        etbl.cell(r, ci).text = v
        style_cell(etbl.cell(r, ci), fill=fill, size=8.5, color=txt, bold=True,
                   align=(PP_ALIGN.LEFT if ci == 1 else PP_ALIGN.CENTER))
    for ci, v in zip((3, 4, 5, 6), (sa, c, pm, tot)):
        etbl.cell(r, ci).text = str(v)
        style_cell(etbl.cell(r, ci), fill=fill, size=8.5, color=txt, bold=True,
                   align=PP_ALIGN.CENTER)
set_table_borders(etbl, n, 7)
etbl.rows[0].height = Inches(0.24)
# Footnote MUST name what the contingency is for and that unused is not billed.
add_textbox(s, 0.40, 4.72, 9.10, 0.42,
            [f"Base effort {BASE_TOT} hrs  ·  {int(CONTINGENCY*100)}% contingency "
             f"+{CONT_TOT} hrs  ·  total committed capacity {COMMIT_TOT} hrs  ·  "
             f"fixed fee {FEE_STR}.  The contingency covers {CONTINGENCY_COVERS}; "
             "unused contingency is not billed."],
            size=7.5, color=BODY_GREY, line_pct=104)

# ── 18 — Risks and Mitigations ───────────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Risks and Mitigations")
rx = [0.40, 3.47, 6.54]; ry = [1.30, 3.20]; rw = 2.93; rh_ = 1.78; rhdr = 0.34
for i, (title, sev, sevc, risk, mit) in enumerate(RISKS):
    x = rx[i % 3]; y = ry[i // 3]
    add_shape_text(s, MSO_SHAPE.RECTANGLE, x, y, rw, rhdr, title, DK2, WHITE,
                   font_size=8.5, bold=True, alignment=PP_ALIGN.LEFT)
    add_shape_text(s, MSO_SHAPE.RECTANGLE, x + rw - 0.78, y, 0.78, rhdr, sev,
                   sevc, (WHITE if sev == "HIGH" else DK1), font_size=7.5, bold=True)
    bod = add_rect(s, x, y + rhdr, rw, rh_ - rhdr, LIGHT_BG)
    tf = bod.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Pt(7); tf.margin_right = Pt(6)
    tf.margin_top = Pt(5); tf.margin_bottom = Pt(4)
    for j, txt in enumerate([risk, mit]):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = txt
        r.font.name = "Arial"; r.font.size = Pt(7.5); r.font.color.rgb = DK1
        line_spacing(p, 104)
        if j == 0:
            p.space_after = Pt(4)

# ── 19 — Pricing ─────────────────────────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Pricing")
pk = [(FEE_STR, "Fixed Fee"),
      (f"{DURATION_WKS} Weeks", "Indicative Duration"),
      (f"{COMMIT_TOT} hrs", "Committed Capacity"),
      (f"{len(SF_ROLES)} Roles", "Sr. SA · Consultant · PM")]
kx = 0.40; kw = 2.16; kgap = 0.13
for i, (v, lab) in enumerate(pk):
    fill = DK2 if i % 2 == 0 else SF_BLUE
    add_kpi(s, kx + i * (kw + kgap), 1.20, kw, 1.00, v, lab, fill=fill, vsize=20,
            label_color=(TEAL if fill == DK2 else WHITE))
add_shape_text(s, MSO_SHAPE.RECTANGLE, 0.40, 2.50, 9.10, 0.32,
               "WHAT THE FIXED FEE COVERS", DK2, WHITE, font_size=9.5, bold=True,
               alignment=PP_ALIGN.LEFT)
covers = add_rect(s, 0.40, 2.82, 9.10, 1.42, LIGHT_BG)
tf = covers.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
tf.margin_left = Pt(9); tf.margin_right = Pt(8)
tf.margin_top = Pt(6); tf.margin_bottom = Pt(5)
for i, it in enumerate(FEE_COVERS):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    r = p.add_run()
    r.text = it.format(base=BASE_TOT, pct=int(CONTINGENCY * 100), commit=COMMIT_TOT)
    r.font.name = "Arial"; r.font.size = Pt(9); r.font.color.rgb = DK1
    set_bullet(p, char="•", color=SF_BLUE, size_pct=80)
    line_spacing(p, 108)
# The load-bearing sentence: the fee is based on committed hours, not weeks.
add_shape_text(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.40, 4.36, 9.10, 0.68,
               f"Proposed as a fixed-fee delivery of {FEE_STR}, funded through "
               f"{FUNDING}. The {DURATION_WKS}-week duration is indicative; the "
               "fixed fee is based on committed hours, not elapsed weeks. Role mix "
               "is confirmed at staffing and does not change the fixed fee.",
               LIGHT_BLUE, DK1, font_size=8.5, bold=False, alignment=PP_ALIGN.LEFT)

# ── 20 — Milestone Payment Schedule ──────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Milestone Payment Schedule")
set_ph(s, 1, f"The {FEE_STR} fixed fee allocated across {len(BILLING)} billing "
             "milestones, each tied to accepted deliverables")
kx = 0.40; kw = 2.16; kgap = 0.13
for i, (lbl, _n, _p, _d, _g, _h, fee, pct) in enumerate(BILLING):
    fill = DK2 if i % 2 == 0 else SF_BLUE
    box = add_rect(s, kx + i * (kw + kgap), 1.22, kw, 0.94, fill)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Pt(4); tf.margin_right = Pt(4)
    accent = TEAL if fill == DK2 else WHITE
    for j, (txt, sz, col) in enumerate([(lbl, 7.5, accent),
                                        (f"${fee:,}", 19, WHITE),
                                        (f"{pct} of fixed fee", 7.5, accent)]):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = txt
        r.font.name = "Arial"; r.font.size = Pt(sz); r.font.bold = True
        r.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER
bwidths = [0.52, 2.05, 1.28, 3.35, 0.62, 0.66, 0.62]
n = len(BILLING) + 2
btbl = s.shapes.add_table(n, 7, Inches(0.40), Inches(2.32),
                          Inches(sum(bwidths)), Inches(0.26)).table
for ci, w in enumerate(bwidths):
    btbl.columns[ci].width = Inches(w)
for ci, h in enumerate(["#", "Billing Milestone", "Phases / WS",
                        "Deliverables Accepted", "Gates", "Hrs", "Fee"]):
    btbl.cell(0, ci).text = h
    style_cell(btbl.cell(0, ci), fill=DK2, size=8.5, color=WHITE, bold=True,
               align=(PP_ALIGN.LEFT if ci in (1, 2, 3) else PP_ALIGN.CENTER))
BM_STYLE = [dict(size=8.5, color=DK2, bold=True, align=PP_ALIGN.CENTER),
            dict(size=8, color=DK1, bold=True, align=PP_ALIGN.LEFT),
            dict(size=7.5, color=TBL_GREY, align=PP_ALIGN.LEFT),
            dict(size=7, color=TBL_GREY, align=PP_ALIGN.LEFT),
            dict(size=7.5, color=DK1, bold=True, align=PP_ALIGN.CENTER),
            dict(size=8, color=DK1, bold=True, align=PP_ALIGN.CENTER),
            dict(size=8.5, color=DK1, bold=True, align=PP_ALIGN.CENTER)]
for ri, (lbl, name, phs, dv, gates, hrs, fee, pct) in enumerate(BILLING):
    r = ri + 1
    rowfill = WHITE if ri % 2 == 0 else LIGHT_ROW
    vals = [lbl, name, phs, dv, gates, str(hrs), f"${fee // 1000}K"]
    for ci, v in enumerate(vals):
        btbl.cell(r, ci).text = v
        style_cell(btbl.cell(r, ci), fill=rowfill, **BM_STYLE[ci])
r = len(BILLING) + 1
tot_fee = sum(b[6] for b in BILLING)
tot_hrs = sum(b[5] for b in BILLING)
for ci, v in enumerate(["", "Total",
                        f"{len(set(w[3] for w in WS))} phases · {len(WS)} WS",
                        "All engagement deliverables",
                        f"{GATES[0][0]}–{GATES[-1][0]}", str(tot_hrs),
                        f"${tot_fee // 1000}K"]):
    btbl.cell(r, ci).text = v
    style_cell(btbl.cell(r, ci), fill=DK2, size=8.5, color=WHITE, bold=True,
               align=(PP_ALIGN.LEFT if ci in (1, 2, 3) else PP_ALIGN.CENTER))
set_table_borders(btbl, n, 7)
btbl.rows[0].height = Inches(0.24)
add_shape_text(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.40, 4.62, 9.10, 0.58,
               f"Each billing milestone is invoiced on {CUSTOMER}'s acceptance of "
               "the deliverables listed, against the corresponding "
               f"{GATES[0][0]}–{GATES[-1][0]} acceptance gates. Allocation is "
               f"pro-rata to committed hours and does not change the {FEE_STR} "
               "fixed fee; unused contingency is not billed.",
               LIGHT_BLUE, DK1, font_size=8, bold=False, alignment=PP_ALIGN.LEFT)

# ── 21 — Next Steps ──────────────────────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Next Steps")
sx = [0.40, 5.05]; sy0 = 1.36; srh = 0.90; sbw = 4.55; bsz = 0.40
half = (len(NEXT_STEPS) + 1) // 2
for i, st in enumerate(NEXT_STEPS):
    col = 0 if i < half else 1
    row = i if i < half else i - half
    x = sx[col]; y = sy0 + row * srh
    add_shape_text(s, MSO_SHAPE.OVAL, x, y, bsz, bsz, f"{i+1}", SF_BLUE, WHITE,
                   font_size=13, bold=True)
    add_shape_text(s, MSO_SHAPE.RECTANGLE, x + bsz + 0.10, y, sbw - bsz - 0.10,
                   bsz, st, LIGHT_BG, DK1, font_size=9, bold=True,
                   alignment=PP_ALIGN.LEFT)

# ── 22 — Appendix divider (Layout 18) ────────────────────────────────────────
s = prs.slides.add_slide(L[18])
set_ph(s, 1, "APPENDIX")

# ── 23 — Appendix: Target-State Architecture ─────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Appendix: Target-State Architecture")
set_ph(s, 1, "Source change capture through to a governed, history-preserving "
             "Snowflake data product")
fx = 0.40; fgap = 0.13; fy = 1.62; fh = 1.22
fw = (9.10 - fgap * (len(ARCH_FLOW) - 1)) / len(ARCH_FLOW)
for i, (label, desc, fill) in enumerate(ARCH_FLOW):
    x = fx + i * (fw + fgap)
    box = add_rect(s, x, fy, fw, fh, fill)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Pt(3); tf.margin_right = Pt(3)
    for j, (txt, sz, col, bold) in enumerate([(label, 7.5, WHITE, True),
                                              (desc, 7, TEAL, False)]):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = txt
        r.font.name = "Arial"; r.font.size = Pt(sz); r.font.bold = bold
        r.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER
    if i < len(ARCH_FLOW) - 1:
        add_shape_text(s, MSO_SHAPE.CHEVRON, x + fw - 0.02, fy + fh / 2 - 0.16,
                       fgap + 0.04, 0.32, "", SF_BLUE, WHITE, font_size=6)
for i, (txt, fill) in enumerate(ARCH_BANDS):
    add_shape_text(s, MSO_SHAPE.RECTANGLE, 0.40, fy + fh + 0.20 + i * 0.50,
                   9.10, 0.42, txt, fill, WHITE, font_size=8.5, bold=True)

# ── 24 — Appendix: Change Capture Mechanics ──────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Appendix: Change Capture Mechanics")
set_ph(s, 1, "Why the historical model is built from the journal table rather "
             "than the merged destination")
mx = [0.40, 5.05]
for i, (title, fill, items) in enumerate(MECHANICS):
    add_card(s, mx[i], 1.28, 4.55, 1.72, title.upper(), items,
             header_fill=fill, header_size=9.5, body_size=8.5)
add_shape_text(s, MSO_SHAPE.RECTANGLE, 0.40, 3.16, 9.10, 0.32,
               "WHAT THIS MEANS FOR THE ENGAGEMENT", DK2, WHITE, font_size=9.5,
               bold=True, alignment=PP_ALIGN.LEFT)
impl = add_rect(s, 0.40, 3.48, 9.10, 1.52, LIGHT_BG)
tf = impl.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
tf.margin_left = Pt(9); tf.margin_right = Pt(8)
tf.margin_top = Pt(7); tf.margin_bottom = Pt(5)
for i, it in enumerate(MECHANICS_IMPL):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    r = p.add_run(); r.text = it
    r.font.name = "Arial"; r.font.size = Pt(8.5); r.font.color.rgb = DK1
    set_bullet(p, char="•", color=SF_BLUE, size_pct=80)
    line_spacing(p, 106)
    p.space_after = Pt(3)

# ── 25 — Appendix: Source Data Model ─────────────────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Appendix: Source Data Model")
set_ph(s, 1, "As described on the scoping call; to be confirmed against the DDL "
             "and ERD once supplied")
simple_table(s, ["Table Class", "Count", "Role in the Model",
                 "Proposed Treatment", "Change Rate"],
             [1.75, 0.62, 3.30, 2.68, 0.85],
             [[(cls, dict(size=9, color=DK2, bold=True)),
               (cnt, dict(size=10, color=DK1, bold=True, align=PP_ALIGN.CENTER)),
               (role, dict(size=8.5, color=TBL_GREY)),
               (treat, dict(size=8.5, color=DK1)),
               (rate, dict(size=8.5, color=BODY_GREY, bold=True,
                           align=PP_ALIGN.CENTER))]
              for cls, cnt, role, treat, rate in DATA_MODEL],
             top=1.30, hdr_size=9, center_cols=(1, 4), row_h=0.60)
# Known vs. unknown side by side — this is the honest-TBD doctrine as a visual.
for x, hdr, fill, items in [
        (0.40, "CONFIRMED ON THE SCOPING CALL", DK2, MODEL_KNOWN),
        (5.05, "TO BE CONFIRMED FROM THE DDL / ERD", SF_BLUE, MODEL_UNKNOWN)]:
    add_shape_text(s, MSO_SHAPE.RECTANGLE, x, 3.42, 4.45, 0.32, hdr, fill, WHITE,
                   font_size=9.5, bold=True, alignment=PP_ALIGN.LEFT)
    box = add_rect(s, x, 3.74, 4.45, 1.24, LIGHT_BG)
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Pt(8); tf.margin_right = Pt(7)
    tf.margin_top = Pt(6); tf.margin_bottom = Pt(4)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = it
        r.font.name = "Arial"; r.font.size = Pt(8.5); r.font.color.rgb = DK1
        set_bullet(p, char="•", color=SF_BLUE, size_pct=80)
        line_spacing(p, 106)

# ── 26 — Appendix: Transformation Pattern Options ────────────────────────────
s = prs.slides.add_slide(L[0]); content_chrome(s)
set_ph(s, 0, "Appendix: Transformation Pattern Options")
set_ph(s, 1, f"{CUSTOMER} has asked for our recommendation; selection is made and "
             "approved at the M2 gate")
simple_table(s, ["Pattern", "How It Works", "Strengths", "Considerations"],
             [1.60, 2.55, 2.50, 2.45],
             [[(name, dict(size=9.5, color=DK2, bold=True)),
               (how, dict(size=8, color=TBL_GREY)),
               (pro, dict(size=8, color=DK1)),
               (con, dict(size=8, color=TBL_GREY))]
              for name, how, pro, con in OPTIONS],
             top=1.28, hdr_size=9, row_h=0.90)
add_shape_text(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.40, 4.10, 9.10, 0.86,
               OPTIONS_NOTE, LIGHT_BLUE, DK1, font_size=8.5, bold=False,
               alignment=PP_ALIGN.LEFT)

# ── 27 — Thank You (Layout 28) ───────────────────────────────────────────────
s = prs.slides.add_slide(L[28])
set_ph(s, 1, "THANK\nYOU")
panel = add_rect(s, 5.55, 3.55, 4.05, 1.45, DK2)
tf = panel.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Pt(10); tf.margin_right = Pt(8)
tf.margin_top = Pt(6); tf.margin_bottom = Pt(6)
first = True
for name, role in PRESENTERS:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run(); r.text = name
    r.font.name = "Arial"; r.font.size = Pt(11); r.font.bold = True
    r.font.color.rgb = WHITE
    p2 = tf.add_paragraph(); r2 = p2.add_run(); r2.text = role
    r2.font.name = "Arial"; r2.font.size = Pt(8.5); r2.font.color.rgb = TEAL
    p2.space_after = Pt(4)

# ═════════════════════════════════════════════════════════════════════════════
# ASSERTS — the only thing keeping four numbers consistent across six slides.
# Never delete these. If one fires, the deck is mispriced, not the assert wrong.
# ═════════════════════════════════════════════════════════════════════════════
assert (tot_sa, tot_c, tot_pm) == (EXPECT_SA, EXPECT_C, EXPECT_PM), (
    f"role column totals drifted: {tot_sa}/{tot_c}/{tot_pm} — fixed fee is now "
    f"wrong (expected {EXPECT_SA}/{EXPECT_C}/{EXPECT_PM})")
assert EXTENDED <= FEE, (
    f"committed hours price to ${EXTENDED:,}, above the stated fee {FEE_STR}")
assert FEE - EXTENDED < 1000, (
    f"committed hours price to ${EXTENDED:,}, more than $1K under {FEE_STR} — "
    "adjust rates or hours rather than presenting a gap")
assert tot_fee == FEE, f"billing milestones sum to {tot_fee:,}, expected {FEE:,}"
assert tot_hrs == COMMIT_TOT, f"billing hrs {tot_hrs} != committed {COMMIT_TOT}"
assert BILLING[0][7] and float(BILLING[0][7].rstrip('%')) <= 25.0, (
    "BM1 exceeds 25% of the fee — front-loading reads badly to procurement")
ws_hrs = {w[0]: int(w[4]) for w in WS}
eff_hrs = {e[0]: e[3] + e[4] + e[5] for e in EFFORT}
assert ws_hrs == eff_hrs, (
    f"scope-slide Base Hrs disagree with the effort table: {ws_hrs} vs {eff_hrs}")

save_deck(prs, OUTPUT)
print(f"  Base hrs: {BASE_TOT}  Committed: {COMMIT_TOT}")
print(f"  Price check: {COMMIT_SA}*{RATE_SA} + {COMMIT_C}*{RATE_C} + "
      f"{COMMIT_PM}*{RATE_PM} = ${EXTENDED:,}  (presented as {FEE_STR})")
