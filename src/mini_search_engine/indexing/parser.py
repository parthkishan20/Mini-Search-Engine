from __future__ import annotations

import hashlib
from pathlib import Path

from bs4 import BeautifulSoup


def parse_html_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else path.name
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    body_node = soup.body if soup.body else soup
    text = " ".join(body_node.get_text(separator=" ").split())
    checksum = hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()

    return {
        "title": title,
        "description": description,
        "text": text,
        "checksum": checksum,
        "modified_at": path.stat().st_mtime,
    }
