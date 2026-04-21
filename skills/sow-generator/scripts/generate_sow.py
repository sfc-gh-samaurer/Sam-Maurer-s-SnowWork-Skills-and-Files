#!/usr/bin/env python3
"""
Snowflake PS SOW Document Generator

Generates a properly formatted .docx SOW Attachment 1 matching the
Snowflake PS template specification.

Usage:
    python generate_sow.py <json_input_path> <output_path>

The JSON input must conform to the SOW schema (see SKILL.md for details).
"""

import importlib.util
import json
import sys
import os
from datetime import date
from docx import Document
from docx.shared import Pt, Inches, Emu, Twips
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


# ── Formatting Constants (from MERGED template) ──────────────────────────
FONT_NAME = "Arial"
FONT_SIZE = Pt(7.5)  # 95250 EMU
PAGE_WIDTH = 7772400   # 8.5 in
PAGE_HEIGHT = 10058400  # 11 in
MARGIN_LR = 457200     # 0.5 in
MARGIN_TOP = 337185     # ~0.37 in
MARGIN_BOTTOM = 640080  # 0.7 in
TABLE_WIDTH_DXA = 10800
LINE_SPACING = 170  # twips, ~0.85 line spacing


def create_document():
    """Create a blank document with correct page setup."""
    doc = Document()

    # Page setup
    section = doc.sections[0]
    section.page_width = PAGE_WIDTH
    section.page_height = PAGE_HEIGHT
    section.left_margin = MARGIN_LR
    section.right_margin = MARGIN_LR
    section.top_margin = MARGIN_TOP
    section.bottom_margin = MARGIN_BOTTOM

    # Remove default empty paragraph
    if doc.paragraphs:
        p = doc.paragraphs[0]._element
        p.getparent().remove(p)

    return doc


def set_run_format(run, bold=False):
    """Apply standard font formatting to a run."""
    run.font.name = FONT_NAME
    run.font.size = FONT_SIZE
    run.bold = bold
    # Force Arial for East Asian text too
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{FONT_NAME}" w:hAnsi="{FONT_NAME}" w:eastAsia="{FONT_NAME}" w:cs="{FONT_NAME}"/>')
        rPr.insert(0, rFonts)
    else:
        rFonts.set(qn('w:ascii'), FONT_NAME)
        rFonts.set(qn('w:hAnsi'), FONT_NAME)
        rFonts.set(qn('w:eastAsia'), FONT_NAME)
        rFonts.set(qn('w:cs'), FONT_NAME)


def set_paragraph_spacing(paragraph):
    """Apply standard line spacing to a paragraph."""
    pPr = paragraph._p.get_or_add_pPr()
    spacing = pPr.find(qn('w:spacing'))
    if spacing is None:
        spacing = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="{LINE_SPACING}" w:lineRule="auto"/>')
        pPr.append(spacing)
    else:
        spacing.set(qn('w:before'), '0')
        spacing.set(qn('w:after'), '0')
        spacing.set(qn('w:line'), str(LINE_SPACING))
        spacing.set(qn('w:lineRule'), 'auto')


def add_heading(doc, text, level=1):
    """Add a heading paragraph. Level 1 = bold, Level 2 = non-bold."""
    para = doc.add_paragraph()
    set_paragraph_spacing(para)
    run = para.add_run(text)
    set_run_format(run, bold=(level == 1))
    return para


def add_body_text(doc, text, bold=False):
    """Add a body text paragraph."""
    para = doc.add_paragraph()
    set_paragraph_spacing(para)
    run = para.add_run(text)
    set_run_format(run, bold=bold)
    return para


def add_blank_line(doc):
    """Add an empty paragraph as a spacer."""
    para = doc.add_paragraph()
    set_paragraph_spacing(para)
    return para


def add_bullet(doc, text):
    """Add a bullet point using Unicode bullet character."""
    para = doc.add_paragraph()
    set_paragraph_spacing(para)
    run = para.add_run(f"\u2022 {text}")
    set_run_format(run)
    return para


def set_table_borders(table):
    """Apply black single-line borders to a table."""
    tbl = table._tbl
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        tbl.insert(0, tblPr)

    # Remove existing borders
    existing = tblPr.find(qn('w:tblBorders'))
    if existing is not None:
        tblPr.remove(existing)

    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)


