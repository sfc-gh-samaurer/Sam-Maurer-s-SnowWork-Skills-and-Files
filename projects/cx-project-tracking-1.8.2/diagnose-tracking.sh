#!/bin/zsh

# ═══════════════════════════════════════════════════════════════
# cx-project-tracking — Full Diagnostic Script
# ═══════════════════════════════════════════════════════════════
# Runs the FAQ checklist programmatically, then optionally
# captures fresh CoCo logs for hook-related error analysis.
#
# Usage:
#   zsh diagnose-tracking.sh              # run checklist only
#   zsh diagnose-tracking.sh --logs       # checklist + log capture/analysis
#   zsh diagnose-tracking.sh --logs-only  # skip checklist, just log capture
# ═══════════════════════════════════════════════════════════════

setopt NO_UNSET PIPE_FAIL 2>/dev/null

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass()  { ((PASS++)); echo "  ${GREEN}✓${NC} $1"; }
fail()  { ((FAIL++)); echo "  ${RED}✗${NC} $1"; }
warn()  { ((WARN++)); echo "  ${YELLOW}!${NC} $1"; }
info()  { echo "  ${CYAN}→${NC} $1"; }
header(){ echo ""; echo "${BOLD}$1${NC}"; }

HOOKS_DIR="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"
HOOKS_DIR_OLD="$HOME/.snowflake/cortex/hooks/cx-project-tracking"
CONNECTIONS_TOML="$HOME/.snowflake/connections.toml"
CONFIG_TOML="$HOME/.snowflake/config.toml"
HOOKS_JSON="$HOME/.snowflake/cortex/hooks.json"
SNOW_PATH_FILE="$HOOKS_DIR/.snow_path"
SD_PROJECTS="$HOOKS_DIR/sd_projects.txt"
LOG_DIR="$HOME/.snowflake/cortex/logs"
COCO_LOG="$LOG_DIR/coco.log"
COCO_ERRORS="$LOG_DIR/coco_errors.log"

MODE="check"
[[ "${1:-}" == "--logs" ]] && MODE="both"
[[ "${1:-}" == "--logs-only" ]] && MODE="logs-only"

DETECTED_CONN=""
DETECTED_AUTH=""
DETECTED_WH=""
SNOW_BIN=""
EXPECTED_VERSION="1.8.2"

find_snowhouse_conn() {
    local file="$1"
    python3 -c "
import re
with open('$file') as f:
    content = f.read()
current_section = ''
for line in content.splitlines():
    m = re.match(r'^\s*\[([^]]+)\]', line)
    if m:
        current_section = m.group(1).strip()
        continue
    if re.search(r'account\s*=\s*\"[^\"]*snowhouse[^\"]*\"', line, re.IGNORECASE):
        name = current_section.split('.')[-1] if '.' in current_section else current_section
        print(name)
        break
" 2>/dev/null
}

get_conn_field() {
    local file="$1" conn="$2" field="$3"
    python3 -c "
import re
with open('$file') as f:
    content = f.read()
in_section = False
for line in content.splitlines():
    m = re.match(r'^\s*\[([^]]+)\]', line)
    if m:
        sec = m.group(1).strip()
        bare = sec.split('.')[-1] if '.' in sec else sec
        in_section = (bare == '$conn' or sec == '$conn')
        continue
    if in_section:
        m = re.match(r'^${field}\s*=\s*\"([^\"]*)\"|^${field}\s*=\s*(.+)', line)
        if m:
            print(m.group(1) if m.group(1) is not None else m.group(2))
            break
" 2>/dev/null
}

get_raw_section_name() {
    local file="$1" conn="$2"
    python3 -c "
import re
with open('$file') as f:
    content = f.read()
for line in content.splitlines():
    m = re.match(r'^\s*\[([^]]+)\]', line)
    if m:
        sec = m.group(1).strip()
        bare = sec.split('.')[-1] if '.' in sec else sec
        if bare == '$conn' or sec == '$conn':
            print(sec)
            break
" 2>/dev/null
}

