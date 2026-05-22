from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .analyzer import Analyzer
from .parser import parse_html_file


def _new_postings_dict():
    return defaultdict(lambda: defaultdict(list))


def _new_field_freq_dict():
    return defaultdict(lambda: defaultdict(int))


def build_index(input_dir: str, analyzer: Analyzer) -> dict:
    postings = _new_postings_dict()
    field_postings = {
        "title": _new_field_freq_dict(),
        "description": _new_field_freq_dict(),
        "body": _new_field_freq_dict(),
    }

    documents: dict[str, dict] = {}
    checksums: list[str] = []
    total_length = 0

    for file_path in sorted(Path(input_dir).glob("*.html")):
        parsed = parse_html_file(file_path)
        doc_id = file_path.name

        title_tokens = analyzer.tokenize(parsed["title"])
        description_tokens = analyzer.tokenize(parsed["description"])
        body_tokens = analyzer.tokenize(parsed["text"])

        for position, token in enumerate(body_tokens):
            postings[token][doc_id].append(position)
            field_postings["body"][token][doc_id] += 1

        for token in title_tokens:
            field_postings["title"][token][doc_id] += 1

        for token in description_tokens:
            field_postings["description"][token][doc_id] += 1

        documents[doc_id] = {
            "doc_id": doc_id,
            "path": str(file_path),
            "title": parsed["title"],
            "description": parsed["description"],
            "text": parsed["text"],
            "length": len(body_tokens),
            "modified_at": parsed["modified_at"],
            "checksum": parsed["checksum"],
        }

        checksums.append(parsed["checksum"])
        total_length += len(body_tokens)

    doc_count = len(documents)
    avg_doc_length = (total_length / doc_count) if doc_count else 0.0
    doc_freqs = {term: len(docs) for term, docs in postings.items()}

    index = {
        "schema_version": "1.0",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "input_dir": input_dir,
        "doc_count": doc_count,
        "avg_doc_length": avg_doc_length,
        "corpus_hash": hashlib.sha256("".join(sorted(checksums)).encode("utf-8")).hexdigest(),
        "documents": documents,
        "postings": {term: dict(docs) for term, docs in postings.items()},
        "field_postings": {
            field: {term: dict(docs) for term, docs in fp.items()} for field, fp in field_postings.items()
        },
        "doc_freqs": doc_freqs,
        "vocabulary": sorted(postings.keys()),
    }
    return index
