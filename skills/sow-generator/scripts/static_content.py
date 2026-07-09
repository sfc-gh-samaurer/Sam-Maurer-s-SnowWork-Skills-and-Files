"""
Snowflake PS SOW — Static Boilerplate Content

LEGAL TEXT VERSION — update this when legal approves any boilerplate change.
All generated SOWs embed this version in the document footer comment so reviewers
can verify which legal text revision was used.
"""

LEGAL_TEXT_VERSION = "2026-Q2"
LEGAL_TEXT_DATE    = "June 2026"

"""

All verbatim text for the Order Form Exhibit sections.
Text is sourced directly from the JD Power v5 SOW (canonical reference).
Placeholders use {key} Python format syntax for dynamic substitution.

Section map (lettered headers — A through I):
  A  Description of Technical Services
  B  Custom Fixed Fee                    [dynamic: per-attachment text list]
  C  Training Funds                      [dynamic: {training_amount}]
  D  Payments and Expenses
  E  Scheduling and Term                 [dynamic: {engagement_duration}]
  F  Snowflake Access                    [F.1 dynamic: source/target environments]
  G  Additional Terms                    [G.5 dynamic if subcontractor]
  H  Fixed Fee Engagement Terms          [OPTIONAL — Assumption Validation Checkpoint]
  I  Subcontractor Technical Services    [OPTIONAL — partner name parameterized]

Subsection format: {SectionLetter}.{SubsectionNumber}
  e.g. F.1 Scope of Snowflake Access, G.1 Governing Terms
"""

# ── Header and Preamble ───────────────────────────────────────────────────────

HEADER = 'Order Form Exhibit - TECHNICAL SERVICES SOW'

PREAMBLE_P1 = (
    'This Statement of Work (\u201cStatement of Work\u201d or \u201cSOW\u201d) sets forth '
    'the terms and conditions for the Technical Services to be provided hereunder by '
    'Snowflake. This SOW is effective and binding as of the Effective Date set forth '
    'in the applicable Order Form.'
)

PREAMBLE_P2 = (
    'As used in this SOW, (i) \u201cCustomer\u201d or \u201c{customer_name}\u201d means '
    'the entity specified in the Order Form that is purchasing Technical Services; '
    '(ii) \u201cOrder Form\u201d means the Snowflake-approved ordering document to which '
    'this SOW is attached; (iii) \u201cAgreement\u201d means the agreement between the '
    'parties governing the Order Form; and (iv) \u201cTerm\u201d means the period of '
    'performance set forth in the Order Form.'
)

# ── A. Description of Technical Services ─────────────────────────────────────

SECTION_A_TITLE = 'A.  Description of Technical Services'

SECTION_A_BODY = (
    'Snowflake will provide Customer with the Technical Services specified in this SOW '
    'subject to the descriptions, terms and conditions herein, the Agreement, and the '
    'applicable quantities, pricing, hours, timelines, and other terms set forth in the '
    'Order Form.'
)

# ── B. Custom Fixed Fee ───────────────────────────────────────────────────────

SECTION_B_TITLE = 'B.  Custom Fixed Fee'

SECTION_B_INTRO = (
    'Snowflake will provide the Technical Services specified in the Attachments below '
    'on a fixed fee basis, subject to the terms and conditions of this SOW and each '
    'attachment.'
)

# Per-attachment bold labels + description lines generated dynamically from
# attachments[].title and attachments[].brief_description in the JSON input.

# ── C. Training Funds ─────────────────────────────────────────────────────────

SECTION_C_TITLE = 'C.  Training Funds'

# Substitutes: {training_amount}, {training_expiry}
SECTION_C_BODY = (
    'As part of this engagement, the fees include Snowflake University training credits '
    'in the amount of {training_amount} (\u201cTraining Funds\u201d). Training Funds may '
    'be applied toward Snowflake University instructor-led or on-demand training courses '
    'and certifications during the Term. Training Funds must be used within {training_expiry} '
    'of the engagement Effective Date, are non-transferable, and have no cash value.'
)

SECTION_C_AMOUNT_DEFAULT = '$[TBD]'
SECTION_C_EXPIRY_DEFAULT = 'twelve (12) months'

# ── D. Payments and Expenses ──────────────────────────────────────────────────

SECTION_D_TITLE = 'D.  Payments and Expenses'

