from ai_api.evals.golden_dataset import build_default_golden_evaluation_dataset
from ai_api.evals.schemas import (
    EvaluationDatasetValidationMetric,
    EvaluationDatasetValidationResponse,
    EvaluationScenarioType,
    GoldenEvaluationDataset,
)


REQUIRED_SCENARIO_TYPES: list[EvaluationScenarioType] = [
    "requirement_analysis",
    "rag_answer",
    "qa_agent",
    "data_analyst_agent",
    "multi_agent_qa_copilot",
    "mcp_tool",
]


class GoldenEvaluationDatasetService:
    def get_default_dataset(self) -> GoldenEvaluationDataset:
        return build_default_golden_evaluation_dataset()


class GoldenEvaluationDatasetValidationService:
    def validate(
        self,
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationResponse:
        metrics = [
            self._validate_non_empty_dataset(dataset),
            self._validate_unique_scenario_ids(dataset),
            self._validate_required_type_coverage(dataset),
            self._validate_scenario_inputs(dataset),
            self._validate_scenario_expectations(dataset),
        ]

        failed_metrics = [
            metric
            for metric in metrics
            if metric.status == "failed"
        ]
        warning_metrics = [
            metric
            for metric in metrics
            if metric.status == "warning"
        ]

        if failed_metrics:
            status = "invalid"
        elif warning_metrics:
            status = "warning"
        else:
            status = "valid"

        type_coverage = self._build_type_coverage(dataset)
        missing_required_types = self._find_missing_required_types(type_coverage)

        return EvaluationDatasetValidationResponse(
            status=status,
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            scenario_count=len(dataset.scenarios),
            type_coverage=type_coverage,
            missing_required_types=missing_required_types,
            metrics=metrics,
            metadata={
                "validator": "golden-evaluation-dataset-validator-v1",
                "required_scenario_types": REQUIRED_SCENARIO_TYPES,
            },
        )

    def validate_default_dataset(self) -> EvaluationDatasetValidationResponse:
        dataset = build_default_golden_evaluation_dataset()

        return self.validate(dataset)

    @staticmethod
    def _validate_non_empty_dataset(
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationMetric:
        if dataset.scenarios:
            return EvaluationDatasetValidationMetric(
                name="non_empty_dataset",
                status="passed",
                summary="Dataset contains at least one scenario.",
                metadata={
                    "scenario_count": len(dataset.scenarios),
                },
            )

        return EvaluationDatasetValidationMetric(
            name="non_empty_dataset",
            status="failed",
            summary="Dataset does not contain any scenarios.",
            metadata={
                "scenario_count": 0,
            },
        )

    @staticmethod
    def _validate_unique_scenario_ids(
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationMetric:
        scenario_ids = [
            scenario.id
            for scenario in dataset.scenarios
        ]

        duplicate_ids = sorted(
            {
                scenario_id
                for scenario_id in scenario_ids
                if scenario_ids.count(scenario_id) > 1
            }
        )

        if not duplicate_ids:
            return EvaluationDatasetValidationMetric(
                name="unique_scenario_ids",
                status="passed",
                summary="All scenario identifiers are unique.",
                metadata={
                    "duplicate_ids": [],
                },
            )

        return EvaluationDatasetValidationMetric(
            name="unique_scenario_ids",
            status="failed",
            summary="Duplicate scenario identifiers were found.",
            metadata={
                "duplicate_ids": duplicate_ids,
            },
        )

    def _validate_required_type_coverage(
        self,
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationMetric:
        type_coverage = self._build_type_coverage(dataset)
        missing_required_types = self._find_missing_required_types(type_coverage)

        if not missing_required_types:
            return EvaluationDatasetValidationMetric(
                name="required_type_coverage",
                status="passed",
                summary="Dataset covers all required scenario types.",
                metadata={
                    "type_coverage": type_coverage,
                    "missing_required_types": [],
                },
            )

        return EvaluationDatasetValidationMetric(
            name="required_type_coverage",
            status="failed",
            summary="Dataset is missing one or more required scenario types.",
            metadata={
                "type_coverage": type_coverage,
                "missing_required_types": missing_required_types,
            },
        )

    @staticmethod
    def _validate_scenario_inputs(
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationMetric:
        scenarios_without_input = [
            scenario.id
            for scenario in dataset.scenarios
            if not scenario.input_payload
        ]

        if not scenarios_without_input:
            return EvaluationDatasetValidationMetric(
                name="scenario_inputs",
                status="passed",
                summary="All scenarios contain input payloads.",
                metadata={
                    "scenarios_without_input": [],
                },
            )

        return EvaluationDatasetValidationMetric(
            name="scenario_inputs",
            status="failed",
            summary="One or more scenarios do not contain input payloads.",
            metadata={
                "scenarios_without_input": scenarios_without_input,
            },
        )

    @staticmethod
    def _validate_scenario_expectations(
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationMetric:
        scenarios_without_expectations = [
            scenario.id
            for scenario in dataset.scenarios
            if (
                scenario.expectations.expected_status is None
                and scenario.expectations.expected_quality_gate is None
                and not scenario.expectations.required_output_markers
                and not scenario.expectations.required_metadata_keys
            )
        ]

        if not scenarios_without_expectations:
            return EvaluationDatasetValidationMetric(
                name="scenario_expectations",
                status="passed",
                summary="All scenarios contain at least one expectation.",
                metadata={
                    "scenarios_without_expectations": [],
                },
            )

        return EvaluationDatasetValidationMetric(
            name="scenario_expectations",
            status="warning",
            summary="One or more scenarios have weak expectations.",
            metadata={
                "scenarios_without_expectations": scenarios_without_expectations,
            },
        )

    @staticmethod
    def _build_type_coverage(
        dataset: GoldenEvaluationDataset,
    ) -> dict[str, int]:
        type_coverage = {
            scenario_type: 0
            for scenario_type in REQUIRED_SCENARIO_TYPES
        }

        for scenario in dataset.scenarios:
            type_coverage[scenario.type] = type_coverage.get(
                scenario.type,
                0,
            ) + 1

        return type_coverage

    @staticmethod
    def _find_missing_required_types(
        type_coverage: dict[str, int],
    ) -> list[str]:
        return [
            scenario_type
            for scenario_type in REQUIRED_SCENARIO_TYPES
            if type_coverage.get(scenario_type, 0) == 0
        ]
