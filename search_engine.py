"""CLI entrypoint wrapper."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mini_search_engine.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
