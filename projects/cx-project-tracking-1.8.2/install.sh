#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# cx_projects_tracking — Installer
# ═══════════════════════════════════════════════════════════════
# Creates ~/.snowflake/cortex/hooks/cx_projects_tracking/,
# copies hook scripts from cli/ and snowwork/ subdirectories,
# merges entries into hooks.json, and installs skills.
#
# Prerequisites:
#   - sd_projects.txt must be in the same folder as this script
#     OR already placed in the target folder,
#     OR a Snowhouse connection must be available.
#
# Usage:  bash install.sh
# ═══════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.snowflake/cortex/hooks/cx_projects_tracking"
HOOKS_JSON="$HOME/.snowflake/cortex/hooks.json"

echo ""
echo "═══ cx_projects_tracking Installer ═══"
echo ""

# --- Step 0: Check for CoCo CLI install directories ---
if [[ ! -d "$HOME/.snowflake" ]]; then
    echo "  ✗ ERROR: CoCo CLI install directories were not detected."
    echo "    Expected: $HOME/.snowflake"
    echo ""
    exit 1
fi

# --- Step 0.25: Fix CRLF line endings (WSL / Windows round-trip) ---
fix_crlf() {
    local f="$1"
    if grep -qP '\r$' "$f" 2>/dev/null; then
        if command -v dos2unix &>/dev/null; then
            dos2unix "$f" 2>/dev/null
        elif command -v sed &>/dev/null; then
            sed -i'' $'s/\r$//' "$f"
        fi
        return 0
    fi
    return 1
}
CRLF_FIXED=0
for f in "$SCRIPT_DIR"/cli/*.sh "$SCRIPT_DIR"/snowwork/*.sh "$SCRIPT_DIR"/diagnose-tracking.sh "$SCRIPT_DIR"/install.sh; do
    [[ -f "$f" ]] && fix_crlf "$f" && CRLF_FIXED=$((CRLF_FIXED + 1))
done
if [[ "$CRLF_FIXED" -gt 0 ]]; then
    echo "  ✓ Fixed CRLF line endings in $CRLF_FIXED file(s)"
else
    echo "  ✓ No CRLF line endings detected"
fi
echo ""

# --- Step 0.5: Validate connections.toml format ---
CONN_TOML="$HOME/.snowflake/connections.toml"
if [[ -f "$CONN_TOML" ]]; then
    HAS_PREFIX=$(grep -c '^\[connections\.' "$CONN_TOML" 2>/dev/null) || true
    HAS_PREFIX=${HAS_PREFIX:-0}
    HAS_BARE=$(grep -cE '^\[[A-Za-z0-9_-]+\]' "$CONN_TOML" 2>/dev/null) || true
    HAS_BARE=${HAS_BARE:-0}
    HAS_BARE=$((HAS_BARE - HAS_PREFIX))
    if [[ "$HAS_PREFIX" -gt 0 ]] && [[ "$HAS_BARE" -gt 0 ]]; then
        echo "  ⚠ WARNING: connections.toml has mixed section formats."
        echo "    Found $HAS_PREFIX sections with [connections.xxx] prefix"
        echo "    and $HAS_BARE sections with bare [xxx] format."
        echo ""
        echo "    The Snowflake CLI (snow) cannot parse mixed formats and will"
        echo "    fail with: 'String' object has no attribute 'items'"
        echo ""
        echo "    FIX: Use one consistent format. Recommended: bare [name] format."
        echo "    Example: rename [connections.snowhouse] to [snowhouse]"
        echo ""
        read -r -p "    Continue anyway? (y/N) " REPLY
        if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
            echo "    Fix connections.toml and re-run install.sh"
            exit 1
        fi
    elif [[ "$HAS_PREFIX" -gt 0 ]]; then
        echo "  ⚠ WARNING: connections.toml uses [connections.xxx] prefix format."
        echo "    The Snowflake CLI (snow) may not resolve connection names correctly."
        echo "    Recommended: rename sections to bare [name] format."
        echo "    Example: rename [connections.snowhouse] to [snowhouse]"
        echo ""
    fi
    # Permissions check — Snow CLI requires 0600
    CONN_PERMS=$(stat -f '%Lp' "$CONN_TOML" 2>/dev/null || stat -c '%a' "$CONN_TOML" 2>/dev/null)
    if [[ -n "$CONN_PERMS" ]] && [[ "$CONN_PERMS" != "600" ]]; then
        echo "  ⚠ WARNING: connections.toml permissions are $CONN_PERMS (must be 600)."
        echo "    Snow CLI will refuse to read it. Fix: chmod 600 $CONN_TOML"
    else
        echo "  ✓ connections.toml permissions: $CONN_PERMS"
    fi
elif [[ -f "$HOME/.snowflake/config.toml" ]]; then
    echo "  ⚠ No connections.toml found. Only config.toml exists."
    echo "    Snow CLI prefers connections.toml. Create it and add your connections there."
    echo "    Note: connections.toml uses [name] format (not [connections.name] like config.toml)."
fi
echo ""

# --- Step 0.75: Clean and recreate target folder ---
if [[ -d "$TARGET_DIR" ]]; then
    rm -rf "$TARGET_DIR"
    echo "  ✓ Removed stale $TARGET_DIR"
fi
mkdir -p "$TARGET_DIR"
echo "  ✓ Created $TARGET_DIR"

# --- Step 0.8: Check for Snowflake CLI (snow) ---
if command -v snow &>/dev/null; then
    SNOW_VER=$(snow --version 2>/dev/null | head -1)
    SNOW_PATH="$(command -v snow)"
    echo "  ✓ Snowflake CLI found: $SNOW_VER ($SNOW_PATH)"
else
    for CANDIDATE in \
        /opt/homebrew/bin/snow \
        /usr/local/bin/snow \
        "$HOME/.local/bin/snow" \
        "$HOME/Library/Python"/3.*/bin/snow \
        /Applications/SnowflakeCLI.app/Contents/MacOS/snow; do
        if [[ -x "$CANDIDATE" ]]; then
            SNOW_PATH="$CANDIDATE"
            SNOW_VER=$("$SNOW_PATH" --version 2>/dev/null | head -1)
            echo "  ✓ Snowflake CLI found (not on PATH): $SNOW_VER ($SNOW_PATH)"
            echo "    Consider adding $(dirname "$SNOW_PATH") to your PATH."
            break
        fi
    done
