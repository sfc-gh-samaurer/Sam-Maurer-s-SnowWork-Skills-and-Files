#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Test: CRLF detection and auto-fix in install.sh
# ═══════════════════════════════════════════════════════════════
# Injects CRLF line endings into scripts, then verifies
# install.sh Step 0.25 detects and fixes them.
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

PASS=0
FAIL=0

pass() { echo "  ✓ PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ FAIL: $1"; FAIL=$((FAIL + 1)); }

echo ""
echo "═══ CRLF Detection & Fix — Test Suite ═══"
echo ""

SNOWFLAKE_DIR="$HOME/.snowflake"
mkdir -p "$SNOWFLAKE_DIR"
cat > "$SNOWFLAKE_DIR/connections.toml" << 'TOML'
[snowhouse]
account = "sfcogsops-snowhouse_aws_us_west_2"
user = "testuser"
authenticator = "externalbrowser"
TOML

# --- Test 1: Inject CRLF into hook scripts ---
echo "--- Test 1: Inject CRLF line endings ---"
cd /project
for f in cli/session-tag-init.sh cli/user-prompt-check.sh cli/session-end.sh snowwork/session-tag-init.sh snowwork/user-prompt-check.sh snowwork/session-end.sh; do
    if [[ -f "$f" ]]; then
        sed -i 's/$/\r/' "$f"
        if grep -qP '\r$' "$f"; then
            pass "Injected CRLF: $f"
        else
            fail "CRLF injection failed: $f"
        fi
    fi
done
echo ""

# --- Test 2: Verify CRLF causes bash syntax errors ---
echo "--- Test 2: CRLF breaks bash ---"
FIRST_SCRIPT="cli/session-tag-init.sh"
if bash -n "$FIRST_SCRIPT" 2>/dev/null; then
    fail "CRLF script should fail syntax check but didn't"
else
    pass "CRLF script correctly fails bash -n syntax check"
fi
echo ""

# --- Test 3: Run install.sh (should fix CRLF) ---
echo "--- Test 3: install.sh CRLF auto-fix ---"
OUTPUT=$(bash install.sh <<< "y" 2>&1) || true
if echo "$OUTPUT" | grep -q "Fixed CRLF"; then
    pass "install.sh reported fixing CRLF"
else
    fail "install.sh did not report fixing CRLF"
fi
echo ""

# --- Test 4: Source scripts no longer have CRLF ---
echo "--- Test 4: Source scripts are clean ---"
CRLF_REMAINING=0
for f in cli/session-tag-init.sh cli/user-prompt-check.sh cli/session-end.sh snowwork/session-tag-init.sh snowwork/user-prompt-check.sh snowwork/session-end.sh; do
    if [[ -f "$f" ]] && grep -qP '\r$' "$f" 2>/dev/null; then
        fail "CRLF still present in source: $f"
        CRLF_REMAINING=$((CRLF_REMAINING + 1))
    fi
done
if [[ "$CRLF_REMAINING" -eq 0 ]]; then
    pass "All source scripts cleaned (LF only)"
fi
echo ""

# --- Test 5: Installed scripts also clean ---
echo "--- Test 5: Installed scripts are clean ---"
TARGET_DIR="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"
CRLF_INSTALLED=0
for f in "$TARGET_DIR"/cli/*.sh "$TARGET_DIR"/snowwork/*.sh; do
    if [[ -f "$f" ]] && grep -qP '\r$' "$f" 2>/dev/null; then
        fail "CRLF in installed: $f"
        CRLF_INSTALLED=$((CRLF_INSTALLED + 1))
    fi
done
if [[ "$CRLF_INSTALLED" -eq 0 ]]; then
    pass "All installed scripts are clean"
fi
echo ""

# --- Test 6: Cleaned scripts pass bash syntax check ---
echo "--- Test 6: Cleaned scripts pass syntax check ---"
for f in cli/session-tag-init.sh cli/user-prompt-check.sh cli/session-end.sh snowwork/session-tag-init.sh snowwork/user-prompt-check.sh snowwork/session-end.sh; do
    if [[ -f "$f" ]]; then
        if bash -n "$f" 2>/dev/null; then
            pass "Syntax OK: $f"
        else
            fail "Syntax error: $f"
        fi
    fi
done
echo ""

# --- Test 7: dos2unix vs sed fallback ---
echo "--- Test 7: sed fallback (no dos2unix) ---"
sed -i 's/$/\r/' cli/session-tag-init.sh
if command -v dos2unix &>/dev/null; then
    SAVED_PATH="$PATH"
    export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "$(dirname "$(which dos2unix)")" | tr '\n' ':')
fi
SCRIPT_DIR="/project"
source_file="cli/session-tag-init.sh"
if grep -qP '\r$' "$source_file" 2>/dev/null; then
    if command -v sed &>/dev/null; then
        sed -i'' $'s/\r$//' "$source_file"
        if grep -qP '\r$' "$source_file" 2>/dev/null; then
            fail "sed fallback did not remove CRLF"
        else
            pass "sed fallback successfully removed CRLF"
        fi
    else
        fail "Neither dos2unix nor sed available"
    fi
fi
if [[ -n "${SAVED_PATH:-}" ]]; then
    export PATH="$SAVED_PATH"
fi
echo ""

# --- Summary ---
echo "═══════════════════════════════════════════"
echo "  PASS: $PASS   FAIL: $FAIL"
echo "═══════════════════════════════════════════"
echo ""

if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
exit 0
