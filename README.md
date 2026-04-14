# ⚡ TestForge

**A polyglot test automation framework** — one project, five languages, real software testing concepts.

Built to go beyond Python-only development and demonstrate multi-language software engineering skills.

---

## 🗂 Project Structure

```
testforge/
├── orchestrator/
│   └── runner.py           # Python — test coordinator & CLI
├── tests/
│   └── sample/
│       └── test_calculator.py  # Python — pytest test suite
├── java-module/
│   ├── pom.xml             # Maven build config
│   └── src/test/java/com/testforge/
│       └── StringUtilsTest.java  # Java — JUnit 5 tests
├── node-api/
│   ├── server.js           # Node.js — Express REST API
│   ├── package.json
│   └── routes/
│       └── server.test.js  # JavaScript — Jest tests
├── dashboard/
│   └── index.html          # HTML/CSS/JS — live results dashboard
├── ci/
│   ├── run_tests.sh        # Bash — local CI runner
│   └── github-actions.yml  # YAML — GitHub Actions workflow
├── config/
│   └── default.yaml        # YAML — test suite configuration
├── reports/                # JSON results (auto-generated)
└── requirements.txt
```

---

## 🛠 Languages & What They Do

| Language | Role | Tool |
|----------|------|------|
| **Python** | Orchestrator, test runner | pytest |
| **Java** | Unit testing module | JUnit 5 + Maven |
| **JavaScript** | REST API + API tests | Node.js, Express, Jest |
| **Bash** | CI/CD pipeline | Shell scripting |
| **HTML/CSS/JS** | Live reporting dashboard | Vanilla JS |
| **YAML** | Config, GitHub Actions | Human-readable config |

---

## 🚀 Getting Started

### Prerequisites

| Tool | Min version | Check |
|------|-------------|-------|
| Python | 3.11+ | `python --version` |
| Java JDK | 17+ | `java -version` |
| Maven | 3.9+ | `mvn --version` |
| Node.js | 20+ | `node --version` |

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/testforge.git
cd testforge

# Python deps
pip install -r requirements.txt

# Node deps
cd node-api && npm install && cd ..
```

### 2. Run all tests

```bash
# Using the Python orchestrator
python orchestrator/runner.py --all

# Using the Bash CI script
chmod +x ci/run_tests.sh
./ci/run_tests.sh --all
```

### 3. View the dashboard

```bash
# Start the Node.js API
node node-api/server.js

# Then open in browser
open http://localhost:3000
```

---

## 🧪 Running Modules Individually

```bash
# Python only
python orchestrator/runner.py --python
python -m pytest tests/ -v

# Java only
python orchestrator/runner.py --java
cd java-module && mvn test

# Node.js only
python orchestrator/runner.py --node
cd node-api && npm test
```

---

## 📊 How It Works

```
GitHub Push
    │
    ▼
Bash CI / GitHub Actions
    │
    ▼
Python Orchestrator (runner.py)
    ├── spawns pytest       → Python tests
    ├── spawns mvn test     → Java/JUnit tests
    └── spawns npm test     → Node/Jest tests
    │
    ▼
JSON Results (reports/)
    │
    ▼
Node.js REST API (server.js)
    │
    ▼
HTML Dashboard (dashboard/index.html)
```

---

## 🔬 Software Testing Concepts Covered

- **Unit testing** — pytest (Python), JUnit 5 (Java), Jest (JavaScript)
- **Parametrized tests** — `@pytest.mark.parametrize` and `@ParameterizedTest`
- **Test fixtures** — pytest `@fixture` and JUnit `@BeforeEach`
- **Nested test classes** — JUnit 5 `@Nested`
- **Exception testing** — `pytest.raises`, `assertThrows`
- **API testing** — supertest + Jest (integration tests)
- **Test aggregation** — Python orchestrator collects cross-language results
- **CI/CD** — GitHub Actions parallel jobs per language
- **Test reporting** — JSON → REST API → HTML dashboard

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | API status |
| GET | `/api/results/latest` | Most recent run |
| GET | `/api/results` | List all run IDs |
| GET | `/api/results/:runId` | Specific run |
| GET | `/api/stats` | Trend data (last 20 runs) |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Run the full test suite: `./ci/run_tests.sh --all`
4. Push and open a PR

---

## 📄 License

MIT — Mohammed Saqib (saqib777)
"# Testforge" 
