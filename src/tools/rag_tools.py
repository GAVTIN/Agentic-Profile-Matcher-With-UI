"""
Milestone 2: RAG search tool.

Two interchangeable index backends behind one `search_resumes` tool:

  _EmbeddingIndex  (live mode) - local HuggingFace sentence-transformers
                    embeddings + a persisted Chroma vector store. Real
                    semantic search: "frontend engineer comfortable owning
                    features end to end" will match resumes that never use
                    those exact words.

  _TfidfIndex       (mock mode) - scikit-learn TF-IDF + cosine similarity.
                    Zero network calls, builds in under a second for 100
                    resumes. Keyword-driven rather than semantic, but a
                    perfectly legitimate first-pass filter (plenty of real
                    ATS systems do exactly this) and it's what lets this
                    whole project run with no API key.

Both return the same SearchHit shape, so nothing downstream needs to know
which one answered the query.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from langchain_core.tools import tool

from .. import config
from .filesystem_tools import load_candidate_metadata


@dataclass
class SearchHit:
    candidate_id: str
    name: str
    score: float  # roughly 0-1, higher = better match (scale differs slightly by backend)
    snippet: str


def _load_all_resumes() -> tuple[list[str], list[str]]:
    ids, texts = [], []
    for path in sorted(config.RESUME_DIR.glob("CAND-*.txt")):
        ids.append(path.stem)
        texts.append(path.read_text(encoding="utf-8"))
    return ids, texts


class _TfidfIndex:
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._ids, self._texts = _load_all_resumes()
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform(self._texts)
        self._meta = load_candidate_metadata()

    def search(self, query: str, k: int) -> list[SearchHit]:
        from sklearn.metrics.pairwise import cosine_similarity

        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:k]
        hits = []
        for i in ranked:
            cid = self._ids[i]
            name = self._meta.get(cid, {}).get("name", cid)
            hits.append(SearchHit(candidate_id=cid, name=name, score=float(sims[i]), snippet=self._texts[i][:300]))
        return hits


class _EmbeddingIndex:
    def __init__(self):
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        from .. import llm as llm_module

        embeddings = llm_module.get_embeddings()
        ids, texts = _load_all_resumes()
        meta = load_candidate_metadata()
        docs = [
            Document(
                page_content=text,
                metadata={"candidate_id": cid, "name": meta.get(cid, {}).get("name", cid)},
            )
            for cid, text in zip(ids, texts)
        ]
        self._store = Chroma.from_documents(
            docs,
            embeddings,
            collection_name="resumes",
            persist_directory=str(config.VECTOR_STORE_DIR),
        )

    def search(self, query: str, k: int) -> list[SearchHit]:
        results = self._store.similarity_search_with_relevance_scores(query, k=k)
        hits = []
        for doc, score in results:
            hits.append(
                SearchHit(
                    candidate_id=doc.metadata["candidate_id"],
                    name=doc.metadata.get("name", doc.metadata["candidate_id"]),
                    score=float(score),
                    snippet=doc.page_content[:300],
                )
            )
        return hits


@lru_cache(maxsize=1)
def _get_index():
    if config.MODE == "live":
        return _EmbeddingIndex()
    return _TfidfIndex()


def reset_index_cache() -> None:
    """Call after changing config.MODE at runtime (mainly useful in tests)."""
    _get_index.cache_clear()


@tool
def search_resumes(query: str, k: int = 10) -> list[dict]:
    """Search the resume corpus and return the top-k most relevant candidates.

    Give it a natural-language description of what you're looking for, e.g.
    "senior React TypeScript engineer with fintech experience" - it returns
    each match's candidate_id, name, a similarity score, and a text snippet.
    """
    hits = _get_index().search(query, k=k)
    return [
        {"candidate_id": h.candidate_id, "name": h.name, "score": round(h.score, 4), "snippet": h.snippet}
        for h in hits
    ]


RAG_TOOLS = [search_resumes]
