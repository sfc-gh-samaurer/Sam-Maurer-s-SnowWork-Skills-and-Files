# ═══════════════════════════════════════════════════════════════
# cx_projects_tracking — Full Installer (Windows PowerShell)
# ═══════════════════════════════════════════════════════════════
# PowerShell equivalent of install.sh.
# Creates hooks directory, copies scripts, merges hooks.json
# and settings.json, installs skills, tests connection.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SnowflakeDir = Join-Path $env:USERPROFILE ".snowflake"
$CortexDir = Join-Path $SnowflakeDir "cortex"
$TargetDir = Join-Path $CortexDir "hooks\cx_projects_tracking"
$HooksJson = Join-Path $CortexDir "hooks.json"
$SettingsJson = Join-Path $CortexDir "settings.json"
$ConnectionsToml = Join-Path $SnowflakeDir "connections.toml"
$ConfigToml = Join-Path $SnowflakeDir "config.toml"
$SkillsDir = Join-Path $CortexDir "skills"

function Pass($msg) { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "  ✗ $msg" -ForegroundColor Red }
function Warn($msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Info($msg) { Write-Host "  → $msg" -ForegroundColor Cyan }

Write-Host ""
Write-Host "═══ cx_projects_tracking Installer (Windows) ═══" -ForegroundColor White
Write-Host ""

# --- Step 0: Check for CoCo directories ---
if (-not (Test-Path $SnowflakeDir)) {
    Fail "CoCo install directories not detected."
    Info "Expected: $SnowflakeDir"
    exit 1
}
Pass "Snowflake directory found: $SnowflakeDir"

# --- Step 1: Check for Snowflake CLI (snow) ---
Write-Host ""
Write-Host "Step 1: Snowflake CLI" -ForegroundColor White
$snowCmd = Get-Command snow -ErrorAction SilentlyContinue
if ($snowCmd) {
    $snowPath = $snowCmd.Source
    $snowVer = & snow --version 2>&1 | Select-Object -First 1
    Pass "snow found: $snowVer ($snowPath)"
} else {
    Warn "Snowflake CLI (snow) not found on PATH."
    $pipxCmd = Get-Command pipx -ErrorAction SilentlyContinue
    $pip3Cmd = Get-Command pip3 -ErrorAction SilentlyContinue
    $pipCmd  = Get-Command pip  -ErrorAction SilentlyContinue
    if ($pipxCmd) {
        Info "Installing via pipx..."
        & pipx install snowflake-cli
    } elseif ($pip3Cmd) {
        Info "Installing via pip3..."
        & pip3 install snowflake-cli
    } elseif ($pipCmd) {
        Info "Installing via pip..."
        & pip install snowflake-cli
    } else {
        Fail "No pip/pipx found. Install Python from https://python.org then run: pip install snowflake-cli"
    }
    $snowCmd = Get-Command snow -ErrorAction SilentlyContinue
    if ($snowCmd) {
        $snowPath = $snowCmd.Source
        $snowVer = & snow --version 2>&1 | Select-Object -First 1
        Pass "Snowflake CLI installed: $snowVer ($snowPath)"
    } else {
        $snowPath = $null
        Warn "snow still not on PATH — restart terminal after install completes"
    }
}

# --- Step 2: Clean and create target directory ---
Write-Host ""
Write-Host "Step 2: Hook directory" -ForegroundColor White
if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
    Pass "Removed stale $TargetDir"
}
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
Pass "Created $TargetDir"

# --- Step 3: Save binary paths ---
if ($snowCmd) {
    $snowBinDir = Split-Path -Parent $snowCmd.Source
    Set-Content -Path (Join-Path $TargetDir ".snow_path") -Value $snowBinDir -NoNewline
    Pass "Saved snow path: $snowBinDir"
}
$pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $pythonCmd) { $pythonCmd = Get-Command python -ErrorAction SilentlyContinue }
if ($pythonCmd) {
    $pyBinDir = Split-Path -Parent $pythonCmd.Source
    Set-Content -Path (Join-Path $TargetDir ".python3_path") -Value $pyBinDir -NoNewline
    Pass "Saved python path: $pyBinDir"
} else {
    Warn "python3/python not found — hooks will attempt runtime detection"
}

# --- Step 4: Copy hook scripts ---
Write-Host ""
Write-Host "Step 4: Hook scripts" -ForegroundColor White
$missing = 0
foreach ($subdir in @("cli", "snowwork")) {
    $srcDir = Join-Path $ScriptDir $subdir
    if (Test-Path $srcDir) {
        $dstDir = Join-Path $TargetDir $subdir
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
        Copy-Item -Path (Join-Path $srcDir "*.sh") -Destination $dstDir -Force
        Pass "Installed $subdir/ directory"
    } else {
        Fail "MISSING: $subdir/ directory not found in $ScriptDir"
        $missing = 1
    }
}
if ($missing -eq 1) {
    Fail "Missing hook script directory(ies). Ensure cli/ and snowwork/ are present."
    exit 1
}

