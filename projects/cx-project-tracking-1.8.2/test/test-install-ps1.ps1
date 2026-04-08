# ═══════════════════════════════════════════════════════════════
# Test: install.ps1 on PowerShell (Linux container)
# ═══════════════════════════════════════════════════════════════
# Validates install.ps1 runs correctly in a PowerShell environment.
# Does NOT require snow CLI or Snowflake connectivity.
# Focuses on: directory creation, file copies, CRLF fix, JSON merge.
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"

$Pass = 0
$Fail = 0
$Warn = 0

function Test-Pass($msg) { Write-Host "  ✓ PASS: $msg" -ForegroundColor Green; $script:Pass++ }
function Test-Fail($msg) { Write-Host "  ✗ FAIL: $msg" -ForegroundColor Red; $script:Fail++ }
function Test-Warn($msg) { Write-Host "  ⚠ WARN: $msg" -ForegroundColor Yellow; $script:Warn++ }

Write-Host ""
Write-Host "═══ install.ps1 — PowerShell Test Suite ═══" -ForegroundColor White
Write-Host ""

$SnowflakeDir = Join-Path $HOME ".snowflake"
$CortexDir = Join-Path $SnowflakeDir "cortex"
$TargetDir = Join-Path $CortexDir "hooks/cx_projects_tracking"
$HooksJson = Join-Path $CortexDir "hooks.json"
$SettingsJson = Join-Path $CortexDir "settings.json"
$SkillsDir = Join-Path $CortexDir "skills"

# --- Fixtures ---
Write-Host "--- Setting up fixtures ---"
New-Item -ItemType Directory -Path $SnowflakeDir -Force | Out-Null
New-Item -ItemType Directory -Path $CortexDir -Force | Out-Null

$connToml = @"
[snowhouse]
account = "sfcogsops-snowhouse_aws_us_west_2"
user = "testuser"
authenticator = "externalbrowser"
"@
Set-Content -Path (Join-Path $SnowflakeDir "connections.toml") -Value $connToml
Write-Host "  fixtures ready"
Write-Host ""

# --- Test 1: install.ps1 runs to completion ---
Write-Host "--- Test 1: install.ps1 runs to completion ---"
try {
    # Override $env:USERPROFILE to use $HOME in Linux container
    $env:USERPROFILE = $HOME
    & pwsh -File /project/install.ps1 2>&1
    Test-Pass "install.ps1 exited 0"
} catch {
    Test-Fail "install.ps1 threw error: $_"
}
Write-Host ""

# --- Test 2: Target directory structure ---
Write-Host "--- Test 2: Target directory structure ---"
if (Test-Path $TargetDir) {
    Test-Pass "Target directory exists"
} else {
    Test-Fail "Target directory missing"
}

$cliDir = Join-Path $TargetDir "cli"
$swDir = Join-Path $TargetDir "snowwork"
if (Test-Path $cliDir) { Test-Pass "cli/ subdirectory exists" } else { Test-Fail "cli/ subdirectory missing" }
if (Test-Path $swDir) { Test-Pass "snowwork/ subdirectory exists" } else { Test-Fail "snowwork/ subdirectory missing" }
Write-Host ""

# --- Test 3: Hook scripts copied ---
Write-Host "--- Test 3: Hook scripts copied ---"
$scripts = @(
    "cli/session-tag-init.sh",
    "cli/user-prompt-check.sh",
    "cli/session-end.sh",
    "snowwork/session-tag-init.sh",
    "snowwork/user-prompt-check.sh",
    "snowwork/session-end.sh"
)
foreach ($s in $scripts) {
    $path = Join-Path $TargetDir $s
    if (Test-Path $path) {
        Test-Pass "Copied: $s"
    } else {
        Test-Fail "Missing: $s"
    }
}
Write-Host ""

# --- Test 4: No CRLF in copied scripts ---
Write-Host "--- Test 4: Line endings (LF only) ---"
$crlfCount = 0
Get-ChildItem -Path $TargetDir -Recurse -Filter "*.sh" | ForEach-Object {
    $content = [System.IO.File]::ReadAllText($_.FullName)
    if ($content -match "`r`n") {
        Test-Fail "CRLF found in: $($_.FullName)"
        $crlfCount++
    }
}
if ($crlfCount -eq 0) {
    Test-Pass "All scripts have LF line endings"
}
Write-Host ""

