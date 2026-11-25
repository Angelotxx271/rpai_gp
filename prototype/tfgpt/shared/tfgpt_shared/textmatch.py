"""Code, not AI, decides whether a quote is really in a text (the source check)."""
import re
import unicodedata

_QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
                         "–": "-", "—": "-", "‐": "-", "‑": "-", " ": " ", "•": " "})
_ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\]|\[…\])\s*")
MIN_PART = 6  # characters: shorter quotes match almost anywhere and prove nothing


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(_QUOTES).lower()
    text = re.sub(r"[*_`#>]+", " ", text)  # Markdown marks a model may keep or drop
    return re.sub(r"\s+", " ", text).strip()


def strip_wrapping(quote: str) -> str:
    return quote.strip().strip('"\'“”‘’').strip()


def find(quote: str | None, text: str) -> bool:
    """True when every part of the quote (split at ellipses) appears in the text, in order."""
    if not quote:
        return False
    parts = [normalise(p) for p in _ELLIPSIS.split(strip_wrapping(quote))]
    parts = [p.strip(" .,;:") for p in parts if p.strip(" .,;:")]
    if not parts or sum(len(p) for p in parts) < MIN_PART:
        return False
    haystack, pos = normalise(text), 0
    for part in parts:
        i = haystack.find(part, pos)
        if i < 0:
            return False
        pos = i + len(part)
    return True


def overlaps(a: str | None, b: str | None, min_chars: int = 12) -> bool:
    """True when two passages share a run of at least min_chars characters (used by the evaluation)."""
    if not a or not b:
        return False
    a, b = normalise(strip_wrapping(a)), normalise(strip_wrapping(b))
    if a in b or b in a:
        return True
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    n = min(min_chars, len(short))
    return any(short[i:i + n] in long_ for i in range(0, len(short) - n + 1))


def words(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))
