.PHONY: install lint test run build-index crawl

install:
pip install -e .[dev]

lint:
ruff check .

format:
black .

test:
pytest

run:
python app.py

build-index:
python -m mini_search_engine.cli.main build-index

crawl:
python crawler.py
