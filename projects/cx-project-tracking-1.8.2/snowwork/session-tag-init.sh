#!/bin/bash

# --- Binary resolution (no PATH mutation) ---
CX_BASE="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"
CX_PYTHON3="$(cat "$CX_BASE/.python3_path" 2>/dev/null)/python3"
[[ ! -x "$CX_PYTHON3" ]] && CX_PYTHON3="$(command -v python3 2>/dev/null)"
[[ ! -x "$CX_PYTHON3" ]] && { echo "python3 not found" >&2; exit 1; }

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

# App-type marker: SnowWork always overwrites (takes priority over CLI)
echo "snowwork" > "${SESSION_DIR}/app_type"

echo "$SESSION_ID" > "${SESSION_DIR}/session_id"
date +%s > "${SESSION_DIR}/start_ts"
echo "$HOOK_CWD" > "${SESSION_DIR}/cwd"
mkdir -p /tmp/cortex_tag/snowwork
echo "$SESSION_ID" > /tmp/cortex_tag/snowwork/latest_session

# Detect the Snowflake connection this session should tag against
CONN="" ; CONN_SOURCE=""

# a. Hook input JSON (active SQL connection — most reliable)
CONN=$(echo "$HOOK_INPUT" | "$CX_PYTHON3" -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('connection_name', d.get('connection', '')))
" 2>/dev/null)
[[ -n "$CONN" ]] && CONN_SOURCE="session"

# b. settings.json cortexAgentConnectionName
if [[ -z "$CONN" ]]; then
    SETTINGS_FILE="$HOME/.snowflake/cortex/settings.json"
    if [[ -f "$SETTINGS_FILE" ]]; then
        CONN=$("$CX_PYTHON3" -c "import json; d=json.load(open('$SETTINGS_FILE')); print(d.get('cortexAgentConnectionName',''))" 2>/dev/null)
        [[ -n "$CONN" ]] && CONN_SOURCE="settings.json"
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
echo "$CONN" > "${SESSION_DIR}/connection"

echo ""
echo "  Project-Milestone ID Tracking Active: Build v1.8.2 (SnowWork)"
echo "  Session ID: ${SESSION_ID}"
if [[ -n "$CONN" ]]; then
    echo "  Active Connection: ${CONN} (${CONN_SOURCE})"
else
    echo "  Active Connection: ⚠ Not detected"
fi
echo ""
echo "  Get started:"
echo "    1. /sd-submit-info           Tag this session with a project/milestone"
echo "    2. /sd-project-list-setup    Generate your project list (one-time setup)"
echo "    3. /sd-verify-tracking       Validate your tracking configuration"
echo ""

exit 0
