from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report_utils import build_html  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Render Use Case Compliance HTML from JSON data (no Snowflake connection needed)")
    parser.add_argument("--data", default="-", help="Path to JSON data file, or - for stdin")
    parser.add_argument("--output", default=str(Path(__file__).resolve().parent.parent / "output" / "use_case_compliance_report.html"))
    args = parser.parse_args()

    if args.data == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.data).read_text()

    data = json.loads(raw)
    html = build_html(data)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(html)
    print(f"Report written to {args.output}", file=sys.stderr)
    print(f"Open with: open {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
