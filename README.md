# AutoAgent VNext

AutoAgent VNext is a self-healing, self-optimizing multi-agent system that follows a simple autoresearch loop:

1. Observe recent conversations.
2. Detect health degradation and failure patterns.
3. Propose one config change.
4. Evaluate candidate vs baseline.
5. Accept/reject with safety and regression gates.
6. Deploy accepted config as canary and promote or rollback.

This repository is intentionally CLI-first and mock-friendly so the full loop can run locally without external services.

## Architecture

- `agent/`: ADK root agent, specialists, tools, config schema/loader, and FastAPI server.
- `logger/`: SQLite conversation store and logging heuristics.
- `evals/`: YAML test corpus (55 cases), scorer, and eval runner.
- `observer/`: rolling metrics, anomaly detection, and failure classification.
- `optimizer/`: proposal generation, gates, optimization memory, and optimization loop.
- `deployer/`: config versioning and canary management.
- `runner.py`: CLI entry point.
- `tests/`: unit + integration coverage for observer, optimizer, evals, deployer, and full loop.

## Requirements

- Python 3.11+
- `pip`

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

## CLI Usage

All commands are namespaced under `run`:

```bash
python3 runner.py run agent
python3 runner.py run eval
python3 runner.py run observe
python3 runner.py run optimize
python3 runner.py run loop --cycles 5
python3 runner.py run status
```

Optional flags:

- `--db`: path to conversation DB (default `conversations.db`)
- `--configs-dir`: config version directory (default `configs`)
- `--memory-db`: optimizer memory DB (default `optimizer_memory.db`)
- `--category`: eval category for `run eval`

## FastAPI Endpoints

When `run agent` is running:

- `GET /health`
- `GET /dashboard`
- `GET /api/health`
- `GET /api/history`
- `GET /api/config`
- `GET /api/evals`
- `GET /api/conversations`
- `POST /chat`

## Dashboard

Visit `http://localhost:8000/dashboard` for a dark-mode monitoring UI built with Jinja2 + Tailwind CDN + Alpine.js.

Screenshot description:

- A slate-900 themed dashboard with an emerald/amber/rose health score hero.
- Sparkline KPI cards for success rate, latency, error rate, safety violations, and cost per conversation.
- Tabs for optimization history (with config diffs), active YAML config + canary state, eval breakdowns, and expandable recent conversations.
- Styling and spacing intentionally mirrors premium DevOps tooling with subtle borders, panel shadows, and status badges.

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "content-type: application/json" \
  -d '{"message":"Where is my order ORD-1002?"}'
```

## Running Tests

```bash
pytest -q
```

Current suite includes:

- Observer unit tests
- Optimizer gate/memory unit tests
- Eval loading/scoring unit tests
- Deployer version/canary unit tests
- Full integration loop test (observe -> optimize -> deploy -> promote)

## Docker

Build and run:

```bash
docker build -t autoagent-vnext .
docker run --rm -p 8000:8000 autoagent-vnext
```

With Docker Compose:

```bash
docker compose up --build
```

## Notes on Loop Verification

The integration test (`tests/test_integration.py`) verifies the full autoresearch loop using mock LLM/eval behavior:

1. Degraded conversation history is written.
2. Observer requests optimization.
3. Optimizer accepts a single targeted config change.
4. Deployer publishes a canary version.
5. Canary health check promotes to active.

This gives deterministic evidence that the core self-healing loop works end-to-end.
