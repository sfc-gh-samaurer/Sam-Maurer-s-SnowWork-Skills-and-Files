#!/usr/bin/env python3
"""
gdoc_plan.py — Turn a SOW JSON spec into an ordered build plan for Google Docs.

create_document's markdown table parser is unreliable for multi-table documents, so
tables must be built natively via the Docs API. This planner emits an ordered list of
items the agent renders in sequence:
  - {"kind": "md",    "text": "..."}                      -> append_to_document (markdown)
  - {"kind": "table", "headers": [...], "rows": [[...]]}  -> native Docs API table

Narrative blocks (headings, paragraphs, bullets, numbered, signature) are grouped into
"md" items; each table becomes its own "table" item. In-cell bullets are kept as inline
"• a • b" text (one paragraph per cell).

Usage:
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/gdoc_plan.py \
        --spec /abs/path/spec.json --output /abs/path/plan.json
"""
import argparse
import json
import sys

# Reuse the markdown block renderer (non-table blocks only).
from spec_to_markdown import block_to_md, flatten_cell


def build_plan(spec):
    items = []
    md_buf = []

    def flush():
        if md_buf:
            text = "\n".join(md_buf).strip("\n")
            if text.strip():
                items.append({"kind": "md", "text": text})
            md_buf.clear()

    cover = spec.get("cover", {})
    if cover.get("title"):
        md_buf += [f"# {cover['title']}", ""]
    if cover.get("subtitle"):
        md_buf += [f"**{cover['subtitle']}**", ""]
    for lbl, val in cover.get("meta", []):
        md_buf += [f"**{lbl}** {val}", ""]
    if cover.get("note"):
        md_buf += [f"*{cover['note']}*", ""]

    for i, section in enumerate(spec.get("sections", []), 1):
        md_buf += [f"## {i}. {section['heading']}", ""]
        for b in section.get("blocks", []):
            if b.get("type") == "table":
                flush()
                items.append({
                    "kind": "table",
                    "headers": [flatten_cell(h) for h in b["headers"]],
                    "rows": [[flatten_cell(c) for c in row] for row in b["rows"]],
                })
            else:
                md_buf += block_to_md(b)
    flush()
    return {"title": cover.get("title", "Statement of Work"), "items": items}


def main():
    ap = argparse.ArgumentParser(description="Build a Google Docs render plan from a SOW spec")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output", help="Output plan JSON (default: stdout)")
    args = ap.parse_args()

    with open(args.spec) as f:
        spec = json.load(f)
    plan = build_plan(spec)

    payload = json.dumps(plan, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(payload)
        n_tables = sum(1 for it in plan["items"] if it["kind"] == "table")
        print(f"Plan: {len(plan['items'])} items, {n_tables} tables -> {args.output}", file=sys.stderr)
    else:
        print(payload)


if __name__ == "__main__":
    main()
