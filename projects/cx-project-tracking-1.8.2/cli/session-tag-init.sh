#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# Session Tag Init — SessionStart Hook
# ═══════════════════════════════════════════════════════════════
# Saves session_id, start timestamp, and detects the active
# Snowflake connection for use at session end.
# All temp files are suffixed with session_id for concurrency.

# --- Binary resolution (no PATH mutation) ---
CX_BASE="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"

CX_SNOW_BIN="$(cat "$CX_BASE/.snow_path" 2>/dev/null)/snow"
[[ ! -x "$CX_SNOW_BIN" ]] && CX_SNOW_BIN="$(command -v snow 2>/dev/null)"
[[ ! -x "$CX_SNOW_BIN" ]] && { echo "snow CLI not found" >&2; exit 1; }

CX_PYTHON3="$(cat "$CX_BASE/.python3_path" 2>/dev/null)/python3"
[[ ! -x "$CX_PYTHON3" ]] && CX_PYTHON3="$(command -v python3 2>/dev/null)"
[[ ! -x "$CX_PYTHON3" ]] && { echo "python3 not found" >&2; exit 1; }

# Prevent recursion from the tagging sub-session
[[ "$SD_CORTEX_TAG_ONLY" == "1" ]] && exit 0

HOOK_INPUT=$(cat)
SESSION_ID=$(echo "$HOOK_INPUT" | "$CX_PYTHON3" -c "import json,sys; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null)
HOOK_CWD=$(echo "$HOOK_INPUT" | "$CX_PYTHON3" -c "import json,sys; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null)
[[ -z "$HOOK_CWD" ]] && HOOK_CWD="$PWD"

SESSION_DIR="/tmp/cortex_tag/${SESSION_ID}"
mkdir -p "$SESSION_DIR"

# Clean stale menu/block state on every start
rm -f "${SESSION_DIR}/block_count"

# Only clean tag files if tag was NOT successfully registered (resume re-prompts)
if ! grep -q "^PROJECT=.\+" "${SESSION_DIR}/values" 2>/dev/null; then
    rm -f "${SESSION_DIR}/values" \
          "${SESSION_DIR}/submitted"
fi

# App-type marker: only set to "cli" if SnowWork hasn't already claimed it
[[ ! -f "${SESSION_DIR}/app_type" ]] && \
    echo "cli" > "${SESSION_DIR}/app_type"

# Session-specific temp files
echo "$SESSION_ID" > "${SESSION_DIR}/session_id"
date +%s > "${SESSION_DIR}/start_ts"
echo "$HOOK_CWD" > "${SESSION_DIR}/cwd"

# Latest session pointer (for diagnostics)
echo "$SESSION_ID" > /tmp/cortex_tag/latest_session

# Detect the Snowflake connection this session should tag against
CONN="" ; CONN_SOURCE=""

# a. Hook input JSON (active CLI SQL connection — most reliable)
CONN=$(echo "$HOOK_INPUT" | "$CX_PYTHON3" -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('connection_name', d.get('connection', '')))
" 2>/dev/null)
[[ -n "$CONN" ]] && CONN_SOURCE="session"

# b. Parent process -c / --connection flag
if [[ -z "$CONN" ]]; then
    PARENT_ARGS=$(ps -o args= -p $PPID 2>/dev/null || true)
    if echo "$PARENT_ARGS" | grep -qE '\-\-connection[= ]'; then
        CONN=$(echo "$PARENT_ARGS" | sed -n 's/.*--connection[= ]\([^ ]*\).*/\1/p')
        CONN_SOURCE="-c flag"
    elif echo "$PARENT_ARGS" | grep -qE '\-c '; then
        CONN=$(echo "$PARENT_ARGS" | sed -n 's/.*-c \([^ ]*\).*/\1/p')
        CONN_SOURCE="-c flag"
    fi
fi

# c. default_connection_name from config files
if [[ -z "$CONN" ]]; then
    CONN=$(grep -m1 'default_connection_name' ~/.snowflake/connections.toml 2>/dev/null | cut -d'"' -f2)
    [[ -n "$CONN" ]] && CONN_SOURCE="connections.toml default"
fi
if [[ -z "$CONN" ]]; then
    CONN=$(grep -m1 'default_connection_name' ~/.snowflake/config.toml 2>/dev/null | cut -d'"' -f2)
    [[ -n "$CONN" ]] && CONN_SOURCE="config.toml default"
fi

# d. snow connection list fallback
if [[ -z "$CONN" ]]; then
    CONN=$("$CX_SNOW_BIN" connection list --format json 2>/dev/null \
        | "$CX_PYTHON3" -c "
import json,sys
conns=json.load(sys.stdin)
for c in conns:
    if c.get('is_default'): print(c.get('connection_name','')); break
" 2>/dev/null)
    [[ -n "$CONN" ]] && CONN_SOURCE="snow default"
fi
echo "$CONN" > "${SESSION_DIR}/connection"

echo ""
echo "  Project-Milestone ID Tracking Active: Build v1.8.2"
echo "  Session ID: ${SESSION_ID}"
if [[ -n "$CONN" ]]; then
    echo "  Active Connection: ${CONN} (${CONN_SOURCE})"
else
    echo "  Active Connection: ⚠ Not detected — start with: snow cortex code -c <connection_name>"
fi
echo ""
echo "  Get started:"
echo "    1. /sd-submit-info           Tag this session with a project/milestone"
echo "    2. /sd-project-list-setup    Generate your project list (one-time setup)"
echo "    3. /sd-verify-tracking       Validate your tracking configuration"
echo ""

exit 0
