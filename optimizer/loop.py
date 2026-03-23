"""Core optimization loop: propose -> validate -> eval -> gate -> accept/reject."""

from __future__ import annotations

import json
import time
import uuid

from .gates import Gates
from .memory import OptimizationAttempt, OptimizationMemory
from .proposer import Proposer
from agent.config.schema import AgentConfig, config_diff, validate_config
from evals.runner import EvalRunner
from evals.scorer import CompositeScore
from observer.metrics import HealthReport


class Optimizer:
    """Runs one optimization cycle: propose a config change, evaluate it, gate it."""

    def __init__(
        self,
        eval_runner: EvalRunner,
        memory: OptimizationMemory | None = None,
        proposer: Proposer | None = None,
        gates: Gates | None = None,
    ) -> None:
        self.eval_runner = eval_runner
        self.memory = memory or OptimizationMemory()
        self.proposer = proposer or Proposer(use_mock=True)
        self.gates = gates or Gates()

    def optimize(
        self, health_report: HealthReport, current_config: dict
    ) -> tuple[dict | None, str]:
        """Run one optimization cycle. Returns (new_config_or_None, status_message)."""

        # 1. Gather failure samples and past attempts for the proposer
        failure_samples: list[dict] = []  # In real system, would pull from conversation store
        past_attempts = [
            {
                "change_description": a.change_description,
                "config_section": a.config_diff,
                "status": a.status,
            }
            for a in self.memory.recent(limit=20)
        ]

        # 2. Propose a config change
        proposal = self.proposer.propose(
            current_config=current_config,
            health_metrics=health_report.metrics.to_dict(),
            failure_samples=failure_samples,
            failure_buckets=health_report.failure_buckets,
            past_attempts=past_attempts,
        )
        if proposal is None:
            return None, "No proposal generated"

        # 3. Validate the proposed config against the schema
        try:
            validated_new = validate_config(proposal.new_config)
        except Exception as e:
            validated_old = validate_config(current_config)
            # Build a best-effort AgentConfig for diff even though validation failed
            attempt = OptimizationAttempt(
                attempt_id=str(uuid.uuid4())[:8],
                timestamp=time.time(),
                change_description=proposal.change_description,
                config_diff=f"Invalid config: {e}",
                status="rejected_invalid",
                health_context=json.dumps(health_report.metrics.to_dict()),
            )
            self.memory.log(attempt)
            return None, f"Invalid config: {e}"

        # 4. Run eval suite on baseline and candidate configs
        baseline_score = self.eval_runner.run(config=current_config)
        candidate_score = self.eval_runner.run(config=proposal.new_config)

        # 5. Run gates
        accepted, status, reason = self.gates.evaluate(candidate_score, baseline_score)

        # 6. Compute config diff for logging
        validated_old = validate_config(current_config)
        diff_str = config_diff(validated_old, validated_new)

        # 7. Log the attempt
        attempt = OptimizationAttempt(
            attempt_id=str(uuid.uuid4())[:8],
            timestamp=time.time(),
            change_description=proposal.change_description,
            config_diff=diff_str,
            status=status,
            score_before=baseline_score.composite,
            score_after=candidate_score.composite,
            health_context=json.dumps(health_report.metrics.to_dict()),
        )
        self.memory.log(attempt)

        if accepted:
            return proposal.new_config, f"ACCEPTED: {reason}"
        return None, f"REJECTED ({status}): {reason}"
