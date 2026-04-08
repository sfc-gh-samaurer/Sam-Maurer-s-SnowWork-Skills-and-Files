#!/bin/bash

CX_BASE="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"
CX_SNOW_BIN="$(cat "$CX_BASE/.snow_path" 2>/dev/null)/snow"
[[ ! -x "$CX_SNOW_BIN" ]] && CX_SNOW_BIN="$(command -v snow 2>/dev/null)"
[[ ! -x "$CX_SNOW_BIN" ]] && exit 0

CX_PYTHON3="$(cat "$CX_BASE/.python3_path" 2>/dev/null)/python3"
[[ ! -x "$CX_PYTHON3" ]] && CX_PYTHON3="$(command -v python3 2>/dev/null)"
[[ ! -x "$CX_PYTHON3" ]] && exit 0

TAG_LOG="${CX_BASE}/.tag_log"
HOOK_INPUT=$(cat)
SESSION_ID=$(echo "$HOOK_INPUT" | "$CX_PYTHON3" -c "import json,sys; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null)
SESSION_DIR="/tmp/cortex_tag/${SESSION_ID}"
SD_TAG_VALUES="${SESSION_DIR}/values"
SD_TAG_SUBMITTED="${SESSION_DIR}/submitted"

[[ "$SD_CORTEX_TAG_ONLY" == "1" ]] && exit 0

APP_TYPE=$(cat "${SESSION_DIR}/app_type" 2>/dev/null)
[[ "$APP_TYPE" == "snowwork" ]] && exit 0

TAG_CONN=$(cat "${SESSION_DIR}/connection" 2>/dev/null)
CONN_SOURCE="session_init"
[[ -z "$TAG_CONN" ]] && CONN_SOURCE="none"

if [[ -f "$SD_TAG_SUBMITTED" ]]; then
    if [[ -f "$SD_TAG_VALUES" ]] && grep -q "^PROJECT=.\+" "$SD_TAG_VALUES" 2>/dev/null; then
        source "$SD_TAG_VALUES"
        QUERY_TAG="{\"app\":\"${APP:-cortex_code_cli}\",\"customer\":\"${CUSTOMER}\",\"project_id\":\"${PROJECT_ID}\",\"project\":\"${PROJECT}\",\"milestone_id\":\"${MILESTONE_ID}\",\"milestone\":\"${MILESTONE}\",\"email\":\"${EMAIL}\",\"session_id\":\"${SESSION_ID}\"}"
        QUERY_TAG="${QUERY_TAG//\'/\'\'}"
        "$CX_SNOW_BIN" sql -q "ALTER SESSION SET QUERY_TAG = '${QUERY_TAG}'; SELECT 1;" ${TAG_CONN:+--connection "$TAG_CONN"} >/dev/null 2>&1 &
        if [[ "$PROJECT" == "UNTAGGED" ]]; then
            REMIND_FILE="${SESSION_DIR}/untagged_remind_count"
            REMIND_COUNT=$(cat "$REMIND_FILE" 2>/dev/null)
            REMIND_COUNT=${REMIND_COUNT:-0}
            REMIND_COUNT=$((REMIND_COUNT + 1))
            echo "$REMIND_COUNT" > "$REMIND_FILE"
            if [[ $((REMIND_COUNT % 20)) -eq 0 ]]; then
                printf '{"systemMessage":"⚠ This session is still tagged as PROJECT=UNTAGGED. Run /sd-submit-info to tag your actual project and milestone."}\n'
            fi
        fi
        exit 0
    fi
    rm -f "$SD_TAG_SUBMITTED" "$SD_TAG_VALUES"
fi

BLOCK_COUNT_FILE="${SESSION_DIR}/block_count"
BLOCK_COUNT=$(cat "$BLOCK_COUNT_FILE" 2>/dev/null)
BLOCK_COUNT=${BLOCK_COUNT:-0}
BLOCK_COUNT=$((BLOCK_COUNT + 1))
echo "$BLOCK_COUNT" > "$BLOCK_COUNT_FILE"

if [[ "$BLOCK_COUNT" -lt 5 ]]; then
    REMAINING=$((5 - BLOCK_COUNT))
    printf '{"systemMessage":"⚠ This session is not tagged for SD project tracking. Run /sd-submit-info to tag it. It will auto-tag as UNTAGGED in %d prompt(s)."}\n' "$REMAINING"
    exit 0
fi

if [[ "$BLOCK_COUNT" -ge 5 ]]; then
    EMAIL=""
    for SRC in "$CX_BASE/sd_projects.txt" "$CX_BASE/.snowhouse_cache"; do
        [[ -z "$EMAIL" ]] && EMAIL=$(grep -v '^\s*#' "$SRC" 2>/dev/null | grep -v '^\s*$' | head -1 | awk -F'|' '{print $NF}' | tr -d ' ')
    done
    for SEL in "$CX_BASE/.last_selection_cli" "$CX_BASE/.last_selection_snowwork"; do
        [[ -z "$EMAIL" ]] && EMAIL=$(grep '^LAST_EMAIL=' "$SEL" 2>/dev/null | cut -d= -f2)
    done
    EMAIL="${EMAIL:-UNKNOWN}"
    EMAIL=$(echo "$EMAIL" | tr -cd 'A-Za-z0-9_.@-')

    cat > "$SD_TAG_VALUES" << EOF
APP=cortex_code_cli
CUSTOMER=UNKNOWN
PROJECT_ID=000
PROJECT=UNTAGGED
MILESTONE_ID=000
MILESTONE=UNTAGGED
EMAIL=${EMAIL}
EOF

    QUERY_TAG="{\"app\":\"cortex_code_cli\",\"customer\":\"UNKNOWN\",\"project_id\":\"000\",\"project\":\"UNTAGGED\",\"milestone_id\":\"000\",\"milestone\":\"UNTAGGED\",\"email\":\"${EMAIL}\",\"session_id\":\"${SESSION_ID}\"}"

    "$CX_SNOW_BIN" sql -q "ALTER SESSION SET QUERY_TAG = '${QUERY_TAG}'; SELECT 1;" ${TAG_CONN:+--connection "$TAG_CONN"} >/dev/null 2>&1 &
    TAG_PID=$!
    wait "$TAG_PID" 2>/dev/null
    TAG_RC=$?

    if [[ $TAG_RC -eq 0 ]]; then
        echo "$(date +%s)|${SESSION_ID}|TAG_AUTO|cli|UNTAGGED/${EMAIL}|conn=${TAG_CONN:-none}(${CONN_SOURCE})" >> "$TAG_LOG"
    else
        echo "$(date +%s)|${SESSION_ID}|TAG_FAIL|cli|auto_tag_rc=${TAG_RC}|conn=${TAG_CONN:-none}(${CONN_SOURCE})" >> "$TAG_LOG"
    fi
    touch "$SD_TAG_SUBMITTED"
    printf '{"systemMessage":"⚠ Session auto-tagged as PROJECT=UNTAGGED. Run /sd-submit-info now to tag your actual project and milestone."}\n'
fi

exit 0
