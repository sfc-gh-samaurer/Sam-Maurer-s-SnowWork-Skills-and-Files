## SOW Spec Schema

`build_sow.py` renders a `.docx` from a single JSON object. Sections auto-number
(`1.`, `2.`, ...) in array order — do **not** put the leading section number in
`heading`. Sub-numbering inside a section (e.g. `2.1`, `11.3`) is supplied
explicitly by you in block fields so it stays aligned with the auto section number.

### Top-level

```json
{
  "output": "/abs/path/Client_SOW_Attachment.docx",
  "theme": { "navy": "11567F", "accent": "29B5E8" },
  "footer": "Confidential — Snowflake Professional Services | <Client> SOW Attachment",
  "cover": { ... },
  "sections": [ { "heading": "...", "blocks": [ ... ] } ]
}
```

- `output` — absolute path. Can be overridden with the `--output` CLI flag.
- `theme` — optional hex overrides. Keys: `navy`, `accent`, `body`, `grey`,
  `hdr_bg`, `alt_bg`, `line`, `font`. Defaults are Snowflake brand.
- `footer` — optional centered footer text.

### cover

```json
{
  "title": "STATEMENT OF WORK — ATTACHMENT A",
  "subtitle": "Scope of Services: <Client> — <Engagement>",
  "meta": [["Provider:", "Snowflake Inc. — Professional Services"],
           ["Client:", "<Client>, Inc."],
           ["Term:", "16 Weeks from confirmed Kickoff (Week 1)"]],
  "note": "This Attachment is incorporated into and governed by the Order Form and MSA ..."
}
```

### Block types (inside `sections[].blocks`)

| type | fields | renders |
|------|--------|---------|
| `paragraph` | `text`, optional `num` | body paragraph; `num` prefixes a bold navy label (e.g. `14.1`) |
| `subheading` | `num` (optional), `text` | bold navy sub-heading (e.g. `1.1  Our Understanding`) |
| `bullets` | `items` (string[]) | bulleted list |
| `numbered` | `items`: `[{num, bold, text}]` | definition-style numbered list; `bold` and `text` optional |
| `table` | `headers` (string[]), `rows` (string[][]), optional `widths` (inches, float[]), `header_size`, `body_size` | branded table, navy header row, zebra body. Use `\n` + `•` inside a cell for in-cell bullets |
| `signature` | `parties` (string[]) | signature block, one column per party |

### Conventions for a legal SOW attachment

- Formalize numerals: "sixteen (16) weeks", "three (3) sessions".
- Add an MSA/Order-Form incorporation clause in `cover.note`.
- Frame effort hours as estimates supporting a fixed fee, not a T&M commitment.
- Reference the acceptance/review window (e.g. five business days) where deliverables are accepted.
- Ensure milestone payments sum exactly to the total fixed fee.
