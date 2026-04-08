#!/bin/bash

CX_BASE="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"
CX_PYTHON3="$(cat "$CX_BASE/.python3_path" 2>/dev/null)/python3"
[[ ! -x "$CX_PYTHON3" ]] && CX_PYTHON3="$(command -v python3 2>/dev/null)"
[[ ! -x "$CX_PYTHON3" ]] && exit 0

HOOK_INPUT=$(cat)
SESSION_ID=$(echo "$HOOK_INPUT" | "$CX_PYTHON3" -c "import json,sys; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null)
SESSION_DIR="/tmp/cortex_tag/${SESSION_ID}"
SD_TAG_VALUES="${SESSION_DIR}/values"
SD_TAG_SUBMITTED="${SESSION_DIR}/submitted"

APP_TYPE=$(cat "${SESSION_DIR}/app_type" 2>/dev/null)
[[ "$APP_TYPE" == "snowwork" ]] && exit 0

if [[ -f "$SD_TAG_SUBMITTED" ]] && [[ -f "$SD_TAG_VALUES" ]]; then
    PROJECT=$(grep '^PROJECT=' "$SD_TAG_VALUES" 2>/dev/null | cut -d= -f2)
    if [[ "$PROJECT" == "UNTAGGED" ]]; then
        printf '{"systemMessage":"⚠ Session ended with PROJECT=UNTAGGED. Next time, run /sd-submit-info early to tag your actual project."}\n'
    fi
elif [[ ! -f "$SD_TAG_SUBMITTED" ]]; then
    printf '{"systemMessage":"⚠ Session ended without any project tag. Run /sd-submit-info at the start of your next session."}\n'
fi

exit 0
