"""
The four higher-level screening tools:
  - extract_requirements       (Part A, required)
  - compare_candidates         (Part A, required)
  - generate_interview_questions (Part A, required)
  - recommend_hire_decision    (added for Part C.1's third screening round -
                                 "generate hire/no-hire recommendation")

Each has a LIVE path (LLM call, structured output where it matters) and a
MOCK path (rule-based, using the resume metadata sidecar as ground truth).
The two paths return the *same* shape so nothing downstream needs to care
which one ran.

State-derived context (current requirements, current shortlist, current
deep-analysis) is passed in as JSON-string kwargs. The LLM *can* fill these
in during tool-calling, but src/graph/nodes.py always overwrites them with
the authoritative value from AgentState right before invoking the tool -
we don't trust the model to transcribe facts we already have.
"""

from __future__ import annotations

import json
import random
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .. import config, llm
from .filesystem_tools import load_candidate_metadata, read_resume

# ==========================================================================
# extract_requirements
# ==========================================================================

_MUST_HEADERS = ("requirements", "must have", "must-have", "qualifications", "what you'll need", "you have")
_NICE_HEADERS = ("nice to have", "nice-to-have", "preferred", "bonus", "a plus", "good to have")
_STOP_HEADERS = ("what success looks like", "about the", "benefits", "compensation",
                 "how to apply", "responsibilities", "about us")

# Shared skill vocabulary used to (a) pull atomic skills out of free-text JD
# bullets during heuristic extraction and (b) match those skills back against
# resume text during mock-mode scoring. Doesn't need to be exhaustive - just
# broad enough to cover common tech-hiring vocabulary, matched case-insensitively.
KNOWN_SKILLS = [
    "React", "TypeScript", "JavaScript", "HTML5", "CSS3", "Redux", "Redux Toolkit", "Next.js",
    "Vue.js", "Angular", "Webpack", "Vite", "Jest", "Cypress", "Playwright", "Tailwind CSS",
    "GraphQL", "Storybook", "Web Accessibility", "WCAG", "Responsive Design", "Zustand",
    "Node.js", "REST API", "SQL", "Git", "Python", "Java", "Go", "Express.js", "Django", "FastAPI",
    "Spring Boot", "PostgreSQL", "MongoDB", "Redis", "Microservices", "Docker", "Kubernetes",
    "RabbitMQ", "Kafka", "JWT", "OAuth2", "Pandas", "NumPy", "Apache Spark", "Airflow",
    "Machine Learning", "TensorFlow", "PyTorch", "Tableau", "Power BI", "Snowflake", "dbt",
    "Terraform", "AWS", "Azure", "GCP", "Jenkins", "GitHub Actions", "Ansible", "Prometheus",
    "Grafana", "React Native", "Swift", "Kotlin", "Flutter", "Xcode", "Selenium", "Postman", "CI/CD",
]
_COMMON_SKILLS = KNOWN_SKILLS  # backwards-compat alias


class _ExtractedRequirements(BaseModel):
    role_title: str = Field(description="The job title being hired for")
    must_have: list[str] = Field(description="Hard requirements / must-have qualifications, short phrases")
    nice_to_have: list[str] = Field(description="Preferred but not required qualifications, short phrases")
    min_years_experience: int = Field(description="Minimum years of relevant experience required; 0 if unspecified")
    seniority: str = Field(description="Junior, Mid-level, Senior, Staff/Lead, or Principal")


_SOFT_REQUIREMENT_MARKERS = (
    "bachelor's degree", "bachelor degree", "comfortable ", "ability to work", "strong communication",
    "team player", "collaborate", "collaborating", "equivalent practical experience", "work directly with",
)


def _atomize_bullet(bullet: str) -> list[str]:
    """Turn one JD bullet into zero or more short, matchable requirement items.

    JD bullets are usually full sentences ("3+ years of professional
    experience building production React applications"). Matching that whole
    sentence against resume text almost never hits. Instead, pull out any
    recognizable skill names.

    Two special cases matter:
    - Alternatives ("Redux, Redux Toolkit, Zustand, or equivalent") should
      become ONE requirement, not three separate must-haves that no single
      candidate could ever fully satisfy - we keep whichever recognized
      skill appears first in the bullet.
    - Purely soft/interpersonal requirements ("comfortable working with
      designers", "Bachelor's degree...") aren't verifiable from resume text
      at all; keeping them as unmatchable must-haves just drags every
      candidate's score down uniformly and clutters the report, so we drop
      them rather than falling back to a truncated sentence.
    """
    found = [s for s in KNOWN_SKILLS if s.lower() in bullet.lower()]
    if found:
        if " or " in bullet.lower() and len(found) > 1:
            found_sorted = sorted(found, key=lambda s: bullet.lower().find(s.lower()))
            return [found_sorted[0]]
        return found
    low = bullet.lower()
    if any(marker in low for marker in _SOFT_REQUIREMENT_MARKERS):
        return []
    short = bullet.strip()
    if len(short) > 50:
        # A long sentence with no recognizable skill in it is almost always a
        # soft/narrative requirement ("experience shipping features
        # independently, from design through to production") rather than a
        # single checkable qualification - keeping it would just make it an
        # unmatchable "must-have" for every candidate. Only short unmatched
        # phrases are kept, on the chance they're a real but uncommon
        # qualification (e.g. "GDPR compliance") not in KNOWN_SKILLS.
        return []
    return [short]