fi

if [[ -n "$SNOW_PATH" ]]; then
    SNOW_BIN_DIR="$(dirname "$SNOW_PATH")"
    echo "$SNOW_BIN_DIR" > "$TARGET_DIR/.snow_path"
    echo "  ✓ Saved Snowflake CLI path: $SNOW_BIN_DIR"
    # Version check: hooks require >= 3.16
    SNOW_VER_NUM=$(snow --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
    SNOW_MAJOR=$(echo "$SNOW_VER_NUM" | cut -d. -f1)
    SNOW_MINOR=$(echo "$SNOW_VER_NUM" | cut -d. -f2)
    if [[ -n "$SNOW_MAJOR" ]] && [[ -n "$SNOW_MINOR" ]]; then
        if [[ "$SNOW_MAJOR" -lt 3 ]] || { [[ "$SNOW_MAJOR" -eq 3 ]] && [[ "$SNOW_MINOR" -lt 16 ]]; }; then
            echo "  ⚠ WARNING: Snow CLI version $SNOW_VER_NUM detected. Hooks require >= 3.16."
            echo "    Update: brew upgrade snowflake-cli   OR   pip install --upgrade snowflake-cli"
            echo "    If old version persists after upgrade, remove stale binary:"
            echo "      rm -rf ~/Applications/SnowflakeCLI.app/ /Applications/SnowflakeCLI.app/"
            echo "    Then open a new terminal and run: hash -r && snow --version"
        else
            echo "  ✓ Snow CLI version $SNOW_VER_NUM (>= 3.16)"
        fi
    fi
fi

# --- Save python3 path for hooks ---
PYTHON3_PATH="$(command -v python3 2>/dev/null)"
if [[ -n "$PYTHON3_PATH" ]]; then
    PYTHON3_BIN_DIR="$(dirname "$PYTHON3_PATH")"
    echo "$PYTHON3_BIN_DIR" > "$TARGET_DIR/.python3_path"
    echo "  ✓ Saved python3 path: $PYTHON3_BIN_DIR"
else
    echo "  ⚠ python3 not found on PATH — hooks will fall back to command -v at runtime"
fi

if [[ -z "$SNOW_PATH" ]]; then
    echo "  ⚠ Snowflake CLI (snow) not found on PATH."
    OS_TYPE="$(uname -s)"
    case "$OS_TYPE" in
        Darwin)
            if command -v brew &>/dev/null; then
                echo "    → Installing via Homebrew..."
                brew tap snowflakedb/snowflake-cli 2>/dev/null
                brew install snowflake-cli
                if command -v snow &>/dev/null; then
                    echo "  ✓ Snowflake CLI installed successfully"
                else
                    echo "  ✗ Homebrew install completed but 'snow' not on PATH."
                    echo "    Try opening a new terminal or run: brew link snowflake-cli"
                fi
            else
                echo "    Homebrew not found. Trying pip..."
                if command -v pip3 &>/dev/null; then
                    pip3 install snowflake-cli
                    echo "  ✓ Snowflake CLI installed via pip"
                elif command -v pipx &>/dev/null; then
                    pipx install snowflake-cli
                    echo "  ✓ Snowflake CLI installed via pipx"
                else
                    echo "  ✗ No package manager found. Install manually:"
                    echo "    brew install snowflake-cli  OR  pip install snowflake-cli"
                fi
            fi
            ;;
        Linux)
            if command -v pipx &>/dev/null; then
                echo "    → Installing via pipx..."
                pipx install snowflake-cli
                echo "  ✓ Snowflake CLI installed via pipx"
            elif command -v pip3 &>/dev/null; then
                echo "    → Installing via pip3..."
                pip3 install snowflake-cli
                echo "  ✓ Snowflake CLI installed via pip3"
            elif command -v pip &>/dev/null; then
                echo "    → Installing via pip..."
                pip install snowflake-cli
                echo "  ✓ Snowflake CLI installed via pip"
            else
                echo "  ✗ No pip/pipx found. Install manually:"
                echo "    pip install snowflake-cli"
                echo "    Or download deb/rpm from: https://sfc-repo.snowflakecomputing.com/snowflake-cli/index.html"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "    Windows detected (Git Bash/MSYS). Trying pip..."
            if command -v pip &>/dev/null; then
                pip install snowflake-cli
                echo "  ✓ Snowflake CLI installed via pip"
            elif command -v pip3 &>/dev/null; then
                pip3 install snowflake-cli
                echo "  ✓ Snowflake CLI installed via pip3"
            else
                echo "  ✗ pip not found. Install manually:"
                echo "    pip install snowflake-cli"
                echo "    Or use the Windows installer from: https://sfc-repo.snowflakecomputing.com/snowflake-cli/index.html"
                echo "    Or run the PowerShell installer: install.ps1"
            fi
            ;;
        *)
            echo "  ✗ Unknown platform: $OS_TYPE. Install manually:"
            echo "    pip install snowflake-cli"
            ;;
    esac
