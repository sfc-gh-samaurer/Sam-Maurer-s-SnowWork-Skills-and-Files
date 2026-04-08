# Changelog

All notable changes to cx-project-tracking are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## v1.8.2 (2026-03-30)

### Added
- **UNTAGGED auto-tag confirmation message** — When the session auto-tags as `PROJECT=UNTAGGED` after 5 prompts, a warning now confirms the auto-tag and prompts the user to run `/sd-submit-info` to tag their actual project.
- **Periodic UNTAGGED reminder** — While a session remains tagged as `PROJECT=UNTAGGED`, a reminder fires approximately every hour (~20 prompts) urging the user to run `/sd-submit-info`.
- **`SessionEnd` hook** — New `cli/session-end.sh` and `snowwork/session-end.sh` fire when a session ends. If the session is still `UNTAGGED` (or was never tagged), a final warning is shown. Note: CoCo `SessionEnd` is non-blocking, so the session cannot be prevented from closing.
- **`SessionEnd` hook registration** — `install.sh` and `install.ps1` now register `SessionEnd` hooks in `hooks.json` (CLI) and `settings.json` (SnowWork) alongside `SessionStart` and `UserPromptSubmit`.
- **Diagnose `SessionEnd` checks** — `diagnose-tracking.sh` and `diagnose-tracking.ps1` now verify `SessionEnd` hook registration and `session-end.sh` file presence.

### Docs
- **FAQ: "Fixing an UNTAGGED Session"** — New section covering session resume for retroactive tagging (`cortex --continue` / `cortex --resume`), SnowWork conversation history, `QUERY_HISTORY` immutability, `/tmp` reboot behavior, and a reporting query for correlating UNTAGGED sessions.
- **FAQ: Diagnostics table** — Check 5 updated to include `SessionEnd` hook verification.
- **Pseudocode rewrite** — `USER_FLOW_PSEUDOCODE.md` updated for v1.8.2: Phase 5 (SessionEnd hook), warning delivery mechanism (CLI: `systemMessage` JSON, SnowWork: plain `echo` text), countdown warnings (prompts 1-4), periodic UNTAGGED reminder (every ~20 prompts), auto-tag confirmation message, app isolation guard, `untagged_remind_count` state file, `conn=` suffix in TAG_AUTO/TAG_FAIL log format. Mermaid diagrams rewritten: A1 expanded with warning branches and SessionEnd, A3 replaced (warning tiers with CLI/SnowWork delivery note), A4 added (session resume recovery flow).
- **Gap analysis revision** — `GAP_ANALYSIS.md` updated for v1.8.2: Revision notice added. Resolved 7 pseudocode alignment gaps (C3, C4, C5, C7, C8, C9, W1) via pseudocode rewrite. Added new gaps **SE1** (SessionEnd warning not rendered by CoCo CLI `quit`) and **SE2** (`[ctx] no in_progress task found` message is CoCo-internal, not hook-controllable). Suggested branches pruned. Summary and PR coverage updated.

### Changed
- **Hook warning delivery split** — CLI hooks (`cli/user-prompt-check.sh`) output `{"systemMessage":"..."}` JSON, which CoCo injects as a system-level instruction to the LLM. SnowWork hooks (`snowwork/user-prompt-check.sh`) output plain `echo` text instead — the `systemMessage` JSON approach did not work for SnowWork (the LLM would ingest the instruction but not relay it to the user). Either way, warnings fire regardless of working directory or `.cortex/INSTRUCTIONS.md` presence.
- **`.cortex/INSTRUCTIONS.md` warning section** — Replaced the manual tag-file-check mechanism with a note that hooks handle warning delivery via `systemMessage`. No manual response-appending needed.
- **`diagnose-tracking.sh` log analysis** — Updated `UserPromptSubmit` check to detect both `systemMessage` (CLI) and plain echo warning text (SnowWork) in addition to the legacy "hook blocked" log pattern.

## v1.8.1 (2026-03-28) — PR #44 feedback

