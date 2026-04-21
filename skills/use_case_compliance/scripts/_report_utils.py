from __future__ import annotations

from datetime import datetime


def _esc(val) -> str:
    return str(val or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_table_rows(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        active = r.get("IS_PROJECT_ACTIVE")
        if isinstance(active, bool):
            active_str = str(active)
        else:
            active_str = str(active or "")
        active_class = "active-yes" if active_str.lower() == "true" else "active-no"
        mid = _esc(r.get("MILESTONE_ID") or "")
        sf_url = f"https://snowforce.lightning.force.com/lightning/r/pse__Milestone__c/{mid}/view"
        owner_email = _esc(r.get('OWNER_EMAIL') or '')
        owner_email_td = f'<a href="mailto:{owner_email}" style="color:var(--accent);text-decoration:none;">{owner_email}</a>' if owner_email else ''
        lines.append(
            f"<tr>"
            f'<td><a href="{sf_url}" target="_blank" style="color:var(--accent);text-decoration:none;">{mid}</a></td>'
            f"<td>{_esc(r.get('MILESTONE_NAME') or '')}</td>"
            f"<td>{_esc(r.get('PROJECT_NAME') or '')}</td>"
            f"<td>{_esc(r.get('PROJECT_MANAGER') or '')}</td>"
            f"<td>{_esc(r.get('OWNER_NAME') or '')}</td>"
            f"<td>{_esc(r.get('OWNER_ROLE') or '')}</td>"
            f"<td>{owner_email_td}</td>"
            f"<td>{_esc(r.get('ACCOUNT_NAME') or '')}</td>"
            f"<td>{_esc(r.get('MILESTONE_STATUS') or '')}</td>"
            f"<td>{_esc(r.get('USE_CASE_ID') or '')}</td>"
            f"<td>{_esc(r.get('REASON') or '')}</td>"
            f'<td class="{active_class}">{active_str}</td>'
            f"</tr>"
        )
    return "\n".join(lines)


def _build_pm_options(rows: list[dict]) -> str:
    pms = sorted({str(r.get("PROJECT_MANAGER") or "").strip() for r in rows if r.get("PROJECT_MANAGER")})
    return "\n".join(f'<option value="{_esc(pm)}">{_esc(pm)}</option>' for pm in pms)


def build_html(data: dict) -> str:
    rows = data["milestones"]
    summary = data.get("summary", {})
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    blank = summary.get("BLANK_USE_CASE_ID", "?")
    invalid = summary.get("INVALID_USE_CASE_ID", "?")

    active_count = sum(1 for r in rows if str(r.get("IS_PROJECT_ACTIVE") or "").lower() == "true")
    inactive_count = len(rows) - active_count
    total_rows = len(rows)

    pm_options = _build_pm_options(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Use Case Compliance Report</title>
<script>
(function(){{
  document.documentElement.setAttribute('data-theme', 'dark');
}})();
</script>
<style>
:root {{
    --bg: #fafafa; --surface: #ffffff; --border: #e0e0e0;
    --text: #424242; --text-muted: #757575; --accent: #11567f;
}}
[data-theme="dark"] {{
    --bg: #0f1117; --surface: #1a1d27; --border: #2d3140;
    --text: #e0e0e0; --text-muted: #8b8fa3; --accent: #29b5e8;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; padding: 24px; }}
.header {{ text-align: center; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }}
.header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
.header .subtitle {{ color: var(--text-muted); font-size: 14px; }}
.stats {{ display: flex; gap: 16px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }}
.stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; text-align: center; min-width: 130px; }}
.stat .val {{ font-size: 24px; font-weight: 700; color: var(--accent); }}
.stat .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.4px; color: var(--text-muted); margin-top: 2px; }}
.filter-bar {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }}
.filter-bar label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }}
.filter-bar select {{ background: var(--surface); border: 1px solid var(--border); color: var(--text); border-radius: 6px; padding: 6px 32px 6px 10px; font-size: 13px; cursor: pointer; appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M6 8L1 3h10z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; min-width: 220px; }}
.filter-bar select:focus {{ outline: none; border-color: var(--accent); }}
.filter-clear {{ background: none; border: 1px solid var(--border); color: var(--text-muted); border-radius: 6px; padding: 6px 10px; font-size: 12px; cursor: pointer; display: none; }}
.filter-clear:hover {{ border-color: var(--accent); color: var(--accent); }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th {{ text-align: left; padding: 8px 10px; background: var(--surface); border-bottom: 2px solid var(--border); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.4px; color: var(--text-muted); cursor: pointer; user-select: none; white-space: nowrap; }}
th:hover {{ color: var(--accent); }}
td {{ padding: 7px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
tr:hover {{ background: rgba(41,181,232,0.06); }}
.active-yes {{ color: #4caf50; font-weight: 600; }}
.active-no {{ color: var(--text-muted); }}
.table-summary {{ font-size: 12px; color: var(--text-muted); margin-top: 6px; }}
.footer {{ text-align: center; color: var(--text-muted); font-size: 11px; padding-top: 20px; margin-top: 24px; border-top: 1px solid var(--border); }}
.theme-toggle {{ position: absolute; top: 16px; right: 16px; background: rgba(128,128,128,0.15); border: 1px solid rgba(128,128,128,0.25); color: var(--text-muted); border-radius: 20px; padding: 5px 12px; font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: background 0.2s; }}
.theme-toggle:hover {{ background: rgba(128,128,128,0.3); }}
.theme-toggle .icon {{ font-size: 14px; }}
.daa-logo {{ position: absolute; top: 10px; left: 0; height: 32px; width: auto; }}
[data-theme="dark"] .daa-logo {{ filter: brightness(0) invert(1); }}
</style>
</head>
<body>

<div class="header" style="position:relative">
    <img class="daa-logo" src="data:image/png;base64,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" alt="Powered by DAA">
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
        <span class="icon" id="theme-icon">&#9788;</span>
        <span id="theme-label">Light</span>
    </button>
    <h1>Use Case Compliance Report</h1>
    <div class="subtitle">PS Milestones with type "Use Case" missing a valid Use Case ID &middot; Generated {generated_at}</div>
</div>

<div class="stats">
    <div class="stat"><div class="val" id="stat-noncompliant">{total_rows}</div><div class="label">Non-Compliant</div></div>
    <div class="stat"><div class="val" id="stat-blank">{blank}</div><div class="label">Blank ID</div></div>
    <div class="stat"><div class="val" id="stat-invalid">{invalid}</div><div class="label">Invalid ID</div></div>
</div>

<div class="filter-bar">
    <label for="pm-filter">Project Manager</label>
    <select id="pm-filter" onchange="filterTable()">
        <option value="">All Project Managers</option>
        {pm_options}
    </select>
    <button class="filter-clear" id="filter-clear" onclick="clearFilter()">&#x2715; Clear</button>
</div>

<table id="tbl-compliance">
    <thead><tr>
        <th onclick="sortTable('tbl-compliance',0)">Milestone ID</th>
        <th onclick="sortTable('tbl-compliance',1)">Milestone Name</th>
        <th onclick="sortTable('tbl-compliance',2)">Project Name</th>
        <th onclick="sortTable('tbl-compliance',3)">Project Manager</th>
        <th onclick="sortTable('tbl-compliance',4)">Owner Name</th>
        <th onclick="sortTable('tbl-compliance',5)">Owner Role</th>
        <th onclick="sortTable('tbl-compliance',6)">Owner Email</th>
        <th onclick="sortTable('tbl-compliance',7)">Account Name</th>
        <th onclick="sortTable('tbl-compliance',8)">Milestone Status</th>
        <th onclick="sortTable('tbl-compliance',9)">Use Case ID</th>
        <th onclick="sortTable('tbl-compliance',10)">Reason</th>
        <th onclick="sortTable('tbl-compliance',11)">Active Project</th>
    </tr></thead>
    <tbody>{build_table_rows(rows)}</tbody>
</table>
<div class="table-summary" id="tbl-summary">{total_rows} non-compliant milestones &middot; {active_count} on active projects &middot; {inactive_count} on inactive projects</div>

<div class="footer">
    Use Case Compliance Report &middot; SNOW_CERTIFIED.PROFESSIONAL_SERVICES &middot; SNOW_CERTIFIED.SALESFORCE_USE_CASE
</div>

<script>
var TOTAL_ROWS = {total_rows};
var ORIG_BLANK = {blank};
var ORIG_INVALID = {invalid};

function filterTable() {{
    var pm = document.getElementById('pm-filter').value;
    var tbody = document.querySelector('#tbl-compliance tbody');
    var allRows = Array.from(tbody.querySelectorAll('tr'));
    var visible = 0;
    var activeVisible = 0;
    var blankCount = 0;
    var invalidCount = 0;
    allRows.forEach(function(row) {{
        var rowPM = row.cells[3] ? row.cells[3].textContent.trim() : '';
        var show = !pm || rowPM === pm;
        row.style.display = show ? '' : 'none';
        if (show) {{
            visible++;
            var reason = row.cells[10] ? row.cells[10].textContent.trim() : '';
            if (reason === 'Blank Use Case ID') blankCount++;
            else if (reason === 'Invalid Use Case ID') invalidCount++;
            var activeCell = row.cells[11] ? row.cells[11].textContent.trim().toLowerCase() : '';
            if (activeCell === 'true') activeVisible++;
        }}
    }});
    var clearBtn = document.getElementById('filter-clear');
    clearBtn.style.display = pm ? 'inline-block' : 'none';
    document.getElementById('stat-noncompliant').textContent = pm ? visible : TOTAL_ROWS;
    document.getElementById('stat-blank').textContent = pm ? blankCount : ORIG_BLANK;
    document.getElementById('stat-invalid').textContent = pm ? invalidCount : ORIG_INVALID;
    var summary = document.getElementById('tbl-summary');
    if (pm) {{
        var inactiveVisible = visible - activeVisible;
        summary.textContent = visible + ' of ' + TOTAL_ROWS + ' non-compliant milestones \u00b7 ' + activeVisible + ' on active projects \u00b7 ' + inactiveVisible + ' on inactive projects';
    }} else {{
        summary.textContent = TOTAL_ROWS + ' non-compliant milestones \u00b7 {active_count} on active projects \u00b7 {inactive_count} on inactive projects';
    }}
}}

function clearFilter() {{
    document.getElementById('pm-filter').value = '';
    filterTable();
}}

function sortTable(tableId, colIdx) {{
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const dir = table.dataset.sortCol == colIdx && table.dataset.sortDir === 'asc' ? 'desc' : 'asc';
    table.dataset.sortCol = colIdx;
    table.dataset.sortDir = dir;
    rows.sort((a, b) => {{
        let aVal = a.cells[colIdx]?.textContent.trim() || '';
        let bVal = b.cells[colIdx]?.textContent.trim() || '';
        const aNum = parseFloat(aVal.replace(/[$,KM]/g, ''));
        const bNum = parseFloat(bVal.replace(/[$,KM]/g, ''));
        if (!isNaN(aNum) && !isNaN(bNum)) {{
            return dir === 'asc' ? aNum - bNum : bNum - aNum;
        }}
        return dir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }});
    rows.forEach(r => tbody.appendChild(r));
}}

function toggleTheme() {{
    var el = document.documentElement;
    var cur = el.getAttribute('data-theme');
    var next = (cur === 'dark') ? 'light' : 'dark';
    el.setAttribute('data-theme', next);
    document.getElementById('theme-icon').innerHTML = (next === 'dark') ? '&#9788;' : '&#9790;';
    document.getElementById('theme-label').textContent = (next === 'dark') ? 'Light' : 'Dark';
}}
</script>
</body>
</html>"""
