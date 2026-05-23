from __future__ import annotations

import json
from pathlib import Path


def save_index(index_data: dict, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index_data, ensure_ascii=False), encoding="utf-8")


def load_index(index_path: str) -> dict:
    path = Path(index_path)
    return json.loads(path.read_text(encoding="utf-8"))
