import csv
from dataclasses import dataclass
from pathlib import Path

import chromadb

from .bm25 import BM25


def _reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    k: int = 60,
) -> list[tuple[str, float]]:
    """
    Reciprocal Rank Fusion (RRF) to combine multiple ranked lists.
    score(doc_id) = sum over each list: 1 / (k + rank)
    """
    scores: dict[str, float] = {}
    for lst in ranked_lists:
        for rank, doc_id in enumerate(lst, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    rule_id: str
    domain: str
    source_file: str
    error_code: str
    historical_context: str
    severity: str
    difficulty: str
    text: str


class TheoryRetriever:
    def __init__(self, chunks_csv: Path, chroma_dir: Path) -> None:
        self.chunks: list[Chunk] = []
        with chunks_csv.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.chunks.append(
                    Chunk(
                        chunk_id=row["chunk_id"],
                        rule_id=row["rule_id"],
                        domain=row["domain"],
                        source_file=row["source_file"],
                        error_code=row["error_code"],
                        historical_context=row["historical_context"],
                        severity=row["severity"],
                        difficulty=row["difficulty"],
                        text=row["text"],
                    )
                )

        chroma_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(chroma_dir))
        self.collection = self.client.get_or_create_collection(name="theory_chunks")
        # Upsert corpus each boot for deterministic local dev behavior.
        self.collection.upsert(
            ids=[c.chunk_id for c in self.chunks],
            documents=[c.text for c in self.chunks],
            metadatas=[
                {
                    "rule_id": c.rule_id,
                    "domain": c.domain,
                    "source_file": c.source_file,
                    "error_code": c.error_code,
                    "historical_context": c.historical_context,
                    "severity": c.severity,
                    "difficulty": c.difficulty,
                }
                for c in self.chunks
            ],
        )
        # BM25 index for fusion retrieval (vector + keyword)
        self._bm25 = BM25()
        self._bm25.fit([c.text for c in self.chunks])
        self._chunk_id_by_idx = [c.chunk_id for c in self.chunks]

    def search(
        self,
        query: str,
        *,
        top_k: int = 3,
        domain: str | None = None,
        error_code: str | None = None,
        use_fusion: bool = True,
    ) -> list[dict]:
        """
        Retrieve theory chunks. When use_fusion=True (default), combines
        vector (ChromaDB) and keyword (BM25) search via Reciprocal Rank Fusion.
        """
        clauses = []
        if domain:
            clauses.append({"domain": domain})
        if error_code:
            clauses.append({"error_code": error_code})
        # Fetch more for fusion; we'll trim to top_k after RRF
        fetch_k = max(top_k * 3, 15) if use_fusion else top_k
        kwargs = {"query_texts": [query], "n_results": min(fetch_k, len(self.chunks))}
        if len(clauses) == 1:
            kwargs["where"] = clauses[0]
        elif len(clauses) > 1:
            kwargs["where"] = {"$and": clauses}
        results = self.collection.query(**kwargs)
        vector_ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if use_fusion and self._chunk_id_by_idx:
            bm25_hits = self._bm25.topk(query, k=min(fetch_k, len(self.chunks)))
            bm25_ids = [self._chunk_id_by_idx[idx] for idx, _ in bm25_hits]
            fused = _reciprocal_rank_fusion([list(vector_ids), bm25_ids], k=60)
            seen = set()
            order_ids = []
            for cid, _ in fused:
                if cid not in seen:
                    seen.add(cid)
                    order_ids.append(cid)
            # Build id_to_data from vector results (may need to include bm25-only hits)
            id_to_doc = dict(zip(vector_ids, docs)) if docs else {}
            id_to_meta = {}
            for i, cid in enumerate(vector_ids):
                m = metas[i] if i < len(metas) and metas[i] is not None else {}
                id_to_meta[cid] = m
            for c in self.chunks:
                if c.chunk_id not in id_to_meta:
                    id_to_meta[c.chunk_id] = {
                        "rule_id": c.rule_id, "domain": c.domain, "source_file": c.source_file,
                        "error_code": c.error_code, "historical_context": c.historical_context,
                        "severity": c.severity, "difficulty": c.difficulty,
                    }
                    id_to_doc[c.chunk_id] = c.text
            # Apply metadata filters to fused results
            def _matches(cid: str) -> bool:
                m = id_to_meta.get(cid, {})
                if domain and m.get("domain") != domain:
                    return False
                if error_code and m.get("error_code") != error_code:
                    return False
                return True
            filtered = [cid for cid in order_ids if _matches(cid)]
            out = []
            for cid in filtered[:top_k]:
                m = id_to_meta.get(cid, {})
                out.append({
                    "chunk_id": cid,
                    "rule_id": m.get("rule_id", ""),
                    "domain": m.get("domain", ""),
                    "source_file": m.get("source_file", ""),
                    "error_code": m.get("error_code", ""),
                    "historical_context": m.get("historical_context", ""),
                    "severity": m.get("severity", ""),
                    "difficulty": m.get("difficulty", ""),
                    "score": 0.0,
                    "text": id_to_doc.get(cid, ""),
                })
            return out

        out = []
        for i in range(len(vector_ids)):
            m = metas[i] if i < len(metas) and metas[i] is not None else {}
            out.append({
                "chunk_id": vector_ids[i],
                "rule_id": m.get("rule_id", ""),
                "domain": m.get("domain", ""),
                "source_file": m.get("source_file", ""),
                "error_code": m.get("error_code", ""),
                "historical_context": m.get("historical_context", ""),
                "severity": m.get("severity", ""),
                "difficulty": m.get("difficulty", ""),
                "score": float(distances[i]) if i < len(distances) else 0.0,
                "text": docs[i] if i < len(docs) else "",
            })
        return out[:top_k]

