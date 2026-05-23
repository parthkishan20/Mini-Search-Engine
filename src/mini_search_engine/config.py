from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    input_dir: str = os.getenv("MSE_INPUT_DIR", "input_pages")
    stopwords_path: str = os.getenv("MSE_STOPWORDS_PATH", "stopwords.txt")
    index_path: str = os.getenv("MSE_INDEX_PATH", "index_data/index.json")
    flask_secret_key: str = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
    flask_debug: bool = _bool("FLASK_DEBUG", False)
    enable_cors: bool = _bool("MSE_ENABLE_CORS", False)
    max_query_length: int = int(os.getenv("MSE_MAX_QUERY_LENGTH", "200"))
    default_page_size: int = int(os.getenv("MSE_DEFAULT_PAGE_SIZE", "10"))
    max_page_size: int = int(os.getenv("MSE_MAX_PAGE_SIZE", "50"))
    rate_limit_per_minute: int = int(os.getenv("MSE_RATE_LIMIT_PER_MINUTE", "60"))
    default_ranker: str = os.getenv("MSE_DEFAULT_RANKER", "bm25")
    bm25_k1: float = float(os.getenv("MSE_BM25_K1", "1.5"))
    bm25_b: float = float(os.getenv("MSE_BM25_B", "0.75"))