SECTION_D_P1 = (
    'The fees for Technical Services under this SOW are set forth in the applicable '
    'Order Form and Attachments hereto. All fees are fixed and milestone-gated as '
    'described in each Attachment. Fixed fees are inclusive of Snowflake Professional '
    'Services delivery management and practice management oversight.'
)

SECTION_D_P2 = (
    'Expenses. If estimated expenses, such as reasonable travel, hotel, or any expenses '
    'related to on-site meetings and working sessions, are incurred by Snowflake in '
    'connection with this SOW, Customer agrees to reimburse Snowflake for such expenses, '
    'provided that such travel and associated costs are authorized in writing by Customer '
    'at least one (1) month in advance.'
)

# ── E. Scheduling and Term ────────────────────────────────────────────────────

SECTION_E_TITLE = 'E.  Scheduling and Term'

# Substitutes: {engagement_duration}
SECTION_E_BODY = (
    'Technical Services under this SOW are performed during regular business hours '
    '(8am to 5pm Customer\u2019s local time), Monday through Friday, excluding public '
    'holidays. The estimated duration of this engagement is {engagement_duration} from '
    'the Effective Date. If any milestone extends beyond its target date due to '
    'Customer-caused delays, a Change Order will be required to extend support for the '
    'affected activities.'
)

SECTION_E_DURATION_DEFAULT = 'twelve (12) months'

# ── F. Snowflake Access ───────────────────────────────────────────────────────

SECTION_F_TITLE = 'F.  Snowflake Access'

F_1_HEADER = 'F.1  Scope of Snowflake Access.'

# F.1 body built dynamically — uses source_environments + target_environments from JSON
F_1_BODY_TEMPLATE = (
    'Under this SOW, Snowflake will receive access to Customer\u2019s source data '
    'environments ({source_list}), Customer\u2019s {target_env}, and any third-party '
    'systems reasonably necessary to perform the Technical Services described herein.'
)

F_1_BODY_GENERIC = (
    'Under this SOW, Snowflake will receive access to Customer\u2019s source data '
    'environments, Customer\u2019s Snowflake account(s), and any third-party systems '
    'reasonably necessary to perform the Technical Services described herein.'
)

F_2_HEADER = 'F.2  Snowflake Obligations.'

F_2_BODY = (
    'For access to Customer Assets identified in this SOW, Snowflake agrees to: '
    '(a) use Customer Data and Customer Assets solely to perform the Technical Services; '
    '(b) not disclose Customer Data to any third party except as required to perform '
    'the Technical Services; and (c) return or destroy Customer Data upon completion '
    'of the engagement.'
)

F_3_HEADER = 'F.3  Customer Obligations.'

F_3_BODY = (
    'Customer shall ensure that: (a) multi-factor authentication (MFA) is configured '
    'and enabled for all accounts to which Snowflake will have access; (b) Snowflake '
    'is provided with the minimum access required to perform the Technical Services; '
    'and (c) no medical data, PHI, PII, or other sensitive data is accessible to '
    'Snowflake beyond what is explicitly defined in the agreed data handling and '
    'masking strategy.'
)

# Appended to F.3 when production_access.needed is True
F_3_PROD_NOTE = (
    'Production environment access, where explicitly required by the scope of '
    'Technical Services, shall be limited in duration and scope to the minimum '
    'necessary for performance of the applicable services, and must be authorized '
    'in writing by the Customer Project Sponsor prior to provisioning.'
)

F_4_HEADER = 'F.4  No Access to Sensitive Data.'

F_4_BODY = (
    'Snowflake will not access, process, or migrate data that Customer has identified '
    'as out of scope for data validation or migration. Customer is solely responsible '
    'for ensuring that sensitive data is masked or excluded from all '
    'Snowflake-accessible environments.'
)

# ── G. Additional Terms ───────────────────────────────────────────────────────

SECTION_G_TITLE = 'G.  Additional Terms'

G_1_HEADER = 'G.1  Governing Terms.'

G_1_BODY = (
    'This SOW shall be governed by the Agreement as defined in the applicable Order '
    'Form. In the event of any conflict between this SOW and the Agreement, the terms '
    'of the Agreement will control unless this SOW expressly states otherwise.'
)

G_2_HEADER = 'G.2  Change Orders.'