def set_table_width(table, width_dxa=TABLE_WIDTH_DXA):
    """Set table to full page width."""
    tbl = table._tbl
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        tbl.insert(0, tblPr)

    tblW = tblPr.find(qn('w:tblW'))
    if tblW is None:
        tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="{width_dxa}" w:type="dxa"/>')
        tblPr.append(tblW)
    else:
        tblW.set(qn('w:w'), str(width_dxa))
        tblW.set(qn('w:type'), 'dxa')


def format_table_cell(cell, text, bold=False):
    """Format a table cell with standard text."""
    # Clear existing content
    for p in cell.paragraphs:
        if p.text:
            for run in p.runs:
                run.text = ""

    para = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
    set_paragraph_spacing(para)

    if isinstance(text, list):
        # Multi-line cell content (e.g., bullet lists within cells)
        for i, item in enumerate(text):
            if i > 0:
                para = cell.add_paragraph()
                set_paragraph_spacing(para)
            run = para.add_run(str(item))
            set_run_format(run, bold=bold)
    else:
        run = para.add_run(str(text))
        set_run_format(run, bold=bold)


def add_table(doc, headers, rows, header_bold=True, col_widths=None):
    """Add a formatted table with headers and data rows."""
    num_cols = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    set_table_borders(table)
    set_table_width(table)

    # Header row
    for ci, header_text in enumerate(headers):
        format_table_cell(table.rows[0].cells[ci], header_text, bold=header_bold)

    # Data rows
    for ri, row_data in enumerate(rows):
        for ci, cell_text in enumerate(row_data):
            if ci < num_cols:
                format_table_cell(table.rows[ri + 1].cells[ci], cell_text)

    # Column widths
    if col_widths:
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                if ci < len(col_widths):
                    tc = cell._tc
                    tcPr = tc.find(qn('w:tcPr'))
                    if tcPr is None:
                        tcPr = parse_xml(f'<w:tcPr {nsdecls("w")}/>')
                        tc.insert(0, tcPr)
                    tcW = tcPr.find(qn('w:tcW'))
                    if tcW is None:
                        tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{col_widths[ci]}" w:type="dxa"/>')
                        tcPr.append(tcW)
                    else:
                        tcW.set(qn('w:w'), str(col_widths[ci]))

    return table


# ── Section Generators ────────────────────────────────────────────────────

def gen_section_header(doc, number, title):
    """Generate a numbered section header."""
    add_blank_line(doc)
    if number:
        add_heading(doc, f"{number}. {title.upper()}", level=1)
    else:
        add_heading(doc, title.upper(), level=1)


def gen_scope_of_services(doc, data):
    """Section 1: Scope of Services."""
    gen_section_header(doc, None, "SCOPE OF SERVICES")
    add_blank_line(doc)

    scope = data.get("scope_of_services", {})

    # 1.1 Executive Summary
    add_heading(doc, "1.1 Executive Summary", level=2)
    add_blank_line(doc)
    for para_text in scope.get("executive_summary", []):
        add_body_text(doc, para_text)
        add_blank_line(doc)

    # Expected Business Outcomes (optional table or bullets)
    outcomes = scope.get("business_outcomes", [])
    if outcomes:
        add_body_text(doc, "Expected Business Outcomes:", bold=True)
        if isinstance(outcomes[0], dict):
            rows = [[o.get("outcome", ""), o.get("description", "")] for o in outcomes]
            add_table(doc, ["Outcome", "Description"], rows)
        else:
            for o in outcomes:
                add_bullet(doc, o)
        add_blank_line(doc)

    # 1.2 Our Understanding
    understanding = scope.get("our_understanding", {})
    if understanding:
        add_heading(doc, "1.2 Our Understanding", level=2)
        for para_text in understanding.get("paragraphs", []):
            add_body_text(doc, para_text)

        challenges = understanding.get("challenges", [])
        if challenges:
            add_blank_line(doc)
            rows = [[c.get("challenge", ""), c.get("description", "")] for c in challenges]
            add_table(doc, ["Challenge", "Description"], rows)

        solution_paragraphs = understanding.get("solution_paragraphs", [])
        if solution_paragraphs:
            add_blank_line(doc)
            add_body_text(doc, "Snowflake Solution:", bold=True)
            for para_text in solution_paragraphs:
                add_body_text(doc, para_text)

        solution_components = understanding.get("solution_components", [])
        if solution_components:
            rows = [[c.get("component", ""), c.get("description", "")] for c in solution_components]
            add_table(doc, ["Component", "Description"], rows)
        add_blank_line(doc)

    # 1.3 Methodology and Engagement Approach
    methodology = scope.get("methodology", {})
    if methodology:
        add_heading(doc, "1.3 Methodology and Engagement Approach", level=2)
        add_blank_line(doc)
        for para_text in methodology.get("paragraphs", []):
            add_body_text(doc, para_text)
            add_blank_line(doc)

        for phase in methodology.get("phases", []):
            add_body_text(doc, phase.get("title", ""), bold=True)
            for para_text in phase.get("paragraphs", []):
                add_body_text(doc, f"\t{para_text}")
            for item in phase.get("activities", []):
                add_bullet(doc, item)
            add_blank_line(doc)


