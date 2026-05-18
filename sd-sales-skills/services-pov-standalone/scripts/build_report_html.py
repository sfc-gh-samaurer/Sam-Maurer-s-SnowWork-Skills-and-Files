#!/usr/bin/env python3
"""
build_report_html.py - Convert an Account Discovery markdown report to styled HTML.

Uses Snowflake brand guidelines (colors, fonts, layout).

Usage:
    python <SKILL_DIR>/scripts/build_report_html.py \
        --input <markdown_file> --output <html_file>
"""

import argparse
import re
import html as html_lib


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def md_to_html(md_text):
    lines = md_text.split("\n")
    out = []
    in_table = False
    in_code = False
    in_ul = False
    in_blockquote = False
    table_rows = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            return ""
        header = table_rows[0]
        body = table_rows[2:] if len(table_rows) > 2 else []
        h = "<table><thead><tr>"
        for cell in header:
            h += f"<th>{cell.strip().strip('*')}</th>"
        h += "</tr></thead><tbody>"
        for row in body:
            h += "<tr>"
            for cell in row:
                h += f"<td>{cell.strip().strip('*')}</td>"
            h += "</tr>"
        h += "</tbody></table>"
        table_rows = []
        in_table = False
        return h

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            in_ul = False
            return "</ul>"
        return ""

    def flush_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            in_blockquote = False
            return "</div>"
        return ""

    def inline_format(text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
        return text

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_table:
                out.append(flush_table())
            if in_ul:
                out.append(flush_ul())
            if in_code:
                out.append("</pre></div>")
                in_code = False
            else:
                in_code = True
                out.append('<div class="code-block"><pre>')
            continue

        if in_code:
            out.append(html_lib.escape(line))
            continue

        if stripped.startswith(">"):
            if in_table:
                out.append(flush_table())
            if in_ul:
                out.append(flush_ul())
            content = stripped.lstrip(">").strip()
            if not in_blockquote:
                in_blockquote = True
                css_class = "talking-points" if "talking point" in content.lower() else "quick-win-card" if "quick win" in content.lower() else "talking-points"
                out.append(f'<div class="{css_class}">')
            content = inline_format(content)
            if content:
                out.append(f"<p>{content}</p>")
            continue
        elif in_blockquote:
            out.append(flush_blockquote())

        if stripped.startswith("|") and stripped.endswith("|"):
            if in_ul:
                out.append(flush_ul())
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            continue
        elif in_table:
            out.append(flush_table())

        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                in_ul = True
                out.append("<ul>")
            content = stripped[2:]
            content = inline_format(content)
            out.append(f"<li>{content}</li>")
            continue
        elif re.match(r'^\d+\.\s', stripped):
            if not in_ul:
                in_ul = True
                out.append("<ol>")
            content = re.sub(r'^\d+\.\s', '', stripped)
            content = inline_format(content)
            out.append(f"<li>{content}</li>")
            continue
        elif in_ul:
            tag = "</ol>" if "<ol>" in "\n".join(out[-20:]) else "</ul>"
            out.append(tag)
            in_ul = False

        if stripped == "---":
            out.append("<hr>")
            continue

        if stripped.startswith("######"):
            text = stripped[6:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            out.append(f"<h6>{text}</h6>")
        elif stripped.startswith("#####"):
            text = stripped[5:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            out.append(f"<h5>{text}</h5>")
        elif stripped.startswith("####"):
            text = stripped[4:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            out.append(f"<h4>{text}</h4>")
        elif stripped.startswith("###"):
            text = stripped[3:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            out.append(f"<h3>{text}</h3>")
        elif stripped.startswith("##"):
            text = stripped[2:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            section_id = slugify(text)
            out.append(f'<h2 id="{section_id}">{text}</h2>')
        elif stripped.startswith("#"):
            text = stripped[1:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            out.append(f"<h1>{text}</h1>")
        elif stripped:
            text = inline_format(stripped)
            out.append(f"<p>{text}</p>")

    if in_table:
        out.append(flush_table())
    if in_ul:
        out.append(flush_ul())
    if in_blockquote:
        out.append(flush_blockquote())
    if in_code:
        out.append("</pre></div>")

    return "\n".join(out)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap" rel="stylesheet">
<style>
:root {{
  --snow-blue: #29B5E8;
  --mid-blue: #11567F;
  --iceberg: #003545;
  --winter: #24323D;
  --star-blue: #71D3DC;
  --valencia: #FF9F36;
  --purple-moon: #7D44CF;
  --first-light: #D45B90;
  --windy-city: #8A999E;
  --bg: #FAFBFC;
  --card-bg: #FFFFFF;
  --border: #E2E8F0;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg);
  color: var(--winter);
  line-height: 1.65;
  font-size: 15px;
}}
.header {{
  background: linear-gradient(135deg, var(--iceberg) 0%, var(--mid-blue) 100%);
  color: white;
  padding: 48px 0 40px;
  position: relative;
  overflow: hidden;
}}
.header::before {{
  content: '';
  position: absolute;
  top: -50%; right: -20%;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(41,181,232,0.15) 0%, transparent 70%);
  border-radius: 50%;
}}
.header-inner {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 32px;
  position: relative;
  z-index: 1;
}}
.logo-bar {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  opacity: 0.9;
}}
.logo-bar svg {{ width: 32px; height: 32px; }}
.logo-bar span {{ font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }}
.header h1 {{
  font-size: 36px;
  font-weight: 900;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}}
.header .subtitle {{
  font-size: 18px;
  color: var(--star-blue);
  font-weight: 400;
}}
.header .meta {{
  margin-top: 16px;
  font-size: 13px;
  color: var(--windy-city);
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}}
.header .meta span {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
}}
.tam-badge {{
  display: inline-block;
  background: rgba(41,181,232,0.2);
  border: 1px solid rgba(41,181,232,0.4);
  color: var(--snow-blue);
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 20px;
  font-weight: 700;
  margin-top: 20px;
}}
nav.toc {{
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 12px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
nav.toc .toc-inner {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
}}
nav.toc::-webkit-scrollbar {{ display: none; }}
nav.toc a {{
  white-space: nowrap;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: var(--mid-blue);
  text-decoration: none;
  border: 1px solid var(--border);
  transition: all 0.2s;
}}
nav.toc a:hover {{
  background: var(--snow-blue);
  color: white;
  border-color: var(--snow-blue);
}}
.container {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px;
}}
.section {{
  background: var(--card-bg);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
h2 {{
  font-size: 24px;
  font-weight: 900;
  color: var(--iceberg);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 3px solid var(--snow-blue);
  letter-spacing: -0.3px;
}}
h3 {{
  font-size: 18px;
  font-weight: 700;
  color: var(--mid-blue);
  margin: 24px 0 12px;
}}
h4 {{
  font-size: 15px;
  font-weight: 700;
  color: var(--iceberg);
  margin: 20px 0 8px;
}}
p {{ margin-bottom: 12px; }}
strong {{ color: var(--iceberg); }}
code {{ background: #EDF2F7; padding: 2px 6px; border-radius: 4px; font-size: 13px; font-family: 'SF Mono', 'Fira Code', monospace; color: var(--mid-blue); }}
hr {{
  border: none;
  height: 1px;
  background: var(--border);
  margin: 8px 0;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 13px;
}}
thead th {{
  background: var(--iceberg);
  color: white;
  padding: 10px 14px;
  text-align: left;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
tbody td {{
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
tbody tr:nth-child(even) {{ background: #F8FAFC; }}
tbody tr:hover {{ background: #EEF4F8; }}
ul, ol {{
  margin: 8px 0 12px 20px;
}}
li {{
  margin-bottom: 6px;
  line-height: 1.6;
}}
.code-block {{
  background: var(--iceberg);
  color: var(--star-blue);
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  overflow-x: auto;
  font-size: 11px;
  line-height: 1.5;
}}
.code-block pre {{
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
  white-space: pre;
}}
.metrics-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin: 16px 0;
}}
.metric-card {{
  background: linear-gradient(135deg, #F0F8FF 0%, #FAFBFC 100%);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}}
.metric-card .label {{
  font-size: 11px;
  font-weight: 700;
  color: var(--windy-city);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}}
.metric-card .value {{
  font-size: 22px;
  font-weight: 900;
  color: var(--iceberg);
}}
.score-badge {{
  display: inline-block;
  background: var(--snow-blue);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}}
.use-case-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.priority-high {{ background: #E53E3E; }}
.priority-med {{ background: var(--valencia); }}
.priority-low {{ background: var(--windy-city); }}
.talking-points {{
  background: linear-gradient(135deg, #FFFBEB 0%, #FFF7E0 100%);
  border-left: 4px solid var(--valencia);
  border-radius: 0 8px 8px 0;
  padding: 16px 20px;
  margin: 16px 0;
  font-size: 14px;
}}
.talking-points strong {{ color: var(--valencia); }}
.quick-win-card {{
  background: linear-gradient(135deg, #F0FFF4 0%, #FAFBFC 100%);
  border: 1px solid #C6F6D5;
  border-left: 4px solid #38A169;
  border-radius: 0 8px 8px 0;
  padding: 16px 20px;
  margin: 12px 0;
}}
.quick-win-card strong {{ color: #276749; }}
.health-summary {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 20px 0;
}}
.health-card {{
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  border-top: 3px solid var(--snow-blue);
}}
.health-card .health-label {{
  font-size: 11px;
  font-weight: 700;
  color: var(--windy-city);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}}
.health-card .health-value {{
  font-size: 20px;
  font-weight: 900;
  color: var(--iceberg);
}}
.health-card .health-signal {{
  font-size: 11px;
  color: var(--windy-city);
  margin-top: 4px;
}}
.one-pager {{
  border: 2px solid var(--snow-blue);
  border-radius: 12px;
  padding: 32px;
  page-break-after: always;
}}
.footer {{
  text-align: center;
  padding: 32px;
  color: var(--windy-city);
  font-size: 12px;
}}
.footer .sf-logo {{ color: var(--snow-blue); font-weight: 700; }}
@media (max-width: 768px) {{
  .header h1 {{ font-size: 24px; }}
  .container {{ padding: 16px; }}
  .section {{ padding: 20px; }}
  .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .health-summary {{ grid-template-columns: 1fr; }}
  nav.toc .toc-inner {{ padding: 0 16px; }}
}}
@media print {{
  nav.toc {{ display: none; }}
  .header {{ padding: 24px 0; }}
  .header h1 {{ font-size: 24px; }}
  .tam-badge {{ font-size: 16px; }}
  .container {{ padding: 0; }}
  .section {{
    break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ddd;
    margin-bottom: 12px;
    padding: 20px;
  }}
  body {{ font-size: 11px; line-height: 1.5; }}
  table {{ font-size: 10px; }}
  .code-block {{ font-size: 9px; padding: 12px; }}
  h2 {{ font-size: 18px; }}
  h3 {{ font-size: 14px; }}
  .one-pager {{ page-break-after: always; }}
  a {{ color: inherit; text-decoration: none; }}
}}
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <div class="logo-bar">
      <svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g fill="#29B5E8" fill-rule="nonzero" transform="translate(0, 0.53)">
          <path d="M37.26 33.13l-9.18-5.3c-1.29-.74-2.94-.3-3.68.99-.29.51-.4 1.07-.35 1.61v10.36c0 1.48 1.2 2.68 2.69 2.68 1.48 0 2.68-1.2 2.68-2.68v-5.96l5.14 2.97c1.29.75 2.94.3 3.68-.99.75-1.29.3-2.94-.99-3.68"/>
          <path d="M14.44 21.77c.02-.96-.48-1.85-1.31-2.33L3.95 14.14c-.4-.23-.86-.35-1.31-.35-.94 0-1.82.5-2.28 1.32-.73 1.26-.3 2.87.95 3.6l5.29 3.05-5.29 3.05c-.61.35-1.05.92-1.23 1.6-.18.68-.09 1.39.26 2 .47.81 1.35 1.31 2.28 1.31.46 0 .92-.12 1.32-.35l9.18-5.3c.82-.47 1.32-1.36 1.31-2.31"/>
          <path d="M6.03 10.39l9.18 5.3c1.07.62 2.39.42 3.23-.41.54-.49.87-1.2.87-1.98V2.69C19.31 1.2 18.11 0 16.63 0c-1.48 0-2.69 1.2-2.69 2.69v6.04l-5.21-3.01c-1.29-.75-2.94-.3-3.68.99-.75 1.29-.3 2.94.99 3.68"/>
          <path d="M26.67 22.2c0 .2-.12.48-.26.63l-3.64 3.64c-.14.14-.43.26-.63.26h-.93c-.2 0-.49-.12-.63-.26l-3.64-3.64c-.15-.15-.26-.43-.26-.63v-.93c0-.2.12-.49.26-.63l3.64-3.64c.14-.15.43-.26.63-.26h.93c.2 0 .49.12.63.26l3.64 3.64c.14.14.26.43.26.63v.93zm-3.25-.45v-.04c0-.15-.09-.35-.19-.46l-1.07-1.07c-.11-.11-.32-.2-.47-.2h-.04c-.15 0-.35.09-.46.2l-1.07 1.07c-.11.11-.2.32-.2.46v.04c0 .15.09.36.2.46l1.07 1.07c.11.11.32.2.46.2h.04c.15 0 .36-.09.46-.2l1.07-1.07c.11-.11.2-.32.2-.46z"/>
          <path d="M28.09 15.69l9.18-5.3c1.29-.74 1.73-2.39.99-3.68-.75-1.29-2.39-1.73-3.68-.99l-5.14 2.97V2.69C29.43 1.2 28.22 0 26.74 0c-1.48 0-2.69 1.2-2.69 2.69v10.41c-.05.54.06 1.1.35 1.61.75 1.29 2.39 1.73 3.68.99"/>
          <path d="M17.05 27.52c-.61-.12-1.26-.02-1.84.31l-9.18 5.3c-1.29.74-1.73 2.39-.99 3.68.75 1.29 2.39 1.73 3.68.99l5.21-3.01v5.99c0 1.48 1.2 2.69 2.69 2.69 1.48 0 2.68-1.2 2.68-2.69V30.17c0-1.34-.98-2.45-2.26-2.65"/>
          <path d="M43 15.08c-.74-1.29-2.39-1.73-3.68-.99l-9.18 5.3c-.88.51-1.36 1.44-1.35 2.38-.01.94.48 1.86 1.35 2.36l9.18 5.3c1.29.74 2.94.3 3.68-.99.75-1.29.3-2.94-.99-3.68l-5.2-3 5.2-3c1.29-.74 1.73-2.39.99-3.68"/>
        </g>
      </svg>
      <span>Snowflake</span>
    </div>
    <h1>{company}</h1>
    <div class="subtitle">Account Discovery & Use Case Analysis</div>
    <div class="meta">
      <span>{date}</span>
      <span>{industry}</span>
      <span>CONFIDENTIAL</span>
    </div>
    <div class="tam-badge">Estimated TAM: {tam_range}</div>
  </div>
</div>

<nav class="toc">
  <div class="toc-inner">
{nav_links}
  </div>
</nav>

<div class="container">
{content}
</div>

<div class="footer">
  <span class="sf-logo">SNOWFLAKE</span> &middot; Account Discovery & Use Case Analysis &middot; {date} &middot; Confidential
</div>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Convert Account Discovery markdown to styled HTML")
    parser.add_argument("--input", required=True, help="Path to markdown file")
    parser.add_argument("--output", required=True, help="Output HTML path")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        md_text = f.read()

    title_match = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
    company = "Company"
    if title_match:
        raw = title_match.group(1).strip()
        company = raw.split(" - ")[0].strip() if " - " in raw else raw

    date_match = re.search(r'\*\*Date:\*\*\s*([^|\n]+)', md_text)
    date_str = date_match.group(1).strip().rstrip('*').strip() if date_match else "2026"

    industry_match = re.search(r'\*\*Industry:\*\*\s*([^|\n]+)', md_text)
    industry = industry_match.group(1).strip().rstrip('*').strip() if industry_match else ""

    dash = r'[\u2013\u2014\-]'
    tam_patterns = [
        r'\*{0,2}Estimated Total TAM\*{0,2}[:\s|]*\s*\*{0,2}(\$[\d.,]+[A-Za-z]*\s*' + dash + r'\s*\$?[\d.,]+[A-Za-z]*)',
        r'(?:\*{0,2})(?:Estimated Snowflake TAM|Total Estimated TAM|Estimated TAM)(?:\*{0,2})[:\s]*\s*(\$[\d.,]+[A-Za-z]*\s*' + dash + r'\s*\$[\d.,]+[A-Za-z]*)',
        r'(?:Snowflake TAM|Estimated TAM)[^$]*?\*{0,2}(\$[\d.,]+[A-Za-z]*\s*' + dash + r'\s*\$[\d.,]+[A-Za-z]*)',
        r'(?:Estimated|Total)\s+(?:Snowflake\s+)?(?:Total\s+)?TAM[:\s|]*\s*(\$[\d.,]+[A-Za-z]*\s*' + dash + r'\s*\$?[\d.,]+[A-Za-z]*)',
        r'(\$[\d.,]+[A-Za-z]*\s*' + dash + r'\s*\$[\d.,]+[A-Za-z]*)\s*(?:Data\s*[&]\s*Analytics\s*)?TAM',
        r'Total Snowflake TAM[^$]*?(\$[\d.,]+[A-Za-z]*\s*' + dash + r'\s*\$?[\d.,]+[A-Za-z]*)',
        r'(?:Conservative|Mid|Realistic)\s+TAM\s*\|?\s*(\$[\d.,]+[A-Za-z]*)',
    ]
    tam_match = None
    for pat in tam_patterns:
        tam_match = re.search(pat, md_text, re.MULTILINE)
        if tam_match:
            break
    tam_range = tam_match.group(1).strip().strip('|').strip('*').strip() if tam_match else "TBD"

    h2_headings = re.findall(r'^##\s+(.+)', md_text, re.MULTILINE)
    short_labels = {
        "executive summary": "Executive Summary",
        "company profile": "Company Profile",
        "it spending": "IT Spending",
        "it & data spending": "IT Spending",
        "data landscape": "Data Landscape",
        "key data pipeline": "Pipelines",
        "data architecture": "Architecture",
        "tech stack": "Tech Stack",
        "feature adoption": "Features",
        "consumption": "Consumption",
        "tam estimation": "TAM",
        "tam ": "TAM",
        "gap analysis": "TAM",
        "c-suite": "Org Chart",
        "organizational chart": "Org Chart",
        "org chart": "Org Chart",
        "domain ownership": "Domain Owners",
        "power center": "Power Center",
        "use case pipeline": "Pipeline",
        "top 5 use case": "Use Cases",
        "top use case": "Use Cases",
        "quick win": "Quick Wins",
        "immediate action": "Quick Wins",
        "proposal": "Proposals",
        "demo plan": "Demos",
        "demo strategy": "Demos",
        "executive one-pager": "One-Pager",
        "appendix": "Appendix",
    }
    nav_links_list = []
    for h in h2_headings:
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', h).strip()
        slug = slugify(clean)
        label = clean
        for key, short in short_labels.items():
            if key in clean.lower():
                label = short
                break
        nav_links_list.append(f'    <a href="#{slug}">{label}</a>')
    nav_links = "\n".join(nav_links_list)

    body_html = md_to_html(md_text)

    sections = re.split(r'(<h2[^>]*>)', body_html)
    wrapped = []
    i = 0
    while i < len(sections):
        if sections[i].startswith('<h2'):
            content = sections[i]
            if i + 1 < len(sections):
                content += sections[i + 1]
                i += 1
            next_start = len(content)
            wrapped.append(f'<div class="section">{content}</div>')
        else:
            if sections[i].strip():
                wrapped.append(sections[i])
        i += 1

    final_content = "\n".join(wrapped)

    result = HTML_TEMPLATE.format(
        title=f"{company} - Account Discovery & Use Case Analysis",
        company=company,
        date=date_str,
        industry=industry,
        tam_range=tam_range,
        nav_links=nav_links,
        content=final_content,
    )

    with open(args.output, "w") as f:
        f.write(result)

    print(f"HTML saved: {args.output}")


if __name__ == "__main__":
    main()
