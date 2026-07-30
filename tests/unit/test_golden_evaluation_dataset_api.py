from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    EvaluationDatasetValidationResponse,
    GoldenEvaluationDataset,
    get_golden_evaluation_dataset_service,
    get_golden_evaluation_dataset_validation_service,
)
from ai_api.main import app


class StubGoldenEvaluationDatasetService:
    def get_default_dataset(self) -> GoldenEvaluationDataset:
        return GoldenEvaluationDataset(
            name="stub-golden-dataset",
            version="0.1.0",
            description="Stub dataset for API tests.",
            scenarios=[],
            metadata={
                "source": "stub-service",
            },
        )


class StubGoldenEvaluationDatasetValidationService:
    def __init__(self) -> None:
        self.last_dataset: Any | None = None

    def validate_default_dataset(self) -> EvaluationDatasetValidationResponse:
        return EvaluationDatasetValidationResponse(
            status="valid",
            dataset_name="stub-golden-dataset",
            dataset_version="0.1.0",
            scenario_count=1,
            type_coverage={
                "requirement_analysis": 1,
            },
            missing_required_types=[],
            metrics=[],
            metadata={
                "source": "stub-validation-service",
            },
        )

    def validate(
        self,
        dataset: GoldenEvaluationDataset,
    ) -> EvaluationDatasetValidationResponse:
        self.last_dataset = dataset

        return EvaluationDatasetValidationResponse(
            status="valid",
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            scenario_count=len(dataset.scenarios),
            type_coverage={},
            missing_required_types=[],
            metrics=[],
            metadata={
                "source": "stub-validation-service",
            },
        )


def test_get_golden_evaluation_dataset_endpoint_should_return_dataset() -> None:
    app.dependency_overrides[
        get_golden_evaluation_dataset_service
    ] = lambda: StubGoldenEvaluationDatasetService()

    try:
        client = TestClient(app)

        response = client.get("/evals/golden-dataset")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-golden-dataset"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-service"
    finally:
        app.dependency_overrides.clear()


def test_validate_default_golden_evaluation_dataset_endpoint_should_return_validation() -> None:
    app.dependency_overrides[
        get_golden_evaluation_dataset_validation_service
    ] = lambda: StubGoldenEvaluationDatasetValidationService()

    try:
        client = TestClient(app)

        response = client.get("/evals/golden-dataset/validation")

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "valid"
        assert body["dataset_name"] == "stub-golden-dataset"
        assert body["metadata"]["source"] == "stub-validation-service"
    finally:
        app.dependency_overrides.clear()


def test_validate_golden_evaluation_dataset_endpoint_should_validate_payload() -> None:
    service = StubGoldenEvaluationDatasetValidationService()
    app.dependency_overrides[
        get_golden_evaluation_dataset_validation_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/golden-dataset/validate",
            json={
                "name": "custom-dataset",
                "version": "0.1.0",
                "description": "Custom dataset for API validation.",
                "scenarios": [],
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "valid"
        assert body["dataset_name"] == "custom-dataset"
        assert service.last_dataset is not None
        assert service.last_dataset.name == "custom-dataset"
    finally:
        app.dependency_overrides.clear()


def test_validate_golden_evaluation_dataset_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/golden-dataset/validate",
        json={
            "name": "",
            "version": "0.1.0",
            "description": "Invalid dataset.",
            "scenarios": [],
        },
    )

    assert response.status_code == 422
