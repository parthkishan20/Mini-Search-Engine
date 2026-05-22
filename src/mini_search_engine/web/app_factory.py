from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

from mini_search_engine.api.routes import api_bp
from mini_search_engine.config import AppConfig
from mini_search_engine.indexing.analyzer import Analyzer, load_stopwords
from mini_search_engine.indexing.builder import build_index
from mini_search_engine.indexing.serializer import load_index, save_index
from mini_search_engine.observability.logging import Metrics, configure_logging
from mini_search_engine.search.query_parser import QueryValidationError
from mini_search_engine.search.service import SearchService

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    def __init__(self, max_per_minute: int) -> None:
        self.max_per_minute = max_per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        queue = self._hits[key]
        while queue and now - queue[0] > 60:
            queue.popleft()
        if len(queue) >= self.max_per_minute:
            return False
        queue.append(now)
        return True


def _load_or_build_index(config: AppConfig, analyzer: Analyzer) -> dict:
    path = Path(config.index_path)
    if path.exists():
        return load_index(config.index_path)

    index_data = build_index(config.input_dir, analyzer)
    save_index(index_data, config.index_path)
    logger.info("index built", extra={"event": "index_build_completed"})
    return index_data


def create_app(config: AppConfig | None = None) -> Flask:
    configure_logging()
    app_config = config or AppConfig()

    app = Flask(__name__)
    app.secret_key = app_config.flask_secret_key
    app.config["MSE_DEFAULT_PAGE_SIZE"] = app_config.default_page_size

    if app_config.enable_cors:
        CORS(app)

    analyzer = Analyzer(load_stopwords(app_config.stopwords_path))
    index_data = _load_or_build_index(app_config, analyzer)

    service = SearchService(index_data=index_data, analyzer=analyzer, config=app_config)
    metrics = Metrics()
    limiter = SimpleRateLimiter(app_config.rate_limit_per_minute)

    app.extensions["search_service"] = service
    app.extensions["metrics"] = metrics

    @app.before_request
    def _start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def _log_request(response):
        latency_ms = (time.perf_counter() - getattr(request, "_start_time", time.perf_counter())) * 1000
        logger.info(
            "request complete",
            extra={
                "event": "request_completed",
                "path": request.path,
                "method": request.method,
                "status": response.status_code,
                "latency_ms": round(latency_ms, 3),
                "ip": request.remote_addr,
            },
        )
        return response

    @app.before_request
    def _rate_limit():
        if request.endpoint in {"home", "api.search_api"}:
            ip = request.remote_addr or "unknown"
            if not limiter.allow(ip):
                return jsonify({"error": "Rate limit exceeded"}), 429
        return None

    @app.get("/health/live")
    def health_live():
        return jsonify({"status": "alive"})

    @app.get("/health/ready")
    def health_ready():
        return jsonify({"status": "ready" if service.is_ready() else "not_ready"})

    @app.get("/health/index")
    def health_index():
        return jsonify(service.index_stats())

    @app.get("/metrics")
    def metrics_endpoint():
        return app.extensions["metrics"].to_prometheus(), 200, {"Content-Type": "text/plain; version=0.0.4"}

    @app.route("/view/<path:filename>")
    def view_page(filename: str):
        return send_from_directory(app_config.input_dir, filename)

    @app.route("/", methods=["GET", "POST"])
    def home():
        results = []
        query = ""
        total = 0

        if request.method == "POST":
            query = request.form.get("query", "").strip()
            try:
                payload = service.search(query=query, page=1, page_size=app_config.default_page_size)
                results = payload["results"]
                total = payload["total"]
                if payload.get("cache_hit"):
                    metrics.query_cache_hits += 1
                else:
                    metrics.query_cache_misses += 1
                metrics.search_requests_total += 1
                metrics.search_latency_samples.append(payload["elapsed_ms"] / 1000)
            except QueryValidationError as exc:
                metrics.search_errors_total += 1
                return render_template("index.html", results=[], query=query, total=0, error=str(exc))

        return render_template("index.html", results=results, query=query, total=total, error=None)

    app.register_blueprint(api_bp)
    return app
