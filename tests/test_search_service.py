from pathlib import Path

from mini_search_engine.config import AppConfig
from mini_search_engine.indexing.analyzer import Analyzer
from mini_search_engine.indexing.builder import build_index
from mini_search_engine.search.service import SearchService


def test_phrase_query_filters_results(tmp_path: Path):
    (tmp_path / "doc1.html").write_text("<html><body>mini search engine demo</body></html>", encoding="utf-8")
    (tmp_path / "doc2.html").write_text("<html><body>mini demo search engine</body></html>", encoding="utf-8")

    analyzer = Analyzer(stopwords=set())
    index_data = build_index(str(tmp_path), analyzer)
    service = SearchService(index_data=index_data, analyzer=analyzer, config=AppConfig())

    payload = service.search('"search engine"')

    files = [result["file"] for result in payload["results"]]
    assert "doc1.html" in files
    assert "doc2.html" in files

    phrase_payload = service.search('"mini search engine"')
    phrase_files = [result["file"] for result in phrase_payload["results"]]
    assert phrase_files == ["doc1.html"]