G_2_BODY = (
    'This SOW (including any of its attachments or exhibits) may not be modified or '
    'amended except in a written amendment or change order signed by a duly authorized '
    'representative of each party. Snowflake will not commence work on any out-of-scope '
    'activities without a signed Change Order.'
)

G_3_HEADER = 'G.3  Project Management.'

G_3_BODY = (
    'Customer will ensure that a Customer project manager is assigned for the duration '
    'of the project who will coordinate all Customer activities, provide timely access '
    'to Customer resources and environments, and serve as the primary decision-making '
    'authority for Customer-owned activities.'
)

G_4_HEADER = 'G.4  Deliverables.'

G_4_BODY = (
    'All electronic and/or hard copy versions of any materials or other Deliverables '
    'provided as part of the Technical Services are intended solely for Customer\u2019s '
    'internal business use. Snowflake retains all right, title, and interest in and to '
    'its methodologies, tools, frameworks, and pre-existing intellectual property used '
    'in delivery of the Technical Services.'
)

G_5_HEADER = 'G.5  Third Party Software.'

# Used when no subcontractor is named
G_5_NO_PARTNER = (
    'Snowflake is not responsible or liable for software or components not developed '
    'by Snowflake, including third-party migration tools, partner subcontractor '
    'deliverables, or Customer-owned systems.'
)

# Used when a named subcontractor is present — substitutes {partner_name} and {attachment_reference}
G_5_WITH_PARTNER = (
    'Snowflake is not responsible or liable for software or components not developed '
    'by Snowflake, including third-party migration tools, partner subcontractor '
    'deliverables, or Customer-owned systems. {partner_name}\u2019s services are '
    'provided under {attachment_reference} as a subcontractor on Snowflake paper; '
    'Snowflake SD acts as the Architecture Authority over all {partner_name} deliverables.'
)

# ── H. Fixed Fee Engagement Terms (OPTIONAL — Assumption Validation Checkpoint) ──

SECTION_H_TITLE = 'H.  Fixed Fee Engagement Terms'

H_1_HEADER = 'H.1  Assumption Validation Checkpoint.'

# Substitutes: {trigger_milestone}, {duration}
H_AVC_BODY = (
    'Following the completion of {trigger_milestone}, the project will enter a '
    '{duration} Assumption Validation Checkpoint. During the Assumption Validation '
    'Checkpoint, the Snowflake Professional Services team will present a point of view '
    'comparing original scoping assumptions against findings from the initial discovery '
    'and conversion work, including complexity, dependency mapping, data source coverage, '
    'and any edge cases or outliers identified. Both parties will review the impact of '
    'any gaps on timeline, level of effort, and downstream milestones, and will align '
    'on a mutually agreeable path forward. Where material variances are identified, the '
    'parties will work together in good faith to adjust scope, sequencing, or estimates, '
    'and document any required scope adjustments through a change order before proceeding '
    'into the next phase of execution.'
)

H_AVC_GOVERNANCE_LABEL = 'Governance Language'

H_AVC_GOVERNANCE_BODY = (
    'The Assumption Validation Checkpoint serves as a formal governance gate within this '
    'engagement. Progression into the next phase of execution is contingent on joint '
    'sign-off by the Customer and Snowflake Professional Services on the Assumption '
    'Validation Findings document and the agreed path forward. If the parties identify '
    'material variances from the original scope, sequencing, or level of effort, work '
    'on subsequent milestones will pause until a change order is executed or both parties '
    'confirm in writing that the engagement may proceed under the original terms. '
    'Sign-off authority for the Assumption Validation Checkpoint rests with the '
    'designated Customer Project Sponsor and the Snowflake Professional Services '
    'Engagement Lead.'
)

# ── I. Subcontractor Technical Services (OPTIONAL) ───────────────────────────

SECTION_I_TITLE = 'I.  Subcontractor Technical Services'

# Substitutes: {partner_name}, {partner_role}, {attachment_reference}
I_SUBCONTRACTOR_BODY = (
    '{partner_name} is contracted on Snowflake paper as the {partner_role} for this '
    'engagement. Under Snowflake SD architecture authority oversight, {partner_name} '
    'will perform the activities described in {attachment_reference}. Snowflake SD '
    'acts as Architecture Authority over all {partner_name} deliverables and retains '
    'final sign-off authority on all quality gates and milestone acceptances.'
)
