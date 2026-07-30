from ai_api.evals.services import (
    GoldenEvaluationDatasetService,
    GoldenEvaluationDatasetValidationService,
)


def get_golden_evaluation_dataset_service() -> GoldenEvaluationDatasetService:
    return GoldenEvaluationDatasetService()


def get_golden_evaluation_dataset_validation_service() -> (
    GoldenEvaluationDatasetValidationService
):
    return GoldenEvaluationDatasetValidationService()
