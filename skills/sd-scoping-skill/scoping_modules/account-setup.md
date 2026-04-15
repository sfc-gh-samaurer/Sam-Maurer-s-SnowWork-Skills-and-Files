## Acccount Setup & RBAC 

### Focus Areas 
- Org / account strategy (single vs multi-account, regions, editions) 
- SSO / IdP integration (e.g., Entra/Okta), MFA 
- SCIM / group sync strategy (who owns which groups) 
- Definition of platform admin roles, functional roles, access/database roles, service/project roles 
- Naming standards and inheritance patterns (e.g., admin > write > read)
- Least-privilege model, managed schemas vs unmanaged, database roles vs direct grants
- Pattern for DEV/TEST/PROD accounts, segregation of duties, break-glass roles 
- Choice and setup of RBAC automation (Terraform, internal SPs, Permifrost/RBGM, etc.)

### Key Objects 
- Organization, accounts, regions, editions
- Users, SCIM groups / roles mapped from IdP 
- Network policies, session policies, password policies 
- Platform/admin roles (platform ops, security admin, user admin) 
- Database roles / access roles (DB_READ, DB_WRITE, SCHEMA_READ, etc.) 
- Service / integration roles for ETL, BI tools, AI apps
- Databases, schemas (MANAGED ACCESS), database roles
- Warehouses and warehouse grants
- Row access policies, masking policies, tag-based masking, classification tags
- Secure shares, reader accounts, data clean rooms RBAC alignment 

### Risk Areas
- Over-Privileged Access
- Direct Object Grants / DAC Sprawl
- Inconsistent Role Patterns
- Compliance & SoD
- Lack of Automation / Drift
- Role Explosion / Role Per User
- Private Link
- VPS , Gov regions 

### Complexity driver  

- Number of Snowflake Accounts / Environments
- Business Domain & Persona Breadth ( of business domains / data products, # of distinct personas ,
analyst, engineer, ops, finance, etc.)
- Regulatory & Compliance Requirements , SOX, PCI, HIPAA, GDPR, data residency, internal security controls
- Legacy RBAC to Map / Migrate . Greenfield vs heavy legacy (DB roles, AD groups, custom RLS, per-table grants)
- Identity Landscape . Single IdP vs multiple IdPs; SCIM availability; maturity of group taxonomy 
- Security Features in Scope. Basic RBAC only vs RBAC + RLS/CLS + masking + tags + data classification
- Automation Expectations . Manual SQL + some templates vs full IaC/CI-CD for RBAC (Terraform, internal SPs, Permifrost/RBGM).
- Zero/Low Downtime Migration Needs. Need to re-platform RBAC in PROD with minimal downtime, coordinated cutovers, and rollback – major multiplier.


### Typical Phases 

- Phase 0 – Discovery & Assessment
- Phase 1 – Target RBAC Design & Governance Model
- Phase 2 – Foundation Setup (Account & Core Roles)
- Phase 3 – Automation & Rollout per Domain/Environment
- Phase 4 – Migration & Cutover of Existing Access
- Phase 5 – Handover, Runbooks & KT


#### Phase 0 – Discovery & Assessment
- Activities:
     Current-state review: roles, grants, schemas, IdP integration, JML, compliance requirements.
     Inventory of personas, data domains, sensitive data, existing pain points.
- Ownership:
     Customer: environment access, SMEs, current docs.
     Snowflake/Partner : questionnaires, analysis, findings.


#### Phase 1 – Target RBAC Design & Governance Model
- Activities:
     Define target role taxonomy (platform, functional, DB roles, service roles).
     Define environment strategy & SoD patterns.
     Define request/approval/review processes, role ownership, and naming standards.
- Ownership:
     Snowflake/Partner (lead): design options, best practices.
     Customer: approve model, align with internal policies, nominate role owners.


#### Phase 2 – Foundation Setup (Account & Core Roles)
- Activities:
     Configure org/account settings relevant to security (network policies, MFA requirements, etc.).
     Normalize system role usage; establish platform admin roles.
     Implement base functional + DB roles and privilege templates in lower env(s).
- Ownership:
     Snowflake/Partner  (lead): design + implementation scripts.
     Customer: review/approve, validate access patterns.

#### Phase 3 – Automation & Rollout per Domain/Environment
- Activities:
     Implement RBAC automation (SPs, Terraform, Permifrost/RBGM, CI/CD).
     Onboard priority domains: create DB roles, schema roles, functional roles, mappings.
     Implement RLS/CLS/masking + tags where in scope.
- Ownership:
     Snowflake/Partner (lead): patterns, automation, initial rollout.
     Customer: domain SMEs provide rules, run UAT.

#### Phase 4 – Migration & Cutover of Existing Access
- Activities:
     Map old roles/groups to new model; create migration plan.
     Execute revokes / grants, transfer ownership, enable managed schemas.
     Coordinate cutover windows and fallbacks.
- Ownership:
     Snowflake/Partner (lead): migration scripts, execution, support.
     Customer: blackout approval, business validation, communication.

#### Phase 5 – Handover, Runbooks & KT
- Activities:
     Finalize runbooks (how to request/change roles, onboard new domains, audit).
     KT sessions for platform admins, security, and domain owners.
     Post-go-live support / hypercare window.
- Ownership:
     Snowflake/Partner (lead): documentation, KT, hypercare.
     Customer: accept ownership, integrate into internal processes/tools.


### Effort Baseline 

#### Small – Single Account, Limited Domains (S)
- Assumptions:
     1 Snowflake account, 1–2 environments (e.g., non-prod + prod).
     ≤3 business domains, ≤5 personas.
     Basic RBAC (system + functional + DB roles), no complex RLS/CLS.
     Single IdP, basic SSO, minimal legacy to migrate.
- Indicative effort
     Snowflake/Partner : ~24–40 hours (3–5 days)
     Discovery & design: 8–12h
     Implementation & testing (lower env + prod): 12–20h
     KT & docs: 4–8h
     Customer: ~16–24 hours (workshops, decisions, UAT).

#### Medium – Multi-Env, Multiple Domains (M)
- Assumptions:
     1–3 accounts (DEV/TEST/PROD or multi-BU).
     4–8 domains, 6–12 personas.
     DB roles + schema roles, some RLS/CLS + masking on sensitive data.
     SCIM integration, more legacy roles/groups to rationalize.
     Light automation (SQL scripts + some IaC).
- Indicative effort
      Snowflake/Partner: ~64–120 hours (8–15 days)
     Discovery & design: 16–24h
     Implementation & automation setup: 32–64h
     Migration & cutover: 16–24h
     KT & docs: 8–12h
     Customer: ~40–80 hours (SMEs, security, UAT, governance setup).

#### Large / Complex – Multi-Account, Regulated, Heavily Automated (L+)
- Assumptions:
     Multi-account org (prod/non-prod, regional accounts, data products).
     Many domains/personas; strict compliance (SOX, PCI, HIPAA, etc.).
     Full “Pure RBAC”-style implementation: managed schemas, DB roles everywhere.
     Rich RLS/CLS/masking/tagging; deep integration with HR/IAM and ticketing.
     Full IaC / CI-CD; zero/low-downtime migration of significant legacy.
- Indicative effort
     Snowflake/Partner: 160–320+ hours (20–40+ days), often multi-sprint.
     Customer: comparable internal effort across IAM, security, data platform, and business.

