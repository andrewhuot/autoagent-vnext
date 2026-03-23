# AutoAgent VNext — Implementation Plan

## Build Order & Dependencies

### Phase 1: Foundation (no deps)
1. `pyproject.toml` — project config, dependencies (~30 lines)
2. `agent/config/schema.py` — config dataclass + validation (~80 lines)
3. `agent/config/base_config.yaml` — default agent config (~60 lines)
4. `configs/v001_base.yaml` — copy of base config as version 1 (~60 lines)
5. `agent/config/loader.py` — load YAML config + canary routing (~60 lines)

### Phase 2: Agent Core (depends on Phase 1)
6. `agent/tools/catalog.py` — mock product catalog tool (~60 lines)
7. `agent/tools/orders_db.py` — mock order database tool (~60 lines)
8. `agent/tools/faq.py` — mock FAQ search tool (~50 lines)
9. `agent/specialists/support.py` — customer support sub-agent (~50 lines)
10. `agent/specialists/orders.py` — order management sub-agent (~50 lines)
11. `agent/specialists/recommendations.py` — recommendation sub-agent (~50 lines)
12. `agent/root_agent.py` — root orchestrator (~80 lines)
13. `agent/__init__.py` — agent package init (~10 lines)

### Phase 3: Logger (depends on Phase 1)
14. `logger/store.py` — SQLite conversation store (~120 lines)
15. `logger/middleware.py` — logging middleware + outcome detection (~100 lines)
16. `logger/__init__.py` — logger package init (~5 lines)

### Phase 4: Eval Suite (depends on Phase 2, 3)
17. `evals/fixtures/mock_data.py` — mock product/order data (~80 lines)
18. `evals/scorer.py` — composite scoring logic (~100 lines)
19. `evals/runner.py` — eval suite runner (~120 lines)
20. `evals/cases/happy_path.yaml` — 15+ happy path cases (~200 lines)
21. `evals/cases/edge_cases.yaml` — 12+ edge cases (~160 lines)
22. `evals/cases/safety.yaml` — 13+ safety probes (~170 lines)
23. `evals/cases/regression.yaml` — 10+ regression cases (~130 lines)
24. `evals/__init__.py` (~5 lines)

### Phase 5: Observer (depends on Phase 3)
25. `observer/metrics.py` — rolling health metrics (~100 lines)
26. `observer/anomaly.py` — 2σ anomaly detection (~70 lines)
27. `observer/classifier.py` — failure classification (~80 lines)
28. `observer/__init__.py` (~5 lines)

### Phase 6: Optimizer (depends on Phase 4, 5)
29. `optimizer/memory.py` — SQLite attempt memory (~80 lines)
30. `optimizer/proposer.py` — LLM-based change proposer + mock (~100 lines)
31. `optimizer/gates.py` — safety/improvement/regression gates (~80 lines)
32. `optimizer/loop.py` — core optimization loop (~120 lines)
33. `optimizer/__init__.py` (~5 lines)

### Phase 7: Deployer (depends on Phase 1)
34. `deployer/versioning.py` — config version management (~100 lines)
35. `deployer/canary.py` — canary deploy logic (~100 lines)
36. `deployer/__init__.py` (~5 lines)

### Phase 8: CLI + Server (depends on all above)
37. `runner.py` — CLI entry point with all commands (~150 lines)
38. `agent/server.py` — FastAPI server (~80 lines)

### Phase 9: Tests
39. `tests/test_observer.py` (~120 lines)
40. `tests/test_optimizer.py` (~150 lines)
41. `tests/test_evals.py` (~100 lines)
42. `tests/test_deployer.py` (~100 lines)
43. `tests/test_integration.py` (~150 lines)
44. `tests/conftest.py` — shared fixtures (~80 lines)

### Phase 10: Docker
45. `Dockerfile` (~30 lines)
46. `docker-compose.yaml` (~30 lines)

## Estimated Total: ~3,500 lines code + ~700 lines tests + ~660 lines YAML test cases

## Key Design Decisions
- Config is a flat YAML with sections: routing, prompts, tools, thresholds
- Mock LLM returns deterministic responses based on input patterns
- SQLite DB auto-creates tables on first use
- Eval runner executes agent against test cases using mock tools
- Observer reads last 100 conversations from store
- Optimizer proposes changes to YAML config sections
- Deployer copies config files with version numbers
- Canary is simulated via config loader reading canary percentage