# --- Step 5: Fix CRLF in copied scripts (WSL compatibility) ---
Write-Host ""
Write-Host "Step 5: Line ending normalization" -ForegroundColor White
$fixedCount = 0
Get-ChildItem -Path $TargetDir -Recurse -Filter "*.sh" | ForEach-Object {
    $content = [System.IO.File]::ReadAllText($_.FullName)
    if ($content -match "`r`n") {
        $content = $content -replace "`r`n", "`n"
        [System.IO.File]::WriteAllText($_.FullName, $content)
        $fixedCount++
    }
}
if ($fixedCount -gt 0) {
    Pass "Fixed CRLF → LF in $fixedCount script(s)"
} else {
    Pass "No CRLF line endings detected"
}

# --- Step 6: Merge hooks.json (CLI hooks) ---
Write-Host ""
Write-Host "Step 6: hooks.json (CLI)" -ForegroundColor White

$pyExe = if ($pythonCmd) { $pythonCmd.Source } else { "python" }
$mergeScript = @"
import json, os, sys

hooks_path = r'$HooksJson'
sa_dir = r'$TargetDir'

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
    print("SKIP")
else:
    with open(hooks_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("OK")
"@

$result = $mergeScript | & $pyExe 2>&1
if ($result -match "SKIP") {
    Pass "hooks.json already up to date"
} elseif ($result -match "OK") {
    Pass "hooks.json updated"
} else {
    Fail "hooks.json merge failed: $result"
}

# --- Step 7: Merge settings.json (SnowWork hooks) ---
Write-Host ""
Write-Host "Step 7: settings.json (SnowWork)" -ForegroundColor White

$settingsScript = @"
import json, os, sys

settings_path = r'$SettingsJson'
sa_dir = r'$TargetDir'

sw_hooks = {
    "SessionStart": {
        "hooks": [{"type": "command", "command": os.path.join(sa_dir, "snowwork", "session-tag-init.sh"), "enabled": True}]
    },
    "UserPromptSubmit": {
        "hooks": [{"type": "command", "command": os.path.join(sa_dir, "snowwork", "user-prompt-check.sh"), "enabled": True}]
    },
    "SessionEnd": {
        "hooks": [{"type": "command", "command": os.path.join(sa_dir, "snowwork", "session-end.sh"), "enabled": True}]
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
    print("SKIP")
else:
    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("OK")
"@

$result = $settingsScript | & $pyExe 2>&1
if ($result -match "SKIP") {
    Pass "settings.json already up to date"
} elseif ($result -match "OK") {
    Pass "settings.json updated (SnowWork hooks registered)"
} else {
    Fail "settings.json merge failed: $result"
}

# --- Step 8: Install skills ---
Write-Host ""
Write-Host "Step 8: Skills" -ForegroundColor White

foreach ($skill in @("sd-submit-info", "sd-project-list-setup", "sd-verify-tracking")) {
    $skillSrc = Join-Path $ScriptDir "skills\$skill\SKILL.md"
    $skillDst = Join-Path $SkillsDir $skill
    if (Test-Path $skillSrc) {
        New-Item -ItemType Directory -Path $skillDst -Force | Out-Null
        Copy-Item -Path $skillSrc -Destination (Join-Path $skillDst "SKILL.md") -Force
        Pass "Installed $skill skill"
    } else {
        Warn "SKILL.md not found for $skill — skipped"
    }
}

# --- Step 9: Copy sd_projects.txt if available ---
Write-Host ""
Write-Host "Step 9: Project list" -ForegroundColor White

$sdProjectsSrc = Join-Path $ScriptDir "sd_projects.txt"
$sdProjectsDst = Join-Path $TargetDir "sd_projects.txt"
if (Test-Path $sdProjectsSrc) {
    Copy-Item -Path $sdProjectsSrc -Destination $sdProjectsDst -Force
    $entryCount = (Get-Content $sdProjectsDst | Where-Object { $_ -notmatch '^\s*#|^\s*$' }).Count
    Pass "Copied sd_projects.txt ($entryCount entries)"
} elseif (Test-Path $sdProjectsDst) {
    Pass "sd_projects.txt already in target folder"
} else {
    Warn "No sd_projects.txt found"
    Info "Run /sd-project-list-setup in your first session to generate it"
}

# --- Step 10: Connection test ---
Write-Host ""
Write-Host "Step 10: Connection test" -ForegroundColor White

if ($snowCmd -and (Test-Path $ConnectionsToml)) {
    $detectScript = @"
import re
with open(r'$ConnectionsToml') as f:
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
"@
    $testConn = ($detectScript | & $pyExe 2>&1).Trim()
    if ($testConn) {
        Info "Testing connection: $testConn"
        try {
            & snow sql -q "SELECT 1;" --connection $testConn 2>&1 | Out-Null
            Pass "snow sql --connection $testConn succeeded"
        } catch {
            Fail "snow sql --connection $testConn FAILED"
            Info "Fix the connection before troubleshooting hooks"
        }
    } else {
        Warn "No Snowhouse connection detected in connections.toml"
    }
} elseif (-not $snowCmd) {
    Warn "Skipped — snow CLI not available"
} else {
    Warn "Skipped — connections.toml not found"
}

# --- Summary ---
Write-Host ""
Write-Host "═══ Installation Complete ═══" -ForegroundColor White
Write-Host ""
Info "Start a new Cortex Code or SnowWork session to test."
Info "Run /sd-submit-info to tag your first session."
Info "Run /sd-project-list-setup once to cache your project list."
Write-Host ""
