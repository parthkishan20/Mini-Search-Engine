"""Crawler entrypoint wrapper."""

# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mini_search_engine.crawl.service import crawl_site

SEED_URL = "https://en.wikipedia.org/"
MAX_PAGES = 10
SAVE_DIR = "input_pages"

if __name__ == "__main__":
    result = crawl_site(seed_url=SEED_URL, save_dir=SAVE_DIR, max_pages=MAX_PAGES)
    print(json.dumps(result, indent=2))
