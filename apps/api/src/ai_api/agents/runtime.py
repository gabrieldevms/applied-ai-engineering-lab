import hashlib
from datetime import UTC, datetime

from ai_api.agents.schemas import AgentRunResponse, AgentStep


class AgentRuntime:
    def run(
        self,
        objective: str,
        context: str | None = None,
        max_steps: int = 3,
        metadata: dict | None = None,
    ) -> AgentRunResponse:
        cleaned_objective = objective.strip()
        cleaned_context = context.strip() if context else None

        if not cleaned_objective:
            raise ValueError("objective cannot be blank")

        if max_steps < 1:
            raise ValueError("max_steps must be greater than zero")

        run_id = self._build_run_id(cleaned_objective)

        planned_steps = self._build_steps(
            objective=cleaned_objective,
            context=cleaned_context,
            max_steps=max_steps,
        )

        return AgentRunResponse(
            run_id=run_id,
            objective=cleaned_objective,
            status="completed",
            final_answer=self._build_final_answer(
                objective=cleaned_objective,
                context=cleaned_context,
                total_steps=len(planned_steps),
            ),
            steps=planned_steps,
            metadata={
                **(metadata or {}),
                "runtime": "deterministic-agent-runtime-v1",
                "created_at": datetime.now(UTC).isoformat(),
                "max_steps": max_steps,
                "has_context": cleaned_context is not None,
            },
        )

    def _build_steps(
        self,
        objective: str,
        context: str | None,
        max_steps: int,
    ) -> list[AgentStep]:
        candidate_steps = [
            AgentStep(
                step_id="step-1",
                name="understand_objective",
                status="completed",
                input={"objective": objective},
                output={
                    "summary": "Objective was received and normalized.",
                },
            ),
            AgentStep(
                step_id="step-2",
                name="inspect_context",
                status="completed" if context else "skipped",
                input={"has_context": context is not None},
                output={
                    "summary": (
                        "Context was provided and inspected."
                        if context
                        else "No context was provided."
                    )
                },
            ),
            AgentStep(
                step_id="step-3",
                name="produce_final_answer",
                status="completed",
                input={
                    "objective": objective,
                    "has_context": context is not None,
                },
                output={
                    "summary": "Final answer was produced.",
                },
            ),
        ]

        return candidate_steps[:max_steps]

    def _build_final_answer(
        self,
        objective: str,
        context: str | None,
        total_steps: int,
    ) -> str:
        if context:
            return (
                "Agent execution completed using the provided context. "
                f"Objective: {objective}. "
                f"Executed steps: {total_steps}."
            )

        return (
            "Agent execution completed without additional context. "
            f"Objective: {objective}. "
            f"Executed steps: {total_steps}."
        )

    def _build_run_id(self, objective: str) -> str:
        objective_hash = hashlib.sha256(
            objective.encode("utf-8")
        ).hexdigest()[:12]

        return f"agent-run-{objective_hash}"