def gen_milestones(doc, data):
    """Section 2: Outcomes and Acceptance Criteria (milestone table)."""
    gen_section_header(doc, "2", "OUTCOMES AND ACCEPTANCE CRITERIA")
    milestones_data = data.get("milestones", {})
    intro = milestones_data.get("intro", "The following table sets forth the milestones, deliverables, and acceptance criteria for this engagement.")
    add_body_text(doc, intro)
    add_blank_line(doc)

    engagement_type = data.get("engagement_type", "fixed_fee")
    milestones = milestones_data.get("items", [])

    if engagement_type == "fixed_fee":
        headers = ["Milestone", "Payment", "Description", "Deliverable"]
        col_widths = [2200, 1200, 4000, 3400]
        rows = []
        for m in milestones:
            rows.append([
                m.get("name", ""),
                m.get("payment", ""),
                m.get("description", ""),
                m.get("deliverable", "")
            ])
        add_table(doc, headers, rows, col_widths=col_widths)
    else:
        # T&M: milestones without payment column
        headers = ["Milestone", "Description", "Deliverable"]
        col_widths = [2400, 4400, 4000]
        rows = []
        for m in milestones:
            rows.append([
                m.get("name", ""),
                m.get("description", ""),
                m.get("deliverable", "")
            ])
        add_table(doc, headers, rows, col_widths=col_widths)
    add_blank_line(doc)


def gen_acceptance_process(doc, data):
    """Section 3: Acceptance Process."""
    gen_section_header(doc, "3", "ACCEPTANCE PROCESS")

    acceptance = data.get("acceptance_process", {})
    subsections = acceptance.get("subsections", [])

    for sub in subsections:
        number = sub.get("number", "")
        title = sub.get("title", "")
        add_heading(doc, f"{number} {title}", level=2)
        for para_text in sub.get("paragraphs", []):
            add_body_text(doc, para_text)
        add_blank_line(doc)


def gen_key_scope_items(doc, data):
    """Section 4: Key Scope Items."""
    gen_section_header(doc, "4", "KEY SCOPE ITEMS")

    scope_items = data.get("key_scope_items", {})

    # In-scope table
    in_scope = scope_items.get("in_scope", [])
    if in_scope:
        add_heading(doc, "4.1 Deliverables", level=2)
        add_blank_line(doc)
        headers = ["Phase", "Scope Item"]
        rows = [[item.get("phase", ""), item.get("scope_item", "")] for item in in_scope]
        add_table(doc, headers, rows, col_widths=[3600, 7200])
        add_blank_line(doc)

    # Out-of-scope — supports both flat strings and structured objects
    out_scope = scope_items.get("out_of_scope", [])
    if out_scope:
        add_heading(doc, "4.2 Out-of-Scope Activities", level=2)
        add_blank_line(doc)
        if isinstance(out_scope[0], dict):
            # Structured format: numbered subsections with title + description
            headers = ["#", "Item", "Description"]
            rows = [[item.get("number", str(i + 1)), item.get("title", ""), item.get("description", "")] for i, item in enumerate(out_scope)]
            add_table(doc, headers, rows, header_bold=False, col_widths=[1000, 3000, 6800])
        else:
            # Simple string format (backward compatible)
            headers = ["#", "Out-of-Scope Item"]
            rows = [[str(i + 1), item] for i, item in enumerate(out_scope)]
            add_table(doc, headers, rows, header_bold=False, col_widths=[800, 10000])
        add_blank_line(doc)


