"""
TestForge Orchestrator
Python test runner that coordinates all language modules,
collects results, and generates reports.
"""

import subprocess
import json
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

RESULTS_DIR = Path(__file__).parent.parent / "reports"
CONFIG_DIR  = Path(__file__).parent.parent / "config"


# ─────────────────────────── helpers ────────────────────────────

def log(level: str, msg: str):
    icons = {"INFO": "●", "PASS": "✔", "FAIL": "✘", "WARN": "▲"}
    colors = {"INFO": "\033[94m", "PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m"}
    reset = "\033[0m"
    ts = datetime.now().strftime("%H:%M:%S")
    icon = icons.get(level, "●")
    color = colors.get(level, "")
    print(f"  {color}{icon} [{ts}] {msg}{reset}")


def load_suite(suite_name: str) -> dict:
    path = CONFIG_DIR / f"{suite_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Suite not found: {path}")
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        # fallback: minimal parser for simple YAML
        with open(path) as f:
            content = f.read()
        log("WARN", "PyYAML not installed — using fallback parser")
        return {"name": suite_name, "raw": content}


# ─────────────────────────── runners ────────────────────────────

def run_python_tests(suite: dict) -> dict:
    log("INFO", "Running Python tests (pytest)...")
    start = time.time()
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short",
         "--json-report", "--json-report-file=reports/pytest_results.json"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    duration = round(time.time() - start, 2)
    passed = result.returncode == 0
    log("PASS" if passed else "FAIL", f"Python tests done in {duration}s")
    return {
        "language": "Python",
        "tool": "pytest",
        "passed": passed,
        "duration": duration,
        "stdout": result.stdout[-2000:],
        "returncode": result.returncode,
    }


def run_java_tests() -> dict:
    log("INFO", "Running Java tests (Maven + JUnit)...")
    java_dir = Path(__file__).parent.parent / "java-module"
    start = time.time()
    result = subprocess.run(
        ["mvn", "test", "-q"],
        capture_output=True, text=True, cwd=java_dir
    )
    duration = round(time.time() - start, 2)
    passed = result.returncode == 0
    log("PASS" if passed else "FAIL", f"Java tests done in {duration}s")
    return {
        "language": "Java",
        "tool": "JUnit 5 / Maven",
        "passed": passed,
        "duration": duration,
        "stdout": result.stdout[-2000:],
        "returncode": result.returncode,
    }


def run_node_tests() -> dict:
    log("INFO", "Running Node.js tests (Jest)...")
    node_dir = Path(__file__).parent.parent / "node-api"
    start = time.time()
    result = subprocess.run(
        ["npm", "test", "--", "--json"],
        capture_output=True, text=True, cwd=node_dir
    )
    duration = round(time.time() - start, 2)
    passed = result.returncode == 0
    log("PASS" if passed else "FAIL", f"Node.js tests done in {duration}s")
    return {
        "language": "JavaScript",
        "tool": "Jest",
        "passed": passed,
        "duration": duration,
        "stdout": result.stdout[-2000:],
        "returncode": result.returncode,
    }


# ─────────────────────────── aggregation ────────────────────────

def aggregate_results(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    total_duration = round(sum(r["duration"] for r in results), 2)

    return {
        "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "duration_seconds": total_duration,
            "success_rate": round((passed / total) * 100, 1) if total else 0,
        },
        "results": results,
    }


def save_report(report: dict) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"run_{report['run_id']}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    # also overwrite latest.json for the dashboard
    latest = RESULTS_DIR / "latest.json"
    with open(latest, "w") as f:
        json.dump(report, f, indent=2)
    return path


def print_summary(report: dict):
    s = report["summary"]
    print()
    print("  ╔══════════════════════════════════╗")
    print(f"  ║  TestForge run {report['run_id']}  ║")
    print("  ╠══════════════════════════════════╣")
    print(f"  ║  Total:    {s['total']} suites             ║")
    print(f"  ║  Passed:   {s['passed']} ({'✔' * s['passed']})                ║")
    print(f"  ║  Failed:   {s['failed']} ({'✘' * s['failed']})                ║")
    print(f"  ║  Duration: {s['duration_seconds']}s              ║")
    print(f"  ║  Score:    {s['success_rate']}%              ║")
    print("  ╚══════════════════════════════════╝")
    print()


# ─────────────────────────── CLI ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TestForge — polyglot test orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--suite",  default="default", help="Test suite name (from config/*.yaml)")
    parser.add_argument("--python", action="store_true", help="Run Python tests only")
    parser.add_argument("--java",   action="store_true", help="Run Java tests only")
    parser.add_argument("--node",   action="store_true", help="Run Node.js tests only")
    parser.add_argument("--all",    action="store_true", help="Run all language modules")
    args = parser.parse_args()

    run_all = args.all or not any([args.python, args.java, args.node])

    print()
    log("INFO", f"TestForge starting — suite: {args.suite}")
    print()

    results = []
    if run_all or args.python:
        results.append(run_python_tests({}))
    if run_all or args.java:
        results.append(run_java_tests())
    if run_all or args.node:
        results.append(run_node_tests())

    report = aggregate_results(results)
    path   = save_report(report)
    print_summary(report)

    log("INFO", f"Report saved → {path}")
    log("INFO", "Open dashboard/index.html to view results")
    print()

    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

