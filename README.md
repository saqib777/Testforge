# ⚡ TestForge

**A polyglot test automation framework** — one project, six languages, real software testing concepts, end-to-end CI/CD pipeline.

![Languages](https://img.shields.io/badge/languages-6-blue)
![Python](https://img.shields.io/badge/Python-pytest-3776AB?logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-JUnit_5-ED8B00?logo=openjdk&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Jest-F7DF1E?logo=javascript&logoColor=black)
![Bash](https://img.shields.io/badge/Bash-CI_runner-4EAA25?logo=gnubash&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-config-CB171E)
![HTML](https://img.shields.io/badge/HTML%2FCSS-dashboard-E34F26?logo=html5&logoColor=white)
![Tests](https://img.shields.io/badge/tests-72%20passing-brightgreen)

---

## 🧠 What Is This Project?

TestForge is a **multi-language test automation framework** that coordinates test suites written in Python, Java, and JavaScript — running them all from a single command, collecting their results, and displaying them on a live web dashboard.

Most beginner developers write tests only in one language, usually the same one they write their application code in. TestForge was built to break out of that pattern. It treats **testing itself as a first-class engineering discipline** that spans the entire software stack — not just one language or one tool.

The project is structured the way a real company's CI/CD pipeline works: different teams own different modules in different languages, a central orchestrator coordinates them all, results are stored as structured data, exposed via a REST API, and visualised in a browser dashboard that updates automatically.

---

## ❓ What Problem Does It Solve?

### The single-language trap

When you only ever test in Python, you miss the fact that testing is a universal discipline. Every language has its own testing ecosystem — JUnit for Java, Jest for JavaScript, RSpec for Ruby — and senior engineers are expected to understand testing concepts regardless of which language is in front of them. TestForge forces you to think about testing as a concept, not just a tool.

### The "tests live in isolation" problem

In most student or beginner projects, tests are an afterthought — a single file that checks a few functions. In real software engineering, tests are part of the CI/CD pipeline. They run automatically on every code push, results are stored, trends are tracked, and failures block deployments. TestForge demonstrates exactly this pipeline from end to end.

### The "I only know Python" GitHub profile problem

Looking at a GitHub profile where every repo is Python tells one story. A repo that contains Python, Java, JavaScript, Bash, YAML, and HTML — all working together coherently — tells a much more interesting one. TestForge adds genuine language diversity to a portfolio in a way that makes engineering sense, not just "I wrote Hello World in 6 languages."

### The visibility problem

When tests fail in a terminal, the information dies there. TestForge persists results as JSON, serves them through a REST API, and renders them in a live dashboard. This mirrors how real engineering teams use tools like Allure, ReportPortal, or Datadog to make test results visible across the organisation.

---

## 🔄 How It Works — The Full Flow

```
┌─────────────────────────────────────────────────────────┐
│                    You / GitHub Actions                  │
│              git push  or  ./ci/run_tests.sh             │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Bash CI Runner                          │
│                ci/run_tests.sh                           │
│  Checks dependencies (python, java, node, mvn)          │
│  Logs everything to reports/ci_<timestamp>.log           │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Python Orchestrator                         │
│            orchestrator/runner.py                        │
│  Uses subprocess to spawn each language runtime          │
│  Collects exit codes, stdout, and duration per module    │
└──────┬──────────────────┬──────────────────┬────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌────────────┐   ┌──────────────┐   ┌──────────────────┐
│   Python   │   │     Java     │   │   JavaScript     │
│   pytest   │   │   JUnit 5    │   │      Jest        │
│            │   │   + Maven    │   │   + Supertest    │
│ calculator │   │ StringUtils  │   │  REST API tests  │
│ bank acct  │   │ TaskManager  │   │  5 endpoints     │
│ API tests  │   │              │   │                  │
└─────┬──────┘   └──────┬───────┘   └────────┬─────────┘
      │                 │                     │
      └─────────────────┼─────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                JSON Results Store                        │
│     reports/run_<timestamp>.json  +  reports/latest.json │
│  { run_id, timestamp, summary: {passed, failed, ...},   │
│    results: [ {language, tool, passed, duration} ] }     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               Node.js REST API                           │
│              node-api/server.js                          │
│  GET /api/health          — server status                │
│  GET /api/results/latest  — most recent run              │
│  GET /api/results         — list all run IDs             │
│  GET /api/results/:runId  — specific run by ID           │
│  GET /api/stats           — trend data (last 20 runs)    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               HTML Dashboard                             │
│             dashboard/index.html                         │
│  Fetches from Node API every 30 seconds                  │
│  Shows: pass/fail counts, duration bars, run log         │
│  Works in demo mode if server is not running             │
└─────────────────────────────────────────────────────────┘
```

### Step-by-step walkthrough

**Step 1 — Trigger.** You either push to GitHub (which triggers the GitHub Actions workflow in `ci/github-actions.yml`) or run `./ci/run_tests.sh` locally. Both paths ultimately call the Python orchestrator.

**Step 2 — Bash CI checks the environment.** `run_tests.sh` verifies that Python, Java, Maven, and Node.js are all installed before attempting to run anything. If a tool is missing it warns you and skips that module gracefully rather than crashing the whole run.

**Step 3 — Python orchestrator spawns child processes.** `runner.py` uses Python's `subprocess` module to execute `pytest`, `mvn test`, and `npm test` as separate operating system processes. This is the key architectural decision — Python doesn't *know* how to run Java tests. It just tells the OS "run this command" and waits for the result. This is exactly how real CI systems like Jenkins or GitHub Actions work internally.

**Step 4 — Each language runs its own tests independently.** Python runs pytest across two test files. Java runs JUnit 5 via Maven's Surefire plugin. Node.js runs Jest against the Express API. Each module has no knowledge of the others — they're completely independent. The orchestrator is the only thing that knows about all of them.

**Step 5 — Results are aggregated into JSON.** The orchestrator collects the exit code (0 = passed, non-zero = failed), stdout output, and wall-clock duration from each subprocess. It builds a structured JSON report and saves it twice: once as `reports/run_<timestamp>.json` (permanent record) and once as `reports/latest.json` (overwritten every run, used by the dashboard).

**Step 6 — Node.js API serves the results.** `server.js` is a lightweight Express application that reads the JSON files from disk and exposes them as REST endpoints. It also serves the HTML dashboard as a static file. The API is the bridge between the file system and the browser.

**Step 7 — Dashboard renders live.** `dashboard/index.html` uses vanilla JavaScript to call the Node.js API every 30 seconds. It shows a summary of the latest run — how many suites passed, which languages failed, duration per module, and a formatted run log. If the API is not running it falls back to embedded demo data so the page always renders something useful.

---

## 🧪 Software Testing Concepts Demonstrated

### Unit testing
Testing individual functions or classes in complete isolation, with no external dependencies. The `Calculator` and `BankAccount` Python classes, `StringUtils` and `TaskManager` Java classes are all tested this way — no database, no network, no file system.

### Parametrized tests
Instead of writing one test per input, parametrized tests let you define a table of inputs and expected outputs and run the same test logic across all of them automatically. Used in Python with `@pytest.mark.parametrize` and in Java with `@ParameterizedTest` + `@CsvSource` / `@EnumSource` / `@ValueSource`.

### Test fixtures
Setup and teardown logic that runs before and after each test to ensure a clean, predictable state. In Python: `@pytest.fixture`. In Java: `@BeforeEach` and `@AfterEach`. Fixtures prevent tests from depending on each other's side effects, which is one of the most common sources of flaky tests.

### Nested test classes
Grouping related tests into nested classes for better organisation and readability. Both Python (pytest classes) and Java (JUnit 5 `@Nested`) use this pattern. It mirrors how a real test suite is structured in professional codebases.

### Exception and error testing
Verifying that code fails correctly — that the right exception is thrown with the right message under invalid conditions. Python uses `pytest.raises`, Java uses `assertThrows`. The `BankAccount` tests verify that withdrawing more than the balance raises `InsufficientFundsError`, and that a failed withdrawal leaves the balance unchanged.

### State machine testing
Testing that a system enforces valid state transitions and rejects invalid ones. The `TaskManager` Java tests verify that you cannot move a `DONE` or `CANCELLED` task back to `IN_PROGRESS` — the business rule is encoded in the tests, not just the implementation.

### Integration / API testing
Testing that multiple components work together correctly across a network boundary. `tests/integration/test_api.py` uses Python's `requests` library to call the Node.js REST API and verify that every endpoint returns the correct shape, status codes, and data types. This is cross-language integration testing — Python verifying a JavaScript service.

### Test aggregation and reporting
Collecting results from multiple independent test runners into a single unified report. The Python orchestrator does this across three languages. This is what tools like Allure Report, ReportPortal, and TestRail do at enterprise scale.

### CI/CD pipeline integration
Running tests automatically on every code push using GitHub Actions. The `ci/github-actions.yml` workflow defines three parallel jobs — one per language — that each run their own tests and upload artifacts. A fourth job aggregates the results. This is a simplified version of the pipeline pattern used at every major software company.

---

## 🗂 Project Structure

```
testforge/
├── orchestrator/
│   └── runner.py                         # Python — coordinates all modules
├── tests/
│   ├── sample/
│   │   ├── test_calculator.py            # Python — arithmetic unit tests
│   │   └── test_bank_account.py          # Python — OOP + exception testing
│   └── integration/
│       └── test_api.py                   # Python — calls Node.js API over HTTP
├── java-module/
│   ├── pom.xml                           # Maven build configuration
│   └── src/test/java/com/testforge/
│       ├── StringUtilsTest.java          # Java — string utility unit tests
│       └── TaskManagerTest.java          # Java — state machine + lifecycle tests
├── node-api/
│   ├── server.js                         # JavaScript — Express REST API
│   ├── package.json                      # Node.js dependencies
│   └── routes/
│       └── server.test.js                # JavaScript — Jest + Supertest API tests
├── dashboard/
│   └── index.html                        # HTML/CSS/JS — live results dashboard
├── ci/
│   ├── run_tests.sh                      # Bash — local CI pipeline runner
│   └── github-actions.yml               # YAML — GitHub Actions workflow
├── config/
│   └── default.yaml                      # YAML — test suite configuration
├── reports/                              # JSON results (auto-generated on each run)
├── setup.sh                              # One-command dependency installer
├── pytest.ini                            # pytest configuration
└── requirements.txt                      # Python dependencies
```

---

## 🛠 Languages & What Each One Does

| Language | File(s) | Role | Why this language |
|----------|---------|------|-------------------|
| **Python** | `runner.py`, `test_*.py` | Orchestrator + test suites | Best for scripting, subprocess control, and rapid test writing. The glue that holds everything together. |
| **Java** | `*Test.java`, `pom.xml` | Unit testing module | Java has the most mature testing ecosystem (JUnit is 25+ years old). Demonstrates OOP testing patterns, annotations, and Maven builds. |
| **JavaScript** | `server.js`, `server.test.js` | REST API + API tests | Node.js is the standard for lightweight REST APIs. Jest + Supertest is the industry standard for testing Express applications. |
| **Bash** | `run_tests.sh` | CI runner | Shell scripts are universal in CI/CD. Every pipeline runner (Jenkins, GitHub Actions, CircleCI) uses shell commands under the hood. |
| **YAML** | `github-actions.yml`, `default.yaml` | Configuration | YAML is the lingua franca of DevOps. GitHub Actions, Kubernetes, Docker Compose, Ansible — all use YAML for configuration. |
| **HTML/CSS/JS** | `index.html` | Live dashboard | Results are useless if nobody can see them. A browser dashboard makes the output of the entire pipeline visible at a glance. |

---

## 🚀 Getting Started

### Prerequisites

| Tool | Min version | Install |
|------|-------------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| Java JDK | 17+ | [adoptium.net](https://adoptium.net) |
| Maven | 3.9+ | [maven.apache.org](https://maven.apache.org) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |

### 1. Setup (one time only)

```bash
git clone https://github.com/saqib777/testforge.git
cd testforge
chmod +x setup.sh && ./setup.sh
```

Or manually:
```bash
pip install -r requirements.txt
cd node-api && npm install && cd ..
copy reports\latest.json reports\run_20260415_120000.json
```

### 2. Run all tests

```bash
python orchestrator/runner.py --all
```

### 3. Start the dashboard

Open **two terminals**:

```bash
# Terminal 1 — keep this running
cd node-api
node server.js

# Terminal 2 — run tests
cd ..
python -m pytest tests/ -v
```

Then open `http://localhost:3000` in your browser.

---

## 🧩 Running Individual Modules

```bash
# Python unit tests only (no server needed)
python -m pytest tests/sample/ -v

# Python integration tests (requires node server running on :3000)
python -m pytest tests/integration/ -v

# Java tests only
cd java-module && mvn test

# Node.js Jest tests only
cd node-api && npm test

# Everything via orchestrator
python orchestrator/runner.py --all
python orchestrator/runner.py --python
python orchestrator/runner.py --java
python orchestrator/runner.py --node
```

---

## 🌐 REST API Reference

| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/health` | `{ status, timestamp, version }` |
| GET | `/api/results/latest` | Full report of the most recent run |
| GET | `/api/results` | `{ count, runs: [{run_id, file}] }` |
| GET | `/api/results/:runId` | Full report for a specific run ID |
| GET | `/api/stats` | `{ trend: [{run_id, passed, failed, duration}] }` |

---

## 🔜 Next Steps

- [ ] Add `--watch` mode to the orchestrator — re-run tests automatically when files change
- [ ] Add coverage reports — `pytest-cov` for Python, JaCoCo for Java, Istanbul for JavaScript
- [ ] Add a Go or Rust module to expand language coverage further
- [ ] Deploy the Node.js API + dashboard to Railway or Render for a public URL
- [ ] Add GitHub status badges showing live pass/fail from the Actions workflow
- [ ] Add a test history graph to the dashboard showing the trend over time

---

## 👤 Author

**Mohammed Saqib** ([@saqib777](https://github.com/saqib777))

- 405 contributions in 2026
- 🔥 23-day current streak
- 72-day longest streak
- 37 public repos

---

## 📄 License

MIT
