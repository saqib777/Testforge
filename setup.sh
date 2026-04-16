#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  TestForge setup script
#  Checks all dependencies, installs packages, verifies the stack.
#  Usage: chmod +x setup.sh && ./setup.sh
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; AMBER='\033[0;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "  ${GREEN}✔${RESET}  $*"; }
fail() { echo -e "  ${RED}✘${RESET}  $*"; ERRORS=$((ERRORS+1)); }
info() { echo -e "  ${BLUE}●${RESET}  $*"; }
warn() { echo -e "  ${AMBER}▲${RESET}  $*"; }

ERRORS=0
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "  ${BOLD}TestForge Setup${RESET}"
echo "  ─────────────────────────────────"
echo ""

# ── 1. Check Python ───────────────────────────────────────────────
info "Checking Python..."
if command -v python3 &>/dev/null; then
  PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  MAJOR=$(echo "$PY_VER" | cut -d. -f1)
  MINOR=$(echo "$PY_VER" | cut -d. -f2)
  if [[ $MAJOR -ge 3 && $MINOR -ge 11 ]]; then
    ok "Python $PY_VER found"
  else
    warn "Python $PY_VER found — 3.11+ recommended"
  fi
  PYTHON=python3
elif command -v python &>/dev/null; then
  ok "Python found"
  PYTHON=python
else
  fail "Python not found — install from https://python.org"
fi

# ── 2. Check Java ─────────────────────────────────────────────────
info "Checking Java..."
if command -v java &>/dev/null; then
  JAVA_VER=$(java -version 2>&1 | head -1 | awk -F '"' '{print $2}')
  ok "Java $JAVA_VER found"
else
  fail "Java not found — install JDK 17+ from https://adoptium.net"
fi

# ── 3. Check Maven ────────────────────────────────────────────────
info "Checking Maven..."
if command -v mvn &>/dev/null; then
  MVN_VER=$(mvn -version 2>&1 | head -1 | awk '{print $3}')
  ok "Maven $MVN_VER found"
else
  fail "Maven not found — install from https://maven.apache.org"
fi

# ── 4. Check Node.js ──────────────────────────────────────────────
info "Checking Node.js..."
if command -v node &>/dev/null; then
  NODE_VER=$(node --version)
  ok "Node.js $NODE_VER found"
else
  fail "Node.js not found — install from https://nodejs.org"
fi

# ── 5. Check npm ──────────────────────────────────────────────────
info "Checking npm..."
if command -v npm &>/dev/null; then
  NPM_VER=$(npm --version)
  ok "npm $NPM_VER found"
else
  fail "npm not found (usually bundled with Node.js)"
fi

echo ""

# ── bail early if hard deps missing ──────────────────────────────
if [[ $ERRORS -gt 0 ]]; then
  echo -e "  ${RED}${BOLD}$ERRORS dependency check(s) failed.${RESET}"
  echo "  Please install the missing tools and re-run setup.sh"
  echo ""
  exit 1
fi

# ── 6. Install Python packages ────────────────────────────────────
info "Installing Python packages..."
if $PYTHON -m pip install -r "$ROOT/requirements.txt" -q; then
  ok "Python packages installed (pytest, pyyaml, ...)"
else
  fail "pip install failed"
fi

# ── 7. Install Node packages ──────────────────────────────────────
info "Installing Node packages..."
if (cd "$ROOT/node-api" && npm install --silent); then
  ok "Node packages installed (express, jest, supertest)"
else
  fail "npm install failed"
fi

# ── 8. Create reports dir ─────────────────────────────────────────
mkdir -p "$ROOT/reports"
ok "reports/ directory ready"

# ── 9. Make scripts executable ───────────────────────────────────
chmod +x "$ROOT/ci/run_tests.sh"
ok "ci/run_tests.sh is executable"

echo ""
echo "  ─────────────────────────────────"
echo -e "  ${GREEN}${BOLD}Setup complete!${RESET}"
echo ""
echo "  Quick start:"
echo -e "  ${BLUE}1.${RESET} Run all tests:     ${BOLD}python orchestrator/runner.py --all${RESET}"
echo -e "  ${BLUE}2.${RESET} Start dashboard:   ${BOLD}node node-api/server.js${RESET}"
echo -e "  ${BLUE}3.${RESET} Open browser:      ${BOLD}http://localhost:3000${RESET}"
echo -e "  ${BLUE}4.${RESET} Run CI locally:    ${BOLD}./ci/run_tests.sh --all${RESET}"
echo ""

