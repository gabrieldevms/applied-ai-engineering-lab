from fastapi import Request
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST


KNOWN_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})


class OperationalMetrics:
    def __init__(self) -> None:
        self._registry = CollectorRegistry()
        self._requests = Counter(
            "ai_quality_http_requests_total",
            "Completed application HTTP requests.",
            ("method", "route", "status_class"),
            registry=self._registry,
        )
        self._duration = Histogram(
            "ai_quality_http_request_duration_seconds",
            "Application HTTP request duration in seconds.",
            ("method", "route"),
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
            registry=self._registry,
        )
        self._readiness = Gauge(
            "ai_quality_readiness",
            "Last observed API readiness result: 1 ready, 0 not ready.",
            registry=self._registry,
        )
        self._readiness.set(0)

    def record_request(
        self, request: Request, status_code: int, duration_seconds: float
    ) -> None:
        if request.url.path == "/metrics":
            return

        method = self.method_label(request.method)
        route = self.route_label(request)
        self._requests.labels(method, route, self.status_class(status_code)).inc()
        self._duration.labels(method, route).observe(duration_seconds)

    def set_readiness(self, ready: bool) -> None:
        self._readiness.set(1 if ready else 0)

    def render(self) -> bytes:
        return generate_latest(self._registry)

    @staticmethod
    def method_label(method: str) -> str:
        return method if method in KNOWN_METHODS else "OTHER"

    @staticmethod
    def route_label(request: Request) -> str:
        route = request.scope.get("route")
        template = getattr(route, "path", None)
        return template if isinstance(template, str) else "unmatched"

    @staticmethod
    def status_class(status_code: int) -> str:
        return f"{status_code // 100}xx" if 100 <= status_code < 600 else "other"


operational_metrics = OperationalMetrics()

__all__ = ["CONTENT_TYPE_LATEST", "OperationalMetrics", "operational_metrics"]