def gen_raci(doc, data):
    """Section 5: RACI and Work Products."""
    gen_section_header(doc, "5", "RESPONSIBILITY ASSIGNMENT (RACI)")

    raci_data = data.get("raci", {})

    # 5.1 RACI intro
    intro = raci_data.get("intro", "")
    if intro:
        add_heading(doc, "5.1 RACI Matrix", level=2)
        add_body_text(doc, intro)
        # Accountability note (e.g., "Customer is Accountable (A) for every activity")
        accountability_note = raci_data.get("accountability_note", "")
        if accountability_note:
            add_body_text(doc, accountability_note, bold=True)
        add_blank_line(doc)

    # RACI table
    raci_items = raci_data.get("items", [])
    if raci_items:
        headers = ["Activity", "Responsible (R)", "Accountable (A)", "Consulted (C)", "Informed (I)"]
        rows = []
        for item in raci_items:
            # Support phase header rows (bold, spans conceptually)
            if item.get("is_phase_header"):
                rows.append([item.get("activity", ""), "", "", "", ""])
            else:
                rows.append([
                    item.get("activity", ""),
                    item.get("responsible", ""),
                    item.get("accountable", ""),
                    item.get("consulted", ""),
                    item.get("informed", "")
                ])
        add_table(doc, headers, rows, header_bold=False, col_widths=[3600, 1800, 1800, 1800, 1800])
        add_blank_line(doc)

    # 5.2 Work Products
    work_products = raci_data.get("work_products", [])
    if work_products:
        add_heading(doc, "5.3 Work Products", level=2)
        add_blank_line(doc)
        headers = ["Phase", "Work Product", "Primary Owner"]
        rows = [[wp.get("phase", ""), wp.get("work_product", ""), wp.get("owner", "")] for wp in work_products]
        add_table(doc, headers, rows, header_bold=False, col_widths=[2400, 5400, 3000])
        add_blank_line(doc)


def gen_roles(doc, data):
    """Section 6: Roles and Responsibilities."""
    gen_section_header(doc, "6", "ROLES AND RESPONSIBILITIES")

    roles_data = data.get("roles", {})

    # Snowflake roles
    sf_roles = roles_data.get("snowflake", [])
    if sf_roles:
        add_heading(doc, "6.1 Snowflake Team", level=2)
        add_blank_line(doc)
        headers = ["Role", "Responsibilities"]
        rows = [[r.get("role", ""), r.get("responsibilities", "")] for r in sf_roles]
        add_table(doc, headers, rows, header_bold=False, col_widths=[3000, 7800])
        add_blank_line(doc)

    # Customer roles
    cust_roles = roles_data.get("customer", [])
    if cust_roles:
        add_heading(doc, "6.2 Customer Team", level=2)
        add_blank_line(doc)
        headers = ["Role", "Responsibilities"]
        rows = [[r.get("role", ""), r.get("responsibilities", "")] for r in cust_roles]
        add_table(doc, headers, rows, col_widths=[3000, 7800])
        add_blank_line(doc)


def gen_governance(doc, data):
    """Section 7: Project Governance."""
    gen_section_header(doc, "7", "PROJECT GOVERNANCE")

    governance = data.get("governance", {})
    intro = governance.get("intro", "")
    if intro:
        add_body_text(doc, intro)
        add_blank_line(doc)

    # 7.1 Project Alignment (optional subsection)
    alignment = governance.get("alignment", {})
    if alignment:
        add_heading(doc, "7.1 Project Alignment", level=2)
        for para_text in alignment.get("paragraphs", []):
            add_body_text(doc, para_text)
        add_blank_line(doc)

    forums = governance.get("forums", [])
    if forums:
        if alignment:
            add_heading(doc, "7.2 Governance Forums", level=2)
            add_blank_line(doc)
        headers = ["Forum", "Cadence", "Key Participants", "Responsibility", "Materials"]
        rows = [[
            f.get("forum", ""),
            f.get("cadence", ""),
            f.get("participants", ""),
            f.get("responsibility", ""),
            f.get("materials", "")
        ] for f in forums]
        add_table(doc, headers, rows, col_widths=[2000, 1600, 2400, 2400, 2400])
        add_blank_line(doc)


def gen_assumptions(doc, data):
    """Section 8: Assumptions."""
    gen_section_header(doc, "8", "ASSUMPTIONS")

    assumptions = data.get("assumptions", [])
    if assumptions:
        headers = ["#", "Assumption"]
        rows = []
        for i, a in enumerate(assumptions):
            if isinstance(a, dict):
                # Structured format: {"number": "8.1", "assumption": "..."}
                rows.append([a.get("number", str(i + 1)), a.get("assumption", "")])
            else:
                # Simple string format (backward compatible)
                rows.append([str(i + 1), a])
        add_table(doc, headers, rows, col_widths=[800, 10000])
        add_blank_line(doc)


