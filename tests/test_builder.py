from pathlib import Path

from mini_search_engine.indexing.analyzer import Analyzer
from mini_search_engine.indexing.builder import build_index


def test_build_index_tracks_positions_and_docs(tmp_path: Path):
    html = "<html><head><title>Mini Search</title></head><body>mini search engine mini</body></html>"
    (tmp_path / "doc1.html").write_text(html, encoding="utf-8")
    analyzer = Analyzer(stopwords=set())

    index_data = build_index(str(tmp_path), analyzer)

    assert index_data["doc_count"] == 1
    assert index_data["postings"]["mini"]["doc1.html"] == [0, 3]
    assert index_data["field_postings"]["title"]["mini"]["doc1.html"] == 1
