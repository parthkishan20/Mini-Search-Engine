# Mini Search Engine

A compact, production-oriented Python search engine demo with offline indexing,
phrase search, TF/BM25 ranking, a small crawler, REST APIs, a CLI and a minimal
Flask UI.

## Features
- Offline index builder that produces `index_data/index.json`
- Positional inverted index with phrase query support ("exact phrase")
- Pluggable rankers: TF and BM25 (configurable `k1` and `b`)
- Shared `SearchService` used by CLI, REST API and UI
- Endpoints: search, suggestions, index stats, health, and metrics
- Minimal crawler to populate `input_pages/`
- Structured JSON logging and in-memory rate limiting

## Tech Stack
- Language: Python 3.10+
- Web: Flask
- Parsing: BeautifulSoup + requests (crawler)
- Ranking: custom TF and BM25 implementations
- Packaging: `pyproject.toml` (setuptools) and editable install
- Dev/test: `pytest`, `ruff`, `black`
- Optional: Docker / Docker Compose

## Project Structure (important parts)
- `app.py` — small Flask entrypoint wrapper for local runs
- `crawler.py` — bounded crawler that saves pages to `input_pages/`
- `src/mini_search_engine/` — main package
    - `web/app_factory.py` — creates Flask app and registers routes
    - `api/routes.py` — HTTP JSON API (`/api/v1/*`)
    - `cli/main.py` — CLI (`build-index`, `search`, `crawl`)
    - `indexing/` — `analyzer.py`, `builder.py`, `parser.py`, `serializer.py`
    - `ranking/` — `bm25.py`, `tf.py`
    - `search/` — query parsing and service layer
    - `observability/logging.py` — JSON logging + simple metrics
- `templates/`, `static/` — Flask UI assets
- `input_pages/` — sample HTML pages included for quick testing
- `pyproject.toml`, `Makefile`, `Dockerfile`, `docker-compose.yml`

## Prerequisites
- Python 3.10+ (3.11/3.13 tested in CI/local runs)
- Git (optional)
- Docker (optional, only if you want to containerize)

## Installation (local, recommended)
Clone the repo and create a virtual environment:

```bash
git clone https://github.com/parthkishan20/Mini-Search-Engine.git
cd Mini-Search-Engine
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .[dev]
```

## Environment variables
The app reads configuration from environment variables (defaults shown):

- `FLASK_SECRET_KEY` — secret for Flask sessions (`dev-only-change-me`)
- `FLASK_DEBUG` — `true`/`false` (default `false`)
- `MSE_INPUT_DIR` — input HTML dir (default `input_pages`)
- `MSE_STOPWORDS_PATH` — stopwords file (default `stopwords.txt`)
- `MSE_INDEX_PATH` — persisted index (default `index_data/index.json`)
- `MSE_DEFAULT_RANKER` — `bm25` or `tf` (default `bm25`)
- `MSE_BM25_K1`, `MSE_BM25_B` — BM25 params (defaults in `AppConfig`)
- `MSE_DEFAULT_PAGE_SIZE`, `MSE_MAX_PAGE_SIZE` — pagination

Set them in your shell or in Docker Compose environment section.

## Running (development)
Build an index from bundled pages (recommended before searching):

```bash
# build index and persist to default path
mini-search-engine build-index --input-dir input_pages --output index_data/index.json
```

Start the web UI (development):

```bash
python app.py
# or with explicit port
python -c "from mini_search_engine.web.app_factory import create_app; create_app().run(port=5001)"
```

Open http://127.0.0.1:5000 (or the port you started on).

Alternative: use the packaged CLI without editable install:

```bash
python -m mini_search_engine.cli.main search --query "your query" --index index_data/index.json
```

## Docker
Build and run with Docker Compose (maps `index_data/` as a volume):

```bash
docker compose up --build
```

Service will be available on port `5000` (see `docker-compose.yml`).

## Scripts / Makefile
- `make install` — install editable package with dev extras
- `make build-index` — runs CLI index builder
- `make run` — `python app.py`
- `make test` — runs `pytest`
- `make lint` / `make format` — run `ruff` / `black`

## How the app works (brief)
1. `mini_search_engine.indexing.builder` parses HTML files in `input_pages/`,
     tokenizes and builds a positional inverted index and document store.
2. `serializer.save_index` persists `index_data/index.json` (documents, postings,
     vocabulary, stats).
3. `SearchService` loads the index and answers queries using the selected ranker
     (TF or BM25) and supports phrase checks using positional postings.
4. UI/CLI/API call into the same `SearchService` for consistent behavior.

## Troubleshooting
- TemplateNotFound for `index.html`: ensure you run `app.py` from repo root or
    that Flask `template_folder` points to the top-level `templates/` directory.
- Port in use: if `5000` is occupied, start with `python app.py` and pass
    `create_app().run(port=5001)` or free the port with `lsof -n -iTCP:5000 -sTCP:LISTEN`.
- If searches return no results, confirm you built the index and that
    `MSE_INDEX_PATH` points to the right file.

## Tests
Run the unit test suite:

```bash
pytest
```

## Contributing
- Fork, create a topic branch, make changes and open a PR.
- Run `make test` and `make lint` before submitting.
- Keep changes small and provide tests for logic changes.

## License
This repository does not explicitly declare a license file. If you are the
maintainer, add a `LICENSE` file (MIT/Apache-2.0 are common choices). If you
intend this to be open-source, add a license before accepting community
contributions.

---
_If anything in this README conflicts with your expected setup, tell me which
part to adjust — I verified commands and paths against the repository files._
