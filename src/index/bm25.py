"""In-memory Okapi BM25 over canonical chunk records, with no dependencies."""

from collections import Counter
import math
import re
import unicodedata

_TOKEN = re.compile(r"[A-Za-z0-9_]+|[\u0600-\u06FF]+")
_ARABIC = str.maketrans({"ي": "ی", "ك": "ک", "\u200c": " "})


def tokenize(text: str) -> list[str]:
    """Normalize Arabic/Persian forms; ``std::vector`` becomes two tokens."""
    return _TOKEN.findall(unicodedata.normalize("NFKC", text).translate(_ARABIC).lower())


class BM25Index:
    """BM25 over records in canonical order; equal scores preserve that order."""

    def __init__(self, chunks: list[dict], k1: float = 1.5, b: float = 0.75):
        self.ids = [chunk["chunk_id"] for chunk in chunks]
        if len(set(self.ids)) != len(self.ids):
            raise ValueError("duplicate chunk IDs")
        self.k1, self.b = k1, b
        self.documents = [Counter(tokenize(chunk["text"])) for chunk in chunks]
        self.lengths = [sum(doc.values()) for doc in self.documents]
        self.average = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        df = Counter(token for doc in self.documents for token in doc)
        n = len(self.documents)
        self.idf = {token: math.log(1 + (n - count + 0.5) / (count + 0.5))
                    for token, count in df.items()}

    def search(self, question: str, k: int) -> list[tuple[str, float]]:
        if k < 0:
            raise ValueError("k must be non-negative")
        tokens = sorted(set(tokenize(question)))
        scores = []
        for doc, length in zip(self.documents, self.lengths):
            norm = self.k1 * (1 - self.b + self.b * length / self.average) if self.average else 0
            score = sum(self.idf[t] * doc[t] * (self.k1 + 1) / (doc[t] + norm)
                        for t in tokens if doc[t])
            scores.append(score)
        order = sorted(range(len(self.ids)), key=lambda i: (-scores[i], i))
        return [(self.ids[i], scores[i]) for i in order[:k]]