def _heuristic_extract(jd_text: str) -> dict:
    lines = [l.strip() for l in jd_text.splitlines()]
    title_line = next((l for l in lines if l.strip()), "Unknown Role")
    role_title = title_line.split("—")[0].split("|")[0].strip() or "Unknown Role"

    # Two passes: first reconstruct logical bullets (joining word-wrapped
    # continuation lines back into the bullet they belong to - plain-text
    # JDs are very often wrapped at ~70-80 chars, so without this a bullet
    # like "...Redux, Redux Toolkit, Zustand,\n  or equivalent)" would lose
    # its second line entirely), then atomize each complete bullet.
    must_bullets: list[str] = []
    nice_bullets: list[str] = []
    mode = None
    current_list: list[str] | None = None
    for line in lines:
        low = line.lower().strip()
        if not low:
            continue
        looks_like_header = len(low) < 60 and line.strip()[0].isupper()
        if looks_like_header and any(h in low for h in _STOP_HEADERS):
            mode, current_list = None, None
            continue
        if looks_like_header and any(h in low for h in _NICE_HEADERS):
            mode, current_list = "nice", nice_bullets
            continue
        if looks_like_header and any(h in low for h in _MUST_HEADERS):
            mode, current_list = "must", must_bullets
            continue
        if not mode:
            continue
        if line.strip()[:1] in ("-", "*", "•"):
            current_list.append(line.strip().lstrip("-*• ").strip())
        elif current_list:
            # wrapped continuation of the previous bullet
            current_list[-1] = f"{current_list[-1]} {line.strip()}"

    must, nice = [], []
    for b in must_bullets:
        must.extend(_atomize_bullet(b))
    for b in nice_bullets:
        nice.extend(_atomize_bullet(b))

    # de-dup while preserving order
    must = list(dict.fromkeys(must))
    nice = list(dict.fromkeys(nice))

    if not must:
        low_text = jd_text.lower()
        must = [s for s in KNOWN_SKILLS if s.lower() in low_text][:8]

    years_match = re.search(r"(\d+)\+?\s*years?", jd_text, re.IGNORECASE)
    min_years = int(years_match.group(1)) if years_match else 0

    seniority = "Mid-level"
    for word, label in (("principal", "Principal"), ("staff", "Staff/Lead"), ("lead", "Staff/Lead"),
                         ("senior", "Senior"), ("junior", "Junior"), ("entry-level", "Junior")):
        if word in jd_text.lower():
            seniority = label
            break

    return {
        "role_title": role_title,
        "must_have": must,
        "nice_to_have": nice,
        "min_years_experience": min_years,
        "seniority": seniority,
    }


@tool
def extract_requirements(jd_text: str) -> dict:
    """Parse a job description into structured must-have vs nice-to-have requirements,
    minimum years of experience, and seniority level."""
    if config.MODE == "live":
        model = llm.get_chat_model(fast=True)
        structured = model.with_structured_output(_ExtractedRequirements)
        result = structured.invoke([
            SystemMessage(content=(
                "You are a precise technical recruiter. Extract structured hiring "
                "requirements from the job description. Clearly separate hard "
                "requirements (must-have) from preferred/bonus qualifications "
                "(nice-to-have). Keep each item short - a few words to one phrase."
            )),
            HumanMessage(content=jd_text),
        ])
        return result.model_dump()
    return _heuristic_extract(jd_text)


# ==========================================================================
# compare_candidates
# ==========================================================================

class _ComparisonRow(BaseModel):
    candidate_id: str
    name: str
    matched_must_have: list[str]
    missing_must_have: list[str]
    matched_nice_to_have: list[str]
    notable_strengths: list[str] = Field(description="1-3 standout strengths specific to this candidate")


