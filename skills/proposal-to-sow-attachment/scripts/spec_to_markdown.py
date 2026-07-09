#!/usr/bin/env python3
"""
spec_to_markdown.py — Convert a SOW JSON spec into Google-Docs-friendly markdown.

The markdown is intended for the Google Workspace MCP `create_document` tool, which
converts markdown into a formatted Google Doc (headings, bold, bullets, tables).

Because markdown table cells cannot contain line breaks, multi-line / in-cell bullet
content (e.g. "\\n\u2022 ...") is flattened to a single inline "\u2022 a \u2022 b" line.

Usage:
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/spec_to_markdown.py \
        --spec /abs/path/spec.json --output /abs/path/sow.md
"""
import argparse
import json
import sys


def flatten_cell(text):
    """Collapse in-cell newlines/bullets into one markdown-table-safe line."""
    s = str(text).replace("\r", "")
    parts = [p.strip() for p in s.split("\n") if p.strip()]
    line = " ".join(parts)
    return line.replace("|", "\\|")


def md_table(headers, rows):
    out = []
    out.append("| " + " | ".join(flatten_cell(h) for h in headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        out.append("| " + " | ".join(flatten_cell(c) for c in r) + " |")
    out.append("")
    return out


def block_to_md(b):
    t = b.get("type")
    if t == "paragraph":
        num = b.get("num")
        prefix = f"**{num}**  " if num else ""
        return [prefix + b["text"], ""]
    if t == "subheading":
        num = b.get("num")
        label = f"{num}  {b['text']}" if num else b["text"]
        return [f"### {label}", ""]
    if t == "bullets":
        return [f"- {it}" for it in b["items"]] + [""]
    if t == "numbered":
        lines = []
        for it in b["items"]:
            num = it.get("num", "")
            bold = it.get("bold", "")
            text = it.get("text", "")
            head = " ".join(x for x in [num, bold] if x)
            if head and text:
                lines.append(f"**{head}.** {text}")
            elif head:
                lines.append(f"**{head}**")
            else:
                lines.append(text)
        return lines + [""]
    if t == "table":
        return md_table(b["headers"], b["rows"])
    if t == "signature":
        lines = []
        for party in b["parties"]:
            lines.append(f"**{party}**")
            lines.append("")
            for lbl in ["Signature: ____________________________",
                        "Name: ____________________________",
                        "Title: ____________________________",
                        "Date: ____________________________"]:
                lines.append(lbl + "  ")
            lines.append("")
        return lines
    raise ValueError(f"Unknown block type: {t}")


def spec_to_markdown(spec):
    md = []
    cover = spec.get("cover", {})
    if cover.get("title"):
        md += [f"# {cover['title']}", ""]
    if cover.get("subtitle"):
        md += [f"**{cover['subtitle']}**", ""]
    for lbl, val in cover.get("meta", []):
        md += [f"**{lbl}** {val}", ""]
    if cover.get("note"):
        md += [f"*{cover['note']}*", ""]
    md += ["---", ""]

    for i, section in enumerate(spec.get("sections", []), 1):
        md += [f"## {i}. {section['heading']}", ""]
        for b in section.get("blocks", []):
            md += block_to_md(b)
    return "\n".join(md).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Convert SOW JSON spec to markdown for Google Docs")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output", help="Output .md path (default: stdout)")
    args = ap.parse_args()

    with open(args.spec) as f:
        spec = json.load(f)
    md = spec_to_markdown(spec)

    if args.output:
        with open(args.output, "w") as f:
            f.write(md)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
