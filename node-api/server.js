/**
 * TestForge — Node.js REST API
 * Serves test results and exposes endpoints for the dashboard.
 * Run: node server.js
 */

const express = require("express");
const path    = require("path");
const fs      = require("fs");

const app  = express();
const PORT = process.env.PORT || 3000;
const REPORTS_DIR = path.join(__dirname, "..", "reports");

app.use(express.json());
app.use(express.static(path.join(__dirname, "..", "dashboard")));

// ── CORS for local dev ──────────────────────────────────────────
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type");
  next();
});

// ── helpers ─────────────────────────────────────────────────────
function loadReport(filename) {
  const filePath = path.join(REPORTS_DIR, filename);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function listReports() {
  if (!fs.existsSync(REPORTS_DIR)) return [];
  return fs.readdirSync(REPORTS_DIR)
    .filter(f => f.startsWith("run_") && f.endsWith(".json"))
    .sort()
    .reverse();
}

// ── routes ───────────────────────────────────────────────────────

/**
 * GET /api/health
 * Returns API status.
 */
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString(), version: "1.0.0" });
});

/**
 * GET /api/results/latest
 * Returns the most recent test run.
 */
app.get("/api/results/latest", (req, res) => {
  const report = loadReport("latest.json");
  if (!report) return res.status(404).json({ error: "No results found" });
  res.json(report);
});

/**
 * GET /api/results
 * Lists all available run IDs.
 */
app.get("/api/results", (req, res) => {
  const files = listReports();
  const runs = files.map(f => ({
    run_id: f.replace("run_", "").replace(".json", ""),
    file: f,
  }));
  res.json({ count: runs.length, runs });
});

/**
 * GET /api/results/:runId
 * Returns a specific run by ID.
 */
app.get("/api/results/:runId", (req, res) => {
  const report = loadReport(`run_${req.params.runId}.json`);
  if (!report) return res.status(404).json({ error: "Run not found" });
  res.json(report);
});

/**
 * GET /api/stats
 * Aggregates pass/fail trends across all runs.
 */
app.get("/api/stats", (req, res) => {
  const files = listReports().slice(0, 20); // last 20 runs
  const trend = files.reverse().map(f => {
    const r = loadReport(f);
    return {
      run_id:   r.run_id,
      timestamp: r.timestamp,
      passed:   r.summary.passed,
      failed:   r.summary.failed,
      duration: r.summary.duration_seconds,
    };
  });
  res.json({ trend });
});

// ── 404 catch-all ─────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ error: "Endpoint not found" });
});

// ── start ─────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\n  ● TestForge API running → http://localhost:${PORT}`);
  console.log(`  ● Dashboard          → http://localhost:${PORT}/index.html`);
  console.log(`  ● Latest results     → http://localhost:${PORT}/api/results/latest\n`);
});

module.exports = app; // for Jest tests

