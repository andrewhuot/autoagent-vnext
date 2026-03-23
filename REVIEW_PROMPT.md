# AutoAgent VNext — Deep Review + Polish Task

## Phase 1: Code Review & Optimization

Thoroughly review every Python file in this project. For each module:

1. **Read the code carefully** — understand what it does
2. **Check algorithmic correctness** — are the observer metrics, optimizer gates, eval scoring, anomaly detection, and canary logic actually correct?
3. **Simplify** — remove unnecessary abstractions, dead code, over-engineering. This should be Karpathy-simple.
4. **Optimize** — are there performance issues? Unnecessary DB queries? Bad data structures?
5. **Fix bugs** — any logic errors, edge cases, import issues, type errors?
6. **Improve the autoresearch loop** — is the optimizer/loop.py actually effective? Does the proposer generate useful changes? Are the gates well-calibrated?
7. **Verify integration** — does runner.py → observer → optimizer → deployer actually connect properly end-to-end?
8. **Tests** — run existing tests. Fix any that fail. Add missing coverage for critical paths.

Key files to review:
- `optimizer/loop.py` + `optimizer/proposer.py` + `optimizer/gates.py` (THE CORE)
- `observer/metrics.py` + `observer/anomaly.py` + `observer/classifier.py`
- `evals/runner.py` + `evals/scorer.py`
- `deployer/canary.py` + `deployer/versioning.py`
- `agent/root_agent.py` + `agent/specialists/*.py`
- `runner.py` (CLI)
- All test files

## Phase 2: Build a Status Dashboard

Currently this project has NO frontend — just CLI. Build a lightweight but polished web dashboard:

### Tech: Single-page app served from FastAPI
- Add `/dashboard` route to the existing FastAPI app in `agent/server.py`
- Use **Jinja2 templates** + **Tailwind CSS (CDN)** + **Alpine.js (CDN)** — no build step needed
- One HTML file: `agent/templates/dashboard.html`
- Static assets if needed: `agent/static/`

### Dashboard Pages (tabs or sections on one page):

**1. System Health (hero section)**
- Current config version + uptime
- Health score (big number with color: green/yellow/red)
- Key metrics cards: success rate, avg latency, error rate, safety violations, cost/conversation
- Trend sparklines for each metric (last 24h)

**2. Optimization History**
- Timeline of optimization attempts
- Each entry shows: timestamp, change proposed, status (accepted/rejected + reason), score before → after
- Visual diff of config changes (before/after YAML)

**3. Active Config**
- Current YAML config rendered nicely
- Version history dropdown
- Canary status (if active): traffic split, canary metrics vs baseline

**4. Eval Results**
- Last eval run summary: composite score, per-category breakdown
- Pass/fail for each test case category (happy path, edge cases, safety, regression)
- Expandable details per test case

**5. Recent Conversations**
- Last 20 conversations from the store
- Each shows: timestamp, outcome (success/fail), latency, cost, turns
- Click to expand full conversation

### Design Requirements
- **Dark mode** with clean, modern aesthetic
- Color palette: slate-900 background, emerald for success, amber for warning, rose for errors
- Typography: Inter font (Google Fonts CDN)
- Responsive but primarily desktop-optimized
- Cards with subtle borders and shadows
- Status badges with color coding
- The dashboard should feel like a premium DevOps monitoring tool (think: Vercel dashboard meets Datadog)

### API Endpoints (add to FastAPI)
- `GET /api/health` — current health metrics
- `GET /api/history` — optimization history
- `GET /api/config` — active config
- `GET /api/evals` — last eval results
- `GET /api/conversations` — recent conversations
- These power the dashboard via fetch() calls

## Deliverables
1. All code fixes and optimizations from Phase 1
2. Working dashboard accessible at `http://localhost:8000/dashboard`
3. Updated README with dashboard screenshot description
4. All tests still passing after changes