fi
echo ""

# --- Step 2: Copy hook scripts ---
MISSING=0
for subdir in cli snowwork; do
    if [[ -d "$SCRIPT_DIR/$subdir" ]]; then
        mkdir -p "$TARGET_DIR/$subdir"
        cp "$SCRIPT_DIR/$subdir/"*.sh "$TARGET_DIR/$subdir/"
        echo "  ✓ Installed $subdir/ directory"
        chmod +x "$TARGET_DIR/$subdir/"*.sh
    else
        echo "  ✗ MISSING: $subdir/ directory not found in $SCRIPT_DIR"
        MISSING=1
    fi
done

if [[ "$MISSING" -eq 1 ]]; then
    echo ""
    echo "ERROR: Missing hook script directory(ies). Ensure cli/ and snowwork/ directories are in the same folder as install.sh."
    exit 1
fi

# --- Step 3: Update hooks.json (merge, don't overwrite) ---
python3 << 'PYEOF'
import json, os, sys

hooks_path = os.path.expanduser("~/.snowflake/cortex/hooks.json")
sa_dir = os.path.expanduser("~/.snowflake/cortex/hooks/cx_projects_tracking")

new_entries = {
    "SessionStart": {
        "hooks": [{"type": "command", "command": os.path.join(sa_dir, "cli", "session-tag-init.sh"), "enabled": True}]
    },
    "UserPromptSubmit": {
        "hooks": [{"type": "command", "command": os.path.join(sa_dir, "cli", "user-prompt-check.sh"), "enabled": True}]
    },
    "SessionEnd": {
        "hooks": [{"type": "command", "command": os.path.join(sa_dir, "cli", "session-end.sh"), "enabled": True}]
    }
}

