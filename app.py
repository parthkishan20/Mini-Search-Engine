from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mini_search_engine.config import AppConfig
from mini_search_engine.web.app_factory import create_app

app = create_app(AppConfig())

if __name__ == "__main__":
    config = AppConfig()
    app.run(debug=config.flask_debug)