class _ComparisonResult(BaseModel):
    candidates: list[_ComparisonRow]
    summary: str = Field(description="2-4 sentence plain-English summary of who comes out ahead and why")


def skill_mentioned(item: str, skills_lower: set[str]) -> bool:
    item_l = item.lower()
    return any(item_l in sk or sk in item_l for sk in skills_lower)


def _heuristic_compare(candidate_ids: list[str], requirements: dict | None) -> dict:
    meta = load_candidate_metadata()
    must = list((requirements or {}).get("must_have", []))
    nice = list((requirements or {}).get("nice_to_have", []))

    rows = []
    for cid in candidate_ids:
        c = meta.get(cid)
        if not c:
            rows.append({"candidate_id": cid, "name": cid, "matched_must_have": [], "missing_must_have": must,
                         "matched_nice_to_have": [], "notable_strengths": [], "error": "resume not found"})
            continue
        # Match against the actual resume text (not the curated metadata skills
        # list) so results agree exactly with round-1 scoring in ranking.py -
        # two different "does this candidate have X" checks would be a real
        # explainability bug (e.g. round 1 says 4/6, compare says 5/6).
        resume_text_lower = read_resume.invoke({"candidate_id": cid}).lower()
        matched_must = [s for s in must if skill_mentioned(s, {resume_text_lower})]
        missing_must = [s for s in must if s not in matched_must]
        matched_nice = [s for s in nice if skill_mentioned(s, {resume_text_lower})]
        strengths = c["certifications"][:1] + [f"{c['years_experience']} yrs in {c['domain_experience'][0]}"]
        rows.append({
            "candidate_id": cid, "name": c["name"],
            "matched_must_have": matched_must, "missing_must_have": missing_must,
            "matched_nice_to_have": matched_nice, "notable_strengths": strengths,
            "years_experience": c["years_experience"],
        })

    valid = [r for r in rows if "error" not in r]
    if len(valid) >= 2:
        ranked = sorted(valid, key=lambda r: (len(r["matched_must_have"]), len(r["matched_nice_to_have"]),
                                               r.get("years_experience", 0)), reverse=True)
        best, runner_up = ranked[0], ranked[1]
        summary = (
            f"{best['name']} leads this comparison, covering {len(best['matched_must_have'])}/{len(must)} "
            f"must-have requirement(s) versus {runner_up['name']}'s {len(runner_up['matched_must_have'])}/{len(must)}. "
        )
        missing_for_runner = [m for m in runner_up["missing_must_have"] if m not in best["missing_must_have"]]
        if missing_for_runner:
            summary += f"The gap comes down to {', '.join(missing_for_runner[:2])}."
        else:
            summary += f"{best['name']} also has more relevant nice-to-have coverage."
    else:
        summary = "Could not fully compare - one or more candidate_ids were not found."

    return {"candidates": rows, "summary": summary}


@tool
def compare_candidates(candidate_ids: list[str], requirements_json: str = "") -> dict:
    """Head-to-head comparison of two or more candidates against the current job
    requirements. Pass the candidate_ids you want compared (from search_resumes
    or the shortlist)."""
    requirements = json.loads(requirements_json) if requirements_json else None

    if config.MODE == "live":
        resumes = {cid: read_resume.invoke({"candidate_id": cid}) for cid in candidate_ids}
        resume_block = "\n\n---\n\n".join(f"[{cid}]\n{text}" for cid, text in resumes.items())
        model = llm.get_chat_model(fast=False)
        structured = model.with_structured_output(_ComparisonResult)
        result = structured.invoke([
            SystemMessage(content=(
                "You are a technical recruiter comparing candidates head-to-head "
                "against a job's requirements. Be specific and evidence-based - cite "
                "what's actually in each resume, don't guess."
            )),
            HumanMessage(content=(
                f"REQUIREMENTS:\n{json.dumps(requirements, indent=2)}\n\n"
                f"CANDIDATES:\n{resume_block}"
            )),
        ])
        return result.model_dump()

    return _heuristic_compare(candidate_ids, requirements)


# ==========================================================================
# generate_interview_questions
# ==========================================================================

class _InterviewQuestions(BaseModel):
    questions: list[str] = Field(description="5-7 targeted screening questions for this specific candidate")


