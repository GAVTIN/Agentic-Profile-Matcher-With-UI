# Demo Video Script (5–6 minutes)

A shot-by-shot guide for recording the submission video. Free screen
recorders that work well for this: OBS Studio (free, cross-platform),
Loom (free tier covers this length), or Windows' built-in Xbox Game Bar
(Win+G) since you're on Windows.

**Before you hit record:**
- `cp .env.example .env` and add a real `GROQ_API_KEY` if you want to show
  live mode (optional — mock mode alone is a complete, honest demo and
  needs no setup; showing both is the strongest version of this video)
- Widen your terminal font size so it's readable on screen
- Close anything with notifications
- Do one silent dry run first so you're not narrating cold

---

## 0:00–0:40 — What this is (talking head or slide, no screen yet)

Say what it does in three sentences: a LangGraph agent that screens
resumes against a job description in three rounds (initial screen, deep
analysis, hire recommendation), then hands control to a conversational
loop where you can compare candidates, ask why one ranked over another,
request interview questions, or adjust requirements and get a live re-rank.
Mention it's built for a course assignment but structured as a real
portfolio project — LangGraph, RAG, tool-calling, human-in-the-loop.

## 0:40–1:20 — Architecture, fast

Show `diagrams/state_machine.mmd` rendered (paste it into
[mermaid.live](https://mermaid.live) beforehand, or view it on GitHub if
you've already pushed). Trace the flow with your cursor: Parse JD →
Extract Requirements → Search Resumes → Rank Candidates → Generate Report
→ Human Feedback Loop, with the loop-back edge for refinements. One
sentence on the live/mock dual-mode design from `docs/ARCHITECTURE.md` —
"it runs fully offline with a rule-based fallback so anyone can clone and
try it with zero setup, or with Groq for real LLM reasoning."

## 1:20–3:30 — Live terminal walkthrough (the core of the video)

```bash
python matching_agent.py --jd data/job_descriptions/senior_frontend_react.txt
```

Narrate as it runs:
- **Parse + extract** — point out the must-have vs nice-to-have split
  appearing in real time
- **Search + rank** — "it just searched all 100 resumes and scored them —
  here's the top 10"
- **Report** — scroll through the round-1 table and the round-2
  strengths/gaps breakdown; call out one borderline candidate's
  improvement suggestions specifically (Part C.2's explainability ask)

Then drive the conversation live — type these, pausing to narrate each
result before the next:

1. `Compare the top 3 matches side by side`
2. `Why did John rank higher than Jane?` — this is the moment to slow down;
   it's the assignment's own example question, and the answer names the
   exact single differentiating requirement. Say so explicitly.
3. `We also need AWS experience` — narrate the re-rank and point at the
   "What changed since the last ranking" section — call out that this is
   answering Part B.2's "explains changes in rankings" requirement by name
4. `Give me interview questions for John`
5. `Give me a hire recommendation for John` — this is round 3

## 3:30–4:15 — Streamlit interface

```bash
streamlit run app_streamlit.py
```

Pick a different sample JD than the terminal run (e.g. Backend Engineer)
so it's visibly a fresh run, not a repeat. Show the sidebar's live
requirements/shortlist summary and the download-report button. Ask one
follow-up question in the chat box to show it's the same agent, just a
different skin.

## 4:15–5:00 — Code tour (optional but strengthens the "real engineering"
## impression)

Open, in order, spending ~10 seconds on each:
- `matching_agent.py` — the actual `StateGraph` wiring (nodes + edges),
  so it's visibly not hidden away
- `src/graph/nodes.py::human_feedback_node` — point at the `interrupt()`
  call
- `src/tools/screening_tools.py` — one live-mode tool (structured output)
  next to its mock-mode counterpart, to make the dual-mode point concrete
- `tests/test_scenarios.md` — "these six transcripts aren't hand-written,
  they're captured by actually running the agent" — scroll past a couple

## 5:00–5:45 — Wrap-up

Recap against the brief in one breath: state design, the required graph
shape, all the required + extra tools, conversational refinement,
multi-round screening, explainability, two interfaces, real test
scenarios. Mention the GitHub link/README for anyone who wants to run it
themselves.

---

## If you're short on time, cut to this 3-minute version

0:00–0:30 what it is → 0:30–1:00 diagram → 1:00–2:30 terminal walkthrough
(steps 2 and 3 from above are the two moments that matter most: the "why
did John rank higher" explainability answer, and the live re-rank with the
diff explanation) → 2:30–3:00 quick Streamlit glance + wrap-up.