### Added
- **`.gitattributes`** — Enforces LF line endings for `.sh`, `.md`, `.toml`, `.json`, `.yaml` files. PowerShell `.ps1` files keep CRLF. Prevents WSL breakage from Windows round-trip.
- **`install.ps1`** — Full Windows PowerShell installer (equivalent to `install.sh`). Copies hooks, merges `hooks.json` and `settings.json`, installs skills, normalizes CRLF, tests connection.
- **`diagnose-tracking.ps1`** — Windows PowerShell diagnostic script (8 checks: CLI, `.snow_path`, connections, hooks.json, settings.json, hook scripts, connection test, sd_projects.txt).
- **CRLF auto-fix in `install.sh`** — Step 0.25 detects and fixes CRLF line endings in all `.sh` files at install time (uses `dos2unix` or `sed` fallback).
- **Known Issues** — Documented Python keychain popup (macOS), CRLF/WSL, and SnowWork double-run (confirmed as CoCo CLI skill-loading limitation, not a hook bug) in README.
- **`test/`** — Docker-based test suite: 3 containers (Ubuntu for `install.sh`, Ubuntu for CRLF injection/fix, PowerShell for `install.ps1`). Tests directory creation, file copies, JSON merge, idempotency, CRLF round-trip, skills installation. Run via `bash test/run-tests.sh`.

### Changed
- **Windows Install section in README** — Now references `install.ps1` as the Windows installer. Removed `install-snow-cli.ps1` (auto-install logic merged into `install.ps1` Step 1).
- **Troubleshooting section** — Added `diagnose-tracking.ps1` usage for Windows.

## v1.8.0 (2026-03-27)

### Changed
- **Non-blocking hooks** — `UserPromptSubmit` hooks for both CLI and SnowWork always `exit 0`. Prompts are never blocked. Project selection happens exclusively through the `sd-submit-info` skill. The CLI menu system (~370 lines), Snowhouse query logic, warehouse detection, state machine, gatekeeper blocking, and skill whitelist have all been removed from the hooks.
- **Silent auto-tag** — After 5 untagged prompts, hooks fire a default tag (`PROJECT=UNTAGGED`) with the user's email resolved from cached files (`sd_projects.txt` → `.snowhouse_cache` → `.last_selection_*` → `UNKNOWN`). The tag is a real `ALTER SESSION SET QUERY_TAG` + `SELECT 1` beacon. Background `wait` captures the exit code — successes log `TAG_AUTO`, failures log `TAG_FAIL` with connection info. Replaces the previous safety valve and `TAG_SKIP` log type.
- **INSTRUCTIONS.md warning mechanism** — `.cortex/INSTRUCTIONS.md` now contains a system-reminder that appends an informational warning to every response when the session is untagged. Warnings stop once the user runs `/sd-submit-info` or the auto-tag fires.
- **Session banner** — Both CLI and SnowWork banners now show Session ID, Active Connection (with resolution source), and list the three available skills (`/sd-submit-info`, `/sd-project-list-setup`, `/sd-verify-tracking`).
- **Session directory structure** — Session state files live under `/tmp/cortex_tag/<SID>/` instead of flat `/tmp/cortex_tag_*_<SID>.txt` files, improving concurrency isolation.
- **Multi-layer connection detection** — CLI uses a 5-layer cascade (hook input JSON → PPID args → `connections.toml` default → `config.toml` default → `snow connection list`); SnowWork uses a 4-layer cascade (hook JSON → `settings.json` → `connections.toml` → `config.toml`). `CONN_SOURCE` is tracked in log entries for traceability.
- **App isolation** — An `app_type` marker (`cli` or `snowwork`) prevents CLI hooks from interfering with SnowWork-owned sessions and vice versa.
- **Beacon re-fire on every prompt** — After the initial tag is set, each subsequent prompt re-fires `ALTER SESSION SET QUERY_TAG` + `SELECT 1` in the background, ensuring continuous `QUERY_HISTORY` coverage.
- **`SD_` variable namespace** — Renamed `CORTEX_TAG_ONLY` → `SD_CORTEX_TAG_ONLY`, `TAG_VALUES` → `SD_TAG_VALUES`, `TAG_SUBMITTED` → `SD_TAG_SUBMITTED` to avoid collisions with other hooks.
- **Structured tag logging** — Tag attempts are logged as `TAG_OK`, `TAG_FAIL`, or `TAG_AUTO` entries with connection context in `.tag_log`. Empty `TAG_CONN` is caught before firing, logging `TAG_FAIL|no_connection_detected`.
- **`sd_projects.txt` priority with 7-day TTL** — The user-editable `sd_projects.txt` is checked first. Snowhouse is queried only when the file is missing or older than 7 days.
- **Persistent Snowhouse cache** — Project list cache moved to `${BASE_DIR}/.snowhouse_cache` with a 24-hour TTL, shared between CLI and SnowWork in a 6-field pipe-delimited format.
- **CWD-scoped previous selection** — Previous selection is loaded from the working directory first (`.cx_last_selection_cli` / `.cx_last_selection_snowwork`), then falls back to a global file in the hooks directory.
- **SnowWork parity with CLI** — SnowWork hooks use `CX_SNOW_BIN` for binary resolution, same 3-tier project loading, `SELECT 1` beacon, and consistent banner format.
- **Config.toml auto-copy** — Snowhouse connection entries in `config.toml` are auto-copied to `connections.toml` with a `grep -q` duplicate guard.
- **Cross-platform `stat` compatibility** — `_file_mtime()` helper tries `stat -c '%Y'` (Linux) first, falls back to `stat -f '%m'` (macOS).

