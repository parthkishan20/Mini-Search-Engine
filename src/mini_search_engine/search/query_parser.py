from __future__ import annotations

import re
from dataclasses import dataclass

from mini_search_engine.indexing.analyzer import Analyzer

PHRASE_RE = re.compile(r'"([^"]+)"')


@dataclass
class ParsedQuery:
    raw: str
    terms: list[str]
    phrases: list[list[str]]


class QueryValidationError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def parse_query(query: str, analyzer: Analyzer, max_query_length: int) -> ParsedQuery:
    query = query.strip()
    if not query:
        raise QueryValidationError("empty_query")
    if len(query) > max_query_length:
        raise QueryValidationError("query_too_long")

    phrase_strings = PHRASE_RE.findall(query)
    phrases = [analyzer.tokenize(phrase) for phrase in phrase_strings if phrase.strip()]

    query_wo_phrases = PHRASE_RE.sub(" ", query)
    terms = analyzer.tokenize(query_wo_phrases)

    if not terms and not phrases:
        raise QueryValidationError("no_searchable_terms")

    return ParsedQuery(raw=query, terms=terms, phrases=[p for p in phrases if p])
