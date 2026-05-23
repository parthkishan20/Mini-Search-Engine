from __future__ import annotations

import argparse
import json

from mini_search_engine.config import AppConfig
from mini_search_engine.crawl.service import crawl_site
from mini_search_engine.indexing.analyzer import Analyzer, load_stopwords
from mini_search_engine.indexing.builder import build_index
from mini_search_engine.indexing.serializer import load_index, save_index
from mini_search_engine.search.service import SearchService


def _build_index(config: AppConfig, args: argparse.Namespace) -> int:
    input_dir = args.input_dir or config.input_dir
    output_path = args.output or config.index_path
    analyzer = Analyzer(load_stopwords(config.stopwords_path))
    index_data = build_index(input_dir, analyzer)
    save_index(index_data, output_path)
    print(f"Index built at {output_path}")
    print(json.dumps({k: index_data[k] for k in ('doc_count', 'avg_doc_length', 'corpus_hash')}, indent=2))
    return 0


def _search(config: AppConfig, args: argparse.Namespace) -> int:
    analyzer = Analyzer(load_stopwords(config.stopwords_path))
    index_data = load_index(args.index or config.index_path)
    service = SearchService(index_data, analyzer, config)
    payload = service.search(args.query, page=args.page, page_size=args.page_size, ranker_name=args.ranker)
    for item in payload["results"]:
        print(f"{item['file']} (score={item['score']}) - {item['title']}")
    if not payload["results"]:
        print("No results found")
    return 0


def _crawl(args: argparse.Namespace) -> int:
    result = crawl_site(
        seed_url=args.seed_url,
        save_dir=args.save_dir,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        timeout_seconds=args.timeout,
        retries=args.retries,
    )
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mini Search Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-index", help="Build and persist index artifacts")
    build.add_argument("--input-dir", default=None)
    build.add_argument("--output", default=None)

    search = sub.add_parser("search", help="Search using persisted index")
    search.add_argument("--query", required=True)
    search.add_argument("--index", default=None)
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--page-size", type=int, default=10)
    search.add_argument("--ranker", choices=["tf", "bm25"], default=None)

    crawl = sub.add_parser("crawl", help="Run bounded crawler")
    crawl.add_argument("--seed-url", default="https://en.wikipedia.org/")
    crawl.add_argument("--save-dir", default="input_pages")
    crawl.add_argument("--max-pages", type=int, default=10)
    crawl.add_argument("--max-depth", type=int, default=2)
    crawl.add_argument("--timeout", type=int, default=10)
    crawl.add_argument("--retries", type=int, default=2)

    return parser


def main() -> int:
    config = AppConfig()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "build-index":
        return _build_index(config, args)
    if args.command == "search":
        return _search(config, args)
    if args.command == "crawl":
        return _crawl(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
