# cx-project-tracking

Session tracking for Cortex Code CLI and SnowWork. Tags each session with project/milestone metadata via `QUERY_TAG` on a `SELECT 1` beacon.

## Key Constraints

- **QUERY_TAG schema is frozen (v1.6)**: `{app, customer, project_id, project, milestone_id, milestone, email, session_id}`. Do not add, remove, or rename fields.
- **connections.toml is the canonical connection source.** The `snow` CLI resolves `--connection` from `connections.toml`, not `config.toml`. All connection detection should check `connections.toml` first.
- **Binary resolution uses absolute paths**, not PATH mutation. Hook scripts read `.snow_path` and `.python3_path` files written by `install.sh`. Variables: `CX_SNOW_BIN`, `CX_PYTHON3`.
- **Sanitize all values before SQL interpolation.** Strip to `[A-Za-z0-9_-]` for identifiers, `[A-Za-z0-9_.@-]` for email. Escape single quotes as `''`.
- **Tagging is best-effort.** If `snow sql` fails, log to `.tag_log` and let the session continue. Hooks never block (`exit 0` always). Silent auto-tag fires after 5 untagged prompts.

## Session Tag Warning

Warning delivery is handled by the `UserPromptSubmit` hooks (`cli/user-prompt-check.sh` and `snowwork/user-prompt-check.sh`) via JSON `systemMessage` output. No manual check or response-appending is needed — the hook infrastructure injects the warning automatically into both CLI and SnowWork sessions.

## Conventions

- Shell scripts use `#!/bin/bash` (hooks) or `#!/bin/zsh` (diagnose-tracking.sh).
- Temp files: `/tmp/cortex_tag/<session_id>/` directory per session for concurrency isolation.
- Persistent state: `~/.snowflake/cortex/hooks/cx_projects_tracking/` (`.last_selection_cli`, `.last_selection_snowwork`, `.snowhouse_cache`, `.tag_log`, `.snow_path`, `.python3_path`, `sd_projects.txt`). CWD-scoped state: `.cx_last_selection_cli` and `.cx_last_selection_snowwork` written to the working directory (app-scoped to prevent CLI/SnowWork from overwriting each other).
- Use `uv` for Python virtual environments.
- CHANGELOG.md tracks releases. Do not inline release notes in README.

## Concurrency

Session-scoped temp directories (`/tmp/cortex_tag/<session_id>/`) prevent cross-session interference.
Two persistent files use last-writer-wins:
- `.cx_last_selection_cli` / `.cx_last_selection_snowwork` (CWD-scoped): stores the previous project choice for the "0" shortcut, written to the directory where the session was launched. Each app writes its own file so CLI and SnowWork selections don't overwrite each other. Cosmetic race only if two sessions of the same app type write from the same directory simultaneously.
- `.last_selection_cli` / `.last_selection_snowwork` (global fallback): same format, written to the hooks dir as a fallback when no CWD-scoped file exists.

`.tag_log` is append-only; interleaved lines are expected and each is self-contained.

## Testing

- After modifying hook scripts, start a Cortex Code CLI session and verify the banner shows skill list and prompts pass through without blocking.
- After modifying install.sh, run it and check hooks.json/settings.json were updated correctly.
- Run `zsh diagnose-tracking.sh` to validate a full setup.
- The GitHub Actions workflow (`query-tag-validation.yml`) validates QUERY_TAG schema on every PR.

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/USER_FLOW_PSEUDOCODE.md` | Master flow pseudocode — source of truth |
| `docs/GAP_ANALYSIS.md` | Pseudocode vs script gap tracker |
| `docs/USER_OPERATIONAL_PATTERNS.md` | Known + potential user activity patterns |
| `docs/FAQ.md` | User-facing troubleshooting |
| `CONTRIBUTING.md` | Developer guidelines and PR process |

## File Roles

| File | Purpose |
|------|---------|
| `cli/session-tag-init.sh` | SessionStart hook: saves session_id, CWD, detects connection from PPID args |
| `cli/user-prompt-check.sh` | UserPromptSubmit hook: beacon re-fire, silent auto-tag via `snow sql` |
| `snowwork/session-tag-init.sh` | SnowWork SessionStart: reads connection from settings.json |
| `snowwork/user-prompt-check.sh` | SnowWork UserPromptSubmit: beacon re-fire, silent auto-tag |
| `install.sh` | Full installer: CLI check, hook copy, hooks.json merge, skill install |
| `diagnose-tracking.sh` | 10-check diagnostic + log capture mode |

last_reviewed: 2026-03-27