### Fixed
- **[CRITICAL] Safety valve infinite loop (DF2)** — The safety valve wrote `SD_TAG_SUBMITTED` without populating `SD_TAG_VALUES`, causing the beacon validation gate to delete the marker and re-trigger indefinitely. Now writes `PROJECT=UNTAGGED` before marking complete.
- **CI false positive in query-tag-validation** — Tightened the QUERY_TAG regex to `QUERY_TAG=.*{` (bash variable assignments only) and scoped to `*.sh` files.
- **Bare `snow` binary in `cli/session-tag-init.sh`** — `snow connection list` fallback now resolves via `CX_SNOW_BIN`.

### Removed
- **Hook-based menus (CLI)** — `cli/user-prompt-check.sh` reduced from 434 to ~80 lines. Menu, Snowhouse queries, warehouse detection, state machine, selection parsing, `_read_pipe_file()`, `_find_snowhouse_conn()`, and `_write_last_selection()` all removed.
- **Gatekeeper blocking (SnowWork)** — `snowwork/user-prompt-check.sh` no longer blocks with `exit 2` or displays a gatekeeper message.
- **Skill whitelist** — No longer needed since hooks never block.
- **State file** — `/tmp/cortex_tag/<SID>/state` is no longer written or read.
- **`.menu_cache`** — Consolidated into `.snowhouse_cache`.

### Docs
- **Pseudocode rewrite** — `USER_FLOW_PSEUDOCODE.md` rewritten for the non-blocking architecture: unified CLI/SnowWork flow, warning mechanism, auto-tag, `TAG_AUTO` log type.
- **Documentation sweep** — `USER_FLOW_PSEUDOCODE.md` rewritten. `FAQ.md`, `GAP_ANALYSIS.md`, `USER_OPERATIONAL_PATTERNS.md`, and `INSTRUCTIONS.md` partially updated; full alignment deferred to a follow-up pass.

### Security
- **QUERY_TAG field sanitization** — Values stripped to `[A-Za-z0-9_-]` for identifiers, `[A-Za-z0-9_.@-]` for email. Single quotes escaped as `''`.

## v1.7.0 (2026-03-26)

### Fixed
- **Session tagging silently failing for non-default connections**: `snow sql` in `user-prompt-check.sh` ran without `--connection`, so it resolved against a literal `[default]` section in `connections.toml` rather than the session's actual connection. Users whose Snowhouse entry was named anything other than `[default]` saw "Session tagged" in the logs while nothing actually reached Snowflake. The hook now reads the connection saved by `session-tag-init.sh` at session start and passes it via `--connection`. ([PR #10](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/10), [Slack thread](https://snowflake.slack.com/archives/C0AMJ8X8L9X/p1774306911706559))

