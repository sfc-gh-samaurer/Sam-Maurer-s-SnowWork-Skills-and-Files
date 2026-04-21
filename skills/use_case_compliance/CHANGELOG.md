# use_case_compliance Changelog

## 1.0.0 (2026-03-31)

### Added
- Initial release: PS milestone use case ID compliance check
- Queries `DD_PROFESSIONAL_SERVICES_MILESTONE` for all milestones of type "Use Case"
- Left-joins `DD_SALESFORCE_USE_CASE` to classify violations as "Blank Use Case ID" or "Invalid Use Case ID"
- Self-contained HTML report with summary stats bar (total, compliant, non-compliant, blank, invalid, compliance %)
- Sortable columns, dark/light theme toggle
- Active projects sorted first; Active Project column color-coded (green = active)
- Milestone ID column is a clickable hyperlink to the Salesforce record
- `generate_report.py` — PEP 723 script, queries Snowflake, writes HTML
- `render_report.py` — offline re-render from cached JSON, no Snowflake connection
- `_report_utils.py` — shared HTML rendering utilities
- `output/.gitignore` — prevents generated reports from being committed
- Registered in `skill_registry.yml` and attached to `sales_services_delivery` profile