if os.path.isfile(hooks_path):
    with open(hooks_path) as f:
        data = json.load(f)
else:
    data = {}

if "hooks" not in data or not isinstance(data["hooks"], dict):
    data["hooks"] = {}


skipped = 0
for hook_type, entry in new_entries.items():
    if hook_type not in data["hooks"]:
        data["hooks"][hook_type] = []
    entries = data["hooks"][hook_type]
    replaced = False
    for i, existing in enumerate(entries):
        for h in existing.get("hooks", []):
            if "cx_projects_tracking" in h.get("command", ""):
                if entries[i] == entry:
                    skipped += 1
                else:
                    entries[i] = entry
                replaced = True
                break
        if replaced:
            break
    if not replaced:
        entries.append(entry)

if skipped == len(new_entries):
    print("  ✓ hooks.json already up to date")
else:
    with open(hooks_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("  ✓ hooks.json updated")
PYEOF

# --- Step 3b: Update settings.json for SnowWork (merge, don't overwrite) ---
echo ""
echo "  Updating settings.json for SnowWork..."
python3 << 'SWEOF'
import json, os

settings_path = os.path.expanduser("~/.snowflake/cortex/settings.json")
base = os.path.expanduser("~/.snowflake/cortex/hooks/cx_projects_tracking")

sw_hooks = {
    "SessionStart": {
        "hooks": [{"type": "command", "command": f"{base}/snowwork/session-tag-init.sh", "enabled": True}]
    },
    "UserPromptSubmit": {
        "hooks": [{"type": "command", "command": f"{base}/snowwork/user-prompt-check.sh", "enabled": True}]
    },
    "SessionEnd": {
        "hooks": [{"type": "command", "command": f"{base}/snowwork/session-end.sh", "enabled": True}]
    }
}

if os.path.isfile(settings_path):
    with open(settings_path) as f:
        data = json.load(f)
else:
    data = {}

if "hooks" not in data or not isinstance(data["hooks"], dict):
    data["hooks"] = {}

skipped = 0
for hook_type, entry in sw_hooks.items():
    if hook_type not in data["hooks"]:
        data["hooks"][hook_type] = []
    entries = data["hooks"][hook_type]
    replaced = False
    for i, existing in enumerate(entries):
        for h in existing.get("hooks", []):
            if "cx_projects_tracking" in h.get("command", ""):
                if entries[i] == entry:
                    skipped += 1
                else:
                    entries[i] = entry
                replaced = True
                break
        if replaced:
            break
    if not replaced:
        entries.append(entry)

if skipped == len(sw_hooks):
    print("  ✓ settings.json already up to date")
else:
    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("  ✓ settings.json updated (SnowWork hooks registered)")
SWEOF

# --- Step 4: Install skills to global skills directory ---

SKILL_SRC="$SCRIPT_DIR/skills/sd-project-list-setup/SKILL.md"
SKILL_DST="$HOME/.snowflake/cortex/skills/sd-project-list-setup"
CONN_TOML="$HOME/.snowflake/connections.toml"
CONFIG_TOML="$HOME/.snowflake/config.toml"

HAS_SNOWHOUSE_CONN=0
HAS_SNOWHOUSE_CFG=0
grep -qi 'account\s*=\s*"[^"]*snowhouse[^"]*"' "$CONN_TOML" 2>/dev/null && HAS_SNOWHOUSE_CONN=1
grep -qi 'account\s*=\s*"[^"]*snowhouse[^"]*"' "$CONFIG_TOML" 2>/dev/null && HAS_SNOWHOUSE_CFG=1

if [[ "$HAS_SNOWHOUSE_CONN" -eq 1 ]] && [[ "$HAS_SNOWHOUSE_CFG" -eq 1 ]]; then
    echo ""
    echo "  ⚠ WARNING: Snowhouse connection found in BOTH config.toml and connections.toml."
    echo "    This can cause the hook to read the wrong account identifier."
    echo "    Remove the [connections.snowhouse] section from config.toml and keep"
    echo "    the entry in connections.toml (which should have the full account locator)."
fi

HAS_SNOWHOUSE=0
if [[ "$HAS_SNOWHOUSE_CONN" -eq 0 ]] && [[ "$HAS_SNOWHOUSE_CFG" -eq 1 ]]; then
    echo ""
    echo "  ⚠ WARNING: Snowhouse connection found in config.toml but NOT in connections.toml."
    echo "    The tagging hook uses 'snow sql --connection' which resolves from connections.toml."
    echo "    Tags will fail silently until the connection is added to connections.toml."
    echo "    Copy the Snowhouse [connections.*] section to $CONN_TOML"
fi

[[ "$HAS_SNOWHOUSE_CONN" -eq 1 ]] || [[ "$HAS_SNOWHOUSE_CFG" -eq 1 ]] && HAS_SNOWHOUSE=1

SKILL_SRC="$SCRIPT_DIR/skills/sd-verify-tracking/SKILL.md"
SKILL_DST="$HOME/.snowflake/cortex/skills/sd-verify-tracking"
if [[ -f "$SKILL_SRC" ]]; then
    mkdir -p "$SKILL_DST"
    cp "$SKILL_SRC" "$SKILL_DST/SKILL.md"
    echo "  ✓ Installed sd-verify-tracking skill to $SKILL_DST"
else
    echo "  ⚠ SKILL.md not found — verification skill not installed"
fi

SKILL_SRC="$SCRIPT_DIR/skills/sd-submit-info/SKILL.md"
SKILL_DST="$HOME/.snowflake/cortex/skills/sd-submit-info"
if [[ -f "$SKILL_SRC" ]]; then
    mkdir -p "$SKILL_DST"
    cp "$SKILL_SRC" "$SKILL_DST/SKILL.md"
    echo "  ✓ Installed sd-submit-info skill to $SKILL_DST"
else
    echo "  ⚠ SKILL.md not found at $SKILL_SRC — sd-submit-info skill not installed"
fi


SKILL_SRC="$SCRIPT_DIR/skills/sd-project-list-setup/SKILL.md"
SKILL_DST="$HOME/.snowflake/cortex/skills/sd-project-list-setup"
if [[ "$HAS_SNOWHOUSE" -eq 1 ]]; then
    if [[ -f "$SKILL_SRC" ]]; then
        mkdir -p "$SKILL_DST"
        cp "$SKILL_SRC" "$SKILL_DST/SKILL.md"
        echo "  ✓ Installed sd-project-list-setup skill to $SKILL_DST"
    else
        echo "  ⚠ SKILL.md not found at $SKILL_SRC — skill not installed"
    fi
else
    echo "  ⚠ No snowhouse connection found in $CONN_TOML or $CONFIG_TOML — sd-project-list-setup skill skipped"
fi


# --- Step 5: Live connection test (snow sql) ---
echo ""
echo "  Testing live connection with snow sql..."
TEST_CONN=""
if [[ -f "$CONN_TOML" ]]; then
    TEST_CONN=$(python3 -c "
import re
with open('$CONN_TOML') as f:
    content = f.read()
current_section = ''
for line in content.splitlines():
    m = re.match(r'^\s*\[([^]]+)\]', line)
    if m:
        current_section = m.group(1).strip()
        continue
    if current_section and re.search(r'account\s*=\s*"[^"]*snowhouse[^"]*"', line, re.IGNORECASE):
        name = current_section.split('.')[-1] if '.' in current_section else current_section
        print(name)
        break
" 2>/dev/null)
fi
if [[ -z "$TEST_CONN" ]] && [[ -f "$CONN_TOML" ]]; then
    TEST_CONN=$(grep -m1 'default_connection_name' "$CONN_TOML" 2>/dev/null | cut -d'"' -f2)
fi
if [[ -n "$TEST_CONN" ]] && [[ -n "$SNOW_PATH" ]]; then
    TEST_ERR=$(snow sql -q "SELECT 1;" --connection "$TEST_CONN" 2>&1 >/dev/null) && TEST_RC=0 || TEST_RC=$?
    if [[ $TEST_RC -eq 0 ]]; then
        echo "  ✓ snow sql --connection $TEST_CONN succeeded — tagging will work"
    else
        echo "  ✗ snow sql --connection $TEST_CONN FAILED (exit code $TEST_RC)"
        echo "    Error: $TEST_ERR"
        echo ""
        echo "    This means tags will fail at runtime. Common causes:"
        echo "    - Connection not in connections.toml (only in config.toml)"
        echo "    - Auth token expired (regenerate PAT or re-auth)"
        echo "    - Wrong permissions on connections.toml (need 600)"
        echo "    - Warehouse suspended or inaccessible"
    fi
elif [[ -z "$SNOW_PATH" ]]; then
    echo "  ⚠ Skipped — snow CLI not available"
elif [[ -z "$TEST_CONN" ]]; then
    echo "  ⚠ Skipped — no connection detected to test"
    echo "    Set default_connection_name in connections.toml or add a snowhouse connection"
fi
echo ""

# --- Step 6: Handle sd_projects.txt and final status ---
if [[ -f "$SCRIPT_DIR/sd_projects.txt" ]]; then
    cp "$SCRIPT_DIR/sd_projects.txt" "$TARGET_DIR/sd_projects.txt"
    ENTRY_COUNT=$(grep -cv '^\s*#\|^\s*$' "$TARGET_DIR/sd_projects.txt" 2>/dev/null) || true
    ENTRY_COUNT=${ENTRY_COUNT:-0}
    echo "  ✓ Copied sd_projects.txt ($ENTRY_COUNT entries)"
    echo ""
    echo "  Installation successful! Start a new cortex session to test."
    echo ""
elif [[ -f "$TARGET_DIR/sd_projects.txt" ]] || [[ "$HAS_SNOWHOUSE" -eq 1 ]]; then
    if [[ -f "$TARGET_DIR/sd_projects.txt" ]]; then
        echo "  ✓ sd_projects.txt already in target folder"
    fi
    echo ""
    echo "  Installation successful! Start a new cortex session to test."
    echo "  Tip: Run 'sd-project-list-setup' in your first session to generate sd_projects.txt"
    echo "  so future sessions load your project list instantly without querying Snowhouse."
    echo ""
else
    echo ""
    echo "  ⚠ WARNING: You have installed in a location with no detected connection"
    echo "  to Snowhouse and you do not have an sd_projects.txt file. You will not"
    echo "  have a project/milestone list to choose from until you create this file."
    echo ""
fi
