"""
Node functions for the LangGraph pipeline defined in matching_agent.py:

    START -> parse_jd -> extract_requirements -> search_resumes ->
    rank_candidates -> generate_report -> human_feedback -> END

Every node takes the full AgentState and returns a *partial* dict that
LangGraph merges back in. The five pipeline nodes are deterministic
(same input -> same shape of output); human_feedback is where the agent
gets conversational - it pauses with interrupt(), then classifies and
dispatches whatever the user says, either by looping back into the
pipeline (a real refinement + re-rank) or by calling tools directly and
replying in place.
"""

from __future__ import annotations

import json
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from .. import config, llm, ranking, report_generator, tools
from ..state import AgentState

_TOOL_BY_NAME = {t.name: t for t in tools.ALL_TOOLS}


# ==========================================================================
# 1. Parse JD
# ==========================================================================

def parse_jd(state: AgentState) -> dict:
    jd_text = (state.get("job_description_raw") or "").strip()
    if not jd_text:
        return {
            "messages": [AIMessage(content="I don't have a job description yet — paste one in and I'll take it from there.")],
            "session_done": True,
        }
    word_count = len(jd_text.split())
    ack = AIMessage(content=f"Got the job description ({word_count} words). Parsing requirements...")
    return {"job_description_raw": jd_text, "messages": [ack]}


# ==========================================================================
# 2. Extract Requirements
# ==========================================================================

def extract_requirements_node(state: AgentState) -> dict:
    requirements = tools.extract_requirements.invoke({"jd_text": state["job_description_raw"]})
    summary = (
        f"**{requirements['role_title']}** — {requirements['seniority']}, "
        f"{requirements['min_years_experience']}+ yrs\n\n"
        f"**Must-have:** {', '.join(requirements['must_have']) or 'none extracted'}\n"
        f"**Nice-to-have:** {', '.join(requirements['nice_to_have']) or 'none extracted'}"
    )
    return {"requirements": requirements, "messages": [AIMessage(content=summary)]}


# ==========================================================================
# 3. Search Resumes  (Milestone 2 RAG tool, queried over the full pool)
# ==========================================================================

def search_resumes_node(state: AgentState) -> dict:
    req = state["requirements"]
    all_ids = tools.list_resumes.invoke({})
    pool_size = len(all_ids)
    query = f"{req.get('role_title', '')} " + " ".join(req.get("must_have", []) + req.get("nice_to_have", []))
    hits = tools.search_resumes.invoke({"query": query.strip() or "software engineer", "k": pool_size})
    ack = AIMessage(content=f"Searched all {pool_size} resumes in the pool. Scoring and ranking now...")
    return {"search_results": hits, "pool_size": pool_size, "messages": [ack]}


# ==========================================================================
# 4. Rank Candidates  (round 1: top N of pool_size)
# ==========================================================================

def rank_candidates_node(state: AgentState) -> dict:
    req = state["requirements"]
    hits = state["search_results"]
    resume_texts = {h["candidate_id"]: tools.read_resume.invoke({"candidate_id": h["candidate_id"]}) for h in hits}
    shortlist = ranking.rank_candidates(hits, resume_texts, req, top_n=config.ROUND1_SHORTLIST_SIZE)

    lines = [f"**Round 1 shortlist — top {len(shortlist)} of {state['pool_size']}:**"]
    for i, c in enumerate(shortlist, 1):
        lines.append(f"{i}. {c['name']} ({c['candidate_id']}) — {c['score']:.1f}/100")

    return {
        "shortlist": shortlist,
        "previous_shortlist": state.get("shortlist", []),
        "round": 1,
        "messages": [AIMessage(content="\n".join(lines))],
    }


# ==========================================================================
# 5. Generate Report  (round 2: deep analysis of the shortlist)
# ==========================================================================

def generate_report_node(state: AgentState) -> dict:
    req = state["requirements"]
    shortlist = state["shortlist"]

    deep_analysis: dict[str, dict] = {}
    for c in shortlist:
        deep_analysis[c["candidate_id"]] = tools.deep_analyze_candidate.invoke({
            "candidate_id": c["candidate_id"],
            "requirements_json": json.dumps(req),
            "round1_score_json": json.dumps(c),
        })

    report_md = report_generator.generate_full_report(req, shortlist, deep_analysis, state["pool_size"])

    diff = report_generator.diff_shortlists(state.get("previous_shortlist", []), shortlist)
    if diff:
        report_md = diff + "\n" + report_md

    saved_path = tools.save_report.invoke({
        "filename": req.get("role_title", "report").replace(" ", "_"),
        "content": report_md,
    })

    return {
        "deep_analysis": deep_analysis,
        "report_markdown": report_md,
        "last_report_path": saved_path,
        "round": 2,
        "messages": [AIMessage(content=report_md + f"\n\n_(saved to `{saved_path}`)_")],
        "awaiting_human": True,
    }


