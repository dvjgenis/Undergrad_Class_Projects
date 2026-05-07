import math
import re
from collections import Counter, defaultdict


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lens = []
        self.avgdl = 0.0
        self.df = defaultdict(int)
        self.idf = {}

    @staticmethod
    def tokenize(text: str) -> list[str]:
        clean = re.sub(r"[^\w\s]", " ", (text or "").lower())
        return [w for w in clean.split() if len(w) > 2]

    def fit(self, documents: list[str]) -> None:
        self.corpus = [self.tokenize(doc) for doc in documents]
        if not self.corpus:
            self.doc_lens = []
            self.avgdl = 0.0
            self.df.clear()
            self.idf.clear()
            return
        self.doc_lens = [len(d) for d in self.corpus]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens)

        self.df.clear()
        for doc in self.corpus:
            for token in set(doc):
                self.df[token] += 1

        n_docs = len(self.corpus)
        self.idf = {
            token: math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            for token, freq in self.df.items()
        }

    def score(self, query: str, idx: int) -> float:
        if not self.corpus or idx >= len(self.corpus):
            return 0.0
        tokens = self.tokenize(query)
        if not tokens:
            return 0.0
        doc = self.corpus[idx]
        tf = Counter(doc)
        dl = self.doc_lens[idx]
        score = 0.0
        for t in tokens:
            if t not in tf:
                continue
            idf = self.idf.get(t, 0.0)
            numer = tf[t] * (self.k1 + 1.0)
            denom = tf[t] + self.k1 * (1.0 - self.b + self.b * (dl / max(self.avgdl, 1e-9)))
            score += idf * (numer / denom)
        return score

    def topk(self, query: str, k: int = 5) -> list[tuple[int, float]]:
        scored = [(i, self.score(query, i)) for i in range(len(self.corpus))]
        scored = [x for x in scored if x[1] > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

