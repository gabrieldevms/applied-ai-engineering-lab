import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_SRC = PROJECT_ROOT / "apps" / "api" / "src"

if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from ai_api.evals import (  # noqa: E402
    CIEvaluationPipelineRunRequest,
    CIEvaluationPipelineService,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic AI evaluation pipeline."
    )

    parser.add_argument(
        "--output",
        default=".data/ai-evaluation-pipeline-report.json",
        help="Path where the JSON evaluation report will be written.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with non-zero status when the pipeline returns warning.",
    )
    parser.add_argument(
        "--skip-golden-smoke",
        action="store_true",
        help="Skip the golden dataset smoke stage.",
    )
    parser.add_argument(
        "--skip-llm-as-judge",
        action="store_true",
        help="Skip the controlled LLM-as-judge evaluation stage.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = CIEvaluationPipelineService()

    response = service.run(
        CIEvaluationPipelineRunRequest(
            include_golden_dataset_smoke=not args.skip_golden_smoke,
            include_llm_as_judge_evaluation=not args.skip_llm_as_judge,
            fail_on_warning=args.fail_on_warning,
            metadata={
                "source": "script:run_ai_evaluation_pipeline",
                "run_id": "ai-evaluation-pipeline",
            },
        )
    )

    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            response.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": response.status,
                "score": response.score,
                "stage_count": response.stage_count,
                "passed_count": response.passed_count,
                "warning_count": response.warning_count,
                "failed_count": response.failed_count,
                "should_fail_ci": response.should_fail_ci,
                "report_path": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if response.should_fail_ci:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
