from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def load_stopwords(filepath: str) -> set[str]:
    with open(filepath, "r", encoding="utf-8") as file:
        return {word.strip().lower() for word in file if word.strip()}


@dataclass
class Analyzer:
    stopwords: set[str]

    def tokenize(self, text: str) -> list[str]:
        words = TOKEN_RE.findall(text.lower())
        return [word for word in words if word not in self.stopwords]