# ==========================================================================
# 6. Human Feedback Loop
# ==========================================================================

class _Intent(BaseModel):
    intent: str = Field(description="Exactly one of: REFINE_REQUIREMENTS, END_SESSION, OTHER")
    refinement_instruction: str = Field(
        default="", description="If intent is REFINE_REQUIREMENTS, a clean one-line restatement of what should change")


class _MergedRequirements(BaseModel):
    role_title: str
    must_have: list[str]
    nice_to_have: list[str]
    min_years_experience: int
    seniority: str


_REFINE_TRIGGERS = (
    "also require", "also need", "also want", "we also", "must also", "should also",
    "increase the minimum", "increase minimum", "raise the minimum", "raise the bar",
    "bump up the", "change the requirement", "update the requirement", "add a requirement",
    "add requirement", "now require", "actually we need", "actually i need", "actually, we need",
    "make it a requirement", "drop the requirement", "remove the requirement", "no longer require",
)
_END_TRIGGERS = (
    "that's all", "thats all", "we're done", "were done", "i'm done", "im done", "exit", "quit",
    "goodbye", "good bye", "wrap up", "no more questions", "stop here", "nothing else", "all set",
)


def _classify_intent_mock(user_msg: str) -> tuple[str, str]:
    low = user_msg.lower()
    if any(t in low for t in _END_TRIGGERS):
        return "END_SESSION", ""
    if any(t in low for t in _REFINE_TRIGGERS):
        return "REFINE_REQUIREMENTS", user_msg
    return "OTHER", ""


def _classify_intent_live(user_msg: str) -> tuple[str, str]:
    model = llm.get_chat_model(fast=True).with_structured_output(_Intent)
    result = model.invoke([
        SystemMessage(content=(
            "Classify the recruiter's message into exactly one intent.\n"
            "REFINE_REQUIREMENTS: they want to add, remove, or change a hiring requirement "
            "(a skill, years of experience, seniority) and re-rank candidates against it.\n"
            "END_SESSION: they're done, said thanks-and-goodbye, or want to stop.\n"
            "OTHER: anything else - questions, comparisons, requests for interview questions "
            "or a hire recommendation, or general conversation."
        )),
        HumanMessage(content=user_msg),
    ])
    return result.intent, result.refinement_instruction


def _merge_requirements_mock(current: dict, refinement_instruction: str) -> dict:
    from ..tools.screening_tools import KNOWN_SKILLS

    updated = dict(current)
    updated["must_have"] = list(current.get("must_have", []))
    updated["nice_to_have"] = list(current.get("nice_to_have", []))

    low = refinement_instruction.lower()
    is_removal = any(w in low for w in ("drop", "remove", "no longer"))
    found_skills = [s for s in KNOWN_SKILLS if s.lower() in low]
    target_list = "nice_to_have" if any(w in low for w in ("nice to have", "prefer", "bonus")) else "must_have"

    for s in found_skills:
        other_list = "nice_to_have" if target_list == "must_have" else "must_have"
        if is_removal:
            updated["must_have"] = [x for x in updated["must_have"] if x != s]
            updated["nice_to_have"] = [x for x in updated["nice_to_have"] if x != s]
        else:
            # If the skill is already tracked on the *other* list, this
            # instruction promotes/demotes it (e.g. "we also need GraphQL"
            # when GraphQL is currently only a nice-to-have) - move it
            # rather than silently no-op'ing because it's "already there".
            if s in updated[other_list]:
                updated[other_list] = [x for x in updated[other_list] if x != s]
            if s not in updated[target_list]:
                updated[target_list].append(s)

    updated["min_years_experience"] = _extract_years_from_instruction(refinement_instruction) \
        or updated.get("min_years_experience", 0)

    return updated


def _extract_years_from_instruction(text: str) -> int | None:
    """More liberal than the JD-parsing years regex - a refinement is
    conversational ("bump the minimum up to 5 years", "increase the minimum
    years to 5"), not formal JD phrasing, so it needs to catch the number
    landing on either side of "years"."""
    m = re.search(r"(\d+)\+?\s*years?", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:years?|minimum|experience).{0,20}?\bto\s+(\d+)\b", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _merge_requirements_live(current: dict, refinement_instruction: str) -> dict:
    model = llm.get_chat_model(fast=True).with_structured_output(_MergedRequirements)
    result = model.invoke([
        SystemMessage(content=(
            "You update a structured job-requirements object based on a recruiter's "
            "follow-up instruction. Keep everything unchanged except what the instruction "
            "asks to change. Return the FULL updated object, not just the delta."
        )),
        HumanMessage(content=(
            f"CURRENT REQUIREMENTS:\n{json.dumps(current, indent=2)}\n\n"
            f"INSTRUCTION:\n{refinement_instruction}"
        )),
    ])
    return result.model_dump()


