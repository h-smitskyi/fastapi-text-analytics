"""
Core text-analysis service — pure algorithmic implementations.

Design Principles
-----------------
* **No external NLP libraries** — every operation uses raw Python data
  structures so that algorithmic fluency is front-and-centre.
* **Hash-map frequency counting** — ``collections.Counter`` gives O(1)
  amortised look-ups → overall O(N) pass to build the frequency table.
* **Min-Heap Top-K extraction** — ``heapq.nlargest`` runs in O(N log K)
  which is strictly better than a full O(N log N) sort when K ≪ N.
* **CPU-bound safety** — the public coroutine delegates to
  ``asyncio.to_thread`` so the event loop is never blocked.
"""

from __future__ import annotations

import asyncio
import heapq
import re
import string
from collections import Counter
from functools import lru_cache
from typing import Any

from app.models.schemas import TextAnalysisResponse, TextMetrics, WordFrequency


# ---- stop words (frozen at import time for O(1) membership tests) ----------

@lru_cache(maxsize=1)
def _stop_words() -> frozenset[str]:
    """Return an immutable set of common English stop words.

    Using ``frozenset`` ensures O(1) membership checks and guarantees
    that the set is allocated exactly once across the process lifetime.
    """
    return frozenset({
        "a", "about", "above", "after", "again", "against", "all", "am",
        "an", "and", "any", "are", "aren't", "as", "at", "be", "because",
        "been", "before", "being", "below", "between", "both", "but", "by",
        "can", "can't", "cannot", "could", "couldn't", "did", "didn't",
        "do", "does", "doesn't", "doing", "don't", "down", "during",
        "each", "few", "for", "from", "further", "get", "got", "had",
        "hadn't", "has", "hasn't", "have", "haven't", "having", "he",
        "he'd", "he'll", "he's", "her", "here", "here's", "hers",
        "herself", "him", "himself", "his", "how", "how's", "i", "i'd",
        "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
        "it's", "its", "itself", "just", "let's", "me", "might", "more",
        "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
        "off", "on", "once", "only", "or", "other", "ought", "our",
        "ours", "ourselves", "out", "over", "own", "same", "shan't",
        "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
        "some", "such", "than", "that", "that's", "the", "their",
        "theirs", "them", "themselves", "then", "there", "there's",
        "these", "they", "they'd", "they'll", "they're", "they've",
        "this", "those", "through", "to", "too", "under", "until", "up",
        "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
        "we've", "were", "weren't", "what", "what's", "when", "when's",
        "where", "where's", "which", "while", "who", "who's", "whom",
        "why", "why's", "will", "with", "won't", "would", "wouldn't",
        "you", "you'd", "you'll", "you're", "you've", "your", "yours",
        "yourself", "yourselves",
    })


# ---- translation table (built once) ----------------------------------------

_PUNCT_TABLE: dict[int, None] = str.maketrans("", "", string.punctuation)

# Pre-compiled sentence-boundary regex
_SENTENCE_RE = re.compile(r"[.!?]+")


# ---- internal helpers -------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace.

    Complexity: O(N) where N = len(text).
    """
    return text.lower().translate(_PUNCT_TABLE).split()


def _compute_frequencies(tokens: list[str]) -> Counter[str]:
    """Build a frequency table using ``collections.Counter``.

    Each insertion / lookup is O(1) amortised (hash-map), so the full
    pass is O(N).  Stop words are filtered in a single generator pass.
    """
    stops = _stop_words()
    return Counter(tok for tok in tokens if tok not in stops and len(tok) > 1)


def _top_n_words(frequencies: Counter[str], n: int) -> list[WordFrequency]:
    """Extract the *n* most common words via a min-heap.

    ``heapq.nlargest`` is backed by a heap of size *K* that scans the
    full frequency map once.  This gives **O(N log K)** — strictly
    better than a full sort when K ≪ N.
    """
    top = heapq.nlargest(n, frequencies.items(), key=lambda item: item[1])
    return [WordFrequency(word=word, count=count) for word, count in top]


def _compute_metrics(text: str, tokens: list[str]) -> TextMetrics:
    """Derive basic text metrics in a single pass.

    * **character_count** — ``len(text)`` is O(1) in CPython.
    * **sentence_count** — regex split on sentence-ending punctuation.
    * **average_word_length** — sum of token lengths / count.
    """
    word_count = len(tokens)
    total_chars = sum(len(t) for t in tokens) if word_count else 0
    avg_length = round(total_chars / word_count, 2) if word_count else 0.0

    # Sentence count: split on one or more sentence-ending marks, then
    # subtract 1 if the text does not end with punctuation (trailing empty).
    sentences = _SENTENCE_RE.split(text.strip())
    sentence_count = max(len([s for s in sentences if s.strip()]), 1)

    return TextMetrics(
        character_count=len(text),
        word_count=word_count,
        sentence_count=sentence_count,
        average_word_length=avg_length,
    )


# ---- public API -------------------------------------------------------------

def _analyze_sync(text: str, top_n: int) -> dict[str, Any]:
    """Synchronous analysis — run inside a thread to keep the loop free."""
    tokens = _tokenize(text)
    frequencies = _compute_frequencies(tokens)
    top_words = _top_n_words(frequencies, top_n)
    metrics = _compute_metrics(text, tokens)

    return TextAnalysisResponse(
        metrics=metrics,
        top_words=top_words,
        word_frequencies=dict(frequencies),
    )


async def analyze_text(text: str, top_n: int = 10) -> TextAnalysisResponse:
    """Analyse *text* asynchronously.

    The CPU-bound work is delegated to a thread-pool via
    ``asyncio.to_thread`` so the FastAPI event loop remains responsive
    under concurrent requests.
    """
    return await asyncio.to_thread(_analyze_sync, text, top_n)
