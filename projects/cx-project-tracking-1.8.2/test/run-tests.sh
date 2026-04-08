#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Run all Docker-based tests for cx-project-tracking
# ═══════════════════════════════════════════════════════════════
# Usage:
#   bash test/run-tests.sh           # run all
#   bash test/run-tests.sh bash      # bash installer only
#   bash test/run-tests.sh crlf      # CRLF tests only
#   bash test/run-tests.sh ps1       # PowerShell installer only
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

SUITE="${1:-all}"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0
RESULTS=()

run_test() {
    local name="$1"
    local service="$2"
    echo ""
    echo -e "${CYAN}═══ Running: $name ═══${NC}"
    echo ""
    if docker compose -f "$SCRIPT_DIR/docker-compose.yml" run --rm --build "$service" 2>&1; then
        echo -e "${GREEN}✓ $name PASSED${NC}"
        PASSED=$((PASSED + 1))
        RESULTS+=("✓ $name")
    else
        echo -e "${RED}✗ $name FAILED${NC}"
        FAILED=$((FAILED + 1))
        RESULTS+=("✗ $name")
    fi
}

case "$SUITE" in
    bash)
        run_test "Bash Installer (Linux)" "test-bash"
        ;;
    crlf)
        run_test "CRLF Detection & Fix" "test-crlf"
        ;;
    ps1|powershell)
        run_test "PowerShell Installer" "test-powershell"
        ;;
    all)
        run_test "Bash Installer (Linux)" "test-bash"
        run_test "CRLF Detection & Fix" "test-crlf"
        run_test "PowerShell Installer" "test-powershell"
        ;;
    *)
        echo "Usage: $0 [all|bash|crlf|ps1]"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════"
echo "  Test Results Summary"
echo "═══════════════════════════════════════════"
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo ""
echo "  PASSED: $PASSED   FAILED: $FAILED"
echo "═══════════════════════════════════════════"
echo ""

if [[ "$FAILED" -gt 0 ]]; then
    exit 1
fi
exit 0
