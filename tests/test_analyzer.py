from mini_search_engine.indexing.analyzer import Analyzer


def test_tokenize_removes_stopwords_and_normalizes():
    analyzer = Analyzer(stopwords={"the", "and"})
    tokens = analyzer.tokenize("The quick, brown fox and 123 jumps")
    assert tokens == ["quick", "brown", "fox", "123", "jumps"]
