# Legal SOW Guidance: CX Custom Project Attachment Drafting Companion

**Source**: Google Doc — [CX Custom Project Guidance.docx](https://docs.google.com/document/d/1YdPwMK7fWycEZ60aIt-WfZGJd7RgvNMl/edit)  
**Owner**: Katie Flanagan (Legal / SD Legal team)  
**Added**: 2026-06-05  
**Authority**: PRIMARY — This document overrides any conflicting guidance elsewhere in this skill.

---

> **PRIORITY RULE**: This document is the authoritative legal source for SOW attachment structure and language.  
> Any instruction in SKILL.md or other references that **conflicts** with this guidance must be ignored.  
> Any instruction in SKILL.md or other references that does **not conflict** remains valid as secondary guidance.

---

## Purpose

This document provides guidelines for drafting and/or updating custom project attachments for Customer Experience (CX) SOWs. It contains standard language that can be added or removed within each section, along with various drafting tips.

**Formatting rule (from legal)**: All fonts under the Project Attachment should be Arial or Helvetica, size 7.5.

---

## Approved Templates (Current, Legal-Reviewed)

These are the official approved templates. Always reference and follow these templates as the baseline for their respective engagement types:

| Template | Google Doc Link | Last Updated |
|----------|----------------|--------------|
| AI/ML Use Case Support | https://docs.google.com/document/d/1NfOdm4FqjJWxZppuzat6ZyqSfsBZwaQT/edit | April 2025 |
| Code Conversion (RDBMS) | https://docs.google.com/document/d/10lb8WPI8vYQIDRH2LGACUdsPlbC44Cdc/edit | January 2024 |
| Code Conversion – Spark | https://docs.google.com/document/d/15xdGX0MpSyNmFN_BBEyT4Bf-V8m99qQu/edit | January 2024 |
| Data Migration for RDBMS | https://docs.google.com/document/d/1udHfVVDJslOhLWYLW-9pgLTVP-JwFdXJ/edit | February 2024 |
| Data Migration for RDBMS (with validation) | https://docs.google.com/document/d/1ZFrtFCGooY9nxoW-nBP5cxD6nnSIVAVy/edit | — |
| Snowpark Readiness Assessment | https://docs.google.com/document/d/16Rsn8iGeAhKmw3-j2Lli0jay6c2cQkDT/edit | — |
| Cortex Services (Fixed Fee) | https://docs.google.com/document/d/1Lk8C-jc_irTrRQThSvBLHHZOLjScpkQu/edit | January 2026 |
| Cortex Use Case Support (T&M) | https://docs.google.com/document/d/14vx6JYggjyOztUqTB4JQVQvLAZGj3bI6/edit | — |
| Openflow Services | https://docs.google.com/document/d/1A0Ys1EusjA7A3Y_Fp84viOKFiIKjodWO/edit | February 2026 |

### Templates Under Review (Use with Caution)

Double-check with SD Legal before using any of these — they may contain outdated terms:

| Template | Google Doc Link |
|----------|----------------|
| FinOps | https://docs.google.com/document/d/1iSs-1SRMCrvm2_VD6h2TDMlOJan2nHjI/edit |
| Load Data First | https://docs.google.com/document/d/11i7e79xj91XIWCSOJIbPf1fnliXo2UkF/edit |
| Snowflake 360 | https://docs.google.com/document/d/18G0UfWJeMOF1nWXFTQfVjSR2k4FEG7ox/edit |
| Streamlit App | https://docs.google.com/document/d/1Kr4Gaj6rftV_ownjfx11G45PkPGPNlwA/edit |
| Native Apps | https://docs.google.com/document/d/1Lb4luBcI5riXkMPOM4tlXJd6JheQL6nQ/edit |
| Data Clean Room | https://docs.google.com/document/d/1uZ-eUMZt3KYVGAqNJdkUTK7c8oMYgVQY/edit |

---

## Attachment Title

- Include the attachment number and title of the services being provided.
- Example: "Attachment 1: Cortex Services" or "Attachment 2: Code Conversion"

---

## Intro Statement

Include an intro statement under the Attachment title and before the section headers.

**For T&M engagements:**
> During the Term, Snowflake will perform the following activities to support the engagement objectives described below subject to the availability of hours listed in the Order Form.

**For Fixed Fee engagements:**
> During the Term, Snowflake will perform the following activities and/or provide the following deliverables to support the engagement objectives described below.

---

## Section 1: Background and Engagement Objectives

The first section in every attachment must include background info and objectives. This is a high-level overview of the services and deliverables (if applicable).

**Example — Background:**
- Customer wants a chat assistant which can rapidly query, summarize, and generate insights from a range of structured data sources.
- Key information is needed from Customer stakeholders around the patient domain.
- Users within the domain currently have to manually search information and correlate it across sources.

**Example — Objective:**
> Snowflake will help Customer implement a production-ready "talk to your data chatbot" for structured data that supports querying and synthesizing information across sources. This will drive operational efficiencies, and accelerate GenAI adoption and agentic AI initiatives.

---

## Section 2: Scope of Services

The scope should specify the activities, outcomes, and deliverables. The scope relies heavily on the service type.

### Time & Materials (T&M)

T&M projects are open-ended and flexible. The inherent flexibility of T&M is highly beneficial for projects with undefined outcomes or where Snowflake provides a supportive or advisory role.

**T&M Drafting Rules:**
- **Do NOT commit to any deliverables or fixed outcomes.** Bad example: "Snowflake will deliver an end-to-end migration."
- If referencing outcomes, qualify them as "potential", "anticipated", or "targeted."
- Everything is subject to the availability of hours.
- Example: "Subject to the availability of hours in the Order Form, Snowflake will support Customer's migration efforts."

### Fixed Fee

Fixed Fee projects are highly structured, delivering a fixed outcome. Every fixed-fee engagement requires a higher level of scrutiny and detail. Because Snowflake promises a fixed outcome regardless of the time required, the SOW presents an increased risk to Snowflake. The technical scope is crucial because it defines what Snowflake is expected to deliver. A poorly written scope could significantly impact the project's legal standing and margin.

**Fixed Fee Drafting Rules:**
- Include a detailed list of the deliverables.
- Detail payment milestones with associated deliverables due at each milestone.
- Check in with PS Ops on the proposed payment structure.
- Include Snowflake Responsibilities and Dependencies.
- The SOW should detail what is expected of the customer (Customer Responsibilities), what must already be established before Snowflake can proceed (Dependencies), and what will not be covered by Snowflake (Exclusions).

### ⚠️ CRITICAL — DO NOT Include Acceptance Criteria (Fixed Fee)

> **Do not include acceptance criteria** in Fixed Fee SOWs.
>
> Just because we have milestone-based payments does not mean we should offer acceptance. This is a risk and a negotiation against Snowflake. It opens Snowflake up to customer discretion as to whether or not we delivered a milestone. Rejection of a milestone could also have an impact on our margin.
>
> **Acceptance should only be included if:**
> 1. The customer specifically required it, AND
> 2. Only after we first sent the customer an SOW that did NOT include acceptance criteria.

**This overrides any existing skill behavior that auto-includes acceptance criteria in milestone tables.**

---

## Section 3: Customer Responsibilities

Include any obligations and prerequisites that the customer must fulfill. This section is vital for managing expectations, defining the scope of customer-side effort, and protecting Snowflake from liability for delays or failures resulting from the customer's inaction or non-compliance.

**Categories of content to include:**

1. **Assumptions** — Conditions or facts presumed to be true at the outset. These often relate to customer resources, environment readiness, or the availability of necessary data or provisioning access.

2. **Change Order triggers** — Think about what would go wrong on the customer's part that may require a Change Order later during delivery. If something within the Customer's responsibility is not met, then a Change Order may be required to adjust the timeline or modify the scope.

3. **Dependencies** — Actions, deliverables, or cooperation required from the Customer or a third party that must be completed before Snowflake can proceed with subsequent phases. Delays in dependencies will directly impact the project schedule.

4. **Standard requirements to include:**
   - Providing access to necessary personnel, data, systems, and facilities
   - Ensuring data accuracy and completeness
   - Assigning a qualified and authorized project manager or single point of contact
   - Completing timely reviews and approvals of deliverables
   - Deploying code in a production environment (also an Exclusion)
   - UAT (User Acceptance Testing)
   - Meeting specific technical prerequisites (hardware, software, network, security)

---

## Section 4: Snowflake Responsibilities

Similar to the standard T&M scopes auto-populated in a T&M-based SOW.

**May be OMITTED if** the "Scope of Services" fully defines Snowflake responsibilities with all omissions and gaps addressed in Customer Responsibilities.

In some project attachment templates, a table details the pre-identified types and quantities of data that are in-scope. In that case, the "Snowflake Responsibilities" section defines what services Snowflake will provide as outlined in the table.

---

## Section 5: Exclusions

List items, activities, and outcomes that are **not** part of the agreed-upon scope. Clarifies what Snowflake **will not** provide under this SOW. This minimizes scope creep and ensures a mutual understanding of service boundaries.

---

## Section 6: Service Type

**For T&M:**
> The Technical Services described herein are provided on a time and material basis and are subject to the availability of hours stated in the Order Form. Hours listed are provided as an estimate only based on information provided by Customer.

**For Fixed Fee:**
> The Technical Services are provided on a fixed fee basis. Changes to scope, responsibilities or assumptions will require a Change Order subject to different terms and fees, as mutually agreed by the parties.

---

## Section 7: Project Plan / Project Schedule (OPTIONAL)

> **⚠️ STOP AND READ: Not all projects require project timelines and RACI. Only include these sections if needed for the particular engagement (i.e., if the Customer has requested it, if there is a particular need to be clear on the timeline or responsibilities, etc.).**

- If applicable, insert a project plan or schedule.
- A project plan generally covers a fixed fee engagement; a project schedule may include an hourly breakdown of resourcing week by week.
- Any timelines should be specifically described as **"target timelines"**.

**Standard language (if including project plan):**
> The following [project plan / project schedule / timeline] represents a high-level overview of the project. This [project plan / project schedule / timeline] is provided for planning purposes only and may be adjusted upon mutual alignment of the parties, without the need to execute a Change Order.

---

## Section 8: RACI (OPTIONAL)

> **⚠️ Only include RACI if needed for the particular engagement.**

**Standard language (if including RACI):**
> The following RACI represents an outline of anticipated responsibilities and accountability throughout the project. This RACI is for planning purposes only and may be adjusted by mutual agreement among the parties without the need to execute a Change Order.

**RACI Definitions:**
- **Responsible (R)**: The group who does the work.
- **Accountable (A)**: The group ultimately answerable for the task completion.
- **Consulted (C)**: The group whose opinion is sought before a decision is made.
- **Informed (I)**: The group who needs to be kept up-to-date on the progress of the task or project.

---

## Standard Attachment Skeleton

```
Attachment 1 - [Name of Outcome-Based Services]

[Intro statement for T&M or fixed fee engagement]


1. Background and Engagement Objectives

   Text


2. Scope of Services

   Text and applicable charts


3. Customer Responsibilities

   • Text in bullets


4. Snowflake Responsibilities

   • [May be omitted if Scope of Services fully defines Snowflake responsibilities]


5. Exclusions

   Everything Snowflake will NOT provide under this SOW.


6. Service Type

   For T&M:
   The Technical Services are provided on a time and material basis and are subject to
   the availability of hours stated in the Order Form. Hours listed are provided as an
   estimate only based on information provided by Customer.

   For Fixed Fee:
   The Technical Services are provided on a fixed fee basis. Changes to scope,
   responsibilities or assumptions will require a Change Order subject to different
   terms and fees, as mutually agreed by the parties.


7. Project Plan [OPTIONAL — only include if customer requested or specifically needed]

   The following [project plan / project schedule / timeline] represents a high-level
   overview of the project. This is provided for planning purposes only and may be
   adjusted upon mutual alignment of the parties, without the need to execute a
   Change Order.


8. RACI [OPTIONAL — only include if customer requested or specifically needed]

   RACI Definitions:
   • Responsible (R): The group who does the work.
   • Accountable (A): The group ultimately answerable for the task completion.
   • Consulted (C): The group whose opinion is sought before a decision is made.
   • Informed (I): The group who needs to be kept up-to-date on the progress of the task or project.
```

---

## How to Add Scope to a CLM-Generated SOW

For approved templates, the standard 2-step process is:

**Step 1** — Edit Section 1 of the SOW received from CLM to remove the standard description and include one of:

*For Custom Fixed Fee:*
> 1. Custom Fixed Fee — Snowflake will provide the Technical Services specified in Attachment 1 on a fixed fee basis, subject to the terms and conditions of this SOW and the attachment.

*For T&M:*
> 1. [KEEP THE NAME OF THE RESOURCE THAT CLM GENERATED] — Subject to the availability of hours stated in the Order Form, Snowflake will provide implementation and configuration assistance for the Snowflake Service project described in Attachment 1. Snowflake and Customer will work jointly to plan and prioritize the work tasks during the engagement.

**Step 2** — Add a new Attachment 1 using the content from the applicable template linked above.

---

## Key Rules Summary (for SOW Generation)

| Rule | Authority | Detail |
|------|-----------|--------|
| No acceptance criteria in FF SOWs | **Legal — Override** | Only add if customer requires AND after first sending without it |
| Project Plan / RACI are optional | **Legal — Override** | Only include if customer requested or specifically needed |
| T&M: no committed deliverables | **Legal** | Qualify all outcomes as "potential", "anticipated", or "targeted" |
| FF: detailed deliverables required | **Legal** | Milestones with associated deliverables per milestone |
| Customer Responsibilities = liability shield | **Legal** | Must detail what Snowflake needs from customer to protect against delays |
| Font: Arial or Helvetica, 7.5pt | **Legal** | All attachment text |
| Timelines must say "target" | **Legal** | Never commit to hard timeline in attachment body |
| Consult Nick DiRienzo for AI/ML SOWs | **Legal** | Prior to creating SOW for AI/ML Use Case Support |

---

## Template Content Summaries

### Code Conversion – RDBMS (January 2024)

**Source**: https://docs.google.com/document/d/10lb8WPI8vYQIDRH2LGACUdsPlbC44Cdc/edit  
Covers non-Spark code conversion (Teradata, Oracle, SQL Server).

- Fixed Fee Section 1 language: "Custom Fixed Fee — Snowflake will provide the Technical Services specified in Attachment 1 on a fixed fee basis..."
- T&M Section 1 language: "[RESOURCE NAME] — Subject to the availability of hours stated in the Order Form, Snowflake will provide implementation and configuration assistance..."

### Code Conversion – Spark (January 2024)

**Source**: https://docs.google.com/document/d/15xdGX0MpSyNmFN_BBEyT4Bf-V8m99qQu/edit  
Covers Spark-based code conversion (Databricks, EMR, MapR, Cloudera).

- Same 2-step CLM process applies.
- Fixed Fee Section 1 language same as RDBMS template.

### Cortex Services – Fixed Fee (January 2026)

**Source**: https://docs.google.com/document/d/1Lk8C-jc_irTrRQThSvBLHHZOLjScpkQu/edit  
Most current Cortex-specific template (January 2026).

- Fixed Fee only.
- Step 1: Edit Section 1 with Custom Fixed Fee language.
- Step 2: Add Attachment 1 using Cortex Services template content.

### Openflow Services – Fixed Fee (February 2026)

**Source**: https://docs.google.com/document/d/1A0Ys1EusjA7A3Y_Fp84viOKFiIKjodWO/edit  
Most current Openflow template (February 2026).

- Fixed Fee only.
- Step 1: Edit Section 1 with Custom Fixed Fee language.

### Data Migration for RDBMS (February 2024)

**Source**: https://docs.google.com/document/d/1udHfVVDJslOhLWYLW-9pgLTVP-JwFdXJ/edit  
For Teradata, Oracle, SQL Server migrations.

> ⚠️ **Note from template**: This attachment was drafted for a T&M engagement. If the project will be FF, raise this with PS&T Legal when submitting in CLM. Legal will ask for clarity on "completion/success criteria" for when both parties can objectively determine when the project is complete.

### AI/ML Use Case Support (April 2025)

**Source**: https://docs.google.com/document/d/1NfOdm4FqjJWxZppuzat6ZyqSfsBZwaQT/edit

> ⚠️ **Note from template**: Prior to creating a SOW for AI/ML Use Case Support, consult **Nick DiRienzo** or someone on his team to determine the applicable language.

For enablement-only engagements, this attachment is **not needed**. Instead, update the SOW directly and include the following in Section E as an additional subsection:

> 8. AI/ML Enablement. To facilitate the AI/ML enablement activities described above in Section A, the following assumptions apply:
> - Customer will co-invest time from their teams, and provide access to required personnel (developers, data scientists, etc.) and information as reasonably requested...
> - Features in Preview may run into incompatibilities or inconsistencies of libraries in Snowflake...
