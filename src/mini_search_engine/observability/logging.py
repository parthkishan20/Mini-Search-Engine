from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", record.getMessage()),
            "message": record.getMessage(),
        }
        for key in ("path", "method", "status", "latency_ms", "ip", "query"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


class Metrics:
    def __init__(self) -> None:
        self.search_requests_total = 0
        self.search_errors_total = 0
        self.search_latency_samples: list[float] = []
        self.query_cache_hits = 0
        self.query_cache_misses = 0
        self.start_time = time.time()

    def to_prometheus(self) -> str:
        count = len(self.search_latency_samples)
        avg_latency = sum(self.search_latency_samples) / count if count else 0.0
        cache_total = self.query_cache_hits + self.query_cache_misses
        hit_ratio = self.query_cache_hits / cache_total if cache_total else 0.0
        uptime = time.time() - self.start_time
        return "\n".join(
            [
                f"search_requests_total {self.search_requests_total}",
                f"search_errors_total {self.search_errors_total}",
                f"search_request_latency_seconds_avg {avg_latency:.6f}",
                f"query_cache_hit_ratio {hit_ratio:.6f}",
                f"app_uptime_seconds {uptime:.2f}",
                "",
            ]
        )
