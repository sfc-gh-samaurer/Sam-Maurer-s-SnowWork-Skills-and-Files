# Gap Analysis: Pseudocode vs Code on `main`

> Evaluates the code on `main` after PR#29 (with stacked PRs #37-#43) merged.
> Reference: [USER_FLOW_PSEUDOCODE.md](USER_FLOW_PSEUDOCODE.md) (source of truth for pseudocode)
> Date: 2026-03-27 (revised 2026-03-30)
> Analyst: Cortex Code + tmathew

> **⚠ Revision Notice (v1.8.2, 2026-03-30):**
> This document was originally written against v1.7/PRs #29-#43. The v1.8.2 pseudocode rewrite resolved most "Remaining Open Gaps":
> - **C3, C4, C8** (stale cleanup, app_type marker/guard) — now documented in pseudocode Phases 1-2
> - **C5** (connection cascade) — pseudocode Phase 1 step 7 documents multi-layer cascade
> - **C7, C9** (beacon validation, Phase 4 re-fire) — now documented in pseudocode Phases 2/4
> - **W1** (SnowWork connection cascade) — pseudocode documents it
> - **Phase 5** (SessionEnd hook) added to pseudocode
> - **Warning delivery** mechanism documented (CLI: `systemMessage` JSON; SnowWork: plain `echo` text)
> - **Periodic UNTAGGED reminder** (every ~20 prompts) added
> - **New gap SE1**: SessionEnd `systemMessage` not rendered by CoCo CLI `quit` (platform limitation)
>
> The "Remaining Open Gaps" and "Suggested Branches" sections below are updated accordingly.

---

## CLI Gaps

### Pseudocode vs `cli/session-tag-init.sh` + `cli/user-prompt-check.sh`

#### Flow-Breaking (tags may not fire or error is hidden)

