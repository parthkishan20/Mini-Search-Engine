from __future__ import annotations

from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def crawl_site(
    seed_url: str,
    save_dir: str,
    max_pages: int = 10,
    max_depth: int = 2,
    timeout_seconds: int = 10,
    retries: int = 2,
) -> dict:
    parsed_seed = urlparse(seed_url)
    allowed_domain = parsed_seed.netloc
    out = Path(save_dir)
    out.mkdir(parents=True, exist_ok=True)

    queue = deque([(seed_url, 0)])
    visited: set[str] = set()
    saved = 0
    failures = 0

    while queue and saved < max_pages:
        current_url, depth = queue.popleft()
        normalized = urldefrag(current_url)[0]
        if normalized in visited or depth > max_depth:
            continue

        visited.add(normalized)

        response = None
        for _ in range(retries + 1):
            try:
                response = requests.get(normalized, timeout=timeout_seconds)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                response = None

        if response is None or response.status_code != 200:
            failures += 1
            continue

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            continue

        saved += 1
        file_path = out / f"page{saved}.html"
        file_path.write_text(response.text, encoding="utf-8", errors="ignore")

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            next_url = urldefrag(urljoin(normalized, link["href"]))[0]
            parsed = urlparse(next_url)
            if parsed.scheme not in {"http", "https"}:
                continue
            if parsed.netloc != allowed_domain:
                continue
            if next_url not in visited:
                queue.append((next_url, depth + 1))

    return {"saved_pages": saved, "visited_pages": len(visited), "failures": failures}
