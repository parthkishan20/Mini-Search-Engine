from __future__ import annotations

from abc import ABC, abstractmethod


class Ranker(ABC):
    @abstractmethod
    def score(self, doc_id: str, query_terms: list[str], index_data: dict) -> float:
        raise NotImplementedError
