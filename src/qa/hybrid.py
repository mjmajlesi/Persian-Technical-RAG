"""Research-only reciprocal-rank fusion; never changes the dense gate."""

from src.index.bm25 import BM25Index


def rrf_fuse(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Fuse ranked IDs; ties follow first appearance across the input rankings."""
    if k < 0:
        raise ValueError("k must be non-negative")
    scores: dict[str, float] = {}
    for ranking in rankings:
        seen = set()
        for rank, chunk_id in enumerate(ranking, 1):
            if chunk_id not in seen:
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + rank)
                seen.add(chunk_id)
    return sorted(scores.items(), key=lambda item: -item[1])


class HybridRetriever:
    """Fuse the top 20 dense and lexical candidates from a single pack."""

    def __init__(self, dense, chunks: list[dict]):
        self.dense = dense
        self.chunks = {chunk["chunk_id"]: chunk for chunk in chunks}
        self.bm25 = BM25Index(chunks)

    def retrieve(self, question: str, k: int = 5) -> list[dict]:
        dense = self.dense.retrieve(question, k=20)
        return self.fuse(question, dense, k)

    def fuse(self, question: str, dense: list[dict], k: int = 5) -> list[dict]:
        """Fuse already-retrieved dense candidates without a second encoding."""
        dense_scores = {row["chunk_id"]: row["score"] for row in dense}
        lexical = self.bm25.search(question, k=20)
        fused = rrf_fuse([[row["chunk_id"] for row in dense], [cid for cid, _ in lexical]])
        return [dict(self.chunks[cid], score=score, dense_score=dense_scores.get(cid))
                for cid, score in fused[:k]]

    def dense_top1_score(self, question: str) -> float:
        return self.dense.retrieve(question, k=1)[0]["score"]
