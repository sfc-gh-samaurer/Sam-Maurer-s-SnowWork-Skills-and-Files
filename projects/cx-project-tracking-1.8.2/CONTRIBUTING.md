# Contributing to cx-project-tracking

## Getting Started

1. Clone the repo:
   ```bash
   git clone git@github.com:Snowflake-Solutions/cx-project-tracking.git
   cd cx-project-tracking
   ```
2. Run the installer to set up hooks locally:
   ```bash
   bash install.sh
   ```
3. Start a Cortex Code session and verify the project menu appears on first prompt.
4. Run the diagnostic to confirm setup:
   ```bash
   zsh diagnose-tracking.sh
   ```

## Documentation

All design and analysis documents live in `docs/`:

| Document | Purpose |
|---|---|
| [docs/USER_FLOW_PSEUDOCODE.md](docs/USER_FLOW_PSEUDOCODE.md) | Master flow pseudocode (CLI + SnowWork). **Source of truth.** |
| [docs/GAP_ANALYSIS.md](docs/GAP_ANALYSIS.md) | Pseudocode vs script gap tracker with branch suggestions |
| [docs/USER_OPERATIONAL_PATTERNS.md](docs/USER_OPERATIONAL_PATTERNS.md) | Known and potential user activity patterns |
| [docs/FAQ.md](docs/FAQ.md) | User-facing troubleshooting and common questions |

`README.md` and `CHANGELOG.md` remain at the repo root.

## Key Policies

### Pseudocode is source of truth

`docs/USER_FLOW_PSEUDOCODE.md` is the team-agreed design document. Do NOT modify it without explicit approval from all CODEOWNERS. Scripts should implement the pseudocode; deviations are tracked in `docs/GAP_ANALYSIS.md`.

### QUERY_TAG schema is frozen (v1.6)

The JSON schema `{app, customer, project_id, project, milestone_id, milestone, email, session_id}` must not change. Adding, removing, or renaming fields breaks downstream reporting and the Snowflake task that merges tags into `SD_APPS_DB.COCO_USAGE.CORTEX_CODE_SESSION_TAGS`.

### Binary resolution

Hook scripts resolve `snow` and `python3` via `.snow_path` / `.python3_path` files (written by `install.sh`), with `command -v` fallback. Never mutate PATH in hook scripts.

### Best-effort tagging

If `snow sql` fails, log to `.tag_log` and let the session continue. Never block the user indefinitely. Safety valve releases after 5 blocked prompts.

## Branching Convention

| Prefix | Purpose | Example |
|---|---|---|
| `fix/` | Script bug fixes | `fix/snowadhoc-to-xsmall` |
| `pseudocode/` | Pseudocode updates (requires team agreement) | `pseudocode/beacon-validation` |
| `feature/` | New functionality | `feature/mid-session-retag` |
| `docs/` | Documentation-only changes | `docs/user-patterns` |

Branch from `main`. Target PRs to `main`.

## Pull Request Process

1. Create a **draft PR** first to get early feedback.
2. Link to relevant gap analysis IDs (e.g., "Addresses G9, C7") in the PR description.
3. Include a test plan: what you tested, how to reproduce, diagnostic output.
4. All PRs require review from CODEOWNERS before merge.
5. Update `CHANGELOG.md` with the changes under the appropriate version section.
6. Update `docs/GAP_ANALYSIS.md` if the PR resolves or introduces gaps.

## Testing Checklist

Before submitting a PR:

- [ ] Start a CLI session — project menu appears on first prompt
- [ ] Select a project — "Session tagged" confirmation appears
- [ ] Subsequent prompts pass through without blocking
- [ ] Run `zsh diagnose-tracking.sh` — all 10 checks pass
- [ ] Check `.tag_log` for `TAG_OK` entry
- [ ] If modifying SnowWork hooks: test `sd-submit-info` in a SnowWork session
- [ ] If modifying `install.sh`: run it and verify `hooks.json`/`settings.json` updated

## Code Style

- Shell scripts: `#!/bin/bash` for hooks, `#!/bin/zsh` for `diagnose-tracking.sh`
- Sanitize all values before SQL interpolation (see `.cortex/INSTRUCTIONS.md`)
- Temp files: `/tmp/cortex_tag/<session_id>/` (session-scoped)
- Persistent state: `~/.snowflake/cortex/hooks/cx_projects_tracking/`
- Use `uv` for Python virtual environments

## Code Review

All changes are reviewed by the project owners listed in `.github/CODEOWNERS`. For pseudocode changes, both owners must approve.
