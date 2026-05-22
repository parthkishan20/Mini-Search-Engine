from __future__ import annotations

import re
from markupsafe import escape


def highlight_text_safe(text: str, terms: list[str]) -> str:
    highlighted = str(escape(text))
    unique_terms = sorted({t for t in terms if t}, key=len, reverse=True)
    for term in unique_terms:
        pattern = re.compile(rf"\b({re.escape(term)})\b", re.IGNORECASE)
        highlighted = pattern.sub(r"<mark>\1</mark>", highlighted)
    return highlighted


def build_snippet(text: str, terms: list[str], window: int = 10) -> str:
    words = text.split()
    if not words:
        return ""

    lower_terms = {t.lower() for t in terms}
    match_index = 0
    for i, word in enumerate(words):
        if re.sub(r"[^a-zA-Z0-9]", "", word.lower()) in lower_terms:
            match_index = i
            break

    start = max(match_index - window, 0)
    end = min(match_index + window, len(words))
    snippet = " ".join(words[start:end])
    if end < len(words):
        snippet += " ..."
    return snippet
