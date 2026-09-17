"""Smoke-test the local production-like observability profile."""

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


WEB_URL = "http://127.0.0.1:8080"
PROMETHEUS_URL = "http://127.0.0.1:9090"


def get_text(url: str) -> str:
    with urlopen(url, timeout=5) as response:
        if response.status != 200:
            raise AssertionError(f"Unexpected HTTP {response.status} from {url}")
        return response.read().decode("utf-8")


def get_json(url: str) -> dict:
    return json.loads(get_text(url))


def expect_not_found(url: str) -> None:
    try:
        get_text(url)
    except HTTPError as error:
        if error.code == 404:
            return
        raise AssertionError(f"Expected HTTP 404 from {url}, got {error.code}") from error
    raise AssertionError(f"Expected HTTP 404 from {url}")


def prometheus_query(expression: str) -> dict:
    query = urlencode({"query": expression})
    return get_json(f"{PROMETHEUS_URL}/api/v1/query?{query}")


def main() -> None:
    if '<div id="root">' not in get_text(f"{WEB_URL}/"):
        raise AssertionError("The frontend root did not return the application shell")
    if get_json(f"{WEB_URL}/api/health").get("status") != "ok":
        raise AssertionError("The public API health route is not healthy")
    if get_json(f"{WEB_URL}/api/ready").get("status") != "ready":
        raise AssertionError("The public API readiness route is not ready")
    scorecards = get_json(f"{WEB_URL}/api/observability/quality-scorecards")
    if len(scorecards.get("sections", [])) != 6:
        raise AssertionError("The AI quality scorecard route is unavailable")
    expect_not_found(f"{WEB_URL}/api/metrics")
    expect_not_found(f"{WEB_URL}/api/metrics/hidden")

    get_text(f"{PROMETHEUS_URL}/-/healthy")
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            targets = get_json(f"{PROMETHEUS_URL}/api/v1/targets")
            active = targets.get("data", {}).get("activeTargets", [])
            target_up = any(
                target.get("labels", {}).get("job") == "ai-quality-api"
                and target.get("health") == "up"
                for target in active
            )
            metric = prometheus_query('ai_quality_http_requests_total{route="/health"}')
            samples = metric.get("data", {}).get("result", [])
            if target_up and metric.get("status") == "success" and samples:
                print("Observability stack validated: API, web, Prometheus target, request metric, and private metrics boundary.")
                return
        except (HTTPError, URLError, TimeoutError):
            pass
        time.sleep(2)
    raise AssertionError("Prometheus did not scrape the API health request metric within 90 seconds")


if __name__ == "__main__":
    main()
