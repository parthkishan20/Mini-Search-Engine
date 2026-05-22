from __future__ import annotations

from .base import Ranker


class TFRanker(Ranker):
    def score(self, doc_id: str, query_terms: list[str], index_data: dict) -> float:
        score = 0.0
        postings = index_data["postings"]
        field_postings = index_data.get("field_postings", {})

        for term in query_terms:
            score += len(postings.get(term, {}).get(doc_id, []))
            score += 2.0 * field_postings.get("title", {}).get(term, {}).get(doc_id, 0)
            score += 1.3 * field_postings.get("description", {}).get(term, {}).get(doc_id, 0)
        return score
