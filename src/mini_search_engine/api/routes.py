from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from mini_search_engine.search.query_parser import QueryValidationError
from mini_search_engine.search.service import IndexNotLoadedError

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.get("/search")
def search_api():
    service = current_app.extensions["search_service"]
    metrics = current_app.extensions["metrics"]

    query = request.args.get("q", "")
    ranker = request.args.get("ranker")
    try:
        page = int(request.args.get("page", "1"))
        page_size = int(request.args.get("page_size", str(current_app.config["MSE_DEFAULT_PAGE_SIZE"])))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    try:
        result = service.search(query=query, page=page, page_size=page_size, ranker_name=ranker)
        metrics.search_requests_total += 1
        if result.get("cache_hit"):
            metrics.query_cache_hits += 1
        else:
            metrics.query_cache_misses += 1
        metrics.search_latency_samples.append(result["elapsed_ms"] / 1000)
        return jsonify(result)
    except (QueryValidationError, IndexNotLoadedError) as exc:
        metrics.search_errors_total += 1
        if isinstance(exc, QueryValidationError):
            return jsonify({"error": "Invalid query input"}), 400
        return jsonify({"error": "Search index is unavailable"}), 503


@api_bp.get("/suggest")
def suggest_api():
    service = current_app.extensions["search_service"]
    query = request.args.get("q", "")
    return jsonify({"suggestions": service.suggest(query)})


@api_bp.get("/index/stats")
def index_stats_api():
    service = current_app.extensions["search_service"]
    return jsonify(service.index_stats())


@api_bp.get("/health")
def health_api():
    service = current_app.extensions["search_service"]
    return jsonify({"status": "ok" if service.is_ready() else "degraded"})