def _heuristic_interview_questions(candidate_id: str, requirements: dict | None) -> list[str]:
    meta = load_candidate_metadata()
    c = meta.get(candidate_id)
    if not c:
        return [f"No resume found for candidate_id={candidate_id!r}."]

    must = (requirements or {}).get("must_have", [])
    nice = (requirements or {}).get("nice_to_have", [])
    resume_text_lower = read_resume.invoke({"candidate_id": candidate_id}).lower()
    missing = [s for s in (must + nice) if not skill_mentioned(s, {resume_text_lower})]

    questions = [
        f"Walk me through a production project where you used "
        f"{random.choice(c['skills'])} - what was your specific role, and what "
        f"would you do differently now?",
        f"You've worked across {c['num_previous_companies']} company(ies) in "
        f"{c['years_experience']} years - what's driven those moves?",
    ]
    for gap in missing[:3]:
        questions.append(
            f"This role expects {gap}, which isn't explicit on your resume - "
            f"how would you ramp up on that, and have you touched anything adjacent to it?"
        )
    if c.get("domain_experience"):
        questions.append(
            f"You've worked in {c['domain_experience'][0]} - what's one domain-specific "
            f"constraint from that industry that shaped how you built software?"
        )
    questions.append("Tell me about a time you disagreed with a technical decision on your team. What did you do?")
    return questions


@tool
def generate_interview_questions(candidate_id: str, requirements_json: str = "") -> list[str]:
    """Generate targeted screening questions for one candidate - a mix of
    questions that probe their strongest claimed skills and questions that
    probe any gaps relative to the job requirements."""
    requirements = json.loads(requirements_json) if requirements_json else None

    if config.MODE == "live":
        resume_text = read_resume.invoke({"candidate_id": candidate_id})
        model = llm.get_chat_model(fast=False)
        structured = model.with_structured_output(_InterviewQuestions)
        result = structured.invoke([
            SystemMessage(content=(
                "You are a senior technical interviewer preparing a phone screen. "
                "Write specific, targeted questions for THIS candidate - reference "
                "things actually on their resume, and specifically probe any gap "
                "between their resume and the job's requirements. Avoid generic "
                "questions that could apply to anyone."
            )),
            HumanMessage(content=(
                f"REQUIREMENTS:\n{json.dumps(requirements, indent=2)}\n\n"
                f"CANDIDATE RESUME ({candidate_id}):\n{resume_text}"
            )),
        ])
        return result.questions

    return _heuristic_interview_questions(candidate_id, requirements)


# ==========================================================================
# recommend_hire_decision  (Part C.1, round 3)
# ==========================================================================

class _HireDecision(BaseModel):
    decision: str = Field(description="Exactly one of: 'Hire', 'Hire with reservations', 'No Hire'")
    reasoning: str = Field(description="2-4 sentences of concrete, evidence-based reasoning")


def _heuristic_hire_decision(candidate_id: str, shortlist: list[dict], deep_analysis: dict) -> dict:
    entry = next((c for c in shortlist if c["candidate_id"] == candidate_id), None)
    score = entry["score"] if entry else 0
    gaps = (deep_analysis.get(candidate_id, {}) or {}).get("gaps") or (entry["missing_must_have"] if entry else [])

    if score >= config.HIRE_SCORE_THRESHOLD and not gaps:
        decision = "Hire"
        reasoning = f"Score of {score:.0f}/100 with no missing must-have requirements - a strong, low-risk match."
    elif score >= config.HIRE_WITH_RESERVATIONS_THRESHOLD:
        decision = "Hire with reservations"
        gap_text = ", ".join(gaps[:3]) if gaps else "a couple of secondary gaps"
        reasoning = f"Score of {score:.0f}/100 - solid overall fit, but {gap_text} should be probed in the next round."
    else:
        decision = "No Hire"
        gap_text = ", ".join(gaps[:3]) if gaps else "multiple core requirement gaps"
        reasoning = f"Score of {score:.0f}/100 is below the bar for this role given current requirements ({gap_text})."

    return {"candidate_id": candidate_id, "decision": decision, "reasoning": reasoning}


@tool
def recommend_hire_decision(candidate_id: str, shortlist_json: str = "", deep_analysis_json: str = "") -> dict:
    """Round-3 final call: synthesize everything known about a candidate into a
    Hire / Hire with reservations / No Hire recommendation with reasoning."""
    shortlist = json.loads(shortlist_json) if shortlist_json else []
    deep_analysis = json.loads(deep_analysis_json) if deep_analysis_json else {}

    if config.MODE == "live":
        resume_text = read_resume.invoke({"candidate_id": candidate_id})
        entry = next((c for c in shortlist if c["candidate_id"] == candidate_id), {})
        analysis = deep_analysis.get(candidate_id, {})
        model = llm.get_chat_model(fast=False)
        structured = model.with_structured_output(_HireDecision)
        result = structured.invoke([
            SystemMessage(content=(
                "You are a hiring manager making the final call on a candidate after "
                "two screening rounds. Weigh the match score, the deep-analysis "
                "strengths/gaps, and the resume itself. Be decisive - avoid hedging "
                "into 'Hire with reservations' unless there's a genuine, specific reason."
            )),
            HumanMessage(content=(
                f"CANDIDATE {candidate_id} - ROUND 1 SCORE ENTRY:\n{json.dumps(entry, indent=2)}\n\n"
                f"ROUND 2 DEEP ANALYSIS:\n{json.dumps(analysis, indent=2)}\n\n"
                f"RESUME:\n{resume_text}"
            )),
        ])
        return {"candidate_id": candidate_id, **result.model_dump()}

    return _heuristic_hire_decision(candidate_id, shortlist, deep_analysis)


