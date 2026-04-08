# ═══════════════════════════════════════════════════════════════
# cx-project-tracking — Diagnostic Script (Windows PowerShell)
# ═══════════════════════════════════════════════════════════════
# PowerShell equivalent of diagnose-tracking.sh (checklist only).
# Validates installation, connections, hooks, and scripts.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File diagnose-tracking.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"

$HooksDir = Join-Path $env:USERPROFILE ".snowflake\cortex\hooks\cx_projects_tracking"
$ConnectionsToml = Join-Path $env:USERPROFILE ".snowflake\connections.toml"
$ConfigToml = Join-Path $env:USERPROFILE ".snowflake\config.toml"
$HooksJson = Join-Path $env:USERPROFILE ".snowflake\cortex\hooks.json"
$SettingsJson = Join-Path $env:USERPROFILE ".snowflake\cortex\settings.json"
$SnowPathFile = Join-Path $HooksDir ".snow_path"
$SdProjects = Join-Path $HooksDir "sd_projects.txt"
$ExpectedVersion = "1.8.2"

$script:PassCount = 0
$script:FailCount = 0
$script:WarnCount = 0

function Pass($msg)   { $script:PassCount++; Write-Host "  ✓ $msg" -ForegroundColor Green }
function Fail($msg)   { $script:FailCount++; Write-Host "  ✗ $msg" -ForegroundColor Red }
function Warn($msg)   { $script:WarnCount++; Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Info($msg)   { Write-Host "  → $msg" -ForegroundColor Cyan }
function Header($msg) { Write-Host ""; Write-Host "$msg" -ForegroundColor White }

$pyExe = $null
$pyCmds = @("python3", "python")
foreach ($p in $pyCmds) {
    $c = Get-Command $p -ErrorAction SilentlyContinue
    if ($c) { $pyExe = $c.Source; break }
}

Write-Host ""
Write-Host "═══ cx-project-tracking Diagnostic Checklist (Windows) ═══" -ForegroundColor White

# ── Check 1: Snowflake CLI ──
Header "Check 1: Snowflake CLI (snow)"
$snowCmd = Get-Command snow -ErrorAction SilentlyContinue
if ($snowCmd) {
    Pass "snow found at: $($snowCmd.Source)"
    $snowVer = & snow --version 2>&1 | Select-Object -First 1
    if ($snowVer -match "Snowflake CLI") {
        Pass "Version: $snowVer"
    } elseif ($snowVer) {
        Warn "Version string unexpected: $snowVer"
    } else {
        Fail "snow --version returned nothing"
    }
} else {
    Fail "snow not found in PATH"
    Info "Install: pip install snowflake-cli"
}

# ── Check 2: .snow_path ──
Header "Check 2: .snow_path (hook PATH resolution)"
if (Test-Path $SnowPathFile) {
    $savedPath = (Get-Content $SnowPathFile).Trim()
    $snowExe = Join-Path $savedPath "snow"
    $snowExeWin = Join-Path $savedPath "snow.exe"
    if ((Test-Path $snowExe) -or (Test-Path $snowExeWin)) {
        Pass ".snow_path → $savedPath (valid)"
    } elseif (Test-Path $savedPath) {
        Fail ".snow_path → $savedPath (directory exists but no snow binary)"
        Info "Re-run install.ps1 to re-detect"
    } else {
        Fail ".snow_path → $savedPath (directory does not exist)"
    }
} else {
    if ($snowCmd) {
        Warn ".snow_path not found — hooks rely on system PATH"
    } else {
        Fail ".snow_path not found and snow not in PATH — hooks will fail"
    }
}

# ── Check 3: connections.toml ──
Header "Check 3: connections.toml"
$detectedConn = $null
$detectedWh = $null
$detectedAuth = $null

if (Test-Path $ConnectionsToml) {
    Pass "File exists"

    if ($pyExe) {
        $detectScript = @"
import re
with open(r'$ConnectionsToml') as f:
    content = f.read()
current_section = ''
results = {}
for line in content.splitlines():
    m = re.match(r'^\s*\[([^]]+)\]', line)
    if m:
        current_section = m.group(1).strip()
        continue
    if current_section and re.search(r'account\s*=\s*"[^"]*snowhouse[^"]*"', line, re.IGNORECASE):
        name = current_section.split('.')[-1] if '.' in current_section else current_section
        results['conn'] = name

if 'conn' not in results:
    print('conn=')
else:
    conn = results['conn']
    print(f'conn={conn}')
    in_section = False
    for line in content.splitlines():
        m = re.match(r'^\s*\[([^]]+)\]', line)
        if m:
            sec = m.group(1).strip()
            bare = sec.split('.')[-1] if '.' in sec else sec
            in_section = (bare == conn or sec == conn)
            continue
        if in_section:
            for field in ['warehouse', 'role', 'authenticator']:
                fm = re.match(rf'^{field}\s*=\s*"([^"]*)"', line)
                if fm:
                    print(f'{field}={fm.group(1)}')
"@
        $lines = ($detectScript | & $pyExe 2>&1) -split "`n"
        $fields = @{}
        foreach ($line in $lines) {
            if ($line -match '^(\w+)=(.*)$') {
                $fields[$Matches[1]] = $Matches[2].Trim()
            }
        }

        if ($fields['conn']) {
            $detectedConn = $fields['conn']
            Pass "Snowhouse connection found: [$detectedConn]"

            if ($fields['warehouse']) {
                $detectedWh = $fields['warehouse']
                Pass "warehouse = $detectedWh"
            } else {
                Fail "warehouse not set — #1 cause of 'No active warehouse' errors"
                Info "Add: warehouse = `"XSMALL`""
            }

            if ($fields['role'] -eq "TECHNICAL_ACCOUNT_MANAGER") {
                Pass "role = TECHNICAL_ACCOUNT_MANAGER"
            } elseif ($fields['role']) {
                Warn "role = $($fields['role']) (should be TECHNICAL_ACCOUNT_MANAGER)"
            } else {
                Fail "role not set"
            }

            if ($fields['authenticator']) {
                $detectedAuth = $fields['authenticator']
                if ($detectedAuth -ieq "externalbrowser") {
                    Pass "authenticator = externalbrowser"
                } else {
                    Warn "authenticator = $detectedAuth (externalbrowser recommended)"
                }
            } else {
                Warn "authenticator not set (defaults to snowflake)"
            }
        } else {
            Fail "No Snowhouse connection found"
            Info "Add a connection with: account = `"SFCOGSOPS-SNOWHOUSE_AWS_US_WEST_2`""
        }
    } else {
        Warn "python not available — cannot parse connections.toml details"
    }
} else {
    Fail "File not found: $ConnectionsToml"
    Info "Create it or run install.ps1"
}

# ── Check 4: hooks.json ──
Header "Check 4: hooks.json"
if (Test-Path $HooksJson) {
    Pass "File exists"
    if ($pyExe) {
        $hookCheckScript = @"
import json
with open(r'$HooksJson') as f:
    data = json.load(f)
hooks = data.get('hooks', data) if isinstance(data, dict) else data
ss = ups = se = False
if isinstance(hooks, dict):
    for k, v in hooks.items():
        entries = v if isinstance(v, list) else [v]
        for e in entries:
            for h in (e.get('hooks', []) if isinstance(e, dict) else []):
                cmd = h.get('command', '')
                if 'cx_projects_tracking' in cmd:
                    if 'SessionStart' in k: ss = True
                    if 'UserPromptSubmit' in k: ups = True
                    if 'SessionEnd' in k: se = True
print(f'ss={"found" if ss else "missing"}')
print(f'ups={"found" if ups else "missing"}')
print(f'se={"found" if se else "missing"}')
"@
        $result = ($hookCheckScript | & $pyExe 2>&1) -join "`n"
        if ($result -match 'ss=found') {
            Pass "SessionStart hook registered"
        } else {
            Fail "SessionStart hook NOT registered"
        }
        if ($result -match 'ups=found') {
            Pass "UserPromptSubmit hook registered"
        } else {
            Fail "UserPromptSubmit hook NOT registered"
        }
        if ($result -match 'se=found') {
            Pass "SessionEnd hook registered"
        } else {
            Warn "SessionEnd hook NOT registered (v1.8.2+ feature)"
        }
    }
} else {
    Fail "File not found: $HooksJson"
    Info "Re-run install.ps1"
}

# ── Check 5: settings.json (SnowWork) ──
Header "Check 5: settings.json (SnowWork)"
if (Test-Path $SettingsJson) {
    Pass "File exists"
    if ($pyExe) {
        $swCheckScript = @"
import json
with open(r'$SettingsJson') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
ss = ups = se = False
if isinstance(hooks, dict):
    for k, v in hooks.items():
        entries = v if isinstance(v, list) else [v]
        for e in entries:
            for h in (e.get('hooks', []) if isinstance(e, dict) else []):
                cmd = h.get('command', '')
                if 'cx_projects_tracking' in cmd and 'snowwork' in cmd:
                    if 'SessionStart' in k: ss = True
                    if 'UserPromptSubmit' in k: ups = True
                    if 'SessionEnd' in k: se = True
print(f'ss={"found" if ss else "missing"}')
print(f'ups={"found" if ups else "missing"}')
print(f'se={"found" if se else "missing"}')
"@
        $result = ($swCheckScript | & $pyExe 2>&1) -join "`n"
        if ($result -match 'ss=found') {
            Pass "SnowWork SessionStart hook registered"
        } else {
            Fail "SnowWork SessionStart hook NOT registered"
        }
        if ($result -match 'ups=found') {
            Pass "SnowWork UserPromptSubmit hook registered"
        } else {
            Fail "SnowWork UserPromptSubmit hook NOT registered"
        }
        if ($result -match 'se=found') {
            Pass "SnowWork SessionEnd hook registered"
        } else {
            Warn "SnowWork SessionEnd hook NOT registered (v1.8.2+ feature)"
        }
    }
} else {
    Warn "settings.json not found (SnowWork hooks may not be registered)"
}

# ── Check 6: Hook scripts ──
Header "Check 6: Hook scripts"
foreach ($script in @("cli\session-tag-init.sh", "cli\user-prompt-check.sh", "cli\session-end.sh", "snowwork\session-tag-init.sh", "snowwork\user-prompt-check.sh", "snowwork\session-end.sh")) {
    $fullPath = Join-Path $HooksDir $script
    if (Test-Path $fullPath) {
        Pass "$script exists"
        $content = Get-Content $fullPath -Raw -ErrorAction SilentlyContinue
        if ($content -match "`r`n") {
            Fail "$script has CRLF line endings — will break in WSL/bash"
            Info "Fix: re-run install.ps1 (it normalizes line endings)"
        }
    } else {
        Fail "$script NOT FOUND"
    }
}

$initScript = Join-Path $HooksDir "cli\session-tag-init.sh"
if (Test-Path $initScript) {
    $verMatch = (Get-Content $initScript -Raw) | Select-String -Pattern "Build v(\d+\.\d+\.\d+)"
    if ($verMatch) {
        $installedVer = $verMatch.Matches[0].Groups[1].Value
        if ($installedVer -eq $ExpectedVersion) {
            Pass "Installed version: v$installedVer (current)"
        } else {
            Warn "Installed version: v$installedVer (expected v$ExpectedVersion)"
        }
    }
}

foreach ($variant in @("cli", "snowwork")) {
    $upcScript = Join-Path $HooksDir "$variant\user-prompt-check.sh"
    if (Test-Path $upcScript) {
        $upcContent = Get-Content $upcScript -Raw -ErrorAction SilentlyContinue
        if ($upcContent -match "systemMessage") {
            Pass "$variant/user-prompt-check.sh uses JSON systemMessage output (v1.8.2+)"
        } else {
            Warn "$variant/user-prompt-check.sh missing systemMessage — may be outdated"
            Info "Re-run install.ps1 from the latest release to update"
        }
    }
}

# ── Check 7: Connection test ──
Header "Check 7: Connection test"
if ($snowCmd -and $detectedConn) {
    Info "Running: snow connection test -c $detectedConn"
    try {
        $output = & snow connection test -c $detectedConn 2>&1
        if ($LASTEXITCODE -eq 0) {
            Pass "snow connection test PASSED"
        } else {
            Fail "snow connection test FAILED (exit code $LASTEXITCODE)"
            Info ($output | Out-String).Trim()
        }
    } catch {
        Fail "snow connection test threw an exception"
        Info $_.Exception.Message
    }
} elseif (-not $snowCmd) {
    Fail "Cannot test — snow CLI not found"
} else {
    Fail "Cannot test — no Snowhouse connection detected"
}

# ── Check 8: sd_projects.txt ──
Header "Check 8: sd_projects.txt"
if (Test-Path $SdProjects) {
    $lineCount = (Get-Content $SdProjects | Where-Object { $_ -notmatch '^\s*#|^\s*$' }).Count
    if ($lineCount -gt 0) {
        Pass "sd_projects.txt exists with $lineCount entries"
    } else {
        Warn "sd_projects.txt exists but is empty"
    }
} else {
    Warn "sd_projects.txt not found — sessions will query Snowhouse live"
    Info "Run /sd-project-list-setup in a session to generate it"
}

# ── Summary ──
Write-Host ""
Write-Host "═══ Summary ═══" -ForegroundColor White
Write-Host "  ✓ $($script:PassCount) passed    ✗ $($script:FailCount) failed    ⚠ $($script:WarnCount) warnings"

if ($script:FailCount -eq 0) {
    Write-Host ""
    Write-Host "  All critical checks passed." -ForegroundColor Green
    if ($script:WarnCount -gt 0) {
        Write-Host "  Review warnings above." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "  $($script:FailCount) check(s) failed. Fix items marked with ✗ above." -ForegroundColor Red
}
Write-Host ""
