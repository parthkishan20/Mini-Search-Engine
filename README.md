# Mini Search Engine

A production-oriented Python search engine demo with offline indexing, BM25 ranking, phrase search, REST APIs, and a Flask UI.

## Highlights

- Offline index build + persisted index artifacts (`index_data/index.json`)
- Positional inverted index with phrase query support (`"exact phrase"`)
- Pluggable rankers: TF and BM25
- Shared service layer used by CLI, API, and UI
- API endpoints for search, suggestions, health, and index stats
- Structured JSON logging, basic Prometheus-style metrics, and in-memory rate limiting
- Queue-based bounded crawler with retries/timeouts

## Architecture

```text
crawler -> input_pages/*.html -> analyzer/parser -> index builder -> persisted index
                                                           |
                                              SearchService (TF/BM25)
                                                           |
                                  CLI / Flask UI / REST API (/api/v1/*)
```

## Quick Start

### 1) Install

```bash
make install
```

### 2) Build index

```bash
make build-index
```

### 3) Run app

```bash
make run
```

Open http://localhost:5000

## CLI Usage

```bash
python -m mini_search_engine.cli.main build-index
python -m mini_search_engine.cli.main search --query "mini search engine"
python -m mini_search_engine.cli.main search --query '"search engine"' --ranker bm25
python -m mini_search_engine.cli.main crawl --seed-url https://en.wikipedia.org/ --max-pages 10
```

## API Examples

```bash
curl 'http://localhost:5000/api/v1/search?q=python&page=1&page_size=10&ranker=bm25'
curl 'http://localhost:5000/api/v1/suggest?q=py'
curl 'http://localhost:5000/api/v1/index/stats'
curl 'http://localhost:5000/health/live'
curl 'http://localhost:5000/metrics'
```

## Development

```bash
make lint
make test
```

## Configuration

Set via environment variables:

- `FLASK_SECRET_KEY`
- `FLASK_DEBUG` (default `false`)
- `MSE_INPUT_DIR` (default `input_pages`)
- `MSE_STOPWORDS_PATH` (default `stopwords.txt`)
- `MSE_INDEX_PATH` (default `index_data/index.json`)
- `MSE_DEFAULT_RANKER` (`bm25` or `tf`)
- `MSE_MAX_QUERY_LENGTH`
- `MSE_RATE_LIMIT_PER_MINUTE`

## BM25 Formula

BM25 is used as the default lexical ranker with configurable `k1` and `b`:

- `idf = log(1 + (N - df + 0.5)/(df + 0.5))`
- score sums term contributions with length normalization and field boosts.

## Docker

```bash
docker compose up --build
```

Then visit http://localhost:5000.
