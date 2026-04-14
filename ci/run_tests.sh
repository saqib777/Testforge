#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  TestForge CI Runner
#  Usage:  ./ci/run_tests.sh [--python] [--java] [--node] [--all]
#  Exits:  0 = all passed, 1 = failures
# ─────────────────────────────────────────────────────────────────

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS_DIR="$ROOT_DIR/reports"
LOG_FILE="$REPORTS_DIR/ci_$(date +%Y%m%d_%H%M%S).log"
PASS=0; FAIL=0

mkdir -p "$REPORTS_DIR"

# ── colours ──────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; AMBER='\033[0;33m'
BLUE='\033[0;34m'; RESET='\033[0m'; BOLD='\033[1m'

log()  { echo -e "  ${BLUE}●${RESET} $*" | tee -a "$LOG_FILE"; }
pass() { echo -e "  ${GREEN}✔${RESET} $*" | tee -a "$LOG_FILE"; ((PASS++)); }
fail() { echo -e "  ${RED}✘${RESET} $*" | tee -a "$LOG_FILE"; ((FAIL++)); }
warn() { echo -e "  ${AMBER}▲${RESET} $*" | tee -a "$LOG_FILE"; }

# ── dependency checks ─────────────────────────────────────────────
check_dep() {
  if command -v "$1" &>/dev/null; then
    log "Found $1 $(command -v "$1")"
    return 0
  else
    warn "$1 not found — skipping associated tests"
    return 1
  fi
}

# ── runners ───────────────────────────────────────────────────────
run_python() {
  log "Running Python tests..."
  if check_dep python; then
    if python -m pytest "$ROOT_DIR/tests/" -v \
         --tb=short 2>&1 | tee -a "$LOG_FILE"; then
      pass "Python / pytest — all tests passed"
    else
      fail "Python / pytest — tests failed"
    fi
  fi
}

run_java() {
  log "Running Java tests..."
  if check_dep mvn; then
    if mvn -f "$ROOT_DIR/java-module/pom.xml" test -q \
         2>&1 | tee -a "$LOG_FILE"; then
      pass "Java / JUnit 5 — all tests passed"
    else
      fail "Java / JUnit 5 — tests failed"
    fi
  fi
}

run_node() {
  log "Running Node.js tests..."
  if check_dep node && check_dep npm; then
    (cd "$ROOT_DIR/node-api" && npm install --silent)
    if (cd "$ROOT_DIR/node-api" && npm test 2>&1 | tee -a "$LOG_FILE"); then
      pass "Node.js / Jest — all tests passed"
    else
      fail "Node.js / Jest — tests failed"
    fi
  fi
}

# ── orchestrate ───────────────────────────────────────────────────
main() {
  echo ""
  echo -e "  ${BOLD}TestForge CI${RESET} — $(date)"
  echo "  ──────────────────────────────────"
  echo ""

  # Parse args; default = all
  RUN_PYTHON=false; RUN_JAVA=false; RUN_NODE=false

  if [[ $# -eq 0 ]] || [[ "$*" == *"--all"* ]]; then
    RUN_PYTHON=true; RUN_JAVA=true; RUN_NODE=true
  fi
  [[ "$*" == *"--python"* ]] && RUN_PYTHON=true
  [[ "$*" == *"--java"*   ]] && RUN_JAVA=true
  [[ "$*" == *"--node"*   ]] && RUN_NODE=true

  $RUN_PYTHON && run_python
  $RUN_JAVA   && run_java
  $RUN_NODE   && run_node

  echo ""
  echo "  ──────────────────────────────────"
  echo -e "  ${BOLD}Results:${RESET}  ${GREEN}$PASS passed${RESET}  /  ${RED}$FAIL failed${RESET}"
  echo "  Log: $LOG_FILE"
  echo ""

  if [[ $FAIL -gt 0 ]]; then
    echo -e "  ${RED}CI FAILED${RESET}"
    exit 1
  else
    echo -e "  ${GREEN}CI PASSED${RESET}"
    exit 0
  fi
}

main "$@"

