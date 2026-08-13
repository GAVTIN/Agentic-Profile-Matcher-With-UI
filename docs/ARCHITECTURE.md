# Architecture

## Overview

The agent is a single LangGraph `StateGraph` with six nodes. Five of them
are a deterministic pipeline (parse → extract → search → rank → report);
the sixth, `human_feedback`, is where it becomes genuinely agentic — it
pauses with LangGraph's `interrupt()`, and on resume either answers your
question directly (by calling tools), loops back into the pipeline for a
real re-rank, or ends the session.

```
START -> parse_jd -> extract_requirements -> search_resumes ->
rank_candidates -> generate_report -> human_feedback -> END
```

See `diagrams/state_machine.mmd` for the annotated diagram, or
`diagrams/state_machine.raw.mmd` for the one LangGraph generates directly
from the compiled graph.

## Two modes, one codebase

Every tool that reasons about text (extracting requirements, comparing
candidates, writing interview questions, calling strengths/gaps/hire
decisions) has two implementations behind a single function:

- **`live`** — calls Groq (`langchain-groq`) for reasoning and local
  HuggingFace `sentence-transformers` embeddings + Chroma for RAG search.
  Real semantic search, real LLM judgment. Needs `GROQ_API_KEY`.
- **`mock`** — zero external calls. TF-IDF + cosine similarity for search
  (`src/tools/rag_tools.py::_TfidfIndex`), keyword/regex parsing for
  requirement extraction, and a transparent weighted-scoring formula for
  ranking and comparison (`src/ranking.py`, `src/tools/screening_tools.py`).

`config.MODE` is resolved once at startup (`--mode auto|live|mock`, auto
picks live iff `GROQ_API_KEY` is set) and every tool branches on it. This
isn't a stub for the live path — mock mode is a fully working keyword-based
matcher on its own, which is what makes the whole project runnable and
demoable with zero setup. Every transcript in `tests/test_scenarios.md` was
captured running in mock mode for exactly that reason: it's reproducible
without an API key.

## Why round 1 uses the same scorer in both modes

Running an LLM judgment over all 100 resumes for a first-pass filter would
be slow and wasteful even on fast Groq inference. So **both** modes use the
same deterministic scorer for round 1 (`src/ranking.py::score_candidate`):

```
score = 50% must-have coverage + 20% nice-to-have coverage
      + 15% years-experience fit + 15% RAG/semantic similarity
```

Live mode's extra reasoning power shows up in round 2 (`deep_analyze_candidate`,
one LLM call per *shortlisted* candidate instead of per resume) and in the
conversational tools. This mirrors how real retrieval-then-rerank pipelines
are usually built: cheap filter over everything, expensive reasoning on the
survivors.

One consequence worth knowing: because the round-1 score blends four
signals, the #1 overall candidate won't always have the *highest single-dimension*
must-have coverage — someone else might edge them out on raw coverage while
trailing on experience fit or semantic relevance. That's not a bug; it's why
`compare_candidates` exists as a way to drill into one dimension directly
rather than trusting the blended score alone (see Scenario 2 in
`tests/test_scenarios.md`, where the compare tool surfaces a different
"leader" on must-have coverage than the round-1 aggregate ranking).

## Human-in-the-loop, for real

`human_feedback` calls `interrupt()` and is driven by a `MemorySaver`
checkpointer, so it's a genuine pause-and-resume, not a polling loop:

```python
user_reply = interrupt({"message": question, "report": state["report_markdown"]})
```

The CLI and Streamlit app both drive this the same way: `graph.invoke(...)`
until `"__interrupt__"` shows up in the result, print/show the question,
collect the reply, `graph.invoke(Command(resume=reply), config=thread_config)`,
repeat.

On resume, the message is classified into one of three intents:

- **`REFINE_REQUIREMENTS`** — the requirements object is updated (skills can
  be added, removed, or promoted between must-have/nice-to-have; minimum
  years can change) and the graph loops back into `rank_candidates`
  directly — not back through `search_resumes`, since that node already
  retrieved the full 100-resume pool. Re-scoring against an already-fetched
  pool is faster and just as correct. `generate_report` then diffs the new
  shortlist against the previous one (`report_generator.py::diff_shortlists`)
  so the answer to "how did this change" is explicit, not left for you to
  spot.
- **`END_SESSION`** — graph routes to `END`.
- **`OTHER`** (comparisons, explanations, interview questions, hire calls,
  general questions) — live mode runs a real tool-calling loop (bind all 11
  tools, let the model decide what to call, execute, respond); mock mode
  uses keyword routing over the same tools (`src/graph/nodes.py::_mock_dispatch_other`).
  Either way, state-derived context (current requirements, current
  shortlist, current deep-analysis) is *injected* into tool arguments by
  the orchestration code, not trusted from LLM output — the model doesn't
  need to transcribe facts the graph already has authoritatively.

## State

`src/state.py::AgentState` tracks three things end to end: `messages`
(conversation history, via LangGraph's `add_messages` reducer), the job
requirements understanding (`requirements`, plus `previous_requirements` for
diffing), and the candidate pipeline (`shortlist` with per-candidate
`rationale`, `deep_analysis`, `hire_recommendations`, plus
`previous_shortlist` for diffing). `round` tracks which of the three
screening rounds is active.

## Tools

| Tool | Milestone / Part | Live path | Mock path |
|---|---|---|---|
| `list_resumes`, `read_resume`, `list_job_descriptions`, `read_job_description`, `save_report` | Milestone 1 (filesystem) | — (no LLM involved) | — |
| `search_resumes` | Milestone 2 (RAG) | HuggingFace embeddings + Chroma | TF-IDF + cosine similarity |
| `extract_requirements` | Part A | structured output (Pydantic) | header/bullet parsing + skill vocabulary |
| `compare_candidates` | Part A | structured output | must/nice-have overlap |
| `generate_interview_questions` | Part A | structured output | templated, gap-targeted |
| `deep_analyze_candidate` | Part C.1 round 2 / C.2 | structured output | derived from round-1 score |
| `recommend_hire_decision` | Part C.1 round 3 | structured output | threshold on score + gaps |

`deep_analyze_candidate` and `recommend_hire_decision` extend beyond the
three tools named explicitly in the brief, added because Part C.1
("second round: deep analysis"; "final round: generate hire/no-hire
recommendation") and C.2 ("explainability... improvement suggestions")
describe capabilities that need first-class tools of their own rather than
being folded into `compare_candidates`.

## Known simplifications

- **Requirement extraction is heuristic in mock mode.** It handles common
  JD phrasing well (including word-wrapped bullets and "X, Y, or Z"
  alternatives — see the commit history / code comments in
  `src/tools/screening_tools.py::_atomize_bullet` for what that took to get
  right) but it's not full NLU. Live mode's LLM extraction is materially
  more robust on unusual JD formats.
- **`config.MODE` is a single process-global**, not per-session. Fine for a
  local demo (CLI, or Streamlit run by one person); a multi-tenant
  deployment would need to thread mode through explicitly instead.
- **Candidate name resolution** (`_find_referenced_candidates`) matches
  first names and IDs against the current shortlist, then falls back to the
  full 100-candidate pool. Two candidates sharing a first name outside the
  shortlist could theoretically be ambiguous; not handled beyond
  first-match.
- **The vector store isn't checked into git** (see `.gitignore`) — it's
  rebuilt from `data/resumes/` on first live-mode run. Mock mode doesn't
  need it at all.
