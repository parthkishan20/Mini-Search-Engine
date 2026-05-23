from __future__ import annotations

import math

from .base import Ranker


class BM25Ranker(Ranker):
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    def score(self, doc_id: str, query_terms: list[str], index_data: dict) -> float:
        documents = index_data["documents"]
        postings = index_data["postings"]
        doc_freqs = index_data["doc_freqs"]
        field_postings = index_data.get("field_postings", {})

        doc_count = max(index_data.get("doc_count", 0), 1)
        avg_doc_len = max(index_data.get("avg_doc_length", 0.0), 1e-9)
        doc_len = documents[doc_id]["length"]

        score = 0.0
        for term in query_terms:
            term_postings = postings.get(term, {})
            tf = len(term_postings.get(doc_id, []))
            if tf == 0:
                continue

            df = doc_freqs.get(term, 0)
            idf = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
            norm = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
            score += idf * (tf * (self.k1 + 1)) / max(norm, 1e-9)

            score += 0.7 * field_postings.get("title", {}).get(term, {}).get(doc_id, 0)
            score += 0.3 * field_postings.get("description", {}).get(term, {}).get(doc_id, 0)

        return score