def gen_dependencies(doc, data):
    """Section 9: Dependencies."""
    gen_section_header(doc, "9", "DEPENDENCIES")

    deps = data.get("dependencies", [])
    if deps:
        headers = ["#", "Dependency", "Required By"]
        rows = [[str(i + 1), d.get("dependency", ""), d.get("required_by", "")] for i, d in enumerate(deps)]
        add_table(doc, headers, rows, col_widths=[800, 7000, 3000])
        add_blank_line(doc)


def gen_risks(doc, data):
    """Section 10: Risks."""
    gen_section_header(doc, "10", "RISKS AND MITIGATIONS")

    risks = data.get("risks", [])
    if risks:
        headers = ["#", "Risk", "Impact", "Likelihood", "Mitigation"]
        rows = [[
            str(i + 1),
            r.get("risk", ""),
            r.get("impact", ""),
            r.get("likelihood", ""),
            r.get("mitigation", "")
        ] for i, r in enumerate(risks)]
        add_table(doc, headers, rows, header_bold=False, col_widths=[600, 3000, 1800, 1800, 3600])
        add_blank_line(doc)


def gen_access_security(doc, data):
    """Section 11: Access and Security."""
    gen_section_header(doc, "11", "ACCESS AND SECURITY REQUIREMENTS")

    security = data.get("access_security", {})
    paragraphs = security.get("paragraphs", [])
    for p in paragraphs:
        add_body_text(doc, p)
    if paragraphs:
        add_blank_line(doc)

    items = security.get("items", [])
    for item in items:
        add_bullet(doc, item)
    if items:
        add_blank_line(doc)


def gen_change_management(doc, data):
    """Section 12: Change Management."""
    gen_section_header(doc, "12", "CHANGE MANAGEMENT")

    cm = data.get("change_management", {})
    for para_text in cm.get("paragraphs", []):
        add_body_text(doc, para_text)
        add_blank_line(doc)


def gen_fees(doc, data):
    """Section 13: Fees."""
    gen_section_header(doc, "13", "PROFESSIONAL SERVICES FEES")

    fees = data.get("fees", {})
    engagement_type = data.get("engagement_type", "fixed_fee")

    for para_text in fees.get("paragraphs", []):
        add_body_text(doc, para_text)
        add_blank_line(doc)

    if engagement_type == "fixed_fee":
        # Payment schedule table
        payments = fees.get("payment_schedule", [])
        if payments:
            headers = ["Milestone", "Payment Percentage"]
            rows = [[p.get("milestone", ""), p.get("percentage", "")] for p in payments]
            add_table(doc, headers, rows, col_widths=[5400, 5400])
            add_blank_line(doc)

        total = fees.get("total", "")
        if total:
            add_body_text(doc, f"Total Fixed Fee: {total}", bold=True)
            add_blank_line(doc)
    else:
        # T&M: rate card or phase-based
        rate_card = fees.get("rate_card", [])
        if rate_card:
            headers = ["Role", "Rate"]
            rows = [[r.get("role", ""), r.get("rate", "")] for r in rate_card]
            add_table(doc, headers, rows, col_widths=[5400, 5400])
            add_blank_line(doc)

        phases = fees.get("phases", [])
        if phases:
            headers = ["Phase", "Estimated Hours", "Estimated Cost"]
            rows = [[p.get("phase", ""), p.get("hours", ""), p.get("cost", "")] for p in phases]
            add_table(doc, headers, rows, col_widths=[4000, 3400, 3400])
            add_blank_line(doc)

        total = fees.get("total", "")
        not_to_exceed = fees.get("not_to_exceed", "")
        if total:
            add_body_text(doc, f"Estimated Total: {total}", bold=True)
        if not_to_exceed:
            add_body_text(doc, f"Not-to-Exceed: {not_to_exceed}", bold=True)
        if total or not_to_exceed:
            add_blank_line(doc)


def gen_term(doc, data):
    """Section 14: Term."""
    gen_section_header(doc, "14", "TERM")

    term = data.get("term", {})
    for para_text in term.get("paragraphs", []):
        add_body_text(doc, para_text)
        add_blank_line(doc)


