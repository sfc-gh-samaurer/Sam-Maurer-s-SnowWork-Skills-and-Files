#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Test: install.sh on Linux (simulates WSL / Ubuntu)
# ═══════════════════════════════════════════════════════════════
# Validates install.sh runs correctly on a clean Linux environment.
# Does NOT require snow CLI or Snowflake connectivity.
# Focuses on: directory creation, file copies, CRLF fix, JSON merge.
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✓ PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ FAIL: $1"; FAIL=$((FAIL + 1)); }
warn() { echo "  ⚠ WARN: $1"; WARN=$((WARN + 1)); }

echo ""
echo "═══ install.sh — Linux Test Suite ═══"
echo ""

SNOWFLAKE_DIR="$HOME/.snowflake"
CORTEX_DIR="$SNOWFLAKE_DIR/cortex"
HOOKS_DIR="$CORTEX_DIR/hooks"
TARGET_DIR="$HOOKS_DIR/cx_projects_tracking"
HOOKS_JSON="$CORTEX_DIR/hooks.json"
SETTINGS_JSON="$CORTEX_DIR/settings.json"

# --- Fixtures ---
echo "--- Setting up fixtures ---"
mkdir -p "$SNOWFLAKE_DIR"
mkdir -p "$CORTEX_DIR"
cat > "$SNOWFLAKE_DIR/connections.toml" << 'TOML'
[snowhouse]
account = "sfcogsops-snowhouse_aws_us_west_2"
user = "testuser"
authenticator = "externalbrowser"
TOML
echo "  fixtures ready"
echo ""

# --- Test 1: install.sh completes without error ---
echo "--- Test 1: install.sh runs to completion ---"
cd /project
if bash install.sh <<< "y" 2>&1; then
    pass "install.sh exited 0"
else
    fail "install.sh exited non-zero"
fi
echo ""

# --- Test 2: Target directory was created ---
echo "--- Test 2: Target directory structure ---"
if [[ -d "$TARGET_DIR" ]]; then
    pass "Target directory exists: $TARGET_DIR"
else
    fail "Target directory missing"
fi

if [[ -d "$TARGET_DIR/cli" ]]; then
    pass "cli/ subdirectory exists"
else
    fail "cli/ subdirectory missing"
fi

if [[ -d "$TARGET_DIR/snowwork" ]]; then
    pass "snowwork/ subdirectory exists"
else
    fail "snowwork/ subdirectory missing"
fi
echo ""

# --- Test 3: Hook scripts were copied ---
echo "--- Test 3: Hook scripts copied ---"
for f in cli/session-tag-init.sh cli/user-prompt-check.sh cli/session-end.sh snowwork/session-tag-init.sh snowwork/user-prompt-check.sh snowwork/session-end.sh; do
    if [[ -f "$TARGET_DIR/$f" ]]; then
        pass "Copied: $f"
    else
        fail "Missing: $f"
    fi
done
echo ""

# --- Test 4: Scripts are executable ---
echo "--- Test 4: Script permissions ---"
for f in cli/session-tag-init.sh cli/user-prompt-check.sh cli/session-end.sh snowwork/session-tag-init.sh snowwork/user-prompt-check.sh snowwork/session-end.sh; do
    if [[ -x "$TARGET_DIR/$f" ]]; then
        pass "Executable: $f"
    else
        warn "Not executable: $f (may be fine on Windows)"
    fi
done
echo ""

# --- Test 5: No CRLF in copied scripts ---
echo "--- Test 5: Line endings (LF only) ---"
CRLF_COUNT=0
for f in "$TARGET_DIR"/cli/*.sh "$TARGET_DIR"/snowwork/*.sh; do
    if [[ -f "$f" ]] && grep -qP '\r$' "$f" 2>/dev/null; then
        fail "CRLF found in: $f"
        CRLF_COUNT=$((CRLF_COUNT + 1))
    fi
done
if [[ "$CRLF_COUNT" -eq 0 ]]; then
    pass "All scripts have LF line endings"
fi
echo ""

# --- Test 6: hooks.json was created/updated ---
echo "--- Test 6: hooks.json ---"
if [[ -f "$HOOKS_JSON" ]]; then
    pass "hooks.json exists"
    if python3 -c "
import json, sys
with open('$HOOKS_JSON') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
ss = hooks.get('SessionStart', [])
ups = hooks.get('UserPromptSubmit', [])
se = hooks.get('SessionEnd', [])
found_ss = any('cx_projects_tracking' in str(e) for e in ss)
found_ups = any('cx_projects_tracking' in str(e) for e in ups)
found_se = any('cx_projects_tracking' in str(e) for e in se)
if found_ss and found_ups and found_se:
    print('OK')
    sys.exit(0)
print(f'SS={found_ss} UPS={found_ups} SE={found_se}')
sys.exit(1)
" 2>/dev/null; then
        pass "hooks.json has SessionStart + UserPromptSubmit + SessionEnd entries"
    else
        fail "hooks.json missing expected hook entries"
    fi
else
    fail "hooks.json not created"
fi
echo ""

# --- Test 7: settings.json was created/updated ---
echo "--- Test 7: settings.json ---"
if [[ -f "$SETTINGS_JSON" ]]; then
    pass "settings.json exists"
    if python3 -c "
import json, sys
with open('$SETTINGS_JSON') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
ss = hooks.get('SessionStart', [])
ups = hooks.get('UserPromptSubmit', [])
se = hooks.get('SessionEnd', [])
found_ss = any('cx_projects_tracking' in str(e) and 'snowwork' in str(e) for e in ss)
found_ups = any('cx_projects_tracking' in str(e) and 'snowwork' in str(e) for e in ups)
found_se = any('cx_projects_tracking' in str(e) and 'snowwork' in str(e) for e in se)
if found_ss and found_ups and found_se:
    print('OK')
    sys.exit(0)
print(f'SS={found_ss} UPS={found_ups} SE={found_se}')
sys.exit(1)
" 2>/dev/null; then
        pass "settings.json has SnowWork hook entries"
    else
        fail "settings.json missing expected hook entries"
    fi
else
    fail "settings.json not created"
fi
echo ""

# --- Test 8: Idempotency — run again ---
echo "--- Test 8: Idempotency (re-run) ---"
if bash install.sh <<< "y" 2>&1; then
    pass "Second install.sh run exited 0"
else
    fail "Second install.sh run failed"
fi

ENTRY_COUNT=$(python3 -c "
import json
with open('$HOOKS_JSON') as f:
    data = json.load(f)
ss = data.get('hooks', {}).get('SessionStart', [])
count = sum(1 for e in ss if 'cx_projects_tracking' in str(e))
print(count)
" 2>/dev/null)
if [[ "$ENTRY_COUNT" == "1" ]]; then
    pass "No duplicate entries after re-install (count=$ENTRY_COUNT)"
else
    fail "Duplicate entries found after re-install (count=$ENTRY_COUNT)"
fi
echo ""

# --- Test 9: Skills installed ---
echo "--- Test 9: Skills ---"
SKILLS_DIR="$CORTEX_DIR/skills"
for skill in sd-submit-info sd-project-list-setup sd-verify-tracking; do
    if [[ -f "$SKILLS_DIR/$skill/SKILL.md" ]]; then
        pass "Skill installed: $skill"
    else
        fail "Skill missing: $skill"
    fi
done
echo ""

# --- Summary ---
echo "═══════════════════════════════════════════"
echo "  PASS: $PASS   FAIL: $FAIL   WARN: $WARN"
echo "═══════════════════════════════════════════"
echo ""

if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
exit 0
