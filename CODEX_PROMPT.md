# AutoAgent VNext — Build Task

Read BUILD_BRIEF.md thoroughly. This is a self-healing, self-optimizing ADK agent system following Karpathy's autoresearch pattern.

## What to build (in order):

### Step 1: Plan
Create a detailed implementation plan in PLAN.md before writing any code. Include file-by-file breakdown, dependencies, and build order.

### Step 2: ADK Agent
- Root orchestrator + 3 specialists (support, orders, recommendations)
- Externalized config (YAML) — this is what the optimizer edits
- Mock tools (catalog, orders DB, FAQ)
- FastAPI endpoint to serve conversations

### Step 3: Conversation Logger + Store
- SQLite-backed conversation logging
- Outcome detection heuristics

### Step 4: Eval Suite
- 50+ test cases in YAML (happy path, edge cases, safety probes, regression)
- Runner + composite scorer (40% quality, 25% safety, 20% latency, 15% cost)
- Safety hard gate

### Step 5: Observer
- Rolling health metrics from conversation store
- Anomaly detection (2σ)
- Failure classification into buckets

### Step 6: Optimizer (THE CORE)
- LLM-as-optimizer: reads failures, proposes config change
- Accept/reject gates: safety (hard), improvement (soft), regression (5% threshold)
- Simple flat memory table of past attempts
- One change at a time

### Step 7: Deployer
- Config versioning (configs/ directory)
- Canary logic (10% → monitor → promote/rollback)

### Step 8: CLI Runner
- `run agent`, `run observe`, `run optimize`, `run loop`, `run eval`, `run status`

### Step 9: Tests
- Unit tests for observer, optimizer, evals, deployer
- Integration test: full loop with mock LLM

### Step 10: Docker
- Dockerfile + docker-compose.yaml

## Key constraints:
- Use Google ADK Python SDK (`google-adk`)
- Mock all LLM/external calls for testability
- Under 5,000 lines of code (excluding tests)
- No frontend/dashboard — CLI only
- This must actually work as a loop: observe → diagnose → propose → eval → accept/reject → deploy

When completely finished, run: openclaw system event --text 'Done: AutoAgent VNext Codex build complete' --mode now