# ==========================================================================
# deep_analyze_candidate  (Part C.1, round 2 + Part C.2 explainability)
# ==========================================================================

class _DeepAnalysis(BaseModel):
    strengths: list[str] = Field(description="3-5 specific strengths relative to the requirements")
    gaps: list[str] = Field(description="Specific gaps relative to the requirements; empty list if none")
    improvement_suggestions: list[str] = Field(
        description="Concrete suggestions IF this candidate is borderline; empty list for clearly strong or clearly weak candidates")
    verdict: str = Field(description="Exactly one of: 'Strong match', 'Borderline', 'Not a fit'")


def _heuristic_deep_analyze(candidate_id: str, round1_score: dict | None, requirements: dict | None) -> dict:
    if not round1_score:
        return {"candidate_id": candidate_id, "strengths": [], "gaps": [],
                "improvement_suggestions": [], "verdict": "n/a - not in round 1 shortlist"}

    strengths = list(round1_score.get("matched_must_have", [])) + list(round1_score.get("matched_nice_to_have", []))
    gaps = list(round1_score.get("missing_must_have", []))
    score = round1_score.get("score", 0)

    if score >= config.STRONG_MATCH_THRESHOLD:
        verdict = "Strong match"
    elif score >= config.BORDERLINE_SCORE_BAND[0]:
        verdict = "Borderline"
    else:
        verdict = "Not a fit"

    suggestions = []
    if config.BORDERLINE_SCORE_BAND[0] <= score <= config.BORDERLINE_SCORE_BAND[1]:
        for gap in gaps[:3]:
            suggestions.append(f"Hands-on {gap} experience would meaningfully strengthen this application.")
        min_years = (requirements or {}).get("min_years_experience", 0)
        years = round1_score.get("years_experience", 0)
        if not gaps and years < min_years:
            suggestions.append(f"Currently under the {min_years}+ year bar - worth probing depth in the interview.")

    return {
        "candidate_id": candidate_id,
        "strengths": strengths or ["Relevant overall background for this role."],
        "gaps": gaps,
        "improvement_suggestions": suggestions,
        "verdict": verdict,
    }


@tool
def deep_analyze_candidate(candidate_id: str, requirements_json: str = "", round1_score_json: str = "") -> dict:
    """Round-2 deep dive on one candidate: specific strengths, specific gaps
    relative to the job requirements, and (only if genuinely borderline)
    concrete suggestions for what would strengthen their application."""
    requirements = json.loads(requirements_json) if requirements_json else None
    round1_score = json.loads(round1_score_json) if round1_score_json else None

    if config.MODE == "live":
        resume_text = read_resume.invoke({"candidate_id": candidate_id})
        model = llm.get_chat_model(fast=False)
        structured = model.with_structured_output(_DeepAnalysis)
        result = structured.invoke([
            SystemMessage(content=(
                "You are a senior technical recruiter doing a deep second-round review of "
                "one candidate against a job's requirements. Be specific and evidence-based - "
                "cite what's actually in the resume. Only populate improvement_suggestions if "
                "this candidate is genuinely borderline (close to qualifying, with real, fixable "
                "gaps) - leave it empty for candidates who are clearly strong or clearly not a fit."
            )),
            HumanMessage(content=(
                f"REQUIREMENTS:\n{json.dumps(requirements, indent=2)}\n\n"
                f"ROUND 1 SCORE:\n{json.dumps(round1_score, indent=2)}\n\n"
                f"RESUME:\n{resume_text}"
            )),
        ])
        return {"candidate_id": candidate_id, **result.model_dump()}

    return _heuristic_deep_analyze(candidate_id, round1_score, requirements)


SCREENING_TOOLS = [extract_requirements, compare_candidates, generate_interview_questions,
                    deep_analyze_candidate, recommend_hire_decision]
