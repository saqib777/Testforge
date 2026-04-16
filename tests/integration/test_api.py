"""
tests/integration/test_api.py

Python integration tests for the TestForge Node.js REST API.
Demonstrates cross-language testing: Python calling a JS service.

Prerequisites:
    node node-api/server.js &   # API must be running on port 3000
    pip install requests pytest
"""

import pytest
import requests
import json
import os

BASE_URL = os.environ.get("TESTFORGE_API", "http://localhost:3000")


# ── helpers ──────────────────────────────────────────────────────

def get(path: str) -> requests.Response:
    return requests.get(f"{BASE_URL}{path}", timeout=5)


# ── health check ─────────────────────────────────────────────────

class TestHealthEndpoint:

    def test_health_returns_200(self):
        res = get("/api/health")
        assert res.status_code == 200

    def test_health_body_has_status_ok(self):
        res = get("/api/health")
        assert res.json()["status"] == "ok"

    def test_health_body_has_timestamp(self):
        res = get("/api/health")
        data = res.json()
        assert "timestamp" in data
        # must be parseable as ISO datetime
        from datetime import datetime
        datetime.fromisoformat(data["timestamp"])

    def test_health_content_type_is_json(self):
        res = get("/api/health")
        assert "application/json" in res.headers["Content-Type"]


# ── latest results ───────────────────────────────────────────────

class TestLatestResults:

    def test_returns_200(self):
        res = get("/api/results/latest")
        assert res.status_code == 200

    def test_has_run_id(self):
        res = get("/api/results/latest")
        assert "run_id" in res.json()

    def test_has_summary(self):
        data = get("/api/results/latest").json()
        assert "summary" in data
        summary = data["summary"]
        for field in ("total", "passed", "failed", "duration_seconds", "success_rate"):
            assert field in summary, f"Missing field: {field}"

    def test_summary_values_are_numeric(self):
        summary = get("/api/results/latest").json()["summary"]
        assert isinstance(summary["total"],            int)
        assert isinstance(summary["passed"],           int)
        assert isinstance(summary["failed"],           int)
        assert isinstance(summary["duration_seconds"], (int, float))
        assert isinstance(summary["success_rate"],     (int, float))

    def test_passed_plus_failed_equals_total(self):
        summary = get("/api/results/latest").json()["summary"]
        assert summary["passed"] + summary["failed"] == summary["total"]

    def test_has_results_array(self):
        data = get("/api/results/latest").json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_each_result_has_required_fields(self):
        results = get("/api/results/latest").json()["results"]
        required = {"language", "tool", "passed", "duration"}
        for r in results:
            missing = required - set(r.keys())
            assert not missing, f"Missing fields in result: {missing}"

    def test_success_rate_is_percentage(self):
        summary = get("/api/results/latest").json()["summary"]
        assert 0 <= summary["success_rate"] <= 100


# ── results list ─────────────────────────────────────────────────

class TestResultsList:

    def test_returns_200(self):
        res = get("/api/results")
        assert res.status_code == 200

    def test_has_count_and_runs(self):
        data = get("/api/results").json()
        assert "count" in data
        assert "runs"  in data

    def test_count_matches_runs_length(self):
        data = get("/api/results").json()
        assert data["count"] == len(data["runs"])

    def test_each_run_has_run_id(self):
        runs = get("/api/results").json()["runs"]
        for run in runs:
            assert "run_id" in run


# ── specific run ─────────────────────────────────────────────────

class TestSpecificRun:

    @pytest.fixture(autouse=True)
    def get_run_id(self):
        data = get("/api/results/latest").json()
        self.run_id = data["run_id"]

    def test_fetch_by_valid_id(self):
        res = get(f"/api/results/{self.run_id}")
        assert res.status_code == 200

    def test_fetched_run_matches_id(self):
        res = get(f"/api/results/{self.run_id}")
        assert res.json()["run_id"] == self.run_id

    def test_unknown_run_id_returns_404(self):
        res = get("/api/results/run_0000000_000000")
        assert res.status_code == 404

    def test_404_body_has_error_field(self):
        res = get("/api/results/run_0000000_000000")
        assert "error" in res.json()


# ── stats ────────────────────────────────────────────────────────

class TestStats:

    def test_returns_200(self):
        res = get("/api/stats")
        assert res.status_code == 200

    def test_has_trend_array(self):
        data = get("/api/stats").json()
        assert "trend" in data
        assert isinstance(data["trend"], list)

    def test_trend_entries_have_required_fields(self):
        trend = get("/api/stats").json()["trend"]
        if trend:  # only check if data exists
            required = {"run_id", "timestamp", "passed", "failed", "duration"}
            for entry in trend:
                missing = required - set(entry.keys())
                assert not missing, f"Missing trend fields: {missing}"


# ── 404 catch-all ────────────────────────────────────────────────

class TestNotFound:

    def test_unknown_route_returns_404(self):
        res = get("/api/thisdoesnotexist")
        assert res.status_code == 404

    def test_404_body_is_json(self):
        res = get("/api/thisdoesnotexist")
        assert res.headers["Content-Type"].startswith("application/json")