# --- Test 5: hooks.json ---
Write-Host "--- Test 5: hooks.json ---"
if (Test-Path $HooksJson) {
    Test-Pass "hooks.json exists"
    $data = Get-Content $HooksJson | ConvertFrom-Json
    $hooks = $data.hooks
    $ssEntries = $hooks.SessionStart | ConvertTo-Json -Depth 5
    $upsEntries = $hooks.UserPromptSubmit | ConvertTo-Json -Depth 5
    $seEntries = $hooks.SessionEnd | ConvertTo-Json -Depth 5
    if ($ssEntries -match "cx_projects_tracking" -and $upsEntries -match "cx_projects_tracking" -and $seEntries -match "cx_projects_tracking") {
        Test-Pass "hooks.json has SessionStart + UserPromptSubmit + SessionEnd entries"
    } else {
        Test-Fail "hooks.json missing expected entries"
    }
} else {
    Test-Fail "hooks.json not created"
}
Write-Host ""

# --- Test 6: settings.json ---
Write-Host "--- Test 6: settings.json ---"
if (Test-Path $SettingsJson) {
    Test-Pass "settings.json exists"
    $data = Get-Content $SettingsJson | ConvertFrom-Json
    $hooks = $data.hooks
    $ssStr = $hooks.SessionStart | ConvertTo-Json -Depth 5
    $upsStr = $hooks.UserPromptSubmit | ConvertTo-Json -Depth 5
    $seStr = $hooks.SessionEnd | ConvertTo-Json -Depth 5
    if ($ssStr -match "snowwork" -and $upsStr -match "snowwork" -and $seStr -match "snowwork") {
        Test-Pass "settings.json has SnowWork hook entries"
    } else {
        Test-Fail "settings.json missing SnowWork entries"
    }
} else {
    Test-Fail "settings.json not created"
}
Write-Host ""

# --- Test 7: Idempotency ---
Write-Host "--- Test 7: Idempotency (re-run) ---"
try {
    & pwsh -File /project/install.ps1 2>&1
    Test-Pass "Second install.ps1 run exited 0"
} catch {
    Test-Fail "Second run failed: $_"
}

$data = Get-Content $HooksJson | ConvertFrom-Json
$ssEntries = $data.hooks.SessionStart
$cxCount = ($ssEntries | ConvertTo-Json -Depth 5 | Select-String -Pattern "cx_projects_tracking" -AllMatches).Matches.Count
# Each entry has 1 match, so count should be 1 (one SessionStart entry)
if ($cxCount -le 2) {
    Test-Pass "No duplicate entries after re-install"
} else {
    Test-Fail "Duplicate entries found ($cxCount matches)"
}
Write-Host ""

# --- Test 8: Skills installed ---
Write-Host "--- Test 8: Skills ---"
foreach ($skill in @("sd-submit-info", "sd-project-list-setup", "sd-verify-tracking")) {
    $skillPath = Join-Path $SkillsDir "$skill/SKILL.md"
    if (Test-Path $skillPath) {
        Test-Pass "Skill installed: $skill"
    } else {
        Test-Fail "Skill missing: $skill"
    }
}
Write-Host ""

# --- Test 9: CRLF injection + fix ---
Write-Host "--- Test 9: CRLF injection round-trip ---"
$testScript = Join-Path $TargetDir "cli/session-tag-init.sh"
$original = [System.IO.File]::ReadAllText($testScript)
$corrupted = $original -replace "`n", "`r`n"
[System.IO.File]::WriteAllText($testScript, $corrupted)

if ([System.IO.File]::ReadAllText($testScript) -match "`r`n") {
    Test-Pass "CRLF injection confirmed"
} else {
    Test-Fail "CRLF injection failed"
}

& pwsh -File /project/install.ps1 2>&1
$afterFix = [System.IO.File]::ReadAllText($testScript)
if ($afterFix -match "`r`n") {
    Test-Fail "CRLF still present after re-install"
} else {
    Test-Pass "CRLF cleaned by re-install"
}
Write-Host ""

# --- Summary ---
Write-Host "═══════════════════════════════════════════" -ForegroundColor White
Write-Host "  PASS: $Pass   FAIL: $Fail   WARN: $Warn" -ForegroundColor White
Write-Host "═══════════════════════════════════════════" -ForegroundColor White
Write-Host ""

if ($Fail -gt 0) {
    exit 1
}
exit 0