run_checklist() {
    echo ""
    echo "${BOLD}═══ cx-project-tracking Diagnostic Checklist ═══${NC}"

    # ── Check 1: Snowflake CLI ──
    header "Check 1: Snowflake CLI (snow)"

    SNOW_BIN=$(whence -p snow 2>/dev/null || which snow 2>/dev/null || true)
    if [[ -n "$SNOW_BIN" ]]; then
        pass "snow found at: $SNOW_BIN"
        SNOW_VER=$(snow --version 2>/dev/null || echo "unknown")
        if [[ "$SNOW_VER" == *"Snowflake CLI"* ]]; then
            pass "Version: $SNOW_VER"
        elif [[ "$SNOW_VER" == "unknown" ]]; then
            fail "snow --version returned nothing"
            info "The binary may be corrupted or not the Snowflake CLI"
        else
            warn "Version string unexpected: $SNOW_VER"
        fi

        SNOW_LOCATION_NOTE=""
        case "$SNOW_BIN" in
            /opt/homebrew/*|/usr/local/*)
                info "Installed via Homebrew" ;;
            */.local/bin/*|*/Library/Python/*)
                SNOW_LOCATION_NOTE="pip/pipx"
                info "Installed via pip/pipx" ;;
            */miniconda*|*/anaconda*|*/conda*)
                SNOW_LOCATION_NOTE="conda"
                info "Installed via conda" ;;
            *)
                SNOW_LOCATION_NOTE="unusual"
                info "Installed from: $SNOW_BIN" ;;
        esac
    else
        fail "snow not found in PATH"
        info "Install: brew install snowflake-cli"

        SNOWSQL_BIN=$(whence -p snowsql 2>/dev/null || which snowsql 2>/dev/null || true)
        if [[ -n "$SNOWSQL_BIN" ]]; then
            warn "snowsql found at $SNOWSQL_BIN — this is SnowSQL, NOT Snowflake CLI"
            info "The hooks need 'snow' (Snowflake CLI), not 'snowsql' (SnowSQL)"
        fi
    fi

    # ── Check 2: .snow_path ──
    header "Check 2: .snow_path (hook PATH resolution)"

    if [[ -f "$SNOW_PATH_FILE" ]]; then
        SAVED_PATH=$(cat "$SNOW_PATH_FILE")
        if [[ -d "$SAVED_PATH" ]]; then
            if [[ -x "$SAVED_PATH/snow" ]]; then
                pass ".snow_path → $SAVED_PATH (valid, contains snow binary)"
            else
                fail ".snow_path → $SAVED_PATH (directory exists but no snow binary inside)"
                info "Re-run install.sh to re-detect the CLI path"
            fi
        else
            fail ".snow_path → $SAVED_PATH (directory does not exist)"
            info "Re-run install.sh to re-detect the CLI path"
        fi
    else
        if [[ -n "$SNOW_BIN" ]]; then
            warn ".snow_path not found — hooks rely on system PATH to find snow"
            info "Re-running install.sh would create .snow_path for reliability"
        else
            fail ".snow_path not found and snow not in PATH — hooks will fail"
            info "Install snow CLI first, then re-run install.sh"
        fi
    fi

    # ── Check 3: connections.toml ──
    header "Check 3: connections.toml"

    if [[ -f "$CONNECTIONS_TOML" ]]; then
        pass "File exists"

        PERMS=$(stat -f "%Lp" "$CONNECTIONS_TOML" 2>/dev/null || stat -c "%a" "$CONNECTIONS_TOML" 2>/dev/null)
        if [[ "$PERMS" == "600" ]]; then
            pass "Permissions: $PERMS (correct)"
        else
            fail "Permissions: $PERMS (should be 600)"
            info "Fix: chmod 0600 ~/.snowflake/connections.toml"
        fi

        BAD_SECTIONS=$(grep -E '^\[connections\.' "$CONNECTIONS_TOML" 2>/dev/null || true)
        if [[ -n "$BAD_SECTIONS" ]]; then
            fail "Found [connections.xxx] prefix — this is config.toml syntax, not connections.toml"
            info "In connections.toml, use bare names: [snowhouse] instead of [connections.snowhouse]"
            echo "$BAD_SECTIONS" | while read -r line; do info "  $line"; done
        else
            pass "Section headers use correct bare format (no [connections.] prefix)"
        fi

        CONN=$(find_snowhouse_conn "$CONNECTIONS_TOML")
        if [[ -n "$CONN" ]]; then
            pass "Snowhouse connection found: [$CONN]"
            DETECTED_CONN="$CONN"

            ACCT=$(get_conn_field "$CONNECTIONS_TOML" "$CONN" "account")
            [[ -n "$ACCT" ]] && pass "account = $ACCT" || fail "account field missing"

            WH=$(get_conn_field "$CONNECTIONS_TOML" "$CONN" "warehouse")
            if [[ -n "$WH" ]]; then
                pass "warehouse = $WH"
                DETECTED_WH="$WH"
            else
                fail "warehouse not set — this is the #1 cause of 'No active warehouse' errors"
                info "FIX: Add to your [$CONN] section: warehouse = \"XSMALL\""
                info "See Check 9 below for more details"
            fi

            ROLE=$(get_conn_field "$CONNECTIONS_TOML" "$CONN" "role")
            if [[ "$ROLE" == "TECHNICAL_ACCOUNT_MANAGER" ]]; then
                pass "role = TECHNICAL_ACCOUNT_MANAGER"
            elif [[ -n "$ROLE" ]]; then
                warn "role = $ROLE (should be TECHNICAL_ACCOUNT_MANAGER for project table access)"
            else
                fail "role not set"
                info "Add: role = \"TECHNICAL_ACCOUNT_MANAGER\""
            fi

            AUTH=$(get_conn_field "$CONNECTIONS_TOML" "$CONN" "authenticator")
            AUTH_LC=$(echo "$AUTH" | tr '[:upper:]' '[:lower:]')
            if [[ "$AUTH_LC" == "externalbrowser" ]]; then
                pass "authenticator = externalbrowser"
            elif [[ -n "$AUTH" ]]; then
                warn "authenticator = $AUTH (externalbrowser recommended — PATs disabled March 31)"
            else
                warn "authenticator not set (defaults to snowflake — externalbrowser recommended)"
            fi
            DETECTED_AUTH="$AUTH"

            PWD_FIELD=$(get_conn_field "$CONNECTIONS_TOML" "$CONN" "password")
            TOKEN_FIELD=$(get_conn_field "$CONNECTIONS_TOML" "$CONN" "token")
            if [[ -n "$PWD_FIELD" ]] || [[ -n "$TOKEN_FIELD" ]]; then
                warn "password/token field present — remove it if using externalbrowser auth"
                info "PAT fields can cause 300s timeouts or wrong role resolution"
            fi
        else
            fail "No Snowhouse connection found (no account value containing 'snowhouse')"
            info "Add a connection with: account = \"SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2\""
        fi
    else
        fail "File not found: $CONNECTIONS_TOML"
        info "The hook reads connections from this file, not config.toml"
        info "Run install.sh or create it manually"
    fi

    # ── Check 4: config.toml ──
    header "Check 4: config.toml (format & duplicate check)"

    if [[ -f "$CONFIG_TOML" ]]; then
        PERMS_CFG=$(stat -f "%Lp" "$CONFIG_TOML" 2>/dev/null || stat -c "%a" "$CONFIG_TOML" 2>/dev/null)
        if [[ "$PERMS_CFG" == "600" ]]; then
            pass "Permissions: $PERMS_CFG (correct)"
        else
            warn "Permissions: $PERMS_CFG (should be 600)"
            info "Fix: chmod 0600 ~/.snowflake/config.toml"
        fi

        BARE_SECTIONS_IN_CONFIG=$(grep -E '^\[[a-zA-Z0-9_-]+\]$' "$CONFIG_TOML" 2>/dev/null \
            | grep -v '^\[default\]$' \
            | grep -v '^\[options\]$' \
            | grep -v '^\[cli\]$' || true)
        if [[ -n "$BARE_SECTIONS_IN_CONFIG" ]]; then
            warn "config.toml has bare connection sections (should use [connections.xxx] prefix):"
            echo "$BARE_SECTIONS_IN_CONFIG" | while read -r line; do info "  $line → should be [connections.${line//[\[\]]/}]"; done
            info "In config.toml, connections use [connections.name] format"
            info "In connections.toml, connections use bare [name] format"
        else
            pass "config.toml uses correct [connections.xxx] format"
        fi

        CONFIG_CONN=$(find_snowhouse_conn "$CONFIG_TOML")
        if [[ -n "$CONFIG_CONN" ]] && [[ -n "$DETECTED_CONN" ]]; then
            warn "Snowhouse connection found in BOTH config.toml AND connections.toml"
            info "Remove from config.toml to avoid confusion — hooks only read connections.toml"

            CFG_WH=$(get_conn_field "$CONFIG_TOML" "$CONFIG_CONN" "warehouse")
            CFG_ROLE=$(get_conn_field "$CONFIG_TOML" "$CONFIG_CONN" "role")
            CFG_AUTH=$(get_conn_field "$CONFIG_TOML" "$CONFIG_CONN" "authenticator")
            DIFFS=""
            [[ -n "$CFG_WH" ]] && [[ "$CFG_WH" != "$DETECTED_WH" ]] && DIFFS="${DIFFS}\n    warehouse: config.toml=$CFG_WH vs connections.toml=$DETECTED_WH"
            [[ -n "$CFG_ROLE" ]] && [[ "$CFG_ROLE" != "$ROLE" ]] && DIFFS="${DIFFS}\n    role: config.toml=$CFG_ROLE vs connections.toml=$ROLE"
            [[ -n "$CFG_AUTH" ]] && [[ "$CFG_AUTH" != "$DETECTED_AUTH" ]] && DIFFS="${DIFFS}\n    authenticator: config.toml=$CFG_AUTH vs connections.toml=$DETECTED_AUTH"
            if [[ -n "$DIFFS" ]]; then
                warn "Duplicate entries have DIFFERENT values:$DIFFS"
                info "The hook reads connections.toml — the config.toml values are ignored but confusing"
            fi
        elif [[ -n "$CONFIG_CONN" ]] && [[ -z "$DETECTED_CONN" ]]; then
            warn "Snowhouse connection only in config.toml — hook won't find it there"
            info "Move it to connections.toml (the hook only reads connections.toml)"

            CONFIG_RAW_SEC=$(get_raw_section_name "$CONFIG_TOML" "$CONFIG_CONN")
            if [[ "$CONFIG_RAW_SEC" == connections.* ]]; then
                info "Section [$CONFIG_RAW_SEC] in config.toml → use [$CONFIG_CONN] (bare) in connections.toml"
            fi
        else
            pass "No duplicate Snowhouse entry in config.toml"
        fi
    else
        info "config.toml not found (that's fine — hooks read connections.toml)"
    fi

    # ── Check 5: hooks.json ──
    header "Check 5: hooks.json"

    if [[ -f "$HOOKS_JSON" ]]; then
        pass "File exists"

        HOOKS_PARSE=$(python3 -c "
import json, sys
with open('$HOOKS_JSON') as f:
    data = json.load(f)

def search_nested(obj, target_event, target_path):
    if isinstance(obj, dict):
        if target_event in obj:
            val = obj[target_event]
            if isinstance(val, list):
                for item in val:
                    if search_nested(item, target_event, target_path):
                        return True
            elif isinstance(val, dict):
                if search_nested(val, target_event, target_path):
                    return True
        for k, v in obj.items():
            if k == 'command' and isinstance(v, str) and target_path in v:
                return True
            if isinstance(v, (dict, list)):
                if search_nested(v, target_event, target_path):
                    return True
    elif isinstance(obj, list):
        for item in obj:
            if search_nested(item, target_event, target_path):
                return True
    return False

hooks_key = data.get('hooks', data) if isinstance(data, dict) else data
ss = False
ups = False
se = False
if isinstance(hooks_key, dict):
    for event_name, event_val in hooks_key.items():
        if 'SessionStart' in event_name:
            if search_nested(event_val, event_name, 'cx_projects_tracking'):
                ss = True
        if 'UserPromptSubmit' in event_name:
            if search_nested(event_val, event_name, 'cx_projects_tracking'):
                ups = True
        if 'SessionEnd' in event_name:
            if search_nested(event_val, event_name, 'cx_projects_tracking'):
                se = True
elif isinstance(hooks_key, list):
    for h in hooks_key:
        ev = h.get('event','')
        cmd = h.get('command','') + ' ' + ' '.join(h.get('args',[]))
        if 'SessionStart' in ev and 'cx_projects_tracking' in cmd: ss = True
        if 'UserPromptSubmit' in ev and 'cx_projects_tracking' in cmd: ups = True
        if 'SessionEnd' in ev and 'cx_projects_tracking' in cmd: se = True

if not ss and not ups:
    if search_nested(data, '', 'cx_projects_tracking'):
        ss_deep = search_nested(data.get('hooks',{}).get('SessionStart',{}), '', 'cx_projects_tracking') if isinstance(data, dict) else False
        ups_deep = search_nested(data.get('hooks',{}).get('UserPromptSubmit',{}), '', 'cx_projects_tracking') if isinstance(data, dict) else False
        if ss_deep: ss = True
        if ups_deep: ups = True
        se_deep = search_nested(data.get('hooks',{}).get('SessionEnd',{}), '', 'cx_projects_tracking') if isinstance(data, dict) else False
        if se_deep: se = True

print(f'ss={\"found\" if ss else \"missing\"}')
print(f'ups={\"found\" if ups else \"missing\"}')
print(f'se={\"found\" if se else \"missing\"}')
" 2>/dev/null || echo "parse_error")

        if [[ "$HOOKS_PARSE" == "parse_error" ]]; then
            fail "hooks.json could not be parsed — may be invalid JSON"
            info "Check for trailing commas, missing brackets, or syntax errors"
        else
            SS_STATUS=$(echo "$HOOKS_PARSE" | grep 'ss=' | cut -d= -f2)
            UPS_STATUS=$(echo "$HOOKS_PARSE" | grep 'ups=' | cut -d= -f2)
            SE_STATUS=$(echo "$HOOKS_PARSE" | grep 'se=' | cut -d= -f2)

            if [[ "$SS_STATUS" == "found" ]]; then
                pass "SessionStart hook registered for cx_projects_tracking"
            else
                fail "SessionStart hook NOT registered for cx_projects_tracking"
                info "Re-run install.sh to register hooks"
            fi

            if [[ "$UPS_STATUS" == "found" ]]; then
                pass "UserPromptSubmit hook registered for cx_projects_tracking"
            else
                fail "UserPromptSubmit hook NOT registered for cx_projects_tracking"
                info "Re-run install.sh to register hooks"
            fi

            if [[ "$SE_STATUS" == "found" ]]; then
                pass "SessionEnd hook registered for cx_projects_tracking"
            else
                warn "SessionEnd hook NOT registered (v1.8.2+ feature)"
                info "Re-run install.sh to register hooks"
            fi
        fi
    else
        fail "File not found: $HOOKS_JSON"
        info "Re-run install.sh to create it"
    fi

    # ── Check 6: Hook scripts ──
    header "Check 6: Hook scripts"

    for SCRIPT in "cli/session-tag-init.sh" "cli/user-prompt-check.sh" "cli/session-end.sh"; do
        FULL_PATH="$HOOKS_DIR/$SCRIPT"
        if [[ -f "$FULL_PATH" ]]; then
            pass "$SCRIPT exists"
            if [[ -x "$FULL_PATH" ]] || head -1 "$FULL_PATH" | grep -q "#!/bin/bash"; then
                pass "$SCRIPT is executable or has bash shebang"
            else
                warn "$SCRIPT may not be executable — run: chmod +x $FULL_PATH"
            fi
        else
            fail "$SCRIPT NOT FOUND at $FULL_PATH"
            info "Re-run install.sh to copy hook scripts"
        fi
    done

    if [[ -d "$HOOKS_DIR" ]]; then
        pass "Hook directory exists: $HOOKS_DIR"
    else
        fail "Hook directory missing: $HOOKS_DIR"
        info "Re-run install.sh"
    fi

    INIT_SCRIPT="$HOOKS_DIR/cli/session-tag-init.sh"
    if [[ -f "$INIT_SCRIPT" ]]; then
        INSTALLED_VER=$(grep -oE "Build v[0-9]+\.[0-9]+\.[0-9]+" "$INIT_SCRIPT" 2>/dev/null | head -1 | sed 's/Build v//')
        if [[ -n "$INSTALLED_VER" ]]; then
            if [[ "$INSTALLED_VER" == "$EXPECTED_VERSION" ]]; then
                pass "Installed version: v$INSTALLED_VER (current)"
            else
                warn "Installed version: v$INSTALLED_VER (expected v$EXPECTED_VERSION)"
                info "Re-run install.sh from the latest release to update"
            fi
        else
            warn "Could not detect installed version from session-tag-init.sh"
        fi
    fi

    for VARIANT in cli snowwork; do
        UPC_SCRIPT="$HOOKS_DIR/$VARIANT/user-prompt-check.sh"
        if [[ -f "$UPC_SCRIPT" ]]; then
            if grep -q 'systemMessage\|IMPORTANT: You MUST display' "$UPC_SCRIPT" 2>/dev/null; then
                pass "$VARIANT/user-prompt-check.sh has warning output (v1.8.2+)"
            else
                warn "$VARIANT/user-prompt-check.sh missing warning output — may be outdated"
                info "Re-run install.sh from the latest release to update"
            fi
        fi
    done

    # ── Check 7: Old install ──
    header "Check 7: Old install cleanup"

    if [[ -d "$HOOKS_DIR_OLD" ]]; then
        warn "Old hook directory exists: $HOOKS_DIR_OLD"
        info "Remove it: rm -rf $HOOKS_DIR_OLD"
        info "The old naming (hyphens) can conflict with the current install (underscores)"
    else
        pass "No old cx-project-tracking directory found"
    fi

    # ── Check 8: snow connection test ──
    header "Check 8: Connection test"

    if [[ -n "$DETECTED_CONN" ]] && [[ -n "$SNOW_BIN" ]]; then
        AUTH_TYPE_LC=$(echo "${DETECTED_AUTH:-}" | tr '[:upper:]' '[:lower:]')
        CONN_TMP="/tmp/diag_conn_test_$$.txt"
        if [[ "$AUTH_TYPE_LC" == "externalbrowser" ]]; then
            info "Auth is externalbrowser — this may open a browser window"
            info "Running: snow connection test -c $DETECTED_CONN (30s timeout)"
            echo ""
            snow connection test -c "$DETECTED_CONN" > "$CONN_TMP" 2>&1 &
            SNOW_PID=$!
            ( sleep 30 && kill $SNOW_PID 2>/dev/null ) &
            WD_PID=$!
            wait $SNOW_PID 2>/dev/null
            CONN_RC=$?
            kill $WD_PID 2>/dev/null 
            wait $WD_PID 2>/dev/null
            cat "$CONN_TMP" 2>/dev/null
            rm -f "$CONN_TMP"
            echo ""
            if [[ $CONN_RC -eq 0 ]]; then
                pass "snow connection test PASSED (using $SNOW_BIN)"
            elif [[ $CONN_RC -eq 137 ]] || [[ $CONN_RC -eq 143 ]]; then
                warn "snow connection test timed out after 30s (browser auth may not have completed)"
                info "To initiate browser auth from the terminal, run:"
                info "  snow connection test -c $DETECTED_CONN"
                info "This opens your default browser for SSO. Complete the login, then return here."
                info "After the first successful auth, an ID_TOKEN is cached in the macOS keychain"
                info "and subsequent connections won't need the browser."
            else
                fail "snow connection test FAILED (exit code $CONN_RC, using $SNOW_BIN)"
                info "Fix the connection issues before troubleshooting hooks"
            fi
        else
            info "Running: snow connection test -c $DETECTED_CONN"
            echo ""
            if snow connection test -c "$DETECTED_CONN" 2>&1; then
                echo ""
                pass "snow connection test PASSED (using $SNOW_BIN)"
            else
                echo ""
                fail "snow connection test FAILED (using $SNOW_BIN, see output above)"
                info "Fix the connection issues before troubleshooting hooks"
            fi
        fi
    elif [[ -z "$SNOW_BIN" ]]; then
        fail "Cannot test connection — snow CLI not found"
    elif [[ -z "$DETECTED_CONN" ]]; then
        fail "Cannot test connection — no Snowhouse connection detected"
    fi

    # ── Check 9: Warehouse accessibility ──
    header "Check 9: Warehouse accessibility"

    if [[ -z "$DETECTED_WH" ]] && [[ -n "$DETECTED_CONN" ]]; then
        fail "No 'warehouse' field in connections.toml [$DETECTED_CONN]"
        info "This is the #1 cause of 'No active warehouse detected' errors"
        info "FIX: Add this line to your [$DETECTED_CONN] section in ~/.snowflake/connections.toml:"
        info "  warehouse = \"XSMALL\""
        info "XSMALL and SNOWADHOC are both available to TECHNICAL_ACCOUNT_MANAGER role"
    elif [[ -n "$DETECTED_CONN" ]] && [[ -n "$SNOW_BIN" ]] && [[ -n "$DETECTED_WH" ]]; then
        pass "warehouse = $DETECTED_WH is set in connections.toml"
        info "Checking if warehouse '$DETECTED_WH' is usable with connection '$DETECTED_CONN'..."
        WH_OUTPUT=$(snow sql -q "SELECT CURRENT_WAREHOUSE();" --connection "$DETECTED_CONN" --format json 2>&1) && WH_RC=0 || WH_RC=$?
        if [[ $WH_RC -eq 0 ]]; then
            CURRENT_WH=$(echo "$WH_OUTPUT" | python3 -c "
import json, sys
try:
    rows = json.load(sys.stdin)
    v = rows[0].get('CURRENT_WAREHOUSE()', '')
    print(v if v and v != 'null' else '')
except:
    print('')
" 2>/dev/null)
            if [[ -n "$CURRENT_WH" ]]; then
                pass "Active warehouse confirmed: $CURRENT_WH"
                if [[ "$CURRENT_WH" != "$DETECTED_WH" ]]; then
                    warn "Active warehouse ($CURRENT_WH) differs from connection config ($DETECTED_WH)"
                    info "Snowflake may be using your user-level DEFAULT_WAREHOUSE instead"
                    info "This usually works fine, but if you hit issues, ensure both match"
                fi
            else
                fail "Query succeeded but CURRENT_WAREHOUSE() returned null"
                info "Warehouse '$DETECTED_WH' may be suspended, dropped, or your role can't access it"
                info "FIX: Try a different warehouse in connections.toml:"
                info "  warehouse = \"SNOWADHOC\""
            fi
        else
            fail "Could not query CURRENT_WAREHOUSE() — connection or auth may be broken"
            info "This is what the hook does behind the scenes — if this fails, the hook fails"
            WH_ERR=$(echo "$WH_OUTPUT" | tail -3)
            [[ -n "$WH_ERR" ]] && info "Error: $WH_ERR"
        fi

        info "Checking if SNOWADHOC fallback warehouse works..."
        FALLBACK_OUTPUT=$(snow sql -q "USE WAREHOUSE SNOWADHOC;" --connection "$DETECTED_CONN" 2>&1) && FB_RC=0 || FB_RC=$?
        if [[ $FB_RC -eq 0 ]]; then
            pass "SNOWADHOC fallback warehouse is accessible"
        else
            warn "SNOWADHOC fallback not accessible (hook falls back to this if configured warehouse fails)"
        fi
    else
        info "Skipping warehouse live check (no connection or CLI available)"
        if [[ -n "$DETECTED_WH" ]]; then
            pass "warehouse = $DETECTED_WH is set in connections.toml (cannot verify live)"
        fi
    fi

    # ── Check 10: sd_projects.txt ──
    header "Check 10: sd_projects.txt (primary project list)"

    if [[ -f "$SD_PROJECTS" ]]; then
        LINE_COUNT=$(wc -l < "$SD_PROJECTS" | tr -d ' ')
        if [[ "$LINE_COUNT" -gt 0 ]]; then
            pass "sd_projects.txt exists with $LINE_COUNT entries"
        else
            warn "sd_projects.txt exists but is empty"
            info "Run 'sd-project-list-setup' in a Cortex Code or SnowWork session to populate it"
        fi
    else
        warn "sd_projects.txt not found — sessions will fall back to live Snowhouse queries"
        info "Run 'sd-project-list-setup' in a Cortex Code or SnowWork session to generate it"
        info "This is recommended after installation so future sessions load the project list instantly"
    fi

    # ── Summary ──
    echo ""
    echo "${BOLD}═══ Summary ═══${NC}"
    echo "  ${GREEN}✓ ${PASS} passed${NC}    ${RED}✗ ${FAIL} failed${NC}    ${YELLOW}! ${WARN} warnings${NC}"

    if [[ $FAIL -eq 0 ]]; then
        echo ""
        echo "  ${GREEN}All critical checks passed.${NC}"
        if [[ $WARN -gt 0 ]]; then
            echo "  ${YELLOW}Review warnings above — they may cause issues in edge cases.${NC}"
        fi
    else
        echo ""
        echo "  ${RED}$FAIL check(s) failed. Fix the items marked with ✗ above.${NC}"
        echo "  Work through them top to bottom — earlier failures often cause later ones."
    fi
    echo ""
}

run_log_capture() {
    echo ""
    echo "${BOLD}═══ Log Capture & Analysis ═══${NC}"
    echo ""

    if [[ ! -d "$LOG_DIR" ]]; then
        fail "Log directory not found: $LOG_DIR"
        info "CoCo hasn't been run yet, or logs are in a different location"
        return 1
    fi

    LOG_BACKUP="$LOG_DIR/pre_diag_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$LOG_BACKUP"

    if [[ -f "$COCO_LOG" ]]; then
        cp "$COCO_LOG" "$LOG_BACKUP/"
        info "Backed up coco.log to $LOG_BACKUP/"
    fi
    if [[ -f "$COCO_ERRORS" ]]; then
        cp "$COCO_ERRORS" "$LOG_BACKUP/"
        info "Backed up coco_errors.log to $LOG_BACKUP/"
    fi

    : > "$COCO_LOG" 2>/dev/null || true
    : > "$COCO_ERRORS" 2>/dev/null || true
    pass "Cleared coco.log and coco_errors.log"

    echo ""
    echo "${BOLD}Now do this in a separate terminal:${NC}"
    echo "  1. Start a new CoCo CLI session (cortex -c <connection>)"
    echo "  2. Wait for the session to start"
    echo "  3. Reproduce the error (type a prompt and press Enter)"
    echo "  4. Once you see the error (or the session completes), exit the session"
    echo ""
    echo "${CYAN}Press Enter here when you've completed the above steps...${NC}"
    read -r

    echo ""
    echo "${BOLD}═══ Analyzing fresh logs ═══${NC}"
    echo ""

    if [[ ! -s "$COCO_LOG" ]]; then
        fail "coco.log is empty — CoCo session may not have started, or logs go elsewhere"
        return 1
    fi

    LOG_LINES=$(wc -l < "$COCO_LOG" | tr -d ' ')
    ERROR_LINES=$(wc -l < "$COCO_ERRORS" 2>/dev/null | tr -d ' ')
    info "coco.log: $LOG_LINES lines"
    info "coco_errors.log: ${ERROR_LINES:-0} lines"
    echo ""

    # A. SessionStart
    header "A. SessionStart hook"
    SS_EXEC=$(grep -i "Executing SessionStart hooks" "$COCO_LOG" 2>/dev/null || true)
    SS_DONE=$(grep -i "SessionStart hooks completed" "$COCO_LOG" 2>/dev/null || true)
    if [[ -n "$SS_EXEC" ]]; then
        pass "SessionStart hooks executed"
        SESSION_ID=$(echo "$SS_EXEC" | grep -oE "sessionId: [a-f0-9-]+" | head -1 | cut -d' ' -f2)
        [[ -n "$SESSION_ID" ]] && info "Session ID: $SESSION_ID"
    else
        fail "SessionStart hooks did NOT execute"
        info "Check hooks.json registration (Check 5 above)"
    fi
    if [[ -n "$SS_DONE" ]]; then
        pass "SessionStart hooks completed successfully"
    elif [[ -n "$SS_EXEC" ]]; then
        fail "SessionStart hooks started but did not complete"
    fi

    SS_ERROR=$(grep -iE "SessionStart.*(error|fail|timeout)" "$COCO_LOG" 2>/dev/null || true)
    if [[ -n "$SS_ERROR" ]]; then
        fail "SessionStart errors detected:"
        echo "$SS_ERROR" | head -5 | while read -r line; do info "  $line"; done
    fi

    # B. Hook service
    header "B. Hook service"
    HOOK_INIT=$(grep -i "Hook service initialized" "$COCO_LOG" 2>/dev/null || true)
    if [[ -n "$HOOK_INIT" ]]; then
        pass "Hook service initialized"
    else
        fail "Hook service did not initialize"
    fi

    # C. UserPromptSubmit
    header "C. UserPromptSubmit hook"
    UPS_BLOCKED=$(grep -i "UserPromptSubmit hook blocked" "$COCO_LOG" 2>/dev/null || true)
    UPS_CONTEXT=$(grep -i "UserPromptSubmit hook added context" "$COCO_LOG" 2>/dev/null || true)
    UPS_SYSMSG=$(grep -i "UserPromptSubmit.*systemMessage" "$COCO_LOG" 2>/dev/null || true)
    UPS_ERROR=$(grep -iE "UserPromptSubmit.*(error|fail|timeout)" "$COCO_LOG" 2>/dev/null || true)

    if [[ -n "$UPS_CONTEXT" ]] || [[ -n "$UPS_SYSMSG" ]]; then
        pass "UserPromptSubmit hook fired and injected systemMessage (warning delivered)"
    elif [[ -n "$UPS_BLOCKED" ]]; then
        pass "UserPromptSubmit hook fired and blocked (showing message)"
        echo "$UPS_BLOCKED" | head -3 | while read -r line; do
            MSG=$(echo "$line" | sed 's/.*blocked message: //')
            info "  ${MSG:0:120}"
        done
    else
        fail "No UserPromptSubmit hook activity detected"
        info "Did you submit a prompt? The hook only fires when you type something and press Enter"
    fi

    if [[ -n "$UPS_ERROR" ]]; then
        fail "UserPromptSubmit errors:"
        echo "$UPS_ERROR" | head -5 | while read -r line; do info "  $line"; done
    fi

    TAGGED=$(grep -iE "Session tagged|YOU MAY CONTINUE NORMAL USE" "$COCO_LOG" 2>/dev/null || true)
    if [[ -n "$TAGGED" ]]; then
        pass "Session was successfully tagged"
        echo "$TAGGED" | head -1 | while read -r line; do
            MSG=$(echo "$line" | sed 's/.*blocked message: //')
            info "  $MSG"
        done
    elif [[ -n "$UPS_BLOCKED" ]]; then
        warn "Hook fired but session was not tagged (user may not have completed selection)"
    fi

    # D. Warehouse errors
    header "D. Warehouse errors"
    WH_ERRORS=$(grep -iE "No active warehouse|warehouse.*not available|Could not use warehouse" "$COCO_LOG" 2>/dev/null || true)
    if [[ -n "$WH_ERRORS" ]]; then
        fail "Warehouse errors detected in session:"
        echo "$WH_ERRORS" | head -5 | while read -r line; do info "  $line"; done
    else
        pass "No warehouse errors in session logs"
    fi

    # E. Error log
    header "E. Error log (coco_errors.log)"
    if [[ -s "$COCO_ERRORS" ]]; then
        HOOK_ERRORS=$(grep -iv "podman\|sandbox" "$COCO_ERRORS" 2>/dev/null || true)
        PODMAN_ERRORS=$(grep -i "podman\|sandbox" "$COCO_ERRORS" 2>/dev/null || true)

        if [[ -n "$HOOK_ERRORS" ]]; then
            fail "Non-sandbox errors found:"
            echo "$HOOK_ERRORS" | head -10 | while read -r line; do info "  $line"; done
        else
            pass "No hook-related errors in error log"
        fi

        if [[ -n "$PODMAN_ERRORS" ]]; then
            PODMAN_COUNT=$(echo "$PODMAN_ERRORS" | wc -l | tr -d ' ')
            warn "Podman/sandbox errors ($PODMAN_COUNT lines) — unrelated to tracking hooks"
        fi
    else
        pass "Error log is clean"
    fi

    # F. Permissions
    header "F. Permission issues"
    PERM_DENIED=$(grep -iE "Permission.*(denied|refused)" "$COCO_LOG" 2>/dev/null || true)
    if [[ -n "$PERM_DENIED" ]]; then
        warn "Permission denials detected:"
        echo "$PERM_DENIED" | head -5 | while read -r line; do info "  $line"; done
    else
        pass "No permission denials in session"
    fi

    # G. Connection/auth
    header "G. Connection & auth"
    AUTH_ISSUES=$(grep -iE "auth.*(fail|error)|login.*timeout|token.*expir|connection.*refuse|SSL|certificate" "$COCO_LOG" 2>/dev/null | grep -iv "podman\|sandbox" || true)
    if [[ -n "$AUTH_ISSUES" ]]; then
        fail "Auth/connection issues detected:"
        echo "$AUTH_ISSUES" | head -5 | while read -r line; do info "  $line"; done
    else
        pass "No auth/connection errors in session logs"
    fi

    # H. Timeline
    header "H. Session timeline"
    FIRST_TS=$(head -1 "$COCO_LOG" 2>/dev/null | grep -oE "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}" || true)
    LAST_TS=$(tail -1 "$COCO_LOG" 2>/dev/null | grep -oE "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}" || true)
    if [[ -n "$FIRST_TS" ]] && [[ -n "$LAST_TS" ]]; then
        info "Session window: $FIRST_TS → $LAST_TS"
    fi

    HOOK_EVENTS=$(grep -iE "SessionStart|UserPromptSubmit|Hook service|hook blocked|systemMessage|Session tagged" "$COCO_LOG" 2>/dev/null | head -20)
    if [[ -n "$HOOK_EVENTS" ]]; then
        info "Hook event timeline:"
        echo "$HOOK_EVENTS" | while read -r line; do
            TS=$(echo "$line" | grep -oE "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}" || true)
            EVENT=$(echo "$line" | sed 's/^[0-9-]* [0-9:]* - [^ ]* - [A-Z]* - //')
            echo "    ${CYAN}${TS}${NC}  ${EVENT:0:100}"
        done
    fi

    echo ""
    echo "${BOLD}═══ Log Analysis Summary ═══${NC}"
    echo "  ${GREEN}✓ ${PASS} passed${NC}    ${RED}✗ ${FAIL} failed${NC}    ${YELLOW}! ${WARN} warnings${NC}"
    echo ""
    info "Logs backed up to: $LOG_BACKUP/"
    info "Fresh logs at: $COCO_LOG and $COCO_ERRORS"
    echo ""
}

# ── Main ──
case "$MODE" in
    check)
        run_checklist
        ;;
    both)
        run_checklist
        echo ""
        echo "${BOLD}Proceeding to log capture...${NC}"
        run_log_capture
        ;;
    logs-only)
        run_log_capture
        ;;
esac