| ID | Gap | Location | Pseudocode Ref | Status |
|---|---|---|---|---|
| **G3** | No empty-connection guard at tag fire time — `snow sql` fires without `--connection` if TAG_CONN is empty, may silently fail or tag the wrong session | `cli/user-prompt-check.sh` L368 | CLI Phase 3 step 9 | **FIXED** — `if [[ -z "$TAG_CONN" ]]` guard with `TAG_FAIL\|no_connection_detected` logging (PR#41/43) |
| **G4** | Tag failure invisible — always prints "Session tagged" and touches submitted regardless of `snow sql` exit code | `cli/user-prompt-check.sh` L375-383 | CLI Phase 3 steps 11-14 | **FIXED** — `TAG_ERR`/`TAG_RC` capture; structured `TAG_OK`/`TAG_FAIL` logging with `SAFE_ERR` (PR#41/43) |
| **DF2** | Safety valve writes `touch SD_TAG_SUBMITTED` without writing SD_TAG_VALUES — beacon validation gate sees submitted, checks values for `^PROJECT=.+`, fails, deletes submitted, safety valve re-fires next prompt. User sees "Tagging skipped" on every prompt forever | `cli/user-prompt-check.sh` L401 | CLI Safety Valve step 2b | **FIXED** — writes `PROJECT=UNTAGGED` to `SD_TAG_VALUES` before `touch SD_TAG_SUBMITTED` (PR#43) |

#### Script goes beyond pseudocode (not bugs — additive defenses)

| ID | Gap | Pseudocode says | Script does | Severity | Suggested Branch |
|---|---|---|---|---|---|
| **C1** | Phase 1 binary resolution | "Resolve python3" only | Resolves both `CX_SNOW_BIN` + `CX_PYTHON3` (init L10-19) | Low | N/A — cosmetic, pseudocode intentionally abstracts |
| **C2** | Phase 1 `mkdir -p` | Not mentioned | `mkdir -p "$SESSION_DIR"` (init L30) | Low | N/A — implied by "write session files" |
| **C3** | Phase 1 stale state cleanup | Not mentioned | Cleans `state`, `block_count`; conditionally `values`/`submitted` (init L32-40) | **Medium** | `pseudocode/stale-cleanup` |
| **C4** | Phase 1 `app_type` marker | Not mentioned | Writes `cli` to `app_type` if not already claimed (init L43-44) | **Medium** | `pseudocode/app-type-isolation` |
| **C5** | Phase 1 connection detection | "Get connection from active coco cli SQL connection" (single source) | 5-layer cascade: JSON → `-c` flag → connections.toml → config.toml → `snow connection list` (init L55-97) | **Medium** | N/A — pseudocode intentionally abstracts |
| **C6** | Phase 1 banner version | "Build v1.8.0" | "Build v1.8.0" (init L101) | **RESOLVED** — version aligned | — |
| **C7** | Phase 2/4 "already tagged" gate | "SD_TAG_VALUES + SD_TAG_SUBMITTED exist → exit 0" (simple file check) | Regex `grep -q "^PROJECT=.\+"` + beacon re-fire in background + invalid-delete fallthrough (prompt L49-59) | **Medium** | `pseudocode/beacon-validation` |
| **C8** | Phase 2 `app_type` check | Not mentioned | `[[ "$APP_TYPE" == "snowwork" ]] && exit 0` (prompt L45-46) | **Medium** | `pseudocode/app-type-isolation` |
| **C9** | Phase 4 passthrough | "SD_TAG_VALUES + SD_TAG_SUBMITTED exist → exit 0" (silent) | Same regex + beacon re-fire as C7 — Phase 4 IS the "already tagged" gate | **Medium** | `pseudocode/beacon-validation` |

#### Non-Breaking (functional but worth fixing)

| ID | Gap | Location | Pseudocode Ref | Status | Suggested Branch |
|---|---|---|---|---|---|
| **G7** | Overly broad `$`/`/` passthrough — any prompt starting with `$` or `/` skips tagging, not just the 3 tracking skills | `cli/user-prompt-check.sh` L64-65 | CLI Phase 2 step 3d | **FIXED** — `SD_SKILL_WHITELIST` regex: only passes `sd-project-setup-list\|sd-submit-info\|sd-verify-tracking` (PR#38) | — |
| **G8** | `sd_projects.txt` is read but never checked for staleness — pseudocode says >7 days should trigger Snowhouse refresh | `cli/user-prompt-check.sh` L92-114 | CLI Phase 2 step 5a | **FIXED** — `SD_FILE_TTL=604800` (7 days), `FILE_AGE` check via `_file_mtime()`, sd_projects.txt checked first with TTL (PR#40) | — |
| **G9** | SNOWADHOC (2XL warehouse) used as default Snowhouse warehouse — pseudocode says use XSMALL | `cli/user-prompt-check.sh` L218 | CLI Phase 2 step 5c | **NOT FIXED** — still uses `SNOWADHOC` as last-resort fallback | `fix/snowadhoc-to-xsmall` |
| **G12** | `stat -f '%m'` in Snowhouse cache TTL check is macOS-only — fails silently on Linux (returns 0, cache always appears stale) | `cli/user-prompt-check.sh` L22 | CLI Phase 2 step 5d | **FIXED** — `_file_mtime()` helper tries `stat -c '%Y'` (Linux) first, falls back to `stat -f '%m'` (macOS) (PR#43) | — |
| **G13** | Config.toml auto-copy to connections.toml has no duplicate-section check — if `[snowhouse]` already exists in connections.toml, appending a second block causes unpredictable TOML parsing | `cli/user-prompt-check.sh` | N/A (not in pseudocode) | **FIXED** — `grep -q` guard before appending (PR#43) | — |

---

## SnowWork Gaps

### Pseudocode vs `snowwork/session-tag-init.sh` + `snowwork/user-prompt-check.sh`

#### Flow-Breaking

| ID | Gap | Location | Pseudocode Ref | Status |
|---|---|---|---|---|
| **SDF2** | Same DF2 bug as CLI — safety valve does `touch SD_TAG_SUBMITTED` without writing SD_TAG_VALUES, causing infinite "Tagging skipped" loop when beacon validation gate deletes submitted | `snowwork/user-prompt-check.sh` L59 | SnowWork Safety Valve | **FIXED** — writes `PROJECT=UNTAGGED` to `SD_TAG_VALUES` before `touch SD_TAG_SUBMITTED` (PR#43) |
| **SG7** | Overly broad `$`/`/` passthrough in SnowWork prompt hook — same as CLI G7 | `snowwork/user-prompt-check.sh` L45-46 | SnowWork Phase 2 step 3c | **FIXED** — `SD_SKILL_WHITELIST` regex matching CLI whitelist (PR#42/43) |
| **SG8** | Bare `snow` command in beacon re-fire — SnowWork prompt hook uses `snow sql` instead of `$CX_SNOW_BIN`, may resolve wrong binary or fail if snow is not in PATH | `snowwork/user-prompt-check.sh` L6-8 | SnowWork Phase 4 step 1c | **FIXED** — `CX_SNOW_BIN` resolution from `.snow_path` with `command -v` fallback (PR#42/43) |

#### Script goes beyond pseudocode (not bugs — additive defenses)

| ID | Gap | Pseudocode says | Script does | Severity | Suggested Branch |
|---|---|---|---|---|---|
| **W1** | Phase 1 connection detection | "one active connection" (simple) | 4-layer cascade: JSON → settings.json → connections.toml → config.toml (init L39-64) | **Medium** | `fix/snowwork-conn-simplify` or `pseudocode/conn-cascade-annotate` |
| **W2** | Phase 1 stale cleanup + `app_type` | Not in pseudocode | Script cleans `block_count`, conditionally `values`/`submitted`, writes `app_type=snowwork` (init L19-29) | Low | `pseudocode/stale-cleanup` (shared with C3/C4) |
| **W3** | Phase 2 binary resolution | "Resolve python3" only | Resolves both `CX_SNOW_BIN` + `CX_PYTHON3` (prompt L6-12) | Low | N/A — cosmetic, pseudocode intentionally abstracts |
| **W4** | Phase 2 "already tagged" validation | "SD_TAG_VALUES + SD_TAG_SUBMITTED exist → re-fire beacon, exit 0" | Also does regex `grep -q "^PROJECT=.\+"` + invalid-delete fallthrough (prompt L29-39) | Low | `pseudocode/beacon-validation` (shared with C7/C9) |

#### Non-Breaking

| ID | Gap | Location | Pseudocode Ref | Status | Suggested Branch |
|---|---|---|---|---|---|
| **SG3** | SnowWork init — `sd-submit-info` skill now uses CWD-scoped `.cx_last_selection_snowwork` with `.last_selection_snowwork` global fallback | `snowwork/session-tag-init.sh` | SnowWork Phase 1 | **Addressed** — skill reads CWD-scoped then global app-scoped selection files | `fix/snowwork-cwd-tracking` |
| **SG4** | SnowWork init uses PATH prepending instead of absolute binary resolution — inconsistent with CLI init which uses `CX_PYTHON3` | `snowwork/session-tag-init.sh` L3-7 | SnowWork Phase 1 step 1 | **FIXED** — `CX_PYTHON3` absolute resolution from `.python3_path` with `command -v` fallback (verified on main) | — |

---

## Resolved Gaps (fixed by PR#29 + stacked PRs #37-#43)

| ID | Original Gap | Fixed By | How |
|---|---|---|---|
| **G1** | No connection fallback when all sources miss | PR#29 | 5-layer cascade: hook input JSON -> PPID args -> connections.toml -> config.toml -> `snow connection list` |
| **G2** | Empty connection written silently | PR#29 | Banner shows `CONN_SOURCE` or prints warning if not detected |
| **G3** | No empty-connection guard at tag fire | PR#41/43 | `if [[ -z "$TAG_CONN" ]]` guard with `TAG_FAIL|no_connection_detected` |
| **G4** | Tag failure invisible | PR#41/43 | `TAG_ERR`/`TAG_RC` capture, `TAG_OK`/`TAG_FAIL` structured logging |
| **G5** | Empty TAG_VALUES passes passthrough gate | PR#29 | `grep -q "^PROJECT=.\+"` content validation; invalid -> delete both files |
| **G6** | Snowhouse project list re-queried every session | PR#29 | Persistent `.snowhouse_cache` with 24h TTL |
| **G7** | Overly broad `$`/`/` passthrough | PR#38 | `SD_SKILL_WHITELIST` regex in CLI and SnowWork |
| **G8** | sd_projects.txt staleness not checked | PR#40 | `SD_FILE_TTL=604800`, `_file_mtime()` age check |
| **G10** | Flat `/tmp/cortex_tag_*_<SID>.txt` file layout | PR#29 | Session directory `/tmp/cortex_tag/<SID>/` |
| **G11** | Banner missing Session ID | PR#29 | Banner shows SID and connection source |
| **G12** | `stat -f '%m'` macOS-only | PR#43 | `_file_mtime()` helper: Linux-first `stat -c '%Y'` + macOS fallback |
| **G13** | Duplicate config.toml auto-copy | PR#43 | `grep -q` guard before appending |
| **DF2** | CLI safety valve infinite loop | PR#43 | `echo "PROJECT=UNTAGGED" > "$SD_TAG_VALUES"` before touch |
| **SDF2** | SnowWork safety valve infinite loop | PR#43 | Same fix as DF2 |
| **SG1** | No warning when connection empty in SnowWork | PR#29 | Banner shows connection or warning |
| **SG4** | SnowWork init uses PATH prepending | PR#43 | `CX_PYTHON3` absolute resolution |
| **SG7** | SnowWork broad passthrough | PR#42/43 | `SD_SKILL_WHITELIST` matching CLI |
| **SG8** | Bare `snow` in SnowWork beacon | PR#42/43 | `CX_SNOW_BIN` from `.snow_path` |
| **S1** | Session directory path mismatch — pseudocode said `/tmp/<SID>/cortex_tag_*.txt`, scripts use `/tmp/cortex_tag/<SID>/` | Pseudocode update | Pseudocode updated to `/tmp/cortex_tag/<SID>/` with short filenames to match scripts |
| **S2** | File naming mismatch — pseudocode said `cortex_tag_session_id.txt` etc., scripts use short names (`session_id`, `values`, etc.) | Pseudocode update | Pseudocode updated to short filenames matching scripts |
| **S3** | `latest_session` location — pseudocode said `/tmp/<SID>/cortex_tag_latest_session.txt` (inside session dir), scripts use `/tmp/cortex_tag/latest_session` (global) | Pseudocode update | Pseudocode updated to `/tmp/cortex_tag/latest_session` (global) |
| N/A | No app isolation between CLI and SnowWork | PR#29 | `app_type` marker file; CLI exits if `app_type == snowwork` |
| N/A | No beacon re-fire on subsequent prompts | PR#29 | Re-fires `ALTER SESSION SET QUERY_TAG` in background on every post-tagging prompt |
| N/A | No stale file cleanup on session start | PR#29 | Init hook cleans state/block_count; preserves valid values/submitted for --resume |
| N/A | Bare `snow`/`python3` in CLI scripts | PR#37 | Absolute binary resolution via `CX_SNOW_BIN`/`CX_PYTHON3` with `.snow_path`/`.python3_path` files |

---

## Remaining Open Gaps

> **Note (v1.8.2)**: The pseudocode rewrite (2026-03-30) resolved all Medium-priority pseudocode alignment gaps.
> **C3/C4/C8** (stale cleanup, app_type) are now documented in Phase 1 steps 4-5 and Phase 2 step 4.
> **C5** (connection cascade) is documented in Phase 1 step 7.
> **C7/C9** (beacon validation, Phase 4 re-fire) are documented in Phases 2/4.
> **W1** (SnowWork connection cascade) is documented alongside CLI in Phase 1 step 7.
> Phase 5 (SessionEnd) and warning delivery mechanism are now fully documented (CLI uses `systemMessage` JSON, SnowWork uses plain `echo`).

| ID | Gap | Priority | Status | Notes |
|---|---|---|---|---|
| **SG3** | No CWD tracking in SnowWork init | Low | Open | SnowWork sessions often don't have meaningful CWD. `sd-submit-info` handles CWD-scoped selection independently. Low value fix. |
| **SE1** | SessionEnd `systemMessage` not rendered by CoCo CLI `quit` | Medium | Open — platform limitation | Hook fires correctly and emits valid JSON, but CoCo CLI exits before reading/rendering SessionEnd stdout. `SessionEnd` is non-blocking (`Block? = No`). Verified via debug logging: `app_type=cli`, correct branch taken, `printf` executes. The message is emitted but swallowed by the exit process. Not a hook bug — requires CoCo platform change to fix. |
| **SE2** | `[ctx] no in_progress task found` message at session exit is CoCo-internal, not hook-controllable | Low | Open — platform limitation | The `[ctx]` line printed below the CoCo CLI session summary box comes from CoCo's built-in task tracking system (`system_todo_write`), not from our `SessionEnd` hook. We cannot inject content into or suppress lines from the session summary. A previous-session UNTAGGED banner in `session-tag-init.sh` and a resume hint in `session-end.sh` were prototyped but reverted — even if they worked, they would not affect this `[ctx]` message. Any fix requires a CoCo platform change to the session summary renderer. |
| **C3** | Phase 1 stale state cleanup not in pseudocode | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 1 step 4 now documents stale cleanup and `--resume` preservation |
| **C4** | Phase 1 `app_type` marker not in pseudocode | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 1 step 5 now documents `app_type` marker |
| **C5** | Phase 1 connection detection abstracted in pseudocode | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 1 step 7 documents multi-layer cascade for both CLI and SnowWork |
| **C7** | Phase 2/4 "already tagged" gate simplified in pseudocode | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 2 step 6 documents regex validation, beacon re-fire, and invalid-delete fallthrough |
| **C8** | Phase 2 `app_type` check not in pseudocode | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 2 step 4 documents app isolation guard |
| **C9** | Phase 4 beacon re-fire not in CLI pseudocode | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 4 step 1 documents beacon re-fire with UNTAGGED periodic reminder |
| **W1** | SnowWork Phase 1 connection detection not simplified | Medium | **Resolved (v1.8.2)** | Pseudocode Phase 1 step 7 documents both CLI and SnowWork cascades side by side |

> **Superseded (v1.8.0)**: **G9** (SNOWADHOC warehouse) — hooks no longer query Snowhouse; warehouse detection removed entirely.

---

## Suggested Branches (from main)

> **Updated (v1.8.2)**: The pseudocode rewrite resolved all `pseudocode/*` branches. Only low-priority script fixes remain.

| Branch Name | Gaps Addressed | Type | Scope |
|---|---|---|---|
| `fix/snowwork-cwd-tracking` | SG3 | **Script fix** | Add CWD tracking to SnowWork init. Low value — SnowWork sessions may not have meaningful CWD. |

> **SE1** (SessionEnd rendering) requires a CoCo platform change, not a branch in this repo.
>
> **Resolved branches (no longer needed):**
> - ~~`pseudocode/stale-cleanup`~~ (C3, C4, C8) — resolved by v1.8.2 pseudocode rewrite
> - ~~`pseudocode/beacon-validation`~~ (C7, C9) — resolved by v1.8.2 pseudocode rewrite
> - ~~`fix/snowwork-conn-simplify`~~ (W1) — resolved by pseudocode documenting the cascade

---

## Summary

| Category | Count |
|---|---|
| Flow-breaking gaps (all fixed) | 6 (G3, G4, DF2, SDF2, SG7, SG8) |
| Pseudocode alignment gaps (S1-S3, resolved) | 3 |
| Script-beyond-pseudocode gaps (C1-C9, W1-W4) | 13 (7 resolved by v1.8.2 pseudocode rewrite) |
| Remaining open gaps | 3 (SG3, SE1, SE2) |
| Superseded gaps | 1 (G9) |
| Resolved by pseudocode rewrite (v1.8.2) | 7 (C3, C4, C5, C7, C8, C9, W1) |
| Previously resolved gaps | 22+ |

The remaining open gaps:
1. **SG3** — Low-priority script fix (SnowWork CWD tracking)
2. **SE1** — CoCo platform limitation: SessionEnd `systemMessage` not rendered during `quit` exit. Hook fires correctly but CoCo swallows the output. Requires CoCo platform change.
3. **SE2** — CoCo platform limitation: `[ctx] no in_progress task found` message at session exit is from CoCo's internal task system, not our hooks. Cannot inject into or suppress session summary output.

---

## PR Coverage Summary

| PR# | What It Brings | Gaps Resolved |
|---|---|---|
| #29 | Session directory, SD_ namespace, 4-layer connection detection, app isolation, beacon re-fire, stale cleanup, config.toml auto-copy, Snowhouse cache TTL, connection source banner | G1, G2, G5, G6, G10, G11, SG1 |
| #37 | Absolute binary resolution (`CX_SNOW_BIN`/`CX_PYTHON3`) | Bare binary issue |
| #38 | Skill whitelist: `sd-project-setup-list\|sd-submit-info\|sd-verify-tracking` | G7 |
| #39 | CWD-scoped `.cx_last_selection_cli` / `.cx_last_selection_snowwork` with PREV_SOURCE tracking | — |
| #40 | sd_projects.txt first with 7-day TTL, Snowhouse fallback | G8 |
| #41 | Connection validation, TAG_ERR/TAG_RC capture, structured logging, error surfacing | G3, G4 |
| #42 | SnowWork alignment: CX_SNOW_BIN, CWD, cleanup, banner parity, skill whitelist | SG4, SG7, SG8 |
| #43 | DF2 safety valve fix, CI regex, bare snow in init, cross-platform stat, duplicate config guard | DF2, SDF2, G12, G13 |
| **#44** | **v1.8.0 release** — pseudocode alignment (S1-S3), version bump, diagnose regex fix | S1, S2, S3 |
| v1.8.2 | Pseudocode rewrite: Phase 5 (SessionEnd), systemMessage delivery, app isolation, beacon validation, periodic UNTAGGED reminder, connection cascade docs, Mermaid diagrams, FAQ session-resume guidance | C3, C4, C5, C7, C8, C9, W1 |
