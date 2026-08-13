"""
Renders already-computed shortlist + deep-analysis data into the markdown
report shown to the user and saved to disk. Pure formatting - no scoring
logic lives here (that's ranking.py) and no LLM calls happen here (those
happen upstream, in nodes.py, before this is called).
"""

from __future__ import annotations


def diff_shortlists(previous: list[dict], current: list[dict]) -> str:
    """Explains what changed between two shortlists (Part B.2: 'explains changes
    in rankings'). Returns '' if there's no previous shortlist to diff against."""
    if not previous:
        return ""

    prev_ids = [c["candidate_id"] for c in previous]
    curr_ids = [c["candidate_id"] for c in current]
    prev_rank = {cid: i + 1 for i, cid in enumerate(prev_ids)}
    curr_rank = {cid: i + 1 for i, cid in enumerate(curr_ids)}
    names = {c["candidate_id"]: c["name"] for c in current + previous}

    lines = ["## What changed since the last ranking", ""]
    added = [cid for cid in curr_ids if cid not in prev_rank]
    dropped = [cid for cid in prev_ids if cid not in curr_rank]
    moved = []
    for cid in curr_ids:
        if cid in prev_rank and prev_rank[cid] != curr_rank[cid]:
            direction = "up" if curr_rank[cid] < prev_rank[cid] else "down"
            moved.append(f"- {names.get(cid, cid)} moved {direction}: #{prev_rank[cid]} → #{curr_rank[cid]}")

    if added:
        lines.append(f"- Newly in the top {len(current)}: {', '.join(names.get(c, c) for c in added)}")
    if dropped:
        lines.append(f"- Dropped out of the top {len(current)}: {', '.join(names.get(c, c) for c in dropped)}")
    lines.extend(moved)
    if not (added or dropped or moved):
        lines.append("- Ranking order is unchanged, though scores may have shifted slightly.")
    lines.append("")
    return "\n".join(lines)


def generate_full_report(requirements: dict, shortlist: list[dict], deep_analysis: dict[str, dict],
                          pool_size: int) -> str:
    lines: list[str] = []
    role = requirements.get("role_title", "Role")
    lines.append(f"# Candidate Match Report — {role}")
    lines.append("")
    lines.append(f"**Seniority:** {requirements.get('seniority', 'n/a')}  ")
    lines.append(f"**Minimum experience:** {requirements.get('min_years_experience', 0)}+ years  ")
    lines.append(f"**Must-have:** {', '.join(requirements.get('must_have', [])) or 'none specified'}  ")
    lines.append(f"**Nice-to-have:** {', '.join(requirements.get('nice_to_have', [])) or 'none specified'}  ")
    lines.append("")
    lines.append(f"## Round 1 — Initial screen: top {len(shortlist)} of {pool_size} resumes")
    lines.append("")
    lines.append("| Rank | Candidate | Score /100 | Must-have coverage | Why |")
    lines.append("|---|---|---|---|---|")
    for i, c in enumerate(shortlist, 1):
        total_must = len(c["matched_must_have"]) + len(c["missing_must_have"])
        must_cov = f"{len(c['matched_must_have'])}/{total_must}" if total_must else "n/a"
        lines.append(f"| {i} | {c['name']} ({c['candidate_id']}) | {c['score']:.1f} | {must_cov} | {c['rationale']} |")
    lines.append("")
    lines.append("## Round 2 — Deep analysis of the shortlist")
    lines.append("")
    for c in shortlist:
        da = deep_analysis.get(c["candidate_id"], {})
        verdict = da.get("verdict", "n/a")
        lines.append(f"### {c['name']} ({c['candidate_id']}) — {verdict}")
        lines.append("")
        lines.append("**Strengths**")
        for s in da.get("strengths", []) or ["None identified."]:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("**Gaps**")
        gaps = da.get("gaps", [])
        for g in gaps or ["None identified against current requirements."]:
            lines.append(f"- {g}")
        if da.get("improvement_suggestions"):
            lines.append("")
            lines.append("**Improvement suggestions** _(borderline candidate)_")
            for s in da["improvement_suggestions"]:
                lines.append(f"- {s}")
        lines.append("")
    lines.append("---")
    lines.append(
        "_Ask for a head-to-head comparison, interview questions, or a hire/no-hire "
        "recommendation for any candidate above - or refine the requirements and I'll re-rank._"
    )
    return "\n".join(lines)


def format_comparison(result: dict) -> str:
    """Conversational (non-report) formatter for compare_candidates() output."""
    lines = ["**Comparison**", ""]
    for row in result.get("candidates", []):
        if row.get("error"):
            lines.append(f"- **{row['candidate_id']}**: {row['error']}")
            continue
        lines.append(f"- **{row['name']} ({row['candidate_id']})** — "
                      f"matches {len(row.get('matched_must_have', []))} must-have(s), "
                      f"{len(row.get('matched_nice_to_have', []))} nice-to-have(s)"
                      + (f"; strengths: {', '.join(row['notable_strengths'])}" if row.get("notable_strengths") else ""))
    lines.append("")
    lines.append(result.get("summary", ""))
    return "\n".join(lines)


def format_interview_questions(candidate_id: str, name: str, questions: list[str]) -> str:
    lines = [f"**Screening questions for {name} ({candidate_id})**", ""]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q}")
    return "\n".join(lines)


def format_hire_decision(result: dict, name: str) -> str:
    return (f"**Round 3 recommendation — {name} ({result['candidate_id']})**\n\n"
            f"**Decision: {result['decision']}**\n\n{result['reasoning']}")