def _find_referenced_candidates(user_msg: str, shortlist: list[dict]) -> list[str]:
    """Looks for candidate names/IDs mentioned in the user's message. Checks
    the current shortlist first (fast path, has scores handy), then falls
    back to the full candidate pool so a question like "why did John rank
    higher than Jane" still resolves Jane even when she didn't make the
    current top-N and so isn't in `shortlist` at all."""
    low = user_msg.lower()
    found = []
    for c in shortlist:
        first_name = c["name"].split()[0].lower() if c["name"].split() else ""
        if c["candidate_id"].lower() in low or (first_name and re.search(rf"\b{re.escape(first_name)}\b", low)):
            found.append(c["candidate_id"])

    if len(found) < 2:
        from ..tools.filesystem_tools import load_candidate_metadata

        meta = load_candidate_metadata()
        for cid, c in meta.items():
            if cid in found:
                continue
            first_name = c["name"].split()[0].lower() if c["name"].split() else ""
            if cid.lower() in low or (first_name and re.search(rf"\b{re.escape(first_name)}\b", low)):
                found.append(cid)

    return found


def _mock_dispatch_other(state: AgentState, user_msg: str) -> tuple[AIMessage, dict]:
    low = user_msg.lower()
    shortlist = state.get("shortlist", [])
    req = state.get("requirements") or {}
    referenced = _find_referenced_candidates(user_msg, shortlist)

    if "compare" in low or ("why" in low and ("rank" in low or " than " in low or "higher" in low)):
        ids = referenced if len(referenced) >= 2 else [c["candidate_id"] for c in shortlist[:3]]
        result = tools.compare_candidates.invoke({"candidate_ids": ids, "requirements_json": json.dumps(req)})
        return AIMessage(content=report_generator.format_comparison(result)), {}

    if "interview" in low or "screening question" in low:
        cid = referenced[0] if referenced else (shortlist[0]["candidate_id"] if shortlist else None)
        if not cid:
            return AIMessage(content="I don't have a shortlist yet to generate questions from."), {}
        name = next((c["name"] for c in shortlist if c["candidate_id"] == cid), cid)
        questions = tools.generate_interview_questions.invoke({"candidate_id": cid, "requirements_json": json.dumps(req)})
        return AIMessage(content=report_generator.format_interview_questions(cid, name, questions)), {}

    if "hire" in low or "recommend" in low:
        cid = referenced[0] if referenced else (shortlist[0]["candidate_id"] if shortlist else None)
        if not cid:
            return AIMessage(content="I don't have a shortlist yet to make a recommendation from."), {}
        name = next((c["name"] for c in shortlist if c["candidate_id"] == cid), cid)
        result = tools.recommend_hire_decision.invoke({
            "candidate_id": cid,
            "shortlist_json": json.dumps(shortlist),
            "deep_analysis_json": json.dumps(state.get("deep_analysis", {})),
        })
        updated_recs = {**state.get("hire_recommendations", {}), cid: result}
        return AIMessage(content=report_generator.format_hire_decision(result, name)), {"hire_recommendations": updated_recs}

    if any(w in low for w in ("analy", "detail", "gap", "strength", "deep")):
        cid = referenced[0] if referenced else (shortlist[0]["candidate_id"] if shortlist else None)
        if not cid:
            return AIMessage(content="I don't have a shortlist yet to analyze."), {}
        name = next((c["name"] for c in shortlist if c["candidate_id"] == cid), cid)
        match = next((c for c in shortlist if c["candidate_id"] == cid), None)
        result = tools.deep_analyze_candidate.invoke({
            "candidate_id": cid, "requirements_json": json.dumps(req),
            "round1_score_json": json.dumps(match) if match else "",
        })
        text = (f"**{name} ({cid}) — {result['verdict']}**\n\n"
                f"Strengths: {', '.join(result['strengths']) or 'none'}\n\n"
                f"Gaps: {', '.join(result['gaps']) or 'none'}")
        return AIMessage(content=text), {}

    names = ", ".join(c["name"] for c in shortlist[:3])
    fallback = (
        f"I can compare candidates, generate interview questions, give a hire/no-hire "
        f"recommendation, or re-rank if you adjust the requirements. Current top 3: {names or 'n/a'}."
    )
    return AIMessage(content=fallback), {}