### Added
- **`connections.toml` format validation during install** — The installer detects mixed section header formats (`[name]` vs `[connections.name]`) and warns before they cause silent `snow sql` failures downstream. ([PR #9](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/9))
- **`diagnose-tracking.sh` diagnostic script** — 10-check troubleshooting tool covering CLI install, `.snow_path`, `connections.toml` format/fields, `config.toml` duplicates, `hooks.json` registration, hook scripts, old install cleanup, connection test, warehouse access, and `sd_projects.txt`. Includes `--logs` mode for live log capture and analysis. ([PR #11](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/11))
- **README: Prerequisites, Troubleshooting, and Known Issues sections** — Documented the `connections.toml` format requirement, `diagnose-tracking.sh` usage, and known failure modes (silent tagging, mixed formats, config.toml-only connections). ([PRs #9, #10, #11](https://github.com/Snowflake-Solutions/cx-project-tracking/pulls))
- **Overview and Install documentation** — consolidated into `README.md` (the standalone `docs/1. Overview and Install.docx` was removed). ([PR #8](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/8))
- **Entro secret scanning and QUERY_TAG schema validation** — Pre-commit hook, GitHub Actions workflow, and `repo_meta.yaml`. ([PR #6](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/6))
- **`CHANGELOG.md`** — Release history starting from v1.6.
- **`FAQ.md`** — Self-service troubleshooting guide covering project list failures, multiple sessions, diagnostics walkthrough, and distribution without GitHub access.
- **CWD-scoped `.cx_last_selection`** — Previous project selection is now written to the working directory so each project folder remembers its own last choice, with a global fallback in the hooks directory. ([PR #23](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/23))
- **Hook input JSON `cwd` parsing** — `session-tag-init.sh` and `user-prompt-check.sh` now read the `cwd` field from hook input JSON (3-tier fallback: hook JSON -> saved temp file -> `$PWD`). ([PR #23](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/23))
- **`.cortex/INSTRUCTIONS.md`** — Developer guide covering key constraints, conventions, concurrency, testing, and file roles.
- **`pyproject.toml`** — Dependency groups for `uv`: `dashboard` (Streamlit) and `dev` (linting/testing).

### Security
- **QUERY_TAG field sanitization and SQL quote escaping** — `PROJECT_ID` and `MILESTONE_ID` now stripped to alphanumeric/underscore/hyphen before SQL interpolation; single quotes in the assembled QUERY_TAG are escaped to prevent injection. ([PR #26](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/26))

### Changed
- **Absolute binary resolution (`CX_SNOW_BIN` / `CX_PYTHON3`)** — All four hook scripts no longer mutate `PATH`. Instead they resolve `snow` and `python3` from `.snow_path` / `.python3_path` files written by `install.sh`, falling back to `command -v`. Installer now also saves `python3` location. ([PR #28](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/28))
- **Removed `connections.toml` auto-write (Python block)** — The Python block that silently appended Snowhouse connection sections from `config.toml` to `connections.toml` has been replaced with a stderr warning and a `TAG_FAIL|config_toml_only` entry in `.tag_log`. A safer bash-based auto-copy with `grep -q` duplicate guard was later added in v1.8.0. ([PR #28](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/28))
- **Tag verification with `.tag_log` logging** — `user-prompt-check.sh` now captures the `snow sql` exit code and logs `TAG_OK` or `TAG_FAIL` with connection and project context to `~/.snowflake/cortex/hooks/cx_projects_tracking/.tag_log`. Tag submission marker is written even on failure (best-effort). ([PR #27](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/27))
- **Install pre-checks** — Installer now validates Snow CLI version (>= 3.16), `connections.toml` file permissions (600), warns when connections exist only in `config.toml`, and runs a live `snow sql` connection test at the end. ([PR #27](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/27))
- **Debug script deprecated** — `cli/debug.sh` now prints a deprecation notice directing users to `diagnose-tracking.sh`. ([PR #23](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/23))
- **README flow diagrams updated** — CLI and SnowWork diagrams now reflect CWD saving, `.cx_last_selection`, `.tag_log` logging, and auto-tag on untagged prompts.
- **SnowWork parity** — `settings.json` hook registration (Step 3b in installer), `sd-submit-info` SKILL.md updated with sanitization rules, combined `ALTER SESSION + SELECT 1` call, tag verification with `.tag_log`, and best-effort semantics. ([PR #27](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/27))
- **SnowWork connection detection** — `session-tag-init.sh` now checks `connections.toml` before `config.toml` (was reversed). ([PR #27](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/27))
- **README reporting query** — WHERE clause updated from `QUERY_TEXT = 'SELECT 1'` to `TRY_PARSE_JSON(QUERY_TAG):app::STRING IN ('cortex_code_cli', 'snowwork')`. ([PR #27](https://github.com/Snowflake-Solutions/cx-project-tracking/pull/27))

## v1.6

Initial tracked release. Baseline CLI and SnowWork hook system for session tagging.

- CLI hooks (`session-tag-init.sh`, `user-prompt-check.sh`) for automatic project/milestone selection and `ALTER SESSION SET QUERY_TAG`
- SnowWork `sd-submit-info` skill for manual session tagging
- `install.sh` installer with Snowflake CLI auto-install, Snowhouse connection detection, and `config.toml` to `connections.toml` migration
- `sd-project-list-setup` and `sd-verify-tracking` skills
- `debug.sh` post-session diagnostic
- Streamlit dashboard (`dashboard/app.py`) for tag history
- `sd_projects.txt` fallback for offline/VDI deployments
