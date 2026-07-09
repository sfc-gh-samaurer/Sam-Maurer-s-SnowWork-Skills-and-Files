#!/usr/bin/env python3
"""
gdoc_fill_requests.py — Emit Docs API batchUpdate requests to fill ONE native table.

Given the structure of a freshly-inserted empty table (from get_document_structure)
and the desired content, this prints a JSON array of requests that:
  - insert each cell's text (processed in DESCENDING start index so indices stay valid),
  - bold the header row (row 0).

Cells are filled back-to-front so that every insertText uses an index that is still
valid from the single structure snapshot. Header styling is paired with its own insert;
later lower-index inserts shift the styled text but preserve the run styling.

Usage:
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/gdoc_fill_requests.py \
        --table-json /abs/path/table.json --content-json /abs/path/content.json

  table.json   : one table object from get_document_structure, e.g. {"rows": [[{row,col,startIndex,...}]]}
  content.json : {"headers": [...], "rows": [[...]]}  (rows excludes the header)
"""
import argparse
import json


def build_requests(table, content):
    headers = content["headers"]
    data_rows = content["rows"]

    cells = []
    for row in table["rows"]:
        for cell in row:
            cells.append(cell)

    def text_for(r, c):
        if r == 0:
            return headers[c] if c < len(headers) else ""
        dr = data_rows[r - 1] if (r - 1) < len(data_rows) else []
        return dr[c] if c < len(dr) else ""

    requests = []
    for cell in sorted(cells, key=lambda x: x["startIndex"], reverse=True):
        r, c, idx = cell["row"], cell["col"], cell["startIndex"]
        txt = str(text_for(r, c))
        if not txt:
            continue
        requests.append({"insertText": {"location": {"index": idx}, "text": txt}})
        if r == 0:
            requests.append({"updateTextStyle": {
                "range": {"startIndex": idx, "endIndex": idx + len(txt)},
                "textStyle": {"bold": True},
                "fields": "bold",
            }})
    return requests


def main():
    ap = argparse.ArgumentParser(description="Emit Docs API requests to fill a native table")
    ap.add_argument("--table-json", required=True)
    ap.add_argument("--content-json", required=True)
    args = ap.parse_args()

    with open(args.table_json) as f:
        table = json.load(f)
    with open(args.content_json) as f:
        content = json.load(f)

    print(json.dumps(build_requests(table, content), ensure_ascii=False))


if __name__ == "__main__":
    main()
