from mini_search_engine.ranking.bm25 import BM25Ranker


def test_bm25_scores_docs_deterministically():
    index_data = {
        "documents": {"a.html": {"length": 4}, "b.html": {"length": 10}},
        "postings": {"python": {"a.html": [0, 2], "b.html": [1]}},
        "doc_freqs": {"python": 2},
        "doc_count": 2,
        "avg_doc_length": 7,
        "field_postings": {"title": {}, "description": {}},
    }

    ranker = BM25Ranker(k1=1.5, b=0.75)
    score_a = ranker.score("a.html", ["python"], index_data)
    score_b = ranker.score("b.html", ["python"], index_data)

    assert score_a > score_b
