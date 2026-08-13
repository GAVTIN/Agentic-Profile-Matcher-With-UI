"""
Round 1 scoring: turns RAG search hits into a scored, explained shortlist.

This is deterministic pipeline logic, not an LLM tool - it's what the "Rank
Candidates" graph node calls. It's intentionally mode-independent: running an
LLM judgment over all 100 resumes for a first-pass filter would be slow and
wasteful even on fast Groq inference, so BOTH live and mock mode use this
same keyword/years scorer for round 1. Where they differ is what happens
next - round 2 (deep analysis) is where live mode's LLM reasoning kicks in,
on just the round-1 survivors instead of the full pool. That mirrors how
real retrieval-then-rerank pipelines are usually built.

Score = 50% must-have coverage + 20% nice-to-have coverage
      + 15% years-experience fit + 15% RAG semantic/keyword similarity
"""

from __future__ import annotations

import re

from .tools.screening_tools import skill_mentioned

MUST_WEIGHT = 50
NICE_WEIGHT = 20
YEARS_WEIGHT = 15
RAG_WEIGHT = 15

_YEARS_RE = re.compile(r"(\d+)\s*years?\s*experience", re.IGNORECASE)


def _extract_years(resume_text: str) -> int:
    m = _YEARS_RE.search(resume_text)
    return int(m.group(1)) if m else 0


def score_candidate(candidate_id: str, name: str, resume_text: str, requirements: dict,
                     rag_score: float = 0.0) -> dict:
    """Score one candidate's resume text against structured requirements.
    rag_score is the raw similarity score from search_resumes (0-1 scale,
    already roughly normalized by both index backends)."""
    must = requirements.get("must_have", []) or []
    nice = requirements.get("nice_to_have", []) or []
    min_years = requirements.get("min_years_experience", 0) or 0

    text_lower = resume_text.lower()
    # skill_mentioned does substring checks; wrapping the whole resume text as a
    # single-element set reuses the same helper used elsewhere for per-skill sets.
    matched_must = [s for s in must if skill_mentioned(s, {text_lower})]
    missing_must = [s for s in must if s not in matched_must]
    matched_nice = [s for s in nice if skill_mentioned(s, {text_lower})]

    must_score = (len(matched_must) / len(must)) * MUST_WEIGHT if must else MUST_WEIGHT
    nice_score = (len(matched_nice) / len(nice)) * NICE_WEIGHT if nice else NICE_WEIGHT

    years = _extract_years(resume_text)
    if min_years > 0:
        years_score = min(years / min_years, 1.0) * YEARS_WEIGHT
    else:
        years_score = YEARS_WEIGHT

    rag_score_clamped = max(0.0, min(rag_score, 1.0))
    rag_component = rag_score_clamped * RAG_WEIGHT

    total = round(must_score + nice_score + years_score + rag_component, 1)
    total = min(total, 100.0)

    rationale = _build_rationale(matched_must, missing_must, matched_nice, years, min_years, len(must))

    return {
        "candidate_id": candidate_id,
        "name": name,
        "score": total,
        "matched_must_have": matched_must,
        "missing_must_have": missing_must,
        "matched_nice_to_have": matched_nice,
        "years_experience": years,
        "rationale": rationale,
    }


def _build_rationale(matched_must: list[str], missing_must: list[str], matched_nice: list[str],
                      years: int, min_years: int, total_must: int) -> str:
    parts = []
    if total_must:
        parts.append(f"matches {len(matched_must)}/{total_must} must-have requirement(s)"
                     + (f" ({', '.join(matched_must[:4])})" if matched_must else ""))
    if missing_must:
        parts.append(f"missing {', '.join(missing_must[:3])}")
    if matched_nice:
        parts.append(f"also brings {len(matched_nice)} nice-to-have(s): {', '.join(matched_nice[:3])}")
    if min_years:
        cmp = "meets" if years >= min_years else "is below"
        parts.append(f"{years} yrs experience {cmp} the {min_years}+ yr bar")
    return "; ".join(parts) if parts else "General match based on resume content."


def rank_candidates(search_hits: list[dict], resume_texts: dict[str, str], requirements: dict,
                     top_n: int = 10) -> list[dict]:
    """search_hits: output of search_resumes (candidate_id, name, score, snippet).
    resume_texts: candidate_id -> full resume text (for accurate skill matching -
    the RAG snippet alone is too short to check every requirement against).
    Returns the top_n candidates sorted by score, descending."""
    scored = []
    for hit in search_hits:
        cid = hit["candidate_id"]
        text = resume_texts.get(cid, hit.get("snippet", ""))
        scored.append(score_candidate(cid, hit["name"], text, requirements, rag_score=hit.get("score", 0.0)))
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:top_n]
