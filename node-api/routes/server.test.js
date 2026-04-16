/**
 * TestForge — Node.js API tests (Jest)
 * Tests the Express REST endpoints using supertest.
 */

const request = require("supertest");
const app     = require("../server");
const path    = require("path");
const fs      = require("fs");

const REPORTS_DIR = path.join(__dirname, "..", "..", "reports");

// ── helpers ──────────────────────────────────────────────────────

function seedReport(runId, data) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
  fs.writeFileSync(
    path.join(REPORTS_DIR, `run_${runId}.json`),
    JSON.stringify(data)
  );
  fs.writeFileSync(
    path.join(REPORTS_DIR, "latest.json"),
    JSON.stringify(data)
  );
}

const MOCK_REPORT = {
  run_id: "20260101_120000",
  timestamp: "2026-01-01T12:00:00",
  summary: { total: 3, passed: 3, failed: 0, duration_seconds: 4.2, success_rate: 100 },
  results: [
    { language: "Python",     tool: "pytest",   passed: true, duration: 1.2 },
    { language: "Java",       tool: "JUnit 5",  passed: true, duration: 2.0 },
    { language: "JavaScript", tool: "Jest",     passed: true, duration: 1.0 },
  ],
};

beforeAll(() => seedReport(MOCK_REPORT.run_id, MOCK_REPORT));

afterAll(() => {
  const files = [
    path.join(REPORTS_DIR, `run_${MOCK_REPORT.run_id}.json`),
    path.join(REPORTS_DIR, "latest.json"),
  ];
  files.forEach(f => { if (fs.existsSync(f)) fs.unlinkSync(f); });
});

// ── /api/health ──────────────────────────────────────────────────

describe("GET /api/health", () => {
  it("returns 200 with status ok", async () => {
    const res = await request(app).get("/api/health");
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe("ok");
  });

  it("returns a valid ISO timestamp", async () => {
    const res = await request(app).get("/api/health");
    expect(() => new Date(res.body.timestamp)).not.toThrow();
  });

  it("returns version field", async () => {
    const res = await request(app).get("/api/health");
    expect(res.body).toHaveProperty("version");
  });
});

// ── /api/results/latest ──────────────────────────────────────────

describe("GET /api/results/latest", () => {
  it("returns the latest report", async () => {
    const res = await request(app).get("/api/results/latest");
    expect(res.statusCode).toBe(200);
    expect(res.body.run_id).toBe(MOCK_REPORT.run_id);
  });

  it("includes summary object", async () => {
    const res = await request(app).get("/api/results/latest");
    expect(res.body).toHaveProperty("summary");
    expect(res.body.summary.total).toBe(3);
  });

  it("includes results array", async () => {
    const res = await request(app).get("/api/results/latest");
    expect(Array.isArray(res.body.results)).toBe(true);
    expect(res.body.results).toHaveLength(3);
  });
});

// ── /api/results ─────────────────────────────────────────────────

describe("GET /api/results", () => {
  it("returns list of runs", async () => {
    const res = await request(app).get("/api/results");
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty("runs");
    expect(Array.isArray(res.body.runs)).toBe(true);
  });

  it("includes count field", async () => {
    const res = await request(app).get("/api/results");
    expect(res.body.count).toBeGreaterThanOrEqual(1);
  });
});

// ── /api/results/:runId ──────────────────────────────────────────

describe("GET /api/results/:runId", () => {
  it("returns report for valid run ID", async () => {
    const res = await request(app).get(`/api/results/${MOCK_REPORT.run_id}`);
    expect(res.statusCode).toBe(200);
    expect(res.body.run_id).toBe(MOCK_REPORT.run_id);
  });

  it("returns 404 for unknown run ID", async () => {
    const res = await request(app).get("/api/results/run_9999");
    expect(res.statusCode).toBe(404);
    expect(res.body).toHaveProperty("error");
  });
});

// ── /api/stats ───────────────────────────────────────────────────

describe("GET /api/stats", () => {
  it("returns trend array", async () => {
    const res = await request(app).get("/api/stats");
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body.trend)).toBe(true);
  });
});

// ── 404 catch-all ────────────────────────────────────────────────

describe("Unknown routes", () => {
  it("returns 404 for unknown endpoint", async () => {
    const res = await request(app).get("/api/nonexistent");
    expect(res.statusCode).toBe(404);
  });
});