def _build_context_prompt(state: AgentState) -> str:
    req = state.get("requirements") or {}
    shortlist = state.get("shortlist", [])
    lines = [
        "You are a recruiting copilot helping a hiring manager evaluate candidates for a role.",
        f"Role: {req.get('role_title', 'n/a')} ({req.get('seniority', 'n/a')}, "
        f"{req.get('min_years_experience', 0)}+ yrs)",
        f"Must-have: {', '.join(req.get('must_have', [])) or 'none'}",
        f"Nice-to-have: {', '.join(req.get('nice_to_have', [])) or 'none'}",
        "",
        "Current shortlist (candidate_id: name — score):",
    ]
    for c in shortlist:
        lines.append(f"- {c['candidate_id']}: {c['name']} — {c['score']:.1f}/100")
    lines.append("")
    lines.append(
        "Use the available tools to answer thoroughly and specifically - call "
        "compare_candidates, generate_interview_questions, deep_analyze_candidate, or "
        "recommend_hire_decision as needed. Reference candidates by name. Be concise but concrete."
    )
    return "\n".join(lines)


def _inject_state_context(tool_name: str, args: dict, state: AgentState) -> dict:
    req = state.get("requirements")
    if tool_name in ("compare_candidates", "generate_interview_questions", "deep_analyze_candidate"):
        args["requirements_json"] = json.dumps(req) if req else ""
    if tool_name == "deep_analyze_candidate":
        shortlist = state.get("shortlist", [])
        match = next((c for c in shortlist if c["candidate_id"] == args.get("candidate_id")), None)
        args["round1_score_json"] = json.dumps(match) if match else ""
    if tool_name == "recommend_hire_decision":
        args["shortlist_json"] = json.dumps(state.get("shortlist", []))
        args["deep_analysis_json"] = json.dumps(state.get("deep_analysis", {}))
    return args


def _live_dispatch_other(state: AgentState, user_msg: str) -> tuple[AIMessage, dict]:
    model = llm.get_chat_model(fast=False).bind_tools(tools.ALL_TOOLS)
    conversation = [SystemMessage(content=_build_context_prompt(state)), *list(state["messages"])[-6:],
                     HumanMessage(content=user_msg)]

    ai_response = model.invoke(conversation)
    conversation.append(ai_response)
    state_updates: dict = {}

    if ai_response.tool_calls:
        for call in ai_response.tool_calls:
            args = _inject_state_context(call["name"], dict(call["args"]), state)
            tool_fn = _TOOL_BY_NAME.get(call["name"])
            try:
                result = tool_fn.invoke(args) if tool_fn else {"error": f"unknown tool {call['name']}"}
            except Exception as exc:  # keep the conversation alive even if a tool call fails
                result = {"error": str(exc)}
            if call["name"] == "recommend_hire_decision" and isinstance(result, dict) and "candidate_id" in result:
                state_updates["hire_recommendations"] = {
                    **state.get("hire_recommendations", {}), result["candidate_id"]: result
                }
            conversation.append(ToolMessage(content=json.dumps(result, default=str), tool_call_id=call["id"]))
        final = model.invoke(conversation)
        return AIMessage(content=final.content), state_updates

    return AIMessage(content=ai_response.content), state_updates


def human_feedback_node(state: AgentState) -> dict:
    question = (
        "What would you like to do next? You can compare candidates, ask why one ranked "
        "higher than another, request interview questions, get a hire recommendation, "
        "adjust the requirements, or say you're done."
    )
    user_reply = interrupt({"message": question, "report": state.get("report_markdown", "")})
    human_msg = HumanMessage(content=user_reply)

    if config.MODE == "live":
        intent, refinement_instruction = _classify_intent_live(user_reply)
    else:
        intent, refinement_instruction = _classify_intent_mock(user_reply)

    if intent == "END_SESSION":
        ai_msg = AIMessage(content=(
            "Sounds good — wrapping up here. The full report is saved to disk if you want to "
            f"revisit it (`{state.get('last_report_path', 'data/reports/')}`). Good luck with the search!"
        ))
        updates = {"session_done": True}
    elif intent == "REFINE_REQUIREMENTS":
        current = state.get("requirements") or {}
        new_req = (_merge_requirements_live(current, refinement_instruction) if config.MODE == "live"
                   else _merge_requirements_mock(current, refinement_instruction))
        ai_msg = AIMessage(content=(
            f"Got it — updating the requirements and re-ranking against all "
            f"{state.get('pool_size', 0)} resumes..."
        ))
        updates = {"requirements": new_req, "previous_requirements": current, "next_action": "rerank"}
    else:
        ai_msg, updates = (_live_dispatch_other(state, user_reply) if config.MODE == "live"
                            else _mock_dispatch_other(state, user_reply))
        updates.setdefault("next_action", "continue")

    return {"messages": [human_msg, ai_msg], **updates}


def route_after_feedback(state: AgentState) -> str:
    if state.get("session_done"):
        return "end"
    if state.get("next_action") == "rerank":
        return "rerank"
    return "continue"
