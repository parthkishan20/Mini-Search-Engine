from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass

from mini_search_engine.config import AppConfig
from mini_search_engine.indexing.analyzer import Analyzer
from mini_search_engine.ranking.bm25 import BM25Ranker
from mini_search_engine.ranking.tf import TFRanker
from mini_search_engine.search.query_parser import parse_query
from mini_search_engine.search.snippets import build_snippet, highlight_text_safe


class IndexNotLoadedError(RuntimeError):
    pass


@dataclass
class SearchResult:
    title: str
    score: float
    snippet: str
    file: str


class SearchService:
    def __init__(self, index_data: dict, analyzer: Analyzer, config: AppConfig) -> None:
        self.index_data = index_data
        self.analyzer = analyzer
        self.config = config
        self.rankers = {
            "tf": TFRanker(),
            "bm25": BM25Ranker(k1=config.bm25_k1, b=config.bm25_b),
        }
        self._cache: OrderedDict[tuple, dict] = OrderedDict()
        self._cache_size = 256

    def is_ready(self) -> bool:
        return bool(self.index_data and self.index_data.get("doc_count", 0) >= 0)

    def index_stats(self) -> dict:
        if not self.index_data:
            raise IndexNotLoadedError("Index not loaded")
        return {
            "schema_version": self.index_data.get("schema_version"),
            "built_at": self.index_data.get("built_at"),
            "doc_count": self.index_data.get("doc_count"),
            "avg_doc_length": self.index_data.get("avg_doc_length"),
            "corpus_hash": self.index_data.get("corpus_hash"),
            "vocabulary_size": len(self.index_data.get("vocabulary", [])),
        }

    def suggest(self, prefix: str, limit: int = 10) -> list[str]:
        token = "".join(ch for ch in prefix.lower().strip() if ch.isalnum())
        if not token:
            return []
        return [term for term in self.index_data.get("vocabulary", []) if term.startswith(token)][:limit]

    def _phrase_matches_doc(self, doc_id: str, phrase_tokens: list[str]) -> bool:
        if not phrase_tokens:
            return False
        postings = self.index_data["postings"]
        base = postings.get(phrase_tokens[0], {}).get(doc_id, [])
        if not base:
            return False

        for position in base:
            ok = True
            for offset, token in enumerate(phrase_tokens[1:], start=1):
                if (position + offset) not in postings.get(token, {}).get(doc_id, []):
                    ok = False
                    break
            if ok:
                return True
        return False

    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int | None = None,
        ranker_name: str | None = None,
    ) -> dict:
        if not self.index_data:
            raise IndexNotLoadedError("Index not loaded")

        page_size = page_size or self.config.default_page_size
        page_size = min(max(page_size, 1), self.config.max_page_size)
        page = max(page, 1)

        parsed = parse_query(query, self.analyzer, self.config.max_query_length)
        query_terms = parsed.terms + [token for phrase in parsed.phrases for token in phrase]
        ranker = self.rankers.get((ranker_name or self.config.default_ranker).lower(), self.rankers["bm25"])

        cache_key = (tuple(sorted(query_terms)), tuple(tuple(p) for p in parsed.phrases), page, page_size, ranker_name)
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            cached = dict(self._cache[cache_key])
            cached["cache_hit"] = True
            return cached

        start = time.perf_counter()
        postings = self.index_data["postings"]
        candidate_docs = set()

        for term in query_terms:
            candidate_docs.update(postings.get(term, {}).keys())

        if parsed.phrases:
            candidate_docs = {
                doc_id
                for doc_id in candidate_docs
                if all(self._phrase_matches_doc(doc_id, phrase) for phrase in parsed.phrases)
            }

        scored = []
        for doc_id in candidate_docs:
            score = ranker.score(doc_id, query_terms, self.index_data)
            score += 1.5 * sum(
                1 for phrase in parsed.phrases if self._phrase_matches_doc(doc_id, phrase)
            )
            if score > 0:
                scored.append((doc_id, score))

        scored.sort(key=lambda item: item[1], reverse=True)

        total = len(scored)
        start_offset = (page - 1) * page_size
        end_offset = start_offset + page_size
        paged = scored[start_offset:end_offset]

        terms_for_highlight = list(dict.fromkeys(query_terms))
        results = []
        for doc_id, score in paged:
            doc = self.index_data["documents"][doc_id]
            snippet = build_snippet(doc.get("text", ""), terms_for_highlight)
            results.append(
                SearchResult(
                    title=highlight_text_safe(doc.get("title", doc_id), terms_for_highlight),
                    score=round(score, 5),
                    snippet=highlight_text_safe(snippet, terms_for_highlight),
                    file=doc_id,
                )
            )

        payload = {
            "query": query,
            "results": [result.__dict__ for result in results],
            "total": total,
            "page": page,
            "page_size": page_size,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
            "cache_hit": False,
            "ranker": ranker_name or self.config.default_ranker,
        }

        self._cache[cache_key] = payload
        self._cache.move_to_end(cache_key)
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

        return payload