def gen_general_provisions(doc, data):
    """Section 15: General Provisions."""
    gen_section_header(doc, "15", "GENERAL PROVISIONS")

    provisions = data.get("general_provisions", {})
    for para_text in provisions.get("paragraphs", []):
        add_body_text(doc, para_text)
        add_blank_line(doc)


def gen_signatures(doc, data):
    """Section 16: Signatures."""
    gen_section_header(doc, "16", "SIGNATURES")

    sigs = data.get("signatures", {})
    customer_name = data.get("customer_name", "Customer")
    intro = sigs.get("intro", f"IN WITNESS WHEREOF, the parties have executed this SOW as of the date last signed below.")
    add_body_text(doc, intro)
    add_blank_line(doc)

    # Snowflake signature block
    headers_sf = ["", ""]
    rows_sf = [
        ["Signature:", "_________________________________"],
        ["Name:", "_________________________________"],
        ["Title:", "_________________________________"],
        ["Date:", "_________________________________"],
    ]
    add_body_text(doc, "SNOWFLAKE INC.", bold=True)
    add_table(doc, ["Signature:", "_________________________________"], [
        ["Name:", "_________________________________"],
        ["Title:", "_________________________________"],
        ["Date:", "_________________________________"],
    ], header_bold=False, col_widths=[5400, 5400])
    add_blank_line(doc)

    # Customer signature block
    add_body_text(doc, customer_name.upper(), bold=True)
    add_table(doc, ["Signature:", "_________________________________"], [
        ["Name:", "_________________________________"],
        ["Title:", "_________________________________"],
        ["Date:", "_________________________________"],
    ], header_bold=False, col_widths=[5400, 5400])


def _load_attachment_generator():
    """Load generate_project_attachments.py from the same scripts directory."""
    path = os.path.join(os.path.dirname(__file__), "generate_project_attachments.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("generate_project_attachments", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate_sow(data, output_path):
    """Main generation function."""
    doc = create_document()

    # Title
    add_heading(doc, "SOW ATTACHMENT 1", level=1)
    add_blank_line(doc)

    customer_name = data.get("customer_name", "Customer")
    sow_title = data.get("sow_title", f"Statement of Work — {customer_name}")
    add_body_text(doc, sow_title, bold=True)
    add_blank_line(doc)

    # Generate each section based on what's present in data
    section_generators = [
        ("scope_of_services", gen_scope_of_services),
        ("milestones", gen_milestones),
        ("acceptance_process", gen_acceptance_process),
        ("key_scope_items", gen_key_scope_items),
        ("raci", gen_raci),
        ("roles", gen_roles),
        ("governance", gen_governance),
        ("assumptions", gen_assumptions),
        ("dependencies", gen_dependencies),
        ("risks", gen_risks),
        ("access_security", gen_access_security),
        ("change_management", gen_change_management),
        ("fees", gen_fees),
        ("term", gen_term),
        ("general_provisions", gen_general_provisions),
        ("signatures", gen_signatures),
    ]

    for key, gen_func in section_generators:
        if key in data:
            gen_func(doc, data)

    doc.save(output_path)

    # Auto-generate project attachments if keys are present
    attachments = []
    att_mod = _load_attachment_generator()
    if att_mod:
        out_dir    = os.path.dirname(output_path)
        customer   = data.get("customer_name", "Customer").replace(" ", "_")
        today      = date.today().strftime("%Y-%m-%d")

        if "dmva_attachment" in data:
            att_path = os.path.join(out_dir, f"{customer}_DMVA_Attachment_{today}.docx")
            att_mod.generate_dmva_attachment(data["dmva_attachment"], att_path)
            attachments.append(att_path)

        if "code_conversion_attachment" in data:
            att_path = os.path.join(out_dir, f"{customer}_CodeConversion_Attachment_{today}.docx")
            att_mod.generate_code_conv_attachment(data["code_conversion_attachment"], att_path)
            attachments.append(att_path)

    return output_path, attachments


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_sow.py <json_input_path> <output_path>")
        print("  json_input_path: Path to JSON file with SOW content")
        print("  output_path: Path for the output .docx file")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(json_path):
        print(f"Error: Input file not found: {json_path}")
        sys.exit(1)

    with open(json_path, 'r') as f:
        data = json.load(f)

    result, attachments = generate_sow(data, output_path)
    print(f"SOW generated: {result}")
    for att in attachments:
        print(f"Attachment generated: {att}")


if __name__ == "__main__":
    main()
