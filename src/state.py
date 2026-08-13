"""
Agent state schema.

This is Part A.1 of the assignment: a single AgentState that tracks
(1) conversation history, (2) job-requirements understanding, and
(3) the candidate shortlist + reasoning, plus enough control-flow fields
to support multi-round screening and iterative refinement.

LangGraph merges a node's *returned* dict into this state after every
step. `messages` uses the `add_messages` reducer (append with de-dup by
message id); every other field is replace-on-write, which is what we want
for things like "shortlist" - a re-rank should replace it, not append to it.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Requirements(TypedDict):
    """Structured understanding of the job description (Part A tool: extract_requirements)."""
    role_title: str
    must_have: list[str]
    nice_to_have: list[str]
    min_years_experience: int
    seniority: str


class CandidateMatch(TypedDict):
    """One entry in the shortlist - a candidate plus the *reasoning* for their rank."""
    candidate_id: str
    name: str
    score: float                       # 0-100
    matched_must_have: list[str]
    missing_must_have: list[str]
    matched_nice_to_have: list[str]
    rationale: str                     # human-readable "why this rank"


class DeepAnalysis(TypedDict):
    """Round 2 output: a fuller per-candidate breakdown (Part C.2 explainability)."""
    candidate_id: str
    strengths: list[str]
    gaps: list[str]
    improvement_suggestions: list[str]  # populated for borderline candidates
    verdict: Literal["Strong match", "Borderline", "Not a fit"]


class HireRecommendation(TypedDict):
    """Round 3 output."""
    candidate_id: str
    decision: Literal["Hire", "Hire with reservations", "No Hire"]
    reasoning: str


class AgentState(TypedDict):
    # ---- conversation history --------------------------------------------------
    messages: Annotated[list[BaseMessage], add_messages]

    # ---- job requirements understanding ----------------------------------------
    job_description_raw: str
    requirements: Requirements | None
    previous_requirements: Requirements | None   # set on refinement, used to explain deltas

    # ---- candidate pipeline (multi-round screening, Part C.1) -------------------
    round: int                          # 1 = initial screen, 2 = deep analysis, 3 = hire/no-hire
    pool_size: int                       # resumes considered in round 1 (e.g. 100)
    search_results: list[dict]           # raw RAG hits before ranking (round 1 input)
    shortlist: list[CandidateMatch]      # round 1 output: top-N ranked candidates + reasoning
    previous_shortlist: list[CandidateMatch]  # set on re-rank, used to explain rank changes
    deep_analysis: dict[str, DeepAnalysis]        # round 2: candidate_id -> analysis
    hire_recommendations: dict[str, HireRecommendation]  # round 3: candidate_id -> decision

    # ---- explainability / output --------------------------------------------------
    report_markdown: str
    last_report_path: str

    # ---- control flow ------------------------------------------------------------
    next_action: str | None   # routing hint set by the human-feedback intent classifier
    awaiting_human: bool      # True once we've surfaced a report and are waiting on the user
    session_done: bool        # True once the user is done and the graph should end


def new_state(job_description_raw: str = "") -> AgentState:
    """Factory for a fresh AgentState (used by matching_agent.py / app_streamlit.py)."""
    return AgentState(
        messages=[],
        job_description_raw=job_description_raw,
        requirements=None,
        previous_requirements=None,
        round=1,
        pool_size=0,
        search_results=[],
        shortlist=[],
        previous_shortlist=[],
        deep_analysis={},
        hire_recommendations={},
        report_markdown="",
        last_report_path="",
        next_action=None,
        awaiting_human=False,
        session_done=False,
    )
